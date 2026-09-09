// gap_review.js - reconcile every AGGREGAAT row against what the register captured beneath it.
//
//   node tools/gap_review.js [--min 50000] [--json out.json]
//
// Run prep_data.py first. Reads build/streams.json and crosswalks/aggregate_coverage.csv.
//
// ---------------------------------------------------------------------------------------------
// WHAT THIS ANSWERS
//
// The 80/20 selection ranks what the register CAN see. This asks the mirror question: for every
// total the sources report, how much of it is explained by named streams underneath, and how much
// is still just a lump? A total that is fully explained is not a gap however large it is; a total
// with nothing beneath it is a gap however small.
//
// THE ENGINE IS derive.js, NOT A SECOND DERIVATION. `database/CLAUDE.md`: a sub-project owns one
// derivation and consumers read it. Every reported/components/ratio figure here is lifted straight
// off the node derive.js built - `node.covByStage[stage]` for a stage total, `group.check` for a
// subset. Nothing is recomputed.
//
// The per-child list is CONTEXT, not arithmetic: it answers "what sits under this total", and its
// values are each child's own figure at that stage. It does NOT generally sum to `components`,
// because derive folds quantity types per node before summing (`displayOf`: agri-food waste wins
// over its own nevenstroom+voedselverlies split), so a parent's fold and the sum of its children's
// folds are different quantities whenever the children mix quantity types. Where the two ARE
// comparable - a subset group, which derive scores on one quantity type - the breakdown is
// asserted against derive's own number and a drift is a hard error.
//
// TWO WAYS A TOTAL CAN BE RESOLVED, AND derive ONLY SCORES ONE OF THEM
//
// derive checks an aggregate against the node's CHILDREN - deeper commodity detail. But a total
// can equally be resolved by its own SIBLINGS at the same node: C-043 (Voedselreststromen
// aardappelen, 548.305 t) is exactly C-005 (niet-geoogst 308.000) + C-042 (excl. niet-geoogst
// 240.305), two component claims sitting beside it on the Aardappel node, which has no children.
// derive scores that 0% and marks it `indicative`, which read as "nothing beneath it" - the
// opposite of the truth, and on one of the best-resolved rows in the corpus.
//
// So this tool computes a SECOND measure, `selfComponents`, from `node.ownBySource[edition]` -
// the node's own component claims at that stage and quantity type, aggregates excluded (derive
// builds its tree from components only, derive.js:284). The disposition is taken on whichever
// measure explains more, and both are reported, with `explainedBy` saying which one answered.
//
// DISPOSITIONS
//   resolved      >= 95% of the total is explained by captured components
//   partly        50-95% explained - real detail exists, but not all of it
//   thin          5-50% explained - a token amount beneath a big lump
//   gap           < 5% explained, with components present but negligible
//   opaque        NO components at all: the figure cannot be checked, and nothing under it is
//                 selectable. derive.js calls this `indicative` and still shows the figure.
//   over          components exceed the total (>105%) - a placement or double-count problem,
//                 never a gap
//   unallocated   the aggregate spans two parents or levels, so it hangs from nothing. Visible
//                 and usable, never compared - by design, not a defect.
//   shelved       the registry deliberately took it out of the derivation (`allocatable = no`,
//                 or DECISION = unallocated). A decision, not a failure to place.
// ---------------------------------------------------------------------------------------------
const fs = require("fs"), path = require("path");
const D = require("./derive.js");
const HERE = __dirname, ROOT = path.dirname(HERE);
const P = JSON.parse(fs.readFileSync(path.join(ROOT, "build", "streams.json"), "utf8"));

const argMin = process.argv.indexOf("--min");
const MIN = argMin > -1 ? Number(process.argv[argMin + 1]) : 0;

// ---- the registry, for the placement each aggregate was given ------------------------------
function readRegistry() {
  const raw = fs.readFileSync(path.join(ROOT, "crosswalks", "aggregate_coverage.csv"), "utf8")
    .replace(/^﻿/, "");
  const lines = raw.split(/\r?\n/).filter(l => l.trim());
  const head = lines[0].split(";");
  const out = {};
  for (const line of lines.slice(1)) {
    // the file has no quoted separators in practice, but be safe about them
    const cells = []; let cur = "", q = false;
    for (const ch of line) {
      if (ch === '"') q = !q;
      else if (ch === ";" && !q) { cells.push(cur); cur = ""; }
      else cur += ch;
    }
    cells.push(cur);
    const r = {}; head.forEach((h, i) => r[h.trim()] = (cells[i] || "").trim());
    if (r.claim_id) out[r.claim_id] = r;
  }
  return out;
}
const REG = readRegistry();

