"""Promote register rows that are TOTALS of other rows to `AGGREGAAT - ` rows.

Protocol v2.4 made the `AGGREGAAT - ` name prefix load-bearing: it decides whether a row sums
with its siblings or becomes the total they are checked against. Rows extracted before v2.4
predate that rule, and a sector total sitting in the register as an ordinary component is added
to its own parts - which is why coverage ran to 132% for akkerbouw and 165% for the primary
stage.

Two kinds of row are promoted:

  * NAME EVIDENCE - the source itself calls the row a total ("Voedselreststromen akkerbouw
    totaal", "... (totaal)"). A row that says it is a total, is one.
  * ARITHMETIC EVIDENCE - the row equals the sum of its siblings in the same source, commodity
    path and quantity type (C-043 = C-005 + C-042). Listed explicitly below so each can be
    checked against the archived PDF.

Rows are NOT promoted on wording like "incl. ..." alone: "Voedselverliezen aardappelen (incl.
niet-geoogste aardappelen)" is the only voedselverlies figure for that node, so it is a reading,
not a total.

Nor are they promoted when the row is a QUANTITY-TYPE total rather than a commodity one. The
vocabulary defines `agri-food waste = nevenstroom + voedselverlies`, so an agri-food-waste row
always equals its own split - that is the definition, not evidence of aggregation, and the
protocol says all three are captured as different quantity types that never sum across each
other. Promoting such a row turns a claim into a denominator on the strength of one word in the
source's label: OVAM 2020 wrote "(totaal)" after suikerbieten, melk and eieren while the 2023
edition wrote nothing, and the identical construct was treated two different ways.

The distinction that matters is whether the row also has SAME-quantity-type siblings it could be
totalling. C-043 (Aardappel 2023) decomposes both ways - 429.871 voedselverlies + 118.434
nevenstroom, and 308.000 niet-geoogst + 240.305 excl. niet-geoogst - and the second pair are two
agri-food-waste components, so it is a genuine commodity total and stays promoted. C-154, C-157
and C-158 have no same-type siblings at all, so their only decomposition is across quantity
types and they are claims, not aggregates.

Reads and writes the `Streams` sheet BY COLUMN HEADER. Idempotent - a row already prefixed is
left alone. Writes the workbook last and reports if Excel holds it open.

    database/.venv/Scripts/python.exe database/register/promote_totals.py --dry-run
    database/.venv/Scripts/python.exe database/register/promote_totals.py
"""
import pathlib, re, sys
import openpyxl

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                      # register/ - HERE is register/tools/
WB = ROOT / "BIOLOOP_streams_and_sources.xlsx"
SHEET = "Streams"
DRY = "--dry-run" in sys.argv
PREFIX = "AGGREGAAT - "

# the source's own word for it
NAME_RE = re.compile(r"\btotaal\b", re.I)

# proven by arithmetic against siblings; see detect_totals in the session log
ARITHMETIC = {
    "C-043": "= C-005 (308.000 niet-geoogst) + C-042 (240.305 excl. niet-geoogst)",
}

# these look like totals by name but are NOT promoted - each is the only figure for its node
KEEP = {
    "C-057": "the only voedselverlies figure for Aardappel; 'incl.' names its scope, not a total",
}

# the columns that decide which rows are siblings of one another
GROUP_COLS = ("source_short", "reference_year", "L2_commodity_group", "L3_commodity_subgroup",
              "L4_ingredient", "L5_fraction_as_named", "chain_L2")
SPLIT = ("voedselverlies", "nevenstroom")


