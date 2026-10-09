require('./legacy-fixtures.cjs');
const {setup}=require('./accessibility.cjs');
const assert=require('assert'),fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'prototype-data.json')));
const providers=data.filter(x=>x.resource_role==='housing_provider');
assert.equal(providers.length,16);
const mapped=new Set(providers.flatMap(x=>x.service_area));assert.equal(mapped.size,86);
const counties=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-county-veterans-offices.json')));
assert.equal(counties.filter(c=>!mapped.has(c.county)).length,2);
for(const c of counties){
 const t=setup('?view=housing&county='+encodeURIComponent(c.county));
 for(const p of providers)assert.equal(t.nodes.results.innerHTML.includes('resource-'+p.program_id),p.service_area.includes(c.county),p.program_id+' '+c.county);
 assert(t.nodes.results.innerHTML.includes('resource-va-housing-help'),c.county+' retains national referral');
}
for(const county of ['Morrow','Marion','Delaware','Knox'])assert(mapped.has(county));
const sa=providers.find(x=>x.program_id==='ohio-salvation-army-ssvf');assert.equal(sa.service_area.length,11);assert(sa.service_area.includes('Richland'));assert.equal(sa.public_contact.phone,'614-437-2130');
const lss=providers.find(x=>x.program_id==='ohio-lss-ssvf');assert(!lss.service_area.includes('Franklin'));assert.equal(lss.public_contact.phone,'740-277-2334');
const dayton=providers.find(x=>x.program_id==='ohio-st-vincent-ssvf');assert.equal(dayton.public_contact.phone,'888-751-1238');assert(!dayton.service_area.includes('Wayne'));
const knox=setup('?view=housing&county=Knox');assert(knox.nodes.results.innerHTML.includes('VA Knox County homeless resources'));assert(knox.nodes.results.innerHTML.includes('lcchousing.org/need-help'));
const mr=setup('?view=housing&county=Morrow');assert(mr.nodes.results.innerHTML.includes('tel:6144372130'));
for(const page of ['pa.html','ny.html','mi.html','ky.html']){const t=setup('?view=housing',page),rs=vm.runInContext('DATA',t.ctx);assert(!rs.some(x=>x.resource_role==='housing_provider'));for(const p of providers)assert(!t.nodes.results.innerHTML.includes(p.program_id));}
console.log('PASS: all 88 Ohio county housing views, 86 mapped counties, 2 honest coverage gaps, primary evidence links, intake limits and state isolation.');

const axess=providers.find(x=>x.program_id==='ohio-axess-ssvf');assert.equal(axess.public_contact.phone,'855-234-7310');assert.equal(axess.service_area.length,9);assert(axess.service_area.includes('Ashtabula'));assert(!axess.service_area.includes('Cuyahoga'));

const glcap=providers.find(x=>x.program_id==='ohio-glcap-ssvf');assert.equal(glcap.service_area.length,10);assert.equal(glcap.public_contact.phone,'800-775-9767');assert(glcap.service_area.includes('Wyandot'));assert(!glcap.service_area.includes('Williams'));
const talbert=providers.find(x=>x.program_id==='ohio-talbert-ssvf');assert.deepEqual(talbert.service_area,['Butler','Clermont','Hamilton','Warren']);assert.equal(talbert.public_contact.phone,'513-993-7230');

assert.deepEqual(counties.filter(c=>!mapped.has(c.county)).map(c=>c.county),['Putnam','Van Wert']);
const source=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-ssvf-intake-evidence.json')));assert.equal(source.records.length,13);assert.equal(source.source_sha256.length,64);
const wm=providers.find(x=>x.program_id==='ohio-wmcap-ssvf');assert.equal(wm.service_area.length,15);assert(wm.service_area.includes('Pike'));
assert(providers.find(x=>x.program_id==='ohio-lcch-ssvf').service_area.includes('Holmes'));
for(const p of providers)for(const e of p.source_evidence||[])if(e.row){const r=source.records.find(x=>x.row===e.row);assert(r,p.program_id);assert.equal(e.source_sha256,source.source_sha256);}
for(const [id,county,phone] of [['ohio-voa-cleveland-ssvf','Cuyahoga','216-541-9000 ext. 1305'],['ohio-voa-columbus-ssvf','Franklin','614-546-8119'],['ohio-voa-dayton-ssvf','Montgomery','937-253-7042 ext. 1468']]){const p=providers.find(x=>x.program_id===id);assert.deepEqual(p.service_area,[county]);assert.equal(p.public_contact.phone,phone);}
console.log('PASS: VA workbook row evidence, grant-specific intake routes, 86 mapped counties and two remaining provider gaps.');
