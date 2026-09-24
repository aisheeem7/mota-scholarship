# MoTA Scholarship Management API Contract

Version: 0.1.0

## Base URL

http://127.0.0.1:8000

## GET /health

Purpose: Check whether the backend is running.

Response: 200 OK

{
  "status": "ok",
  "service": "mota-scholarship-api"
}

## POST /api/v1/applications

Purpose: Create a new scholarship application.

### Request

{
  "student_id": "00000000-0000-0000-0000-000000000001",
  "scheme_id": "PRE_MATRIC"
}

### Response

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

## GET /api/v1/applications/{application_id}

Purpose: Get an application by its ID.

### Response

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

### Not Found

404 Not Found

{
  "detail": "Application not found"
}

## Application Statuses

SUBMITTED
PROCESSING
APPROVED
DEFICIENT
RESUBMITTED
FLAGGED_FOR_REVIEW
ADMIN_REVIEW
REJECTED

## Scheme IDs

PRE_MATRIC
POST_MATRIC
TOP_CLASS
NATIONAL_FELLOWSHIP
NATIONAL_OVERSEAS

## Document OCR Statuses

PROCESSING
READABLE
UNREADABLE
PARTIALLY_READABLE

## Validation Severity

NONE
LOW
MEDIUM
HIGH

## Validation

passed=true means validation was evaluated and passed.
passed=false means validation was evaluated and failed.
passed=null means validation could not be evaluated because required evidence is missing or unreadable.

extracted_value, expected_condition, reasoning, and severity may be null.

The current database contract does not define a separate NOT_EVALUABLE state or a validation document_id.

## CORS

Allowed local frontend origin:

http://localhost:3000

## Current Implementation

Applications are currently stored in an in-memory Python dictionary as a Day 2 development stub.

Supabase/database integration will be added after the API contract is finalized.
