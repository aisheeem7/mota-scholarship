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

Request:

{
  "student_name": "Test Student",
  "scheme_id": "TEST-SCHEME-001"
}

Response: 201 Created

{
  "id": "application-id",
  "student_name": "Test Student",
  "scheme_id": "TEST-SCHEME-001",
  "status": "SUBMITTED",
  "created_at": "2026-09-21T17:54:28.265101Z"
}

## GET /api/v1/applications/{application_id}

Purpose: Get an application by its ID.

Response: 200 OK

{
  "id": "application-id",
  "student_name": "Test Student",
  "scheme_id": "TEST-SCHEME-001",
  "status": "SUBMITTED",
  "created_at": "2026-09-21T17:54:28.265101Z"
}

Response: 404 Not Found

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

## Document Processing States

SUBMITTED
PROCESSING
COMPLETED
FAILED

## Validation

student_name: minimum 2 characters, maximum 120 characters

scheme_id: required string

Invalid request: 422 Unprocessable Entity

## CORS

Allowed local frontend origin:

http://localhost:3000

## Current Implementation

Applications are currently stored in an in-memory Python dictionary as a Day 1 stub.

Supabase/database integration will be added after the database fields and statuses are finalized.
