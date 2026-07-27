## Status
- **Workstream:** Database (BioMobi)
- **Current objective:** between sessions — next session opens **phase 2** (seed the old internal Excel into the schema).
- **Last session:** 2026-07-27 — phase 1 complete: live schema baselined into a committed migration, verified schema-identical against the live project by a local `db reset`.
- **Progress:**
  - done: strategy (scope, source triage, 4-phase plan, tooling survey); phase 1 — local toolchain (Supabase CLI 2.109.1 + Docker/WSL2), `supabase init` + `link`, baseline migration, verification.
  - in progress: —
  - not started: all ingestion (phases 2–4).
- **Key artifacts:**
  - `database/CLAUDE.md` — workstream conventions / enforcement glue.
  - `database/supabase/migrations/20260727114134_remote_schema.sql` — the baseline; schema of record.
  - `database/supabase/config.toml` — local stack config; project ref `bljaqfeqkjaqvdxwbpkx`.
  - `database/ingest/`, `database/crosswalks/` — ingestion scripts + name crosswalks *(created from phase 2)*.
- **Next action:** phase 2 — seed the old internal Excel into the schema via a committed `database/ingest/` script, validating the schema end-to-end before heavier harvesting.

<!-- Everything below this line is LOCAL to the database workstream. -->

## Scope (compressed — see `charter.md` for the full version)
Flemish **agri-food biomass side streams**, excluding manure and OFMSW. Inclusion is **expert-curated**: cast a wide but *bounded* net — the union of streams named across the vault expert list, OVAM Inventaris, MONBIO, FoodWasteEXplorer/FOWCUS, and a confirming literature scan — then narrow. The 80/20 is a **prioritisation sort**, not a hard gate; the ranking basis (fresh tonnage / dry matter / value) is left open and applied as a first-pass sort, with the final call human.

## Build plan (four phases)
1. **Version the schema.** Capture the live Supabase schema into `database/supabase/migrations/`; scaffold this hub + `CLAUDE.md`. Independent of scope; unblocks everything.
2. **Streams + canonical dictionary + volumes.**
   - *First:* seed the old internal Excel into the schema (pandas) — a filled-in example that validates the schema end-to-end before heavier harvesting.
   - Then: literature review + OVAM Inventaris (+ voedselverlies monitor) + AgroCycle conversion data → candidate stream register **at side-stream grain** → expert curation (the 80/20 call) → populate `stream`, `supply_observation`, `source`, and `unit`/`basis`/`geography` as needed. Classification postponed.
3. **Composition.** Couple source names → canonical via crosswalks; ingest FoodWasteEXplorer (filtered export first), FOWCUS, AgroCycle characterisation, and gap-fill literature → `property_measurement`. Parameter catalogue registers-on-encounter.
4. **Classification facets.** Load reference vocabularies into `classification_scheme` / `classification_term` and attach via the bridge — EWC likely first (join key to OVAM/MATIS-coded volumes), plus a sector facet.

## Schema & migration changelog
*(newest first; one line per migration)*

| Migration | Date | Summary |
|-----------|------|---------|
| `20260727114134_remote_schema.sql` | 2026-07-27 | Baseline of the live schema: 11 tables (star + reference), 66 columns, 11 PKs, 16 FKs, 9 CHECKs, 21 indexes, RLS enabled on all 11. Plus one hand-added block creating PostGIS in `extensions` (see note below). |

**Baseline method (phase-1 decision, closes the local open question).** `supabase db pull` was unusable: CLI 2.109.1's new `pg-delta` diff engine returned an empty diff against an 11-table schema and reported "No schema changes found" (`LegacyDbPullInSyncError`). The fallback named in `CLAUDE.md` was used instead — `supabase db dump --linked --schema public`, i.e. `pg_dump` — which produced a faithful baseline and, being a dump rather than a diff, emitted none of the spurious `DROP EXTENSION` statements the diff path is known for. **If a future session needs a migration generated from live drift, do not trust `db pull`/`db diff` on this CLI version without checking the output is non-empty.**

