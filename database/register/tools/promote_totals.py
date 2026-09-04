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


def main():
    if not WB.exists():
        sys.exit(f"missing {WB.name}")
    wb = openpyxl.load_workbook(WB)
    ws = wb[SHEET]
    col = {str(c.value).strip(): c.column for c in ws[1] if c.value}
    for need in ("claim_id", "stream_name_NL", "L1_role", "volume_t_per_yr"):
        if need not in col:
            sys.exit(f"column '{need}' not found in {SHEET}")

    promoted, skipped = [], []
    for row in range(2, ws.max_row + 1):
        cid = ws.cell(row=row, column=col["claim_id"]).value
        if not cid:
            continue
        cid = str(cid).strip()
        cell = ws.cell(row=row, column=col["stream_name_NL"])
        name = "" if cell.value is None else str(cell.value).strip()
        role = ws.cell(row=row, column=col["L1_role"]).value
        vol = ws.cell(row=row, column=col["volume_t_per_yr"]).value
        if not name or name.upper().startswith("AGGREGAAT"):
            continue
        if cid in KEEP:
            skipped.append((cid, name, KEEP[cid]))
            continue
        why = None
        if cid in ARITHMETIC:
            why = "arithmetic: " + ARITHMETIC[cid]
        elif NAME_RE.search(name):
            why = "the source calls it a total"
        if not why:
            continue
        cell.value = PREFIX + name
        promoted.append((cid, str(role), float(vol or 0), name, why))

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
