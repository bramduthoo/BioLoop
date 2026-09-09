# BIOLOOP — the candidate stream register (`register/`)

The claim-level corpus of Flemish agri-food side-stream figures, and the pipeline that turns it into
a browsable overview and a selectable stream list. Everything derived here is a **pure function of
the workbook**: it regenerates deterministically after each extraction, so it cannot drift.

**Status: closed 2026-09-04.** The workstream's consolidated account — what it produced, the
decisions that bind future work, the gap classes and the hand-off into BioMobi — now lives one
level up, in **`database/hub.md` → "2b — the candidate stream register"**, with the project-level
items routed to `state.md`, `flags.md` (F-002, F-003) and `charter.md`. This file stays the
technical entry point to the folder; `log.md` stays the per-session record.

## Layout

```
register/
  BIOLOOP_streams_and_sources.xlsx   the corpus — 803 claims, edit only Streams and Sources
  streams_export.csv                 its git-diffable export; the committed audit trail
  destination_index.csv              where each source keeps its destination/route volumes
  CLAUDE.md                          the extraction protocol (v2.6) — the rulebook
  log.md                             the per-session record
  README.md                          this file
  archive/  inbox/                   verified source PDFs (gitignored)
  dictionaries/                      the three binding vocabularies
  crosswalks/                        the live human gates
  tools/                             every script — nothing else runs
  build/                             generated output — never hand-edit, safe to delete
  deliverables/                      the two shareable lists + README.md, which is the METHOD
  migrations/                        finished one-offs, kept for provenance — do not re-run
```

## Regenerate

Run with the repo's venv interpreter (`database/.venv`, which carries `pandas` + `openpyxl`).
From `database/register/`:

```bash
../.venv/Scripts/python tools/build_overview.py          # auto-finds the workbook
../.venv/Scripts/python tools/build_overview.py /path/to/workbook.xlsx
```

macOS / Linux: `../.venv/bin/python tools/build_overview.py`. There is no `python3` on Windows —
use the path above, or `py -3`.

Open `build/stream_overview.html` in a browser; no server needed. Outside the venv any Python 3
with `pandas` + `openpyxl` will do.

## Files

Everything in `tools/` runs again for every new source. Finished one-off migrations live in
`migrations/` and must not be re-run — see `migrations/README.md`.

### The view pipeline

| File | Role |
|------|------|
| `tools/build_overview.py` | Generator. Runs `prep_data.py`, then injects `derive.js` + `build/streams.json` into `template.html` → `build/stream_overview.html`. |
| `tools/prep_data.py` | Reads the `Streams` sheet + `crosswalks/aggregate_coverage.csv` → `build/streams.json`. Honours `DECISION_expert`: a retired claim leaves the derivation entirely. `BIOLOOP_REGISTRY` overrides the registry path, `BIOLOOP_XLSX` the workbook. |
| `tools/derive.js` | Pure, DOM-free derivation (also runnable in Node). Builds the commodity tree, places the aggregates, computes coverage. |
| `tools/template.html` | The view. Placeholders `/*__DERIVE__*/` and `/*__DATA__*/` are filled by the generator. |
| `tools/export_streams.py` | Writes `streams_export.csv` in canonical column order. Importable. |
| `tools/render_log.py` | `log.md` → `build/log.html` (derived, gitignored, never hand-edited). |

### The selection

| File | Role |
|------|------|
| `tools/select_streams.js` | The 80/20 selection. Ranks streams by the largest tonnage any one source gives them, never summing across sources; prints the ranking, per-source coverage, the fraction breakdown and the divergence list. `node tools/select_streams.js 24 --json out.json`. Its header comment states the four method choices. |
| `tools/make_gap_list.js` | **Derives** the gap list from the data as the mirror of the selection: asserted mass minus reachable mass per (place × chain stage), de-nested, merged only within a monitor family. `--min` sets the threshold (50.000 t default), `--json` writes `build/gaps_derived.json`. |
| `tools/make_deliverables.py` | Renders both lists into `deliverables/` as `.xlsx` **and** `.html`, from `select_streams.js` and `make_gap_list.js` output. Layout only — it computes no figure of its own. |

### The checks — run these after every extraction

| File | Role |
|------|------|
| `tools/audit_register.py` | Eight structural checks; exits non-zero while anything is open. `--source S0xx` to scope it, `--csv` to write a fix sheet. **23 findings is the known baseline** (2026-09-08). Twenty are `Productievolume`; three — C-186, C-314, C-501 — are `Reststroom` and always were, so the earlier "all of them `Productievolume`" was wrong. |
| `tools/find_hidden_streams.py` | Catches what `audit_register.py` structurally cannot: a live residual row sitting at L2/L3 with an *ordinary* name, which passes every name-based check and is invisible to the selection. Writes `crosswalks/HIDDEN_STREAMS.csv` as a human gate. |
| `tools/final_check.py` | Partitions **every** claim into one disposition and asserts the property that makes it safe. This is what answers *"could anything still be a selectable stream that is not one?"* with evidence rather than confidence. |
| `tools/gap_review.js` | The mirror question: for every `AGGREGAAT` total, how much is explained by what sits beneath it? Reconciles all 224 aggregate claims against `derive.js`'s own coverage numbers — nothing is recomputed — and dispositions each as resolved / partly / thin / gap / opaque / over / unallocated / shelved. `--min 50000` to scope it, `--json out.json` to feed a review. Run it when the gap list is being revisited, not on every extraction. |
| `tools/verify_overview.py` | Regression test for the derivation — eight arithmetic identities from the sources themselves. Run after any change to `derive.js`. |

