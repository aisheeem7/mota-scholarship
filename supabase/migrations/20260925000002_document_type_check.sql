-- Adds a CHECK constraint on documents.document_type, per Issue #6 item 5
-- (frozen 2026-09-25, after confirming the handbook defines
-- no official per-scheme required-documents list -- Ch.32 demo story is the
-- only source, used as a PROTOTYPE CONFIGURATION set, not official MoTA policy):
--   INCOME_CERTIFICATE | CASTE_CERTIFICATE | ACADEMIC_RECORD | IDENTITY_DOCUMENT
-- No per-scheme required-document mapping is enforced here -- that lives in
-- config/schemes.json, not the DB.
-- documents table had zero rows at the time this constraint was added, so no
-- backfill/cleanup was needed.
alter table documents add constraint documents_document_type_check
  check (document_type in ('INCOME_CERTIFICATE', 'CASTE_CERTIFICATE', 'ACADEMIC_RECORD', 'IDENTITY_DOCUMENT'));
