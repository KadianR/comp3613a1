from datetime import date

from fastapi import Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status

from app.dependencies import SessionDep
from app.dependencies.auth import LandlordDep
from app.repositories.accommodation import AccommodationRepository
from app.services.accommodation_service import AccommodationService
from app.utilities.flash import flash
from . import router, templates


@router.get("/landlord/requests", response_class=HTMLResponse, name="landlord_requests_view")
async def landlord_requests_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    status_filter: str | None = Query(default=None),
):
    service = AccommodationService(AccommodationRepository(db))
    requests = service.list_landlord_requests(user.id, status_filter)

    return templates.TemplateResponse(
        request=request,
        name="landlord-requests.html",
        context={
            "user": user,
            "requests": requests,
            "status_filter": status_filter,
        },
    )


@router.get(
    "/landlord/requests/{request_id}",
    response_class=HTMLResponse,
    name="landlord_request_detail_view",
)
async def landlord_request_detail_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    booking_request = service.get_landlord_request(request_id, user.id)
    if booking_request is None:
        raise HTTPException(status_code=404, detail="Booking request not found")
    return templates.TemplateResponse(
        request=request,
        name="landlord-request-detail.html",
        context={
            "user": user,
            "booking": booking_request,
        },
    )


@router.post("/landlord/requests/{request_id}/status", name="landlord_request_decision")
async def landlord_request_decision(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    request_id: int,
    decision: str = Form(),
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        service.decide_booking_request(request_id, user.id, decision)
        result = "approved" if decision == "approved" else "declined"
        flash(request, f"Booking {result}.")
    except ValueError as exc:
        flash(request, str(exc), "warning")
    return RedirectResponse(
        url=request.url_for(
            "landlord_request_outcome_view",
            request_id=request_id,
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/landlord/requests/{request_id}/outcome",
    response_class=HTMLResponse,
    name="landlord_request_outcome_view",
)
async def landlord_request_outcome_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    booking_request = service.get_landlord_outcome(request_id, user.id)
    if booking_request is None or booking_request["request"].status == "pending":
        raise HTTPException(status_code=404, detail="Booking outcome not found")
    return templates.TemplateResponse(
        request=request,
        name="landlord-request-outcome.html",
        context={
            "user": user,
            "booking": booking_request,
            "can_complete": booking_request["request"].end_date < date.today(),
        },
    )


@router.post("/landlord/requests/{request_id}/complete", name="mark_booking_complete")
async def mark_booking_complete(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        service.mark_booking_complete(request_id, user.id)
        flash(request, "Booking marked complete.")
    except ValueError as exc:
        flash(request, str(exc), "warning")
    return RedirectResponse(
        url=request.url_for("landlord_request_outcome_view", request_id=request_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/landlord/requests/clear-declined", name="clear_declined_requests")
async def clear_declined_requests(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
):
    service = AccommodationService(AccommodationRepository(db))
    cleared_count = service.clear_declined_requests(user.id)
    flash(request, f"Cleared {cleared_count} declined request(s).")
    return RedirectResponse(
        url=request.url_for("landlord_requests_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/landlord/requests/{request_id}/details",
    response_class=HTMLResponse,
    name="landlord_approved_request_details_view",
)
async def landlord_approved_request_details_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    request_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    booking_request = service.get_landlord_outcome(request_id, user.id)
    if booking_request is None or booking_request["request"].status not in {"approved", "completed"}:
        raise HTTPException(status_code=404, detail="Approved booking not found")
    return templates.TemplateResponse(
        request=request,
        name="landlord-request-outcome.html",
        context={
            "user": user,
            "booking": booking_request,
            "can_complete": booking_request["request"].end_date < date.today(),
        },
    )