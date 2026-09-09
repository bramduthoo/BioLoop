# `deliverables/` — the two shareable lists, and how they are made

Four files, all **regenerated from the workbook** and all gitignored. Nothing here is
hand-maintained; if a figure looks wrong, fix the corpus or the tool, never the output.

```
BIOLOOP_stream_selection_<date>.xlsx / .html    which streams BioMobi registers first
BIOLOOP_gap_list_<date>.xlsx      / .html       where the data claims mass we cannot select
```

## Regenerate

```bash
cd database/register
../.venv/Scripts/python tools/prep_data.py                       # workbook -> build/streams.json
node tools/select_streams.js 69 --json build/sel_raw.json        # the selection
node tools/make_gap_list.js     --json build/gaps_derived.json   # the gap list
../.venv/Scripts/python tools/make_deliverables.py build/sel_raw.json
```

`make_deliverables.py` is layout only — it computes no figure of its own.

---

## THE SELECTION — what it is and how it is built

**Question:** which streams carry the mass, so BioMobi registers them first?

1. **Unit.** One selectable stream = one **L4 commodity node**, keyed `L2 | L4`. L3 is dropped from
   the key because sources use different nomenclatures at that layer for the same thing. An L4's
   total already contains its L5 fractions, so every fraction is counted exactly once.
2. **Value.** `V(source, stream)` is the derived repTotal of that stream **inside one source's own
   derivation**.
3. **Rank.** `M(stream) = max over sources`. **Never a mean.** A source that does not report a
   stream has not measured it — absence is not zero — so averaging folds invented zeros into the
   rank and rewards a stream for being *ubiquitous* rather than *large*.
4. **Denominators.** Two, side by side: *pool* (the sum of a source's L4 nodes — the selectable
   ceiling) and *L1* (what that source claims exists). A source cannot be asked for depth it never
   published.

Current result: **7.301.257 t over 69 streams; 80% at 13, 90% at 20.**

Markers in the sheet: `[BE]` = a Belgian figure; **`[BE+VL]`** = the row adds a Flemish and a
Belgian figure, so the number is neither — the fractions beneath show which half is which.

---

## THE GAP LIST — what it is and how it is built

**Question — the mirror of the selection:** where does the data still claim mass arises that no
selectable stream accounts for?

```
gap(place) = asserted(place) − reached(place)
```

* **asserted** — the total a source reports at that place
* **reached** — the mass beneath it a selection could actually pick

Everything else is a rule that keeps that subtraction honest. **All five were learned by getting
them wrong first**; do not drop one without reading why it exists.

### 1. Reachability must follow the selection exactly

A node **at or below L4** sits inside a selectable stream and is **fully reached**. Above L4,
reached is the sum of the L4 nodes in its subtree.

> Score it any other way and every L5 fraction looks like a gap: *Maisstro* reads as 1,4 Mt
> unreachable while its parent *Mais* is the #1 selected stream.

### 2. Never sum nested places

`Reststroom` and `Reststroom > Varia > Dranken` overlap. Each row therefore carries only its **own**
gap — `gap(place) − Σ gap(children)` — so the rows are a decomposition, not a pile, and they add up
to the stage total by construction. The tool asserts that identity and complains if it breaks.

> This is bookkeeping for *display*, not a second measurement. The measurement is always
> `asserted − reached`, from totals in the workbook. Subtracting the children's gaps only stops a
> parent row from re-reporting a child row's tonnes when you read down the list.

### 3. Merge sources only within a school

Sources are grouped by **what they count as a residual**, never by their name:

| school | sources | counts |
|---|---|---|
| `voedselverlies` | OVAM 2020, OVAM 2023, **ILVO 239** | food-linked losses only |
| `productieresidu` | MONBIO 3.0, MONBIO 4.0, **GeNeSys** | everything that arises (straw, leaf, oogstresten) |

Within a school the largest reach wins — it is the same measurement twice. **Across schools,
never**: `state.md` (2026-09-01) records MONBIO at 5.499.135 t against OVAM's 2.583.633 t on the
same year, 2,1× apart by construction, so letting one cancel the other erases a real gap by
comparing two different things.

