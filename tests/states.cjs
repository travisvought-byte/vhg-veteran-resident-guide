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
 const countyRows=JSON.parse(read(s.offices)),counties=countyRows.map(c=>c.county),records=JSON.parse(read(s.resources));
 const own=new Set([...(s.statewide_area_names||[]).map(n=>n.toLowerCase()),...statewideLabels]);
 const limited=records.filter(r=>r.state!=='shared'&&(r.service_area||[]).length&&!(r.service_area||[]).some(a=>own.has(a.toLowerCase())));
 d.querySelector('[data-route="all"]').click();
 for(const county of counties){
  change('county',county);
  const row=countyRows.find(c=>c.county===county);
  assert(d.getElementById('county-panel').textContent.includes(['independent_city','statewide','borough','census_area','city_and_county'].includes(row.county_type)?county:county+(row.county_type==='parish'?' Parish':' County')),s.code+' '+county+' county panel');
  const shown=new Set([...d.querySelectorAll('#results article[id^="resource-"]')].map(a=>a.id.slice(9)));
  for(const r of limited)if(!r.service_area.includes(county))assert(!shown.has(r.program_id),s.code+' '+county+': '+r.program_id+' is limited to '+r.service_area.slice(0,4).join(', ')+' but appears here');
 }
}
console.log('PASS: county panels and county-limited resources for every registered county.');

// 4. A state with one statewide entry shows its contacts as soon as the state is chosen; every other state waits for a county.
const digits=v=>String(v||'').replace(/\D/g,'');
for(const s of registry){
 change('edition-state',s.code);
 const rows=JSON.parse(read(s.offices)),single=rows.length===1,picker=d.getElementById('county');
 assert.equal(picker.value,single?rows[0].county:'',s.code+' county starts '+(single?'on its one statewide entry':'unchosen'));
 assert.equal(picker.parentElement.hidden,single,s.code+' county picker is '+(single?'put away':'shown'));
 assert.equal(d.querySelector('.office-directory').hidden,single,s.code+' county directory');
 const coverage=d.getElementById('coverage-detail').textContent;
 assert(!/\b1 counties\b/.test(coverage),s.code+' coverage sentence');
 if(single){
  assert(digits(d.getElementById('county-panel').textContent).includes(digits(rows[0].phone)),s.code+' statewide veterans phone shows without choosing a county');
  // A starter edition says its local offices are not listed yet; a full edition with one locality (D.C.) names it instead.
  if(s.starter)assert(coverage.includes('statewide referral routes'),s.code+' starter coverage sentence');
  else assert(coverage.includes('referral routes for '+rows[0].county)&&!coverage.includes('not listed yet'),s.code+' single-locality coverage sentence');
 }
 // The footer date is the newest review of this state's own veterans office contacts.
 const dates=rows.map(c=>c.reviewed_on).filter(v=>/^\d{4}-\d{2}-\d{2}$/.test(v||'')).sort();
 assert(dates.length,s.code+' office contacts carry review dates');
 const newest=new Date(dates.at(-1)+'T12:00:00').toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'});
 assert.equal(d.getElementById('edition-updated').textContent,'Most recent review of '+s.name+' veterans office contacts: '+newest+'.',s.code+' footer review date');
}
assert(registry.filter(s=>s.starter).every(s=>s.counties===1),'any starter edition has one statewide entry');
console.log('PASS: single-entry states show their statewide contacts at once, county states wait for a county, and every footer date comes from the records.');

// 5. Phone header: the first four links stay in view and the rest open from one real button.
const toggle=d.getElementById('jump-toggle'),more=d.getElementById('jump-more');
assert(/<button type="button" class="jump jump-toggle" id="jump-toggle" aria-expanded="false" aria-controls="jump-more" hidden>/.test(read('index.html')),'the button stays hidden until the page script runs');
assert.equal(toggle.hidden,false,'the page script shows the button');
assert.equal(toggle.nextElementSibling,more,'the folded links follow their button');
assert.deepEqual([...d.querySelectorAll('header .brand-copy > a.jump')].map(a=>a.textContent),['Find a county veterans office','Find resources','Bingo & Senior Centers','I’m helping someone'],'links that stay in view');
assert.equal(more.querySelectorAll('a.jump').length,9,'folded links');
toggle.click();assert.equal(toggle.getAttribute('aria-expanded'),'true');assert.equal(toggle.textContent,'Fewer guides');
toggle.click();assert.equal(toggle.getAttribute('aria-expanded'),'false');assert.equal(toggle.textContent,'More guides');
const css=read('assets/unified.css');
assert(css.includes('header .jump-toggle:not([hidden])[aria-expanded=false]+.jump-more{display:none}'),'links fold only when the button is available');
assert(css.includes('.jump-more{display:contents}.jump-toggle{display:none}'),'wider screens show every link and no button');
// Visual pass (November 20, 2026): an icon beside every need button's words, phone icons, and dark mode.
{
  const page=read('index.html');
  const routes=[...page.matchAll(/<button data-route="([a-z]+)"[^>]*><strong>/g)].map(m=>m[1]);
  assert(routes.length>=15,'need buttons found');
  for(const route of routes)
    assert(css.includes(`.quick-links [data-route=${route}] strong::before{--icon:url("data:image/svg+xml,`),'need icon for '+route);
  assert(css.includes('.quick-links #helper-open strong::before{--icon:')&&css.includes('a.phone::before{--icon:'),'helper and phone icons');
  assert(/content:"";display:inline-block;[^}]*background:currentColor;-webkit-mask:var\(--icon\)/.test(css),'icons are empty decoration in the text color');
  const dark=css.match(/@media screen and \(prefers-color-scheme:dark\)\{([\s\S]*)\}\s*$/);
  assert(dark,'dark mode follows the device setting, on screen only');
  const lum=h=>{const n=h.slice(1);const [r,g,b]=[0,2,4].map(i=>parseInt(n.slice(i,i+2),16)/255).map(c=>c<=0.03928?c/12.92:((c+0.055)/1.055)**2.4);return 0.2126*r+0.7152*g+0.0722*b};
  const ratio=(a,b)=>{const [x,y]=[lum(a),lum(b)].sort((m,n)=>n-m);return (x+0.05)/(y+0.05)};
  // Text and link colors in dark mode on each dark surface: WCAG AA.
  for(const fg of ['#e4ecef','#dce9f2','#9fd0ef','#b6c4ca'])for(const bg of ['#10181d','#1a242b','#1d2e27','#2c2614','#0f171c'])
    assert(ratio(fg,bg)>=4.5,`${fg} on ${bg}`);
  for(const [fg,bg] of [['#d7eee1','#25372e'],['#f2dfb2','#382d17'],['#ecd28c','#1a242b'],['#ffffff','#2a4a63'],['#ffffff','#0d2333']])assert(ratio(fg,bg)>=4.5,`${fg} on ${bg}`);
  for(const hex of dark[1].match(/#[0-9a-f]{6}/gi))assert(['#10181d','#0d2333','#dce9f2','#e4ecef','#9fd0ef','#0f171c','#83988f','#1a242b','#b6c4ca','#1d2e27','#93d6b1','#25372e','#d7eee1','#382d17','#f2dfb2','#ecd28c','#2c2614','#2a4a63','#3d4d55'].includes(hex.toLowerCase()),'dark color '+hex+' is one of the checked set');
}
console.log('PASS: phone header keeps four links in view and opens the rest from one button.');
