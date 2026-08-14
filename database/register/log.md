# BIOLOOP register — extraction log

*One entry per source-extraction session, newest first. The running record of what was
extracted, what looked wrong, and whether it has been verified against the archived PDF.
This is local working memory for the register workstream; project-level status still goes to
`database/hub.md` at session end.*

## How to use
- After each source session, add one row to the **Sessions** table.
- If the anomalies for a source need more than a line (a suspected source error, a unit
  oddity, a stream that forced a new dictionary entry), write it out under **Anomaly notes**
  keyed by `source_id`, and just point to it from the table.
- `Verified?` flips to `yes` only after a human has checked `Streams` against the PDF in
  `archive/`.

## Sessions

| Date | source_id | source_short | PDF (in archive/) | Claims added | Verified? | Commit | Anomalies / flags |
|------|-----------|--------------|-------------------|-------------:|-----------|--------|-------------------|
| 2026-08-14 | S080 | OVAM Monitor 2023 | `S080_OVAM Monitor voedselverlies 2023.pdf` | 310 (C-001…C-310) | no | *(this session)* | 6 internal contradictions incl. a suspected typo; Zotero item still missing — see [S080](#s080) |

## Anomaly notes (detail, keyed by source_id)

### S080 — OVAM Monitor voedselverlies 2023

98-page PDF, read cover-to-cover from the text layer; Figuren 3, 4, 6 and 13 were additionally
rendered to image and read directly (only **Figuur 6** carries tonnages that the text layer
does not). 310 claims: 131 `agri-food waste`, 64 `voedselverlies`, 61 `nevenstroom`,
54 `hoofdstroom`. Reference years 2015 (92), 2017 (3), 2020 (88), 2023 (127).

**Zotero — NOT DONE.** No Zotero MCP is wired in this repo (`.mcp.json` holds only the
Supabase server), so step 2 of the protocol could not run. The PDF *was* moved to
`archive/`, so the frozen artifact exists, but `Sources.S080.citation_key` is still blank and
no Zotero item was created. Raised as **F-002** in `flags.md`.

#### Contradictions inside the source (all preserved, none reconciled)

1. **`nevenstromen` landbouw 2023 — suspected typo.** Tabel 14 gives the landbouw total as
   **21.060 t**; Tabel 16 and the running text on p.32 both give **215.060 t**, and 215.060 is
   what the subsector rows sum to. Both figures are recorded (C-227 = 21.060 from Tabel 14,
   C-230 = 215.060 from Tabel 16). Almost certainly a dropped digit in Tabel 14 — but *not*
   corrected here.
2. **Totale voedselreststroom landbouw 2023, excl. niet-geoogste aardappelen:**
   Tabel 12 says **623.935 t**, Tabel 16 says **623.934 t**. Both recorded.
3. **Totale voedselreststroom voedingsindustrie 2015:** Tabel 5 says **2.442.771 t**,
   Tabel 26 says **2.442.711 t** (digit transposition). Both recorded.
4. **Totale voedselverliezen retail 2023:** Tabel 30 and Tabel 32 say **59.849 t**,
   Tabel 34 says **58.849 t**. Both recorded.
5. **Voedselverliezen catering 2023 — three different values:** **7.467 t** (Tabel 39),
   **7.475 t** (Tabel 40), **7.476 t** (Tabel 43 and the text on p.67). All three recorded.
   Nevenstromen catering likewise **7.696 t** (Tabel 39/43) vs **7.688 t** (Tabel 40).
6. **Visveilingen 2015/2023, Vlaanderen vs België.** Tabel 10 (titled *Belgische havens*)
   totals 101,8 t opgehouden in 2015 and 203 t in 2023; Tabel 11 (titled *Vlaanderen*) gives
   102 t and 203 t. Tabel 10 rows are recorded with `geography = Belgie`, Tabel 11 rows with
   `geography = Vlaanderen` — never silently merged. Tabel 7 rounds the 2023 split to
   102/102 where Tabel 11 gives 101,5/101,5.
   Also note **huishoudens 2023 = 356.172 t** (Tabel 2/44/47/48/49) vs **356.175 t**
   (Tabel 54) — not captured here, households being out of scope (below).

#### Deliberate exclusions (nothing dropped silently)

- **Huishoudens — excluded by decision (user, this session).** `chain_L2.csv` has no household
  stage; the chain ends at retail / horeca & catering. Skipped: the household totals
  (356.172 t voedselreststroom, 200.766 t voedselverlies, 155.406 t nevenstromen, plus the
  2015/2020 series in Tabel 49) and the per-commodity restafval tonnages in Tabel 46
  (groenten/fruit 43.412, brood 41.756, bereide gerechten 40.716, desserts 17.496, zuivel
  16.586, vlees/vis 15.573, onvermijdbaar composteerbaar 117.819, niet-composteerbaar 18.041,
  tuinafval 19.901 t/jaar). **These are real, well-resolved Flemish tonnages** — if the
  register ever admits the consumer stage, this table is the first thing to come back for.
- **Whole-chain grand totals — excluded by the depth rule** (`commodity_hierarchy.md`: "No 1").
  Skipped: 3.210.384 t (Tabel 5) / 3.210.385 t (Figuur 4 — note the 1 t discrepancy),
  1.194.295 t voedselverlies and 2.016.092 t nevenstromen (Figuur 4, 2023); 2.987.959 /
  882.843 / 2.105.116 t (Figuur 3, 2020). **Reconsider:** these are exactly the totals a
  bottom-up sum check would want. Flipping the depth rule to admit level-1 rows is a
  dictionary decision, not an extraction one.
- **Destination and collection-route splits — not stream volumes.** Every "waarheen ging het"
  cell was skipped: bestemmingen (Tabel 5, 13, 17, 23, 25, 29, 30, 37, 47) and the
  selectief-ingezameld / in-restafval split (Tabel 7, 8, 22, 28, 32, 35, 36, 40, 42, 43, 44,
  48). Only the arising totals were taken. One casualty worth noting: Tabel 8 gives
  voedingsindustrie nevenstromen selectief as **1.543.934 t** where Tabel 22 gives
  **1.543.962 t** — a seventh contradiction, in cells that were not captured either way.
- **Schenkingen — out of scope** per `quantity_type.csv`. Skipped: Tabel 4 (9.511 / 11.226 t),
  Tabel 21, Tabel 27, the 535 t donated by PO's, and the Tabel 20 "Totaal" column
  (15.949 / 17.586 / 15.724 t), which mixes schenking into the residual total.
- **Non-Flemish geography.** Walloon, Brussels, Belgian and EU-member-state figures
  (Tabel 3, 51–56) were skipped: the register's `geography` vocabulary admits `Belgie` only
  where no Flemish figure exists, and here Flemish figures do exist. The only `Belgie` rows in
  this extraction are Tabel 10's fish landings, which the source itself frames as Belgian.
- **Not quantities of material:** cascade-index scores, kg/inw figures, percentage shares,
  sorteeranalyse weight-% (Tabel 33, 41, 45, Figuur 13), the ±5.000 ha unharvested area, and
  year-on-year deltas ("+20.760 ton t.o.v. 2015").
- **Rounded restatements in the running text** ("afgerond 341.000 ton", "932.000 ton",
  "624.000 ton", "circa 29.500 ton") were not given their own rows; the precise table value
  was recorded instead.

#### Judgement calls a reviewer should check

- **Komkommers (226.200) and Kropsla (50.931) in Figuur 6 are reported in *1.000 stuks*,
  not tonnes** — no mass conversion exists in the source, so they were **not** captured
  rather than converted with an invented piece-weight. The other 8 crops in that figure are
  in tonnes and were captured as `hoofdstroom`.
- **"ruim 700.000 ton" aanvoer (PO's, 2023)** was recorded as 700000 with the source's own
  wording kept in `source_type_label`; it is a lower bound, not an exact figure.
- **Fevia's 15,8 miljoen ton** production estimate for the food industry is explicitly an
  order of magnitude ("qua grootteorde"); recorded as `hoofdstroom` with that caveat in the
  label.
- **The 308.000 t unharvested potatoes** are recorded as one `voedselverlies` claim, *and*
  appear inside the "incl." variants of the aardappelen / akkerbouw / landbouw totals. Note
  the source contradicts itself on scope: p.16 says these pre-harvest losses "vallen buiten de
  scope van de gerapporteerde cijfers", yet Tabel 12/14/16 carry incl.-variants that contain
  them. Both variants are recorded, each labelled.
- **`type_assumed = TRUE`** was set where the source gives a residual total but no
  edible/inedible split for that particular stream: the per-species opgehouden fish, the eight
  voedingsindustrie subsectors (the source states on p.52 it deliberately does not publish the
  split per subsector), and the retail / horeca / catering subsector rows.
- **50.000 t of slaughterhouse material** (huiden, botten) was removed from the 2020 figures
  because "het niet om voedsel gaat" (p.52). Not captured — it falls outside this source's
  scope — but it is a real Flemish stream and a candidate for another source.

#### Dictionary members added this session

- `chain_L2.csv`: **`meerdere stadia`** made an explicit row (the file's own note already
  prescribed the value). Used for the primaire-sector totals and "Landbouw en PO's".
- `commodity_hierarchy.md`: L3 `Vis` with the 14 species at L4; L3 `Vlees` and `Eieren` under
  `Dierlijk – vee`; L4 `Champignon` under `Groenten beschut`; plus a written rule for when to
  use `Gemengd` vs `Aggregaat` at L2.
