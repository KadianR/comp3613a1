from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel


class BookingRequestCreate(SQLModel):
    accommodation_id: int
    start_date: date
    end_date: date
    message: str = ""


class AccommodationCreate(SQLModel):
    title: str
    address: str
    description: str
    price_per_month: Decimal


class StayReviewCreate(SQLModel):
    booking_request_id: int
    rating: int
    review_text: str = ""