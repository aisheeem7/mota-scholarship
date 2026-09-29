# Database Contract

The source of truth is `supabase/migrations/`. This document explains the schema. Where the two differ, the migrations are authoritative.

## Tables

| Table | Purpose |
|---|---|
| `students` | Applicant record (name, date of birth, category) |
| `applications` | One scholarship application per student and scheme, with workflow status and risk score |
| `documents` | Metadata, OCR status and OCR text for each uploaded document |
| `validations` | One row per rule evaluated for an application |
| `student_document_matches` | Cross-document field comparison results |
| `workflow_events` | Audit trail of every status transition |
| `dbt_mock_transactions` | Demonstration Direct Benefit Transfer record, one per application |

All tables use UUID primary keys, foreign keys and timestamps. Row Level Security is enabled on every table.

## Constrained Fields

These constraints are enforced in the database with CHECK constraints and mirrored in `services/api/app/schemas/`.

### `applications.scheme_id`

`PRE_MATRIC | POST_MATRIC | TOP_CLASS | NATIONAL_FELLOWSHIP | NATIONAL_OVERSEAS`

### `applications.status`

`SUBMITTED | PROCESSING | APPROVED | DEFICIENT | RESUBMITTED | FLAGGED_FOR_REVIEW | ADMIN_REVIEW | REJECTED`

- `ADMIN_REVIEW` supports the review workflow `FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> officer decision` (migration `20260924000001_admin_review_status.sql`).
- DBT state is deliberately **not** an application status. An application's lifecycle and its downstream transfer state are kept separate (see `dbt_mock_transactions`).

### `applications.risk_score`

Integer from 0 to 100 inclusive, nullable. It is a prototype review-priority value, not an official fraud threshold.

### `documents.document_type`

`INCOME_CERTIFICATE | CASTE_CERTIFICATE | ACADEMIC_RECORD | IDENTITY_DOCUMENT` (migration `20260925000002_document_type_check.sql`).

This is **prototype configuration, not official MoTA policy**. The project handbook defines no official per-scheme list of required documents. These four types come from the handbook's demonstration scenario. Per-scheme requirements live in `config/schemes.json`, not in the database.

### `documents.ocr_status`

`PROCESSING | READABLE | UNREADABLE | PARTIALLY_READABLE`

### `validations.passed`

Nullable boolean (migration `20260924000002_validations_passed_nullable.sql`):

| Value | Meaning |
|---|---|
| `true` | Evaluated and passed |
| `false` | Evaluated and failed |
| `NULL` | Not evaluable, because the evidence is missing or unreadable |

### `validations.severity`

`NONE | LOW | MEDIUM | HIGH`

### `student_document_matches.match_status`

`NULL | EXACT_MATCH | HARMLESS_VARIANT | CONFLICT`. `NULL` is the intended state before evaluation, when the row exists but matching has not run yet.

### `dbt_mock_transactions`

| Column | Notes |
|---|---|
| `id` | Primary key |
| `application_id` | `UNIQUE`, foreign key to `applications(id)` with `ON DELETE CASCADE`, so there is one transaction per application |
| `status` | `PENDING \| SUCCESS \| FAILED` |
| `transaction_id`, `amount`, `created_at` | Transaction details |

Read by `GET /api/v1/applications/{application_id}/dbt-transaction`, which returns 200 with the row or 404 when no row exists.

## Composite Integrity

`student_document_matches.left_document_id` and `right_document_id` each have a composite foreign key against `documents(id, application_id)`. Both documents must therefore belong to the same `application_id` as the match row, so a match row cannot mix documents from different applications. This was verified against Supabase with negative-case inserts.

## Storage

- Bucket: `application-documents`, **private** (`public = false`).
- Document files are never stored in PostgreSQL. Only metadata is stored: `storage_path`, `document_type`, `ocr_status`, `ocr_text` and `embedding`.
- Path convention: `applications/{application_id}/{document_id}-{document_type}.{ext}`
  - The `application_id` prefix keeps an application's documents together, so they are cheap to list and scope.
  - `document_id` keeps names unique when a document type is uploaded again on resubmission.
  - `document_type` keeps paths readable for debugging.

## Access Model

- **Row Level Security is enabled on all tables with no policies yet.** This denies all access by default until the student and officer authentication model is in place (see `20260921000002_rls_draft.sql` for the intended policy for each table).
- The **backend uses the Supabase service-role key**, which bypasses RLS and is the intended server-side credential. It is configured through `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `services/api/.env`.
- The **service-role key must never be exposed to the frontend.** The web application talks only to the FastAPI backend and holds no Supabase credentials.

The backend client is created once and injected as a FastAPI dependency (`services/api/app/core/supabase_client.py`):

```python
@lru_cache
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
```

`validations` is indexed on `application_id` (`idx_validations_application_id`).

## Planned

- Role-based RLS policies once authentication is added.
- Signed, time-limited URLs so officers can view original documents without the frontend ever receiving a raw storage path.
