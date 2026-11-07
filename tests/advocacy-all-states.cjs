const fs=require('fs'),{JSDOM}=require('jsdom');
const html=fs.readFileSync('disability-advocacy.html','utf8'),script=fs.readFileSync('assets/disability-advocacy.js','utf8');
function load(q){const dom=new JSDOM(html,{url:'https://example.org/disability-advocacy.html'+q,runScripts:'outside-only'});const w=dom.window;w.HTMLAnchorElement.prototype.click=function(){};w.print=()=>{};w.eval(script);return {w,d:w.document};}
const {d:d0}=load('');const states=[...d0.getElementById('start-state').options].map(o=>[o.value,o.textContent.trim()]);
const data=JSON.parse(d0.getElementById('advocacy-data').textContent);
const issues=[];const bad=/\{state\}|undefined|null|NaN|\[object|__[A-Z]+__/;
for(const [code,name] of states){
 const {w,d}=load('?state='+code);const $=id=>d.getElementById(id);
 const set=(id,v)=>{$(id).value=v;$(id).dispatchEvent(new w.Event('change'));};
 if($('start-state').value!==code)issues.push([code,'start-state not set']);
 if($('compose-state').value!==code)issues.push([code,'compose-state not set']);
 d.querySelectorAll('.problem-grid a').forEach(a=>{if(!a.href.includes('state='+code))issues.push([code,'problem link',a.href])});
 const g=$('start-guide');if(g&&!g.href.includes(code))issues.push([code,'guide link',g.href]);
 // topic cards
 d.querySelectorAll('[data-state-ask]').forEach(e=>{const t=e.textContent;if(bad.test(t))issues.push([code,'card bad text',t.slice(0,80)]);if(code!=='OH'&&/\bOhio\b/.test(t))issues.push([code,'card mentions Ohio']);});
 for(const topic of data.topics.map(t=>t.id))for(const scope of ['state','US'])for(const fmt of ['short','letter']){
  set('topic',topic);set('scope',scope);set('format',fmt);$('build').click();
  const m=$('message').value,s=$('subject').value,c=$('contacts').textContent,links=[...$('contacts').querySelectorAll('a')].map(a=>a.href);
  const tag=[code,topic,scope,fmt].join('/');
  if(!m||m.length<200)issues.push([tag,'short message',m.length]);
  if(bad.test(m)||bad.test(s)||bad.test(c))issues.push([tag,'placeholder/undefined in output']);
  if(code!=='OH'&&/\bOhio\b/.test(m+c+s))issues.push([tag,'Ohio leaks']);
  if(scope==='state'&&!m.includes(name)&&!(code==='DC'&&/District of Columbia|D\.C\./.test(m)))issues.push([tag,'state name missing in message']);
  if(scope==='state'&&!c.includes(name)&&code!=='DC')issues.push([tag,'contacts lacks state name']);
  if(!links.length||links.some(l=>!l.startsWith('https://')))issues.push([tag,'contact links',links.join(' ')]);
  if(scope==='US'&&!/Congress|Representative|Senator|senator|representative/.test(m+c))issues.push([tag,'federal wording missing']);
  const so=$('scope').selectedOptions[0].textContent;if(scope==='state'&&!so.includes(name)&&!(code==='DC'))issues.push([tag,'scope label',so]);
 }
}
const counts={};issues.forEach(i=>{const k=i[1];counts[k]=(counts[k]||0)+1});
if(issues.length){console.error(issues.slice(0,25).map(i=>i.join(' | ')).join('\n'));process.exit(1);}
console.log(`PASS advocacy all states: ${states.length} jurisdictions (50 states and D.C.) x ${data.topics.length} topics x state/federal x short/letter build complete, state-specific messages with official https contact links and no Ohio or placeholder leaks.`);
