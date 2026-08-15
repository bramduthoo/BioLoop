# BIOLOOP register — extraction log

*One entry per source-extraction session, newest first. The running record of what was
extracted, what looked wrong, and whether it has been verified against the archived PDF.
This is local working memory for the register workstream; project-level status still goes to
`database/hub.md` at session end.*

## How to use
- After each source session, add one row to the **Sessions** table.
- If the anomalies for a source need more than a line, write them out under **Anomaly notes**
  keyed by `source_id`, and just point to it from the table.
- `Verified?` flips to `yes` only after a human has checked `Streams` against the PDF in
  `archive/`.

### What an anomaly note must contain

Keep these five headings, in this order, so notes stay comparable across sources:

1. **Variant readings** — the same quantity stated more than once with different values, all
   captured. List them plainly; these may be rounding, revision, or genuinely different
   measurements. **Not** errors, and not to be described as such.
2. **Suspected source errors** — only where there is *arithmetic evidence* (a figure breaks
   its own table's total, or its digit order contradicts every other statement of the same
   quantity). Captured as recorded, never corrected. State the evidence and name the
   `claim_id` so `DECISION_expert` can retire that row.
3. **Deliberate exclusions** — every figure seen and not captured, with the reason: an
   out-of-scope stage (horeca / catering / households), an aggregate containing one, a
   destination or collection-route value, `schenking` / `slib` / `afgeleid product`, a
   non-Flemish geography, a non-convertible unit, or a value that is not a quantity of
   material. Name the tables so a reviewer can see nothing vanished silently. Note that a
   `voedselverlies` / `nevenstroom` split is **not** a route value — it is `quantity_type`
   and belongs in the corpus, even when the source prints it inside a route cross-tab.
4. **Completeness sweep** — the disposition of every numbered table and figure in the source's
   own index: captured (with claim ids), excluded (with the reason, which may point at the
   list above), or carries no numbers. Group freely — one line per chapter of out-of-scope
   tables is fine. This is what makes "nothing was missed" checkable rather than asserted.
5. **Judgement calls & new dictionary members** — anything a reviewer should second-guess,
   and every vocabulary member added during the session.

## Sessions

