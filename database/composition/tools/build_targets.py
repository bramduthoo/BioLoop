"""Round 2 targets: read the selection deliverable, apply the reviewer's 50 kt rule.

    ../.venv/Scripts/python tools/build_targets.py   ->  ../extraction/round2_targets.csv

THE RULE (reviewer, 2026-09-11). The selection lists commodities, and for some of them
the fractions beneath. A high-ranking commodity drags its own small fractions into the
list -- aardappel is #3, and `voerzetmeel` at 23.905 t rides in behind it. So:

    where a commodity has FRACTIONS, take only the fractions at >= 50.000 t/yr;
    where it has none, the commodity itself is the target.

Then the whole list is worked in DESCENDING TONNAGE ORDER. That ordering matters more
than the cut-off: it means the mass is covered first whatever the budget turns out to
be, and it makes the reading of the rule almost irrelevant for the items that count.
Targets below 50 kt are still written out, marked `below_threshold`, so the tail is
visible rather than silently dropped -- and so a later session can extend downward
without re-deriving the list.

TWO NAMES, ONE MATERIAL. GeNeSys and MONBIO name the same field residue differently:
GeNeSys writes *blad- en stengelmassa* / *stengelmassa* / *bladmassa*, MONBIO writes
*loof* / *stokken*. 2c settled that these are one object, so they are collapsed here
too and the larger figure is carried. Not collapsing them would give BioMobi two stream
rows for one material -- the exact error the object grain rule exists to prevent.

STREAM CODES ARE PROVISIONAL. BioMobi holds 20 `stream` rows, from the top-13 selection
of 2026-09-04. Most round-2 targets have no row yet. The code proposed here is what the
`streams/` pipeline would generate; the composition load stays blocked on that pipeline
being re-run against this newer selection, and the loader will refuse a stream_code that
does not exist. That is the correct failure, not a problem to work around.
"""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SELECTION = ROOT.parent / "register" / "deliverables" / "BIOLOOP_stream_selection_2026-09-11.xlsx"
OUT = ROOT / "extraction" / "round2_targets.csv"

THRESHOLD = 50_000

# GeNeSys wording -> MONBIO wording. One material, two nomenclatures (settled in 2c).
FRACTION_ALIAS = {
    "blad- en stengelmassa": "loof",
    "bladmassa (groene deel)": "loof",
    "bladmassa": "loof",
    "stengelmassa": "stokken",
}

# where the generated code would be wrong or unhelpful, the human overrides it
CODE_OVERRIDE = {
    ("Kool- en raapzaad", "geen fractie benoemd"): "raapzaad-schroot",
    ("Aardappel", "geen fractie benoemd|Voedingsindustrie"): "aardappel-industrieresidu",
    ("Aardappel", "geen fractie benoemd|Primaire productie"): "aardappel",
    ("Suikerbiet", "pulp"): "suikerbiet-pulp",
    ("Spruiten", "stokken"): "spruitstokken",
    ("Lijnzaad", ""): "lijnzaad-schroot",
    ("Soja", ""): "soja-schroot",
    ("Zonnebloem", ""): "zonnebloem-schroot",
    ("Mais", ""): "mais-stro",
    ("Tarwe", ""): "tarwe-stro",
    ("Zemelen", ""): "zemelen",
    ("Zetmeel", ""): "zetmeel-reststroom",
}


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"\[.*?\]", "", t).strip().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t


def clean(name: str) -> str:
    """Strip the tree glyphs and the [BE]/[BE+VL] geography marker off a label."""
    n = str(name).lstrip("·•└─├- ").strip()
    return re.sub(r"\s*\[[^\]]*\]\s*", " ", n).strip()


def geography(name: str) -> str:
    m = re.search(r"\[([^\]]*)\]", str(name))
    return m.group(1) if m else "VL"


