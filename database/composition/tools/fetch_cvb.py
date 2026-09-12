"""Extract product sheets from the CVB Veevoedertabel PDF.

    ../.venv/Scripts/python tools/fetch_cvb.py --find stoomschil
    ../.venv/Scripts/python tools/fetch_cvb.py --page 561
    ../.venv/Scripts/python tools/fetch_cvb.py --emit          -> ../extraction/cvb_rows.csv

WHY THIS SOURCE. GeNeSys (S065), the ILVO study the register takes several of these
tonnages from, cites `CVB, 2007` for the dry-matter content of exactly these horticultural
streams and carries no composition table of its own. The CVB Veevoedertabel is therefore
the source our own source points at, it is Dutch rather than tropical or Mediterranean,
and it is a free PDF. Rounds 1 and 2 never opened it.

WHAT IT IS. Stichting CVB, 2023 edition, 708 pages, one sheet per feed material, every
sheet in the same shape: Weende analysis and carbohydrates, then minerals, then trace
elements, all in g/kg dry matter with dry matter itself in g/kg product, and a standard
deviation (`sdc`) beside each mean where CVB has one.

WHAT IS DELIBERATELY NOT TAKEN. Everything below the `Verteringscoefficienten` line -
VEM, DVE, OEB, FOS, the digestibility coefficients, the amino-acid and fatty-acid blocks.
The digestibilities and feed-value figures are facts about a material AND an animal and
belong to the model's rule layer, not a facts-only data layer; the amino acids are
expressed as `g/16g N`, an expression relative to protein rather than a unit, which is
the same reason they were left out of the FoodWasteEXplorer harvest.
"""

from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path

import pdfplumber

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PDF = Path(sys.argv[0]).parent.parent / "data" / "raw" / "cvb-veevoedertabel-2023.pdf"
FALLBACK = Path(r"C:\Users\bduthoo\AppData\Local\Temp\claude"
                r"\C--Users-bduthoo-repo-s-BioLoop-database"
                r"\d805cd10-4894-4b70-b54e-967ad7aba38d\scratchpad\cvb2023.pdf")

# CVB column label -> (parameter, unit, basis, method, note)
WEENDE = {
    "DS":    ("dry_matter", "g/kg", "fresh", "", "CVB gives dry matter per kg PRODUCT"),
    "RAS":   ("ash", "g/kg", "dry", "", ""),
    "RE":    ("crude_protein", "g/kg", "dry", "", "CVB's RE, nitrogen times 6,25"),
    "RVET":  ("fat_total", "g/kg", "dry", "ee-diethyl", "CVB's RVET"),
    "RVETh": ("fat_total", "g/kg", "dry", "ee-hcl", "CVB's RVETh, after acid hydrolysis"),
    "RC":    ("crude_fibre", "g/kg", "dry", "", ""),
    "OK":    ("nfe", "g/kg", "dry", "", "CVB's OK, the Weende by-difference remainder"),
    "ZETew": ("starch", "g/kg", "dry", "starch-polarimetric", "CVB's ZETew, the Ewers method"),
    "ZETam": ("starch", "g/kg", "dry", "starch-enzymatic", "CVB's ZETam, amyloglucosidase"),
    "SUI":   ("total_sugars", "g/kg", "dry", "", ""),
    "NDF":   ("ndf", "g/kg", "dry", "", ""),
    "ADF":   ("adf", "g/kg", "dry", "", ""),
    "ADL":   ("lignin", "g/kg", "dry", "lignin-adl", ""),
}
MINERALS = {
    "Ca": ("calcium", "g/kg"), "P": ("phosphorus", "g/kg"), "Mg": ("magnesium", "g/kg"),
    "K": ("potassium", "g/kg"), "Na": ("sodium", "g/kg"), "Cl": ("chloride", "g/kg"),
    "S": ("sulphur", "g/kg"),
}
TRACE = {"Fe": ("iron", "mg/kg"), "Mn": ("manganese", "mg/kg"), "Zn": ("zinc", "mg/kg"),
         "Cu": ("copper", "mg/kg"), "Se": ("selenium", "mg/kg")}

