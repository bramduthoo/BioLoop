## Status
- **Workstream:** Database (BioMobi)
- **Current objective:** **phase 2 IN PROGRESS — not finished.** Seed the legacy internal Excel into the schema. Loader is built and tested; **paused awaiting human curation of the manifests.**
- **Last session:** 2026-07-30 — inspected the workbook, agreed the mapping, built + tested an idempotent loader. No data loaded into any database yet.
- **Last session (2b):** 2026-08-11 — parallel candidate-register workstream (see below). Read S002 (Monitor 2020) and S087 (Marktanalyse 2024) cover-to-cover in PDF and extended the standalone register. No schema or database touched.
- **Progress:**
  - done: phase 1 (baseline migration); phase-2 workbook inspection; column→schema mapping; curation-manifest design; `load_biomobi_excel.py` written and verified against the local stack (idempotency, convergence, spot-checks all pass).
  - in progress: **phase 2 — awaiting the `DECISION` columns in `database/crosswalks/`, then the real load.**
  - in progress (2b, parallel): candidate stream register — 276 claims from 13 sources (9 read cover-to-cover in PDF), held in a single live workbook + reading-guide docx + 90-source register CSV under `/mnt/user-data/outputs/`. Pre-database artifact; not yet committed to the repo.
  - not started: phases 3–4 (composition harvesting, classification facets).
- **Key artifacts:**
  - `database/supabase/migrations/20260727114134_remote_schema.sql` — the baseline; schema of record. **Phase 2 required no schema change.**
  - `database/ingest/load_biomobi_excel.py` — the phase-2 loader (+ `requirements.txt`).
  - `database/crosswalks/biomobi_excel_{streams,sources,parameters}.csv` — curation manifests. **The two `DECISION` columns are unfilled.**
  - `database/data/raw/BioMobi_Biomass_RevA.xlsx` — the input. **Deliberately not versioned** (see decisions below).
- **Next action:** fill the `DECISION` cells, resolve the `Sugar_beet` naming blocker, then run the loader and verify. See **"Where we are / what's next"** below.

<!-- Everything below this line is LOCAL to the database workstream. -->

## Where we are / what's next (read this first on reopening)

**State:** nothing has been loaded into any database. The local stack was used for testing and then truncated back to empty. The live Supabase project is untouched. No migration was needed — the phase-1 schema absorbed the data as-is, which is itself a useful result.

**State (2b — candidate stream register):** a parallel workstream builds a standalone, claim-level corpus of Flemish agri-food side-stream figures for expert review — the "literature review + monitors → candidate stream register" half of build-plan step 2. Each row is one figure exactly as a source reported it; contradictions are preserved, never averaged, and nothing is silently deleted (unverifiable claims are downgraded + flagged for the user, who decides). Currently 276 claims from 13 sources (9 read cover-to-cover in PDF). It lives in `/mnt/user-data/outputs/` (`BIOLOOP_streams_and_sources.xlsx` — single live file, no version suffix — plus the reading-guide docx and the 90-source register CSV), **not yet in the repo**, and touches no schema or database until 2a is committed.

**To finish phase 2, in order:**

1. **Fill the `DECISION` column** (`include` / `exclude`) in:
   - `database/crosswalks/biomobi_excel_streams.csv` — **5 blank cells** (8 rows pre-filled `exclude` for manure/OFMSW).
   - `database/crosswalks/biomobi_excel_sources.csv` — **19 blank cells** (7 pre-filled `exclude`).
   - `biomobi_excel_parameters.csv` needs nothing — blank means "accept the proposal".
   - The files are `;`-delimited with a UTF-8 BOM so Belgian Excel opens them in columns. The loader **refuses to run** while any cell is blank.
2. **Resolve the `Sugar_beet` blocker.** Its `proposed_code` is the placeholder `suikerbiet-REVIEW`, and the loader hard-fails on any code ending `-REVIEW` because `stream.code` is a primary key other tables will reference. Note the evidence below that this may need *splitting into two streams*, not just renaming.
3. **Decide `Pig_SH_WW`** — pig slaughterhouse wastewater. Not manure, but is a liquid effluent a BioMobi stream at all?
4. **Run it:**
   ```
   database/.venv/Scripts/python database/ingest/load_biomobi_excel.py --dry-run
   database/.venv/Scripts/python database/ingest/load_biomobi_excel.py
   ```
   (Requires the local stack up: `supabase start`. Never target the live project.)
5. **Verify**, then update this hub, `state.md`, and commit.

