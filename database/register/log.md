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
| 2026-08-16 | S007 | MONBIO 3.0 | `S007_MONBIO3.0.pdf` | 195 (C-398…C-592) | no | `e3c61bc` | See [S007](#s007) — 1 suspected source error (in **S091**, found from here), 6 variant readings, 3 new dictionary members, no Zotero item (F-002) |
| 2026-08-16 | S091 | MONBIO 4.0 | `S091_MONBIO4.0.pdf` | 183 (C-215…C-397) | no | `0ae8225` | See [S091](#s091) — 0 suspected source errors, 5 variant readings, 4 session scope decisions, 15 new dictionary members, no Zotero item (F-002) |
| 2026-08-15 | S002 | OVAM Monitor voedselverlies 2020 | `S002_OVAM Monitor voedselverlies 2020.pdf` | 100 (C-115…C-214) | no | `73910c0` | See [S002](#s002) — 2 suspected source errors, 3 variant readings, no Zotero item (F-002) |
| 2026-08-15 | S080 | OVAM Monitor voedselverlies 2023 | `S080_OVAM Monitor voedselverlies 2023.pdf` | 114 (C-001…C-114), 1 retired | **yes** (2026-08-15) | `2486196` + `8d23344` | See [S080](#s080) — 1 source error retired by the reviewer, 3 variant readings, no Zotero item (F-002) |

*Note: S080 was extracted once before, on 2026-08-14 under protocol v1, producing 310 claims.
That run was **discarded** on 2026-08-15 — it captured horeca and catering, and predated the
provenance/unit columns. See commit `ad3b36c` for the withdrawn output. The row above is the
clean v2 re-run and supersedes it entirely.*

## Anomaly notes (detail, keyed by source_id)

### S007

**Same series, one edition back.** MONBIO 3.0 is the 2020 edition of the source extracted as S091.
The four session decisions taken for S091 were applied unchanged — **mest out**, **productie only**
(no import / export / aanbod), **MONBIO's `nevenstroom` and `productieresidu` both → `agri-food
waste` with `type_assumed = TRUE`**, **agri-food sectors only** — and none of them needed
revisiting. Reference year **2020** throughout; no MONBIO edition reprints its predecessor's
biomass years, so the S091 → S007 → S006 → S005 partition (2021 / 2020 / 2019 / 2018) holds without
a single contested figure.

**`source_page` uses dual notation here.** Unlike S080, S002 and S091, this PDF's **file page is
the printed folio + 2** throughout, so every row reads `73 (gedrukt 71)`. Note also that the NACE
product tables live in **Annex 2 at the back** (Tabel 78–87, file p.251–266) rather than inline as
in S091 — the discussion of each sector is in §5.2.1 and points forward to them.

**Structural differences from S091 worth a reviewer's eye.** Five, all of which changed what could
be captured:

1. **Tabel 15's TOTAAL row is not capturable here, where S091's was.** S007's consolidated table
   carries BOSBOUW (481 kton) and LANDSCHAPSBEHEER (151 kton) rows, so its TOTAAL (23.389 kton
   hoofd / 27.346 nev-res) spans material outside the register's agri-food scope. S091's table had
   no such rows, so its TOTAAL was landbouw + visserij and *was* captured (C-217). Only the
   LANDBOUW row survives here (C-398).
2. **The visserij figure and text measure different things here.** See *Variant readings*.
3. **Three Prodcom cells that were confidential in S091 carry a value here** — 106220 afvallen van
   zetmeelfabrieken (284.549 t, C-550), 108120 bietenpulp en andere afvallen van de suikerindustrie
   (661.550 t, C-555) and 108311 gebrande koffie (36.953 t, C-560) — plus 103213 pompelmoessap and
   103214 ananassap, and 102024 gerookte vis and 102034 bereide schaal-/weekdieren. Seven claims
   that have no counterpart in the 2021 edition.
4. **Tabel 28 classifies gries/griesmeel as a hoofdstroom, its own text as a nevenstroom.** See
   *Judgement calls*.
5. **Tabel 28's suiker-nevenstroom total uses the grondgebied basis, not the export proxy.** 56.806
   (melasse) + 337.649 (bietenpulp) = 394.455 ≈ the printed 394 kton, while Tabel 85's export-proxy
   cells give 111.298 + 661.550. Both bases are captured and cross-referenced.

#### 1. Variant readings

All captured; none of these is called an error.

- **Zeevisserij 2020: 18.306 t (tekst) vs 18.099 t (Figuur 30).** These are *not* two readings of
  one quantity — they are the total landing and its hoofdstroom subset, and the difference resolves
  exactly: vis 14.335 − 14.136 = 199, schaaldieren 1.287 − 1.285 = 2, weekdieren 2.684 − 2.678 = 6,
  against the 199 + 2 + 7 t opgehouden/afgekeurd stated on folio 91 (the weekdieren figure is 6 vs
  7, a one-tonne rounding). Both series captured — C-450…C-452 (aanlanding) and C-453…C-456
  (hoofdstromen) — cross-referenced and never to be summed. **This differs from S091**, where the
  figure was titled *Aanlanding* and matched the text exactly, so only one series existed there.
- **Suikerproductie Vlaanderen: 538.889 vs 275.044 vs 650.000 ton (C-553, C-572, C-573).** Same
  three-way split as S091: export proxy (69%), grondgebied share (35%), and a FoodIndustry (2020)
  estimate the source quotes beside its own. All three captured, never summed.
- **Melasse: 111.298 vs 56.806 ton (C-554, C-574); bietenpulp: 661.550 vs 337.649 ton (C-555,
  C-575).** Export proxy vs grondgebied, as above. Note S091 had no Prodcom value for bietenpulp at
  all, so this pair is new information.
- **Bier 2020: 23.572.769 hl vs 22.465.944 hl (C-586, C-587).** The federation's member figure —
  which it says covers 95% of volume — again exceeds Statbel's national total. Same unreconciled
  pair as in S091.
- **Mengvoederproductie Vlaanderen: 6.343.558 t (BFA) vs 7.509.423 t (PRODCOM) (C-577, C-583),**
  with Tabel 86's Prodcom lines (C-584 + C-585 = 7.810.524 + 201.771) a third reading. The source
  states it uses the BFA figure.
- **Rundsvlees, Vlaamse productie: the source's own sum changed definition between editions.**
  Here 67.677 = 101111 + 101131 (C-490); in S091 the equivalent 63.770 = 101111 + 101131 + 101312,
  i.e. the gezouten line was folded in. Both are the source's own arithmetic and both are captured
  as printed; the difference is recorded on the rows.

#### 2. Suspected source errors

One, and it is **not in this source — it is in S091**, found by comparing the two editions.

- **S091's Tabel 34 reprints three Flemish cells unchanged from S007's Tabel 82: C-339 (34.401 t),
  C-340 (66.426 t) and C-341 (395.511 t).** Arithmetic evidence that these are stale rather than
  coincidental:
  - Every other Flemish cell in these tables is the Belgian Prodcom quantity times a stated export
    ratio. In **S007** all three hold: 36.105 → 34.401, 69.715 → 66.426 and 445.329 → 395.511 all
    imply a ratio of about 0,95–0,89, in line with the table's own import/export columns.
  - In **S091** the same three Flemish values sit beside *different* Belgian quantities — 43.215,
    59.450 and 393.330 — and the implied ratios become 0,80, **1,12** and 1,01. **A Flemish figure
    cannot exceed its Belgian parent**, so C-340 is arithmetically impossible on S091's own data.
  - Applying S091's own export ratio (393.969 / 435.545 = 0,905) to its margarine quantity gives
    355.767, not 395.511.
  Captured as recorded in both sources, never corrected. **C-339, C-340 and C-341 now carry the
  cross-reference on the row**, so a reviewer meeting them in the 2021 extraction is pointed here;
  `DECISION_expert` can retire them in favour of the S007 rows C-529, C-530 and C-531, which are the
  values these cells actually describe.

Three further arithmetic oddities fell short of the evidence bar and are recorded here instead:

- **Tabel 19 (folio 82) sums to 23.479.129 against a printed TOTAAL of 23.482.130** — a gap of
  3.001 t, larger than rounding. Every row involved is mest and excluded, as is the total.
- **Tabel 16 (folio 80) sums to 6.732.317 against a printed 6.732.318** — one tonne. Captured as
  printed (C-445).
- **Tabel 28's "Vlees- en gevogelteverwerking, nev/res = 595 kton" (C-462) again counts 100.000
  *stuks* huiden as tonnes**, exactly as S091's 631 kton did: the mass-unit nevenstroom lines sum
  to 494.819, and 494.819 + 100.000 = 594.819 ≈ 595. The same unit slip in two consecutive editions.
  Captured as printed; a reviewer may want to retire both.

#### 3. Deliberate exclusions

Every figure seen and not captured, with its reason.

- **Out-of-scope sectors (session decision 4)** — §5.1.2 Bosbouw (T21–T23, F29), §5.1.4
  Landschapsbeheer (T24–T27), §5.2.2 Biogebaseerde economie in full (T35–T43, T88–T96), §5.2.3
  Verwerking van biologisch afval en afvalwater (T44–T47), and HOOFDSTUK 4 (the chemical BBS
  determination, T13–T14). Named tonnages left on the table include 482 kton bosbouwhout, 151 kton
  landschapsbeheer, ~600 kton pre-consumer houtnevenstromen, 1.285 kton papier, 103 kton zaaghout,
  and the vlas chain on folio 124 (130.000 t strovlas → 26.000 t gezwingeld vlas, 15.000 t klodden,
  65.000 t lemen, 15.000 t lijnzaad) — the last of which is also **referentiejaar 2019**, so it
  belongs to S006 twice over.
- **Sierteelt** — Figuur 21 prints **131.018 ton sierteelt-hoofdstroom** and Figuur 20 its 5.580 ha.
  Ornamental horticulture is not agri-food and has no member in `commodity_hierarchy.md`. Same call
  as in S091; the consequence is again that the eight captured gewasgroep rows do not sum to the
  plantaardige total (16.157.622 − 131.018 = 16.026.604).
- **Mest (session decision 1)** — Tabel 19 (folio 82): rundermest **14.774.109 ton**, varkensmest
  **7.417.245**, gevogeltemest **607.903**, andere mest **595.872**, and the TOTAAL **23.482.130**;
  Tabel 20 repeats them as *aanbod* and adds "mest (niet gedefinieerd) 440.000". With them go the
  mest-dominated aggregates of Tabel 15 (folio 71): LANDBOUW nev/res **27.195 kton**, DIERLIJK
  nev/res **23.482 kton**, TOTAAL nev/res **27.346 kton**. The two non-mest rows of Tabel 19 *were*
  captured (C-448, C-449). Also excluded: the mest trade on folio 82 (1 miljoen t import, 560.000 t
  export) and the mestverwerking figures on folio 155.
- **Import, export and aanbod (session decision 2)** — Tabel 15's six trade columns; Tabel 17,
  Tabel 18, Tabel 20; Figuur 22, 23, 24, 25, 26, 28 (folio 75–80); Figuur 31, 32 (folio 91–92);
  Tabel 56; and the NBB import/export columns of every NACE table. Named figures left there include
  15 miljoen ton geïmporteerde landbouwgrondstoffen, the 96.131 ton visserij-aanbod (folio 91) and
  the 3.478.092 ton aardappelaanbod aan de verwerkende industrie (folio 78).
- **Tabel 32 (folio 120), input voor de mengvoeders (8.256.158 t BE / 7.430.542 t VL and its
  breakdown)** — consumption of feedstuffs, not a stream arising. Named explicitly because it is
  again the richest nevenstroom table in the source (bijproducten oliehoudende zaden 1.494.971 t,
  bijproducten vermaling granen 804.769 t, suikerbereidingen 430.142 t, Vlaamse cijfers), and a
  reviewer may well want it back.
- **Values belonging to an earlier edition in the `Sources` sheet** — the four OVAM/IMJV tables for
  **2018** (Tabel 44, 45, 46, 47, folio 152–158, incl. the 1.797.073 t TOTAAL nevenstromen zonder
  afvalstatuut and the 1.701 kton vers plantaardig en dierlijk materiaal quoted on folio 5), which
  are S005's; Tabel 41's 2019 energiebalans and the 2019 vlas chain, which are S006's; the 2019
  visserij-aanlanding of 19.309 ton (folio 90) and the 2019 landbouwareaal (615.042 / 449.490 ha,
  folio 73), also S006's; and the 2018 teruggooi of 8.775 ton (folio 90), which is S005's. The
  zuivel sentence on folio 115 quoting the 2018 OVAM estimate (melkwei 49.722 t, zuiveringsslib
  20.445 t) is skipped for the same reason — but note Tabel 28's zuivel nev/res of 70 kton (C-467),
  captured as a 2020 figure, is 49.722 + 20.445 = 70.167, i.e. the source carries the 2018 estimate
  forward. Flagged on the row, exactly as in S091.
- **2020 voedselreststroom figures reprinted from the OVAM monitor** — Tabel 29 (folio 110) and the
  folio 110 text (1.999.983 t totaal, 229.240 t voedselverlies, 1,77 miljoen t nevenstromen,
  1,1 miljoen t naar diervoeder). Already captured from **S002** (C-190…C-193). Indexed in
  `destination_index.csv`.
- **Destination and collection-route values** — indexed in `destination_index.csv` (4 rows):
  Tabel 29, Tabel 43, Tabel 44/45, Tabel 41/42.
- **`afgeleid product`** (out of scope by `quantity_type.csv`) — Prodcom **101316** "Meel, poeder en
  pellets van vlees, niet geschikt voor menselijke consumptie; kanen" (**122.916 ton**, Tabel 78)
  and **104119** "Andere dierlijke vetten en oliën" (**76.939 ton**, Tabel 82). Both are made *from*
  slaughterhouse residuals. The raw streams they come from are captured (C-483 niet-eetbare ruwe
  slachtafvallen, C-482 dierlijk vet).
- **Non-convertible units** — Prodcom **101142** huiden en vellen, **100.000 stuks** (Tabel 78);
  Prodcom **105210 consumptie-ijs, 64.571.415 liter** (Tabel 83), for which the source gives a
  density for melk and for dranken but not for ice cream; Prodcom **110110 gedistilleerde dranken,
  133.952 hl** (Tabel 87), where the footnote says *hectoliter zuivere alcohol*. All areas
  (624.727 / 611.644 / 447.353 ha, Figuur 19 and 20) and all m³ volumes (77.316 m³ landschapsbeheer,
  267.000 m³ rondhout) are likewise not masses.
- **Regulatory allowances, not arisings** — folio 90 states that Belgium may still discard "105 ton
  tong, 152 ton wijting, en 43 ton andere soorten" under its EU exemption. These are permitted
  quantities set by policy, not measured volumes.
- **Confidential cells (`C`)** — a large share of every NACE table, worst in Tabel 82 where the
  source says outright that "het grootste volume, de nevenstroom van schroot of meel is
  confidentieel". A `C` is an absence, never a zero.
- **Not a quantity of material** — Tabel 4–12 (economic indicators), Tabel 1, 2, 3 (the *taxonomy*
  lists of which streams exist — no numbers), Tabel 48–77 (indicator framework, per-capita
  purchases, IDR, nutrient balances, erosion, cascade-index, GHG, patents, incomes, methodology,
  NACE/Prodcom systematics), the animal-count column of Tabel 16 (268.090.501 dieren), every
  percentage column, and all year-on-year deltas (−404.718 t, −185.488 t, −128.686 t, −106.231 t,
  +43.000 t, +412.490 t, −308.535 t, −199.240 t, −112.873 t, −322.621 t, −230.000 t).
- **Ranges and shares with no single value** — "Tereos-Syral verwerkt jaarlijks 600.000 tot 700.000
  ton tarwe" (folio 117, a company *input* and a range); the mouterij nevenstromen given only as
  percentages (orgettes 2-3%, moutkiempellets 3% op de mout, folio 122); schuimaarde (6% van de
  bieten) and bietenstaartjes (2-3%) on folio 118.
- **Aggregates with no valid `quantity_type`** — Tabel 28's **Visverwerking (44 kton)** and
  **Verwerking van fruit, groenten en hun sappen (1.598 kton)** sit in cells *merged across* the
  hoofd and nev/res columns, so neither is a hoofdstroom nor a reststroom figure. Same call as
  S091's and S002's. Nothing is lost: both reconcile against captured detail lines — visverwerking
  11.082 + 3.948 + 20.490 + 182 + 8.000 = 43.702, and fruit/groenten/sappen 107.972 (sappen, at the
  source's own 1.040 g/l) + 1.489.887 (vaste producten) = 1.597.859. Tabel 28's diervoeder nev/res
  reads "-", which is "not applicable", not a zero.
- **Non-Flemish geography where a Flemish figure exists** — the Belgian **Prodcom "Hoeveelheid"**
  column of every NACE table, since each of those tables also carries the source's own "Productie
  Vlaanderen" column. The one visible case in the text is bostel: folio 122 calls 113.637 ton a
  Belgian figure while Tabel 87 places it in the Vlaanderen column; captured as Flemish (C-590)
  with the discrepancy on the row. **Tabel 30, Tabel 31 and Tabel 34 are the exception** — FEDIOL
  and Belgische Brouwers publish only nationally, so those 14 rows carry `geography = Belgie`
  (C-513…C-524, C-586, C-587).
- **Rounded restatements of a figure captured precisely elsewhere** — "16,2 miljoen ton" and
  "3,7 miljoen ton" (folio 4, 78); Tabel 15's 16.158 / 6.732 / 18 kton, where Figuur 21, Tabel 16
  and Figuur 30 give the precise value; "509 / 384 / 68 kton" vlees and "216 kton" slachtafval
  (folio 4); "1.732 kton" and "55 kton" aardappel; "33 miljoen liter appelsap", "44 miljoen liter
  gemengde sappen", "1,2 miljoen ton diepvriesgroenten" (folio 113); "meer dan 581 miljoen liter
  melk" and "780 kton" (folio 115, folio 5); "23,6 / 22,5 / 16,5 miljoen hl bier" (folio 122);
  "800 kton chocolade", "6.344 kton mengvoeder", "114 kton bostel", "630 kton" and "1.376 kton"
  (folio 4-5). Each is listed in `also_stated_in` on the row holding the precise value.

#### 4. Completeness sweep — disposition of all 96 tables and 55 figures

**Captured** (17 tables + 2 figures + 6 text passages):

| Object | Page (file / gedrukt) | Claims |
|---|---|---|
| Tabel 15 | 73 / 71 | C-398 |
| Figuur 21 | 76 / 74 | C-399…C-407 |
| tekst (gewassen) | 77 / 75 | C-408…C-418 |
| Figuur 27 | 81 / 79 | C-419…C-426 |
| tekst (nevenstromen per gewas) | 80-81 / 78-79 | C-427…C-438 |
| Tabel 16 | 82 / 80 | C-439…C-445 |
| tekst (paarden-/schapenvlees) | 82 / 80 | C-446…C-447 |
| Tabel 19, de twee niet-mest rijen | 84 / 82 | C-448…C-449 |
| tekst + Figuur 30 (visserij) | 92-93 / 90-91 | C-450…C-460 |
| Tabel 28 | 110 / 108 | C-461…C-472 |
| Tabel 78 | 251-252 / 249-250 | C-473…C-489 |
| tekst (vlees-sommen) | 113 / 111 | C-490…C-493 |
| Tabel 79 | 253 / 251 | C-494…C-498 |
| Tabel 80 | 254 / 252 | C-499…C-501 |
| Tabel 81 | 255-256 / 253-254 | C-502…C-512 |
| Tabel 30 | 117 / 115 | C-513…C-518 |
| Tabel 31 | 118 / 116 | C-519…C-524 |
| Tabel 82 | 257-258 / 255-256 | C-525…C-532 |
| Tabel 83 | 259 / 257 | C-533…C-541 |
| Tabel 84 | 260-261 / 258-259 | C-542…C-552 |
| Tabel 85 | 262-264 / 260-262 | C-553…C-571 |
| tekst (suiker, melasse, pulp, chocolade) | 120 / 118 | C-572…C-576 |
| Tabel 33 | 123 / 121 | C-577…C-583 |
| Tabel 86 | 265 / 263 | C-584…C-585 |
| Tabel 34 | 124 / 122 | C-586…C-588 |
| Tabel 87 | 266 / 264 | C-589…C-590 |
| tekst (cichorei, vlas) | 181 / 179 | C-591…C-592 |

**Excluded, with reason:**

| Object | Reason |
|---|---|
| T1, T2, T3 | taxonomietabellen: welke hoofd- en nevenstromen bestaan per sector — bevatten geen cijfers |
| T4–T12 | macro-economische indicatoren (euro, jobs, arbeidsproductiviteit) — geen hoeveelheid materiaal |
| T13, T14 | PRODCOM-lijsten voor de chemische BBS-bepaling (hoofdstuk 4) — methodologie |
| T17, T18, T20 | handelsbalans resp. aanbod veeteelt — sessiebeslissing 2 (enkel productie) |
| T19, mestrijen | mest — sessiebeslissing 1; tonnages staan in de uitsluitingslijst hierboven |
| T21–T27 | bosbouw en landschapsbeheer — geen agrovoedingsschakel (sessiebeslissing 4) |
| T29 | bestemmingen voedselreststromen 2020 (OVAM & ALZ) — bestemmingsas én reeds gecapteerd via S002 |
| T32 | input/verbruik van de voedersector — geen ontstane stroom (sessiebeslissing 2) |
| T35, T36, T37 | zagerij-, hout- en papiersector — buiten scope |
| T38, T39, T40 | chemische productfamilies en BBS-toplijsten — geen hoeveelheid materiaal |
| T41, T42, T43 | bio-energiebalans in PJ; T41 bovendien referentiejaar 2019 (hoort bij S006); T43 zuivere verbrandingsbestemming |
| T44–T47 | OVAM/IMJV-afvaltabellen met referentiejaar 2018 — horen bij S005 (geverifieerd in de S005-PDF) |
| T48–T55, T57–T66 | indicatorenkader, aankopen per capita, IDR, dood hout, nutriëntenbalansen, erosie, cascade-index, broeikasgassen, octrooien, inkomens, beleidsdoelen |
| T56 | handel en netto import 2020 — handelsstromen (sessiebeslissing 2) |
| T67–T77 | Annex 1: methodologie, NACE/Prodcom-systematiek, sectorselectie, databronnen |
| T88–T96 | Annex 2: textiel, kleding, leder, hout, meubelen, papier, chemie, farma, kunststof — buiten scope |
| F19, F20 | landbouwareaal in ha — oppervlakte, geen massa |
| F22, F23, F24 | handelsbalans, import en export plantaardige hoofdstromen — sessiebeslissing 2 |
| F25, F26, F28, F31, F32 | aanbodfiguren (landbouw, verwerkende industrie, nevenstromen, visserij) — sessiebeslissing 2 |
| F29 | houtvoorraad per boomsoort in m³ — bosbouw, en geen massa |
| F35, F36, F37 | sectorverhoudingsschema's in % binnen de voedingssector — geen tonnages |
| F17, F18, F33, F34 | conceptuele stroomschema's van de bio-economie — bevatten geen cijfers |
| F1–F16, F38–F55 | economische, indicator- en methodologiefiguren van hoofdstuk 3, 6 en 7 |

#### 5. Judgement calls & new dictionary members

- **Gries en griesmeel (Prodcom 106132, C-548) was classified as a nevenstroom, following the
  source's own text and against its own Tabel 28.** Folio 117 says the maalderijen produce tarwemeel
  as hoofdstroom "en een aantal nevenstromen zoals gries, griesmeel en zemelen". But Tabel 28's
  maalderij hoofd of 2.248 kton only reconciles *with* the gries line included (2.149.880 + 98.390 =
  2.248.270), and its nev/res of 563 kton is exactly zemelen + afvallen van zetmeelfabrieken
  (278.865 + 284.549 = 563.414). S091 does the opposite: its hoofd of 2.102 kton excludes gries.
  The text is explicit and consistent across both editions, so the text wins; the discrepancy is
  recorded on the row.
- **The visserij aanlanding and hoofdstroom series are both captured** (11 claims where S091 needed
  7), because here they are genuinely different quantities. See *Variant readings* for the
  reconciliation. Retire C-450…C-452 if the reviewer prefers only the hoofdstroom series.
- **Cichorei (90.000 t) and vlas (23.000 t) were captured from HOOFDSTUK 6** (C-591, C-592), not
  from the biomass chapter. §6.2.4 is the only place in the source that quantifies these two crops
  for 2020, and both are 2020 primary production, so they pass all three filters even though the
  surrounding paragraph is about the *destination* of the biomass.
- **Paardenvlees (1.163 t) and schapen-/geitenvlees (1.858 t) were assigned `Primaire productie`**
  (C-446, C-447), the same call as in S091 and for the same reason: the source presents them inside
  the veeteelt-hoofdstromen section. Note that here, unlike in S091, they do **not** reconcile
  Tabel 15's DIERLIJK row against Tabel 16's TOTAAL — S007's 6.732 kton is simply Tabel 16's
  6.732.318 rounded, so the two editions define that row differently. Flagged.
- **The NACE 10.13 / 10.7 / 10.42 lines the source excludes from its own totals were captured**
  (C-485…C-489 bacon, worst, conserven; C-551 vers brood; C-552 koekjes; C-531 margarine), under
  "do not inherit the source's own scope exclusions". The source drops them **to avoid double
  counting**, which is a real reason, so every row says so and **they must never be summed with
  their precursors**.
- **Approximations captured with the source's wording**: teruggooi "minstens 7.707 ton" (C-457),
  afgekeurde appelen "14.000 ton" (C-438), bietenpulp "337.649 ton (3.5-5% van de biet)" (C-575),
  chocolade "ongeveer 800.000 ton" (C-576), suiker "650.000 ton" (C-573), cichorei "ruim 90.000 ton"
  (C-591).
- **Unit conversions all use factors the source itself supplies** (folio 106): 1.040 g/l for sappen,
  1.030 g/l for melk, 1.050 g/l for dranken (applied per hl, ×0,105), plus kton → ton. No other
  conversion was made.
- **`type_assumed = TRUE` on all 53 `agri-food waste` rows**, by session decision 3 — MONBIO never
  states edible vs inedible.
- **New dictionary members** (three): `Koffie` under `Specerijen`, and `Cichorei` and `Vlas` under
  `Industriele gewassen`. The last two already existed under `Suikerbieten en nijverheidsgewassen`,
  so they now sit in both — the direct consequence of carrying MONBIO's overlapping crop partition,
  and covered by the never-sum-across warning in `commodity_hierarchy.md`.
- **The `Sources` sheet's stale `extraction_status` was corrected this session** (user decision,
  2026-08-16): S005 and S006 read "EXTRACTED - source read, claims taken" but have no row in the
  corpus. Both now read "NOT EXTRACTED (was stale metadata from the superseded root-level corpus;
  corrected 2026-08-16)". S007's own status was set to EXTRACTED by this session.
- **No Zotero item exists and `Sources.S007.citation_key` is blank** — flag **F-002** is still open.
  The PDF is archived at `register/archive/S007_MONBIO3.0.pdf`.

### S091

**What this source is, and why it reads nothing like S080/S002.** MONBIO 4.0 is an *economy-wide
bio-economy monitor* (297 p., 96 tables, 68 figures), not a food-loss monitor. It measures the
whole Vlaamse bio-economie — landbouw, visserij, bosbouw, landschapsbeheer, voeding & dranken,
textiel, hout, papier, chemie, bio-energie, afvalsectoren — in **productie / import / export /
aanbod** columns, and it splits every stream into **hoofdstromen / nevenstromen /
productieresiduen**. Almost all of the extraction effort therefore went into *scope*, not into
reading numbers. Four session decisions (all taken by the user at session open) shaped it:

1. **Mest is out.** `database/hub.md` scopes BioMobi as "agri-food biomass side streams,
   excluding manure and OFMSW"; that exclusion is treated as binding on the register too. See
   *Deliberate exclusions* for every mest tonnage, so nothing is lost.
2. **Productie only.** Import, export and *aanbod* (= productie + import − export, computed by
   the source) are not quantities of material arising in Flanders, so they are not claims. This
   removed roughly two-thirds of the source's numbers.
3. **MONBIO's `nevenstroom` and `productieresidu` both map to `agri-food waste`, with
   `type_assumed = TRUE` on every such row.** MONBIO's split is *economic* (has value / has none),
   not edible/inedible as `quantity_type.csv` requires, so neither term can be mapped onto the
   register's `nevenstroom`. The source's own word is kept in `source_type_label`. Both terms are
   now recorded in `quantity_type.csv`.
4. **Agri-food sectors only** — §2.1 Landbouw, §2.2 Visserij en aquacultuur, §2.5 Voedings- en
   drankensector. Bosbouw, landschapsbeheer, hout, papier, textiel/kleding/leder, chemie/farma/
   kunststof, bio-energie and de afvalsectoren are not agri-food chain stages.

**Reference year: 2021, and it needed no negotiation.** S091's biomass chapters are *entirely*
2021; S007 (MONBIO 3.0) is entirely 2020, S006 (2.0) 2019 and S005 (1.0) 2018. Unlike the OVAM
series, MONBIO editions do **not** print evolution tables of their predecessors' years, so the
cross-source restatement rule bit in exactly one place: the four OVAM/IMJV waste tables that every
edition reprints unchanged for **2018** (T62–T65 here, T44–T47 in S007, T40–T41 in S005). Those
were checked in the S005 PDF and confirmed identical, so they belong to S005 and were skipped.
The chapter-1 economic indicators do run to 2022 — but they are euros and jobs, never tonnages.

Also of note: in this PDF the **file page equals the printed folio** throughout, so `source_page`
needs no dual notation. And the title page says *"update 2022"* while the Sources sheet says
*"update 2021-2022"* and every biomass table says 2021 — worth a reviewer's eye, but it changes
nothing: the tables state their own year.

**MONBIO's chain has no retail and no veilingen.** Every claim here sits at `Primaire productie`,
`Visserij`, `Visveilingen` (3 rows) or `Voedingsindustrie`. One row is `meerdere stadia`
(C-217, landbouw + visserij — both in scope, so the aggregate rule is satisfied).

#### 1. Variant readings

All captured; none of these is called an error.

- **Dierlijke hoofdstromen 2021: 6.682 kton (C-216) vs 6.723.055 ton (C-264).** Tabel 13 (p.39)
  and Tabel 14 (p.49) count different things, and the arithmetic says exactly what:
  6.723.055 − 43.110 (geiten- en schapenmelk) + 490 (paardenvlees) + 1.569 (schapen-/geitenvlees)
  = 6.682.004. Both rows carry the difference in their `stream_name_NL` and cross-reference each
  other. Tabel 14's own "TOTAAL (excl. geiten en schapen)" label is misleading: it applies to the
  *animal-count* column (which does sum to 273.488.996 without goats and sheep), not to the
  tonnage column, which does include the 43.110 ton.
- **Suikerproductie Vlaanderen: 556.283 vs 289.188 vs 650.000 ton (C-361, C-379, C-380).** The
  source itself prints three. 556.283 applies the export proxy (67% Vlaams); 289.188 applies the
  *grondgebied* share (35%, "geproduceerd op Vlaamse productiesites"); 650.000 is a Food Industry
  (2020) estimate the source quotes beside its own. These are three definitions, not three
  measurements — all three captured, cross-referenced, never summed.
- **Melasse: 91.958 vs 47.805 ton (C-362, C-381).** Same export-proxy vs grondgebied split as the
  sugar above.
- **Bier 2021: 24.003.327 hl vs 22.823.924 hl (C-393, C-394).** The federation's member figure
  (which it says covers 95% of volume) is *higher* than Statbel's national total. The source
  prints both side by side in Tabel 41 without reconciling them. Both captured, geography `Belgie`.
- **Mengvoederproductie Vlaanderen: 6.175.148 t (BFA) vs 7.444.934 t (PRODCOM) (C-384, C-390).**
  The source prints both in Tabel 39 and states it uses the BFA figure. Tabel 40's Prodcom lines
  (C-391 + C-392 = 7.716.604 + 198.524 = 7.915.128) are a third reading on the Belgian→Flemish
  ratio of the same quantity. All captured, cross-referenced, never summed.
- **Perskoeken/schroot: 1.019.363 t Vlaanderen (C-342, Tabel 34) vs 1.149 kton Belgie (C-335,
  Tabel 33).** Different scopes (Prodcom Vlaanderen vs FEDIOL Belgie) and the source says it used
  the FEDIOL figure for its totals. Not a contradiction; recorded because a reviewer will see two
  similar-sized oilseed-meal numbers.

#### 2. Suspected source errors

**None.** No figure in the in-scope chapters breaks its own table's total in a way that meets the
arithmetic-evidence bar. Three arithmetic oddities fell short of it and are listed here instead:

- **Tabel 17 (p.51) sums to 23.408.755 against a printed TOTAAL of 23.408.754.** A one-tonne
  rounding gap. The whole row set is mest-dominated and excluded anyway.
- **Tabel 26's "Vlees- en gevogelteverwerking, nev/res = 631 kton" (C-277) counts 100.000
  *stuks* huiden as if they were tonnes.** The Prodcom nevenstroom lines that *do* have a mass
  unit sum to 531.159 ton; 531.159 + 100.000 = 631.159, i.e. exactly the printed 631. This is
  arithmetic evidence of a **unit** slip rather than a digit slip, and the affected number is an
  aggregate the source computed, not a figure it measured — so C-277 is captured as printed with
  the finding recorded here. **A reviewer may want to retire it**; the hides themselves were not
  captured (see *Deliberate exclusions*).
- **Tabel 28's eetbaar-slachtafval text sum is 217.672 against 217.671 from its own lines**
  (82.576 + 84.141 + 49.893 + 1.061). One-tonne rounding; both the sum (C-308) and the lines are
  captured.

#### 3. Deliberate exclusions

Every figure seen and not captured, with its reason.

- **Out-of-scope sectors (session decision 4)** — §2.3 Bosbouw (T19–T21, F19), §2.4
  Landschapsbeheer (T22–T25), §2.6 Biogebaseerde sectoren in full (T43–T61, F21 is in-scope but
  carries no numbers, F23), §2.7 Afvalsectoren (T62–T65). None of these is an agri-food chain
  stage. Named tonnages left on the table there include 482 kton bosbouwhout, ~600 kton
  pre-consumer houtnevenstromen, 1.439 kton papier, 100.000 ton huishoudelijk afvalhout and
  420.000 ton groenafval (p.164).
- **Sierteelt** — Figuur 8 prints **137.091 ton sierteelt-hoofdstroom** (bosplanten,
  sierplanten) and Figuur 7 its 5.777 ha. Ornamental horticulture is grown on agricultural land
  but is not agri-food, and `commodity_hierarchy.md` has no member for it. Not captured; the
  akkerbouw/tuinbouw group rows around it (C-219…C-226) *are*, and the plantaardige total
  (C-218) includes sierteelt, so the eight captured groups do not sum to it.
- **Mest (session decision 1)** — Tabel 17 (p.51): rundermest **14.754.093 ton**, varkensmest
  **7.313.192**, gevogeltemest **626.178**, andere mest **628.292**, and the TOTAAL
  **23.408.754**; Tabel 18 (p.51) repeats them as *aanbod* and adds "mest (niet gedefinieerd)
  240.000". The mest-dominated aggregates of Tabel 13 (p.39) go with them: LANDBOUW nev/res
  **27.021 kton**, DIERLIJK nev/res **23.409 kton**, TOTAAL nev/res **27.021 kton** — 94% of the
  dierlijke figure is manure by the source's own account (p.39: "voor het overgrote deel …
  mest"). The two non-mest rows of Tabel 17 (dode dieren, afgekeurde melk) *were* captured
  (C-267, C-268). Also excluded: the mest trade and mestverwerking figures on p.51 and p.165
  (800.000 / 560.000 ton import/export, 34,4 miljoen kg N).
- **Import, export and aanbod (session decision 2)** — Tabel 13's six import/export columns
  (p.39); Tabel 15, Tabel 16, Tabel 18 (p.50-51); Figuur 9, 10, 11, 12, 13, 15 (p.43-49); Figuur
  17, 18 (p.56); Tabel 74 (p.200); the import/export/consumptie columns of Tabel 32, 33, 39, 41;
  and the NBB import/export columns of every NACE table (T28–T42). Named figures left there
  include 15 miljoen ton geïmporteerde landbouwgrondstoffen, the 101.700 ton visserij-aanbod
  (p.56), and the 3.480.729 ton aardappelaanbod aan de verwerkende industrie (p.46).
- **Tabel 38 (p.104), input voor de mengvoeders (7.978.403 t BE / 7.180.563 t VL and its
  breakdown)** — consumption of feedstuffs by the feed industry, not a stream arising. Excluded
  under the same decision. Named explicitly because it is the single richest nevenstroom table in
  the source (bijproducten oliehoudende zaden 1.415.473 t, bijproducten vermaling granen 813.871 t,
  suikerbereidingen 397.437 t, Vlaamse cijfers) and a reviewer may well want it back.
- **Values belonging to an earlier edition in the `Sources` sheet** — the four OVAM/IMJV tables
  for **2018**: Tabel 62 en 63 (p.161-162, secundaire afvalstoffen en grondstoffen door de
  afvalsectoren), Tabel 64 (p.166-167, primaire afvalstoffen per NACE-sector) and Tabel 65
  (p.168-169, nevenstromen en productieresiduen zonder afvalstatuut per NACE-sector, TOTAAL
  1.797.073 ton). Verified present in the S005 PDF (its Tabel 40 and 41, p.129 and p.131), so
  S005 owns them. The p.94 zuivel sentence quoting the same 2018 source (melkwei 49.722 ton,
  zuiveringsslib 20.445 ton) is skipped for the same reason — but note that Tabel 26's zuivel
  nev/res of 70 kton (C-282), which *is* captured as a 2021 figure, is 49.722 + 20.445 = 70.167,
  i.e. the source carries the 2018 estimate forward as its 2021 number. Flagged on the row.
  Also skipped: the 2020 visserij-aanlanding of 18.099 ton (p.55 → S007), the 2018 teruggooi of
  8.775 ton (p.54 → S005), and Tabel 59's 2019 energiebalans (→ S006).
- **2020 voedselreststroom figures reprinted from the OVAM monitor** — Tabel 27 (p.78) and the
  p.77 text (1.999.983 ton totaal, 229.240 ton voedselverlies, 1,77 miljoen ton nevenstromen,
  1,1 miljoen ton naar diervoeder). These are OVAM & ALZ (2023) figures already captured from
  **S002** (C-190…C-193). Indexed in `destination_index.csv`.
- **Destination and collection-route values** — not extracted, indexed instead in
  `destination_index.csv` (4 rows): Tabel 27 (p.78), Tabel 61 (p.159), Tabel 62/63 (p.161-162),
  Tabel 59/60 (p.157-158).
- **`afgeleid product`** (out of scope by `quantity_type.csv`) — Prodcom **101316** "Meel, poeder
  en pellets van vlees, niet geschikt voor menselijke consumptie; kanen" (**121.541 ton**,
  Tabel 28 p.82) and **104119** "Andere dierlijke vetten en oliën" (**74.278 ton**, Tabel 34
  p.92). Both are products manufactured *from* slaughterhouse residuals — the dictionary names
  "diermeel, dierlijke vetten" as its examples. The raw streams they are made from *are* captured
  (C-298 niet-eetbare ruwe slachtafvallen, C-297 dierlijk vet).
- **Non-convertible units** — Prodcom **101142** "Gehele huiden en vellen van runderen of van
  paardachtigen, ongelooid: **100.000 stuks**" (Tabel 28 p.81): a piece count with no mass basis
  anywhere in the source. Prodcom **105210 consumptie-ijs, 65.497.290 liter** (Tabel 35 p.95):
  the source supplies a density for *melk* (1.030 g/l) and for *dranken* (1.050 g/l) but none for
  ice cream. Prodcom **110110 gedistilleerde dranken, 164.694 hl** (Tabel 42 p.107): the footnote
  says this is *hectoliter zuivere alcohol*, to which the source's general drinks density does not
  apply. All areas (624.634 / 611.359 / 447.074 ha, Figuur 6 and 7) and all volumes in m³
  (bosbouw, 40.000 m³ houtbouw p.199) are likewise not masses.
- **Confidential cells (`C`)** — a large share of every NACE table. Tabel 34 (oliën) is the worst
  hit: the source says outright that "het grootste volume, de nevenstroom van schroot of meel is
  confidentieel". A `C` is an absence, not a zero, and was never filled in.
- **Not a quantity of material** — Tabel 1–9 (economic indicators, €/jobs/productivity),
  Tabel 10, 11, 12 (p.38-39: these are the *taxonomy* lists of which streams exist, no numbers),
  Tabel 66–96 (indicator framework, per-capita purchases, IDR ratios, nutrient balances, erosion,
  cascade-index, GHG, patents, incomes, NACE/Prodcom methodology, chemical BBS), the animal-count
  column of Tabel 14 (273.488.996 dieren), the percentage columns of Tabel 14/16/17/18/32/33/38/39,
  and every year-on-year delta (+531.220 t, +672.732 t, −101.263 t, +87.566 t, −409.355 t,
  −1.637 t, −131 t, −816.222 t, +33.000 t).
- **Ranges and shares with no single value** — "Tereos-Syral verwerkt jaarlijks 600.000 tot
  700.000 ton tarwe" (p.96, a company processing *input*, and a range); the mouterij nevenstromen
  given only as percentages ("orgettes 2-3%", "moutkiempellets 3% op de mout", p.106); schuimaarde
  ("6% op het gewicht aan bieten") and bietenstaartjes ("2-3%") on p.99.
- **Aggregates with no valid `quantity_type`** — Tabel 26's **Visverwerking (32 kton)** and
  **Verwerking van fruit, groenten en hun sappen (1.563 kton)** are printed in cells *merged
  across* the hoofd and nev/res columns, so neither is a hoofdstroom figure nor a reststroom
  figure. Same call as S002's Tabel 26 "Totaal 17.586 ton". Their component lines are captured
  from Tabel 29 and Tabel 31, and both merged cells do reconcile against those lines
  (visverwerking 11.591 + 20.169 = 31.760; groenten/fruit/sappen 91.104 + 1.318.543 + 153.028 =
  1.562.675), which is why nothing is lost by dropping them. Tabel 26's diervoeder nev/res reads
  "-", which is "not applicable", not a zero, and was not captured either.
- **Non-Flemish geography where a Flemish figure exists** — the Belgian **Prodcom "Hoeveelheid"**
  column of every NACE table. Each of those tables also carries a "Productie Vlaanderen" column,
  which the source derives itself by applying a stated export ratio or sector share; that Flemish
  column is what was captured. The one place this is visible in the text is bostel: p.106 says
  "in België zo'n 176.989 ton", Tabel 42 gives 134.653 ton for Vlaanderen, and C-397 holds the
  Flemish figure with the Belgian one noted. **Tabel 32, Tabel 33 and Tabel 41 are the
  exception** — FEDIOL and Belgische Brouwers publish only at Belgian level, so those rows carry
  `geography = Belgie` (C-324…C-335 en C-393, C-394), per the protocol's "Belgie where only a
  national figure exists".
- **Rounded restatements of a figure captured precisely elsewhere** — "16,7 miljoen ton" and
  "3,6 miljoen ton" (p.4, p.47); "16.689 / 3.612 / 6.682 / 16 kton" in Tabel 13 where Figuur 8,
  Figuur 14 and Figuur 16 give the precise value; "23.371 en 16 kton" restated on p.189;
  "549 / 443 / 64 kton" vlees and "218 kton" slachtafval (p.4); "33 miljoen liter appelsap",
  "40 miljoen liter gemengde sappen", "1,2 miljoen ton diepvriesgroenten" (p.87); "meer dan 539
  miljoen liter melk" (p.94); "24 / 22,8 / 17,4 miljoen hl bier" (p.106); "zo'n 900 kton
  chocolade" (p.5); "504 kton" and "1.149 kton" (p.4, p.90); "57 kton" aardappelnevenstroom and
  "135 kton" bostel in Tabel 26. Each is listed in `also_stated_in` on the row that holds the
  precise value.

#### 4. Completeness sweep — disposition of all 96 tables and 68 figures

Every numbered object in the source's own *Lijst van tabellen* (p.14-17) and *Lijst van figuren*
(p.18-21), in exactly one bucket.

**Captured** (18 tables + 2 figures + 6 text passages), with the exact id ranges:

| Object | Page | Claims |
|---|---|---|
| Tabel 13 | 39 | C-215…C-217 |
| Figuur 8 | 42 | C-218…C-226 |
| tekst (gewassen) | 43 | C-227…C-237 |
| Figuur 14 | 48 | C-238…C-245 |
| tekst (nevenstromen per gewas) | 47 | C-246…C-257 |
| Tabel 14 | 49 | C-258…C-264 |
| tekst (paarden-/schapenvlees) | 49 | C-265…C-266 |
| Tabel 17, de twee niet-mest rijen | 51 | C-267…C-268 |
| Figuur 16 | 55 | C-269 |
| tekst (aanlanding per groep) | 54 | C-270…C-272 |
| tekst (teruggooi, opgehouden vis) | 55 | C-273…C-275 |
| Tabel 26 | 76 | C-276…C-287 |
| Tabel 28 | 81-82 | C-288…C-304 |
| tekst (vlees-sommen) | 79-80 | C-305…C-308 |
| Tabel 29 | 84 | C-309…C-311 |
| Tabel 30 | 86 | C-312…C-314 |
| Tabel 31 | 88-89 | C-315…C-323 |
| Tabel 32 | 91 | C-324…C-329 |
| Tabel 33 | 91 | C-330…C-335 |
| Tabel 34 | 92-93 | C-336…C-342 |
| Tabel 35 | 95 | C-343…C-350 |
| Tabel 36 | 97-98 | C-351…C-360 |
| Tabel 37 | 100-102 | C-361…C-378 |
| tekst (suiker, melasse, pulp, chocolade) | 99 | C-379…C-383 |
| Tabel 39 | 105 | C-384…C-390 |
| Tabel 40 | 105 | C-391…C-392 |
| Tabel 41 | 106 | C-393…C-395 |
| Tabel 42 | 107 | C-396…C-397 |

**Excluded, with reason:**

| Object | Reason |
|---|---|
| T1–T9, F1–F5 | macro-economische indicatoren (euro, jobs, arbeidsproductiviteit) — geen hoeveelheid materiaal |
| T10, T11, T12 | taxonomietabellen: welke hoofd- en nevenstromen bestaan per sector — bevatten geen cijfers |
| T15, T16, T18 | handelsbalans resp. aanbod veeteelt — sessiebeslissing 2 (enkel productie) |
| T17, mestrijen | mest — sessiebeslissing 1; tonnages staan in de uitsluitingslijst hierboven |
| T19–T25, F19 | bosbouw en landschapsbeheer — geen agrovoedingsschakel (sessiebeslissing 4) |
| T27 | bestemmingen voedselreststromen 2020 (OVAM & ALZ) — bestemmingsas én reeds gecapteerd via S002 |
| T38 | input/verbruik van de voedersector — geen ontstane stroom (sessiebeslissing 2) |
| T43–T58 | textiel, kleding, leder, hout, meubelen, papier, chemie, farma, kunststof — buiten scope |
| T59, T60, T61 | bio-energiebalans in PJ; T59 bovendien referentiejaar 2019 (hoort bij S006); T61 zuivere verbrandingsbestemming |
| T62–T65 | OVAM/IMJV-afvaltabellen met referentiejaar 2018 — horen bij S005 (geverifieerd in de S005-PDF) |
| T66–T73, T75–T82 | indicatorenkader, aankopen per capita, IDR, dood hout, nutriëntenbalansen, erosie, cascade-index, broeikasgassen, octrooien, inkomens — geen hoeveelheid materiaal |
| T74 | handel en netto import 2020 — handelsstromen én referentiejaar 2020 (hoort bij S007) |
| T83–T96 | methodologie: NACE/Prodcom-systematiek, sectorselectie, databronnen, chemische BBS-lijsten |
| F6, F7 | landbouwareaal in ha — oppervlakte, geen massa |
| F9, F10, F11 | handelsbalans, import en export plantaardige hoofdstromen — sessiebeslissing 2 |
| F12, F13, F15, F17, F18 | aanbodfiguren (landbouw, verwerkende industrie, nevenstromen, visserij) — sessiebeslissing 2 |
| F20, F21, F22, F23 | sectorverhoudingsschema's in % binnen de voedingssector resp. papiersector — geen tonnages |
| F24–F44, F46–F68 | indicatoren-, methodologie- en conceptfiguren van hoofdstuk 3 en 4 |
| F45 | DMI-biomassa-inzet 2010-2021 (CE Monitor) — staafdiagram zonder afgedrukte waarden, en import + extractie samen |

**Carries no numbers** (5): F51, F52, F53, F54, F55 (conceptuele stroomschema's van de
bio-economie, hoofdstuk 4) — plus F56, F57 in the same series.

#### 5. Judgement calls & new dictionary members

- **MONBIO's gewasgroepen are a *second, overlapping* crop partition.** `Suiker- en
  zetmeelgewassen` (suikerbiet + aardappel) cuts straight across the register's existing
  `Aardappelen en knolgewassen` and `Suikerbieten en nijverheidsgewassen`; `Groenten` spans
  `Groenten openlucht` and `Groenten beschut`; `Industriele gewassen` (cichorei, vlas) overlaps
  `Suikerbieten en nijverheidsgewassen`. All four are now members, with an explicit
  **never-sum-across** warning in `commodity_hierarchy.md`. The alternative — re-cutting MONBIO's
  groups onto the OVAM partition — would have been a derivation, not a reading.
- **The plantaardige group rows do not sum to the plantaardige total**, by design: C-218
  (16.688.841 t) includes sierteelt, and the eight captured group rows (C-219…C-226) do not.
  16.688.841 − 137.091 (sierteelt) = 16.551.750. Same for the nevenstroom side, where Figuur 14
  simply has no fruit group.
- **`Vlees- en gevogelteverwerking` was given `Dierlijk - vee / Vlees` rather than `Gemengd`**
  (C-276, C-277), by the same reasoning the S080 session used for `Zuivel`: it is unambiguously
  animal meat, unlike OVAM's `Vlees, vis en gevogelte`, which mixes in fish. Every other MONBIO
  NACE grouping takes `Gemengd`, level 2.
- **Paardenvlees (490 t) and schapen-/geitenvlees (1.569 t) were assigned `Primaire productie`,
  not `Voedingsindustrie`** (C-265, C-266), even though meat arises at slaughter. The source
  presents them inside §2.1.4 *Veeteelt – hoofdstromen* and, as the arithmetic under *Variant
  readings* shows, counts them in its **primary-production** total. Assigning them by the chapter
  would have been wrong; assigning them by the event would have contradicted the source's own
  accounting. Flagged so a reviewer can overrule.
- **The NACE 10.13 / 10.7 / 10.42 / 10.9 lines the source excludes from its own totals were
  captured** (C-300…C-304 bacon, worst, conserven; C-359 vers brood; C-360 koekjes; C-341
  margarine; C-391, C-392 Prodcom-veevoeder), under the protocol's "do not inherit the source's
  own scope exclusions". The source drops them **to avoid double counting** with the upstream
  lines, which is a real reason — so every one of these rows says so in `source_type_label` and
  **they must never be summed with their precursors**. This is the largest single block a reviewer
  might want to retire, and it is deliberately grouped so that it can be.
- **Approximations captured with the source's wording in `source_type_label`**, following the
  S080 "ruim 700.000 ton" precedent: teruggooi ">7.500 ton" (C-273), afgekeurde appelen
  "± 14.000 ton" (C-257), bietenpulp "ongeveer 350.000 ton" (C-382), chocolade "ongeveer 900.000
  ton" (C-383), suiker "650.000 ton" (C-380).
- **Unit conversions all use factors the source itself supplies** (protocol: never derive one):
  1.040 g/l for sappen and 1.030 g/l for melk, both stated on p.74; 1.050 g/l for dranken, stated
  on p.75 (applied per hl, i.e. ×0,105); and kton → ton (×1.000). No other conversion was made —
  see *Non-convertible units* for the three cases where no factor existed.
- **`type_assumed = TRUE` on every `agri-food waste` row** (all 50 of them), by session decision 3:
  MONBIO never states edible vs inedible, so the quantity type is defaulted on every residual row
  in this source. This is a heavier use of the flag than in S080/S002 and is expected.
- **`Vis (alle soorten)`, `Schaaldieren` and `Weekdieren` were added as L4 members** so that
  Figuur 16's three components sit one level below the 16.683 t total (C-269). S080's combined
  `Schaal- en weekdieren` stays in the dictionary for the auction row (C-275), where the source
  does not split them.
- **The `Sources` sheet's `extraction_status` is stale for S005, S006 and S007** — all three read
  "EXTRACTED - source read, claims taken", but `streams_export.csv` holds no row from any of them.
  That metadata predates the in-repo register and describes the superseded root-level corpus. Left
  as found rather than silently rewritten, but a later session must not read it as "already done".
- **No Zotero item exists and `Sources.S091.citation_key` is blank** — flag **F-002** is still
  open. The PDF is archived at `register/archive/S091_MONBIO4.0.pdf`.

### S002

**Session rule (set by the user at session open):** only the **2020** column of this monitor's
evolution tables was captured. S002 is the third edition of the series (2015 · 2017 · 2020 ·
2023); S080 already captured 2023 and explicitly left 2020 to this source. The 2015 and 2017
columns were left to **S004** (2015 nulmeting, PDF queued in `inbox/`) and **S003** (2017
edition, in the `Sources` sheet but with **no PDF and not among the queued sources**). The
2017 risk was put to the user before extraction and the strict rule was chosen — see
*Deliberate exclusions* for exactly which tables and years were skipped, so they stay
recoverable from the archived PDF.

Also of note: in this PDF the **file page equals the printed folio** throughout (every page
prints "pagina N of 99"), so `source_page` needs no dual notation.

**Duplicate tables.** The source prints **Tabel 1 (p.11) and Tabel 7 (p.26) identically**, and
likewise **Tabel 2 (p.12) and Tabel 8 (p.27)** — same titles, same numbers, once in the
"Samenvattend overzicht" and once in the synthesis chapter. Every figure in them was captured
from the sector chapters instead (the more specific location) and both locations are listed in
`also_stated_in`.

#### 1. Variant readings

All captured or noted; none of these is called an error.

- **Visveilingen totale voedselreststroom 2020: 207,6 vs 208 ton.** Tabel 13 (p.35) prints the
  per-species total as 207,6; Tabel 4 (p.21), Tabel 5 (p.22), Tabel 16 (p.37) and the running
  text on p.35 and p.36 all print 208. This is a **rounded restatement**, so only the precise
  207,6 got a row (C-144), with the other locations in `also_stated_in`. Consequence worth
  knowing: the 104 + 104 voedselverlies/nevenstroom split (C-145, C-146) is derived by the
  source from 208, not from 207,6, so those two do not sum to C-144.
- **Retail selectief ingezameld: Tabel 43 (p.69-70) vs Tabel 36/40.** Tabel 43 gives 72.400 ton
  selectief ingezamelde voedselreststromen and 27.205 ton selectief ingezamelde
  voedselverliezen, where Tabel 36 (p.64) gives 71.967 and Tabel 40 (p.65) gives 26.897. Both
  are collection-route cells whose quantity-type totals are printed and captured, so neither
  became a row; recorded here and in `destination_index.csv`.
- **Rounding-level mismatches inside table totals** (captured as printed, nothing retired):
  Tabel 30's eight subsector totals sum to 1.999.384 against a printed 1.999.383; the primary
  sector parts (0 + 207,6 + 479.095 + 15.954 = 495.256,6) fall 0,4 ton short of Tabel 5's
  printed 495.257, which is the same 207,6/208 rounding.
- **Schenkingen: 17.035 vs 16.979 ton.** Tabel 3 (p.20) totals the donations at 17.035 ton;
  Figuur 1 (p.8) states 16.979 ton. Both are `schenking` and out of scope, so neither became a
  row.

#### 2. Suspected source errors

Both captured as recorded, never corrected, so `DECISION_expert` can retire them.

- **C-193 — voedingsindustrie, totale voedselreststroom 2020, Tabel 5 (p.22) prints
  1.999.983 ton.** Arithmetic evidence that two digits are transposed: Tabel 4 (p.21), Tabel 29
  (p.53), Tabel 30 (p.54), Tabel 34 (p.61) and Figuur 8 (p.57) all print **1.999.383**; Tabel
  29's own parts give 2.034 + 227.206 + 7.011 + 1.763.132 = 1.999.383; and Tabel 4's 2020
  column sums to exactly 3.051.469 — the printed chain total — only on the 1.999.383 basis.
  Retire C-193 in favour of C-190.
- **C-185 — veehouderij, totale voedselreststroom 2020, running text p.41 states "afgerond
  22.000 ton".** Arithmetic evidence: Tabel 17 (p.39) prints 12.989, Tabel 20 (p.41) gives
  12.891 + 98 = 12.989, the text on p.39 says "afgerond 13.000 ton", and the landbouw total
  reconciles exactly as 310.944 + 155.162 + 12.989 = 479.095. The same sentence also quotes
  "93%" voedselverliezen, which is the **2015** ratio in Tabel 21 (2020 = 99%), so this reads as
  a paragraph carried over unrevised from the previous edition. Retire C-185 in favour of C-159.

#### 3. Deliberate exclusions

Every figure seen and not captured, with its reason.

- **Out-of-scope chain stages** — §3.7 horeca en catering (Tabel 44, 45, 46, 47, 48, 49, 50, 51,
  52; Figuur 11, 12) and §3.8 huishoudens (Tabel 53, 54, 55, 56, 57, 58, 59, 60, 61; Figuur 13,
  14), in full. Likewise the horeca-, catering- and huishoudens-rows of Tabel 1, 2, 4, 5, 6, 7,
  8, 9 and 10.
- **Aggregates spanning an out-of-scope stage** — Tabel 4's "Totaal keten" (3.051.469 ton for
  2020); Tabel 5's "Totaal voedingsindustrie t/m huishoudens" (2.556.213 ton) and its "Totaal"
  row (3.051.469 ton plus the destination split); Figuur 1's whole-chain 3.051.469 /
  2.167.727 / 883.742 / 6.484.757 ton and the p.8 text restating "3 miljoen ton"; the p.11 text
  restating 883.742 ton; Tabel 11 (whole-chain per capita). **Figuur 2 (p.10)** is excluded
  three times over: it is the same whole-chain infographic as Figuur 1 but for **2015**, so it
  fails the stage rule, the reference-year rule and the destination rule at once.
- **Values belonging to an earlier edition in the `Sources` sheet** (see the session rule above)
  — the **2015** columns of Tabel 4, 5, 6, 9, 12, 17, 20, 21, 22, 23, 25, 26, 27, 34, 43 and
  Figuur 2, and the **2017** columns of Tabel 12 and Tabel 13. Named explicitly because they are
  the largest single block left on the table: Tabel 17/20's full 2015 landbouw breakdown (449.352
  ton total, 330.319 voedselverliezen, 119.033 nevenstromen), Tabel 13's 2015 and 2017 aanvoer
  and opgehouden per vissoort, and the 2015 sector totals 102 / 15.277 / 2.442.711 / 62.574 ton.
  These belong to **S004** (2015) and **S003** (2017). *S002 does state on p.21 that "een aantal
  data van 2015 werden lichtjes bijgestuurd" — the keten total moving from 3.485.157 to
  3.481.083 ton — but that revision is only quantified for the whole-chain figure, which is out
  of scope on its own; no in-scope 2015 sector figure is given a stated correction, so nothing
  was captured under the revision clause.*
- **Visserij (§3.1) yielded no reststroom figure.** Tabel 12 (p.34) has columns for 2015, 2017
  and 2020, and every 2020 cell reads "N/A" — since the aanlandingsplicht took full effect in
  2019, the source says teruggooi volumes are no longer tracked. Tabel 4 (p.21) likewise prints
  "n/a". **Tabel 5 (p.22) nevertheless prints a bare 0** for visserij 2020; that printed zero was
  captured as **C-148** and cross-referenced to the two n/a statements, because the register
  records what a source prints. The undersized-fish (BMS) stream is described on p.33 and
  explicitly excluded by the source as "niet-slachtrijp"; **no tonnage is given for it**, so
  there was nothing to capture under the "do not inherit the source's own scope exclusions"
  rule. The only visserij-stage rows in this extraction are the Tabel 13 aanvoer figures.
- **Destination and collection-route values** — not extracted, indexed instead in
  `destination_index.csv` (19 rows). This is the *destination* axis (voeder voor dieren,
  biochemie, bodem, vergisting/compostering, gfvo/biodiesel, dierlijke afvalverwerking,
  verbranden, andere) and the *collection* axis (selectief ingezameld vs restafval). It is **not**
  the `voedselverlies` / `nevenstroom` axis, which is register data and was captured throughout.
  Unlike S080, **every** quantity-type total in this source is printed somewhere outside a route
  cross-tab, so no equivalent of S080's C-111…C-114 was needed here.
- **`schenking`** (out of scope by `quantity_type.csv`) — Tabel 3 (p.20), Tabel 28 (p.52), Tabel
  35 (p.62), the 1.632 ton PO gratis verdeling (p.46, Tabel 26 and Figuur 7), the 16.979 ton in
  Figuur 1, the 5.697 / 2.428 / 3.269 / 9.706 / 1.664 ton on p.19, p.52 and p.62, and the
  schenkingen rows of Tabel 34 and Tabel 43. Also Tabel 26's "Totaal 17.586 ton" niet-verkocht
  product, because it is the sum of a captured reststroom (15.954) and a donation (1.632) and
  therefore has no valid `quantity_type` — the same call S080 made on its Tabel 20.
- **`slib`** (out of scope by `quantity_type.csv`) — the 484.693 ton waterzuiveringsslib of the
  voedingsindustrie (Tabel 29 p.53, the p.54 text, Tabel 30 p.55 and Tabel 34 p.61), and the
  5.030 + 40 ton vetslib of the retail (p.63 text, Tabel 37 and Tabel 38).
- **Non-convertible units** — all kg/inwoner figures (Tabel 10's rightmost column, Tabel 11,
  Figuur 15) are per-capita and cannot be converted without applying the population figure,
  which would be a derivation. The p.71 catering figure of "37 gram verlies per passage" has no
  mass basis either.
- **Not a quantity of material** — all cascade-index values (Tabel 6, 15, 19, 24, 31, 39, 47,
  56, 62), every percentage table (Tabel 9, 14, 18, 21, 23, 42, and the % rows of 5, 29, 30, 32,
  36, 37, 38, 40), the IMJV sample sizes and response rates (Tabel 33, 41 — counts of
  businesses, not tonnages), the Superlijst index scores (Figuur 9), and the year-on-year deltas
  ("+8.576 ton", "+27.639 ton", "-4.411 ton", "-443.328 ton", "+3.759 ton", "-447.086 ton",
  "met 106 ton verhoogd").
- **Non-Flemish geography** — the België row of Tabel 11 and all other member states in it.
- **Rounded restatements of a figure captured precisely elsewhere** — "479.000 ton" (p.38),
  "afgerond 311.000 / 155.000 / 13.000 ton" (p.39), "349.000 ton" and "130.000 ton" (p.41),
  "afgerond 155.000 ton" (p.41), "bijna 2 miljoen ton" (p.53), "ruim 1,1 miljoen ton" (p.46),
  "208 ton" for 207,6 (p.35, p.36, Tabel 4, 5, 16), "3 miljoen ton" (p.8).
- **Exact restatements** (same value, different location; captured once, from the location named
  in the workbook) — Tabel 1 and Tabel 7 are the same table, as are Tabel 2 and Tabel 8;
  479.095 / 348.786 / 130.309 recur across Tabel 4, 5, 17, 20, 22 and Figuur 6; 15.954 / 15.156 /
  798 recur across Tabel 4, 5, 23, 25, 26, 27 and Figuur 7; 1.999.383 / 229.240 / 1.770.143
  recur across Tabel 4, 29, 30, 32, 34 and Figuur 8; 85.802 / 37.381 / 48.421 recur across Tabel
  4, 5, 36, 37, 38, 40, 43 and Figuur 10. **Chapter 4 does not exist in this edition**; the
  synthesis chapter (§2) produced only four new claims — C-148, C-193 and C-210 from Tabel 5 and
  the four EU rows from Tabel 10.

#### 4. Completeness sweep — disposition of all 62 tables, 15 figures and 1 schema

Every numbered object in the source's own *Figuren* / *Tabellen* index (p.92-95), in exactly
one bucket.

**Captured** (11 tables + 1 text passage set): T5, rij Visserij / Totaal primaire sector /
Voedingsindustrie-variant (C-148, C-210, C-193) · T10 (C-211…C-214) · T13 (C-115…C-144) ·
T16 (C-145, C-146) · T17 (C-149…C-160) · T20 (C-161…C-184) · T25 (C-187, C-188) · T27 (C-186) ·
T29 (C-190…C-192) · T30 (C-194…C-201) · T36 (C-203…C-205) · T38 (C-208, C-209) · T40 (C-206,
C-207). Plus four running-text figures: p.34 (C-147), p.41 (C-185), p.48 (C-189), p.56 (C-202).

**Excluded, with reason:**

| Object | Reason |
|---|---|
| T1, T7 | identieke tabellen; alle in-scope cijfers gecapteerd uit de sectorhoofdstukken |
| T2, T8 | identieke inzamelwijze-cross-tabs; alle quantity_type-totalen staan elders en zijn daar gecapteerd |
| T3, T28, T35 | `schenking` — buiten scope per `quantity_type.csv` |
| T4 | synthese-tabel; elk in-scope 2020-cijfer is gecapteerd uit het sectorhoofdstuk; 2015-kolom hoort bij S004 |
| T6, T15, T19, T24, T31, T39, T47, T56, T62 | cascade-index en wegingscoëfficiënten — geen hoeveelheid materiaal |
| T9, T14, T18, T21, T23, T42 | percentages, geen tonnages (T23's Totaal-kolom in ton is wel gecapteerd als C-186) |
| T11 | kg/inwoner, en alle andere lidstaten buiten scope |
| T12 | 2020-kolom = N/A; 2015/2017 horen bij S004 resp. S003 |
| T22, T34, T43 | evolutie-overzichten; elk 2020-cijfer herhaalt een gecapteerd cijfer, 2015-kolom hoort bij S004 |
| T26 | bestemmingen niet-verkocht product; het Totaal (17.586 t) mengt reststroom en schenking |
| T32, T37 | bestemmingssplitsing van een reeds gecapteerd totaal |
| T33, T41 | aantallen bevraagde bedrijven en responsgraden — geen hoeveelheid materiaal |
| T44–T52, F11, F12 | horeca en catering — ketenschakel buiten scope |
| T53–T61, F13, F14 | huishoudens — ketenschakel buiten scope |
| F1 | volledige keten (bevat horeca/catering/huishoudens) + bestemmingsdata |
| F2 | idem, én referentiejaar 2015 (hoort bij S004) |
| F5 | Vlaco-stroomschema: verwerkingsstromen naar vergisting, mengt horeca-keukenafval en import |
| F6, F7, F8, F10 | cascade-infographics; elk cijfer erin herhaalt een gecapteerde waarde |
| F9 | Superlijst-scores — geen hoeveelheid materiaal |
| F15 | kg/inwoner, EU-lidstaten |

**Carries no numbers** (3): F3 (schema voedselgerelateerde stromen, p.16) · F4 (cascade van
waardebehoud, p.17) · Schema 1 (Vlaams en Europees kader, p.18).

#### 5. Judgement calls & new dictionary members

- **C-148, the printed 0 for visserij in Tabel 5**, was captured even though Tabel 4 and Tabel 12
  print "n/a" for the same quantity. The register records what the source prints, and a zero the
  source actually prints is a reading — but this one asserts something the source elsewhere says
  it does not know, so it is cross-referenced on the row and flagged here. Retire it via
  `DECISION_expert` if the reviewer reads the 0 as a formatting artefact for n/a.
- **C-147, "jaarlijks zo'n 17 miljoen kg vis"** (p.34, sourced to Vlaamse Visveiling 2022), is the
  one row in this extraction whose `reference_year` is not 2020. It is a generic annual-throughput
  statement, not a 2020 measurement, and it does not match either the 2020 aanvoer (12.795,6 ton)
  or the 2015 one (18.376,5 ton). Captured under "capture and flag rather than drop"; retire it if
  the reviewer prefers only year-resolved figures.
- **C-202, "meer dan 15 miljoen ton" productie voedingsindustrie** (p.56), is an order-of-magnitude
  estimate by Fevia that the source uses as the denominator for its 1,3% relative loss figure. The
  source's own wording is kept in `source_type_label`. Same treatment as S080's C-086
  ("ruim 700.000 ton").
- **Aanvoer vs opgehouden sit at different chain stages.** Per `chain_L2.csv` a landing volume is
  `Visserij` and a withdrawn-at-auction figure is `Visveilingen`, so Tabel 13's two halves were
  split across the two stages even though they share a table — the same call S080 made on its
  Tabel 10.
- **Tabel 13 rows carry `geography = Vlaanderen`** even though the table is titled "in Belgische
  havens", under the single sanctioned Belgium→Flanders exception in the protocol. The source's
  own wording is preserved in `source_type_label`.
- **The EU-definition rows (C-211…C-214) are a parallel accounting**, captured beside the Flemish
  figures per the S080 session decision. They are far smaller than their Flemish counterparts
  because the EU scope counts only material going to compostering/vergisting, dierlijke
  afvalverwerking and verbranding — feed, bodem, biochemie and biodiesel fall outside it. Two
  reconciliations hold exactly and are worth recording: voedingsindustrie 311.700 + 485.912 +
  9.045 = 806.657, and retail 51.947 + 13.835 = 65.782. Note also that the landbouw EU figure
  (28.746) is numerically identical to the landbouw "in restafval/lozing/andere bestemming"
  voedselverlies cell of Tabel 2/8 — a consequence of the definitions, not a transcription slip.
- **`type_assumed = TRUE`** was set on the per-species opgehouden rows (the 50/50 edible split is a
  sector-level assumption, not per species), the eight voedingsindustrie subsector rows (the source
  states outright on p.60 that it does not publish the split per subsector), the primary-sector
  aggregate, the four EU-definition rows, and C-148 and C-185.
- **No new dictionary members were needed.** Every commodity grouping, chain stage and quantity
  type in this source was already in the three dictionaries after S080 — including the eight
  voedingsindustrie subsector groupings and the two retail segments, which this edition names
  identically. `Zuivel` again takes `Dierlijk - vee / Melk` per the S080 rule.
- **No Zotero item exists and `Sources.S002.citation_key` is blank** — flag **F-002** is still
  open. (A Zotero MCP did appear in this session's tool list, but the user asked to leave the
  connection issue aside; the flag stays open and the backfill is a separate job.) The PDF is
  archived at `register/archive/S002_OVAM Monitor voedselverlies 2020.pdf`.

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
