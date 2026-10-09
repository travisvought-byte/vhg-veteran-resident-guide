// Real browser checks for the public single-page interface and caregiver workflow.
const assert=require('node:assert/strict'),path=require('node:path');
const {chromium}=require(process.env.GUIDE_PLAYWRIGHT|| (process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES?process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES+'/playwright':'playwright'));
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const fs=require('fs'),http=require('http');let server;
 if(!process.env.GUIDE_TEST_URL){server=http.createServer((req,res)=>{let file=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(file.endsWith('/'))file+='index.html';const target=path.join(__dirname,'..',file);try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream');res.end(fs.readFileSync(target))}catch{res.statusCode=404;res.end()}});await new Promise(r=>server.listen(0,'127.0.0.1',r))}
 const base=process.env.GUIDE_TEST_URL||'http://127.0.0.1:'+server.address().port+'/';
 await page.goto(base);await page.waitForFunction(()=>document.querySelector('#count').textContent.length>0);
 const expected={OH:88,PA:67,NY:62,MI:83,KY:120};
 for(const [state,n] of Object.entries(expected)){
  await page.selectOption('#edition-state',state);
  assert.equal(await page.locator('#county option').count(),n+1);
  assert(new URL(page.url()).searchParams.get('state')===state);
  assert(new URL(page.url()).pathname.endsWith('index.html')||new URL(page.url()).pathname.endsWith('/'));
  const counties=await page.locator('#county option').evaluateAll(nodes=>nodes.slice(1).map(n=>n.value));
  for(const county of counties){await page.selectOption('#county',county);assert((await page.locator('#county-panel').textContent()).includes(county+' County'));assert(await page.locator('#results article').count()>0)}
  await page.click('#helper-open');await page.selectOption('#helper-person','veteran');
  for(const need of ['benefits','daily','housing','accessibility','rights','crisis']){await page.selectOption('#helper-need',need);assert((await page.locator('#helper-next').textContent()).length>80);assert(await page.locator('#helper-next .contact-grid article').count()>0)}
  await page.selectOption('#helper-person','other');await page.selectOption('#helper-need','benefits');assert(!(await page.locator('#helper-next').textContent()).includes('County veterans office'));
  await page.click('#helper-resources');assert(await page.locator('#seniors-guide').isVisible());
  await page.selectOption('#helper-person','survivor');await page.selectOption('#helper-need','accessibility');await page.click('#helper-resources');assert.equal(await page.locator('#access-veteran').inputValue(),'no');assert.equal(await page.locator('#access-home').inputValue(),'facility');
  await page.click('#helper-close');await page.click('[data-route="all"]');assert(!(await page.locator('#helper-guide').isVisible()));
  await page.selectOption('#county','');
 }
 assert.deepEqual(errors,[]);
 // A state change clears stale county/search values without navigation or listener accumulation.
 await page.selectOption('#edition-state','OH');await page.selectOption('#county','Morrow');await page.fill('#search','Medicaid');await page.selectOption('#edition-state','PA');assert.equal(await page.locator('#county').inputValue(),'');assert.equal(await page.locator('#search').inputValue(),'');
 await page.goto(base+'?state=NY&county=Bronx&view=rights');assert.equal(await page.locator('#edition-state').inputValue(),'NY');assert.equal(await page.locator('#county').inputValue(),'Bronx');
 // Mobile layout and printable caregiver handoff.
 await page.setViewportSize({width:390,height:844});await page.click('#helper-open');await page.selectOption('#helper-person','unknown');await page.selectOption('#helper-need','daily');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.evaluate(()=>{window.print=()=>{window.__printed=true}});await page.click('#helper-print');assert(await page.evaluate(()=>window.__printed&&document.body.classList.contains('print-helper')));
 await page.emulateMedia({media:'print'});assert(await page.locator('#helper-guide').isVisible());assert(!(await page.locator('#directory').isVisible()));assert(await page.locator('.helper-paper').isVisible());
 await page.emulateMedia({media:'screen'});await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
 await page.locator('#helper-guide').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(require('os').tmpdir(),'vhg-helper-mobile.png')});
 await page.setViewportSize({width:1280,height:900});await page.screenshot({path:path.join(require('os').tmpdir(),'vhg-helper-desktop.png'),fullPage:false});
 if(server){await page.goto(base+'ky.html?county=Christian&view=rights');await page.waitForFunction(()=>document.querySelector('#count')?.textContent.length>0);assert.equal(await page.locator('#edition-state').inputValue(),'KY');assert.equal(await page.locator('#county').inputValue(),'Christian')}
 // Bingo ZIP search, shared links, mobile layout and submission prefill.
 await page.clock.install({time:new Date('2026-10-09T12:00:00Z')});
 await page.goto(base+'bingo.html?zip=43334&radius=25&day=4');
 await page.waitForFunction(()=>document.querySelector('#count').textContent.includes('closest first'));
 assert.equal(await page.locator('#bingo-zip').inputValue(),'43334');
 assert.equal(await page.locator('#bingo-day').inputValue(),'4');assert(await page.locator('#marengo-legion-710').isVisible());assert.equal(await page.locator('#cardington-legion-97').count(),0);
 assert((await page.locator('#count').textContent()).includes('within 25 miles of 43334'));
 const distances=await page.locator('#listings article .badge').allTextContents();assert(distances.some(t=>t.includes('miles away')));
 await page.selectOption('#bingo-radius','10');assert.equal(new URL(page.url()).searchParams.get('radius'),'10');
 await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.locator('#marengo-legion-710 [data-submit]').click();assert.equal(await page.locator('#submit-venue').inputValue(),'American Legion Post 710');
 await page.click('#bingo-reset');assert.equal(await page.locator('#bingo-zip').inputValue(),'');assert.equal(await page.locator('#listings article').count(),732);assert.equal(await page.locator('#bingo-day').inputValue(),'');
 await page.selectOption('#bingo-kind','centers');assert.equal(await page.locator('#listings article').count(),15);assert((await page.locator('#listings').textContent()).includes('Centerburg Senior Services'));await page.selectOption('#bingo-kind','meals');assert.equal(await page.locator('#listings article').count(),10);await page.selectOption('#bingo-kind','');
 await page.selectOption('#bingo-day','2');assert.equal(new URL(page.url()).searchParams.get('day'),'2');assert((await page.locator('#northmor-music-bingo').textContent()).includes('Tuesday, Oct 20, 2026'));await page.reload();assert.equal(await page.locator('#bingo-day').inputValue(),'2');await page.click('#bingo-reset');
 await page.fill('#bingo-zip','00000');await page.locator('#bingo-nearby button').click();assert((await page.locator('#nearby-status').textContent()).includes('valid five-digit'));
 await page.emulateMedia({media:'print'});assert(!(await page.locator('#bingo-zip').isVisible()));assert(!(await page.locator('#bingo-day').isVisible()));assert(!(await page.locator('#bingo-submit').isVisible()));await page.emulateMedia({media:'screen'});
 assert.deepEqual(errors,[]);await browser.close();if(server)server.close();console.log('PASS: one public view, all 420 county panels, five-state switching, caregiver routes, deep links, legacy redirect, mobile width and print handoff.');
})().catch(e=>{console.error(e);process.exit(1)});
