# -*- coding: utf-8 -*-
"""make_deliverables.py - the two shareable outputs, as files you can attach to an e-mail.

    node tools/select_streams.js 69 --json build/sel_raw.json
    node tools/make_gap_list.js       --json build/gaps_derived.json
    database/.venv/Scripts/python tools/make_deliverables.py build/sel_raw.json

Writes into deliverables/, each as .xlsx and .html:
    BIOLOOP_stream_selection_<date>   the selection, parent rows + their fractions
    BIOLOOP_gap_list_<date>           the gaps, de-nested, largest first

BOTH ARE RENDERINGS, NOT SOURCES. The selection comes from select_streams.js and the gap list
from make_gap_list.js; this file decides layout and nothing else. In particular the gap list is
DERIVED from the data as a consequence of the selection - asserted mass minus selectable mass per
place - and is never carried over from a previous edition of itself. It used to be a hand-curated
`deliverables/gaps.json`; that file is gone, deliberately (2026-09-09).

Every figure in the gap sheet carries the claim id it comes from, so it can be checked against
streams_export.csv without opening the workbook.
"""
import json, sys, pathlib, datetime, io, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                      # register/ - HERE is register/tools/
OUT = ROOT / "deliverables"; OUT.mkdir(exist_ok=True)
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
def GEO(r):
    """Geography marker. A mixed row is flagged apart from a wholly Belgian one."""
    return "  [BE+VL]" if r.get("mixed") else ("  [BE]" if r.get("be") else "")


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
            rgeo = r.get("geo") or []
            fr.append(dict(label="geen fractie benoemd" if un else r["label"], unfrac=un,
                           stage=r["label"][2:] if un else " · ".join(r.get("st") or []),
                           mn=p[0], mx=p[-1], n=len(p),
                           be="Belgie" in rgeo,
                           mixed="Belgie" in rgeo and "Vlaanderen" in rgeo))
        fr.sort(key=lambda x: -x["mx"]["v"])
        # A plain [BE] marker said only "Belgian somewhere", so Kool- en raapzaad (99,3% of the
        # node's value is a Belgian figure) and Bloemkool (1,9%) read identically. A node whose
        # value ADDS a Flemish and a Belgian figure is a different thing from a wholly Belgian
        # one, and the reviewer has to be able to see which is which (2026-09-08 review).
        mixed = "Belgie" in s["geo"] and "Vlaanderen" in s["geo"]
        rows.append(dict(rank=i + 1, name=s["l4"], l2=s["l2"], stages=" · ".join(s["stages"]),
                         be="Belgie" in s["geo"], mixed=mixed, n=s["nSrc"], mn=per[0], mx=per[-1],
                         cum=cum / d["TOT"],
                         # always open a mixed node, so its Flemish and Belgian halves are visible
                         frac=fr if (len(fr) > 1 or mixed) else []))

    wb = Workbook(); ws = wb.active; ws.title = "Selectie"
    ws["A1"] = "BIOLOOP — BioMobi kandidaat-stroomselectie"
    ws["A1"].font = Font(bold=True, size=15)
    ws["A2"] = ("%s t/jaar — de som van het grootste gerapporteerde cijfer per stroom  ·  "
                "%d stromen dragen 80%%  ·  %d dragen 90%%  ·  %d stromen in totaal  ·  %s"
                % (format(round(d["TOT"]), ",d").replace(",", "."), n80, n90, len(rows), TODAY))
    ws["A2"].font = Font(size=9, color=MUT)
    ws["A3"] = ("Cijfers worden NOOIT opgeteld over bronnen heen: waar twee bronnen dezelfde stroom "
                "meten staan beide er. Een inspringende rij is een fractie van de stroom erboven; "
                "de ouderrij is per bron de som van haar fracties.  ·  [BE] = het cijfer is Belgisch; "
                "[BE+VL] = de ouderrij telt een Vlaams en een Belgisch cijfer bij elkaar op, dus het "
                "getal is geen van beide — de fracties eronder tonen welke helft welke is.")
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
        ws.append([r["rank"], r["name"] + GEO(r),
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
            ws.append(["", "     └ " + f["label"] + GEO(f),
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
# The gap list is DERIVED, never curated: `tools/make_gap_list.js` computes asserted-minus-
# selectable per (place x chain stage), de-nested so nothing is counted twice and merged only
# within a scope family, because state.md forbids OVAM and MONBIO from cross-checking each other.
# This function renders that output; it invents nothing and inherits nothing from a previous list.
GAPSRC = ROOT / "build" / "gaps_derived.json"


def _gaprows(src):
    """Flatten the derived gap list into report rows, parents before their nested children."""
    rows = sorted(src["rows"], key=lambda r: -r["ownGap"])
    bykey = {r["key"]: r for r in rows}
    out, seen = [], set()

    def emit(r, depth):
        if r["key"] in seen:
            return
        seen.add(r["key"])
        out.append((depth, r))
        for c in sorted((x for x in rows if x.get("parentKey") == r["key"]),
                        key=lambda x: -x["ownGap"]):
            emit(c, depth + 1)

    for r in rows:
        if not r.get("parentKey") or r["parentKey"] not in bykey:
            emit(r, 0)
    for r in rows:                      # safety net: never drop a row
        emit(r, 0)
    return out


def gaps():
    if not GAPSRC.exists():
        sys.exit("missing build/gaps_derived.json - run: node tools/make_gap_list.js "
                 "--json build/gaps_derived.json")
    src = json.load(io.open(GAPSRC, encoding="utf-8"))
    rows = _gaprows(src)
    total = sum(r["ownGap"] for _, r in rows)

    wb = Workbook(); ws = wb.active; ws.title = "Gaps"
    ws["A1"] = "BIOLOOP — waar de data massa beweert die geen selecteerbare stroom dekt"
    ws["A1"].font = Font(bold=True, size=15)
    ws["A2"] = ("%s t/jaar over %d plekken, drempel %s t  ·  afgeleid uit de stroomselectie: "
                "per plek het grootste totaal dat één bron rapporteert, min de massa die op L4/L5 "
                "selecteerbaar is  ·  %s"
                % (format(round(total), ",d").replace(",", "."), len(rows),
                   format(src["min"], ",d").replace(",", "."), TODAY))
    ws["A2"].font = Font(size=9, color=MUT)
    ws["A3"] = ("Geneste plekken worden NOOIT opgeteld: elke rij draagt alleen het gat dat haar "
                "eigen takken niet al dragen, dus de rijen vormen een opdeling en geen stapel. "
                "Bronnen worden alleen samengevoegd binnen één monitorfamilie — OVAM en MONBIO "
                "meten verschillende dingen (2,1x uit elkaar) en mogen elkaars gat niet wegstrepen. "
                "Een ingesprongen rij zit binnen de rij erboven.")
    ws["A3"].font = Font(size=9, color=MUT); ws["A3"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A3:H3"); ws.row_dimensions[3].height = 30

    hdr = ["#", "plek", "ketenschakel", "bron", "beweerd", "bereikbaar", "gat",
           "wat er ontbreekt", "wat het zou sluiten", "claims"]
    ws.append([]); ws.append(hdr)
    hrow = ws.max_row
    for c in range(1, len(hdr) + 1):
        cell = ws.cell(hrow, c); cell.font = F_H; cell.fill = FILL_H
        cell.alignment = Alignment(horizontal="right" if c in (1, 5, 6, 7) else "left")
    ws.freeze_panes = ws.cell(hrow + 1, 1)

    for i, (depth, r) in enumerate(rows, 1):
        named = [u for u in r.get("unplaced", []) if not u.get("parallel")]
        claims = ", ".join(u["id"] for u in named) or                  ", ".join(c["id"] for c in (r.get("claims") or [])[:6])
        ws.append([i, ("      " * depth) + r["place"], r["stage"], r["family"],
                   r["asserted"], r["reached"], r["ownGap"],
                   r["what"], r["close"], claims])
        j = ws.max_row
        ws.cell(j, 2).font = Font(bold=depth == 0)
        for c in range(1, len(hdr) + 1):
            cell = ws.cell(j, c)
            cell.alignment = Alignment(wrap_text=c in (2, 8, 9, 10), vertical="top")
            cell.border = Border(bottom=THIN)
            if c in (5, 6, 7): cell.number_format = "#.##0"
            if depth: cell.fill = FILL_SUB
        ws.cell(j, 7).font = Font(bold=True)
        ws.row_dimensions[j].height = 60
        # the sector rows that name an otherwise unattributable residual
        for u in named:
            ws.append(["", "         · " + u["name"], "", "", "", "", u["v"], "", "", u["id"]])
            k = ws.max_row
            for c in range(1, len(hdr) + 1):
                cell = ws.cell(k, c); cell.fill = FILL_SUB; cell.border = Border(bottom=THIN)
                cell.font = Font(size=10, color="FF454A41")
                cell.alignment = Alignment(wrap_text=c == 2, vertical="top")
                if c == 7: cell.number_format = "#.##0"
    autosize(ws, [4, 40, 26, 14, 13, 13, 13, 52, 52, 22])
    out = OUT / ("BIOLOOP_gap_list_%s.xlsx" % TODAY); wb.save(out)
    print("wrote", out.name, "-", len(rows), "gap rows,",
          format(round(total), ",d").replace(",", "."), "t")
    return src, rows, total


# ---------------------------------------------------------------- html
CSS = """
:root{--pap:#F7F6F2;--card:#fff;--ink:#1A1C1E;--mut:#6E7276;--rule:#DFDCD3;--acc:#1F4B73;
--gap:#9E3B22;--ok:#2E6144;--sub:#F2F0EA;color-scheme:light}
@media(prefers-color-scheme:dark){:root{--pap:#141517;--card:#1C1E21;--ink:#ECEAE6;--mut:#93979C;
--rule:#2E3236;--acc:#7FB0DC;--gap:#E08B6E;--ok:#7FBE9A;--sub:#232629;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--pap);color:var(--ink);
font:14px/1.5 "Segoe UI",system-ui,sans-serif}
.wrap{max-width:1400px;margin:0 auto;padding:28px 22px 60px}
h1{font-size:23px;margin:0 0 4px}p.sub{color:var(--mut);font-size:13px;margin:0 0 4px;max-width:100ch}
table{width:100%;border-collapse:collapse;font-size:12.5px;background:var(--card);
border:1px solid var(--rule);border-radius:7px;overflow:hidden;margin-top:18px}
th{text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:#fff;
background:var(--acc);padding:8px;font-weight:700}
td{padding:7px 8px;border-top:1px solid var(--rule);vertical-align:top}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;
font-family:ui-monospace,Menlo,monospace}
tr.sub td{background:var(--sub);color:var(--mut);font-size:11.5px}
tr.d1 td:first-child{padding-left:26px}tr.d2 td:first-child{padding-left:44px}
.gapn{color:var(--gap);font-weight:700}.b{font-weight:700}
.band80{background:rgba(46,97,68,.10)}.band90{background:rgba(180,140,30,.10)}
.tag{display:inline-block;font-size:10px;font-weight:700;padding:1px 6px;border-radius:3px;
background:var(--sub);color:var(--mut);margin-left:5px}
"""


def _esc(x):
    return (str("" if x is None else x).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _n(v):
    return "" if v in (None, "") else format(round(v), ",d").replace(",", ".")


def html_page(title, sub, note, head, body_rows, name):
    h = ["<!doctype html><html lang=nl><head><meta charset=utf-8>",
         "<meta name=viewport content='width=device-width,initial-scale=1'>",
         "<title>%s</title><style>%s</style></head><body><div class=wrap>" % (_esc(title), CSS),
         "<h1>%s</h1><p class=sub>%s</p><p class=sub>%s</p>" % (_esc(title), _esc(sub), _esc(note)),
         "<table><thead><tr>" + "".join("<th>%s</th>" % _esc(c) for c in head) + "</tr></thead><tbody>",
         "".join(body_rows), "</tbody></table></div></body></html>"]
    out = OUT / name
    io.open(out, "w", encoding="utf-8").write("".join(h))
    print("wrote", out.name)
    return out


def gaps_html(src, rows, total):
    body = []
    for i, (depth, r) in enumerate(rows, 1):
        body.append(
            "<tr class='d%d'><td class=b>%s</td><td>%s</td><td>%s</td><td class=n>%s</td>"
            "<td class=n>%s</td><td class='n gapn'>%s</td><td>%s</td><td>%s</td></tr>"
            % (depth, _esc(r["place"]), _esc(r["stage"]), _esc(r["family"]),
               _n(r["asserted"]), _n(r["reached"]), _n(r["ownGap"]),
               _esc(r["what"]), _esc(r["close"])))
        for u in [u for u in r.get("unplaced", []) if not u.get("parallel")]:
            body.append("<tr class='sub d%d'><td colspan=4>· %s <span class=tag>%s</span></td>"
                        "<td class=n></td><td class=n>%s</td><td colspan=2></td></tr>"
                        % (depth + 1, _esc(u["name"]), _esc(u["id"]), _n(u["v"])))
    return html_page(
        "BIOLOOP — gaplijst",
        "%s t/jaar over %d plekken · afgeleid uit de stroomselectie: per plek het grootste totaal "
        "dat één bron rapporteert, min de massa die op L4/L5 selecteerbaar is · %s"
        % (_n(total), len(rows), TODAY),
        "Geneste plekken worden nooit opgeteld — elke rij draagt alleen het gat dat haar eigen "
        "takken niet al dragen. Bronnen worden alleen binnen één monitorfamilie samengevoegd, "
        "omdat OVAM en MONBIO verschillende dingen meten en elkaars gat niet mogen wegstrepen.",
        ["plek", "ketenschakel", "bron", "beweerd", "bereikbaar", "gat",
         "wat er ontbreekt", "wat het zou sluiten"],
        body, "BIOLOOP_gap_list_%s.html" % TODAY)


def selection_html(raw):
    d = json.load(io.open(raw, encoding="utf-8"))
    cum = 0.0; n80 = n90 = 0; body = []
    for i, s in enumerate(d["items"]):
        cum += s["M"]
        if not n80 and cum / d["TOT"] >= .80: n80 = i + 1
        if not n90 and cum / d["TOT"] >= .90: n90 = i + 1
    cum = 0.0
    for i, s in enumerate(d["items"], 1):
        cum += s["M"]
        per = sorted(({"src": SH(e), "v": s["by"][e]["v"]} for e in d["EDS"] if e in s["by"]),
                     key=lambda x: x["v"])
        geo = s.get("geo") or []
        mark = ("<span class=tag>BE+VL</span>" if "Belgie" in geo and "Vlaanderen" in geo
                else "<span class=tag>BE</span>" if "Belgie" in geo else "")
        band = "band80" if i <= n80 else "band90" if i <= n90 else ""
        body.append(
            "<tr class='%s'><td class=n>%d</td><td class=b>%s %s</td><td class=n>%s</td><td>%s</td>"
            "<td class=n>%s</td><td>%s</td><td>%s</td><td>%s</td><td class=n>%d</td>"
            "<td class=n>%.1f%%</td></tr>"
            % (band, i, _esc(s["l4"]), mark,
               _n(per[0]["v"]) if len(per) > 1 else "", _esc(per[0]["src"]) if len(per) > 1 else "",
               _n(per[-1]["v"]), _esc(per[-1]["src"]), _esc(s["l2"]),
               _esc(" · ".join(s.get("stages") or [])), s["nSrc"], 100 * cum / d["TOT"]))
        for f in s.get("fracRows", []):
            v = sorted(f["by"].values())
            fgeo = f.get("geo") or []
            fm = ("<span class=tag>BE+VL</span>" if "Belgie" in fgeo and "Vlaanderen" in fgeo
                  else "<span class=tag>BE</span>" if "Belgie" in fgeo else "")
            body.append("<tr class='sub d1'><td></td><td>· %s %s</td><td class=n>%s</td><td></td>"
                        "<td class=n>%s</td><td colspan=5></td></tr>"
                        % (_esc(f["label"]), fm, _n(v[0]) if len(v) > 1 else "", _n(v[-1])))
    return html_page(
        "BIOLOOP — kandidaat-stroomselectie",
        "%s t/jaar — de som van het grootste cijfer dat één bron per stroom geeft · %d stromen "
        "dragen 80%%, %d dragen 90%%, %d in totaal · %s"
        % (_n(d["TOT"]), n80, n90, len(d["items"]), TODAY),
        "Cijfers worden nooit opgeteld over bronnen heen. Een ingesprongen rij is een fractie van "
        "de stroom erboven. [BE] = een Belgisch cijfer; [BE+VL] = de rij telt een Vlaams en een "
        "Belgisch cijfer bij elkaar op, dus het getal is geen van beide.",
        ["#", "stroom / fractie", "laagste", "bron", "hoogste", "bron", "tak", "ketenschakel",
         "bronnen", "cum. %"],
        body, "BIOLOOP_stream_selection_%s.html" % TODAY)


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else "sel_raw.json"
    selection(raw)
    selection_html(raw)
    src, rows, total = gaps()
    gaps_html(src, rows, total)
