// Final cross-source selection. Objective: maximise the MEAN share of each edition's *selectable
// ceiling* that the set captures - the fair test, since an edition cannot be asked for depth it
// does not have. Volumes are never summed across sources.
const D = require("./derive.js"), P = require("./streams.json"), fs = require("fs");
const pc = x => (100 * x).toFixed(1) + "%";
const EDS = ["MONBIO 4.0","MONBIO 3.0","OVAM Monitor voedselverlies 2023",
             "OVAM Monitor voedselverlies 2020","ILVO 239 tuinbouw","GeNeSys ILVO 165"];
const SHORT = {"MONBIO 4.0":"MB4","MONBIO 3.0":"MB3","OVAM Monitor voedselverlies 2023":"OV23",
  "OVAM Monitor voedselverlies 2020":"OV20","ILVO 239 tuinbouw":"ILVO","GeNeSys ILVO 165":"GNS"};
const FAM  = {"MONBIO 4.0":"MONBIO","MONBIO 3.0":"MONBIO",
  "OVAM Monitor voedselverlies 2023":"OVAM","OVAM Monitor voedselverlies 2020":"OVAM",
  "ILVO 239 tuinbouw":"ILVO","GeNeSys ILVO 165":"ILVO"};
const YR = {"MONBIO 4.0":2021,"MONBIO 3.0":2020,"OVAM Monitor voedselverlies 2023":2023,
  "OVAM Monitor voedselverlies 2020":2020,"ILVO 239 tuinbouw":2015,"GeNeSys ILVO 165":"2010-12"};
function walk(n,o){o.push(n);(n.children||[]).forEach(c=>walk(c,o));return o;}

const per = {};
EDS.forEach(ed => {
  const r = D.derive(P.claims,{editions:new Set([ed])});
  const rest = r.roots.find(x=>x.label==="Reststroom"); if(!rest) return;
  const deep = walk(rest,[]).filter(n=>(n.level==="l4"||n.level==="l5")&&(n.repTotal||0)>0)
    .filter(n=>!(n.level==="l4"&&n.children.some(c=>(c.repTotal||0)>0)));
  const byKey={};
  deep.forEach(n=>{const p=n.path.split(D.SEP); const l2=p[1], l4=p[3]||p[2], l5=p[4]||"";
    const k=l2+"|"+l4; (byKey[k]=byKey[k]||{v:0,l2,l4,fr:new Set()});
    byKey[k].v+=n.repTotal; if(l5) byKey[k].fr.add(l5);});
  per[ed]={L1:rest.repTotal||0, byKey, nItems:deep.length,
    ceil:Object.values(byKey).reduce((a,x)=>a+x.v,0)};
});

const keys={};
EDS.forEach(ed=>{const q=per[ed]; Object.entries(q.byKey).forEach(([k,o])=>{
  (keys[k]=keys[k]||{l2:o.l2,l4:o.l4,fr:new Set(),in:{}});
  o.fr.forEach(f=>keys[k].fr.add(f));
  keys[k].in[ed]={v:o.v,shareL1:o.v/q.L1,shareCeil:o.v/q.ceil};});});
Object.values(keys).forEach(o=>{o.fams=[...new Set(Object.keys(o.in).map(e=>FAM[e]))];});

const covCeil=(sel,ed)=>{const q=per[ed];let s=0;sel.forEach(k=>{if(q.byKey[k])s+=q.byKey[k].v;});return s/q.ceil;};
const covL1  =(sel,ed)=>{const q=per[ed];let s=0;sel.forEach(k=>{if(q.byKey[k])s+=q.byKey[k].v;});return s/q.L1;};

const pool=Object.keys(keys), sel=[], trace=[];
for(let i=0;i<24;i++){
  let best=null,bs=-1;
  pool.filter(k=>!sel.includes(k)).forEach(k=>{
    const t=[...sel,k];
    const sc=EDS.reduce((a,e)=>a+covCeil(t,e),0);
    if(sc>bs){bs=sc;best=k;}});
  if(!best)break;
  sel.push(best);
  const cc=EDS.map(e=>covCeil(sel,e)), cl=EDS.map(e=>covL1(sel,e));
  trace.push({n:sel.length,key:best,l4:keys[best].l4,l2:keys[best].l2,
    fams:keys[best].fams, fr:[...keys[best].fr],
    ceil:Object.fromEntries(EDS.map((e,i)=>[SHORT[e],cc[i]])),
    l1:Object.fromEntries(EDS.map((e,i)=>[SHORT[e],cl[i]])),
    meanCeil:cc.reduce((a,b)=>a+b,0)/cc.length, minCeil:Math.min(...cc),
    meanL1:cl.reduce((a,b)=>a+b,0)/cl.length});
}

console.log("n  stream                          fam  "+EDS.map(e=>SHORT[e].padStart(8)).join("")+"    mean     min");
trace.forEach(t=>{
  console.log(String(t.n).padStart(2)+"  "+(t.l4+" ["+t.l2.replace(/^(Plantaardig|Dierlijk) - /,"")+"]").slice(0,29).padEnd(30)+
    String(t.fams.length).padStart(3)+"  "+
    EDS.map(e=>pc(t.ceil[SHORT[e]]).padStart(8)).join("")+
    pc(t.meanCeil).padStart(8)+pc(t.minCeil).padStart(8));
});
console.log("\nceilings: "+EDS.map(e=>SHORT[e]+"="+pc(per[e].ceil/per[e].L1)).join("  "));

fs.writeFileSync("_sel_out.json", JSON.stringify({
  editions:EDS.map(e=>({ed:e,short:SHORT[e],fam:FAM[e],yr:YR[e],L1:per[e].L1,
     ceil:per[e].ceil, ceilPct:per[e].ceil/per[e].L1, nItems:per[e].nItems})),
  streams:Object.entries(keys).map(([k,o])=>({key:k,l2:o.l2,l4:o.l4,fr:[...o.fr],
     fams:o.fams, in:Object.fromEntries(Object.entries(o.in).map(([e,x])=>[SHORT[e],x]))})),
  trace}, null, 1));
console.log("\nwrote _sel_out.json");
