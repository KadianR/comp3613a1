from decimal import Decimal

from fastapi import File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status

from app.dependencies import SessionDep
from app.dependencies.auth import LandlordDep
from app.repositories.accommodation import AccommodationRepository
from app.schemas.accommodation import AccommodationCreate
from app.services.accommodation_service import AccommodationService
from app.utilities.flash import flash
from . import router, templates


@router.get("/landlord/properties", response_class=HTMLResponse, name="landlord_properties_view")
async def landlord_properties_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
):
    service = AccommodationService(AccommodationRepository(db))
    return templates.TemplateResponse(
        request=request,
        name="landlord-properties.html",
        context={"user": user, "properties": service.list_owned(user.id)},
    )


@router.get("/landlord/properties/new", response_class=HTMLResponse, name="new_property_view")
async def new_property_view(request: Request, user: LandlordDep):
    return templates.TemplateResponse(
        request=request,
        name="new-property.html",
        context={"user": user},
    )


@router.post("/landlord/properties/new", name="create_property")
async def create_property(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    title: str = Form(),
    address: str = Form(),
    description: str = Form(),
    price_per_month: Decimal = Form(),
    image: UploadFile | None = File(default=None),
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        await service.create_listing(
            landlord_id=user.id,
            listing_data=AccommodationCreate(
                title=title,
                address=address,
                description=description,
                price_per_month=price_per_month,
            ),
            image=image,
        )
        flash(request, "Property listed successfully.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
        return RedirectResponse(
            url=request.url_for("new_property_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url=request.url_for("landlord_properties_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/landlord/properties/{accommodation_id}/edit",
    response_class=HTMLResponse,
    name="edit_property_view",
)
async def edit_property_view(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    accommodation_id: int,
):
    service = AccommodationService(AccommodationRepository(db))
    property_item = service.get_owned(accommodation_id, user.id)
    if property_item is None:
        return RedirectResponse(
            url=request.url_for("landlord_properties_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request=request,
        name="edit-property.html",
        context={"user": user, "property": property_item},
    )


@router.post("/landlord/properties/{accommodation_id}/edit", name="update_property")
async def update_property(
    request: Request,
    user: LandlordDep,
    db: SessionDep,
    accommodation_id: int,
    title: str = Form(),
    address: str = Form(),
    description: str = Form(),
    price_per_month: Decimal = Form(),
    image: UploadFile | None = File(default=None),
):
    service = AccommodationService(AccommodationRepository(db))
    try:
        await service.update_listing(
            accommodation_id=accommodation_id,
            landlord_id=user.id,
            listing_data=AccommodationCreate(
                title=title,
                address=address,
                description=description,
                price_per_month=price_per_month,
            ),
            image=image,
        )
        flash(request, "Property details updated.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("landlord_properties_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )