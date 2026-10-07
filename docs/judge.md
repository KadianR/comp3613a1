# student-judge competency report

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
| M7 | Slice explanation | 2 | yes | Student engaged with model and thin-route checks (“its good as is,” “done”). No snippet markers remain in the current app source, but the chat records brief confirmations rather than enough explanation to establish independent authorship of each snippet. |
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
1. Snippet authorship remains partially unclear. No placeholder markers remain in the current app source, but the chat records brief confirmations and does not establish independent authorship of each required model and route snippet.
2. No automated pytest suite was collected; workflow verification is recorded as manual.

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
- Explain in your own words how one model field and the landlord requests route work together, including where persistence is performed.

## Integrity note
- Clean. No paste dump, instruction override, edited course skills, or sincerity blocks were found. Skill integrity verification passed.

## Provenance flags
- None observed. Six native project chats were available: Phases 1–6.

## Sincerity log summary
- Blocks found: 0 | max round: N/A | min/mean/final confidence: N/A | trend: N/A | cleared: N/A (no suspicion protocol needed)

## Skips
- Skips: 0/3 used (from Guide record).