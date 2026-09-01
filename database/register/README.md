# BIOLOOP — stream overview (register/)

Interactive, English-language overview of the `Streams` claim register. It is a **pure
function of the workbook** and regenerates deterministically after each extraction — no
manual editing, so it cannot drift.

## Regenerate
Put `BIOLOOP_streams_and_sources.xlsx` in this folder, then run it with the repo's venv
interpreter (`database/.venv`, which already carries `pandas` + `openpyxl`).

Windows (PowerShell or Git Bash), from `database/register/`:
```
../.venv/Scripts/python.exe build_overview.py            # auto-finds the workbook here
../.venv/Scripts/python.exe build_overview.py /path/to/workbook.xlsx
```
macOS / Linux:
```bash
../.venv/bin/python build_overview.py
```
There is no `python3` on Windows — use the path above (or `py -3`), not `python3`.

Open the generated `stream_overview.html` in a browser (no server needed).

Outside the venv it needs any Python 3 with `pandas` + `openpyxl`:
```bash
pip install pandas openpyxl
```

## Files

Everything here runs again for every new source. Finished one-off migrations live in
`migrations/` and must not be re-run — see `migrations/README.md`.

| File | Role |
|------|------|
| `build_overview.py` | Generator. Runs `prep_data.py`, then injects `derive.js` + `streams.json` into `template.html` → `stream_overview.html`. |
| `prep_data.py` | Reads the `Streams` sheet + `crosswalks/aggregate_coverage.csv` → `streams.json`. Honours `DECISION_expert`: a retired claim leaves the derivation entirely. |
| `derive.js` | Pure, DOM-free derivation (also runnable in Node). Builds the commodity tree, places the aggregates, computes coverage. |
| `template.html` | The view. Placeholders `/*__DERIVE__*/` and `/*__DATA__*/` are filled by the generator. |
| `make_aggregate_coverage.py` | Proposes what each `AGGREGAAT` row totals → `crosswalks/aggregate_coverage.csv` (human-gated). Owns the residual-class rule. `--refresh` re-proposes placements and carries decisions forward. |
| `promote_totals.py` | Gives the `AGGREGAAT - ` prefix to rows that are totals, on name or arithmetic evidence. Idempotent. |
| `audit_register.py` | **Run after every extraction.** Seven structural checks; exits non-zero while anything is open. `--source S0xx` to scope it, `--csv` to write a fix sheet. |
| `apply_fixes.py` | Applies `DECISION_fix = ok` rows from any decision sheet in `crosswalks/`. |
| `export_streams.py` | Writes `streams_export.csv` in canonical column order. Importable. |
| `verify_overview.py` | Regression test for the derivation — eight arithmetic identities from the sources themselves. Run after any change to `derive.js`. |
| `render_log.py` | `log.md` → `log.html` (derived, gitignored, never hand-edited). |
| `stream_overview.html` | The generated, self-contained deliverable. |
| `streams.json` | Generated intermediate (gitignored). |

**Source-specificity.** The whole view pipeline — `prep_data.py`, `derive.js`, `template.html`,
`build_overview.py`, `apply_fixes.py`, `export_streams.py`, `render_log.py` — contains **zero**
source names and **zero** claim ids: it is a pure function of the workbook. Per-claim judgement is
confined to the `OVERRIDE` table in `make_aggregate_coverage.py` and two entries in
`promote_totals.py`, both grouped and commented so a new source does not inherit them. An explicit
`OVERRIDE` entry always beats the residual-class pattern, so there is one place a judgement lives.

## The two open review sheets

Both live in `crosswalks/`, are `;`-delimited with a UTF-8 BOM, and are filled in Excel. They are
disjoint on purpose: one reviews *decisions*, the other reviews *defects*.

| Sheet | Rows | Column to fill | What you are deciding |
|---|---|---|---|
| `REVIEW_2026-08-31.csv` | 189 | `DECISION_review` | every provisional decision Claude took while the reviewer was away — exclusions, `AGGREGAAT` promotions, aggregate placements, one override of an explicit human decision |
| `FIXES_2026-09-01.csv` | 103 | `DECISION_fix` | three structural defects in the register itself, found by the integrity audit |

`FIXES_2026-09-01.csv` carries three classes, each with its own evidence:

- **`A-prodcom-level`** (75 rows) — a Prodcom row names a *product*, so it belongs at L4 under its
  subgroup; these sit at L3 with no L4. Pre-existing, from the S091/S007 extractions: the same rule
  was applied to the Prodcom rows that went through `varia_reclass` and never to those filed under
  real commodity groups. Set `level_1to5 = 4` and `L4_ingredient` to the product name.
- **`B-level-mismatch`** (14 rows) — `level_1to5` does not match the columns actually filled.
  Introduced by Claude on 2026-08-31: `level` was set to the level the aggregate *totals*, which
  belongs in `aggregate_coverage.totals_level`, not to the row's own commodity depth.
- **`C-unmarked-total`** (14 rows) — `Nevenstromen en productieresiduen <gewasgroep>` rows that are
  exact totals of the fraction rows beneath them but carry no `AGGREGAAT - ` prefix, so they sum
  with their own parts. `promote_totals.py` missed them because their name never says *totaal*.
  Worth ~2.8 Mt of double counting. Note the two cross-partition cases (C-240, C-421): their
  fractions sit under a *different* L3, because MONBIO's gewasgroepen cut across the OVAM subgroups.

