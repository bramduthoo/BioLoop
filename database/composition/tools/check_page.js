// Render-check a generated page without a browser.
//
//   node tools/check_page.js ../build/analysis.js      (the extracted <script>)
//
// A minimal DOM stub, enough to answer the only question that matters before
// publishing: does every section actually BUILD, and does it produce nodes?
//
// This exists because the analysis page shipped once with a table head assembled
// wrongly. The throw took every section after it down, so the page arrived EMPTY
// rather than partly wrong - and an empty page looks like a data problem when it is
// a one-line code problem. `node --check` passes on that file: it is valid syntax.
// A syntax check is not a render check.
function mk(tag){
  const n = { tagName: tag, className:'', textContent:'', innerHTML:'', children:[],
    style:{}, dataset:{}, title:'', colSpan:1, id:'',
    append(...xs){ xs.forEach(x=>this.children.push(x)); },
    appendChild(x){ this.children.push(x); return x; },
    querySelector(){ return null; }, querySelectorAll(){ return []; },
    addEventListener(){}, setAttribute(){}, getAttribute(){ return null; } };
  return n;
}
const byId = {};
global.document = {
  createElement: mk,
  createTextNode: t => ({ nodeValue:t, textContent:String(t) }),
  querySelector(sel){
    if (sel.startsWith('#')) { const k = sel.slice(1); return byId[k] || (byId[k]=mk('div')); }
    if (sel === '.wrap') return byId.__wrap || (byId.__wrap = mk('div'));
    return mk('div');
  },
  querySelectorAll(){ return []; }, body: mk('body'),
};
const fs = require('fs');
try { eval(fs.readFileSync(process.argv[2],'utf8')); } catch(e){ console.log('THREW:', e.message); }
function deep(n){ return !n ? 0 : 1 + (n.children||[]).reduce((a,c)=>a+deep(c),0); }
for (const k of ['tiles','srctab','matrix','parbars','stbars','qcbox','work','mxlegend','foot']) {
  const n = byId[k];
  console.log(`  ${k.padEnd(10)} ${n ? String((n.children||[]).length).padStart(4) : '   -'} direct, ${n?deep(n):0} nodes`);
}
const errs = (byId.__wrap && byId.__wrap.children || []).filter(c=>c.className==='note');
console.log(errs.length ? `  !! ${errs.length} section(s) reported a build error` : '  no section errors');
