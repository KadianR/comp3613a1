from fastapi import Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.accommodation import AccommodationRepository
from app.schemas.accommodation import StayReviewCreate
from app.services.accommodation_service import AccommodationService
from app.utilities.flash import flash
from fastapi import Body, Form, HTTPException, Request
from . import router, api_router, templates


@router.get(
    "/bookings/{booking_request_id}/review",
    response_class=HTMLResponse,
    name="student_review_view",
)
async def student_review_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    booking_request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    stays = service.list_student_requests(user.id)
    booking = next(
        (
            item
            for item in stays
            if item["request"].id == booking_request_id and item["completed"]
        ),
        None,
    )
    if booking is None:
        raise HTTPException(status_code=404, detail="Completed stay not found")

    return templates.TemplateResponse(
        request=request,
        name="student-review.html",
        context={
            "user": user,
            "booking": booking,
        },
    )


@router.post("/bookings/{booking_request_id}/review", name="create_stay_review")
async def create_stay_review(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    booking_request_id: int,
    rating: int = Form(),
    review_text: str = Form(default=""),
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        service.create_stay_review(
            student_id=user.id,
            student_name=user.username,
            review_data=StayReviewCreate(
                booking_request_id=booking_request_id,
                rating=rating,
                review_text=review_text,
            ),
        )
        flash(request, "Stay review submitted.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for(
            "student_review_view",
            booking_request_id=booking_request_id,
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )


# API: Submit a review for a completed stay
@api_router.post(
    "/bookings/{booking_request_id}/reviews",
    status_code=201
)
async def api_submit_review(
    booking_request_id: int,
    user: AuthDep,
    db: SessionDep,
    rating: int = Body(embed=True),
    review_text: str = Body(default="", embed=True),
):
    if user.role != "regular_user":
        raise HTTPException(
            status_code=403,
            detail="Only students can submit reviews"
        )

    service = AccommodationService(AccommodationRepository(db))

    try:
        review = service.create_stay_review(
            student_id=user.id,
            student_name=user.username,
            review_data=StayReviewCreate(
                booking_request_id=booking_request_id,
                rating=rating,
                review_text=review_text
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    return {
        "id": review.id,
        "booking_request_id": review.booking_request_id,
        "rating": review.rating,
        "review_text": review.review_text
    }
