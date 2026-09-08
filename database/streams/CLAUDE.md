# `streams/` — conventions and decisions for the selection → SQL transfer

*Local rules for this folder only. Read with, not instead of, `database/CLAUDE.md` and the root
`protocol.md`. Anything here that turns out to bind **every** database session belongs one level
up; anything that binds only this transfer stays here.*
*Last updated: 2026-09-08.*

## The one rule that governs this folder

**The register is the truth; this folder is a transfer.** Its input is the selection the register
already produced and a human already reviewed. This folder does not re-open that selection, does
not re-rank it, and — above all — **does not recompute its numbers**.

A first version of the loader did compute per-material tonnages of its own. It disagreed with
`register/tools/derive.js` on Aardappel — 429.871 t against the pipeline's 548.305 t, because
OVAM's *voedselverlies* and *nevenstroom* are additive components there, not alternatives. The
rival derivation was deleted rather than reconciled. **One derivation, and it lives in the
register.** Carry its figure, cite the claim, compute nothing.

## The grain rule — a stream row is an OBJECT

**A stream is a thing you could put in a bag.** If a name only makes sense by saying where the
material came from, it is not an object and must not be a row.

The selection ranks **commodities**; BioMobi stores **objects**. Some commodities are one object
(`Zemelen`, `Dierlijk vet`); others are several, because the register measures physically
different materials under one crop name and they share no composition:

| commodity (rank) | objects |
|---|---|
| Aardappel (3) | `aardappel` · `aardappel-loof` |
| Suikerbiet (4) | `suikerbiet` · `suikerbiet-loof` · `suikerbiet-pulp` |
| Kool- en raapzaad (2) | `raapzaad-stro` · `raapzaad-schroot` |
| Bloemkool (9) | `bloemkool` · `bloemkool-loof` · `bloemkool-harten` |
| Spruiten (13) | `spruiten` · `spruitstokken` |

13 commodities → **20 objects**.

**Chain stage is never part of an object's identity.** Where a material arises is a property of an
*observation* of it, and `supply_observation` already carries geography, year and source for that.
A first version of this transfer made chain stage a stream facet, and it produced stage-named
pseudo-objects — `aardappel-industrie`, `aardappel-primair`, `suikerbiet-primair`,
`bloemkool-primair`, `spruiten-primair`. A potato peel is a potato peel wherever it arises.
`bloemkool` is now **one** object whose claims span field, auction and processor.

**An object's siblings are not summable.** The register's 80/20 arithmetic runs at commodity level
(the largest figure any one source gives a commodity), so adding up `suikerbiet` + `-loof` +
`-pulp` produces a quantity no source supports. Each manifest row carries its commodity's
authoritative rank and figure *beside* its own largest single claim, and the loader totals nothing.

This still dissolves the register's **G-08** "incompatible quantities" problem: *oogstresten* and
*voedselreststromen* of one crop, with spreads up to 50,5×, were measurements of **different
objects** (`spruitstokken` vs `spruiten`), not contradictory measurements of one.

## The classification facet — one scheme, the workbook's own commodity levels

`bioloop-commodity`, built from the register workbook's `l2` / `l3` columns
(`../register/dictionaries/commodity_hierarchy.md`), loaded as a **two-level ladder**: L2 terms
are parents, L3 terms are children carrying `parent_term_id`, and **each object is linked to its
L3 only**. Rolling up to the branch is a recursive walk, not a second stored link — which is what
`parent_term_id` is for, per the schema's own *"Type → Klasse → Subclasse"* comment.

4 L2 terms · 7 L3 terms · 20 links:

```
Plantaardig - akkerbouw   Aardappelen en knolgewassen · Suikerbieten en nijverheidsgewassen
                          Granen · Oliehoudende gewassen
Plantaardig - tuinbouw    Groenten openlucht
Dierlijk - vee            Vlees
Varia                     Zetmeel en zetmeelproducten
```

**One collapse is applied:** the register carries the same L3 under two source nomenclatures —
MONBIO writes `Groenten`, ILVO 239 and GeNeSys write `Groenten openlucht`. `select_streams.js`
drops L3 from its own key for exactly this reason; here they collapse to the dictionary's term,
`Groenten openlucht`. If a source ever reports `Groenten beschut` material, that becomes a second
L3 and this alias must be re-examined.

**Chain stage is deliberately not a facet** — see the grain rule. It arrives with the volumes, on
`supply_observation`.

