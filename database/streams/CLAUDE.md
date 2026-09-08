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
chosen — `INSERT`s into `classification_scheme` / `classification_term`, never a migration, and
never a change to these rows. That is the whole point of the three-table design: `scheme` names
the axis, `term` holds its vocabulary (nested via `parent_term_id`), `stream_classification` tags
objects, and a new axis touches none of the existing ones.

## What is judgement here, and therefore open to challenge

**`aardappel` absorbs the processing residue.** Two claims (C-314, C-501) are Prodcom 103113 —
*meel, gries, vlokken, korrels en pellets van gedroogde aardappelen* — a residue of potato
processing that no source in the corpus names as an object. It sits on `aardappel` because objects,
not stages, are rows, and because inventing `aardappelschillen` would put a word in a source's
mouth. **The corpus has no potato-processing object at all** — that is gap **G-10**, the
register's top-priority hunt.

**`zetmeel-reststroom` is named after the factory it leaves**, not after what it is: the source
says only *"afvallen van zetmeelfabrieken" (Prodcom 106220)*. It is the one row that still fails
the object test, kept because there is no better name in the corpus and the tonnage is real
(284.549 t, rank 5). Rename it the moment a source says what the material is.

**`spruitstokken` and `bloemkool-loof` each merge two source names** — GeNeSys's *stengelmassa*
and MONBIO's *spruitstokken*; GeNeSys's *blad- en stengelmassa* and MONBIO's *bloemkoolloof*.
Judged the same material under two nomenclatures.

**Names are cheap to change now and expensive later.** `stream.code` is the primary key every fact
row will reference. The FKs are `ON UPDATE CASCADE`, so a rename is mechanically safe while no
measurements exist — that stops being comfortable once phase 3 hangs composition off these codes.

## The manifest and its gate

`crosswalks/register_streams.csv` — `;`-delimited, UTF-8 BOM (Belgian Excel). One row per object,
carrying its commodity L2/L3, the register claim ids it rests on, its commodity's rank and figure,
its own largest claim, and a human `DECISION`.

- **The loader exits non-zero, naming every offending row, while any `DECISION` is blank or is not
  `include`/`exclude`.** It did refuse the first dry run of each rebuild.
- **The gate is about the *objects*, not about the selection.** The selection was reviewed and
  closed when 2b closed; re-approving it here would be ceremony. What the column actually gates is
  the commodity → object mapping and the judgement rows above.
- **The session filled all cells with `include`** (2026-09-07, redone 2026-09-08 for the object
  rebuild) on the reviewer's instruction in conversation, not by the reviewer typing them.
  Recorded here because the difference matters if anyone later reads the file as evidence of a
  per-row human review.

**The manifest is authored, not generated**, so the loader re-checks it against
`../register/build/streams.json` on every run: each claim must exist, sit under the L4 the manifest
names, be used by exactly one object, and match the recorded largest figure. A retired or
re-levelled claim fails the load instead of drifting silently. `--skip-register-check` exists for
the case where the register's `build/` has not been generated; do not use it to get past a real
disagreement.

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
