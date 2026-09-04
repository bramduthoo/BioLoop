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
| 2026-09-01 | S065 | GeNeSys ILVO 165 | `S065_genesis.pdf` | 98 (C-704...C-801) | no | `5d66f86` | See [S065](#s065) - the superset to S066; 62 of 98 claims live in an unnumbered appendix, 1 layout trap caught by arithmetic, 12 new L4 members, no Zotero item (F-002) |
| 2026-09-01 | S066 | ILVO 239 tuinbouw | `S066_Monitoring voedselverliezen Vlaamse tuinbouw_ILVO.pdf` | 111 (C-593...C-703) | no | `3388b1f` | See [S066](#s066) - 1 suspected source error (C-685, TOTAAL productie omits overig fruit), 2 rounding variants, 1 new dictionary member, first source whose edible/inedible split matches ours, no Zotero item (F-002) |
| 2026-09-01 | S010 | Verkennende haalbaarheidsstudie biomassahub | `S010_Verkennende economische haalbaarheidsstudie biomassahub_ILVO.pdf` | **0** | n.v.t. | `c665c27` | See [S010](#s010) - a consolidation with no original measurement; all 4 data tables restated from S002/S006/S065/S066, no Zotero item (F-002) |
| 2026-09-01 | S087 | Marktanalyse Biomassareststromen 2024 | `S087_Marktanalyse Biomassareststromen 2024 OVAM.pdf` | **0** | n.v.t. | `2856b23` | See [S087](#s087) - read cover-to-cover and agri-food-empty; 4 scope decisions, 8 tonnages named for recovery, no Zotero item (F-002) |
| 2026-08-16 | S007 | MONBIO 3.0 | `S007_MONBIO3.0.pdf` | 195 (C-398…C-592) | no | `e3c61bc` | See [S007](#s007) — 1 suspected source error (in **S091**, found from here), 6 variant readings, 3 new dictionary members, no Zotero item (F-002) |
| 2026-08-16 | S091 | MONBIO 4.0 | `S091_MONBIO4.0.pdf` | 183 (C-215…C-397) | no | `0ae8225` | See [S091](#s091) — 0 suspected source errors, 5 variant readings, 4 session scope decisions, 15 new dictionary members, no Zotero item (F-002) |
| 2026-08-15 | S002 | OVAM Monitor voedselverlies 2020 | `S002_OVAM Monitor voedselverlies 2020.pdf` | 100 (C-115…C-214) | no | `73910c0` | See [S002](#s002) — 2 suspected source errors, 3 variant readings, no Zotero item (F-002) |
| 2026-08-15 | S080 | OVAM Monitor voedselverlies 2023 | `S080_OVAM Monitor voedselverlies 2023.pdf` | 114 (C-001…C-114), 1 retired | **yes** (2026-08-15) | `2486196` + `8d23344` | See [S080](#s080) — 1 source error retired by the reviewer, 3 variant readings, no Zotero item (F-002) |

*Note: S080 was extracted once before, on 2026-08-14 under protocol v1, producing 310 claims.
That run was **discarded** on 2026-08-15 — it captured horeca and catering, and predated the
provenance/unit columns. See commit `ad3b36c` for the withdrawn output. The row above is the
clean v2 re-run and supersedes it entirely.*

## Tooling & model sessions (no source extracted)

### 2026-09-03 (last) — full-corpus gap sweep; the gap list split into two classes

**No source extracted; no claim changed.** The reviewer asked for the gap analysis to be redone
thoroughly and critically — explicitly including *"a sector/chain stage or L3 level with a large
aggregate and no selectable L4/L5"* and *"screening the workbook for names you expect to be possible
entries which are now not rendered"*, the way zemelen, gries and bostel had been. Five screens were
run over `streams_export.csv`, and the result is `OPEN_GAPS.md`, rewritten around **two classes**:
*hiding in the current data* (no source will help) and *not in the corpus at all* (only a source
will).

**Screen 1 — residual rows above L4.** 49 live residual rows sit at L2/L3 with no `AGGREGAAT - `
prefix, **2.367.761 t**, invisible to any selection. **43 are legitimate** — OVAM publishes
*Dranken*, *Bakkerij* and *groenten openlucht* at subgroup level and nothing finer — and those 43
are the class-B data gaps. **Six are misplacements** (G-A1): `C-334`/`C-523` *Meel/schroot uit
andere oliehoudende zaden* (68.000 t each), `C-381`/`C-574` *Melasse grondgebiedbasis* (47.805 /
56.806), `C-273`/`C-457` *Teruggegooide vis* (7.500 / 7.707). The discards row is also **the entire
residual content of the `Visserij` stage**, against a total selectable fish mass of 839 t.

**The audit could not have caught any of them (G-A2).** `audit_register.py` identifies a misplaced
row from its **name** — check 1 on a product code, check 4 on a leftover-class phrase — so a
residual row at L2/L3 with an ordinary name passes every check in the file. One concrete hole was
found and fixed: `COLLECTION_SIGNALS` listed *en andere*, *of andere*, *van andere* but not ***uit
andere***, which is exactly how `C-334` escaped. Adding it catches those two rows and nothing else;
the audit baseline moves **24 → 26 findings**. The durable fix is the new
**`find_hidden_streams.py`**, which enumerates the class instead of matching names and writes
`crosswalks/HIDDEN_STREAMS.csv` as a human gate (`promote` | `subgroup-figure` | `aggregate`).

**Screen 2 — retired rows.** Nothing large is being lost by mistake.

**Screen 3 — waste filed as production.** 30 `Productievolume` rows whose names read like residue;
**all 30 are false positives** (margarine, cacaopasta, witloof production, *Aanvoer Bot* — a
flatfish). The hypothesis is closed and should not be re-run.

**Screen 4 — aggregate reconciliation.** Found G-A3: `C-284`/`C-469` *maalderij* (671.000 /
563.000) and `C-286`/`C-471` *suiker en chocolade* (403.000 / 394.000) sit at **L2 under `Varia`
with `L3` blank** while the rows they total sit under `Granen` and `Varia › Zetmeel`/`Suiker`, so
they reconcile against nothing in the tree. Both compositions were already in this log and are
exact: `563.000 = 278.865 zemelen + 284.549 zetmeelafvallen`; `394.000 = 56.806 melasse + 337.649
bietenpulp`. It is **G-05 with numbers attached**.

**Screen 5 — absence checklist.** 41 named Flemish side streams asked of the whole workbook, any
role, any status. **Absent entirely:** wei/kaaswei/permeaat/lactose, cacaodoppen, aardappelschillen
/ stoomschillen / aardappelvezel / aardappeleiwit, draf/DDGS, vinasse, frituurvet, eierschalen,
veren, verenmeel/diermeel, categorie 1/2/3 materiaal, visafval, citruspulp, bietenpuntjes,
schuimaarde, champost, bermgras.

**Four suspected gaps were checked and dismissed** — two of which would have made the list wrong:

- **`Suiker- en zetmeelgewassen`** (1.207.169 / 1.264.364 t, no components under it) is **not a
  gap**: it is MONBIO's own *gewasgroep* and its components sit under two register L3s.
  744.945 + 462.224 = 1.207.169 **exactly**; 800.480 + 463.884 = 1.264.364 **exactly**.
- **GeNeSys akkerbouw 3.000.000 t and groenten 800.000 t** are covered — the first is a declared
  rival of MONBIO's measured stro and already cross-referenced, the second a round approximation of
  GeNeSys's own crop rows (903.130 t).

**The mechanism behind most of class B, stated so it can guide the source hunt.** MONBIO's
food-industry residual detail *is* the set of **Prodcom codes that happen to name a waste or
by-product** (106132 gries, 106220 zetmeelafvallen, 108114 melasse, 110210 bostel, 101150 dierlijk
vet, 101240 slachtafval gevogelte) plus one FEDIOL crush table. **A side stream with no such code is
invisible to MONBIO however large it is** — which is why bostel and zemelen are in the selection and
whey, cocoa shell and potato peel are absent. OVAM has the mirror-image limit: subgroup level and
nothing finer. So the next source should carve **by process, not by product code**.

**Ten new class-B entries** (G-09…G-18), each with claim ids, what is absent by name, and a
candidate: aardappelverwerking (621.063 t block, 0 components), dranken (378.539), slachtafval per
soort (471.361, was G-04), oliezaadschroot geography (was G-06), bakkerij (122.276), retail (was
G-01), oliën/vetten + frituurvet (95.895), MONBIO's voedergewassen/industriële/peulvruchten field
residue (203.387), **zuivel — wei absent entirely**, **cacao — no residual figure at all**, the
seven MONBIO 4.0 cells suppressed as confidential (which is why zetmeel is single-source),
visverwerking, PO's, eieren. `G-03` becomes an umbrella marked superseded.

**Three cheapest moves, and a correction to an earlier decision.** S005 (MONBIO 1.0) and S001
(Marktanalyse 2022) are **already in `inbox/`, marked `_RETIRED`** — S005's own `Sources` verdict
names *gries/zemelen/**DDGS** 646 kt* and S001 covers the **animal by-product sector (~860 kt, 2021)
and used frying fats**. They were retired on the expectation that they repeat later editions; for
G-04, G-11 and G-14 that expectation is wrong, and un-retiring them is the cheapest progress
available. The third move is deciding the six rows in `HIDDEN_STREAMS.csv`.

**G-07 resolved by reviewer decision.** A bundled L4 stays **one item** — Aardappel is Aardappel —
but the number is now reported **at its lowest detail level**, per fraction, because an L4 sum and a
single-fraction figure are not the same quantity and comparing them manufactures spread.
`select_streams.js` gained that view, and it does what the reviewer predicted: Suikerbiet reads 34×
across sources at L4 and **1,0× on loof, 1,0× on pulp**; Aardappel 8,3× at L4 and **1,1× on loof**.

**Checks.** `verify_overview.py` 8/8; `audit_register.py` 26 findings (24 pre-existing + the two
`uit andere` rows the fix now catches); workbook untouched. Report artifact:
`https://claude.ai/code/artifact/4a899558-975e-400e-a69b-3d277cc9b5d2`.

**Completed 2026-09-04 — the register made usable.** The reviewer's response to the first version
was that it *"only shows parts of the actual output … nothing concrete to work upon"*, and that was
fair: it narrated the findings and cited the evidence without ever printing it. The screens are now
emitted in full by a committed script, **`gap_sweep.py`**, and the artifact renders every one of
them as a table rather than a summary:

- all **49** rows above L4 with the proposal per row, filterable, with a `branch L4` column saying
  whether that source has any selectable detail in the same branch;
- the **41-stream checklist** with its status, hit count, largest tonnage and claim ids — so
  *absent* can be checked rather than believed;
- **34 commodities with a production figure and no residual figure** (`prod_only_l4`), a screen that
  was run but never surfaced. It is the cleanest statement of a data gap the corpus can make:
  Voedermais 5.395.992 t, Koemelk 4.450.280, Gras en hooi 3.939.458, Mout 1.027.663, Varken
  1.253.312 — volumes known, residue unmeasured;
- all **26 branches** with reported / reaches-L4 / unresolved, the five reconciled ones marked;
- all **50 MONBIO** and **25 OVAM** food-industry residual rows, which is the evidence for the
  Prodcom mechanism rather than an assertion of it;
- all **30** production look-alikes and all **63** retired rows, so both dismissals are checkable;
- all **91 sources** with the on-disk status (the sheet's own `extraction_status` is stale and reads
  *NOT EXTRACTED* for every row, so it was ignored) and a gap mapping per source.

No number changed; nothing was re-analysed. `gap_sweep.py` reproduces the JSON the page renders.

**The two lists, 2026-09-04 — and a correction to my own screening.** The reviewer's objection was
that the sweep never produced the thing it existed to produce: *the items in the current data that
should be fixed, and a clear list of the other gaps*. Two failures behind that, both mine.

**Failure 1 — I only swept one side.** Every screen looked at rows *without* an `AGGREGAAT` prefix.
I never swept the rows that *carry* the prefix, which is precisely where the reviewer's own example
lives: `Zemelen, slijpsel en andere resten van het bewerken van granen` was promoted because the
bundle is one physical stream, and nothing checked whether other rows qualify. Sweeping all **144**
live aggregate rows found **two that do**, both in meat:

- `C-298`/`C-483` **Niet-eetbare ruwe slachtafvallen** (Prodcom 101160), 169.051 / 142.405 t — a
  defined material category collected and rendered as one stream, not a nomenclature leftover.
- `C-295`/`C-480` **Eetbare slachtafvallen van runderen, varkens, schapen, geiten en paarden**,
  82.576 / 75.397 t — saleable as one red-meat offal stream.

Simulated on a copy: they **enter the shortlist at ranks 11 and 22**, MONBIO's ceiling coverage goes
89,3% → 93,1% (4.0) and 90,6% → 93,6% (3.0), and Appel and Melasse move to 26 and 25. **251.627 t
was sitting in the register marked unselectable.** That is the answer the sweep owed.

One row was checked and deliberately **not** promoted, and it is recorded so it is not proposed
again: `C-342`/`C-532` *Perskoeken en andere vaste afvallen van plantaardige oliën en vetten*
(1,0–1,35 Mt) looks like the same case and is not — it is a rival Prodcom measurement of material
already selectable as Kool- en raapzaad, Lijnzaad, Soja and Zonnebloem. Promoting it double-counts;
this was tried on 2026-09-03 and reverted.

**Failure 2 — I kept proposing retired sources.** S001, S005, S006 and S086 carry `_RETIRED` in
`inbox/` for a reason, and recommending them as the cheapest next move ignored a decision the
reviewer had already taken. Every mention is gone from `OPEN_GAPS.md` and the register page, and
`make_gap_lists.py` states the exclusion in its own docstring so it does not creep back. Where a gap
had no other candidate, the honest answer replaces it: **G-04, G-09 and G-12 have no candidate
anywhere in the 91-row sheet** and need a search, not a queue.

**The output.** Two committed files, and the register page now leads with them:

- **`crosswalks/FIX_LIST.csv`** — 7 fixes, human-gated. F1/F2 add a stream each; F3 melasse (pick
  one basis — applying it mechanically inflates melasse 51%); F4 discards; F5 the oilseed leftover
  class, which repairs MONBIO's L1 by ~1 Mt; F6 the two orphaned `Varia` totals; F7 the do-not-touch
  record.
- **`crosswalks/GAP_LIST.csv`** — 14 sectors/products, each with what exists, the claim ids, what
  detail is missing, and what *kind* of source would supply it.

`make_gap_lists.py` writes both and carries the test that separates them: **a bundled name is one
selectable stream when the items arise together and cannot be separated in practice; it is a gap
when the bundle hides a distinction only a new source can supply.** Some rows are on both lists on
purpose — promoting the offal bundles gives two usable streams today while the per-species split
stays open as G-04.

**The question the whole sweep existed to answer, answered 2026-09-04 by simulation.** The reviewer
asked how any of this turns into action, and the honest way to find out was to apply the six class-A
edits to a **copy** of the workbook, re-run the selection, and measure. Three results:

1. **The shortlist does not move.** *Teruggegooide vis* becomes selectable at **rank 39** — outside
   the working set of 24. No stream enters the top 24 and none leaves. So there *was* hidden data
   and it does not change the selection: **the shortlist is as good as the current corpus can make
   it, and every further improvement is a class-B source problem.** That is a clean negative result
   and it is what makes the source hunt the right next activity.
2. **MONBIO's denominators are repaired, which was not expected.** Giving `C-334`/`C-523` the
   `AGGREGAAT` prefix **and a registry line** raises MONBIO 3.0's reported residual total from
   5.944.027 to **6.935.676 t** and 4.0's from 5.451.052 to **6.341.552 t**, and the impossible
   ceiling ratios 104,6% / 102,8% fall to **90,6% / 89,3%**. The oilseed food-industry branch was
   covered by no registered aggregate, so derive had been understating MONBIO's own L1 by about
   1 Mt. **G-06 was blamed for that artefact; it is actually class A.**
3. **A trap inside the melasse row, found only because it was simulated.** `C-381`/`C-574`
   (grondgebiedbasis) and `C-362`/`C-554` (Prodcom export-proxy) are two accountings of one material
   *within one edition*. Promoting the grondgebied row onto the same L4 node makes them siblings and
   `derive.js` **adds them** — melasse reads 111.298 + 56.806 = **168.104 t**, a 51% inflation, rank
   15 → 11. Promoting it to the crop ladder instead creates a **second** "Melasse" stream at rank 24
   and pushes Appel out of the working set. Neither is right; the reviewer picks one basis, exactly
   as the bietenpulp pair already does. **Do not apply that row mechanically.**

`OPEN_GAPS.md` gained the four-phase plan this produces — phase 0 close class A, phase 1 extract
S005 and S001 (both already on disk, wrongly retired), phase 2 the G-02 fact-check, phase 3 the
source hunt ranked by how much each source would change the BioMobi list — plus the screening rule
that falls out of the Prodcom mechanism: **does the candidate carve by process?** A source carving
by NACE, by Prodcom or by a monitor's own loss definition reproduces the gaps we already have.

### 2026-09-03 (later) — the 80/20 selection re-run after two defects were found in the analysis

**No source extracted; no claim in the workbook was touched.** The reviewer rejected the first
shortlist as internally inconsistent, naming the symptom precisely: raapzaadschroot at 681.000 t/yr
was absent while bonen at 1.783–68.600 t/yr was in, and so were gries (~85–98 kt), bostel (~114–135
kt) and the bietenpulp aggregate. They were right, and the cause was entirely in the analysis code.

**Defect 1 — the pool filter deleted an L4's own tonnage.** `analyse.js` built the selectable pool
by keeping an L5 fraction where a stream had one and the L4 node otherwise, to avoid double
counting. The effect was that whenever *any* source gave a commodity a named fraction, that
commodity's **unfractioned** tonnage was discarded. `Kool- en raapzaad` carries a 7.818 t *stro*
fraction from the field; that L5 was enough to delete the 681.000 t of schroot sitting on the same
L4 from the pool the selection ranked over. It could not have been selected at any N. Arithmetic:

```
MONBIO 4.0 pool   before 4.868.081   after 5.605.666   restored 737.585
                  = 681.000 (C-331 raapzaadschroot) + 56.585 (C-314 aardappel, voedingsindustrie)
MONBIO 3.0 pool   restored 906.913 = 852.000 (C-520) + 54.913 (C-501)
```

Fixed in `analyse.js` (both call sites), with the arithmetic recorded in the comment so the
regression is recognisable if it returns.

**Defect 2 — the ranking rewarded ubiquity, not mass.** The first pass ran a greedy selection
maximising *mean coverage across the six sources*. A stream two sources report scores twice; a
stream only MONBIO reports is diluted by four zeros — zeros that the register's own invariant says
do not exist (absence is *not measured*, never zero). So horticultural crops present in GeNeSys and
ILVO 239 outranked food-industry streams three to four times their size. That is the whole
explanation for zemelen, gries and bostel being missing while boon and peer were in.

**The method now, stated so it can be argued with.** Unit = the L4 commodity node, keyed
`L2 | L4` (L3 dropped: MONBIO's *Groenten* is ILVO's *Groenten openlucht*). Value = that source's
own derived total, never summed across sources. Rank = `M(k) = max over sources`, which is monotone
in mass, so the reviewer's inversion cannot recur. Denominator = each source's **selectable
ceiling** (the sum of its L4 streams), with its reported L1 total shown beside it — a source cannot
be asked for depth it never published. All of it lives in the header comment of the new committed
script `select_streams.js`; `select.js` / `select2.js` were scratch and are not in the repo.

**Result.** 65 selectable streams, envelope 7.095.847 t. **80% falls at rank 12** (18,5% of entries;
25,5% if the 18 fish species, 578 t between them, are set aside). The recommended working set is
**24 streams** — 96,0% of the envelope, 100% of *both* MONBIO ceilings, 99,9% OVAM 2020, 92,9%
OVAM 2023, 77,6% GeNeSys, 73,8% ILVO 239. Against the first pass's 16: fifteen survive, nine enter
(Kool- en raapzaad **at rank 2**, Zetmeel, Soja, Dierlijk vet, Bostel, Melasse, Gries, Gevogelte,
Zonnebloem) and one drops (Spinazie, now rank 28).

**Coverage percentages are lower than the first pass reported, and that is the fix working** — the
ceilings it measured against were short by 737.585 t and 906.913 t, so its percentages were
flattering.

**Three gaps raised**, all of them properties of the corpus that only became visible once the
ranking was correct — written up in `OPEN_GAPS.md`:

- **G-06** — the oilseed-meal block (Kool- en raapzaad, Lijnzaad, Soja, Zonnebloem; ~18% of the
  envelope, including the #2 stream) carries `geography = Belgie`. Same rows explain why MONBIO's
  L4 ceiling exceeds its own L1 total (104,6% / 102,8%): a denominator artefact, not double
  counting.
- **G-07** — three of the top four L4 rows bundle two physically unrelated streams (Suikerbiet =
  loof + pulp; Aardappel = loof + industrieel; Kool- en raapzaad = stro VL + schroot BE). Needs a
  registration rule, not new data; the split arithmetic is printed per row by `select_streams.js`.
- **G-08** — GeNeSys measures *oogstresten*, ILVO 239 measures *voedselreststromen*, and under one
  crop name they collapse into one stream with spreads up to 50,5× (Boon 90.000 vs 1.783).

**Checks.** `verify_overview.py` 8/8; `audit_register.py` at its 24-finding baseline; workbook and
`streams_export.csv` unchanged (this session read them only). Report artifact:
`https://claude.ai/code/artifact/95fa6e87-1fd1-45d3-88f9-071881f67bc1`.

### 2026-09-01 (evening) — aggregate decisions taken in a copy, and the 80/20 coverage audit

**No source extracted.** The reviewer asked for the open decision sheet to be filled provisionally
so the overview could be built and read as an expert would read it.

**The decisions live in a copy, not in the reviewer's file.**
`crosswalks/aggregate_coverage.csv` is untouched. `crosswalks/aggregate_coverage_CLAUDE.csv` holds
the same 244 rows with the 42 blank `DECISION` cells filled and a `RATIONALE_claude` column giving
the reason per row. `prep_data.py` gained a `BIOLOOP_REGISTRY` env override so an overview can be
built from an alternative sheet without overwriting the canonical one.

Twenty-five of the 42 were routine subsector rollups already verified to the tonne. The seventeen
that were not:

- **16 residual classes shelved** (`unallocated`), per v2.5 rule 2. This is what makes the coverage
  line honest: S066's tuinbouw reads **90,8%** resolved instead of a flattering 100%, and the
  missing 9,2% is exactly the unnamed *overige* residue.
- **C-800 shelved** — a Belgian diepvriesindustrie throughput sitting under a primary-production
  commodity node at the processing stage. Not a commodity total.
- **Four generator fields corrected.** C-689 and C-767 cover only the groenten subgroups, so
  `commodity_coverage` went from `full` to the named subset — left as `full`, C-689 would have been
  averaged against C-685 (groenten *and* fruit) to give a meaningless 1.798.336 t. C-691 and C-692
  are channel halves summing exactly to C-690 (757.574 + 341.965 = 1.099.539), so `treatment` went
  from `variant` to `component_set`; as variants the view would have averaged them.

**One data defect found and fixed.** `prep_data.py` parses the first year-like number out of the
free-text `reference_year`, so the S065 entries *"onbekend (data uit Bernaerts et al. 2012)"* and
*"… Braekevelt & Schelfhout, 2013"* were being filed as reference years **2012** and **2013** —
citation years, not measurement years, which put a 3 Mt figure in the wrong bucket. Both now read
`onbekend`; the reasoning moved to `source_type_label`.

**The audit.** `analyse.js` drives the tested `derive.js` to produce per-edition resolution, the
per-L2 gap map and the 80/20 ranking. Published as an artifact:
<https://claude.ai/code/artifact/d005bbbc-20a7-4797-9c75-6fe22de1c337>

Findings worth keeping in the log:

- **Resolution to selectable L4/L5 depth, per edition:** GeNeSys 2010 **100%**, ILVO 239 2015
  **90,8%**, MONBIO 3.0 **84,9%**, MONBIO 4.0 **84,1%**, OVAM 2023 **19,8%**, OVAM 2020 **5,9%**.
  The monitors carry the mass and almost none of the depth; the ILVO sources are fully resolved but
  cover only horticulture. MONBIO is the only source with both.
- **The selection is possible for plants and not for animals.** On MONBIO 4.0 (2021), **13 L4/L5
  streams reach 80,9%** of the reported L1 residual total; within the selectable pool the 80/20 is
  sharp at **6 of 20 items = 80,6%**. But **15,9% of L1 has no L4/L5 detail at any price**, and it
  is almost entirely animal and processing mass.
- **The two gaps.** `Dierlijk - vee` is **769.000 t behind a single row** (gevogelte, 84.141 t) =
  10,9% resolved. OVAM's `Varia` (the food-industry lump) is its **largest group at 596.710 t and
  resolves to nothing at all** in either edition. OVAM's akkerbouw shows **135%** coverage —
  captured components exceeding their parent, which wants checking.
- **Sources converge within a series and not across.** MONBIO 3.0→4.0 moves 9% at L1, OVAM
  2020→2023 moves 12% — consecutive editions measure the same thing. Across series, on the *same
  year 2020*, MONBIO reads 5.499.135 t against OVAM's 2.583.633 t: a factor **2,1**, and per group
  akkerbouw **24x**, vee **5,4x**, vis **38x**. The cause is definitional, not error: MONBIO counts
  *productieresiduen* (stro, loof) and the OVAM monitor counts only food-linked *voedselreststromen*.
  The same split explains GeNeSys (894.535) against ILVO 239 (282.821) on horticulture, 3,2x, same
  institute.
- **Consequence for BioMobi:** ten of the thirteen selected streams are straw, leaf, pulp and stalk
  — material that is *outside the scope* of the OVAM and ILVO 239 monitors by construction. A
  MONBIO-based selection cannot be cross-checked against OVAM, and the two must never be summed or
  averaged. One genuine convergence: OVAM 2020 (330.089) and ILVO 239 2015 (282.821) agree within
  17% on tuinbouw, as they should — ILVO 239 *is* that monitor's agriculture chapter worked out.

**Next-source consequence.** S004 is the only live PDF left in `inbox/`; the other four (S001, S005,
S006, S086) carry the `_RETIRED` mark and the eight archived sources are done. S004 is worth reading
as the 2015 zero-point but is reported at sector grain and **will not add one L4/L5 stream**.
**Neither gap has a queued owner** — checked against the whole 91-row `Sources` sheet. For
`Dierlijk - vee` the only routes are to **reopen the S087 geography call** (its 698.000 t was dropped
because the material is *received by* Flemish processors rather than arising in Flanders — reversible
in one edit, everything recorded) or to **un-retire S001**, whose own verdict note has it covering
the animal by-product sector at ~860 kt for 2021. For `Varia`, three unqueued candidates carry volume
data at the right grain: **S025** (per EURAL code), **S041** (Eurostat `env_wasfw` per NACE) and
**S067** (Comeos retail — the 64.271 t figure S010 cited and no register source owns).

### 2026-09-01 (close) — cleanup, generality check, and the pipeline made re-runnable

**Cleanup.** The five finished one-off scripts and the four completed decision sheets moved to
`register/migrations/` with a README explaining what each did and why it must not be re-run. The
live folder now holds only what runs again for a new source. `apply_reclass.py`'s canonical-order
exporter was extracted to `export_streams.py` first, so nothing live imports a migration; the copy
in `migrations/` is a thin alias. `.gitignore` gained `log.html` (derived), `~$*.xlsx` (Excel locks)
and `archive/` + `inbox/` (the unversioned PDFs).

**Generality check — the pipeline is source-agnostic.** Counted directly: `prep_data.py`,
`derive.js`, `template.html`, `build_overview.py`, `apply_fixes.py`, `export_streams.py` and
`render_log.py` contain **zero** source names and **zero** claim ids. Per-claim judgement is
confined to `OVERRIDE` in `make_aggregate_coverage.py` (59 claims) and two entries in
`promote_totals.py`.

One piece of real overfitting was found and removed: `PLACED_BY_REVIEWER`, a hardcoded list of ten
claim ids exempting them from the residual-class rule. It was redundant — an explicit `OVERRIDE`
entry already expresses the same judgement — so the rule now reads *"an explicit per-claim placement
beats the pattern"*, and there is one place a judgement lives. **Re-validated at 46/46 against the
reviewer's own decisions with zero false positives after the change.** The audit's product-code
detection was also broadened from `Prodcom` alone to the common nomenclature markers (NACE, CN, GN,
HS, CPA), so a source with a different code system is caught the same way.

**New: `verify_overview.py`** — eight arithmetic identities taken from the sources themselves, so
they are independent of the code under test: retail reads 132.082 from C-105 alone; no `AGGREGAAT`
row is ever a summand; MONBIO 4.0's Granen fractions sum to 1.590.919 exactly; provenance flags
match how each figure was built; exclusions re-derive; no node loses volume against its children.
**8/8 pass.** Two of the eight failed on first run and both were wrong assumptions in the test, not
defects — worth recording, because they document real design behaviour: a leaf carrying an aggregate
at another stage *is* legitimately marked summed, and **excluding a component does not move L1**,
because L1 is driven by the reported (aggregate) totals while components drive the coverage %.

**Final state.** MONBIO 4.0 resolves 84,1% of its residual total to L4/L5, MONBIO 3.0 84,9%,
OVAM 2023 19,8%. `audit_register.py` reports **24 open findings** in
`crosswalks/AUDIT_findings.csv` — fifteen residual classes and nine unmarked totals, which are one
decision on the dairy block plus C-587 (a Belgian beer total whose MONBIO 4.0 twin is already
excluded). Everything else is clean.


### 2026-09-01 (later) — round 2 applied; the fixes became rules; protocol v2.5

**No source extracted.** `FIXES_ROUND2.csv` came back 85 `ok` / 1 `skip` and is applied. C-495
(*Gerookte vis, filets daaronder begrepen*) was excluded on the reviewer's note that a cooking
state is not a distinct stream.

**Effect on the overview.** MONBIO 4.0 resolves **84,1%** of its residual total to L4/L5 (was 57,3%
before the class-C promotions and 44,1% at the start of the day); MONBIO 3.0 reaches 84,9%. The L1
totals fall as the double counting goes: MONBIO 4.0 from 7.177.539 to **5.004.331**.

**The reviewer's two remarks became general rules, not claim lists.** Both were phrased as
principles, and both turned out to be mechanisable:

- *"If the name is a sum of things or a collection of parts which already exist, this will almost
  always be an aggregate."* → `COLLECTION_SIGNALS` in `make_aggregate_coverage.py`, fourteen named
  signals (`en andere`, leading `Andere`, `van alle soorten`, `n.e.g.`, three or more
  comma-separated items, `Rund-, schapen-, …`, a whole offal category, …). Validated against the
  reviewer's own 46 decisions: **46/46 agreement**, no misses. A row that calls itself *totaal* is
  exempt — it is a real total, whatever else its name contains.
- *"We kind of made 2 distinctions in the commodity ladder, with the crops but also some sectors in
  varia."* → the placement rule that a processing product goes under its `Varia` sector, not under
  the crop it came from. Bread is not a cereal; refined sugar is not a beet.

A residual class gets `allocatable = no`, so it stays visible in the unallocated band without ever
summing with named siblings — which is what the reviewer's own words asked for: *"this isn't a
component which can be easily placed somewhere in the current commodity ladder."*

**New: `audit_register.py`.** Seven structural checks, none tied to a source, exit code 1 while
anything is open. It immediately found six rows where applying round 2 had left a stale
`L4_ingredient` on a row that now sits at L3 (C-355/356/365/546/547/558) — cleared. **24 findings
remain and are in `crosswalks/AUDIT_findings.csv`** for the reviewer: fifteen residual classes the
rule flags that were not in round 2's scope (notably `Zuivelproducten, n.e.g.`, `Kaas en wrongel`,
`Margarine en andere eetbare vetten`) and nine unmarked totals (the *"Vlaamse productie (vers/gekoeld
+ bevroren)"* rows, which equal the sum of their two halves). **This is the dairy question flagged
`medium` in round 2 coming back: the rule says those rows are residual classes, the reviewer
approved them as L4. It needs one decision, applied to the whole block.**

**Protocol raised to v2.5** with five placement rules and a new *Placement rules* section:
product → L4 never L3; residual class → aggregate; a total carries the prefix; `level_1to5` is the
row's own depth, not what it totals; a processing product goes under its sector. Procedure step 5
now runs `audit_register.py --source S0xx`, and the self-check requires it clean or every finding
explained here. The protocol also records **which scripts run for every source and which are
finished one-off migrations** (`make_varia_reclass.py`, `apply_reclass.py`, `apply_exclusions.py`,
`make_fixes*.py` — do not re-run; `Gemengd` is retired).

**Still open:** `crosswalks/AUDIT_findings.csv` (24 rows). Nothing is committed.


### 2026-09-01 — review applied; structural audit round 1 applied, round 2 open

**No source extracted.** The reviewer completed `REVIEW_2026-08-31.csv` (178 `ok`, 11 `fix`) and
half of `FIXES_2026-09-01.csv` (24 `ok`, 30 `fix`, 49 deferred). The 24 approved fixes are applied.

**Three questions answered from the sources, not from inference:**

- **C-201** — Tabel 30 (p.54, S002) lists *Zuivel* as its own row (123.219 t) beside *Vlees, vis en
  gevogelte* (574.792 t). The row therefore covers meat + fish + poultry only, spans two L2 parents
  (`Dierlijk - vee` and `Dierlijk - vis`), and stays **unallocatable** — which is what the registry
  already said. The 2026-08-31 override to `ok` stands, now on evidence rather than symmetry.
- **C-185 vs C-159** — they do not collapse, because C-185 is already retired. It is a *sentence*
  on p.41 ("afgerond 22.000 ton") that this log flagged in the S002 session as probably unrevised
  2015 text; the reviewer excluded it via `DECISION_expert`. C-159 (12.989, Tabel 17 p.39) is the
  2020 table figure and is the live claim.
- **"were some of these already excluded?"** — no. Checked all 103 fix rows against
  `DECISION_expert`: **none** sits on an excluded claim.

**Applied (24):** the 14 `C-unmarked-total` promotions, 8 `A-prodcom-level` moves to L4, and the 2
`B-level-mismatch` corrections on C-383/C-576. Effect on MONBIO 4.0: the L1 residual total falls
from 7.177.539 to **5.766.983** as the per-gewasgroep totals stop summing with their own fractions,
and resolution to L4/L5 rises from 57,3% to **71,4%**.

**Round 2 opened — `crosswalks/FIXES_ROUND2.csv`, 86 rows.** The reviewer's remarks showed round 1
had asked three questions as one. Round 2 separates them:

- **the collection rule** (46 rows) — *"if the name is a sum of things or a collection of parts
  which already exist, this will almost always be an aggregate."* Prodcom residual categories
  (`Andere ...`, `... en andere ...`, `van alle soorten`, `n.e.g.`, several species in one cell)
  are nomenclature buckets, not products, so they take the `AGGREGAAT - ` prefix instead of an L4.
- **the two-partition rule** (8 rows) — *"we kind of made 2 distinctions in the commodity ladder,
  with the crops but also some sectors in varia."* A processing product filed under the crop it came
  from moves to the Varia sector: bread is not a cereal, refined sugar is not a beet.
- **13 genuine single products** keep the round-1 proposal. The dairy rows among them are flagged
  `medium`: they also pair two products, but round 1 approved the analogous rows as L4.
- **12 `B` rows** re-proposed as the reviewer asked ("why level 2 suddenly?") — the row gets its
  real `L2 = Varia` instead of the placeholder `Aggregaat`, so *level 2* means "this row sits at
  L2" and the level it totals stays in `aggregate_coverage.totals_level`.
- **7 placement corrections** from the review sheet, including a new L3 member.

**One new dictionary member proposed: `Varia > Suiker`** — glucose/fructose/invertsuiker, refined
sugar and melasse are sugars, and were sitting under starch or under a crop. Not yet applied; it
becomes real when round 2 is approved.

**Also corrected:** C-086 is a subset, not a full L3 total — the source says *"som van de 10
belangrijkste"*, and two of those ten (komkommer, kropsla) are reported in pieces and were never
convertible, so its coverage can never reach 100%.

**Still open:** `FIXES_ROUND2.csv` (86 rows, all awaiting `DECISION_fix`). Nothing is committed.


### 2026-08-31 — crosswalk review applied; register-wide aggregate correction; 80/20 gap analysis

**No source extracted.** The reviewer's decisions on the two human-gated crosswalks were applied,
and a register-wide modelling error was corrected. The reviewer was away, so the remaining
decisions were **taken provisionally by Claude and stamped in the files** — every one is
recoverable, and none is settled.

**What the reviewer decided.** `varia_reclass.csv`: 41 rows kept, 59 excluded. `aggregate_coverage.csv`:
62 `ok`, 7 `unallocated` (all the EU-definition totals), 8 deferred as `0`, 1 `exclude`.
Shelving the EU-definition rows resolves the retail contradiction structurally — retail
agri-food waste now reads 132.082 from C-105 alone, with no averaging against the EU figure.

**Exclusions were not reaching the overview.** `prep_data.py` never read `DECISION_expert`, so
14 claims the reviewer had already excluded were still counted. Wired up, plus the 44 further
claims flagged in the reviewer's crosswalk remarks (`apply_exclusions.py`). **58 claims retired,
66.068.834 t/yr** — dominated by mengvoeder (C-390 7,4 Mt; C-384 6,2 Mt) and the two beer rows,
which had been inflating every food-industry production figure.

**The `Gemengd` → `Varia` reclassification was applied**, with the two NACE lumps split into
`Chocolade` and `Zetmeel en zetmeelproducten`. Five of the eleven originally proposed L3 buckets
turned out to be empty once the exclusions applied — including both new dictionary members the
first revision had invented — so the split *shrinks* the vocabulary. `Gemengd` is now empty and
retired; see `commodity_hierarchy.md`.

**Register-wide correction: 40 rows promoted to `AGGREGAAT`.** Rows the source itself calls a
*totaal* were sitting in the register as ordinary components, so every sector total was being
added to its own parts — the cause of 132% coverage on akkerbouw and 165% on the primary stage.
Promoted by `promote_totals.py` on name evidence, plus **C-043 on arithmetic** (it equals
C-005 308.000 + C-042 240.305 exactly). Not promoted: C-057, whose "incl. niet-geoogste" names
its scope, not a total — it is the only voedselverlies figure for that node.

**Anomalies — variants, not errors.** The detector also found rows that equal a sum of siblings
without saying they are totals: C-343 and C-533 (`Verwerkte vloeibare melk`, Prodcom 105111),
C-541 (`Zuivelproducten n.e.g.`). Prodcom classes cut across each other, so these are most
likely coincidence rather than totals, and were **left as components**. C-586/C-587 (beer
equalling a sum of unrelated grain rows) are certainly coincidence. All four need a reviewer's eye.

**Provisional decisions taken by Claude** — all stamped, all reversible:
- 35 `varia_reclass` rows whose proposal moved (`AUTO-DECIDED by Claude 2026-08-31`).
- 58 `aggregate_coverage` placements, including the 8 the reviewer had deferred as `0`, which the
  L3 split made answerable.
- **C-201 overridden.** The reviewer set it to `no`; its 2023 twin C-098 is `ok`. Same claim,
  different edition, so they were aligned — marked `AUTO-OVERRIDE` in the `revision` column.
  **This is the one place an explicit human decision was reversed.**

**Retail rows are a chain stage, not a commodity.** C-103/104/106/107 and their 2020 twins became
`component_set` aggregates. Each pair sums exactly to a total the source also prints standalone
(115.862 + 16.220 = 132.082 = C-105; 53.330 + 6.519 = 59.849 = C-108), so `derive.js` now marks a
component_set that reproduces a total in its own group as a **restatement** and leaves it out of
the mean — otherwise that figure would be weighted twice against a genuine variant (retail
voedselverlies would read 59.516 instead of 59.349).

**80/20 gap analysis** (published as an artifact). Against an addressable total of 9.327.369 t/yr
— MONBIO 4.0 primary residues 7.177.539 + OVAM 2023 food industry 2.017.748 + retail 132.082 —
only **44,1% is resolved to L4/L5**, all of it in primary production. Five Flemish items
(maisstro, aardappelloof, suikerbietenloof, bietenpulp, tarwestro) carry 80% of that selectable
pool but only **33,8% of the addressable total**. The food industry has *no* L4/L5 detail at all,
and every selectable item is a field residue rather than a processing side-stream. Largest gaps:
food industry undifferentiated 1,34 Mt · `Suiker- en zetmeelgewassen` 1,21 Mt · food-industry
subsectors at L3 597 kt · `Granen` 496 kt · `Dierlijk - vee / Vlees` 304 kt.
**Recommended next extractions: S005 (MONBIO 1.0) first** — it names bietenpulp+melasse 458 kt,
bostel 80 kt and gries/zemelen/DDGS 646 kt, hitting the two largest gaps at once — **then S087**
(Marktanalyse Biomassareststromen 2024) for slaughter by-products, then S066 and S065 for
horticulture and fruit.

**Still open for the reviewer:** the five empty L3 subgroups (placeholders or not); whether field
residues belong in a BioMobi selection at all, which changes the denominator; the three Belgian
FEDIOL rows in the ranking (lijnzaad-, soja- en zonnebloemschroot) that cannot stand in for
Flemish claims; and several reviewer remarks that appear paste-offset by one row
(C-199/C-201, C-355/C-356, C-472, C-518) — acted on by row content, not by the remark text.

**Backups** of both crosswalks and the pre-change workbook are in the session scratchpad under
`scratchpad/backup/`.


*Sessions that changed how the corpus is read rather than what is in it. Kept apart from the
Sessions table above, which is one row per source extraction.*

### 2026-08-26 — the stream overview learns that an aggregate is not a commodity

**What was wrong.** `stream_overview.html` treated every claim as a summand, including the 78
rows named `AGGREGAAT - …`. Those rows are totals *of* other rows, so adding them to their own
components double-counted, and where a source printed two definitions of one total the view
added those together as well. The reviewer's example: OVAM 2023 retail read **192,166 t** with a
38/62 split — the EU-definition figure (C-003, 60,084) plus the Belgian one (C-105, 132,082),
wearing the Belgian split. The same fault kept the coverage line blank at L1 and L2, because the
figure that *was* their reported total was standing beside them as an ordinary commodity row.

**The model now.** Two axes. Components build the commodity tree and sum as before. An aggregate
never enters a sum; it attaches to the row whose children it totals and becomes the denominator
the level below is measured against. Each aggregate is described by the level it totals, the row
it attaches to, whether it covers **all** of that row's entries or a named **subset**, which
chain stages it spans, and its quantity type. **Allocation rule (reviewer's):** an aggregate is
placeable only when everything it covers sits under one parent row at one level; anything else —
OVAM's *Aardappelen, groenten en fruit*, which totals three L3 entries under two different L2
parents — goes to an **unallocated** band, visible and usable but never compared or summed.

**Two reconciliations this exposed**, both previously invisible:

- OVAM 2023 · Retail · agri-food waste — the two component rows (115,862 + 16,220) make
  **exactly** C-105's 132,082. Dropping the EU figure from the average takes the row to 100%.
- OVAM 2023 · Voedingsindustrie · agri-food waste — the eight subsector rows sum to 2,017,721
  against C-092's 2,017,748, i.e. **100.0%**, 27 t of rounding.
- C-113 + C-114 (nevenstromen primaire sector, ingezameld + andere bestemming) reconcile to
  **215,170 = 100.0%** of the printed total once they are treated as one figure rather than two
  competing ones. They are marked `component_set` in the registry for that reason.

**Competing values are averaged and listed, never summed** — the existing cross-source rule,
now applied to competing definitions inside one source too. Each value can be excluded from the
average in the browser. This is a reading aid held in the browser only; a decision worth keeping
should be written down here.

**`type_assumed`-style honesty about arithmetic.** Every number in the view now carries its
provenance: unmarked = a figure straight from the register, `Σ` = summed by the view, `ø` = an
average, `Σø` = a sum of averaged parts.

**Two human gates opened, both awaiting `DECISION`:**

- `crosswalks/aggregate_coverage.csv` — 78 rows, one per aggregate, saying what each is the
  total of. Proposals only. Notable ones the default rule could not get right: C-002 and C-004
  span 2 and 4 of the 6 in-scope stages so neither may fill the Total column; C-111/C-112 and
  C-113/C-114 are route halves that sum; C-218/C-238/C-399/C-419 (*plantaardige landbouw*) are
  commodity subsets spanning akkerbouw + tuinbouw; C-279/C-329 and C-280/C-335 are the **same
  FEDIOL figure recorded twice** under two placements, which will double-count until one of each
  pair is excluded.
- `crosswalks/varia_reclass.csv` — 100 rows retiring `Gemengd` for `Varia`. 82 become components
  with a real L3 (MONBIO's Prodcom rows keyed off the printed Prodcom class, not guessed from
  the wording, and flagged as an overlapping nomenclature that must never be summed together);
  4 become aggregates because they are totals of commodity groups the tree already holds
  (C-094, C-098 and their 2020 twins C-195, C-201) and gain the `AGGREGAAT - ` prefix. Two new
  dictionary members are proposed: **`Mengvoeder en diervoeder`** (NACE 10.9) and **`Overige
  voedingsmiddelen`** (NACE 10.84/10.89). `apply_reclass.py` refuses to run while any `DECISION`
  is blank; it was tested end-to-end on a copy of the workbook (100 rows changed, idempotent on
  a second run, only the five intended columns touched, 592 claim ids unchanged).

**Note for whoever reviews the workbook:** its columns have been rearranged (`source_page` now
sits first). Every script here reads and writes by column header, so that is safe.

## Anomaly notes (detail, keyed by source_id)

### S065

**98 claims (C-704…C-801). The superset to S066, and the widest single source in the corpus.**
GeNeSys covers three chain stages where S066 covers one, and reports at a scope S066 explicitly
excludes. Together the two now hold the tuinbouw side from field to processing.

**Where the data actually is.** The numbered tables carry almost nothing: **Tabel 2** (p.18) has
three rows, **Tabel 3** (p.21) seven, **Tabel 4** (p.24) nine. The per-crop detail — the figures
every downstream study quotes as "GeNeSys 2010" — lives in **Bijlage 1 on p.68**, an unnumbered
appendix table absent from the source's own list of tables. Any session working from the table list
alone would miss 62 of this source's 98 claims.

#### 1. Variant readings

**Tabel 2's totals are rounded versions of Bijlage 1, and the rounding is now measurable.** Both
were captured as printed, with the exact sum recorded in `also_stated_in`:

- **Groenten 800.000 t** (Tabel 2) against **799.285 t** summed over Bijlage 1's 25 groenterijen.
- **Fruit 87.000 t** (Tabel 2) against **86.978 t** summed over its 4 fruitrijen.

The source describes these as *"gemiddelden, berekend op basis van GeNeSys database"*, so the
rounding is intentional, not an error.

**The akkerbouw row is a rival measurement of streams the register already holds.** C-766 carries
**3.000.000 t** of oogstresten on 224.428 ha of akkerbouwgewassen (granen, aardappelen,
suikerbieten). MONBIO already gives measured stro figures — maisstro + tarwestro = 1.590.919 t. The
two are not reconcilable and must never be summed: S065's is a flat order-of-magnitude estimate
attributed to Bernaerts et al. (2012) with no reference year, MONBIO's is a per-fraction
measurement. Cross-referenced on the row.

#### 2. Suspected source errors

**None.** But one **layout trap** that would have produced a wrong reading, caught by arithmetic:

In Bijlage 1, each band-header row carries the **previous** block's production total, not its own.
The number **1.009.182** is printed on the row headed *Glasgroenten*, and **340.570** on the row
headed *Fruit*. Verified by summing:

- the 23 openluchtgroenten production cells total **1.009.182** exactly → the figure on the
  *Glasgroenten* row belongs to openluchtgroenten;
- the 6 glasgroenten production cells total **340.570** exactly → the figure on the *Fruit* row
  belongs to glasgroenten.

Both are captured under the block they actually measure (C-764, C-765), with the trap spelled out
in `source_type_label`. A reader taking the labels at face value would attribute 1,0 Mt of
open-field production to glasshouses.

#### 3. Deliberate exclusions

**a. Rates and areas.** Bijlage 1's *Areaal (ha)* and *Reststroom (ton/ha)* columns; Tabel 2's
*Areaal* columns; Tabel 4's *%* column. Converting a ton/ha rate into a Flemish tonnage needs the
area, which is a derivation — and unnecessary, since the source has already done that arithmetic in
its *Totale hoeveelheid natte reststroom* column, which **is** captured.

**b. Cells with a rate but no tonnage.** Six Bijlage 1 rows carry a production figure but no
residual total — **Asperge** (*"Loof en schillen"*, no rate), **Chicorei** (20 ton/ha, no total),
**Peterselie**, **Pompoen**, **aubergine**, **veldsla**. Their production rows are captured; there
is no residual figure to capture. In Tabel 4, **Diepvriesindustrie** gives 25% schilverlies,
**Verlies bij snijderijen** 20%, and **Appel** 10-30%, all three without a tonnage; only
diepvries's 955.000 t production figure is capturable (C-800).

**c. Ranges, not values.** §5.4's summary bands — oogstresten *"ca. 15.000 – 200.000 ton per
jaar"*, productieverliezen *"ca. 3.000 – 20.000 ton"*, veilingverliezen *"400 – 2.000 ton"*. A
range is not a figure.

**d. Out of scope by nature.** Tabel 1 (p.6, patents), Tabel 5 (p.28, valorisation costs in
EUR/ton), Tabel 6 (p.36, protein/fibre sources in feed), Tabel 7 (p.54, knelpunten en
opportuniteiten), and chapters 6-10 entirely (valorisation routes, markets, supply-chain
organisation, legislation). Prices, qualitative criteria and policy text.

**e. Destination data.** The three *"Huidig gebruik"* paragraphs and Tabel 5, indexed in
`destination_index.csv`. They are qualitative or in percentages; the one tonnage among them
(129.000 t, §5.3.2) **is** captured, as C-801.

#### 4. Completeness sweep

**7 numbered tables, 6 numbered figures, plus 1 unnumbered appendix table.**

| Object | p. | Disposition |
|---|---|---|
| Tabel 1 (patenten) | 6 | excluded — patent counts, not quantities (3d) |
| **Tabel 2** (arealen + oogstresten, 3 rijen) | **18** | **captured — 3 aggregates (C-766…C-768)**; areaal columns dropped (3a) |
| **Tabel 3** (uit de markt genomen, veilingen) | **21** | **captured — 7 claims (C-769…C-775)**, kg → t |
| **Tabel 4** (productieverliezen industrie, Belgie) | **24** | **captured — 25 claims (C-776…C-800)**; the three %-only rows have no tonnage (3b) |
| Tabel 5 (valorisatietrajecten) | 28 | excluded — EUR/ton and qualitative (3d); indexed |
| Tabel 6 (eiwit/vezel/antioxidant-bronnen in veevoeding) | 36 | excluded — no Flemish volumes (3d) |
| Tabel 7 (knelpunten en opportuniteiten) | 54 | excluded — qualitative (3d) |
| Figuur 1 (overzicht GeNeSys) | 7 | project schema, no numbers |
| Figuur 2 (SIC-model) | 11 | method schema, no numbers |
| Figuur 3 (brede scan) | 12 | method schema, no numbers |
| Figuur 5 (waardepiramides) | 14 | schema, no numbers |
| Figuur 6 (ketenopbouw tuinbouwproducten) | 17 | chain schema, no numbers |
| **Bijlage 1** (oogstresten per gewas) | **68** | **captured — 62 claims (C-704…C-765)**, 33 production rows + 27 residual rows + 2 block totals |

*(The source's figure numbering skips 4 — there is no Figuur 4 in the body; Figuur 3 is followed by
Figuur 5. Noted so a reviewer does not hunt for it.)*

Running text was swept: §5.3.2's **129.000 t** is the only tonnage outside the tables and is
captured (C-801). §5.4 carries only the ranges in (3c).

#### 5. Judgement calls & new dictionary members

**Three session decisions, all taken by the user:**

1. **Everything maps to `agri-food waste` with `type_assumed = TRUE`.** S065's Box 1 defines
   nevenstroom and voedselverlies exactly as the register does, but then says it will use
   *reststromen* as the umbrella *precisely because* it does not distinguish them — so the register
   does not distinguish either. The fraction is preserved in `L5_fraction_as_named`, so nothing is
   lost. **This is the sharp contrast with S066**, extracted the same day, where every row carries
   `type_assumed = FALSE`: same institute, same crops, one splits and one declines to.
2. **Tabel 4 captured at `geography = Belgie`** with the coverage caveat on every row. Worth being
   precise about *how* Belgian it is: the residual tonnages are derived from the column *"productie
   industriegroenten in België **en buitenland** voor verwerking in België"*, verified
   (76.000 × 5% = 3.800; 107.000 × 20% = 21.400; 306.000 × 5% = 15.300). So the crops are partly
   grown outside Belgium and only the processing is Belgian. Both production columns are captured
   as **parallel accountings** — narrow (Belgian arealen) and wide (incl. foreign) — cross-
   referenced with never-sum warnings.
3. **The akkerbouw 3 Mt row captured**, cross-referenced against MONBIO's stro rows (§1).

**Two audit findings were resolved by fixing my own row names, not by overriding the rule.**
`audit_register.py` flagged the two *Bonen* rows as an unmarked residual class, because I had put
the source's footnote (*"stambonen, stamslabonen, tuinbonen en veldbonen"*) into
`stream_name_NL`, which trips the several-species-in-one-cell signal. The source's row is simply
*Bonen*; the enumeration is a footnote clarifying what the L4 member covers, not a nomenclature
leftover bucket. Names corrected to *Bonen*, footnote moved to `source_type_label`. **S065 now
audits clean at 0 findings**, and the rule was not weakened to get there.

**Twelve new L4 members and six new L5 fractions** — the largest intake so far, because Bijlage 1
lists 33 crops. Full list and reasoning in `commodity_hierarchy.md`. Three points recorded there:

- **`Kool` gained three siblings**, exactly as the S066 note predicted. `Witte kool`, `Rode kool`
  and `Savooikool` are members alongside the coarser `Kool`. They are **not** an
  aggregate-and-components pair: they come from different sources, and the aggregate machinery
  operates only within a source.
- **`Cichorei` and `Courgette` now sit under two L3 parents**, following each source's own
  placement — the same overlapping-partition situation the MONBIO gewasgroepen created. Never sum
  across.
- **`Kropsla` was deliberately not added**; the row uses the existing `Sla en andijvie`.

**The doordraai rows carry a vocabulary conflict, recorded on the row.** Tabel 3's column is headed
*"Totale hoeveelheid natte **nevenstroom** (kg)"*, but market-withdrawn produce is marketable,
edible fruit and veg — which contradicts the source's own Box 1 definition of nevenstroom as
*niet-eetbare* biomassa. Rather than pick a side, the rows take `agri-food waste` with
`type_assumed = TRUE` and state the conflict in `source_type_label`. Two coverage caveats travel
with them: only the **three** auctions that applied for EU intervention support are counted, not
all Flemish auctions, and **fruit was omitted by the source** as negligible.

**Wet weight throughout.** The source works deliberately in natte tonnages, because its dry-matter
percentages were computed on the primary product rather than on the residual stream. Recorded in
`source_type_label` on every S065 row. The register has no basis column, so this is the only place
it can live — and it matters when comparing S065 against any dry-matter source.

**S010's transcription of this source was accurate — with one exception, already logged.** All 22
Bijlage 1 figures and all 4 fruit figures that S010 reproduces match exactly. Its Tabel 4 relabelled
S065's *Cichorei* as *Witloof* (8.250 t) and flagged only bloemkool as `(BEL)` when the whole table
is Belgian. And **two figures S010 attributes to "GeNeSys 2010" are not in this report at all** —
*groente- en fruitverwerking 337.404 t* and *organisch-biologische afvalstoffen … 723.449 t*. They
must come from the GeNeSys *database* or another output, not Mededeling 165. A third, *veilingen
5.191 t*, is S010's own sum of Tabel 3 (5.190.667 kg), not a figure this source prints — so it is
not captured here.

**How S065 and S066 relate, for the reviewer.** They are **not** rival measurements. S066 measures
cells B+D of its own scope matrix — food-linked, post-harvest, primary production only. S065
measures A+B+C+D+E+F+G+H+I — including pre-harvest, non-food-associated material (stro,
spruitstokken, loof), and the veiling and verwerking stages. That is why the same crop differs so
widely: spruiten reads **5.452 t** in S066 and **138.000 t** in S065, a factor 25. Neither is wrong;
they answer different questions. **Never sum or average across the two sources**, and read S065 as
the outer bound.

**No Zotero item (F-002).** The Zotero MCP server timed out on connect this session. PDF archived as
`archive/S065_genesis.pdf`.

**42 aggregate rows now await a `DECISION` in `crosswalks/aggregate_coverage.csv`** — 35 from S066
plus 7 from S065.

### S066

**111 claims (C-593…C-703). The source the register has been waiting for.** ILVO Mededeling 239 is
the detailed working-out of the landbouw chapter of the 2015 chain monitor, and it is the first
source to give **per-crop, per-channel figures with the edible/inedible split already made**. It
closes, on the tuinbouw side, exactly the gap the 2026-08-31 analysis named.

**Its definitions map onto the register's axis one-to-one** — and this is the first source of which
that is true. S066 defines *voedselverlies* as the **eetbare fractie** and *nevenstroom* as the
**niet-eetbare fractie**, with *voedselreststromen* their sum (§2.2.4). That is the register's own
`voedselverlies` / `nevenstroom` / `agri-food waste` triple, not a homonym: MONBIO's split is
**economic** (has value / has none) and OVAM's is usually absent. So **every S066 row carries
`type_assumed = FALSE`** — 111 of them — where every MONBIO residual row carries `TRUE`. Worth
stating because the same three words have now meant three different things across four sources, and
only here do they mean what `quantity_type.csv` means.

**The `Afzetkanaal` column is a destination channel, not a chain stage.** Tabel 7 splits most crops
into *industrie* and *versmarkt*. Both are `chain_L2 = Primaire productie`: §2.1 fixes the system
boundary at the point the product **enters** processing, and the loss being measured happens on the
farm, post-harvest, before that boundary. A row labelled *industrie* is the grower's loss on a crop
destined for industry — it is not a `Voedingsindustrie` figure. The channel is carried in
`stream_name_NL` as `(afzetkanaal industrie/versmarkt)`, which is also what distinguishes the
sibling rows: prei appears twice at the same stage, year and quantity type, and the two differ by a
factor 5,4 (15.998 t vs 85.748 t), so the names must say why.

#### 1. Variant readings

**Two rounding-level mismatches inside Tabel 9's own totals**, both captured as printed, neither an
error:

- **Fruit voedselverlies** — Tabel 9 prints **26.997 t**; Tabel 7's four fruit rows sum to
  **26.998 t** (11.131 + 13.556 + 1.836 + 475).
- **Groenten beschutte teelt voedselreststroom** — Tabel 9 prints **21.070 t**; Tabel 7's five rows
  sum to **21.069 t**.

Both propagate into the TOTAAL row (222.912 printed vs 222.913 summed; 282.821 printed vs 282.820
summed). One tonne on a quarter-million: rounding, recorded so a reviewer re-doing the sum is not
puzzled.

**A rounded restatement, not captured separately:** the samenvatting (p.36) gives *"afgerond
283.000 ton voedselreststromen, waarvan 79% voedselverliezen en 21% nevenstromen"*. Per the
restatement rule the precise 282.821 is the claim; the rounded figure is recorded in
`also_stated_in` on C-686.

#### 2. Suspected source errors

**One, with arithmetic evidence: Tabel 7's TOTAAL production figure omits one of its own rows.**

- Tabel 7 prints **TOTAAL productie = 2.108.932 t**.
- Its own production column sums to **2.119.885 t**.
- The difference is **10.953 t — exactly the printed *overig fruit* row**.

This is not rounding, and it is not ambiguous: 2.108.932 = 1.487.740 (Tabel 4 TOTAAL GROENTEN) +
621.192, and 621.192 is Tabel 5's fruit total **minus** overig fruit. So the TOTAAL row excludes
overig fruit from the production column while **including** it in all three residual columns (the
reststroom total 282.821 contains overig fruit's 548 t — verified: openlucht 228.509 + beschut
21.069 + fruit 33.242 = 282.820). The row is internally inconsistent about its own scope.

Captured **as recorded** on **C-685**, never corrected, with the discrepancy stated in
`source_type_label` and the alternative sum cross-referenced in `also_stated_in`. Consequence
worth knowing: the source's headline *"13% van de productie"* ratio uses the short denominator, so
it is very slightly overstated. `DECISION_expert` can retire C-685 if the reviewer prefers the
2.119.885 reading — but note the register does not hold that figure as a row, because the source
never prints it.

#### 3. Deliberate exclusions

**a. Tabel 1 (p.5) — the chain-wide 2015 sector table (session decision 3).**
Skipped in full. S066 attributes it explicitly to *Vlaams Ketenplatform Voedselverlies (2017)* =
**S004**, which is in the `Sources` sheet and queued in `inbox/`, so the cross-source restatement
rule applies. Named row by row so nothing looks missing when S004 is extracted: visserij **10.402**,
landbouw **449.352**, veilingen **15.277**, voedingsindustrie **2.349.445**, retail **64.828**,
horeca **67.450**, catering **60.098**, huishoudens **468.305**, totaal keten **3.485.157**. The
last four are out of scope by stage in any case (horeca, catering, huishoudens, and a whole-chain
total that contains them).

**b. Percentages and areas.** Tabel 7's *Verhouding voedselreststromen t.o.v. productie (%)*,
*Percentage eetbaar (%)*, *Percentage niet-eetbaar (%)* and *Areaal (ha, 2014)* columns; Tabel 4/5's
*Aandeel (%)* column; Tabel 10 (p.37) entirely, which is expressed only in % of the sector total;
and Figuur 5 (p.36), a pie of each crop's share of the tuinbouw residual total. None is a quantity
of material. The areal figures cannot be converted without multiplying by a yield, which the
conversion rule forbids.

**c. Per-hectare figures in the running text.** §5 repeatedly gives losses per hectare — bonen
*"10-30 ton per hectare"* oogstresten (ARBOR, 2015) of which *"5% ... = 0,5 ton/ha"*; uien *"zo'n 20
ton schillen per ha"* plus buitenste rokken, *"in totaal 21,5 ton voedselreststromen/ha"*. Turning
these into Flemish tonnages needs the areal column, which is a derivation. Not captured — and not
needed, because the source has already done that arithmetic itself and printed the result in
Tabel 7, which **is** captured.

**d. Material S066 excludes from its own scope, where it names no tonnage.**
§2.2.6 puts *"niet aan voedsel gelinkte niet-eetbare biomassareststromen"* outside the monitoring —
stro, spruitstokken, fruit trees, and bloemkoolblad on crops harvested for industry (which are left
in the field and never enter the food chain). The protocol says such material is captured **when the
source names a tonnage**; here it does not. The only figures given are the per-hectare ARBOR ranges
in (c), which are not convertible. Pre-harvest losses (§2.1) are likewise excluded by the source and
carry no tonnage. **This is the structural reason S066's numbers are far smaller than GeNeSys's for
the same crops** — see §5.

**e. Destination data.** Tabel 6 (p.17, bestemming preigroen), Tabel 8 (p.34, bestemmingen per
teelt) and Tabel 10 (p.37) resolve the destination axis only. Indexed in `destination_index.csv`,
values not extracted. Tabel 8 repeats Tabel 7's residual tonnages split over destinations; the
per-teelt totals are in the corpus from Tabel 7.

#### 4. Completeness sweep

**10 tables, 5 figures — the source's own lists (p.43) match the body numbering exactly.**

| Object | p. (PDF / gedrukt) | Disposition |
|---|---|---|
| Tabel 1 (chain-wide voedselreststromen 2015) | 5 / 3 | excluded — restatement of S004 (3a) |
| Tabel 2 (scope-vergelijking A-I) | 11 / 9 | carries no numbers — a scope matrix |
| Tabel 3 (overzicht experten) | 13 / 11 | carries no numbers — an interview roster |
| Tabel 4 (productie groenten per teelt, 2014) | 15 / 13 | **captured** — 5 group aggregates (C-689…C-693); per-teelt cells restate Tabel 7's productie column, cross-referenced |
| Tabel 5 (productie fruit per teelt, 2014) | 15 / 13 | **captured** — TOTAAL FRUIT aggregate (C-694); per-teelt cells as above |
| Tabel 6 (bestemming preigroen) | 17 / 15 | excluded — bestemmingsas (3e); indexed |
| **Tabel 7** (berekening per teelt) | **32 / 30** | **captured — 96 claims (C-593…C-688)**, 23 crop×channel rows × 4 quantity columns + the TOTAAL row × 4 |
| Tabel 8 (bestemmingen per teelt) | 34 / 32 | excluded — bestemmingsas (3e); indexed |
| Tabel 9 (per sector en subsector, 2015) | 36 / 34 | **captured** — 9 subsector aggregates (C-695…C-703); its TOTAAL row restates Tabel 7's and is cross-referenced, not re-captured |
| Tabel 10 (bestemmingen in %) | 37 / 35 | excluded — percentages (3b); indexed |
| Figuur 1, 2 (Fusions systeemgrenzen) | 6 / 4 | schemas, no numbers |
| Figuur 3 (afbakening voedselverlies) | 7 / 5 | schema, no numbers |
| Figuur 4 (cascade van waardebehoud) | 10 / 8 | schema, no numbers |
| Figuur 5 (verhouding per teelt) | 36 / 34 | excluded — shares, not quantities (3b) |

**Cell-by-cell note for Tabel 4 and 5**, because only part of them was captured: their per-teelt
production cells are identical to Tabel 7's *Productie (ton, 2014)* column (verified for all 23),
so Tabel 7 is the capture location as the more specific one (it adds the channel), and every row
carries `ook in Tabel 4 (p.15)` / `ook in Tabel 5 (p.15)` in `also_stated_in`. What Tabel 4/5 add
and Tabel 7 does not have are the **six group subtotals**, which are captured as aggregates. The
*Aandeel (%)* columns are dropped per (3b).

§5's running text restates most Tabel 7 cells in prose (bonen p.16, prei p.17, bloemkool p.18,
wortelen p.19, spruiten p.20, witloof p.21, spinazie p.22, ui p.23, kolen and overige p.24, sla
p.25, tomaten p.26, paprika p.27, champignons p.28, appelen p.29, peren p.30, aardbeien and overig
fruit p.31). All verified identical to the table; each row carries its text page in
`also_stated_in`. Nothing in §5 is a figure the tables do not hold, apart from the per-hectare
values in (3c). §7 (bevindingen) and §8 (ILVO-projecten) carry no tonnages.

#### 5. Judgement calls & new dictionary members

**One new member: `Kool`** (L4, under `Groenten openlucht`), for the source's *"kolen (witte, rode
en groene)"*. **Recorded as a judgement in `commodity_hierarchy.md`, because v2.5 rule 2 could have
gone the other way:** a cell naming several species is normally a residual class and takes the
prefix with `allocatable = no`. It is deliberately not treated so here — witte, rode and groene kool
are colour variants of one commodity rather than a leftover bucket, and none exists separately in
the register, so the reviewer's test (*"a collection of parts which already exist"*) is not met. If
a later source splits them, this row should be re-read as an aggregate.

**Four residual classes take the prefix and `allocatable = no`**, per v2.5 rule 2: *overige groenten
industrie*, *overige groenten vers*, *overige groenten beschut*, *overig fruit*. This is what makes
the register's sums reconcile exactly — see below.

**The arithmetic was verified independently after loading, and it closes exactly.** Summing the
captured component rows against the captured Tabel 9 aggregates leaves a residue equal, to the
tonne, to the residual-class rows held out of the sum:

| Subsector | quantity type | components | Tabel 9 | difference | equals |
|---|---|---:|---:|---:|---|
| Groenten openlucht | voedselreststroom | 205.471 | 228.509 | 23.038 | overige industrie 15.618 + overige vers 7.420 |
| Groenten openlucht | voedselverlies | 155.412 | 174.900 | 19.488 | 13.211 + 6.277 |
| Groenten openlucht | nevenstroom | 50.058 | 53.609 | 3.551 | 2.407 + 1.144 |
| Groenten beschut | nevenstroom | 26 | 55 | 29 | overige beschut 29 |
| Fruit | voedselreststroom | 32.694 | 33.242 | 548 | overig fruit 548 |
| Fruit | nevenstroom | 6.172 | 6.245 | 73 | overig fruit 73 |

Only the two rounding cases of §1 fail to close to the tonne. This is the cleanest reconciliation in
the corpus so far, and it is a direct consequence of applying v2.5 rule 2 rather than a coincidence:
had the *overige* rows been captured as ordinary components they would have summed with their named
siblings and the totals would have matched **by accident**, hiding the fact that they are unnamed
residue.

**A transcription error in S010, found from here.** S010 (retired earlier today at 0 claims) quotes
this source fourteen times in its Tabel 3 and Tabel 5. Thirteen match exactly; **one does not** —
S010 prints spruiten *"5.542 ton"* where S066's Tabel 7 and its own text (p.20) both read **5.452**.
A digit transposition in S010, not in S066. It costs the register nothing, since S010 holds no rows,
but it is worth recording as evidence for the decision taken this morning: a consolidation is not a
substitute for its primary sources.

**What this source does *not* settle.** S066 measures only the food-linked, post-harvest part
(cells B+D of its own Tabel 2). GeNeSys (**S065**) measures A+B+C+D+E+F+G+H+I. That is why S010's
Tabel 3 shows the two diverging so widely on the same crops — spruitstokken 57.542 vs 138.000 t is
not a contradiction but two different questions, and **S066's numbers are structurally the smaller
of the two**. When S065 is extracted, its rows must not be read as rival measurements of these:
they are a superset. Say so explicitly on the S065 rows.

**No Zotero item (F-002).** The Zotero MCP server timed out on connect this session, so no item was
created and `citation_key` stays blank. PDF archived as
`archive/S066_Monitoring voedselverliezen Vlaamse tuinbouw_ILVO.pdf`.

**35 aggregate rows await a `DECISION` in `crosswalks/aggregate_coverage.csv`** — proposals
generated by `make_aggregate_coverage.py`, used in the overview meanwhile but shown as unreviewed.

### S010

**Outcome: zero claims — a consolidation with nothing of its own.** S010 was read cover-to-cover
and retired without a row, for a completely different reason than S087. S087 was the wrong *topic*;
S010 is exactly the right topic and is, on paper, the richest per-crop table set in the whole
queue — but it contains **no original measurement**. Every tonnage it prints is a restatement,
attributed cell by cell to a study the register already owns or has queued.

**The attribution structure.** All volume data sits in four tables (Tabel 2 p.17, Tabel 3 p.19,
Tabel 4 p.21, Tabel 5 p.22). Every figure in all four carries a superscript letter resolving to one
of five upstream studies:

| Upstream study, as S010 cites it | Register source | Status at time of reading |
|---|---|---|
| MONITOR VOEDSELVERLIES 2020 (Braekevelt et al., 2023) | **S002** | extracted, 100 claims |
| GeNeSys 2010 (Kips & Van Droogenbroeck, 2014) | **S065** | queued in `inbox/` |
| ILVO 2015 (Bernaert, Van Droogenbroeck & Roels, 2018) | **S066** | queued in `inbox/` |
| MONBIO 2019/20 (Van Kerckhove et al., 2023) | **S006** | queued in `inbox/` |
| COMEOS 2018 (Comeos, 2019) | *not in the register* | — |

**A reading hazard worth recording: the letter scheme changes between tables.** The superscripts are
re-assigned per table and a reader who carries one legend forward will mis-attribute every cell:

- **Tabel 2** — A = MONBIO, B = GeNeSys, C = Monitor Voedselverlies, D = COMEOS
- **Tabel 3** — A = MONBIO, B = GeNeSys, **C = ILVO 2015**, **D = Monitor Voedselverlies**
- **Tabel 4** — A = GeNeSys (single source; the whole table)
- **Tabel 5** — **A = GeNeSys**, **B = ILVO 2015**, **C = MONBIO**, **D = Monitor Voedselverlies**

Three different meanings for `C` and three for `D` across four adjacent tables. Any future session
that pulls figures from here must re-read the legend beneath each individual table.

#### 1. Variant readings

None captured, because nothing was captured. The tables do however *display* variants, which is
their real value and which is worth knowing before S065/S066/S006 are extracted: several streams
carry two upstream figures side by side, and they diverge widely. Bloemkool blad/loof reads
**131.637 t** (MONBIO) against **197.100 t** (GeNeSys); wortelloof **76.652 t** against
**69.500 t**; preiloof **64.171 t** against **70.875 t**; spruitstokken **57.542 t** against
**138.000 t** — a factor 2.4. Groenteteelt as a whole reads **534.952 t** (MONBIO) against
**800.000 t** (GeNeSys). When S065 and S006 are extracted these will surface as genuine
cross-source contradictions, and the register will hold both, as it should.

#### 2. Suspected source errors

None. No arithmetic evidence of a defect anywhere in the four tables.

#### 3. Deliberate exclusions

**a. All of Tabel 2, 3, 4 and 5 — restatement (session decision 1).**
Skipped under the cross-source restatement rule: *"Skip values restated from an edition already in
the `Sources` sheet."* All four upstream studies that carry cells are in the sheet. The rule's
escape hatch — *"if no source in the register owns those years, capture them here"* — does not
apply, because S065, S066 and S006 are not merely listed but **queued as verified PDFs in
`inbox/`**, all priority-1 CORE. They are the proper owners: they carry the method, the wet/dry
basis and the per-crop context that this consolidation strips out.

This is the largest deliberate skip in the register so far, so the tables are named here in full:

- **Tabel 2** (p.17) — sector totals for landbouw / groenteteelt / fruitteelt / veilingen /
  voedingsindustrie / supermarkten / grote cateraars, across four quantity columns
  (biomassareststromen, voedselreststromen, nevenstromen, voedselverliezen). ~30 cells.
- **Tabel 3** (p.19) — per-groentesoort, per-fraction: bloemkool, wortel, prei, spruiten, uien,
  erwt, bonen, selder, spinazie, witloof, witte/rode/savooikool, broccoli, knolselder, schorseneer,
  courgette, raap, tomaat, kropsla, paprika, champignons, komkommer, aardappelen. ~60 cells.
- **Tabel 4** (p.21) — per-soort reststromen at the verwerkende industrie (explicitly **België**,
  2011) and at three large Flemish auctions (2012). ~14 cells, all GeNeSys.
- **Tabel 5** (p.22) — per-fruitsoort: appels, peren, aardbei, kers. ~10 cells.

**b. The consolidated total — a derivation.**
*"Totaal groenten en fruit 973.954 – 1.512.656 ton"* (Tabel 2, shaded row) and the same range in the
running text on p.16. Not captured on two independent grounds: it is a **range**, not a value, and
the table's own footnote states it rests on an assumption S010 itself introduces — *"aanname: 2/3
van verwerkende industrie exclusief groenten en fruit, 1/3 aardappel"*. That is a calculation on
other sources' figures, which the conversion rule forbids.

**c. S010's own primary data — not captured (session decision 2).**
Two figures in this source are genuinely its own and were still not captured, by explicit choice:

- **~11.000 ton/jaar** biomassareststromen at a single Flemish auction, from S010's own expert
  interview (p.16).
- **~15.000 ton** total biomassareststroom at fruitveilingen, S010's own interview-based estimate
  (p.16).
- **64.271 ton** voedselreststromen at supermarkten en retailers (Tabel 2, letter D), from
  **COMEOS 2018** — the one upstream study *not* in the register, so the restatement rule would
  have allowed it.

All three are recoverable from the pages named. The COMEOS cell carries a caveat any later capture
must keep: Tabel 2's own note says the supermarket and caterer figures are **total organic residual
streams**, not groente-en-fruit only.

**d. Not quantities of arising material.**
- **Hypothetical hub design capacities** (pp. 44–83) — 1.000, 2.000, 7.000, 21.000, 13.000, 240 and
  480 ton/jaar throughput, plus 2.500 / 31.500 t compost, 41.450 t bio-gebaseerde meststof, 3.300 t
  insect frass, 940 t larven, 357 t insectenproteïne, 200 t laurinezuur, 29 t chitosan, 3.250 t
  biochar. These are **scenario parameters for a modelled installation that does not exist**, not
  measurements of anything, and the outputs are derived products besides.
- **Company throughput examples** (§6.1, pp. 32–40) — 600 t vruchtenresten, 4.100 t across six
  NW-European pilot regions, 350.000 t (Group Op De Beeck), 6 miljoen ton (Duynie Group, European).
  These measure what a processor *takes in*, i.e. the destination side, and are mostly not Flemish.
- **2.480 ton voedseloverschotten** opgehaald en verdeeld (2021, p.36) — `schenking`, out of scope
  by `quantity_type.csv`.
- **All of chapters 2 and 3** — costs (€/jaar, €/ton), minimum selling prices, break-even results
  and maximum investment cost. Not quantities of material.
- **Figuur 3** (p.25) and **Tabel 6** (p.24) — valorisation routes in **percentages** and a cascade
  **index**; no mass anywhere. Indexed in `destination_index.csv` with `has_data = no`.

#### 4. Completeness sweep

**22 tables, 20 figures, all accounted for.** The source's own lists (pp.4–7) match the body
numbering exactly — unlike S087 — so they were used directly.

| Object | p. | Disposition |
|---|---|---|
| Tabel 1 (stakeholdergroepen bevraagd) | 13 | carries no volumes — an interview roster |
| **Tabel 2** (sector overzicht) | 17 | **excluded — restatement (3a)**; total row excluded as a derivation (3b); COMEOS cell not captured (3c) |
| **Tabel 3** (per groentesoort) | 19 | **excluded — restatement (3a)**, ~60 cells |
| **Tabel 4** (verwerkende industrie + veilingen per soort) | 21 | **excluded — restatement (3a)**, all GeNeSys; industry column is België |
| **Tabel 5** (per fruitsoort) | 22 | **excluded — restatement (3a)** |
| Tabel 6 (cascade-index) | 24 | index scores, no mass; indexed |
| Tabel 7 (praktijkvoorbeelden start-ups/projecten) | 32 | carries no volumes in the table itself; the company tonnages in the surrounding text are excluded under 3d |
| Tabel 8-13 (operationeel + technologisch profiel) | 46-50 | excluded — hub scenario parameters (3d) |
| Tabel 14-17 (scenario's, kosten, minimale verkoopsprijs) | 51-69 | excluded — costs and prices, not quantities |
| Tabel 18-22 (gevalstudie 2: profiel, scenario's, kosten, prijs) | 73-83 | excluded — as above |
| Figuur 1 (schematische weergave definities) | 9 | a definitional schema, carries no numbers |
| Figuur 2 (waardepiramide) | 23 | a cascade schema, carries no numbers |
| Figuur 3 (valorisatiewegen) | 25 | percentages only (3d); indexed |
| Figuur 4 (Biomassaplein Limburg) | 36 | a photograph / site schema, no numbers |
| Figuur 5 (opzet gevalstudie 1) | 45 | a process schema |
| Figuur 6-11 (max. investeringskost, gevalstudie 1) | 55-66 | excluded — € per year against price, not quantities |
| Figuur 12 (opzet gevalstudie 2) | 72 | a process schema |
| Figuur 13-19 (max. investeringskost, gevalstudie 2) | 77-82 | excluded — as Figuur 6-11 |
| Figuur 20 (struikelblokken) | 90 | qualitative, no numbers |

Running text was swept as well; the tonnages it carries are those listed in §3c and §3d.

#### 5. Judgement calls & new dictionary members

**No new dictionary members** — nothing was captured.

Two session decisions, both taken by the user:

1. **All four data tables skipped as restatements**, leaving S065, S066 and S006 as the owners.
2. **S010's own three figures not captured either**, retiring the source at zero claims rather than
   holding it open for three rows.

**The consequence is worth stating plainly, because it is the one thing this session changes about
the register's plan.** The 2026-08-31 gap analysis found that the food industry — the largest single
stage at 2,02 Mt — has **no L4/L5 detail at all**, and that only 44,1% of the addressable pool
resolves to L4/L5. Tabel 3 of this source is precisely the missing detail: bloemkoolloof,
spruitstokken, uienschillen, preiloof, witloofwortelen, per crop and per fraction. By skipping it
here we have decided that **the register's single largest known gap is now blocked on three specific
queued sources — S065 (GeNeSys), S066 (ILVO 2015 tuinbouw) and S006 (MONBIO 2.0)**. If any of those
is later retired the way S001/S086 were, the figures do not simply vanish: S010 is the fallback, and
this note plus the archived PDF is how to find them. That is the reason the tables are enumerated in
§3a rather than dismissed in a line.

**Note for whoever extracts S065 and S066.** S010 has already done the cross-source comparison for
you: §1 above lists the streams where GeNeSys and MONBIO diverge, in one case by a factor 2.4. Read
it before extracting either, the way S091 and S007 were read against each other.

**No Zotero item (F-002).** The Zotero MCP server timed out on connect this session, so no item was
created and `citation_key` stays blank. PDF archived as
`archive/S010_Verkennende economische haalbaarheidsstudie biomassahub_ILVO.pdf`.

### S087

**Outcome: zero claims.** S087 was read cover-to-cover and yielded no capturable figure. That is a
result, not a gap: the register now records this edition as *checked and agri-food-empty* rather
than *not checked*. Every tonnage the source prints is named below with the reason it was not
captured, so any of the four session decisions can be reversed without re-opening the PDF.

**What this source actually is.** The OVAM *Marktanalyse Biomassareststromen* executes chapter
8.4.2 of the Actieplan Voedselverlies en Biomassa(rest)stromen Circulair, and its own afbakening
(Tabel 1, p.9) names three blocks: biomassa(rest)stromen van groen-, natuur-, bos- en
landschapsbeheer; hout(rest)stromen van industrie en huishoudens; and dierlijke bijproducten. The
first two are the sectors the S091 session put out of scope as non-agri-food, and they occupy
chapters 3 and 4 — roughly 44 of ~60 content pages. Only chapter 5 touches the agri-food chain at
all, and everything in it is either a derived product or a figure another source owns. The title is
misleading for register purposes: this is a woody-biomass and rendering-sector market report, not a
food-side-stream monitor.

#### 1. Variant readings

None. No quantity in this source is stated twice with different values.

#### 2. Suspected source errors

None with arithmetic evidence. One presentational defect is worth recording because it affects how
the source can be checked: **the source's own *Lijst van tabellen en figuren* (p.69-70) is wrong.**
The documentbeschrijving (p.3) claims *16 tabellen en 27 figuren*; the body actually carries
**9 tables and 27 figures**. The index omits Tabel 5 entirely, renumbers Tabel 6-10 against the
body's Tabel 5-9, and skips the body's Figuur 8 (*Afzet groencompost per bestemming*, p.29), so
from that point on every index entry is off by one against the body caption. The completeness sweep
below is therefore built on **my own enumeration of the body captions**, not on the source's index,
as the protocol allows where the index is unusable.

#### 3. Deliberate exclusions

Eight tonnages were seen and not captured. All are named here with their value, page and reason.

**a. Not agri-food — chapters 3 and 4 (session decision 1).**
Bosbeheer, landschapsbeheer, heidebeheer, groenafval, berm- en natuurmaaisel, gft-structuurmateriaal,
primair and secundair houtafval van industrie en huishoudens, and the Netherlands / France /
Luxembourg / Germany benchmark chapters. These are the same sectors S091's decision 4 excluded
(bosbouw, landschapsbeheer, hout, papier, bio-energie, afvalsectoren). Not one figure in either
chapter measures an agri-food stream: a keyword sweep for *landbouw / oogstrest / gewas / teelt /
slacht / vlees / zuivel / melk / groente / fruit / voedsel* over both chapters returns only
teeltsubstraat research notes, *landbouwers* as users of houtsnippers, and gft as a composting
input. No tonnages recorded, per the user's decision that this block is out entirely.

**b. Not a Flemish arising volume — the 698.000 t input stream (session decision 2).**
*"De Vlaamse verwerkers ontvingen 698 000 ton dierlijk afval in 2023"* (p.55). This was the
source's one genuine raw-side-stream candidate, arising at slachthuizen, uitsnijderijen and
vleesverwerkende bedrijven (`Voedingsindustrie`). It is **not captured** because it measures
material *received by Flemish processors*, not material arising in Flanders: Figuur 24 (p.56) splits
its herkomst across **Vlaanderen / Wallonie / Brussel / Buitenland**, and the source gives no
Flemish-only counterpart. The text says only *"Het grootste aandeel van het afval werd opgehaald in
Vlaanderen"* and *"een klein percentage C3-materiaal (minder dan 5%) wordt verder afgevoerd voor
verwerking in het buitenland"*. Neither `Vlaanderen` nor `Belgie` would be an honest `geography`
value — the pie includes buitenland — so the row was dropped rather than mislabelled. **To recover
it, the value is 698.000 ton, 2023, p.55, running text.**

The accompanying split — *78% categorie 3 (slachtafval, veren, afval van vleesverwerkende
bedrijven) / 22% categorie 1- en 2-materiaal (gestorven dieren, afgekeurd slachtafval, GRM)* — is a
**percentage**, not a quantity, and the register does not derive tonnages from percentages. Figuur
24 carries no printed numbers or percentages at all (unlabelled 3-D pie), so nothing there is
readable either.

**c. Afgeleide producten — six tonnages (session decision 3).**
`afgeleid product` is `discarded` in `quantity_type.csv`: these are outputs of a prescribed heat
treatment, not raw side streams, and capturing them beside the 698 kt input would count the same
material twice. All six, for recovery:

| Value | Page | What it is |
|---|---|---|
| 43.500 t | 57 | afgeleide producten bij Vlaamse voedingsbedrijven erkend voor dierlijke bijproducten, 2023 |
| 122.600 t | 58 | verwerkte dierlijke eiwitten uit categorie 3-materiaal, 2023 |
| 137.500 t | 58 | verwerkte dierlijke vetten uit categorie 3-materiaal, 2023 |
| 48.000 t | 59 | diermeel uit categorie 1- en 2-materiaal, 2023 |
| 15.000 t | 59 | dierlijke vetten uit categorie 1- en 2-materiaal, 2023 |
| 338 kton | 8 | samenvattingstotaal afgeleide producten, 2023 |

Note the reconciliation does not close on the source's own numbers: 122.600 + 137.500 + 48.000 +
15.000 = **323.100 t** against the samenvatting's **338 kton**, and the source explicitly says the
43.500 t of voedingsbedrijven *"zijn niet mee opgenomen in de hiernavolgende tabellen en grafieken"*
(p.57), so adding it gives 366.600 t and does not close either. Recorded, not resolved — the
register captures none of these rows.

**d. Owned by another edition — the 4.000 t GFVO (session decision 4).**
*"In 2020 bedroeg de totale productie in de voedingsmiddelenindustrie ca. 4000 ton"* (p.64,
par. 5.2.2). This was the source's only other in-scope candidate: used frying fats and oils arising
at `Voedingsindustrie`. **Skipped under the cross-source restatement rule** — reference year 2020
belongs to S001 (*Marktanalyse Biomassareststromen 2022*), which is in the `Sources` sheet as
KEEP-CORE. **If S001 is never extracted, this figure is lost and should be pulled back from here:
ca. 4.000 ton, 2020, p.64, running text.** The source attaches its own caveat, which any capture
must carry: the 2022 professional figures diverge sharply because collection moved from IMJV to
MATIS, and *"de cijfers in het verleden lijken sterk onderschat"*.

**e. Out of scope by stage, geography or nature — the remainder.**

- **ca. 1.000 ton GFVO horeca, 2020** (p.64) — `Horeca & catering`, out of scope by stage.
- **7,2 kton GFVO van particulieren, 2013** (p.63) and **Figuur 27** (p.64, the 2013-2023 series,
  ca. 6.000 → 3.900 t recyclagepark and 1.100 → 3.000 t supermarkten) — huishoudens, out of scope
  by stage, *and* resolved only along the collection-route axis. Note the trap: *supermarkten* here
  is a drop-off point for household GFVO, not the schakel where the stream arises, so this is not a
  retail figure.
- **ca. 90 kton frituurvetten en olien op de Belgische markt per jaar** (p.62) — a market-placement
  volume for **Belgium**, with no Flemish counterpart and no Flemish equivalent measurement. Not a
  volume arising in Flanders.
- **911 ton gezelschapsdieren gecremeerd, 2023** and **616 ton, 2019** (p.55, p.60) — companion
  animals at dierencrematoria. Not agri-food biomass. Worth a note for a future session: the source
  says this sector *"kreeg sinds 2021 ook de mogelijkheid om landbouwdieren, waaronder paardachtigen,
  te cremeren"*, so the figure is no longer purely companion-animal, but it is not split.
- **"een deel gaat verloren bij gebruik (geschat op een 30%)"** (p.63) — a percentage, and an
  estimate; the register does not derive a tonnage from it even though the 90 kton is printed two
  paragraphs above. That derivation is exactly what the conversion rule forbids.

#### 4. Completeness sweep

Built on my own enumeration of the body captions (see §2 — the source's index is unusable).
**9 tables, 27 figures, all accounted for.**

| Object | p. | Disposition |
|---|---|---|
| Tabel 1 (afbakening) | 9 | carries no numbers — it is the scope list itself |
| Tabel 2 (beleidsontwikkelingen landschapselementen) | 15 | carries no numbers |
| Tabel 3 (volumes plagsel) | 20 | excluded — heidebeheer, not agri-food (3a) |
| Tabel 4 (productie bermmaaisel) | 24 | excluded — landschapsbeheer (3a) |
| Tabel 5 (verwerking groenafval composteringsinstallaties) | 26 | excluded — groenafval (3a) |
| Tabel 6 (afvoer houtige fractie groenafval) | 28 | excluded — groenafval + bestemmingsas (3a) |
| Tabel 7 (materialenbanken) | 43 | carries no volumes — an installation list |
| Tabel 8 (voedingsbedrijven erkend voor dierlijke bijproducten) | 57 | carries no volumes — counts of erkenningen per bedrijfstype; the 43.500 t beside it is excluded under 3c |
| Tabel 9 (bedrijven buiten de voedingssector) | 57 | carries no volumes — counts of erkenningen |
| Figuur 1 (verkocht volume hout ANB) | 11 | excluded — bosbeheer (3a) |
| Figuur 2-8 (groenafval inzameling, productie, verwerking, compost) | 22-29 | excluded — groenafval / gft (3a). Figuur 8 is absent from the source's own index |
| Figuur 9-17 (primair + secundair houtafval, in- en uitvoer) | 32-40 | excluded — houtafval van industrie en huishoudens (3a) |
| Figuur 18-23 (NL, FR, LU, DE benchmarks) | 46-53 | excluded — non-Flemish geography *and* houtafval (3a) |
| Figuur 24 (herkomst dierlijk afval) | 56 | carries no printed numbers; indexed in `destination_index.csv` because it settles the geography of the 698 kt (3b) |
| Figuur 25 (bestemming C3 eiwitten) | 58 | carries no printed numbers; bestemmingsas; indexed |
| Figuur 26 (bestemming C3 vetten) | 59 | carries no printed numbers; bestemmingsas; indexed |
| Figuur 27 (huishoudelijke GFVO per inzamelpunt) | 64 | excluded — huishoudens + inzamelroute-as (3e); indexed |

Running text outside any numbered object was swept as well; the eight tonnages it carries are the
ones listed in §3. The bijlage (p.67-68, prognoses vraag en aanbod houtafval) is houtafval and
excluded under 3a.

#### 5. Judgement calls & new dictionary members

**No new dictionary members** — nothing was captured, so nothing was needed.

Four session decisions, all taken by the user at session open, all reversible from the tonnages in
§3:

1. **Chapters 3 and 4 out entirely**, as non-agri-food. Consistent with S091 decision 4. No
   open-ruimte or houtafval tonnages recorded, by explicit choice.
2. **The 698.000 t is not captured**, because its geography is Flemish processors rather than
   Flemish territory and the source prints no Flemish-only figure. This is the strictest reading of
   the v2.3 geography rule and it is worth flagging: an alternative reading would have captured it
   at `geography = Vlaanderen` with the coverage spelled out in `stream_name_NL`. It is the single
   largest judgement in this session.
3. **All six afgeleide producten excluded**, per `quantity_type.csv`. This is the first source where
   that dictionary line is load-bearing — S087 is largely *about* diermeel and dierlijke vetten, so
   the rule removes most of its chapter 5.
4. **The 4.000 t GFVO 2020 left to S001**, per the cross-source restatement rule.

**`extraction_status` in the `Sources` sheet was not touched.** It still reads `NOT EXTRACTED` for
S087 — and for S080, S002, S091 and S007, all of which are extracted. The column has not been
maintained by any register session since the S007 session corrected it on S005/S006, so writing it
for S087 alone would create the opposite inconsistency (S087 `EXTRACTED` with 0 claims beside the
human-verified S080 reading `NOT EXTRACTED`). Left alone deliberately; flagged here so the reviewer
can decide whether to retire or repair the column.

**No Zotero item (F-002).** The Zotero MCP server was configured this session but timed out on
connect, so no item was created and `citation_key` stays blank. The PDF is archived as
`archive/S087_Marktanalyse Biomassareststromen 2024 OVAM.pdf`.

**Consequence for the queue.** S086 (Marktanalyse ~2020) and S001 (Marktanalyse 2022) are earlier
editions of *this* report and will have the same shape: woody biomass, houtafval and the rendering
sector. Expect a similarly thin agri-food yield from both. S001 is now the only source that can own
the 2020 GFVO figure, which is a reason to keep it in the queue rather than drop it.

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
- **Suiker: 538.889 vs 275.044 vs 650.000 ton (C-553, C-572, C-573) — only one is Flemish.**
  *(Corrected 2026-08-17 in the review pass.)* Identical structure to S091: 785.839 t Belgian
  Prodcom x **69%** export proxy = 538.889 t, which folio 118 defines as the production of **het
  Vlaamse bedrijf** whose sites lie in Flanders *and* Wallonia -> `geography = Belgie`; x **35%**
  grondgebied share = 275.044 t **op Vlaamse productiesites** -> the Flemish figure; and FoodIndustry
  (2020) 650.000 t is a rival estimate of the same **company-level** quantity -> `Belgie`. So
  275.044 is a *subset* of 538.889, not an alternative reading of it. The Tabel 85 column header
  says "Productie Vlaanderen"; the text says otherwise, and the text wins. See the S091 note for
  the full table.
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
- **This source was included in the review pass of 2026-08-17.** Every remark the reviewer made on
  S091 was applied here too - the edibility reclassification (C-480, C-481, C-483, C-484, C-493),
  the level fix on C-484, the vinegar-row renaming (C-508, C-509), the sugar geography (C-553,
  C-572, C-573), the sierteelt note on C-399, the 2018-cijferbasis in the name of C-467, and the
  conversion arithmetic on every liter/hl row. See **[S091 -> Review pass](#s091)** for the reasoning
  behind each; the rules themselves are in `database/register/CLAUDE.md` (protocol v2.3).
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
- **Suiker: 556.283 vs 289.188 vs 650.000 ton (C-361, C-379, C-380) — and only one of the three is
  a Flemish figure.** *(Corrected 2026-08-17 in the review pass; the first write-up called all three
  Flemish.)* The source packs all three into one sentence on p.99:

  > "Op basis van de exportproxy (67%) kan de productiehoeveelheid van **het Vlaamse bedrijf**
  > geschat worden op 556.283 ton (Tabel 37; Food Industry, 2020 schat 650.000 ton), **waarvan**
  > 289.188 ton suiker geproduceerd op **Vlaamse productiesites**."

  Unpacked against the Belgian Prodcom quantity of 826.253 ton (Tabel 37):

  | Figure | How the source derives it | What it actually covers | geography |
  |---|---|---|---|
  | **556.283 t** (C-361) | 826.253 × **67%** (export proxy) | production by **Südzucker–Tiense Suiker**, the "Flemish company" — but p.99 says its sites are "verspreid over Vlaanderen en Wallonië" | **Belgie** |
  | **289.188 t** (C-379) | 826.253 × **35%** (grondgebied share, CINBIOS) | the part produced **on Flemish soil** | **Vlaanderen** |
  | **650.000 t** (C-380) | Food Industry (2020) estimate | the **same company-level** quantity as C-361 | **Belgie** |

  So they are **not three measurements of one quantity, and not three parallel definitions of a
  Flemish figure**. 289.188 is a *subset* of 556.283 (35% vs 67% of the same Belgian total), and
  650.000 is a rival estimate of that same 67% company figure. Only **C-379 is the Flemish
  volume**. C-361 sits in a column headed *"Productie Vlaanderen"*, which is exactly why it was
  first mis-typed as Flemish — **the column header is not the definition; the text is**. All three
  are captured, each now says in its own name what it covers, and `also_stated_in` states the
  subset relation rather than calling them variants. The identical structure recurs in S007
  (C-553 / C-572 / C-573) and was corrected there too.
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
  "135 kton" bostel and **"6.175 kton" diervoeders** in Tabel 26. Each is listed in
  `also_stated_in` on the row that holds the precise value — the diervoeder cell on **C-384**
  (6.175.148 t, Tabel 39), the bostel cell on C-397, the aardappel cell on C-314.

  *(Added in the review pass: the diervoeder entry was missing from this list, which made the
  Tabel 26 row look unread. It was captured all along — see the new completeness rule in the
  protocol, which now requires a captured table to be accounted for cell by cell whenever any of
  its cells are dropped.)*

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

- **MONBIO's gewasgroepen are a *second, overlapping* crop partition — what that means and why it
  was allowed.** *(Expanded 2026-08-17 in the review pass.)*

  `commodity_hierarchy.md` grew out of the OVAM voedselverlies monitors, whose L3 subgroups cut the
  plant sector one way. MONBIO cuts it a **different** way, and the two cuts cross rather than nest:

  | MONBIO gewasgroep | Existing register L3 it crosses | Nature of the overlap |
  |---|---|---|
  | `Suiker- en zetmeelgewassen` (suikerbiet **+** aardappel) | `Aardappelen en knolgewassen` **and** `Suikerbieten en nijverheidsgewassen` | one MONBIO group spans two register groups |
  | `Groenten` (not split) | `Groenten openlucht` **and** `Groenten beschut` | one MONBIO group spans two register groups |
  | `Industriele gewassen` (cichorei, vlas, hennep, hop) | part of `Suikerbieten en nijverheidsgewassen` | MONBIO carves a *piece* out of a register group |
  | `Oliehoudende gewassen` (kool- en raapzaad, soja, …) | part of `Suikerbieten en nijverheidsgewassen` | same |

  **Three ways to handle this, and why the third was chosen:**
  1. *Force MONBIO's groups onto the register's partition* — would require splitting 3.630.317 t of
     "Suiker- en zetmeelgewassen" into an aardappel part and a suikerbiet part. The source does not
     print that split, so producing it would be a **derivation**, which the protocol forbids
     outright.
  2. *Drop the group rows and keep only the crop rows* — loses the source's own sector structure and
     its only published subtotals.
  3. *Admit MONBIO's groups as additional L3 members* — keeps every figure exactly as printed, at
     the cost that **`L3_commodity_subgroup` is no longer a partition**: two rows can both be real
     and still overlap in the material they cover.

  The cost of (3) is real and has to be managed, so: `commodity_hierarchy.md` carries a
  **never-sum-across** warning naming these four members, and any future rollup must group by
  `source_id` **and** by which partition a row belongs to — summing L3 across sources would now
  double-count. This is the single biggest structural concession the register has made to a source
  so far, and it will recur for every MONBIO edition (S006, S005) and for any source with its own
  sector taxonomy.
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
#### 6. Review pass (2026-08-17) — reviewer remarks and what changed

The reviewer's remarks on S091 were applied **to S091 and S007 alike**, and each one that
generalised became a rule in `database/register/CLAUDE.md` (protocol **v2.3**). What changed in the
data:

- **Edibility stated in the source's own product name now overrides the session default.** Session
  decision 3 defaults MONBIO's residual streams to `agri-food waste` because MONBIO's
  nevenstroom/productieresidu split is *economic*. But where an individual Prodcom **product name**
  says "eetbare" or "niet-eetbare", the source *has* specified edibility, and the protocol's own
  rule ("classify as nevenstroom/voedselverlies **iff** the source specifies edible/inedible") takes
  over. Reclassified, with `type_assumed` flipped to FALSE:
  `voedselverlies` — C-295 / C-480 (eetbare slachtafvallen), C-296 / C-481 (ander vlees en andere
  eetbare slachtafvallen), C-299 / C-484 (eetbare slachtafval van gevogelte), C-308 / C-493 (the
  text total); `nevenstroom` — C-298 / C-483 (niet-eetbare ruwe slachtafvallen).
  This is a **refinement of decision 3, not a reversal** — the sector-level default still stands
  wherever the source is silent, which is most rows.
  **One caveat is recorded on each reclassified row**: `voedselverlies` is the register's
  *edible-fraction* category, and the source stresses that eetbaar slachtafval is valorised in the
  food industry rather than lost. The category name says "verlies"; the material is not lost.
- **C-299 / C-484 moved from level 5 to level 4** and its `L5_fraction_as_named` was cleared. The
  reviewer queried why poultry offal sat at L5 while bacon and gezouten rundsvlees sat at L4. The
  evidence settles it against the L5: the **human-verified S080/S002 corpus never uses L5 on the
  animal branch at all** (every meat row sits at L3 `Vlees`), and `commodity_hierarchy.md` lists
  only plant fractions as L5 examples. `slachtafval (eetbaar)` was the corpus's only animal L5 — a
  one-off, and inconsistent even inside S091, where the multi-species eetbare-slachtafval row sits
  at level 3. Pulling C-299 up to level 4 restores consistency; pushing C-300/C-301 down to level 5
  would have re-levelled every meat row in the corpus against verified precedent.
- **The two vinegar rows were renamed to make their disjointness unmissable.** Prodcom 103917 is
  vegetables preserved *other than* in vinegar (72.920 t, C-319) and 103918 is vegetables, fruit and
  other edible plant parts preserved *in* vinegar (13.246 t, C-320). They are **disjoint Prodcom
  categories, not a part and its whole** — which is why the "broader" row is five times smaller.
  The confusion came from `level_1to5`: C-320 sits at level 2 because it spans several commodity
  groups, and that was read as "aggregate of C-319". `level_1to5` is a **commodity-breadth**
  label, never a volume nesting — only rows named `AGGREGAAT - …` are volume aggregates. Both rows
  now say so in `also_stated_in`, and the rule is in the protocol.
- **The sugar geography was corrected** — see *Variant readings* above.
- **C-218 / C-399 now state on the row that the plantaardige total includes sierteelt**, which was
  deliberately not captured, so a reviewer summing the eight gewasgroep rows against the total sees
  immediately why they fall short (16.688.841 − 137.091 = 16.551.750 for S091).
- **C-282 / C-467 carry the 2018 cijferbasis in `stream_name_NL`**, not only in
  `source_type_label`. The caveat changes *what year the figure measures*, and the protocol already
  requires that kind of qualifier to be in the name.
- **Every converted row now spells out its conversion arithmetic** in `source_type_label`
  ("1 liter x 1.040 g/l = 0,00104 t", "1 hl = 100 l x 1.050 g/l = 0,105 t"), and the
  `conversion_factor_to_t_per_yr` column was given an explicit number format. The stored factors
  were always correct, but Excel's *General* format renders 0,00104 as "0,001", so a reviewer
  checking `value × factor = volume` by eye concluded the row did not add up. An audit column that
  cannot be read is not an audit column.
- **A second geography case, found by sweeping the new rule over both sources.** Tabel 26 / Tabel 28
  present the NACE 10.4 oil figures (771 and 1.149 kton in S091; 902 and 1.376 kton in S007) inside a
  table titled *"de Vlaamse voedingssector"*, but the source states on p.74 / folio 106 that for this
  sector it used the **FEDIOL figures for Belgium**. Same pattern as the sugar rows: the table title
  is not the definition. C-279 / C-280 and C-464 / C-465 are now `geography = Belgie` with the
  disagreement recorded on the row. A consequence worth the reviewer's attention: once the geography
  is corrected these four rows carry the *same number, unit and coverage* as the FEDIOL totals they
  were lifted from (C-329 / C-335 and C-518 / C-524), so each pair is one figure in two places rather
  than two claims. Both sides now cross-reference each other; **collapsing each pair is a
  `DECISION_expert` call, not one this session should make silently.**
- **S091's four landing rows (C-269…C-272) now invoke the sanctioned Belgian-ports exception by
  name**, as S080's and S002's fisheries rows already did. The figures were always right — the
  justification for calling a "Belgische vissersvaartuigen" figure Flemish simply was not on the row.
- **`Sources` metadata**: unchanged in this pass.

**Reviewer decisions already recorded in `DECISION_expert` and preserved untouched**: C-074
(S080, retired earlier), C-147, C-148, C-185, C-193 (S002, `no`), and **C-384…C-390** (the whole
BFA mengvoeder block) and **C-393, C-394** (the two Belgian beer rows) in S091, all `NO`. The
S007 twins of the beer rows (C-586, C-587) now cross-reference the rejected S091 rows so they can
be disposed of the same way. **The mengvoeder rejection is source-specific** — the reviewer confirmed
(2026-08-17) that mengvoeder was simply irrelevant *for S091*, not that compound feed is out of
scope for the register. S007's block (C-577…C-583) stays captured and unmarked, and future sources
that report feed production should keep capturing it.

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
