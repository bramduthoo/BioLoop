# `streams/` — the register's stream selection, turned into BioMobi vocabulary

The one job of this folder: take the **stream selection produced by `database/register/`** and
register it in BioMobi as `stream` rows plus classification facets. Nothing else. It holds no
corpus of its own and settles no question the register already settled.

**Input (the truth):** the register's selection — `../register/tools/select_streams.js` and the
dated `BIOLOOP_stream_selection_<date>.xlsx` it feeds in `../register/deliverables/` (those files
are generated and gitignored, so regenerate rather than expect a particular date). Figures are read
from there and never recomputed here.

**The manifest is re-checked against the register on every run**, so a change in the register that
touches one of these 21 streams fails the load instead of drifting. The 2026-09-08 selection-control
round changed 20 claims and added 2, and this loader's `--dry-run` passed unchanged — none of the 21
rests on a touched claim.

**Output:** rows in `stream`, `classification_scheme`, `classification_term`,
`stream_classification`. **No `supply_observation`** — volumes are blocked on **F-002**.

## Layout

```
streams/
  README.md                      this file
  CLAUDE.md                      the rules and decisions local to this transfer
  crosswalks/register_streams.csv  the human gate: 21 rows, one per stream, with DECISION
  tools/load_streams.py          the loader (idempotent; refuses a non-local DSN by default)
  build/                         generated, gitignored, safe to delete
```

## Review the SQL before anything is applied

```bash
cd database/streams
../.venv/Scripts/python tools/load_streams.py --emit-sql build/streams.sql
```

Writes the exact statements the loader will run, in order, as readable SQL, and touches no
database. It is a *rendering* of the loader's plan — do not apply it by hand; run the loader.

Other ways to look at the result once it is loaded locally:

```bash
supabase start          # bring the local stack up (Docker must be running)
supabase db reset       # rebuild the schema from migrations alone
../.venv/Scripts/python tools/load_streams.py            # load into the local stack
supabase db dump --local --data-only -f build/local.sql  # what is actually in there
```

For a clickable view, start the stack **without** `-x studio` and open Supabase Studio at
<http://127.0.0.1:54323>.

## Run it

```bash
../.venv/Scripts/python tools/load_streams.py --dry-run   # parse + check, touch nothing
../.venv/Scripts/python tools/load_streams.py             # local stack
../.venv/Scripts/python tools/load_streams.py --dsn "<live DSN>" --allow-remote
```

The loader refuses a non-local DSN without `--allow-remote`, refuses to run while any `DECISION`
cell is blank, and refuses to run if the manifest has drifted from the register corpus.

Re-running is safe: it rebuilds only the classification links of the stream codes the manifest
names, inside the two schemes it owns, in one transaction. It never deletes a `stream` row.

## Status

Loaded and verified on the local stack (2026-09-07): 21 streams, 2 schemes, 7 terms, 44 links.
**Not yet applied to the live project.**

See `CLAUDE.md` here for why 21 rows and not 13, and for the decisions this transfer rests on.
The consolidated account for the workstream is `database/hub.md` → "2c".
