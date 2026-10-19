// Wave 1: handoff copy must use the selected state's public referral records.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
const root=path.join(__dirname,'..');
const editions=fs.readdirSync(path.join(root,'assets/editions')).filter(x=>x.endsWith('.js')).sort().map(x=>fs.readFileSync(path.join(root,'assets/editions',x),'utf8')).join('\n');
const guide=fs.readFileSync(path.join(root,'assets/guide.js'),'utf8');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const registry=JSON.parse(fs.readFileSync(path.join(root,'states/registry.json'),'utf8'));

function setup(query=''){
 const dom=new JSDOM(html,{url:'https://vethomeguard.org/directory/?'+query,runScripts:'outside-only',pretendToBeVisual:true});
 dom.window.HTMLElement.prototype.scrollIntoView=function(){};
 dom.window.print=function(){};
 dom.window.eval(editions+'\n'+guide+'\nwindow.__wave1Copy=helperHandoffText;');
 const d=dom.window.document;
 const captures=[];
 Object.defineProperty(dom.window.navigator,'clipboard',{configurable:true,value:{writeText:async text=>{captures.push(text)}}});
 const change=(id,value)=>{const n=d.getElementById(id);n.value=value;n.dispatchEvent(new dom.window.Event('change',{bubbles:true}))};
 return {dom,d,change,captures};
}
async function clickCopy(t){
 t.d.getElementById('helper-copy').click();
 await new Promise(resolve=>setImmediate(resolve));
}
(async()=>{
 let count=0;
 for(const s of registry){
  const t=setup('q=PRIVATE_SEARCH_STRING&resident=SECRET&state='+s.code);
  t.change('edition-state',s.code);
  const county=t.d.getElementById('county').options[1].value;
  const offices=JSON.parse(fs.readFileSync(path.join(root,s.offices),'utf8'));
  const office=offices.find(x=>x.county===county);
  assert(office,s.code+' county office');
  t.change('county',county);
  t.d.getElementById('helper-open').click();
  t.change('helper-person','veteran');
  t.change('helper-need','benefits');
  await clickCopy(t);
  assert.equal(t.captures.length,1,s.code+' copies one handoff');
  let copy=t.captures[0];
  assert(copy.includes('Location: '+s.name+' · '+county+' County'),s.code+' correct location');
  assert(copy.includes(office.phone),s.code+' includes published phone');
  assert(copy.includes('Source: https://'),s.code+' includes source link');
  assert(copy.includes('Need: Benefits or help paying for care'),s.code+' contextualizes need');
  assert(copy.includes('Follow-up:'),s.code+' actionable follow-up fields');
  const url=new URL(copy.split('Guide: ')[1].split('\n')[0]);
  assert.equal(url.searchParams.get('state'),s.code);
  assert.equal(url.searchParams.get('county'),county);
  assert.equal(url.searchParams.get('help'),'1');
  assert.equal(url.searchParams.has('q'),false,s.code+' strips search');
  assert.equal(url.searchParams.has('resident'),false,s.code+' strips arbitrary query data');
  assert(!copy.includes('PRIVATE_SEARCH_STRING'));
  assert(!copy.includes('SECRET'));
  assert(t.d.getElementById('helper-status').textContent.includes('copied'),s.code+' success announcement');
  t.dom.window.close();count++;
 }
 const missing=setup();
 missing.d.getElementById('helper-open').click();
 await clickCopy(missing);
 assert.equal(missing.captures.length,0,'no county means no clipboard write');
 assert(missing.d.getElementById('helper-status').textContent.includes('Choose a county'));
 missing.change('county','Morrow');
 missing.change('helper-need','daily');
 assert.equal(missing.d.getElementById('helper-status').textContent,'','changing selections clears old statuses');
 Object.defineProperty(missing.dom.window.navigator,'clipboard',{configurable:true,value:undefined});
 await clickCopy(missing);
 assert(missing.d.getElementById('helper-status').textContent.includes('Print this handoff'),'clipboard fallback');
 missing.dom.window.close();
 console.log('PASS: copy referral handoff, published phones/sources, safe county links, no private query strings and clipboard fallbacks in '+count+' states.');
})().catch(e=>{console.error(e);process.exit(1)});
