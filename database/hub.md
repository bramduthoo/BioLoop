## Status
- **Workstream:** Database (BioMobi)
- **Current objective:** between sessions. Two threads: **2a — phase 2 paused**, awaiting the human `DECISION` columns before the legacy-Excel load; **2b — the candidate stream register, closed 2026-09-04** and handed over as a reviewed deliverable.
- **Last session:** 2026-09-06 — register findings consolidated into the backbone (this hub, `state.md`, `flags.md`, `charter.md`). No extraction, no schema, no database touched.
- **Progress:**
  - done: phase 1 (baseline migration, verified); phase-2 workbook inspection, column→schema mapping, curation-manifest design, `load_biomobi_excel.py` written and verified against the local stack.
  - done: **2b — the candidate stream register.** Eight sources read, 801 claims, protocol settled at v2.5, pipeline reproducible, deliverables issued. See "2b — the candidate stream register" below.
  - in progress: **phase 2 (2a) — awaiting the `DECISION` columns in `database/crosswalks/`, then the real load.** Nothing is loaded into any database.
  - not started: phases 3–4 (composition harvesting, classification facets).
- **Key artifacts:**
  - `database/supabase/migrations/20260727114134_remote_schema.sql` — the baseline; schema of record. **Phase 2 required no schema change.**
  - `database/ingest/load_biomobi_excel.py` — the phase-2 loader (+ `requirements.txt`).
  - `database/crosswalks/biomobi_excel_{streams,sources,parameters}.csv` — curation manifests. **The two `DECISION` columns are unfilled.**
  - `database/data/raw/BioMobi_Biomass_RevA.xlsx` — the input. **Deliberately not versioned.**
  - `database/register/` — the candidate stream register: the corpus, its protocol (`CLAUDE.md` v2.5), the pipeline (`tools/`), the gap record (`OPEN_GAPS.md`) and the shareable deliverables. `register/README.md` is its entry point.
- **Next action:** fill the `DECISION` cells, resolve the `Sugar_beet` naming blocker, then run the loader and verify. See **"Where we are / what's next"** below. The register's own next action is not a database session — it is the source hunt, raised as **F-003**.

<!-- Everything below this line is LOCAL to the database workstream.
     The per-session narrative for 2b lives in `register/log.md`, not here. -->

## Where we are / what's next (read this first on reopening)

**State (2a):** nothing has been loaded into any database. The local stack was used for testing and then truncated back to empty. The live Supabase project is untouched. No migration was needed — the phase-1 schema absorbed the data as-is, which is itself a useful result.

**State (2b):** the candidate stream register is **closed**. It is a pre-database artifact and still populates no table; its output is a reviewed stream selection plus a gap record, both of which feed the volume half of phase 2 once 2a lands. The consolidated account is the next section.

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

**Expected result (2a)** under the proposed decisions: ~271 measurements across 5 streams, 19 sources, ~25 parameters.

---

## 2b — the candidate stream register (closed 2026-09-04)

*The consolidated account. Detail lives in `database/register/`: `README.md` (what each file is), `CLAUDE.md` (the extraction protocol, v2.5), `log.md` (the per-session record and every anomaly note), `OPEN_GAPS.md` (the gap record), `CLEANUP.md` (how the folder was closed out). The per-session narrative is **not** repeated here.*

### What it is

A standalone, claim-level corpus of Flemish agri-food side-stream figures, built for expert review. **One row = one figure exactly as one source reported it.** Contradictions are preserved, never averaged; nothing is silently dropped or harmonised; every row carries a page and a table/figure so it can be re-checked against the archived PDF in seconds.

It exists to answer one question the charter asks and BioMobi cannot answer for itself: **which Flemish agri-food side streams carry ~80% of the volume, and can that be shown rather than asserted?** It is a *pre-database* artifact — it populates no BioMobi table and is not a BioMobi input in its raw form.

### The corpus — eight sources, 801 claims

