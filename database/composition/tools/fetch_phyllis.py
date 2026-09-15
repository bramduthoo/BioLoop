"""Phyllis2 (TNO) harvester -- the whole index, then the records we decided to take.

    ../.venv/Scripts/python tools/fetch_phyllis.py --index          # refresh the index cache
    ../.venv/Scripts/python tools/fetch_phyllis.py --grep potato    # search it
    ../.venv/Scripts/python tools/fetch_phyllis.py                  # extract RECORDS -> csv

WHY THIS EXISTS AS A TOOL AND NOT AS A SESSION'S BROWSING. Rounds 1-3 searched Phyllis2
by typing words into its search box, and it cost us three times: `animal fat` and `meat
and bone meal` sat there through two rounds of "no source for the animal streams", and
`potato shreds, sorting waste` sat there through a round of "Feedipedia has no raw
cuttings". The same failure as the CVB page scan that stepped over p. 658 -- A SAMPLING
STRIDE IS NOT A SEARCH. Phyllis2 publishes /Browse/PlainList, every record in one page,
so the index is cached here and grepped. What a future session can no longer say is
"Phyllis2 has nothing for X" without having grepped for X.

THE ar COLUMN IS NEVER TAKEN, AND THE PAGE ITSELF SAYS WHY. Phyllis prints each
determination on `ar` / `dry` / `daf`, but only some of those are STORED: the rest carry
a `data-phyllis-expression` attribute and an empty cell, and the browser computes them
from the stored one. A computed cell is a restatement of a value we already have, not a
second measurement, so the parser takes stored cells only -- which is the machine-checkable
version of the rule composition/CLAUDE.md states for lhv, where the restatement is NOT a
multiplication and reproducing it by hand would be wrong.

WHAT A RECORD'S `Method` COLUMN BUYS. Phyllis prints the determination beside the value:
`van Soest` against one wheat-bran cellulose and `Sugar Analysis` against another, whose
figures differ (12,00 vs 13,80 wt% dry). That is the method axis doing exactly the work it
was introduced for -- two determinations of one analyte, not two analytes -- so it lands on
`method_code` and not in a note. Where Phyllis says only `Measured`, `Calculated`,
`Unknown` or `Average`, that is a value_origin and not a method, and method_code stays
NULL rather than being guessed.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "phyllis"
OUT = ROOT / "extraction" / "phyllis_rows.csv"

BASE = "https://phyllis.nl"
UA = {"User-Agent": "Mozilla/5.0 (BIOLOOP research harvest; contact bram.duthoo@gmail.com)"}

SOURCE_KEY = "phyllis2-tno"


# ---------------------------------------------------------------------------
# WHAT WE TAKE, AND WHAT WE LOOKED AT AND REFUSED.
#
# Both halves are the record. A rejected record with its reason is worth as much as a
# taken one -- it is what stops the next session re-finding it and taking it.
# ---------------------------------------------------------------------------

RECORDS: dict[int, tuple[str, str]] = {
    # id: (stream_code, variant label)
    428:  ("zuivelnevenstroom", "Whey, BIOBIB compilation"),
    1066: ("aardappel-snippers", "Potato shreds, sorting waste"),   # taken in round 4
    1067: ("aardappel", "Potato sorting waste"),
    2540: ("zemelen", "Wheat bran, ATO laboratories analysis 282"),
    2593: ("soja-schroot", "Soya bean meal"),
    2595: ("bostel", "Brewers grains"),
    2622: ("suikerbiet-loof", "Sugarbeet, leaves and tops"),
    2623: ("suikerbiet-loof", "Sugarbeet, leaves and tops, 90 days ensilaged"),
    3491: ("dierlijk-vet", "Animal fat, Rotterdam NL"),             # taken in round 4
    3492: ("niet-eetbare-slachtafvallen", "Meat and bone meal, Rotterdam NL"),
    3578: ("bostel", "Brewery spent grains, Biofficiency, untreated"),
}

REJECTED: dict[int, str] = {
    2389: "wheat bran, but its literature is the CORNELL SUBSTRATE COMPOSITION TABLE -- a "
          "composting teaching resource. The reviewer's condition on compilations (2026-09-09) "
          "is that they carry a sample basis: mean, SD, min, max, n. This one carries none of "
          "them, so it fails the condition that let Feedipedia in. #2540 covers the same "
          "material from a named laboratory.",
    3486: "Rapeseed CAKE, not schroot. Cake is pressed and keeps its residual oil; schroot is "
          "solvent-extracted. The record proves it rather than assuming it -- C 53,50 wt% dry, "
          "H 7,30 and LHV 22,69 MJ/kg are an oilseed with the oil still in it, against CVB's "
          "extracted meal at far less. Same error as putting potato on potato peel.",
    2817: "`rapeseed residues` is rapeseed STRAW (`Residues collected from fields`). BioMobi has "
          "no object for it: rape/cabbage straw is inside the 80% line at about 5 kt/yr and is "
          "exactly what the 50 kt/yr fraction filter exists to keep out.",
    3579: "the same Biofficiency spent grains as #3578 but HTC-treated at 280 degC for 4 h. That "
          "is a CONVERSION PRODUCT, not the stream -- LHV 30,93 against 19,94 MJ/kg dry. A "
          "process output is not a composition of the input.",
    1564: "`cauliflower`, but the plant part is unstated and the literature is the 1993 Dutch "
          "GFT household-waste survey. bloemkool-loof is specifically the LEAF. Same ground as "
          "the Brussels sprouts rejection in round 4.",
    1565: "as #1564.",
    1566: "as #1564 -- eight heavy metals, plant part still unstated.",
    1567: "`potato` from the same 1993 GFT survey. Household potato waste is mostly PEEL, and "
          "BioMobi has no peel object until G-10 closes. Four heavy metals, no plant part.",
    1568: "as #1567.",
    1569: "as #1567.",
    1570: "`potato`, and this one Phyllis itself files under NTA [522] aardappelSCHILLEN. It is "
          "peel, which is the object G-10 has not yet created. LOCATED, not lost: eight heavy "
          "metals on dry, ready to attach the day the register splits the peel out.",
    1065: "`potato fibres` -- starch-industry material, so it belongs to zetmeel-reststroom, "
          "which is BLOCKED on G-19. Cellulose 26,00 / hemicellulose 11,80 / protein 14,90 / "
          "starch 17,10 / pectin 15,30 wt% dry, Beldman et al. 1983. LOCATED AND HELD.",
    1068: "`potato rests`, same 1997 confidential ECN report as #1066/#1067, same blocked "
          "object. Cellulose 26,00 / hemicellulose 11,80 / starch 40,00 wt% dry. LOCATED AND HELD.",
    2841: "`potato mash` is mashed potato prepared as an ETHANOL FERMENTATION FEEDSTOCK "
          "(Srichuwong et al. 2009), not a side stream. Not zetmeel-reststroom either.",
}


# ---------------------------------------------------------------------------
# Property -> catalogue. Phyllis's own wording on the left, exactly as printed.
# ---------------------------------------------------------------------------

PROPERTY = {
    "Moisture content": ("moisture", None),
    "Ash content": ("ash", None),
    "Ash content at 550°C": ("ash", "ash-550"),
    "Volatile matter": ("volatile_matter", None),
    "Fixed carbon": ("fixed_carbon", None),
    "Carbon": ("total_carbon", None),
    "Hydrogen": ("hydrogen", None),
    "Oxygen": ("oxygen", None),
    "Nitrogen": ("total_nitrogen", None),
    "Sulphur": ("sulphur", None),
    "Chlorine (Cl)": ("chlorine", None),
    "Bromine (Br)": ("bromine", None),
    "Fluorine (F)": ("fluorine", None),
    "Net calorific value (LHV)": ("lhv", None),
    "Gross calorific value (HHV)": ("hhv", None),
    "Cellulose": ("cellulose", None),
    "Hemicellulose": ("hemicellulose", None),
    "Lignin": ("lignin", None),
    "Acid insoluble lignin (Klason) (AIL)": ("acid_insoluble_lignin", "lignin-klason"),
    "Acid soluble lignin (ASL)": ("acid_soluble_lignin", None),
    "Pectin": ("pectin", None),
    "Starch": ("starch", None),
    "Protein": ("crude_protein", None),
    "Lipids": ("fat_total", None),
    "Extractives EtOH/toluene": ("extractives", "extr-etoh-toluene"),
    "Extractives 95% EtOH": ("extractives", "extr-etoh-95"),
    "Extractives hot water": ("extractives", "extr-hot-water"),
    "Arabinan": ("arabinan", None),
    "Xylan": ("xylan", None),
    "Mannan": ("mannan", None),
    "Galactan": ("galactan", None),
    "Glucan": ("glucan", None),
    "Rhamnan": ("rhamnan", None),
    "Sum C5": ("c5_sugars_total", None),
    "Sum C6": ("c6_sugars_total", None),
    "Total non-structural carbo-hydrates (TNC)": ("tnc", None),
    "Cadmium (Cd)": ("cadmium", None),
    "Lead (Pb)": ("lead", None),
    "Arsenic (As)": ("arsenic", None),
    "Chromium (Cr)": ("chromium", None),
    "Copper (Cu)": ("copper", None),
    "Mercury (Hg)": ("mercury", None),
    "Nickel (Ni)": ("nickel", None),
    "Zinc (Zn)": ("zinc", None),
    "IDT (initial deformation temperature)": ("ash_melting_dt", "ash-melt-astm"),
    "SOT (softening or spherical temperature)": ("ash_melting_st", "ash-melt-astm"),
    "HT (hemispherical temperature)": ("ash_melting_ht", "ash-melt-astm"),
    "FT (fluid temperature)": ("ash_melting_ft", "ash-melt-astm"),
    "SH (shrinkage temperature)": ("ash_melting_sh", "ash-melt-cen"),
    "DEF (deformation temperature)": ("ash_melting_dt", "ash-melt-cen"),
    "HE (hemispherical temperature)": ("ash_melting_ht", "ash-melt-cen"),
    "FL (flow temperature)": ("ash_melting_ft", "ash-melt-cen"),
}

# Phyllis prints one of these where a method would go. They are a value_origin, not a
# determination: recording `Measured` as a method would be recording nothing.
ORIGIN_WORDS = {
    "Measured": "measured",
    "Calculated": "calculated",
    "Unknown": "unknown",
    "Average": "measured",
}

# ...and these ARE determinations.
METHOD_WORDS = {
    "van Soest": "fibre-van-soest",
    "Sugar Analysis": "fibre-sugar-analysis",
}

# A parameter Phyllis computes rather than determines, whatever its Method cell says.
ALWAYS_CALCULATED = {"fixed_carbon", "c5_sugars_total", "c6_sugars_total"}

# Phyllis's ash-free restatement. Not a determination of anything; see the module docstring.
SKIP_PROPERTY = {
    "Total (with halides)",      # a checksum over the ultimate analysis, not a property
    "Total ash + biochemical",   # likewise over the biochemical block
    "HHVMilne",                  # a correlation from C/H/O, not a bomb-calorimeter figure
}

BASIS = {0: "fresh", 1: "dry", 2: "dry_ash_free"}

# Filled by parse_record: (record id, parameter, the string as printed). See the refusal
# in parse_record for why these are not rows.
CENSORED: list[tuple[int, str, str]] = []


class _Table(HTMLParser):
    """Rows of (text, attrs) cells, which is all the shape this page needs."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[tuple[str, dict]]] = []
        self._row: list | None = None
        self._cell: list | None = None
        self._attrs: dict = {}

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell, self._attrs = [], dict(attrs)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(("".join(self._cell).strip(), self._attrs))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def fetch(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", "replace")
    dest.write_text(text, encoding="utf-8")
    return text


def refresh_index() -> Path:
    """/Browse/PlainList is every record in the database, on one page."""
    dest = RAW / "index.html"
    if dest.exists():
        dest.unlink()
    fetch(f"{BASE}/Browse/PlainList", dest)
    pairs = re.findall(r'/Biomass/View/(\d+)">([^<]+)', dest.read_text(encoding="utf-8"))
    tsv = RAW / "index.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as fh:
        for rid, name in pairs:
            fh.write(f"{rid}\t{html.unescape(name).strip()}\n")
    print(f"index: {len(pairs)} records -> {tsv}")
    return tsv


def grep_index(pattern: str) -> None:
    tsv = RAW / "index.tsv"
    if not tsv.exists():
        sys.exit("no index cached -- run with --index first")
    rx = re.compile(pattern, re.I)
    hits = [ln for ln in tsv.read_text(encoding="utf-8").splitlines() if rx.search(ln)]
    for ln in hits:
        print(" ", ln)
    print(f"{len(hits)} of {len(tsv.read_text(encoding='utf-8').splitlines())} records")


def _clean(num: str) -> str:
    """Phyllis thin-spaces its thousands: `1 430` is 1430."""
    return num.replace(" ", "").replace(" ", "")


def parse_record(rid: int) -> tuple[dict, list[dict]]:  # noqa: C901
    raw = fetch(f"{BASE}/Biomass/View/{rid}", RAW / f"{rid}.html")
    raw = re.sub(r"<script.*?</script>", "", raw, flags=re.S)
    p = _Table()
    p.feed(raw)

    meta: dict[str, str] = {}
    values: list[dict] = []
    for row in p.rows:
        # A value row is preceded by one `indent` cell per nesting level of the heading
        # tree it sits under, so the property is never at a fixed index.
        cells = [(html.unescape(re.sub(r"\s+", " ", t)).strip(), a) for t, a in row]
        while cells and "indent" in cells[0][1].get("class", "") and not cells[0][0]:
            cells.pop(0)
        if not cells:
            continue
        texts = [c[0] for c in cells]

        if len(cells) == 2 and texts[0] and "number" not in cells[1][1].get("class", ""):
            meta.setdefault(texts[0], texts[1])
            continue
        prop = texts[0]
        if prop in SKIP_PROPERTY or prop not in PROPERTY:
            continue
        param, fixed_method = PROPERTY[prop]

        # The unit cell may pin the basis in brackets: `wt% (ar)`, `mg/kg (dry)`.
        m = re.match(r"([^()]+?)\s*(?:\((ar|dry|daf)\))?$", texts[1] if len(cells) > 1 else "")
        unit = (m.group(1) if m else "").strip()
        pinned = m.group(2) if m and m.group(2) else None

        # Walk the three basis columns by COLSPAN, not by index: a pinned-basis row
        # carries one `colspan=3` cell where an unpinned one carries three.
        col, taken = 0, []
        rest = cells[2:]
        while rest and col < 3:
            text, attrs = rest.pop(0)
            span = int(attrs.get("colspan", 1) or 1)
            taken.append((col, text, attrs.get("class", "")))
            col += span
        tail = [t for t, _ in rest]                      # Std dev, Det lim, Lab, Date, Method, Remarks
        method_cell = tail[4] if len(tail) > 4 else ""
        note = " | ".join(t for t in tail[2:] if t and t != method_cell).strip()

        origin = ORIGIN_WORDS.get(method_cell, "measured")
        method = fixed_method or METHOD_WORDS.get(method_cell)
        if param in ALWAYS_CALCULATED:
            origin = "calculated"
        if method_cell and method_cell not in ORIGIN_WORDS and method_cell not in METHOD_WORDS:
            note = (method_cell + (" | " + note if note else "")).strip()

        for idx, text, cls in taken:
            if not text:
                continue
            if "ar-value" in cls:
                continue      # derived client-side -- see the module docstring
            if text.lstrip().startswith("<"):
                # A CENSORED VALUE, and the decision on it is round 4's, unchanged: the
                # schema holds a point or an observed spread, and `< 1 mg/kg` is neither.
                # Recorded here as a refusal with its number intact rather than dropped
                # silently, because how many there are is itself worth knowing.
                CENSORED.append((rid, param, text))
                continue
            if pinned:
                basis = {"ar": "fresh", "dry": "dry", "daf": "dry_ash_free"}[pinned]
            elif "water-value" in cls:
                basis = "fresh"      # moisture is only ever reported as received
            else:
                basis = BASIS.get(idx, "unknown")
            values.append(dict(parameter_code=param, unit=unit, value=_clean(text),
                               basis=basis, method_code=method or "",
                               value_origin=origin, reported_label=prop, notes=note))
    return meta, values


UNIT = {"wt%": "%", "MJ/kg": "MJ/kg", "mg/kg": "mg/kg", "°C": "degC", "": "unknown"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", action="store_true", help="refresh the cached index")
    ap.add_argument("--grep", help="search the cached index")
    args = ap.parse_args()

    if args.index:
        refresh_index()
        return
    if args.grep:
        grep_index(args.grep)
        return

    rows = []
    for rid, (stream, label) in sorted(RECORDS.items()):
        meta, values = parse_record(rid)
        lit = meta.get("Literature", "")
        year = ""
        ym = re.findall(r"\((\d{4})\)", lit) or re.findall(r"\b(19|20)\d{2}\b", lit)
        if ym:
            year = ym[-1] if len(ym[-1]) == 4 else ""
        for v in values:
            unit = UNIT.get(v["unit"], v["unit"])
            if unit == "unknown" and v["unit"]:
                sys.exit(f"#{rid}: unmapped unit {v['unit']!r} on {v['parameter_code']}")
            rows.append(dict(
                stream_code=stream, parameter_code=v["parameter_code"],
                value_type="point", value_num=v["value"], value_min="", value_max="",
                sd="", n_samples="", unit_code=unit, basis_code=v["basis"],
                method_code=v["method_code"], value_origin=v["value_origin"],
                source_key=SOURCE_KEY, source_ref=f"Phyllis2 record #{rid}",
                year=year, reported_label=v["reported_label"], variant=label,
                restatement="no", flag="", transcription="machine", DECISION="",
                notes=(v["notes"] + (" | " if v["notes"] and lit else "") + lit)[:900],
            ))
        print(f"  #{rid:>5}  {stream:<28} {len(values):>3} values  {label}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), delimiter=";",
                       lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    OUT.write_text(buf.getvalue(), encoding="utf-8-sig")
    streams = {r["stream_code"] for r in rows}
    print(f"\nwrote {OUT}: {len(rows)} rows over {len(streams)} streams")
    print(f"{len(REJECTED)} records looked at and refused -- see REJECTED in this file")
    if CENSORED:
        print(f"\n{len(CENSORED)} BELOW-DETECTION-LIMIT values not recorded "
              f"(round 4's rule, now enforced by code rather than by memory):")
        for rid, param, text in CENSORED:
            print(f"    #{rid}  {param:<22} {text}")
        print("    REVIEWER DECISION OPEN: these are mostly heavy metals, and `below the "
              "detection limit` is\n    a real and useful claim about a material headed for "
              "combustion. If the schema should hold\n    them, the shape is value_max with "
              "no value_min -- say so and they become rows.")


if __name__ == "__main__":
    main()
