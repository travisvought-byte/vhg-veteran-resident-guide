require('./michigan.cjs');
const {setup}=require('./accessibility.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
const t=setup('','ky.html');
const counties=vm.runInContext('COUNTIES',t.ctx),data=vm.runInContext('DATA',t.ctx);
const expected='Adair,Allen,Anderson,Ballard,Barren,Bath,Bell,Boone,Bourbon,Boyd,Boyle,Bracken,Breathitt,Breckinridge,Bullitt,Butler,Caldwell,Calloway,Campbell,Carlisle,Carroll,Carter,Casey,Christian,Clark,Clay,Clinton,Crittenden,Cumberland,Daviess,Edmonson,Elliott,Estill,Fayette,Fleming,Floyd,Franklin,Fulton,Gallatin,Garrard,Grant,Graves,Grayson,Green,Greenup,Hancock,Hardin,Harlan,Harrison,Hart,Henderson,Henry,Hickman,Hopkins,Jackson,Jefferson,Jessamine,Johnson,Kenton,Knott,Knox,LaRue,Laurel,Lawrence,Lee,Leslie,Letcher,Lewis,Lincoln,Livingston,Logan,Lyon,McCracken,McCreary,McLean,Madison,Magoffin,Marion,Marshall,Martin,Mason,Meade,Menifee,Mercer,Metcalfe,Monroe,Montgomery,Morgan,Muhlenberg,Nelson,Nicholas,Ohio,Oldham,Owen,Owsley,Pendleton,Perry,Pike,Powell,Pulaski,Robertson,Rockcastle,Rowan,Russell,Scott,Shelby,Simpson,Spencer,Taylor,Todd,Trigg,Trimble,Union,Warren,Washington,Wayne,Webster,Whitley,Wolfe,Woodford'.split(',');
assert.deepEqual(Array.from(counties,c=>c.county),expected.slice().sort());
assert.equal(t.nodes['edition-state'].value,'KY');
assert.equal(data.length,81);assert.equal(new Set(data.map(x=>x.program_id)).size,81);
assert.deepEqual(JSON.parse(JSON.stringify(counties)),JSON.parse(fs.readFileSync(path.join(root,'data/public/kentucky-county-veterans-offices.json'))));
assert.deepEqual(JSON.parse(JSON.stringify(data)),JSON.parse(fs.readFileSync(path.join(root,'data/public/kentucky-resources.json'))));
assert(counties.every(c=>c.office_type==='regional'));
for(const county of expected){
 t.nodes.county.value=county;t.nodes.county.events.change();
 const office=counties.find(c=>c.county===county);
 const contacts=data.filter(x=>x.regional_role&&x.service_area.includes(county));
 for(const role of ['aging_agency','ombudsman','supported_living'])assert.equal(contacts.filter(x=>x.regional_role===role).length,1,county+' '+role);
 const senior=setup('?county='+encodeURIComponent(county)+'&view=seniors&topic=daily','ky.html');
 const access=setup('?county='+encodeURIComponent(county)+'&view=accessibility','ky.html');
 const rights=setup('?county='+encodeURIComponent(county)+'&view=seniors&topic=rights','ky.html');
 const seniorAccess=setup('?county='+encodeURIComponent(county)+'&view=seniors&topic=accessibility','ky.html');
 for(const rep of office.representatives){
  for(const h of [t.nodes['county-panel'].innerHTML,access.nodes['access-first'].innerHTML,t.nodes['office-list'].innerHTML]){assert(h.includes(rep.phone),county+' veterans contact');assert(h.includes(rep.name));if(rep.service_scope)assert(h.includes(rep.service_scope));}
 }
 for(const c of contacts){
  assert(t.nodes['county-panel'].innerHTML.includes(c.public_contact.phone),county+' local contact');
  if(c.regional_role==='aging_agency'){
   assert(t.nodes.results.innerHTML.includes('resource-'+c.program_id));
   assert(senior.nodes['seniors-contact'].innerHTML.includes(c.public_contact.phone));
   assert(access.nodes['access-first'].innerHTML.includes(c.public_contact.phone));
  }
  if(c.regional_role==='ombudsman'){
   assert(senior.nodes['seniors-contact'].innerHTML.includes(c.public_contact.phone));
   assert(rights.nodes.results.innerHTML.includes('resource-'+c.program_id));
  }
  if(c.regional_role==='supported_living'){
   assert(access.nodes['access-first'].innerHTML.includes(c.public_contact.phone));
   assert(access.nodes.results.innerHTML.includes('resource-'+c.program_id));
   assert(seniorAccess.nodes.results.innerHTML.includes('resource-'+c.program_id));
  }
 }
 for(const s of [senior,rights,seniorAccess]){assert(!s.nodes.results.innerHTML.includes('resource-va-'));assert(!s.nodes.results.innerHTML.includes('resource-ky-claims'));assert(!s.nodes.results.innerHTML.includes('resource-ky-homeless'));}
 t.nodes['print-handoff'].onclick();assert(t.print().printed&&t.print().printMode);
 access.nodes['print-handoff'].onclick();assert(access.print().printed&&access.print().printMode);
 for(const r of data.filter(x=>x.regional_role&&!x.service_area.includes(county)))assert(!t.nodes.results.innerHTML.includes('resource-'+r.program_id),county+' regional isolation');
}
// Counties with multiple KDVA representatives and differing regional boundaries.
for(const [county,n] of [['Hardin',2],['Jefferson',3],['Boyle',2],['Christian',2]])assert.equal(counties.find(c=>c.county===county).representatives.length,n);
const christian=setup('?county=Christian','ky.html');assert(christian.nodes['county-panel'].innerHTML.includes('Sherrie Sellers · KDVA region 20 · Fort Campbell'));
const carroll=setup('?county=Carroll','ky.html');assert(carroll.nodes['county-panel'].innerHTML.includes('Northern Kentucky Area Agency'));assert(carroll.nodes['county-panel'].innerHTML.includes('Kelly Warren · KDVA region 8'));
const ohio=setup('?county=Ohio','ky.html');assert(ohio.nodes.results.innerHTML.includes('resource-ky-aging-green-river'));assert(!ohio.nodes.results.innerHTML.includes('resource-ky-aging-bluegrass'));
for(const [county,ext] of [['Floyd','tel:6068862374;ext=335'],['Boyd','tel:6063291321;ext=2323'],['Jefferson','tel:5026379786;ext=280'],['Hardin','tel:5026379786;ext=213']])assert(setup('?county='+county,'ky.html').nodes['county-panel'].innerHTML.includes(ext));
const ship=setup('?county=Jefferson&view=seniors&topic=costs','ky.html');assert(ship.nodes.results.innerHTML.includes('tel:8772937447'));assert(!ship.nodes.results.innerHTML.includes('tel:8772937447;ext=2'));assert(ship.nodes.results.innerHTML.includes('menu option 2'));
const a=setup('?county=Jefferson&view=accessibility','ky.html');
a.nodes['access-veteran'].value='yes';a.nodes['access-home'].value='new';a.nodes['access-home'].events.change();assert(a.nodes['access-first'].innerHTML.includes('VA adapted housing team'));assert(a.nodes['access-routing'].innerHTML.includes('HISA excludes new construction'));
a.nodes['access-home'].value='family';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('Temporary family home'));
a.nodes['access-veteran'].value='no';a.nodes['access-home'].value='rent';a.nodes['access-home'].events.change();assert(!a.nodes['access-routing'].innerHTML.includes('Veteran route:'));assert(a.nodes['access-routing'].innerHTML.includes('notarized owner permission'));assert(a.nodes['access-first'].innerHTML.includes('Kentucky aging and disability counseling'));
assert(a.nodes['access-routing'].innerHTML.includes('up to six months'));assert(a.nodes['access-routing'].innerHTML.includes('does not build ramps'));
a.nodes['access-home'].value='facility';a.nodes['access-home'].events.change();assert(a.nodes['access-routing'].innerHTML.includes('HCB waiver intake'));
a.nodes['access-waiver'].value='waiver';a.nodes['access-waiver'].events.change();assert(a.nodes['access-first'].innerHTML.includes('Your waiver case manager'));assert(!vm.runInContext('shareURL().href',a.ctx).includes('access-home'));
for(const [topic,id] of [['vision','ky-blind'],['hearing','ky-hearing'],['costs','ky-ship'],['rights','ky-ombudsman'],['accessibility','ky-hart']])assert(setup('?county=Fayette&view=seniors&topic='+topic,'ky.html').nodes.results.innerHTML.includes('resource-'+id));
for(const page of ['index.html','pa.html','ny.html','mi.html','ky.html'])for(const [state,target] of [['OH','/index.html'],['PA','/pa.html'],['NY','/ny.html'],['MI','/mi.html'],['KY','/ky.html']]){
 const s=setup('?county=Wayne&view=seniors',page);s.nodes['edition-state'].value=state;s.nodes['edition-state'].events.change();const u=new URL(s.navigation());assert.equal(u.pathname,target);assert.equal(u.searchParams.get('view'),'seniors');assert(!u.searchParams.has('county'));
}
for(const ids of Object.values(vm.runInContext('routes',t.ctx)))for(const id of ids)assert(data.some(r=>r.program_id===id),id);
assert(data.every(r=>['KY','shared'].includes(r.state)));
assert.equal(setup('?county=Morrow','ky.html').nodes.county.value,'');assert.equal(setup('?view=community','ky.html').count(),3);
const html=fs.readFileSync(path.join(root,'ky.html'),'utf8');assert(!/ohio\.gov|pa\.gov|ny\.gov|michigan\.gov|PASSPORT|OSHIIP|HOME Choice|PA Link|TechOWL|NY Connects|NHTD|TRAID|MI Options|MI Choice|AMVETS directory|800-642-4838|866-485-9393|800-803-7174/.test(html));
for(const page of ['index.html','pa.html','ny.html','mi.html','ky.html'])assert(fs.readFileSync(path.join(root,page),'utf8').includes('<option value="KY">Kentucky</option>'));
const share=fs.readFileSync(path.join(root,'share-ky.html'),'utf8');assert(share.includes('assets/guide-qr-ky.svg'));assert(share.includes('ky.html?view=seniors'));assert(share.includes('all 120 Kentucky counties'));assert(!share.includes('mi.html?view='));assert(!share.includes('county veterans offices'));
for(const page of ['share.html','share-pa.html','share-ny.html','share-mi.html','share-ky.html'])for(const file of ['share.html','share-pa.html','share-ny.html','share-mi.html','share-ky.html'])assert(fs.readFileSync(path.join(root,page),'utf8').includes('href="'+file+'"'));
console.log('PASS: all 120 Kentucky county routes, 15 aging regions, 15 district ombudsmen, six supported-living regions, multiple KDVA contacts, Fort Campbell scope, menu and extension handling, print actions and five-state switching.');
