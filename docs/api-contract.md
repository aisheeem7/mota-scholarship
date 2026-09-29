# TRISETU API Contract

Version: 0.1.0

## Conventions

- **Base URL (local):** `http://localhost:8000`
- **Interactive documentation:** `http://localhost:8000/docs`
- **Format:** JSON request and response bodies. Document upload uses `multipart/form-data`.
- **Errors:** every error response has the shape `{ "detail": "<message>" }`.
- **CORS:** the allowed frontend origin is `http://localhost:3000`.

## Endpoint Summary

| Method | Endpoint | Success |
|---|---|---|
| `GET` | `/health` | 200 |
| `POST` | `/api/v1/applications` | 201 |
| `GET` | `/api/v1/applications/{application_id}` | 200 |
| `POST` | `/api/v1/applications/{application_id}/documents` | 202 |
| `GET` | `/api/v1/applications/{application_id}/documents` | 200 |
| `POST` | `/api/v1/applications/{application_id}/process` | 202 |
| `GET` | `/api/v1/applications/{application_id}/validations` | 200 |
| `POST` | `/api/v1/applications/{application_id}/resubmit` | 200 |
| `GET` | `/api/v1/applications/{application_id}/dbt-transaction` | 200 |
| `GET` | `/api/v1/admin/applications` | 200 |
| `POST` | `/api/v1/admin/applications/{application_id}/review` | 200 |

---

## Health

### `GET /health`

Checks whether the backend is running.

**200 OK**

```json
{
  "status": "ok",
  "service": "mota-scholarship-api"
}
```

---

## Applications

### The Application Object

Every application endpoint returns this shape (`ApplicationResponse`).

```json
{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "SUBMITTED",
  "risk_score": null,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-22T15:14:03Z"
}
```

`risk_score` is an integer from 0 to 100, or `null` before processing.

### `POST /api/v1/applications`

Creates a new application with status `SUBMITTED`.

**Request**

```json
{
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC"
}
```

**201 Created:** the application object.

### `GET /api/v1/applications/{application_id}`

Returns one application.

| Status | Meaning |
|---|---|
| 200 | The application object |
| 404 | `Application not found` |

---

## Documents

### `POST /api/v1/applications/{application_id}/documents`

Uploads one document for an application.

**Form fields**

| Field | Value |
|---|---|
| `document_type` | `INCOME_CERTIFICATE`, `CASTE_CERTIFICATE`, `ACADEMIC_RECORD` or `IDENTITY_DOCUMENT` |
| `file` | A PDF, JPG, JPEG or PNG file |

**202 Accepted**

```json
{
  "id": "document-id",
  "application_id": "application-id",
  "document_type": "INCOME_CERTIFICATE",
  "ocr_status": "PROCESSING"
}
```

**Errors**

| Status | Detail |
|---|---|
| 400 | `Unsupported file type` |
| 400 | `Unsupported content type` |
| 400 | `Empty file` |
| 404 | `Application not found` |

**Storage path convention:** `applications/{application_id}/{document_id}-{document_type}.{extension}` in the private `application-documents` bucket.

### `GET /api/v1/applications/{application_id}/documents`

Lists the application's documents with their OCR status, ordered by document type.

**200 OK:** an array of document objects, in the same shape as the upload response.

| Status | Meaning |
|---|---|
| 404 | `Application not found` |

---

## Processing

### `POST /api/v1/applications/{application_id}/process`

Moves the application to `PROCESSING`, records the workflow event and starts the verification pipeline as a background task. The pipeline runs OCR, extraction, eligibility rules, cross-document matching and risk scoring, then moves the application to its final status.

**Allowed starting statuses:** `SUBMITTED`, `RESUBMITTED`

| Status | Meaning |
|---|---|
| 202 | The application object with status `PROCESSING` |
| 400 | Invalid workflow transition from the current status |
| 404 | `Application not found` |

### `POST /api/v1/applications/{application_id}/resubmit`

Resubmits a deficient application. Transition: `DEFICIENT -> RESUBMITTED`, recorded as a workflow event.

