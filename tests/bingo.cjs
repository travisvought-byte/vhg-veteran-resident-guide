require('./legacy-fixtures.cjs');
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'bingo.html'),'utf8'),canonical=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-bingo.json'),'utf8'));
const authorized=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-bingo-authorized.json'),'utf8'));const centers=JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-community-centers.json'),'utf8'));const base=canonical.map(r=>{const c=centers.find(c=>c.id===r.id);return c?{...r,...c,sources:Array.from(new Map(r.sources.concat(c.sources).map(s=>[s.url+'|'+s.scope,s])).values())}:r}).concat(centers.filter(c=>!canonical.some(r=>r.id===c.id)));const known=new Set(canonical.filter(r=>r.license_number).map(r=>r.license_number));const combined=base.concat(authorized.filter(r=>!known.has(r.license_number)));
const nodes=Object.fromEntries(['bingo-county','bingo-kind','bingo-day','bingo-time','hidden-note','flyer','bingo-search','bingo-reset','bingo-print','count','listings','bingo-submit','submit-venue','submit-county','submit-info','submit-source','submit-contact','bingo-nearby','bingo-zip','bingo-radius','nearby-status'].map(id=>[id,{value:'',innerHTML:'',textContent:'',options:[],addEventListener(){}}]));nodes['bingo-county'].options=[{value:''},...JSON.parse(fs.readFileSync(path.join(root,'data/public/ohio-county-veterans-offices.json'),'utf8')).map(c=>({value:c.county}))];
class GuideDate extends Date {constructor(...args){super(...(args.length?args:['2026-10-09T12:00:00Z']))}}
const context=vm.createContext({Date:GuideDate,URL,URLSearchParams,document:{getElementById:id=>nodes[id]},location:{href:'https://example.org/bingo.html',search:''},history:{replaceState(){}},window:{print(){}}});vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(BINGO)',context)),combined);
assert.equal(vm.runInContext("filteredBingo('Morrow','charitable','').length",context),3);assert.equal(vm.runInContext("filteredBingo('Knox','senior','').length",context),1);assert.equal(vm.runInContext("filteredBingo('Morrow','senior','').length",context),0);assert.equal(vm.runInContext("filteredBingo('','','cardington').length",context),1);
assert.equal(new Set(canonical.map(r=>r.id)).size,canonical.length);assert.equal(canonical.filter(r=>r.firsthand_confirmation).length,2);
for(const r of canonical){assert.equal(r.state,'OH');assert.equal(!!r.license_number,r.category==='charitable');assert.equal(r.accessibility,null);assert(r.sources.length);for(const s of r.sources)assert(new URL(s.url).protocol==='https:');const card=nodes.listings.innerHTML.split(`id="${r.id}"`)[1]?.split('</article>')[0];assert(!card.includes('Not yet verified'));assert(card.includes('Add or update details'));}
assert(canonical.find(r=>r.id==='cardington-legion-97').schedule==='Saturday: doors open 4 p.m.; bingo starts 6 p.m.');assert(canonical.find(r=>r.id==='marion-senior-bingo').schedule===null);assert(html.includes('717 state-listed bingo entries'));assert.equal(authorized.length,717);assert.equal(combined.length,815);assert.equal(vm.runInContext("filteredBingo('','licensed','').length",context),717);assert.equal(new Set(combined.map(r=>r.id)).size,815);assert(authorized.every(r=>r.license_type==='Type I'));assert.equal(authorized.filter(r=>r.schedule).length,68);
assert(fs.readFileSync(path.join(root,'index.html'),'utf8').includes('id="ohio-bingo-link"'));for(const page of ['pa.html','ny.html','mi.html','ky.html'])assert(!fs.readFileSync(path.join(root,page),'utf8').includes('id="ohio-bingo-link"'));
console.log('PASS: bingo county/type/search boundaries, canonical data, per-field limits, firsthand scope, corrections and Ohio-only integration.');

