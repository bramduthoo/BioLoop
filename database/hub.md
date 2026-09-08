## Status
- **Workstream:** Database (BioMobi)
- **Current objective:** between sessions. **2a is abandoned** (the legacy Excel was judged unusable, 2026-09-07); **2b closed 2026-09-04**; its 80%-selection is now registered as BioMobi vocabulary.
- **Last session:** 2026-09-08 — restructured 2c on reviewer challenge: BioMobi's streams are now **20 object-grain rows under one commodity facet**, replacing 21 rows under a chain-stage facet. First data of any kind in the database.
- **Progress:**
  - done: phase 1 (baseline migration, verified).
  - done: **2b — the candidate stream register.** Eight sources read, 803 claims, protocol at v2.6, pipeline reproducible, deliverables issued; full selection control run 2026-09-08. See "2b — the candidate stream register" below.
  - done: **2c — the selection registered.** The 13 commodities carrying 80% of the envelope entered BioMobi as **20 object-grain `stream` rows** under the `bioloop-commodity` ladder (L2→L3). **Names and classification only — no volumes** (see F-002).
  - **abandoned: 2a — the legacy-Excel seed.** The workbook is not a usable input; the loader and its manifests were deleted. See "2a — abandoned" below.
  - not started: volumes (`supply_observation`), phase 3 (composition harvesting), EWC facet.
- **Key artifacts:**
  - `database/supabase/migrations/20260727114134_remote_schema.sql` — the baseline; schema of record. **Nothing since has needed a schema change.**
  - `database/streams/` — the selection → BioMobi transfer, now a generated pipeline: `tools/build_manifest.py` (register → objects) → `crosswalks/register_streams.csv` (generated, `DECISION` gate) → `tools/load_streams.py --emit-migration` → `supabase/migrations/`. The only human-owned file is `crosswalks/object_decisions.csv` (9 exception rows). **Nothing pushed to live.**
  - `database/register/` — the candidate stream register: the corpus, its protocol (`CLAUDE.md` v2.6), the pipeline (`tools/`), the gap record (`OPEN_GAPS.md`) and the shareable deliverables. `register/README.md` is its entry point.
- **Next action:** decide how register **claims** become `supply_observation` rows — which needs F-002 (citation keys) closed and the 687 unverified claims curated. The register's own next action is not a database session — it is the source hunt, raised as **F-003**.

<!-- Everything below this line is LOCAL to the database workstream.
     The per-session narrative for 2b lives in `register/log.md`, not here. -->

## Where we are / what's next (read this first on reopening)

**BioMobi now holds data.** 20 object-grain `stream` rows, 1 classification scheme, 11 terms (7 nested), 20 links. Nothing else — no `source`, no `property_measurement`, no `supply_observation`, no `parameter`, no `geography`. The vocabulary is in; the facts are not.

**State (2a):** abandoned 2026-09-07. The legacy internal Excel is not a usable input and nothing from it was ever loaded. Loader and manifests deleted. See "2a — abandoned" below.

**State (2b):** the candidate stream register is **closed**. It remains a pre-database artifact; the corpus itself populates no table. What crossed into BioMobi is its **selection**, as vocabulary.

**State (2c):** the selection is registered. See "2c — the selection in BioMobi" below.

**Next, in order:**

1. **Decide the claims hand-off.** The register's live claims are candidate `supply_observation` rows, but two gates stand in front of them: **F-002** (all eight source PDFs have a blank `citation_key`, and `source_key` is `NOT NULL`) and **per-claim curation** (most claims are still `awaiting verification`; only S080 has been checked). Neither is a session task on its own. **Each claim's chain stage lands on the observation, not on the object** — that is what the 2026-09-08 restructure freed up.
2. **Push 2c to the live project.** Nothing has been applied there. The migration is committed — review it, then `supabase db push`. The loader is the generator, not the route to live.
3. **Phase 3 — composition.** The 20 registered objects are exactly the `stream_code` values a composition harvest will hang `property_measurement` rows from.

---

## 2a — abandoned (2026-09-07)

