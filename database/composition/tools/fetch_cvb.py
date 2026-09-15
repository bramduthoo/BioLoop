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
    "DS":    ("dry_matter", "g/kg", "fresh", "", "CVB gives dry matter per kg product"),
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
    # Added after reading CVB's OWN definitions rather than guessing at the abbreviations.
    # `REin` is deliberately NOT here: section 3 says it equals RE except for roughages and
    # moist concentrates, so mapping it would register one determination twice.
    "OKh":   ("nfe", "g/kg", "dry", "nfe-vs-hydrolysed-fat",
              "CVB's OKh - the same by-difference remainder as OK, but subtracting RVETh"),
    "GOS":   ("oligosaccharides", "g/kg", "dry", "", "CVB's GOS, the raffinose family"),
    "NSPh":  ("nsp", "g/kg", "dry", "",
              "CVB section 4.2.2.5: NOT determined, computed as OS - RE - RVETh - ZETam - GOS "
              "- CF_DI*SUI. CVB warns the result can be negative"),
    "RNSP":  ("nsp_residual", "g/kg", "dry", "",
              "CVB section 3.4.2.7: rest-NSP = NSP - NDF. Computed, not determined"),
}

# CVB computes these rather than determining them, and says so in its own methodology
# chapter. Recording them as `measured` would be the quiet fabrication value_origin exists
# to prevent.
CVB_CALCULATED = {"nfe", "nsp", "nsp_residual"}
MINERALS = {
    "Ca": ("calcium", "g/kg"), "P": ("phosphorus", "g/kg"), "Mg": ("magnesium", "g/kg"),
    "K": ("potassium", "g/kg"), "Na": ("sodium", "g/kg"), "Cl": ("chloride", "g/kg"),
    "S": ("sulphur", "g/kg"), "IP": ("phytate_phosphorus", "g/kg"),
}
TRACE = {"Fe": ("iron", "mg/kg"), "Mn": ("manganese", "mg/kg"), "Zn": ("zinc", "mg/kg"),
         "Cu": ("copper", "mg/kg"), "Se": ("selenium", "mg/kg"),
         "Mo": ("molybdenum", "mg/kg"), "J": ("iodine", "mg/kg"),
         "Co": ("cobalt", "mg/kg")}

# The amino-acid block sits on the FACING page of each product, laid out as
#   NAME  <g/16g N gem>  <sdc>  <g/kg>  <VC pigs> <g/kg> <VC poultry> <g/kg>
# Only the third number is taken. The first is an EXPRESSION relative to protein, not a
# unit; everything from the fourth column on is standardised ileal digestibility, which is
# a fact about a material AND an animal and belongs to the model's rule layer.
AMINO = {
    "LYS": "lysine", "MET": "methionine", "CYS": "cystine", "THR": "threonine",
    "TRP": "tryptophan", "ILE": "isoleucine", "ARG": "arginine", "PHE": "phenylalanine",
    "HIS": "histidine", "LEU": "leucine", "TYR": "tyrosine", "VAL": "valine",
    "ALA": "alanine", "ASP": "aspartic_acid", "GLU": "glutamic_acid", "GLY": "glycine",
    "PRO": "proline", "SER": "serine",
}
AMINO_NOTE = {
    "CYS": "CVB prints CYS - cystine, or cysteine plus half-cystine; the source does not say which",
    "ASP": "CVB prints ASP - in a hydrolysate this is aspartic acid plus asparagine",
    "GLU": "CVB prints GLU - in a hydrolysate this is glutamic acid plus glutamine",
}


# The FATTY-ACID block sits on the same facing page as the amino acids, laid out as
#   LABEL  <% of total fatty acids>  <g/kg>
# Only the second is taken. A percentage OF THE FATTY ACIDS is a share of a sum, not a
# content: it cannot be compared across materials and it changes when the fat content
# does. `RVET(h)` heads the block with the fat itself and is already captured from the
# Weende block, so it is skipped here rather than recorded twice.
FATTY = {
    "<=C10": "fa_c10_or_less", "C12:0": "fa_c12_0", "C14:0": "fa_c14_0",
    "C16:0": "fa_c16_0", "C16:1": "fa_c16_1", "C18:0": "fa_c18_0",
    "C18:1": "fa_c18_1", "C18:2": "fa_c18_2", "C18:3": "fa_c18_3",
    ">=C20": "fa_c20_or_more",
}