const email=new URL(vm.runInContext("submissionEmail('Hall & Friends','Morrow','Tuesday 7 p.m.\\n$10','https://example.org/?a=1&b=2','Visitor')",context));
assert.equal(email.pathname,'travis@vethomeguard.org');assert.equal(email.searchParams.get('subject'),'Community activity details: Hall & Friends');assert(email.searchParams.get('body').includes('Tuesday 7 p.m.\n$10'));assert(email.searchParams.get('body').includes('https://example.org/?a=1&b=2'));
nodes.listings.onclick({target:{closest:()=>({dataset:{submit:'cardington-legion-97'}})}});
assert.equal(nodes['submit-venue'].value,'Jenkins-Vaughan American Legion Post 97');assert.equal(nodes['submit-county'].value,'Morrow');
nodes['submit-info'].value='Saturday 6 p.m.';let prevented=false;nodes['bingo-submit'].onsubmit({preventDefault(){prevented=true}});assert(prevented);assert(context.location.href.startsWith('mailto:travis@vethomeguard.org?'));
assert.equal(vm.runInContext("filteredBingo('','scheduled','').length",context),75);
console.log('PASS: submission prefill, email draft recipient/encoding and schedule filter.');

const zero=vm.runInContext('milesBetween([40,-83],[40,-83])',context);assert.equal(zero,0);
const equator=vm.runInContext('milesBetween([0,0],[0,1])',context);assert(Math.abs(equator-69.09)<0.1);
assert(vm.runInContext("nearbyBingo(BINGO,'43334',25).some(r=>r.id==='marengo-legion-710')",context));
assert(!vm.runInContext("nearbyBingo(BINGO,'43334',25).some(r=>r.id==='oh-license-0100-49-543-5')",context));
assert(vm.runInContext("nearbyBingo(BINGO,'00000',50)===null",context));
const close=JSON.parse(vm.runInContext("JSON.stringify(nearbyBingo(BINGO,'43334',50))",context));assert(close.length>3);assert(close.every((r,i)=>r.distanceMiles<=50&&(!i||close[i-1].distanceMiles<=r.distanceMiles)));
nodes['bingo-zip'].value='43334';nodes['bingo-radius'].value='25';nodes['bingo-nearby'].onsubmit({preventDefault(){}});assert(nodes.count.textContent.includes('within 25 miles of 43334'));assert(nodes.listings.innerHTML.includes('miles away'));
nodes['bingo-zip'].value='00000';nodes['bingo-nearby'].onsubmit({preventDefault(){}});assert(nodes['nearby-status'].textContent.includes('valid five-digit'));assert(nodes.count.textContent.includes('published schedules'));assert(nodes['hidden-note'].innerHTML.includes('state-licensed bingo locations with no published schedule yet'));
nodes['bingo-reset'].onclick();assert.equal(nodes['bingo-zip'].value,'');assert.equal(nodes['bingo-radius'].value,'50');
console.log('PASS: ZIP distance math, nearest sorting, radius inclusion, invalid ZIP and reset.');

