-- Makes validations.passed nullable, per Issue #6 item 3 (frozen semantics):
--   true  = evaluated and passed
--   false = evaluated and failed
--   NULL  = not evaluable (evidence missing/unreadable)
-- The backend ValidationResult.passed field was updated to bool | None in the
-- same change (API tests passing).
alter table validations alter column passed drop not null;
