# -*- coding: utf-8 -*-
"""select_fractions.py - the 80/20 selection at FRACTION grain, as a table-only deliverable.

    node tools/select_streams.js 69 --json build/sel_raw.json      # first, as always
    database/.venv/Scripts/python tools/select_fractions.py

Writes deliverables/BIOLOOP_stream_selection_per_fractie_<date>.html (self-contained, no external
fonts or scripts, so it survives being embedded in a slide deck).

WHY A SECOND SELECTION (reviewer, 2026-09-29). select_streams.js ranks one L4 product per row, the
value being, per source, the SUM of that source's fractions, then the max over sources. That is the
intuitive list, but it is not the 80/20 list: a product is not an object. Here every fraction is
ranked on its own, and where a source names no fraction the product is split PER CHAIN STAGE
(Kool- en raapzaad in the food industry). That is the stream-grain rule of 2026-09-08 applied to the
ranking, and it makes laagste/hoogste compare one object across sources instead of one source's
bundle against another's.

THE NUMBERS ARE NOT RE-DERIVED. Per-source fraction values are read from build/sel_raw.json, i.e.
from select_streams.js, which owns the derivation. The only extra arithmetic: an unfractioned part
that a source spread over two chain stages is split back per stage from its own claims, and only
when those claims add up to the part exactly (else it is left whole and reported).

HUMAN GATE. crosswalks/fraction_selection_decisions.csv holds the reviewer's decisions: `exclude`
(the row is not a selectable object), `merge` (synonym fractions of one object), `override_value`
(use another figure the source prints) and `note`. Only rows with DECISION = approved are applied;
rows with a blank DECISION are proposals and are listed at the end of the run, never applied.
Values are still never summed across sources: a merged row sums fractions WITHIN one source, then
takes the max over sources.
"""
import csv, io, json, html, pathlib, datetime, collections, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
TODAY = datetime.date.today().isoformat()
SH = lambda e: (e.replace("OVAM Monitor voedselverlies ", "OVAM ").replace(" ILVO 165", "")
                 .replace(" tuinbouw", "").replace(" (UGent TETRA)", ""))

sel = json.load(io.open(ROOT / "build/sel_raw.json", encoding="utf-8"))
P = json.load(io.open(ROOT / "build/streams.json", encoding="utf-8"))
with io.open(ROOT / "crosswalks/fraction_selection_decisions.csv", encoding="utf-8-sig", newline="") as f:
    DEC = list(csv.DictReader(f, delimiter=";"))
live = [d for d in DEC if d["DECISION"].strip().lower() == "approved"]
open_ = [d for d in DEC if not d["DECISION"].strip()]
key = lambda l4, frac, stage: (l4, frac or "", stage)

# ---------------------------------------------------------------- one row per fraction x stage
rows = collections.OrderedDict()
unsplit = []
for rank, s in enumerate(sel["items"], 1):
    for ed, b in s["by"].items():
        for p in b["parts"]:
            parts = [p]
            if p["label"] == "(zonder fractie)" and len(p["st"]) > 1:
                cl = [c for c in P["claims"] if c["ed"] == ed and c["l2"] == s["l2"] and c["l4"] == s["l4"]
                      and not c["l5"] and c["role"] == "Reststroom" and c["qt"] == "agri-food waste"
                      and c["st"] in p["st"] and not c["name"].startswith("AGGREGAAT")]
                by = collections.defaultdict(lambda: {"v": 0.0, "geo": set()})
                for c in cl:
                    by[c["st"]]["v"] += c["v"]; by[c["st"]]["geo"].add(c["geo"])
                if by and abs(sum(x["v"] for x in by.values()) - p["v"]) < 0.01:
                    parts = [{"label": p["label"], "v": x["v"], "st": [st], "geo": sorted(x["geo"])} for st, x in by.items()]
                else:
                    unsplit.append((s["l4"], ed, p["v"], p["st"]))
            for q in parts:
                unf = q["label"] == "(zonder fractie)"
                k = key(s["l4"], None if unf else q["label"], " / ".join(q["st"]))
                r = rows.setdefault(k, {"l4": s["l4"], "f": None if unf else q["label"], "st": " / ".join(q["st"]),
                                        "geo": set(), "by": {}, "prank": rank, "ed": {}})
                r["by"][SH(ed)] = r["by"].get(SH(ed), 0) + q["v"]; r["ed"][SH(ed)] = ed
                r["geo"] |= set(q["geo"])

