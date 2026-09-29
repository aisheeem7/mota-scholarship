-- Locks student_document_matches.match_status to the agreed three-value enum
-- (agreed during schema review on PR #2).
alter table student_document_matches
  add constraint student_document_matches_match_status_check
  check (match_status is null or match_status in ('EXACT_MATCH', 'HARMLESS_VARIANT', 'CONFLICT'));

-- Schema-integrity fix from the PR #2 review:
-- left_document_id and right_document_id must both belong to the SAME
-- application_id already recorded on the match row. The individual per-column
-- FKs (documents.id) are valid independently, so without this a row could
-- reference two documents from different applications while claiming a third
-- application_id. Enforced declaratively via a composite FK against a unique
-- (id, application_id) pair on documents, preferred over application-only
-- validation.
alter table documents
  add constraint documents_id_application_id_key
  unique (id, application_id);

alter table student_document_matches
  add constraint sdm_left_document_application_fk
  foreign key (left_document_id, application_id)
  references documents (id, application_id);

alter table student_document_matches
  add constraint sdm_right_document_application_fk
  foreign key (right_document_id, application_id)
  references documents (id, application_id);