One statement was added to the dump by hand: `db dump --schema public` does not emit extension DDL, but `public.geography.geom` is typed `extensions.geometry`, so the migration would fail on an empty database. The added `CREATE SCHEMA IF NOT EXISTS "extensions"` + `CREATE EXTENSION IF NOT EXISTS "postgis" WITH SCHEMA "extensions"` mirrors the live project (postgis 3.3.7 in `extensions`) and makes the migration self-contained.

**Verification (2026-07-27).** `supabase db reset` rebuilt the schema locally from the migration alone; the result was cross-checked read-only against the live project via the project-scoped MCP. Table count and names matched, as did md5 checksums over the full column signature (name/type/nullability/identity/default), every constraint definition, and every index definition.

## Source register & load status
*(tier: **V** = volume/geography · **C** = composition · **R** = reference/conversion)*

| Source | Tier | Access | Status | Notes |
|--------|:----:|--------|--------|-------|
| Old internal Excel | V/C | file | not started | Phase-2 seed + small vocab probe; small — treat as seed. |
| OVAM Inventaris Biomassa | V | PDF (non-commercial licence) | not started | Biennial; sector-aggregated; PDF extraction toolchain. |
| OVAM voedselverlies monitor | V | PDF / dashboard | not started | Food-loss volumes. |
| MONBIO (ILVO / VITO) | V | PDF | not started | Economic bio-economy monitor; volumes + stream taxonomy. |
| AgroCycle reports | R/C | PDF (downloaded) | not started | AWCB characterisation + value-chain **conversion %** (enables coarse→fine volume attribution). |
| FoodWasteEXplorer | C | web export | not started | Food→side-stream→component maps onto schema; try filtered export before scraping; per-value refs → `source`. |
| FOWCUS (2025) | C | open dataset | not started | Fresher composition supplement; evaluate at phase 3. |
| Literature (gap-fill) | C | Zotero / BBT | not started | Values carry BBT citation keys. |

*Ruled out / subsumed:* **Symbiose platform** (no DB access) · **Fevia** (no data found) · **Noshan** (composition already folded into FoodWasteEXplorer; remainder is feed-process technology, out of scope) · **MATIS** (OVAM regulatory-reporting system — its "API" is a machine-to-machine *reporting* channel for obligated firms, no research-pull; the only route to its granularity is a data request to OVAM, opportunistic and not planned around).

## Crosswalks
`database/crosswalks/<source>.csv` maps each source's stream naming to the canonical `stream.code`. Because the mapping is cross-lingual (NL canonical ↔ EN sources) and semantic (peel / pomace / pulp), it is **LLM-proposed + human-verified**, not fuzzy-string. Committed, auditable, and reused as each new source arrives.

## Design invariants (local reminders)
- Facts only — rules/transformations live in the model layers, never here.
- Composition vector = model-layer projection; BioMobi stays sparse; absence = "not measured".
- Every fact row carries a resolvable `source_key`.
- Canonical grain = the finest any source distinguishes; volumes attach **upward**.
- Register parameters/streams once; **map, never duplicate**; keep `basis` separate from `unit`.

## Open questions (local)
- **80/20 ranking basis** (fresh vs dry vs value) — resolve empirically once the register has tonnages; not a blocker.
- **Classification facet priority** — EWC-first assumed; confirm at phase 4.
- **FoodWasteEXplorer export format** (CSV / XLSX) — confirm at phase-3 kickoff.
- ~~**Baseline method** — Docker `db pull` vs `pg_dump --schema-only`~~ — resolved 2026-07-27: `db dump` (pg_dump), see the changelog note above.
- **Commit raw source data?** — `database/data/raw/BioMobi_Biomass_RevA.xlsx` (60 KB) is untracked and *not* currently ignored; root `.gitignore` has `# data/raw/` commented out. Decide at phase-2 start: committing it at this size makes the ingestion reproducible (script + input versioned together), but sets a precedent for the much larger PDFs later.
- **RLS with no policies** — all 11 tables have RLS enabled but zero policies, so `anon`/`authenticated` can read nothing despite the grants. Fine while ingestion runs server-side under `service_role`; revisit if anything ever reads BioMobi through the API.

*Last updated: 2026-07-27.*
