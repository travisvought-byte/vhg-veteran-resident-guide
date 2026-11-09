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
{const {$,visible}=load('?state=OH&need=learning');assert.equal(visible('#cards .resource')[0],'lda');assert(/made for learning/.test($('result-status').textContent));}
// Every state's first calls name its own early intervention program; parent centers are named where one statewide center is listed.
for(const code of Object.keys(data.states)){const {$}=load('?state='+code);const a=$('anchor-list').textContent;
 assert(a.includes(data.early_intervention[code].phone),code);
 if(code==='OH')assert(a.includes('OCECD'));else if(data.parent_centers[code])assert(a.includes(data.parent_centers[code].name),code);else assert(a.includes('parent centers (more than one serves the state)'),code);
 assert.equal($('ohio-crisis').hidden,code!=='OH',code);}
{const {$}=load('?state=TX&stage=early');const a=$('anchor-list').textContent;assert(a.includes('Early Childhood Intervention (ECI)')&&!a.includes('parent center'));}
{const {$,d}=load('?state=OH');const btn=d.querySelector('.stage[data-stage=early]');
 assert.equal(btn.getAttribute('aria-labelledby'),'st-early');assert.equal(d.getElementById('st-early').textContent,'Birth to age 3');}
// Only California and New York still fall back to the national parent center map.
assert.deepEqual(Object.keys(data.states).filter(c=>c!=='OH'&&!data.parent_centers[c]).sort(),['CA','NY']);
{const {d,visible}=load('?state=OH&stage=concern&need=autism');assert(visible('#cards .resource').includes('oh-hospital-eval'));
 const card=d.getElementById('r-oh-hospital-eval');assert.equal(card.querySelectorAll('.locations li').length,5);assert.equal(card.querySelectorAll('.locations a[href^="tel:"]').length,5);assert(!card.querySelector('.visit'));}
{const {visible}=load('?state=PA&stage=concern');assert(!visible('#cards .resource').includes('oh-hospital-eval'));}
{const {visible}=load('?state=OH&need=adhd');const cards=visible('#cards .resource');assert(cards.indexOf('oh-chadd')>-1&&cards.indexOf('oh-chadd')<cards.indexOf('oh-medicaid'));}
{const {w,$}=load('?state=PA#military');assert($('military-details').open);}

// Verified Ohio contacts: one Disability Rights Ohio number, Ohio F2F's currently published line, honest MRSS hours.
{const {$,d}=load('?state=OH');
 assert(!html.includes('844-644-6323'),'retired Ohio F2F 844 number');
 assert($('anchor-list').textContent.includes('513-803-5557'));
 assert(d.getElementById('r-oh-sdm-toolkit').textContent.includes('800-282-9181')&&!html.includes('614-466-7264'));
 assert(/8 a\.m\. to 8 p\.m\./.test($('ohio-crisis').textContent)&&/next day/.test($('ohio-crisis').textContent));
 assert(/8 a\.m\. to 8 p\.m\./.test(d.getElementById('r-oh-mrss').textContent));}

// Spanish: the top of the page switches, listings stay English with a note, the choice rides in the URL and switches back.
{const {w,$,d}=load('?state=OH&county=Morrow&stage=early&need=autism&lang=es');
 const top=d.querySelector('h1');assert.equal(top.getAttribute('lang'),'es');assert(top.textContent.startsWith('Ayuda para familias'));
 assert($('urgent-help').textContent.includes('marque 2')&&$('ohio-crisis').textContent.includes('MRSS'));
 assert.equal($('anchors-title').textContent,'Sus primeras llamadas en Ohio');
 const a=$('anchor-list').textContent;assert(a.includes('Menores de 3 años')&&a.includes('Derechos de las personas con discapacidad'));
 assert(!/Under age 3|Disability rights and legal help/.test(a));
 assert($('county-result').textContent.includes('Condado de Morrow')&&$('county-result').textContent.includes('419-947-1159'));
 const s=$('result-status').textContent;assert(s.startsWith('Mostrando ')&&s.includes('en el condado de Morrow, Ohio')&&s.includes('«Desde el nacimiento hasta los 3 años»')&&s.includes('autismo'),s);
 assert.equal(d.getElementById('st-early').textContent,'Desde el nacimiento hasta los 3 años');
 assert.equal(d.querySelector('[data-i18n-need=adhd]').textContent,'TDAH');
 assert(d.querySelector('input[value=autism]').checked,'need checkbox survives translation');
 assert(!$('es-note').hidden&&$('es-note').textContent.includes('inglés'));
 assert.equal($('lang-toggle').textContent,'English');
 assert(!bad.test($('finder').textContent+$('urgent-help').textContent+d.querySelector('header').textContent));
 d.querySelector('.stage[data-stage=school]').click();assert(w.location.search.includes('lang=es')&&w.location.search.includes('stage=school'));
 $('lang-toggle').click();
 assert.equal(d.querySelector('h1').textContent,'Help for families raising a child with a disability');assert(!d.querySelector('h1').hasAttribute('lang'));
 assert.equal($('anchors-title').textContent,'Your first calls in Ohio');assert($('es-note').hidden);assert(!w.location.search.includes('lang='));
 assert($('result-status').textContent.startsWith('Showing '));assert(d.querySelector('input[value=autism]').checked);
 $('lang-toggle').click();assert(w.location.search.includes('lang=es'));assert.equal($('lang-toggle').textContent,'English');}
