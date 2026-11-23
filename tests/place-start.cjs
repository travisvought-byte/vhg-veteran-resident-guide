// The guide opens with crisis numbers, then a map of every state and a way into the world pages.
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const registry=JSON.parse(read('states/registry.json'));
const world=JSON.parse(read('data/world/countries.json')).countries.length;
const tiles=html=>[...html.matchAll(/<li style="grid-column:(\d+);grid-row:(\d+)"><a href="([^"]+)" data-state="([A-Z]{2})"( aria-current="page")?>/g)];
for(const s of registry){
 const page=s.page,html=read(page),t=tiles(html);
 assert.equal(t.length,51,page+' shows every state');
 assert.equal(new Set(t.map(m=>m[1]+','+m[2])).size,51,page+' no two tiles share a cell');
 for(const m of t){const target=registry.find(r=>r.code===m[4]);assert.equal(m[3],target.page==='index.html'?'./':target.page,m[4]+' links to its own page');assert(html.includes('<span class="sr-only">'+target.name.replace('&','&amp;')+'</span>'),m[4]+' has its full name for screen readers')}
 assert.deepEqual(t.filter(m=>m[5]).map(m=>m[4]),[s.code],page+' marks only its own state');
 assert(html.includes('in '+world+' countries'),page+' world count comes from the data');
 const main=html.indexOf('<main>'),urgent=html.indexOf('id="urgent-help"'),map=html.indexOf('id="place-start"'),picker=html.indexOf('class="edition-picker"'),county=html.indexOf('id="county-start"'),coverage=html.indexOf('id="edition-coverage"');
 assert(main<urgent&&urgent<map&&map<picker&&picker<coverage&&coverage<county,page+' order: crisis, map, list, coverage, county');
 if(page==='index.html')assert(/<section id="place-start"[^>]*aria-labelledby="place-title"><h2 id="place-title">Where do you need help\?<\/h2>/.test(html),'home page opens the map');
 else assert(/<details id="place-start" class="place-start"><summary>/.test(html),page+' keeps the map one tap away');
}
const runtime=read('assets/guide-runtime.js');
assert(runtime.includes(".state-tiles a').forEach(a=>a.dataset.state===state?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current'))"),'switching state moves the highlight');
console.log('PASS: every page opens with crisis numbers, then a map of all 51 states (each its own link, full names for screen readers) and the '+world+'-country world pages.');
