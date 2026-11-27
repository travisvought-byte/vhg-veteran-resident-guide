// The county and category picker on the veteran programs pages (assets/opportunities.js, scripts/build_opportunities.py).
const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
const script=fs.readFileSync('assets/opportunities.js','utf8');
function load(page,q=''){
 const dom=new JSDOM(fs.readFileSync(page,'utf8'),{url:'https://example.org/'+page+q,runScripts:'outside-only'});
 const w=dom.window;w.eval(script);const d=w.document,$=id=>d.getElementById(id);
 const set=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new w.Event('change'));};
 const ids=tier=>[...$('tier-'+tier).querySelectorAll('[data-opp]:not([hidden])')].map(a=>a.id);
 return {w,d,$,set,ids};
}
const oh='opportunities/oh/index.html';
// No county: the form shows, statewide comes first, the county tiers stay hidden, every program is listed.
let p=load(oh);
const total=p.d.querySelectorAll('[data-opp]').length;
assert(!p.$('opp-filter').hidden);
assert(p.$('tier-yours').hidden&&p.$('tier-nearby').hidden);
assert(!p.$('tier-state').hidden&&!p.$('tier-local').hidden);
assert.match(p.$('opp-status').textContent,new RegExp('Showing '+total+' programs'));
// Delaware County: the programs that name it first, then the rest of central Ohio, then statewide.
p=load(oh,'?county=delaware');
assert.equal(p.$('opp-county').value,'delaware');
assert(!p.$('tier-yours').hidden);
assert(p.ids('yours').includes('delaware-county-veteran-transportation'));
assert(p.ids('yours').every(id=>p.$(id).dataset.counties.includes('|delaware|')));
assert(p.ids('nearby').includes('central-ohio-stand-down'));
assert(!p.ids('nearby').some(id=>p.$(id).dataset.counties.includes('|delaware|')));
const order=[...p.d.querySelectorAll('[data-tier]')].map(s=>s.id);
assert(order.indexOf('tier-yours')<order.indexOf('tier-nearby')&&order.indexOf('tier-nearby')<order.indexOf('tier-state'));
assert.equal(p.$('tier-local-h').textContent,'Elsewhere in Ohio');
assert.equal(p.d.querySelectorAll('[data-opp]').length,total);
// Cuyahoga: the Golden Age Games held in Cleveland count as local.
p=load(oh,'?county=cuyahoga');
assert(p.ids('yours').includes('va-golden-age-games-2027'));
// A region with only region-wide programs: Lucas gets Northwest Ohio's Honor Flight as nearby.
p=load(oh,'?county=lucas');
assert(p.ids('nearby').includes('flag-city-honor-flight'));
assert.match(p.$('opp-status').textContent,/None name Lucas County yet/);
// A kind of help hides the rest, and empty tiers and groups disappear; choosing All brings everything back.
p=load(oh);p.set('opp-cat','education');
const shown=[...p.d.querySelectorAll('[data-opp]:not([hidden])')];
assert(shown.length>0&&shown.every(a=>a.dataset.cat==='education'));
for(const s of p.d.querySelectorAll('[data-tier]'))assert.equal(s.hidden,!s.querySelector('[data-opp]:not([hidden])'));
assert.match(p.w.location.search,/cat=education/);
p.set('opp-cat','');assert.equal(p.d.querySelectorAll('[data-opp]:not([hidden])').length,total);
// Changing county puts the last county's programs back.
p=load(oh,'?county=delaware');p.set('opp-county','hamilton');
assert(!p.ids('yours').includes('delaware-county-veteran-transportation'));
assert(p.ids('yours').includes('heroes-on-the-water-southwest-ohio'));
p.set('opp-county','');assert(p.$('tier-yours').hidden);
// Pennsylvania has no county picker; the nationwide page has categories only. Nothing prints undefined.
for(const page of ['opportunities/pa/index.html','opportunities/mi/index.html','opportunities/us/index.html']){
 p=load(page,'?cat=housing');assert(!p.$('opp-county'));assert.equal(p.$('opp-cat').value,'housing');
 assert(!/undefined|NaN|null/.test(p.$('opp-status').textContent));
}
console.log('opportunities picker: ok');
