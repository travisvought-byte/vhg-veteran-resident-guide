const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
const html=fs.readFileSync('family-guide.html','utf8'),script=fs.readFileSync('assets/family-guide.js','utf8');
function load(q=''){
 const dom=new JSDOM(html,{url:'https://example.org/family-guide.html'+q,runScripts:'outside-only'});
 const w=dom.window;w.print=()=>{};w.eval(script);const d=w.document,$=id=>d.getElementById(id);
 const set=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new w.Event('change'));};
 return {w,d,$,set};
}

const data=JSON.parse(load('?state=US').$('family-data').textContent);
assert(data.resources.every(r=>r.scope!=='OH'));
const start=load('?state=US');assert.equal(start.$('state').value,'US');assert(start.$('anchors').hidden);
for(const state of Object.keys(data.states).filter(s=>s!=='OH')){
 const {$,d}=load('?state='+state);
 assert.equal($('state').value,state);
 assert(!$('anchors').hidden);
 assert($('anchors-title').textContent.includes(data.states[state]));
 assert(!$('r-cdc-find-ei').hidden);
 assert(!d.querySelector('[data-scope="OH"]'));
 assert(!/undefined|NaN/.test($('result-status').textContent));
}
assert(load('?state=NY&lang=es').d.querySelector('h1').textContent.includes('familias'));
const vm=require('node:vm'),routing=fs.readFileSync('assets/family-routing.js','utf8');
for(const query of ['', '?state=OH&county=Knox&stage=school&lang=es','?state=NY','?state=US']){
 let destination=null;
 vm.runInNewContext(routing,{URLSearchParams,location:{search:query,hash:'#military',replace:u=>destination=u}});
 if(!query||query.includes('state=OH'))assert.equal(destination,'https://www.ohiomom.org/family-guide.html'+query+'#military');
 else assert.equal(destination,null);
}
console.log('PASS 50 other jurisdictions, national entry, Ohio redirect and preserved query/hash');
