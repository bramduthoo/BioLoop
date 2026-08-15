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
| **L4** | `L4_ingredient` | The specific ingredient: `Wortel`, `Appel`, `Aardappel`, `Schelvis`. **Blank** when the source reported only at subgroup level. | Blank ⟺ `level_1to5` = 3. |
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
├─ Plantaardig – akkerbouw → Aardappelen, Granen, Suikerbieten, Voedergewassen, …
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

**Using `Gemengd` at L2.** Processing- and distribution-stage aggregates that genuinely mix
plant and animal commodities (`Vlees, vis en gevogelte`, `Dranken`, `Grootdistributie en
supermarkten`, `Catering onderwijs`, …) take `L2 = Gemengd`, `L3` blank, `level = 2`. Reserve
`L2 = Aggregaat` (and the `AGGREGAAT - ` name prefix) for whole-sector totals. Where a sector
total *is* exactly one commodity group — `Tuinbouw`, `Akkerbouw`, `Veehouderij` — use that real
group at L2 with `L3` blank, not `Aggregaat`.

## Maintenance

- The rules above are fixed — change only by explicit decision, recorded in `state.md`.
- Members grow as sources arrive: when a new subgroup / ingredient / fraction first appears,
  add it here in the *same* session (the crosswalk step), then use it.
- Review regularly for drift: the same fraction at inconsistent levels, near-duplicate names,
  an `L4` that should be an `L3`, a `chain_L2` value that leaked in from the commodity axis.
