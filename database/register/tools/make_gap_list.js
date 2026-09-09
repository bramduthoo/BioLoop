// make_gap_list.js - derive the gap list from the data, as a consequence of the stream selection.
//
//   node tools/make_gap_list.js [--min 50000] [--json build/gaps_derived.json]
//
// Run prep_data.py first.
//
// ---------------------------------------------------------------------------------------------
// WHAT A GAP IS
//
// A gap is ASSERTED MASS MINUS SELECTABLE MASS, at a place in the data. Not a curated list and
// never inherited from a previous version: it is what falls out of the selection. The question
// it answers is the mirror of the selection's own - "where does the data still say material
// arises, that no selectable stream accounts for?"
//
//   asserted   the total a source reports at that place
//   reached    the mass beneath it that the selection could actually pick
//   gap        asserted - reached
//
// REACHABILITY follows select_streams.js exactly, or the two would disagree about what
// "selectable" means. One selectable stream = one L4 commodity node, and an L4 node's total
// already contains its L5 fractions. So a node AT or BELOW L4 is fully reached (it sits inside a
// selectable stream); above L4, reached is the sum of the L4 nodes in its subtree. Getting this
// wrong makes every L5 fraction look like a gap - Maisstro would be reported as 1,4 Mt
// unreachable while its parent Mais is the #1 selected stream.
//
// TWO RULES CARRY OVER FROM THE SELECTION, because they are the same rules.
//
// 1. NEVER SUM NESTED PLACES. `Reststroom` and `Reststroom > Varia > Dranken` overlap, so adding
//    their gaps counts the same tonnes twice. Each place therefore carries only its OWN gap:
//    ownGap(p) = gap(p) - sum of gap(children of p). That partitions exactly - the own-gaps sum
//    to the root's gap - so the list can be read as a decomposition rather than a pile.
//
// 2. NEVER SUM ACROSS SOURCES - but the mirror image of that rule needs care here. Taking the
//    best-reached figure across ALL sources would let one monitor cancel another's gap, and
//    `state.md` (2026-09-01) forbids exactly that: on the same year MONBIO reads 5.499.135 t
//    against OVAM's 2.583.633 t, 2,1x apart, because MONBIO counts productieresiduen and OVAM
//    only food-linked voedselreststromen. Ten of the thirteen selected streams are straw, leaf,
//    pulp and stalk - outside OVAM's scope by construction. Cancelling OVAM's food-industry lump
//    with MONBIO's processing detail would erase a real gap by comparing two different things.
//
//    So sources are merged WITHIN A SCOPE FAMILY and never across. Editions of one monitor
//    measure the same thing and are genuinely the same gap seen twice, so the largest reach
//    among them wins. Different monitors stay separate and each reports its own gap.
//
// GRANULARITY is (place x chain stage), because a source asserts per stage and a commodity node
// spans stages. That also locates the mass that has no commodity at all - OVAM's food-industry
// and retail lumps sit at the root, and without the stage axis they would be one opaque blob.
// ---------------------------------------------------------------------------------------------
const fs = require("fs"), path = require("path");
const D = require("./derive.js");
const HERE = __dirname, ROOT = path.dirname(HERE);
const P = JSON.parse(fs.readFileSync(path.join(ROOT, "build", "streams.json"), "utf8"));

const argMin = process.argv.indexOf("--min");
const MIN = argMin > -1 ? Number(process.argv[argMin + 1]) : 50000;
const walk = (n, o) => { o.push(n); (n.children || []).forEach(c => walk(c, o)); return o; };
const fmt = n => Math.round(n || 0).toLocaleString("de-DE");
const SHORT = e => e.replace("OVAM Monitor voedselverlies ", "OVAM ")
  .replace(" ILVO 165", "").replace(" tuinbouw", "");