def _num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def is_quantity_type_total(rec, siblings):
    """True when `rec` is agri-food waste equal to its own voedselverlies+nevenstroom split AND
    has no same-quantity-type sibling it could instead be totalling.

    `siblings` is every row sharing GROUP_COLS with `rec`, including `rec` itself.
    """
    if (rec["quantity_type"] or "").strip().lower() != "agri-food waste":
        return None
    same_type = [s for s in siblings
                 if s is not rec and (s["quantity_type"] or "").strip().lower() == "agri-food waste"]
    if same_type:                       # a real commodity total - let the normal rules decide
        return None
    parts = {q: [s for s in siblings if (s["quantity_type"] or "").strip().lower() == q]
             for q in SPLIT}
    if not all(parts.values()):         # no split present, so nothing is being restated
        return None
    total = sum(_num(s["volume_t_per_yr"]) for q in SPLIT for s in parts[q])
    mine = _num(rec["volume_t_per_yr"])
    if abs(total - mine) > max(1.0, abs(mine) * 0.005):
        return None
    return ("quantity-type total, not a commodity one: %s = %s voedselverlies + %s nevenstroom, "
            "and it has no agri-food-waste sibling to total"
            % (format(int(mine), ",d").replace(",", "."),
               format(int(sum(_num(s["volume_t_per_yr"]) for s in parts["voedselverlies"])), ",d").replace(",", "."),
               format(int(sum(_num(s["volume_t_per_yr"]) for s in parts["nevenstroom"])), ",d").replace(",", ".")))


def main():
    if not WB.exists():
        sys.exit(f"missing {WB.name}")
    wb = openpyxl.load_workbook(WB)
    ws = wb[SHEET]
    col = {str(c.value).strip(): c.column for c in ws[1] if c.value}
    for need in ("claim_id", "stream_name_NL", "L1_role", "volume_t_per_yr",
                 "quantity_type") + GROUP_COLS:
        if need not in col:
            sys.exit(f"column '{need}' not found in {SHEET}")

    # read the sheet once, by header, so sibling lookups do not re-walk it
    recs = []
    for row in range(2, ws.max_row + 1):
        cid = ws.cell(row=row, column=col["claim_id"]).value
        if not cid:
            continue
        rec = {k: ws.cell(row=row, column=col[k]).value
               for k in set(GROUP_COLS) | {"quantity_type", "volume_t_per_yr", "L1_role",
                                           "stream_name_NL"}}
        rec["claim_id"] = str(cid).strip()
        rec["_row"] = row
        recs.append(rec)

    groups = {}
    for r in recs:
        groups.setdefault(tuple((r[k] or "") for k in GROUP_COLS), []).append(r)

    promoted, skipped = [], []
    for rec in recs:
        cid = rec["claim_id"]
        cell = ws.cell(row=rec["_row"], column=col["stream_name_NL"])
        name = "" if cell.value is None else str(cell.value).strip()
        if not name or name.upper().startswith("AGGREGAAT"):
            continue
        if cid in KEEP:
            skipped.append((cid, name, KEEP[cid]))
            continue
        why = None
        if cid in ARITHMETIC:
            why = "arithmetic: " + ARITHMETIC[cid]          # an explicit entry always wins
        elif NAME_RE.search(name):
            # only a row the name rule would otherwise promote is worth testing
            qt = is_quantity_type_total(rec, groups[tuple((rec[k] or "") for k in GROUP_COLS)])
            if qt:
                skipped.append((cid, name, qt))
                continue
            why = "the source calls it a total"
        if not why:
            continue
        cell.value = PREFIX + name
        promoted.append((cid, str(rec["L1_role"]), _num(rec["volume_t_per_yr"]), name, why))

    promoted.sort(key=lambda r: -r[2])
    print(f"promoting {len(promoted)} row(s) to AGGREGAAT:\n")
    for cid, role, vol, name, why in promoted:
        print(f"  {cid:7} {vol:>12,.0f}  {role:16} {name[:58]}")
        print(f"          -> {why}")
    if skipped:
        print("\ndeliberately NOT promoted:")
        for cid, name, why in skipped:
            print(f"  {cid:7} {name[:56]}\n          -> {why}")

    if DRY:
        print("\n--dry-run: workbook not written")
        return
    if not promoted:
        print("nothing to write")
        return
    try:
        wb.save(WB)
    except PermissionError:
        sys.exit(f"\nCannot write {WB.name} - it is open in Excel. Close it and run this again.")
    print(f"\nwrote {WB.name} — now re-run make_aggregate_coverage.py --refresh and build_overview.py")


if __name__ == "__main__":
    main()
