const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL=u=>/^https?:\/\//.test(u||'')?u:'';
const labels={official_source_reviewed:'Official source reviewed',official_search_extract_only:'Search excerpt only — needs verification',needs_recheck:'Needs confirmation',imported_unverified:'Not re-reviewed — needs verification'};
const types={benefits_and_funding:'Benefits and care costs',care_facilities:'Care facilities',child_development_autism:'Child development and autism',dd_intake_service_coordination:'Developmental disability support',education_special_education:'Special education',employment_transition:'Employment and transition',equipment_home_accessibility:'Equipment and home accessibility',general_navigation:'Finding help and advocacy',help_at_home:'Help at home',veteran_services:'Veteran services'};
let DATA=[],COUNTIES=[],STATE='OH',priority=[],routes={},seniorTopics={},routeNames={},route='priority';
const regionalIDs=role=>DATA.filter(x=>x.regional_role===role).map(x=>x.program_id);
const officeLegacyIds=new Set(['morrow-vso','knox-vso','marion-vso','delaware-vso']);
const tel=p=>{const parts=p.split(/\s+ext\.?\s*/i);return 'tel:'+parts[0].replace(/[^+0-9]/g,'')+(parts[1]?';ext='+parts[1].replace(/\D/g,''):'')};
function localityLabel(value){const c=typeof value==='string'?COUNTIES.find(c=>c.county===value):value;return c?(['independent_city','statewide','borough','census_area','city_and_county'].includes(c.county_type)?c.county:c.county+(c.county_type==='parish'?' Parish':' County')):(value||'')}
const phoneLink=p=>p?'<a class="phone" href="'+esc(tel(p))+'">'+esc(p)+'</a>':'';
const sourceURL=c=>c.source_url+(c.source_page?'#page='+c.source_page:'');
function officeCard(...args){return EDITIONS[STATE].officeCard(...args)}
function regionalContact(x,title,help){return `<section class="regional-contact"><h3>${esc(title)}</h3><p class="small">${esc(x.organization)}</p><p>${phoneLink(x.public_contact.phone)}</p><p class="small">${esc(help)}</p><p class="meta"><a href="${esc(x.official_url)}" target="_blank" rel="noopener">Contact source · region ${esc(x.region_id)}</a></p></section>`}
function renderCounty(...args){return EDITIONS[STATE].renderCounty(...args)}

function renderOfficeList(...args){return EDITIONS[STATE].renderOfficeList(...args)}
const national=a=>['statewide','national','federal',...EDITIONS[STATE].statewideNames].includes(a.toLowerCase());
function matchesCounty(x,county){return !county||(x.service_area||[]).some(a=>a.toLowerCase()===county.toLowerCase()||national(a))}
function audience(...args){return EDITIONS[STATE].audience(...args)}
function renderAccessibility(...args){return EDITIONS[STATE].renderAccessibility(...args)}

function seniorTopicIDs(topic){const ids=seniorTopics[topic]||routes.seniors;return [...ids,...(['daily','costs','accessibility','memory'].includes(topic)?regionalIDs('aging_agency'):[]),...(topic==='rights'?regionalIDs('ombudsman'):[])]}
function renderSeniorGuide(...args){return EDITIONS[STATE].renderSeniorGuide(...args)}