// A family is sources that measure THE SAME THING, not sources with the same name. Grouping by
// name prefix left ILVO 239 and GeNeSys as singletons, so OVAM's `Groenten openlucht` lump
// (291.180 t, no L4 rows of its own) read as a gap even though ILVO 239 resolves it with 36 named
// rows - a scoping artefact reported as missing data (reviewer, 2026-09-09).
//
// The register already settled which school each source belongs to (log.md, 2026-09-03):
//   "OVAM 2020 (330.089) and ILVO 239 2015 (282.821) agree within 17% on tuinbouw, as they should
//    - ILVO 239 IS that monitor's agriculture chapter worked out"
//   "GeNeSys (894.535) against ILVO 239 (282.821) on horticulture, 3,2x, same institute"
// So the split is on WHAT COUNTS AS A RESIDUAL, exactly as state.md says of MONBIO vs OVAM:
//   voedselverlies    - food-linked losses only        OVAM monitors + ILVO 239
//   productieresidu   - everything that arises         MONBIO + GeNeSys (straw, leaf, oogstresten)
// Cross-family cancellation stays forbidden; within a family it is the same measurement twice.
const FAMILY = e => (e.startsWith("OVAM") || e.startsWith("ILVO 239")) ? "voedselverlies-school"
  : (e.startsWith("MONBIO") || e.startsWith("GeNeSys")) ? "productieresidu-school"
  : e;

// the registry's own words about each aggregate - why a row is unplaceable travels with it
const REGNOTE = (() => {
  const f = path.join(ROOT, "crosswalks", "aggregate_coverage.csv");
  const out = {};
  if (!fs.existsSync(f)) return out;
  const lines = fs.readFileSync(f, "utf8").replace(/^﻿/, "").split(/\r?\n/).filter(l => l.trim());
  const head = lines[0].split(";");
  const iNote = head.indexOf("note"), iCov = head.indexOf("commodity_coverage");
  lines.slice(1).forEach(l => {
    const c = l.split(";");
    if (c[0]) out[c[0].trim()] = { note: (c[iNote] || "").trim(), cov: (c[iCov] || "").trim() };
  });
  return out;
})();

const EDS = [...new Set(P.claims.filter(c => c.role === "Reststroom").map(c => c.ed))].sort();
const byId = new Map(P.claims.map(c => [c.id, c]));

// mass at `node` on `stage` that a selection can reach - see REACHABILITY above
function reachedAt(node, stage) {
  if (node.level === "l4" || node.level === "l5") return (node.repAgg[stage] || {}).display || 0;
  return walk(node, []).filter(x => x.level === "l4")
    .reduce((a, x) => a + ((x.repAgg[stage] || {}).display || 0), 0);
}

/* ---- reviewer-confirmed additions from the unallocated screening -----------------------------
 * An unallocatable aggregate can never enter the arithmetic - its 0% is structural. But screening
 * them one by one (tools/screen_unallocated.js, then read by hand) does turn up mass the
 * arithmetic cannot see. Those findings enter HERE, explicitly, so the list stays complete
 * without the arithmetic being bent to produce them.
 *
 * Two kinds, and the difference decides whether the total moves:
 *   nested    - names part of a residual that is ALREADY counted. Adds detail, never tonnage.
 *   additive  - mass no row in the list carries, because the aggregate that asserts it cannot be
 *               placed and the branch it belongs to has no node at all. Adds to the total.
 *
 * Reviewer decisions, 2026-09-09: C-094/C-195 nested under the food-industry residual, since that
 * is what they are part of; voedergewassen added; industriele gewassen (C-424/C-243, ~57.000 t)
 * deliberately left out as too small to act on.
 */
const FINDINGS = [
  { id: "S1", kind: "nested", family: "voedselverlies-school", stage: "Voedingsindustrie",
    under: "Reststroom", t: 621063, claims: "C-094 (2023), C-195 (2020)",
    place: "Aardappel-, groente- en fruitverwerking",
    what: "Van het onverklaarde deel van deze schakel is dit het grootste benoemde stuk. "
        + "Aardappelverwerking heeft in deze school geen enkele reststroom - de twee MONBIO-rijen "
        + "zijn Prodcom-cijfers voor gedroogde-aardappelmeel, een product en een andere school. "
        + "FRUITVERWERKING heeft nul rijen in het hele register. ILVO 239 helpt niet: die monitor "
        + "heeft geen enkele rij op de voedingsindustrie-schakel.",
    close: "een aardappelverwerkingsbron die per processtroom snijdt (schil, stoomschil, vezel, "
         + "eiwit) en een fruitverwerkingsbron (perskoek, schillen, pitten)" },
  { id: "S2", kind: "additive", family: "productieresidu-school", stage: "Primaire productie",
    t: 101780, claims: "C-242 (MONBIO 4.0), C-423 (MONBIO 3.0)",
    place: "Plantaardig - akkerbouw ¦ Voedergewassen",
    what: "MONBIO stelt 101.780 t nevenstromen en productieresiduen van voedergewassen, en er "
        + "staat GEEN ENKELE reststroomrij onder, in geen enkele bron. De gewassen zelf zijn "
        + "groot: voedermais 5.395.992, gras en hooi 3.939.458, voederbiet 360.547 t productie. "
        + "Onzichtbaar voor de rekensom omdat het aggregaat niet plaatsbaar is - er bestaat geen "
        + "Voedergewassen-knoop aan de reststroomkant om iets tegen af te rekenen.",
    close: "een bron die de residuen van voedermais, gras en voederbiet apart rapporteert; let op "
         + "dat deze gewassen als hele plant geoogst worden, dus het residu wordt zelden apart "
         + "gemeten" },
];

