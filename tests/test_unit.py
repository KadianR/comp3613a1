
from unittest.mock import Mock
from app.services.accommodation_service import AccommodationService
import pytest
from datetime import date, timedelta
from app.schemas.accommodation import BookingRequestCreate
import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.services.accommodation_service import AccommodationService
from app.schemas.accommodation import BookingRequestCreate, StayReviewCreate

def test_search_available():
    mock_repo = Mock()
    mock_repo.list_available.return_value = ["studio listing"]
    service = AccommodationService(mock_repo)

    result = service.search_available("studio", "lowest_price")

    mock_repo.list_available.assert_called_once_with("studio", "lowest_price")
    assert result == ["studio listing"]


def test_invalid_sort():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    service.search_available("room", "invalid_sort")

    mock_repo.list_available.assert_called_once_with("room", "newest")

def test_past_start_date():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=7)
    )

    with pytest.raises(ValueError, match="Start date cannot be in the past"):
        service.create_booking_request(1, booking)

    mock_repo.create_booking_request.assert_not_called()


def test_invalid_end_date():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=1)
    )

    with pytest.raises(ValueError, match="End date must be after the start date"):
        service.create_booking_request(1, booking)

    mock_repo.create_booking_request.assert_not_called()


# UT-03: Reject booking with a past start date
def test_past_start_date():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=7)
    )

    with pytest.raises(ValueError, match="Start date cannot be in the past"):
        service.create_booking_request(1, booking)

    mock_repo.create_booking_request.assert_not_called()


# UT-04: Reject booking with an invalid end date
def test_invalid_end_date():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=1)
    )

    with pytest.raises(ValueError, match="End date must be after the start date"):
        service.create_booking_request(1, booking)

    mock_repo.create_booking_request.assert_not_called()


# UT-05: Reject booking for unavailable accommodation
def test_unavailable_listing():
    mock_repo = Mock()
    mock_repo.get_available.return_value = None
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=30)
    )

    with pytest.raises(ValueError, match="This accommodation is no longer available"):
        service.create_booking_request(1, booking)

    mock_repo.create_booking_request.assert_not_called()


# UT-06: Create a valid booking request
def test_valid_booking():
    mock_repo = Mock()
    mock_repo.get_available.return_value = Mock()
    mock_repo.create_booking_request.side_effect = lambda booking: booking
    service = AccommodationService(mock_repo)

    booking = BookingRequestCreate(
        accommodation_id=1,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=30)
    )

    result = service.create_booking_request(1, booking)

    assert result.status == "pending"
    assert result.student_id == 1
    mock_repo.create_booking_request.assert_called_once()


# UT-07: Reject invalid booking decision
def test_invalid_decision():
    mock_repo = Mock()
    service = AccommodationService(mock_repo)

    with pytest.raises(ValueError, match="Booking requests can only be approved or declined"):
        service.decide_booking_request(
            request_id=1,
            landlord_id=2,
            status="completed"
        )

    mock_repo.update_booking_status.assert_not_called()


# UT-08: Approve or decline a booking request
def test_booking_decision():
    for status in ("approved", "declined"):
        mock_repo = Mock()
        mock_repo.update_booking_status.return_value = Mock(status=status)
        service = AccommodationService(mock_repo)

        result = service.decide_booking_request(
            request_id=1,
            landlord_id=2,
            status=status
        )

        mock_repo.update_booking_status.assert_called_once_with(
            request_id=1,
            landlord_id=2,
            status=status
        )
        assert result.status == status


# UT-09: Reject rating outside 1-5
def test_invalid_review_rating():
    for rating in (0, 6):
        mock_repo = Mock()
        service = AccommodationService(mock_repo)

        review = StayReviewCreate(
            booking_request_id=1,
            rating=rating,
            review_text="Test review"
        )

        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            service.create_stay_review(
                student_id=1,
                student_name="Test Student",
                review_data=review
            )

        mock_repo.create_stay_review.assert_not_called()


# UT-10: Reject review for ineligible stay
def test_ineligible_review():
    mock_repo = Mock()
    mock_repo.create_stay_review.return_value = None
    service = AccommodationService(mock_repo)

    review = StayReviewCreate(
        booking_request_id=1,
        rating=5,
        review_text="Great accommodation"
    )

    with pytest.raises(ValueError, match="This stay cannot be reviewed"):
        service.create_stay_review(
            student_id=1,
            student_name="Test Student",
            review_data=review
        )

    mock_repo.create_stay_review.assert_called_once()
