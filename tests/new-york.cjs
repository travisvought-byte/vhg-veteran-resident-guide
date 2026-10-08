require('./pennsylvania.cjs');
const {setup}=require('./accessibility.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
const t=setup('','ny.html');
const counties=vm.runInContext('COUNTIES',t.ctx),data=vm.runInContext('DATA',t.ctx);
const expected='Albany,Allegany,Bronx,Broome,Cattaraugus,Cayuga,Chautauqua,Chemung,Chenango,Clinton,Columbia,Cortland,Delaware,Dutchess,Erie,Essex,Franklin,Fulton,Genesee,Greene,Hamilton,Herkimer,Jefferson,Kings,Lewis,Livingston,Madison,Monroe,Montgomery,Nassau,New York,Niagara,Oneida,Onondaga,Ontario,Orange,Orleans,Oswego,Otsego,Putnam,Queens,Rensselaer,Richmond,Rockland,Saratoga,Schenectady,Schoharie,Schuyler,Seneca,St. Lawrence,Steuben,Suffolk,Sullivan,Tioga,Tompkins,Ulster,Warren,Washington,Wayne,Westchester,Wyoming,Yates'.split(',');
assert.deepEqual(Array.from(counties,c=>c.county),expected);
assert.equal(t.nodes['edition-state'].value,'NY');
assert.equal(data.length,102);
assert.equal(new Set(data.map(x=>x.program_id)).size,data.length);
assert.deepEqual(JSON.parse(JSON.stringify(counties)),JSON.parse(fs.readFileSync(path.join(root,'data/public/new-york-county-veterans-offices.json'))));
assert.deepEqual(JSON.parse(JSON.stringify(data)),JSON.parse(fs.readFileSync(path.join(root,'data/public/new-york-resources.json'))));
for(const county of expected){
 t.nodes.county.value=county;t.nodes.county.events.change();
 const office=counties.find(c=>c.county===county),aging=data.filter(x=>x.regional_role==='aging_agency'&&x.service_area.includes(county));
 assert.equal(aging.length,1,county);
 assert(t.nodes['county-panel'].innerHTML.includes(office.phone),county+' veterans contact');
 assert(t.nodes['county-panel'].innerHTML.includes(aging[0].public_contact.phone),county+' aging contact');
 assert(t.nodes['county-panel'].innerHTML.includes('855-582-6769'));
 assert(t.nodes.results.innerHTML.includes('resource-ny-connects'));
 assert(t.nodes.results.innerHTML.includes('resource-'+aging[0].program_id));
 const senior=setup('?county='+encodeURIComponent(county)+'&view=seniors&topic=daily','ny.html');
 assert(senior.nodes['seniors-contact'].innerHTML.includes(aging[0].public_contact.phone));
 assert(!senior.nodes.results.innerHTML.includes('resource-ny-access-heroes'));
 assert(!senior.nodes.results.innerHTML.includes('resource-va-'));
 const access=setup('?county='+encodeURIComponent(county)+'&view=accessibility','ny.html');
 assert(access.nodes['access-first'].innerHTML.includes(office.phone));
 assert(access.nodes['access-first'].innerHTML.includes(aging[0].public_contact.phone));
 access.nodes['print-handoff'].onclick();assert(access.print().printed&&access.print().printMode);
 for(const r of data.filter(x=>x.regional_role&& !x.service_area.includes(county))) assert(!t.nodes.results.innerHTML.includes('resource-'+r.program_id),county+' county isolation');
}
assert.equal(counties.find(c=>c.county==='Chemung').phone,'607-737-5445');
assert.equal(counties.find(c=>c.county==='Chenango').phone,'607-337-1775');
assert.equal(counties.find(c=>c.county==='Essex').office_type,'state');
for(const county of ['Bronx','Kings','New York','Queens','Richmond']){
 const b=setup('?county='+encodeURIComponent(county),'ny.html');
 assert(b.nodes['county-panel'].innerHTML.includes('NYC citywide intake'));
 assert(b.nodes['county-panel'].innerHTML.includes('Within NYC, dial 311'));
}
for(const [alias,county] of [['Brooklyn','Kings'],['Manhattan','New York'],['Staten Island','Richmond']]){
 const a=setup('?county='+encodeURIComponent(alias),'ny.html');assert.equal(a.nodes.county.value,county);
 const url=new URL(vm.runInContext('shareURL().href',a.ctx));assert.equal(url.searchParams.get('county'),county);
 a.nodes['office-search'].value=alias;a.nodes['office-search'].events.input();assert(a.nodes['office-list'].innerHTML.includes(county+' County'));
}
const montgomery=setup('?county=Montgomery','ny.html');assert(montgomery.nodes['county-panel'].innerHTML.includes('tel:5188432300;ext=229'));
const schenectady=setup('?county=Schenectady','ny.html');assert(schenectady.nodes['county-panel'].innerHTML.includes('tel:5183828481;ext=1'));
const a=setup('?county=Chemung&view=accessibility','ny.html');
a.nodes['access-veteran'].value='yes';a.nodes['access-home'].value='new';a.nodes['access-home'].events.change();assert(a.nodes['access-first'].innerHTML.includes('VA adapted housing team'));assert(a.nodes['access-routing'].innerHTML.includes('HISA excludes new construction'));
a.nodes['access-home'].value='family';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('Temporary family home'));
a.nodes['access-veteran'].value='no';a.nodes['access-home'].value='rent';a.nodes['access-home'].events.change();assert(!a.nodes['access-routing'].innerHTML.includes('Veteran route:'));assert(!a.nodes['access-routing'].innerHTML.includes('Access to Home for Heroes'));assert(a.nodes['access-routing'].innerHTML.includes('notarized owner permission'));
a.nodes['access-home'].value='facility';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('NHTD Regional Resource Development Center'));
a.nodes['access-waiver'].value='waiver';a.nodes['access-waiver'].events.change();assert(a.nodes['access-first'].innerHTML.includes('Your service coordinator'));assert(!vm.runInContext('shareURL().href',a.ctx).includes('access-home'));
for(const [topic,id] of [['vision','ny-vision'],['hearing','ny-relay'],['costs','ny-hiicap'],['rights','ny-ombudsman'],['accessibility','ny-access-home']]){
 const s=setup('?county=Monroe&view=seniors&topic='+topic,'ny.html');assert(s.nodes.results.innerHTML.includes('resource-'+id));assert(!s.nodes.results.innerHTML.includes('resource-va-'));
}
for(const page of ['index.html','pa.html','ny.html'])for(const [state,target] of [['OH','/index.html'],['PA','/pa.html'],['NY','/ny.html']]){
 const switcher=setup('?county=Delaware&view=seniors',page);switcher.nodes['edition-state'].value=state;switcher.nodes['edition-state'].events.change();const u=new URL(switcher.navigation());assert.equal(u.pathname,target);assert.equal(u.searchParams.get('view'),'seniors');assert(!u.searchParams.has('county'));
}
for(const ids of Object.values(vm.runInContext('routes',t.ctx)))for(const id of ids)assert(data.some(r=>r.program_id===id),id);
assert(data.every(r=>['NY','shared'].includes(r.state)));
assert(!/ohio\.gov|pa\.gov|PASSPORT|OSHIIP|HOME Choice|PA Link|TechOWL|PATF|AMVETS directory/.test(fs.readFileSync(path.join(root,'ny.html'),'utf8')));
assert.equal(setup('?county=Morrow','ny.html').nodes.county.value,'');
assert.equal(setup('?view=community','ny.html').count(),3);
const share=fs.readFileSync(path.join(root,'share-ny.html'),'utf8');assert(share.includes('assets/guide-qr-ny.svg'));assert(share.includes('ny.html?view=seniors'));assert(!share.includes('pa.html?view='));
console.log('PASS: all 62 NY county veterans and aging referrals, borough aliases, corrected phones, extensions, senior and accessibility routing, printable handoffs, privacy and three-state switching.');
