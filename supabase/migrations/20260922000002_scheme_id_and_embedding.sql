-- Fix stale placeholder scheme_id value now that Ashmita's config is final (PR #4,
-- config/schemes.json): the seed data used NSS_TOP_CLASS before the real ID (TOP_CLASS)
-- was confirmed. Must run before the constraint below, or the constraint add fails
-- against this row.
update applications set scheme_id = 'TOP_CLASS' where scheme_id = 'NSS_TOP_CLASS';

-- Lock applications.scheme_id to the 5 finalized scheme IDs (Ashmita, PR #4;
-- confirmed on PR #2). Was freeform text with no constraint until now.
alter table applications
  add constraint applications_scheme_id_check
  check (scheme_id in ('PRE_MATRIC', 'POST_MATRIC', 'TOP_CLASS', 'NATIONAL_FELLOWSHIP', 'NATIONAL_OVERSEAS'));

-- Lock documents.embedding to the confirmed model dimension (Debopriya: text-embedding-3-small,
-- 1536-d -- "keep the model + dimension fixed across indexing and similarity search"). Was
-- dimensionless on purpose pending this confirmation.
alter table documents
  alter column embedding type vector(1536);
