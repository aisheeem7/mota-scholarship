# Database contract — MoTA Scholarship (Track 3, Adrija)

Source of truth: `supabase/migrations/`. This doc explains what's there; the migrations are canonical.

## Tables

`students`, `applications`, `documents`, `validations`, `workflow_events`, `student_document_matches`, `dbt_mock_transactions` — UUID PKs, FKs, timestamps. RLS enabled on all 7, zero policies yet (pending the auth model — see Day 2 open items below).

## Enums / constrained fields (DB-enforced via CHECK, mirrored in `services/api/app/schemas/`)

- `applications.scheme_id` — `PRE_MATRIC | POST_MATRIC | TOP_CLASS | NATIONAL_FELLOWSHIP | NATIONAL_OVERSEAS`
- `applications.status` — `SUBMITTED | PROCESSING | APPROVED | DEFICIENT | RESUBMITTED | FLAGGED_FOR_REVIEW | REJECTED | ADMIN_REVIEW`
  `ADMIN_REVIEW` added 2026-09-24 (migration `20260924000001_admin_review_status.sql`), per Issue #6 item 2 — confirmed by Debopriya (her `ApplicationStatus` Pydantic enum updated in the same coordination window, API tests 6/6 passing) and Aishee. Workflow: `FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> admin decision`.
  **`DBT_MOCK` — resolved 2026-09-25 (migration `20260925000001_dbt_mock_transactions.sql`), per Issue #6 item 4.** Frozen by Aishee, confirmed by Debopriya: kept as a **separate table**, not an `applications.status` value — an application's lifecycle status and its downstream DBT transfer state are not conflated.
  - New table `dbt_mock_transactions`: `id` (PK), `application_id` (`UNIQUE`, FK -> `applications(id)` on delete cascade — one transaction per application), `status` (`PENDING | SUCCESS | FAILED`), `transaction_id`, `amount`, `created_at`. RLS enabled, zero policies (matches every other table).
  - Consumed by `GET /api/v1/applications/{application_id}/dbt-transaction` — 200 returns `application_id, status, transaction_id, amount, created_at`; 404 when no row exists for that application. Debopriya to align the FastAPI schema/endpoint against this shape.
- `documents.ocr_status` — `PROCESSING | READABLE | UNREADABLE | PARTIALLY_READABLE`
- `validations.severity` — `NONE | LOW | MEDIUM | HIGH`
- `validations.passed` — `boolean`, nullable (made nullable 2026-09-24, migration `20260924000002_validations_passed_nullable.sql`), per Issue #6 item 3 — frozen semantics, confirmed by Aishee + Debopriya (her `ValidationResult.passed` updated to `bool | None` in the same coordination window, API tests 6/6 passing):
  - `true` = evaluated and passed
  - `false` = evaluated and failed
  - `NULL` = not evaluable (evidence missing/unreadable)
- `student_document_matches.match_status` — `NULL | EXACT_MATCH | HARMLESS_VARIANT | CONFLICT`. `NULL` is the intentional pre-evaluation state (row exists before the matching step has run).
- `applications.risk_score` — integer, `0-100` inclusive, nullable. Prototype review-prioritization value only, not an official fraud threshold.
- `documents.document_type` — `INCOME_CERTIFICATE | CASTE_CERTIFICATE | ACADEMIC_RECORD | IDENTITY_DOCUMENT`, resolved 2026-09-25 (migration `20260925000002_document_type_check.sql`), per Issue #6 item 5. **PROTOTYPE CONFIGURATION, not official MoTA policy** — Ashmita confirmed the handbook (Ch.1-36) defines no official per-scheme required-documents list; these four values come from the Ch.32 demo-story narrative and were frozen as a team decision by Aishee. No per-scheme required-document mapping exists anywhere in this system — the handbook (Ch.1-36) defines none (confirmed by Ashmita, `docs/scheme-rules.md`), so `REQUIRED_DOCUMENTS` in `config/schemes.json` stays a category name only, not a per-scheme list, until an official source is supplied.

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

## Backend (FastAPI) Supabase connection

Added 2026-09-25 for Debopriya's validation-list endpoint work — `services/api` had no Supabase client/config yet, only the `supabase` package installed.

**Credential: service-role key, not anon.** Root cause: RLS is enabled on all 6 tables with zero policies (see `supabase/migrations/20260921000002_rls_draft.sql`, top comment) — that's a deny-all default until the auth model exists. The anon key can't read or write anything right now. The service-role key bypasses RLS and is explicitly the intended server-side credential per that migration's own comment: *"only the service-role key can reach these tables -- exactly what the FastAPI backend should use server-side. Never put it in Next.js client code."*

**Env vars: reuse the root `.env.example` names, don't invent new ones.**
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

**Suggested pattern** (no existing backend Supabase client to follow — this is the first one):

`services/api/app/core/config.py`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

`services/api/app/core/supabase_client.py`
```python
from functools import lru_cache

from supabase import create_client, Client

from app.core.config import settings


@lru_cache
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
```

Usage as a FastAPI dependency:
```python
from fastapi import Depends
from supabase import Client

from app.core.supabase_client import get_supabase


@router.get("/applications/{application_id}/validations")
def list_validations(application_id: str, supabase: Client = Depends(get_supabase)):
    result = (
        supabase.table("validations")
        .select("*")
        .eq("application_id", application_id)
        .execute()
    )
    return result.data
```

`validations` is already indexed on `application_id` (`idx_validations_application_id`, since Day 1) — no DB change needed for this query.

**Guardrail:** service-role key stays in `.env`, out of Git, and never crosses into `apps/web`. Same rule as the frontend exposure check above.
