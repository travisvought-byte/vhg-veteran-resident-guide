const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
const html=fs.readFileSync('family-guide.html','utf8'),script=fs.readFileSync('assets/family-guide.js','utf8');
function load(q=''){
 const dom=new JSDOM(html,{url:'https://example.org/family-guide.html'+q,runScripts:'outside-only'});const w=dom.window;w.print=()=>{w.printed=true;};w.eval(script);
 const d=w.document,$=id=>d.getElementById(id);
 const visible=sel=>[...d.querySelectorAll(sel)].filter(e=>!e.hidden).map(e=>e.dataset.id);
 const set=(id,v)=>{$(id).value=v;$(id).dispatchEvent(new w.Event('change'));};
 return {w,d,$,visible,set};
}
const data=JSON.parse(load().$('family-data').textContent);
const bad=/undefined|null|NaN|\[object|__[A-Z]+__/;
assert(!/__[A-Z]+__/.test(html),'unreplaced template token');

// Default: Ohio, everything shown; Ohio replacements hide national locators.
{const {$,visible,d}=load();
 const cards=visible('#cards .resource');
 assert(cards.includes('oh-help-me-grow')&&cards.includes('oh-ocecd'));
 assert(!cards.includes('cdc-find-ei')&&!cards.includes('parent-center'));
 assert.equal(cards.length,data.resources.filter(r=>r.scope!=='MIL'&&!(r.state_replacements||{}).OH).length);
 assert(!cards.includes('family-voices')&&!cards.includes('p2p-usa')&&cards.includes('oh-f2f-p2p'));
 assert.equal(visible('#military-cards .resource').length,data.resources.filter(r=>r.scope==='MIL').length);
 assert.equal($('military-count').textContent,String(data.resources.filter(r=>r.scope==='MIL').length));assert(!$('military-details').open);
 assert.equal(d.querySelectorAll('.glossary dt').length,data.glossary.length);
 assert(!$('county-wrap').hidden);assert($('anchors-title').textContent.includes('Ohio'));
 assert.equal(d.querySelectorAll('#pa-list li').length,51);
 assert(!bad.test($('result-status').textContent));}

// Every state: no Ohio listings outside Ohio, a named rights agency, clean text and correction links.
for(const [code,name] of Object.entries(data.states)){
 const {$,d,visible}=load('?state='+code);
 assert.equal($('state').value,code,code);
 const cards=visible('#cards .resource');
 if(code!=='OH'){
  assert(cards.every(id=>!id.startsWith('oh-')),code);
  assert(cards.includes('cdc-find-ei')&&cards.includes('parent-center'),code);
  assert($('county-wrap').hidden,code);
  assert($('anchor-list').textContent.includes(data.protection_advocacy[code].name),code);
 }
 assert($('anchors-title').textContent.endsWith(name),code);
 assert(!bad.test($('anchors').textContent+$('result-status').textContent),code);
 assert($('back-guide').getAttribute('href')==='./?state='+code,code);
 const report=d.querySelector('a.report').getAttribute('href');
 assert(report.startsWith('mailto:travis@vethomeguard.org?subject=')&&decodeURIComponent(report).includes('('+code+')'),code);
}

// Stage and need filters, deep links and URL state.
{const {w,$,d,visible}=load('?state=TX&stage=school&need=autism');
 assert.equal(d.querySelector('.stage[aria-pressed=true]').dataset.stage,'school');
 assert.deepEqual(visible('#cards .resource').sort(),['autism-society','parent-center']);
 assert(visible('#military-cards .resource').includes('mil-acd'));
 assert(!visible('#military-cards .resource').includes('va-champva'));
 d.querySelector('.stage[data-stage=all]').click();
 assert(w.location.search.includes('need=autism')&&!w.location.search.includes('stage='));
 d.querySelector('input[value=autism]').checked=false;d.querySelector('input[value=autism]').dispatchEvent(new w.Event('change'));
 assert.equal(w.location.search,'?state=TX');}
{const {visible}=load('?state=OH&need=adhd');const cards=visible('#cards .resource');
 assert(cards.includes('chadd-nrc')&&cards.includes('oh-ohiorise')&&!cards.includes('autism-society')&&!cards.includes('oh-autism-scholarship'));}
{const {$,visible}=load('?state=OH&stage=rights&need=physical');
 assert(visible('#cards .resource').length>0&&$('empty').hidden);}

// Ohio counties: pilot boards use their published intake phone; others use the directory and state line.
{const {$,set,w}=load('?state=OH&county=Morrow');
 assert($('county-result').textContent.includes('419-947-1159')&&$('county-result').textContent.includes('Morrow County Board of DD'));
 assert($('cvso-link').getAttribute('href')==='./?state=OH&county=Morrow');
 set('county','Adams');assert($('county-result').textContent.includes('800-617-6733'));assert(w.location.search.includes('county=Adams'));
 set('state','PA');assert.equal($('county').value,'');assert.equal($('county-result').textContent,'');assert(!w.location.search.includes('county'));}
{const {$}=load('?state=OH&county=Atlantis');assert.equal($('county').value,'');}
{const {w,$}=load('?state=ZZ&stage=bogus&need=bogus');assert.equal($('state').value,'OH');$('print').click();assert(w.printed);
 assert.equal(w.localStorage.length+w.sessionStorage.length,0);}

// Stage-aware first calls, need matches sorted first, and print context.
{const {$,d,visible}=load('?state=OH&stage=transition');
 const a=$('anchor-list').textContent;assert(!a.includes('Under age 3')&&a.includes('OCECD')&&a.includes('Disability Rights Ohio'));
 const cards=visible('#cards .resource');assert(cards.includes('oh-sdm-toolkit')&&cards.includes('sdm-center')&&cards.includes('oh-ood-preets'));
 assert($('print-context').textContent.includes('Teens heading into adulthood'));}
{const {$,d,visible}=load('?state=OH&need=autism');
 const cards=visible('#cards .resource');const first=d.getElementById('r-'+cards[0]);
 assert(first.classList.contains('match')&&first.dataset.needs.includes('autism'),cards[0]);
 assert($('needs-box').open);assert(/made for autism are at the top/.test($('result-status').textContent));}
{const {$}=load('?state=OH&need=learning');assert(/None are only for learning/.test($('result-status').textContent));}
{const {$,d}=load('?state=OH');const btn=d.querySelector('.stage[data-stage=early]');
 assert.equal(btn.getAttribute('aria-labelledby'),'st-early');assert.equal(d.getElementById('st-early').textContent,'Birth to age 3');}
{const {w,$}=load('?state=PA#military');assert($('military-details').open);}
console.log('PASS family guide: 51 state entries, Ohio replacements, stage/need filters, county board routes, correction links, stage-aware first calls, need ordering, military toggle, glossary and no storage.');
