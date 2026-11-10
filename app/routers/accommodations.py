from datetime import date

from fastapi import Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.accommodation import AccommodationRepository
from app.schemas.accommodation import BookingRequestCreate
from app.services.accommodation_service import AccommodationService
from app.utilities.flash import flash
from . import router, api_router, templates


@router.get("/accommodations", response_class=HTMLResponse)
async def accommodation_search_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    query: str = Query(default="", max_length=100),
    sort: str = Query(default="newest"),
):
    service = AccommodationService(AccommodationRepository(db))
    accommodations = service.search_available(query, sort)

    return templates.TemplateResponse(
        request=request,
        name="accommodations.html",
        context={
            "user": user,
            "query": query,
            "sort": sort,
            "accommodations": accommodations,
            "ratings": service.rating_summaries(accommodations),
        },
    )


@router.get(
    "/accommodations/{accommodation_id}",
    response_class=HTMLResponse,
    name="accommodation_detail_view",
)
async def accommodation_detail_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    accommodation_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    accommodation = service.get_available(accommodation_id)
    if accommodation is None:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    return templates.TemplateResponse(
        request=request,
        name="accommodation-detail.html",
        context={
            "user": user,
            "accommodation": accommodation,
        },
    )


@router.post("/accommodations/request", name="create_booking_request")
async def create_booking_request(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    accommodation_id: int = Form(),
    start_date: date = Form(),
    end_date: date = Form(),
    message: str = Form(default=""),
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        booking_request = service.create_booking_request(
            student_id=user.id,
            booking_data=BookingRequestCreate(
                accommodation_id=accommodation_id,
                start_date=start_date,
                end_date=end_date,
                message=message,
            ),
        )
    except ValueError as exc:
        flash(request, str(exc), "danger")
        return RedirectResponse(
            url=request.url_for(
                "accommodation_detail_view",
                accommodation_id=accommodation_id,
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url=request.url_for(
            "booking_request_confirmation_view",
            booking_request_id=booking_request.id,
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/bookings/{booking_request_id}/submitted",
    response_class=HTMLResponse,
    name="booking_request_confirmation_view",
)
async def booking_request_confirmation_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    booking_request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    booking = service.get_student_booking(booking_request_id, user.id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking request not found")
    return templates.TemplateResponse(
        request=request,
        name="booking-request-confirmation.html",
        context={
            "user": user,
            "booking": booking,
        },
    )


@router.get("/bookings", response_class=HTMLResponse, name="student_bookings_view")
async def student_bookings_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    service = AccommodationService(AccommodationRepository(db))
    return templates.TemplateResponse(
        request=request,
        name="bookings.html",
        context={
            "user": user,
            "bookings": service.list_student_requests(user.id),
        },
    )


@api_router.get("/accommodations")
async def api_list_accommodations(
    user: AuthDep,
    db: SessionDep,
    query: str = Query(default="", max_length=100),
    sort: str = Query(default="newest"),
):
    service = AccommodationService(AccommodationRepository(db))
    listings = service.search_available(query, sort)

    return [
        {
            "id": listing.id,
            "title": listing.title,
            "address": listing.address,
            "description": listing.description,
            "price_per_month": float(listing.price_per_month),
            "status": listing.status,
        }
        for listing in listings
    ]

@api_router.get("/accommodations/{accommodation_id}")
async def api_accommodation_details(
    accommodation_id: int,
    user: AuthDep,
    db: SessionDep,
):
    service = AccommodationService(AccommodationRepository(db))

    accommodation = service.get_available(accommodation_id)

    if accommodation is None:
        raise HTTPException(
            status_code=404,
            detail="Accommodation not found"
        )

    return {
        "id": accommodation.id,
        "title": accommodation.title,
        "address": accommodation.address,
        "description": accommodation.description,
        "price_per_month": float(accommodation.price_per_month),
        "status": accommodation.status,
    }


@api_router.post("/bookings", status_code=201)

async def api_create_booking(
    
    booking_data: BookingRequestCreate,
    user: AuthDep,
    db: SessionDep,
):
    
    if user.role != "regular_user":
        raise HTTPException(
            status_code=403,
            detail="Only students can submit bookings"
        )

    service = AccommodationService(AccommodationRepository(db))

    try:
        booking = service.create_booking_request(
            student_id=user.id,
            booking_data=booking_data
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    return {
        "id": booking.id,
        "accommodation_id": booking.accommodation_id,
        "student_id": booking.student_id,
        "start_date": booking.start_date,
        "end_date": booking.end_date,
        "status": booking.status,
        "message": booking.message
    }


@api_router.get("/bookings/my")
async def api_student_bookings(
    user: AuthDep,
    db: SessionDep,
):
    if user.role != "regular_user":
        raise HTTPException(
            status_code=403,
            detail="Only students can view their bookings"
        )

    service = AccommodationService(AccommodationRepository(db))
    bookings = service.list_student_requests(user.id)

    return [
        {
            "id": item["request"].id,
            "accommodation_id": item["request"].accommodation_id,
            "status": item["request"].status,
            "start_date": item["request"].start_date,
            "end_date": item["request"].end_date,
        }
        for item in bookings
    ]
