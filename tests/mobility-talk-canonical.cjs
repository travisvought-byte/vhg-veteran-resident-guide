const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
for(const p of ['mobility-rights.html','disability-advocacy.html','mobility-independence.html']){
 const html=fs.readFileSync(p,'utf8'),d=new JSDOM(html).window.document;
 assert.equal(d.querySelector('link[rel=canonical]').href,'https://mobilitytalk.org/'+p,p+' canonical points to Mobility Talk');
 const note=d.querySelector('main .moved-note a');assert(note&&note.href==='https://mobilitytalk.org/'+p,p+' links to its Mobility Talk page');
}
const sm=fs.readFileSync('sitemap.xml','utf8');
for(const p of ['mobility-rights.html','disability-advocacy.html','mobility-independence.html'])assert(!sm.includes('guide.vethomeguard.org/'+p),p+' stays out of this sitemap');
assert(fs.readFileSync('index.html','utf8').includes('https://mobilitytalk.org/states/'),'home links to Mobility Talk states');
console.log('PASS mobility talk: duplicate pages canonicalize to mobilitytalk.org, link to it, stay out of this sitemap, and the guide home links to it.');
