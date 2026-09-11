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
| `vocabulary/parameters.csv` | the parameter catalogue — 68 rows, and it is **meant to grow** |
| `tools/emit_vocabulary.py` | validates the three CSVs and emits the data migration |
| `SOURCE_HUNT.md` | round 1 of the source hunt: what supplies each of the 16 targets, how far it was checked, and the two that failed |
| `crosswalks/SOURCE_CANDIDATES.csv` | the machine-readable worklist behind it — 21 candidate rows over 16 objects |
| `tools/build_targets.py` | selection deliverable → `round2_targets.csv`, applying the 50 kt rule |
| `tools/build_round1.py` · `tools/round2_data.py` | what was read off each source. **The transcription of record — corrections are made here**, never in the database and never in the page |
| `tools/merge_round2.py` | per-item JSONs → `round2_measurements.csv`, and the status back into the worklist |
| `extraction/round2/<code>.json` | one file per target, written the moment that item is finished — so a session that runs out of budget loses nothing |
| `extraction/round1_*.csv` · `round2_*.csv` | 495 candidate `property_measurement` rows, each with a blank `DECISION` |
| `tools/build_review.py` + `review_template.html` | build the reviewer's page from those CSVs |
| `build/review.html` | the generated page (published as an Artifact; not committed as a deliverable) |
| `crosswalks/` | also holds one crosswalk per harvested source: its parameter and stream names → the catalogue, with the human `DECISION` gate. None yet |

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

## State (2026-09-11) — round 2

**All 35 targets of the 2026-09-11 selection worked through.** `495 candidate rows` over
`24 streams` from `3 sources`, none loaded.

| | streams | t/yr |
|---|--:|--:|
| extracted | 21 | 5.934.397 |
| checked, no usable source | 14 | 2.223.519 |
| **total in scope (>= 50 kt)** | **35** | **8.157.916** |

**73% of the in-scope mass now has composition behind it.** The 27% that does not splits in
two, and the split is the useful part: **six streams have no source** (potato haulm, cauliflower
leaf, sprout stalk, leek and leek leaf, bean haulm, onion skin — all field or vegetable residue,
and all absent from every feed and fuel database), while **four are not waiting on a search at
all** but on a decision about what the object is (`zetmeel-reststroom`,
`aardappel-industrieresidu`, `slachthuisstromen`, `eetbare-slachtafvallen-rood-vlees`).

**The structural finding: there is no vector for a fat stream.** Every parameter in the
catalogue describes a solid. `dierlijk-vet` (145.498 t) needs a fatty-acid profile, free fatty
acids, iodine value and slip melting point, and the catalogue holds none of them because every
source read so far has been a solid. INFOODS already nests fatty acids under *Fat components*,
so it is an extension rather than a redesign — and it is the first item of round 3.

## State (2026-09-09) — round 1

- **Vocabulary loaded:** 28 units · 6 bases · **68 parameters** (57 chemical, 5 physical,
  6 microbiological), across two stacked migrations —
  `20260909120000_biomobi_composition_vocabulary.sql` (the starting core, 62) and
  `20260909150000_biomobi_composition_vocabulary_v2.sql` (+6, added the same day because verified
  sources print them).
- **Verified** by `supabase db reset` against the local stack, twice: the database rebuilds from
  migrations alone, the two migrations stack, and **7 of 11 tables now hold rows**. `source`,
  `geography`, `property_measurement` and `supply_observation` are still empty.
- **Not pushed to live.** Neither is the streams migration that precedes it.
- **No measurements loaded.** Round 1 is extracted but **not in the database**: 180 candidate rows
  over 12 objects, from 3 sources. All 180 validate against the registered vocabulary (0 violations
  on `parameter`, `unit`, `basis` and `stream` codes, checked against the local stack) — that is a
  structural check, not a check of the numbers.
- **Two published pages.** The review surface at
  `https://claude.ai/code/artifact/b7b1fe21-df01-41fe-9e68-8579e72bcbd1`, and a schema explainer for
  the method axis at `https://claude.ai/code/artifact/5b9ec082-29ab-4e5b-ac3b-c9128335c558`. Both are
  generated from this folder; `build/` is gitignored.
- **The numbers are awaiting human review.** They were transcribed off the source pages by a model.
  The review page is at `https://claude.ai/code/artifact/b7b1fe21-df01-41fe-9e68-8579e72bcbd1`;
  marks and remarks come back through its store at `remarks/<stream_code>`.
- **Four objects have no data**: `aardappel-loof` (no source anywhere → F-004),
  `zetmeel-reststroom` (deliberately blocked, gap G-19), and `bloemkool-loof` / `bloemkool-harten`
  (source identified, full text unreachable → F-005).

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
