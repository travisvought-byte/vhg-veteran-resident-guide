// Browser checks for on-demand state loading: only the needed state downloads,
// deep links wait for their state, and a failed download is reported and recoverable.
const assert=require('node:assert/strict'),path=require('node:path'),fs=require('fs'),http=require('http');
const {chromium}=require(process.env.GUIDE_PLAYWRIGHT||'playwright');
const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'..','states/registry.json'),'utf8'));
(async()=>{
 const server=http.createServer((req,res)=>{let file=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(file.endsWith('/'))file+='index.html';const target=path.join(__dirname,'..',file);try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream');res.end(fs.readFileSync(target))}catch{res.statusCode=404;res.end()}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+server.address().port+'/';
 const browser=await chromium.launch({headless:true});
 const ready=(page,code)=>page.waitForFunction(s=>document.documentElement.dataset.edition===s,code);
 const editionsRequested=page=>{const seen=[];page.on('request',r=>{const m=new URL(r.url()).pathname.match(/assets\/editions\/(\w+)\.js$/);if(m)seen.push(m[1])});return seen};

 // Default view downloads the base state only.
 let page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let seen=editionsRequested(page);await page.goto(base);await ready(page,registry[0].code);
 assert.deepEqual(seen,[registry[0].code.toLowerCase()],'only the base state downloads on first visit');
 // Switching downloads that state once; switching back does not download again.
 const second=registry[1].code;await page.selectOption('#edition-state',second);await ready(page,second);
 await page.selectOption('#edition-state',registry[0].code);await ready(page,registry[0].code);
 await page.selectOption('#edition-state',second);await ready(page,second);
 assert.deepEqual(seen,[registry[0].code,second].map(c=>c.toLowerCase()),'each state downloads once');
 assert.equal(await page.locator('#county option').count(),registry[1].counties+1);
 assert.deepEqual(errors,[]);await page.close();

 // A deep link to any registered state restores that state and county.
 for(const s of registry.slice(1)){
  page=await browser.newPage();const county=JSON.parse(fs.readFileSync(path.join(__dirname,'..',s.offices),'utf8'))[0].county;
  await page.goto(base+'?state='+s.code+'&county='+encodeURIComponent(county));await ready(page,s.code);
  assert.equal(await page.locator('#county').inputValue(),county,s.code+' deep-linked county');
  assert((await page.locator('#county-panel').textContent()).includes(county+' County'));await page.close();
 }

 // A failed download keeps the current state, explains the problem and allows a retry.
 page=await browser.newPage();await page.goto(base);await ready(page,registry[0].code);
 const target=registry[registry.length-1];let block=true;
 await page.route('**/assets/editions/'+target.code.toLowerCase()+'.js*',route=>block?route.abort():route.continue());
 await page.selectOption('#edition-state',target.code);
 await page.waitForFunction(()=>/could not load/.test(document.getElementById('edition-status').textContent));
 assert.equal(await page.locator('#edition-state').inputValue(),registry[0].code,'menu returns to the working state');
 assert.equal(await page.evaluate(()=>document.documentElement.dataset.edition),registry[0].code);
 block=false;await page.selectOption('#edition-state',target.code);await ready(page,target.code);
 assert.equal(await page.locator('#edition-status').textContent(),'');
 assert.equal(await page.locator('#county option').count(),target.counties+1);

 // An unknown state in a shared link falls back to the base state without errors.
 await page.goto(base+'?state=ZZ');await ready(page,registry[0].code);
 await browser.close();server.close();
 console.log('PASS: base-only first download, one download per state, deep links for every state, failed-download recovery and unknown-state fallback.');
})().catch(e=>{console.error(e);process.exit(1)});
