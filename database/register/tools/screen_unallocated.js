// screen_unallocated.js - assess every unallocatable aggregate on its own terms.
//
//   node tools/screen_unallocated.js [--min 50000] [--json build/unalloc_screen.json]
//
// Run prep_data.py first.
//
// ---------------------------------------------------------------------------------------------
// WHY THIS EXISTS, AND WHY IT IS SEPARATE FROM THE GAP LIST
//
// An aggregate is UNALLOCATABLE when the things it totals do not sit under one parent row at one
// level. C-094 totals `Aardappelen en knolgewassen` (an L3 under akkerbouw) together with
// `Groenten openlucht`, `Groenten beschut`, `Groenten` and `Fruit` (L3s under tuinbouw). There is
// no row it can hang from, so the derivation never measures anything against it and its coverage
// is 0% BY CONSTRUCTION.
//
// That is why such a row must never enter the gap list: its 0% is a property of the commodity
// ladder, not of the data, and treating it as unreached mass inflates the gap.
//
// But the row is not worthless - it is often the only figure a source publishes for a whole
// sector. So it gets its own screening, which asks the question the ladder cannot:
//
//     TAKE WHAT THIS AGGREGATE SAYS IT TOTALS, PART BY PART, AND ASK WHAT THE REGISTER HOLDS
//     FOR EACH PART - wherever that part happens to live, and from whichever source.
//
// Two things follow from "wherever it lives, whichever source":
//
//   * A part is looked up ACROSS THE WHOLE TREE, not under the aggregate's parent, because the
//     whole point is that its parts are scattered. `Aardappelen en knolgewassen` is found under
//     akkerbouw even though the aggregate also spans tuinbouw.
//   * A part's figure is reported PER SOURCE and never merged. The gap list may not let MONBIO
//     cancel OVAM (state.md, 2026-09-01) and neither may this. Here the other source's figure is
//     shown BESIDE the aggregate's own, labelled, so the reviewer can see that a part OVAM never
//     resolves is one MONBIO does - which is a fact about the two monitors, not a reconciliation.
//
// So this screening verifies coverage of the underlying data; it does not produce a gap figure
// and nothing here is added to the gap list.
// ---------------------------------------------------------------------------------------------
const fs = require("fs"), path = require("path");
const D = require("./derive.js");
const HERE = __dirname, ROOT = path.dirname(HERE);
const P = JSON.parse(fs.readFileSync(path.join(ROOT, "build", "streams.json"), "utf8"));

const argMin = process.argv.indexOf("--min");
const MIN = argMin > -1 ? Number(process.argv[argMin + 1]) : 50000;
const walk = (n, o) => { o.push(n); (n.children || []).forEach(c => walk(c, o)); return o; };
const fmt = n => Math.round(n || 0).toLocaleString("de-DE");
const SH = e => e.replace("OVAM Monitor voedselverlies ", "OVAM ").replace(" ILVO 165", "")
  .replace(" tuinbouw", "");

// ---- the registry, for what each aggregate says it totals ------------------------------------
const REG = (() => {
  const f = path.join(ROOT, "crosswalks", "aggregate_coverage.csv");
  const out = {};
  const lines = fs.readFileSync(f, "utf8").replace(/^﻿/, "").split(/\r?\n/).filter(l => l.trim());
  const head = lines[0].split(";");
  lines.slice(1).forEach(l => {
    const c = l.split(";"), r = {};
    head.forEach((h, i) => r[h.trim()] = (c[i] || "").trim());
    if (r.claim_id) out[r.claim_id] = r;
  });
  return out;
})();

const EDS = [...new Set(P.claims.map(c => c.ed))].sort();

// every node of every edition, both roles, indexed by label - a part is looked up by NAME because
// the whole point is that it does not live where the aggregate hangs
const trees = {}, nodesByLabel = new Map();
EDS.forEach(ed => {
  const r = D.derive(P.claims, { editions: new Set([ed]) });
  trees[ed] = r;
  r.roots.forEach(root => walk(root, []).forEach(n => {
    const k = n.label.toLowerCase();
    if (!nodesByLabel.has(k)) nodesByLabel.set(k, []);
    nodesByLabel.get(k).push({ ed, node: n, role: root.label });
  }));
});

const selectableUnder = (n, stage) => (n.level === "l4" || n.level === "l5")
  ? ((n.repAgg[stage] || {}).display || 0)
  : walk(n, []).filter(x => x.level === "l4")
      .reduce((a, x) => a + ((x.repAgg[stage] || {}).display || 0), 0);

// ---- collect the unallocatable residual aggregates --------------------------------------------
const unalloc = new Map();
EDS.forEach(ed => (trees[ed].unallocated || []).forEach(u => {
  const c = u.claim;
  if (c.role !== "Reststroom" || !(c.v > 0)) return;
  if (!unalloc.has(c.id))
    unalloc.set(c.id, { id: c.id, ed, v: c.v, stage: c.st, qt: c.qt,
                        name: (c.name || "").replace("AGGREGAAT - ", ""), reason: u.reason });
}));

// A row the REGISTRY shelved (allocatable = no -> prep_data blanks its parent) is a decision that
// was already taken - a duplicate measurement, a parked scope variant, a parallel accounting. It
// is not a structural placement failure and does not need screening.
const SHELVED = /^no row "" in the tree/;