function shareURL(){const u=new URL(location.href);u.pathname=u.pathname.replace(/[^/]*$/, STATE_PAGES[STATE]);u.search='';u.hash='';if($('county').value)u.searchParams.set('county',$('county').value);if(route!=='priority')u.searchParams.set('view',route);if(route==='seniors'&&$('senior-topic').value)u.searchParams.set('topic',$('senior-topic').value);if($('search').value.trim())u.searchParams.set('q',$('search').value.trim());if($('need').value)u.searchParams.set('type',$('need').value);if($('status').value)u.searchParams.set('status',$('status').value);return u}
const FEEDBACK_EMAIL='travis@vethomeguard.org',FEEDBACK_ASK=['','What needs fixing? (wrong phone, office moved, program ended, or something else)','','Your role, optional (facility staff, family member, agency staff):','','Please share public listing information only. Do not include resident names or health details.'];
function reportHref(subject,lines){return 'mailto:'+FEEDBACK_EMAIL+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(lines.join('\n'))}
function reportLink(x,county){return '<a class="report" href="'+esc(reportHref('Guide correction: '+STATE+' · '+x.name,['Listing: '+x.name,'Record: '+STATE+' · '+x.program_id,'County viewed: '+(county||'none'),...FEEDBACK_ASK]))+'">Report a problem with this listing</a>'}
function countyReportLink(county){return '<p class="report-row"><a class="report" href="'+esc(reportHref('Guide correction: '+STATE+' · '+localityLabel(county)+' contacts',[({independent_city:'Independent city: ',parish:'Parish: ',borough:'Borough: ',census_area:'Census area: ',city_and_county:'City and borough: '}[COUNTIES.find(c=>c.county===county)?.county_type]||'County: ')+county+' ('+STATE+')','Section: county contacts',...FEEDBACK_ASK]))+'">Report a problem with these county contacts</a></p>'}
function evidenceLinks(x){return (x.source_evidence||[]).map(e=>{const u=safeURL(e.url);return u?'<p><a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(e.title||'Official evidence')+'</a>'+ (e.scope?'<br>'+esc(e.scope):'')+'</p>':''}).join('')}
function render(){const q=$('search').value.toLowerCase().trim(),county=$('county').value,need=$('need').value,status=$('status').value;
const rows=DATA.filter(x=>!officeLegacyIds.has(x.program_id)&&(route==='all'||(route==='priority'?priority:routes[route]).includes(x.program_id))&&matchesCounty(x,county)&&(route!=='seniors'||!$('senior-topic').value||seniorTopicIDs($('senior-topic').value).includes(x.program_id))&&(!q||[x.name,x.description,x.next_step,x.organization,...(x.needs_supported||[])].join(' ').replaceAll('_',' ').toLowerCase().includes(q))&&(!need||(x.needs_supported||[]).includes(need))&&(!status||x.verification.record_status===status)).sort((a,b)=>{const rank=x=>priority.includes(x.program_id)?priority.indexOf(x.program_id):999;return rank(a)-rank(b)||a.name.localeCompare(b.name)});
$('count').textContent=routeNames[route]+' · '+rows.length+' resources'+(county?' for '+localityLabel(county):' across listed service areas');
$('results').innerHTML=rows.map(x=>{const c=x.public_contact||{},v=x.verification||{},u=safeURL(x.official_url),recommended=priority.includes(x.program_id),constraints=(x.constraints||[]).filter(s=>!/(Claude|schema v|intentionally null|fetch failed|indexed extract)/i.test(s)),who=audience(x);return `<article id="resource-${esc(x.program_id)}" class="${recommended?'recommended':''}">${recommended?'<div class="recommended-label">'+(v.record_status==='official_source_reviewed'?'Useful starting point':'Potential starting point — confirm with provider')+'</div>':''}<h2>${esc(x.name)}</h2><div class="meta">${esc((x.service_area||[]).map(a=>national(a)?'All '+EDITIONS[STATE].name+(STATE==='VA'?' counties and independent cities':' counties'):a).filter((a,i,s)=>s.indexOf(a)===i).join(' · ')||'Ask the provider about service area')}${x.organization?'<br>'+esc(x.organization):''}</div><p>${esc(x.description||'Use this provider’s resource information to explore available help.')}</p>${who?'<p class="suitable"><strong>Who to ask about:</strong> '+esc(who)+'</p>':''}<p class="step"><strong>Your next step</strong><br>${esc(x.next_step||'Ask the provider what help is available and how to get started.')}</p>${constraints.length?'<details class="small"><summary>Limits and conditions</summary><p>'+esc(constraints.join(' '))+'</p></details>':''}<div class="links">${c.phone?phoneLink(c.phone):''}${u?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">Resource website ↗</a>':''}${/discharge upgrade|upgrade or correct a discharge/i.test((x.name||'')+' '+(x.description||''))?'<a href="bad-paper/">Bad paper guide: VA options, upgrade boards, free help</a>':''}</div><p class="source-status ${v.record_status==='official_source_reviewed'?'':'notice'}"><strong>${esc(labels[v.record_status]||'Needs verification')}</strong>${v.record_status==='official_source_reviewed'?'':'<br>Full verification is incomplete. Confirm the contact and service details with the provider before relying on this referral.'}</p><details class="source-details"><summary>${esc(labels[v.record_status]||'Source status not recorded')} · ${esc(v.last_reviewed_on||'Date not recorded')}</summary><p>Source review is a check of published information, not direct confirmation of service availability. Ask the provider about eligibility and the current process.</p>${evidenceLinks(x)}</details>${reportLink(x,county)}</article>`}).join('')||'<div class="empty">No matches in this view. Try Browse all resources, clear the search or choose a different resource type.</div>';
renderCounty();renderAccessibility();renderSeniorGuide();renderHelper();if(county&&!$('county-panel').hidden&&COUNTIES.some(c=>c.county===county))$('county-panel').innerHTML+=countyReportLink(county);document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));$('share-status').textContent='';history.replaceState(null,'',shareURL())}

const EDITIONS=window.VHG_EDITIONS=window.VHG_EDITIONS||{};
const EDITION_FILES={"OH": "assets/editions/oh.js?v=8cd918de57", "PA": "assets/editions/pa.js?v=3d54266455", "NY": "assets/editions/ny.js?v=4d13f5cfeb", "MI": "assets/editions/mi.js?v=81d28b6b49", "KY": "assets/editions/ky.js?v=cb4a0d852e", "UT": "assets/editions/ut.js?v=715fdddd12", "IN": "assets/editions/in.js?v=dcbe942c21", "WV": "assets/editions/wv.js?v=2771748836", "TX": "assets/editions/tx.js?v=c019240944", "FL": "assets/editions/fl.js?v=c966b914d6", "CA": "assets/editions/ca.js?v=452d3ebe80", "VA": "assets/editions/va.js?v=673e67aee3", "NC": "assets/editions/nc.js?v=680a875a65", "GA": "assets/editions/ga.js?v=ca2a33e068", "AZ": "assets/editions/az.js?v=d8e4a35ec8", "WA": "assets/editions/wa.js?v=f45cbbf31c", "TN": "assets/editions/tn.js?v=6b187076db", "SC": "assets/editions/sc.js?v=0b1f719054", "IL": "assets/editions/il.js?v=eba7d92e2c", "MO": "assets/editions/mo.js?v=6647da18fb", "CO": "assets/editions/co.js?v=a90c97a4c0", "AL": "assets/editions/al.js?v=a1580e51df", "MD": "assets/editions/md.js?v=1b17406f5a", "WI": "assets/editions/wi.js?v=058073c872", "MN": "assets/editions/mn.js?v=dfabadb709", "OK": "assets/editions/ok.js?v=0ed1785f2a", "NJ": "assets/editions/nj.js?v=b4c0f67b1a", "OR": "assets/editions/or.js?v=45f61497c1", "LA": "assets/editions/la.js?v=933899d624", "NV": "assets/editions/nv.js?v=c25509cb50", "KS": "assets/editions/ks.js?v=6900e04125", "NE": "assets/editions/ne.js?v=d5091696d1", "NM": "assets/editions/nm.js?v=d5bf60886a", "MS": "assets/editions/ms.js?v=4415ddb758", "ID": "assets/editions/id.js?v=e39d8bddda", "SD": "assets/editions/sd.js?v=c498f5e66a", "NH": "assets/editions/nh.js?v=e98b9a4c78", "ME": "assets/editions/me.js?v=5e5464d251", "HI": "assets/editions/hi.js?v=37336048b0", "DE": "assets/editions/de.js?v=645dff7081", "RI": "assets/editions/ri.js?v=c93d785828", "VT": "assets/editions/vt.js?v=a3009f3561", "WY": "assets/editions/wy.js?v=46d13e290e", "DC": "assets/editions/dc.js?v=f32c242cf4", "MT": "assets/editions/mt.js?v=80db5a7b85", "AK": "assets/editions/ak.js?v=438bcb21f5", "ND": "assets/editions/nd.js?v=35b85ead2f", "IA": "assets/editions/ia.js?v=cbe57538c0", "CT": "assets/editions/ct.js?v=b1b0f965f1", "MA": "assets/editions/ma.js?v=dadf2b3a04", "AR": "assets/editions/ar.js?v=a2d25f9458"};
const STATE_PAGES={"OH": "", "PA": "pa.html", "NY": "ny.html", "MI": "mi.html", "KY": "ky.html", "UT": "ut.html", "IN": "in.html", "WV": "wv.html", "TX": "tx.html", "FL": "fl.html", "CA": "ca.html", "VA": "va.html", "NC": "nc.html", "GA": "ga.html", "AZ": "az.html", "WA": "wa.html", "TN": "tn.html", "SC": "sc.html", "IL": "il.html", "MO": "mo.html", "CO": "co.html", "AL": "al.html", "MD": "md.html", "WI": "wi.html", "MN": "mn.html", "OK": "ok.html", "NJ": "nj.html", "OR": "or.html", "LA": "la.html", "NV": "nv.html", "KS": "ks.html", "NE": "ne.html", "NM": "nm.html", "MS": "ms.html", "ID": "id.html", "SD": "sd.html", "NH": "nh.html", "ME": "me.html", "HI": "hi.html", "DE": "de.html", "RI": "ri.html", "VT": "vt.html", "WY": "wy.html", "DC": "dc.html", "MT": "mt.html", "AK": "ak.html", "ND": "nd.html", "IA": "ia.html", "CT": "ct.html", "MA": "ma.html", "AR": "ar.html"};
let helperActive=false,helperShowingResults=false,helperRoute='benefits';
function agingContactsHTML(...args){return EDITIONS[STATE].agingContactsHTML(...args)}
function countyContactsHTML(...args){return EDITIONS[STATE].countyContactsHTML(...args)}
function veteransContactsHTML(c){return EDITIONS[STATE].veteransContactsHTML(c)}
function setState(state,initial=false){
 if(!Object.hasOwn(EDITION_FILES,state))state='OH';
 if(!Object.hasOwn(EDITIONS,state)){
  const previous=STATE,name=$('edition-state').querySelector('option[value="'+state+'"]')?.textContent||state;
  $('edition-state').value=state;$('edition-status').textContent='Loading '+name+'…';
  loadEdition(state).then(()=>{$('edition-status').textContent='';setState(state,initial)},()=>{$('edition-state').value=previous;$('edition-status').textContent=name+' could not load. Check your connection and try again.'});
  return;
 }
 STATE=state;const config=EDITIONS[state];DATA=config.data;COUNTIES=config.counties;
 ({priority,routes,seniorTopics,routeNames}=config.configure());
 // National records every state shares join the state's own counseling and housing lists, whatever order the state set them in.
 Object.entries({crisis:['va-vet-centers','va-vet-center-mst','va-women-veterans-call-center'],housing:['va-home-loans']}).forEach(([key,ids])=>{const own=routes[key]||[];routes[key]=[...own,...ids.filter(id=>!own.includes(id)&&DATA.some(x=>x.program_id===id))]});
 if(routes.crisis.length)routeNames.crisis='Counseling and mental health';
 routeNames.housing='Housing, home loans and homelessness';
 if(!Object.hasOwn(routeNames,route))route='priority';
 $('edition-state').value=state;$('county').innerHTML='<option value="">Choose a county or city…</option>';$('county').value='';
 COUNTIES.forEach(c=>{const o=document.createElement('option');o.value=c.county;o.textContent=localityLabel(c);$('county').append(o)});
 // A starter edition has one statewide entry. Choose it and put the one-choice picker away, so its contacts show without an extra step.
 const single=COUNTIES.length===1;
 if(single)$('county').value=COUNTIES[0].county;
 $('county').parentElement.hidden=single;$('county-start').classList.toggle('single-area',single);document.querySelector('.office-directory').hidden=single;
 $('need').innerHTML='<option value="">All resource types</option>';
 [...new Set(DATA.flatMap(x=>x.needs_supported||[]))].sort().forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent=types[n]||n.replaceAll('_',' ');$('need').append(o)});
 ['search','need','status','office-search'].forEach(id=>$(id).value='');
 for(const [id,markup] of Object.entries(config.markup)){const wrapper=document.createElement('div');wrapper.innerHTML=markup;const replacement=wrapper.firstElementChild;$(id).replaceWith(replacement)}
 // Keep state-specific instructions available without making the first screen an explanation of the data model.
 const pending=DATA.filter(x=>x.verification.record_status!=='official_source_reviewed').length;
 $('coverage-detail').innerHTML='<p>'+esc(config.name)+(single&&(config.statewideNames||[]).length?': statewide referral routes. Local offices are not listed yet.':single?': referral routes for '+localityLabel(COUNTIES[0])+'. Local service coverage is still growing.':': referral routes for '+COUNTIES.length+(state==='VA'?' counties and independent cities.':state==='LA'?' parishes.':' counties.')+' Local service coverage is still growing.')+'</p><p>'+pending+' resource records need further source checks. Check the status on each listing and confirm availability with the agency.</p>';
 if(config.coverageNote)$('coverage-detail').innerHTML+='<p>'+esc(config.coverageNote)+'</p>';
 document.querySelector('label[for="county"]').textContent=(state==='VA'?'County or independent city in ':state==='LA'?'Parish in ':'County in ')+config.name;
 $('aid-open').hidden=state!=='OH';document.querySelectorAll('.ohio-only').forEach(e=>{e.hidden=state!=='OH'});document.querySelector('.office-directory summary').textContent='Browse '+config.name+(state==='VA'?' county and city contacts':state==='LA'?' parish contacts':' county contacts');
 $('office-search').placeholder='Search '+config.name+(state==='VA'?' counties or independent cities':state==='LA'?' parishes':' counties');
 // Each state's own heading and opening (data/landing/states.json); Ohio is the site root, so it shows the home page's.
 const land=config.landing||{};document.title=land.title||config.name+' Veteran Resource Guide | Veteran Home Guardians';
 if(land.h1&&$('guide-title')){$('guide-title').innerHTML=land.h1;$('guide-intro').textContent=land.intro;$('guide-eyebrow').textContent='Veteran Home Guardians · '+land.eyebrow}
 document.querySelectorAll('#who-start [data-states]').forEach(a=>{a.closest('li').hidden=!a.dataset.states.split(' ').includes(state)});
 // Search engines get one address per state: its own page, with Ohio at the root.
 const home=new URL(STATE_PAGES[state]||'./',document.querySelector('link[rel=canonical]')?.href||location.href).href;
 document.querySelector('link[rel=canonical]')?.setAttribute('href',home);document.querySelector('meta[property="og:url"]')?.setAttribute('content',home);
 // The footer date comes from the records, so it cannot go stale: the newest review of this state's veterans office contacts.
 // (Program records are left out because federal ones are shared by every state and would date them all alike.)
 const reviewed=COUNTIES.map(c=>c.reviewed_on).filter(v=>/^\d{4}-\d{2}-\d{2}$/.test(v||'')).sort().at(-1);
 $('edition-updated').textContent=reviewed?'Most recent review of '+config.name+' veterans office contacts: '+new Date(reviewed+'T12:00:00').toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})+'.':'';
 // The bad-paper card opens that guide on this state's veterans agency, named here from the state's own record.
 document.querySelectorAll('[data-bad-paper]').forEach(a=>{a.href='bad-paper/?state='+state;const r=DATA.find(x=>x.program_id===(state==='OH'?'ohio-dvs-fallback':state.toLowerCase()+'-claims')),s=a.querySelector('[data-bad-paper-agency]');if(s)s.textContent=r&&r.organization?'. In '+config.name+': '+r.organization+'.':''});
 document.querySelectorAll('[data-advocacy-route]').forEach(a=>a.href='disability-advocacy.html?state='+state);document.querySelectorAll('[data-family-route]').forEach(a=>a.href=(state==='OH'?'https://www.ohiomom.org/family-guide.html':'family-guide.html')+'?state='+state);
 document.querySelectorAll('a[href^="share"]').forEach(a=>a.href=config.sharePage);
 document.querySelectorAll('.footer-links a').forEach(a=>{if(a.textContent==='County contact data')a.href=config.files.offices;if(a.textContent==='Resource data')a.href=config.files.resources});
 document.querySelectorAll('#urgent-help a[href^="?view="],#urgent-help a[data-view]').forEach(a=>{a.dataset.view??=new URL(a.href,location.href).searchParams.get('view');const u=new URL(STATE_PAGES[state]||'./',location.href);u.searchParams.set('view',a.dataset.view);a.href=u.href});
 bindStateControls();
 document.querySelectorAll('.state-tiles a,.usmap a').forEach(a=>a.dataset.state===state?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current'));
 document.documentElement.dataset.edition=state;
 if(!initial){render();renderOfficeList()}
}
// Each state's records live in their own file so a phone downloads only the state in use.
const editionLoads={};
function loadEdition(state){
 if(Object.hasOwn(EDITIONS,state))return Promise.resolve();
 if(!editionLoads[state])editionLoads[state]=new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=EDITION_FILES[state];s.onload=()=>Object.hasOwn(EDITIONS,state)?resolve():reject(new Error('Edition did not register'));s.onerror=reject;document.head.append(s)}).catch(e=>{delete editionLoads[state];throw e});
 return editionLoads[state];
}
function bindStateControls(){
 $('senior-topic').addEventListener('change',render);
 ['access-veteran','access-home','access-waiver'].forEach(id=>$(id).addEventListener('change',renderAccessibility));
 $('print-handoff').onclick=()=>{if(!$('county').value){$('print-handoff-status').textContent='Choose a county first.';$('county').focus();return}clearPrintMode();document.body.classList.add('print-handoff');window.print()};
 $('print-accessibility').onclick=()=>{accessPrintStates=Array.from(document.querySelectorAll('#accessibility-guide details'),el=>({el,open:el.open}));accessPrintStates.forEach(({el})=>el.open=true);clearPrintMode();document.body.classList.add('print-accessibility');window.print()};
}
function clearPrintMode(){document.body.classList.remove('print-helper','print-handoff','print-accessibility')}
let accessPrintStates=[];
function helperContacts(county,need,person){
 const c=COUNTIES.find(c=>c.county===county),aging=DATA.filter(x=>x.regional_role==='aging_agency'&&x.service_area.includes(county));
 const omb=DATA.filter(x=>x.regional_role==='ombudsman'&&x.service_area.includes(county));
 const card=x=>'<article><h3>'+esc(x.name)+'</h3>'+(x.public_contact?.phone?'<p>'+phoneLink(x.public_contact.phone)+'</p>':'')+'<p>'+esc(x.next_step)+'</p>'+(['IN','WV','TX','VA'].includes(STATE)&&x.regional_role?'<p class="small">'+esc((x.constraints||[]).join(' '))+'</p>':'')+'<a href="'+esc(safeURL(x.official_url))+'" target="_blank" rel="noopener">Contact information</a><p class="meta">'+esc(labels[x.verification.record_status])+' · '+esc(x.verification.last_reviewed_on)+'</p></article>';
 if(need==='crisis')return '<article><h3>Immediate support</h3><p>Call '+phoneLink('988')+'. Veterans: press 1. For immediate danger, call '+phoneLink('911')+'.</p></article>';
 if(need==='housing'&&person!=='other')return card(DATA.find(x=>x.program_id==='va-housing-help'));
 if(need==='rights'){
  if(STATE==='WV')return card(DATA.find(x=>x.program_id==='wv-ombudsman'))+'<p>Give the facility name and county and ask for the current regional advocate. Doddridge is missing from the published regional list; Kanawha is split without a published boundary.</p>';
  if(STATE==='IN'&&['Randolph','Boone','Marion','Bartholomew','Brown','Decatur','Jackson','Jennings','Monroe','Owen','Clark','Floyd','Harrison','Scott'].includes(county))return card(DATA.find(x=>x.program_id==='in-ombudsman'))+'<p>Give the facility’s exact location. The local directory has conflicting entries or subcounty assignments; ask the state office to identify the correct ombudsman.</p>';
  const contacts=omb.length?omb:DATA.filter(x=>routes.rights.includes(x.program_id)&&/ombudsman/i.test(x.name)&&matchesCounty(x,county));
  return contacts.slice(0,2).map(card).join('');
 }
 if(need==='daily'||person==='other')return aging.map(card).join('');
 return (c?officeCard(c):'')+(person==='unknown'?aging.map(card).join(''):'');
}
function renderHelper(){
 $('helper-guide').hidden=!helperActive;$('helper-open').setAttribute('aria-pressed',String(helperActive));
 $('directory').hidden=helperActive;
 $('results').hidden=helperActive&&!helperShowingResults;document.querySelector('.count-row').hidden=helperActive&&!helperShowingResults;
 if(!helperActive)return;
 $('county-panel').hidden=true;
 if(!helperShowingResults){['seniors-guide','community-guide','accessibility-guide'].forEach(id=>$(id).hidden=true)}
 const county=$('county').value,need=$('helper-need').value,person=$('helper-person').value;
 const mapped={benefits:person==='survivor'?'survivors':person==='other'?'seniors':'benefits',daily:['other','survivor'].includes(person)?'seniors':'care',housing:'housing',accessibility:'accessibility',rights:'rights',crisis:'crisis'};
 helperRoute=mapped[need];
 const text={benefits:'Ask for a benefits and care-cost screening.',daily:'Ask for an assessment and caregiver support.',housing:'Ask about housing assistance and the next intake step.',accessibility:'Ask the discharge planner or case manager to coordinate the assessment, home access and timing before discharge.',rights:'Ask the ombudsman about the resident’s concern and preferences.',crisis:'Connect with urgent support now.'};
 let contacts=helperContacts(county,need,person);
 if(!county&&need!=='crisis'&&!(need==='housing'&&person!=='other'))contacts='<p><a href="#county-start">Choose a county above</a> to see the first local contact.</p>';
 if(person==='other'&&need==='housing')contacts='<article><h3>Local housing assistance</h3><p>Call '+phoneLink('211')+' and ask about housing support in '+esc(county?localityLabel(county)+', '+EDITIONS[STATE].name:EDITIONS[STATE].name)+'.</p></article>';
 if(need==='accessibility'&&person==='survivor')text.accessibility='Ask the discharge planner and local aging agency to coordinate home access. A spouse’s military service alone does not establish eligibility for veteran-only housing adaptations.';
 if(need==='accessibility'&&person==='survivor')contacts=DATA.filter(x=>x.regional_role==='aging_agency'&&county&&x.service_area.includes(county)).map(x=>'<article><h3>'+esc(x.organization)+'</h3><p>'+phoneLink(x.public_contact.phone)+'</p></article>').join('')||'<p>Choose a county for the local aging contact.</p>';
 $('helper-next').innerHTML='<h3>'+esc(EDITIONS[STATE].name)+(county?' · '+esc(localityLabel(county)):'')+'</h3><p><strong>'+esc(text[need])+'</strong></p><div class="contact-grid">'+contacts+'</div><div class="call-script"><strong>What to ask</strong><p>“I’m helping someone who wants support with '+esc($('helper-need').selectedOptions[0].textContent.toLowerCase())+'. What is the intake process, what documents are needed, and can you help if they cannot travel?”</p></div><p>Agree on who will follow up and when. Confirm eligibility and availability directly.</p>';
}
// Copy only on-screen public referrals, selected categories, and follow-up questions.
function helperHandoffText(){
 const county=$('county').value;
 if(!county)return '';
 const tidy=s=>(s||'').replace(/\s+/g,' ').trim();
 const el=$('helper-next');
 const heading=tidy(el.querySelector('h3')?.textContent);
 const step=tidy(el.querySelector('p strong')?.textContent);
 const person=tidy($('helper-person').selectedOptions[0]?.textContent);
 const need=tidy($('helper-need').selectedOptions[0]?.textContent);
 const contacts=[...el.querySelectorAll('.contact-grid article')].map(article=>{
  const title=tidy(article.querySelector('h2,h3')?.textContent)||'Referral contact';
  const details=[...article.querySelectorAll('p')].map(p=>tidy(p.textContent)).filter(Boolean);
  const source=[...article.querySelectorAll('a[href^="https://"]')].find(a=>a.getAttribute('href'));
  return [title,...details,source?'Source: '+source.getAttribute('href'):null].filter(Boolean).join('\n');
 });
 const questions=tidy(el.querySelector('.call-script p')?.textContent);
 const url=new URL(STATE_PAGES[STATE]||'./',location.href);
 url.search='';url.hash='';
 url.searchParams.set('county',county);
 url.searchParams.set('help','1');
 return [
  'Veteran Home Guardians — Referral handoff',
  'Location: '+heading,
  'Helping: '+person,
  'Need: '+need,
  'First step: '+step,
  '',
  'Published starting contacts:',
  contacts.length?contacts.join('\n\n'):'No matching local contact displayed. Ask the relevant statewide agency for current routing.',
  '',
  'What to ask: '+questions,
  'Follow-up: Contact made / date: ________  Documents needed: ________  Who follows up / when: ________',
  'Confirm current intake, eligibility and availability with the agency.',
  'Guide: '+url.href,
  'This handoff contains public referral information only. Keep resident details in your usual private records.'
 ].join('\n');
}
function openHelper(){helperActive=true;helperShowingResults=false;render();$('helper-title').focus({preventScroll:true});$('helper-guide').scrollIntoView({behavior:'smooth'})}
const params=new URLSearchParams(location.search);
// A state's own page (ky.html) opens that state; an old ?state= link still picks the state and is moved to its page.
const HOME_STATE=Object.hasOwn(EDITION_FILES,document.documentElement.dataset.homeState)?document.documentElement.dataset.homeState:'OH';
let initialState=Object.hasOwn(EDITION_FILES,params.get('state'))?params.get('state'):HOME_STATE;
route=params.get('view')||'priority';
function startGuide(){
setState(initialState,true);
const requestedCounty=params.get('county');const matched=COUNTIES.find(c=>c.county===requestedCounty||(c.county_aliases||[]).includes(requestedCounty));if(matched)$('county').value=matched.county;
if(!Object.hasOwn(routeNames,route))route='priority';
$('search').value=params.get('q')||'';if(Object.hasOwn(types,params.get('type')))$('need').value=params.get('type');if(Object.hasOwn(labels,params.get('status')))$('status').value=params.get('status');if(route==='seniors'&&Object.hasOwn(seniorTopics,params.get('topic')))$('senior-topic').value=params.get('topic');
if(($('search').value||$('need').value||$('status').value)&&!['seniors','community'].includes(route))route='all';
helperActive=params.get('help')==='1';
const originalShareURL=shareURL;shareURL=function(){const u=originalShareURL();if(helperActive)u.searchParams.set('help','1');return u};
document.querySelectorAll('[data-route]').forEach(b=>b.onclick=()=>{helperActive=false;route=b.dataset.route;$('senior-topic').value='';['search','need','status'].forEach(id=>$(id).value='');render();if(['seniors','community','accessibility'].includes(route)){const id={seniors:'seniors',community:'community',accessibility:'accessibility'}[route];$(id+'-guide').scrollIntoView({behavior:'smooth'});$(id+'-title').focus({preventScroll:true})}});
['search','need','status'].forEach(id=>$(id).addEventListener('input',()=>{if(!['seniors','community'].includes(route))route='all';render()}));
$('county').addEventListener('change',render);$('office-search').addEventListener('input',renderOfficeList);
$('edition-state').addEventListener('change',()=>setState($('edition-state').value));
$('reset').onclick=()=>{$('senior-topic').value='';['search','need','status'].forEach(id=>$(id).value='');if(!['seniors','community'].includes(route))route='priority';render()};
$('share').onclick=async()=>{try{await navigator.clipboard.writeText(shareURL().href);$('share-status').textContent='Link copied.'}catch{$('share-status').textContent='Copy the page address to share this view.'}};
$('print-results').onclick=()=>{clearPrintMode();window.print()};
// Phones: the header's extra links open from one button (assets/unified.css keeps them all visible on wider screens).
const moreGuides=$('jump-toggle');moreGuides.hidden=false;moreGuides.onclick=()=>{const open=moreGuides.getAttribute('aria-expanded')!=='true';moreGuides.setAttribute('aria-expanded',String(open));moreGuides.textContent=open?'Fewer guides':'More guides'};
// "I'm here as...": open the matching need in place, keeping the county, then bring its results into view.
document.querySelectorAll('#who-start a[data-view]').forEach(a=>a.onclick=ev=>{const view=a.dataset.view,b=document.querySelector('.quick-links [data-route="'+view+'"]');if(!b||!Object.hasOwn(routeNames,view))return;ev.preventDefault();b.click();if(!['seniors','community','accessibility'].includes(view))document.querySelector('.count-row').scrollIntoView({behavior:'smooth'})});
document.querySelectorAll('#who-start a[data-help]').forEach(a=>a.onclick=ev=>{ev.preventDefault();openHelper()});
$('helper-open').onclick=openHelper;$('helper-header').onclick=e=>{e.preventDefault();openHelper()};
['helper-person','helper-need'].forEach(id=>$(id).addEventListener('change',()=>{helperShowingResults=false;$('helper-status').textContent='';render()}));
$('helper-close').onclick=()=>{helperActive=false;helperShowingResults=false;route='priority';render();$('directory').scrollIntoView({behavior:'smooth'})};
$('helper-resources').onclick=()=>{helperShowingResults=true;route=helperRoute;['search','need','status'].forEach(id=>$(id).value='');if(route==='accessibility'){$('access-veteran').value=$('helper-person').value==='veteran'?'yes':$('helper-person').value==='unknown'?'unknown':'no';$('access-home').value='facility'}if(route==='seniors')$('senior-topic').value=$('helper-need').value==='benefits'?'costs':$('helper-need').value==='daily'?'daily':'';render();const target=route==='accessibility'?'accessibility-guide':route==='seniors'?'seniors-guide':'results';$(target).scrollIntoView({behavior:'smooth'})};
$('helper-copy').onclick=async()=>{
 if(!$('county').value){$('helper-status').textContent='Choose a county first.';$('county').focus();return}
 const summary=helperHandoffText();
 try{
  if(!navigator.clipboard?.writeText)throw new Error('Clipboard not available');
  await navigator.clipboard.writeText(summary);
  $('helper-status').textContent='Referral handoff copied. Paste it into your message or care-team note.';
 }catch{
  $('helper-status').textContent='Copy is unavailable in this browser. Use Print this handoff instead.';
 }
};
$('helper-print').onclick=()=>{if(!$('county').value){$('helper-status').textContent='Choose a county first.';$('county').focus();return}$('helper-status').textContent='';clearPrintMode();document.body.classList.add('print-helper');window.print()};
window.addEventListener('afterprint',()=>{clearPrintMode();accessPrintStates.forEach(({el,open})=>el.open=open);accessPrintStates=[]});
render();renderOfficeList();
}
if(Object.hasOwn(EDITIONS,initialState))startGuide();
else loadEdition(initialState).catch(()=>{initialState=HOME_STATE}).then(startGuide);
