#!/usr/bin/env python3
"""FastStarter project CLI — stdlib argparse (no extra CLI library).

From the project root (venv active, deps installed; ``.env`` optional — falls back to ``.env.example``):

    python manage.py init
    python manage.py run
    python manage.py users
    python manage.py report --name "Student Name" --id "816000000"
    python manage.py usecase
    python manage.py skills-verify
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path


def _ensure_models_loaded() -> None:
    import app.models  # noqa: F401


def cmd_init(args: argparse.Namespace) -> None:
    """Create database tables (drops existing by default) and seed demo users."""
    from app.config import get_settings, mask_database_uri
    from app.database import drop_all, ensure_db_and_tables

    _ensure_models_loaded()
    if args.drop:
        print("Dropping all tables…")
        # Drop can fail on a brand-new empty DB; create path still retries.
        try:
            drop_all()
        except Exception as exc:  # noqa: BLE001
            from app.database import is_db_not_ready_error

            if not is_db_not_ready_error(exc):
                raise
            print(f"Database not ready yet while dropping ({exc}); continuing…")
    print("Creating tables…")
    ensure_db_and_tables()
    print(f"Database ready ({mask_database_uri(get_settings().database_uri)}).")
    if getattr(args, "seed", True):
        cmd_seed(args)


_NEW_STUDENTS = [
    "anika.mohammed", "jerome.baptiste", "nadia.persad", "marcus.joseph",
    "priya.maharaj", "devon.charles", "shanice.williams", "ravi.singh",
    "tiana.thomas", "kyle.alexander", "sasha.ali", "isaiah.phillip",
]

_BASE_TITLES = [
    "Savannah Heights", "Maraval Garden Apartment", "Chaguanas Central Flat",
    "San Fernando Hill View", "Scarborough Bay Apartment",
]

# Remote seed photos are reused because only these URLs have been confirmed to load.
_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=85",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=85",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85",
    "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1200&q=85",
    "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=85",
]

_EXTRA_LISTINGS = [
    ("St. Augustine Student Studio", "14 Gordon Street, St. Augustine, Trinidad",
     "A compact furnished studio a short walk from the UWI St. Augustine campus.", 3200),
    ("Curepe Junction Flat", "3 Churchill Roosevelt Highway, Curepe, Trinidad",
     "A bright two-bedroom flat near the Curepe junction with easy maxi taxi access.", 3800),
    ("Arima Heights Apartment", "22 Cleaver Road, Arima, Trinidad",
     "A quiet, secure apartment in the Arima hills with parking and a shared yard.", 3000),
    ("Couva Gardens Townhouse", "41 Southern Main Road, Couva, Trinidad",
     "A spacious townhouse with a study nook, close to shopping and the highway.", 4200),
    ("Diego Martin Hillside Suite", "8 Ibis Avenue, Diego Martin, Trinidad",
     "A modern suite with a balcony and a cool breeze, minutes from Westmoorings.", 5200),
    ("Mount Hope Residence", "17 Mount Hope Road, Mount Hope, Trinidad",
     "A furnished room-and-kitchen unit near the medical sciences complex.", 3600),
]

# One list of ratings per listing, in _BASE_TITLES + _EXTRA_LISTINGS order.
_RATING_PATTERNS = [
    [5, 4, 5, 4], [4, 4, 3, 5], [5, 5, 4], [3, 4, 4, 3], [4, 5, 5, 4], [3, 3, 4],
    [5, 4, 4, 5], [4, 3, 5], [2, 4, 3, 4], [5, 5, 5], [4, 4, 3, 4],
]

_REVIEW_TEXT = {
    5: [
        "Spotless and quiet, with a quick commute to campus. The landlord answered every message the same day.",
        "Exactly as pictured. Great water pressure, reliable internet and a very safe neighbourhood.",
        "The best place I have stayed as a student. Bright rooms, friendly neighbours and fair rent.",
    ],
    4: [
        "Comfortable and well located. A couple of small repairs took a few days but were handled politely.",
        "Good value for the area. Quiet at night and close to maxi taxi routes.",
        "Clean, furnished and easy to settle into. Parking was a little tight.",
    ],
    3: [
        "Decent for the price, but the water supply was patchy some mornings.",
        "Convenient location, though the furniture was dated and the street can get noisy.",
        "Fine for a semester. Communication could have been quicker.",
    ],
    2: ["Rent was fair but maintenance was slow and the kitchen needed attention."],
}

# (username, listing, kind, start offset in days, length in days, message)
_EXTRA_BOOKINGS = [
    ("bob", "Scarborough Bay Apartment", "past", -100, 60, "I spent the semester here and would like to leave a review."),
    ("bob", "Maraval Garden Apartment", "past", -210, 90, "A quiet semester stay near campus; I would like to review it."),
    ("bob", "Chaguanas Central Flat", "past", -180, 60, "I stayed here during the term and would like to leave feedback."),
    ("bob", "San Fernando Hill View", "past", -150, 75, "A comfortable past stay that I want to review."),
    ("bob", "St. Augustine Student Studio", "past", -120, 60, "This studio worked well for my semester near UWI."),
    ("bob", "Curepe Junction Flat", "past", -90, 45, "I finished my stay and would like to share a review."),
    ("alice", "Savannah Heights", "past", -90, 60, "Stayed for two months while on placement."),
    ("carmen", "San Fernando Hill View", "past", -75, 45, "Short stay during exam season."),
    ("anika.mohammed", "St. Augustine Student Studio", "current", -20, 90, "Moving in for the full semester."),
    ("jerome.baptiste", "Curepe Junction Flat", "current", -10, 60, "Sharing with a classmate this term."),
    ("kyle.alexander", "Couva Gardens Townhouse", "current", 30, 90, "Booking ahead for next semester."),
    ("nadia.persad", "Savannah Heights", "pending", 14, 60, "Is the apartment available from the start of next month?"),
    ("marcus.joseph", "Maraval Garden Apartment", "pending", 21, 90, "I am a postgraduate student and need a quiet space."),
    ("priya.maharaj", "Scarborough Bay Apartment", "pending", 30, 60, "Doing a placement in Tobago for two months."),
    ("devon.charles", "Diego Martin Hillside Suite", "pending", 18, 120, "Looking for a longer stay close to the city."),
    ("shanice.williams", "Mount Hope Residence", "pending", 25, 90, "Close to my clinical rotations, which is ideal."),
    ("sasha.ali", "Arima Heights Apartment", "pending", 12, 60, "Can I arrange a viewing this weekend?"),
    ("ravi.singh", "Savannah Heights", "declined", 10, 30, "Hoping for a short-term booking."),
    ("tiana.thomas", "Arima Heights Apartment", "declined", 20, 30, "Needed somewhere for a month."),
]


def _find_booking(session, student_id: int, listing_id: int, kind: str):
    from sqlmodel import select

    from app.models.accommodation import BookingRequest

    statement = select(BookingRequest).where(
        BookingRequest.student_id == student_id,
        BookingRequest.accommodation_id == listing_id,
    )
    if kind == "past":
        statement = statement.where(
            BookingRequest.status.in_(["approved", "completed"]),
            BookingRequest.end_date < date.today(),
        )
    elif kind == "current":
        statement = statement.where(
            BookingRequest.status == "approved",
            BookingRequest.end_date >= date.today(),
        )
    else:
        statement = statement.where(BookingRequest.status == kind)
    return session.exec(statement).first()


def _seed_extra_demo(session, user_repo, accommodation_repo, landlord) -> None:
    """Add listings, completed stays with reviews, and varied requests; safe to rerun."""
    from datetime import datetime, time

    from sqlmodel import select

    from app.models.accommodation import Accommodation, BookingRequest, StayReview

    titles = list(_BASE_TITLES)
    for index, (title, address, description, price) in enumerate(_EXTRA_LISTINGS):
        titles.append(title)
        if session.exec(select(Accommodation).where(Accommodation.title == title)).first():
            continue
        accommodation_repo.create(
            Accommodation(
                title=title,
                address=address,
                description=description,
                price_per_month=price,
                image_url=_IMAGE_URLS[index % len(_IMAGE_URLS)],
                status="available",
                landlord_id=landlord.id,
            )
        )
        print(f"  create {title} (accommodation)")

    listings = {
        listing.title: listing
        for listing in session.exec(select(Accommodation).where(Accommodation.title.in_(titles))).all()
    }
    reviewers = [user_repo.get_by_username(name) for name in _NEW_STUDENTS]
    today = date.today()
    reviews_added = 0

    review_plan = [(listings.get(title), ratings) for title, ratings in zip(titles, _RATING_PATTERNS)]
    known = set(titles)
    # Listings created through the UI also get ratings so every place can be demoed.
    review_plan += [
        (listing, [4, 5, 4])
        for listing in session.exec(select(Accommodation)).all()
        if listing.title not in known
        and not session.exec(select(StayReview).where(StayReview.accommodation_id == listing.id)).first()
    ]

    for i, (listing, ratings) in enumerate(review_plan):
        if listing is None:
            continue
        for k, rating in enumerate(ratings):
            student = reviewers[(i + 3 * k) % len(reviewers)]
            if student is None:
                continue
            booking = _find_booking(session, student.id, listing.id, "past")
            if booking is None:
                end = today - timedelta(days=15 + 25 * k + 4 * i)
                booking = accommodation_repo.create_booking_request(
                    BookingRequest(
                        student_id=student.id,
                        accommodation_id=listing.id,
                        start_date=end - timedelta(days=30 * (1 + (i + k) % 3)),
                        end_date=end,
                        status="completed" if k % 2 == 0 else "approved",
                        message="Looking for a place close to campus for the semester.",
                    )
                )
            if session.exec(select(StayReview).where(StayReview.booking_request_id == booking.id)).first():
                continue
            texts = _REVIEW_TEXT[rating]
            session.add(
                StayReview(
                    student_name=student.username,
                    student_id=student.id,
                    accommodation_id=listing.id,
                    booking_request_id=booking.id,
                    rating=rating,
                    review_text=texts[(i + k) % len(texts)],
                    created_at=datetime.combine(booking.end_date + timedelta(days=1), time(10, 0)),
                )
            )
            session.commit()
            reviews_added += 1

    bookings_added = 0
    for username, title, kind, offset, length, message in _EXTRA_BOOKINGS:
        student = user_repo.get_by_username(username)
        listing = listings.get(title)
        if student is None or listing is None or _find_booking(session, student.id, listing.id, kind):
            continue
        start = today + timedelta(days=offset)
        accommodation_repo.create_booking_request(
            BookingRequest(
                student_id=student.id,
                accommodation_id=listing.id,
                start_date=start,
                end_date=start + timedelta(days=length),
                status="declined" if kind == "declined" else "pending" if kind == "pending" else "approved",
                message=message,
            )
        )
        bookings_added += 1
    print(f"  added {reviews_added} review(s) and {bookings_added} booking(s)")


def cmd_seed(args: argparse.Namespace) -> None:
    """Insert demo users.

    bob / bobpass       (regular_user)
    admin / adminpass   (admin)
    """
    from app.database import ensure_db_and_tables, get_cli_session
    from sqlmodel import select

    from app.models.accommodation import Accommodation, BookingRequest
    from app.repositories.accommodation import AccommodationRepository
    from app.repositories.user import UserRepository
    from app.schemas.user import AdminCreate, RegularUserCreate
    from app.utilities.security import encrypt_password

    _ensure_models_loaded()
    ensure_db_and_tables()

    demo_users = [
        ("bob", "bob@example.com", "bobpass", "regular_user"),
        ("admin", "admin@example.com", "adminpass", "admin"),
        ("alice", "alice@example.com", "alicepass", "regular_user"),
        ("carmen", "carmen@example.com", "carmenpass", "regular_user"),
    ] + [(name, f"{name}@example.com", "studentpass", "regular_user") for name in _NEW_STUDENTS]

    created = 0
    skipped = 0
    with get_cli_session() as session:
        repo = UserRepository(session)
        for username, email, password, role in demo_users:
            existing_user = repo.get_by_username(username)
            if existing_user:
                if existing_user.role != role:
                    existing_user.role = role
                    session.add(existing_user)
                    session.commit()
                    print(f"  update {username} ({role})")
                else:
                    print(f"  skip  {username} (already exists)")
                    skipped += 1
                continue
            payload_cls = AdminCreate if role == "admin" else RegularUserCreate
            repo.create(
                payload_cls(
                    username=username,
                    email=email,
                    password=encrypt_password(password),
                    role=role,
                )
            )
            print(f"  create {username} ({role})")
            created += 1

        landlord = repo.get_by_username("admin")
        accommodation_repo = AccommodationRepository(session)
        if landlord:
            available_listings = accommodation_repo.list_available()
            riverside = next(
                (listing for listing in available_listings if listing.title == "Savannah Heights"),
                None,
            )
            if riverside is None:
                riverside = accommodation_repo.create(
                    Accommodation(
                        title="Savannah Heights",
                        address="12 Ariapita Avenue, Port of Spain, Trinidad",
                        description="A bright furnished apartment near Queen's Park Savannah, restaurants, and public transport.",
                        price_per_month=4800,
                        image_url="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=85",
                        status="available",
                        landlord_id=landlord.id,
                    )
                )
                print("  create Savannah Heights (accommodation)")
            elif riverside.landlord_id != landlord.id:
                riverside.landlord_id = landlord.id
                session.add(riverside)
                session.commit()
                print("  update Savannah Heights (landlord=admin)")

            student = repo.get_by_username("bob")
            if student:
                existing_completed_booking = session.exec(
                    select(BookingRequest).where(
                        BookingRequest.student_id == student.id,
                        BookingRequest.accommodation_id == riverside.id,
                        BookingRequest.status == "approved",
                    )
                ).first()
                if existing_completed_booking is None:
                    accommodation_repo.create_booking_request(
                        BookingRequest(
                            student_id=student.id,
                            accommodation_id=riverside.id,
                            start_date=date.today() - timedelta(days=60),
                            end_date=date.today() - timedelta(days=30),
                            status="approved",
                            message="I enjoyed the location and would like to share my experience.",
                        )
                    )
                    print("  create completed Savannah Heights booking (review fixture)")

            listing_specs = [
                (
                    "Maraval Garden Apartment",
                    "18 Saddle Road, Maraval, Trinidad",
                    "A secure, airy apartment close to schools, groceries, and the Port of Spain city centre.",
                    6200,
                    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=85",
                ),
                (
                    "Chaguanas Central Flat",
                    "27 Main Road, Chaguanas, Trinidad",
                    "A practical furnished flat near the town centre, markets, and major transport routes.",
                    3500,
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85",
                ),
                (
                    "San Fernando Hill View",
                    "6 Independence Avenue, San Fernando, Trinidad",
                    "A comfortable apartment with views toward San Fernando Hill and a quiet residential feel.",
                    4000,
                    "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1200&q=85",
                ),
                (
                    "Scarborough Bay Apartment",
                    "9 Milford Road, Scarborough, Tobago",
                    "A breezy apartment close to the waterfront, shops, and everyday island amenities.",
                    4500,
                    "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=85",
                ),
            ]
            listings = {listing.title: listing for listing in available_listings}
            listings.setdefault("Savannah Heights", riverside)
            for title, address, description, price_per_month, image_url in listing_specs:
                listing = session.exec(
                    select(Accommodation).where(Accommodation.title == title)
                ).first()
                if listing is None:
                    listing = accommodation_repo.create(
                        Accommodation(
                            title=title,
                            address=address,
                            description=description,
                            price_per_month=price_per_month,
                            image_url=image_url,
                            status="available",
                            landlord_id=landlord.id,
                        )
                    )
                    print(f"  create {title} (accommodation)")
                listings[title] = listing

            request_fixtures = [
                ("alice", "Maraval Garden Apartment", "I am looking for a quiet place close to my classes."),
                ("carmen", "Chaguanas Central Flat", "I would love to arrange a viewing and ask about transport links."),
                ("alice", "San Fernando Hill View", "The apartment looks like a good fit for my study schedule."),
            ]
            for username, title, message in request_fixtures:
                student = repo.get_by_username(username)
                listing = listings.get(title)
                if not student or not listing:
                    continue
                existing_request = session.exec(
                    select(BookingRequest).where(
                        BookingRequest.student_id == student.id,
                        BookingRequest.accommodation_id == listing.id,
                        BookingRequest.status == "pending",
                    )
                ).first()
                if existing_request is None:
                    accommodation_repo.create_booking_request(
                        BookingRequest(
                            student_id=student.id,
                            accommodation_id=listing.id,
                            start_date=date.today() + timedelta(days=14),
                            end_date=date.today() + timedelta(days=44),
                            status="pending",
                            message=message,
                        )
                    )
                    print(f"  create {username} request for {title}")

            _seed_extra_demo(session, repo, accommodation_repo, landlord)

    print(f"Seed done — created {created}, skipped {skipped}.")
    print("Login with bob/bobpass, admin/adminpass, or any extra student with password studentpass")


def cmd_run(args: argparse.Namespace) -> None:
    """Start the FastAPI app with Uvicorn."""
    import uvicorn

    from app.config import get_settings

    settings = get_settings()
    bind_host = args.host or settings.app_host
    bind_port = args.port or settings.app_port
    if args.reload is None:
        use_reload = settings.env.lower() != "production"
    else:
        use_reload = args.reload
    print(f"Starting FastStarter on http://{bind_host}:{bind_port} (reload={use_reload})")
    uvicorn.run(
        "app.main:app",
        host=bind_host,
        port=bind_port,
        reload=use_reload,
    )


def cmd_report(args: argparse.Namespace) -> None:
    """Build the submission package: merge judge, package transcripts, write PDF.

    Guide must (1) write ``docs/judge.md`` and (2) pull every Guide chat into
    ``docs/transcripts/*.md`` before this command. Report only packages those files.
    """
    from app.report_pdf import export_report
    from app.skill_integrity import format_report, verify

    result = export_report(
        name=args.name,
        student_id=args.student_id,
        source=None if args.src is None else Path(args.src),
        output=None if args.output is None else Path(args.output),
    )
    print()
    print("Report package:")
    print(
        f"  Judge:       {'merged docs/judge.md' if result.judge_merged else 'MISSING - Guide must run student-judge first'}"
    )
    print(
        f"  Transcripts: {result.transcript_count} chat(s) in docs/transcripts/"
        + (
            ""
            if result.transcript_count
            else " (EMPTY - Guide must pull Copilot/Cursor/OpenCode chats first)"
        )
    )
    if result.transcript_zip:
        print(f"  Zip:         {result.transcript_zip.as_posix()}")
    print(f"  PDF:         {result.pdf_path.as_posix()}")
    print(format_report(verify()))


def cmd_transcripts(args: argparse.Namespace) -> None:
    """Package agent-written markdown under docs/transcripts/ (+ zip)."""
    from app.transcript_export import package_transcripts

    result = package_transcripts(make_zip=not args.no_zip)
    if result.found == 0:
        print(
            "Warning: no chat markdown in docs/transcripts/. "
            "The Guide agent must pull every Guide chat for this project "
            "(Copilot Agent, Cursor, or OpenCode) into docs/transcripts/<slug>.md first."
        )
        raise SystemExit(2)
    print(f"Submission package ready: {result.out_dir}")
    if result.zip_path:
        print(f"Zip for submission: {result.zip_path}")


def cmd_skills_verify(args: argparse.Namespace) -> None:
    """Check course skill files against .agents/skills.lock.json."""
    from app.skill_integrity import format_report, verify

    result = verify()
    print(format_report(result))
    if not result.ok:
        raise SystemExit(1)


def cmd_usecase(args: argparse.Namespace) -> None:
    """Render docs/diagrams/use-case.json to a UML use-case PNG."""
    from app.usecase_diagram import render_usecase_png

    dest = render_usecase_png(
        spec_path=None if args.spec is None else Path(args.spec),
        output=None if args.output is None else Path(args.output),
    )
    print(f"Wrote {dest}")


def cmd_skills_lock(args: argparse.Namespace) -> None:
    """Rewrite the skill lockfile (course authors only)."""
    from app.skill_integrity import write_lock

    dest = write_lock()
    print(f"Wrote {dest}")


def cmd_users(args: argparse.Namespace) -> None:
    """List users currently in the database."""
    from sqlmodel import select

    from app.database import get_cli_session
    from app.models.user import User

    _ensure_models_loaded()
    with get_cli_session() as session:
        users = session.exec(select(User)).all()
        if not users:
            print("No users found. Run: python manage.py init")
            return
        for user in users:
            print(
                f"  id={user.id}  username={user.username}  "
                f"role={user.role}  email={user.email}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python manage.py",
        description="FastStarter Python CLI — init database, seed demo data, run the app.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser(
        "init",
        help="Create DB tables and seed demo users (drops existing tables by default)",
    )
    p_init.add_argument(
        "--no-drop",
        dest="drop",
        action="store_false",
        help="Create tables without dropping existing ones",
    )
    p_init.add_argument(
        "--no-seed",
        dest="seed",
        action="store_false",
        help="Skip demo user seed after creating tables",
    )
    p_init.set_defaults(drop=True, seed=True, func=cmd_init)

    p_seed = sub.add_parser(
        "seed",
        help="Insert demo users only (idempotent; also runs as part of init)",
    )
    p_seed.set_defaults(func=cmd_seed)

    p_run = sub.add_parser("run", help="Start the web app (uvicorn)")
    p_run.add_argument("--host", default=None, help="Bind host")
    p_run.add_argument("--port", type=int, default=None, help="Bind port")
    reload_group = p_run.add_mutually_exclusive_group()
    reload_group.add_argument(
        "--reload", dest="reload", action="store_true", default=None, help="Enable auto-reload"
    )
    reload_group.add_argument(
        "--no-reload", dest="reload", action="store_false", help="Disable auto-reload"
    )
    p_run.set_defaults(func=cmd_run, reload=None)

    p_users = sub.add_parser("users", help="List users in the database")
    p_users.set_defaults(func=cmd_users)

    p_report = sub.add_parser(
        "report",
        help=(
            "Build submission package: merge docs/judge.md, package docs/transcripts/, "
            "write docs/report.pdf (Guide pulls chats + runs student-judge first)"
        ),
    )
    p_report.add_argument("--name", required=True, help="Student name (printed on the PDF cover)")
    p_report.add_argument("--id", dest="student_id", required=True, help="Student ID (PDF only)")
    p_report.add_argument("--src", default=None, help="Markdown path (default: docs/report.md)")
    p_report.add_argument("--output", default=None, help="PDF path (default: docs/report.pdf)")
    p_report.set_defaults(func=cmd_report)

    p_transcripts = sub.add_parser(
        "transcripts",
        help="Package agent-written docs/transcripts/*.md into INDEX + zip (no IDE scrape)",
    )
    p_transcripts.add_argument(
        "--no-zip",
        action="store_true",
        help="Skip writing docs/transcripts.zip",
    )
    p_transcripts.set_defaults(func=cmd_transcripts)

    p_usecase = sub.add_parser(
        "usecase",
        help="Render docs/diagrams/use-case.json to a UML use-case PNG",
    )
    p_usecase.add_argument("--spec", default=None, help="JSON spec (default: docs/diagrams/use-case.json)")
    p_usecase.add_argument("--output", default=None, help="PNG path (default: docs/diagrams/use-case.png)")
    p_usecase.set_defaults(func=cmd_usecase)

    p_skills_verify = sub.add_parser(
        "skills-verify",
        help="Check course skills against .agents/skills.lock.json",
    )
    p_skills_verify.set_defaults(func=cmd_skills_verify)

    p_skills_lock = sub.add_parser(
        "skills-lock",
        help="Rewrite .agents/skills.lock.json (course authors; needs FASTSTARTER_SKILLS_LOCK=1)",
    )
    p_skills_lock.set_defaults(func=cmd_skills_lock)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
