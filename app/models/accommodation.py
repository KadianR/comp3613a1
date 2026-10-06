from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Index, Numeric
from sqlmodel import Field, SQLModel


class Accommodation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    address: str
    description: str
    price_per_month: Decimal = Field(
        sa_column=Column("price_per_week", Numeric(10, 2), nullable=False)
    )
    image_url: Optional[str] = None
    # STUDENT SNIPPET: choose the SQLModel field definition for the listing status.
    status: str = Field(default="available")
    landlord_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookingRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    accommodation_id: int = Field(foreign_key="accommodation.id", index=True)
    start_date: date
    end_date: date
    # STUDENT SNIPPET: choose the SQLModel field definition used for landlord decisions.
    status: str = Field(default="pending", index=True)
    message: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StayReview(SQLModel, table=True):
    __table_args__ = (
        Index("uq_stayreview_booking_request_id", "booking_request_id", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    student_id: int = Field(foreign_key="user.id", index=True)
    accommodation_id: int = Field(foreign_key="accommodation.id", index=True)
    booking_request_id: int = Field(foreign_key="bookingrequest.id")
    # STUDENT SNIPPET: choose the SQLModel field definition for a 1-to-5 stay rating.
    rating: int = Field(ge=1, le=5)
    review_text: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)