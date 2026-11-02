'use strict';
(() => {
 document.documentElement.classList.add('advocacy-ready');
 const data=JSON.parse(document.getElementById('advocacy-data').textContent),$=id=>document.getElementById(id);
 const topics=new Map(data.topics.map(t=>[t.id,t]));
 const names=new Map([...$('start-state').options].map(o=>[o.value,o.textContent]));
 const validState=s=>names.has(s)?s:'OH';
 const stateLabel=s=>s==='DC'?'D.C. Council members':names.get(s)+' state lawmakers';
 const scopeLabel=(scope,s)=>scope==='US'?'Federal lawmakers':stateLabel(s);
 const ask=(topic,scope,s)=>scope==='US'?topic.asks.US:s==='OH'?topic.asks.OH:topic.asks.STATE.replaceAll('{state}',s==='DC'?'the District of Columbia':names.get(s));
 const greeting=(scope,s)=>scope==='US'?'Dear member of Congress,':s==='DC'?'Dear D.C. Councilmember,':'Dear '+names.get(s)+' state lawmaker,';
 let draftTopic='repair',draftScope='state',draftFormat='short',draftState='OH';
 function selection(){return {topic:topics.get($('topic').value),scope:$('scope').value,format:$('format').value,state:$('compose-state').value};}
 function count(){$('message-count').textContent=$('message').value.length+' characters. Contact forms may have their own length limits.';}
 function contacts(){
  const local=draftScope!=='US',ohio=local&&draftState==='OH';
  $('draft-context').textContent='Current draft: '+topics.get(draftTopic).title+' · '+scopeLabel(draftScope,draftState)+' · '+(draftFormat==='short'?'Short message':'Detailed letter')+'.';
  $('contacts').replaceChildren();const title=document.createElement('h3');title.textContent='3. Contact your lawmakers';$('contacts').append(title);
  const who=!local?'your U.S. representative and U.S. senators':draftState==='DC'?'your ward councilmember and the at-large D.C. Council members':'your '+names.get(draftState)+' state senator and state representative';
  const p=document.createElement('p');p.textContent='For this '+(local?names.get(draftState):'federal')+' policy request, use '+who+'. Ask the office to explain its role and direct agency questions to the responsible program.';$('contacts').append(p);
  const routes=ohio?[['Find your Ohio senator','https://ohiosenate.gov/members/district-map'],['Find your Ohio representative','https://www.ohiohouse.gov/members/directory']]:[[local?'Find your state and local elected officials':'Find your U.S. representative and senators','https://www.usa.gov/elected-officials']];
  for(const [label,url] of routes){const a=document.createElement('a');a.textContent=label+' (new tab)';a.href=url;a.target='_blank';a.rel='noopener';$('contacts').append(a,document.createElement('br'));}
  const list=document.createElement('ol');list.className='send-checklist';for(const text of ['Copy your message, then open the official contact link.','Choose your lawmaker. Paste the subject and message into their form and add the details their office requests.','Review and send on the official site. Keep any confirmation and note when you want to follow up.']){const li=document.createElement('li');li.textContent=text;list.append(li);}$('contacts').append(list);
  const alternate=document.createElement('p');alternate.className='small';alternate.textContent='You can also use the message for a phone call, relay call or printed letter. Choose the method that works for you.';$('contacts').append(alternate);
 }
 function topicURL(){const {topic,scope,format,state}=selection();const u=new URL(location.href);u.search='';u.hash='compose';u.searchParams.set('topic',topic.id);u.searchParams.set('state',state);u.searchParams.set('scope',scope);u.searchParams.set('format',format);return u;}
 function changed(){const {topic,scope,state}=selection();$('selection-status').textContent='Selected: '+topic.title+' · '+scopeLabel(scope,state)+'. Your current message, subject and contact routes are unchanged. Choose Build message to replace them.';const u=topicURL();u.hash=location.hash;history.replaceState(null,'',u);}
 // One state choice drives the problem links, the builder and the topic cards.
 function applyState(s){
  $('start-state').value=s;$('compose-state').value=s;$('scope').querySelector('option[value="state"]').textContent=stateLabel(s);
  document.querySelectorAll('[data-barrier]').forEach(a=>{const u=new URL(a.href);u.searchParams.set('state',s);a.href=u.href;});
  const u=new URL($('start-state-policy').href);u.searchParams.set('state',s);$('start-state-policy').href=u.href;
  $('start-guide').href='./?state='+s;
  const place=s==='DC'?'District of Columbia':names.get(s);
  document.querySelectorAll('[data-state-ask-title]').forEach(h=>h.textContent='Proposed '+place+' request');
  document.querySelectorAll('[data-state-ask]').forEach(p=>{const t=topics.get(p.dataset.stateAsk);if(t)p.textContent=ask(t,'state',s);});
 }
 function load(){const p=new URLSearchParams(location.search);applyState(validState(p.get('state')));$('topic').value=topics.has(p.get('topic'))?p.get('topic'):'repair';$('scope').value=p.get('scope')==='US'?'US':'state';$('format').value=p.get('format')==='letter'?'letter':'short';}
 function build(focus=true){
  const {topic,scope,format,state}=selection();draftTopic=topic.id;draftScope=scope;draftFormat=format;draftState=state;const story=$('experience').value.trim();
  const intro=format==='letter'?'I am asking you to help people with disabilities maintain their independence and participate in everyday life.\n\n':'';
  const close=format==='letter'?'Please explain what steps your office can take, which agency is responsible and how people with disabilities can participate in the next decision.':'Please tell me what your office can do and how people with disabilities can take part.';
  $('subject').value=topic.subject;$('message').value=greeting(scope,state)+'\n\n'+intro+ask(topic,scope,state)+(story?'\n\n'+story:'')+'\n\n'+close+'\n\nThank you.';
  contacts();count();$('selection-status').textContent='Message rebuilt from your current choices. Review and edit it before sharing.';$('action-status').textContent='';if(focus)$('message').focus();
 }
 $('start-state').addEventListener('change',()=>{applyState($('start-state').value);changed();});
 $('compose-state').addEventListener('change',()=>{applyState($('compose-state').value);changed();});
 $('build').addEventListener('click',()=>build());for(const id of ['topic','scope','format'])$(id).addEventListener('change',changed);$('message').addEventListener('input',count);
 document.querySelectorAll('[data-topic]').forEach(a=>a.addEventListener('click',()=>{$('topic').value=a.dataset.topic;changed();$('topic').focus();}));
 function hasText(){if($('message').value.trim())return true;$('action-status').textContent='Build or write a message first.';return false;}
 async function copyField(id,label){if(!$(id).value.trim()){$('action-status').textContent='Build or write a '+label.toLowerCase()+' first.';return;}try{await navigator.clipboard.writeText($(id).value);$('action-status').textContent=label+' copied. Paste it into the official contact form when ready.';}catch{$(id).focus();$(id).select();$('action-status').textContent='Select the '+label.toLowerCase()+' and use your device’s Copy command.';}}
 $('copy').addEventListener('click',()=>copyField('message','Message'));$('copy-subject').addEventListener('click',()=>copyField('subject','Subject'));
 $('share-topic').addEventListener('click',async()=>{const url=topicURL().href;try{await navigator.clipboard.writeText(url);$('share-status').textContent='Topic link copied. It includes only the topic, state, lawmaker level and message length.';}catch{$('share-status').textContent='Copy this topic link: '+url;}});
 $('download').addEventListener('click',()=>{if(!hasText())return;const url=URL.createObjectURL(new Blob([$('message').value],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='disability-advocacy-message.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('action-status').textContent='Text download prepared.';});
 const printText=()=>{$('print-letter').textContent=$('message').value;};window.addEventListener('beforeprint',printText);
 $('print').addEventListener('click',()=>{if(!hasText())return;printText();window.print();});
 $('clear').addEventListener('click',()=>{$('experience').value='';$('message').value='';$('subject').value='';$('print-letter').textContent='';count();$('action-status').textContent='Your experience, subject and message have been cleared.';});
 window.addEventListener('popstate',()=>{load();changed();});load();build(false);
})();
