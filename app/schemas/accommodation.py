from datetime import date
from decimal import Decimal

from sqlmodel import Field, SQLModel


class BookingRequestCreate(SQLModel):
    accommodation_id: int
    start_date: date
    end_date: date
    message: str = ""


class AccommodationCreate(SQLModel):
    title: str
    address: str
    description: str
    price_per_month: Decimal = Field(gt=0)


class StayReviewCreate(SQLModel):
    booking_request_id: int
    rating: int
    review_text: str = ""