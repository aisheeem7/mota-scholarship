# Database contract — MoTA Scholarship (Track 3, Adrija)

Source of truth: `supabase/migrations/`. This doc explains what's there; the migrations are canonical.

## Tables

`students`, `applications`, `documents`, `validations`, `workflow_events`, `student_document_matches` — UUID PKs, FKs, timestamps. RLS enabled on all 6, zero policies yet (pending the auth model — see Day 2 open items below).

## Enums / constrained fields (DB-enforced via CHECK, mirrored in `services/api/app/schemas/`)

- `applications.scheme_id` — `PRE_MATRIC | POST_MATRIC | TOP_CLASS | NATIONAL_FELLOWSHIP | NATIONAL_OVERSEAS`
- `applications.status` — `SUBMITTED | PROCESSING | APPROVED | DEFICIENT | RESUBMITTED | FLAGGED_FOR_REVIEW | REJECTED`
  **Day 2 open item:** the project workflow spec also defines `ADMIN_REVIEW` (`FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> admin decision`) and `DBT_MOCK` (`APPROVED -> DBT_MOCK`), neither of which is in this CHECK constraint yet. `ADMIN_REVIEW` is proposed for addition. `DBT_MOCK`'s representation (status value vs. a separate `dbt_mock_transactions` table) is **not yet decided** — pending confirmation with Debopriya + Aishee (gate G7). Do not assume either shape until that's confirmed.
- `documents.ocr_status` — `PROCESSING | READABLE | UNREADABLE | PARTIALLY_READABLE`
- `validations.severity` — `NONE | LOW | MEDIUM | HIGH`
- `validations.passed` — currently `boolean not null`. **Day 2 open item:** there is no way to represent "not evaluable" (e.g. rule couldn't be checked because the evidence was missing/unreadable) without it looking like a real failure. Proposed fix: make `passed` nullable, `NULL` = not evaluable. Not yet applied — pending confirmation with Debopriya, since her `ValidationResult.passed` is currently a required `bool`.
- `student_document_matches.match_status` — `NULL | EXACT_MATCH | HARMLESS_VARIANT | CONFLICT`. `NULL` is the intentional pre-evaluation state (row exists before the matching step has run).
- `applications.risk_score` — integer, `0-100` inclusive, nullable. Prototype review-prioritization value only, not an official fraud threshold.

## Storage

Bucket: `application-documents` (private, `public = false`). Documents are never stored in Postgres — only metadata (`documents.storage_path`, `document_type`, `ocr_status`, `ocr_text`, `embedding`).

**Path convention (Day 2):** `applications/{application_id}/{document_id}-{document_type}.{ext}`
e.g. `applications/9e1e98a1-37ee-422b-9e31-69de40b371d3/3fa2c1e0-...-INCOME_CERTIFICATE.pdf`

Rationale: keyed by `application_id` first so all of an application's documents sit under one prefix (cheap to list/scope); `document_id` keeps names unique even for the same `document_type` re-uploaded on resubmission; `document_type` stays human-scannable in the path for debugging. Backend (Debopriya's upload endpoint) should generate `storage_path` this way when writing to the bucket and to the `documents` row.

Signed-URL delivery (so the frontend never gets a raw `storage_path` it can freely re-request) is **not implemented yet** — flagged by Anmol on PR #2 as a forward item, still open for Day 2/3.

## Composite integrity

`student_document_matches.left_document_id` and `right_document_id` are each constrained (via a composite FK against `documents(id, application_id)`) to belong to the same `application_id` recorded on the match row — prevents a match row from referencing documents across two different applications. Verified live against Supabase with two negative-case inserts (see PR #2 comments for the exact FK-violation evidence).

## Service-role key exposure

Checked (2026-09-22): no reference to `SUPABASE_SERVICE_ROLE_KEY` / `service_role` anywhere in `apps/web` across `main`, `feat/frontend-foundation`, or `feat/frontend-day2-contract-sync`. Only `.env.example` variable *names* exist, no values. Frontend should keep using the anon key only; service-role stays server-side (FastAPI) only.