# CVB page -> BioMobi stream code. Only the 19 in-scope targets.
PAGES: dict[int, tuple[str, str]] = {
    561: ("zuivelnevenstroom", "Kaaswei, vers - RE 175-275 g/kg DS"),
    563: ("zuivelnevenstroom", "Kaaswei, vers - RE > 275 g/kg DS"),
    595: ("suikerbiet-loof", "Bietenblad met koppen, vers"),
    597: ("suikerbiet-loof", "Bietenblad, vers"),
    687: ("tarwe-stro", "Tarwestro"),
    591: ("aardappel", "Aardappelen, vers"),
    105: ("bostel", "Bierbostel, gedroogd"),
    213: ("lijnzaad-schroot", "Lijnzaadschroot"),
    301: ("raapzaad-schroot", "Raapzaadschroot - RE < 370 g/kg"),
    303: ("raapzaad-schroot", "Raapzaadschroot - RE > 370 g/kg"),
    343: ("soja-schroot", "Sojaschroot - HiPro, RC < 45, RE < 485 g/kg"),
    351: ("soja-schroot", "Sojaschroot - RC > 70 g/kg"),
    109: ("suikerbiet-pulp", "Bietenpulp, gedroogd - SUI < 100 g/kg"),
    397: ("zemelen", "Tarwemaalderijproducten - Tarwezemelen"),
    505: ("aardappel-stoomschillen", "Aardappelstoomschillen, vers en kuil - ZETam < 350 g/kg DS"),
    511: ("aardappel-stoomschillen", "Aardappelstoomschillen, vers en kuil - ZETam > 600 g/kg DS"),
    559: ("zuivelnevenstroom", "Kaaswei, vers - RE < 175 g/kg DS"),
}


def open_pdf():
    path = PDF if PDF.exists() else FALLBACK
    if not path.exists():
        sys.exit(f"FAIL: the CVB PDF is not on disk. Raw inputs are gitignored - download "
                 f"https://www.cvbdiervoeding.nl/bestand/10900/cvb-veevoedertabel-20232.pdf.ashx "
                 f"to {PDF}")
    return pdfplumber.open(path)


def parse_sheet(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """-> (product title, [(label, mean, sd), ...]) for the blocks we take."""
    lines = [l.rstrip() for l in text.split("\n")]
    title = lines[0].strip() if lines else ""
    out: list[tuple[str, str, str]] = []
    i = 0
    while i < len(lines) - 1:
        head = lines[i].split()
        # a header line is a run of known labels; the next line starts with gem.
        if head and lines[i + 1].startswith("gem."):
            vals = lines[i + 1].split()[1:]
            sds = lines[i + 2].split()[1:] if i + 2 < len(lines) and lines[i + 2].startswith("sdc") else []
            if len(vals) >= len(head):
                for j, label in enumerate(head):
                    v = vals[j] if j < len(vals) else "-"
                    sd = sds[j] if j < len(sds) else "-"
                    out.append((label, v, sd))
            i += 2
            # CVB repeats the amino-acid and fatty-acid blocks lower down; stop there
            if "Verteringscoefficient" in text[:text.find(lines[i])] if lines[i:] else False:
                break
        i += 1
    return title, out


def emit() -> None:
    rows = []
    with open_pdf() as pdf:
        for page, (code, variant) in sorted(PAGES.items()):
            text = pdf.pages[page - 1].extract_text() or ""
            title, cells = parse_sheet(text)
            # everything after the digestibility block is animal-nutrition, not composition
            cut = text.find("Verteringscoefficient")
            head_text = text[:cut] if cut > 0 else text
            _, cells = parse_sheet(head_text)
            for label, val, sd in cells:
                m = WEENDE.get(label) or None
                if m:
                    param, unit, basis, method, note = m
                elif label in MINERALS:
                    param, unit = MINERALS[label]; basis, method, note = "dry", "", ""
                elif label in TRACE:
                    param, unit = TRACE[label]; basis, method, note = "dry", "", ""
                else:
                    continue
                if val in ("-", "", None):
                    continue
                rows.append(dict(
                    stream_code=code, parameter_code=param, value_type="point",
                    value_num=val, value_min="", value_max="",
                    sd="" if sd in ("-", "") else sd, n_samples="",
                    unit_code=unit, basis_code=basis, method_code=method,
                    value_origin="measured", source_key="cvb-veevoedertabel-2023",
                    source_ref=f"CVB Veevoedertabel 2023, p. {page}", year="2023",
                    reported_label=label, variant=f"{title.rsplit(' ', 1)[0]} ({variant})",
                    restatement="no", flag="", transcription="machine", DECISION="",
                    notes=note,
                ))

    out = ROOT / "extraction" / "cvb_rows.csv"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), delimiter=";", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    out.write_text(buf.getvalue(), encoding="utf-8-sig")
    per: dict[str, int] = {}
    for r in rows:
        per[r["stream_code"]] = per.get(r["stream_code"], 0) + 1
    print(f"wrote {out}: {len(rows)} rows over {len(per)} streams")
    for c, n in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {c}")


def main() -> None:
    if "--find" in sys.argv:
        needle = sys.argv[sys.argv.index("--find") + 1].lower()
        with open_pdf() as pdf:
            for i, p in enumerate(pdf.pages):
                t = (p.extract_text() or "").split("\n")
                if t and needle in t[0].lower():
                    print(f"{i + 1:>4}  {t[0][:80]}")
    elif "--page" in sys.argv:
        n = int(sys.argv[sys.argv.index("--page") + 1])
        with open_pdf() as pdf:
            print((pdf.pages[n - 1].extract_text() or "")[:1400])
    elif "--emit" in sys.argv:
        emit()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