const items = [...unalloc.values()]
  .filter(x => x.v >= MIN && !SHELVED.test(x.reason))
  .sort((a, b) => b.v - a.v);

// ---- screen each one, part by part ------------------------------------------------------------
function partsOf(x) {
  const r = REG[x.id];
  if (!r) return [];
  const cov = (r.commodity_coverage || "").trim();
  if (cov && cov.toLowerCase() !== "full")
    return cov.split(",").map(s => s.trim()).filter(Boolean);
  // `full` means "every entry under the parent row" - name them from the parent's own children,
  // looking in the production tree too, since a branch with no residual rows has no residual node
  const parent = (r.parent_row || "").split(" ¦ ").pop();
  const hits = nodesByLabel.get((parent || "").toLowerCase()) || [];
  const kids = new Set();
  hits.forEach(h => (h.node.children || []).forEach(c => kids.add(c.label)));
  return [...kids];
}

const screened = items.map(x => {
  const parts = partsOf(x).map(label => {
    const hits = (nodesByLabel.get(label.toLowerCase()) || [])
      .filter(h => h.role === "Reststroom");
    const per = {};
    hits.forEach(h => {
      const v = (h.node.repAgg[x.stage] || {}).display || 0;
      const sel = selectableUnder(h.node, x.stage);
      if (v > 0 || sel > 0) per[h.ed] = { v, sel, path: h.node.path, level: h.node.level };
    });
    const own = per[x.ed] || null;
    const others = Object.keys(per).filter(e => e !== x.ed)
      .map(e => ({ ed: e, ...per[e] })).sort((a, b) => b.v - a.v);
    // a part that exists nowhere as a residual row at this stage - check production, so the
    // difference between "no residue reported" and "commodity absent entirely" stays visible
    const prod = (nodesByLabel.get(label.toLowerCase()) || [])
      .filter(h => h.role === "Productievolume")
      .map(h => ({ ed: h.ed, v: (h.node.repAgg[x.stage] || {}).display || 0 }))
      .filter(h => h.v > 0).sort((a, b) => b.v - a.v);
    return { label, own, others, prod };
  });
  const ownSum = parts.reduce((a, p) => a + (p.own ? p.own.v : 0), 0);
  const bestSum = parts.reduce((a, p) =>
    a + Math.max(p.own ? p.own.v : 0, ...(p.others.length ? p.others.map(o => o.v) : [0])), 0);
  const ownSel = parts.reduce((a, p) => a + (p.own ? p.own.sel : 0), 0);
  const bestSel = parts.reduce((a, p) =>
    a + Math.max(p.own ? p.own.sel : 0, ...(p.others.length ? p.others.map(o => o.sel) : [0])), 0);
  return { ...x, parts, ownSum, bestSum, ownSel, bestSel,
           ownPct: x.v > 0 ? ownSum / x.v : null, bestPct: x.v > 0 ? bestSum / x.v : null };
});

// ---- report ------------------------------------------------------------------------------------
console.log("=".repeat(104));
console.log(`SCREENING VAN ONPLAATSBARE AGGREGATEN - elk apart, deel voor deel (drempel ${fmt(MIN)} t)`);
console.log("=".repeat(104));
console.log("Deze cijfers gaan NIET naar de gaplijst. Ze controleren wat het register per onderdeel bevat.\n");

screened.forEach(x => {
  console.log("-".repeat(104));
  console.log(`${x.id}  ${fmt(x.v)} t   [${SH(x.ed)}, ${x.stage}, ${x.qt}]`);
  console.log(`   ${x.name.slice(0, 96)}`);
  console.log(`   onplaatsbaar omdat: ${x.reason.slice(0, 88)}`);
  if (!x.parts.length) { console.log("   (registry noemt geen onderdelen)"); return; }
  console.log("   onderdelen:");
  x.parts.forEach(p => {
    const own = p.own ? fmt(p.own.v) : "—";
    const oth = p.others.length
      ? p.others.map(o => `${SH(o.ed)} ${fmt(o.v)}`).join(", ") : "";
    const pr = (!p.own && !p.others.length && p.prod.length)
      ? `   (geen reststroom; hoofdstroom ${SH(p.prod[0].ed)} ${fmt(p.prod[0].v)})` : "";
    console.log(`      ${p.label.padEnd(30)} eigen bron ${own.padStart(10)}`
      + (oth ? `   andere: ${oth}` : "") + pr);
  });
  console.log(`   som onderdelen: eigen bron ${fmt(x.ownSum)} = ${(100 * x.ownPct).toFixed(0)}%`
    + `   |   beste per onderdeel over alle bronnen ${fmt(x.bestSum)} = ${(100 * x.bestPct).toFixed(0)}%`);
  console.log(`   daarvan selecteerbaar (L4/L5): eigen bron ${fmt(x.ownSel)}   beste ${fmt(x.bestSel)}`);
});

console.log("\n" + "=".repeat(104));
console.log(`${screened.length} onplaatsbare aggregaten gescreend`);
const jf = process.argv[process.argv.indexOf("--json") + 1];
if (process.argv.includes("--json") && jf) {
  fs.writeFileSync(jf, JSON.stringify({ min: MIN, items: screened }, null, 1));
  console.log(`wrote ${jf}`);
}