/* Annotations that a reviewer asked for on a specific place: what the corpus DOES know about a
 * gap, even when it sits in the other school and therefore cannot reduce it. */
const PLACE_NOTES = {
  "Reststroom ¦ Varia ¦ Dranken": "Bostel is de enige benoemde drankenreststroom in het corpus: "
    + "134.653 t (MONBIO 4.0) / 113.637 t (3.0), oftewel 36% van dit cijfer. Het staat in de "
    + "andere school, dus het verkleint dit gat niet rekenkundig - maar het is wel verreweg het "
    + "grootste identificeerbare deel ervan, en plausibel naast 1,7-1,8 Mt Vlaamse bierproductie. "
    + "De overige ~244.000 t heeft geen enkele benoemde stroom: sapperskoek, koffiedik, gist en "
    + "trub, frisdrankresidu. Appelsap (34.219 t) en koffie (36.953 t) staan wel als productie in "
    + "het register, hun residu niet.",
};

// ---- collect asserted / reached per (family, place, stage) -----------------------------------
const fams = new Map();
EDS.forEach(ed => {
  const fam = FAMILY(ed);
  const r = D.derive(P.claims, { editions: new Set([ed]) });
  const rest = r.roots.find(x => x.label === "Reststroom");
  if (!rest) return;
  const F = fams.get(fam) || { name: fam, eds: new Set(), places: new Map(), stages: new Set() };
  fams.set(fam, F);
  F.eds.add(ed);

  const stages = Object.keys(rest.covByStage || {});
  walk(rest, []).forEach(node => {
    stages.forEach(stage => {
      // the root's asserted figure per stage is the reported total derive already reconciles;
      // deeper nodes assert their own rolled-up figure for that stage
      const asserted = node.depth === 1
        ? ((rest.covByStage[stage] || {}).reported || 0)
        : ((node.repAgg[stage] || {}).display || 0);
      if (!(asserted > 0)) return;
      F.stages.add(stage);
      const key = node.path + " @@ " + stage;
      const p = F.places.get(key) || {
        key, path: node.path, depth: node.depth, label: node.label, level: node.level,
        stage, asserted: 0, reached: 0, assertedEd: "", reachedEd: "", per: {}, claims: []
      };
      if (asserted > p.asserted) {
        p.asserted = asserted; p.assertedEd = ed;
        // the aggregate rows that carry this assertion, for provenance on the row
        p.claims = (node.aggregates || [])
          .filter(a => a.claim.ed === ed && (a.stages || []).indexOf(stage) >= 0)
          .map(a => ({ id: a.claim.id, name: a.claim.name, v: a.claim.v }));
        if (node.depth === 1) {
          const set = (rest.totalSets[stage] || {});
          p.claims = Object.keys(set).flatMap(k => (set[k].values || [])
            .filter(v => v.isAgg).flatMap(v => v.members || [v])
            .map(v => ({ id: v.id, name: v.name, v: v.v })));
        }
      }
      const re = reachedAt(node, stage);
      if (re > p.reached) { p.reached = re; p.reachedEd = ed; }
      p.per[ed] = { asserted, reached: re };
      F.places.set(key, p);
    });
  });
});

