from datetime import date

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.models.accommodation import Accommodation, BookingRequest, StayReview
from app.repositories.accommodation import AccommodationRepository
from app.schemas.accommodation import AccommodationCreate, BookingRequestCreate, StayReviewCreate


class AccommodationService:
    def __init__(self, accommodation_repo: AccommodationRepository):
        self.accommodation_repo = accommodation_repo

    def search_available(self, query: str = "", sort: str = "newest"):
        allowed_sorts = {"lowest_price", "highest_price", "highest_rating", "newest"}
        selected_sort = sort if sort in allowed_sorts else "newest"
        return self.accommodation_repo.list_available(query, selected_sort)

    def get_available(self, accommodation_id: int):
        return self.accommodation_repo.get_available(accommodation_id)

    def list_owned(self, landlord_id: int):
        return self.accommodation_repo.list_owned(landlord_id)

    def get_owned(self, accommodation_id: int, landlord_id: int):
        return self.accommodation_repo.get_owned(accommodation_id, landlord_id)

    async def create_listing(
        self,
        landlord_id: int,
        listing_data: AccommodationCreate,
        image: UploadFile | None,
    ) -> Accommodation:
        listing = self.accommodation_repo.create(
            Accommodation(
                title=listing_data.title,
                address=listing_data.address,
                description=listing_data.description,
                price_per_month=listing_data.price_per_month,
                status="available",
                landlord_id=landlord_id,
            )
        )
        await self._save_listing_image(listing.id, image)
        return listing

    async def update_listing(
        self,
        accommodation_id: int,
        landlord_id: int,
        listing_data: AccommodationCreate,
        image: UploadFile | None,
    ) -> Accommodation:
        listing = self.accommodation_repo.update_owned(
            accommodation_id=accommodation_id,
            landlord_id=landlord_id,
            title=listing_data.title,
            address=listing_data.address,
            description=listing_data.description,
            price_per_month=listing_data.price_per_month,
        )
        if listing is None:
            raise ValueError("Property not found")
        await self._save_listing_image(listing.id, image)
        return listing

    async def _save_listing_image(self, listing_id: int, image: UploadFile | None) -> None:
        if not image or not image.filename:
            return
        allowed_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}
        suffix = allowed_types.get(image.content_type or "")
        if suffix is None:
            raise ValueError("Upload a JPG, PNG, WEBP, or GIF image")
        upload_dir = Path("app/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        image_path = upload_dir / f"accommodation-{listing_id}-{uuid4().hex}{suffix}"
        image_path.write_bytes(await image.read())

    def create_booking_request(
        self,
        student_id: int,
        booking_data: BookingRequestCreate,
    ) -> BookingRequest:
        booking_request = BookingRequest(
            student_id=student_id,
            accommodation_id=booking_data.accommodation_id,
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
            message=booking_data.message,
        )
        return self.accommodation_repo.create_booking_request(booking_request)

    def list_student_requests(self, student_id: int):
        bookings = self.accommodation_repo.list_student_requests(student_id)
        for booking in bookings:
            start_date = booking["request"].start_date
            end_date = booking["request"].end_date
            booking["completed"] = (
                booking["request"].status in {"approved", "completed"}
                and end_date < date.today()
            )
            booking["currently_happening"] = (
                booking["request"].status == "approved"
                and start_date <= date.today() <= end_date
            )
        return bookings

    def get_student_booking(self, booking_request_id: int, student_id: int):
        return self.accommodation_repo.get_student_booking(booking_request_id, student_id)

    def create_stay_review(
        self,
        student_id: int,
        student_name: str,
        review_data: StayReviewCreate,
    ) -> StayReview:
        if review_data.rating < 1 or review_data.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        review = self.accommodation_repo.create_stay_review(
            student_id=student_id,
            student_name=student_name,
            booking_request_id=review_data.booking_request_id,
            rating=review_data.rating,
            review_text=review_data.review_text,
        )
        if review is None:
            raise ValueError("This stay cannot be reviewed")
        return review

    def list_landlord_requests(self, landlord_id: int, status_filter: str | None = None):
        allowed_statuses = {None, "pending", "approved", "declined", "completed"}
        selected_status = status_filter if status_filter in allowed_statuses else None
        return self.accommodation_repo.list_landlord_requests(landlord_id, selected_status)

    def clear_declined_requests(self, landlord_id: int) -> int:
        return self.accommodation_repo.delete_declined_requests(landlord_id)

    def get_landlord_request(self, request_id: int, landlord_id: int):
        return self.accommodation_repo.get_landlord_request(request_id, landlord_id)

    def get_landlord_outcome(self, request_id: int, landlord_id: int):
        return self.accommodation_repo.get_landlord_outcome(request_id, landlord_id)

    def mark_booking_complete(self, request_id: int, landlord_id: int):
        booking_request = self.accommodation_repo.mark_booking_complete(request_id, landlord_id)
        if booking_request is None:
            raise ValueError("This booking cannot be marked complete yet")
        return booking_request

    def decide_booking_request(
        self,
        request_id: int,
        landlord_id: int,
        status: str,
    ):
        if status not in {"approved", "declined"}:
            raise ValueError("Booking requests can only be approved or declined")
        booking_request = self.accommodation_repo.update_booking_status(
            request_id=request_id,
            landlord_id=landlord_id,
            status=status,
        )
        if booking_request is None:
            raise ValueError("This booking request already has a final decision")
        return booking_request