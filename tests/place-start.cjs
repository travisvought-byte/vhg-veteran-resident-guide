// The guide opens with a map of every state and a way into the world pages. The crisis and urgent lines are
// listed with the guide's other resources near the end of the page (before Support VHG), not in a box at the top.
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const registry=JSON.parse(read('states/registry.json'));
const world=JSON.parse(read('data/world/countries.json')).countries.length;
// The map: real state shapes (Nina's Map), each a link named for screen readers; then the same states by name.
const shapes=html=>[...html.matchAll(/<a href="([^"]+)" data-state="([A-Z]{2})"( aria-current="page")? aria-label="([^"]+)"><title>[^<]+<\/title><path d="M[^"]+"\/><\/a>/g)];
const named=html=>[...html.matchAll(/<li><a href="([^"]+)" data-state="([A-Z]{2})"( aria-current="page")?>([^<]+)<\/a><\/li>/g)];
for(const s of registry){
 const page=s.page,html=read(page),m=shapes(html),n=named(html);
 assert.equal((html.match(/<svg class="usmap"/g)||[]).length,1,page+' has one state map');
 assert(/<svg class="usmap" viewBox="0 0 \d+ \d+" role="group" aria-labelledby="usmap-t usmap-d"><title id="usmap-t">/.test(html),page+' map is named for screen readers');
 assert.equal(m.length,51,page+' map shows every state');
 assert.equal(n.length,51,page+' list names every state');
 for(const [list,what] of [[m,'map'],[n,'list']])for(const x of list){const target=registry.find(r=>r.code===x[2]);assert.equal(x[1],target.page==='index.html'?'./':target.page,x[2]+' '+what+' links to its own page');assert.equal(x[4],target.name.replace('&','&amp;'),x[2]+' '+what+' carries its full name')}
 assert.deepEqual(m.filter(x=>x[3]).map(x=>x[2]),[s.code],page+' map marks only its own state');
 assert.deepEqual(n.filter(x=>x[3]).map(x=>x[2]),[s.code],page+' list marks only its own state');
 assert(html.includes('in '+world+' countries'),page+' world count comes from the data');
 const main=html.indexOf('<main>'),urgent=html.indexOf('id="urgent-help"'),map=html.indexOf('id="place-start"'),picker=html.indexOf('class="edition-picker"'),county=html.indexOf('id="county-start"'),coverage=html.indexOf('id="edition-coverage"');
 assert(main<map&&map<picker&&picker<coverage&&coverage<county,page+' order: map, list, coverage, county');
 const support=html.indexOf('id="support-vhg"'),results=html.indexOf('id="results"');
 assert(results<urgent&&urgent<support,page+' crisis and urgent lines sit near the end, after the resource list');
 assert.equal((html.match(/id="urgent-help"/g)||[]).length,1,page+' lists the crisis lines once');
 assert(/<section id="urgent-help" class="help-lines" aria-labelledby="urgent-title"><h2 id="urgent-title">Crisis and urgent lines<\/h2><p>Crisis: <a href="tel:988">988<\/a> \(veterans: press 1\)/.test(html),page+' crisis lines are a plain section');
 assert(html.includes('<div class="footer-links"><a href="#urgent-help">Crisis and urgent lines</a>'),page+' footer points to the crisis lines');
 if(page==='index.html')assert(/<section id="place-start"[^>]*aria-labelledby="place-title"><h2 id="place-title">Where do you need help\?<\/h2>/.test(html),'home page opens the map');
 else assert(/<details id="place-start" class="place-start"><summary>/.test(html),page+' keeps the map one tap away');
}
const runtime=read('assets/guide-runtime.js');
assert(runtime.includes(".state-tiles a,.usmap a').forEach(a=>a.dataset.state===state?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current'))"),'switching state moves the highlight');
console.log('PASS: every page opens with a map of all 51 states (real shapes, each its own named link), the same states by name, and the '+world+'-country world pages; crisis lines sit near the end.');
