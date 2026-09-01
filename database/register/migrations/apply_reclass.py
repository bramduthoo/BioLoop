"""Apply the human-verified `Gemengd` -> `Varia` reclassification to the register workbook.

This is the gate the database workstream requires of every loader: it EXITS NON-ZERO, naming
every unreviewed row, while any `DECISION` in the crosswalk is blank. Nothing is written until
you have gone through crosswalks/varia_reclass.csv.

    DECISION = ok    apply the proposal on that row
    DECISION = skip  leave that claim exactly as it is
    (blank)          not reviewed -> this script refuses to run

It reads and writes the `Streams` sheet BY COLUMN HEADER, never by position, so a reviewer who
has rearranged the columns loses nothing. The workbook is written last, and if Excel is holding
the file open the script says so rather than half-applying. Idempotent: running it twice leaves
the same workbook.

    database/.venv/Scripts/python.exe database/register/apply_reclass.py            # apply
    database/.venv/Scripts/python.exe database/register/apply_reclass.py --dry-run  # report only
"""
import csv, io, pathlib, sys
import openpyxl

HERE = pathlib.Path(__file__).resolve().parent
WB = HERE / "BIOLOOP_streams_and_sources.xlsx"
CROSSWALK = HERE / "crosswalks" / "varia_reclass.csv"
EXPORT = HERE / "streams_export.csv"
SHEET = "Streams"
DRY = "--dry-run" in sys.argv

# The reviewer works in Excel and writes plain words, so accept the obvious synonyms rather
# than make a correct decision fail on its spelling. `0` means "deferred, decide later" and is
# deliberately NOT accepted - it must block, like a blank.
APPLY = {"ok", "yes", "ja", "j", "include", "apply"}
SKIP = {"skip", "no", "nee", "n", "exclude"}

# crosswalk column -> workbook column
FIELDS = {"proposed_L2":"L2_commodity_group", "proposed_L3":"L3_commodity_subgroup",
          "proposed_L4":"L4_ingredient", "proposed_level":"level_1to5",
          "proposed_name":"stream_name_NL"}


def load_crosswalk():
    if not CROSSWALK.exists():
        sys.exit(f"missing {CROSSWALK.name} — run make_varia_reclass.py first")
    rows = list(csv.DictReader(io.open(CROSSWALK, encoding="utf-8-sig"), delimiter=";"))
    blank = [r["claim_id"] for r in rows if not (r.get("DECISION") or "").strip()]
    if blank:
        print(f"REFUSING TO RUN — {len(blank)} of {len(rows)} rows in {CROSSWALK.name} have a "
              f"blank DECISION.\nFill each one with 'ok' or 'skip', then run this again.\n")
        print("unreviewed:")
        for i in range(0, len(blank), 10):
            print("  " + ", ".join(blank[i:i+10]))
        sys.exit(1)
    bad = [r["claim_id"] for r in rows
           if r["DECISION"].strip().lower() not in APPLY | SKIP]
    if bad:
        sys.exit(f"DECISION must be one of {sorted(APPLY | SKIP)}; unrecognised on: "
                 f"{', '.join(bad)}")
    return {r["claim_id"]: r for r in rows if r["DECISION"].strip().lower() in APPLY}


def header_map(ws):
    return {str(c.value).strip(): c.column for c in ws[1] if c.value}


def main():
    todo = load_crosswalk()
    if not WB.exists(): sys.exit(f"missing {WB.name}")
    print(f"{len(todo)} row(s) marked ok in {CROSSWALK.name}")

    wb = openpyxl.load_workbook(WB)
    if SHEET not in wb.sheetnames: sys.exit(f"no '{SHEET}' sheet in {WB.name}")
    ws = wb[SHEET]
    col = header_map(ws)
    missing = [c for c in list(FIELDS.values())+["claim_id"] if c not in col]
    if missing: sys.exit(f"columns not found in {SHEET}: {', '.join(missing)}")

    changed, untouched, seen = 0, 0, set()
    for row in range(2, ws.max_row + 1):
        cid = ws.cell(row=row, column=col["claim_id"]).value
        if not cid or str(cid).strip() not in todo: continue
        cid = str(cid).strip(); seen.add(cid)
        r, edits = todo[cid], []
        for src, dst in FIELDS.items():
            new = (r.get(src) or "").strip()
            cell = ws.cell(row=row, column=col[dst])
            cur = "" if cell.value is None else str(cell.value).strip()
            if dst == "level_1to5":
                new_val = int(new) if new else None
                if cur != new: edits.append((dst, cur, new)); cell.value = new_val
            elif new != cur:
                edits.append((dst, cur, new)); cell.value = new if new else None
        if edits: changed += 1
        else: untouched += 1
        if edits and len(edits) <= 6:
            print(f"  {cid}: " + " · ".join(f"{d}: {a or '(blank)'} -> {b or '(blank)'}" for d,a,b in edits))

    absent = sorted(set(todo) - seen)
    if absent: print(f"  ! not found in the sheet: {', '.join(absent)}")
    print(f"\n{changed} row(s) changed, {untouched} already correct")

    if DRY:
        print("--dry-run: workbook not written"); return
    if not changed:
        print("nothing to write"); return

    try:
        wb.save(WB)                       # written last, so a lock cannot half-apply the change
    except PermissionError:
        sys.exit(f"\nCannot write {WB.name} — it is open in Excel. Close it and run this again.")
    print(f"wrote {WB.name}")
    export(wb)


def export(wb):
    """Kept as a thin alias: the canonical-order exporter now lives in export_streams.py."""
    from export_streams import export as _export
    _export(wb)


if __name__ == "__main__":
    main()