// ---- context for the unattributable residual --------------------------------------------------
// CAREFUL. The mass left at a stage root belongs to no commodity branch, and the source DOES name
// it - but only through aggregates that are UNALLOCATABLE BY DESIGN, and their figures are not
// measurements of it.
//
// `crosswalks/aggregate_coverage.csv` settled this in an earlier phase and says so on the rows:
// C-094 "totals 3 L3 entries under 2 different L2 parents - unallocatable by design", C-098
// "totals meat + fish, which sit under 2 different L2 parents", C-097 and C-099 "OVAM subsector
// lump; includes components the register does not capture - the coverage % is a floor".
//
// C-094 mixes an L4 (Aardappel, under Aardappelen en knolgewassen) with two L3s (Groenten, Fruit)
// across two L2 groups. It therefore has no parent row at one level, its coverage is 0% BY
// CONSTRUCTION rather than by measurement, and part of its mass is reachable in another branch
// entirely. Summing these rows against the residual is comparing a structural artefact with a
// figure. An earlier version of this file did exactly that and reported them as the residual's
// composition (reviewer, 2026-09-09).
//
// They are kept because they are the only thing that NAMES the largest gap in the corpus -
// aardappelverwerking is the top target of the source hunt - but they are carried as CONTEXT:
// never summed, never a partition, always labelled with the registry's reason.
EDS.forEach(ed => {
  const fam = FAMILY(ed);
  const F = fams.get(fam); if (!F) return;
  const r = D.derive(P.claims, { editions: new Set([ed]) });
  F.unplaced = F.unplaced || new Map();
  (r.unallocated || []).forEach(u => {
    const c = u.claim;
    if (c.role !== "Reststroom" || !(c.v > 0)) return;
    // A row the REGISTRY shelved (allocatable = no, so prep_data blanks its parent) is a decision
    // already taken - a duplicate measurement, a parked scope variant, a parallel accounting. It is
    // not a structural placement failure and must not be offered as context for a gap.
    if (/^no row "" in the tree/.test(u.reason || "")) return;
    const key = c.st + " @@ " + (c.name || "").replace("AGGREGAAT - ", "");
    const cur = F.unplaced.get(key);
    if (!cur || c.v > cur.v)
      F.unplaced.set(key, { stage: c.st, name: (c.name || "").replace("AGGREGAAT - ", ""),
                            v: c.v, id: c.id, ed, qt: c.qt,
                            structural: true, why: (REGNOTE[c.id] || {}).note || u.reason || "" });
  });
});

// ---- de-nest: each place keeps only the gap its children do not already carry ----------------
const rows = [];
fams.forEach(F => {
  const all = [...F.places.values()];
  all.forEach(p => {
    p.gap = Math.max(0, p.asserted - p.reached);
    /* A cross-source gap takes the largest claim from one source and the best coverage from
       another. That answers "what does NOBODY reach", but the number itself is a hybrid that no
       single source supports - and the two sides can differ in year and in scope. `Groenten
       openlucht`: OVAM 2023 asserts 291.180 while ILVO 239 (2015) reaches 205.471, so the 85.709
       belongs to neither. Report the same-source gap beside it and mark the row, so a hybrid is
       never mistaken for a measurement (reviewer, 2026-09-09). */
    p.sameSourceGap = Math.max(0, ...Object.values(p.per).map(x => x.asserted - x.reached));
    p.sameSourceEd = (Object.entries(p.per)
      .filter(([, x]) => Math.max(0, x.asserted - x.reached) === p.sameSourceGap)[0] || [""])[0];
    p.hybrid = p.assertedEd !== p.reachedEd && p.reached > 0;
  });
  const childrenOf = p => all.filter(q => q.stage === p.stage
    && q.path.startsWith(p.path + " ¦ ") && q.depth === p.depth + 1);
  all.forEach(p => {
    const kidGap = childrenOf(p).reduce((a, q) => a + q.gap, 0);
    p.ownGap = p.gap - kidGap;
    p.nKids = childrenOf(p).length;
  });
  F.rows = all;
  // the identity that makes this a decomposition rather than a pile
  F.stages.forEach(stage => {
    const root = all.find(p => p.depth === 1 && p.stage === stage);
    if (!root) return;
    const sum = all.filter(p => p.stage === stage).reduce((a, p) => a + p.ownGap, 0);
    if (Math.abs(sum - root.gap) > Math.max(1, root.gap * 0.001))
      console.log(`!! ${F.name} / ${stage}: ownGap-som ${fmt(sum)} != wortelgap ${fmt(root.gap)}`);
  });
  all.forEach(p => {
    if (p.depth !== 1) return;
    // Only the edition that supplied the asserted figure, or the list mixes two editions of the
    // same monitor and reads as if it summed. EU-definitie rows are a PARALLEL accounting of the
    // same material (protocol: "same stream, incompatible definitions"), so they are marked and
    // never counted as a part.
    p.unplaced = [...(F.unplaced || new Map()).values()]
      .filter(u => u.stage === p.stage && u.ed === p.assertedEd)
      .map(u => Object.assign({ parallel: /EU-definitie/i.test(u.name) }, u))
      .sort((a, b) => b.v - a.v);
  });
  all.filter(p => p.ownGap >= MIN).forEach(p => rows.push(Object.assign({ family: F.name }, p)));
});

