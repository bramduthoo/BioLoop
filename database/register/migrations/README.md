# Finished migrations — do not re-run

Everything here did its job once, between 2026-08-26 and 2026-09-01, and is kept for **provenance**:
the scripts show how the register was reshaped, and the CSVs record roughly 290 human decisions that
justify the shape it has now. Nothing in the live pipeline imports any of it.

**Do not run these against a new source.** They target claim ids and a vocabulary (`Gemengd`) that no
longer exists. The rules they encoded are now in `register/CLAUDE.md` (protocol v2.5) and enforced by
`audit_register.py`.

## The scripts

| File | What it did |
|---|---|
| `make_varia_reclass.py` | Proposed retiring `Gemengd` for `Varia`, twice — revision 2 split two NACE lumps into `Chocolade` and `Zetmeel en zetmeelproducten` after the first review round. |
| `apply_reclass.py` | Applied that crosswalk to the workbook. Its canonical-order exporter now lives in `../export_streams.py`; the copy here is a thin alias. |
| `apply_exclusions.py` | Wrote 44 exclusions into `DECISION_expert` from the reviewer's crosswalk remarks. |
| `make_fixes.py` | Round 1 of the structural audit (75 + 14 + 14 findings). Superseded by `../audit_register.py`, which runs the same checks generically. |
| `make_fixes_round2.py` | Round 2, after the reviewer's answers showed round 1 had asked three questions as one. |

## The decision sheets

| File | Rows | What the reviewer decided |
|---|---|---|
| `varia_reclass.csv` | 100 | which `Gemengd` claims become `Varia` components, aggregates, or leave the register |
| `REVIEW_2026-08-31.csv` | 189 | every provisional decision Claude took while the reviewer was away — 178 `ok`, 11 `fix` |
| `FIXES_2026-09-01.csv` | 103 | round 1 of the structural fixes — 24 `ok`, 30 `fix`, 49 deferred |
| `FIXES_ROUND2.csv` | 86 | round 2 — 85 `ok`, 1 `skip` |

## What replaced them

Two of the reviewer's remarks in `FIXES_ROUND2.csv` were phrased as principles and became rules:

- *"If the name is a sum of things or a collection of parts which already exist, this will almost
  always be an aggregate."* → `COLLECTION_SIGNALS` in `../make_aggregate_coverage.py`, validated at
  **46/46** against the decisions in that sheet.
- *"We kind of made 2 distinctions in the commodity ladder, with the crops but also some sectors in
  varia."* → placement rule 5 in protocol v2.5.

If a future source raises a case these rules get wrong, fix the rule and re-validate it against the
sheets here — they are the regression set.

## Added at close-out, 2026-09-04

The September gap analysis and the fix round it produced. Same rule: kept for provenance, not for
running.

| File | What it did |
|---|---|
| `apply_fixes.py` | Applied the reviewer's round-1 structural fixes, 2026-09-01. |
| `gap_sweep.py` | Ran the five screens behind the gap analysis (rows above L4, retired rows, production look-alikes, aggregate reconciliation, a 41-stream absence checklist) and dumped each in full. Its recurring part now lives in `../final_check.py`; its findings are in `../OPEN_GAPS.md`. |
| `make_gap_lists.py` | Wrote `FIX_LIST.csv` and `GAP_LIST.csv`. It carries the test that separates them — a bundled name is one selectable stream when the items arise together, and a gap when the bundle hides a distinction only a new source can supply. |
| `GAP_DECISIONS.csv` | 8 gaps, decided and applied 2026-09-03. |
| `FIX_LIST.csv` | 7 fixes, decided and applied 2026-09-04 — the round that recovered the two slaughter-residue streams. |
| `HIDDEN_STREAMS.csv` | The screen behind fixes F3–F5: 49 residual rows sitting above L4, with a proposal per row. Regenerate a fresh one with `../find_hidden_streams.py` when a new source is extracted. |
| `gap_decisions_2026-09-03_export.md` | The reviewer's browser export of the gap-desk decisions. |
| `aggregate_coverage.csv.pre-FIXLIST` | The registry as it stood before the fix round. |
| `BIOLOOP_streams_and_sources_pre-FIXLIST_2026-09-04.xlsx` | The workbook before the ten fix-list edits. |
