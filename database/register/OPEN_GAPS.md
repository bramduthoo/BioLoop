# BIOLOOP register — open gaps

*Created 2026-09-03, from the coverage audit at 801 claims / six extracted sources.
**Rewritten the same day** after a systematic sweep of the whole corpus — every residual row, every
aggregate, every chain stage, an absence checklist of 41 named Flemish side streams, and all 91 rows
of the `Sources` sheet.*

**How to use this file.** One entry per gap. A gap leaves this file when either (a) a source is
extracted that resolves it, or (b) it is fact-checked and turns out not to be a gap — in which case
the entry stays with its status flipped to `closed`, so the check is not repeated. Do not delete
entries.

## How the list was last checked — the gap control of 2026-09-08

Every `AGGREGAAT` row in the corpus (224 of them) was reconciled against what the register captured
beneath it, with the 95 residual aggregates ≥ 50.000 t/yr reviewed one by one
(`tools/gap_review.js`; console at
`https://claude.ai/code/artifact/9f9bec09-dd33-48e6-af8a-7328da51fc9d`), then reviewed again by the
reviewer on 2026-09-09, which found four defects in the coverage layer and three "gaps" that do not
exist. **The list survived**: no entry turned out to be imaginary, and nothing large surfaced that is
not already named here. Four things changed how it should be read.

1. **A total can be resolved by its SIBLINGS, not only by its children.** `derive.js` scores an
   aggregate against the node's children only, so `C-043` (*Voedselreststromen aardappelen*,
   548.305 t) — which is exactly `C-005` + `C-042` sitting beside it — scored 0% and read as
   *"nothing beneath it"*. Eleven aggregates were mis-read this way. **Before calling a total
   unexplained, check its siblings.**
2. **Every "parts exceed the total" was one artefact, and it is now settled.** The 308.000 t
   niet-geoogste aardappelen of 2023 are reported by OVAM both inside and outside its totals, and the
   registry averaged the pair as if two scopes were two measurements — producing a denominator the
   source never printed (akkerbouw: 423.389 t). **Reviewer decision, 2026-09-09: the incl. reading is
   the basis**, because the unharvested potatoes sit in the tree as a component (C-005), so the total
   that includes them is simply the sum of the parts. The four excl. totals (C-044, C-049, C-075,
   C-076) are parked with `allocatable = no` — still in the corpus as the source's second reading,
   but steering nothing. **Twelve rows became two, and coverage is now exactly 100% at akkerbouw and
   landbouw.** The two that remain, C-004 and C-111, are the *primary-sector* totals and they are
   over by **exactly 308.000 t**: those are `ingezameld` figures, and potatoes never harvested were
   never collected. Explained to the tonne — leave them.
3. **"Unallocated" hides two different states.** A row the derivation *could not place* is not a row
   the registry *deliberately shelved*. `C-532`/`C-342` (perskoeken, 1,35 / 1,02 Mt) are the largest
   rows in the corpus that look like gaps and are not: they are **98,1%** and **88,7%** of `C-524` /
   `C-335`, i.e. two measurements of one quantity — Prodcom 104141 against the FEDIOL crush statistic —
   and the source itself uses the FEDIOL table for its totals. Promoting them double-counts.
4. **A total can also be resolved ACROSS PARENTS, and no rule can find that.** The `suiker en
   chocolade` sector total is not 12-14% explained but **~100%**: melasse (`Varia > Suiker`) +
   bietenpulp (`Plantaardig - akkerbouw > Suikerbieten`) = 394.455 against a printed 394 kton. Beet
   pulp is a sugar-industry residue the register files under the *crop*, so the two explaining rows
   sit under different parents and only domain knowledge connects them. Held as a small,
   human-confirmed `CROSS_PARENT` table in `gap_review.js`, deliberately not automated.

**Where the gap mass actually is:** after the 2026-09-09 corrections, **7,1 Mt** sits behind a total
with too little or nothing beneath it — down from 11,1 Mt, because the meat sector turned out to be
~90% explained and the sugar/chocolate total ~100%. What remains is concentrated in the food industry
and retail: G-01, G-03, G-10 and G-19.

**Two coverage defects were fixed in the process, and both had been overstating gaps.** `displayOf`
folded the summed quantity-type columns of a roll-up, which discards every child that reports a
*different* type than its sibling — on the `Vlees` node it returned 145.498 t (Dierlijk vet alone)
instead of 481.266 t, scoring a sector total at 23% when it is 76%. And a quantity-type aggregate was
being scored against the whole node's folded figure rather than its own type. Both are fixed;
`verify_overview.py` stays 8/8 and the stream selection did not move.

## The two classes

Every gap below is one of two kinds, and they need opposite responses:

- **Class A — hiding in the current data.** The figure is already in the register but the selection
  cannot see it, because it sits above L4, carries the wrong marker, or is parented in the wrong
  branch. **No new source will help.** These are decided in
  `crosswalks/HIDDEN_STREAMS.csv` and applied.
- **Class B — not in the corpus at all.** No source the register holds measures this. **Only a new
  source will help**, and the entry names which one.

The distinction matters because they were being confused: the first coverage audit reported
*"the food industry has no L4/L5 detail"* as one 2 Mt data gap, when part of it was placement
(class A) and the rest is five separate, differently-sourced data gaps (class B).

## How the sweep was run

Five screens over `streams_export.csv`. The script that ran them, `gap_sweep.py`, is archived in
`migrations/` — its recurring part now lives in `tools/final_check.py`, which runs the same
partition on every claim and asserts it. So this file's claims can be re-derived from the
workbook rather than trusted. The browser version of the same output, with the
raw tables, is the **Gap Register** artifact at
`https://claude.ai/code/artifact/4a899558-975e-400e-a69b-3d277cc9b5d2`.

The screens:

1. every **live residual row above L4** without an `AGGREGAAT - ` prefix — 49 rows, 2.367.761 t
   (`find_hidden_streams.py`);
