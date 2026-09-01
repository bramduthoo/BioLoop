// 80/20 + gap analysis over the register, driven by the tested derivation.
const D = require("./derive.js"), P = require("./streams.json");

const fmt = n => n == null ? "-" : Math.round(n).toLocaleString("en-US");
const pct = x => x == null ? "-" : (100 * x).toFixed(1) + "%";

// which (edition, year) pairs carry residual claims
const combos = new Map();
P.claims.forEach(c => {
  if (c.role !== "Reststroom") return;
  const k = c.ed + " || " + c.yr;
  combos.set(k, (combos.get(k) || 0) + 1);
});

function walk(node, out) { out.push(node); (node.children || []).forEach(c => walk(c, out)); return out; }

function analyse(ed, yr) {
  const r = D.derive(P.claims, { year: yr, editions: new Set([ed]) });
  const rest = r.roots.find(x => x.label === "Reststroom");
  if (!rest) return null;
  const nodes = walk(rest, []);
  const deep = nodes.filter(n => (n.level === "l4" || n.level === "l5") && (n.repTotal || 0) > 0);
  // avoid double counting an l4 that also has l5 children: keep l5 where present
  const keep = deep.filter(n => !(n.level === "l4" && n.children.some(c => (c.repTotal || 0) > 0)));
  const l4sum = keep.reduce((a, n) => a + n.repTotal, 0);
  return { r, rest, nodes, keep, l4sum, unalloc: r.unallocated || [] };
}

console.log("=".repeat(100));
console.log("PART 1 - per source edition: reported L1 residual total vs what resolves to L4/L5");
console.log("=".repeat(100));
console.log(["edition / year", "L1 Reststroom", "L4+L5 sum", "resolved", "#L4/L5", "prov"]
  .map((s, i) => s.padEnd([46, 15, 15, 10, 8, 6][i])).join(""));

const rowsOut = [];
[...combos.keys()].sort().forEach(k => {
  const [ed, yrs] = k.split(" || "); const yr = Number(yrs);
  const a = analyse(ed, yr); if (!a) return;
  const rep = a.rest.repTotal || 0;
  rowsOut.push({ ed, yr, rep, l4: a.l4sum, n: a.keep.length, a });
  console.log([`${ed} (${yr})`.slice(0, 45), fmt(rep), fmt(a.l4sum),
    rep ? pct(a.l4sum / rep) : "-", String(a.keep.length),
    a.rest.totalProv || ""].map((s, i) => String(s).padEnd([46, 15, 15, 10, 8, 6][i])).join(""));
});

console.log("\n" + "=".repeat(100));
console.log("PART 2 - per L2 group, per edition: share of that edition's L1, and L4/L5 depth");
console.log("=".repeat(100));
rowsOut.forEach(({ ed, yr, rep, a }) => {
  console.log(`\n--- ${ed} (${yr})   L1 residual = ${fmt(rep)} t ---`);
  a.rest.children.forEach(g => {
    const nodes = walk(g, []);
    const deep = nodes.filter(n => (n.level === "l4" || n.level === "l5") && (n.repTotal || 0) > 0)
      .filter(n => !(n.level === "l4" && n.children.some(c => (c.repTotal || 0) > 0)));
    const dsum = deep.reduce((x, n) => x + n.repTotal, 0);
    const share = rep ? (g.repTotal || 0) / rep : 0;
    const flag = deep.length === 0 ? "  <-- NO L4/L5 DATA" :
      (g.repTotal && dsum / g.repTotal < 0.5 ? "  <-- thin" : "");
    console.log("   " + g.label.padEnd(26) + fmt(g.repTotal).padStart(12) +
      "  " + pct(share).padStart(7) + " of L1   L4/L5=" + fmt(dsum).padStart(11) +
      " (" + (g.repTotal ? pct(dsum / g.repTotal) : "-").padStart(6) + ", n=" +
      String(deep.length).padStart(2) + ")" + flag);
  });
  if (a.unalloc.length)
    console.log("   [unallocated band: " + a.unalloc.length + " aggregates, " +
      fmt(a.unalloc.reduce((x, u) => x + (u.v || u.repTotal || 0), 0)) + " t not placed]");
});

console.log("\n" + "=".repeat(100));
console.log("PART 3 - 80/20 selection, per edition (L4/L5 only, ranked by volume)");
console.log("=".repeat(100));
rowsOut.forEach(({ ed, yr, rep, a }) => {
  const items = a.keep.slice().sort((x, y) => y.repTotal - x.repTotal);
  const tot = a.l4sum; let cum = 0, n80 = 0;
  items.forEach((it, i) => { if (cum / tot < 0.8) { cum += it.repTotal; n80 = i + 1; } });
  console.log(`\n--- ${ed} (${yr}) --- ${items.length} selectable L4/L5 items, ${fmt(tot)} t`);
  console.log(`    ${n80} items (${pct(n80 / items.length)} of entries) carry 80% of the L4/L5 pool` +
    (rep ? ` = ${pct(0.8 * tot / rep)} of the reported L1 residual total` : ""));
  let c = 0;
  items.slice(0, 12).forEach((it, i) => {
    c += it.repTotal;
    console.log("      " + String(i + 1).padStart(2) + ". " +
      it.path.replace(/^Reststroom › /, "").slice(0, 58).padEnd(60) +
      fmt(it.repTotal).padStart(11) + "  cum " + pct(c / tot).padStart(6));
  });
});