for(const code of Object.keys(data.states)){const {$,d}=load('?lang=es&state='+code);
 assert($('anchors-title').textContent.startsWith('Sus primeras llamadas en'),code);
 const a=$('anchor-list');[...a.querySelectorAll('strong')].forEach(s=>assert(!/^(Under|Age|Parent|County|Health|Talk|Disability)/.test(s.textContent),code+s.textContent));
 assert(!bad.test(a.textContent+$('result-status').textContent),code);}

// Quick start: two age choices ahead of the filters; the written-request letter appears for school-age evaluation.
{const {w,$,d}=load('?state=OH');
 const q=[...d.querySelectorAll('.quick-btn')];assert.equal(q.length,2);
 assert(d.querySelector('.quick').compareDocumentPosition(d.querySelector('.stages'))&w.Node.DOCUMENT_POSITION_FOLLOWING,'quick start comes before the stage cards');
 assert($('letter').hidden);
 q[0].click();assert.equal(q[0].getAttribute('aria-pressed'),'true');assert(w.location.search.includes('stage=early'));
 assert($('anchor-list').textContent.includes('800-755-4769'));assert($('letter').hidden);
 q[1].click();assert.equal(q[1].getAttribute('aria-pressed'),'true');assert.equal(q[0].getAttribute('aria-pressed'),'false');
 assert(w.location.search.includes('stage=school'));assert(!$('letter').hidden);
 assert($('anchor-list').textContent.includes('ask your public school district in writing'));
 const v=$('letter-text').value;assert(v.startsWith('Dear Director of Special Education')&&v.includes('[briefly describe what you')&&v.includes('request an evaluation'));
 assert(!/undefined|null/.test(v));
 d.querySelector('.stage[data-stage=transition]').click();assert($('letter').hidden);
 d.querySelector('.stage[data-stage=concern]').click();assert(!$('letter').hidden);
 $('letter-copy').click();}
{const {$,d}=load('?state=TX&stage=school&lang=es');
 assert(!$('letter').hidden);assert($('letter-text').value.startsWith('Estimado/a director/a'));
 assert.equal(d.querySelector('.quick-btn[data-quick=early]').textContent,'Mi hijo tiene menos de 3 años');
 assert.equal(d.querySelector('.quick-btn[data-quick=school]').getAttribute('aria-pressed'),'true');
 const box=$('letter-text');box.value='edited';box.dispatchEvent(new d.defaultView.Event('input'));
 $('lang-toggle').click();assert.equal(box.value,'edited','a parent\'s edits survive a language switch');}
{const {$}=load('?state=OH');assert($('partner').textContent.startsWith("In partnership with Deb's Yoga"));assert(!/autis/i.test($('partner').textContent),'partner credit names no diagnosis');}
console.log('PASS family guide: 51 state entries, Ohio replacements, stage/need filters, county board routes, correction links, stage-aware first calls, need ordering, military toggle, glossary, each state early intervention and parent center, Ohio crisis line, verified Ohio first calls, Ohio hospital evaluation centers, CHADD of Ohio, quick start, evaluation request letter, Spanish top of page in all 51 jurisdictions and no storage.');
