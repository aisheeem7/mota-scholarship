-- Adds dbt_mock_transactions table, per Issue #6 item 4 (DBT_MOCK, frozen contract
-- confirmed by Aishee + Debopriya):
--   - separate table from applications (Option B), keyed 1:1 to an application
--     via UNIQUE(application_id) -- an application's lifecycle status and its
--     downstream DBT transfer state are deliberately not conflated
--   - status: PENDING | SUCCESS | FAILED
--   - consumed by GET /api/v1/applications/{application_id}/dbt-transaction
--     (200: application_id, status, transaction_id, amount, created_at; 404 when
--     no row exists for that application)
create table if not exists dbt_mock_transactions (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null unique references applications(id) on delete cascade,
  status text not null check (status in ('PENDING', 'SUCCESS', 'FAILED')),
  transaction_id text not null,
  amount integer not null,
  created_at timestamptz not null default now()
);

-- RLS enabled, zero policies -- matches every other table in this schema.
-- Only the service-role key can reach this table (see 20260921000002_rls_draft.sql).
alter table dbt_mock_transactions enable row level security;