// derive.js's own quantity-type rule (derive.js:43). Restated for the per-child breakdown only;
// asserted against the node's component total below.
const qtValue = (s, k) => !s ? 0 : (k === "afwE" ? (s.afwE > 0 ? s.afwE : s.nev + s.voe) : s[k]);
const walk = (n, o) => { o.push(n); (n.children || []).forEach(c => walk(c, o)); return o; };
const byId = new Map(P.claims.map(c => [c.id, c]));

// A total can also be resolved by its own siblings at the same node - see the note above.
// `ownBySource` holds component claims only, so an aggregate never explains itself.
function selfOf(node, ed, stages, k) {
  const per = node && node.ownBySource && node.ownBySource[ed];
  if (!per) return 0;
  const sts = (stages || []).includes("alle stadia") ? Object.keys(per) : (stages || []);
  return sts.reduce((a, st) => a + qtValue(per[st], k), 0);
}

// Which entry of the RETIRED hand-maintained gap list named this claim. The G-01..G-19 ids are
// legacy as of 2026-09-09 - the gap list is now derived by tools/make_gap_list.js - but the
// mapping is still useful context when re-reading an old note. Absent file degrades to {}.
function readGaps() {
  const f = path.join(ROOT, "migrations", "GAP_LIST_retired_2026-09-09.csv");
  if (!fs.existsSync(f)) return {};
  const raw = fs.readFileSync(f, "utf8").replace(/^﻿/, "");
  const out = {};
  // claim ids are quoted inside free text; a regex over the whole row is enough to link them
  raw.split(/\r?\n/).slice(1).forEach(line => {
    const gid = (line.split(";")[0] || "").trim();
    if (!/^G-\d+/.test(gid)) return;
    const sector = (line.split(";")[1] || "").trim();
    (line.match(/C-\d{3}/g) || []).forEach(cid => { out[cid] = out[cid] || { gid, sector }; });
  });
  return out;
}
const GAPS = readGaps();

/* CROSS-PARENT RECONCILIATIONS — the third way a total can be resolved, and the only one that
 * cannot be computed. derive checks an aggregate against its children; gap_review adds its
 * siblings; but a total is sometimes explained by rows filed under a DIFFERENT parent, and no
 * rule in the register can find them, because what makes them belong is domain knowledge.
 *
 * Beet pulp is a sugar-industry residue that the register files under the CROP (Suikerbieten),
 * while molasses sits under the SECTOR (Varia > Suiker). So the `suiker en chocolade` sector
 * total looks 12-14% explained and is in fact ~100% explained — which also proves the thing
 * G-12 actually claims: cacao contributes essentially nothing to it.
 *
 * Each entry is a reviewer-confirmed arithmetic identity, not a guess. Keep it that way: add a
 * row only when the sum has been checked against the printed figure and a human has agreed.
 */
const CROSS_PARENT = {
  "C-471": { by: ["C-574", "C-575"], why: "melasse 56.806 (Varia > Suiker) + bietenpulp 337.649 " +
    "(Plantaardig - akkerbouw > Suikerbieten) = 394.455 tegen een gedrukte 394 kton" },
  "C-286": { by: ["C-381", "C-382"], why: "melasse 47.805 (Varia > Suiker) + bietenpulp 350.000 " +
    "(Plantaardig - akkerbouw > Suikerbieten) = 397.805 tegen een gedrukte 403 kton" },
};
const claimV = id => { const c = byId.get(id); return c ? c.v : 0; };

function disposition(ratio, components) {
  if (ratio == null) return "unallocated";
  if (!(components > 0)) return "opaque";
  if (ratio > 1.05) return "over";
  if (ratio >= 0.95) return "resolved";
  if (ratio >= 0.50) return "partly";
  if (ratio >= 0.05) return "thin";
  return "gap";
}

// ---- one record per aggregate claim ---------------------------------------------------------
const recs = new Map();
const EDS = [...new Set(P.claims.map(c => c.ed))].sort();
const drift = [];

// `variantSet` folds a component_set (the halves of a collection-route split) into ONE synthetic
// entry carrying the members in `.members`, so the individual claim ids never appear at top level.
// Flatten them, or eight retail rows and two production totals silently go unreviewed.
const expand = items => items.flatMap(v => (v.members && v.members.length) ? v.members.map(
  m => Object.assign({}, m, { partOf: v.id })) : [v]);

