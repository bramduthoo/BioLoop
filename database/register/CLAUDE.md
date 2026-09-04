# Register workstream — Claude Code extraction protocol (phase 2b)

*The session runbook for building the candidate stream register. **One source per session**:
receive a human-verified PDF, archive it in Zotero, extract its volume claims into the
workbook, verify. Read this **with**, not instead of, the root `CLAUDE.md`, `protocol.md`,
and `database/CLAUDE.md`. Detail lives here; only project-level status rises to
`database/hub.md` and `state.md`.*

*Protocol v2 (2026-08-15) — chain-stage scope made explicit, provenance and unit columns
added to `Streams`, destination/collection-route metadata split off into its own index.*

*Protocol v2.1 (2026-08-15) — from the S080 review, all of it things a reviewer had to catch by
hand. **A correction first:** the destination/route ban had been swallowing `quantity_type`
data, because sources print the `voedselverlies` / `nevenstroom` split as a cross-tab against a
collection route. Such tables are now read **by axis, not by table**. Added: a completeness
sweep over the source's own table/figure index; a 26th column `also_stated_in` carrying
restatement and variant trails on the row; `stream_name_NL` must disambiguate sibling rows;
parallel accounting definitions handled explicitly; `chain_L2` assigned by the measured event
rather than the chapter; a cross-source restatement rule for series editions; and a canonical
export order independent of the sheet's own column arrangement.*

*Protocol v2.2 (2026-08-16) — tooling only, no extraction rule changed. `log.md` gained a
derived HTML view (`render_log.py` → `log.html`), regenerated as part of procedure step 7, so
the log can be read and reviewed outside an editor.*

*Protocol v2.3 (2026-08-17) — from the human review of S091, all of it things a reviewer had to
catch by hand on a source with per-product statistics. **Geography tightened**: where a figure
exists for both Belgium and Flanders, the Flemish one is the claim — and a column headed
"Vlaanderen" does not make a figure Flemish if the source's own text defines it otherwise. Added:
a source's own product name can specify edible/inedible and then overrides a session-level default;
`level_1to5` is a commodity-breadth label and never implies that one row contains another; the
conversion factor must be **legible and its arithmetic spelled out**; a scope caveat that changes
*what* or *which year* a figure measures belongs in `stream_name_NL`; an aggregate that includes a
deliberately-excluded component must say so on the row; and the completeness sweep must account for
a captured table **cell by cell** whenever any of its cells are dropped.*

*Protocol v2.4 (2026-08-26) — no extraction rule changed, but one marker became load-bearing.
The derived overview now reads the **`AGGREGAAT - ` name prefix as a structural claim**: a row
carrying it is a *total of other rows*, so it is never summed with its siblings and instead
becomes the reported total they are checked against. Apply the prefix to every such row and to no
others. Each aggregate also needs a line in `crosswalks/aggregate_coverage.csv` saying what it
totals. The `Gemengd` → `Varia` reclassification is **proposed** in `crosswalks/varia_reclass.csv`
and awaits the reviewer's `DECISION`; until it is applied, `Gemengd` remains the live vocabulary.*

*Protocol v2.5 (2026-09-01) — **five placement rules, all of them learned the hard way.** The
`Gemengd` → `Varia` reclassification is applied and `Gemengd` is retired. Cleaning up after it took
three review rounds over ~190 rows, and every round traced back to the same handful of decisions
being made ad hoc during extraction. They are now rules, and `audit_register.py` enforces them, so
a new source is checked in seconds instead of re-litigated:*
*(1) a row that names a **product** sits at **L4**, never at L3 — an L3 row is invisible to a
selection, which only reaches L4/L5; (2) a **residual class of a nomenclature** (`Andere …`,
`n.e.g.`, `van alle soorten`, several species in one cell) is an **aggregate**, not a component —
it is a real volume but not a named stream, and it lands in the unallocated band; (3) a row that
**totals other rows** carries the prefix, whether the source says* totaal *or the arithmetic shows
it; (4) `level_1to5` is the row's **own commodity depth**, never the level an aggregate totals —
that lives in `aggregate_coverage.totals_level`; (5) a **processing product goes under its sector**,
not under the crop it came from — the register has two partitions, crops and `Varia` sectors, and
bread is not a cereal.*

## What this workstream produces

`BIOLOOP_streams_and_sources.xlsx` — a standalone, claim-level corpus of Flemish agri-food
side-stream figures for expert review. **It is not a BioMobi input and populates no database
table.** One row = one figure exactly as one source reported it. Contradictions are preserved,
never averaged; nothing is silently dropped or harmonised.

**Only the copy under `database/register/` is canonical.** A file of the same name exists at
the repo root: it is a superseded legacy corpus and must never be opened, read, or used as
precedent.

Alongside it, two smaller committed artifacts: `destination_index.csv` (where each source
keeps its destination / collection-route volumes) and `log.md` (the per-session record).

