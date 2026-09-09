# The volume source hunt — round 1, the twelve derived gaps

*Result of the 2026-09-09 session (F-003). One entry per gap: what would supply the tonnage, how
far that was actually checked, and which of it is a measurement rather than a calculation of ours.*
*This file is a **worklist**, not data. Nothing below has been extracted and no claim was added.*
*Companion: `crosswalks/VOLUME_SOURCE_CANDIDATES.csv` — 29 candidates over 12 gaps, `DECISION` blank.*

The targets are the derived gap list of 2026-09-09 (`deliverables/`): **10 places + 2 screened
findings, 2.928.726 t/yr**. Gap rows renumber on every run, so every candidate is anchored on
**place × chain stage** plus the claim ids in the last column of the gap sheet — never on the row
number.

## How to read the two classifying columns

`checked` follows the register's own discipline, and the composition hunt's vocabulary:
**inspected** (the table or file was fetched and read) · **listed** (the source's own index confirms
the figure exists, not opened) · **named** (plausible, nothing verified) · **absent** (searched for
and not there).

`source_class` is new here, and it exists because of a decision taken at the start of this session:
**a source that publishes a production volume or a loss fraction is in scope, but it is never a
claim.** Six classes:

| class | what the source publishes | what it still needs |
|---|---|---|
| `direct` | a residual tonnage | nothing — it is a claim |
| `denominator` | a throughput or production volume | a fraction |
| `conversion` | a fraction, yield or split | a volume |
| `allocation` | a regional or temporal share | a figure to reallocate |
| `datarequest` | nothing — the figure exists unpublished | a request |
| `restatement` | a figure another corpus source owns | nothing; it is not a measurement |

Only `direct` can become a `supply_observation`. The other five feed a **derivation**, and a
derivation is the model layer's business, not BioMobi's — so they are recorded, cited and kept
visible, and they are never summed into the corpus. This is the same line the register already drew
for S015, S018, S019 and AgroCycle; the classes just make it explicit and extend it to the leads
that motivated this session (Fevia's loss percentages, STATBEL's regional split, seasonality as a
proxy).

---

## The one finding that matters most

**The largest gap is not missing. It is unpublished — and the request that would close it is one
cross-tabulation.**

OVAM publishes *Bedrijfsafval en secundaire grondstoffen* for Flanders, production years 2012–2022,
as a report plus a 126 kB Excel. The Excel was downloaded and read end to end. It has eight sheets,
and two of them are the mapping tables that give the game away:

- `Indeling sectoren` — **944 rows, NACE 4-digit → one of 52 OVAM sectors**
- `Indeling stromen` — **993 rows, EURAL 6-digit → one of 56 OVAM streams**

