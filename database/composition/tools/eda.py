"""Exploratory analysis of the composition dataset: what is there, and where the holes are.

    ../.venv/Scripts/python tools/eda.py            # report
    ../.venv/Scripts/python tools/eda.py --json     # for the analysis page

Three questions, and the third is the one that decides what to harvest next.

  WHICH PARAMETERS EXIST, and how many streams carry a value for each. A parameter with
  one stream behind it is not a column of the composition vector yet, it is one source's
  habit; a parameter with fifteen is something the model can actually reason over.

  HOW MANY PARAMETERS PER STREAM, against that stream's tonnage. A thin vector on a large
  stream is where the next round pays off most.

  WHAT IS ABSENT rather than merely sparse. The coverage matrix has holes of two kinds --
  a parameter nobody measures on that material, and a parameter everybody measures that
  this stream simply has not been harvested for. Only the second is work.
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT = ROOT / "extraction"
ROUNDS = ["round1_measurements.csv", "round2_measurements.csv", "round3_measurements.csv"]


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(fh, delimiter=";")]


def build() -> dict:
    rows: list[dict] = []
    for f in ROUNDS:
        rows += read(EXTRACT / f)
    targets = {t["stream_code"]: t for t in read(EXTRACT / "round3_targets.csv")}
    pcsv = read(ROOT / "vocabulary" / "parameters.csv")
    params = {p["code"]: p for p in pcsv}
    groups = {g["code"]: g for g in read(ROOT / "vocabulary" / "parameter_groups.csv")}
    srcs = {}
    for f in ("round1_sources.csv", "round2_sources.csv", "round3_sources.csv"):
        for s in read(EXTRACT / f):
            srcs[s["citation_key"]] = s

    def family(code: str) -> str:
        g = groups.get(code)
        if not g:
            return "?"
        return groups[g["parent_code"]]["name"] if g.get("parent_code") else g["name"]

    in_scope = [c for c in targets]
    cell = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        cell[r["stream_code"]][r["parameter_code"]].append(r)

    # per parameter: how many IN-SCOPE streams carry it
    par_rows = []
    for code, p in params.items():
        streams = [s for s in in_scope if code in cell.get(s, {})]
        other = [s for s in cell if code in cell[s] and s not in targets]
        n_vals = sum(len(cell[s][code]) for s in streams)
        par_rows.append(dict(
            code=code, name=p["name"], group=p["group_code"],
            group_name=groups.get(p["group_code"], {}).get("name", "?"),
            family=family(p["group_code"]),
            sort=int(groups.get(p["group_code"], {}).get("sort_order", 999)),
            streams=len(streams), streams_out=len(other), values=n_vals,
            stream_list=sorted(streams),
        ))
    par_rows.sort(key=lambda d: (-d["streams"], d["sort"], d["code"]))

    # per stream: how many parameters and how many sources
    st_rows = []
    for code, t in targets.items():
        ps = cell.get(code, {})
        fams = collections.Counter(family(params[p]["group_code"]) for p in ps if p in params)
        st_rows.append(dict(
            code=code, name=t["commodity"] + (" / " + t["fraction"] if t["fraction"] else ""),
            tonnes=int(t["tonnes"]), rank=int(t["rank"]),
            parameters=len(ps), values=sum(len(v) for v in ps.values()),
            sources=len({r["source_key"] for v in ps.values() for r in v}),
            families=dict(fams),
            parameter_list=sorted(ps),
        ))
    st_rows.sort(key=lambda d: -d["tonnes"])

    # the core: parameters at least half the covered streams have. A stream missing one of
    # these is a harvesting hole, not a property of the material.
    covered = [s for s in st_rows if s["parameters"]]
    core = [p["code"] for p in par_rows if p["streams"] >= max(2, len(covered) // 2)]
    for s in st_rows:
        s["core_missing"] = [c for c in core if c not in s["parameter_list"]] if s["parameters"] else core

    return dict(
        n_values=len(rows), n_streams_in_scope=len(targets),
        n_streams_with_data=len(covered),
        n_parameters_registered=len(params), n_parameters_used=sum(1 for p in par_rows if p["values"]),
        tonnes_total=sum(t["tonnes"] for t in st_rows),
        tonnes_covered=sum(t["tonnes"] for t in covered),
        core=core,
        sources=[dict(key=k, kind=v.get("kind", ""), country=v.get("country", ""),
                      year=v.get("year", ""),
                      values=sum(1 for r in rows if r["source_key"] == k))
                 for k, v in srcs.items()],
        parameters=par_rows, streams=st_rows,
    )


def main() -> None:
    d = build()
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False))
        return

    print(f"{d['n_values']} values · {d['n_parameters_used']} of {d['n_parameters_registered']} "
          f"parameters used · {d['n_streams_with_data']} of {d['n_streams_in_scope']} streams "
          f"covered · {d['tonnes_covered']:,} of {d['tonnes_total']:,} t/yr\n")

    print("SOURCES")
    for s in sorted(d["sources"], key=lambda s: -s["values"]):
        print(f"  {s['values']:>5}  {s['key']:<34} {s['kind']:<22} {s['country']} {s['year']}")

    print(f"\nPARAMETERS BY REACH (core = at least {max(2, d['n_streams_with_data'] // 2)} streams)")
    fam = None
    for p in d["parameters"]:
        if not p["values"]:
            continue
        if p["family"] != fam:
            fam = p["family"]
            print(f"\n  -- {fam}")
        mark = "core" if p["code"] in d["core"] else "    "
        print(f"  {mark} {p['streams']:>3} streams {p['values']:>5} values  "
              f"{p['code']:<22} {p['name'][:36]}")

    print("\nSTREAMS BY TONNAGE")
    print(f"  {'t/yr':>10}  {'stream':<28} {'par':>4} {'val':>5} {'src':>4}  missing from the core")
    for s in d["streams"]:
        miss = ", ".join(s["core_missing"][:6])
        if len(s["core_missing"]) > 6:
            miss += f" (+{len(s['core_missing']) - 6})"
        print(f"  {s['tonnes']:>10,}  {s['code']:<28} {s['parameters']:>4} {s['values']:>5} "
              f"{s['sources']:>4}  {miss}")

    unused = [p for p in d["parameters"] if not p["values"]]
    print(f"\n{len(unused)} registered parameters carry no value yet:")
    print("  " + ", ".join(p["code"] for p in unused))


if __name__ == "__main__":
    main()