function record(items, node, stages, qtKey, rep, components, kids, covLabel) {
  for (const it of expand(items)) {
    const c = byId.get(it.id) || {};
    const selfComp = selfOf(node, it.ed, stages, qtKey);
    const xp = CROSS_PARENT[it.id];
    const xpComp = xp ? xp.by.reduce((a, id) => a + claimV(id), 0) : 0;
    const best = Math.max(components || 0, selfComp, xpComp);
    const ratio = rep > 0 ? (components == null && !selfComp && !xpComp ? null : best / rep) : null;
    const explainedBy = !(best > 0) ? "none"
      : xpComp === best ? "cross-parent"
      : selfComp > (components || 0) ? "siblings" : "children";
    recs.set(it.id, {
      id: it.id, name: it.name, ed: it.ed, yr: c.yr, v: it.v,
      stage: (stages || []).join(" + "), qt: c.qt, lvl: c.lvl,
      l2: c.l2, l3: c.l3, l4: c.l4,
      page: c.page, tbl: c.tbl, label: c.label, alt: c.alt,
      node: node ? node.path : null,
      nodeLevel: node ? node.level : null,
      cov: covLabel,
      reported: rep, components, selfComponents: selfComp, crossParent: xpComp || null,
      crossWhy: xp ? xp.why : null, explained: best, ratio, explainedBy,
      disp: disposition(ratio, best),
      gap: GAPS[it.id] || null,
      kids: (kids || []).filter(k => k.v > 0).sort((a, b) => b.v - a.v),
      nKids: (kids || []).length,
      reg: REG[it.id] || null,
      treatment: it.treatment, reviewed: it.reviewed, note: it.note,
      partOf: it.partOf || null,
    });
  }
}

EDS.forEach(ed => {
  const r = D.derive(P.claims, { editions: new Set([ed]) });
  const nodes = r.roots.flatMap(x => walk(x, []));

  nodes.forEach(node => {
    // Full stage totals. derive scores these on the FOLDED view, so its own covByStage numbers
    // are the reconciliation; `own:` entries in totalSets are the node's own component claims,
    // not aggregates, and are skipped.
    Object.keys(node.totalSets || {}).forEach(st => {
      const cov = node.covByStage && node.covByStage[st];
      Object.keys(node.totalSets[st] || {}).forEach(k => {
        const g = node.totalSets[st][k];
        if (!g || !g.values) return;
        const items = g.values.filter(v => v.isAgg);
        if (!items.length) return;
        /* An aggregate carrying a SPECIFIC quantity type must be scored against the children's
           figure FOR THAT TYPE, not against the node's folded total. `Eetbare slachtafvallen,
           totaal` is a voedselverlies row: its components are the children's voedselverlies
           (82.576 + 84.141), not the whole Vlees node. Scoring it on the fold both inflated it
           past 100% and listed `Niet-eetbare slachtafvallen` as a child of an EDIBLE total
           (reviewer, 2026-09-08). Only an `agri-food waste` aggregate takes the fold, because
           that is what the fold means. */
        const folded = k === "afwE";
        const kids = (node.children || []).map(c => ({
          label: c.label,
          v: folded ? ((c.repAgg[st] || {}).display || 0) : ((c.repAgg[st] || {})[k] || 0)
        }));
        // ... and against its OWN reported value, not the node's folded one, for the same reason
        const comp = folded
          ? (cov ? cov.components : null)
          : kids.reduce((a, x) => a + x.v, 0);
        const rep = folded ? (cov ? cov.reported : g.rep) : g.rep;
        record(items, node, [st], k, rep, comp, kids, "full");
      });
    });
    // All-stage totals (derive's "Total column"): an aggregate spanning every stage at once.
    // Its reconciliation is the node's own repTotal against the sum of its children's repTotals.
    Object.keys(node.totalColSets || {}).forEach(k => {
      const g = node.totalColSets[k];
      if (!g || !g.values) return;
      const items = g.values.filter(v => v.isAgg);
      if (!items.length) return;
      const kids = (node.children || []).map(c => ({ label: c.label, v: c.repTotal || 0 }));
      record(items, node, ["alle stadia"], k, g.rep, node.childTotal, kids, "full (alle stadia)");
    });

    // subsets: an aggregate covering only named children
    (node.subsetSets || []).forEach(g => {
      if (!g.set || !g.items || !g.items.length) return;
      const kids = (g.cov === "full" ? node.children
        : (node.children || []).filter(c => g.cov.indexOf(c.label) >= 0))
        .map(c => ({ label: c.label, v: g.stages.reduce((a, st) => a + qtValue(c.repAgg[st], g.qtKey), 0) }));
      const comp = kids.reduce((a, x) => a + x.v, 0);
      if (g.check && Math.abs(g.check.components - comp) > Math.max(1, g.check.components * 0.001))
        drift.push(`${node.path} subset ${g.key}: derive ${Math.round(g.check.components)} vs breakdown ${Math.round(comp)}`);
      record(g.items, node, g.stages, g.qtKey, g.set.rep, comp, kids,
        g.cov === "full" ? "full" : g.cov.join(", "));
    });
  });

  // aggregates the derivation could not hang anywhere
  (r.unallocated || []).forEach(u => {
    const c = u.claim;
    if (recs.has(c.id) || !(c.name || "").startsWith("AGGREGAAT - ")) return;
    recs.set(c.id, {
      id: c.id, name: c.name, ed: c.ed, yr: c.yr, v: c.v, stage: c.st, qt: c.qt, lvl: c.lvl,
      l2: c.l2, l3: c.l3, l4: c.l4, page: c.page, tbl: c.tbl, label: c.label, alt: c.alt,
      node: null, nodeLevel: null, cov: null,
      reported: c.v, components: null, selfComponents: null, explained: null,
      ratio: null, explainedBy: null,
      // prep_data blanks `parent_row` when the registry shelves a row (`allocatable = no`, or
      // DECISION = unallocated), so an empty parent means a DECISION was taken, not that the
      // placement failed. The two read identically in derive's reason string; keep them apart.
      disp: /^no row "" in the tree/.test(u.reason || "") ? "shelved" : "unallocated",
      kids: [], nKids: 0, reg: REG[c.id] || null, gap: GAPS[c.id] || null,
      treatment: null, reviewed: null,
      // derive names the field `reason`, and it says WHY the row hangs from nothing - the most
      // useful sentence on an unallocated row, so do not lose it to a typo
      note: (u.reason || ""),
    });
  });
});

