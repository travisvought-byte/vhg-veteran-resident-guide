// Every entry page speaks to the person most likely to land on it: its own title, description, heading and
// opening (data/landing/), Open Graph tags for shared links, and on the home and state pages an
// "I'm here as..." chooser whose every option leads to something that exists in that state.
const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {JSDOM}=require(process.env.GUIDE_JSDOM||'jsdom');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const registry=JSON.parse(read('states/registry.json'));
const land=JSON.parse(read('data/landing/states.json'));
const chooser=JSON.parse(read('data/landing/chooser.json'));
const doc=html=>new JSDOM(html).window.document;
const meta=(d,key)=>(d.querySelector('meta[property="'+key+'"]')||d.querySelector('meta[name="'+key+'"]'))?.content;
const seen={title:new Set(),description:new Set(),h1:new Set(),intro:new Set()};
for(const s of registry){
 const html=read(s.page),d=doc(html),l=s.base?land.home:land.states[s.code];
 const h1=d.querySelector('h1').textContent,intro=d.getElementById('guide-intro').textContent;
 assert.equal(intro,l.intro,s.code+' opening comes from its landing data');
 if(!s.base){assert(h1.startsWith(s.name+' '),s.code+' heading names the state');assert(d.title.startsWith(s.name+' Veteran Resource Guide: '),s.code+' title')}
 const url='https://guide.vethomeguard.org/'+(s.base?'':s.page);
 assert.equal(d.querySelector('link[rel=canonical]').href,url);assert.equal(meta(d,'og:url'),url,s.code+' og:url');
 for(const key of ['og:title','og:description','og:image','og:site_name','twitter:card','twitter:title'])assert(meta(d,key),s.code+' '+key);
 assert.equal(meta(d,'og:description'),d.querySelector('meta[name=description]').content);
 for(const [k,v] of [['title',d.title],['description',meta(d,'description')],['h1',h1],['intro',intro]]){assert(!seen[k].has(v),s.code+' '+k+' is unique: '+v);seen[k].add(v)}
 // The chooser opens the page, before the map; the crisis and urgent lines come later, with the other resources.
 const who=html.indexOf('id="who-start"');assert(html.indexOf('<main>')<who&&who<html.indexOf('id="place-start"')&&who<html.indexOf('id="urgent-help"'),s.code+' chooser placement');
 assert.equal(d.querySelectorAll('#who-start a[data-who]').length,chooser.options.length);
 // "More help made for you": each of the other free guides, named with who it is built for, on its own site (November 28, 2026).
 assert.equal(d.querySelector('#who-start h3').textContent,chooser.more_help.title,s.code+' more help heading');
 assert.deepEqual([...d.querySelectorAll('#who-start a[data-guide]')].map(a=>a.getAttribute('href')),chooser.more_help.options.map(o=>o.href),s.code+' more help links');
 for(const a of d.querySelectorAll('#who-start a[data-guide]'))assert(a.querySelector('strong').textContent.includes(': '),s.code+' '+a.dataset.guide+' names who it is for and the guide');
 for(const a of d.querySelectorAll('#who-start a[data-states]'))assert.equal(a.closest('li').hidden,!a.dataset.states.split(' ').includes(s.code),s.code+' '+(a.dataset.who||a.dataset.guide)+' shown only where it applies');
}
console.log('PASS landing: home and '+(registry.length-1)+' state pages each have their own title, description, heading, opening and Open Graph tags, with the chooser first.');