assert.equal(vm.runInContext("filteredBingo('','centers','').length",context),98);
assert.equal(vm.runInContext("filteredBingo('','bingo','').length",context),723);
assert.equal(vm.runInContext("filteredBingo('','exercise','').length",context),5);
assert.equal(vm.runInContext("filteredBingo('','meals','').length",context),10);
assert.equal(vm.runInContext("filteredBingo('','crafts','').length",context),5);
assert.equal(vm.runInContext("filteredBingo('','','euchre').length",context),1);
assert(vm.runInContext("nearbyBingo(filteredBingo('','centers',''),'43334',25).some(r=>r.id==='centerburg-senior-services')",context));
assert(vm.runInContext("nearbyBingo(filteredBingo('','meals',''),'43334',25).some(r=>r.id==='seniors-on-center')",context));
assert(centers.every(c=>c.is_center&&c.sources.length));
console.log('PASS: ninety-eight senior centers, non-bingo categories, no duplicate centers and ZIP integration.');
assert(nodes.listings.innerHTML.includes('Senior Centers (98)'));
assert(!nodes.listings.innerHTML.includes('Bingo (717)'));nodes['hidden-note'].onclick({target:{closest:()=>({dataset:{all:'1'}})}});assert(nodes.listings.innerHTML.includes('Bingo (717)'));assert(nodes['hidden-note'].innerHTML.includes('Show only published schedules'));
nodes['bingo-kind'].value='bingo';vm.runInContext('render()',context);
assert(nodes.listings.innerHTML.includes('Bingo (723)'));
assert(!nodes.listings.innerHTML.includes('Senior Centers ('));
nodes['bingo-kind'].value='';vm.runInContext('render()',context);
console.log('PASS: distinct groups, no duplicate all-view cards and center bingo included in Bingo filter.');
assert(html.includes('bingo.html?zip=43334&amp;radius=25'));
assert(nodes.listings.innerHTML.includes('How to join:'));
assert(nodes.listings.innerHTML.includes('https://www.google.com/maps/search/?api=1&amp;query=41%20West%20Center'));
assert(vm.runInContext("filteredBingo('Morrow','','accessible transportation').some(r=>r.id==='seniors-on-center')",context));
assert(!vm.runInContext("filteredBingo('Knox','','accessible transportation').some(r=>r.id==='seniors-on-center')",context));
console.log('PASS: local ZIP shortcut, address directions, participation steps and county-scoped transport search.');
const lexington=centers.find(c=>c.id==='lexington-senior-civic-center');
assert.equal(lexington.schedule,'Tuesday and Thursday, 1 p.m.');
assert(vm.runInContext("filteredBingo('Richland','scheduled','').some(r=>r.id==='lexington-senior-civic-center')",context));
assert(vm.runInContext("nearbyBingo(filteredBingo('','centers',''),'43334',50).some(r=>r.id==='lexington-senior-civic-center')",context));
assert(nodes.listings.innerHTML.includes('Bingo: 1¢ per card. Lunch: $9 per meal.'));
assert(vm.runInContext("filteredBingo('Delaware','scheduled','').some(r=>r.license_number==='0219-48'&&r.schedule.includes('2 p.m.'))",context));
assert.equal(authorized.find(r=>r.license_number==='0080-34').cost,'$29 small pack or $41 large pack; third Wednesday of the month, packets $7 off.');
assert.equal(authorized.find(r=>r.license_number==='0219-48').authorized_days,'Sunday, Tuesday, Thursday');
assert(!authorized.find(r=>r.license_number==='0169-32').schedule);
assert(vm.runInContext("filteredBingo('Union','scheduled','').some(r=>r.id==='windsor-community-seniors'&&r.schedule==='Tuesday, 1:30 p.m.')",context));
assert.equal(centers.find(c=>c.id==='lcap-heritage-hall').activities[0],'Social lunch: Monday–Friday, 11:30 a.m.');
assert(vm.runInContext("nearbyBingo(filteredBingo('Union','centers',''),'43334',50).some(r=>r.id==='richwood-civic-center')",context));
assert(!vm.runInContext("filteredBingo('Morrow','centers','').some(r=>r.id==='lcap-heritage-hall')",context));

