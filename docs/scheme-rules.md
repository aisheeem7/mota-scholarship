# Scheme rules — field reference

Explains every field in [`config/schemes.json`](../config/schemes.json). Policy facts here are traced to
the Team Handbook, Ch.4 "Target Schemes" and Ch.5 "Policy as Configuration". UI wording lives separately
in `config/translations/*.json` (not yet created) — this file is stable IDs and eligibility facts only.

## Stable IDs

Five schemes, locked for Day 1. Use these exact strings everywhere `scheme_id` is read or written
(`applications.scheme_id` in the DB, `ApplicationCreate.scheme_id` in the API, frontend scheme selector):

| id | name |
|---|---|
| `PRE_MATRIC` | Pre-Matric Scholarship |
| `POST_MATRIC` | Post-Matric Scholarship |
| `TOP_CLASS` | National Scholarship Scheme — Top Class |
| `NATIONAL_FELLOWSHIP` | National Fellowship Scheme |
| `NATIONAL_OVERSEAS` | National Overseas Scholarship (NOS) |

`applications.scheme_id` is currently a freeform `text` column with no check constraint (see
`supabase/migrations/20260921000001_initial_schema.sql`) — this file, not a DB enum, is the source of
truth for which IDs are valid. If we want DB-level enforcement later, add a check constraint referencing
this list explicitly rather than duplicating the values inline.

## Field meanings

- **sponsorship** — `CENTRALLY_SPONSORED` (state-administered, central funding) vs `NATIONAL`
  (centrally administered). Informational only; not currently used by the rules engine.
- **target_level** — academic stage or institution class the scheme applies to.
- **category** — applicant category the scheme is restricted to. All five schemes are ST-only per the
  handbook's project scope (Ministry of Tribal Affairs).
- **income** — `{ limit, operator }` in INR/year, or `null` if the scheme has no income test
  (`NATIONAL_FELLOWSHIP`). `operator` is always `LESS_THAN_OR_EQUAL` today; kept explicit rather than
  hard-coded `<=` so a future scheme with a different comparison doesn't need a code change.
- **benefit_components** — what the scheme pays out. Some schemes pay a single `SCHOLARSHIP` amount;
  `POST_MATRIC` pays two components (`MAINTENANCE_ALLOWANCE` + `INSTITUTIONAL_FEE`); the amounts
  themselves aren't in the handbook yet — TODO once official rulebook is supplied.
- **stipend** — fellowship-specific monthly amounts, keyed by academic stage.
- **slot_limit** — annual cap on approvals, where the scheme is quota-based rather than open-ended.
- **tracked_fields** — extra fields the rules engine must validate for that scheme beyond the common set.
- **validations_required** — which validation categories the rules engine runs for this scheme; maps to
  `validations.rule_id` rows the engine writes per application.

## Open TODOs (do not guess — confirm against official scheme material)

- `TOP_CLASS.target_level`: exact roster of the 265 premier institutes.
- `NATIONAL_OVERSEAS.slot_limit.note`: whether PVTG is a distinct `category` value or a sub-tag of `ST`.
- Exact INR amounts for `POST_MATRIC` benefit components (maintenance allowance / fee slabs).

## Handoffs

- Rule IDs (table above) → Debopriya, for `applications.scheme_id` / any future check constraint.
- This file + `config/schemes.json` → Nirmalya + Anmol for the 13:00 / 21:00 review checkpoints.
