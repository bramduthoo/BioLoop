# BIOLOOP register — extraction log

*One entry per source-extraction session, newest first. The running record of what was
extracted, what looked wrong, and whether it has been verified against the archived PDF.
This is local working memory for the register workstream; project-level status still goes to
`database/hub.md` at session end.*

## How to use
- After each source session, add one row to the **Sessions** table.
- If the anomalies for a source need more than a line, write them out under **Anomaly notes**
  keyed by `source_id`, and just point to it from the table.
- `Verified?` flips to `yes` only after a human has checked `Streams` against the PDF in
  `archive/`.

### What an anomaly note must contain

Keep these four headings, in this order, so notes stay comparable across sources:

1. **Variant readings** — the same quantity stated more than once with different values, all
   captured. List them plainly; these may be rounding, revision, or genuinely different
   measurements. **Not** errors, and not to be described as such.
2. **Suspected source errors** — only where there is *arithmetic evidence* (a figure breaks
   its own table's total, or its digit order contradicts every other statement of the same
   quantity). Captured as recorded, never corrected. State the evidence and name the
   `claim_id` so `DECISION_expert` can retire that row.
3. **Deliberate exclusions** — every figure seen and not captured, with the reason: an
   out-of-scope stage (horeca / catering / households), an aggregate containing one, a
   destination or collection-route split, `schenking` / `slib` / `afgeleid product`, a
   non-Flemish geography, a non-convertible unit, or a value that is not a quantity of
   material. Name the tables so a reviewer can see nothing vanished silently.
4. **Judgement calls & new dictionary members** — anything a reviewer should second-guess,
   and every vocabulary member added during the session.

## Sessions

| Date | source_id | source_short | PDF (in archive/) | Claims added | Verified? | Commit | Anomalies / flags |
|------|-----------|--------------|-------------------|-------------:|-----------|--------|-------------------|
| —    | —         | —            | —                 | —            | —         | —      | *(none yet — protocol v2, first source not run)* |

*Note: S080 (OVAM Monitor voedselverlies 2023) was extracted on 2026-08-14 under protocol v1
and produced 310 claims. That run was **discarded** on 2026-08-15 — it captured horeca and
catering, and predated the provenance/unit columns. Its PDF is back in `inbox/` for a clean
re-run under v2. See commit `ad3b36c` for the withdrawn output.*

## Anomaly notes (detail, keyed by source_id)

*(Empty. Add a `### S0xx` heading here with the four headings above once a source needs one.)*
