require('./legacy-fixtures.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'facilities.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-facilities.json'),'utf8'));
const source=JSON.parse(fs.readFileSync(path.join(root,'data/source/ohio-facilities-source.json'),'utf8'));
const counties=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-county-veterans-offices.json'),'utf8'));
const mk=()=>({value:'',innerHTML:'',textContent:'',options:[],addEventListener(){}});
const nodes=Object.fromEntries(['fac-county','fac-own','fac-type','fac-search','fac-reset','fac-print','fac-count','listings','fac-nearby','fac-zip','fac-radius','fac-status'].map(id=>[id,mk()]));
nodes['fac-county'].options=[{value:''},...counties.map(c=>({value:c.county}))];
const ctx=vm.createContext({URL,URLSearchParams,document:{getElementById:id=>nodes[id]},location:{href:'https://example.org/facilities.html',search:''},history:{replaceState(){}},window:{print(){}}});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
// Data integrity and provenance.
assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(FAC)',ctx)),data);
const nh=data.filter(f=>f.facility_type==='nursing_home'),rc=data.filter(f=>f.facility_type==='residential_care');
assert.equal(nh.length,924);assert.equal(source.nursing_homes.ohio_rows,924);assert.equal(rc.length,817);assert.equal(source.residential_care.rows,817);assert.equal(data.length,1741);
assert.equal(new Set(data.map(f=>f.id)).size,1741);assert.equal(new Set(nh.map(f=>f.ccn)).size,924);assert.equal(new Set(rc.map(f=>f.license_id)).size,817);
for(const k of ['nursing_homes','residential_care'])assert(/^[0-9a-f]{64}$/.test(source[k].sha256),k);assert(source.nursing_homes.source_url.startsWith('https://data.cms.gov/'));assert(source.residential_care.source_url.startsWith('https://publicapps.odh.ohio.gov/'));assert(source.residential_care.scope.includes('not published'));
const known=new Set(counties.map(c=>c.county));
for(const f of data){assert(known.has(f.county),f.id);assert(/^\d{5}$/.test(f.zip),f.id);assert(/^\d{3}-\d{3}-\d{4}$/.test(f.phone),f.id);assert(f.beds>=0,f.id);assert(f.address.endsWith('OH '+f.zip),f.id);assert(!('rating' in f)&&!('penalties' in f)&&!('fines' in f),f.id);assert(!Object.keys(f).some(k=>/mail|fax/i.test(k)||['owner','owner_name','owner_phone','owner_address'].includes(k)),f.id)}
for(const f of nh){assert(f.beds>0,f.id);assert(['Non profit','For profit','Government'].includes(f.ownership),f.id)}
for(const f of rc){assert(/^OHL\d+$/.test(f.license_id),f.id);assert.equal(f.ownership,null);assert(!f.vhg_visiting&&!f.ohio_veterans_home,f.id)}
assert(!JSON.stringify(data).includes('@'),'no email addresses may be published');
const byId=new Map(data.map(f=>[f.id,f]));for(const f of rc.filter(f=>f.campus_nursing_home))assert.equal(byId.get(f.campus_nursing_home).facility_type,'nursing_home');assert(rc.filter(f=>f.campus_nursing_home).length>100);
assert.equal(new Set(nh.map(f=>f.county)).size,88);assert.equal(new Set(rc.map(f=>f.county)).size,82);
// Guardian-visited and veterans-home flags are limited to the known records.
assert.deepEqual(data.filter(f=>f.vhg_visiting).map(f=>f.name).sort(),['Bennington Glen Nursing & Rehabilitation Center','Centerburg Pointe','Morrow Manor Nursing Center','Woodside Village Care Center']);
assert.equal(data.filter(f=>f.ohio_veterans_home).length,2);
// Filters, search and sorting.
assert.equal(vm.runInContext("filteredFacilities('Morrow','','','nursing_home').length",ctx),3);
assert.equal(vm.runInContext("filteredFacilities('Marion','','','nursing_home').length",ctx),6);
assert.equal(vm.runInContext("filteredFacilities('Knox','','','nursing_home').length",ctx),7);
assert.equal(vm.runInContext("filteredFacilities('Delaware','','','nursing_home').length",ctx),8);
assert.equal(vm.runInContext("filteredFacilities('','','centerburg pointe').length",ctx),1);
assert(vm.runInContext("filteredFacilities('','','Trilogy').length",ctx)>20);
assert.equal(vm.runInContext("filteredFacilities('','Government','').length",ctx),data.filter(f=>f.ownership==='Government').length);
assert.equal(vm.runInContext("filteredFacilities('','','zzzz-none').length",ctx),0);
assert.equal(vm.runInContext("filteredFacilities('Marion','','').length",ctx),10);assert.equal(vm.runInContext("filteredFacilities('Marion','','','residential_care').length",ctx),4);assert.equal(vm.runInContext("filteredFacilities('Morrow','','','residential_care').length",ctx),0);
assert.equal(vm.runInContext("filteredFacilities('','','','residential_care').length",ctx),817);
// Rendering: cards show the right links and the Guardian badge, and escape unsafe text.
vm.runInContext('render()',ctx);assert(nodes['fac-count'].textContent.includes('of 1741 facilities'));
assert(nodes.listings.innerHTML.indexOf('Veteran Home Guardians visits here')<nodes.listings.innerHTML.indexOf('class="badge">Non profit'));
nodes['fac-county'].value='Marion';nodes['fac-type'].value='nursing_home';vm.runInContext('render()',ctx);
const card=nodes.listings.innerHTML.split('id="cms-366304"')[1].split('</article>')[0];
assert(card.includes('Marion Valley Post Acute'));assert(card.includes('tel:7403871225'));assert(card.includes('bingo.html?zip=43302&amp;radius=25&amp;kind=bingo'));assert(card.includes('Update this listing'));assert(card.includes('google.com/maps'));
const mail=new URL(vm.runInContext("updateEmail(FAC.find(f=>f.ccn==='366304'))",ctx));assert.equal(mail.pathname,'travis@vethomeguard.org');assert(mail.searchParams.get('body').includes('CMS number: 366304'));
assert.equal(vm.runInContext("esc('<b>\"x\"</b>')",ctx),'&lt;b&gt;&quot;x&quot;&lt;/b&gt;');
const al=nodes['fac-type'];al.value='residential_care';vm.runInContext('render()',ctx);assert(nodes.listings.innerHTML.includes('Assisted living / residential care'));assert(nodes.listings.innerHTML.includes('licensed beds'));assert(!nodes.listings.innerHTML.includes('certified beds'));
const cardAL=nodes.listings.innerHTML.split('id="odh-')[1].split('</article>')[0];assert(cardAL.includes('Update this listing'));assert(!cardAL.replaceAll('travis@vethomeguard.org','').includes('@'));
const mailAL=new URL(vm.runInContext("updateEmail(FAC.find(f=>f.facility_type==='residential_care'))",ctx));assert(mailAL.searchParams.get('body').includes('Ohio license: OHL'));
nodes['fac-type'].value='';nodes['fac-county'].value='';
// ZIP distance: nearest first, within radius, bad ZIP rejected, reset clears.
const near=JSON.parse(vm.runInContext("JSON.stringify(nearbyFacilities(FAC,'43334',10))",ctx));assert(near.length>=1);assert(near.every((f,i)=>f.distanceMiles<=10&&(!i||near[i-1].distanceMiles<=f.distanceMiles)));assert(near.some(f=>f.ccn==='366194'));
assert.equal(vm.runInContext("nearbyFacilities(FAC,'00000',10)",ctx),null);
nodes['fac-zip'].value='43334';nodes['fac-radius'].value='25';nodes['fac-nearby'].onsubmit({preventDefault(){}});assert(nodes['fac-count'].textContent.includes('within 25 miles of 43334'));assert(nodes.listings.innerHTML.includes('miles away'));
nodes['fac-zip'].value='99999';nodes['fac-nearby'].onsubmit({preventDefault(){}});assert(nodes['fac-status'].textContent.includes('valid five-digit'));
nodes['fac-reset'].onclick();assert.equal(nodes['fac-zip'].value,'');assert.equal(nodes['fac-type'].value,'');assert(nodes['fac-count'].textContent.includes('of 1741'));
// Page copy states its limits, and the guide links to it from Ohio only.
assert(html.includes('does not identify memory care units'));assert(html.includes('does not rate or recommend'));
const index=fs.readFileSync(path.join(root,'index.html'),'utf8');assert(index.includes('href="facilities.html"')&&index.includes('ohio-only'));
console.log('PASS: 924 nursing homes and 817 assisted living facilities, provenance, filters, ZIP distance, cards, links, escaping and Ohio-only entry point.');
// Name and address hygiene: no doubled words from abbreviation cleanup, no stray spaces or trailing commas.
for(const f of data){assert(!/ive\b.*Driveive|Driveive|Roadad/.test(f.address),f.id);assert(!/\s{2,}/.test(f.name+f.address),f.id);assert(!/[,;\s]$/.test(f.name),f.id);assert(!/\b(Dr|Rd)\b(?!\.)/.test(f.address),f.id)}
console.log('PASS: facility names and addresses are clean.');

// Paging: the full list is never drawn at once; "Show more" adds a page; filters and printing behave.
const cardsIn=h=>(h.match(/<article /g)||[]).length;
nodes['fac-reset'].onclick();assert.equal(cardsIn(nodes.listings.innerHTML),60);assert(nodes.listings.innerHTML.includes('id="fac-more"'));assert(nodes.listings.innerHTML.includes('Showing 60 of 1741'));assert(nodes['fac-count'].textContent.includes('of 1741 facilities'));
nodes.listings.onclick({target:{closest:sel=>sel==='#fac-more'?{}:null}});assert.equal(cardsIn(nodes.listings.innerHTML),120);assert(nodes.listings.innerHTML.includes('Showing 120 of 1741'));
nodes['fac-county'].value='Marion';nodes['fac-county'].addEventListener=()=>{};vm.runInContext('refresh()',ctx);assert.equal(cardsIn(nodes.listings.innerHTML),10);assert(!nodes.listings.innerHTML.includes('fac-more'));
nodes['fac-county'].value='';vm.runInContext('refresh()',ctx);assert.equal(cardsIn(nodes.listings.innerHTML),60);
let printedCards=0;ctx.window.print=()=>{printedCards=cardsIn(nodes.listings.innerHTML)};nodes['fac-print'].onclick();assert.equal(printedCards,1741);assert.equal(cardsIn(nodes.listings.innerHTML),60);
nodes['fac-reset'].onclick();
console.log('PASS: paged listings, show more, filter reset to first page, and print includes every match.');
