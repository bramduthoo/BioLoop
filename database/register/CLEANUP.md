# Closing out `register/` — what stays and what goes

*Written 2026-09-04, when the reviewer asked whether the folder can be cleaned once `FIX_LIST.csv`
is returned. Short answer: yes, and none of it is destructive — the deletions are either derived
files or one-off scaffolding whose result is already committed elsewhere.*

**Do not run any of this until `FIX_LIST.csv` has been decided and applied.** Several of the scripts
below are what applies it.

---

## One prerequisite, and it is load-bearing

`crosswalks/aggregate_coverage.csv` — the reviewer's own registry — still has **42 blank `DECISION`
cells**. `crosswalks/aggregate_coverage_CLAUDE.csv` is a copy of it with all 244 decided, and
**every figure in the overview and the selection is currently built from the copy**, via the
`BIOLOOP_REGISTRY` override.

So before the copy can be deleted, those 42 decisions have to be reviewed and merged into
`aggregate_coverage.csv`. Until then the copy is not scaffolding — it is the live input, and
deleting it silently changes every number. **Merge first, then delete.**

---

## Keep — the corpus and its record

| file | why |
|---|---|
| `BIOLOOP_streams_and_sources.xlsx` | the corpus itself |
| `streams_export.csv` | the git-diffable copy of `Streams`; the committed audit trail |
| `destination_index.csv` | where each source keeps its destination/route volumes |
| `archive/`, `inbox/` | the verified PDFs (gitignored, but the files matter) |
| `dictionaries/` | the three binding vocabularies |
| `CLAUDE.md`, `README.md` | the protocol and the folder's own guide |
| `log.md` | the per-session record |
| `OPEN_GAPS.md` | the gap record |
| `crosswalks/aggregate_coverage.csv` | the human gate the overview reads |
| `crosswalks/GAP_LIST.csv` | the source-hunting worklist — the one output that stays live |
| `migrations/` | already the archive of finished one-offs; it has its own README |

## Keep — the pipeline that turns the corpus into the overview

| file | role |
|---|---|
| `prep_data.py` | workbook + registry → `streams.json` |
| `derive.js` | the derivation: aggregates, variants, coverage |
| `build_overview.py` + `template.html` | → `stream_overview.html` |
| `verify_overview.py` | the 8 arithmetic identities |
| `audit_register.py` | the structural audit, run per source |
| `promote_totals.py` | run per source, per the protocol |
| `make_aggregate_coverage.py` | proposes registry lines when a new source adds aggregates |
| `export_streams.py` | writes `streams_export.csv` |
| `render_log.py` | `log.md` → `log.html` |
| `select_streams.js` | the 80/20 selection |

That is **ten scripts** and it is the whole working set. Everything below is not part of it.

---

## Move to `migrations/` — finished one-offs whose result is already in the data

These are kept for provenance, not for running. `migrations/README.md` already explains the
convention; add a line for each.

- `apply_fixes.py` — applied 2026-09-01
- `crosswalks/GAP_DECISIONS.csv` — the eight gaps, decided and applied 2026-09-03
- `crosswalks/HIDDEN_STREAMS.csv` — **after** its decisions are applied
- `crosswalks/FIX_LIST.csv` — **after** its decisions are applied
- `decisions/gap_decisions_2026-09-03_export.md` — the reviewer's browser export; then delete the
  empty `decisions/` folder

## Delete — scaffolding for the September gap analysis

Each produced an output that is committed elsewhere; none is needed to rebuild the overview.

| file | what it produced | where that output lives now |
|---|---|---|
| `analyse.js` | the first coverage audit | superseded by `select_streams.js` |
| `gap_sweep.py` | the five screens as JSON | the findings are in `OPEN_GAPS.md` and `GAP_LIST.csv` |
| `find_hidden_streams.py` | `HIDDEN_STREAMS.csv` | that CSV, then `FIX_LIST.csv` |
| `make_gap_lists.py` | `FIX_LIST.csv` + `GAP_LIST.csv` | those two CSVs |
| `crosswalks/AUDIT_findings.csv` | a fix sheet | regenerable with `audit_register.py --csv` |
| `crosswalks/aggregate_coverage_CLAUDE.csv` | the decided registry | **only after the 42 are merged** |

**One caveat before deleting `find_hidden_streams.py`.** It is the only check that catches a residual
row sitting above L4 with an ordinary name — `audit_register.py` structurally cannot, because it
matches on names. If the register ever takes another source, that screen has to be re-run. Either
keep it, or fold its check into `audit_register.py` as an eighth check first. **Folding it in is the
better ending** — one script, one place, and the blind spot closed permanently.

## Delete — derived and junk

- `streams.json`, `log.html` — gitignored, rebuilt on demand
- `__pycache__/`, `~$BIOLOOP_streams_and_sources.xlsx` — the lock file is gitignored;
  `__pycache__` is **not**, and should be added to `.gitignore`
- `stream_overview.html` — currently **tracked**, though `.gitignore` carries a commented-out line
  for it. Decide one way: either keep committing it (it is the shareable artefact) or un-comment the
  line and stop. Do not leave it half-committed.

---

## Suggested order

1. Decide and apply `FIX_LIST.csv`; re-run `select_streams.js`, `verify_overview.py`,
   `audit_register.py`.
2. Review the 42 blank cells in `aggregate_coverage.csv`; merge from the `_CLAUDE` copy.
3. Rebuild from the reviewer's own registry with no `BIOLOOP_REGISTRY` override and confirm the
   numbers are unchanged. **This is the check that licenses step 4.**
4. Fold the `find_hidden_streams.py` screen into `audit_register.py`, then move and delete per above.
5. Write the session report per `protocol.md` — hub status, `state.md`, `flags.md` — and commit.

After that the folder is: the workbook, its export, the PDFs, three dictionaries, two registries
(`aggregate_coverage.csv`, `GAP_LIST.csv`), ten scripts, four documents (`CLAUDE.md`, `README.md`,
`log.md`, `OPEN_GAPS.md`), and `migrations/`.
