// Registry-driven checks that every registered state must pass. A new state added to
// states/registry.json is covered here automatically; no test edits are needed.
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {JSDOM}=require(process.env.GUIDE_JSDOM||'jsdom');
const root=path.resolve(__dirname,'..');
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const registry=JSON.parse(read('states/registry.json'));
const statewideLabels=new Set(['statewide','national','federal']);

// 1. Registry integrity.
assert(registry.length>0&&registry[0].base,'first registry entry is the base edition');
assert.equal(new Set(registry.map(s=>s.code)).size,registry.length,'unique state codes');
for(const s of registry){
 for(const key of ['code','name','page','share_page','qr','counties','offices','resources','coverage_scope'])assert(s[key]!==undefined&&s[key]!=='',s.code+' registry field '+key);
 assert(/^[A-Z]{2}$/.test(s.code),s.code+' two-letter code');
 for(const f of [s.page,s.share_page,s.qr,s.offices,s.resources])assert(fs.existsSync(path.join(root,f)),s.code+' file exists: '+f);
 if(!s.base){
  for(const f of [s.programs,s.referrals,'states/'+s.code.toLowerCase()+'/edition.json','states/'+s.code.toLowerCase()+'/adapter.js'])assert(fs.existsSync(path.join(root,f)),s.code+' file exists: '+f);
  assert(s.share_description,s.code+' sharing description');
 }
}

// 2. Data coverage: every county resolves to a veterans, aging and ombudsman route with sources.
const otherCodes=code=>registry.filter(s=>s.code!==code).map(s=>s.code.toLowerCase());
for(const s of registry){
 const counties=JSON.parse(read(s.offices)),records=JSON.parse(read(s.resources));
 const names=new Set(counties.map(c=>c.county));
 const own=new Set([...(s.statewide_area_names||[]).map(n=>n.toLowerCase()),...statewideLabels]);
 assert.equal(counties.length,s.counties,s.code+' county count matches registry');
 assert.equal(names.size,counties.length,s.code+' county names are unique');
 const isStatewide=r=>(r.service_area||[]).some(a=>own.has(a.toLowerCase()));
 for(const c of counties){
  const veterans=c.phone||(c.representatives||[]).some(r=>r.phone);
  assert(veterans,s.code+' '+c.county+': veterans contact phone');
  assert(/^https:\/\//.test(c.source_url||c.official_url||''),s.code+' '+c.county+': veterans contact source');
  const scoped=role=>records.some(r=>r.regional_role===role&&(r.service_area||[]).includes(c.county));
  assert(scoped('aging_agency'),s.code+' '+c.county+': local aging route');
  const statewideOmbudsman=records.some(r=>/ombudsman/i.test(r.program_id+' '+r.name)&&isStatewide(r));
  assert(scoped('ombudsman')||statewideOmbudsman,s.code+' '+c.county+': ombudsman route');
 }
 for(const r of records){
  assert(/^https:\/\//.test(r.official_url||''),s.code+' '+r.program_id+': official source link');
  assert(r.verification&&r.verification.record_status&&r.verification.last_reviewed_on,s.code+' '+r.program_id+': source status and review date');
  if(r.state==='shared')continue;
  // State-scoped records must name this state's counties or a statewide label, never another state's ids.
  if(!s.base)assert(!otherCodes(s.code).some(code=>r.program_id.startsWith(code+'-')),s.code+' '+r.program_id+': record belongs to another state');
  // The base edition keeps some descriptive VA service areas; added states use county names or statewide labels only.
  if(!s.base)for(const a of r.service_area||[])assert(names.has(a)||own.has(a.toLowerCase()),s.code+' '+r.program_id+': unknown service area '+a);
 }
}
console.log('PASS: registry integrity, county counts, veterans/aging/ombudsman routes, sources and state isolation for '+registry.map(s=>s.code).join(', ')+'.');

// 3. Interface: county-limited records stay inside their counties, even when a county shares the state's name.
const dom=new JSDOM(read('index.html'),{url:'https://example.org/?view=all',runScripts:'outside-only',pretendToBeVisual:true});
dom.window.HTMLElement.prototype.scrollIntoView=function(){};dom.window.print=()=>{};
const editions=fs.existsSync(path.join(root,'assets/editions'))?fs.readdirSync(path.join(root,'assets/editions')).filter(f=>f.endsWith('.js')).sort().map(f=>read('assets/editions/'+f)).join('\n'):'';
dom.window.eval(editions+'\n'+read('assets/guide.js'));
const d=dom.window.document,change=(id,value)=>{const n=d.getElementById(id);n.value=value;n.dispatchEvent(new dom.window.Event('change'))};
for(const s of registry){
 change('edition-state',s.code);
 assert.equal(d.getElementById('edition-state').value,s.code,s.code+' selectable');
 const counties=JSON.parse(read(s.offices)).map(c=>c.county),records=JSON.parse(read(s.resources));
 const own=new Set([...(s.statewide_area_names||[]).map(n=>n.toLowerCase()),...statewideLabels]);
 const limited=records.filter(r=>r.state!=='shared'&&(r.service_area||[]).length&&!(r.service_area||[]).some(a=>own.has(a.toLowerCase())));
 d.querySelector('[data-route="all"]').click();
 for(const county of counties){
  change('county',county);
  assert(d.getElementById('county-panel').textContent.includes(county+' County'),s.code+' '+county+' county panel');
  const shown=new Set([...d.querySelectorAll('#results article[id^="resource-"]')].map(a=>a.id.slice(9)));
  for(const r of limited)if(!r.service_area.includes(county))assert(!shown.has(r.program_id),s.code+' '+county+': '+r.program_id+' is limited to '+r.service_area.slice(0,4).join(', ')+' but appears here');
 }
}
console.log('PASS: county panels and county-limited resources for every registered county.');
