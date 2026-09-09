# The composition source hunt — round 1, the top 10 commodities

*Result of the 2026-09-09 session. One entry per target object: what would supply its composition,
how far that was actually checked, and what is still unsourced.*
*This file is a **worklist**, not data. Nothing below has been loaded.*

## How to read the "checked" column

The register's own discipline applies here: **checked-and-empty is recorded, never discarded**, and
a candidate that was merely *named* must stay distinguishable from one that was *opened*.

- **inspected** — the record or table was fetched and its parameter list read verbatim.
- **listed** — the source's own index confirms an entry for this material exists, but the entry
  itself was not opened.
- **named** — the source plausibly covers it and nothing was verified.
- **absent** — the source's index was searched and the material is **not** in it.

## The three databases that carry most of this round

**Phyllis2** (TNO, `phyllis.nl`) — physico-chemical composition of lignocellulosic biomass. **One
record = one literature reference**, cited on the record, with XLSX and PDF export. Verified on
record #3161 (wheat straw): proximate (moisture, ash at 550 °C, volatile matter, fixed carbon),
ultimate (C, H, O, N, S), Cl, LHV and HHV, K and Na, and a full ash-oxide breakdown, reported on
**three bases at once** — as received, dry, and dry-ash-free.

*Consequence for us:* its provenance model is the cleanest of the three (a record names its own
paper, so `source_key` is unambiguous), but its parameter set is **fuel-oriented**. It reports no
Weende and no Van Soest fibre at all. It supplied four of the six parameters added to the catalogue
this session, and its ash-oxide block is a further ten that were **deliberately not added** until a
harvest actually needs them.

**Feedipedia / feedtables.com** (INRAE · CIRAD · AFZ · FAO) — feed materials. Verified on the
rapeseed-meal datasheet: dry matter, crude protein, crude fibre, NDF, ADF, lignin, ether extract,
ash, insoluble ash, starch (polarimetric *and* enzymatic), total sugars and gross energy — each
with **mean, SD, min, max and n**. That maps almost one-to-one onto the catalogue, and onto
`property_measurement`'s `sd`, `n_samples`, `value_min` and `value_max`.

*Two things about it need a reviewer decision, and they are in the open questions below:* it is a
**compilation**, not a primary measurement, and it marks **predicted values with an asterisk** —
values derived from prediction equations rather than measured.

**FoodWasteEXplorer** (EuroFIR, `foodwasteexplorer.eu`) — confirmed **live and free** on
2026-09-09, searchable by food / side stream / component, with export for offline analysis.
~27.069 data points from peer-reviewed papers and grey literature. Its examples are
processing-side streams (apple pomace, brewer's grains, citrus pulp, grape marc, olive cake), so it
is likely strong on our `-schroot` and `-pulp` objects and weak on field residue.

## Per-object result

| # | object | material | best source found | checked |
|--:|---|---|---|---|
| 1 | `mais-stro` | maize stover | Phyllis2 #704 *corn stover*, #517 *corn stalks*, #1030 *maize stalk straw* · Feedipedia *Maize stover* (node 16072) | listed |
| 2 | `raapzaad-stro` | rape straw | Phyllis2 #3131 *Rapestraw*, #3162 *Rape stalk* | listed |
| 2 | `raapzaad-schroot` | rapeseed meal | **Feedipedia node 52** — full table read | **inspected** |
| 3 | `aardappel` | rejected / unharvested tubers | Feedipedia *Potato tubers* (node 547) | listed |
| 3 | `aardappel-loof` | potato haulm | **nothing found** — see below | **absent** |
| 4 | `suikerbiet` | rejected beet | Feedipedia *Sugar beet roots* (node 535) | listed |
| 4 | `suikerbiet-loof` | beet tops and leaves | Feedipedia node 709 *Sugar beet tops* + node 11835 *Beet leaves and tops, fresh* · Phyllis2 #1053 *beet tail and beet green* | listed |
| 4 | `suikerbiet-pulp` | exhausted beet pulp | Feedipedia node 710 *pressed or wet* · Phyllis2 #1054 *beet pulp*, #2365 *beet pulp dried* | listed |
| 5 | `zetmeel-reststroom` | **undefined** | **blocked — see below** | n/a |
| 6 | `zemelen` | wheat bran | Feedipedia *wheat bran* · **absent from Phyllis2** | listed / absent |
| 7 | `tarwe-stro` | wheat straw | **Phyllis2 #3161** — full record read; also #945, #991, #1271, #1368, #2038, #3201 · Feedipedia *Straws* (node 60) | **inspected** |
| 8 | `lijnzaad-schroot` | linseed meal | Feedipedia node 735 | listed |
| 9 | `bloemkool` | rejected cauliflower | Phyllis2 #1564, #1565, #1566 · food-composition tables · FoodWasteEXplorer | listed |
| 9 | `bloemkool-loof` | cauliflower leaves | *Potential of Recycling Cauliflower and Romanesco Wastes in Ruminant Feeding* (PMC7459492) — reports **leaves, stems and florets separately**, DM < 10%, CP 19,9–33,0%, sugars 16,3–28,7%, NDF 21,6–32,3%, ME 9,3–10,8 MJ/kg DM · *Variation in the Accumulation of Phytochemicals … Aerial Parts of Cauliflower* (PMC8533432) | named |
| 9 | `bloemkool-harten` | cauliflower stems | the same two papers, stem fraction | named |
| 10 | `soja-schroot` | soybean meal | Feedipedia, oil-processing by-products group | named |

**Twelve of sixteen objects have a concrete, named candidate. Two are inspected end to end. Two
have no usable source at all, and for opposite reasons.**

## The two that failed, and why they are different problems

**`aardappel-loof` — genuinely unsourced.** Potato haulm is **absent from Phyllis2's index** (which
was searched, not assumed) and has no Feedipedia datasheet. It is not a small target: the register
sizes potato haulm at 744.945 t, the single largest component of the #3 commodity. It is also the
one field residue that is chemically desiccated before harvest, which is a reason a feed database
would not carry it. **This is a real composition gap and belongs on the F-003 worklist as one**,
distinct from the volume gaps already there.

