# `composition/` — conventions and decisions for BioMobi's composition layer

*Local rules for this folder only. Read with, not instead of, `database/CLAUDE.md` and the root
`protocol.md`. Anything here that turns out to bind **every** database session belongs one level
up; anything that binds only the composition work stays here.*
*Created 2026-09-09.*

## What this folder owns

The **characterisation** half of BioMobi: `unit`, `basis`, the `parameter` catalogue, and the
`property_measurement` rows that hang off the `stream` codes `streams/` registered. It does not
own volumes (`supply_observation`) and it does not own stream identity — a composition value that
has no object to attach to is a **gap**, not a licence to invent a stream row.

## The catalogue is a vocabulary, not a required vector

The charter calls composition "a single, fixed-shape vector", and the schema comment on
`parameter` repeats it. **That vector is a model-layer projection built over this catalogue — it
is not a shape any BioMobi row has to fill.** BioMobi stays sparse. A parameter with no row for a
stream means *not measured*; it never means zero, and it is never padded to make a stream look
complete. This is the workstream's "absence means not measured" invariant applied to composition.

The consequence, and it is the point: **uniformity across streams is not required.** One stream may
carry proximate analysis and heavy metals, another only dry matter and pH. Both are correct rows.

## The catalogue grows — that is designed, not tolerated

The 62 parameters registered on 2026-09-09 are a **starting core**, chosen to be what most
composition sources actually report (Weende proximate, Van Soest fibre, sugars and starch, the
elements, energy, a small physical and microbiological set). They were deliberately not derived
from any one source's shape — the mistake 2c made when it let the register deliverable's columns
dictate BioMobi's facets.

**When a source reports something the catalogue does not have, add it.** One row in
`vocabulary/parameters.csv`, then a **new** migration. Never squeeze the value onto a
near-neighbour to avoid the edit — that is exactly the near-duplicate the workstream rule
"register once, then map" forbids, running in the other direction.

## What makes two parameters different, and what makes them the same

**A method-defined quantity is its own parameter.** These are not better or worse measurements of
one thing, they are different things, and collapsing them destroys the value:

- `crude_protein` (Kjeldahl-N × a factor) ≠ `total_nitrogen` (the N itself) ≠ `true_protein`
  (amino-acid sum). Which factor the source used goes in the measurement's `notes`.
- `crude_fibre` (Weende) ≠ `ndf` / `adf` / `adl` (Van Soest) ≠ `total_dietary_fibre` (AOAC).
- `cellulose` and `hemicellulose` are registered **only when a source reports them**. Deriving them
  from `ndf − adf` or `adf − adl` is a calculation, and calculations belong to the model layer.
- `organic_matter` and `volatile_solids`: the *basis* `volatile_solids` exists and is not silently
  equated to `dry_ash_free`. Record the source's term in `notes`.

**A reported chemical form is a parameter, not a unit.** `phosphorus` (as P) and
`phosphorus_p2o5` (as P₂O₅) are separate rows, likewise `potassium` / `potassium_k2o`. The
conversion between them is fixed and well known, which is precisely why it belongs in the model
layer and not in a silent harmonisation on the way in. `property_measurement` has no `reported_as`
column (only `supply_observation` does), so the alternative would be burying the form in prose.

## Units, bases, and the two kinds of missing

- **A unit may differ between measurements of one parameter** — `%`, `g/kg` and `g/100g` are all
  valid rows for `dry_matter`, and the conversion is the model's problem. Record what the source
  printed. `parameter.default_unit_code` is a **hint only**; it never overrides a measurement.
- **Basis is never folded into a unit.** No `%DS`. `unit_code` = `%`, `basis_code` = `dry`.
- **`unknown` and `n.a.` are different claims** and exist for both `unit` and `basis`. The source
  did not say → `unknown`. No basis can apply (pH, C/N, temperature) → `n.a.`. Collapsing them
  turns "we don't know" into "there is nothing to know".
- **`total solids` maps to basis `dry`**, with the source's own wording kept in `notes`. They are
  the same determination; registering both would be the near-duplicate the workstream forbids.
- **`as received` / `as fed` / `wet basis` / `vers gewicht` all map to `fresh`.**

## The value must be measured on the object it is attached to

This is the rule that decides most of the harvest, and it is stricter than it looks.

**A measurement attaches to the `stream` row whose material was actually analysed.** Generic
commodity data cannot stand in for a fraction of it: potato-peel composition is not potato
composition, beet-pulp composition is not sugar-beet composition, rapeseed-meal composition is not
rapeseed composition. The objects were split in 2c precisely because these materials *share no
composition* — undoing that split at harvest time would waste the split.

