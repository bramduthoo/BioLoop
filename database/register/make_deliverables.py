# -*- coding: utf-8 -*-
"""make_deliverables.py - the two shareable outputs, as files you can attach to an e-mail.

    node select_streams.js 65 --json sel_raw.json
    database/.venv/Scripts/python make_deliverables.py sel_raw.json

Writes into deliverables/:
    BIOLOOP_stream_selection_<date>.xlsx   the selection, parent rows + their fractions
    BIOLOOP_gap_list_<date>.xlsx           the nine gaps, one row each

Every figure in the gap sheet carries the claim id it comes from, so it can be checked against
streams_export.csv without opening the workbook.
"""
import json, sys, pathlib, datetime, io, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "deliverables"; OUT.mkdir(exist_ok=True)
TODAY = datetime.date.today().isoformat()
SH = lambda e: (e.replace("OVAM Monitor voedselverlies ", "OVAM ")
                 .replace(" ILVO 165", "").replace(" tuinbouw", ""))

INK = "FF1A1E18"; MUT = "FF767C6F"
F_H = Font(name="Calibri", bold=True, size=10, color="FFFFFFFF")
FILL_H = PatternFill("solid", fgColor="FF3D4A38")
FILL_80 = PatternFill("solid", fgColor="FFE3EDE4")
FILL_90 = PatternFill("solid", fgColor="FFF6EEDC")
FILL_SUB = PatternFill("solid", fgColor="FFF7F8F4")
THIN = Side(style="thin", color="FFD5D9CD")
BAND = Border(top=Side(style="medium", color="FF3D6B4E"))