| Status | Meaning |
|---|---|
| 200 | The application object with status `RESUBMITTED` |
| 400 | The application is not currently `DEFICIENT` |
| 404 | `Application not found` |

---

## Validations

### `GET /api/v1/applications/{application_id}/validations`

Returns the validation scorecard. The response is an empty array if the application has no validation records yet.

**200 OK**

```json
[
  {
    "rule_id": "INCOME",
    "passed": true,
    "extracted_value": "120000",
    "expected_condition": "Annual income must be <= 250000",
    "reasoning": "Extracted annual income satisfies the configured income condition.",
    "severity": "NONE"
  }
]
```

**Result semantics**

| `passed` | Meaning |
|---|---|
| `true` | Evaluated and passed |
| `false` | Evaluated and failed |
| `null` | Not evaluable, because the evidence is missing or unreadable |

`extracted_value`, `expected_condition`, `reasoning` and `severity` may be `null`. Severity is one of `NONE`, `LOW`, `MEDIUM` or `HIGH`.

---

## DBT (Demonstration)

### `GET /api/v1/applications/{application_id}/dbt-transaction`

Returns the mock Direct Benefit Transfer transaction for an application. The data is for demonstration and is not connected to PFMS.

**200 OK**

```json
{
  "application_id": "application-id",
  "status": "SUCCESS",
  "transaction_id": "string",
  "amount": 0,
  "created_at": "2026-09-25T00:00:00Z"
}
```

`status` is one of `PENDING`, `SUCCESS` or `FAILED`.

| Status | Meaning |
|---|---|
| 404 | `DBT transaction not found` |

---

## Administration

### `GET /api/v1/admin/applications`

Returns every application, newest first, as an array of application objects.

### `POST /api/v1/admin/applications/{application_id}/review`

Records an officer's final decision on a flagged application. A reason is required for every decision.

**Request**

```json
{
  "decision": "APPROVE",
  "reason": "All required documents and configured eligibility validations have passed."
}
```

**Decision mapping**

| Decision | Resulting Status |
|---|---|
| `APPROVE` | `APPROVED` |
| `REJECT` | `REJECTED` |
| `REQUEST_RESUBMISSION` | `DEFICIENT` |

**Workflow:** `FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> APPROVED | REJECTED | DEFICIENT`. Each transition is recorded in `workflow_events`. After a resubmission request, the student continues with `DEFICIENT -> RESUBMITTED -> PROCESSING`.

| Status | Meaning |
|---|---|
| 200 | The application object with its new status |
| 400 | Invalid workflow transition from the current status |
| 404 | `Application not found` |
| 422 | `decision` is not an allowed value, or `reason` is missing |

---

## Reference Values

### Application Statuses

`SUBMITTED`, `PROCESSING`, `APPROVED`, `DEFICIENT`, `RESUBMITTED`, `FLAGGED_FOR_REVIEW`, `ADMIN_REVIEW`, `REJECTED`

### Scheme IDs

`PRE_MATRIC`, `POST_MATRIC`, `TOP_CLASS`, `NATIONAL_FELLOWSHIP`, `NATIONAL_OVERSEAS`

### Document Types

`INCOME_CERTIFICATE`, `CASTE_CERTIFICATE`, `ACADEMIC_RECORD`, `IDENTITY_DOCUMENT`

These are prototype configuration, not an official per-scheme MoTA list.

### OCR Statuses

`PROCESSING`, `READABLE`, `UNREADABLE`, `PARTIALLY_READABLE`

### Workflow Events

Every transition is saved in `workflow_events`:

```json
{
  "application_id": "application-id",
  "from_status": "FLAGGED_FOR_REVIEW",
  "to_status": "ADMIN_REVIEW",
  "reason": "Application requires administrative review."
}
```

### PVTG Handling

PVTG is treated as a sub-tag of ST, not as a separate category. The National Overseas Scholarship allocation of 17 ST and 3 PVTG slots is kept in the scheme configuration.
