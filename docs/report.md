<!-- student-build:skill-integrity
status: pass
root: e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb
expected_root: e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb
mismatches: none
-->

# COMP 3613 Assignment 1

Draft this file with the Guide. **Update it after every phase milestone** before you pause. The use-case diagram is a UML PNG at `docs/diagrams/use-case.png`, linked from this file as `diagrams/use-case.png` (path relative to `docs/report.md`). The model diagram is Mermaid. **Embed wireframe images** as `wireframes/<file>` (files live in `docs/wireframes/`).

Do not put your student ID in this file if you will commit it. The PDF cover adds your name and ID at export time.

## Assigned project

Student Accommodation

## Three workflows

### 1. Search and request accommodation (Student)

### 2. Review and manage booking requests (Landlord)

### 3. Review a completed stay (Student)

## Use case diagram

![Use case diagram](diagrams/use-case.png)

Student is directly associated with Search Accommodation, View Booking Status, Request Accommodation, and View Listing Details. View Listing Details is a standalone use case, not an extension. Student and Landlord share Sign In. Approve or Decline Booking Request optionally extends Review Booking Requests, so a landlord may leave a request pending. Reviewing a completed stay remains a Student use case.

## Model diagram

First draft. Update this section in Phase 5 when polish revises the model, and note what changed.

```mermaid
erDiagram
  User {
    int id PK
    string username UK
    string email UK
    string password
    string role
  }

  Accommodation {
    int id PK
    string title
    string address
    string description
    decimal price_per_month
    string image_url
    string status
    int landlord_id FK
    datetime created_at
  }

  BookingRequest {
    int id PK
    int student_id FK
    int accommodation_id FK
    date start_date
    date end_date
    string status
    text message
    datetime created_at
  }

  StayReview {
    int id PK
    string student_name
    int student_id FK
    int accommodation_id FK
    int booking_request_id FK, UK
    int rating
    text review_text
    datetime created_at
  }

  User ||--o{ BookingRequest : submits
  User ||--o{ StayReview : writes
  User ||--o{ Accommodation : owns
  Accommodation ||--o{ BookingRequest : receives
  Accommodation ||--o{ StayReview : has
  BookingRequest ||--o| StayReview : verifies
```

The implementation uses one `User` table with `role=regular_user` for students and `role=admin` or `role=landlord` for landlords. A user can submit many booking requests, each tied to one accommodation and one request window defined by start_date and end_date. Each approved booking can later become completed and receive one StayReview. Each accommodation belongs to one landlord user and may receive many requests over time. Seeded listings use remote apartment image URLs, while landlord-uploaded images are stored under `app/static/uploads`; both are represented by `image_url`. The code exposes `price_per_month`; its SQLModel column keeps the legacy physical column name `price_per_week` for existing database compatibility.

## Wireframes

### Student Accommodation wireframe set

![Student Accommodation wireframe](wireframes/COMP3613%20A1%20Wireframe.png)

This wireframe covers the core student and landlord flows: search/listing, request and booking state, landlord approval, review and completed stay feedback. It matches the project model and use-case draft closely, though the request lifecycle could be clearer at the handoff between the student’s “My Bookings” screen and the landlord “Request Details” action.

### COMP3613 A1 Wireframe

![COMP3613 A1 Wireframe](wireframes/COMP3613 A1 Wireframe.png)

## Theming

Student Accommodation uses a modern, trustworthy, and welcoming tone. The wordmark and main landing heading use Fraunces, paired with Source Sans 3 for navigation, forms, buttons, and body text. The palette uses primary burgundy `#A6192E`, pressed burgundy `#801326`, brighter accent `#C6283E`, warm background `#FAF7F5`, white cards and forms, `#222222` main text, `#666666` secondary text, and `#E5E1DE` borders.

The landing page now presents a dark-to-burgundy gradient with a large white Student Accommodation wordmark, a short welcoming introduction, a five-photo apartment carousel, and separate Create account, Student sign in, and Landlord sign in actions. Registration supports student and landlord roles, and sign-in screens enforce the selected role. Login and register pages no longer use starter branding or demo copy. Starter authentication and `/config` remain available.

## Implementation notes

### Workflow 1 — Search and request accommodation (Student)

The accommodation domain uses `Accommodation` and `BookingRequest` SQLModel tables, an accommodation repository, a service, and thin authenticated routes. Student search supports title search and sorting by newest, lowest monthly rent, highest monthly rent, and highest review rating. Listings display images, Trinidad and Tobago addresses, and TT$ monthly rent. The non-destructive `seed` command adds Tobago/Trinidad sample apartments and pending student requests; `init` resets the database and recreates the sample set.

