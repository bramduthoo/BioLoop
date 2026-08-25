## Status
- **Workstream:** Database (BioMobi)
- **Current objective:** **phase 2 IN PROGRESS — not finished.** Seed the legacy internal Excel into the schema. Loader is built and tested; **paused awaiting human curation of the manifests.**
- **Last session:** 2026-07-30 — inspected the workbook, agreed the mapping, built + tested an idempotent loader. No data loaded into any database yet.
- **Last session (2b):** 2026-08-17 — **review pass on S091, applied to S091 and S007 alike; protocol raised to v2.3.** No new source. The reviewer's remarks on S091 produced **six rule changes** and 44 corrected rows across both MONBIO extractions. The substantive one is **geography**: a figure sitting in a column headed *"Productie Vlaanderen"* was in fact the output of a company with sites in Flanders *and* Wallonia, so three sugar rows were re-read (only the 35%-grondgebied figure is Flemish) and the rule is now *the column header is not the definition, and where both levels exist the Flemish figure is the claim*. Also: a source's own product name saying *eetbaar*/*niet-eetbaar* now overrides a source-wide `quantity_type` default (9 rows reclassified to `voedselverlies`/`nevenstroom`); `level_1to5` is documented as a commodity-breadth label that never implies nesting; the conversion factor must be legible in Excel and its arithmetic spelled out; meaning-changing caveats belong in `stream_name_NL`; and a captured table whose cells were partly dropped must be accounted for cell by cell. Reviewer `DECISION_expert` entries were preserved untouched. No schema or database touched.
- **Previous session (2b):** 2026-08-16 — **S007 (MONBIO 3.0) extracted under protocol v2.2: 195 claims (C-398…C-592), awaiting human verification.** Same series as S091, one edition back, reference year **2020**. The four S091 scope decisions were applied unchanged and none needed revisiting, so the session was mostly mechanical — but it produced one finding that only a second edition could: **three of S091's Tabel 34 cells (C-339, C-340, C-341) are reprinted unchanged from this edition and are arithmetically impossible on S091's own data** (one Flemish figure exceeds its Belgian parent). Captured as recorded in both sources, cross-referenced on the rows, flagged for `DECISION_expert`. Also: S007's Tabel 15 TOTAAL is **not** capturable where S091's was (it spans bosbouw and landschapsbeheer); its visserij figure and text measure genuinely different things (total landing vs hoofdstroom subset, reconciling exactly via the auction withdrawals); and seven Prodcom cells confidential in 2021 carry a value here. 3 new dictionary members, 4 destination locations indexed. **The stale `extraction_status` on S005/S006 was corrected** (user decision) — both had wrongly read EXTRACTED. No schema or database touched.
- **Earlier session (2b):** 2026-08-16 — **S091 (MONBIO 4.0, ILVO/VITO bio-economiemonitor) extracted under protocol v2.2: 183 claims (C-215…C-397), awaiting human verification.** First non-OVAM source, and a very different animal: a 297-page, economy-wide biomass monitor (96 tables, 68 figures) reporting productie / import / export / aanbod and hoofdstromen / nevenstromen / productieresiduen across the whole bio-economy. Four scope decisions taken by the user at session open did most of the work — **mest excluded** (the hub's manure exclusion treated as binding on the register), **productie-only** (import/export/aanbod are not arising volumes), **MONBIO's nevenstroom *and* productieresidu both → `agri-food waste` with `type_assumed = TRUE`** (MONBIO's split is economic, not edible/inedible), and **agri-food sectors only** (bosbouw, landschapsbeheer, hout, papier, chemie, bio-energie, afvalsectoren out). Reference year **2021**, which needed no negotiation: MONBIO editions do not reprint each other's years, so S007→2020, S006→2019, S005→2018 fall out cleanly; the one overlap (the 2018 OVAM/IMJV waste tables T62–T65) was verified present in the S005 PDF and skipped. **No suspected source errors**; 5 variant readings, all from the source printing two definitions side by side. 15 new dictionary members, including a second, deliberately **overlapping** crop partition (MONBIO's own gewasgroepen) with a never-sum-across warning. 4 destination/route locations indexed. `render_log.py` gained a bug fix (bold containing an italic was left unrendered). No schema or database touched.
- **Earlier session (2b):** 2026-08-15 — **S002 (OVAM Monitor voedselverlies 2020) extracted under protocol v2.1: 100 claims (C-115…C-214), awaiting human verification.** Reference year **2020 only** (user decision at session open): S080 owns 2023 and left 2020 to this edition; the 2015 and 2017 columns were skipped for S004 and S003 and logged table-by-table. Two suspected source errors flagged with arithmetic evidence (C-193, a 1.999.983/1.999.383 digit transposition in Tabel 5; C-185, a "22.000 ton" veehouderij sentence that appears to be unrevised 2015 text). No new dictionary members were needed — the v2.1 vocabularies absorbed the source as-is. 19 destination/route locations indexed. No schema or database touched.
- **Earlier session (2b):** 2026-08-15 — **S080 extracted and human-verified the same day: 114 claims (C-001…C-114), 1 retired.** The review found no misread value, but it did find a rule error that was costing `quantity_type` data (+4 claims once fixed); it also retired one row (C-074, a source typo), re-levelled akkerbouw in the dictionary, relabelled the Belgian-ports geography, and drove **protocol v2.1** (below). PDF archived; 18 destination/route locations indexed. No schema or database touched. *(Earlier that day: protocol v2 itself was settled and the withdrawn v1 trial run of S080 — 310 claims, 2026-08-14, which captured horeca/catering and lacked per-row provenance — was discarded.)*
- **Progress:**
  - done: phase 1 (baseline migration); phase-2 workbook inspection; column→schema mapping; curation-manifest design; `load_biomobi_excel.py` written and verified against the local stack (idempotency, convergence, spot-checks all pass).
  - in progress: **phase 2 — awaiting the `DECISION` columns in `database/crosswalks/`, then the real load.**
  - in progress (2b, parallel): candidate stream register — **rebuilt in-repo** under `database/register/` (26-column `Streams` schema, three binding dictionaries, `destination_index.csv`, `inbox/` → `archive/` PDF flow, per-session `log.md` + its derived `log.html`). **Protocol at v2.3; four sources extracted — 114 claims from S080 (human-verified, 1 retired), 100 from S002, 183 from S091 and 195 from S007 (three awaiting verification). Corpus: 592 claims.** 8 verified PDFs still wait in `register/inbox/`, one source per session. Pre-database artifact; populates no table.
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

**S002 session outcome (2026-08-15), relevant to the sources still queued.** The v2.1 protocol
held up without amendment on a second source: no rule change was needed, no dictionary member was
added, and the self-check caught only one mechanical slip (a lower-case `chain_L2` value). Two
things are worth carrying forward. First, **the cross-source restatement rule did real work here** —
S002 is the middle edition of a four-edition series and roughly half its tables are 2015/2020
evolution tables; the rule kept the corpus clean, at the cost that **S003 (2017) is in the `Sources`
sheet but has no PDF and is not queued**, so 2017 stays uncaptured until that is resolved. Second,
unlike S080, **every quantity-type total in S002 is printed outside a route cross-tab**, so the
v2.1 "read by axis, not by table" correction changed nothing here — it is a monitor-specific
hazard, not a universal one.

**State (2b — candidate stream register):** a parallel workstream builds a standalone, claim-level corpus of Flemish agri-food side-stream figures for expert review — the "literature review + monitors → candidate stream register" half of build-plan step 2. Each row is one figure exactly as a source reported it; contradictions are preserved, never averaged, and nothing is silently deleted (unverifiable claims are downgraded + flagged for the user, who decides). It now lives **in the repo** at `database/register/` — `BIOLOOP_streams_and_sources.xlsx` (the only canonical copy; the older root-level file of the same name is superseded and must not be used), `dictionaries/` (three binding vocabularies), `destination_index.csv`, `inbox/` → `archive/` for verified PDFs, `log.md`, and the git-diffable `streams_export.csv`. **Corpus holds 114 claims from one source (S080), human-verified, 1 retired by the reviewer**: protocol v2 settled after the S080 trial run, extraction restarted from scratch under it, and the review then produced v2.1 (below) — 11 sources still queued in `inbox/`. Touches no schema or database.

**S007 session outcome (2026-08-16) — what a second edition of the same series is worth.** S007 is
MONBIO 3.0, one edition behind S091. The four S091 scope decisions carried over unchanged and the
reference years partitioned cleanly (2020 here, 2021 there), so almost nothing had to be decided
again. Three things are worth carrying forward:

- **Reading two editions side by side is what caught the only source error in either.** S091's
  Tabel 34 reprints three Flemish cells verbatim from S007's Tabel 82 (34.401 / 66.426 / 395.511 t)
  beside *different* Belgian quantities, and one of them makes the Flemish figure larger than its
  Belgian parent — impossible. Neither edition alone shows this. **S005 and S006 are the same series
  and should be extracted with the same comparison in mind.**
- **Editions of one series are not interchangeable, even where they look it.** S007's consolidated
  Tabel 15 carries bosbouw and landschapsbeheer rows and S091's does not, so the TOTAAL row is
  capturable in one and not the other. Its visserij figure is the hoofdstroom subset where S091's is
  the whole landing. Its Tabel 28 puts gries/griesmeel in the hoofdstromen where S091's puts it in
  the nevenstromen. Assume nothing from the sibling edition; re-derive per source.
- **Older editions are not strictly poorer.** Seven Prodcom cells confidential in 2021 carry a value
  in 2020 — bietenpulp, afvallen van zetmeelfabrieken, gebrande koffie, two juices, smoked fish and
  prepared shellfish. Confidentiality moves between editions, so a later edition does not supersede
  an earlier one even for the same product.

**S091 session outcome (2026-08-16) — the first non-OVAM source, and what it taught.** MONBIO is an
economy-wide bio-economy monitor, not a food-loss monitor, and it broke none of the v2.2 rules —
but it needed **four scope decisions the protocol does not itself settle**, all taken by the user
at session open and all likely to recur on S005/S006/S007 and on the OVAM Marktanalyse sources:

1. **Mest is out of the register**, on the strength of this hub's own "excluding manure and OFMSW"
   scope line. Roughly 23,4 Mton of 2021 animal side stream was excluded on this ground alone, so
   it is the single largest judgement in the corpus so far. Every tonnage is named in `log.md`.
2. **Only the *productie* column is a claim.** Import, export and *aanbod* (production + import −
   export, computed by the source) are not volumes arising in Flanders. This removed about
   two-thirds of MONBIO's numbers, including its richest nevenstroom table (T38, feed-industry
   input) — named in the log so a reviewer can pull it back.
3. **MONBIO's `nevenstroom` / `productieresidu` split is *economic*, not edible/inedible**, so it
   cannot be mapped onto the register's `nevenstroom`. Both map to `agri-food waste` with
   `type_assumed = TRUE`; both terms are now recorded in `quantity_type.csv`. Consequence worth
   knowing: **every** residual row in this source carries `type_assumed = TRUE` (50 of them).
4. **Agri-food sectors only** — bosbouw, landschapsbeheer, hout, papier, textiel, chemie,
   bio-energie and the afvalsectoren are not agri-food chain stages, so about half the report is out.

Two further things carry forward. **The cross-source restatement rule was nearly free here**:
unlike the OVAM series, MONBIO editions do not print evolution tables of their predecessors'
years, so S091→2021, S007→2020, S006→2019, S005→2018 partition cleanly. The one overlap — the
2018 OVAM/IMJV waste tables every edition reprints — was checked against the S005 PDF before being
skipped. And **MONBIO's crop groups are a second, overlapping partition** of the commodity
hierarchy (`Suiker- en zetmeelgewassen` straddles two existing L3s; `Groenten` straddles
openlucht/beschut). They were added as members with an explicit never-sum-across warning rather
than re-cut onto the OVAM partition, which would have been a derivation.

*(Tooling: `render_log.py` was fixed to render bold that contains an italic — it previously left
both markers raw. Protocol version unchanged.)*

**Register protocol v2.1 (2026-08-15) — from the human review of S080.** The review found **no
misread value** in 110 claims, but it did find a **rule error**: the destination/route ban had
been swallowing `quantity_type` data, because sources print the voedselverlies/nevenstroom
split as a cross-tab against a collection route. Such tables are now read **by axis, not by
table**, which recovered 4 claims here (C-111…C-114) and would have cost data on every monitor
source. The remaining fixes tighten rules where a reviewer had to catch something by hand:
- **Completeness sweep** — the self-check now walks the source's own *Tabellen*/*Figuren* index
  and accounts for every entry (captured / excluded-with-reason / no numbers). A 2020 twin of a
  captured infographic had slipped out of the log unmentioned.