# ---------------------------------------------------------------- the reviewer's decisions
def find(d):
    k = key(d["L4"], d["fraction"], d["chain_stage"])
    if k not in rows:
        sys.exit("decision %s matches no row: %s | %s | %s" % (d["id"], d["L4"], d["fraction"], d["chain_stage"]))
    return k

groups = collections.defaultdict(list)
for d in live:
    k = find(d)
    if d["action"] == "exclude":
        rows[k]["excluded"] = d["id"]
    elif d["action"] == "merge":
        groups[d["merge_group"]].append(k)
    elif d["action"] == "override_value":
        r = rows[k]; src = next(sh for sh, ed in r["ed"].items() if ed == d["source"])
        r["by"][src] = float(d["value_t"])
    elif d["action"] != "note":
        sys.exit("unknown action %r in %s" % (d["action"], d["id"]))

out = []
merged = {k for ks in groups.values() for k in ks}
for g, ks in groups.items():
    a = {"l4": rows[ks[0]]["l4"], "f": " = ".join(rows[k]["f"] for k in ks), "st": rows[ks[0]]["st"],
         "geo": set(), "by": {}, "prank": rows[ks[0]]["prank"]}
    for k in ks:
        a["geo"] |= rows[k]["geo"]
        for s_, v in rows[k]["by"].items(): a["by"][s_] = a["by"].get(s_, 0) + v   # within one source only
    out.append(a)
out += [r for k, r in rows.items() if k not in merged and not r.get("excluded")]
for o in out:
    v = sorted(o["by"].items(), key=lambda x: x[1])
    o.update(M=v[-1][1], Ms=v[-1][0], m=v[0][1], ms=v[0][0], n=len(v))
out.sort(key=lambda o: -o["M"])
T = sum(o["M"] for o in out); c = 0; n80 = n90 = 0
for i, o in enumerate(out, 1):
    c += o["M"]; o["cum"] = c / T
    if not n80 and o["cum"] >= .8: n80 = i
    if not n90 and o["cum"] >= .9: n90 = i

# ---------------------------------------------------------------- render
nl = lambda x: f"{round(x):,}".replace(",", ".")
pct = lambda x: format(100 * x, ".1f").replace(".", ",") + " %"
e = html.escape
body = []
for i, o in enumerate(out, 1):
    band = "b80" if i <= n80 else "b90" if i <= n90 else ""
    cut = " cut" if i in (n80, n90) else ""
    geo = ((" <span class=tag>BE+VL</span>" if "Vlaanderen" in o["geo"] else " <span class=tag>BE</span>")
           if "Belgie" in o["geo"] else "")
    fr = e(o["f"]) if o["f"] else f"<span class=stage>geheel · {e(o['st'])}</span>"
    low = f"{nl(o['m'])}<span class=src>{e(o['ms'])}</span>" if o["n"] > 1 else ""
    body.append(f"<tr class='{band}{cut}'><td class=n>{i}</td><td class=s>{e(o['l4'])}</td><td>{fr}{geo}</td>"
                f"<td class=n>{nl(o['M'])}<span class=src>{e(o['Ms'])}</span></td><td class=n>{low}</td>"
                f"<td class=n>{o['n']}</td><td class=n>{pct(o['cum'])}</td><td class=n>{o['prank']}</td></tr>")
    if i == n80: body.append("<tr class=cutlabel><td colspan=8>80 % van het totaal</td></tr>")
    if i == n90: body.append("<tr class=cutlabel><td colspan=8>90 % van het totaal</td></tr>")

page = (HERE / "template_fractions.html").read_text(encoding="utf-8")
page = (page.replace("{{SUB}}", f"{nl(T)} t/jaar · {n80} stromen dragen 80 % · {n90} dragen 90 % · {len(out)} stromen · {TODAY}")
            .replace("{{ROWS}}", "\n".join(body)))
p = ROOT / "deliverables" / f"BIOLOOP_stream_selection_per_fractie_{TODAY}.html"
p.write_text(page, encoding="utf-8")

print(f"wrote {p.name}: {len(out)} rows, {nl(T)} t, 80% at {n80}, 90% at {n90}")
print(f"decisions applied: {len(live)}   proposals NOT applied (blank DECISION): {len(open_)}")
for d in open_: print(f"   {d['id']}  {d['action']:<8} {d['L4']} | {d['fraction']}")
for u in unsplit: print("   NOTE: multi-stage part left whole (claims do not add up):", u)