**Round 2** (`FIXES_ROUND2.csv`, 86 rows, `make_fixes_round2.py`). The reviewer's answers to
round 1 showed that "is this Prodcom row at the wrong level?" was three questions in one, so
round 2 asks them separately:

- **`A -> aggregate`** (46 rows) — the name is a *collection*, not a product: `Andere ...`,
  `... en andere ...`, `van alle soorten`, `n.e.g.`, or several species in one cell. Prodcom
  residual categories are nomenclature buckets. These get the `AGGREGAAT - ` prefix, not an L4.
- **`A -> move to a Varia sector`** (8 rows) — the register has two partitions, crops *and*
  processing sectors, and a processing product filed under the crop it came from belongs under the
  sector. Bread is not a cereal; refined sugar is not a beet.
- **`A -> L4`** (13 rows) — genuine single products. The dairy rows here are marked `medium`: they
  also pair two products, but round 1 approved the analogous rows as L4, so they follow that
  precedent rather than a fresh judgement.
- **`B - give the row its real L2`** (12 rows) — re-proposed as the reviewer asked. Setting
  `L2 = Varia` instead of the placeholder `Aggregaat` makes `level 2` mean *"this row sits at L2"*,
  while the level it *totals* stays in `aggregate_coverage.totals_level`.
- **`review-fix`** (7 rows) — the placement corrections written on `REVIEW_2026-08-31.csv`.

Round 2 introduces one new L3 member, **`Varia > Suiker`**, because glucose/fructose/invertsuiker,
refined sugar and melasse are sugars and were sitting under starch or under a crop.

Apply approved rows with `apply_fixes.py` (reads both fix sheets, applies only `DECISION_fix = ok`).

Regenerate either proposal with `make_fixes.py` — it is idempotent and preserves any decision
already entered. **Applying `C-unmarked-total` will drop MONBIO's L1 residual total by roughly
2.8 Mt**, so every coverage figure moves; rebuild the overview afterwards.

## The two axes

**1. The commodity tree.** `L1_role` → L2 → L3 → L4 → L5, built from **component** claims,
which sum with their siblings. Rows shade grey (L1) → white (L5); one level opens per click.
Chain stage = columns. Quantity type is folded into the cell value: agri-food waste, carrying
the inedible/edible split when known.

**2. The aggregate axis.** A row named `AGGREGAAT - …` is not a commodity — it claims *"the
total of these rows is X"*. It therefore **never enters a sum**; it becomes the reported total
that the level below is measured against. This is what makes the coverage line meaningful at
L1 and L2, which previously had no total to divide by.

Each aggregate is described by the level it totals (`AGGREGAAT of L2` should equal the sum of
all L2 rows), the row it attaches to, which entries it covers (**full** or a named **subset**),
which chain stages it spans, and its quantity type. That description lives in the human-verified
`crosswalks/aggregate_coverage.csv`; a blank `DECISION` there means the proposal is used but
flagged in the view as `proposal`.

**Allocation rule.** An aggregate is placeable only when everything it covers sits under **one**
parent row at **one** level. A total spanning two L2 groups (OVAM's *Aardappelen, groenten en
fruit* = potatoes + vegetables + fruit) has no row to hang from, so it goes to the
**unallocated** band at the foot: visible and usable for interpretation, never compared, never
summed.

## Reading the view
- **Coverage line** under every open row: what share of the reported total the level below
  explains. `ok` 95–105% · `partly explained` < 95% · `parts exceed the total` 105–150% ·
  **`⚠ CHECK` above 150%**, which also puts a red dot on the collapsed row and a count in the
  bar above the table, so a bad mismatch is findable without opening every level.
- **`indicative`** — an aggregate with nothing captured beneath it cannot be checked, but it is
  still the best estimate for what it covers, so it is shown and marked rather than scored 0%.
- **Competing values.** Several figures for one row, stage and quantity type are *competing
  definitions* (a Flemish total beside an EU-definition one), never a sum. They are shown as
  their mean and listed individually — untick one to drop it from the average. The exception is
  a set the registry marks `component_set` (collection-route halves that genuinely do sum).
- **Provenance.** Every number says how it was made: no mark = a figure straight from the
  register, `Σ` = summed by the view, `ø` = an average, `Σø` = a sum of averaged parts.
- **Sources are never merged.** Where several report the same entry it is shown as one tagged
  row per source, with an `n src · min–max` badge.
- **Filters:** one reference year at a time and any set of source editions. Coverage is most
  meaningful with a single edition selected — the row says so when more than one is on.
- **80/20 selector:** tick waste (L4/L5) items; the sticky bar shows how many items and what
  share of total waste volume the selection captures.

Exclusions are a reading aid, held in the browser only (best-effort `localStorage`, which is
unreliable on `file://` URLs). Use **copy ids** in the bar to paste a decision into `log.md`.

## Test the derivation without a browser
```bash
node -e 'const D=require("./derive.js"),P=require("./streams.json");
const r=D.derive(P.claims,{year:2023,editions:new Set(["OVAM Monitor voedselverlies 2023"])});
const rest=r.roots.find(x=>x.label==="Reststroom");
console.log(rest.coverage, r.unallocated.length, r.severeCount);'
```
