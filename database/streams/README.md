# `streams/` — the register's stream selection, turned into BioMobi vocabulary

The one job of this folder: take the **stream selection produced by `database/register/`** and
register it in BioMobi as **object-grain** `stream` rows plus one commodity facet. Nothing else. It holds no
corpus of its own and settles no question the register already settled.

**Input (the truth):** the register's selection — `../register/tools/select_streams.js` and the
dated `BIOLOOP_stream_selection_<date>.xlsx` it feeds in `../register/deliverables/` (those files
are generated and gitignored, so regenerate rather than expect a particular date). Figures are read
from there and never recomputed here.

**The manifest is re-checked against the register on every run**, so a change in the register that
touches one of these objects fails the load instead of drifting. The 2026-09-08 selection-control round
changed 20 claims and added 2, and the check passed unchanged — none of these objects rests on a
touched claim.

**Output:** 20 objects in `stream`, plus the `bioloop-commodity` ladder in
`classification_scheme` / `classification_term` / `stream_classification`.
**No `supply_observation`** — volumes are blocked on **F-002**, and the chain stage each claim
carries belongs on those rows, never on the object.

## Layout

```
streams/
  README.md                      this file
  CLAUDE.md                      the rules and decisions local to this transfer
  crosswalks/register_streams.csv  the human gate: 20 rows, one per object, with DECISION
  tools/load_streams.py          the loader (idempotent; refuses a non-local DSN by default)
  build/                         generated, gitignored, safe to delete
                                 (the migration lives in ../supabase/migrations/)
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

## How this reaches a database

**Through a committed migration, like everything else.** `supabase/migrations/20260908143000_bioloop_streams_selection.sql`
carries these rows, so `supabase db reset` reproduces them from git alone and `supabase db push`
applies them to live. The loader is the **generator** of that file, not a second way in.

```bash
# regenerate the migration after the manifest changes
../.venv/Scripts/python tools/load_streams.py --emit-migration     ../supabase/migrations/<YYYYMMDDHHMMSS>_bioloop_streams_<what-changed>.sql
```

**When the selection changes** — a resolved gap adding, splitting or renaming an object — update
`crosswalks/register_streams.csv`, then emit a **new** migration. Never edit an applied one. Every
statement is `ON CONFLICT`-guarded, so a migration is safe to re-apply, and a later one simply
supersedes an earlier value.

Two things a new migration will **not** do on its own: it cannot remove an object that has been
dropped from the selection (write that `DELETE` deliberately, knowing `stream_classification`
cascades), and it cannot rename a `stream.code` (the FKs are `ON UPDATE CASCADE`, so an `UPDATE`
is safe while no facts reference it).

## Run the loader directly (development only)

```bash
../.venv/Scripts/python tools/load_streams.py --dry-run   # parse + check, touch nothing
../.venv/Scripts/python tools/load_streams.py             # local stack
```

Useful for iterating on the manifest without minting a migration each time. It refuses a non-local
DSN without `--allow-remote`, refuses to run while any `DECISION` cell is blank, and refuses to run
if the manifest has drifted from the register corpus. Re-running is safe: it rebuilds only the
classification links of the codes the manifest names, inside the one scheme it owns, in a single
transaction, and never deletes a `stream` row.

## Status

Committed as a migration and verified on the local stack (2026-09-08): **20 objects, 1 scheme,
11 terms (7 nested), 20 links**, reproduced by `supabase db reset` from migrations alone.
**Not yet pushed to the live project.**

See `CLAUDE.md` here for the object rule, the commodity facet, and the judgement calls this
transfer rests on.
The consolidated account for the workstream is `database/hub.md` → "2c".