// Every chooser view exists in every state, and switching state in place swaps the heading and opening.
{
 const editions=fs.readdirSync(root+'/assets/editions').filter(f=>f.endsWith('.js')).sort().map(f=>read('assets/editions/'+f)).join('\n');
 const dom=new JSDOM(read('pa.html'),{url:'https://example.org/pa.html',runScripts:'outside-only',pretendToBeVisual:true});
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};dom.window.eval(editions+'\n'+read('assets/guide.js')+'\nwindow.__routeNames=()=>routeNames;');
 const d=dom.window.document,change=v=>{d.getElementById('edition-state').value=v;d.getElementById('edition-state').dispatchEvent(new dom.window.Event('change'))};
 const views=chooser.options.filter(o=>o.view).map(o=>o.view);
 for(const s of registry){
  change(s.code);const names=dom.window.__routeNames(),l=s.base?land.home:land.states[s.code];
  for(const v of views){assert(Object.hasOwn(names,v),s.code+' has the '+v+' view');assert(d.querySelector('.quick-links [data-route="'+v+'"]'),s.code+' '+v+' button')}
  assert.equal(d.getElementById('guide-intro').textContent,l.intro,s.code+' opening after switching');
  assert(d.getElementById('guide-title').textContent.startsWith(s.base?'Veteran':s.name),s.code+' heading after switching');
  assert(d.getElementById('guide-eyebrow').textContent.endsWith(l.eyebrow||'For '+s.name+' veterans and families'));
  assert.equal(d.querySelector('#who-start [data-who="choosing"]').closest('li').hidden,s.code!=='OH');
  assert(d.title.startsWith(s.base?'Veteran Resource Guide':s.name+' Veteran Resource Guide'),s.code+' document title');
 }
 change('KY');d.getElementById('county').value='Christian';d.getElementById('county').dispatchEvent(new dom.window.Event('change'));
 d.querySelector('#who-start a[data-view="survivors"]').click();
 assert.equal(d.querySelector('.quick-links [data-route="survivors"]').getAttribute('aria-pressed'),'true','spouse option opens survivor help in place');
 assert.equal(d.getElementById('county').value,'Christian','and keeps the county');
 d.querySelector('#who-start a[data-help]').click();assert(!d.getElementById('helper-guide').hidden,'family option opens the helper');
 assert(new URL(d.querySelector('#who-start a[data-family-route]').href).searchParams.get('state')==='KY','parent option follows the state');
 dom.window.close();
}
console.log('PASS landing: every chooser option exists in all '+registry.length+' editions; switching state swaps heading, opening and title; options open in place and keep the county.');

// Sharing kits, world pages and the other entry pages.
{
 const titles=new Set();
 for(const s of registry){
  const d=doc(read(s.share_page)),url='https://guide.vethomeguard.org/'+s.share_page;
  assert.equal(d.querySelector('link[rel=canonical]').href,url);assert.equal(meta(d,'og:url'),url);assert.equal(meta(d,'og:image'),'https://guide.vethomeguard.org/assets/vhg-logo.png');
  assert(!titles.has(d.title));titles.add(d.title);assert(d.querySelector('h1').textContent.includes(s.code==='DC'?'Washington, DC':s.name),s.share_page+' heading');
 }
 for(const f of fs.readdirSync(root+'/world').filter(f=>f.endsWith('.html'))){
  const d=doc(read('world/'+f));
  assert(/^(Veterans|U\.S\. veterans)/.test(d.title),f+' title');assert(d.querySelector('.hero .opening'),f+' opening');
  for(const a of d.querySelectorAll('[data-jumps] a'))assert(d.getElementById(a.getAttribute('href').slice(1)),f+' jump '+a.getAttribute('href'));
  for(const key of ['og:image','og:title','og:url','twitter:card'])assert(meta(d,key),f+' '+key);
 }
 const pages=JSON.parse(read('data/landing/pages.json')).pages;
 for(const [f,p] of Object.entries(pages)){
  const d=doc(read(f));assert.equal(d.title,p.title);assert.equal(meta(d,'og:url'),p.url||'https://guide.vethomeguard.org/'+f);assert.equal(meta(d,'description'),p.description);
  if(p.intro)assert.equal(d.querySelector('h1').nextElementSibling.textContent,p.intro,f+' opening');
 }
}
console.log('PASS landing: sharing kits, country pages and the other entry pages carry their own titles, openings and Open Graph tags; every jump link lands.');
