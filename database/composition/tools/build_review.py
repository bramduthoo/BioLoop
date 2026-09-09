"""Build the composition review page from the extraction CSVs.

    ../.venv/Scripts/python tools/build_review.py     ->  ../build/review.html

The page is a pure function of ../extraction/*.csv plus ../vocabulary/parameters.csv,
so a later harvest round regenerates it with one command and nothing drifts. It is
published as an Artifact for the reviewer; their marks and remarks come back through
the artifact's own store, not through this file.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXTRACT = ROOT / "extraction"
BUILD = ROOT / "build"

# The 16 targets: the top 10 commodities of the register selection, at object grain.
# rank / commodity / commodity tonnage come from the register; they are carried, not
# recomputed (one derivation, and it lives in the register).
STREAMS = [
    ("mais-stro",          "Maisstro",                 1, "Mais",              1456062),
    ("raapzaad-stro",      "Kool- en raapzaadstro",    2, "Kool- en raapzaad",  857931),
    ("raapzaad-schroot",   "Kool- en raapzaadschroot", 2, "Kool- en raapzaad",  857931),
    ("aardappel",          "Aardappel",                3, "Aardappel",          855393),
    ("aardappel-loof",     "Aardappelloof",            3, "Aardappel",          855393),
    ("suikerbiet",         "Suikerbiet",               4, "Suikerbiet",         812224),
    ("suikerbiet-loof",    "Suikerbietenloof",         4, "Suikerbiet",         812224),
    ("suikerbiet-pulp",    "Bietenpulp",               4, "Suikerbiet",         812224),
    ("zetmeel-reststroom", "Zetmeelreststroom",        5, "Zetmeel",            284549),
    ("zemelen",            "Zemelen",                  6, "Zemelen",            278865),
    ("tarwe-stro",         "Tarwestro",                7, "Tarwe",              255836),
    ("lijnzaad-schroot",   "Lijnzaadschroot",          8, "Lijnzaad",           245000),
    ("bloemkool",          "Bloemkool",                9, "Bloemkool",          201311),
    ("bloemkool-loof",     "Bloemkoolloof",            9, "Bloemkool",          201311),
    ("bloemkool-harten",   "Bloemkoolharten",          9, "Bloemkool",          201311),
    ("soja-schroot",       "Sojaschroot",             10, "Soja",               170000),
]

SHORT = {
    "feedtables-inrae-cirad-afz-fao": "Feedipedia / feedtables",
    "phyllis2-tno": "Phyllis2 (TNO)",
    "deEvan2020Cauliflower": "De Evan et al. 2020, Animals",
}


def read(path: Path, **kw) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(fh, delimiter=";", **kw)]


def main() -> None:
    params = {p["code"]: p["name"] for p in read(ROOT / "vocabulary" / "parameters.csv")}
    meas = read(EXTRACT / "round1_measurements.csv")
    srcs = read(EXTRACT / "round1_sources.csv")
    nodata = read(EXTRACT / "round1_nodata.csv")

    unknown = sorted({m["parameter_code"] for m in meas if m["parameter_code"] not in params})
    if unknown:
        raise SystemExit(f"FAIL: measurement rows name parameters not in the catalogue: {unknown}")

    rows = [{
        "stream": m["stream_code"],
        "parameter": m["parameter_code"],
        "parameter_label": params[m["parameter_code"]],
        "value": m["value_num"],
        "min": m["value_min"],
        "max": m["value_max"],
        "sd": m["sd"],
        "n": m["n_samples"],
        "unit": m["unit_code"],
        "basis": m["basis_code"],
        "source_ref": m["source_ref"],
        "variant": m["variant"],
        "predicted": m["predicted"],
        "restatement": m["restatement"],
        "flag": m["flag"],
        "notes": m["notes"],
    } for m in meas]

    data = {
        "streams": [{"code": c, "name": n, "rank": r, "commodity": cm, "tons": t}
                    for c, n, r, cm, t in STREAMS],
        "rows": rows,
        "sources": [{
            "key": s["citation_key"],
            "short": SHORT.get(s["citation_key"], s["citation_key"]),
            "url": s["url"],
            "kind": s["kind"],
            "notes": s["notes"],
        } for s in srcs],
        "nodata": [{"stream": n["stream_code"], "state": n["state"],
                    "raised": n["raised_as"], "why": n["why"]} for n in nodata],
    }

    tpl = (HERE / "review_template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if "__DATA__" not in tpl:
        raise SystemExit("FAIL: template has no __DATA__ placeholder")

    BUILD.mkdir(parents=True, exist_ok=True)
    out = BUILD / "review.html"
    out.write_text(tpl.replace("__DATA__", payload), encoding="utf-8")

    covered = len({r["stream"] for r in rows})
    print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")
    print(f"  {len(rows)} rows over {covered} objects, {len(STREAMS)} objects in the round")
    print(f"  {len(nodata)} objects with no data, {len(srcs)} sources")


if __name__ == "__main__":
    main()