**The legacy internal workbook (`BioMobi_Biomass_RevA.xlsx`) is not a BioMobi input.** The reviewer's judgement, taken once 2b had delivered a sourced corpus: the old Excel is not worth the curation it demands when a better-provenanced route exists. Nothing from it was ever loaded into any database, local or live.

Deleted, not archived (a superseded tool invites someone to run it — the same rule the register applied to `analyse.js`): `ingest/load_biomobi_excel.py`, `crosswalks/biomobi_excel_{streams,sources,parameters}.csv`. Git history keeps them. `data/raw/BioMobi_Biomass_RevA.xlsx` was never versioned and is untouched on disk.

**Withdrawn with it:** the `Sugar_beet` grain blocker, the `Pig_SH_WW` question, the 4 in-scope duplicate rows, the pH-in-`mg/L` question, and **flag F-001** (~20 legacy sources needing Zotero entries) — all of them existed only to serve this load.

**Two things from 2a are worth keeping, and they are the reason the thread was not wasted:**

- **The `Dummy` column partitioned the workbook perfectly, and `source_key NOT NULL` reproduced that partition on its own.** Zero `Dummy=Yes` rows carried a source; all 456 rows with both a value and a source were `Dummy=No`. The schema's provenance constraint filtered every fabricated row without being told which they were. That is the strongest validation phase 1 has received, and it survives the input being discarded.
- **The idempotent ownership-namespace pattern** — a loader prefixes the rows it creates, deletes only that namespace, and reloads in one transaction, so a re-run converges on removals as well as additions. Carried forward into `streams/tools/load_streams.py`, which owns a set of stream codes rather than a source-key prefix.

## 2c — the selection in BioMobi (2026-09-07, restructured 2026-09-08)

*Detail, decisions and how to run it live in **`database/streams/`** (`README.md` + `CLAUDE.md`). Not repeated here.*

The register's 80% selection is BioMobi vocabulary — **names and classification only, no volumes**. First data of any kind in the database.

**Loaded:** 20 `stream` rows · 1 `classification_scheme` · 11 `classification_term` (7 with a parent) · 20 `stream_classification` links. **Committed as a migration** (`20260908143000_bioloop_streams_selection.sql`), so `db reset` rebuilds them from git alone and `db push` is the route to live. **Nothing has been pushed to live yet.**

**A stream row is an OBJECT** — a thing you could put in a bag. 13 selected commodities became 20 objects, split where a crop name covers materials that share no composition (`suikerbiet` / `-loof` / `-pulp`; `aardappel` / `-loof`; `bloemkool` / `-loof` / `-harten`; `spruiten` / `spruitstokken`; `raapzaad-stro` / `-schroot`). **Chain stage is never part of identity** — where a material arises is a property of an observation, and `supply_observation` carries it. This closes the "what grain does a register claim become in BioMobi?" question, and dissolves **G-08**: *oogstresten* and *voedselreststromen* of one crop were measurements of different objects, not contradictory figures.

**The objects are derived, not enumerated.** `tools/build_manifest.py` groups the selected commodities' claims by the register's own L5 fraction field — a fraction is its own object, the no-fraction claims are the commodity itself — giving 22 raw groups → 20 objects. A human owns only `crosswalks/object_decisions.csv`: two fraction-synonym merges and seven code/name overrides. Rebuilding the reviewed manifest reproduced every code, name and description **and found a claim the hand-mapping had missed** (`C-154`, 48.662 t, where the hand version used the smaller `C-178`). A new selection is therefore: refresh the corpus, regenerate, decide only what is new.

**One facet: `bioloop-commodity`**, the register workbook's own commodity levels loaded as a ladder — L2 terms are parents, L3 terms carry `parent_term_id`, each object links to its L3 only, and rolling up to the branch is a recursive walk. Chosen to be cheap and revisable; **EWC enters later as a second scheme**, which is `INSERT`s, not a migration.