So the underlying data is **NACE-4 × EURAL-6, for Flanders, per production year**. That is exactly
the grain five of the ten gap rows ask for in their own words (*"een bron die deze schakel per
productgroep rapporteert in plaats van als sectortotaal"*), because inside the single OVAM sector
`e-p-voeding` sit **NACE 10.2 → 12** as separate classes:

| gap row | the NACE classes inside `e-p-voeding` | the EURAL branch |
|---|---|---|
| Varia › Dranken (378.539 t) | 11010–11060 | **02 07** — drink production |
| Varia › Bakkerij (122.276 t) | 10711, 10712, 10720 | **02 06** — bakery & confectionery |
| Varia › Oliën, vetten (95.895 t) | 10410, 10420 | 02 03 03, 04 02 10 |
| [S1] aardappel-/groente-/fruitverwerking (621.063 t) | 10310–10393 | **02 03** — fruit, veg, grain |
| Retail & grootdistributie (132.082 t) | 47113–47192, 472xx | 20 01 08, 02 03 04 |

**The EURAL tree carves by process, not by product code.** `02 07 02` is *afval van de destillatie
van alcoholische dranken*; `02 07 01` is *afval van wassen, schoonmaken en mechanische bewerking van
de grondstoffen*. That is precisely what F-003's screening rule demands and what every Prodcom- and
NACE-keyed candidate so far has failed to give.

**What the publication does not contain: the cross-tab.** `Afval per sector` and `Afval per stroom`
are two independent **marginals** — a sector's total across all 56 streams, and a stream's total
across all 52 sectors. There is no cell for `e-p-voeding × plant&dier`. So the published file is
useful as an upper bound and useless as a measurement, and the gap-closing move is a **data request
to OVAM/MATIS for one cross-tabulation** — not a new publication, and not a commission.

MATIS is already in the `Sources` sheet as **S026, HOLD – GATED**. This hunt's contribution is
knowing *exactly what to ask for*, which the earlier verdict did not.

**Two cautions that must travel with it.**

1. **This is a third school.** `voedselverlies` counts food-linked losses; `productieresidu` counts
   everything that arises; **`bedrijfsafval` counts what was declared under an EURAL code.** A
   sector total also contains packaging, sludge and waste water, so it is not a claim about a
   biomass stream at any grain. Merging it with either existing school is the mistake the gap tool's
   school rule exists to prevent.
2. **The series breaks at 2022.** From production year 2022 OVAM uses MATIS instead of the IMJV
   sample, and `e-p-vlees` falls from **817.448 t (2020) to 169.900 t (2022)** — a 4,8× drop that is
   a method change, not a trend. Any request must ask which years are comparable.

### A latent mis-filing this exposes

`tools/make_gap_list.js` assigns schools by source name: `e.startsWith("OVAM") → voedselverlies-school`.
That is right for the two voedselverlies monitors and **wrong for the Marktanalyse Biomassareststromen**
(S001/S086/S087), which is built on the same IMJV/waste-declaration lineage as `bedrijfsafval`. It
costs nothing today, because S087 produced zero claims. It becomes a real defect the moment a
Marktanalyse or a bedrijfsafval figure enters the corpus. **Fix the `FAMILY` map before, not after.**

---

## Two things the hunt found already in hand

Worth stating before anything is commissioned or requested.

**1. `archive/S087_Marktanalyse Biomassareststromen 2024 OVAM.pdf` prints the meat gap's number, and
the register deliberately dropped it.** Chasing the vlees gap led to a B2BE Facilitator dossier
reporting **698.000 t dierlijk bijproduct, Vlaanderen, 2023**, 78% category 3. That is S087 p.55
verbatim, and the dossier cites OVAM and MONBIO 3.0 for it — a **restatement**, which under the
register's own rule re-owns nothing. `log.md` already records why the figure was dropped: Figuur 24
splits its *herkomst* across Vlaanderen / Wallonië / Brussel / Buitenland in an **unlabelled 3-D pie
with no printed numbers**, so neither `Vlaanderen` nor `Belgie` would be an honest `geography`.

So the vlees gap does not need a source. **It needs one number: the Flemish share of that 698.000 t.**
`log.md` names the reversal as a one-edit recovery and this hunt confirms no third party publishes a
better figure. Routes for the share: Rendac/Darling Ingredients BE, FEBEV, or OVAM's own dierlijke-
bijproducten page.

**2. The two horticulture gaps can be narrowed with a source the corpus already owns.** ILVO 239 is
extracted (111 claims) and carries loss fractions per horticultural crop; Landbouwcijfers Vlaanderen
carries area and production per crop. Applied together they cover the unnamed branches under
*Groenten* and *Groenten openlucht* at zero retrieval cost. It is a `conversion`, it re-computes a
source the corpus already holds, and it must therefore **never** enter as a new claim — but it sizes
the gap before anyone pays to close it.

---

## Per-gap result

Tonnages are the gap, not the asserted total. Full detail, URLs and caveats in the CSV.

| gap | t/yr | best candidate found | class | checked |
|---|--:|---|---|---|
| Voedingsindustrie sectortotaal | 1.293.823 | **OVAM MATIS cross-tab NACE × EURAL** | datarequest | inspected |
| Varia › Dranken | 378.539 | same cross-tab (NACE 1101–1107 × EURAL 02 07) · Belgische Brouwers (21 Mhl BE 2024) | datarequest · denominator | inspected · listed |
| Primaire productie sectortotaal | 256.888 | Landbouwcijfers Vlaanderen × AgroCycle · Statbel Kerncijfers landbouw per gewest | denominator · conversion · allocation | named · listed |
| Dierlijk-vee › Vlees | 149.734 | **the Flemish share of S087's 698.000 t** · Statbel BeStat slachtingen per diersoort | datarequest · denominator | inspected · listed |
| Tuinbouw › Groenten | 142.220 | VBT jaarverslag · ILVO 239 × Landbouwcijfers | direct · conversion | listed · named |
| Retail & grootdistributie | 132.082 | same cross-tab (NACE 47 × EURAL 20 01 08) · Comeos S067 | datarequest · direct | inspected · named |
| Varia › Bakkerij | 122.276 | same cross-tab (NACE 1071–1072 × EURAL 02 06) · Bread2B (HOGent/UGent) | datarequest · direct | inspected · named |
| Varia › Oliën, vetten | 95.895 | same cross-tab (NACE 1041–1042) · Valorfrit | datarequest · direct | inspected · named |
| Groenten openlucht | 85.709 | as Tuinbouw › Groenten | — | — |
| Akkerbouw › Oliehoudende gewassen | 68.000 | FEDIOL annual statistics + its published 60/40 and 80/20 meal-oil split | denominator · conversion | listed · inspected |
| **[S1]** aardappel-/groente-/fruitverwerking | 621.063 | **Belgapom** (6,2 Mt processed BE 2022) × FOWCUS fractions · VEGEBE (gated) · S058 TransBio | denominator · conversion · direct | inspected · named |
| **[S2]** Akkerbouw › Voedergewassen | 101.780 | Landbouwcijfers × residue coefficient | conversion | named |
| *G-02 fact-check* — PO's/veilingen | *15.189* | OVAM `e-p-grooth` 657.273 t (upper bound) · **VBT decides it** | direct | inspected |

**Eleven of the 29 candidates were opened and read; twelve are named only. Every one of the twelve
gaps now has at least one concrete candidate — but only three of them have a `direct` candidate that
is both public and unverified-but-locatable (VBT, Comeos, Bread2B).** The rest run through a data
request or a derivation. That asymmetry is the honest headline of this round.

## What came back empty, and what that means

- **FGBB (Federatie van Grote Bakkerijen van België)** — `absent`. The site carries no statistics,
  no annual report with tonnages, no return figure. Bakkerij has no published sector source.
- **VEGEBE** — no public tonnage, only a member profile. Confirms S020's `HOLD – GATED`. And
  **fruit processing still has zero rows in the entire register**; VEGEBE would not fix that even
  if it opened up.
- **Fevia** — the only quantity findable is **>4.500.000 t of Belgian food-industry by-products
  going to animal feed**. It is destination-side, Belgian, undated and unsplit, so it closes nothing
  — but it is a useful order-of-magnitude sanity check against OVAM's 2.017.748 t assertion, and it
  suggests the food-industry gap is under- rather than over-stated. S011 stays `HOLD – CANNOT VERIFY`.
- **S058 ILVO TransBio** — searched, no public location found. Unchanged since F-003 named it, and
  still the single candidate that would hit potato processing, dranken and the Flemish crush share
  at once.
- **The leads that need a person, not a search** — Belorta (NDA, currently with Nathan), REO,
  REJUICE, BCZ-CBL, Fenavian. BCZ publishes processed-milk volumes (4,9 bn l BE 2023) which is a
  clean `denominator` for the whey question F-003 raises, but no residual tonnage. None of these was
  entered as a candidate row, because a gated lead is a decision for you rather than a search result.

## Next actions, in order

1. **Draft the OVAM/MATIS data request.** One cross-tabulation, `NACE 4-digit × EURAL 6-digit`,
   Flanders, per production year, restricted to EURAL chapter 02 + 20 01 08 + 04 02 10. Ask which
   years are method-comparable across the 2022 MATIS break. It addresses five gap rows and the
   largest screened finding.
2. **Decide the S087 reversal.** Either obtain the Flemish share of the 698.000 t, or un-retire S001
   (whose verdict note already has the sector at ~860 kt for 2021 — but `_RETIRED` sources may not
   be proposed, so only you can lift it). Cheapest item on this list by far.
3. **Fix the `FAMILY` school map** in `tools/make_gap_list.js` before any Marktanalyse or
   bedrijfsafval figure is captured.
4. **Fact-check G-02 against a VBT jaarverslag.** F-003 already ranks this before commissioning
   anything for the auction stage, and `e-p-grooth`'s 657.273 t makes 15.189 t look implausible.
5. **Then the three locatable `direct` sources:** VBT, Comeos (S067), and the Bread2B volume report
   — the last is a retrieval problem, like F-005: the juridical deliverable was downloaded and its
   text layer would not come out; the volume deliverable has not been located at all.
