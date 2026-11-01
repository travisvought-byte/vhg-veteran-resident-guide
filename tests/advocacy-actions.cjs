const assert=require('node:assert/strict'),fs=require('node:fs'),{JSDOM}=require('jsdom');
function page(file,script,query=''){
 const dom=new JSDOM(fs.readFileSync(file,'utf8'),{url:'https://example.org/'+file+query,runScripts:'outside-only'}),w=dom.window,d=w.document,downloads=[];
 w.Blob=Blob;w.URL.createObjectURL=b=>{downloads.push(b);return 'blob:test'};w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){};w.print=()=>{};
 w.eval(fs.readFileSync(script,'utf8'));const $=id=>d.getElementById(id);return {dom,w,d,$,downloads,set:(id,v)=>{$(id).value=v;$(id).dispatchEvent(new w.Event('change'));}};
}
(async()=>{
 const a=page('disability-advocacy.html','assets/disability-advocacy.js','?state=PA');
 assert.equal(a.$('start-state').value,'PA');assert.equal(a.$('start-state').options.length,51);assert.equal(a.d.querySelectorAll('.problem-grid>a').length,6);
 for(const state of [...a.$('start-state').options].map(o=>o.value)){
  a.set('start-state',state);for(const link of a.d.querySelectorAll('[data-barrier]')){const u=new URL(link.href);assert.equal(u.searchParams.get('state'),state);assert(u.searchParams.get('barrier'));assert(!u.search.includes('story'));}
  assert.equal(new URL(a.$('start-state-policy').href).searchParams.get('state'),state);
 }
 a.set('start-state','AL');assert.equal(new URL(a.$('start-guide').href).search,'');a.dom.window.close();
 const p=page('mobility-rights.html','assets/mobility-routes.js','?state=PA&barrier=payer&request=appeal'),{$,set,w,d}=p;
 assert.equal($('request-type').value,'appeal');assert($('request-guidance').textContent.includes('does not file an appeal'));assert($('route-result').textContent.includes('YOUR NEXT ACTION'));assert($('route-result').textContent.includes('What to have ready'));
 set('route-payer','medicare');$('show-route').click();assert($('request-guidance').querySelector('a').href.includes('/appeals'));
 $('story-when').value='Three weeks';$('story-impact').value='Cannot get to work. <img src=x onerror=bad()>';$('story-tried').value='Supplier said it is pending.';$('route-story').value='Please explain my options.';
 const outcome='Find the correct appeal process and deadline';set('route-goal',outcome);$('build-request').click();assert($('route-message').value.includes('not a submitted appeal'));for(const part of ['Three weeks','Cannot get to work','Supplier said',outcome])assert($('route-message').value.includes(part));assert($('route-draft-contacts').textContent.includes('Medicare appeal instructions'));
 const edited='My final edited request\n<em>literal text</em>';$('route-message').value=edited;set('request-type','constituent');assert.equal($('route-message').value,edited);assert($('route-draft-contacts').textContent.includes('Medicare appeal instructions'));$('build-request').click();assert($('route-message').value.startsWith('Dear congressional constituent-services team'));assert($('route-draft-contacts').textContent.includes('U.S. representative'));
 set('route-payer','medicaid');set('route-state','OH');$('show-route').click();set('request-level','state');$('build-request').click();assert($('route-draft-contacts').textContent.includes('Ohio senator'));
 set('request-type','policy');$('build-request').click();assert($('route-message').value.startsWith('Dear Ohio state lawmaker'));set('request-type','help');$('build-request').click();assert($('route-message').value.startsWith('To the responsible provider'));
 set('route-issue','transit');$('show-route').click();assert.equal($('route-goal').value,'');set('request-type','complaint');assert($('request-guidance').textContent.includes('FTA encourages'));$('build-request').click();assert($('route-message').value.includes('not a formally filed complaint'));assert($('route-draft-contacts').textContent.includes('FTA:'));
 $('record-contact').value='Example transit office';$('record-date').value='2026-10-20';$('record-next').value='2026-11-05';$('record-response').value='Awaiting a response. <script>bad()</script>';$('route-message').value=edited;
 $('record-download').click();const record=await p.downloads.at(-1).text();for(const text of ['MOBILITY ACTION RECORD','What to have ready','Example transit office','2026-10-20','2026-11-05',edited,'Timing: Three weeks','not filing deadlines'])assert(record.includes(text));
 $('record-print').click();assert.equal($('route-print-letter').textContent,record);assert.equal($('route-print-letter').children.length,0);
 let copied;Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async v=>{copied=v}}});$('route-share').click();await new Promise(r=>setTimeout(r,0));assert.deepEqual([...new URL(copied).searchParams.keys()],['state','barrier']);for(const privateText of ['Example','2026-10-20','2026-11-05','script','Three'])assert(!copied.includes(privateText));
 set('route-state','NY');$('build-followup').click();assert.equal($('route-message').value,edited);assert($('record-status').textContent.includes('Apply your changed'));$('show-route').click();assert.equal($('route-message').value,edited);$('record-download').click();const mixed=await p.downloads.at(-1).text();assert(mixed.includes('New York'));assert(mixed.includes('Current message: Ohio'));assert(mixed.includes('may differ'));
 $('build-followup').click();assert($('route-subject').value.startsWith('Follow-up:'));assert($('route-message').value.includes('Example transit office'));assert($('route-message').value.includes('2026-10-20'));assert($('route-message').value.includes('Previous response'));assert($('route-draft-context').textContent.includes('New York'));assert.equal(d.querySelectorAll('#route-message script').length,0);
 assert.equal(w.localStorage.length+w.sessionStorage.length,0);$('route-clear').click();for(const id of ['route-story','route-subject','route-message','story-when','story-impact','story-tried','record-contact','record-date','record-next','record-response'])assert.equal($(id).value,'');assert.equal($('route-print-letter').textContent,'');p.dom.window.close();
 const invalid=page('mobility-rights.html','assets/mobility-routes.js','?state=__proto__&barrier=bad&request=toString');assert.equal(invalid.$('route-state').value,'OH');assert.equal(invalid.$('request-type').value,'help');invalid.dom.window.close();
 console.log('PASS advocacy actions: 51-state entry links, five request routes, Medicare and state casework contacts, guided stories and outcomes, exact record exports, pinned drafts, follow-up guards, privacy and clearing.');
})();