- **`also_stated_in` (new 26th column)** — a figure repeated in four places is still one claim,
  captured from the most specific location, but the other locations, and cross-references
  between variant claims, now sit on the row. The reviewer had reported a captured figure as
  missing because the row gave no hint it also appeared in the synthesis chapter.
- **Canonical export order** — the sheet is read and written by column header, and
  `streams_export.csv` always follows the schema order, so a reviewer rearranging columns no
  longer produces a diff in which every row changed.
- **`stream_name_NL` must disambiguate siblings** (incl./excl., subset, definition), not just
  `source_type_label`.
- **Parallel accountings** (a national vs an EU definition of the same stream) are captured
  twice, named apart, and reconciled in the log.
- **`chain_L2` follows the measured event, not the chapter** the table sits in.
- **Cross-source restatement rule** — a series edition does not re-own figures it carries
  forward from an edition already in the `Sources` sheet; skip and log those, capture what it
  measured or revised, and capture the lot if no source owns them. Replaces the earlier,
  over-fitted "one reference year per source" wording.
- **`geography`** gained exactly one sanctioned exception: Belgian fishing ports are Flemish.
  Explicitly not generalisable.

**S080 session decisions (2026-08-15), binding on the sources still queued unless revisited:**
- **Evolution-table years belong to the edition that measured them.** For S080 that meant capturing 2023 only, leaving the 2015 and 2020 columns to S004 and S002, which are queued as their own sources. This is now generalised in the protocol as the **cross-source restatement rule** — the check is against the `Sources` sheet, not against a fixed year, so a source that genuinely measures several years keeps all of them. One documented exception was made here (a 2020-referenced correction unique to S080) — see `log.md`.
- **EU-definition `levensmiddelenafval` figures are captured** for Flemish in-scope chain links, as a parallel accounting to the Flemish monitoring figures (`source_type_label` records which definition applies). Belgian and other-region rows are not.

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