2. every **retired row**, checked for anything large being lost by mistake — nothing was;
3. every **`Productievolume` row whose name reads like a residual** — 30 hits, all false positives,
   so the "waste filed as production" hypothesis is **closed**;
4. every **aggregate** reconciled against the components under it, per source;
5. an **absence checklist** of 41 named Flemish agri-food side streams, asked of the whole workbook
   in any role and any status.

Screens 1 and 5 are what produced almost everything new below.

## The mechanism behind most of class B

**MONBIO's food-industry residual detail is exactly the set of Prodcom product codes that happen to
name a waste or by-product** — 106132 gries, 106220 zetmeelafvallen, 108114 melasse, 110210 bostel,
101150 dierlijk vet, 101240 slachtafval van gevogelte — plus one FEDIOL crush table for oilseed
meal. **A side stream with no such code is invisible to MONBIO no matter how large it is.** That is
why cacaodoppen and potato peel are absent while bostel and zemelen are present, and it
predicts where to look: not another monitor edition, but a sector source that carves by *process*
instead of by product code.

**Correction, 2026-09-08 — whey is not an instance of this mechanism, and was the example used to
state it.** `Prodcom 105155 "Wei"` **exists** and is printed in both MONBIO editions; its value is
`C`, confidential. That is a *suppressed cell*, not a missing code, and the two need opposite
responses: a suppressed cell is closed by a data request or a sector source that publishes the same
quantity, while a missing code needs a source that carves by process. The whey tonnage itself was
never absent either — 49.722 t (2018) is printed in S091 Tabel 65 and S007 Tabel 47 and is now
captured as C-802/C-803; see G-09. **Before citing this mechanism for a stream, check whether the
code exists and is suppressed.**

OVAM's monitors have the mirror-image limit: they publish the food industry at **subgroup level and
nothing finer** (`Dranken`, `Bakkerij`, `Oliën en vetten`, `Aardappelen, groenten en fruit`), so
every OVAM food-industry figure lands in class B by construction.

---

## G-01 · Retail & grootdistributie — 132.082 t, zero rows below sector level

**Status:** open · **Kind:** missing data · **Size:** 132.082 t/yr (OVAM 2023)

**Evidence.** All **17** retail rows in the register are `AGGREGAAT` at level 2. `C-105` gives the
stage total (132.082 t), `C-103` grootdistributie (115.862) and `C-104` detailhandel (16.220), plus
the voedselverlies/nevenstroom splits and the OVAM 2020 equivalents (`C-203`…`C-214`). **Not one row
at any commodity level, in any source.**

**Why it is a gap.** Retail waste is not evenly spread across the shelf — it concentrates in a few
specific, well-known product groups: **bakery goods, bananas and other soft fruit, ready meals,
fresh produce nearing date**. Those are large, and they are exactly the kind of narrow, high-volume
stream BioMobi is meant to select. Reporting the stage only as one number hides all of it.

**What would close it.** A source with retail waste resolved by product group. Candidates already in
the `Sources` sheet, none yet queued:

- **S067** — Comeos, voedselreststromen retail België 2015. The 64.271 t figure S010 cites, which no
  register source owns.
- **S035** — Foodsavers Vlaanderen / distributieplatformen (flagged destination-side).
- **S041** — Eurostat `env_wasfw`, NACE G47 retail, Belgium only.

---

## G-02 · Producentenorganisaties / veilingen — 15.189 t looks too small to be true

**Status:** open · **needs fact-check before it is treated as a gap** · **Size:** 15.189 t/yr (OVAM 2023)

**Evidence.** OVAM reports the whole PO/auction stage at level 2 only: `C-087`–`C-089` (S080,
15.189 t) and `C-186`–`C-188` (S002, 15.954 t). The only L4 detail anywhere in the register is
**S065's seven auction rows totalling 5.190 t** (`C-769`–`C-775`), and those are 2012 doordraai at
**three** auctions that applied for EU intervention support — not all Flemish auctions, and fruit
was omitted by the source as negligible.

**Why it may be a gap.** 15.189 t for the entire Flemish auction and producer-organisation layer is
implausibly small next to 3,4 Mt at primary production and 1,7 Mt at the food industry. Two readings,
and they lead to opposite conclusions:

1. **The number is right.** Doordraai is genuinely small because the GMO intervention regime is a
   crisis instrument, most surplus is sold rather than withdrawn, and unsold produce is often left
   with the grower and counted at primary production instead. Then this is **not a gap** and the
   entry closes.
2. **The number is a floor.** It counts only EU-subsidised withdrawal, missing everything the
   auctions reject on quality, sort out, or route straight to processing. Then the real figure is
   materially larger and the stage is badly under-measured.

