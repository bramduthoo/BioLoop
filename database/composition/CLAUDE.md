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
| `20260909150000_..._vocabulary_v2.sql` | +6 parameters, the same day, because verified sources print them: `volatile_matter`, `fixed_carbon`, `hydrogen`, `oxygen`, `chlorine`, `insoluble_ash` |
| `20260910100000_parameter_groups_and_scope.sql` | **DDL, hand-written** — the first schema change since the baseline. Adds `parameter_group` + `parameter.group_code`, and retires the microbiological parameters under a guard on `property_measurement` |
| `20260910100100_..._vocabulary_v3.sql` | regenerated: 10 groups, English parameter names, every parameter grouped |

Verified by `supabase db reset` on the local stack after each: **62 parameters in 10 groups, 0
ungrouped, 0 microbiological.** **Not yet pushed to live** (nor has the streams migration).

**A basis restatement is not always a multiplication.** Phyllis2 prints each determination on `ar`,
`dry` and `daf`; nine of ten reproduce exactly from `dry = ar × 100/(100−moisture)` and
`daf = dry × 100/(100−ash)` — verified to the last decimal on record #3161. **`lhv` does not**, and
that is physics rather than a defect: the net calorific value subtracts the latent heat of the water
actually present, so it is recomputed per basis (`LHV = HHV − 2,443 × (9·H/100 + moisture/100)`,
which reproduces all three printed values). **Never assume a basis column can be rescaled** — that
is why all three are kept in the extraction CSV even though only `dry` loads.

**The growth rule was exercised on the day it was written, and only on evidence.** Every one of the
six additions is a parameter a source that was actually opened prints — four from Phyllis2's
proximate and ultimate analysis, one from its elemental chlorine, one from Feedipedia's insoluble
ash. Phyllis2's ten-oxide ash breakdown was **left out** for the opposite reason: real and citable,
but nothing needs it yet. **Grow on a source, never on a plausible-sounding gap.**

## The review gate — nothing loads before a human has seen it

**Between "a source was read" and "a row exists in BioMobi" there is a review surface, and it is not
optional.** Reviewer instruction, 2026-09-09: *"ik wil via een interface die je bouwt overzichtelijk
kunnen zien welke bronnen je hebt gevonden, voor welke wastestreams deze compositiewaardes vindt +
per wastestream een voorbeeld van hoe diens compositie er nu uitziet ... zodat ik dit manueel
allemaal kan checken."*

The chain is: **source read → `extraction/round<N>_*.csv` → `tools/build_review.py` → an Artifact →
the reviewer's marks and remarks → corrections at the source → loader → `property_measurement`.**

- `tools/build_round<N>.py` holds what was read off each source and expands it into the CSVs. It is
  the transcription of record; a correction is made **there**, never in the database and never in
  the generated page.
- `tools/build_review.py` builds the page as a **pure function of the CSVs plus the parameter
  catalogue**, so a new round is one command and the page cannot drift from the data. It refuses to
  build if a measurement names a parameter the catalogue does not hold.
- Every extracted row carries `transcription = machine`. **The values were read off the source pages
  by a model, not by a person** — the review exists precisely because that is not good enough to
  load. Anything that looked wrong in passing is named in the row's `flag`.
- The reviewer's marks (per row) and remarks (per object) live in the artifact's own store, read
  back with `read_db` on `remarks/<stream_code>`. They are input to the next session, not data.

Round 1: `https://claude.ai/code/artifact/b7b1fe21-df01-41fe-9e68-8579e72bcbd1`.

## The parameter hierarchy — category → group → parameter

`parameter.category` has three values, so 62 parameters sat in two flat buckets. Reviewer request,
2026-09-10. The middle level is `parameter_group`, and it follows the shape the schema already uses
for streams: a reference table naming the axis's vocabulary, plus an FK from the thing classified.

**A group is an analytical partition, not a chemical family** — Weende proximate, Van Soest fibre,
fuel proximate, elemental, minerals, heavy metals. That is deliberate: in this catalogue a
parameter's identity is method-defined, so grouping by method is the grouping that carries
information. It also puts the honest seams on display: `crude_fibre` sits in `proximate-weende` and
`ndf` in `fibre` precisely because they are not comparable.

**Some placements are calls, and any grouping of analytes has them.** `sulphur` and `chlorine` are
in `elemental` rather than `minerals` because that is the tradition our sources report them in;
`total_nitrogen` is in `elemental` while `crude_protein` is in `proximate-weende`, though both come
off the same determination. A group is a presentation axis, not a claim about chemistry.

`group_code` is **nullable** so a parameter can exist before its group is settled — that is what
"the catalogue grows" needs. `emit_vocabulary.py` refuses to emit when a parameter's category
disagrees with its group's.

**Parameter names are English** (2026-09-10, reviewer). `crude_fibre` had been named *Ruwe celstof*,
which is the correct Dutch term for Weende crude fibre, but the catalogue is read against sources
that are almost all English and a translated analyte name adds a step where nothing is gained. Codes
were already English and did not change. **Stream names stay Dutch** — those are the register's own
wording for Flemish materials, which is a different case.

## Microbiological characterisation is out of scope (2026-09-10)

Reviewer decision. The six microbiological parameters registered on 2026-09-09 were retired the next
day, before any measurement referenced them. **Note that `charter.md` listed microbiological
characterisation as in scope** — it was in the first draft and never acted on — so the charter was
narrowed alongside the migration rather than left to contradict the schema. The
`parameter.category` CHECK still admits `microbiological`, deliberately: reversing this is an
`INSERT`, not a migration.

## Two reviewer decisions, 2026-09-09

**A compilation table is an acceptable source, on condition of quality.** This answers the question
`SOURCE_HUNT.md` raised and it unblocks eight of the sixteen round-1 objects. Feedipedia/feedtables
qualifies: it is public, resolvable, and every value carries mean, SD, min, max and `n`. **The
condition binds** — a compilation without a stated sample basis is not the same thing, and the
distinction between a compilation and a primary measurement stays visible on every row through the
source's `kind` field (`compilation` / `primary-indexed` / `primary`).

**A predicted value is carried through, not filtered out.** Feedipedia marks values derived from
prediction equations with an asterisk. Rather than decide in the abstract whether they are
loadable, they are extracted with `predicted = yes` and shown as such in the review, where the
reviewer judges them per case. **The reason: it is not black and white** — a predicted NDF on 241
samples is a different proposition from a predicted gross energy on 2. What must never happen is a
predicted value entering the database *silently*; the column is what prevents that.

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
