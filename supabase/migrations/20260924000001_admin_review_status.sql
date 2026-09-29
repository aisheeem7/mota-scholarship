-- Adds ADMIN_REVIEW to applications.status, per the workflow spec
-- (FLAGGED_FOR_REVIEW -> ADMIN_REVIEW -> admin decision) and Issue #6 item 2.
-- The backend ApplicationStatus Pydantic enum was updated in the same change
-- (API tests passing).
alter table applications drop constraint applications_status_check;
alter table applications add constraint applications_status_check
  check (status in ('SUBMITTED', 'PROCESSING', 'APPROVED', 'DEFICIENT', 'RESUBMITTED', 'FLAGGED_FOR_REVIEW', 'REJECTED', 'ADMIN_REVIEW'));