> Grouping by *name* instead put ILVO 239 and GeNeSys in singleton families, and OVAM's
> `Groenten openlucht` lump read as a 291.180 t gap even though ILVO 239 resolves it with 9 named
> L4 nodes. `log.md` had already settled the schools: *"OVAM 2020 (330.089) and ILVO 239 2015
> (282.821) agree within 17% on tuinbouw — ILVO 239 IS that monitor's agriculture chapter worked
> out"*, against *"GeNeSys (894.535) against ILVO 239 (282.821), 3,2×, same institute"*.

### 4. Compare like with like

Granularity is **(place × chain stage)**, so a primary-production residue is never credited against
a food-industry total. Both sides of every subtraction use the node's **folded total** (agri-food
waste, or its nevenstroom+voedselverlies split where that is all the source gives), so an *inedible*
fraction can never be credited against an *edible* total. A stage axis is also what stops the mass
that has no commodity at all — OVAM's food-industry and retail lumps — from becoming one blob.

**A row is flagged `HYBRIDE`** when its asserted figure and its reached figure come from *different*
sources. Such a number answers "what does nobody reach", but no single source supports it and the
two sides may differ in year and scope; the same-source gap is printed beside it.

### 5. An unplaceable row is never evidence

An aggregate that spans two parents or two levels is **unallocatable by design**: nothing is ever
measured against it, so its 0% describes the commodity ladder, not the data. `C-094` mixes an L4
(*Aardappel*) with two L3s (*Groenten*, *Fruit*) across two L2 groups. Such rows **never enter the
arithmetic** and appear only as labelled context — `structureel onplaatsbaar — context, geen
meting` — and are never summed.

> The registry says so on the rows themselves: *"unallocatable by design"*, *"the coverage % is a
> floor"*. Before reading any coverage figure as evidence, check whether that row was placeable.

---

## THE SECOND SCREENING — the unplaceable aggregates

Rule 5 keeps unplaceable rows out of the arithmetic, but they are often the only figure a source
publishes for a whole sector. So they get a **separate pass**, which asks the question the ladder
cannot:

> Take what the aggregate says it totals, **part by part**, and ask what the register holds for each
> part — wherever that part lives and from whichever source.

`tools/screen_unallocated.js` lists the parts and what matches them. **The verdict is a human
reading, not the script's output**, because it needs judgement the script cannot supply:

* **Interpret the name.** *"Suiker"* covers sugar production **and its by-products**, so bietenpulp
  belongs under it, not just melasse — that alone moved C-097 from "134.000 t missing" to
  "over-covered". *"Maalderijen"* pulls in zemelen and gries, which are filed under `Granen`.
* **Pick the right figure.** Right chain stage, right quantity type, and the residual rather than
  the product: MONBIO's potato rows are Prodcom *dried potato meal*, a product, not a residue.
* **Respect the schools.** A part covered only by the other school is *measured*, but it does not
  reduce this school's gap.

A finding enters the gap list only by **explicit reviewer decision**, as one of two kinds:

* **`nested`** — names part of a residual the list already counts. Adds detail, never tonnage.
* **`additive`** — mass no row carries, because the aggregate asserting it cannot be placed and its
  branch has no node at all. Adds to the total.

Both live in the `FINDINGS` table at the top of `tools/make_gap_list.js`, with the claim ids and the
reasoning, so the list stays complete without the arithmetic being bent to produce it.

---

## Reading the current gap list

**10 rows + 2 screened findings = 2.826.946 t/jaar**, threshold 50.000 t.

The largest item, and the shape of the whole problem: OVAM asserts **2.017.748 t** of food-industry
residual and only **127.215 t** of it is reachable. Of the 1.293.823 t that hangs on no commodity
branch, the biggest named piece is **aardappel-, groente- en fruitverwerking** — where potato
processing has no residual row in this school at all and **fruit processing has none in the entire
register**.

### Numbering

Gap rows are ordered by size and renumbered on every run. **The stable anchor is the claim id** in
the last column, which resolves in `streams_export.csv`. Screened findings keep fixed ids (`S1`,
`S2`, …) because they are reviewer decisions rather than derived rows.

> A previous hand-written gap list lived in `crosswalks/GAP_LIST.csv` with `G-01 … G-19` ids. It is
> **retired** (`migrations/GAP_LIST_retired_2026-09-09.csv`) and those G-numbers are no longer a
> reference — a gap list that is edited rather than derived silently preserves whatever the last
> edition happened to say.