// ---- what is missing, and what would close it - derived, not inherited ----------------------
const VARIA_SECTOR = /^Reststroom ¦ Varia ¦ /;
function describe(p) {
  const isRoot = p.depth === 1;
  const branch = p.path.replace("Reststroom ¦ ", "");
  if (isRoot) {
    return {
      what: `de bron rapporteert deze schakel als totaal; ${fmt(p.reached)} t is elders in de boom `
        + `bereikbaar, de rest hangt aan geen enkel gewas. De sectorrijen die de bron er wél voor `
        + `geeft zijn structureel onplaatsbaar (mengen een L4 met L3's over twee L2-groepen), dus `
        + `hun cijfers zijn context en geen meting van dit gat`,
      close: `een bron die deze schakel per productgroep rapporteert in plaats van als sectortotaal`
    };
  }
  if (VARIA_SECTOR.test(p.path)) {
    return {
      what: p.reached > 0
        ? `de sector heeft ${fmt(p.reached)} t aan benoemde stromen, maar niet genoeg om het totaal te dekken`
        : `de sector heeft geen enkele benoemde stroom - het totaal is alles wat er is`,
      close: `een sectorbron die per PROCES snijdt in plaats van per productcode (screeningsregel F-003)`
    };
  }
  return {
    what: p.reached > 0
      ? `${p.nKids} tak(ken) eronder leveren samen ${fmt(p.reached)} t; het verschil hangt aan geen benoemde stroom`
      : `geen enkele benoemde stroom onder deze tak`,
    close: `een bron die ${branch} per gewas of per materiaal uitsplitst`
  };
}
rows.forEach(p => Object.assign(p, describe(p)));

// ---- consolidation: nest a deeper gap under the shallower one it sits inside -----------------
// A gap under `Varia` and a gap under `Varia > Dranken` are one story told at two depths; the
// reviewer reads them together. Parents keep their own (already de-nested) tonnage.
rows.sort((a, b) => b.ownGap - a.ownGap);
rows.forEach(p => {
  p.parentKey = null;
  const cands = rows.filter(q => q !== p && q.stage === p.stage
    && p.path.startsWith(q.path + " ¦ "));
  if (cands.length) p.parentKey = cands.sort((a, b) => b.depth - a.depth)[0].key;
});