Verification note: the student ran the app, signed in as `bob`, opened Search accommodation, and confirmed that searching works after initialization.

The request form and booking state follow the wireframe as a separate flow: search results link to an accommodation details page, the student submits start/end dates and an optional message there, and the app redirects to My Bookings with a pending status.

Verification note: the student confirmed the separate details page works, the request form submits, and the request appears in My Bookings.

Polish update: My Bookings is a responsive list showing a property thumbnail, listing/address, dates, status, and a review action for completed stays. Requests are validated for available listings and valid date order; the confirmation page shows the apartment image, address, duration, TT$ monthly rent, and pending status.

Verification note: the student confirmed search, details, booking submission, My Bookings, and booking confirmation work. Additional list sizing and review-page star interactions were polished from student feedback.

Final polish note: the authenticated sidebar was replaced with a responsive top navigation bar matching the wireframe. Landlords can manage owned properties through My Property, create/edit listings, and upload images. Uploaded images take precedence over seeded remote photos; placeholders remain as fallback.

Workflow 1 is ready for the next workflow milestone.

### Workflow 2 — Review and manage booking requests (Landlord)

The landlord review flow uses ownership-scoped repository queries and a role-protected route. Booking requests is a responsive list with All/Pending/Approved/Declined filters; All sorts newest first. Only pending requests can be opened for a decision. Approve/decline decisions are final and lead to an outcome page with listing details and the decision banner. Approved bookings can be marked complete after their end date, and remain available through View details. Landlords can clear declined requests. The `admin` account represents the landlord in the seeded dataset.

Verification note: the student confirmed the landlord summary page, request detail page, decision flow, final decision behavior, and return message all work as intended.

### Workflow 3 — Review a completed stay (Student)

The student review flow is attached to My Bookings rather than exposed as a separate navigation tab. An approved booking becomes Completed after its end date, and the booking then shows a Review stay action. The review page accepts a 1-to-5 rating and written comment, validates completed/approved ownership in the service/repository path, and enforces one review per booking with a unique database index. It displays the saved review with a Return to my bookings action. The page includes the listing image and an interactive star control.

Verification note: the student confirmed the review submission works after the existing review-table schema mismatch was corrected by restoring and populating the required student name field.

## Deployed app

Phase 6. Public Render URL (not localhost). The web service is live at this URL; direct checks returned HTTP 200 at `/` and `{"ok":true}` at `/health`. Render PostgreSQL 16 is connected, and the database reported active connections after the deployment. Marker accounts are listed below.

https://faststarter-lidu.onrender.com

## Logins

Every account a marker needs, including extra users you added. Starter accounts:

- bob / bobpass — student
- alice / alicepass — student
- carmen / carmenpass — student
- Additional demo students, all with password `studentpass`: anika.mohammed, jerome.baptiste, nadia.persad, marcus.joseph, priya.maharaj, devon.charles, shanice.williams, ravi.singh, tiana.thomas, kyle.alexander, sasha.ali, isaiah.phillip
- admin / adminpass — landlord (admin role)

## YouTube URL

## Session transcripts

Filled when the Guide builds the report: the agent writes chat markdown into `docs/transcripts/`; `python manage.py report` packages them.

Guide packaged **6** chat(s) in `docs/transcripts/` (and `docs/transcripts.zip`).

Index: [docs/transcripts/INDEX.md](transcripts/INDEX.md)

- [`phase1-copilot`](transcripts/phase1-copilot.md)
- [`phase2-copilot`](transcripts/phase2-copilot.md)
- [`phase3-copilot`](transcripts/phase3-copilot.md)
- [`phase4-copilot`](transcripts/phase4-copilot.md)
- [`phase5-copilot`](transcripts/phase5-copilot.md)
- [`phase6-copilot`](transcripts/phase6-copilot.md)

## Competency (student-judge)

Filled by Guide from the student-judge run when this report was built.

