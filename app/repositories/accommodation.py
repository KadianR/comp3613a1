from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.accommodation import Accommodation, BookingRequest, StayReview
from app.models.user import User


class AccommodationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_available(self, query: str = "", sort: str = "newest") -> list[Accommodation]:
        average_rating = (
            select(func.avg(StayReview.rating))
            .where(StayReview.accommodation_id == Accommodation.id)
            .correlate(Accommodation)
            .scalar_subquery()
        )
        statement = select(Accommodation).where(Accommodation.status == "available")
        if query:
            statement = statement.where(Accommodation.title.ilike(f"%{query}%"))
        if sort == "lowest_price":
            statement = statement.order_by(Accommodation.price_per_month.asc())
        elif sort == "highest_price":
            statement = statement.order_by(Accommodation.price_per_month.desc())
        elif sort == "highest_rating":
            statement = statement.order_by(average_rating.desc().nullslast())
        else:
            statement = statement.order_by(Accommodation.created_at.desc())
        return list(self.db.exec(statement).all())

    def get_available(self, accommodation_id: int) -> Accommodation | None:
        statement = select(Accommodation).where(
            Accommodation.id == accommodation_id,
            Accommodation.status == "available",
        )
        return self.db.exec(statement).one_or_none()

    def list_owned(self, landlord_id: int) -> list[Accommodation]:
        statement = (
            select(Accommodation)
            .where(Accommodation.landlord_id == landlord_id)
            .order_by(Accommodation.created_at.desc())
        )
        return list(self.db.exec(statement).all())

    def get_owned(self, accommodation_id: int, landlord_id: int) -> Accommodation | None:
        statement = select(Accommodation).where(
            Accommodation.id == accommodation_id,
            Accommodation.landlord_id == landlord_id,
        )
        return self.db.exec(statement).one_or_none()

    def update_owned(
        self,
        accommodation_id: int,
        landlord_id: int,
        title: str,
        address: str,
        description: str,
        price_per_month,
    ) -> Accommodation | None:
        accommodation = self.get_owned(accommodation_id, landlord_id)
        if accommodation is None:
            return None
        accommodation.title = title
        accommodation.address = address
        accommodation.description = description
        accommodation.price_per_month = price_per_month
        self.db.add(accommodation)
        self.db.commit()
        self.db.refresh(accommodation)
        return accommodation

    def create(self, accommodation: Accommodation) -> Accommodation:
        self.db.add(accommodation)
        self.db.commit()
        self.db.refresh(accommodation)
        return accommodation

    def create_booking_request(self, booking_request: BookingRequest) -> BookingRequest:
        self.db.add(booking_request)
        self.db.commit()
        self.db.refresh(booking_request)
        return booking_request

    def list_student_requests(self, student_id: int) -> list[dict]:
        statement = (
            select(BookingRequest, Accommodation, StayReview)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .outerjoin(StayReview, StayReview.booking_request_id == BookingRequest.id)
            .where(BookingRequest.student_id == student_id)
        )
        return [
            {
                "request": booking_request,
                "accommodation": accommodation,
                "review": review,
            }
            for booking_request, accommodation, review in self.db.exec(statement).all()
        ]

    def get_student_booking(self, booking_request_id: int, student_id: int) -> dict | None:
        statement = (
            select(BookingRequest, Accommodation)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .where(
                BookingRequest.id == booking_request_id,
                BookingRequest.student_id == student_id,
            )
        )
        result = self.db.exec(statement).first()
        if result is None:
            return None
        booking_request, accommodation = result
        return {"request": booking_request, "accommodation": accommodation}

    def list_reviewable_stays(self, student_id: int) -> list[dict]:
        statement = (
            select(BookingRequest, Accommodation)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .where(
                BookingRequest.student_id == student_id,
                BookingRequest.status.in_(["approved", "completed"]),
                BookingRequest.end_date < date.today(),
                ~select(StayReview.booking_request_id)
                .where(StayReview.booking_request_id == BookingRequest.id)
                .exists(),
            )
        )
        return [
            {"request": booking_request, "accommodation": accommodation}
            for booking_request, accommodation in self.db.exec(statement).all()
        ]

    def create_stay_review(
        self,
        student_id: int,
        student_name: str,
        booking_request_id: int,
        rating: int,
        review_text: str,
    ) -> StayReview | None:
        statement = select(BookingRequest).where(
            BookingRequest.id == booking_request_id,
            BookingRequest.student_id == student_id,
            BookingRequest.status.in_(["approved", "completed"]),
            BookingRequest.end_date < date.today(),
        )
        booking_request = self.db.exec(statement).one_or_none()
        if booking_request is None:
            return None

        existing_review = self.db.exec(
            select(StayReview).where(
                StayReview.booking_request_id == booking_request_id
            )
        ).one_or_none()
        if existing_review is not None:
            return None

        review = StayReview(
            student_name=student_name,
            student_id=student_id,
            accommodation_id=booking_request.accommodation_id,
            booking_request_id=booking_request_id,
            rating=rating,
            review_text=review_text,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def list_landlord_requests(
        self,
        landlord_id: int,
        status_filter: str | None = None,
    ) -> list[dict]:
        statement = (
            select(BookingRequest, Accommodation, User)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .join(User, BookingRequest.student_id == User.id)
            .where(Accommodation.landlord_id == landlord_id)
        )
        if status_filter:
            statement = statement.where(BookingRequest.status == status_filter)
        else:
            statement = statement.order_by(BookingRequest.created_at.desc())
        return [
            {
                "request": booking_request,
                "accommodation": accommodation,
                "student": student,
            }
            for booking_request, accommodation, student in self.db.exec(statement).all()
        ]

    def get_landlord_request(self, request_id: int, landlord_id: int) -> dict | None:
        statement = (
            select(BookingRequest, Accommodation, User)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .join(User, BookingRequest.student_id == User.id)
            .where(
                BookingRequest.id == request_id,
                Accommodation.landlord_id == landlord_id,
                BookingRequest.status == "pending",
            )
        )
        result = self.db.exec(statement).first()
        if result is None:
            return None
        booking_request, accommodation, student = result
        return {
            "request": booking_request,
            "accommodation": accommodation,
            "student": student,
        }

    def get_landlord_outcome(self, request_id: int, landlord_id: int) -> dict | None:
        statement = (
            select(BookingRequest, Accommodation, User)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .join(User, BookingRequest.student_id == User.id)
            .where(
                BookingRequest.id == request_id,
                Accommodation.landlord_id == landlord_id,
            )
        )
        result = self.db.exec(statement).first()
        if result is None:
            return None
        booking_request, accommodation, student = result
        return {
            "request": booking_request,
            "accommodation": accommodation,
            "student": student,
        }

    def mark_booking_complete(self, request_id: int, landlord_id: int) -> BookingRequest | None:
        statement = (
            select(BookingRequest)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .where(
                BookingRequest.id == request_id,
                Accommodation.landlord_id == landlord_id,
                BookingRequest.status == "approved",
                BookingRequest.end_date < date.today(),
            )
        )
        booking_request = self.db.exec(statement).one_or_none()
        if booking_request is None:
            return None
        booking_request.status = "completed"
        self.db.add(booking_request)
        self.db.commit()
        self.db.refresh(booking_request)
        return booking_request

    def delete_declined_requests(self, landlord_id: int) -> int:
        statement = (
            select(BookingRequest)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .where(
                Accommodation.landlord_id == landlord_id,
                BookingRequest.status == "declined",
            )
        )
        declined_requests = list(self.db.exec(statement).all())
        for booking_request in declined_requests:
            self.db.delete(booking_request)
        self.db.commit()
        return len(declined_requests)

    def update_booking_status(
        self,
        request_id: int,
        landlord_id: int,
        status: str,
    ) -> BookingRequest | None:
        statement = (
            select(BookingRequest)
            .join(Accommodation, BookingRequest.accommodation_id == Accommodation.id)
            .where(
                BookingRequest.id == request_id,
                Accommodation.landlord_id == landlord_id,
                BookingRequest.status == "pending",
            )
        )
        booking_request = self.db.exec(statement).one_or_none()
        if booking_request is None:
            return None
        booking_request.status = status
        self.db.add(booking_request)
        self.db.commit()
        self.db.refresh(booking_request)
        return booking_request