// Date filters must use published sessions, never license authorization days.
for(const r of combined.filter(r=>r.schedule))assert.equal(['session_days','session_dates','session_monthly'].filter(k=>r[k]?.length).length,1,r.id);
assert(!vm.runInContext("filteredBingo('Morrow','','','2','2026-10-09').some(r=>!r.schedule)",context));
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='northmor-music-bingo'),'2','2026-10-09')",context),'2026-10-20');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='northmor-music-bingo'),'today','2026-10-13')",context),null);
assert.equal(vm.runInContext("activeSchedule(BINGO.find(r=>r.id==='northmor-music-bingo'),'2026-10-21')",context),false);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0155-48'),'3','2026-10-09')",context),'2026-11-04');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0155-48'),'today','2026-12-02')",context),'2026-12-02');
assert.equal(vm.runInContext("activeSchedule(BINGO.find(r=>r.license_number==='0155-48'),'2026-12-03')",context),false);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0179-29'),'today','2026-10-31')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0179-29'),'6','2026-10-24')",context),'2026-10-24');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0179-29'),'6','2026-10-25')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='cardington-legion-97'),'tomorrow','2026-10-09')",context),'2026-10-10');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='cardington-legion-97'),'tomorrow','2026-12-31')",context),null);
assert.equal(vm.runInContext("addDays('2026-12-31',1)",context),'2027-01-01');
assert.equal(vm.runInContext("activeSchedule(BINGO.find(r=>r.id==='sourcepoint-bingo'),'2027-01-03')",context),false);
assert.equal(vm.runInContext("activePrice(BINGO.find(r=>r.license_number==='0024-33'),'2026-11-01')",context),null);
assert(vm.runInContext("activePrice(BINGO.find(r=>r.license_number==='0024-33'),'2026-10-31')",context));
nodes['bingo-day'].value='2';vm.runInContext('render()',context);assert(nodes.listings.innerHTML.includes('Tuesday, Oct 20, 2026'));assert(!nodes.listings.innerHTML.includes('id="cardington-legion-97"'));
nodes['bingo-reset'].onclick();assert.equal(nodes['bingo-day'].value,'');assert(nodes.count.textContent.includes('published schedules'));assert(nodes['hidden-note'].innerHTML.includes('state-licensed bingo locations with no published schedule yet'));
vm.runInContext("todayISO=()=> '2026-11-25'",context);nodes['bingo-day'].value='today';vm.runInContext('render()',context);
let sourceCard=nodes.listings.innerHTML.split('id="sourcepoint-bingo"')[1]?.split('</article>')[0];assert(sourceCard.includes('Earlier holiday session'));assert(!sourceCard.includes('2:30-4:30'));
nodes['bingo-reset'].onclick();const northCard=nodes.listings.innerHTML.split('id="northmor-music-bingo"')[1].split('</article>')[0];assert(northCard.includes('Ask the venue for upcoming bingo dates.'));assert(!northCard.includes('Next advertised October session'));assert(!northCard.includes('<strong>When:</strong>'));
const groveCard=nodes.listings.innerHTML.split('id="oh-license-0024-33-232-8"')[1].split('</article>')[0];assert(!groveCard.includes('<strong>Price:</strong>'));assert(!groveCard.includes('Price offer through'));
assert.equal(vm.runInContext("filteredBingo('','licensed','','','2027-01-03').length",context),717);
console.log('PASS: published weekdays, date-only sessions, closures, holiday times, month/year rollover, expiry and venue retention.');
// One-off future dates must not leak into exact-date filters.
assert.equal(vm.runInContext("nextBingoDate({schedule:'October 20',session_dates:['2026-10-20']},'today','2026-10-11')",context),null);
assert.equal(vm.runInContext("nextBingoDate({schedule:'October 20',session_dates:['2026-10-20']},'tomorrow','2026-10-11')",context),null);
assert.equal(vm.runInContext("nextBingoDate({schedule:'October 20',session_dates:['2026-10-20']},'today','2026-10-20')",context),'2026-10-20');
// Ohio dates are stable for visitors browsing from other time zones.
assert.equal(vm.runInNewContext(html.match(/function todayISO\(\)\{[^\n]+/)[0]+';todayISO()', {Date:class extends Date {constructor(){super('2026-10-12T00:30:00Z')}},Intl}),'2026-10-11');
console.log('PASS: exact-date events and Ohio timezone boundary.');
// Selected-date and multi-session sources remain faithful to organizer calendars.
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0476-45'),'today','2026-10-23')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0476-45'),'today','2026-10-16')",context),'2026-10-16');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='1048-46'),'today','2026-11-26')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='1048-46'),'today','2026-11-12')",context),'2026-11-12');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0614-27'),'today','2026-10-15')",context),'2026-10-15');
const evidence=JSON.parse(fs.readFileSync(path.join(root,'research/bingo-session-review-2026-10-11.json'),'utf8'));
assert.equal(evidence.updates.length,17);assert.equal(evidence.updates.filter(r=>!r.before.schedule).length,16);
assert(evidence.updates.every(r=>authorized.some(a=>a.id===r.id&&a.sources.some(s=>s.url===r.source_url))));
console.log('PASS: selected Friday dates, irregular Brightside events, ACO Thursday and source audit.');
// The newly sourced Saturday event is not made into a weekly Saturday session.
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0476-45'),'today','2026-10-24')",context),'2026-10-24');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0476-45'),'today','2026-10-31')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0172-45'),'today','2026-10-12')",context),'2026-10-12');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0172-45'),'today','2026-10-14')",context),'2026-10-14');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0101-28'),'today','2026-10-16')",context),'2026-10-16');
assert(!authorized.find(r=>r.license_number==='1025-28').schedule);
assert(!authorized.find(r=>r.license_number==='1018-34').schedule);
vm.runInContext("todayISO=()=> '2026-10-24'",context);nodes['bingo-day'].value='today';vm.runInContext('render()',context);
const neonCard=nodes.listings.innerHTML.split('id="oh-license-0476-45-432-4"')[1].split('</article>')[0];assert(neonCard.includes('7:15 p.m.'));assert(!neonCard.includes('<strong>When:</strong> Published regular Friday'));
console.log('PASS: one-off Neon date/time, Piqua weekdays and Belpre operator isolation.');

