# BIOLOOP register — open gaps

*Gaps that **cannot** be closed by re-levelling what the register already holds. Each one needs
data the corpus does not contain. Companion to the gap desk, which covers the eight gaps that
**can** be fixed internally (re-levelling, renaming, splitting bundled nomenclature rows).*

*Created 2026-09-03, from the coverage audit at 801 claims / six extracted sources.*

**How to use this file.** One entry per gap. A gap leaves this file when either (a) a source is
extracted that resolves it, or (b) it is fact-checked and turns out not to be a gap — in which case
the entry stays with its status flipped to `closed`, so the check is not repeated. Do not delete
entries.

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
species-resolved rendering-sector figure. The nearest candidates are the retired Marktanalyse
editions (**S001**, animal by-product sector at ~860 kt for 2021) and the S087 geography decision.
Failing that, a slaughterhouse-federation source.

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

## Summary

| id | Gap | Size | Kind | Next action |
|----|-----|------|------|-------------|
| G-01 | Retail below sector level | 132.082 t | missing data | queue S067 / S035 |
| G-02 | PO's & veilingen implausibly small | 15.189 t | **fact-check first** | check VBT / auction jaarverslag |
| G-03 | Food industry stream detail | 1,7–2,2 Mt | granularity + missing data | re-levelling **done** 2026-09-03; next S025 / S058 |
| G-04 | Dierlijk – vee offal below species level | 471 kt | granularity | needs a species-resolved source (S001 / S087) |
| G-05 | `Granen` mixes field and processing residue | n/a | taxonomy | a placement decision, not a source |
| G-06 | Oilseed meal — the #2 stream is a Belgian figure | 1,15–1,31 Mt | missing data (geography) | needs a Flemish crush figure (S058?) |
| G-07 | One L4 row holds two unrelated streams | n/a | taxonomy | a registration rule; arithmetic already printed |
| G-08 | Oogstresten vs voedselreststromen under one crop name | n/a | definition | mark the fraction on the ILVO 239 rows |

**Not in this file:** the eight gaps that can be closed by re-levelling rows the register already
holds. Those live on the gap desk and are decided there, not here.

---

## Where the fixable eight are decided

The eight gaps that **can** be closed by re-levelling live in
**`crosswalks/GAP_DECISIONS.csv`** — same convention as every other human gate here:
`;`-delimited, UTF-8 BOM, blank `DECISION` and `NOTES` columns for you to fill in Excel or VS Code.
Each row carries the claim ids, the mass, why it is a gap and the proposed fix, so it stands on its
own without the artifact.

There is also a browser version of the same eight with the evidence tables and charts —
the **Gap Desk** artifact — but note that anything typed there lives in that browser only.
**`crosswalks/GAP_DECISIONS.csv` is the file of record.** If the two disagree, the CSV wins.

`GAP-6` is marked `fixable_internally = partly`: its internal half (promoting zetmeel) is decided in
the CSV, its external half is **G-03** above.
