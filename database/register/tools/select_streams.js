// select_streams.js - the 80/20 stream selection over the register.
//
//   node select_streams.js [N] [--json out.json]
//
// Run prep_data.py first (BIOLOOP_REGISTRY=... to build from an alternative decision sheet).
//
// ---------------------------------------------------------------------------------------------
// METHOD - four choices, all of them deliberate
//
// 1. UNIT. One selectable stream = one L4 commodity node, keyed "L2 | L4". L3 is dropped from the
//    key because the sources use different nomenclatures at that layer (MONBIO says *Groenten*,
//    ILVO 239 and GeNeSys say *Groenten openlucht* / *beschut*) and they mean the same thing.
//    An L4 node's repTotal already contains its L5 fractions, so every fraction is counted once.
//
// 2. VALUE. V(s,k) is the derived repTotal of stream k inside ONE source's own derivation.
//    Values are never summed across sources - two sources reporting the same stream are two
//    measurements of one quantity, not two quantities.
//
// 3. RANK. M(k) = max over sources of V(s,k): the largest tonnage any single source in the corpus
//    attributes to the stream. NOT a mean. A source that does not report a stream has not measured
//    it - absence is not zero (register invariant) - so averaging would fold invented zeros into
//    the rank and would reward a stream for being *ubiquitous* rather than *large*. That is exactly
//    what went wrong in the first attempt: Boon (max 90.000 t, in two horticulture sources)
//    outranked Zemelen (278.865 t), Bostel (134.653 t) and Gries (98.390 t), which only the two
//    MONBIO editions report.
//
// 4. DENOMINATORS. Two, reported side by side, because they answer different questions:
//      pool(s) = sum of s's L4 nodes  -> the SELECTABLE CEILING: how much of what this source
//                                        published can be reached at L4 at all.
//      L1(s)   = s's own residual total -> how much of what it *claims exists* is reached.
//    A source cannot be asked for depth it never published, so coverage is scored against the
//    ceiling; L1 is shown alongside so the shortfall stays visible.
//    envelope = sum over streams of M(k) -> the corpus-wide size estimate the ranking runs on.
// ---------------------------------------------------------------------------------------------
const D = require("./derive.js"), P = require("../build/streams.json");

const byId = new Map(P.claims.map(c => [c.id, c]));
const fmt = n => n == null ? "-" : Math.round(n).toLocaleString("en-US").replace(/,/g, ".");
const pct = x => x == null || !isFinite(x) ? "-" : (100 * x).toFixed(1) + "%";
const walk = (n, o) => { o.push(n); (n.children || []).forEach(c => walk(c, o)); return o; };
const short = e => e.replace("OVAM Monitor voedselverlies ", "OVAM ")
  .replace(" ILVO 165", "").replace(" tuinbouw", "");

const EDS = [...new Set(P.claims.filter(c => c.role === "Reststroom").map(c => c.ed))].sort();
const src = {};                 // per source: L1, pool, n, per-L2 breakdown
const streams = new Map();      // "L2 | L4" -> { key, l2, l4, by: { source: {...} } }

EDS.forEach(ed => {
  const r = D.derive(P.claims, { editions: new Set([ed]) });   // no year filter: one source, all its years
  const rest = r.roots.find(x => x.label === "Reststroom");
  if (!rest) return;
  const l4 = walk(rest, []).filter(n => n.level === "l4" && (n.repTotal || 0) > 0);
  src[ed] = {
    L1: rest.repTotal || 0,
    pool: l4.reduce((a, n) => a + n.repTotal, 0),
    n: l4.length,
    groups: rest.children.map(g => {
      const gl4 = walk(g, []).filter(n => n.level === "l4" && (n.repTotal || 0) > 0);
      return { label: g.label, total: g.repTotal || 0, pool: gl4.reduce((a, n) => a + n.repTotal, 0), n: gl4.length };
    })
  };
  l4.forEach(n => {
    const p = n.path.split(" ¦ ");                 // Reststroom ¦ L2 ¦ L3 ¦ L4
    const key = p[1] + " | " + p[3];
    const cl = walk(n, []).flatMap(x => x.selfClaims || []).map(c => byId.get(c.id) || c);
    if (!streams.has(key)) streams.set(key, { key, l2: p[1], l4: p[3], by: {} });
    const rec = streams.get(key).by, prev = rec[ed];
    const own = (n.repTotal || 0) - (n.childTotal || 0);
    const cur = {
      v: n.repTotal,
      stages: [...new Set(cl.map(c => c.st))],
      geo: [...new Set(cl.map(c => c.geo))],
      claims: cl.map(c => c.id),
      // the fraction breakdown, so an L4 that bundles two materials is visible on its own row
      parts: (n.children || []).filter(c => (c.repTotal || 0) > 0).map(c => {
        const ccl = walk(c, []).flatMap(x => x.selfClaims || []).map(q => byId.get(q.id) || q);
        return { label: c.label, v: c.repTotal, st: [...new Set(ccl.map(q => q.st))], geo: [...new Set(ccl.map(q => q.geo))] };
      }).concat(own > 1 ? [{
        label: "(zonder fractie)", v: own,
        st: [...new Set((n.selfClaims || []).map(c => (byId.get(c.id) || c).st))],
        geo: [...new Set((n.selfClaims || []).map(c => (byId.get(c.id) || c).geo))]
      }] : [])
    };
    // one L4 label can sit under two L3 parents inside one source (Courgette openlucht + beschut)
    if (prev) {
      cur.v += prev.v;
      cur.claims = prev.claims.concat(cur.claims);
      ["stages", "geo"].forEach(f => cur[f] = [...new Set(prev[f].concat(cur[f]))]);
      cur.parts = prev.parts.concat(cur.parts);
    }
    rec[ed] = cur;
  });
});