| Source | What it is | Claims | Status |
|---|---|---:|---|
| S080 | OVAM Monitor voedselverlies 2023 | 114 | **human-verified** (1 row retired by the reviewer) |
| S002 | OVAM Monitor voedselverlies 2020 | 100 | awaiting verification |
| S091 | MONBIO 4.0 (ILVO/VITO bio-economiemonitor) | 183 | awaiting verification |
| S007 | MONBIO 3.0 | 195 | awaiting verification |
| S066 | ILVO Mededeling 239 — voedselreststromen Vlaamse tuinbouw | 111 | awaiting verification |
| S065 | GeNeSys — ILVO Mededeling 165 | 98 | awaiting verification |
| S087 | OVAM Marktanalyse Biomassareststromen 2024 | **0** | read, archived, **retired — agri-food-empty** |
| S010 | ILVO/KU Leuven, verkennende haalbaarheidsstudie biomassahub | **0** | read, archived, **retired — a consolidation, every cell restates a source we already own** |

**801 claims; 736 live** after the reviewer's exclusions. The two zero-yield sources are kept deliberately: *checked and empty* must stay distinguishable from *not checked*, and every tonnage they were refused is named in `log.md` with its page and reason, so each decision is reversible without re-opening the PDF.

**Still queued:** `register/inbox/` holds **one live PDF — S004** (Monitoring Vlaanderen 2015), the chain-wide zero point of the OVAM monitor series. Four PDFs carry `_RETIRED` (S001, S005, S006, S086) — retired deliberately by the reviewer on 2026-09-04 and **not to be proposed again**; a `PhD_MvantLand_2019.pdf` sits there unregistered, with no row in the `Sources` sheet. **S003 (Monitoring Vlaanderen 2017) has no retrievable PDF, so 2017 is owned by no source** — both S080 and S002 skipped their 2017 columns to it under the cross-source restatement rule.

### The result — the 80/20 selection

Reproducible from the workbook with `node tools/select_streams.js 24`:

```
envelope   7.292.982 t/yr over 67 selectable L4/L5 streams
80%        at rank 13     90%   at rank 20     94,6%  at rank 24
```

The top of the ranking — the streams a BioMobi volume layer should hold first:

| # | Stream | t/yr | # | Stream | t/yr |
|--:|---|---:|--:|---|---:|
| 1 | Mais | 1.456.062 | 8 | Lijnzaad | 245.000 |
| 2 | Kool- en raapzaad | 857.931 | 9 | Bloemkool | 201.311 |
| 3 | Aardappel | 855.393 | 10 | Soja | 170.000 |
| 4 | Suikerbiet | 812.224 | 11 | Niet-eetbare slachtafvallen | 169.051 |
| 5 | Zetmeel | 284.549 | 12 | Dierlijk vet | 145.498 |
| 6 | Zemelen | 278.865 | 13 | Spruiten | 138.000 |
| 7 | Tarwe | 255.836 | | *(80% line)* | |

**How much of each source the selection actually resolves** — the honest measure of the corpus, and the reason the gap list exists:

| Source edition | reported residual total (L1) | resolved to selectable L4/L5 |
|---|---:|---:|
| GeNeSys ILVO 165 | 990.130 | **100,0%** |
| MONBIO 3.0 | 6.824.378 | 93,5% |
| MONBIO 4.0 | 6.249.594 | 93,0% |
| ILVO 239 tuinbouw | 282.821 | 90,8% |
| OVAM Monitor 2023 | 2.891.823 | **24,6%** |
| OVAM Monitor 2020 | 2.583.633 | **11,1%** |

The monitors carry the mass and none of the depth; ILVO's studies carry the depth. That asymmetry is structural, not a defect of the extraction — see the mechanism below.

### The method, and the four choices it rests on

Stated in the header of `tools/select_streams.js` so the ranking can be argued with:

1. **A stream is ranked by the largest tonnage any *one* source gives it — `M = max over sources`, never a sum and never a mean.** Summing across sources would double-count the same material; averaging rewarded ubiquity over mass and once ranked a 1.783 t stream above a 681.000 t one, because the sources that never measured it were being counted as zeros, which the register's own "absence = not measured" invariant says do not exist.
2. **Selection reaches L4/L5 only.** An L4 row is a named product or crop; an L3 row is a subgroup. A figure parked at L3 is invisible to any selection however large it is — which is why placement (below) turned out to matter as much as extraction.
3. **A row named `AGGREGAAT - …` is a total, not a commodity.** It never enters a sum; it becomes the reported total the level below is measured against. This is what makes a coverage percentage mean anything.
4. **Sources are never merged.** Where several report the same entry it stays several tagged rows with a spread badge. MONBIO and OVAM measure different things and **must never be summed**: on the same year 2020, MONBIO reads 5.499.135 t against OVAM's 2.583.633 t (2,1×; akkerbouw 24×, vee 5,4×, vis 38×), because MONBIO counts *productieresiduen* and OVAM only food-linked *voedselreststromen*.

### Decisions that bind any future register or volume work

Project-level ones (supply-side scope, *productie*-only, manure excluded, source-vocabulary mapping) are in `state.md`; the ones below are this workstream's.

- **The five placement rules (protocol v2.5), and why they exist.** They were learned over three review rounds and now decide whether a figure is usable at all: (1) a row naming a **product** sits at L4, never L3 — this alone accounted for 75 rows and ~17 Mt across the first four sources; (2) a **residual class of a nomenclature** (*Andere …*, *n.e.g.*, *van alle soorten*) is an aggregate, not a component; (3) a row that **totals other rows** carries the `AGGREGAAT - ` prefix, on the source's wording or on arithmetic; (4) `level_1to5` is the row's **own** commodity depth, never the level an aggregate totals; (5) a **processing product goes under its sector**, not the crop it came from — bread is not a cereal. `tools/audit_register.py` enforces all five.
- **One mislabel can move a branch by half.** `C-334`, an oilseed leftover class left unmarked at L3, was read as a *rival total for its whole branch* and averaged against `C-335`'s 1.149.000 t, giving 608.500. Marking it what it is returned **+540.500 t** — not the row's own mass, but the half of a 1,15 Mt branch that the mislabel was averaging away. **The lesson generalises: a misplacement is not a small error proportional to the row.**
- **The audit is structurally blind to one class of defect.** `audit_register.py` recognises a misplaced row from its *name* (a product code, a leftover-class phrase), so a residual row sitting at L2/L3 with an ordinary name passes every check. `tools/find_hidden_streams.py` exists for exactly that and **is not optional** on a new source.
- **251.627 t sat in the register marked unselectable the whole time.** Two meat streams (`C-298`/`C-483` *Niet-eetbare ruwe slachtafvallen*, rank 11; `C-295`/`C-480` *Eetbare slachtafvallen (rood vlees)*, rank 22) were recovered by a placement decision, not by new data. Where a name bundles two items and the bundle is itself an acceptable stream, promote it.
- **`_RETIRED` sources are not to be re-proposed** (reviewer, 2026-09-04). A recommendation to un-retire S005/S001 was rejected; every mention was removed from the gap list, and where that left a gap with no candidate, the gap now says so.
- **Reading two editions of one series side by side is what catches source errors.** S091's Tabel 34 reprints three Flemish cells verbatim from S007, one of which makes a Flemish figure larger than its Belgian parent. Neither edition alone shows this. Conversely, **an older edition is not strictly poorer**: seven Prodcom cells confidential in 2021 carry a value in 2020.
- **A source's own scope exclusions are not inherited, and a column header is not a definition.** A tonnage the source names and then excludes from its totals is still captured; a column headed *"Productie Vlaanderen"* whose text defines it as a company's multi-region output is not a Flemish figure.
- **Verification is a human gate.** Only S080 has been checked against its PDF by the reviewer. The other five extracted sources are `awaiting verification` — that is the register's largest open item, and no amount of tooling closes it.

### The two gap classes — `OPEN_GAPS.md`

