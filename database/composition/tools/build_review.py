"""Build the composition review page from the extraction CSVs.

    ../.venv/Scripts/python tools/build_review.py     ->  ../build/review.html

The page is a pure function of ../extraction/*.csv plus the vocabulary, so a later
harvest round regenerates it with one command and nothing drifts. It merges EVERY
round: round 1 (2026-09-09, Main analysis tables) and round 2 (2026-09-11, the 50 kt
target list with minerals, secondary metabolites and the streams round 1 never reached).

The stream list comes from `round2_targets.csv`, so the page always shows the current
worklist rather than a hard-coded set. A stream that carries rows but has since dropped
below the threshold still appears -- throwing away extracted data to match a cut-off
would be worse than showing it.

Published as an Artifact for the reviewer; their marks and remarks come back through the
artifact's own store, not through this file.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXTRACT = ROOT / "extraction"
BUILD = ROOT / "build"

SHORT = {
    "feedtables-inrae-cirad-afz-fao": "Feedipedia / feedtables",
    "phyllis2-tno": "Phyllis2 (TNO)",
    "deEvan2020Cauliflower": "De Evan et al. 2020, Animals",
}

# Streams extracted in round 1 that the 2026-09-11 selection puts below 50 kt.
# They keep their rows and their place on the page.
LEGACY = {
    "suikerbiet":       ("Suikerbiet", 4, "Suikerbiet", 48662),
    "bloemkool":        ("Bloemkool", 9, "Bloemkool", 16388),
    "raapzaad-stro":    ("Kool- en raapzaadstro", 2, "Kool- en raapzaad", 7818),
    "bloemkool-harten": ("Bloemkoolharten", 9, "Bloemkool", 18395),
}


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(fh, delimiter=";")]


def main() -> None:
    pcsv = read(ROOT / "vocabulary" / "parameters.csv")
    params = {p["code"]: p["name"] for p in pcsv}
    pgroup = {p["code"]: p["group_code"] for p in pcsv}
    groups = {g["code"]: g for g in read(ROOT / "vocabulary" / "parameter_groups.csv")}
    methods = {m["code"]: m["name"] for m in read(ROOT / "vocabulary" / "methods.csv")}

    def family(code: str) -> str:
        g = groups[code]
        return groups[g["parent_code"]]["name"] if g["parent_code"] else g["name"]

    meas = read(EXTRACT / "round1_measurements.csv") + read(EXTRACT / "round2_measurements.csv")
    srcs = {s["citation_key"]: s
            for s in read(EXTRACT / "round1_sources.csv") + read(EXTRACT / "round2_sources.csv")}
    targets = read(EXTRACT / "round2_targets.csv")
    legacy_nodata = read(EXTRACT / "round1_nodata.csv")

    unknown = sorted({m["parameter_code"] for m in meas if m["parameter_code"] not in params})
    if unknown:
        raise SystemExit(f"FAIL: measurement rows name parameters not in the catalogue: {unknown}")

    rows = []
    for m in meas:
        g = pgroup[m["parameter_code"]]
        rows.append({
            "stream": m["stream_code"],
            "parameter": m["parameter_code"],
            "parameter_label": params[m["parameter_code"]],
            "group": g,
            "group_label": groups[g]["name"],
            "group_family": family(g),
            "group_ref": groups[g]["external_ref"],
            "group_sort": int(groups[g]["sort_order"]),
            "value": m["value_num"],
            "min": m["value_min"],
            "max": m["value_max"],
            "sd": m["sd"],
            "n": m["n_samples"],
            "unit": m["unit_code"],
            "basis": m["basis_code"],
            "method": m.get("method_code", ""),
            "method_label": methods.get(m.get("method_code", ""), ""),
            "origin": m.get("value_origin", "measured"),
            "source_ref": m["source_ref"],
            "variant": m["variant"],
            "restatement": m.get("restatement", "no"),
            "flag": m["flag"],
            "notes": m["notes"],
        })
    rows.sort(key=lambda r: (r["stream"], r["group_sort"]))

    with_rows = {r["stream"] for r in rows}
    streams, nodata = [], []
    for t in targets:
        if t["status"] == "below_threshold" and t["stream_code"] not in with_rows:
            continue
        streams.append({"code": t["stream_code"],
                        "name": t["commodity"] + (" / " + t["fraction"] if t["fraction"] else ""),
                        "rank": int(t["rank"]), "commodity": t["commodity"],
                        "tons": int(t["tonnes"])})
        if t["status"] == "no-source":
            nodata.append({"stream": t["stream_code"], "state": "geen bruikbare bron",
                           "raised": "", "why": t["note"]})
    known = {s["code"] for s in streams}
    for code, (name, rank, commodity, tons) in LEGACY.items():
        if code in with_rows and code not in known:
            streams.append({"code": code, "name": name, "rank": rank,
                            "commodity": commodity, "tons": tons})
            known.add(code)
    for n in legacy_nodata:
        if n["stream_code"] not in known:
            nodata.append({"stream": n["stream_code"], "state": n["state"],
                           "raised": n["raised_as"], "why": n["why"]})
    streams.sort(key=lambda s: -s["tons"])

    data = {
        "streams": streams,
        "rows": rows,
        "sources": [{"key": s["citation_key"],
                     "short": SHORT.get(s["citation_key"], s["citation_key"]),
                     "url": s["url"], "kind": s["kind"], "notes": s["notes"]}
                    for s in srcs.values()],
        "nodata": nodata,
    }

    tpl = (HERE / "review_template.html").read_text(encoding="utf-8")
    if "__DATA__" not in tpl:
        raise SystemExit("FAIL: template has no __DATA__ placeholder")
    BUILD.mkdir(parents=True, exist_ok=True)
    out = BUILD / "review.html"
    out.write_text(tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False,
                                                      separators=(",", ":"))), encoding="utf-8")

    print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")
    print(f"  {len(rows)} rows over {len(with_rows)} streams, {len(streams)} streams on the page")
    print(f"  {len(nodata)} with no usable source, {len(data['sources'])} sources")


if __name__ == "__main__":
    main()