const pass4=JSON.parse(fs.readFileSync(path.join(root,'research/bingo-session-review-2026-10-12-pass4.json'),'utf8'));
assert.equal(pass4.updates.length,9);assert.equal(pass4.updates.filter(r=>!r.before.schedule).length,8);
assert(pass4.updates.every(r=>authorized.some(a=>a.id===r.id&&a.sources.some(s=>s.url===r.source_url))));
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0168-37'),'today','2026-10-21')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0168-37'),'today','2026-10-28')",context),'2026-10-28');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0051-47'),'today','2026-11-01')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0073-41'),'today','2026-11-16')",context),null);
console.log('PASS: pass-four source audit and selected-date isolation.');

const pass5=JSON.parse(fs.readFileSync(path.join(root,'research/bingo-session-review-2026-10-12-pass5.json'),'utf8'));
assert.equal(pass5.updates.length,6);assert.equal(pass5.updates.filter(r=>!r.before.schedule).length,3);
assert(pass5.updates.every(r=>authorized.some(a=>a.id===r.id&&a.sources.some(s=>s.url===r.source_url))));
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0036-48'),'today','2026-10-15')",context),'2026-10-15');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0036-48'),'today','2026-10-22')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0036-48'),'tomorrow','2026-10-14')",context),'2026-10-15');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0036-48'),'','2026-10-16')",context),'2026-11-05');
assert.equal(vm.runInContext("nextBingoDate({schedule:'monthly',session_monthly:[{weekday:4,weeks:[5]}]},'','2026-11-01')",context),'2026-12-31');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='1056-27'),'today','2026-10-25')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.license_number==='0181-45'),'today','2026-12-12')",context),null);
console.log('PASS: monthly ordinal filters, month rollover, fifth-week gaps and announced-event isolation.');

assert.equal(vm.runInContext("nextBingoDate({schedule:'monthly',session_monthly:[{weekday:2,weeks:[5]}]},'','2027-01-01')",context),'2027-03-30');

