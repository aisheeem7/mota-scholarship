-- Makes validations.passed nullable, per Issue #6 item 3 (frozen semantics,
-- confirmed by Aishee + Debopriya):
--   true  = evaluated and passed
--   false = evaluated and failed
--   NULL  = not evaluable (evidence missing/unreadable)
-- Confirmed by Debopriya: ValidationResult.passed is updated to bool | None
-- in the same coordination window (API tests 6/6 passing).
alter table validations alter column passed drop not null;