**Not loaded: `supply_observation`.** `source_key` is `NOT NULL` and all eight register PDFs still carry a blank `citation_key` (**F-002**, the single gate on the volume side). The claim→object mapping that load needs is in `streams/crosswalks/register_streams.csv`, and each claim's chain stage belongs on those rows.

**What the first attempt got wrong, and why it is worth remembering.** It registered 21 rows over two facets, `bioloop-tak` (register L2) and `bioloop-keten` (chain stage) — chosen because those were the two columns the register's *deliverable* happened to expose. Letting the input's shape dictate the data layer's shape produced stage-named pseudo-objects (`aardappel-industrie`, `aardappel-primair`, `suikerbiet-primair`, `bloemkool-primair`, `spruiten-primair`), left `parent_term_id` unused on all 7 terms, and ignored `state.md`'s standing instruction to decide the classification scheme *before* loading. Corrected on reviewer challenge, 2026-09-08. The design intent was recoverable the whole time — the DDL's own `COMMENT ON` lines say "origin sector, material type, EWC" and "Type → Klasse → Subclasse", and `vault/BioMobi/` holds seven empty notes named *Aardappelen · Brouwerij · Fruit · Granen · Groenten · Vis & vlees · Overige*. **Read `vault/` before modelling anything.**

**Two rows wait on gaps, not on modelling** (reviewer, 2026-09-08): `zetmeel-reststroom` is named after the factory it leaves rather than what it is — **G-19**; and `aardappel` absorbs a Prodcom 103113 processing residue because the corpus names no finer potato object — **G-10**. Both resolve when those gaps close, as a new migration from an updated selection. Names remain cheap to change until phase 3 hangs composition off these codes.

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
envelope   7.301.257 t/yr over 69 selectable L4/L5 streams   (2026-09-08 control; top-13 unchanged)
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

Priority order for the hunt (by how much a source would change the stream list, not by gap size): **aardappelverwerking** (621.063 t, zero components, in the sector Flanders leads — no candidate) → **zuivel/wei** (no longer absent: 49.722 t captured 2026-09-08 from a table both MONBIO editions print; what is missing is a *recent* figure, and the candidate is the retired S005 — a decision, not a search) → **vlees per diersoort** → **retail + bakkerij** (S067, S025, neither with a PDF) → **cacao** and **Flemish oilseed crush**. One gap should be **fact-checked before anything is commissioned**: G-02, the PO's/veilingen stage at 15.189 t, looks too small to be true and an afternoon against VBT decides it. Raised for the literature workstream as **F-003**.

### The human gates, and what "closed" means

Everything judgement-bearing is a `;`-delimited, UTF-8-BOM CSV with a `DECISION` column, proposed by script and decided by the reviewer — the workstream-wide crosswalk convention.

| Gate | State |
|---|---|
| `crosswalks/aggregate_coverage.csv` | **242 rows, 0 blank decisions** — what each `AGGREGAAT` row totals. The overview reads it on every build; the pipeline needs no override. |
| `crosswalks/GAP_LIST.csv` | 15 rows. A **worklist, not a decision sheet** — the input to the source hunt. |
| `crosswalks/HIDDEN_STREAMS.csv` | Not present, deliberately. Regenerate it **when a new source is extracted, not before**; a blank gate sitting there would wrongly imply open work. |
| `migrations/` | Every applied gate and its generator, kept for provenance. **Do not re-run.** |

### The checks that make the close-out a proof rather than a claim

All four reproduce from the workbook alone:

