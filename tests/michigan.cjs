require('./legacy-fixtures.cjs');
require('./new-york.cjs');
const {setup}=require('./accessibility.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
const t=setup('','mi.html');
const counties=vm.runInContext('COUNTIES',t.ctx),data=vm.runInContext('DATA',t.ctx);
const expected='Alcona,Alger,Allegan,Alpena,Antrim,Arenac,Baraga,Barry,Bay,Benzie,Berrien,Branch,Calhoun,Cass,Charlevoix,Cheboygan,Chippewa,Clare,Clinton,Crawford,Delta,Dickinson,Eaton,Emmet,Genesee,Gladwin,Gogebic,Grand Traverse,Gratiot,Hillsdale,Houghton,Huron,Ingham,Ionia,Iosco,Iron,Isabella,Jackson,Kalamazoo,Kalkaska,Kent,Keweenaw,Lake,Lapeer,Leelanau,Lenawee,Livingston,Luce,Mackinac,Macomb,Manistee,Marquette,Mason,Mecosta,Menominee,Midland,Missaukee,Monroe,Montcalm,Montmorency,Muskegon,Newaygo,Oakland,Oceana,Ogemaw,Ontonagon,Osceola,Oscoda,Otsego,Ottawa,Presque Isle,Roscommon,Saginaw,Sanilac,Schoolcraft,Shiawassee,St. Clair,St. Joseph,Tuscola,Van Buren,Washtenaw,Wayne,Wexford'.split(',');
assert.deepEqual(Array.from(counties,c=>c.county),expected);
assert.equal(t.nodes['edition-state'].value,'MI');
assert.equal(data.length,63);
assert.equal(new Set(data.map(x=>x.program_id)).size,63);
assert.deepEqual(JSON.parse(JSON.stringify(counties)),JSON.parse(fs.readFileSync(path.join(root,'data/public/michigan-county-veterans-offices.json'))));
assert.deepEqual(JSON.parse(JSON.stringify(data)),JSON.parse(fs.readFileSync(path.join(root,'data/public/michigan-resources.json'))));
assert.equal(counties.filter(c=>c.office_type==='state').length,1);
for(const county of expected){
 t.nodes.county.value=county;t.nodes.county.events.change();
 const office=counties.find(c=>c.county===county),agencies=data.filter(x=>x.regional_role==='aging_agency'&&x.service_area.includes(county));
 assert.equal(agencies.length,county==='Wayne'?2:1,county+' coverage');
 assert(t.nodes['county-panel'].innerHTML.includes(office.phone),county+' veterans referral');
 assert(t.nodes['county-panel'].innerHTML.includes('866-485-9393'));
 assert(t.nodes.results.innerHTML.includes('resource-mi-options'));
 const senior=setup('?county='+encodeURIComponent(county)+'&view=seniors&topic=daily','mi.html');
 const access=setup('?county='+encodeURIComponent(county)+'&view=accessibility','mi.html');
 assert(access.nodes['access-first'].innerHTML.includes(office.phone));
 for(const agency of agencies){
  assert(t.nodes['county-panel'].innerHTML.includes(agency.public_contact.phone));
  assert(t.nodes.results.innerHTML.includes('resource-'+agency.program_id));
  assert(senior.nodes['seniors-contact'].innerHTML.includes(agency.public_contact.phone));
  assert(access.nodes['access-first'].innerHTML.includes(agency.public_contact.phone));
  if(agency.service_scope)for(const text of [t.nodes['county-panel'].innerHTML,senior.nodes['seniors-contact'].innerHTML,access.nodes['access-first'].innerHTML])assert(text.includes(agency.service_scope));
 }
 assert(!senior.nodes.results.innerHTML.includes('resource-va-'));
 assert(!senior.nodes.results.innerHTML.includes('resource-mi-emergency'));
 access.nodes['print-handoff'].onclick();assert(access.print().printed&&access.print().printMode);
 for(const r of data.filter(x=>x.regional_role&&!x.service_area.includes(county)))assert(!t.nodes.results.innerHTML.includes('resource-'+r.program_id),county+' isolation');
}
const ionia=setup('?county=Ionia','mi.html');assert(ionia.nodes['county-panel'].innerHTML.includes('MVAA statewide referral'));assert(ionia.nodes['county-panel'].innerHTML.includes('not a direct county office number'));
const berrien=setup('?county=Berrien','mi.html');assert(berrien.nodes['county-panel'].innerHTML.includes('tel:2699837111;ext=8224'));
const missaukee=setup('?county=Missaukee','mi.html');assert(missaukee.nodes['county-panel'].innerHTML.includes('tel:2318394200;ext=507'));
assert.equal(counties.find(c=>c.county==='Clinton').phone,'517-887-4390');
assert.equal(counties.find(c=>c.county==='Jackson').phone,'517-788-4425');
assert.equal(counties.find(c=>c.county==='Saginaw').phone,'517-898-7902');
const leelanau=setup('?county=Leelanau','mi.html');assert(leelanau.nodes['county-panel'].innerHTML.includes('Grand Traverse County Veterans Affairs'));assert(leelanau.nodes['county-panel'].innerHTML.includes('current arrangement'));
const a=setup('?county=Wayne&view=accessibility','mi.html');
a.nodes['access-veteran'].value='yes';a.nodes['access-home'].value='new';a.nodes['access-home'].events.change();assert(a.nodes['access-first'].innerHTML.includes('VA adapted housing team'));assert(a.nodes['access-routing'].innerHTML.includes('HISA excludes new construction'));
a.nodes['access-home'].value='family';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('Temporary family home'));
a.nodes['access-veteran'].value='no';a.nodes['access-home'].value='rent';a.nodes['access-home'].events.change();assert(!a.nodes['access-routing'].innerHTML.includes('Veteran route:'));assert(!a.nodes['access-routing'].innerHTML.includes('Michigan veteran emergency support'));assert(a.nodes['access-routing'].innerHTML.includes('notarized owner permission'));assert(a.nodes['access-first'].innerHTML.includes('MI Options'));
a.nodes['access-home'].value='facility';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('MI Choice waiver agency'));
a.nodes['access-waiver'].value='waiver';a.nodes['access-waiver'].events.change();assert(a.nodes['access-first'].innerHTML.includes('Your supports coordinator'));assert(!vm.runInContext('shareURL().href',a.ctx).includes('access-home'));
for(const [topic,id] of [['vision','mi-blind'],['hearing','mi-relay'],['costs','mi-ship'],['rights','mi-ombudsman'],['accessibility','mi-choice']]){
 const s=setup('?county=Monroe&view=seniors&topic='+topic,'mi.html');assert(s.nodes.results.innerHTML.includes('resource-'+id));assert(!s.nodes.results.innerHTML.includes('resource-va-'));assert(!s.nodes.results.innerHTML.includes('resource-mi-emergency'));
}
for(const page of ['index.html','pa.html','ny.html','mi.html'])for(const [state,target] of [['OH','/index.html'],['PA','/pa.html'],['NY','/ny.html'],['MI','/mi.html']]){
 const s=setup('?county=Wayne&view=seniors',page);s.nodes['edition-state'].value=state;s.nodes['edition-state'].events.change();const u=new URL(s.navigation());assert.equal(u.pathname,target);assert.equal(u.searchParams.get('view'),'seniors');assert(!u.searchParams.has('county'));
}
for(const ids of Object.values(vm.runInContext('routes',t.ctx)))for(const id of ids)assert(data.some(r=>r.program_id===id),id);
assert(data.every(r=>['MI','shared'].includes(r.state)));
assert.equal(setup('?county=Morrow','mi.html').nodes.county.value,'');
assert.equal(setup('?view=community','mi.html').count(),3);
const html=fs.readFileSync(path.join(root,'mi.html'),'utf8');assert(!/ohio\.gov|pa\.gov|ny\.gov|PASSPORT|OSHIIP|HOME Choice|PA Link|TechOWL|NY Connects|NHTD|TRAID|AMVETS directory/.test(html));
for(const page of ['index.html','pa.html','ny.html','mi.html']){
 const h=fs.readFileSync(path.join(root,page),'utf8');for(const [state,label] of [['OH','Ohio'],['PA','Pennsylvania'],['NY','New York'],['MI','Michigan']])assert(h.includes('<option value="'+state+'">'+label+'</option>'));
}
const share=fs.readFileSync(path.join(root,'share-mi.html'),'utf8');assert(share.includes('assets/guide-qr-mi.svg'));assert(share.includes('mi.html?view=seniors'));assert(!share.includes('ny.html?view='));
for(const page of ['share.html','share-pa.html','share-ny.html','share-mi.html']){
 const h=fs.readFileSync(path.join(root,page),'utf8');for(const file of ['share.html','share-pa.html','share-ny.html','share-mi.html'])assert(h.includes('href="'+file+'"'));
}
console.log('PASS: all 83 Michigan county routes, 16 aging agencies, Wayne city boundaries, labeled Ionia fallback, extensions, senior and accessibility routes, print actions, source isolation and four-state switching.');
