-- Day 1: relational data model + vector readiness for MoTA Scholarship System.
-- Freezes the contract Debopriya's FastAPI/Pydantic layer builds against.

create extension if not exists pgcrypto with schema extensions;
create extension if not exists vector with schema extensions;

-- students -------------------------------------------------------------
create table if not exists students (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  dob date,
  category text not null,
  created_at timestamptz not null default now()
);

-- applications ------------------------------------------------------------
-- status enum mirrors the workflow state machine (handbook Ch.7)
create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references students(id) on delete cascade,
  scheme_id text not null,
  status text not null default 'SUBMITTED'
    check (status in ('SUBMITTED','PROCESSING','APPROVED','DEFICIENT',
                       'RESUBMITTED','FLAGGED_FOR_REVIEW','REJECTED')),
  risk_score integer check (risk_score is null or (risk_score between 0 and 100)),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_applications_student_id on applications(student_id);
create index if not exists idx_applications_status on applications(status);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_applications_updated_at
before update on applications
for each row execute function set_updated_at();

-- documents ----------------------------------------------------------------
-- embedding left dimensionless on purpose: confirm the exact dimension from
-- the chosen embedding model (text-embedding-3-small defaults to 1536)
-- before locking it in with an index -- not today's job.
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  document_type text not null,
  storage_path text not null,
  ocr_status text not null default 'PROCESSING'
    check (ocr_status in ('PROCESSING','READABLE','UNREADABLE','PARTIALLY_READABLE')),
  ocr_text text,
  embedding vector,
  created_at timestamptz not null default now()
);
create index if not exists idx_documents_application_id on documents(application_id);

-- validations ----------------------------------------------------------------
create table if not exists validations (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  rule_id text not null,
  passed boolean not null,
  extracted_value text,
  expected_condition text,
  reasoning text,
  severity text check (severity is null or severity in ('NONE','LOW','MEDIUM','HIGH')),
  created_at timestamptz not null default now()
);
create index if not exists idx_validations_application_id on validations(application_id);

-- workflow_events ----------------------------------------------------------------
create table if not exists workflow_events (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  from_status text,
  to_status text not null,
  reason text,
  created_at timestamptz not null default now()
);
create index if not exists idx_workflow_events_application_id on workflow_events(application_id);

-- student_document_matches ----------------------------------------------------------------
create table if not exists student_document_matches (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  left_document_id uuid not null references documents(id) on delete cascade,
  right_document_id uuid not null references documents(id) on delete cascade,
  field_name text not null,
  similarity numeric,
  match_status text,
  reasoning text,
  created_at timestamptz not null default now()
);
create index if not exists idx_sdm_application_id on student_document_matches(application_id);
