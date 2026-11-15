const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('jsdom');
const {localDate,onDate,filterVenues}=require('../templates/bingo/network.js');
const venues=JSON.parse(fs.readFileSync('data/bingo/venues.json'));
assert.equal(localDate('America/Los_Angeles',new Date('2026-11-16T02:00:00Z')),'2026-11-15');
assert.equal(localDate('America/New_York',new Date('2026-11-16T05:30:00Z')),'2026-11-16');
const monthly=venues.find(r=>r.id==='ut-hurricane');
assert(onDate(monthly,'2026-11-23'));assert(!onDate(monthly,'2026-11-16'));
assert(!onDate(monthly,'2027-03-08'),'stale schedules excluded');
assert(!onDate(venues.find(r=>r.id==='ut-enterprise'),'2026-11-27'),'holiday exception honored');
const dated=venues.find(r=>r.id==='pa-irishtown');
assert(onDate(dated,'2026-12-06'));assert(!onDate(dated,'2027-12-06'));
assert.equal(filterVenues(venues,{q:'98115',kind:'',day:''},'2026-11-15')[0].id,'wa-mother-aerie');
assert.equal(filterVenues(venues,{q:'',kind:'free_recreation',day:''},'2026-11-15').length,3);
assert(!filterVenues(venues,{q:'Fife',kind:'',day:'today'},'2026-11-15').length,'unknown schedule excluded');
for(const state of ['pennsylvania','new-york','washington','utah']){
 const file='bingo-site/states/'+state+'.html',html=fs.readFileSync(file,'utf8');
 const dom=new JSDOM(html,{url:'https://bingo.vethomeguard.org/states/'+state+'.html',runScripts:'outside-only'});
 const d=dom.window.document;
 assert(d.querySelectorAll('article').length>0,'usable without JS');
 assert(!html.includes('{{'),'all template slots filled');
 for(const a of d.querySelectorAll('[href],[src]')){
  const ref=a.getAttribute('href')||a.getAttribute('src');
  if(/^(https?:|mailto:|tel:|#)/.test(ref))continue;
  let target=path.resolve(path.dirname(file),ref);if(ref.endsWith('/'))target=path.join(target,'index.html');
  assert(fs.existsSync(target),file+' broken link '+ref);
 }
 dom.window.eval(fs.readFileSync('templates/bingo/network.js','utf8'));
 assert(!d.getElementById('filters').hidden);
 d.getElementById('search').value='zz-no-match';d.getElementById('search').dispatchEvent(new dom.window.Event('input',{bubbles:true}));
 assert(!d.getElementById('empty').hidden);assert([...d.querySelectorAll('article')].every(a=>a.hidden));
 assert(dom.window.location.search.includes('q=zz-no-match'));
 dom.window.close();
}
console.log('Bingo network: date, freshness, exclusions, filters, links and DOM checks passed');
