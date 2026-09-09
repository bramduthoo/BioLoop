# `composition/` — BioMobi's characterisation layer

*What this folder is and how to run it. The rules and judgement calls live in `CLAUDE.md`.*

## What it is

BioMobi answers two questions about a stream: **how much of it is there** (`supply_observation`,
owned by `streams/`) and **what is it like** (`property_measurement` — this folder). This folder
owns the second: the controlled vocabulary a composition value needs (`unit`, `basis`,
`parameter`), and the harvest of values themselves.

Its targets are fixed by the layer beneath it: the **20 object-grain `stream` rows** registered by
`streams/` from the register's 80% selection. A composition value attaches to one of those codes or
it does not enter.

## Layout

| Path | What it is |
|---|---|
| `vocabulary/units.csv` | the unit vocabulary — 28 rows, `;`-delimited, UTF-8 BOM |
| `vocabulary/bases.csv` | the reporting-basis vocabulary — 6 rows |
| `vocabulary/parameters.csv` | the parameter catalogue — 62 rows, and it is **meant to grow** |
| `tools/emit_vocabulary.py` | validates the three CSVs and emits the data migration |
| `crosswalks/` | one crosswalk per source: its parameter and stream names → the catalogue, with the human `DECISION` gate. Empty until the first source is harvested |

## How to run it

From `database/composition/`, with the shared venv one level up:

```bash
# validate the vocabulary without writing anything
../.venv/Scripts/python tools/emit_vocabulary.py

# emit a NEW migration (it refuses to overwrite an existing file)
../.venv/Scripts/python tools/emit_vocabulary.py --emit-migration \
    ../supabase/migrations/20260909120000_biomobi_composition_vocabulary.sql

# verify: rebuild the whole database from migrations alone
cd .. && supabase db reset
```

**Changing the vocabulary means editing a CSV and emitting a new migration** — never editing an
applied one. Every statement is `ON CONFLICT`-guarded, so migrations stack.

## State (2026-09-09)

- **Vocabulary loaded:** 28 units · 6 bases · 62 parameters (51 chemical, 5 physical,
  6 microbiological), as `20260909120000_biomobi_composition_vocabulary.sql`.
- **Verified** by `supabase db reset` against the local stack: the database rebuilds from
  migrations alone and **7 of 11 tables now hold rows**. `source`, `geography`,
  `property_measurement` and `supply_observation` are still empty.
- **Not pushed to live.** Neither is the streams migration that precedes it.
- **No measurements yet.** The harvest targets the top 10 commodities of the register selection,
  which are 16 of the 20 registered objects.

## The 16 targets

The register ranks **commodities**; BioMobi stores **objects**. The top 10 commodities split into
16 objects, and a composition value must attach to the object whose material was analysed — not to
its commodity.

| # | commodity | t/yr | objects |
|--:|---|---:|---|
| 1 | Mais | 1.456.062 | `mais-stro` |
| 2 | Kool- en raapzaad | 857.931 | `raapzaad-stro` · `raapzaad-schroot` |
| 3 | Aardappel | 855.393 | `aardappel` · `aardappel-loof` |
| 4 | Suikerbiet | 812.224 | `suikerbiet` · `suikerbiet-loof` · `suikerbiet-pulp` |
| 5 | Zetmeel | 284.549 | `zetmeel-reststroom` |
| 6 | Zemelen | 278.865 | `zemelen` |
| 7 | Tarwe | 255.836 | `tarwe-stro` |
| 8 | Lijnzaad | 245.000 | `lijnzaad-schroot` |
| 9 | Bloemkool | 201.311 | `bloemkool` · `bloemkool-loof` · `bloemkool-harten` |
| 10 | Soja | 170.000 | `soja-schroot` |

The four objects outside this round are `slachtafval-niet-eetbaar`, `dierlijk-vet`, `spruiten` and
`spruitstokken` (commodities ranked 11–13).

**Two targets are provisional**, and `CLAUDE.md` says why: `aardappel` absorbs a processing residue
because the corpus names no finer potato object (gap **G-10**), and `zetmeel-reststroom` is named
after the factory it leaves rather than after what it is (gap **G-19**). Composition hung on either
is hung on a name we expect to change.