The first coverage audit reported *"the food industry has no L4/L5 detail"* as one 2 Mt data gap. It was two different problems, needing opposite responses, and separating them is the gap record's main contribution:

- **Class A — hiding in the current data.** The figure is in the register but the selection cannot see it: wrong level, wrong marker, wrong parent. **No new source helps.** All class-A rows are now decided and applied; the residue is placement judgement (G-05, G-A3), not missing data.
- **Class B — not in the corpus at all.** No source the register holds measures it. **Only a new source helps.** Fifteen entries, in `crosswalks/GAP_LIST.csv`, each carrying the claim ids, the total that exists, the detail that does not, and a candidate — or an explicit *none*.

**The mechanism behind most of class B, and it is what makes the gap list actionable.** MONBIO's food-industry residual detail is exactly *the set of Prodcom product codes that happen to name a waste or by-product* (106132 gries, 110210 bostel, 108114 melasse, 101150 dierlijk vet…), plus one FEDIOL crush table. **A side stream with no such code is invisible to MONBIO however large it is** — which is why bostel and zemelen are present while whey, cacaodoppen and potato peel are absent. OVAM has the mirror-image limit: it publishes the food industry at subgroup level and nothing finer. **Hence the screening rule for any candidate source: does it carve by *process*?** A source that carves by NACE class, by Prodcom code, or by a monitor's own loss definition will reproduce the gaps the register already has — that is how they arose.

Priority order for the hunt (by how much a source would change the stream list, not by gap size): **aardappelverwerking** (621.063 t, zero components, in the sector Flanders leads — no candidate) → **zuivel/wei** (absent from all 801 claims, would likely enter the top ten on its own — no candidate) → **vlees per diersoort** → **retail + bakkerij** (S067, S025, neither with a PDF) → **cacao** and **Flemish oilseed crush**. One gap should be **fact-checked before anything is commissioned**: G-02, the PO's/veilingen stage at 15.189 t, looks too small to be true and an afternoon against VBT decides it. Raised for the literature workstream as **F-003**.

### The human gates, and what "closed" means

Everything judgement-bearing is a `;`-delimited, UTF-8-BOM CSV with a `DECISION` column, proposed by script and decided by the reviewer — the same convention as `database/crosswalks/`.

| Gate | State |
|---|---|
| `crosswalks/aggregate_coverage.csv` | **242 rows, 0 blank decisions** — what each `AGGREGAAT` row totals. The overview reads it on every build; the pipeline needs no override. |
| `crosswalks/GAP_LIST.csv` | 15 rows. A **worklist, not a decision sheet** — the input to the source hunt. |
| `crosswalks/HIDDEN_STREAMS.csv` | Not present, deliberately. Regenerate it **when a new source is extracted, not before**; a blank gate sitting there would wrongly imply open work. |
| `migrations/` | Every applied gate and its generator, kept for provenance. **Do not re-run.** |

### The checks that make the close-out a proof rather than a claim

All four reproduce from the workbook alone:

```
tools/final_check.py       PASS   801 claims, every one dispositioned into 1 of 8 buckets, 7 properties asserted
tools/verify_overview.py   8/8    arithmetic identities taken from the sources themselves
tools/audit_register.py    24 findings over 736 live claims — the known baseline, all Productievolume rows
tools/select_streams.js    7.292.982 t over 67 streams; 80% at 13, 90% at 20
```

`final_check.py` is the one that answers *"could anything still be a selectable stream that is not one?"* with evidence rather than confidence. **The whole view pipeline contains zero source names and zero claim ids** — it is a pure function of the workbook, so it cannot drift and a new source inherits no per-claim judgement.