**`zetmeel-reststroom` — blocked, and must stay blocked.** The object is Prodcom 106220,
*"afvallen van zetmeelfabrieken"*, and no source in the register says what the material is — that
is gap **G-19**. Composition data for starch-industry side streams *does* exist (potato pulp,
potato fruit juice, potato fibre, potato protein concentrate are all well described in the
literature), and it would have been easy to hang it on this row. **It would have been wrong twice
over:** it puts a material name in a source's mouth, and Flanders' starch industry is
predominantly *wheat* starch, so potato-pulp figures are probably the wrong material as well as an
unlicensed guess. **Leave the row empty until G-19 names it.**

## What the hunt changed about the catalogue

The growth mechanism was used the day it was built, and only on parameters a verified source
actually prints:

| added | why | from |
|---|---|---|
| `volatile_matter`, `fixed_carbon` | the proximate pair every fuel-oriented record reports. `volatile_matter` is **not** the `volatile_solids` basis and not organic matter | Phyllis2 |
| `hydrogen`, `oxygen` | complete the ultimate analysis beside the C, N and S already registered | Phyllis2 |
| `chlorine` | total Cl from elemental analysis. Registered **beside** `chloride`, not instead of it — water-soluble chloride is a different determination | Phyllis2 |
| `insoluble_ash` | HCl-insoluble ash residue, a soil-contamination measure feed tables print next to crude ash | Feedipedia |

**Deliberately not added:** Phyllis2's ten-oxide ash breakdown (SiO₂, K₂O, CaO, MgO, Na₂O, P₂O₅,
Fe₂O₃, Al₂O₃, TiO₂, SO₃ as % of ash). Real and citable, but nothing needs it yet, and a catalogue
that grows on speculation is the thing the "starting core" was designed against.

## What this round says about the four sources the hub had queued

- **FoodWasteEXplorer** — **live, free, exportable.** Promote it from "evaluate" to a first-round
  source for the `-schroot` and `-pulp` objects.
- **FOWCUS (2025, Nature Scientific Data)** — **it is not a composition source, and the hub's entry
  should be corrected.** It covers ~280 commodities indexed to FAOSTAT, and what it quantifies is
  the **mass fractions of products and by-products** across the chain, not their chemistry. That
  makes it a **conversion-factor source for the volume side** — exactly the "volumes attach upward
  via conversion factors" mechanism the workstream rules describe — and it should be re-filed
  under `streams/`, not here.
- **AgroCycle** — could not be confirmed accessible. The concrete thing found in its place is
  **AGRIMAX D1.2, *Mapping of AFPW and their characteristics*** (direct PDF), which is the same
  kind of artefact from a sibling H2020 project.
- **OVAM Inventaris Biomassa** — untouched this round; it is a volume source, not a composition one.

## Open questions this hunt raises (for the reviewer)

1. **Does BioMobi accept a compilation table as a source?** Feedipedia/feedtables is curated,
   citable, versioned and states its `n` — but it is an aggregation of other people's
   measurements, which is close to the "secondhand provenance" that got the legacy Excel abandoned
   in 2a. The difference is real (it is public, resolvable and carries sample counts), but the call
   is the reviewer's, and it decides most of this round. If yes, `source_type = 'dataset'` and one
   `source` row per database, or per datasheet.
2. **Feedipedia marks predicted values with `*`.** Those are outputs of prediction equations, not
   measurements. They must either be excluded at the crosswalk gate or loaded with the fact stated
   — and if loaded, "recorded as predicted" needs a home, which today can only be `notes`.
3. **Polarimetric vs enzymatic starch.** Feedipedia prints both for one feed. Under this folder's
   own rule a method-defined quantity is its own parameter, which would mean splitting `starch` in
   two. The counter-argument is that the analyte is genuinely the same, unlike crude vs true
   protein. **Left undecided** rather than settled by the session that noticed it.
4. **Two Phyllis2 records of one material are two sources, not two readings to average** — that
   follows from "record what the source said" and needs no decision, but it means `tarwe-stro` will
   carry seven dry-matter rows, not one. Worth confirming that is what is wanted before the first
   load.

## Next, in order

1. **Settle open questions 1 and 2** — they gate whether Feedipedia is harvestable at all, and
   Feedipedia is the source for eight of the sixteen objects.
2. **Harvest `tarwe-stro` from Phyllis2 as the pilot.** It is the object whose source is fully
   inspected, its provenance is unambiguous (one record, one paper), and it will exercise the
   whole path: `source` rows → crosswalk with a `DECISION` gate → loader → `property_measurement`.
   It also forces the three-bases question immediately, which is the right thing to hit first.
3. **Raise `aardappel-loof` as a composition gap** on F-003, separately from the volume gaps.
4. **Re-file FOWCUS** under the volume side.
