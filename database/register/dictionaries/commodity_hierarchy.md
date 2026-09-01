# BIOLOOP register — commodity hierarchy dictionary (L1 → L5)

*The controlled hierarchy for placing every claim on "what the material is", plus the rule
for how deep a claim goes (`level_1to5`). **The rules per level are fixed**; the **members**
(which subgroups / ingredients / fractions exist) grow as sources are added. Validate new
rows against this every session; change the rules only by explicit decision (note it in
`state.md`).*

## The three axes (reminder)

Every claim is described by three **independent** axes. A valid sum holds two of them fixed
and varies only the commodity level:

1. **What the material is** → this file: `L1_role` + the `L2–L5` commodity ladder.
2. **Where in the chain it arises** → `chain_L2.csv`.
3. **What kind of quantity it is** → `quantity_type.csv` (gated by `L1_role`).

## The ladder — rules per level

| Level | Column | What belongs here | Constraint |
|-------|--------|-------------------|------------|
| **L1** | `L1_role` | The nature of the claim: **Productievolume** (the product itself, a total volume — *not* waste) or **Reststroom** (a residual / side stream). | **Gates `quantity_type`**: Productievolume → only `hoofdstroom`; Reststroom → `agri-food waste` / `nevenstroom` / `voedselverlies`. |
| **L2** | `L2_commodity_group` | Broad group: `Plantaardig - tuinbouw`, `Plantaardig - akkerbouw`, `Dierlijk - vee`, `Dierlijk - vis`, `Gemengd`, `Aggregaat`. | Exactly one L2 per claim. |
| **L3** | `L3_commodity_subgroup` | Subgroup within the group: `Groenten openlucht`, `Groenten beschut`, `Fruit`, `Suikerbieten`, `Granen`, `Melk`, … | **The pivot level**: L4 figures roll up to here in the rollup check. |
| **L4** | `L4_ingredient` | The specific ingredient: `Wortel`, `Appel`, `Aardappel`, `Schelvis`. **Blank** when the source reported only at subgroup level. | Blank ⟺ `level_1to5` = 3. **A single crop, species or product is never an L3** — if the source's "subsector" names one commodity (`aardappelen`, `suikerbieten`), that is an L4 ingredient and the row is level 4; find or add the real subgroup above it. |
| **L5** | `L5_fraction_as_named` | A **genuine physical fraction** of the ingredient, in the source's own words: `loof`, `schillen`, `buitenste rokken`, `stengels`. Two L5s under one L4 (flesh vs peel) are **not** duplicates. | Must be a distinct object, **never a label** for the whole ingredient. |

## `level_1to5` — the depth rule (values 2–5; there is no level 1)

- **5** — the figure is for a *named physical fraction* of a specific ingredient (a distinct part: peel, leaves, stems).
- **4** — the figure is for the *whole ingredient* (`L4` filled; `L5` is a label / whole, not a distinct part).
- **3** — the figure is a *subgroup total* (`L4` blank).
- **2** — the figure is a *commodity-group or sector total*. **This is the ceiling.**
- **No 1.** A single whole-chain grand total for all of Flanders is **not captured**, because
  such a total necessarily mixes in the stages the register excludes — horeca, catering and
  households (see `chain_L2.csv`). The bar is not "too aggregated to be useful"; it is
  "contains material that is out of scope".

