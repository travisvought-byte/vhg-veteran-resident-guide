require('./legacy-fixtures.cjs');
// Feedback links: every listing and county panel offers a prefilled correction email,
// in every edition, without leaking state-specific wording or resident information.
require('./kentucky.cjs');
const {setup}=require('./accessibility.cjs');
const assert=require('assert'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const decode=s=>s.replaceAll('&amp;','&');
const mailtos=html=>[...html.matchAll(/class="report" href="([^"]+)"/g)].map(m=>decode(m[1]));
const editions={OH:['index.html','Morrow'],PA:['pa.html','Centre'],NY:['ny.html','Chemung'],MI:['mi.html','Wayne'],KY:['ky.html','Adair']};
for(const [state,[page,county]] of Object.entries(editions)){
  // Statewide view: one report link per listing, no county named.
  const t=setup('',page);
  const cards=t.count(),links=mailtos(t.nodes.results.innerHTML);
  assert.equal(links.length,cards,state+' every listing has a report link');
  const first=new URL(links[0]);
  assert.equal(first.protocol,'mailto:');assert.equal(first.pathname,'travis@vethomeguard.org');
  assert(first.searchParams.get('subject').startsWith('Guide correction: '+state+' · '),state+' subject');
  const body=first.searchParams.get('body');
  assert(body.includes('Record: '+state+' · '),state+' record id');assert(body.includes('County viewed: none'));
  assert(body.includes('Do not include resident names or health details'),state+' privacy reminder');
  assert(!mailtos(t.nodes['county-panel'].innerHTML).length,state+' no county link without a county');
  // County view: listings carry the county, and the county panel gets its own link.
  const c=setup('?county='+encodeURIComponent(county),page);
  assert(mailtos(c.nodes.results.innerHTML).every(u=>new URL(u).searchParams.get('body').includes('County viewed: '+county)),state+' county in listing reports');
  const panel=mailtos(c.nodes['county-panel'].innerHTML);
  assert.equal(panel.length,1,state+' county panel link');
  assert.equal(new URL(panel[0]).searchParams.get('subject'),'Guide correction: '+state+' · '+county+' County contacts');
  // Views that hide the county panel do not add a hidden link to it.
  const a=setup('?county='+encodeURIComponent(county)+'&view=accessibility',page);
  assert(!mailtos(a.nodes['county-panel'].innerHTML).length,state+' no link in hidden panel');
}
for(const page of ['index.html','pa.html','ny.html','mi.html','ky.html']){
  const html=fs.readFileSync(path.join(root,page),'utf8');
  assert(!html.includes('/issues/new'),page+' no public issue link for corrections');
  assert(/@media print\{\.report,\.report-row\{display:none\}\}/.test(html),page+' report links hidden in print');
}
for(const page of ['share.html','share-pa.html','share-ny.html','share-mi.html','share-ky.html'])assert(fs.readFileSync(path.join(root,page),'utf8').includes('use “Report a problem” on that listing'),page);
console.log('PASS: prefilled correction links on every listing and county panel in all five editions, state and county context, privacy reminder, print hiding and sharing-kit invitation.');
// Evidence limitations must be visible outside collapsed source details in every edition.
const vm=require('vm');
for(const [state,[page]] of Object.entries(editions)){
  const html=fs.readFileSync(path.join(root,page),'utf8');
  const t=setup('?view=all',page),data=vm.runInContext('DATA',t.ctx),counties=vm.runInContext('COUNTIES',t.ctx);
  const pending=data.filter(r=>r.verification.record_status!=='official_source_reviewed').length;
  const excerpts=data.filter(r=>r.verification.record_status==='official_search_extract_only').length;
  assert.equal((html.match(/id="edition-coverage"/g)||[]).length,1,state+' single coverage summary');
  assert(html.includes(`Referral routes cover ${counties.length} counties`),state+' accurate county count');
  assert(html.includes(`${pending} resource records need further verification, including ${excerpts}`),state+' accurate evidence totals');
  for(const r of data.filter(r=>r.verification.record_status!=='official_source_reviewed')){
    const card=t.nodes.results.innerHTML.split(`id="resource-${r.program_id}"`)[1]?.split('</article>')[0];
    if(!card)continue; // Four duplicate Ohio office records are intentionally hidden.
    assert(card.split('<details class="source-details">')[0].includes('Full verification is incomplete'),state+' visible warning '+r.program_id);
    assert(!card.includes('recommended-label">Useful starting point'),state+' no unqualified recommendation '+r.program_id);
  }
  assert(html.includes('.source-status{display:block!important}'),state+' print warning retained');
}
console.log('PASS: visible verification warnings, accurate state coverage/evidence totals, qualified recommendations and print notices across all editions.');
for(const [state,[page]] of Object.entries(editions)){
 const html=fs.readFileSync(path.join(root,page),'utf8'),crisis=setup('?view=crisis',page),housing=setup('?view=housing',page);
 assert.equal((html.match(/id="urgent-help"/g)||[]).length,1,state+' single visible urgent panel');
 assert.equal(crisis.count(),3,state+' crisis route');
 for(const id of ['crisis-988','va-mental-health'])assert(crisis.nodes.results.innerHTML.includes('resource-'+id),state+' '+id);
 for(const id of ['va-housing-help','va-ssvf','va-hud-vash','va-crrc'])assert(housing.nodes.results.innerHTML.includes('resource-'+id),state+' housing '+id);
 assert(html.includes('tel:988?oai_link_source=model_response_hotline'),state+' verified crisis contact');
}
require('./bingo.cjs');
console.log('PASS: urgent panel, crisis support and expanded homelessness routes in every state.');

const aid=setup('?view=aid');assert.equal(aid.count(),8);for(const id of ['ohio-legal-aid','ohio-legion-claims','ohio-utility-assistance','ohio-dav-transport'])assert(aid.nodes.results.innerHTML.includes('resource-'+id));
for(const page of ['pa.html','ny.html','mi.html','ky.html']){const h=fs.readFileSync(path.join(root,page),'utf8');assert(!h.includes('ohio-aid-link'));assert(!h.includes('ohio-legion-claims'));}
assert(aid.nodes.results.innerHTML.includes('not authorized to file claims'));assert(aid.nodes.results.innerHTML.includes('do not cover every community'));
console.log('PASS: Ohio aid route, claims authority and transport limits, and isolation from other state editions.');

require('./housing.cjs');
