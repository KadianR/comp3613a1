# student-judge competency report

**Judged at:** 2026-10-06
**Student / session:** Student Accommodation / GitHub Copilot Guide sessions for `comp3613a1`
**Evidence pass:** Re-read four native GitHub Copilot Chat sessions, the current Phase 5 Guide session, current `docs/report.md`, use-case diagram source/PNG, wireframe image, and five Guide-written transcript records. Prior transcript summary was replaced because its demo accounts/tests/deployment claims did not match the workspace.
**Phases in evidence:** 1–6 (COMP 3613; Phase 5 polish, Phase 6 deploy)

### Totals
| | Count / value |
|--|--|
| Metrics on rubric | 12 (M1–M12) |
| N/A (excluded) | 0 |
| Metrics scored | 12 |
| Scoreable max | 48 |
| Awarded total | 41 / 48 |
| **Overall (avg of scored)** | **3.4 / 4** |
| Impression mark | 17 / 20 |

## Scorecard

| ID | Metric | Score / 4 | In avg | Evidence |
|----|--------|----------:|:------:|----------|
| M1 | Phase discipline | 4 | yes | Phases 1–4 artifacts preceded Phase 5; workflows were built in sequence. Student said, “yes but dont move to workflow 2 as yet.” No premature Phase 6 work. |
| M2 | Problem framing | 3 | yes | Student named three `Feature (user)` workflows, chose shared Sign In and View Listing Details relationships, and revised the ERD with date/FK requirements. |
| M3 | Decision ownership | 4 | yes | Student repeatedly owned product decisions, including “admin = landlord”, the separate request-details flow, role-specific sign-in, and Trinidad and Tobago seed data. |
| M4 | Artefact-before-code | 3 | yes | Phase 2 use-case PNG, Phase 3 ERD, and Phase 4 wireframe were present and used. The ERD was later reconciled with the implemented role-based User table. |
| M5 | Verification habit | 3 | yes | Student verified each core workflow (“it works now”, “yes it works”, “This is good and works”, “that works now”) and continued steering polish. Late visual/data refinements were not all re-verified. |
| M6 | Assignment fit | 3 | yes | Implementation follows Routes → Dependencies → Schemas → Services → Repositories → Models; routers call services, and the models/ERD align. Phase 6 remains outstanding. |
| M7 | Slice explanation | 2 | yes | Student engaged with the SQLModel and thin-route checks, but the marked model snippets were already filled by the Guide and remain marked `STUDENT SNIPPET` in source; the student confirmed rather than visibly completing those model edits. |
| M8 | Prompt quality | 4 | yes | Student prompts were phase-aware and specific, including “This works however i want this to be in another page following the wireframe” and later focused polish requests. |
| M9 | Response to pushback | 4 | yes | Student continuously refined mismatches instead of accepting the first build: “This messes up the site, i want the image to be to the right of the screen to fill up the empty space.” |
| M10 | Integrity | 4 | yes | No paste dump, answer-seeking, or instruction override observed. Student corrections were grounded in the project; `python manage.py skills-verify` passed. |
| M11 | Provenance continuity | 3 | yes | The same three workflows, use-case decisions, ERD changes, and wireframe carry through all phases. The stale transcript summary was replaced with session-backed records. |
| M12 | Sincerity trajectory | 4 | yes | No suspicion spiral was needed; turns remained consistent and goal-directed, e.g. “okay this is good.” |

## Strengths
- Strong ownership of all three workflows and repeated corrections to match the student-created wireframe.
- Sustained Phase 5 polish across search, bookings, landlord review, completed-stay review, role-aware authentication, and visual design.
- Student verified the core workflows and reported concrete failures, including search data and review submission, which led to root-cause fixes.
- ERD and model relationships were reconciled; startup and schema checks pass.

## Gaps (priority order)
1. The required SQLModel snippet was not visibly authored by the student; source still contains `STUDENT SNIPPET` markers for Accommodation status, BookingRequest status, and StayReview rating. Practice making and explaining one small model change in each workflow.
2. Phase 6 deployment is not complete: no public Render URL or deployed workflow verification is recorded.
3. The YouTube presentation URL is still blank in `docs/report.md`.
4. The repository has no collected pytest tests. Core workflows were manually verified, but there is no automated regression coverage; the latest property/image and landing-carousel refinements also lack an explicit student click-through note.

## Phase gate status
| Phase | Status | Note |
|-------|--------|------|
| 1 | met | Student selected Student Accommodation and named three workflows. |
| 2 | met | Use-case relationships and layout were student-steered; UML source and PNG exist. |
| 3 | met | ERD exists and student requested date-range and review-verification fields. |
| 4 | met | Student wireframe is embedded in the report and covers the three workflows. |
| 5 | met | Theme, one-workflow-at-a-time implementation, student verification, and substantial polish are recorded. Model-snippet authorship remains a learning gap. |
| 6 | not met | No public Render URL or deployed Postgres/web service is recorded. |

## Recommended next practice
- Before deployment, add a small focused test set for date validation, final landlord decisions, and one-review-per-booking; then complete a final local click-through of property image upload/edit and the landing carousel.

## Integrity note
- Clean. No laundering flags or sincerity blocks were found. Course skill integrity verification passed. An earlier transcript summary contained claims inconsistent with the current workspace; it was replaced using the available session records.

## Provenance flags
- No student-authored paste dump or instruction override observed.
- The current workspace has a Phase 5 session and four earlier Guide sessions in the local Copilot session store; the transcript index now records all five.

## Sincerity log summary
- Blocks found: 0 | max round: N/A | min/mean/final confidence: N/A | trend: N/A | cleared: N/A (no suspicion protocol needed)

## Skips
- Skips: 0/3 used (from Guide record).