```
tools/final_check.py       PASS   803 claims, every one dispositioned into 1 of 8 buckets, 7 properties asserted
tools/verify_overview.py   8/8    arithmetic identities taken from the sources themselves
tools/audit_register.py    24 findings over 736 live claims — the known baseline, all Productievolume rows
tools/select_streams.js    7.301.257 t over 69 streams; 80% at 13, 90% at 20
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
2. **Streams + canonical dictionary + volumes.** — *ran as three threads. The names are in; the volumes are not.*
   - *2a (**abandoned 2026-09-07**):* seed the old internal Excel. The workbook was judged unusable and the thread was closed with nothing loaded. See "2a — abandoned" above.
   - *2b (**closed 2026-09-04**):* monitors + ILVO studies → candidate stream register → 80/20 selection + gap record. **803 claims from eight sources; 69 selectable streams, 7.301.257 t envelope, 80% at 13.** The corpus itself remains a standalone workbook populating no table. See "2b — the candidate stream register" above.
   - *2c (**done 2026-09-07**):* the selection registered as BioMobi vocabulary — 21 material-grain `stream` rows and two classification facets. **Volumes still outstanding:** per-claim curation (`DECISION_expert`) and real citation keys (F-002) gate them. See "2c — the selection in BioMobi" above.
3. **Composition.** FoodWasteEXplorer, FOWCUS, AgroCycle, gap-fill literature → `property_measurement`.
4. **Classification facets.** EWC likely first, plus a sector facet.

## Schema & migration changelog
*(newest first; one line per migration)*

| Migration | Date | Summary |
|-----------|------|---------|
| `20260908143000_bioloop_streams_selection.sql` | 2026-09-08 | **Data, not DDL.** The register's 80% selection as BioMobi vocabulary: 20 object-grain `stream` rows, the `bioloop-commodity` scheme, 11 terms (7 nested), 20 links. Generated by `streams/tools/load_streams.py --emit-migration`; `ON CONFLICT`-guarded throughout. Do not hand-edit — emit a new one when the selection changes. |
| `20260727114134_remote_schema.sql` | 2026-07-27 | Baseline of the live schema: 11 tables, 66 columns, 11 PKs, 16 FKs, 9 CHECKs, 21 indexes, RLS on all 11. Plus a hand-added PostGIS block. |

**Baseline method (phase-1).** `supabase db pull` was unusable: CLI 2.109.1's `pg-delta` engine returned an empty diff and reported "No schema changes found". `supabase db dump --linked --schema public` (pg_dump) was used instead. **Do not trust `db pull`/`db diff` on this CLI version without checking the output is non-empty.** `db dump --schema public` omits extension DDL, so the PostGIS block was added by hand.

**Verification (2026-07-27).** `supabase db reset` rebuilt the schema from the migration alone; cross-checked read-only against live via MCP — table names, md5 over full column signatures, every constraint and index definition all matched.

## Curation manifests (the approval gate)

Ingestion is **gated on human review**, by explicit decision (2026-07-28). Every manifest carries a machine proposal beside a human `DECISION`, and the loader exits non-zero listing every unreviewed row while any cell is blank. This extends the crosswalk convention (LLM-proposed, human-verified) from name-mapping to *inclusion*. Files are `;`-delimited with a UTF-8 BOM so Belgian Excel opens them in columns. Each manifest lives in its sub-project's `crosswalks/`, next to the loader that reads it.

Live: `streams/crosswalks/register_streams.csv` — 20 rows, all `include` (2026-09-08); `register/crosswalks/` — the register's own gates.

## Idempotency — each loader owns a namespace

A loader must be safe to re-run: it deletes only what it owns, then reloads, in one transaction, so a re-run converges on removals as well as additions. What "owns" means is per loader:

- `streams/tools/load_streams.py` owns **a set of stream codes and two classification schemes**. It rebuilds those `stream_classification` links each run. Verified: three consecutive runs at 21 streams / 7 terms / 44 links; an `exclude` withdrew that stream's links.
- For the fact tables, the namespace is a **source-key prefix** — both use `generated always as identity` PKs with no natural unique key, so a naive re-run duplicates silently. A UNIQUE constraint was rejected: it needs a migration, the natural key is full of NULL-ables, and sources contain rows that are *legitimately* identical.

**Reference vocabulary (`unit`/`basis`/`parameter`/`stream`) is upserted and never deleted**, deliberately: `stream_classification` cascades on stream delete, and an ingestion script must not be able to destroy classification work. A row withdrawn by a `DECISION` flip loses its classifications and is reported; its `stream` row stays.

Source keys are renameable to real Zotero BBT keys later — all source FKs are `ON UPDATE CASCADE`.

## Source register & load status
*(tier: **V** = volume/geography · **C** = composition · **R** = reference/conversion)*

| Source | Tier | Access | Status | Notes |
|--------|:----:|--------|--------|-------|
| Old internal Excel | C | file (not versioned) | **abandoned (2a, 2026-09-07)** | Judged not worth its curation cost once 2b delivered a sourced corpus. Nothing loaded, ever. Loader + manifests deleted. |
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
`<sub-project>/crosswalks/<source>.csv` maps each source's naming to canonical `stream.code`, and carries the human `DECISION` gate. Cross-lingual (NL canonical ↔ EN sources) and semantic (peel / pomace / pulp), so **LLM-proposed + human-verified**, never fuzzy-string.

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
- ~~**What grain does a register claim become in BioMobi?**~~ — **resolved 2026-09-08.** 13 selected commodities became **20 object-grain `stream` rows**. The split needed no new source — the register already measured the parts as separate claims. The rule binds the rest: **a stream is an object; identity is never a chain stage and never a commodity standing in for its own fractions.** Unselected streams (ranks 14–69) are not yet registered and will need the same treatment when they enter.
- **Two of the largest streams are Belgian figures, not Flemish** (G-06: the oilseed-meal block, ~1,15–1,31 Mt, including the corpus's #2 entry). The register captured them honestly as `geography = Belgie`. BioMobi must decide whether a Belgian figure may stand as a Flemish stream volume, or whether those streams enter with no volume until a Flemish figure exists.
- ~~**The same crop can carry two incompatible quantities** (G-08)~~ — **resolved 2026-09-07 by the split.** *Oogstresten* and *voedselreststromen* of one crop are now different `stream` rows (`aardappel-loof` vs `aardappel-primair`, `spruiten-stengelmassa` vs `spruiten-primair`, `bloemkool-loof` vs `bloemkool-primair`), so the two figures no longer collapse into an apparent 50,5× contradiction. The residual work is on the *claims*: each must attach to the material it measures when volumes load.
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
- ~~**`Sugar_beet` grain**~~, ~~**`Pig_SH_WW`**~~, ~~**4 in-scope duplicate rows**~~, ~~**pH recorded in `mg/L`**~~ — all **withdrawn 2026-09-07** with the legacy Excel (2a abandoned). Each existed only to unblock that load.
- **Are the split streams' `canonical_name`s the right ones?** They are the register's own wording, Dutch, material-first (`Bietenpulp`, `Spruitstokken en stengelmassa`). Cheap to change now — `stream.code` is the primary key and the FKs are `ON UPDATE CASCADE`; expensive once measurements reference them.
- **Four streams rest on an interpretation, not on a source's own name:** `aardappel-primair`, `suikerbiet-primair`, `bloemkool-primair`, `spruiten-primair`. Their claims are OVAM/ILVO figures for *voedselverliezen* and *nevenstromen* of a crop, which this session read as "the crop itself, rejected or unharvested" — a distinct material from that crop's field residue. The reading is what makes the G-08 spreads resolve, but no source says it in those words. Worth a reviewer's eye before volumes attach to these four.
- **Classification facet priority** — EWC-first assumed; confirm at phase 4.
- **FoodWasteEXplorer export format** — confirm at phase-3 kickoff.
- **RLS with no policies** — all 11 tables have RLS on and zero policies. Fine while ingestion runs server-side under `service_role`; revisit if anything reads BioMobi through the API.
- ~~**Baseline method**~~ — resolved 2026-07-27: `db dump` (pg_dump).
- ~~**Commit raw source data?**~~ — resolved 2026-07-28: **no.** `**/data/raw/` is gitignored.
- ~~**80/20 ranking basis**~~ — resolved 2026-07-28: **not applicable to already-collected data.** The 80/20 is a rule for *prospective* harvesting. This dataset is small and already collected, so selection is manual, per stream, checking (a) the name, to exclude manure/OFMSW, and (b) the source, to validate the entry. Hence the manifest gate.

*Last updated: 2026-09-06.*