// ---- report ---------------------------------------------------------------------------------
const W = 104;
console.log("=".repeat(W));
console.log(`GAPLIJST - afgeleid uit de data, drempel ${fmt(MIN)} t/jaar eigen gap`);
console.log("=".repeat(W));
fams.forEach(F => {
  const mine = F.rows.filter(p => p.ownGap >= MIN);
  console.log(`\n### ${F.name}   (${[...F.eds].join(" + ")})`);
  if (!mine.length) {
    // a family whose every assertion is reachable is a RESULT, not an empty section
    const worst = F.rows.reduce((a, p) => Math.max(a, p.ownGap), 0);
    console.log(`  geen gap boven de drempel - grootste losse gap ${fmt(worst)} t`);
    return;
  }
  // stages this family actually asserts a total for; the rest are reported without a stage root
  [...F.stages].sort().forEach(stage => {
    const inStage = mine.filter(p => p.stage === stage).sort((a, b) => b.ownGap - a.ownGap);
    if (!inStage.length) return;
    const root = F.rows.find(p => p.depth === 1 && p.stage === stage);
    console.log("  " + stage.padEnd(30) + (root
      ? `beweerd ${fmt(root.asserted).padStart(10)}  bereikbaar ${fmt(root.reached).padStart(10)}`
        + `  GAP ${fmt(root.gap).padStart(10)}`
      : "(deze bron geeft geen schakeltotaal; de gaps hieronder staan op eigen takken)"));
    inStage.forEach(p => {
      console.log(`       ${fmt(p.ownGap).padStart(10)}  `
        + (p.depth === 1 ? "(hangt aan geen enkele commoditytak)"
          : p.path.replace("Reststroom ¦ ", "")).slice(0, 60));
      if (p.hybrid) console.log(`                   ! HYBRIDE: ${SHORT(p.assertedEd)} beweert `
        + `${fmt(p.asserted)}, ${SHORT(p.reachedEd)} bereikt ${fmt(p.reached)}. `
        + `Binnen één bron is het grootste gat ${fmt(p.sameSourceGap)} (${SHORT(p.sameSourceEd)}).`);
      if (p.depth === 1) {
        const ctx = p.unplaced || [];
        if (!ctx.length) { console.log("            (de bron benoemt deze massa niet verder)"); return; }
        console.log("            context - structureel onplaatsbare sectorrijen, GEEN meting en nooit optellen:");
        ctx.forEach(u => console.log(`            ${fmt(u.v).padStart(9)}  ~ ${u.name.slice(0, 52)} [${u.id}]`
          + (u.parallel ? " PARALLELLE TELLING" : "")));
      }
    });
  });
});
console.log("\n" + "=".repeat(104));
console.log("GESCREENDE BEVINDINGEN - uit de onplaatsbare aggregaten, door de reviewer bevestigd");
console.log("=".repeat(104));
FINDINGS.forEach(f => {
  console.log(`\n  [${f.id}] ${f.kind === "additive" ? "TELT MEE" : "genest, telt NIET mee"}  `
    + `${fmt(f.t)} t   ${f.place}`);
  console.log(`       ${f.family} / ${f.stage}   claims: ${f.claims}`);
  console.log(`       ${f.what.slice(0, 92)}`);
});

const tot = rows.reduce((a, p) => a + p.ownGap, 0)
  + FINDINGS.filter(f => f.kind === "additive").reduce((a, f) => a + f.t, 0);
console.log(`\n${rows.length} gaprijen + ${FINDINGS.length} gescreende bevindingen`
  + ` (waarvan ${FINDINGS.filter(f => f.kind === "additive").length} meetellend)`
  + `, samen ${fmt(tot)} t/jaar`);

const jf = process.argv[process.argv.indexOf("--json") + 1];
if (process.argv.includes("--json") && jf) {
  const out = {
    min: MIN, generated: new Date().toISOString().slice(0, 10),
    families: [...fams.values()].map(F => ({
      name: F.name, editions: [...F.eds].sort(),
      stages: [...F.stages].sort().map(stage => {
        const root = F.rows.find(p => p.depth === 1 && p.stage === stage);
        return root ? {
          stage, asserted: root.asserted, reached: root.reached, gap: root.gap,
          claims: root.claims
        } : null;
      }).filter(Boolean)
    })),
    findings: FINDINGS,
    rows: rows.map(p => ({
      family: p.family, key: p.key, parentKey: p.parentKey, stage: p.stage,
      place: p.depth === 1 ? "(geen commoditytak)" : p.path.replace("Reststroom ¦ ", ""),
      path: p.path, depth: p.depth,
      asserted: p.asserted, reached: p.reached, gap: p.gap, ownGap: p.ownGap,
      assertedEd: p.assertedEd, reachedEd: p.reachedEd, hybrid: !!p.hybrid,
      sameSourceGap: p.sameSourceGap, sameSourceEd: p.sameSourceEd,
      claims: p.claims, unplaced: p.unplaced || [],
      note: PLACE_NOTES[p.path] || null,
      what: p.what, close: p.close
    }))
  };
  fs.writeFileSync(jf, JSON.stringify(out, null, 1));
  console.log(`wrote ${jf}`);
}
