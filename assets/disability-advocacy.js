'use strict';
(() => {
 document.documentElement.classList.add('advocacy-ready');
 const data=JSON.parse(document.getElementById('advocacy-data').textContent),$=id=>document.getElementById(id);
 const scopes={OH:'Ohio state lawmakers',US:'Federal lawmakers'},topics=new Map(data.topics.map(t=>[t.id,t]));
 let draftTopic='repair',draftScope='OH';
 function selection(){return {topic:topics.get($('topic').value),scope:$('scope').value};}
 function contacts(){
  const ohio=draftScope==='OH';$('draft-context').textContent='Current draft: '+topics.get(draftTopic).title+' · '+scopes[draftScope]+'.';
  $('contacts').replaceChildren();const title=document.createElement('h3');title.textContent='Take your message to the right office';$('contacts').append(title);
  const p=document.createElement('p');p.textContent=ohio?'For this Ohio policy request, use your state senator and state representative. Ask the office to explain its role and direct agency questions to the responsible program.':'For this federal policy request, use your U.S. representative and U.S. senators. Ask the office to explain its role and direct agency questions to the responsible program.';$('contacts').append(p);
  const routes=ohio?[['Find your Ohio senator','https://ohiosenate.gov/members/district-map'],['Find other elected officials, including your state representative','https://www.usa.gov/elected-officials']]:[['Find your U.S. representative and senators','https://www.usa.gov/elected-officials']];
  for(const [label,url] of routes){const a=document.createElement('a');a.textContent=label;a.href=url;$('contacts').append(a,document.createElement('br'));}
 }
 function changed(){const {topic,scope}=selection();$('selection-status').textContent='Selected: '+topic.title+' · '+scopes[scope]+'. Your current message and its contact routes are unchanged. Choose Build message to replace it.';const u=new URL(location.href);u.search='';u.searchParams.set('topic',topic.id);u.searchParams.set('scope',scope);history.replaceState(null,'',u);}
 function load(){const p=new URLSearchParams(location.search);$('topic').value=topics.has(p.get('topic'))?p.get('topic'):'repair';$('scope').value=p.get('scope')==='US'?'US':'OH';}
 $('build').addEventListener('click',()=>{const {topic,scope}=selection();draftTopic=topic.id;draftScope=scope;const story=$('experience').value.trim();$('message').value=(scope==='OH'?'Dear Ohio state lawmaker,':'Dear member of Congress,')+'\n\nI am asking you to help people with disabilities maintain their independence and participate in everyday life.\n\n'+topic.asks[scope]+(story?'\n\n'+story:'')+'\n\nPlease explain what steps your office can take, which agency is responsible and how people with disabilities can participate in the next decision.\n\nThank you.';contacts();$('selection-status').textContent='Message rebuilt from your current choices. Review and edit it before sharing.';$('action-status').textContent='';});
 $('topic').addEventListener('change',changed);$('scope').addEventListener('change',changed);
 document.querySelectorAll('[data-topic]').forEach(a=>a.addEventListener('click',()=>{$('topic').value=a.dataset.topic;changed();$('topic').focus();}));
 function hasText(){if($('message').value.trim())return true;$('action-status').textContent='Build or write a message first.';return false;}
 $('copy').addEventListener('click',async()=>{if(!hasText())return;try{await navigator.clipboard.writeText($('message').value);$('action-status').textContent='Message copied. Paste it into the official contact form when ready.';}catch{$('message').focus();$('message').select();$('action-status').textContent='Select the message and use your device’s Copy command.';}});
 $('download').addEventListener('click',()=>{if(!hasText())return;const url=URL.createObjectURL(new Blob([$('message').value],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='disability-advocacy-message.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('action-status').textContent='Text download prepared.';});
 const printText=()=>{$('print-letter').textContent=$('message').value;};window.addEventListener('beforeprint',printText);
 $('print').addEventListener('click',()=>{if(!hasText())return;printText();window.print();});
 $('clear').addEventListener('click',()=>{$('experience').value='';$('message').value='';$('print-letter').textContent='';$('action-status').textContent='Your experience and message have been cleared.';});
 window.addEventListener('popstate',()=>{load();changed();});load();if($('topic').value!=='repair'||$('scope').value!=='OH')changed();
})();
