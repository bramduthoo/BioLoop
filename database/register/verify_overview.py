"""Regression test for the overview's derivation. Run it after any change to derive.js.

Each case is an arithmetic identity that holds in the sources themselves, so it is independent of
the code being tested: if the derivation drifts, one of these breaks. They were the reconciliations
that first proved the aggregate axis was right, plus the invariants that must never fail.

    database/.venv/Scripts/python.exe database/register/verify_overview.py

Exit code 0 when every case passes.
"""
import json, pathlib, subprocess, sys, tempfile, textwrap

HERE = pathlib.Path(__file__).resolve().parent

JS = r"""
const D = require(process.argv[2] + "/derive.js");
const P = require(process.argv[2] + "/streams.json");
const out = [];
const ok = (name, got, want, tol) => out.push(
  {name, got, want, pass: want === null ? !!got : Math.abs(got - want) <= (tol || 0)});

function scope(ed, yr) {
  const r = D.derive(P.claims, {year: yr, editions: new Set([ed])});
  return {r, rest: r.roots.find(x => x.label === "Reststroom")};
}
function leaves(n) {
  const o = [];
  (function w(x){ if(x.repTotal<=0) return;
    if(x.depth>=4 && x.children.filter(c=>c.repTotal>0).length===0){o.push(x);return;}
    x.children.forEach(w); })(n);
  return o;
}
function findNode(root, label) {
  let hit = null;
  (function w(x){ if(x.label===label) hit=x; x.children.forEach(w); })(root);
  return hit;
}

// --- 1. OVAM 2023 retail: the two channel halves restate the printed stage total -------------
const ov = scope("OVAM Monitor voedselverlies 2023", 2023);
const retail = ov.rest.covByStage["Retail & grootdistributie"];
ok("OVAM 2023 retail reported total = 132,082 (C-105 alone, no averaging)",
   retail ? retail.reported : 0, 132082, 1);

// --- 2. no AGGREGAAT claim is ever a summand --------------------------------------------------
let aggAsComponent = 0;
(function walk(ns){ for (const n of ns) {
  for (const c of (n.selfClaims || [])) if (String(c.name).toUpperCase().startsWith("AGGREGAAT")) aggAsComponent++;
  walk(n.children); } })(D.derive(P.claims, {}).roots);
ok("no AGGREGAAT row appears as a component anywhere", aggAsComponent, 0, 0);

// --- 3. MONBIO 4.0 Granen: field straw PLUS the mill and brewery residues --------------------
// Was 1.590.919 (maisstro + tarwestro alone) until 2026-09-03, when the reviewer's GAP-4/GAP-5
// decisions promoted zemelen (275.849), gries (85.219) and bostel (134.653) to L4 under Granen.
// 1.590.919 + 495.721 = 2.086.640. The number changed because the tree changed, not because the
// derivation drifted - note that Granen now mixes FIELD residue with MILL/BREWERY residue.
const mb = scope("MONBIO 4.0", 2021);
const granen = findNode({label:"", children: mb.rest.children}, "Granen");
const gset = (granen && granen.subsetSets || []).concat(granen ? [] : []);
ok("MONBIO 4.0 Granen node exists", granen ? 1 : 0, 1, 0);
if (granen) {
  const kids = leaves(granen).reduce((a,b)=>a+b.repTotal,0);
  ok("MONBIO 4.0 Granen leaves sum to 2,086,640 (maisstro + tarwestro + zemelen + gries + bostel)",
     kids, 2086640, 2);
}

// --- 4. every figure's provenance matches how it was built ------------------------------------
// A leaf may legitimately be marked summed when it carries an aggregate at another stage, so the
// invariant is narrower: one claim, one stage, no aggregate => nothing was summed.
let provBad = 0;
(function walk(ns){ for (const n of ns) {
  if (n.isLeaf && n.claims.length === 1 && (n.aggregates || []).length === 0
      && n.totalProv && n.totalProv.sum) provBad++;
  walk(n.children); } })(mb.r.roots);
ok("a leaf with one claim, one stage and no aggregate is never marked summed", provBad, 0, 0);

// --- 5. exclusions re-derive: dropping a claim changes the figure it fed ----------------------
// L1 is driven by the reported (aggregate) totals, so excluding one component does not move it -
// it moves the node that component belongs to, and the coverage % it feeds. That is the design.
function aardappel(excl) {
  const r = D.derive(P.claims, {year:2023, editions:new Set(["OVAM Monitor voedselverlies 2023"]),
                                excluded: excl});
  const rest = r.roots.find(x=>x.label==="Reststroom");
  return findNode({label:"", children: rest.children}, "Aardappel");
}
const a0 = aardappel(undefined), a1 = aardappel(new Set(["C-005"]));
ok("excluding a component lowers the node it belongs to", a0.repTotal > a1.repTotal ? 1 : 0, 1, 0);
ok("excluding C-005 removes it from that node's claims",
   a1.claims.filter(c=>c.id==="C-005").length, 0, 0);

// --- 6. the tree never loses volume: L1 equals the sum of its L2 children ---------------------
let treeBad = 0;
(function walk(ns){ for (const n of ns) {
  if (n.children.length) {
    const kids = n.children.reduce((a,b)=>a+b.repTotal,0);
    if (n.childTotal !== undefined && Math.abs(n.childTotal - kids) > 2) treeBad++;
  } walk(n.children); } })(mb.r.roots);
ok("every node's childTotal equals the sum of its children", treeBad, 0, 0);

console.log(JSON.stringify(out));
"""


def main():
    if not (HERE / "streams.json").exists():
        sys.exit("streams.json missing - run build_overview.py first")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(JS)
        script = fh.name
    try:
        p = subprocess.run(["node", script, str(HERE)], capture_output=True, text=True)
    finally:
        pathlib.Path(script).unlink(missing_ok=True)
    if p.returncode:
        print(p.stderr)
        sys.exit("node failed")
    cases = json.loads(p.stdout.strip().splitlines()[-1])
    width = max(len(c["name"]) for c in cases)
    bad = 0
    for c in cases:
        mark = "PASS" if c["pass"] else "FAIL"
        if not c["pass"]:
            bad += 1
        got = f"{c['got']:,.0f}" if isinstance(c["got"], (int, float)) else c["got"]
        want = f"{c['want']:,.0f}" if isinstance(c["want"], (int, float)) else c["want"]
        print(f"  [{mark}] {c['name']:<{width}}   got {got:>12}   want {want:>12}")
    print(f"\n{len(cases) - bad}/{len(cases)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