**The aggregate registry (v2.4).** `crosswalks/aggregate_coverage.csv` records, per
`AGGREGAAT - ` row, **what that row is the total of**: the level it totals, the parent row it
attaches to, whether it covers all of that row's entries or a named subset, which chain stages it
spans, and whether competing values are variants (the default — averaged, never summed) or a
`component_set` (collection-route halves, which do sum). It is human-gated like every crosswalk
here: `make_aggregate_coverage.py` proposes, the `DECISION` column decides, and a blank `DECISION`
means the proposal is used but shown in the overview as an unreviewed `proposal`.

An aggregate is placeable only when **everything it covers sits under one parent row at one
level**. One that does not — a total of three L3 entries living under two different L2 parents —
is not an error and is not dropped: it goes to the overview's *unallocated* band, where it stays
visible and usable but is never compared or summed. **When a session captures a new aggregate,
add its line to the registry in that same session**, exactly as new dictionary members are added
in the session that first needs them.

**`log.md` has a derived HTML view.** `render_log.py` renders it to `log.html` — a readable,
navigable page for checking the log without an editor. **`log.md` stays the source of truth**;
`log.html` is generated, gitignored and disposable, and is **never hand-edited** (same rule as
the workbook's `Rollup_check` / `Stream_index` sheets). Its summary figures are computed from
the Sessions table and `streams_export.csv`, so they cannot drift.

## Session contract

**At start, read in order:**

1. Root `charter.md`, `state.md`, `flags.md` (filtered to `to: db`) — orient (skim if known).
2. `database/hub.md` (status header) — where the workstream stands.
3. This file — the protocol.
4. `register/dictionaries/` — the three controlled vocabularies (`chain_L2.csv`,
   `quantity_type.csv`, `commodity_hierarchy.md`). **These are binding.**

The session objective is **one named source**, set when the session opens.

**At end:** update `database/hub.md` status; append to `register/log.md`; commit naming the
source. Route project-level items to `state.md`, cross-workstream items to `flags.md`
(per `protocol.md` §4).

## Tools

- **Zotero MCP** — create the source item and attach its PDF. Use **absolute paths**. Create
  items from the **`Sources`-sheet metadata**, *never* from PDF DOI auto-extraction (grey
  literature — ILVO / OVAM / MONBIO — usually has no DOI).
  *Currently unavailable — no Zotero server is wired in `.mcp.json` (flag **F-002**). Until it
  is: archive the PDF, leave `citation_key` blank, and say so in `log.md`.*
- **PDF extraction** (`database/.venv`, which carries `pdfplumber` and `pymupdf`):
  `pdfplumber` for the text layer and borderless tables, `camelot` for bordered tables with
  confidence. **Escalate** messy / merged / scanned tables — and **every figure that might
  carry a number** — to a **rasterize-and-read pass**: render the page to PNG (`pymupdf`) and
  read the image directly. Low volume — favour accuracy over automation.
- **Excel** (`openpyxl` / `pandas`): edit **only** the `Streams` and `Sources` sheets.
  `Rollup_check` and `Stream_index` are **derived** — regenerated by script from `Streams`,
  never hand-edited.

## Inputs (per session)

- A **human-verified PDF** in `register/inbox/`. Extraction runs **only** against this frozen
  file — never a live fetch. (If the source was HTML-only, its PDF was constructed and
  verified upstream; treat it the same.) The PDFs are **gitignored**: the committed audit
  trail is `streams_export.csv` + `log.md`, checked by a human against the local `archive/`
  copy.
- That source's **row in the `Sources` sheet** (its `S0xx` id, title, author, year,
  publisher, URL, access).

---

## Scope — what counts as a claim

Three independent filters. A figure is captured only if it passes **all three**.

### 1. The chain stage must be in scope

The register covers the **supply side of the agri-food chain**: primary production, the
trading/auction layer, processing, and distribution.

| Chain stage (`chain_L2`) | In scope |
|---|---|
| `Primaire productie` (land- en tuinbouw, veehouderij) | **yes** |
| `Visserij` | **yes** |
| `Producentenorganisaties/veilingen` · `Visveilingen` | **yes** |
| `Voedingsindustrie` | **yes** |
| `Retail & grootdistributie` | **yes** |
| `Horeca & catering` | **no** |
| Households / consumers | **no** — and deliberately not even a `chain_L2` member |

Out-of-scope stages are **not extracted at all** — not as totals, not as splits, not as
context. `chain_L2.csv` carries the same table in its `in_scope` column; it is authoritative.

### 2. Aggregates: every stage inside the aggregate must be in scope

