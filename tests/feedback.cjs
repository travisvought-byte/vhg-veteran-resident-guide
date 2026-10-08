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