**Facets are additive.** EWC remains the phase-4 question and enters as a *second* scheme when
chosen — `INSERT`s into `classification_scheme` / `classification_term`, shipped as their own data
migration, needing **no DDL and no change to any row loaded here**. That is the whole point of the
three-table design: `scheme` names the axis, `term` holds its vocabulary (nested via
`parent_term_id`), `stream_classification` tags objects, and a new axis touches none of the
existing ones.

## What is judgement here, and therefore open to challenge

**`aardappel` absorbs the processing residue.** Two claims (C-314, C-501) are Prodcom 103113 —
*meel, gries, vlokken, korrels en pellets van gedroogde aardappelen* — a residue of potato
processing that no source in the corpus names as an object. It sits on `aardappel` because objects,
not stages, are rows, and because inventing `aardappelschillen` would put a word in a source's
mouth. **The corpus has no potato-processing object at all** — that is gap **G-10**, the
register's top-priority hunt, and closing it is what will split this row properly.

**`zetmeel-reststroom` is named after the factory it leaves**, not after what it is: the source
says only *"afvallen van zetmeelfabrieken" (Prodcom 106220)*. It is the one row that still fails
the object test, kept because there is no better name in the corpus and the tonnage is real
(284.549 t, rank 5). **This resolves with gap G-19** (deegwaren / dieetvoeding / zetmeel /
maalderijen) — rename it in a new migration the moment a source says what the material is.

**Both of the above are gap questions, not modelling questions** (reviewer, 2026-09-08). Do not
re-litigate the object model over them: they resolve when **G-10** and **G-19** close, and the fix
arrives as a new migration built from an updated selection.

**`spruitstokken` and `bloemkool-loof` each merge two source names** — GeNeSys's *stengelmassa*
and MONBIO's *spruitstokken*; GeNeSys's *blad- en stengelmassa* and MONBIO's *bloemkoolloof*.
Judged the same material under two nomenclatures.

**Names are cheap to change now and expensive later.** `stream.code` is the primary key every fact
row will reference. The FKs are `ON UPDATE CASCADE`, so a rename is mechanically safe while no
measurements exist — that stops being comfortable once phase 3 hangs composition off these codes.

## The manifest is generated, and the human file is tiny

**The objects are derived, not enumerated.** `tools/build_manifest.py` groups the selected
commodities' claims by the register's own **L5 fraction** field: a fraction (`stro`, `loof`,
`pulp`, `harten`, `stokken`) is its own object; the claims with no fraction are the commodity
itself. That grouping *is* the grain rule, applied by the data. Today it yields **22 raw groups →
20 objects**, and everything a row needs — commodity levels, rank, tonnage, claim ids, geography,
a proposed code and name — falls out of the register with it.

**What a human owns is `crosswalks/object_decisions.csv`: nine rows.** Two fraction merges
(GeNeSys's *blad- en stengelmassa* = MONBIO's *loof*; *stengelmassa* = *stokken*) and seven code
or name overrides, four of which exist because a no-fraction group is really a specific processed
product wearing the commodity's name — the FEDIOL schroot trio, and `zetmeel-reststroom`.

**The generator refuses rather than guesses.** It exits non-zero on a group it cannot name safely
(a no-fraction group whose claims never mention the commodity), a stale decision row matching no
group, or a group spanning several commodity levels. Settle those in `object_decisions.csv` —
**never by editing the generated manifest**, which the next rebuild overwrites.

**What it preserves across a rebuild**, keyed on the object's `code` (stable; the fraction label
is not, because a merge moves it): the `omschrijving` prose and the `DECISION`. It reports which
objects appeared and which vanished. A new object arrives undecided, which blocks the loader.

**The generator is better than the hand-mapping it replaced.** Rebuilding the reviewed 20 objects
reproduced every code, name and description — and found `C-154` (*Voedselreststromen suikerbieten
(totaal)*, 48.662 t), which the hand-built manifest had missed in favour of the smaller `C-178`.
That is the argument for deriving rather than enumerating: a person reading claim lists misses one.

## The manifest and its gate

`crosswalks/register_streams.csv` — generated, `;`-delimited, UTF-8 BOM (Belgian Excel). One row
per object, carrying its commodity L2/L3, the register claim ids it rests on, its commodity's rank
and figure, its own largest claim, and a human `DECISION`.

- **The loader exits non-zero, naming every offending row, while any `DECISION` is blank or is not
  `include`/`exclude`.** It did refuse the first dry run of each rebuild.