def main() -> None:
    wb = openpyxl.load_workbook(SELECTION)
    ws = wb["Selectie"]
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows) if r and str(r[0]).strip() == "#")
    hdr = [str(c).strip() if c is not None else "" for c in rows[hdr_i]]
    col = {h: i for i, h in enumerate(hdr)}

    groups: dict[int, dict] = {}
    rank = None
    for r in rows[hdr_i + 1:]:
        if not r or r[1] is None or str(r[1]).strip() == "":
            continue
        if r[0] not in (None, ""):
            rank = int(r[0])
            groups[rank] = {
                "commodity": clean(r[1]),
                "geo": geography(r[1]),
                "max": float(r[col["hoogste cijfer"]] or 0),
                "chain": str(r[col["ketenschakel"]] or ""),
                "branch": str(r[col["tak"]] or ""),
                "fractions": [],
            }
        else:
            groups[rank]["fractions"].append({
                "label": clean(r[1]),
                "geo": geography(r[1]),
                "max": float(r[col["hoogste cijfer"]] or 0),
                "chain": str(r[col["ketenschakel"]] or ""),
            })

    targets = []
    for rank in sorted(groups):
        g = groups[rank]
        if not g["fractions"]:
            targets.append(dict(rank=rank, commodity=g["commodity"], fraction="",
                                geo=g["geo"], tonnes=g["max"], chain=g["chain"],
                                branch=g["branch"], note=""))
            continue

        # collapse the two-name pairs onto the MONBIO wording, keeping the larger figure
        merged: dict[tuple[str, str], dict] = {}
        for f in g["fractions"]:
            label = FRACTION_ALIAS.get(f["label"], f["label"])
            # a no-fraction row is the commodity itself; keep its chain stage apart,
            # because primary-production and food-industry rows are different materials
            key = (label, f["chain"].split("(")[0].strip() if label.startswith("geen fractie") else "")
            prev = merged.get(key)
            if prev is None or f["max"] > prev["max"]:
                merged[key] = dict(f, label=label,
                                   alias=(f["label"] if f["label"] != label else ""))
            elif f["label"] != label and not prev.get("alias"):
                prev["alias"] = f["label"]

        for (label, chainkey), f in merged.items():
            note = ""
            if f.get("alias"):
                note = (f"two source names for one material, collapsed: "
                        f"{f['alias']} (GeNeSys) = {label} (MONBIO)")
            targets.append(dict(rank=rank, commodity=g["commodity"], fraction=label,
                                geo=f["geo"], tonnes=f["max"], chain=f["chain"],
                                branch=g["branch"], note=note))

    # propose a stream code
    for t in targets:
        frac = t["fraction"]
        key = (t["commodity"], frac if not frac.startswith("geen fractie")
               else f"{frac}|{t['chain'].split('(')[0].strip()}" if frac else frac)
        code = CODE_OVERRIDE.get((t["commodity"], frac)) or CODE_OVERRIDE.get(key)
        if not code:
            if not frac or frac.startswith("geen fractie"):
                code = slug(t["commodity"])
            else:
                code = f"{slug(t['commodity'])}-{slug(frac)}"
        t["stream_code"] = code
        t["status"] = "todo" if t["tonnes"] >= THRESHOLD else "below_threshold"

    targets.sort(key=lambda t: -t["tonnes"])

    fields = ["stream_code", "rank", "commodity", "fraction", "geo", "tonnes", "chain",
              "branch", "status", "sources_found", "rows_extracted", "note"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n",
                       extrasaction="ignore")
    w.writeheader()
    for t in targets:
        t.setdefault("sources_found", "")
        t.setdefault("rows_extracted", "")
        t["tonnes"] = int(round(t["tonnes"]))
        w.writerow(t)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(buf.getvalue(), encoding="utf-8-sig")

    todo = [t for t in targets if t["status"] == "todo"]
    print(f"{len(targets)} targets, {len(todo)} at or above {THRESHOLD:,} t/yr")
    print(f"covered mass (>= threshold): {sum(t['tonnes'] for t in todo):,} t/yr")
    print(f"wrote {OUT}\n")
    for t in todo:
        print(f"  {t['tonnes']:>9,}  {t['stream_code']:<32} #{t['rank']:<3} "
              f"{t['commodity']}{(' / ' + t['fraction']) if t['fraction'] else ''}")


if __name__ == "__main__":
    main()