**Where no object exists, the answer is a gap, not a new stream row.** BioMobi has **no
`aardappelschil` object**: `aardappel` is defined as the tuber (unharvested and rejected) plus a
Prodcom 103113 dried-potato product. Potato-peel composition therefore has nowhere valid to land
until **G-10** closes and the selection is regenerated. Registering a stream to hold literature we
happen to have found would let the composition harvest dictate stream identity — the same error as
letting a deliverable's columns dictate the classification facet.

The two objects that already carry this warning from `streams/CLAUDE.md` are `aardappel` (G-10) and
`zetmeel-reststroom` (G-19, named after the factory it leaves rather than what it is). **Treat both
as provisional targets: a composition value hung on `zetmeel-reststroom` is a value hung on a name
we expect to change.**

## Provenance — every value, one resolvable source

`property_measurement.source_key` is `NOT NULL` and there is no way round it (verified against the
local stack on 2026-09-09: the insert is rejected). Composition sources are **new** literature and
datasets, not the register's eight PDFs, so **F-002 does not block this folder the way it blocks
the volume side** — but the Zotero MCP was again unreachable on 2026-09-09, so BBT keys cannot yet
be checked against the actual library. Source FKs are `ON UPDATE CASCADE`, so a
convention-based key can be renamed to the real BBT key later without touching a measurement.

`source.source_type` is one of `zotero` / `dataset` / `expert` / `internal`. A public inventory
(AgroCycle, Phyllis2, Feedipedia, FoodWasteEXplorer) is a `dataset`; a paper is `zotero`.

## Why the vocabulary CSVs carry no `DECISION` column

The workstream's crosswalk convention — a machine proposal beside a human `include`/`exclude` —
gates **which rows of a source enter the database**. The vocabulary CSVs are not proposals about a
source; they *are* the human-owned artefact, and a `DECISION` column on them would be ceremony.

The gate returns where it belongs: **each source's composition crosswalk** in `crosswalks/`, which
maps that source's parameter names and stream names onto the catalogue and carries the per-row
human decision, `;`-delimited with a UTF-8 BOM. Recorded here because `streams/CLAUDE.md` notes
that a `DECISION` column filled in by the model, not typed by the reviewer, misleads anyone who
later reads the file as evidence of review.

## How to run it

From `database/composition/`:

```
../.venv/Scripts/python tools/emit_vocabulary.py                      # validate only
../.venv/Scripts/python tools/emit_vocabulary.py --emit-migration \
    ../supabase/migrations/<UTCstamp>_biomobi_composition_vocabulary.sql
```

The generator **refuses rather than guesses**: duplicate code, a category the schema's CHECK would
reject, a `default_unit_code` naming no unit, an empty definition, or a missing `unknown` / `n.a.`
row all exit non-zero. It also refuses to overwrite an existing migration file, because an applied
migration is frozen.

Applied so far, and they stack:

| migration | what |
|---|---|
| `20260909120000_biomobi_composition_vocabulary.sql` | the starting core — 28 units, 6 bases, 62 parameters |
| `20260909150000_biomobi_composition_vocabulary_v2.sql` | +6 parameters, the same day, because verified sources print them: `volatile_matter`, `fixed_carbon`, `hydrogen`, `oxygen`, `chlorine`, `insoluble_ash` |

Verified 2026-09-09 by `supabase db reset` on the local stack, after each: 7 of 11 tables hold
rows, 68 parameters. **Not yet pushed to live** (nor has the streams migration).

**The growth rule was exercised on the day it was written, and only on evidence.** Every one of the
six additions is a parameter a source that was actually opened prints — four from Phyllis2's
proximate and ultimate analysis, one from its elemental chlorine, one from Feedipedia's insoluble
ash. Phyllis2's ten-oxide ash breakdown was **left out** for the opposite reason: real and citable,
but nothing needs it yet. **Grow on a source, never on a plausible-sounding gap.**

## Where the harvest stands

`SOURCE_HUNT.md` is round 1 — what supplies each of the 16 targets of the top 10 commodities, how
far each candidate was actually checked, and the four open questions it raises for the reviewer
(chief among them: **is a compilation table like Feedipedia an acceptable source?**, which gates
eight of the sixteen). `crosswalks/SOURCE_CANDIDATES.csv` is its machine-readable worklist.

Two results from it bind this folder:

- **`aardappel-loof` has no composition source at all** — absent from Phyllis2's index, no
  Feedipedia datasheet. At 744.945 t it is the largest component of the #3 commodity. That is a
  **composition gap**, and it is a different kind of thing from the volume gaps on F-003.
- **`zetmeel-reststroom` is blocked and must stay blocked.** Starch-industry side-stream
  composition is well described in the literature and would have been easy to attach — and wrong
  twice: it names a material no source named (**G-19**), and Flanders' starch industry is mostly
  *wheat* starch, so the potato-pulp literature is probably the wrong material as well.