**Judged at:** 2026-10-06
**Student / session:** Student Accommodation / GitHub Copilot Guide sessions for `comp3613a1`
**Artifact:** Native Copilot chats for Phases 1–6, current `docs/report.md`, use-case sources and PNG, wireframe image, application-components diagram, and six Guide-written transcript records. Prior `docs/judge.md` ignored.
**Evidence pass:** Re-read all six project sessions from the local session store, existing transcript markdown, current report and diagrams, and current router/model implementation. Render deployment logs and current service/database status checked in this session.
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy)

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 48 |
| Awarded total | 42 / 48 |
| **Overall (avg of scored)** | **3.5 / 4** |
| Impression mark | 18 / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 4 | yes | Phases 1–4 artifacts preceded implementation; Phase 5 stayed one workflow at a time; Phase 6 followed extensive polish. Student said, “yes but dont move to workflow 2 as yet.” |
| M2 | Problem framing | 3 | yes | Student named all three `Feature (user)` workflows, chose shared Sign In and a separate View Listing Details use case, and revised the model with booking dates and a review FK. |
| M3 | Decision ownership | 4 | yes | Student steered product behavior, including “admin = landlord,” the request-details flow, role-specific sign-in, and Trinidad and Tobago listing data. |
| M4 | Artefact-before-code | 3 | yes | UML, ERD, and student wireframe are present and used. The implementation reconciles the ERD concepts with the actual role-based `User` table. |
| M5 | Verification habit | 3 | yes | Student verified each core workflow (“it works now,” “yes it works,” “This is good and works,” “that works now”) and reported concrete failures. Some final visual refinements were not separately clicked through. |
| M6 | Assignment fit | 4 | yes | Workflows follow the wireframe and layered architecture. Current routers call services; a workspace search found no inline SQL/session queries in `app/routers/`. Render app and PostgreSQL are live after polish. |
| M7 | Slice explanation | 2 | yes | Student engaged with model and thin-route checks (“its good as is,” “done”). Model placeholder markers have since been removed from `app/models/accommodation.py`; one route marker remains in `app/routers/landlord_requests.py`, and independent authorship of every snippet is not evident. |
| M8 | Prompt quality | 4 | yes | Phase-tagged prompts and focused feedback were specific, including “This works however i want this to be in another page following the wireframe.” |
| M9 | Response to pushback | 4 | yes | Student kept refining mismatches, e.g. “This messes up the site, i want the image to be to the right of the screen to fill up the empty space,” until approving the result. |
| M10 | Integrity | 4 | yes | No laundering or answer-seeking flags appeared in the six native chats. Skill-integrity status is pass. |
| M11 | Provenance continuity | 3 | yes | The same workflows, relationship choices, ERD, and wireframe carry through Phases 1–6. Copilot session records and Guide transcripts are available. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion spiral was needed; turns remained consistent and goal-directed across the phases. |

## Strengths
- Student owned all three workflows, use-case decisions, relationship changes, and wireframe-driven UI direction.
- Phase 5 included substantial implementation, student verification, and repeated workflow/model/UI polish rather than accepting the first build.
- Student reported concrete failures in search and review submission, leading to root-cause fixes.
- Phase 6 deployed the app and PostgreSQL. The final Render deployment includes the URI-masking fix and rotated database credential; demo login records were not changed.

## Gaps (priority order)
1. Snippet authorship remains partially unclear. Model placeholder markers have been removed from `app/models/accommodation.py`; a `STUDENT SNIPPET` marker remains on the landlord-requests route, and the chat does not establish independent authorship of every model snippet.
2. No automated pytest suite was collected; workflow verification is recorded as manual.
3. The YouTube presentation URL remains blank in `docs/report.md`.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Student selected Student Accommodation and named three workflows. |
| 2 | met | Student steered include/extend, shared Sign In, and use-case layout; UML source and PNG exist. |
| 3 | met | ERD exists; student requested booking dates and review-verification FK. |
| 4 | met | Student wireframe is embedded and covers all three workflows. |
| 5 | met | Theme, sequential implementation, student verification, and extensive polish are recorded. Snippet authorship remains a learning gap. |
| 6 | met | Public Render URL and marker logins are in the report; web service and PostgreSQL are live and verified. |

## Recommended next practice
- Complete one small SQLModel field and one thin route snippet in the actual files, then explain how the route reaches its service without performing persistence itself.

## Integrity note
- Clean. No paste dump, instruction override, edited course skills, or sincerity blocks were found. Skill integrity verification passed.

## Provenance flags
- None observed. Six native project chats were available: Phases 1–6.

## Sincerity log summary
- Blocks found: 0 | max round: N/A | min/mean/final confidence: N/A | trend: N/A | cleared: N/A (no suspicion protocol needed)

## Skips
- Skips: 0/3 used (from Guide record).

## Skill integrity

Course skills are hashed at export and compared to `.agents/skills.lock.json`. Do not edit `.agents/skills/`, `.cursor/skills/`, or `AGENTS.md`.

- Status: **pass**
- Root: `e84cd692d0b85eefe546385661958c27d07e8be6c5176a82012f68ccff5c8beb`
- none
