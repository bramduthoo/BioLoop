"""Apply the reviewer-approved rows of `crosswalks/FIXES_2026-09-01.csv` to the workbook.

Only rows whose `DECISION_fix` is `ok` are applied. `fix` means the proposal itself was wrong and
goes back for a second round; `0` means deferred. Both are reported and left alone, so this script
is safe to re-run as the sheet fills up.

Writes the `Streams` sheet BY COLUMN HEADER, workbook last, idempotent.

    database/.venv/Scripts/python.exe database/register/apply_fixes.py --dry-run
    database/.venv/Scripts/python.exe database/register/apply_fixes.py
"""
import csv, io, pathlib, sys
import openpyxl

HERE = pathlib.Path(__file__).resolve().parent
WB = HERE / "BIOLOOP_streams_and_sources.xlsx"
SHEET = "Streams"
DRY = "--dry-run" in sys.argv
APPLY = {"ok", "yes", "ja", "j"}
DEFER = {"0", "fix", "skip", "no", "later"}

# crosswalk column -> workbook column
FIELDS = {"SET_level_1to5": "level_1to5",
          "SET_L4_ingredient": "L4_ingredient",
          "SET_stream_name_NL": "stream_name_NL",
          "SET_L2_commodity_group": "L2_commodity_group",
          "SET_L3_commodity_subgroup": "L3_commodity_subgroup"}
INT_COLS = {"level_1to5"}


def load(path):
    if not path.exists():
        sys.exit(f"missing {path.name}")
    return list(csv.DictReader(io.open(path, encoding="utf-8-sig"), delimiter=";"))


def main():
    # Any decision sheet in crosswalks/ that carries a DECISION_fix column: the audit's own
    # findings, plus any FIXES_* sheet still present. Sheets that have been archived to
    # migrations/ simply drop out - nothing here is tied to one review round.
    sheets = sorted((HERE / "crosswalks").glob("FIXES_*.csv"))
    audit = HERE / "crosswalks" / "AUDIT_findings.csv"
    if audit.exists():
        sheets.append(audit)
    if not sheets:
        sys.exit("no decision sheet found in crosswalks/ (FIXES_*.csv or AUDIT_findings.csv)")
    todo, deferred, unknown = {}, [], []
    for p in sheets:
        if not p.exists():
            continue
        for r in load(p):
            d = (r.get("DECISION_fix") or "").strip().lower()
            cid = (r.get("claim_id") or "").strip()
            if d in APPLY:
                todo.setdefault(cid, []).append((p.name, r))
            elif d in DEFER:
                deferred.append((p.name, cid, d))
            elif d:
                unknown.append((p.name, cid, d))
            else:
                deferred.append((p.name, cid, "(blank)"))
    if unknown:
        sys.exit("unrecognised DECISION_fix values: "
                 + ", ".join(f"{c}={d!r} in {f}" for f, c, d in unknown[:10]))
    print(f"{sum(len(v) for v in todo.values())} row(s) approved · {len(deferred)} deferred/fix")

    wb = openpyxl.load_workbook(WB)
    ws = wb[SHEET]
    col = {str(c.value).strip(): c.column for c in ws[1] if c.value}
    changed, already = 0, 0
    for row in range(2, ws.max_row + 1):
        cid = ws.cell(row=row, column=col["claim_id"]).value
        if not cid:
            continue
        cid = str(cid).strip()
        if cid not in todo:
            continue
        edits = []
        for _src, r in todo[cid]:
            for scol, dcol in FIELDS.items():
                new = (r.get(scol) or "").strip()
                if not new or dcol not in col:
                    continue
                cell = ws.cell(row=row, column=col[dcol])
                cur = "" if cell.value is None else str(cell.value).strip()
                if dcol in INT_COLS:
                    new_norm = str(int(float(new)))
                    if cur != new_norm:
                        edits.append((dcol, cur, new_norm)); cell.value = int(float(new))
                elif new != cur:
                    edits.append((dcol, cur, new)); cell.value = new
        if edits:
            changed += 1
            print(f"  {cid}: " + " · ".join(f"{d}: {a or '(blank)'} -> {b}" for d, a, b in edits))
        else:
            already += 1

    print(f"\n{changed} row(s) changed, {already} already correct")
    if DRY:
        print("--dry-run: workbook not written"); return
    if not changed:
        print("nothing to write"); return
    try:
        wb.save(WB)
    except PermissionError:
        sys.exit(f"\nCannot write {WB.name} - it is open in Excel. Close it and run this again.")
    print(f"wrote {WB.name}")

    from export_streams import export
    export(wb)


if __name__ == "__main__":
    main()
