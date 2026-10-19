const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL=u=>/^https?:\/\//.test(u||'')?u:'';
const labels={official_source_reviewed:'Official source reviewed',official_search_extract_only:'Search excerpt only — needs verification',needs_recheck:'Needs confirmation',imported_unverified:'Not re-reviewed — needs verification'};
const types={benefits_and_funding:'Benefits and care costs',care_facilities:'Care facilities',child_development_autism:'Child development and autism',dd_intake_service_coordination:'Developmental disability support',education_special_education:'Special education',employment_transition:'Employment and transition',equipment_home_accessibility:'Equipment and home accessibility',general_navigation:'Finding help and advocacy',help_at_home:'Help at home',veteran_services:'Veteran services'};
let DATA=[],COUNTIES=[],STATE='OH',priority=[],routes={},seniorTopics={},routeNames={},route='priority';
const regionalIDs=role=>DATA.filter(x=>x.regional_role===role).map(x=>x.program_id);
const officeLegacyIds=new Set(['morrow-vso','knox-vso','marion-vso','delaware-vso']);
const tel=p=>{const parts=p.split(/\s+ext\.?\s*/i);return 'tel:'+parts[0].replace(/[^+0-9]/g,'')+(parts[1]?';ext='+parts[1].replace(/\D/g,''):'')};
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

function shareURL(){const u=new URL(location.href);u.pathname=u.pathname.replace(/[^/]*$/, '');u.search='';u.hash='';u.searchParams.set('state',STATE);if($('county').value)u.searchParams.set('county',$('county').value);if(route!=='priority')u.searchParams.set('view',route);if(route==='seniors'&&$('senior-topic').value)u.searchParams.set('topic',$('senior-topic').value);if($('search').value.trim())u.searchParams.set('q',$('search').value.trim());if($('need').value)u.searchParams.set('type',$('need').value);if($('status').value)u.searchParams.set('status',$('status').value);return u}
const FEEDBACK_EMAIL='travis@vethomeguard.org',FEEDBACK_ASK=['','What needs fixing? (wrong phone, office moved, program ended, or something else)','','Your role, optional (facility staff, family member, agency staff):','','Please share public listing information only. Do not include resident names or health details.'];
function reportHref(subject,lines){return 'mailto:'+FEEDBACK_EMAIL+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(lines.join('\n'))}
function reportLink(x,county){return '<a class="report" href="'+esc(reportHref('Guide correction: '+STATE+' · '+x.name,['Listing: '+x.name,'Record: '+STATE+' · '+x.program_id,'County viewed: '+(county||'none'),...FEEDBACK_ASK]))+'">Report a problem with this listing</a>'}
function countyReportLink(county){return '<p class="report-row"><a class="report" href="'+esc(reportHref('Guide correction: '+STATE+' · '+county+' County contacts',['County: '+county+' ('+STATE+')','Section: county contacts',...FEEDBACK_ASK]))+'">Report a problem with these county contacts</a></p>'}
function evidenceLinks(x){return (x.source_evidence||[]).map(e=>{const u=safeURL(e.url);return u?'<p><a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(e.title||'Official evidence')+'</a>'+ (e.scope?'<br>'+esc(e.scope):'')+'</p>':''}).join('')}
function render(){const q=$('search').value.toLowerCase().trim(),county=$('county').value,need=$('need').value,status=$('status').value;
const rows=DATA.filter(x=>!officeLegacyIds.has(x.program_id)&&(route==='all'||(route==='priority'?priority:routes[route]).includes(x.program_id))&&matchesCounty(x,county)&&(route!=='seniors'||!$('senior-topic').value||seniorTopicIDs($('senior-topic').value).includes(x.program_id))&&(!q||[x.name,x.description,x.next_step,x.organization,...(x.needs_supported||[])].join(' ').replaceAll('_',' ').toLowerCase().includes(q))&&(!need||(x.needs_supported||[]).includes(need))&&(!status||x.verification.record_status===status)).sort((a,b)=>{const rank=x=>priority.includes(x.program_id)?priority.indexOf(x.program_id):999;return rank(a)-rank(b)||a.name.localeCompare(b.name)});
$('count').textContent=routeNames[route]+' · '+rows.length+' resources'+(county?' for '+county+' County':' across listed service areas');
$('results').innerHTML=rows.map(x=>{const c=x.public_contact||{},v=x.verification||{},u=safeURL(x.official_url),recommended=priority.includes(x.program_id),constraints=(x.constraints||[]).filter(s=>!/(Claude|schema v|intentionally null|fetch failed|indexed extract)/i.test(s)),who=audience(x);return `<article id="resource-${esc(x.program_id)}" class="${recommended?'recommended':''}">${recommended?'<div class="recommended-label">'+(v.record_status==='official_source_reviewed'?'Useful starting point':'Potential starting point — confirm with provider')+'</div>':''}<h2>${esc(x.name)}</h2><div class="meta">${esc((x.service_area||[]).map(a=>national(a)?'All '+EDITIONS[STATE].name+' counties':a).filter((a,i,s)=>s.indexOf(a)===i).join(' · ')||'Ask the provider about service area')}${x.organization?'<br>'+esc(x.organization):''}</div><p>${esc(x.description||'Use this provider’s resource information to explore available help.')}</p>${who?'<p class="suitable"><strong>Who to ask about:</strong> '+esc(who)+'</p>':''}<p class="step"><strong>Your next step</strong><br>${esc(x.next_step||'Ask the provider what help is available and how to get started.')}</p>${constraints.length?'<details class="small"><summary>Limits and conditions</summary><p>'+esc(constraints.join(' '))+'</p></details>':''}<div class="links">${c.phone?phoneLink(c.phone):''}${u?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">Resource website ↗</a>':''}</div><p class="source-status ${v.record_status==='official_source_reviewed'?'':'notice'}"><strong>${esc(labels[v.record_status]||'Needs verification')}</strong>${v.record_status==='official_source_reviewed'?'':'<br>Full verification is incomplete. Confirm the contact and service details with the provider before relying on this referral.'}</p><details class="source-details"><summary>${esc(labels[v.record_status]||'Source status not recorded')} · ${esc(v.last_reviewed_on||'Date not recorded')}</summary><p>Source review is a check of published information, not direct confirmation of service availability. Ask the provider about eligibility and the current process.</p>${evidenceLinks(x)}</details>${reportLink(x,county)}</article>`}).join('')||'<div class="empty">No matches in this view. Try Browse all resources, clear the search or choose a different resource type.</div>';
renderCounty();renderAccessibility();renderSeniorGuide();renderHelper();if(county&&!$('county-panel').hidden&&COUNTIES.some(c=>c.county===county))$('county-panel').innerHTML+=countyReportLink(county);document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route===route)));$('share-status').textContent='';history.replaceState(null,'',shareURL())}

