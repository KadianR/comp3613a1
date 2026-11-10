"""Local-only Postman test-data fixture endpoint for COMP 3613 A2.

This file is NEVER imported by default.  Enable explicitly from app/main.py
only when ENV=development, DATABASE_URI=sqlite:///..., and the environment
variable A2_ENABLE_POSTMAN_FIXTURES=1.  Do not deploy or enable it publicly.

Fixture creates NEW rows on every run, leaving normal booking rules intact.
"""

import os
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlmodel import select

from app.config import get_settings
from app.dependencies import SessionDep
from app.dependencies.auth import LandlordDep
from app.models.accommodation import Accommodation, BookingRequest
from app.models.user import User

router = APIRouter(prefix="/api/_a2", include_in_schema=False)


class PostmanSeedRequest(BaseModel):
    student_username: str = Field(min_length=1, max_length=100)


def _local_test_mode(request: Request) -> bool:
    settings = get_settings()
    return (
        os.getenv("A2_ENABLE_POSTMAN_FIXTURES") == "1"
        and settings.env.lower() in {"dev", "development", "test", "testing"}
        and settings.database_uri.lower().startswith("sqlite")
        and settings.app_host in {"127.0.0.1", "::1"}
        and request.client is not None
        and request.client.host in {"127.0.0.1", "::1"}
    )


@router.post("/fixture-bookings", status_code=status.HTTP_201_CREATED)
def create_local_booking_fixtures(
    payload: PostmanSeedRequest,
    request: Request,
    landlord: LandlordDep,
    db: SessionDep,
):
    """Seed two pending requests and one ended approved stay.

    Intended for the Postman Collection Runner, NOT the public application.
    Landlord must be authenticated, student must be an existing student.
    """
    if not _local_test_mode(request):
        raise HTTPException(status_code=404, detail="Not found")

    student = db.exec(
        select(User).where(
            User.username == payload.student_username,
            User.role == "regular_user",
        )
    ).first()
    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Test student not found; check studentUsername",
        )

    tag = uuid4().hex[:10]
    listing = Accommodation(
        title=f"A2 Postman Fixture {tag}",
        address="Local Test Accommodation, Trinidad",
        description="Automation fixture for COMP 3613 A2; local SQLite testing only.",
        price_per_month=Decimal("1500.00"),
        status="available",
        landlord_id=landlord.id,
    )
    db.add(listing)
    db.flush()  # obtain listing.id without committing incomplete setup

    today = date.today()
    future_start = today + timedelta(days=3)
    future_end = future_start + timedelta(days=30)
    historical_end = today - timedelta(days=2)
    historical_start = historical_end - timedelta(days=30)

    approval = BookingRequest(
        student_id=student.id,
        accommodation_id=listing.id,
        start_date=future_start,
        end_date=future_end,
        status="pending",
        message=f"A2 {tag} -- for approval",
    )
    decline = BookingRequest(
        student_id=student.id,
        accommodation_id=listing.id,
        start_date=future_start,
        end_date=future_end,
        status="pending",
        message=f"A2 {tag} -- for decline",
    )
    completion = BookingRequest(
        student_id=student.id,
        accommodation_id=listing.id,
        start_date=historical_start,
        end_date=historical_end,
        status="approved",
        message=f"A2 {tag} -- historical stay for completion and review",
    )
    db.add_all([approval, decline, completion])
    db.commit()
    for row in (listing, approval, decline, completion):
        db.refresh(row)

    return {
        "fixture_listing_id": listing.id,
        "approval_booking_id": approval.id,
        "decline_booking_id": decline.id,
        "completed_booking_id": completion.id,
        "student_id": student.id,
        "landlord_id": landlord.id,
    }
