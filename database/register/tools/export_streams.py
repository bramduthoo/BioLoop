"""Write the `Streams` sheet out as `streams_export.csv` in the canonical column order.

The export is what makes a session's claim-level changes git-diffable, so it must not depend on
the order the reviewer happens to have dragged the sheet's columns into. It therefore keeps the
column order already in `streams_export.csv` and appends anything new at the end.

Importable (`from export_streams import export`) and runnable:

    database/.venv/Scripts/python.exe database/register/export_streams.py
"""
import csv, io, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                      # register/ - HERE is register/tools/
WB = ROOT / "BIOLOOP_streams_and_sources.xlsx"
EXPORT = ROOT / "streams_export.csv"
SHEET = "Streams"


def header_map(ws):
    return {str(c.value).strip(): c.column for c in ws[1] if c.value}


def export(wb, sheet=SHEET, out=EXPORT):
    ws = wb[sheet]
    order = [str(c.value).strip() for c in ws[1] if c.value]
    if out.exists():
        with io.open(out, encoding="utf-8-sig") as fh:
            canonical = next(csv.reader(fh, delimiter=";"))
        order = [c for c in canonical if c in order] + [c for c in order if c not in canonical]
    col = header_map(ws)
    with io.open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(order)
        for row in range(2, ws.max_row + 1):
            if not ws.cell(row=row, column=col["claim_id"]).value:
                continue
            w.writerow(["" if ws.cell(row=row, column=col[c]).value is None
                        else ws.cell(row=row, column=col[c]).value for c in order])
    print(f"wrote {out.name} ({len(order)} columns, canonical order)")


def main():
    import openpyxl
    if not WB.exists():
        sys.exit(f"missing {WB.name}")
    export(openpyxl.load_workbook(WB))


if __name__ == "__main__":
    main()