> **2b (parallel register) — goal still open; ASK THE USER.** No tangible completion steps could be written here because 2b has no defined end-state yet: "when is the sweep exhaustive enough / where does it hand off?" is an expert-curation scoping call, not something to hard-code. Ask the user to define the end-state (target sources, saturation rule, hand-off point) before writing concrete 2b steps. What *is* queued in the meantime: finish the remaining tier-1 sources — **S078** (MONBIO 4.0, web portal — different scraping route), **S086** (Marktanalyse ~2020, user's last priority, expected low yield), **S066** (blocked: no retrievable URL, 18 claims still inherited via S010 only; may need a direct ILVO request).

**Expected result** under the proposed decisions: ~271 measurements across 5 streams, 19 sources, ~25 parameters.

**Expected result (2b)** — *open; ask the user.* No tangible target was set because the register's goal is still undefined (how wide/exhaustive the sweep must be is an expert-curation decision). Current standing: 276 claims from 13 sources, 9 read cover-to-cover in PDF.

## Scope (compressed — see `charter.md` for the full version)
Flemish **agri-food biomass side streams**, excluding manure and OFMSW. Inclusion is **expert-curated**: cast a wide but *bounded* net, then narrow. The 80/20 is a **prioritisation sort**, not a hard gate.

## Build plan (four phases)
1. **Version the schema.** — done (phase 1).
2. **Streams + canonical dictionary + volumes.** — *tackled as two parallel workstreams (2026-08-11): (2a) the loader seed, and (2b) the literature/monitor register sweep. 2b stays a pre-database artifact and populates no table until 2a is committed.*
   - *2a (in progress):* seed the old internal Excel via a committed loader. Note the scope correction: this seed exercises **6 of the 11 tables** (`source`, `unit`, `basis`, `parameter`, `stream`, `property_measurement`). The volume/geography and classification halves are **not** touched, because the workbook's only volume figures are fabricated placeholders. Earlier wording claiming this "validates the schema end-to-end" was overstated.
   - *2b (in progress — the workstream advanced in the 2026-08-11 session):* literature review + OVAM Inventaris (+ voedselverlies monitor) + AgroCycle → candidate stream register → expert curation → populate `stream`, `supply_observation`, `source`, `unit`/`basis`/`geography`. Currently a standalone workbook corpus; curation and DB population come after 2a lands.
3. **Composition.** FoodWasteEXplorer, FOWCUS, AgroCycle, gap-fill literature → `property_measurement`.
4. **Classification facets.** EWC likely first, plus a sector facet.

## Schema & migration changelog
*(newest first; one line per migration)*

| Migration | Date | Summary |
|-----------|------|---------|
| `20260727114134_remote_schema.sql` | 2026-07-27 | Baseline of the live schema: 11 tables, 66 columns, 11 PKs, 16 FKs, 9 CHECKs, 21 indexes, RLS on all 11. Plus a hand-added PostGIS block. |

**Baseline method (phase-1).** `supabase db pull` was unusable: CLI 2.109.1's `pg-delta` engine returned an empty diff and reported "No schema changes found". `supabase db dump --linked --schema public` (pg_dump) was used instead. **Do not trust `db pull`/`db diff` on this CLI version without checking the output is non-empty.** `db dump --schema public` omits extension DDL, so the PostGIS block was added by hand.

**Verification (2026-07-27).** `supabase db reset` rebuilt the schema from the migration alone; cross-checked read-only against live via MCP — table names, md5 over full column signatures, every constraint and index definition all matched.

## Phase-2 curation manifests (the approval gate)

Ingestion is **gated on human review**, by explicit decision (2026-07-28). `database/crosswalks/biomobi_excel_*.csv` carry an LLM proposal beside a human `DECISION`; a row loads only if **both** its stream and its source are marked `include`. The loader exits non-zero listing every unreviewed row. This extends the existing crosswalk convention (LLM-proposed, human-verified) from name-mapping to *inclusion*.

`streams` / `sources` are **gates** — blank blocks the load. `parameters` is a **review** — blank means accept.

## Idempotency — the `xls-` ownership namespace

Both fact tables use `generated always as identity` PKs with no natural unique constraint, so a naive re-run duplicates everything. Adding a UNIQUE constraint was rejected: it needs a migration, the natural key is full of NULL-ables, and the workbook contains rows that are *legitimately* identical.

Instead: every source row this loader creates is prefixed **`xls-`**. Each run deletes fact rows in that namespace, then reloads, in one transaction. Verified — 3 consecutive runs held at 271 rows, and flipping a stream to `exclude` **removed** its 38 rows rather than orphaning them. Reference vocabulary (`unit`/`basis`/`parameter`/`stream`) is upserted and **never deleted**, deliberately: `stream_classification` cascades on stream delete, and an ingestion script must not be able to destroy phase-4 classification work.

Source keys are renameable to real Zotero BBT keys later — all source FKs are `ON UPDATE CASCADE`.

## Findings from the workbook (`Template_biomass`, 631 rows, 13 biomass types)

- **The `Dummy` column flags fabricated values, and it partitions the data perfectly**: zero `Dummy=Yes` rows carry a source, and all 456 rows with both a value and a source are `Dummy=No`. The schema's `source_key NOT NULL` filters out every fabricated row on its own — constraint and flag agree exactly. Strong validation of the phase-1 design.
- `year` is **empty in all 631 rows** → every measurement loads `year NULL`, `temporal_resolution='unknown'`.
- Units conflate unit and basis (`%DS`, `% (db)`, `% DS`, `g/kg DS`, `NL/kg VS`). Split on load. **Blank unit → `unknown`, not `n.a.`** — a missing unit and an inapplicable one are different claims; same reasoning as `basis='unknown'` for the 23 rows that never recorded a basis.
- 63 parameter names with heavy near-duplication. Collapsed: `Protein`/`Proteins`/`Total proteins`; `DS`/`TS`/`Total solids`; `VS`/`Volatile solids`; `Lipids/fat`/`Total lipids`. **Kept separate** (different assays): `Crude protein`, `VM`, `TN`/`TKN`/`TAN`, `sCOD`, soluble/insoluble lignin.
- Data errors carried as-recorded but reported: **pH recorded in `mg/L`** (2 rows); one `Source` cell contains `%DS` (column shift); 12 exact duplicate rows (4 in scope).
- **`Sugar_beet` DS spans 89.2–918 g/kg — a 10× range**, i.e. fresh and dried material under one name. Also `Potato_peel` DS 17.8–129 g/kg, `Pig_SH_WW` COD 1470–8627 mg/L.
- Dropped as out of scope: `Logistic` params (`a`/`alpha`/`beta` are transport cost-curve coefficients — model rule layer), `Legal` (HQFR), `Environmental` (all empty), and the `Logistic relevant` / `Dummy` / Pareto columns (judgements and derived values, not facts).
- Sheets `Streams`, `Thoughts`, `Sheet1` dropped (decision 2026-07-28). `Thoughts` holds Dutch design notes on seasonality worth a `vault/Database/` note.

## Source register & load status
*(tier: **V** = volume/geography · **C** = composition · **R** = reference/conversion)*

| Source | Tier | Access | Status | Notes |
|--------|:----:|--------|--------|-------|
| Old internal Excel | C | file (not versioned) | **in progress** | Loader built + tested; awaiting manifest curation. Composition only — its volume figures are fabricated. |
| OVAM Inventaris Biomassa | V | PDF (non-commercial licence) | not started | Biennial; sector-aggregated. |
| OVAM voedselverlies monitor | V | PDF / dashboard | not started | Food-loss volumes. |
| MONBIO (ILVO / VITO) | V | PDF | not started | Volumes + stream taxonomy. |
| AgroCycle reports | R/C | PDF (downloaded) | not started | Characterisation + conversion %. |
| FoodWasteEXplorer | C | web export | not started | Try filtered export before scraping. |
| FOWCUS (2025) | C | open dataset | not started | Evaluate at phase 3. |
| Literature (gap-fill) | C | Zotero / BBT | not started | Values carry BBT citation keys. |

*Ruled out / subsumed:* **Symbiose** (no DB access) · **Fevia** (no data) · **Noshan** (folded into FoodWasteEXplorer) · **MATIS** (regulatory reporting channel; only route is a data request to OVAM).

## Crosswalks
`database/crosswalks/<source>.csv` maps each source's naming to canonical `stream.code`, and (from phase 2) carries the human `DECISION` gate. Cross-lingual (NL canonical ↔ EN sources) and semantic (peel / pomace / pulp), so **LLM-proposed + human-verified**, never fuzzy-string.

## Design invariants (local reminders)
- Facts only — rules/transformations live in the model layers, never here.
- Composition vector = model-layer projection; BioMobi stays sparse; absence = "not measured".
- Every fact row carries a resolvable `source_key`.
- Canonical grain = the finest any source distinguishes; volumes attach **upward**.
- Register parameters/streams once; **map, never duplicate**; keep `basis` separate from `unit`.
- **Record what the source said.** Never silently harmonise units, correct errors, or drop duplicates — load as recorded and *report* the anomaly.
- **Every ingestion script is idempotent via its own source-key namespace.**

## Open questions (local)
- **`Sugar_beet` grain — BLOCKS the phase-2 load.** Beet, pulp, or tops? The 10× DS spread suggests fresh vs dried material conflated, so this may need **two** streams rather than one rename.
- **`Pig_SH_WW`** — is a liquid slaughterhouse effluent a BioMobi stream?
- **4 in-scope duplicate rows** — copy-paste artifact or two genuine agreeing measurements? Kept by default; `--dedupe` collapses them.
- **pH recorded in `mg/L`** — left as recorded. Correct in a later pass, or leave the workbook error visible?
- **Classification facet priority** — EWC-first assumed; confirm at phase 4.
- **FoodWasteEXplorer export format** — confirm at phase-3 kickoff.
- **RLS with no policies** — all 11 tables have RLS on and zero policies. Fine while ingestion runs server-side under `service_role`; revisit if anything reads BioMobi through the API.
- ~~**Baseline method**~~ — resolved 2026-07-27: `db dump` (pg_dump).
- ~~**Commit raw source data?**~~ — resolved 2026-07-28: **no.** `**/data/raw/` is gitignored.
- ~~**80/20 ranking basis**~~ — resolved 2026-07-28: **not applicable to already-collected data.** The 80/20 is a rule for *prospective* harvesting. This dataset is small and already collected, so selection is manual, per stream, checking (a) the name, to exclude manure/OFMSW, and (b) the source, to validate the entry. Hence the manifest gate.

*Last updated: 2026-07-30.*