const items = [...streams.values()].map(s => {
  const vals = EDS.filter(e => s.by[e]).map(e => s.by[e].v);
  s.M = Math.max(...vals); s.min = Math.min(...vals); s.nSrc = vals.length;
  s.spread = s.min > 0 ? s.M / s.min : null;
  ["stages", "geo"].forEach(f => s[f] = [...new Set(EDS.filter(e => s.by[e]).flatMap(e => s.by[e][f]))]);
  return s;
}).sort((a, b) => b.M - a.M);

const TOT = items.reduce((a, s) => a + s.M, 0);
let cum = 0, n80 = 0;
items.forEach((s, i) => { cum += s.M; s.cum = cum / TOT; if (!n80 && s.cum >= 0.80) n80 = i + 1; });

const coverage = sel => {
  const S = new Set(sel.map(s => s.key));
  return EDS.map(e => {
    const got = items.filter(s => S.has(s.key) && s.by[e]).reduce((a, s) => a + s.by[e].v, 0);
    return { e, got, pool: src[e].pool, L1: src[e].L1 };
  });
};

const argN = process.argv.find(a => /^\d+$/.test(a));
const N = Number(argN || n80);

console.log("=".repeat(108));
console.log("PER SOURCE - reported residual total (L1), selectable L4 ceiling (pool), items");
console.log("=".repeat(108));
EDS.forEach(e => console.log("  " + e.padEnd(36) + "L1 " + fmt(src[e].L1).padStart(11) +
  "   pool " + fmt(src[e].pool).padStart(11) + " = " + pct(src[e].pool / src[e].L1).padStart(7) +
  "   items " + String(src[e].n).padStart(3)));

console.log("\n" + "=".repeat(108));
console.log("RANKED STREAMS   envelope = " + fmt(TOT) + " t over " + items.length + " streams");
console.log("=".repeat(108));
items.forEach((s, i) => console.log(
  ("  " + String(i + 1).padStart(2) + " " + s.l4 + " (" + s.l2.replace("Plantaardig - ", "P-").replace("Dierlijk - ", "D-") + ")").padEnd(50) +
  fmt(s.M).padStart(11) + "  " + pct(s.cum).padStart(6) + "  n=" + s.nSrc +
  "  " + (s.spread ? s.spread.toFixed(1) + "x" : "-").padStart(7) +
  "  " + s.stages.map(x => x.slice(0, 11)).join("/") + " | " + s.geo.join("/")));
console.log("\n  -> " + n80 + " of " + items.length + " streams (" + pct(n80 / items.length) +
  " of entries) carry 80% of the envelope");

console.log("\n" + "=".repeat(108));
console.log("COVERAGE by selection size (share of each source's own L4 ceiling)");
console.log("=".repeat(108));
[...new Set([8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 30, n80, N])].sort((a, b) => a - b).forEach(k => {
  const sh = coverage(items.slice(0, k)).map(c => c.got / c.pool);
  console.log("  N=" + String(k).padStart(2) + "  mean " + pct(sh.reduce((a, b) => a + b, 0) / sh.length).padStart(7) +
    "  worst " + pct(Math.min(...sh)).padStart(7) + "   " +
    coverage(items.slice(0, k)).map(c => short(c.e).slice(0, 11) + " " + pct(c.got / c.pool)).join(" | "));
});

console.log("\n" + "=".repeat(108));
console.log("THE SELECTION (N=" + N + ")");
console.log("=".repeat(108));
console.log("  stream".padEnd(36) + EDS.map(e => short(e).slice(0, 11).padStart(12)).join(""));
items.slice(0, N).forEach((s, i) => console.log(
  ("  " + String(i + 1).padStart(2) + ". " + s.l4).padEnd(36) +
  EDS.map(e => (s.by[e] ? fmt(s.by[e].v) : "-").padStart(12)).join("")));
const cov = coverage(items.slice(0, N));
console.log("  " + "-".repeat(34 + 12 * EDS.length));
["selected|got", "L4 ceiling|pool", "L1 total|L1"].forEach(spec => {
  const [lab, f] = spec.split("|");
  console.log(("  " + lab).padEnd(36) + cov.map(c => fmt(c[f]).padStart(12)).join(""));
});
console.log("  % of ceiling".padEnd(36) + cov.map(c => pct(c.got / c.pool).padStart(12)).join(""));
console.log("  % of L1".padEnd(36) + cov.map(c => pct(c.got / c.L1).padStart(12)).join(""));

