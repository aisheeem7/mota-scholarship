-- Day 1 RLS draft: locks every table down (RLS on, zero policies) until the
-- team's auth model (student vs admin) is finalized. With RLS enabled and no
-- policy, only the service-role key can reach these tables -- exactly what
-- the FastAPI backend should use server-side. Never put it in Next.js client code.
--
-- Intended access per entity (draft, pending the authentication model):
--   students                  -> owning student (read own) + admin (read/write all)
--   applications               -> owning student (read own, no direct write) + admin (read/write all)
--   documents                  -> owning student (read own, no raw file access -- signed URLs only) + admin (read/write all)
--   validations                -> owning student (read own) + admin (read/write all)
--   workflow_events             -> owning student (read own) + admin (read/write all)
--   student_document_matches   -> admin only

alter table students enable row level security;
alter table applications enable row level security;
alter table documents enable row level security;
alter table validations enable row level security;
alter table workflow_events enable row level security;
alter table student_document_matches enable row level security;