**What would settle it.** Read S065's §5.2 method note against OVAM's, and check one auction's own
annual figures (VBT, or a single auction's jaarverslag) against the 15.189 t. **Do this before
commissioning any new extraction for this stage** — it is a cheap check that decides whether there
is a gap at all.

---

## G-03 · Voedingsindustrie — 1,7–2,2 Mt of waste, nothing in the 80/20 selection

**Status:** open · **Kind:** missing data (partly), granularity (partly) · **Size:** 1.696.348 t/yr
(MONBIO 4.0) · 2.017.748 t/yr (OVAM 2023)

**Evidence.** The food-industry stage carries the second-largest residual mass in the register, but
only **25 L4/L5 component rows** exist across all sources — against **119** at primary production.
Not one food-industry stream reached the 80/20 selection except melasse. The stage's mass sits in
sector-wide aggregates: `C-092` (2.017.748), `C-193` (1.999.983), `C-280`/`C-465` (oils),
`C-277`/`C-462` (meat), `C-284` (maalderij/zetmeel/bakkerij, 671.000).

**Why it is a gap.** The food industry runs hundreds of processes that each throw off a
characterised, homogeneous side stream — precisely the streams a biomass hub wants, and the ones the
literature already describes well. Their absence from the selection is not credible as a statement
about Flanders; it is a statement about what gets published.

**Why it is hard.** *Sector* aggregates are easy to find and *stream-specific* tonnages are not.
Waste statistics are collected per company and per NACE class, so they aggregate naturally to the
sector and not to the process. Getting below that needs either a nomenclature that happens to name
the stream (Prodcom, which is how bostel and zemelen entered at all) or sector-federation and project
data.

**Partly closable internally.** Gaps 1, 2, 4, 5 and 6 on the gap desk are all food-industry rows that
already exist and only need re-levelling — perskoeken/schroot (1,02 Mt), vleesverwerking (631 kt),
zemelen en gries (361 kt), bostel (135 kt), zetmeel (285 kt). **Doing those first is the cheapest
progress available on this stage**, and it should happen before any new source is commissioned.

**What would close the rest.** Sources that carve the food industry independently of the monitor
method:

- **S025** — OVAM, *Bedrijfsafval en secundaire grondstoffen*, reference year **2022** (newest in the
  queue). Reports per stream grouping and per NACE sector; the *"afval van plantaardige en/of
  dierlijke oorsprong"* line alone is 1.193.784 t primary + 443.956 t secondary for 2022.
  **Caveat found on inspection: it does not publish per EURAL code** — EURAL is only the mapping key
  behind ~113 stream groupings. Methodology break at 2022 (IMJV → MATIS).
- **S058** — ILVO TransBio (Biogas 2.0) WP3, stream volumes behind biomethane potential for the
  agro-food industry. Flemish, direct PDF.
- **S041** — Eurostat `env_wasfw` per NACE, annual 2020–2023, Belgium only.

---

## G-04 · Vlees — de massa is gedekt, de diersoort niet

**Status:** herschreven 2026-09-09 · **Kind:** granularity, niet missing data · **Size:** de
soortsplitsing over ~481.000 t (MONBIO 4.0) / ~441.000 t (3.0)

**Dit was tot 2026-09-09 geboekt als een massagat van 23% dekking. Dat was een meetfout van ons,
niet van de bron.** `displayOf` vouwde de kinderen van de `Vlees`-knoop weg zodra één kind
`agri-food waste` rapporteerde, zodat alleen dierlijk vet (145.498 t) meetelde. De echte som van de
kinderen is **481.266 t** — niet-eetbare slachtafvallen 169.051 + dierlijk vet 145.498 + gevogelte
84.141 + eetbare slachtafvallen 82.576 — dus **76%**, niet 23%.

**En het sectortotaal zelf is te hoog.** De bron telt **100.000 'stuks' huiden als tonnen** mee
(`C-277`: 531.159 + 100.000 = 631.159). Tegen het werkelijke totaal van 531.159 t is de dekking
**90,6%**; voor MONBIO 3.0 **89,1%** tegen 494.819 t.

**Wat er dus werkelijk ontbreekt.** Niet de tonnage — die is al selecteerbaar als vier benoemde
stromen. Wat geen bron geeft is **van welk dier**: rund, varken en kip afzonderlijk, per
slachtafvalcategorie. Dat is een granulariteitsvraag, en ze verlaagt de prioriteit van deze entry in
de zoeklijst fors ten opzichte van G-10 en G-01, waar de massa zelf ontbreekt.

**Wat zou het sluiten.** Een slachterij- of vleessectorbron die per diersoort rapporteert — FEBEV,
of een Vlaamse slachtafvalstudie. Niet in het 91-rijen `Sources`-blad.

## G-05 · `Granen` now mixes field residue with mill and brewery residue

**Status:** open · **Kind:** taxonomy · **Size:** n/a (structural)
*Opened 2026-09-03, as a direct consequence of the GAP-4 and GAP-5 fixes.*

**Evidence.** `Plantaardig – akkerbouw › Granen` now holds **maisstro** and **tarwestro** (field
residue, arising at primary production) alongside **Zemelen**, **Gries** and **Bostel** (mill and
brewery residue, arising at the food industry). Its leaf sum went from 1.590.919 t to 2.086.640 t
for that reason, and `verify_overview.py`'s Granen assertion was updated to match.

**Why it matters.** The node is still arithmetically correct — the chain stage is carried per row,
so nothing is summed across stages that should not be. But the *commodity* node no longer means one
thing, and a reader selecting "Granen" gets two physically unrelated kinds of material. The register
already carries the alternative: v2.5 rule 5 says a processing product goes under its `Varia` sector,
which would put zemelen, gries and bostel under `Varia › Maalderijproducten` / `Varia › Dranken`.

**The precedent cuts the other way, which is why this is left open rather than decided.** Bietenpulp
— also a processing residue — sits under `Suikerbieten en nijverheidsgewassen` on the crop ladder,
not under `Varia › Suiker`. The fixes followed that precedent for consistency. One of the two
placements should win for both, and the choice is the reviewer's.

**What would close it.** A decision, not a source: either move the three mill/brewery streams to
`Varia`, or move bietenpulp to the crop ladder's logic explicitly and record that processing
residues stay with their crop.

---

## G-06 · The oilseed-meal block — the corpus's #2 stream is a Belgian figure

**Status:** open · **Kind:** missing data (geography) · **Size:** 1.150.000 t/yr (MONBIO 4.0) ·
1.308.000 t/yr (MONBIO 3.0)
*Opened 2026-09-03, from the re-run of the 80/20 selection.*

**Evidence.** Four of the twenty-four selected streams carry `geography = Belgie`, not
`Vlaanderen`: **Kool- en raapzaad** (`C-331` 681.000 / `C-520` 852.000), **Lijnzaad** (`C-333`
245.000 / `C-522` 237.000), **Soja** (`C-330` 98.000 / `C-519` 170.000) and **Zonnebloem** (`C-332`
58.000 / `C-521` 49.000). Together they are ~18% of the corpus envelope and include the
**second-largest stream in the register**. MONBIO prints them as *ruwe productie (België)* because
the crushing statistics are only published nationally.

**Why it is a gap.** The register is a Flemish corpus and every other figure in the selection is
Flemish. A selection whose #2 entry rests on a national denominator cannot be scaled or compared
without a stated Flemish share, and the protocol forbids deriving one (that would be a calculation,
not a reading). The sanctioned Belgian→Flemish exception covers fishing ports only and must not be
stretched to cover oilseed crushing, however Ghent-heavy the sector is.

**Second symptom, same cause.** These rows are why MONBIO's selectable L4 ceiling **exceeds its own
reported L1 residual total** (104,6% for MONBIO 3.0, 102,8% for 4.0): the Prodcom food-industry rows
sit under `Plantaardig - akkerbouw › Oliehoudende gewassen`, whose covering aggregate
(`C-419` / `C-238`, *plantaardige landbouw*) counts primary production only. The percentages are a
denominator artefact, not double counting — but they make `% of L1` meaningless for MONBIO, which is
why coverage is scored against the ceiling instead.

**What would close it.** A Flemish crushing / persing figure for oilseed meal, or a source that
states the Flemish share of Belgian crush. Candidates: **S058** (ILVO TransBio WP3), a
sector-federation figure, or the Belgian Prodcom data resolved per region if it exists at all.
Failing that, the four rows stay in the selection with `geography = Belgie` on the face of them.

---

## G-07 · One L4 row can hold two physically unrelated streams

**Status:** open · **Kind:** taxonomy — a decision, not a source · **Size:** n/a (structural,
affects 3 of the top 4)
*Opened 2026-09-03, from the re-run of the 80/20 selection.*

**Evidence.** The selection unit is the L4 commodity node, which buys cross-source comparability
(MONBIO's *Groenten* matches ILVO's *Groenten openlucht*). The price is that a commodity throwing
off residue at two points in the chain lands on one row:

| L4 row | splits into | | |
|---|---|---|---|
| **Suikerbiet** 812.224 | bietenloof 462.224 (primaire productie) | + | bietenpulp 350.000 (voedingsindustrie) |
| **Aardappel** 801.530 | aardappelloof 744.945 (primaire productie) | + | 56.585 (voedingsindustrie) |
| **Kool- en raapzaad** 688.818 | koolzaadstro 7.818 (primaire productie, VL) | + | raapzaadschroot 681.000 (voedingsindustrie, **BE**) |

(MONBIO 4.0 values; MONBIO 3.0 splits the same way. Smaller cases: Bloemkool, Prei, Boon, Wortel in
GeNeSys, where a Flemish field figure sits beside a Belgian industry figure.)

**Why it matters.** BioMobi wants six streams here, not three — bietenpulp and bietenloof have
nothing physically in common, and in the raapzaad case the two halves are not even in the same
country. Ranking and coverage are unaffected (the tonnages are correct either way), but the list
cannot be handed to BioMobi as-is.

**Why it is not simply fixed by keying on L5.** Only some sources name a fraction. Keying the
selection on L5 would split *Bloemkool loof* (MONBIO) from *Bloemkool blad- en stengelmassa*
(GeNeSys) from *Bloemkool* (ILVO 239) — three keys for one crop — and destroy the cross-source
matching the L4 key exists to provide. The split has to be made **at registration time**, from the
fraction breakdown, not by changing the key.

**What would close it.** A rule saying how a bundled L4 is registered in BioMobi. The arithmetic is
already printed per row by `select_streams.js` (its *bundled L4s* block), so no new data is needed.

---

## G-08 · The same horticultural crop carries two incompatible quantities

**Status:** open · **Kind:** definition · **Size:** n/a (affects every tuinbouw stream in the
selection)
*Opened 2026-09-03, from the re-run of the 80/20 selection.*

**Evidence.** GeNeSys (S065) measures **oogstresten** — the leaf and stem mass left in the field;
its rows carry L5 fractions like *blad- en stengelmassa*. ILVO 239 (S066) measures
**voedselreststromen** — product that does not reach the market; its rows have no L5. Under one crop
name the two collapse into one stream with an enormous spread:

| stream | GeNeSys | ILVO 239 | spread |
|---|---|---|---|
| Boon | 90.000 | 1.783 | **50,5×** |
| Spruiten | 138.000 | 5.452 | **25,3×** |
| Bloemkool | 201.311 | 16.388 | **12,3×** |
| Aardbei | 22.500 | 1.836 | **12,3×** |

**Why it is a gap.** This is the MONBIO-vs-OVAM definitional divide reappearing *inside*
horticulture, where it is less obvious because both sources are ILVO and both are Flemish tuinbouw.
Selecting "Boon" without saying which quantity is meant is not usable, and the two figures must
never be averaged or summed. The selection ranks on the **larger** of the two, so every tuinbouw
entry in the shortlist is currently sized as *oogstresten*.

**What would close it.** Partly internal: give the ILVO 239 rows a fraction marker that distinguishes
product loss from field residue, so the two quantities stop sharing a node. Partly external: neither
source states a conversion between the two definitions, and inventing one is a derivation.

---

# Class A — hiding in the current data

*Three misplaced rows and the blind spot that let them through. All decided in
`crosswalks/HIDDEN_STREAMS.csv`; no source needed.*

## G-A1 · Three named streams sit above L4 and appear nowhere

**Status:** open · **Class:** A · **Size:** 255.818 t across the two MONBIO editions

| claims | stream | t/yr | why it is invisible |
|---|---|---|---|
| `C-334` `C-523` | *Meel/schroot uit andere oliehoudende zaden* | 68.000 + 68.000 | a residual class of the oilseed nomenclature, but **unprefixed and at L3** — so it is neither selectable nor an aggregate, and its mass appears in no figure at all |
| `C-381` `C-574` | *Melasse op Vlaamse productiesites (grondgebiedbasis)* | 47.805 + 56.806 | the grondgebied twin of `C-362`/`C-554` *Melasse (Prodcom 108114)*, which **is** at L4 under `Varia › Suiker`. One basis is selectable, the other is stranded at L3 |
| `C-273` `C-457` | *Teruggegooide vis (ongewenste bijvangst)* | 7.500 + 7.707 | a single named stream at L3. It is also **the entire residual content of the `Visserij` stage**, which otherwise has zero L4/L5 rows |

The melasse pair is documented in `log.md`: *"Tabel 28's suiker-nevenstroom total uses the
grondgebied basis … 56.806 (melasse) + 337.649 (bietenpulp) = 394.455 ≈ the printed 394 kton, while
Tabel 85's export-proxy cells give 111.298 + 661.550."* The bietenpulp half of that pair sits at L5
and is in the selection; the melasse half does not.

**Scale check on the discards row:** the register's entire selectable fish mass is **839 t** across
32 rows. `C-273` alone is **nine times** that.

**Fix.** Decide the three pairs in `crosswalks/HIDDEN_STREAMS.csv` (`aggregate` for the oilseed
class, `promote` for melasse and discards) and apply.

### What applying it actually changes — simulated on a copy, 2026-09-04

The six edits were applied to a **copy** of the workbook and the selection re-run, so the effect is
measured rather than assumed. Three results, and the second is the valuable one:

1. **The selection does not move.** *Teruggegooide vis* becomes selectable at **rank 39** — real,
   but outside the working set of 24. No stream enters the top 24 and none leaves. **This is the
   answer to "is there hidden data still missing from the selection": there was hidden data, and it
   does not change the selection.** The shortlist is as good as the current corpus can make it, and
   everything further is class B.
2. **MONBIO's denominators are repaired.** Giving `C-334`/`C-523` an `AGGREGAAT` prefix *and a
   registry line* raises MONBIO 3.0's reported residual total from **5.944.027 to 6.935.676 t** and
   MONBIO 4.0's from **5.451.052 to 6.341.552 t**, and the impossible ceiling ratios
   (**104,6% and 102,8% of L1**) fall to **90,6% and 89,3%**. The oilseed food-industry branch was
   not covered by any registered aggregate, so derive had been understating MONBIO's own L1 by about
   1 Mt. Coverage-against-L1 becomes a meaningful number for MONBIO for the first time.
3. **One genuine decision is hiding inside the melasse row — do not apply it naively.**
   `C-381`/`C-574` (grondgebiedbasis) and `C-362`/`C-554` (Prodcom, export-proxy) are **two
   accountings of one material**, and within *one* edition. Promoting the grondgebied row onto the
   same L4 node makes them siblings and `derive.js` **adds them**: melasse reads
   111.298 + 56.806 = **168.104 t**, a 51% inflation, and jumps from rank 15 to 11. Promoting it to
   the crop ladder instead is worse — it creates a *second* "Melasse" stream at rank 24 and pushes
   Appel out of the working set.

   The register already has the precedent, from the bietenpulp pair: one basis is the selectable
   row, the other is an aggregate cross-referenced to it. **The reviewer picks the basis.** For
   BioMobi, *grondgebied* is arguably the right one — it measures what physically arises on Flemish
   sites, where the export proxy is a share of Belgian production — but that is a scope call, not a
   placement one.

---

## G-A2 · The audit could not see this class, by construction

**Status:** open · **Class:** A · **Size:** structural

`audit_register.py` identifies a misplaced row **from its name**: check 1 fires on a product code
(Prodcom / NACE / CN), check 4 on a leftover-class phrase (*Andere …*, *n.e.g.*, *van alle soorten*).
**A live residual row at L2 or L3 with an ordinary name passes every check in the file.** All three
rows in G-A1 are in that blind spot — none carries a code, none matched a phrase.

One contributing defect, now fixed: `COLLECTION_SIGNALS` listed *en andere*, *of andere* and *van
andere* but **not *uit andere***, which is why *Meel/schroot **uit andere** oliehoudende zaden*
escaped check 4. Adding the preposition catches exactly those two rows and nothing else; the audit
baseline moves from 24 findings to 26.

**Fix, done.** `find_hidden_streams.py` enumerates the whole class rather than pattern-matching
names — 49 rows, 2.367.761 t — and writes them to a human gate. **43 of the 49 are legitimate**:
OVAM publishes *Dranken*, *Bakkerij* and *groenten openlucht* at subgroup level and nothing finer,
so an L3 row there is that source's finest grain. Those 43 are not defects — **they are the class-B
data gaps below**, which is exactly why the screen has to be run before the gap list is trusted.

---

## G-A3 · The `Varia` sector aggregates are parented away from their components

**Status:** open · **Class:** A · **Size:** structural (1.074.000 t of aggregate on MONBIO 4.0)

`C-284`/`C-469` *Vervaardiging van maalderijproducten, zetmeelproducten* (671.000 / 563.000 t) and
`C-286`/`C-471` *Vervaardiging van suiker en chocolade* (403.000 / 394.000 t) sit at **L2 under
`Varia` with `L3` blank**, while the rows they total sit under `Plantaardig - akkerbouw › Granen`
(Zemelen, Gries, Bostel) and `Varia › Zetmeel` / `Varia › Suiker`. The aggregates therefore
reconcile against nothing in the tree, and the overview shows their branch as empty.

Both reconciliations are already recorded in `log.md` and are exact:

```
C-469  563.000 = zemelen 278.865 + zetmeelafvallen 284.549      = 563.414
C-471  394.000 = melasse 56.806  + bietenpulp     337.649       = 394.455   (grondgebied basis)
```

This is **G-05 with numbers attached**: it is the same open placement decision (does a processing
residue live under its crop or under its `Varia` sector), and until it is taken these two aggregates
cannot be checked against anything.

---

# Class B — not in the corpus at all

*Ordered by mass. Each entry names what would close it.*

## G-09 · Zuivelverwerking — wei: the figure exists, but it is from 2018 and its owner is retired

**Status:** partly closed 2026-09-08 · **Class:** was recorded as B; it was neither B nor A ·
**Size:** melkwei **49.722 t** (2018); the NACE 10.5 sector row it sits in is 70.167 t

**This entry was wrong, and the way it was wrong is worth keeping.** It read *"no row anywhere in
the workbook contains wei"* and concluded that nothing measured it, so only a new source could
help. The word was indeed absent from all 801 rows — but the **figure was not**. Both MONBIO
editions print it in a table: `S091 p.168 Tabel 65` and `S007 p.160 Tabel 47`, NACE 10.5
zuivelfabrieken en kaasmakerijen → **70.167 t, waarvan melkwei 49.722 en zuiveringsslib 20.445**.
`C-282`/`C-467` captured only the rounded 70 kton sector line; the split sat in their
`source_type_label` and never reached a claim.

**Why it was skipped, and why that was correct.** The cross-source restatement rule: the 49.722 t
is an OVAM/IMJV estimate for **2018** that MONBIO carries forward unchanged, and 2018 belongs to
**S005 (MONBIO 1.0)**, which is in the `Sources` sheet. Verified this session — S005 p.131 carries
the identical table row. The rule was applied correctly.

**Why it was still a hole.** S005 is `_RETIRED`. So the owner is never extracted, "skip it, S005
has it" resolves to "lose it", and a real 49.722 t stream fell between a correct rule and a
correct decision. Captured 2026-09-08 as **C-802/C-803** under `Dierlijk - vee / Melk /
Zuivelnevenstroom`, as a narrow exception — **the zuivel cell only, never Tabel 65 as a whole**,
whose remaining ~1,8 Mt is genuinely S005's.

**The stated mechanism was also wrong.** This gap was the example for *"a side stream with no
Prodcom code is invisible to MONBIO"*. **Prodcom 105155 "Wei" exists** and is printed in both
editions with `C` — confidential. A suppressed cell is a different failure mode from a missing
code, and it needs a different answer. See the corrected note at the top of this file.

**What is still missing.** A **recent** and unambiguously Flemish measurement. The captured figure
describes 2018 and is carried forward by both editions, so the corpus has no post-2018 dairy
residual measurement at all. Nor is the sector line an upper bound for whey alone: 20.445 t of the
70.167 is `zuiveringsslib`, which `quantity_type.csv` puts out of scope. For scale, the register
holds **koemelk 4.450.280 t** (`C-261`) and **kaas en wrongel 101.256 t** (`C-348`); cheese-making
separates roughly nine parts whey to one part curd — *an industry rule of thumb, deliberately not
derived here* — so 49.722 t is small against that and probably counts only the fraction reported
as a residual rather than sold as a product.

**What would close it, in order.** (1) Decide **S005**: un-retiring it is the complete answer and
it also holds gries/zemelen/DDGS ~646 kt and bietenpulp+melasse ~458 kt. (2) Failing that, a
dairy-sector source — BCZ/MilkBE volumes, or an FOD Economie request to release Prodcom 105155.
**Nothing in the 91-row `Sources` sheet covers dairy processing** other than the retired MONBIO
editions.

---

## G-10 · Aardappelverwerking — no named residue stream, in the world's largest frozen-potato cluster

**Status:** open · **Class:** B · **Size:** 621.063 t (OVAM 2023) / 653.463 t (2020), zero components

**Evidence.** `C-094` *Voedselreststromen Aardappelen, groenten en fruit (voedingsindustrie)* is
**621.063 t with no component rows** — the largest food-industry commodity block in the register
with no detail. The only potato food-industry residual row anywhere is `C-314`/`C-501` *Meel, gries,
vlokken, korrels en pellets van gedroogde aardappelen* (56.585 / 54.913 t), which is a **product**,
not residue. The checklist finds **aardappelschillen, stoomschillen, aardappelvezel and
aardappeleiwit all absent**.

**Why it is a gap.** Flanders hosts the largest concentration of potato processing in Europe. Peel,
steam-peel concentrate, fibre and protein are its characteristic, homogeneous, well-described side
streams — precisely what BioMobi is for — and the register has none of them.

**What would close it.** Belgapom / VLAM sector volumes, or a processing-sector study.
**S058** (ILVO TransBio WP3, in the `Sources` sheet, no PDF yet) is the nearest queued candidate.

---

## G-11 · Dranken — 378.539 t, and only bostel is named

**Status:** open · **Class:** B · **Size:** 378.539 t (OVAM 2023) / 343.166 t (2020)

**Evidence.** `C-095` / `C-196` under `Varia › Dranken`, **zero L4 rows in any source**. MONBIO
supplies exactly one beverage side stream, *Bostel* (134.653 t, Prodcom 110210) — filed under
`Granen`, not under `Dranken`. So at most a third of OVAM's beverage figure has a name.
**Absent from the whole workbook: draf / DDGS, vinasse, biergist, sapresidu.** *Gist* appears only
as a 138.901 t **production** row (`C-376`, retired).

**What would close it.** A brewers' or distillers' federation figure, or a biomethane-potential
study that lists its input streams. In the sheet: **S053** (Biogas-E input streams) and **S012**
(Vlaco) touch it but are destination-side and partial; **S058** is the better bet. Neither has a PDF.

---

## G-12 · Cacao en chocolade — no residual figure at all

**Status:** open · **Class:** B · **Size:** unmeasured

**Evidence.** The aggregate is *named* for it — `C-286`/`C-471` *Vervaardiging van suiker **en
chocolade***, 403.000 / 394.000 t — but the reconciliation in G-A3 shows that figure is **entirely
sugar** (melasse + bietenpulp = 394.455 against a printed 394 kton). The chocolate half contributes
nothing. Production rows exist — *Chocolade en cacaobevattende bereidingen* 554.394 t (`C-365`),
*Cacaopasta* 22.310 t, *Cacaoboter* 1.061 t — but **cacaodoppen, cacaoschillen and cacaoperskoek
appear nowhere in the workbook**.

**Why it is a gap.** Belgium is one of Europe's largest cocoa processors and the plants are in
Flanders. Cocoa shell is a clean, dry, characterised stream with an established market.

**What would close it.** A cocoa/chocolate sector source (Choprabisco, or a plant-level study).
**No candidate in the `Sources` sheet.**

---

## G-13 · Bakkerij — 122.276 t, zero components

**Status:** open · **Class:** B · **Size:** 122.276 t (OVAM 2023) / 37.755 t (2020)

**Evidence.** `C-093` / `C-194` under `Varia › Bakkerij`, no L4 in any source. The register holds
*Vers brood* production 303.437 t but no bread-waste stream. **Note the 3,2× jump between the two
OVAM editions** (37.755 → 122.276) — either a real change or a method change, and it is not
explained on the rows.

**What would close it.** **S067** (Comeos, retail 2015–2018) reaches bakery return from the retail
side; **S025** (OVAM bedrijfsafval, ref. yr 2022) carves by NACE and would give the industry side.
Both are in the `Sources` sheet without a PDF.

---

## G-14 · Oliën en vetten, and used frying fat

**Status:** open · **Class:** B · **Size:** 95.895 t (OVAM 2023) / 57.723 t (2020)

**Evidence.** `C-096` / `C-197` under `Varia › Oliën, vetten`, zero components. MONBIO's oilseed
meal sits in a different branch and is Belgian (**G-06**). *Frituurvet / afgewerkt vet* is **absent
from the workbook**.

**What would close it.** Used-oil collector or federation data, or a NACE/EURAL-carved waste
statistic — **S025** (OVAM *bedrijfsafval*, ref. yr 2022) is the candidate in the sheet, without a
PDF yet.

---

## G-15 · MONBIO's own crop groups with no component rows — 203.387 t of field residue

**Status:** open · **Class:** B · **Size:** 203.387 t (MONBIO 4.0) / 195.757 t (3.0)

**Evidence.** Three L3 residual aggregates carry mass with **zero component rows in either edition**:

| claims | group | MONBIO 4.0 | MONBIO 3.0 |
|---|---|---|---|
| `C-242` `C-423` | Voedergewassen | 101.780 | 90.551 |
| `C-243` `C-424` | Industriële gewassen | 55.065 | 56.987 |
| `C-244` `C-425` | Peulvruchten en eiwitgewassen | 46.542 | 48.219 |

The asymmetry is the tell: the **production** side of these same groups *is* resolved to L4 —
Voedermais 5.395.992 t, Gras (incl. hooi) 3.939.458 t, Voederbiet 360.547 t, Cichorei 90.000 t,
Vlas 23.000 t — so the dictionary has the members and only the residual side is missing.

**What would close it.** A source giving field-residue ratios per fodder / fibre / pulse crop.
**S077** (Vlaanderen Circulair scenariostudie) re-tabulates MONBIO into 14 crop types and may resolve
some of it, though it is a re-aggregation, not a new measurement.

---

## G-16 · Eieren — 1.282 t, zero components; eierschalen absent

**Status:** open · **Class:** B · **Size:** 1.282 t

**Evidence.** `C-047`, `C-060`, `C-170`, `C-071`, `C-182` under `Dierlijk - vee › Eieren`, all at L3,
no L4 anywhere. *Eierschalen* absent from the workbook. Small in tonnage, but it is a **complete**
absence in a sector Flanders has.

---

## G-17 · Visverwerking — everything except discards is absent

**Status:** open · **Class:** B · **Size:** the whole selectable fish mass is **839 t**

**Evidence.** 32 selectable fish rows across the corpus total **839 t**, all of them
*opgehouden vis* at the auctions. *Visafval, visresten, visgraat, viskop* are **absent**. The one
real fisheries residual figure in the register is the discards row of **G-A1** (7.500 t), which is
currently invisible. The `Visserij` chain stage has **zero** L4/L5 rows.

**What would close it.** A fish-processing or ILVO fisheries source; `flag_agrifood_sidestreams`
in the `Sources` sheet marks one row *"yes (FISHERIES side streams)"* — worth locating.

---

## G-18 · Seven MONBIO 4.0 figures exist only in the 2020 edition, because 2021 suppressed them

**Status:** open · **Class:** B (source suppression) · **Size:** 284.549 t on the largest of them

**Evidence.** `log.md` records it exactly: *"Three Prodcom cells that were confidential in S091 carry
a value here — 106220 afvallen van zetmeelfabrieken (284.549 t, C-550), 108120 bietenpulp en andere
afvallen van de suikerindustrie (661.550 t, C-555) and 108311 gebrande koffie (36.953 t, C-560) —
plus 103213 pompelmoessap and 103214 ananassap, and 102024 gerookte vis and 102034 bereide
schaal-/weekdieren. Seven claims that have no counterpart in the 2021 edition."*

**Why it matters here.** **Zetmeel is the #5 stream in the selection and is single-source for this
reason alone** — not because the register missed it. A confidential Prodcom cell is an absence, never
a zero, so no re-reading of S091 will produce it.

**What would close it.** Suppression is per year, not permanent, so a later edition may release a
different subset — **S078** is the MONBIO web portal (a scraping route, not a PDF). Eurostat's own
Prodcom tables are the other route.

---

## Summary

### Class A — hiding in the current data (no source will help)

| id | Gap | Size | Next action |
|----|-----|------|-------------|
| G-A1 | Three named streams sit above L4 and appear nowhere | 255.818 t | decide the 6 rows in `HIDDEN_STREAMS.csv`, then apply |
| G-A2 | The audit is blind to residual rows above L4 with plain names | structural | **done** — `find_hidden_streams.py`; `uit andere` added to the collection rule |
| G-A3 | `Varia` sector aggregates parented away from their components | 1,07 Mt of aggregate | the same decision as G-05 |
| G-05 | `Granen` mixes field and processing residue | n/a | a placement decision, not a source |
| G-07 | One L4 row holds two unrelated streams | n/a | **resolved by decision** — one item, reported at its lowest detail level (`select_streams.js`) |
| G-08 | Oogstresten vs voedselreststromen under one crop name | n/a | mark the fraction on the ILVO 239 rows |

### Class B — not in the corpus (only a new source will help)

**The full list, with what is missing and what kind of source would supply it, is
`crosswalks/GAP_LIST.csv`** — one row per sector or product, carrying the claim ids, the total that
exists, the detail that does not, and the candidate. The table below is its index.

| id | sector / product | size | candidate in the sheet |
|----|-----|------|----------------------|
| G-10 | Aardappelverwerking — no named residue | 621.063 t block, 0 components | S058 (no PDF); otherwise Belgapom / VLAM, **not in the sheet** |
| G-04 | Vlees per diersoort | 631.000 t sector; 217.672 t offal total | **none** — needs a slaughter/rendering source |
| G-11 | Dranken — only bostel is named | 378.539 t | S053, S012, S058 — all without a PDF |
| G-12 | Cacao en chocolade — no residual figure at all | aggregate is provably all sugar | **none** — Choprabisco is not in the sheet |
| G-09 | Zuivelverwerking — wei captured, but 2018 and owned by a retired source | 49.722 t (2018) | **S005**, retired — decide it; else BCZ/MilkBE or an FOD request for Prodcom 105155 |
| G-06 | Oliezaadschroot is a Belgian figure | 1,15–1,31 Mt, incl. the #2 stream | S058 (no PDF) |
| G-01 | Retail below sector level | 132.082 t | S067, S035, S041 — none has a PDF |
| G-13 | Bakkerij | 122.276 t | S025, S067 — no PDF |
| G-15 | Fodder / fibre / pulse field residue | 203.387 t | S077 — a re-aggregation, not a measurement |
| G-14 | Oliën, vetten + frituurvet | 95.895 t | S025 — no PDF |
| G-18 | Seven MONBIO 4.0 cells suppressed | 284.549 t on zetmeel | S078 portal, or Eurostat Prodcom |
| G-02 | PO's & veilingen implausibly small | 15.189 t | **fact-check first**, do not commission |
| G-17 | Visverwerking | 839 t is the whole selectable fish mass | one sheet row flags fisheries side streams — locate it |
| G-16 | Eieren en eierschalen | 1.282 t | none |

**Sources carrying `_RETIRED` in `inbox/` are excluded from every candidate above and must not be
proposed.** They were retired deliberately; if that judgement is ever revisited it is the reviewer's
call, not a gap-list recommendation.

---

## What to do with these two lists

**1. Work `FIX_LIST.csv` first — it is free.** Seven decisions, no new data, and two of them put a
new stream into the shortlist:

| fix | what | effect |
|---|---|---|
| **F1** | promote `C-298`/`C-483` *Niet-eetbare ruwe slachtafvallen* to L4 | **enters the shortlist at rank 11** (169.051 t) |
| **F2** | promote `C-295`/`C-480` *Eetbare slachtafvallen (rood vlees)* to L4 | **enters the shortlist at rank 22** (82.576 t) |
| F3 | melasse: one basis, grondgebied or export-proxy | stays in either way — **do not apply mechanically** |
| F4 | promote *Teruggegooide vis* | selectable at rank 39; it is all the `Visserij` stage has |
| F5 | mark the oilseed leftover class + registry line | repairs MONBIO's L1 by ~1 Mt, kills the >100% ceilings |
| F6 | re-parent the two `Varia` sector totals | makes them reconcilable; same decision as G-05 |
| F7 | **leave `C-342`/`C-532` alone** | recorded so it is not proposed again — it double-counts |

F1 and F2 are the answer to *"a row marked AGGREGAAT because its name bundles two items, when the
bundle is itself an acceptable stream."* They are the same case as `Zemelen, slijpsel en andere
resten van het bewerken van granen`, which was promoted for exactly that reason. **251.627 t has
been sitting in the register the whole time, marked unselectable.**

**2. Then hunt sources with `GAP_LIST.csv`, in this order.** Ranked by how much a source would
change the BioMobi stream list, not by the size of the gap:

1. **Aardappelverwerking (G-10)** — 621.063 t with zero components, in the sector Flanders leads;
   peel, stoomschil, vezel and eiwit would each be a named L4. No candidate in the sheet.
2. **Zuivel / wei (G-09)** — no longer absent: 49.722 t (2018) captured as C-802/C-803 on
   2026-09-08, entering at #15 together with the OVAM sector figure. What is still missing is a
   *recent* Flemish measurement. The candidate is **S005**, which is retired — a decision, not a search.
3. **Vlees per diersoort (G-04)** — F1 and F2 give two usable streams today; the species split needs
   a source. No candidate in the sheet.
4. **Retail + bakkerij (G-01, G-13)** — two gaps, two named candidates (S067, S025), neither with a
   PDF.
5. **Cacao (G-12)** and **Flemish oilseed crush (G-06)** — smaller, but the first is a complete
   absence and the second is the geography of the #2 entry.

**3. Fact-check G-02 before commissioning anything for that stage.** An afternoon against VBT or one
auction's jaarverslag decides whether it is a gap at all.

**The screening rule for any candidate, and it falls straight out of the mechanism above:
does it carve by process?** A source that carves by NACE class, by Prodcom code, or by a monitor's
own loss definition will reproduce the gaps the register already has — that is exactly how they
arose. `S025` is the interesting exception: it carves legally, by EURAL.

---

## Where the class-A rows are decided

Same convention as every other human gate here — `;`-delimited, UTF-8 BOM, blank `DECISION`:

- **`crosswalks/FIX_LIST.csv`** — the seven fixes above, each with its claim ids, the proposed
  change, the simulated effect on the shortlist and the caution that goes with it. Regenerate with
  `make_gap_lists.py`; it refuses to overwrite once any `DECISION` is filled.
- **`crosswalks/GAP_LIST.csv`** — the fourteen genuine gaps, for source hunting. Not gated; it is a
  worklist, not a decision sheet.
- **`crosswalks/HIDDEN_STREAMS.csv`** — the raw screen behind F3–F5: all 49 live residual rows above
  L4, with a proposal per row. 43 of them are legitimate subgroup figures and become the class-B
  gaps above.
- **`crosswalks/GAP_DECISIONS.csv`** — the earlier eight, decided and applied on 2026-09-03. Kept
  for provenance; do not re-run its generator.