An aggregate row is capturable **iff every stage it spans is in scope**. A primary-sector
total (visserij + visveilingen + landbouw + PO's) is fine — all four are in. A
"retail + horeca + catering + consumenten" total is not, and neither is a whole-chain grand
total, because both swallow stages we exclude.

This is *why* `level_1to5` has no 1: a single whole-chain total for all of Flanders
necessarily mixes in horeca, catering and households. The **highest capturable aggregate is
level 2** — a commodity-group or sector total whose stages are all in scope.

### 3. The figure must be a quantity of material, per year

Capture every reported figure that quantifies **how much of an agri-food biomass stream
arises per year** — an annual tonnage/volume — at any in-scope point in the chain, covering
both residual streams (agri-food waste / nevenstroom / voedselverlies) and the hoofdstroom
production-volume totals that give them context, at whatever commodity level the source
reports (group, subgroup, ingredient, or fraction).

**Not quantities of material** — do not capture: composition, nutrient or moisture content,
prices, index scores, percentage shares, per-capita figures, areas (ha), counts of businesses,
year-on-year deltas ("+20.760 ton t.o.v. 2015"), and policy or regulatory text.

**Also out**, by `quantity_type.csv`: `schenking`, `slib`, `afgeleid product`.

**Destination and collection-route splits are not stream volumes.** Two axes are out of scope:

- the **destination** axis — diervoeder, vergisting, compostering, verbranding, biobrandstof,
  biochemie, bodem, storten, petfood: *what was subsequently done with the material*;
- the **collection-route** axis — selectief ingezameld vs in restafval, ingezameld vs andere:
  *how the material was collected*.

Do not extract figures resolved only along those axes; **do** record where they live, in
`destination_index.csv` (procedure step 4).

**`quantity_type` is register data wherever it is printed** (corrected 2026-08-15 — the earlier
wording lost real data). The `voedselverlies` / `nevenstroom` / `agri-food waste` split is one
of the register's three axes, not a routing detail, and sources routinely print it as a
**cross-tab against a destination or collection axis**. Read such a table by axis, not by
table:

- If the source prints the stream × `quantity_type` **total** anywhere, that total is the
  claim; the destination/route cells beside it add nothing and are only indexed.
- If the source prints **no** total and the quantity-type figure exists only as component
  cells, **capture the cells** — naming the route or destination in `stream_name_NL` and
  `source_type_label`. Dropping them would discard quantity-type data; adding them together
  would be a derivation. **Never sum siblings**, and say so on the row.
- A cell that resolves *only* the destination/collection axis, adding no `quantity_type` or
  commodity detail, is never a claim.

### Restatements — capture once, but leave the trail on the row

Sources repeat their headline figures. A figure that appears in several places is **one claim**,
not several:

- **Rounded restatements** ("afgeleid 341.000 ton" next to a table's 340.886) never get their
  own row — capture the precise value.
- **Exact restatements** (the identical number in a synthesis table, a sector table, an
  infographic and the running text) likewise get one row.
- **Which location wins:** the most specific one. A sector chapter's own table beats a
  synthesis-chapter table, which beats an infographic, which beats running text. Record that
  location in `source_page` / `source_table_figure`.
- **Every other location goes in `also_stated_in` (column 25) on that same row** — e.g.
  `ook in Tabel 5 (p.17), Figuur 8 (p.49)`. A reviewer checking the workbook against the PDF
  must be able to see, from the row itself, that a table they are looking at *was* read and
  where its value ended up. Listing restatements only in `log.md` is not enough — that has
  already caused a reviewer to report a captured figure as missing. Cross-references to variant
  claims go here too (`variant: Tabel 34 drukt 58.849 - zie C-110`), so both sides of a
  contradiction point at each other.

### Parallel accountings — same stream, incompatible definitions

A source may report the same stream twice under **different definitions** (a national
definition and an EU regulatory one; a "total arising" and a "waste only" figure). These are
not variants and not errors — they measure different things and will differ by a large factor.

- Capture **both**, and make the definition visible **in `stream_name_NL`**, not only in
  `source_type_label`, so two rows for the same stage and year cannot be mistaken for a
  contradiction.
- State the reconciliation in `log.md` where the source allows it (which destinations one
  definition includes and the other excludes, with the arithmetic), and say so plainly when the
  two do not reconcile exactly.

### Do not inherit the source's own scope exclusions

A source's scope is not the register's scope. When a source **names a tonnage** of agri-food
biomass and then excludes it from its own totals — slaughterhouse hides and bones "because it
is not food", pre-harvest losses "outside the scope of the reported figures", material judged
"not slachtrijp" — **capture it**, and record the source's framing in `source_type_label`.
Only the register's own filters above remove a figure.

If you are unsure whether a number is a stream volume, **capture it and flag it** in `log.md`
rather than drop it.

---

## Procedure

1. **Confirm inputs.** PDF present in `inbox/`; its `Sources` row exists (add the row first
   if the source is new).

2. **Archive in Zotero.** Create the item from the `Sources`-row metadata; attach the PDF
   (absolute path). Confirm / record its **Better BibTeX key** and write it back into the
   `Sources` row (`citation_key`). Then **move the PDF from `inbox/` to `register/archive/`**
   — this archived copy is the frozen, verifiable artifact. *(While F-002 is open: move the
   PDF, leave `citation_key` blank, note it in `log.md`.)*

3. **Extract.** Read the PDF's quantitative content about agri-food waste cover-to-cover,
   applying the three scope filters above. Every figure that survives becomes one `Streams`
   row per the schema and vocabularies below. Record the number **as the source reported it**
   — convert to tonnes/yr only per the conversion rule, and otherwise do not harmonise,
   correct, or de-duplicate; flag anomalies instead.

4. **Index the destination data.** While reading, note every table/figure carrying
   destination or collection-route **volumes** and append a row per location to
   `register/destination_index.csv`. If the source has none, append one row with
   `has_data = no` — "checked and absent" must be distinguishable from "not yet checked".
   Do not extract the values themselves.

5. **Self-check** (checklist below) before the write is final, then **run the structural audit**:

   ```
   database/.venv/Scripts/python database/register/tools/audit_register.py --source S0xx
   ```

   It checks the five placement rules of v2.5 plus provenance and registry consistency, and exits
   non-zero while anything is open. **It must come back clean, or every remaining finding must be
   named in `log.md` with the reason it is not a defect.** `--csv` writes
   `crosswalks/AUDIT_findings.csv` with a `DECISION_fix` column when a reviewer needs to sweep them.
   Then regenerate the aggregate registry and decide the new rows:

   ```
   database/.venv/Scripts/python database/register/tools/make_aggregate_coverage.py
   ```

6. **Export for diffing.** Write a plain-CSV copy of the `Streams` sheet to
   `register/streams_export.csv` (semicolon-delimited, UTF-8 BOM), so the session's
   claim-level changes are git-diffable. **Always write the 25 columns in the canonical order
   of the schema below, whatever order the sheet's columns are currently in** — a reviewer may
   rearrange the sheet to read it (moving `source_page` to the front, say), and the export must
   not turn that into a diff where every row changed. Read and write the sheet **by column
   header, never by position**, for the same reason.

7. **Log.** Append a row to `register/log.md` (source, PDF, #claims, anomalies, commit),
   plus an anomaly note if the source needs one. Then regenerate the HTML view:

   ```
   database/.venv/Scripts/python database/register/tools/render_log.py
   ```

   It reads `log.md` and rewrites `log.html` in place; it never writes to the markdown.
   If a session adds a markdown construct the renderer does not handle, **fix the renderer** —
   do not simplify the log to suit it.

8. **Report up.** Update `database/hub.md` status; commit
   `register: extract <source_id> — <n> claims`.

9. **Human verify.** The reviewer checks `Streams` against the PDF now in `archive/` before
   the source is considered done.

---

## The `Streams` schema (26 columns)

*Canonical order is the order below. The **sheet's** physical column order is the reviewer's
business — they may drag `source_page` to the front to check provenance quickly. Always read
and write the sheet **by column header**, and always write `streams_export.csv` in the
canonical order, so a rearranged sheet never produces a diff where every row changed.*

| # | Column | Meaning / rule |
|---|--------|----------------|
| 1 | `claim_id` | Stable label `C-001...`; keep contiguous. |
| 2 | `stream_name_NL` | The stream in Dutch, roughly as the source named it. `AGGREGAAT - ...` = a sector total (level 2), shaded. **Must carry whatever qualifier distinguishes this row from its siblings** — `(incl./excl. ...)`, `(EU-definitie)`, `(som van de 10 belangrijkste)`, a variant marker. If two rows in the same source share a stage, year and quantity type, their names must differ and must say *why*. Putting the qualifier only in `source_type_label` is not enough: the name is what a reviewer reads. |
| 3 | `L1_role` | `Productievolume` or `Reststroom`. **Gates `quantity_type`.** |
| 4 | `L2_commodity_group` | Broad group (see `commodity_hierarchy.md`). |
| 5 | `L3_commodity_subgroup` | Subgroup; the rollup pivot. |
| 6 | `L4_ingredient` | Specific ingredient; blank if the source reported only at subgroup level. |
| 7 | `L5_fraction_as_named` | Genuine fraction in the source's words; a distinct object, never a label. |
| 8 | `level_1to5` | Depth 2-5 (no 1). See the depth rule in `commodity_hierarchy.md`. |
| 9 | `chain_stage` | The stage in the source's own words. |
| 10 | `chain_L2` | Standardised stage (see `chain_L2.csv`); must be an **in-scope** value. |
| 11 | `source_id` | `S0xx`; join key to `Sources`. |
| 12 | `source_short` | Human-readable source tag. |
| 13 | `reference_year` | The year(s) the figure describes (free text: `2011`, `2010-2011`, `gemengd`, `n.v.t.`); not the publication year. |
| 14 | `volume_t_per_yr` | The quantity in tonnes/yr = `value_as_reported` × `conversion_factor_to_t_per_yr`. Meaningless without `quantity_type`. |
| 15 | `value_as_reported` | The number **exactly as printed** in the source, before any conversion. |
| 16 | `unit_as_reported` | The unit **exactly as printed** (`ton`, `kton`, `miljoen ton`, `kg`, ...). |
| 17 | `conversion_factor_to_t_per_yr` | The multiplier applied. `1` when the source already reports tonnes. See the conversion rule below. |
| 18 | `quantity_type` | One of the 4 canonical values (see `quantity_type.csv`). |
| 19 | `source_type_label` | The source's own word for the stream type (`productieverlies`, `doordraai`, ...), plus any scope caveat the source attached ("excl. niet-geoogst", "valt buiten de scope"); contextual metadata, on every row. |
| 20 | `type_assumed` | `TRUE` when `quantity_type = agri-food waste` was **defaulted** for lack of edible/inedible detail; else `FALSE`. |
| 21 | `geography` | `Vlaanderen`, or `Belgie` where only a national figure exists. |
| 22 | `provenance` | Always `read in PDF` (every source is a verified, archived PDF). |
| 23 | `source_page` | Page of the **archived PDF file** the figure was read from (not the printed folio, which often differs; if it does, note both: `30 (gedrukt 28)`). |
| 24 | `source_table_figure` | Where on that page: `Tabel 12`, `Figuur 6`, `tekst`. Use the source's own numbering. |
| 25 | `also_stated_in` | **Every other place in the same source that states this figure**, and any cross-reference to a variant claim: `ook in Tabel 5 (p.17), Figuur 8 (p.49)`; `variant: Tabel 34 drukt 58.849 - zie C-110`. Blank when the figure appears exactly once. See the restatement rule below. |
| 26 | `DECISION_expert` | Blank — the reviewer's column. |

Columns 23-24 exist so any row can be re-checked against the PDF in seconds, and 15-17 so any
row can be re-derived. **All five are mandatory on every row** — an unfillable one means the
figure was not actually read from a locatable place, which is itself a problem. Column 25 is
what lets a reviewer who is looking at *a different* table find the row that already holds its
value.

**Two rules on where a caveat goes (v2.3).** Both come from the S091 review, where a reviewer
reading only the workbook could not see something the log knew:

- **A caveat that changes *what* — or *which year* — the figure measures belongs in
  `stream_name_NL`**, not only in `source_type_label`. Examples: a figure the source carries
  forward from an older edition (`(cijferbasis 2018, door de bron overgenomen)`); a coverage that
  is a company rather than a territory (`productie van het Vlaamse bedrijf (sites in Vlaanderen en
  Wallonie)`); a definition that differs from the sibling row's. The name is what a reviewer reads;
  a caveat parked in the label will be missed. This extends the existing sibling-disambiguation
  rule from "how does this row differ from its neighbour" to "what does this row actually measure".
- **An aggregate that includes a component you deliberately did not capture must say so on the
  row.** Otherwise a reviewer summing the captured children against the parent finds a gap and
  cannot tell whether something was missed or excluded on purpose. Name the excluded component and
  its tonnage in `source_type_label` — e.g. a plantaardige total that includes an uncaptured
  sierteelt figure.

## Units and conversion

`volume_t_per_yr` must be a **pure unit conversion** of what the source printed:

- **Allowed:** kg → t (×0.001), kton → t (×1 000), miljoen ton → t (×1 000 000), and any
  factor **the source itself supplies** (e.g. it prints a piece-weight or a density).
- **Never derived.** Do not turn pieces into tonnes, kg/inwoner into tonnes via a population,
  a percentage into tonnes via a total, or hectares into tonnes via a yield — even when the
  numbers to do so appear elsewhere in the source. That is a calculation, not a reading.
- A figure whose unit cannot be converted under that rule is **not captured**; record what and
  where it was in `log.md` (e.g. "Figuur 6 reports komkommers in 1.000 stuks — no mass basis
  in the source").
- Never silently harmonise. If two figures in one source use different units, convert each
  independently and let the columns show it.
- **Spell the arithmetic out, and make the factor legible** (v2.3). `conversion_factor_to_t_per_yr`
  exists so a reviewer can re-derive the row, so it has to survive being opened in Excel: give the
  column an explicit number format (`0.#####`), because the default *General* format renders
  0,00104 as "0,001" and a reviewer checking `value × factor = volume` by eye will conclude the row
  is wrong. Where the factor is not the source's stated number but a unit-conversion of it, put the
  chain in `source_type_label` — "1 liter × 1.040 g/l = 0,00104 t", "1 hl = 100 l × 1.050 g/l =
  0,105 t". A stated density in g/l is the source's factor; expressing it in t per reported unit is
  arithmetic on that factor, not a new one.

## Contradictions and anomalies

Sources contradict themselves. **Every variant is captured** — one row each, no averaging, no
deletion. What differs is how the log treats them:

- **Variant readings** — values in a plausible range of each other (a total restated as 59.849
  and 58.849; 7.467 / 7.475 / 7.476). These may be rounding, a later revision, or genuinely
  different measurements. Capture all, list them in the log's anomaly note as *variants*, and
  leave them for the expert. Do not call them errors.
- **Suspected source errors** — reserved for cases with **arithmetic evidence**: the figure
  breaks its own table's total, or its digit order contradicts every other statement of the
  same quantity (a dropped digit: 21.060 where the table's parts sum to 215.060 and the text
  says 215.060). Capture **as recorded** — never correct the cell — but flag it prominently in
  the log, naming the evidence, so `DECISION_expert` can retire that row.

Everything else that looked odd — a unit that could not be converted, a figure the source
excludes from its own totals, a stream that forced a new dictionary member — goes in the
anomaly note too.

## The vocabularies and the rules that bind them

- **`L1_role` gates `quantity_type`.** Productievolume leads to `hoofdstroom` only.
  Reststroom leads to `agri-food waste`, `nevenstroom`, or `voedselverlies`.

- **`quantity_type` is collapsed** (`quantity_type.csv` is authoritative):
  - `biomassareststroom` and `voedselreststroom` are **merged into `agri-food waste`**.
  - `agri-food waste = nevenstroom + voedselverlies`. Use the split only when the source
    specifies edible/inedible; otherwise `agri-food waste`. When a source gives **both** the
    total and the split, capture all three — they are different quantity types and never sum
    across each other.
  - **"The source specifies edible/inedible" includes the source's own product name** (v2.3).
    A session may set a source-wide default (e.g. "this source's residual vocabulary is economic,
    so everything defaults to `agri-food waste`"), but that default is **per-source, not
    per-row**: any individual row whose printed name says *eetbaar* / *niet-eetbaar* (or the
    equivalent) has had its edibility specified, and takes `voedselverlies` / `nevenstroom` with
    `type_assumed = FALSE`. The default governs only rows where the source is silent. When you
    set a source-wide default, say in `log.md` that it is overridden by explicit per-row wording.
    Note the vocabulary trap and record it on the row: `voedselverlies` is the register's
    **edible-fraction** category, not a claim that the material was wasted — an edible by-product
    that is fully valorised still belongs there.
  - Retired stage-names (`productieverlies`, `doordraai`, `voedselafval`): classify as
    `nevenstroom` / `voedselverlies` **iff** the source specifies edible/inedible, else
    `agri-food waste`. In **all** cases keep the source's original word in
    `source_type_label`; when `agri-food waste` was defaulted for lack of detail, set
    `type_assumed = TRUE`. The chain stage goes in `chain_L2`.
  - `schenking`, `slib`, `afgeleid product` are **out of scope** — do not extract.

- **`level_1to5` is in the set {2, 3, 4, 5}** per the depth rule. A distinct fraction is
  always 5. Level 2 is the ceiling (see the aggregate rule above).
  **`level_1to5` is a commodity-breadth label, not a volume hierarchy** (v2.3). A level-2 row is
  not the aggregate of the level-3 rows near it; it is simply a row whose material spans more than
  one commodity group. **Only rows named `AGGREGAAT - …` are volume aggregates.** Two rows from the
  same table can sit at different levels and still be *disjoint* — a statistical nomenclature
  routinely splits one commodity across categories that cut each other (e.g. "preserved in vinegar"
  vs "preserved other than in vinegar"). Where two rows could be misread as part and whole, say in
  `also_stated_in` that they are disjoint and why. Do not rename or re-level a row to make the
  volumes look ordered — the ordering is not the point.
- **`L5_fraction_as_named` is only used where the dictionary already establishes a fraction
  vocabulary for that branch** (v2.3). A processing state (*bevroren*, *gezouten*, *bereid*,
  *geraffineerd*) is a name qualifier, never an L5 fraction. Before inventing the first L5 on a
  branch, check what the human-verified rows on that branch do; if none uses L5, do not be the
  first. Comparable objects inside one table must sit at the same level.

- **`chain_L2`** standardised per `chain_L2.csv`: the source's own stage wording in
  `chain_stage`, the canonical value in `chain_L2`, and only values marked `in_scope = yes`.
  **Assign the stage by the event the number measures, not by the chapter or table it sits
  in.** One table can hold two stages — a landing volume is `Visserij` even when it is printed
  in the visveilingen chapter next to the withdrawn-at-auction figure, which is `Visveilingen`.
  Split such a table across stages rather than inheriting the chapter's heading.

- **`geography`**: `Vlaanderen`, or `Belgie` where only a national figure exists. Never
  silently treat a Belgian number as Flemish. Figures for other regions (Wallonië, Brussel)
  or other countries are out of scope.
  **Where the same quantity is printed at both levels, the Flemish figure is the claim** (v2.3).
  A Belgian figure is captured only when it is a *different measurement* with no Flemish
  counterpart, and then always with `geography = Belgie` and a cross-reference to the Flemish row.
  Never let a Belgian number stand in as the Flemish claim.
  **A column header is not a definition** (v2.3). Statistical tables routinely carry a "Productie
  Vlaanderen" column whose contents the running text defines as something else — a company's
  output across several regions, a sector federation's members, an export-ratio proxy. **Read what
  the text says the column means before trusting the header**, and set `geography` by the material
  coverage, not by the heading. When the two disagree, record the disagreement in
  `source_type_label` — that is the opposite of treating a Belgian number as Flemish silently.
  **One sanctioned exception, and only this one:** figures labelled *Belgische havens /
  Belgische visveilingen / Belgische zeevisserij* are recorded as `Vlaanderen`, because every
  Belgian fishing port lies in Flanders, so the national and Flemish figure are the same
  number. Note the source's own wording in `source_type_label`. **Do not generalise this to any
  other Belgian figure** — no other national number may be relabelled Flemish, however
  Flemish-dominated the sector looks.

- **`reference_year`**: free text as the source frames it; the year the figure *describes*.

### Cross-source restatement — a source does not re-own figures it carries forward

The restatement rule above works *within* a source; the same principle applies *between*
sources, because monitor series reprint their predecessors' numbers in evolution tables
(`2015 | 2020 | 2023`). A source that merely carries a figure forward does not re-own it.

- **Capture what this source measured or revised.** A source that genuinely measures several
  years keeps all of them — this is not a "one year per source" rule.
- **Skip values restated from an edition already in the `Sources` sheet**, and log the skip
  naming the table and the years, so it stays recoverable from the archived PDF.
- **If no source in the register owns those years, capture them here** rather than lose them.
  Check the `Sources` sheet; do not assume.
- **A revision is new information.** Where a later edition *corrects or restates differently*
  an earlier year's figure, that value is unique to this source and is captured with the
  earlier `reference_year`. Flag it in `log.md`, since it will look like a year-rule violation.
- Where a stage's *only* figures fall outside what this source owns, record in the log that it
  yielded nothing — "checked and absent" must stay distinguishable from "not checked".

- **`provenance`**: always `read in PDF`. Search-snippet extraction is no longer used.

- **New members**: when a new subgroup / ingredient / fraction (or a new source-name
  mapping) first appears, add it to the relevant dictionary in the *same* session, then
  use it.

## Placement rules (v2.5) — where a row goes, and what it is

These five decide whether a figure is usable. They were settled after three review rounds over the
first four sources; `audit_register.py` checks all five.

**1. A product sits at L4. A subgroup sits at L3.** If the source names an *article* — anything
carrying a Prodcom/PRODCOM code, or a specific product like *Mout*, *Vers brood*, *Melasse* — it is
`L4_ingredient` under its subgroup. Never leave it at L3 with `L4` blank: BioMobi selects from
**L4/L5 only**, so an L3 row is invisible to a selection no matter how large it is. This alone
accounted for 75 rows and ~17 Mt in the first four sources.

**2. A residual class of the nomenclature is an aggregate, not a component.** Every statistical
nomenclature ends its branches with a leftover bucket: *Andere plantaardige oliën*, *Worst van alle
soorten*, *Gries, griesmeel en pellets van granen, n.e.g.*, *Eetbare slachtafvallen van runderen,
varkens, schapen, geiten en paarden*. That is a real volume but **not a named stream**, and it is
not the total of its siblings either. Give it the `AGGREGAAT - ` prefix and `allocatable = no`: it
stays visible in the unallocated band, and never sums with named siblings. The reviewer's own test:
*"if the name is a sum of things or a collection of parts which already exist, this will almost
always be an aggregate."*

**3. A row that totals other rows carries the prefix.** Two kinds of evidence, both sufficient:
the source's own wording (*totaal*, *totale*, *(totaal)*), or arithmetic — the row equals the sum of
its siblings. `promote_totals.py` applies both and is idempotent. A row that says *totaal* is a
total even when its name also looks like a residual class.

**4. `level_1to5` is the row's own commodity depth.** It equals the deepest of `L2…L5` actually
filled — nothing else. For an aggregate it answers *"where does this row sit"*, not *"what does it
total"*; the level it totals belongs in `aggregate_coverage.totals_level`, and the entries it covers
in `commodity_coverage`. Three separate facts, three separate places.

**5. A processing product goes under its sector, not its crop.** The register carries **two
partitions** — the commodity ladder (`Plantaardig - akkerbouw`, `Dierlijk - vee`, …) *and* the
processing sectors under `Varia` (`Bakkerij`, `Dranken`, `Olien, vetten`, `Chocolade`, `Suiker`,
`Zetmeel en zetmeelproducten`). A product of a process belongs to the **sector**: bread is not a
cereal, refined sugar is not a beet, melasse is not a suikerbiet. Keep the crop ladder for material
that is still the crop (straw, haulm, the tuber itself).

**Where the scripts live, and which run for every source.** Every script is in **`tools/`** and every
generated file in **`build/`** (restructured 2026-09-04). Run for each new source, in this order:
`tools/prep_data.py`, `tools/promote_totals.py`, `tools/make_aggregate_coverage.py`,
`tools/audit_register.py`, **`tools/find_hidden_streams.py`**, `tools/export_streams.py`,
`tools/build_overview.py`, then **`tools/final_check.py`** and `tools/verify_overview.py` as the
closing checks. `find_hidden_streams.py` is not optional: it catches a residual row parked at L2/L3
with an ordinary name, which every name-based check in `audit_register.py` structurally misses.
**Do not re-run anything in `migrations/`** — those are finished one-offs kept for provenance.

## Invariants (never break)

- **Facts only.** No rules, transformations, or valorisation judgements — those are
  model-layer.
- **One row per figure.** The same stream recurs across rows on purpose; four sources
  give four rows.
- **Preserve contradictions.** Never average, silently harmonise units, correct an error,
  or delete a duplicate. Convert units only as allowed above; otherwise record as stated and
  **report** the anomaly in `log.md`.
- **Every row carries a resolvable `source_id`, and a page + table/figure.** No source, no row.
- **Absence = not measured.** Never invent or zero-fill a figure to "complete" a stream. A zero
  the source actually prints is a reading and is captured.

## Self-check before finalising

- **Account for a captured table cell by cell whenever any of its cells are dropped** (v2.3).
  "Captured" is not a sufficient disposition for a table some of whose rows were skipped as rounded
  restatements, confidential, or non-convertible: name those cells and their reason in `log.md`,
  and make sure the row that *does* hold the value carries the table in `also_stated_in`. The
  `also_stated_in` trail only helps a reviewer who starts from the row that has it — a reviewer
  working table by table needs the log entry. This is what makes a captured figure look missing.
- **Completeness sweep — account for every table and figure in the source.** Walk the source's
  own *Tabellen* / *Figuren* index (or, where it has none, your own enumeration of its numbered
  objects) and put each one in exactly one bucket: **captured** (which claims), **excluded**
  (with the reason, in `log.md`), or **carries no numbers**. Nothing may be left unaccounted
  for. A near-duplicate of an object you already handled — the same infographic for a different
  year, a second table restating the first — still needs its own line: it is precisely the item
  that gets silently skipped, and a reviewer who finds it missing from the log cannot tell
  whether it was read.
- Every row: `L1_role` set; `quantity_type` consistent with `L1_role`; `level_1to5` in
  {2, 3, 4, 5} and matching the `L4`-blank rule; `chain_L2` canonical **and in scope**;
  `geography` explicit; `source_id` resolves in `Sources`.
- No row sits at an out-of-scope stage, and no aggregate row spans one.
- Every row has `source_page`, `source_table_figure`, `value_as_reported`,
  `unit_as_reported`, `conversion_factor_to_t_per_yr`; and
  `value_as_reported × factor == volume_t_per_yr` for all of them.
- Every retired stage-name captured in `source_type_label`, with `type_assumed` set where
  the default was used.
- No two rows share a stage, year and `quantity_type` without their names saying how they
  differ; every restated figure carries its other locations in `also_stated_in`, and both
  sides of a variant pair cross-reference each other.
- No single crop, species or product sits at `L3`, and no figure inherited its `chain_L2`
  from the chapter it was printed in rather than from what it measures.
- No cross-type or cross-stage sums implied; no averaged / merged figures.
- Anomalies split into *variants* and *suspected errors* in the log, the latter with their
  arithmetic evidence stated.
- **(v2.3)** No row carries `geography = Vlaanderen` on a figure the source's text defines as
  covering more than Flanders; no Belgian figure is captured where a Flemish one exists for the
  same quantity; every `Belgie` row cross-references its Flemish counterpart if there is one.
- **(v2.3)** Every row whose printed name states *eetbaar* / *niet-eetbaar* carries
  `voedselverlies` / `nevenstroom` with `type_assumed = FALSE`, whatever the source-wide default.
- **(v2.3)** Every converted row spells its conversion chain out in `source_type_label`, and the
  `conversion_factor_to_t_per_yr` column has an explicit number format so small factors stay
  legible in Excel.
- **(v2.3)** Every aggregate that includes an uncaptured component says so on the row; every
  captured table whose cells were partly dropped is accounted for cell by cell in `log.md`.
- **(v2.5)** `audit_register.py --source S0xx` comes back clean, or every remaining finding is
  named in `log.md` with the reason it is not a defect. In particular: no row naming a product sits
  above L4; no residual nomenclature class is left as a component; every row that totals others
  carries the `AGGREGAAT - ` prefix; `level_1to5` equals the deepest filled commodity column on
  every row; every `AGGREGAAT` row has a line in `aggregate_coverage.csv`.
- **(v2.5)** No processing product is filed under the crop it came from rather than its `Varia`
  sector.
- `destination_index.csv` has at least one row for this source (even if `has_data = no`).
- `streams_export.csv` written; `log.md` appended; `database/hub.md` updated.

## What NOT to do

- Do not fetch the source live — extract only from the archived PDF.
- Do not open the root-level `BIOLOOP_streams_and_sources.xlsx`; only the `register/` copy.
- Do not extract horeca, catering or household figures, nor any aggregate containing them.
- Do not extract destination / collection-route values — index them instead.
- Do not derive a conversion factor the source does not give.
- Do not correct a source's figure, even one you are sure is a typo — record and flag it.
- Do not create Zotero items from PDF DOI extraction — use the `Sources`-row metadata.
- Do not edit `Rollup_check` or `Stream_index` (derived), do not hand-edit `log.html`
  (derived — edit `log.md` and re-render), and do not touch any database table.
- Do not invent structure, fractions, or figures; when the source is silent, leave blank
  or flag.
