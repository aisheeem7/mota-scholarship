# MoTA Scholarship Management API Contract

Version: 0.1.0

## Base URL

Default local backend:

http://127.0.0.1:8000

The frontend may target a different local port through `NEXT_PUBLIC_API_URL`. The current E2E hardening run uses http://127.0.0.1:8001.

---

## GET /health

### Purpose

Check whether the backend is running.

### Response

200 OK

```json
{
  "status": "ok",
  "service": "mota-scholarship-api"
}
POST /api/v1/applications
Purpose

Create a new scholarship application.

Request
{
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC"
}
Response

201 Created

{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "SUBMITTED",
  "risk_score": null,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-22T15:14:03Z"
}
GET /api/v1/applications/{application_id}
Purpose

Get an application by its ID.

Response

200 OK

{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "SUBMITTED",
  "risk_score": null,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-22T15:14:03Z"
}
Not Found

404 Not Found

{
  "detail": "Application not found"
}
Application Statuses
SUBMITTED
PROCESSING
APPROVED
DEFICIENT
RESUBMITTED
FLAGGED_FOR_REVIEW
ADMIN_REVIEW
REJECTED
Scheme IDs
PRE_MATRIC
POST_MATRIC
TOP_CLASS
NATIONAL_FELLOWSHIP
NATIONAL_OVERSEAS
Document Types

The following document types are prototype configuration only:

INCOME_CERTIFICATE
CASTE_CERTIFICATE
ACADEMIC_RECORD
IDENTITY_DOCUMENT

No additional document types are defined by this prototype contract.

Document OCR Statuses
PROCESSING
READABLE
UNREADABLE
PARTIALLY_READABLE
POST /api/v1/applications/{application_id}/documents
Purpose

Upload a document for an application.

Accepted File Types
PDF
JPG
JPEG
PNG
Request

The request uses multipart form data.

Form field:

document_type

Allowed values:

INCOME_CERTIFICATE
CASTE_CERTIFICATE
ACADEMIC_RECORD
IDENTITY_DOCUMENT

File field:

file
Response

202 Accepted

{
  "id": "document-id",
  "application_id": "application-id",
  "document_type": "INCOME_CERTIFICATE",
  "ocr_status": "PROCESSING"
}
Unsupported File Type

400 Bad Request

{
  "detail": "Unsupported file type"
}
Unsupported Content Type

400 Bad Request

{
  "detail": "Unsupported content type"
}
Application Not Found

404 Not Found

{
  "detail": "Application not found"
}
Storage Path

Documents use the following storage-path convention:

applications/{application_id}/{document_id}-{document_type}.{extension}

The application-documents storage bucket is private.

GET /api/v1/applications/{application_id}/dbt-transaction
Purpose

Get the mock DBT transaction associated with an application.

Response

200 OK

{
  "application_id": "application-id",
  "status": "string",
  "transaction_id": "string",
  "amount": 0,
  "created_at": "2026-09-25T00:00:00Z"
}
DBT Transaction Statuses
PENDING
SUCCESS
FAILED
Not Found

404 Not Found

Returned when no DBT transaction exists for the application.

{
  "detail": "DBT transaction not found"
}
GET /api/v1/applications/{application_id}/validations
Purpose

Get the validation results for an application.

Response

200 OK

[
  {
    "rule_id": "RULE_001",
    "rule_name": "Example Rule",
    "passed": true,
    "extracted_value": "120000",
    "expected_condition": "Income evidence provided",
    "reasoning": "Income certificate was readable",
    "severity": "NONE"
  }
]
Empty Validation List

If the application has no validation records, the endpoint returns:

[]
Validation Result Semantics

passed=true means the validation was evaluated and passed.

passed=false means the validation was evaluated and failed.

passed=null means the validation could not be evaluated because required evidence is missing or unreadable.

extracted_value, expected_condition, reasoning, and severity may be null.

Validation Severity
NONE
LOW
MEDIUM
HIGH

The current database contract does not define a separate NOT_EVALUABLE state or a validation document_id.

PVTG Handling

PVTG is not represented as a separate application or student category in this prototype.

PVTG is treated as a sub-tag of ST.

The NOS allocation of 17/3 is preserved in scheme configuration.

CORS

Allowed local frontend origin:

http://localhost:3000

Current Implementation

Applications are now persisted through Supabase.

The backend uses the Supabase service-role client server-side for database access.

Document uploads are stored in the private application-documents storage bucket, with document metadata recorded in the documents table.

The DBT endpoint reads from the dbt_mock_transactions table.

The validation endpoint reads validation records from the validations table.

Document upload stores files and metadata; processing is started explicitly with POST /api/v1/applications/{application_id}/process. The processing pipeline then runs OCR, configured extraction, deterministic validation, cross-document matching, risk calculation, and workflow transitions.
---

## POST /api/v1/applications/{application_id}/process

### Purpose

Start document processing for an application.

The endpoint moves the application into `PROCESSING`, records the workflow event, and starts the OCR/AI processing pipeline.

### Allowed Starting Statuses

- SUBMITTED
- RESUBMITTED

### Response

202 Accepted

```json
{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "PROCESSING",
  "risk_score": null,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-26T12:00:00Z"
}
Invalid Workflow Transition

400 Bad Request

Returned when processing is requested from a status that does not allow transition to PROCESSING.

POST /api/v1/applications/{application_id}/resubmit
Purpose

Resubmit an application after it has been marked DEFICIENT.

Workflow Transition
DEFICIENT -> RESUBMITTED

A workflow event is persisted for the transition.

Response

200 OK

{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "RESUBMITTED",
  "risk_score": 20,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-26T12:10:00Z"
}
Invalid Workflow Transition

400 Bad Request

Returned when the application is not currently DEFICIENT.

POST /api/v1/admin/applications/{application_id}/review
Purpose

Allow an administrator to make a final decision on an application that has been flagged for review.

Request
{
  "decision": "APPROVE",
  "reason": "All required documents and configured eligibility validations have passed."
}
Allowed Decisions
APPROVE
REJECT
REQUEST_RESUBMISSION

The reason field is required for every decision.

Decision Mapping
Decision	Resulting Status
APPROVE	APPROVED
REJECT	REJECTED
REQUEST_RESUBMISSION	DEFICIENT
Workflow

For a flagged application:

FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> APPROVED
FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> REJECTED
FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> DEFICIENT

Each workflow transition is persisted in workflow_events.

REQUEST_RESUBMISSION does not introduce a new application status.

After a resubmission request, the student may use:

DEFICIENT -> RESUBMITTED -> PROCESSING
Response

200 OK

The response uses the standard ApplicationResponse schema.

{
  "id": "application-id",
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC",
  "status": "APPROVED",
  "risk_score": 0,
  "created_at": "2026-09-22T15:14:03Z",
  "updated_at": "2026-09-26T12:20:00Z"
}
Invalid Workflow Transition

400 Bad Request

Returned when the application cannot transition from its current status to ADMIN_REVIEW or when an administrator attempts a decision from a status that does not allow that decision.

Validation Error

422 Unprocessable Entity

Returned when:

decision is not one of the allowed values.
reason is missing.
Workflow Event Persistence

Workflow transitions are recorded in the workflow_events table.

Each event contains:

{
  "application_id": "application-id",
  "from_status": "FLAGGED_FOR_REVIEW",
  "to_status": "ADMIN_REVIEW",
  "reason": "Application requires administrative review."
}

No separate database table is required for administrator review.