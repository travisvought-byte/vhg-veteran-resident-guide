require('./legacy-fixtures.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'facilities.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-facilities.json'),'utf8'));
const source=JSON.parse(fs.readFileSync(path.join(root,'data/source/ohio-facilities-source.json'),'utf8'));
const counties=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-county-veterans-offices.json'),'utf8'));
const mk=()=>({value:'',innerHTML:'',textContent:'',options:[],addEventListener(){}});
const nodes=Object.fromEntries(['fac-county','fac-own','fac-search','fac-reset','fac-print','fac-count','listings','fac-nearby','fac-zip','fac-radius','fac-status'].map(id=>[id,mk()]));
nodes['fac-county'].options=[{value:''},...counties.map(c=>({value:c.county}))];
const ctx=vm.createContext({URL,URLSearchParams,document:{getElementById:id=>nodes[id]},location:{href:'https://example.org/facilities.html',search:''},history:{replaceState(){}},window:{print(){}}});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
// Data integrity and provenance.
assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(FAC)',ctx)),data);
assert.equal(data.length,924);assert.equal(source.ohio_rows,924);assert.equal(new Set(data.map(f=>f.id)).size,924);assert.equal(new Set(data.map(f=>f.ccn)).size,924);
assert(/^[0-9a-f]{64}$/.test(source.sha256));assert(source.source_url.startsWith('https://data.cms.gov/'));assert(source.scope.includes('Assisted living'));
const known=new Set(counties.map(c=>c.county));
for(const f of data){assert(known.has(f.county),f.id);assert(/^\d{5}$/.test(f.zip),f.id);assert(/^\d{3}-\d{3}-\d{4}$/.test(f.phone),f.id);assert(f.beds>0,f.id);assert(f.address.endsWith('OH '+f.zip),f.id);assert(['Non profit','For profit','Government'].includes(f.ownership),f.id);assert(!('rating' in f)&&!('penalties' in f)&&!('fines' in f),f.id)}
assert.equal(new Set(data.map(f=>f.county)).size,88);
// Guardian-visited and veterans-home flags are limited to the known records.
assert.deepEqual(data.filter(f=>f.vhg_visiting).map(f=>f.name).sort(),['Bennington Glen Nursing & Rehabilitation Center','Centerburg Pointe','Morrow Manor Nursing Center','Woodside Village Care Center']);
assert.equal(data.filter(f=>f.ohio_veterans_home).length,2);
// Filters, search and sorting.
assert.equal(vm.runInContext("filteredFacilities('Morrow','','').length",ctx),3);
assert.equal(vm.runInContext("filteredFacilities('Marion','','').length",ctx),6);
assert.equal(vm.runInContext("filteredFacilities('Knox','','').length",ctx),7);
assert.equal(vm.runInContext("filteredFacilities('Delaware','','').length",ctx),8);
assert.equal(vm.runInContext("filteredFacilities('','','centerburg pointe').length",ctx),1);
assert(vm.runInContext("filteredFacilities('','','Trilogy').length",ctx)>20);
assert.equal(vm.runInContext("filteredFacilities('','Government','').length",ctx),data.filter(f=>f.ownership==='Government').length);
assert.equal(vm.runInContext("filteredFacilities('','','zzzz-none').length",ctx),0);
// Rendering: cards show the right links and the Guardian badge, and escape unsafe text.
vm.runInContext('render()',ctx);assert(nodes['fac-count'].textContent.includes('of 924 facilities'));
assert(nodes.listings.innerHTML.indexOf('Veteran Home Guardians visits here')<nodes.listings.innerHTML.indexOf('class="badge">Non profit'));
nodes['fac-county'].value='Marion';vm.runInContext('render()',ctx);
const card=nodes.listings.innerHTML.split('id="cms-366304"')[1].split('</article>')[0];
assert(card.includes('Marion Valley Post Acute'));assert(card.includes('tel:7403871225'));assert(card.includes('bingo.html?zip=43302&amp;radius=25&amp;kind=bingo'));assert(card.includes('Update this listing'));assert(card.includes('google.com/maps'));
const mail=new URL(vm.runInContext("updateEmail(FAC.find(f=>f.ccn==='366304'))",ctx));assert.equal(mail.pathname,'travis@vethomeguard.org');assert(mail.searchParams.get('body').includes('CMS number: 366304'));
assert.equal(vm.runInContext("esc('<b>\"x\"</b>')",ctx),'&lt;b&gt;&quot;x&quot;&lt;/b&gt;');
nodes['fac-county'].value='';
// ZIP distance: nearest first, within radius, bad ZIP rejected, reset clears.
const near=JSON.parse(vm.runInContext("JSON.stringify(nearbyFacilities(FAC,'43334',10))",ctx));assert(near.length>=1);assert(near.every((f,i)=>f.distanceMiles<=10&&(!i||near[i-1].distanceMiles<=f.distanceMiles)));assert(near.some(f=>f.ccn==='366194'));
assert.equal(vm.runInContext("nearbyFacilities(FAC,'00000',10)",ctx),null);
nodes['fac-zip'].value='43334';nodes['fac-radius'].value='25';nodes['fac-nearby'].onsubmit({preventDefault(){}});assert(nodes['fac-count'].textContent.includes('within 25 miles of 43334'));assert(nodes.listings.innerHTML.includes('miles away'));
nodes['fac-zip'].value='99999';nodes['fac-nearby'].onsubmit({preventDefault(){}});assert(nodes['fac-status'].textContent.includes('valid five-digit'));
nodes['fac-reset'].onclick();assert.equal(nodes['fac-zip'].value,'');assert(nodes['fac-count'].textContent.includes('of 924'));
// Page copy states its limits, and the guide links to it from Ohio only.
assert(html.includes('assisted living, residential care, memory care or adult day services'));assert(html.includes('does not rate or recommend'));
const index=fs.readFileSync(path.join(root,'index.html'),'utf8');assert(index.includes('href="facilities.html"')&&index.includes('ohio-only'));
console.log('PASS: 924 Ohio facilities, provenance, filters, ZIP distance, cards, links, escaping and Ohio-only entry point.');