def parse_fatty(text: str) -> list[tuple[str, str, str, str, str]]:
    """-> [(parameter, unit, value, sd, note), ...] from the facing page's Vetzuren block."""
    out = []
    for line in text.split("\n"):
        parts = line.split()
        if len(parts) < 3:
            continue
        if parts[0] == "Som" and parts[1] == "VZ":
            val = parts[3] if len(parts) > 3 else "-"
            if val not in ("-", ""):
                out.append(("fatty_acids_total", "g/kg", val, "",
                            "CVB's own sum of the fatty acids it measured - not recomputed here"))
            continue
        name = FATTY.get(parts[0])
        if not name:
            continue
        absolute = parts[2]
        if absolute in ("-", ""):
            continue
        out.append((name, "g/kg", absolute, "", ""))
    return out


def parse_amino(text: str, basis: str) -> list[tuple[str, str, str, str, str]]:
    """-> [(parameter, unit, value, sd, note), ...] from the facing page's amino-acid block."""
    out = []
    for line in text.split("\n"):
        parts = line.split()
        if len(parts) < 4 or parts[0] not in AMINO and parts[0] != "SOM":
            continue
        if parts[0] == "SOM" and len(parts) >= 5 and parts[1] == "AZ":
            # SOM AZ <g/16gN> <g/kg> ...
            val = parts[3]
            if val not in ("-", ""):
                out.append(("amino_acids_total", "g/kg", val, "",
                            "CVB's own sum of the amino acids it measured - not recomputed here"))
            continue
        name = AMINO.get(parts[0])
        if not name:
            continue
        gem, sd, absolute = parts[1], parts[2], parts[3]
        if absolute in ("-", ""):
            continue
        # the sdc CVB prints belongs to the g/16g N column, not to the absolute figure,
        # so it is NOT carried onto this value - a standard deviation in the wrong unit is
        # worse than none
        out.append((name, "g/kg", absolute, "", AMINO_NOTE.get(parts[0], "")))
    return out

# CVB page -> BioMobi stream code. Only the 19 in-scope targets.
# SHEETS READ AND REFUSED. Each is the right commodity and the wrong object, and each is
# written down so the next session does not re-find it and take it.
#
#  653  `Kool (bloemkool)` - DS 72, RE 295, RAS 138, SUI 150, K 42,5 g/kg DS. The PLANT
#       PART IS UNSTATED, and CVB's own naming settles what that means: its sibling sheet
#       p. 658 says `kop+stengels` explicitly, so CVB qualifies the part when it means a
#       part. Unqualified `bloemkool` is the vegetable, and bloemkool-loof is the leaf.
#       Same ground as the Phyllis2 cauliflower records and the Brussels sprouts ones.
#  590  `Aardappelen, schillenkuil` - ensiled potato PEEL. BioMobi has no peel object
#       until G-10 closes. Located, not lost: DS 220, RAS 80, RE 93, RC 188, ZETew 500.
#  499  `Aardappelsnippers, voorgebakken` (and 501, 503) - PRE-FRIED cuttings, graded by
#       their fat. A processed product, not the raw side stream. p. 497 is the raw one.
#  664  `Maiskolvensilage` and 673-679 `Snijmais, kuil` - cob silage and whole-plant
#       silage. mais-stro is STOVER, the residue after the grain comes off. CVB HAS NO
#       MAIZE STOVER SHEET, checked over all 708 pages - which is why the largest stream
#       in the selection still has no CVB row.
#  449  `Vet/olie, Visolie` - fish oil is a different chain from rendered slaughter fat.
#  599, 600, 605, 607, 645, 668, 669  bean, pea, barley, oat, rape and rye straw. All
#       real sheets, none of them an object inside the 80% line.
#
# LOCATED AND HELD, BLOCKED ON G-19. The starch side streams are all here and they are
# the strongest argument yet for closing that gap: 513-527 potato starch in four
# concentration grades, 577-583 WHEAT starch in four, 493/495 potato press fibres,
# 491 potato juice. composition/CLAUDE.md warns that Flanders' starch industry is mostly
# WHEAT starch and that the potato-pulp literature is probably the wrong material -- CVB
# carries both, separately, so the moment the object is named the data is already found.

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
    419: ("dierlijk-vet", "Vet/olie, Dierlijk - 6% linolzuur"),
    421: ("dierlijk-vet", "Vet/olie, Dierlijk - 9% linolzuur"),
    # `kop+stengels` is head AND STEMS -- the stalk material, not the sprout. CVB keeps the
    # two apart on facing sheets (p. 657 is `spruitkool`, the sprout as a vegetable), which
    # is exactly the split BioMobi's objects need and which no other source made.
    658: ("spruitstokken", "Kool (spruitkool, kop+stengels)"),
    596: ("suikerbiet-loof", "Bietenblad, kuil"),
    # Found by reading EVERY sheet title in the PDF rather than a sample of them. The
    # same discipline that turned up p. 658; three of these four were sitting in a source
    # that had already been opened four times.
    497: ("aardappel-snippers", "Aardappelsnippers, rauw"),
    447: ("dierlijk-vet", "Vet/olie, Varkensvet"),
    589: ("aardappel", "Aardappelen, rauw, kuil"),
    465: ("zuivelnevenstroom", "Weipoeder"),
}