const EDITIONS=window.VHG_EDITIONS=window.VHG_EDITIONS||{};
const EDITION_FILES={"OH": "assets/editions/oh.js?v=709ee24be7", "PA": "assets/editions/pa.js?v=c32769a243", "NY": "assets/editions/ny.js?v=313bc0862e", "MI": "assets/editions/mi.js?v=1ac2862276", "KY": "assets/editions/ky.js?v=732b30c095", "UT": "assets/editions/ut.js?v=e6f6af1593", "IN": "assets/editions/in.js?v=d4daff6dcf", "WV": "assets/editions/wv.js?v=c4e1a5fbdd", "TX": "assets/editions/tx.js?v=cef76f0be6", "FL": "assets/editions/fl.js?v=05aed573f2", "CA": "assets/editions/ca.js?v=382c7b0687"};
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
 if(!Object.hasOwn(routeNames,route))route='priority';
 $('edition-state').value=state;$('county').innerHTML='<option value="">Choose a county…</option>';$('county').value='';
 COUNTIES.forEach(c=>{const o=document.createElement('option');o.value=c.county;o.textContent=c.county+' County';$('county').append(o)});
 $('need').innerHTML='<option value="">All resource types</option>';
 [...new Set(DATA.flatMap(x=>x.needs_supported||[]))].sort().forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent=types[n]||n.replaceAll('_',' ');$('need').append(o)});
 ['search','need','status','office-search'].forEach(id=>$(id).value='');
 for(const [id,markup] of Object.entries(config.markup)){const wrapper=document.createElement('div');wrapper.innerHTML=markup;const replacement=wrapper.firstElementChild;$(id).replaceWith(replacement)}
 // Keep state-specific instructions available without making the first screen an explanation of the data model.
 const pending=DATA.filter(x=>x.verification.record_status!=='official_source_reviewed').length;
 $('coverage-detail').innerHTML='<p>'+esc(config.name)+': referral routes for '+COUNTIES.length+' counties. Local service coverage is still growing.</p><p>'+pending+' resource records need further source checks. Check the status on each listing and confirm availability with the agency.</p>';
 if(config.coverageNote)$('coverage-detail').innerHTML+='<p>'+esc(config.coverageNote)+'</p>';
 document.querySelector('label[for="county"]').textContent='County in '+config.name;
 $('aid-open').hidden=state!=='OH';document.querySelector('.office-directory summary').textContent='Browse '+config.name+' county contacts';
 $('office-search').placeholder='Search '+config.name+' counties';
 document.title=config.name+' | Veteran Resident Resource Guide';
 document.querySelectorAll('a[href^="share"]').forEach(a=>a.href=config.sharePage);
 document.querySelectorAll('.footer-links a').forEach(a=>{if(a.textContent==='County contact data')a.href=config.files.offices;if(a.textContent==='Resource data')a.href=config.files.resources});
 document.querySelectorAll('#urgent-help a[href^="?view="]').forEach(a=>{const u=new URL(a.href,location.href);u.searchParams.set('state',state);a.href=u.href});
 bindStateControls();
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
 const card=x=>'<article><h3>'+esc(x.name)+'</h3>'+(x.public_contact?.phone?'<p>'+phoneLink(x.public_contact.phone)+'</p>':'')+'<p>'+esc(x.next_step)+'</p>'+(['IN','WV','TX'].includes(STATE)&&x.regional_role?'<p class="small">'+esc((x.constraints||[]).join(' '))+'</p>':'')+'<a href="'+esc(safeURL(x.official_url))+'" target="_blank" rel="noopener">Contact information</a><p class="meta">'+esc(labels[x.verification.record_status])+' · '+esc(x.verification.last_reviewed_on)+'</p></article>';
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
 if(person==='other'&&need==='housing')contacts='<article><h3>Local housing assistance</h3><p>Call '+phoneLink('211')+' and ask about housing support in '+esc(county?county+' County, '+EDITIONS[STATE].name:EDITIONS[STATE].name)+'.</p></article>';
 if(need==='accessibility'&&person==='survivor')text.accessibility='Ask the discharge planner and local aging agency to coordinate home access. A spouse’s military service alone does not establish eligibility for veteran-only housing adaptations.';
 if(need==='accessibility'&&person==='survivor')contacts=DATA.filter(x=>x.regional_role==='aging_agency'&&county&&x.service_area.includes(county)).map(x=>'<article><h3>'+esc(x.organization)+'</h3><p>'+phoneLink(x.public_contact.phone)+'</p></article>').join('')||'<p>Choose a county for the local aging contact.</p>';
 $('helper-next').innerHTML='<h3>'+esc(EDITIONS[STATE].name)+(county?' · '+esc(county)+' County':'')+'</h3><p><strong>'+esc(text[need])+'</strong></p><div class="contact-grid">'+contacts+'</div><div class="call-script"><strong>What to ask</strong><p>“I’m helping someone who wants support with '+esc($('helper-need').selectedOptions[0].textContent.toLowerCase())+'. What is the intake process, what documents are needed, and can you help if they cannot travel?”</p></div><p>Agree on who will follow up and when. Confirm eligibility and availability directly.</p>';
}
function openHelper(){helperActive=true;helperShowingResults=false;render();$('helper-title').focus({preventScroll:true});$('helper-guide').scrollIntoView({behavior:'smooth'})}
const params=new URLSearchParams(location.search);
let initialState=Object.hasOwn(EDITION_FILES,params.get('state'))?params.get('state'):'OH';
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
$('helper-open').onclick=openHelper;$('helper-header').onclick=e=>{e.preventDefault();openHelper()};
['helper-person','helper-need'].forEach(id=>$(id).addEventListener('change',()=>{helperShowingResults=false;render()}));
$('helper-close').onclick=()=>{helperActive=false;helperShowingResults=false;route='priority';render();$('directory').scrollIntoView({behavior:'smooth'})};
$('helper-resources').onclick=()=>{helperShowingResults=true;route=helperRoute;['search','need','status'].forEach(id=>$(id).value='');if(route==='accessibility'){$('access-veteran').value=$('helper-person').value==='veteran'?'yes':$('helper-person').value==='unknown'?'unknown':'no';$('access-home').value='facility'}if(route==='seniors')$('senior-topic').value=$('helper-need').value==='benefits'?'costs':$('helper-need').value==='daily'?'daily':'';render();const target=route==='accessibility'?'accessibility-guide':route==='seniors'?'seniors-guide':'results';$(target).scrollIntoView({behavior:'smooth'})};
$('helper-print').onclick=()=>{if(!$('county').value){$('helper-status').textContent='Choose a county first.';$('county').focus();return}$('helper-status').textContent='';clearPrintMode();document.body.classList.add('print-helper');window.print()};
window.addEventListener('afterprint',()=>{clearPrintMode();accessPrintStates.forEach(({el,open})=>el.open=open);accessPrintStates=[]});
render();renderOfficeList();
}
if(Object.hasOwn(EDITIONS,initialState))startGuide();
else loadEdition(initialState).catch(()=>{initialState='OH'}).then(startGuide);