**Expected result (2b)** — *open; ask the user.* No tangible target was set because the register's goal is still undefined (how wide/exhaustive the sweep must be is an expert-curation decision). Current standing: **592 claims from four sources** — S080 (114, human-verified), S002 (100), S091 (183) and S007 (195; the last three awaiting verification). 8 verified PDFs still queued in `register/inbox/` (S001, S004, S005, S006, S010, S066, S086, S087), one source per session. **S003 (Monitoring Vlaanderen 2017) has no PDF and is not queued** — while that holds, the 2017 figures skipped from S002 and S080 belong to no source in the register.

**Register protocol v2 (2026-08-15) — settled from the S080 trial run.** The v1 output was withdrawn, not patched, because the scope change touched most rows. What changed:
- **Chain-stage scope is now explicit and gated in `chain_L2.csv` (`in_scope` column).** In: primary production, visserij, veilingen/PO's, voedingsindustrie, retail. Out: **horeca, catering, households**. An aggregate is capturable only if *every* stage it spans is in scope — which is now the stated reason the depth rule has no level 1.
- **`Streams` grew 20 → 25 columns.** Per-row provenance (`source_page`, `source_table_figure`) and per-row unit audit (`value_as_reported`, `unit_as_reported`, `conversion_factor_to_t_per_yr`, mandatory, factor must be a pure unit conversion or one the source itself supplies — never derived).
- **`destination_index.csv`** — destination / collection-route volumes are still not extracted, but every source now records *where* they live, so the metadata is findable later.
- **A source's own scope exclusions are not inherited** — a named tonnage the source excludes from its totals (slaughterhouse hides/bones, pre-harvest losses) is captured, with the source's framing kept in `source_type_label`.
- **Contradictions split two ways** — *variant readings* (captured, listed, not called errors) versus *suspected source errors* (arithmetic evidence required; captured as recorded, flagged for `DECISION_expert`).

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
- **Is compound animal feed (mengvoeder) in scope for the register? — ASK THE USER.** The reviewer
  marked the whole BFA mengvoeder block from S091 `NO` (C-384…C-390: totaal, varkens-, rundvee-,
  pluimveevoeder, andere, voormengsels, and the PRODCOM variant). The identical block from S007
  (C-577…C-583) is still unmarked, and MONBIO 1.0 and 2.0 will each carry one. The likely reason is
  double counting — mengvoeder is manufactured *from* streams the register already captures — but
  the reason was not written down, so it should not be turned into a rule by guesswork. Decide
  whether feed production is (a) out of scope entirely, (b) captured but always flagged as a
  derived product, or (c) kept as-is; then apply it to S007 and to the remaining MONBIO editions.
- **Belgian figures where a Flemish one exists — the two beer rows.** The reviewer also marked
  S091's C-393 and C-394 `NO`. Protocol v2.3 now forbids capturing such rows in future, and the
  S007 twins (C-586, C-587) carry a cross-reference so they can be retired the same way; they were
  left unmarked because `DECISION_expert` is the human gate.
- **S003 (Monitoring Vlaanderen 2017) has no retrievable PDF — 2017 is currently unowned.** Both S080 and S002 skipped their 2017 columns to it under the cross-source restatement rule, but S003 is not in `inbox/` and not queued. Either source it (so 2017 gets extracted properly) or decide that the next series edition to be extracted captures 2017 too. Concretely recoverable from the archived S002 PDF: Tabel 12 (visserij) and Tabel 13 (aanvoer + opgehouden per vissoort) both carry a full 2017 column.
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

*Last updated: 2026-08-17.*