**The aggregate rule.** An aggregate row is capturable **iff every chain stage it spans is in
scope**. A primary-sector total (visserij + visveilingen + landbouw + PO's) qualifies; a
"retail + horeca + catering + consumenten" total does not. Where a level-2 aggregate *is*
exactly one commodity group — `Tuinbouw`, `Akkerbouw`, `Veehouderij` — put that real group at
L2 rather than `Aggregaat`.

**Consistency note (this is what broke before):** a distinct part such as `blad- en stengelmassa`
is *always* level 5, on every crop. Do not assign the same fraction level 4 on one ingredient
and level 5 on another.

## Seeded member tree (grows per source)

*Rules above are fixed. This tree is a starting skeleton from what is already in the data;
extend it as sources arrive.*

```
Reststroom
├─ Plantaardig – tuinbouw
│   ├─ Groenten openlucht → Bloemkool, Prei, Wortel, Ui, Spinazie, Boon, Erwt, Spruiten, Witloof, …
│   ├─ Groenten beschut    → Tomaat, Komkommer, Paprika, Courgette, Aubergine, Sla en andijvie,
│   │                        Champignon
│   └─ Fruit               → Appel, Peer, Aardbei, Kers, …
├─ Plantaardig – akkerbouw
│   ├─ Granen                               → Tarwe, Gerst, Maïs, …
│   ├─ Aardappelen en knolgewassen          → Aardappel
│   ├─ Suikerbieten en nijverheidsgewassen  → Suikerbiet, Cichorei, Vlas, Koolzaad
│   ├─ Peulvruchten en eiwitgewassen        → Erwt, Boon, …
│   └─ Voedergewassen
├─ Dierlijk – vee          → Melk, Vlees, Eieren, Rund, Varken, Gevogelte
├─ Dierlijk – vis
│   └─ Vis                 → Schelvis, Wijting, Heek, Steenbolk, Schol, Bot, Schar, Roggen,
│                            Ponen, Kongeraal, Haaien, Andere demersale soorten,
│                            Pelagische soorten, Schaal- en weekdieren
└─ Gemengd / Aggregaat     → sector totals (level 2)

Productievolume → same commodity tree, but hoofdstroom rows only (context, not sidestreams)
```

**Members added 2026-08-14 (S080, OVAM Monitor voedselverlies 2023):**
- `Dierlijk – vis`: the seed line listed `Vis, Schelvis, …` ambiguously. Settled as **L3 = `Vis`**
  with the species at **L4** (a species is an ingredient, not a subgroup). `Schaal- en
  weekdieren` sits under `Vis` for now because the source reports it inside one fish table —
  revisit if a source treats shellfish separately.
- `Dierlijk – vee`: `Vlees` and `Eieren` added as L3 subgroups (alongside `Melk`); the seeded
  `Rund / Varken / Gevogelte` are L4 ingredients under `Vlees`.
- `Groenten beschut`: `Champignon` added as an L4 ingredient (protected cultivation; grouped
  with the glasshouse crops as the sources do).

**Rule change 2026-08-15 (reviewer decision, recorded in `state.md`) — akkerbouw regrouped.**
The seed tree put single crops (`Aardappelen`, `Suikerbieten`) at L3, which contradicted this
file's own L4 examples and left L3 as a mix of real groups (`Granen`) and one-crop entries.
Akkerbouw now has genuine subgroups at L3 — `Granen`, `Aardappelen en knolgewassen`,
`Suikerbieten en nijverheidsgewassen`, `Peulvruchten en eiwitgewassen`, `Voedergewassen` — with
the crop at L4. A source reporting "aardappelen" is therefore **level 4**
(`L4 = Aardappel`), while one reporting "granen" stays **level 3**. The general rule is in the
L4 row of the table above: a single crop, species or product is never an L3, however the
source labels its own subsectors.

**Members added 2026-08-15 (S080 re-run under protocol v2):**
- `Gemengd` (L2, level 2) now also carries the eight **voedingsindustrie subsector groupings**
  the OVAM monitor reports at: `Bakkerij`, `Aardappelen, groenten en fruit`, `Dranken`,
  `Oliën, vetten`, `Suiker, chocolade, bereide maaltijden, enz.`,
  `Deegwaren, dieetvoeding, zetmeel, maalderijen` (plus the already-listed
  `Vlees, vis en gevogelte`), and the two **retail segments** `Grootdistributie en
  supermarkten` and `Detailhandel voeding`. These are NACE-style processing/distribution
  groupings, not commodity groups.
- **`Zuivel` is the exception** among those subsectors: it is unambiguously dairy, so it takes
  `L2 = Dierlijk - vee`, `L3 = Melk`, `level = 3` rather than `Gemengd`. Judgement call —
  flagged in `log.md` for the reviewer.
- **Chain-stage sector totals take `Aggregaat`**: a whole-schakel total (landbouw,
  voedingsindustrie, retail, primaire sector, "landbouw en PO's") is `L2 = Aggregaat` with the
  `AGGREGAAT - ` prefix. A total that *is* one commodity group keeps that group — so the PO's
  groenten-en-fruit totals sit at `L2 = Plantaardig - tuinbouw` (`L3` blank, level 2) and the
  visveilingen totals at `L2 = Dierlijk - vis`, `L3 = Vis` (level 3), without the prefix.

**Using `Gemengd` at L2.** Processing- and distribution-stage aggregates that genuinely mix
plant and animal commodities (`Vlees, vis en gevogelte`, `Dranken`, `Grootdistributie en
supermarkten`, `Catering onderwijs`, …) take `L2 = Gemengd`, `L3` blank, `level = 2`. Reserve
`L2 = Aggregaat` (and the `AGGREGAAT - ` name prefix) for whole-sector totals. Where a sector
total *is* exactly one commodity group — `Tuinbouw`, `Akkerbouw`, `Veehouderij` — use that real
group at L2 with `L3` blank, not `Aggregaat`.

**Members added 2026-08-16 (S091, MONBIO 4.0) — a second, overlapping crop partition.**
MONBIO groups the plant sector by its *own* gewasgroepen, which cut across the OVAM-derived
subgroups already in this file. Both partitions are now members; **they overlap and must never
be summed across each other**. New L3 members:
- `Plantaardig - akkerbouw`: **`Suiker- en zetmeelgewassen`** (suikerbiet + aardappel — spans the
  existing `Aardappelen en knolgewassen` and `Suikerbieten en nijverheidsgewassen`),
  **`Industriele gewassen`** (cichorei, vlas — overlaps `Suikerbieten en nijverheidsgewassen`),
  **`Oliehoudende gewassen`** (kool- en raapzaad, soja, zonnebloem, lijnzaad, maiskiem),
  **`Specerijen`** (cacao, koffie, thee — MONBIO's own group name for the tropical crops).
- `Plantaardig - tuinbouw`: **`Groenten`** (MONBIO does not split openlucht vs beschut, so this
  spans the existing `Groenten openlucht` and `Groenten beschut`).

New L4 members: under `Voedergewassen` — `Voedermais`, `Gras en hooi`, `Voederbiet`; under
`Oliehoudende gewassen` — `Kool- en raapzaad`, `Soja`, `Zonnebloem`, `Lijnzaad`, `Maiskiem`,
`Palm`, `Kokos`; under `Melk` — `Koemelk`, `Geiten- en schapenmelk`; under `Vlees` — `Paard`,
`Schaap en geit`; under `Specerijen` — `Cacao`; under `Vis` — `Vis (alle soorten)`,
`Schaaldieren`, `Weekdieren` (refining the combined `Schaal- en weekdieren`, which stays for
sources that do not split them).

New L5 fractions (all "in the source's own words", per the L5 rule): `stro`, `loof`, `schillen`,
`stokken`, `harten`, `pulp`, `slachtafval (eetbaar)`.

**MONBIO's NACE processing groupings take `L2 = Gemengd`, level 2**, per the S080 rule, with the
same two exceptions applied by commodity: `Vervaardiging van zuivelproducten` →
`Dierlijk - vee / Melk` (level 3), `Vlees- en gevogelteverwerking` → `Dierlijk - vee / Vlees`
(level 3, unambiguously animal meat — the same judgement as `Zuivel`), and
`Aardappelverwerking` → `Plantaardig - akkerbouw / Aardappelen en knolgewassen / Aardappel`
(level 4 — it is exactly one crop).

**Members added 2026-08-16 (S007, MONBIO 3.0).** Only three, because S091's session had already
absorbed the MONBIO vocabulary one edition later: **`Koffie`** as an L4 under `Specerijen`, and
**`Cichorei`** and **`Vlas`** as L4 ingredients under **`Industriele gewassen`**. Note that
`Cichorei` and `Vlas` were already listed under `Suikerbieten en nijverheidsgewassen` in the seed
tree — they now sit under both, which is the direct consequence of carrying MONBIO's overlapping
crop partition. The never-sum-across warning above covers this.

## Maintenance

- The rules above are fixed — change only by explicit decision, recorded in `state.md`.
- Members grow as sources arrive: when a new subgroup / ingredient / fraction first appears,
  add it here in the *same* session (the crosswalk step), then use it.
- Review regularly for drift: the same fraction at inconsistent levels, near-duplicate names,
  an `L4` that should be an `L3`, a `chain_L2` value that leaked in from the commodity axis.

---

## `Gemengd` is retired — `Varia` replaces it (2026-08-31)

`Gemengd` was one flat L2 lump of 100 claims holding three unrelated kinds of row: genuinely new
processing subsectors, MONBIO's Prodcom product rows, and rows that were really *totals* of
commodity groups already in the tree. It is now **empty and retired**. Do not assign it.

**`Varia` (L2, replaces `Gemengd`)** carries processing subsectors that are not a commodity group
of their own. Its L3 members are exactly the five that hold a captured row:

| L3 under `Varia` | Holds |
|---|---|
| `Bakkerij` | OVAM subsector totals; Prodcom 1072 (koekjes, biscuits, wafels) |
| `Dranken` | OVAM subsector totals; NACE 11 aggregates |
| `Olien, vetten` | OVAM subsector totals; Prodcom 1042 (margarine); NACE 10.4 aggregates |
| `Chocolade` | Prodcom 1082; the Flemish chocolate estimate (an `AGGREGAAT of L4` above it) |
| `Zetmeel en zetmeelproducten` | Prodcom 1062 (zetmeel, glucose/fructose, zetmeelafvallen) |

**Two NACE lumps were split**, because a NACE class is not a commodity subgroup: chocolate and
prepared meals are not one class, and neither are pasta, starch and milling.

- `Suiker, chocolade, bereide maaltijden, enz.` → **`Chocolade`**
- `Deegwaren, dieetvoeding, zetmeel, maalderijen` → **`Zetmeel en zetmeelproducten`**

**The uncaptured halves are deliberately NOT members.** `Suiker`, `Bereide maaltijden`,
`Deegwaren`, `Maalderijproducten` and `Dieetvoeding` hold no claim after the reviewer's
exclusions, so creating them would be inventing structure speculatively. They are instead named
in the aggregates' `commodity_coverage` in `crosswalks/aggregate_coverage.csv`, which is also what
protocol v2.3 requires: an aggregate that includes a component the register does not capture must
say so on the row. **Add one as a real member in the session that first captures a row for it.**

**Two members proposed and then withdrawn.** `Mengvoeder en diervoeder` (NACE 10.9) and
`Overige voedingsmiddelen` (NACE 10.84/10.89) were proposed while the crosswalk was being built,
but every row that would have populated them was excluded by the reviewer. Neither exists.

**Retail is not a commodity.** `Grootdistributie en supermarkten` and `Detailhandel voeding` are
collection *channels*, not subgroups. They were withdrawn as L3 members: the rows are now
`AGGREGAAT` rows with `treatment = component_set` in the registry, because each pair sums exactly
to a retail stage total the source also prints standalone (115.862 + 16.220 = 132.082 = C-105).

## A row that totals other rows carries the prefix — no exceptions (2026-08-31)

Protocol v2.4 made the `AGGREGAAT - ` name prefix load-bearing: it decides whether a row **sums**
with its siblings or becomes the **total they are checked against**. Rows extracted before v2.4
predate that rule, and 40 of them — every row the source itself calls a *totaal* — were sitting in
the register as ordinary components and being added to their own parts. That is what produced
coverage ratios of 132% for akkerbouw and 165% for the primary stage.

**When extracting, apply the prefix by this test:** does the figure count material that another
row in this register also counts? If yes it is an aggregate, whatever level it sits at. The
source's own wording (`totaal`, `totale`, `(totaal)`) is usually decisive; where it is not,
arithmetic is — C-043 was promoted because it equals C-005 + C-042 exactly.

`promote_totals.py` applies both tests and is idempotent, so it can be re-run after any extraction.

**Members added 2026-09-01 (S066, ILVO Mededeling 239 - tuinbouw).** Only one, because S066's
crops were already almost entirely present: **`Kool`** as an L4 ingredient under `Groenten
openlucht`. S066 reports it as *"kolen (witte, rode en groene)"* — three colour variants of
sluitkool in one cell.

**Judgement recorded, because v2.5 rule 2 could have gone the other way.** A cell naming several
species is normally a *residual class of the nomenclature* and takes the `AGGREGAAT - ` prefix with
`allocatable = no`. `Kool` is deliberately **not** treated that way: witte, rode and groene kool are
colour variants of one commodity, not a leftover bucket, and none of them exists separately in the
register, so the reviewer's own test — *"a sum of things or a collection of parts which already
exist"* — is not met. If a later source splits them, `Kool` becomes the parent and the three
colours become its L4 siblings, at which point this row should be re-read as an aggregate.

S066's four genuine residual classes **do** take the prefix and `allocatable = no`: `overige
groenten industrie`, `overige groenten vers`, `overige groenten beschut` and `overig fruit`.

**Members added 2026-09-01 (S065, GeNeSys / ILVO Mededeling 165).** The largest single intake of
members so far, because Bijlage 1 lists 33 crops where earlier sources reported 20-odd.

New **L4** under `Groenten openlucht`: `Asperge`, `Broccoli`, `Knolselder`, `Peterselie`,
`Pompoen`, `Raap`, `Schorseneer`, `Selder` (the source's *"Selder (wit en groen)"*),
`Witte kool`, `Rode kool`, `Savooikool`.
New **L4** under `Groenten beschut`: `Veldsla`.
New **L5** fractions, all in the source's own words: `bladmassa`, `bladmassa (groene deel)`,
`stengelmassa`, `buitenste bladeren`, `blaadjes`, `wortelmassa na forcerie`.

**`Kool` now has three siblings, and that is deliberate.** The S066 note above anticipated this:
S066 reports *"kolen (witte, rode en groene)"* as one cell, S065 splits them. Both stay members —
`Kool` is the coarser member for sources that do not split, `Witte kool` / `Rode kool` /
`Savooikool` the finer ones. **They are not an aggregate-and-components pair**: they come from
different sources, and the aggregate machinery only ever operates *within* a source. Never sum
across them.

**Two crops now sit under two L3 parents, following each source's own placement.** `Cichorei` was
already an L4 under akkerbouw (`Suikerbieten en nijverheidsgewassen`, `Industriele gewassen`);
S065 lists it under **openluchtgroenten**, as the root crop for witloof forcing, and that is where
its S065 rows sit. `Courgette` was seeded under `Groenten beschut`; S065 lists it under
**openluchtgroenten** and its S065 oogstrest row follows the source, while its S065 doordraai row
(Tabel 3) sits under `Groenten beschut` where that table puts it. This is the same overlapping-
partition situation the MONBIO gewasgroepen created: **both placements are members, and rows under
them must never be summed across.**

**`Kropsla` was not added.** S065's *kropsla* row uses the existing L4 `Sla en andijvie`, with
"Kropsla" carried in `stream_name_NL`. Adding a variety-level member for one row would deepen the
ladder for no gain; revisit if a source reports lettuce types separately at volume.
