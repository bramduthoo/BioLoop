# BIOLOOP register — open gaps

*Created 2026-09-03, from the coverage audit at 801 claims / six extracted sources.
**Rewritten the same day** after a systematic sweep of the whole corpus — every residual row, every
aggregate, every chain stage, an absence checklist of 41 named Flemish side streams, and all 91 rows
of the `Sources` sheet.*

**How to use this file.** One entry per gap. A gap leaves this file when either (a) a source is
extracted that resolves it, or (b) it is fact-checked and turns out not to be a gap — in which case
the entry stays with its status flipped to `closed`, so the check is not repeated. Do not delete
entries.

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

Five screens over `streams_export.csv`. **`gap_sweep.py` runs all five and dumps every one of them
in full** — `database/.venv/Scripts/python gap_sweep.py out.json` — so this file's claims can be
re-derived from the workbook rather than trusted. The browser version of the same output, with the
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
why whey, cacaodoppen and potato peel are absent while bostel and zemelen are present, and it
predicts where to look: not another monitor edition, but a sector source that carves by *process*
instead of by product code.

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

## G-04 · Dierlijk – vee — 471 kt still unresolved after the re-levelling

**Status:** open · **Kind:** granularity · **Size:** 471.361 t/yr (65,5% of the group, MONBIO 4.0)
*Opened 2026-09-03, after the gap-desk fixes were applied.*

**Evidence.** The GAP-2/3/8 fixes lifted `Dierlijk – vee` from **10,9% to 34,5%** resolved — Melk
(19.000), Dierlijk vet (145.498) and Gevogelte (84.141) now sit at L4. The remaining **471.361 t**
does not move, because it is held in genuine slaughter-offal aggregates: `C-308` *Eetbare
slachtafvallen, totaal* (217.672), `C-298` *Niet-eetbare ruwe slachtafvallen* (169.051), `C-295`
*Eetbare slachtafvallen van runderen, varkens, schapen, geiten en paarden* (82.576), `C-296` *Ander
vlees en andere eetbare slachtafvallen* (49.893).

**Why it is a gap and why re-levelling cannot close it.** These are real category totals, not
mislabelled streams. Splitting them per animal needs a **measured waste ratio per species**, and no
source in the register gives one — the register has production volumes per species but nothing that
links production to offal yield. Inferring the split from production would be a derivation the
protocol forbids, which is exactly why the reviewer declined it on GAP-2.

**What would close it.** A source that reports slaughter by-products per species, or a
species-resolved rendering-sector figure. **No candidate exists in the `Sources` sheet** that is not retired, so this needs a search: a
slaughterhouse or rendering-sector source reporting by-products per species.

---

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

## G-09 · Zuivelverwerking — wei (whey) is absent from the register entirely

**Status:** open · **Class:** B · **Size:** unknown; the only measured figure is 70.000–89.593 t

**Evidence.** The absence checklist finds **no row anywhere in the workbook** — any role, any status
— containing *wei*, *kaaswei*, *weipoeder*, *melkserum*, *permeaat*, *retentaat* or *lactose*. The
only dairy-processing residual figures in the register are `C-282`/`C-467` *Vervaardiging van
zuivelproducten, productie nevenstromen* (**70.000 t**, L3, **no component rows**) and OVAM's
`Melk` rows (135.226 t in 2020, 89.593 t in 2023, spanning primary production and industry).

**Why it is a gap.** The register does hold the production side: **koemelk 4.450.280 t** (`C-261`)
and **kaas en wrongel 101.256 t** (`C-348`). Cheese-making separates roughly nine parts whey to one
part curd — *an industry rule of thumb, not a register figure, and deliberately not derived here* —
so a 70.000 t dairy nevenstroom cannot be counting whey. It is counted as a **product**, not a loss,
and both monitors measure losses and Prodcom-coded by-products.

**What would close it.** A dairy-sector source: BCZ/CBL (Belgische Confederatie van de Zuivelindustrie)
volumes, or a Flemish dairy-processing study. **Nothing in the 91-row `Sources` sheet covers dairy
processing** — this gap has no candidate at all and needs a search.

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
| G-09 | Zuivelverwerking — wei absent entirely | only 70.000 t measured | **none** — no dairy-processing source in the sheet |
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
2. **Zuivel / wei (G-09)** — absent from all 801 claims and would very likely enter the top ten on
   its own. No candidate in the sheet.
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