| Date | source_id | source_short | PDF (in archive/) | Claims added | Verified? | Commit | Anomalies / flags |
|------|-----------|--------------|-------------------|-------------:|-----------|--------|-------------------|
| 2026-08-15 | S080 | OVAM Monitor voedselverlies 2023 | `S080_OVAM Monitor voedselverlies 2023.pdf` | 114 (C-001…C-114), 1 retired | **yes** (2026-08-15) | `2486196` + `8d23344` | See [S080](#s080) — 1 source error retired by the reviewer, 3 variant readings, no Zotero item (F-002) |

*Note: S080 was extracted once before, on 2026-08-14 under protocol v1, producing 310 claims.
That run was **discarded** on 2026-08-15 — it captured horeca and catering, and predated the
provenance/unit columns. See commit `ad3b36c` for the withdrawn output. The row above is the
clean v2 re-run and supersedes it entirely.*

## Anomaly notes (detail, keyed by source_id)

### S080

**Reviewer outcome (2026-08-15).** The full extraction was checked against the archived PDF by
hand. **No captured value was found to be misread** — every correction below is to
classification, naming or provenance metadata, not to a number.

- **C-074 retired.** The reviewer confirmed the 21.060 / 215.060 discrepancy is a typo in the
  source. `DECISION_expert = exclude`, superseded by C-077. The row is kept, not deleted: the
  audit trail is the point, and downstream consumers filter on `DECISION_expert`.
- **C-005 and C-102 confirmed kept** — the two "captured against the source's own exclusion"
  judgement calls stand as extracted.
- **The 27 Tabel 10 rows moved from `Belgie` to `Vlaanderen`.** Every Belgian fishing port lies
  in Flanders, so the two labels denote the same figure. This is now a **named, single
  exception** in the protocol and must not be generalised to any other Belgian number.
- **Akkerbouw re-levelled** (dictionary rule change, recorded in `state.md`): `Aardappelen` and
  `Suikerbieten` were single crops sitting at L3. They are now L4 ingredients (`Aardappel`,
  `Suikerbiet`) under the new subgroups `Aardappelen en knolgewassen` and `Suikerbieten en
  nijverheidsgewassen`, so those rows became level 4. `Granen` is a genuine subgroup and stays
  level 3.
- **Names disambiguated:** C-057 and C-058 now say `(incl. niet-geoogste aardappelen)`; C-086
  now says `(som van 10 belangrijkste)`.
- **Four claims added from Tabel 7 (C-111…C-114).** The reviewer corrected a rule error, not
  just a row: `voedselverlies` vs `nevenstroom` is `quantity_type` — one of the register's
  three axes — and had been wrongly swept up with the destination/collection axes because
  Tabel 7 prints the two as a cross-tab. The primary-sector quantity-type figures (401.011 /
  23.146 voedselverliezen, 215.162 / 8 nevenstromen) appear nowhere else in the source, so they
  are now captured with the collection route named on the row and a never-sum warning. The
  protocol was rewritten to read such tables **by axis, not by table**.
- **Restatement trails added to 20 rows.** The reviewer reported Tabel 5's voedingsindustrie
  total as missing; it was in fact captured as **C-092** from Tabel 22, the identical value in
  its own sector chapter. That was invisible from the row, so every restated figure now lists
  its other locations in the new **`also_stated_in`** column (26), together with
  cross-references between variant claims.

**Two rows for the voedingsindustrie that look contradictory and are not.** C-092
(2.017.748 ton, Flemish `voedselreststromen`) and C-001 (279.114 ton, EU
`levensmiddelenafval`) measure the same stage and year under incompatible definitions. The EU
definition counts only material that becomes *waste* in the sense of EU waste law, so feed
(79%), biobrandstof (5%), biochemie (2%) and bodem (0,3%) fall outside it. Tabel 2 splits the
EU figure as 274.016 (compostering/vergisting) + 5.098 (verbranding) = 279.114. Note the two
accountings do **not** reconcile exactly: the same two destinations in Tabel 23 sum to
273.063 + 6.832 = 279.895, i.e. 781 ton more than the EU total.

**Session rule (set by the user at session open):** only the **2023** column of this monitor's
evolution tables was captured. The 2015 / 2017 / 2020 columns were left for S004 (2015) and
S002 (2020), which are queued as their own sources. Two consequences worth knowing:

- Where a stream's *only* figures are pre-2023, nothing was captured — see *Deliberate
  exclusions* below (visserij).
- One deliberate exception was made, flagged under *Judgement calls*: the ~50.000 ton
  slaughterhouse stream (C-102), which carries `reference_year = 2020`.

Also of note: in this PDF the **file page equals the printed folio** throughout, so
`source_page` needs no dual notation.

#### 1. Variant readings

All captured; none of these is called an error.

- **Landbouw, totale voedselreststroom 2023 (excl. niet-geoogste aardappelen):
  623.935 vs 623.934 ton.** Tabel 12 (p.30) prints 623.935, Tabel 16 (p.36) and Figuur 5
  (p.35) print 623.934. Both captured (C-049, C-075). The Tabel 5 primary-sector total
  reconciles exactly on the 623.934 basis (623.934 + 203 + 15.189 = 639.326), so the two
  figures are used inconsistently inside the source itself.
- **Retail, totale voedselverliezen 2023: 59.849 vs 58.849 ton.** Tabel 30 (p.56), Tabel 32
  (p.57) and Figuur 9 (p.58) print 59.849; Tabel 34 (p.62) prints 58.849. Both captured
  (C-108, C-110). A single dropped digit is plausible but there is no arithmetic proof either
  way, so this stays a variant.
- **Rounding-level mismatches inside table totals** (captured as printed, no row retired):
  Tabel 12 tuinbouw parts sum to 340.885 against a printed 340.886; Tabel 14 tuinbouw
  voedselverliezen sum to 264.094 against a printed 264.093; Tabel 10's 2023 columns sum to
  12.518 / 202 against printed totals of 12.519 / 203; Tabel 32's 52.011 + 7.837 = 59.848
  against a printed 59.849.
- **Not captured, but noted:** Tabel 8 (p.20) gives voedingsindustrie nevenstromen "selectief
  ingezameld" as 1.543.934 where Tabel 22 (p.45) gives 1.543.962. Both live in
  collection-route cells, which the register does not extract, so neither became a row.

#### 2. Suspected source errors

- **C-074 — landbouw, totale nevenstromen 2023, Tabel 14 (p.33) prints 21.060 ton.** Captured
  as recorded, never corrected. Arithmetic evidence that a digit was dropped: the table's own
  subsector totals sum to 76.792 + 138.140 + 128 = **215.060**; the running text on p.32, Tabel
  16 on p.36 and Figuur 5 on p.35 all state **215.060**; and 716.874 + 215.060 = 931.934, which
  matches the 931.935 landbouw total to within the source's usual one-tonne rounding.
  `DECISION_expert` can retire C-074 in favour of C-077 (215.060, Tabel 16).

#### 3. Deliberate exclusions

Every figure seen and not captured, with its reason.

- **Out-of-scope chain stages** — §3.7 horeca en catering (Tabel 35, 36, 37, 38, 39, 40, 41, 42,
  43; Figuur 10, 11, 12) and §3.8 huishoudens (Tabel 44, 45, 46, 47, 48, 49; Figuur 13, 14), in
  full. Likewise the horeca/catering and huishoudens rows of Tabel 1, 2, 5, 8, 50, 53, 54, 55.
- **Aggregates spanning an out-of-scope stage** — Tabel 5's "Totaal retail, grootdistributie,
  horeca, catering en consumenten" (553.338 ton) and its whole-chain "Totaal" (3.210.384 ton);
  Figuur 4's whole-chain 3 210 385 / 2 016 092 / 1 194 295 ton and the p.20 text restating
  "3,2 miljoen ton" and "1.194.295 ton voedselverlies"; Tabel 56 (whole-chain per capita).
  **Figuur 3 (p.21)** is excluded three times over and was missing from this list until the
  review: it is the same whole-chain destination infographic as Figuur 4 but for **2020**, so
  it fails the stage rule, the reference-year rule and the destination rule at once.
- **Destination and collection-route values** — not extracted, indexed instead in
  `destination_index.csv` (18 rows). This is the *destination* axis (diervoeder, vergisting,
  verbranding, biobrandstof, biochemie, bodem) and the *collection* axis (selectief ingezameld
  vs restafval). It is **not** the `voedselverlies` / `nevenstroom` axis, which is register
  data and was captured throughout — see the correction below.
- **Tabel 8 (p.20) in full, and most of Tabel 7 (p.19)** — both are cross-tabs of
  `quantity_type` against a collection route. Their quantity-type totals are printed elsewhere
  and were captured from there (landbouw in Tabel 16, visveilingen in Tabel 11, PO's in Tabel
  19, voedingsindustrie in Tabel 22, retail in Tabel 32), so the route cells add nothing.
  **The exception is Tabel 7's "Totaal primaire sector" row**, whose quantity-type figures are
  printed *nowhere else* — these were captured as C-111…C-114 with the route named, and must
  never be summed with their siblings.
  - One rounding casualty worth naming: Tabel 7's visveilingen cells (102 and 102 ton) restate
    the 101,5 ton figures of Tabel 11 at whole-tonne precision, so they are a rounded
    restatement of a captured claim rather than a new one.
  - Tabel 7's landbouw `nevenstromen ingezameld` cell reads **215.060**, a third independent
    contradiction of C-074's 21.060.
- **`schenking`** (out of scope by `quantity_type.csv`) — Tabel 4 (p.15), Tabel 21 (p.44),
  Tabel 27 (p.54), the 535 ton PO donation (p.38), the 3.525 / 5.451 ton in Figuur 8 and 9, the
  9 510 ton in Figuur 4, and the schenkingen rows of Tabel 26 and Tabel 34. Also Tabel 20's
  "Totaal 15.724 ton" niet-verkocht product, because it is the sum of a captured reststroom
  (15.189) and a donation (535) and therefore has no valid `quantity_type`.
- **Non-convertible units** — Figuur 6 reports **komkommers (226.200) and kropsla (50.931) in
  1.000 stuks**, with no mass basis anywhere in the source; the other eight crops in that figure
  are in ton and were captured. All kg/inwoner figures (Tabel 1 retail row, Tabel 3, 52, 53,
  54, 55, 56; Figuur 15, 16) are per-capita and cannot be converted without a population
  figure. The ± 5.000 ha of unharvested potato area (p.31) is an area, not a mass.
- **Not a quantity of material** — all cascade-index values (Tabel 6, 18, 24, 31, 38, 47),
  every percentage table (Tabel 13, 15, 33, and the % rows of 22, 23, 29, 30, 32), and the
  year-on-year deltas on p.60 ("+20.760 ton", "8.600 ton meer naar diervoeder", "bijna 49.000
  ton toename").
- **Non-Flemish geography** — the Wallonië, Brussel and België rows of Tabel 51, 52, 53, 54,
  55 and Tabel 3, and all other member states in Tabel 56. Per the session decision, the
  Belgian EU-definition figures were not captured because Flemish figures for the same
  quantities exist.
- **Rounded restatements of a figure captured precisely elsewhere** — "932.000 ton" (p.30),
  "afgerond 341.000 ton" (p.30), "afgerond 269.000 / 577.000 ton" (p.31), "afgerond 14.000 ton"
  (p.31), "624.000 ton" (p.35), "ongeveer 2 miljoen ton" (p.45), "circa 308.000 ton" (p.16).
- **Exact restatements** (same value, different location; captured once, from the location
  named in the workbook) — 279.114 and 60.084 recur in Tabel 50/51/52; 2.017.748, 472.557 and
  1.545.191 recur across Tabel 5, 23, 25, 26 and Figuur 8; 15.189 / 15.181 / 8 recur in Tabel
  17, 20 and Figuur 7; 132.082 / 59.849 / 72.233 recur in Tabel 29, 34 and Figuur 9; 203 recurs
  in the p.27 text and Tabel 10's Totaal row; 215.060, 408.874 and 716.874 recur across the
  p.32 text, Tabel 16 and Figuur 5. **Chapter 4 produced no new claims at all** — every Flemish
  in-scope figure in it restates Tabel 1 or Tabel 2.
- **Visserij (§3.1) yielded nothing.** Tabel 9 (p.26) has columns for 2015, 2017 and 2020 only,
  and its 2020 cells read "N/A" — since the aanlandingsplicht took effect in 2019, the source
  says teruggooi volumes are no longer tracked. Under the 2023-only session rule its 2015
  (10.402 / 5.201 / 5.201 ton) and 2017 (2.823 / 1.417 / 1.417 ton) figures were left for S004.
  The undersized-fish (BMS) stream is named on p.25 but the source gives no tonnage for it.
  **The only visserij-stage rows in this extraction are the Tabel 10 aanvoer figures.**

#### 4. Completeness sweep — disposition of all 57 tables, 16 figures and 1 schema

Every numbered object in the source's own *Tabellen* / *Figuren* index, in exactly one bucket.

**Captured** (13 tables + 1 figure): T1 (C-001) · T2 (C-002, C-003) · T5 (C-004) · T7, rij
Totaal primaire sector (C-111…C-114) · T10 (C-009…C-035) · T11 (C-006…C-008) · T12
(C-036…C-050) · T14 (C-051…C-074) · T16 (C-075…C-077) · T17 (C-087) · T19 (C-088, C-089) ·
T22 (C-090…C-092) · T23 (C-093…C-100) · T28 (C-103…C-105) · T30 (C-106, C-107) · T32 (C-108,
C-109) · T34 (C-110) · F6 (C-078…C-085). Plus five running-text figures: p.31 (C-005), p.38
(C-086), p.48 (C-101), p.52 (C-102), p.28 (within C-006…C-008).

**Excluded, with reason:**

| Object | Reason |
|---|---|
| T3, T55 | België-niveau; Vlaamse cijfers voor dezelfde grootheden bestaan |
| T4, T21, T27 | `schenking` — buiten scope per `quantity_type.csv` |
| T6, T18, T24, T31, T38, T47, T57 | cascade-index en wegingscoëfficiënten — geen hoeveelheid materiaal |
| T8 | inzamelwijze-cross-tab; alle quantity_type-totalen staan elders en zijn daar gecapteerd |
| T9 | enkel 2015/2017/2020; 2020 = "N/A". Visserij levert geen 2023-cijfer |
| T13, T15, T33 | percentages, geen tonnages |
| T20 | bestemmingen niet-verkocht product; het Totaal (15.724 t) mengt reststroom en schenking |
| T25, T29 | bestemmingssplitsing van een reeds gecapteerd totaal |
| T26 | herhalingen + schenkingen + percentages; geen nieuw cijfer voor 2023 |
| T35–T43, F10–F12 | horeca en catering — ketenschakel buiten scope |
| T44–T49, F13, F14 | huishoudens — ketenschakel buiten scope |
| T50, T51, T52 | Vlaamse 2023-cijfers herhalen T1/T2; andere gewesten buiten scope; kg/inw niet converteerbaar |
| T53, T54 | horeca/catering resp. huishoudens, per gewest |
| T56, F15, F16 | kg/inwoner, en volledige keten incl. huishoudens |
| F3, F4 | volledige keten (bevat horeca/catering/huishoudens); F3 bovendien referentiejaar 2020 |
| F5, F7, F8, F9 | cascade-infographics; elk cijfer erin herhaalt een gecapteerde waarde |

**Carries no numbers** (3): F1 (schema voedselgerelateerde stromen) · F2 (cascade van
waardebehoud) · Schema 1 (Vlaams vs Europees kader).

#### 5. Judgement calls & new dictionary members

- **C-102, the ~50.000 ton slaughterhouse stream (p.52), was captured against the 2023-only
  rule, with `reference_year = 2020`.** The protocol explicitly requires capturing a tonnage a
  source names and then excludes from its own totals ("huiden, botten, en dergelijke … omdat
  het niet om voedsel gaat"), and this figure is S080's own correction to the 2020 series — it
  will *not* appear in S002, which had it silently inside its nevenstroom total. Retire it via
  `DECISION_expert` if the reviewer prefers the year rule to win.
- **C-005, the 308.000 ton unharvested potatoes**, is likewise a figure the source excludes
  from its headline numbers ("vallen buiten de scope van de gerapporteerde cijfers") and is
  captured under the same protocol rule. Note it is also the exact difference between the
  excl./incl. variants of the aardappelen and akkerbouw/landbouw totals, so it must never be
  summed with them.
- **Tabel 10 rows carry `geography = Vlaanderen`** (reviewer decision, 2026-08-15) even though
  the table is titled "in Belgische havens" — all Belgian fishing ports lie in Flanders, so the
  two labels denote the same figure, and Tabel 11 indeed calls the same 203 ton total
  "Vlaanderen". The source's own wording is preserved in `source_type_label`. This is the
  **only** sanctioned Belgium→Flanders equivalence in the protocol.
- **Aanvoer vs opgehouden sit at different chain stages.** Per `chain_L2.csv`, a landing volume
  is `Visserij` and a withdrawn-at-auction figure is `Visveilingen`, so Tabel 10's two halves
  were split across the two stages even though they share a table.
- **"ruim 700.000 ton" (C-086) is an approximation**, captured as 700000 with the source's
  wording recorded in `source_type_label`. It is the PO's total aanvoer; the eight convertible
  crops in Figuur 6 sum to 632.483 ton, with komkommer and kropsla making up the rest in pieces.
- **`type_assumed = TRUE`** was set on the EU-definition rows (the source gives a "% eetbaar"
  but no tonnage split), the per-species opgehouden rows, the per-subsector voedingsindustrie
  rows (the source states outright that it does not publish the split per subsector), the two
  retail segment rows, the primary-sector aggregate and the two potato/pre-harvest rows.
- **New dictionary members** (added this session, before use): the voedingsindustrie subsector
  groupings and retail segments under `L2 = Gemengd`; `Zuivel` mapped to
  `Dierlijk - vee / Melk`; the `Aggregaat`-vs-real-group rule for chain-stage totals — all in
  `commodity_hierarchy.md`. In `chain_L2.csv`, the source's wordings
  "Producentenorganisaties groenten en fruit", "Voedingsretail en grootdistributie" and
  "Grootdistributie en supermarkten" were added to `variants_to_map`.
- **No Zotero item exists and `Sources.S080.citation_key` is blank** — flag **F-002** is still
  open; no Zotero MCP is wired. The PDF is archived at
  `register/archive/S080_OVAM Monitor voedselverlies 2023.pdf`.
