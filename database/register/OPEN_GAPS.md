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

## Summary

| id | Gap | Size | Kind | Next action |
|----|-----|------|------|-------------|
| G-01 | Retail below sector level | 132.082 t | missing data | queue S067 / S035 |
| G-02 | PO's & veilingen implausibly small | 15.189 t | **fact-check first** | check VBT / auction jaarverslag |
| G-03 | Food industry stream detail | 1,7–2,2 Mt | granularity + missing data | do the gap-desk re-levelling first, then S025 / S058 |

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
