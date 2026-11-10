
import pytest
from decimal import Decimal
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models import Accommodation, User
from app.repositories.accommodation import AccommodationRepository
from app.services.accommodation_service import AccommodationService
from datetime import date, timedelta
from app.schemas.accommodation import BookingRequestCreate
from app.schemas.accommodation import StayReviewCreate

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        yield db

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


# IT-01: Search available accommodation listings
def test_search_listing(session):
    landlord = User(
        username="landlord1",
        email="landlord1@example.com",
        password="password",
        role="landlord"
    )
    session.add(landlord)
    session.commit()
    session.refresh(landlord)

    repo = AccommodationRepository(session)
    service = AccommodationService(repo)

    repo.create(Accommodation(
        title="Studio near UWI",
        address="St Augustine",
        description="Student studio",
        price_per_month=Decimal("1500"),
        status="available",
        landlord_id=landlord.id
    ))

    repo.create(Accommodation(
        title="Studio in Curepe",
        address="Curepe",
        description="Student studio",
        price_per_month=Decimal("1200"),
        status="unavailable",
        landlord_id=landlord.id
    ))

    repo.create(Accommodation(
        title="Two Bedroom Apartment",
        address="Tunapuna",
        description="Apartment",
        price_per_month=Decimal("2000"),
        status="available",
        landlord_id=landlord.id
    ))

    results = service.search_available("Studio")

    assert len(results) == 1
    assert results[0].title == "Studio near UWI"
    assert results[0].status == "available"


# IT-02: View an accommodation by ID
def test_view_listing(session):
    landlord = User(
        username="landlord2",
        email="landlord2@example.com",
        password="password",
        role="landlord"
    )
    session.add(landlord)
    session.commit()
    session.refresh(landlord)

    repo = AccommodationRepository(session)
    service = AccommodationService(repo)

    listing = repo.create(Accommodation(
        title="Student Apartment",
        address="St Augustine",
        description="Apartment near campus",
        price_per_month=Decimal("1800"),
        status="available",
        landlord_id=landlord.id
    ))

    result = service.get_available(listing.id)

    assert result is not None
    assert result.id == listing.id
    assert result.title == "Student Apartment"


# Helper: Create a student, landlord, and booking
def create_test_booking(session):
    landlord = User(
        username="landlord_test",
        email="landlord@test.com",
        password="password",
        role="landlord"
    )

    student = User(
        username="student_test",
        email="student@test.com",
        password="password",
        role="student"
    )

    session.add_all([landlord, student])
    session.commit()
    session.refresh(landlord)
    session.refresh(student)

    repo = AccommodationRepository(session)
    service = AccommodationService(repo)

    listing = repo.create(Accommodation(
        title="Student Studio",
        address="St Augustine",
        description="Near UWI",
        price_per_month=Decimal("1500"),
        status="available",
        landlord_id=landlord.id
    ))

    booking_data = BookingRequestCreate(
        accommodation_id=listing.id,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=31),
        message="Interested in renting"
    )

    booking = service.create_booking_request(
        student.id, booking_data
    )

    return service, landlord, student, listing, booking


# IT-03: Verify a booking is created
def test_create_booking(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    result = service.get_student_booking(
        booking.id, student.id
    )

    assert result is not None
    assert result["request"].status == "pending"
    assert result["request"].student_id == student.id
    assert result["request"].accommodation_id == listing.id


# IT-04: Verify student can retrieve their bookings
def test_student_bookings(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    results = service.list_student_requests(student.id)

    assert len(results) == 1
    assert results[0]["request"].id == booking.id
    assert results[0]["request"].status == "pending"


# IT-05: Landlord can view their booking requests
def test_landlord_requests(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    results = service.list_landlord_requests(landlord.id, "pending")

    assert len(results) == 1
    assert results[0]["request"].id == booking.id
    assert results[0]["accommodation"].id == listing.id
    assert results[0]["student"].id == student.id

    # Another landlord should not see these requests
    other_results = service.list_landlord_requests(
        landlord.id + 100, "pending"
    )
    assert other_results == []


# IT-06: Approve a booking request
def test_approve_bookings(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    service.decide_booking_request(
        request_id=booking.id,
        landlord_id=landlord.id,
        status="approved"
    )

    session.expire_all()
    result = service.get_student_booking(booking.id, student.id)

    assert result is not None
    assert result["request"].status == "approved"


# IT-07: Decline a booking request
def test_decline_booking(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    service.decide_booking_request(
        request_id=booking.id,
        landlord_id=landlord.id,
        status="declined"
    )

    session.expire_all()
    result = service.get_student_booking(booking.id, student.id)

    assert result is not None
    assert result["request"].status == "declined"


# IT-08: Prevent another landlord from changing a booking
def test_wrong_landlord_decision(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    wrong_landlord_id = landlord.id + 100

    with pytest.raises(ValueError):
        service.decide_booking_request(
            request_id=booking.id,
            landlord_id=wrong_landlord_id,
            status="approved"
        )

    session.expire_all()
    result = service.get_student_booking(booking.id, student.id)

    assert result is not None
    assert result["request"].status == "pending"


# Helper: Prepare an approved stay that has ended
def prepare_completed_stay(session, service, landlord, booking):
    service.decide_booking_request(
        request_id=booking.id,
        landlord_id=landlord.id,
        status="approved"
    )

    # Set historical dates to simulate an ended stay
    booking.start_date = date.today() - timedelta(days=40)
    booking.end_date = date.today() - timedelta(days=10)

    session.add(booking)
    session.commit()
    session.refresh(booking)

    return service.mark_booking_complete(
        request_id=booking.id,
        landlord_id=landlord.id
    )


# IT-09: Complete an approved stay
def test_complete_stay(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    completed = prepare_completed_stay(
        session, service, landlord, booking
    )

    assert completed.status == "completed"

    session.expire_all()
    result = service.get_student_booking(
        booking.id, student.id
    )

    assert result is not None
    assert result["request"].status == "completed"


# IT-10: Submit a review for a completed stay
def test_submit_review(session):
    service, landlord, student, listing, booking = create_test_booking(session)

    prepare_completed_stay(
        session, service, landlord, booking
    )

    review_data = StayReviewCreate(
        booking_request_id=booking.id,
        rating=5,
        review_text="Great accommodation"
    )

    review = service.create_stay_review(
        student_id=student.id,
        student_name=student.username,
        review_data=review_data
    )

    assert review.rating == 5

    session.expire_all()
    reviews = service.accommodation_repo.list_reviews(
        listing.id
    )

    assert len(reviews) == 1
    assert reviews[0].booking_request_id == booking.id
    assert reviews[0].rating == 5
    assert reviews[0].review_text == "Great accommodation"