### Shaping the register

| File | Role |
|------|------|
| `tools/make_aggregate_coverage.py` | Proposes what each `AGGREGAAT` row totals → `crosswalks/aggregate_coverage.csv` (human-gated). Owns the residual-class rule and the `PHYSICAL_BUNDLE` exceptions to it. `--refresh` re-proposes placements and carries decisions forward. |
| `tools/promote_totals.py` | Gives the `AGGREGAAT - ` prefix to rows that are totals, on name or arithmetic evidence. Idempotent. |

**Source-specificity.** The view pipeline contains **zero** source names and **zero** claim ids: it
is a pure function of the workbook. Per-claim judgement is confined to the `OVERRIDE` and
`PHYSICAL_BUNDLE` tables in `make_aggregate_coverage.py`, two entries in `promote_totals.py`, and
the `D_DISPOSED` table in `final_check.py` — all grouped and commented so a new source does not
inherit them. An explicit `OVERRIDE` entry always beats the residual-class pattern, so a judgement
lives in exactly one place.

## The live human gates

Both in `crosswalks/`, `;`-delimited with a UTF-8 BOM, filled in Excel.

| Sheet | What it is |
|---|---|
| `aggregate_coverage.csv` | 239 rows, **0 blank decisions** — what each `AGGREGAAT` row totals, which parent it attaches to, and whether competing values are variants or a `component_set`. The overview reads this on every build. |
| ~~`GAP_LIST.csv`~~ | **Retired 2026-09-09** to `migrations/GAP_LIST_retired_2026-09-09.csv`. It was hand-maintained, so each round edited the previous version. The gap list is now **derived** by `tools/make_gap_list.js`; the method is written up in `deliverables/README.md`. |

`HIDDEN_STREAMS.csv` appears here only while a screen is open: regenerate it with
`find_hidden_streams.py` when a new source is extracted, decide its rows, apply, then archive it to
`migrations/`. The decision sheets from earlier rounds — `REVIEW_2026-08-31.csv`,
`FIXES_2026-09-01.csv`, `FIXES_ROUND2.csv`, `varia_reclass.csv`, `GAP_DECISIONS.csv`,
`FIX_LIST.csv` — are all applied and live in `migrations/`.

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
node -e 'const D=require("./tools/derive.js"),P=require("./build/streams.json");
const r=D.derive(P.claims,{year:2023,editions:new Set(["OVAM Monitor voedselverlies 2023"])});
const rest=r.roots.find(x=>x.label==="Reststroom");
console.log(rest.coverage, r.unallocated.length, r.severeCount);'
```

## The two deliverables — how they are made

Both are **renderings**, and both are regenerated from the workbook; neither is hand-maintained.

```bash
node tools/select_streams.js 69 --json build/sel_raw.json
node tools/make_gap_list.js        --json build/gaps_derived.json
../.venv/Scripts/python tools/make_deliverables.py build/sel_raw.json
```

That writes four files into `deliverables/` — the selection and the gap list, each as `.xlsx` and
`.html`. They are gitignored: regenerate rather than expect a particular date on disk.

**The gap list is derived, not curated.** It is the mirror of the selection: for every place in the
data, *asserted mass* (the largest total any one source reports there) minus *reachable mass* (what
the selection could actually pick at L4/L5). Three rules keep it honest, and all three came from
getting it wrong first:

- **Reachability follows `select_streams.js` exactly.** A node at or below L4 sits inside a
  selectable stream and is fully reached; above L4 it is the sum of the L4 nodes beneath. Score it
  any other way and every L5 fraction looks like a gap — Maisstro would read as 1,4 Mt unreachable
  while its parent Mais is the #1 selected stream.
- **Nested places are never summed.** Each row carries only the gap its own branches do not already
  carry, so the rows are a decomposition and not a pile; they add up to the stage total by
  construction.
- **Sources merge only within a monitor family.** OVAM's editions merge with each other and
  MONBIO's with each other, but never across: `state.md` (2026-09-01) records that the two are 2,1×
  apart by construction and cannot cross-check each other, so letting MONBIO's processing detail
  cancel OVAM's sector lump would erase a real gap by comparing two different things.

Where a stage's residual belongs to no commodity branch, the sector rows the source gives for it are
listed beneath as **context, never as its composition** — because the only rows that cover it are
**unallocatable by design**, and *an unallocatable aggregate's 0% coverage is a structural artefact,
not a measurement*. `C-094` mixes an L4 (`Aardappel`, under `Aardappelen en knolgewassen`) with two
L3s (`Groenten`, `Fruit`) across two L2 groups, so it has no parent row at one level and part of its
mass is reachable in a different branch entirely; `crosswalks/aggregate_coverage.csv` records this on
the rows themselves (*"unallocatable by design"*, *"the coverage % is a floor"*). Summing such rows
against a residual compares an artefact with a figure — the first version of this list did exactly
that. They are kept because they are the only thing that *names* the largest gap in the corpus, and
they are labelled `structureel onplaatsbaar — context, geen meting`. Rows marked
`parallelle telling` are a second accounting of the same material. **Neither kind is ever summed.**

**A previous version of this list was hand-written in `deliverables/gaps.json`.** That file has been
deleted. A gap list must fall out of the data, or it silently preserves whatever the last one
happened to say.
