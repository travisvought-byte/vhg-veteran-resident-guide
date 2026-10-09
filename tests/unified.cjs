const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {JSDOM}=require(process.env.GUIDE_JSDOM||'jsdom');
const root=path.resolve(__dirname,'..');
function setup(query=''){const dom=new JSDOM(fs.readFileSync(root+'/index.html','utf8'),{url:'https://example.org/'+query,runScripts:'outside-only',pretendToBeVisual:true});dom.window.HTMLElement.prototype.scrollIntoView=function(){};let prints=0;dom.window.print=()=>prints++;dom.window.eval(fs.readFileSync(root+'/assets/guide.js','utf8'));const d=dom.window.document;return {dom,d,prints:()=>prints,change(id,value){const n=d.getElementById(id);n.value=value;n.dispatchEvent(new dom.window.Event('change'))},click:id=>d.getElementById(id).click()}}
const t=setup();const expected={OH:88,PA:67,NY:62,MI:83,KY:120};
for(const [state,n] of Object.entries(expected)){
 t.change('edition-state',state);assert.equal(t.d.querySelectorAll('#county option').length,n+1);assert.equal(new URL(t.dom.window.location.href).searchParams.get('state'),state);assert.equal(t.dom.window.location.pathname,'/');assert(!t.d.querySelector('header h1').textContent.includes('Ohio'));assert(t.d.querySelector('.office-directory summary').textContent.includes({OH:'Ohio',PA:'Pennsylvania',NY:'New York',MI:'Michigan',KY:'Kentucky'}[state]));
 const counties=Array.from(t.d.querySelectorAll('#county option')).slice(1).map(x=>x.value);
 for(const c of counties){t.change('county',c);assert(t.d.getElementById('county-panel').textContent.includes(c+' County'));assert(t.d.querySelectorAll('#results article').length>0)}
 t.click('helper-open');assert(!t.d.getElementById('helper-guide').hidden);
 for(const person of ['veteran','survivor','unknown','other']){
  t.change('helper-person',person);
  for(const need of ['benefits','daily','housing','accessibility','rights','crisis']){t.change('helper-need',need);assert(t.d.querySelectorAll('#helper-next article').length>0,state+' '+person+' '+need)}
 }
 t.change('helper-person','survivor');t.change('helper-need','accessibility');t.click('helper-resources');assert.equal(t.d.getElementById('access-veteran').value,'no');assert.equal(t.d.getElementById('access-home').value,'facility');
 t.change('helper-person','other');t.change('helper-need','benefits');t.click('helper-resources');assert(!t.d.getElementById('seniors-guide').hidden);assert.equal(t.d.getElementById('senior-topic').value,'costs');
 t.change('helper-need','daily');t.click('helper-print');assert(t.d.body.classList.contains('print-helper'));t.dom.window.dispatchEvent(new t.dom.window.Event('afterprint'));assert(!t.d.body.classList.contains('print-helper'));
 t.change('county','');t.click('helper-print');assert(t.d.getElementById('helper-status').textContent.includes('Choose'));
 t.d.querySelector('[data-route="all"]').click();assert(t.d.getElementById('helper-guide').hidden);assert.equal(t.d.querySelectorAll('#results article').length,{OH:132,PA:108,NY:107,MI:63,KY:86}[state]);
}
t.change('edition-state','OH');t.change('county','Morrow');t.d.getElementById('search').value='Medicaid';t.change('edition-state','PA');assert.equal(t.d.getElementById('county').value,'');assert.equal(t.d.getElementById('search').value,'');
const ny=setup('?state=NY&county=Manhattan&view=rights');assert.equal(ny.d.getElementById('edition-state').value,'NY');assert.equal(ny.d.getElementById('county').value,'New York');assert(ny.d.getElementById('count').textContent.includes('Care concerns'));
const invalid=setup('?state=INVALID&county=INVALID');assert.equal(invalid.d.getElementById('edition-state').value,'OH');assert.equal(invalid.d.getElementById('county').value,'');
const ky=setup('?state=KY&county=Christian');assert(ky.d.getElementById('county-panel').textContent.includes('Fort Campbell'));
const mi=setup('?state=MI&county=Wayne');assert(mi.d.getElementById('county-panel').textContent.includes('Detroit'));
console.log('PASS: unified DOM, all 420 county panels, every caregiver identity/need combination in five states, state isolation, surviving-spouse access routing, printing, canonical links and NYC aliases.');

const ohioData=JSON.parse(fs.readFileSync(root+'/prototype-data.json','utf8'));
for(const r of ohioData.filter(x=>['caregiver_support','independent_living'].includes(x.resource_role))){
 for(const county of ['Morrow','Franklin','Summit','Cuyahoga','Washington','Adams']){
  const v=setup('?state=OH&county='+county+'&view=local');assert.equal(!!v.d.getElementById('resource-'+r.program_id),(r.service_area.includes(county)||r.service_area.includes('statewide')),r.program_id+' '+county);v.dom.window.close();
 }
}
const daily=setup('?state=OH&county=Morrow&view=seniors&topic=daily');assert(daily.d.getElementById('resource-ohio-district5-caregiver-respite'));
const discharge=setup('?state=OH&county=Franklin&view=accessibility');assert(discharge.d.getElementById('resource-ohio-cil-cde'));
console.log('PASS: Ohio caregiver and disability county boundaries, daily support and discharge accessibility routes.');

const centers=ohioData.filter(x=>x.resource_role==='independent_living');assert.equal(centers.length,12);assert.equal(new Set(centers.map(x=>x.program_id)).size,12);
assert(centers.find(x=>x.program_id==='ohio-cil-ability').service_area.includes('Paulding'));
assert(centers.find(x=>x.program_id==='ohio-cil-acil').constraints.join(' ').includes('limited services'));
assert(centers.find(x=>x.program_id==='ohio-cil-north-central').service_area.includes('Marion'));
assert.equal(centers.find(x=>x.program_id==='ohio-cil-mobile').public_contact.phone,'614-443-5936');
const respite=ohioData.find(x=>x.program_id==='ohio-adult-day-directory');assert(respite.constraints.join(' ').includes('not statewide service availability'));
console.log('PASS: all 12 Ohio independent-living centers, expanded counties, limited-service notices and adult-day directory boundaries.');
