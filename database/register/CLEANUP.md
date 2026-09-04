# Closing out `register/` — what stays, what goes, and how to run it

*Updated 2026-09-04, after `FIX_LIST.csv` was decided and applied. The prerequisite that used to
block this is now met: `crosswalks/aggregate_coverage.csv` is the official registry, 242 rows,
**0 blank `DECISION` cells**, and the whole pipeline builds from it with no `BIOLOOP_REGISTRY`
override.*

None of the cleanup is destructive. Everything deleted is either a derived file that a script
rebuilds, or one-off scaffolding whose result is already committed elsewhere.

---

## Keep — the corpus and its record

| file | why |
|---|---|
| `BIOLOOP_streams_and_sources.xlsx` | the corpus |
| `streams_export.csv` | the git-diffable copy of `Streams`; the committed audit trail |
| `destination_index.csv` | where each source keeps its destination/route volumes |
| `archive/`, `inbox/` | the verified PDFs (gitignored, but the files matter) |
| `dictionaries/` | the three binding vocabularies |
| `CLAUDE.md`, `README.md` | the protocol and the folder's guide |
| `log.md` | the per-session record |
| `OPEN_GAPS.md` | the gap record, with the two lists' index |
| `crosswalks/aggregate_coverage.csv` | the human gate the overview reads — **now complete** |
| `crosswalks/GAP_LIST.csv` | the source-hunting worklist, the one output that stays live |
| `migrations/` | the archive of finished one-offs; has its own README |

## Keep — the twelve scripts

Ten build the overview and the selection; two are the checks that keep it honest.

| file | role |
|---|---|
| `prep_data.py` | workbook + registry → `streams.json` |
| `derive.js` | the derivation: aggregates, variants, coverage |
| `build_overview.py` + `template.html` | → `stream_overview.html` |
| `export_streams.py` | writes `streams_export.csv` |
| `promote_totals.py` | run per source, per the protocol |
| `make_aggregate_coverage.py` | proposes registry lines when a new source adds aggregates |
| `render_log.py` | `log.md` → `log.html` |
| `select_streams.js` | the 80/20 selection |
| `verify_overview.py` | the 8 arithmetic identities |
| `audit_register.py` | the structural audit, run per source |
| **`find_hidden_streams.py`** | **keep — see below** |
| **`final_check.py`** | **keep — see below** |

### Why `find_hidden_streams.py` stays

`audit_register.py` finds a misplaced row by reading its **name**: check 1 fires on a product code,
check 4 on a leftover-class phrase. **A live residual row sitting at L2 or L3 with an ordinary name
passes every check in that file** and is invisible to the selection. That blind spot cost real mass
in September 2026 — `Melasse op Vlaamse productiesites` and `Meel/schroot uit andere oliehoudende
zaden` both fell through it, and the second was silently halving a 1,15 Mt branch.

This script enumerates the class instead of pattern-matching, so it cannot miss the next one.
**Run it whenever a new source is extracted**, alongside `audit_register.py`. It writes
`crosswalks/HIDDEN_STREAMS.csv` and refuses to overwrite once any `DECISION` is filled.

### Why `final_check.py` stays

It is the closing argument: it partitions **every** claim in the workbook into one disposition and
asserts the property that makes that disposition safe — nothing sampled, nothing assumed. It is what
lets the question *"could anything still be a selectable stream that is not one?"* be answered with
evidence rather than confidence. Run it after any structural change, and after every new source.

---

## Move to `migrations/` — finished, kept for provenance

`migrations/README.md` explains the convention; add a line for each.

- `apply_fixes.py` — applied 2026-09-01
- `crosswalks/GAP_DECISIONS.csv` — the eight gaps, applied 2026-09-03
- `crosswalks/FIX_LIST.csv` — the seven fixes, applied 2026-09-04
- `crosswalks/HIDDEN_STREAMS.csv` — the screen behind F3–F5; **regenerate a fresh one per source**
- `decisions/gap_decisions_2026-09-03_export.md` — then delete the empty `decisions/` folder
- `BIOLOOP_streams_and_sources_pre-FIXLIST_2026-09-04.xlsx` — already there; the pre-fix backup
- `crosswalks/aggregate_coverage.csv.pre-FIXLIST` — the registry as it stood before

## Delete — scaffolding, and derived files

| file | why it can go |
|---|---|
| `analyse.js` | superseded by `select_streams.js` |
| `gap_sweep.py` | its findings are in `OPEN_GAPS.md` and `GAP_LIST.csv`; `final_check.py` covers the recurring part |
| `make_gap_lists.py` | it wrote `FIX_LIST.csv` and `GAP_LIST.csv`; both are committed |
| `crosswalks/aggregate_coverage_CLAUDE.csv` | **now safe** — merged into the official registry |
| `crosswalks/AUDIT_findings.csv` | regenerable: `audit_register.py --csv` |
| `streams.json`, `log.html` | gitignored, rebuilt on demand |
| `__pycache__/`, `~$BIOLOOP…xlsx` | junk — add `__pycache__/` to `.gitignore`, the lock file is already ignored |

**One open call:** `stream_overview.html` is currently **tracked**, though `.gitignore` carries a
commented-out line for it. Decide either way — keep committing it because it is the shareable
artefact, or un-comment the line and regenerate on demand. Do not leave it half-committed.

---

## How to run it

Copy-paste, from the repo root. Nothing here touches the workbook.

```bash
cd database/register
V=../.venv/Scripts/python

# 0 — confirm the state the cleanup assumes
$V final_check.py            # must print PASS
$V verify_overview.py        # must print 8/8
$V audit_register.py         # 24 findings is the known baseline, all Productievolume rows

# 1 — confirm the pipeline no longer needs the working copy of the registry
$V prep_data.py              # note: NO BIOLOOP_REGISTRY override
node select_streams.js 24    # envelope 7.292.982 t, 80% at 13 streams, 90% at 20

# 2 — archive the finished gates
git mv apply_fixes.py migrations/
git mv crosswalks/GAP_DECISIONS.csv crosswalks/FIX_LIST.csv crosswalks/HIDDEN_STREAMS.csv migrations/
git mv decisions/gap_decisions_2026-09-03_export.md migrations/
rmdir decisions

# 3 — delete the scaffolding
git rm analyse.js gap_sweep.py make_gap_lists.py
git rm crosswalks/aggregate_coverage_CLAUDE.csv crosswalks/AUDIT_findings.csv
rm -rf __pycache__

# 4 — the last check: everything must still pass with the folder as it now is
$V prep_data.py && $V verify_overview.py && $V final_check.py && node select_streams.js 24

# 5 — commit
git add -A && git commit -m "register: close phase 2b — archive the gates, drop the scaffolding"
```

**Step 4 is the one that matters.** If it passes, nothing deleted was load-bearing. If it fails,
`git checkout` the file it names and record why it had to stay.

After that the folder is: the workbook, its export, the PDFs, three dictionaries, two registries,
twelve scripts, four documents, and `migrations/`.