- **`fractie` is the register's L5 verbatim, and empty means "the commodity itself".** It is data,
  not a label to invent: an earlier hand-built manifest put descriptive words there (`knol`,
  `biet`, `verwerkingsrest`) which looked like fractions but matched no source.
- **The gate is about the *objects*, not about the selection.** The selection was reviewed and
  closed when 2b closed; re-approving it here would be ceremony. What the column actually gates is
  the commodity → object mapping and the judgement rows above.
- **The session filled all cells with `include`** (2026-09-07, redone 2026-09-08 for the object
  rebuild) on the reviewer's instruction in conversation, not by the reviewer typing them.
  Recorded here because the difference matters if anyone later reads the file as evidence of a
  per-row human review.

**The manifest is generated but committed**, so it can still go stale or be hand-edited; the
loader re-checks it against `../register/build/streams.json` on every run: each claim must exist, sit under the L4 the manifest
names, be used by exactly one object, and match the recorded largest figure. A retired or
re-levelled claim fails the load instead of drifting silently. `--skip-register-check` exists for
the case where the register's `build/` has not been generated; do not use it to get past a real
disagreement.

## The migration is the deliverable; the loader generates it

These rows reach a database **through `database/supabase/migrations/`**, like every other change
in this workstream — `supabase db reset` reproduces them from git alone, `supabase db push`
applies them to live. `tools/load_streams.py --emit-migration <path>` writes that file; the loader
running directly against a DSN is a development convenience, not the route to live.

The chain is: **register selection → `crosswalks/register_streams.csv` (human gate) → generated
migration → database.** Each link is committed, so the whole transfer replays from git.

**When the selection changes, emit a NEW migration; never edit an applied one.** The expected
trigger is a resolved gap — the two judgement rows below both dissolve when their gap closes, and
so will the object list when G-10 finally names a potato-processing stream. Every statement is
`ON CONFLICT`-guarded, so migrations stack: a later one supersedes an earlier value harmlessly.

Two things the generator will not do for you, because both are deliberate acts:

- **Removing an object** dropped from the selection. Write that `DELETE` by hand, knowing
  `stream_classification` cascades on stream delete — and knowing the workstream rule is that a
  loader must never be able to do it.
- **Renaming a `stream.code`.** Safe as an `UPDATE` while no fact row references it (`ON UPDATE
  CASCADE`), which is exactly the window we are in now and will not be after phase 3.

Applied so far: `20260908143000_bioloop_streams_selection.sql` — 20 objects, 1 scheme, 11 terms.
**Not yet pushed to live.** It was regenerated in place once, on the day it was written, after
`build_manifest.py` corrected `suikerbiet`'s largest claim. That is only safe because it had
reached no database but a throwaway local stack: **once a migration has been pushed, or has landed
in another clone, it is frozen** — Supabase records the version and will not re-run an edited
file, so a correction must be a new migration.

## Idempotency — what this loader owns

Its namespace is **the set of stream codes the manifest names, inside the one scheme it declares**
(`bioloop-commodity`). Each run rebuilds exactly those `stream_classification` links in one
transaction, so flipping a `DECISION` to `exclude` withdraws that object's classification rather
than orphaning it.

**It never deletes a `stream` row**, even one flipped to `exclude` — `stream_classification`
cascades on stream delete, and an ingestion script must not be able to destroy classification work.
An excluded object keeps its row, loses its link, and is reported.

Verified 2026-09-08 on the local stack: rebuild from migrations, then consecutive loads holding at
**20 objects / 11 terms / 20 links**, 7 of 11 terms carrying a parent, and the L2 roll-up returning
akkerbouw 12 · tuinbouw 5 · vee 2 · Varia 1.

**The five stage-named rows were removed by rebuilding from migrations, not by the loader** — it
never deletes a `stream` row. They existed only on the local stack and never reached live. Had they
been live, retiring them would have been a deliberate `DELETE` outside this loader.

## What deliberately does not load here

`supply_observation`. A volume row needs `source_key NOT NULL`, and all eight archived register
PDFs still carry a blank `citation_key` (**F-002**); most of the register's claims are also still
`awaiting verification`. The claim → object mapping that load will need is already in the
manifest's `claim_ids` column, so this folder is where that work continues — but it is a separate
loader against `supply_observation`, not an extension of this one. **The chain stage each claim
carries belongs on those rows, not on the objects.**