const batch1=JSON.parse(fs.readFileSync(path.join(root,'research/bingo-session-review-2026-10-14-batch1.json'),'utf8'));
assert.equal(batch1.updates.length+batch1.deferred.length,5);assert.equal(batch1.promotion_candidates.length,2);
assert(batch1.updates.every(r=>authorized.some(a=>a.id===r.id&&r.sources.every(url=>a.sources.some(s=>s.url===url)))));
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0148-32-177-9'),'today','2026-10-15')",context),'2026-10-15');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0148-32-177-9'),'today','2026-10-16')",context),null);
assert(!authorized.find(r=>r.id==='oh-license-0148-32-177-8').schedule);
const celina=authorized.find(r=>r.id==='oh-license-0411-27-16-9');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0411-27-16-9'),'today','2026-11-08')",context),'2026-11-08');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0411-27-16-9'),'today','2026-11-15')",context),null);
assert.equal(vm.runInContext("activePrice(BINGO.find(r=>r.id==='oh-license-0411-27-16-9'),'2026-11-09')",context),null);
for(const id of ['oh-license-0381-48-500-9','oh-license-0104-27-99-7','oh-license-0162-49-525-9'])assert(!authorized.find(r=>r.id===id).schedule);
vm.runInContext("todayISO=()=> '2026-11-08'",context);nodes['bingo-day'].value='today';vm.runInContext('render()',context);assert(nodes.listings.innerHTML.includes('Celina Lake Festival Designer Purse Bingo'));assert(nodes.listings.innerHTML.includes('1 p.m.'));
vm.runInContext("todayISO=()=> '2026-11-09'",context);nodes['bingo-day'].value='';vm.runInContext('render()',context);assert(!nodes.listings.innerHTML.includes('<h2>Celina Lake Festival Designer Purse Bingo'));assert(!nodes.listings.innerHTML.includes('href="tel:4197333884"'));
console.log('PASS: five-venue audit, distinct addresses, supported advertising titles, one-off expiry and unresolved schedule exclusion.');