// ---------------------------------------------------------------------------------------------
// THE SELECTION AT ITS LOWEST DETAIL LEVEL (reviewer decision, 2026-09-03)
// A selected stream stays ONE item - Aardappel is Aardappel - but the number is reported per
// fraction rather than as the L4 sum, because an L4 sum and a single-fraction figure are not the
// same quantity and comparing them manufactures spread. Suikerbiet read at L4 spans 34x across
// sources; read at its fractions it does not.
// ---------------------------------------------------------------------------------------------
const fracKey = p => (p.label === "(zonder fractie)" ? "— " + p.st.join("/") : p.label);
items.forEach(s => {
  s.fracRows = new Map();
  EDS.filter(e => s.by[e]).forEach(e => s.by[e].parts.forEach(p => {
    const k = fracKey(p);
    if (!s.fracRows.has(k)) s.fracRows.set(k, { label: k, by: {}, st: p.st, geo: p.geo });
    const row = s.fracRows.get(k);
    row.by[e] = (row.by[e] || 0) + p.v;
    row.geo = [...new Set(row.geo.concat(p.geo))];
  }));
  s.fracRows.forEach(row => {
    const v = Object.values(row.by);
    row.M = Math.max(...v); row.min = Math.min(...v);
    row.spread = v.length > 1 && row.min > 0 ? row.M / row.min : null;
  });
});
console.log("\n" + "=".repeat(108));
console.log("THE SELECTION AT ITS LOWEST DETAIL LEVEL - one item, its fractions spelled out");
console.log("=".repeat(108));
console.log("  " + "stream / fraction".padEnd(44) + EDS.map(e => short(e).slice(0, 10).padStart(11)).join("") + "   spread");
items.slice(0, N).forEach((s, i) => {
  console.log("  " + (String(i + 1).padStart(2) + ". " + s.l4).padEnd(44) +
    EDS.map(e => (s.by[e] ? fmt(s.by[e].v) : "-").padStart(11)).join("") +
    "   " + (s.spread ? s.spread.toFixed(1) + "x" : "-"));
  if (s.fracRows.size > 1 || [...s.fracRows.keys()].some(k => k[0] !== "—"))
    [...s.fracRows.values()].sort((a, b) => b.M - a.M).forEach(row =>
      console.log("      " + ("· " + row.label).slice(0, 40).padEnd(40) +
        EDS.map(e => (row.by[e] ? fmt(row.by[e]) : "-").padStart(11)).join("") +
        "   " + (row.spread ? row.spread.toFixed(1) + "x" : "-") +
        (row.geo.includes("Belgie") ? "  [BE]" : "")));
});

console.log("\n" + "=".repeat(108));
console.log("BUNDLED L4s - one selected stream holding two physically different materials");
console.log("=".repeat(108));
items.slice(0, N).forEach(s => EDS.filter(e => s.by[e] && s.by[e].parts.length > 1).forEach(e =>
  console.log("  " + short(e).padEnd(12) + s.l4.padEnd(20) + fmt(s.by[e].v).padStart(10) + " = " +
    s.by[e].parts.map(p => p.label + " " + fmt(p.v) + " [" + p.st.join("/") + ", " + p.geo.join("/") + "]").join("  +  "))));

console.log("\n" + "=".repeat(108));
console.log("DIVERGENCE - streams two or more sources both report");
console.log("=".repeat(108));
items.filter(s => s.nSrc > 1).sort((a, b) => (b.spread || 0) - (a.spread || 0)).forEach(s => console.log(
  "  " + (s.l4 + " (" + s.l2.replace("Plantaardig - ", "P-").replace("Dierlijk - ", "D-") + ")").padEnd(40) +
  (s.spread ? s.spread.toFixed(1) + "x" : "-").padStart(8) + "   " +
  EDS.filter(e => s.by[e]).map(e => short(e) + "=" + fmt(s.by[e].v)).join("  ")));

console.log("\n" + "=".repeat(108));
console.log("FLAGS on the selection");
console.log("=".repeat(108));
items.slice(0, N).filter(s => s.nSrc === 1).forEach(s =>
  console.log("  single-source  " + s.l4.padEnd(24) + fmt(s.M).padStart(11) + "   only " + Object.keys(s.by)[0]));
items.slice(0, N).filter(s => s.geo.includes("Belgie")).forEach(s =>
  console.log("  Belgian figure " + s.l4.padEnd(24) + fmt(s.M).padStart(11) + "   geo=" + s.geo.join("/")));

const jf = process.argv[process.argv.indexOf("--json") + 1];
if (process.argv.includes("--json") && jf)
  require("fs").writeFileSync(jf, JSON.stringify({ EDS, src, TOT, n80, N, cov: coverage(items.slice(0, N)),
    items: items.map(s => Object.assign({}, s, { fracRows: [...s.fracRows.values()] })) }, null, 1));
