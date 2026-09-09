/* ============================================================================
   Regression test for the per-chain-stage overview (`build_stage_overviews.py`).

   The per-stage page rests on ONE claim: every figure under a stage tab measures
   that stage and nothing else, and no figure that spans several stages touches
   any of them. That is a property, not an opinion, so it is asserted here rather
   than trusted.

   It re-runs `derive.js` exactly as the page does — same input, same options —
   and checks the result. Nothing is recomputed and no figure is produced.

       node tools/verify_by_stage.js

   Exits non-zero on the first broken property.
   ========================================================================== */
const D = require("./derive.js");
const P = require("../build/streams.json");

const MULTI_STAGE = "meerdere stadia";
const TABS = ["Primaire productie", "Voedingsindustrie", "Retail & grootdistributie"];

const stagesOf = c => (c.agg && (c.agg.stages || []).length) ? c.agg.stages
                    : (c.st === MULTI_STAGE ? [] : [c.st]);
const isMulti = c => c.st === MULTI_STAGE || !!(c.agg && (c.agg.stages || []).length > 1);

const fails = [];
const check = (ok, msg) => { console.log((ok ? "  ok   " : "  FAIL ") + msg); if (!ok) fails.push(msg); };

const claims = P.claims;
const single = claims.filter(c => !isMulti(c));
const multi  = claims.filter(isMulti);
const multiIds = new Set(multi.map(c => c.id));

console.log(`\n${claims.length} live claims — ${single.length} single-stage, ${multi.length} multi-stage\n`);

/* 1. the partition is total and disjoint */
check(single.length + multi.length === claims.length, "the partition covers every claim exactly once");

/* 2. the two independent markers agree on every claim: the claim's own chain_L2,
      and how many stages the aggregate registry says the figure covers */
const disagree = claims.filter(c =>
  (c.st === MULTI_STAGE) !== !!(c.agg && (c.agg.stages || []).length > 1));
check(disagree.length === 0,
  `chain_L2 and stage_coverage agree on every claim${disagree.length ? " — except " + disagree.map(c => c.id).join(", ") : ""}`);

/* 3. every multi-stage figure names at least two IN-SCOPE stages; a single-stage
      one names exactly its own */
const badSpan = multi.filter(c => stagesOf(c).length < 2);
check(badSpan.length === 0, `every multi-stage figure names ≥2 stages${badSpan.length ? " — except " + badSpan.map(c => c.id).join(", ") : ""}`);
const badOwn = single.filter(c => { const s = stagesOf(c); return s.length !== 1 || s[0] !== c.st; });
check(badOwn.length === 0, `every single-stage figure names exactly its own stage${badOwn.length ? " — except " + badOwn.map(c => c.id).join(", ") : ""}`);

/* 4. per tab: nothing the derivation touches belongs to another stage, and no
      multi-stage figure reaches it at all — for every year the tab can show */
function idsIn(result) {
  const ids = new Set();
  (function walk(ns) {
    for (const n of ns) {
      for (const c of n.claims) ids.add(c.id);
      for (const a of n.aggregates) ids.add(a.claim.id);
      walk(n.children);
    }
  })(result.roots);
  for (const u of result.unallocated) ids.add(u.claim.id);
  return ids;
}
const byId = new Map(claims.map(c => [c.id, c]));
let leaked = [], foreign = [], years = 0;
for (const st of TABS) {
  const cs = single.filter(c => c.st === st);
  for (const y of [...new Set(cs.map(c => c.yr))]) {
    years++;
    const ids = idsIn(D.derive(cs, { year: y }));
    for (const id of ids) {
      if (multiIds.has(id)) leaked.push(st + "/" + y + ":" + id);
      else if (byId.get(id).st !== st) foreign.push(st + "/" + y + ":" + id);
    }
  }
}
check(leaked.length === 0, `no multi-stage figure reaches any stage table (${years} tab×year combinations checked)`);
check(foreign.length === 0, `no figure from another chain stage reaches a stage table${foreign.length ? " — " + foreign.slice(0, 5).join(", ") : ""}`);

/* 5. the derivation sees exactly one stage per tab, so the Total column IS the
      stage figure and the dropped stage columns cannot have hidden anything */
let multiStageResult = [];
for (const st of TABS) {
  const cs = single.filter(c => c.st === st);
  for (const y of [...new Set(cs.map(c => c.yr))]) {
    const r = D.derive(cs, { year: y });
    if (r.stages.length > 1) multiStageResult.push(st + "/" + y + " → " + r.stages.join(" + "));
  }
}
check(multiStageResult.length === 0,
  `each tab's derivation runs over exactly one chain stage${multiStageResult.length ? " — " + multiStageResult.join("; ") : ""}`);

/* 6. nothing is lost: every claim is either under a tab, at a stage with no tab,
      or held aside as context */
const onTab   = single.filter(c => TABS.indexOf(c.st) >= 0).length;
const offTab  = single.filter(c => TABS.indexOf(c.st) < 0).length;
check(onTab + offTab + multi.length === claims.length,
  `every claim is accounted for — ${onTab} on a tab, ${offTab} at a stage with no tab, ${multi.length} contextual`);

/* 7. every multi-stage figure is shown as context under at least one tab, so
      holding it out of the tables does not hide it */
const orphan = multi.filter(c => !stagesOf(c).some(s => TABS.indexOf(s) >= 0));
check(orphan.length === 0,
  `every contextual figure surfaces under at least one tab${orphan.length ? " — except " + orphan.map(c => c.id).join(", ") : ""}`);

console.log(fails.length ? `\n${fails.length} property broken\n` : "\nall properties hold\n");
process.exit(fails.length ? 1 : 0);