const batch2=JSON.parse(fs.readFileSync(path.join(root,'research/bingo-session-review-2026-10-14-batch2.json'),'utf8'));
assert.equal(batch2.updates.length+batch2.deferred.length,5);assert.equal(new Set([...batch2.updates,...batch2.deferred].map(r=>r.id)).size,5);
assert(batch2.updates.every(r=>authorized.some(a=>a.id===r.id&&r.sources.every(url=>a.sources.some(s=>s.url===url)))));
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0119-42-379-6'),'today','2026-11-06')",context),'2026-11-06');
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0119-42-379-6'),'today','2026-11-13')",context),null);
assert.equal(vm.runInContext("activePrice(BINGO.find(r=>r.id==='oh-license-0119-42-379-6'),'2026-11-07')",context),null);
assert.equal(vm.runInContext("nextBingoDate(BINGO.find(r=>r.id==='oh-license-0237-45-442-9'),'today','2026-10-21')",context),'2026-10-21');
assert(!authorized.find(r=>r.id==='oh-license-0237-45-442-10').schedule);
for(const id of ['oh-license-1015-33-217-10','oh-license-0001-40-337-2','oh-license-0001-40-337-4','oh-license-0174-37-272-8'])assert(!authorized.find(r=>r.id===id).schedule);
vm.runInContext("todayISO=()=> '2026-11-06'",context);nodes['bingo-day'].value='today';vm.runInContext('render()',context);assert(nodes.listings.innerHTML.includes('<h2>Falling for Handbags'));assert(nodes.listings.innerHTML.includes('Age 18 and older; organizer says ID will be checked.'));
vm.runInContext("todayISO=()=> '2026-11-07'",context);nodes['bingo-day'].value='';vm.runInContext('render()',context);assert(!nodes.listings.innerHTML.includes('<h2>Falling for Handbags'));
console.log('PASS: second five-venue batch, one-off offer expiry, separate Delphos/Newark addresses and unresolved schedule boundaries.');
// Activity-director view: published games first, time of day, last-checked dates and the facility flyer.
assert.deepEqual(JSON.parse(vm.runInContext("JSON.stringify(gameTimes('Sunday: doors noon; instant sales 11 a.m.; early birds 3 p.m.; bingo 6:30 p.m.'))",context)),[900,1110]);
assert.deepEqual(JSON.parse(vm.runInContext("JSON.stringify(gameTimes('Friday, 12:45-2 p.m.'))",context)),[765]);
assert.deepEqual(JSON.parse(vm.runInContext("JSON.stringify(gameTimes('doors 3 p.m.; dinner 4 p.m.; bingo 5 p.m.'))",context)),[1020]);
assert.equal(vm.runInContext("gameTimes('Bingo Night announced; start time to be announced.').length",context),0);
assert(vm.runInContext("matchesTime(BINGO.find(r=>r.id==='sourcepoint-bingo'),'afternoon','2026-10-09')",context));
assert(!vm.runInContext("matchesTime(BINGO.find(r=>r.id==='sourcepoint-bingo'),'evening','2026-10-09')",context));
assert(vm.runInContext("matchesTime(BINGO.find(r=>r.id==='cardington-legion-97'),'evening','2026-10-09')",context));
assert(!vm.runInContext("matchesTime(BINGO.find(r=>r.id==='northmor-music-bingo'),'evening','2026-10-21')",context));
assert(!vm.runInContext("matchesTime(BINGO.find(r=>!r.schedule&&r.category==='licensed'),'afternoon','2026-10-09')",context));
nodes['bingo-reset'].onclick();vm.runInContext("todayISO=()=> '2026-10-09'",context);vm.runInContext('render()',context);
const limitedCount=Number(nodes.count.textContent.split(' ')[0]);assert(limitedCount>70&&limitedCount<200,limitedCount);
assert(!nodes.listings.innerHTML.includes('Bingo · state authorization'));assert(nodes.listings.innerHTML.includes('Last checked Oct'));
nodes['bingo-kind'].value='licensed';vm.runInContext('render()',context);assert(nodes.listings.innerHTML.includes('Bingo (717)'));assert.equal(nodes['hidden-note'].innerHTML,'');nodes['bingo-kind'].value='';
nodes['bingo-time'].value='afternoon';vm.runInContext('render()',context);assert(nodes.listings.innerHTML.includes('id="sourcepoint-bingo"'));assert(!nodes.listings.innerHTML.includes('id="cardington-legion-97"'));nodes['bingo-reset'].onclick();assert.equal(nodes['bingo-time'].value,'');
const flyer=JSON.parse(vm.runInContext("JSON.stringify(flyerRows('43334',25,'2026-10-09'))",context));assert(flyer.length&&flyer.length<=10);assert(flyer.every((r,i)=>(r.is_center||r.schedule)&&(!i||flyer[i-1].distanceMiles<=r.distanceMiles)));
vm.runInContext("renderFlyer('Bennington Glen','43334',25,'2026-10-09')",context);assert(nodes.flyer.innerHTML.includes('Bingo &amp; senior activities near Bennington Glen'));assert(nodes.flyer.innerHTML.includes('assets/bingo-qr.svg'));assert(nodes.flyer.innerHTML.includes('Jenkins-Vaughan American Legion Post 97'));
vm.runInContext("renderFlyer('<b>x</b>','43334',10,'2026-10-09')",context);assert(!nodes.flyer.innerHTML.includes('<b>x</b>'));
assert(fs.existsSync(path.join(root,'assets/bingo-qr.svg')));assert(html.includes('id="flyer-form"'));
assert(vm.runInContext("!!ZIP_CENTROIDS['43334']&&!!ZIP_CENTROIDS['15001']&&!ZIP_CENTROIDS['90210']",context));
console.log('PASS: published-first default, time-of-day filter, last-checked dates, facility flyer and regional ZIP data.');
// State enforcement notices are shown, kept factual, and excluded from printed facility flyers.
const noticed=authorized.filter(r=>r.enforcement);assert.equal(noticed.length,4);
for(const r of noticed){assert.equal(r.enforcement.status,'notice_of_intent');assert(r.enforcement.url.startsWith('https://charitable.ohioago.gov/'));assert(r.sources.some(s=>s.url===r.enforcement.url));}
nodes['bingo-reset'].onclick();nodes['bingo-kind'].value='licensed';nodes['bingo-county'].value='Marion';vm.runInContext('render()',context);
const mcab=nodes.listings.innerHTML.split('id="oh-license-0113-39-306-3"')[1].split('</article>')[0];assert(mcab.includes('State licensing notice:'));assert(mcab.includes('This is not a final decision.'));assert(mcab.includes('Nov 18, 2026'));
const koc=nodes.listings.innerHTML.split('id="oh-license-0096-37-272-1"')[1].split('</article>')[0];assert(koc.includes('tel:7403823671'));assert(!koc.includes('State licensing notice'));
nodes['bingo-reset'].onclick();
assert(!JSON.parse(vm.runInContext("JSON.stringify(flyerRows('45042',50,'2026-10-09'))",context)).some(r=>r.enforcement));
console.log('PASS: Attorney General enforcement notices labeled as non-final and excluded from flyers.');
// Structured submissions arrive ready to enter; the organizer flyer points to the form.
const structured=new URL(vm.runInContext("submissionEmail('Hall','Marion','','','',['Game days: Sunday, Thursday','Doors: 5 p.m.','Care-facility groups: Yes, call ahead'])",context));
const sb=structured.searchParams.get('body');assert(sb.includes('Game days: Sunday, Thursday'));assert(sb.indexOf('County: Marion')<sb.indexOf('Game days'));assert(sb.includes('Care-facility groups: Yes, call ahead'));
assert(html.includes('id="submit-groups"')&&html.includes('name="submit-day" value="Sunday"'));
vm.runInContext('renderOrganizerFlyer()',context);assert(nodes.flyer.innerHTML.includes('Is your bingo game listed?'));assert(nodes.flyer.innerHTML.includes('assets/bingo-submit-qr.svg'));assert(nodes.flyer.innerHTML.includes('Inclusion never depends on donations'));
assert(fs.existsSync(path.join(root,'assets/bingo-submit-qr.svg')));
console.log('PASS: structured submission email and organizer flyer.');
// A listing link (#id) must reveal that listing even when it is license-only.
const linkHtml=fs.readFileSync(path.join(root,'bingo.html'),'utf8');
const linkNodes=Object.fromEntries(Object.keys(nodes).map(k=>[k,{value:'',innerHTML:'',textContent:'',options:nodes[k].options,addEventListener(){}}]));
const linkCtx=vm.createContext({Date:GuideDate,URL,URLSearchParams,document:{getElementById:id=>linkNodes[id]},location:{href:'https://example.org/bingo.html#oh-license-0096-37-272-1',search:'',hash:'#oh-license-0096-37-272-1'},history:{replaceState(){}},window:{print(){}}});
vm.runInContext(linkHtml.match(/<script>([\s\S]*?)<\/script>/)[1],linkCtx);
assert(linkNodes.listings.innerHTML.includes('id="oh-license-0096-37-272-1"'));
console.log('PASS: per-listing links reveal license-only cards.');
// First screen: the ZIP search comes before the explanatory text, and quick searches are real buttons-sized links.
const mainStart=html.indexOf('<main class="page-only">');const zipAt=html.indexOf('id="bingo-zip"',mainStart),introAt=html.indexOf('class="intro"',mainStart),noticeAt=html.indexOf('Planning a group outing',mainStart);
assert(mainStart>0&&zipAt>mainStart&&zipAt<introAt&&introAt<noticeAt,'ZIP search must come first');
assert(html.includes('<nav class="quick" aria-label="Quick searches">')&&html.includes('min-height:44px'));
console.log('PASS: ZIP search leads the page and quick searches have 44px touch targets.');