const aggIds = new Set(P.claims.filter(c => (c.name || '').startsWith('AGGREGAAT - ')).map(c => c.id));
const all = [...recs.values()].filter(x => aggIds.has(x.id)).sort((a, b) => b.v - a.v);
const shown = all.filter(x => x.v >= MIN);

// ---- report ---------------------------------------------------------------------------------
const fmt = n => n == null ? "-" : Math.round(n).toLocaleString("de-DE");
const pct = x => x == null ? "  n.v.t." : (100 * x).toFixed(0).padStart(5) + "%";
const W = 108;

if (drift.length) {
  console.log("!! BREAKDOWN WIJKT AF VAN derive.js - niet vertrouwen:");
  drift.forEach(d => console.log("   " + d));
  process.exitCode = 1;
}

const aggClaims = P.claims.filter(c => (c.name || "").startsWith("AGGREGAAT - "));
console.log("=".repeat(W));
console.log(`AGGREGATEN AFGEREKEND TEGEN WAT ERONDER GEVANGEN IS   (${all.length} van ${aggClaims.length} aggregaatclaims)`);
console.log("=".repeat(W));

const order = ["opaque", "gap", "thin", "partly", "resolved", "over", "unallocated", "shelved"];
const tally = {};
all.forEach(x => (tally[x.disp] = tally[x.disp] || { n: 0, v: 0 }, tally[x.disp].n++, tally[x.disp].v += x.v));
order.forEach(k => { if (tally[k]) console.log(`  ${k.padEnd(12)} ${String(tally[k].n).padStart(4)} claims  ${fmt(tally[k].v).padStart(14)} t`); });

console.log("\n" + "=".repeat(W));
console.log(`PER AGGREGAAT${MIN ? `, vanaf ${fmt(MIN)} t/jaar` : ""}  -  ${shown.length} rijen`);
console.log("=".repeat(W));
for (const x of shown) {
  console.log(`\n  ${x.id}  ${fmt(x.v).padStart(11)} t   ${x.disp.toUpperCase()}   ${pct(x.ratio)} verklaard   [${x.ed}, ${x.yr || "-"}]`);
  console.log(`     ${(x.name || "").slice(0, 96)}`);
  console.log(`     knoop ${x.node || "(nergens - unallocated)"}   dekking: ${x.cov || "-"}`);
  if (x.explained != null && x.ratio != null)
    console.log(`     gerapporteerd ${fmt(x.reported)}  vs  verklaard ${fmt(x.explained)} (via ${x.explainedBy})`
      + `  ->  ontbreekt ${fmt(x.reported - x.explained)}`
      + (x.gap ? `   [${x.gap.gid}]` : ""));
  if (x.kids.length)
    console.log("     eronder (context, telt niet noodzakelijk op tot `gevangen`): " + x.kids.slice(0, 6).map(k => `${k.label} ${fmt(k.v)}`).join(" · ")
      + (x.kids.length > 6 ? ` · +${x.kids.length - 6} meer` : ""));
  else
    console.log("     eronder: NIETS gevangen");
}

const jf = process.argv[process.argv.indexOf("--json") + 1];
if (process.argv.includes("--json") && jf) {
  fs.writeFileSync(jf, JSON.stringify({ min: MIN, tally, drift, items: all }, null, 1));
  console.log(`\nwrote ${jf}  (${all.length} aggregaten)`);
}