Two things the close-out itself taught, both worth keeping: **running a kept script end-to-end is the only way to find a silent data-loss bug** (`make_aggregate_coverage.py` was dropping any reviewer-added column on every run — it erased 45 rationale paragraphs during the check, restored from git and fixed), and **a wrong tool is deleted, not archived** (`analyse.js` dropped an L4's own tonnage; keeping it would invite someone to run it).

### What happens to this when 2a lands

The register is not loaded as-is. Its hand-off into BioMobi is three separate things:

1. **The selection** decides which `stream` rows BioMobi registers first, at the grain the register settled (L4/L5, finest grain any source distinguishes).
2. **The claims** become `supply_observation` rows *after* per-claim curation — the `DECISION_expert` column is the gate, and five of the six extracted sources have not been verified yet. Contradictions stay as separate rows with separate sources; nothing is averaged on the way in.
3. **The gap record** is a harvesting worklist, not data. It belongs to the source hunt (F-003), not to a load.

Blocked on the same thing everything else is: **F-002** — no Zotero MCP is declared in `.mcp.json`, so all eight archived PDFs have a blank `citation_key`, and BioMobi's `source_key NOT NULL` will need real BBT keys before any of this loads.

---
## Scope (compressed — see `charter.md` for the full version)
Flemish **agri-food biomass side streams**, excluding manure and OFMSW. Inclusion is **expert-curated**: cast a wide but *bounded* net, then narrow. The 80/20 is a **prioritisation sort**, not a hard gate.

## Build plan (four phases)
1. **Version the schema.** — done (phase 1).
2. **Streams + canonical dictionary + volumes.** — *tackled as two parallel workstreams (2026-08-11): (2a) the loader seed, and (2b) the literature/monitor register sweep. 2b stays a pre-database artifact and populates no table until 2a is committed.*
   - *2a (in progress):* seed the old internal Excel via a committed loader. Note the scope correction: this seed exercises **6 of the 11 tables** (`source`, `unit`, `basis`, `parameter`, `stream`, `property_measurement`). The volume/geography and classification halves are **not** touched, because the workbook's only volume figures are fabricated placeholders. Earlier wording claiming this "validates the schema end-to-end" was overstated.
   - *2b (**closed 2026-09-04**):* monitors + ILVO studies → candidate stream register → 80/20 selection + gap record. **801 claims from eight sources; 67 selectable streams, 7.292.982 t envelope, 80% at 13.** It remains a standalone workbook corpus populating no table; per-claim curation (`DECISION_expert`) and DB population come after 2a lands, and need real citation keys (F-002). See "2b — the candidate stream register" above.
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
| Old internal Excel | C | file (not versioned) | **in progress (2a)** | Loader built + tested; awaiting manifest curation. Composition only — its volume figures are fabricated. |
| OVAM voedselverlies monitor | V | PDF / dashboard | **read into the register (2b)** | 2023 = S080 (verified), 2020 = S002. 2015 = S004 queued; **2017 = S003 has no PDF and is unowned**. |
| MONBIO (ILVO / VITO) | V | PDF | **read into the register (2b)** | 4.0 = S091, 3.0 = S007. 1.0/2.0 (S005/S006) **retired by the reviewer**. Carries the mass, and 93% of it resolves to L4/L5. |
| ILVO studies — Mededeling 239, GeNeSys 165 | V | PDF | **read into the register (2b)** | S066, S065. The depth the monitors lack; the tuinbouw side runs field-to-processing. |
| OVAM Marktanalyse Biomassareststromen | V | PDF | **read, retired at 0 claims** | 2024 = S087, agri-food-empty by its own afbakening. 2022/2020 (S001/S086) retired unread. |
| OVAM Inventaris Biomassa | V | PDF (non-commercial licence) | not started | Biennial; sector-aggregated. Not yet assessed against the register. |
| AgroCycle reports | R/C | PDF (downloaded) | not started | Characterisation + conversion %. |
| FoodWasteEXplorer | C | web export | not started | Try filtered export before scraping. |
| FOWCUS (2025) | C | open dataset | not started | Evaluate at phase 3. |
| Literature (gap-fill) | C | Zotero / BBT | not started | Values carry BBT citation keys. |
| **The class-B gap candidates** | V | mostly no PDF yet | **hunt not started — F-003** | 15 sectors/products in `register/crosswalks/GAP_LIST.csv`. Screening rule: **does the source carve by process?** |

*Ruled out / subsumed:* **Symbiose** (no DB access) · **Fevia** (no data) · **Noshan** (folded into FoodWasteEXplorer) · **MATIS** (regulatory reporting channel; only route is a data request to OVAM).

*The register's own source sheet is the fuller list* — `register/BIOLOOP_streams_and_sources.xlsx`, `Sources` tab, 91 rows with an `extraction_status` per row. This table is the database workstream's view of it.

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

*Register (2b) — carried forward now that the workstream is closed:*
- **Five of the six extracted sources have never been verified against their PDF.** Only S080 has. 687 of the 801 claims sit at `awaiting verification`, and `DECISION_expert` is blank on almost all of them. **This is the register's largest open item and no tooling closes it.** Decide whether verification happens per source before the claims are loaded, or as a curation pass at load time.
- **What grain does a register claim become in BioMobi?** The register's L4/L5 is the finest grain any source distinguishes, which is the hub's own canonical-grain rule — but three of the top four L4 rows **bundle two physically unrelated streams** (Suikerbiet = loof + pulp; Aardappel = loof + industrieel; Kool- en raapzaad = stro VL + schroot BE). The register's answer was "one item, reported at its lowest detail level"; BioMobi will need them **split into separate `stream` rows**, and the split needs a source that measures the halves.
- **Two of the largest streams are Belgian figures, not Flemish** (G-06: the oilseed-meal block, ~1,15–1,31 Mt, including the corpus's #2 entry). The register captured them honestly as `geography = Belgie`. BioMobi must decide whether a Belgian figure may stand as a Flemish stream volume, or whether those streams enter with no volume until a Flemish figure exists.
- **The same crop can carry two incompatible quantities** (G-08): GeNeSys measures *oogstresten* where ILVO 239 measures *voedselreststromen*, collapsing one crop name into one stream with spreads up to 50,5×. Two measurements of different material, not a contradiction — but BioMobi needs the fraction marked, or it will look like one.
- **`Varia` sector aggregates are parented away from their components** (G-05, G-A3, ~1,07 Mt of aggregate). A placement decision, not missing data — `Granen` currently mixes field residue with mill and brewery residue.
- **Is the OVAM Inventaris Biomassa worth reading into the register at all?** It is still `not started` in the source table, but the mechanism above predicts it carves the way OVAM's monitors do — sector-aggregated, no L4. Check before spending a session on it.
- **S003 (Monitoring Vlaanderen 2017) has no retrievable PDF — 2017 is unowned.** Both S080 and S002 skipped their 2017 columns to it under the cross-source restatement rule, but S003 is not in `inbox/`. Either source it, or decide that the next series edition captures 2017 too. Concretely recoverable from the archived S002 PDF: Tabel 12 (visserij) and Tabel 13 (aanvoer + opgehouden per vissoort) both carry a full 2017 column.
- **`register/inbox/PhD_MvantLand_2019.pdf` is unregistered** — no `S0xx` row, no decision. Either give it a `Sources` row or remove it.

*Phase 2 (2a) and general:*
- ~~**Is compound animal feed (mengvoeder) in scope?**~~ — **resolved 2026-08-17: it is not a rule.**
  The reviewer marked S091's BFA mengvoeder block `NO` (C-384…C-390) because **mengvoeder was
  irrelevant for that source**, not because compound feed is out of scope for the register. **Do not
  generalise the rejection**: keep capturing feed production where a source reports it, and leave the
  disposition to `DECISION_expert` per source. S007's block (C-577…C-583) is captured and unmarked,
  which is correct.
- **Belgian figures where a Flemish one exists — the two beer rows.** The reviewer also marked
  S091's C-393 and C-394 `NO`. Protocol v2.3 now forbids capturing such rows in future, and the
  S007 twins (C-586, C-587) carry a cross-reference so they can be retired the same way; they were
  left unmarked because `DECISION_expert` is the human gate.
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

*Last updated: 2026-09-06.*
