/* ============================================================================
   BIOLOOP stream overview — derivation (pure, DOM-free, verifiable in Node).

   TWO AXES, not one.

   1. The commodity tree — role -> L2 -> L3 -> L4 -> L5 — built from COMPONENT
      claims only. Components sum with their siblings, as they always did.

   2. The aggregate axis. An `AGGREGAAT - ` claim is not a commodity; it claims
      "the total of these rows is X". It never enters a sum. It attaches to the
      row whose children it totals and becomes that row's reported total, i.e.
      the DENOMINATOR the coverage check divides into.

   An aggregate is placeable only when everything it covers sits under ONE parent
   row at ONE level. Anything else (a total spanning two L2 groups, say) has no
   row to hang from and goes to `unallocated`: visible, never compared, never
   summed.

   Competing totals for one (row, level, stage, quantity type) are VARIANTS. The
   representative is their mean and every value is kept for display and exclusion
   — they are never added together. The one exception is a set the registry marks
   `component_set` (collection-route halves, which genuinely do sum).

   Every figure carries provenance {sum, avg} so the view can mark what is a
   reading and what is arithmetic.
   ============================================================================ */
(function (root) {
  const LEVELS = ['role','l2','l3','l4','l5'];
  const QTK = {'hoofdstroom':'prod','agri-food waste':'afwE','nevenstroom':'nev','voedselverlies':'voe'};
  const QT_ORDER = ['prod','afwE','nev','voe'];
  const ROLE_ORDER = ['Reststroom','Productievolume'];      // internal keys; UI relabels to English
  const SEP = ' ¦ ';
  const LEVEL_INDEX = {L2:1, L3:2, L4:3, L5:4};

  const sum  = a => a.reduce((x,y)=>x+y,0);
  const mean = a => a.length ? sum(a)/a.length : 0;
  const prov = (s,a) => ({sum:!!s, avg:!!a});
  const provOr = list => prov(list.some(p=>p&&p.sum), list.some(p=>p&&p.avg));
  const emptyStage = () => ({afwE:0,nev:0,voe:0,prod:0,display:0,prov:prov(false,false)});
  const displayOf = s => s.prod>0 ? s.prod : (s.afwE>0 ? s.afwE : s.nev+s.voe);
  /* agri-food waste = nevenstroom + voedselverlies, so a row that reports only the split still
     answers an `agri-food waste` aggregate. */
  const qtValue = (s,k) => !s ? 0 : (k==='afwE' ? (s.afwE>0 ? s.afwE : s.nev+s.voe) : s[k]);

  /* ---------- commodity tree (components only) ---------- */
  function buildNodes(claims, depth, parentPath){
    const level = LEVELS[depth], byKey = new Map();
    for (const c of claims){ const k=c[level]; if(k==null) continue; if(!byKey.has(k)) byKey.set(k,[]); byKey.get(k).push(c); }
    let keys = Array.from(byKey.keys());
    if (level==='role') keys.sort((a,b)=>(ROLE_ORDER.indexOf(a)+1||99)-(ROLE_ORDER.indexOf(b)+1||99));
    const nodes=[];
    for (const label of keys){
      const g=byKey.get(label), next=LEVELS[depth+1];
      const path = parentPath ? parentPath+SEP+label : label;
      const selfClaims = next ? g.filter(c=>c[next]==null) : g;   // claims that stop at this node
      const children   = next ? buildNodes(g, depth+1, path) : [];
      nodes.push({ level, depth: depth+1, label, path, id: path, role: g[0].role,
                   selfClaims, claims:g, children, aggregates:[] });
    }
    return nodes;
  }

  function aggOne(claims){                          // one source -> {stage:{afwE,nev,voe,prod,display}}
    const per = {};
    for (const c of claims){
      const s = per[c.st] = per[c.st] || emptyStage();
      const k = QTK[c.qt]; if(!k) continue;
      s[k] += c.v; s.n = (s.n||0) + 1;
    }
    for (const st in per){ const s=per[st]; s.display = displayOf(s); s.prov = prov(s.n>1, false); }
    return per;
  }

  /* ---------- aggregate placement ---------- */
  function indexNodes(roots){
    const byPath = new Map();
    (function walk(ns){ for(const n of ns){ byPath.set(n.path, n); walk(n.children); } })(roots);
    return byPath;
  }

  /* An aggregate is allocatable iff its parent row exists and every entry it names is a child
     of that row at the level it totals. Otherwise it has no row to hang from. */
  function placeAggregates(roots, aggClaims, allStages){
    const byPath = indexNodes(roots), unallocated = [];
    for (const c of aggClaims){
      const a = c.agg, parent = byPath.get(a.parent);
      let why = null;
      if (!parent) why = 'no row "'+a.parent+'" in the tree';
      else if (parent.depth !== (LEVEL_INDEX[a.level]||99)) why = 'row "'+parent.label+'" is not one level above '+a.level;
      else if (a.cov !== 'full'){
        const labels = new Set(parent.children.map(k=>k.label));
        const missing = a.cov.filter(x=>!labels.has(x));
        if (missing.length === a.cov.length) why = 'none of its entries ('+a.cov.join(', ')+') are rows under "'+parent.label+'"';
      }
      if (why){ unallocated.push({claim:c, reason:why}); continue; }

      const stages = a.stages.filter(s=>allStages.indexOf(s)>=0);
      const spread = stages.length === 0 ? 'none'
                   : stages.length === 1 ? 'stage'
                   : stages.length === allStages.length ? 'all'
                   : 'stage-subset';
      parent.aggregates.push({claim:c, cov:a.cov, stages, spread,
        full: a.cov==='full' && (spread==='stage' || spread==='all'),
        treatment:a.treatment, reviewed:a.reviewed, note:a.note, level:a.level});
    }
    return unallocated;
  }

  /* Competing totals for one key -> one representative. Values are never added, except a
     registry-marked component_set (collection-route halves that genuinely sum). */
  function variantSet(values){
    if (!values.length) return null;
    const parts = [], singles = [];
    for (const v of values) (v.treatment==='component_set' ? parts : singles).push(v);
    const list = singles.slice();
    if (parts.length) list.push({ id: parts.map(p=>p.id).join('+'), ed: parts[0].ed,
        name: parts.map(p=>p.name).join('  +  '), v: sum(parts.map(p=>p.v)),
        isAgg: true, reviewed: parts.every(p=>p.reviewed), members: parts, summed: true });
    if (!list.length) return null;

    /* A component_set that adds up to a total already stated in this group is a RESTATEMENT of
       it, not a rival measurement of it — the halves of a collection-route split reproduce the
       stage total the source printed beside them. Averaging both would weight that one figure
       twice against a genuine variant. Keep it visible, mark what it restates, and leave it out
       of the mean. */
    for (const x of list){
      if (!x.summed) continue;
      const same = list.find(y => y !== x && !y.summed && y.v>0 && Math.abs(y.v-x.v)/y.v < 0.005);
      if (same){ x.restates = same.id; }
    }
    const counted = list.filter(x=>!x.restates);
    return { values: list, rep: mean(counted.map(x=>x.v)),
             prov: prov(counted.some(x=>x.summed), counted.length>1) };
  }

  /* ---------- per-node computation ---------- */
  function compute(node, allStages){
    for (const c of node.children) compute(c, allStages);

    // one value per source from this node's own component claims (a source's rows sum)
    const bySrc = {};
    for (const c of node.selfClaims) (bySrc[c.ed] = bySrc[c.ed] || []).push(c);
    node.ownBySource = {};
    for (const ed in bySrc) node.ownBySource[ed] = aggOne(bySrc[ed]);

    // totals[stage][qtKey] and the Total column's own set, from own claims + full aggregates
    const totals = {}, totalCol = {};
    const put = (bag, st, k, val) => { (bag[st] = bag[st] || {}); (bag[st][k] = bag[st][k] || []).push(val); };
    for (const ed in node.ownBySource){
      const per = node.ownBySource[ed];
      for (const st in per) for (const k of QT_ORDER) if (per[st][k] > 0)
        put(totals, st, k, {id:'own:'+ed+':'+st+':'+k, ed, name:'reported at this level', v:per[st][k],
                            isAgg:false, reviewed:true, summed:per[st].prov.sum});
    }
    node.subsets = [];
    for (const a of node.aggregates){
      const k = QTK[a.claim.qt]; if(!k) continue;
      const val = {id:a.claim.id, ed:a.claim.ed, name:a.claim.name, v:a.claim.v, isAgg:true,
                   reviewed:a.reviewed, treatment:a.treatment, note:a.note, cov:a.cov, stages:a.stages};
      if (a.full && a.spread==='stage') put(totals, a.stages[0], k, val);
      else if (a.full && a.spread==='all') put(totalCol, '__all__', k, val);
      else node.subsets.push(a);                       // partial commodity or partial stage coverage
    }
    node.totalSets = {};
    for (const st in totals){ node.totalSets[st] = {}; for (const k in totals[st]) node.totalSets[st][k] = variantSet(totals[st][k]); }
    node.totalColSets = {};
    for (const k in (totalCol['__all__']||{})) node.totalColSets[k] = variantSet(totalCol['__all__'][k]);

    // per stage: children's roll-up, then the chosen figure (a reported total wins over the sum)
    node.childAgg = {}; node.repAgg = {}; node.covByStage = {};
    for (const st of allStages){
      const kids = node.children.map(c=>c.repAgg[st]).filter(Boolean);
      const cs = emptyStage();
      for (const k of QT_ORDER) cs[k] = sum(kids.map(x=>x[k]));
      cs.display = displayOf(cs);
      // provenance is transitive: a roll-up of a roll-up is still arithmetic, not a reading
      cs.prov = prov(kids.length>1 || kids.some(x=>x.prov.sum), kids.some(x=>x.prov.avg));
      node.childAgg[st] = cs;

      const chosen = emptyStage(); const ps = [];
      for (const k of QT_ORDER){
        const set = node.totalSets[st] && node.totalSets[st][k];
        if (set){ chosen[k] = set.rep; ps.push(set.prov); }
        else { chosen[k] = cs[k]; if (cs[k]>0) ps.push(cs.prov); }
      }
      chosen.display = displayOf(chosen);
      chosen.prov = provOr(ps);
      node.repAgg[st] = chosen;

      const anyTotal = node.totalSets[st] && Object.keys(node.totalSets[st]).length;
      node.covByStage[st] = (anyTotal && chosen.display>0)
        ? {reported:chosen.display, components:cs.display, ratio:cs.display/chosen.display,
           status:severityOf(cs.display/chosen.display, cs.display)} : null;
    }

    // Total column: an all-stage aggregate if there is one, else the sum across stages
    const stageDisplays = allStages.map(st=>node.repAgg[st].display);
    const allSet = node.totalColSets.prod || node.totalColSets.afwE || node.totalColSets.nev || node.totalColSets.voe;
    node.childTotal = sum(node.children.map(c=>c.repTotal||0));
    if (allSet){ node.repTotal = allSet.rep; node.totalProv = allSet.prov; node.totalFromAggregate = true; }
    else {
      node.repTotal = sum(stageDisplays);
      node.totalProv = prov(stageDisplays.filter(v=>v>0).length>1
                              || allStages.some(st=>node.repAgg[st].prov.sum),
                            allStages.some(st=>node.repAgg[st].prov.avg));
      node.totalFromAggregate = false;
    }

    // coverage — measured only over the stages that actually have a reported total
    const withTotal = allStages.filter(st=>node.covByStage[st]);
    node.coverage = null;
    if (withTotal.length){
      const rep = sum(withTotal.map(st=>node.covByStage[st].reported));
      const comp = sum(withTotal.map(st=>node.covByStage[st].components));
      if (rep>0) node.coverage = {reported:rep, components:comp, ratio:comp/rep, stages:withTotal};
    }
    node.severity = node.coverage ? severityOf(node.coverage.ratio, node.coverage.components) : null;

    /* Subset checks. Group first — two halves of one collection-route split are one figure,
       and two definitions of one subset are variants of each other; checking either of them
       row by row produces nonsense percentages. */
    const groups = new Map();
    for (const a of node.subsets){
      const k = QTK[a.claim.qt]; if(!k) continue;
      const covKey = a.cov==='full' ? 'full' : a.cov.slice().sort().join('+');
      const key = [a.level, a.stages.join('+'), k, covKey].join('|');
      if (!groups.has(key)) groups.set(key, {key, qtKey:k, cov:a.cov, stages:a.stages,
                                            level:a.level, spread:a.spread, items:[]});
      groups.get(key).items.push({id:a.claim.id, ed:a.claim.ed, name:a.claim.name, v:a.claim.v,
        isAgg:true, reviewed:a.reviewed, treatment:a.treatment, note:a.note});
    }
    node.subsetSets = Array.from(groups.values()).map(g=>{
      const set = variantSet(g.items);
      const kids = g.cov==='full' ? node.children : node.children.filter(c=>g.cov.indexOf(c.label)>=0);
      const comp = sum(kids.map(c=>sum(g.stages.map(st=>qtValue(c.repAgg[st], g.qtKey)))));
      const check = (set && set.rep>0) ? {components:comp, ratio:comp/set.rep, n:kids.length} : null;
      g.set = set; g.check = check;
      g.severity = check ? severityOf(check.ratio, check.components) : null;
      return g;
    });

    // display extras carried over from the previous derivation
    node.isLeaf = node.children.length === 0;
    node.nSources = new Set(node.claims.map(c=>c.ed)).size;
    node.sourceRows = Object.keys(node.ownBySource).map(ed=>({
        ed, agg: node.ownBySource[ed], claims: bySrc[ed],
        total: sum(Object.values(node.ownBySource[ed]).map(s=>s.display)),
        assumed: bySrc[ed].some(c=>c.asm) })).filter(r=>r.total>0).sort((a,b)=>b.total-a.total);
    node.nSelfSources = node.sourceRows.length;
    node.selfSources = node.sourceRows.map(r=>r.ed);
    const owns = node.sourceRows.map(r=>r.total);
    node.spreadMin = owns.length?Math.min(...owns):null;
    node.spreadMax = owns.length?Math.max(...owns):null;
    node.deepLeafSum = node.isLeaf ? node.repTotal : sum(node.children.map(c=>c.deepLeafSum));
    node.deepPct = node.repTotal>0 ? node.deepLeafSum/node.repTotal : 1;
    node.leafCount = node.isLeaf ? 1 : sum(node.children.map(c=>c.leafCount));
    node.assumed = node.claims.some(c=>c.asm);
    node.unreviewed = node.aggregates.some(a=>!a.reviewed);
    return node;
  }

  /* No components beneath an aggregate is not 0% coverage — it is a figure that cannot be
     checked at all. Such an aggregate is still the best estimate for what it covers, so it is
     kept and marked `indicative` rather than scored. */
  function severityOf(r, components){
    if (r==null) return null;
    if (!(components>0)) return 'indicative';
    if (r > 1.5)  return 'severe';                    // parts exceed the total by half again
    if (r > 1.05) return 'over';
    if (r < 0.95) return 'under';
    return 'ok';
  }

  function countSevere(nodes){
    let n = 0;
    (function walk(ns){ for(const x of ns){ if(x.severity==='severe') n++;
      for(const a of x.subsetSets||[]) if(a.severity==='severe') n++; walk(x.children); } })(nodes);
    return n;
  }

  function derive(claims, opts){
    const o = opts || {}, yr = o.year, eds = o.editions, ex = o.excluded;
    const f = claims.filter(c => (yr==null || c.yr===yr) && (!eds || eds.has(c.ed)) && !(ex && ex.has(c.id)));
    const components = f.filter(c=>!c.agg), aggs = f.filter(c=>c.agg);
    const allStages = Array.from(new Set(f.map(c=>c.st).filter(Boolean)));
    const roots = buildNodes(components, 0, '');
    const unallocated = placeAggregates(roots, aggs, allStages);
    roots.forEach(r=>compute(r, allStages));
    return { roots, unallocated, stages: allStages, severeCount: countSevere(roots) };
  }

  const api = { derive, LEVELS, QTK, QT_ORDER, ROLE_ORDER, SEP, severityOf };
  if (typeof module!=='undefined' && module.exports) module.exports = api;
  else root.DERIVE = api;
})(typeof window!=='undefined' ? window : globalThis);
