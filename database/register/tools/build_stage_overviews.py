#!/usr/bin/env python3
"""BIOLOOP per-chain-stage stream-overview generator.

Same corpus, same derivation and the same view as `build_overview.py` — with one
structural difference: the chain stage is not a column, it is the filter the whole
page turns on. One tab per stage; the table under a tab is built ONLY from claims
whose chain stage is that stage and nothing else.

Figures that span several chain stages (`chain_L2 = meerdere stadia`, i.e. an
aggregate whose `stage_coverage` names more than one stage) are held out of every
number in the table and shown in their own contextual panel, for each stage they
span. They are never summed, never averaged and never compared — a figure covering
four stages cannot be measured against one of them — but they are never dropped
either, so "not measured" stays distinguishable from "measured across stages".

Output is a pure function of the `Streams` sheet + `crosswalks/aggregate_coverage.csv`
and regenerates deterministically.

  python build_stage_overviews.py                       # auto-find the workbook
  python build_stage_overviews.py /path/to/workbook.xlsx
"""
import subprocess, sys, pathlib, json

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                      # register/ - HERE is register/tools/

subprocess.run([sys.executable, str(HERE / "prep_data.py"), *sys.argv[1:]], check=True)

derive = (HERE / "derive.js").read_text(encoding="utf-8")
payload_path = ROOT / "build" / "streams.json"
data = payload_path.read_text(encoding="utf-8")
html = ((HERE / "template_by_stage.html").read_text(encoding="utf-8")
        .replace("/*__DERIVE__*/", derive)
        .replace("/*__DATA__*/", data))
out = ROOT / "build" / "stream_overview_by_stage.html"
out.write_text(html, encoding="utf-8")

# --- report the partition the page rests on, so a bad split is visible here too ---
MULTI = "meerdere stadia"
TABS = ["Primaire productie", "Voedingsindustrie", "Retail & grootdistributie"]
claims = json.loads(data)["claims"]


def stages_of(c):
    agg = c.get("agg") or {}
    if agg.get("stages"):
        return agg["stages"]
    return [] if c["st"] == MULTI else [c["st"]]


def is_multi(c):
    agg = c.get("agg") or {}
    return c["st"] == MULTI or len(agg.get("stages") or []) > 1


single = [c for c in claims if not is_multi(c)]
multi = [c for c in claims if is_multi(c)]
disagree = [c for c in multi if (c["st"] == MULTI) != (len((c.get("agg") or {}).get("stages") or []) > 1)]

print(f"wrote {out.name}  ({len(html)//1024} KB) - open it in a browser")
print(f"  {len(single)} single-stage claims - {len(multi)} multi-stage, held aside as context")
for st in TABS:
    n = sum(1 for c in single if c["st"] == st)
    ctx = sum(1 for c in multi if st in stages_of(c))
    print(f"    {st:34} {n:4} claims  + {ctx} context")
off = sorted({c["st"] for c in single if c["st"] and c["st"] not in TABS})
if off:
    n = sum(1 for c in single if c["st"] in off)
    print(f"  {n} claims sit at a stage with no tab: {', '.join(off)}")
if disagree:
    print("  ! chain_L2 and stage_coverage disagree on: " + ", ".join(c["id"] for c in disagree))
    sys.exit(1)