def autosize(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------- selection
def selection(raw):
    d = json.load(io.open(raw, encoding="utf-8"))
    cum = 0.0; n80 = n90 = 0; rows = []
    for i, s in enumerate(d["items"]):
        cum += s["M"]
        if not n80 and cum / d["TOT"] >= .80: n80 = i + 1
        if not n90 and cum / d["TOT"] >= .90: n90 = i + 1
        per = sorted(({"src": SH(e), "v": s["by"][e]["v"]} for e in d["EDS"] if e in s["by"]),
                     key=lambda x: x["v"])
        fr = []
        for r in s.get("fracRows", []):
            p = sorted(({"src": SH(e), "v": r["by"][e]} for e in d["EDS"] if e in r["by"]),
                       key=lambda x: x["v"])
            un = r["label"].startswith("— ")
            fr.append(dict(label="geen fractie benoemd" if un else r["label"], unfrac=un,
                           stage=r["label"][2:] if un else " · ".join(r.get("st") or []),
                           mn=p[0], mx=p[-1], n=len(p),
                           be="Belgie" in (r.get("geo") or [])))
        fr.sort(key=lambda x: -x["mx"]["v"])
        rows.append(dict(rank=i + 1, name=s["l4"], l2=s["l2"], stages=" · ".join(s["stages"]),
                         be="Belgie" in s["geo"], n=s["nSrc"], mn=per[0], mx=per[-1],
                         cum=cum / d["TOT"], frac=fr if len(fr) > 1 else []))

    wb = Workbook(); ws = wb.active; ws.title = "Selectie"
    ws["A1"] = "BIOLOOP — BioMobi kandidaat-stroomselectie"
    ws["A1"].font = Font(bold=True, size=15)
    ws["A2"] = ("%s t/jaar — de som van het grootste gerapporteerde cijfer per stroom  ·  "
                "%d stromen dragen 80%%  ·  %d dragen 90%%  ·  %d stromen in totaal  ·  %s"
                % (format(round(d["TOT"]), ",d").replace(",", "."), n80, n90, len(rows), TODAY))
    ws["A2"].font = Font(size=9, color=MUT)
    ws["A3"] = ("Cijfers worden NOOIT opgeteld over bronnen heen: waar twee bronnen dezelfde stroom "
                "meten staan beide er. Een inspringende rij is een fractie van de stroom erboven; "
                "de ouderrij is per bron de som van haar fracties.")
    ws["A3"].font = Font(size=9, color=MUT); ws["A3"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A3:I3"); ws.row_dimensions[3].height = 28

    hdr = ["#", "stroom / fractie", "laagste cijfer", "bron", "hoogste cijfer", "bron",
           "tak", "ketenschakel", "bronnen", "cum. %"]
    ws.append([]); ws.append(hdr)
    hrow = ws.max_row
    for c in range(1, len(hdr) + 1):
        cell = ws.cell(hrow, c); cell.font = F_H; cell.fill = FILL_H
        cell.alignment = Alignment(horizontal="right" if c in (1, 3, 5, 9, 10) else "left")
    ws.freeze_panes = ws.cell(hrow + 1, 1)

    for r in rows:
        band = FILL_80 if r["rank"] <= n80 else FILL_90 if r["rank"] <= n90 else None
        ws.append([r["rank"], r["name"] + ("  [BE]" if r["be"] else ""),
                   r["mn"]["v"] if r["n"] > 1 else None, r["mn"]["src"] if r["n"] > 1 else "",
                   r["mx"]["v"], r["mx"]["src"], r["l2"], r["stages"], r["n"], r["cum"]])
        i = ws.max_row
        ws.cell(i, 2).font = Font(bold=True)
        for c in range(1, 11):
            cell = ws.cell(i, c)
            if band: cell.fill = band
            cell.border = Border(bottom=THIN)
            if c in (3, 5): cell.number_format = "#.##0"
            if c == 10: cell.number_format = "0,0%"
        if r["rank"] in (n80, n90):
            for c in range(1, 11): ws.cell(i, c).border = Border(bottom=Side(style="medium", color="FF3D6B4E"))
        for f in r["frac"]:
            ws.append(["", "     └ " + f["label"] + ("  [BE]" if f["be"] else ""),
                       f["mn"]["v"] if f["n"] > 1 else None, f["mn"]["src"] if f["n"] > 1 else "",
                       f["mx"]["v"], f["mx"]["src"], "",
                       (f["stage"] + "  (hele stroom bij deze schakel)") if f["unfrac"] else f["stage"],
                       f["n"], None])
            j = ws.max_row
            for c in range(1, 11):
                cell = ws.cell(j, c); cell.fill = FILL_SUB; cell.border = Border(bottom=THIN)
                cell.font = Font(size=10, color="FF454A41")
                if c in (3, 5): cell.number_format = "#.##0"
    autosize(ws, [5, 46, 15, 13, 15, 13, 26, 34, 9, 9])
    p = OUT / ("BIOLOOP_stream_selection_%s.xlsx" % TODAY); wb.save(p)
    print("wrote", p.name, "-", len(rows), "streams")
    return p


# ---------------------------------------------------------------- gaps
GAPS = json.loads(io.open(HERE / "deliverables" / "gaps.json", encoding="utf-8").read()) \
    if (HERE / "deliverables" / "gaps.json").exists() else None


def gaps():
    src = json.load(io.open(HERE / "deliverables" / "gaps.json", encoding="utf-8"))
    wb = Workbook(); ws = wb.active; ws.title = "Gaps"
    ws["A1"] = "BIOLOOP — negen gaps, in volgorde van belang"
    ws["A1"].font = Font(bold=True, size=15)
    ws["A2"] = ("Sectoren waar een grote reststroom gerapporteerd wordt en er niets gepubliceerd is "
                "over waaruit die bestaat. Elk vraagt een nieuwe bron; geen enkele is op te lossen "
                "met de data die we hebben.  ·  " + TODAY)
    ws["A2"].font = Font(size=9, color=MUT); ws["A2"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:F2"); ws.row_dimensions[2].height = 26
    hdr = ["#", "sector", "cijfer", "wat dat cijfer is", "wie het rapporteert",
           "wat er ontbreekt"]
    ws.append([]); ws.append(hdr)
    hrow = ws.max_row
    for c in range(1, len(hdr) + 1):
        cell = ws.cell(hrow, c); cell.font = F_H; cell.fill = FILL_H
    ws.freeze_panes = ws.cell(hrow + 1, 1)
    for i, g in enumerate(src, 1):
        ws.append([i, g["n"], g["amt"], g["unit"], g["who_plain"], " ".join(g["p"])])
        r = ws.max_row
        ws.cell(r, 2).font = Font(bold=True)
        for c in range(1, 7):
            ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
            ws.cell(r, c).border = Border(bottom=THIN)
        ws.row_dimensions[r].height = 96
    autosize(ws, [4, 34, 14, 30, 56, 78])
    p = OUT / ("BIOLOOP_gap_list_%s.xlsx" % TODAY); wb.save(p)
    print("wrote", p.name, "-", len(src), "gaps")
    return p


if __name__ == "__main__":
    selection(sys.argv[1] if len(sys.argv) > 1 else "sel_raw.json")
    gaps()