def open_pdf():
    path = PDF if PDF.exists() else FALLBACK
    if not path.exists():
        sys.exit(f"FAIL: the CVB PDF is not on disk. Raw inputs are gitignored - download "
                 f"https://www.cvbdiervoeding.nl/bestand/10900/cvb-veevoedertabel-20232.pdf.ashx "
                 f"to {PDF}")
    return pdfplumber.open(path)


def parse_sheet(text: str) -> tuple[str, list[tuple[str, str, str, str]]]:
    """-> (product title, [(label, mean, sd, basis), ...]) for the blocks we take.

    THE BASIS IS NOT CONSTANT ACROSS SHEETS, and reading it off each block header is the
    whole reason this function exists. CVB heads a block either `(g/kg DS)` or plain
    `(g/kg)`: the first is per kg DRY MATTER, the second per kg PRODUCT. Page 301
    (raapzaadschroot) is the second kind, and there RAS + RE + RVET + RC + OK = 882 g/kg,
    which is exactly its own DS figure -- the Weende partition closing on the product
    rather than on 1000. An earlier version assumed `dry` everywhere, and the
    Weende-closure check in `qc_values.py` is what caught it.
    """
    lines = [l.rstrip() for l in text.split("\n")]
    title = lines[0].strip() if lines else ""
    out: list[tuple[str, str, str, str]] = []
    basis = "dry"
    i = 0
    while i < len(lines) - 1:
        low = lines[i].lower().replace(" ", "")
        if "(g/kg" in low or "(mg/kg" in low:
            basis = "dry" if "ds)" in low else "fresh"
        head = lines[i].split()
        # a header line is a run of known labels; the next line starts with gem.
        if head and lines[i + 1].startswith("gem."):
            vals = lines[i + 1].split()[1:]
            sds = lines[i + 2].split()[1:] if i + 2 < len(lines) and lines[i + 2].startswith("sdc") else []
            if len(vals) >= len(head):
                for j, label in enumerate(head):
                    v = vals[j] if j < len(vals) else "-"
                    sd = sds[j] if j < len(sds) else "-"
                    out.append((label, v, sd, basis))
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
            # everything after the digestibility block is animal-nutrition, not composition
            cut = text.find("Verteringscoefficient")
            head_text = text[:cut] if cut > 0 else text
            title, cells = parse_sheet(head_text)
            # the Weende block's basis is the sheet's prevailing one
            sheet_default = next((b for lbl, _, _, b in cells if lbl == "RAS"), "dry")
            for label, val, sd, sheet_basis in cells:
                m = WEENDE.get(label) or None
                if m:
                    param, unit, _, method, note = m
                elif label in MINERALS:
                    param, unit = MINERALS[label]; method, note = "", ""
                elif label in TRACE:
                    param, unit = TRACE[label]; method, note = "", ""
                else:
                    continue
                basis = sheet_basis
                if param == "dry_matter":
                    # dry matter is a fraction OF the product, whatever the block header says
                    basis, note = "fresh", "CVB gives dry matter per kg product"
                if val in ("-", "", None):
                    continue
                rows.append(dict(
                    stream_code=code, parameter_code=param, value_type="point",
                    value_num=val, value_min="", value_max="",
                    sd="" if sd in ("-", "") else sd, n_samples="",
                    unit_code=unit, basis_code=basis, method_code=method,
                    value_origin=("calculated" if param in CVB_CALCULATED else "measured"),
                    source_key="cvb-veevoedertabel-2023",
                    source_ref=f"CVB Veevoedertabel 2023, p. {page}", year="2023",
                    reported_label=label, variant=f"{title.rsplit(' ', 1)[0]} ({variant})",
                    restatement="no", flag="", transcription="machine", DECISION="",
                    notes=note,
                ))

            # the amino-acid block is printed on the FACING page of the same product
            facing = pdf.pages[page].extract_text() or "" if page < len(pdf.pages) else ""
            if facing.startswith(text.split("\n")[0].rsplit(" ", 1)[0]):
                for param, unit, val, sd, note in (parse_amino(facing, sheet_default)
                                                   + parse_fatty(facing)):
                    rows.append(dict(
                        stream_code=code, parameter_code=param, value_type="point",
                        value_num=val, value_min="", value_max="", sd=sd, n_samples="",
                        unit_code=unit, basis_code=sheet_default, method_code="",
                        value_origin="measured", source_key="cvb-veevoedertabel-2023",
                        source_ref=f"CVB Veevoedertabel 2023, p. {page + 1}", year="2023",
                        reported_label=param, variant=f"{title.rsplit(' ', 1)[0]} ({variant})",
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
