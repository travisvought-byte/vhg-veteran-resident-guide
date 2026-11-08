const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const server=http.createServer((req,res)=>{const file=path.join(root,decodeURIComponent(new URL(req.url,'http://localhost').pathname));try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file))}catch{res.statusCode=404;res.end()}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}:{});
 try{
  const base='http://127.0.0.1:'+server.address().port+'/family-guide.html';
  const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));await page.route('**/gc.zgo.at/**',r=>r.abort());
  await page.goto(base);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.click('.stage[data-stage=early]');
  assert(await page.locator('#r-oh-help-me-grow').isVisible());assert(!(await page.locator('#r-oh-jpsn').isVisible()));
  await page.selectOption('#county','Knox');assert((await page.locator('#county-result').innerText()).includes('740-397-4656'));
  assert(page.url().includes('county=Knox')&&page.url().includes('stage=early'));
  await page.selectOption('#state','MI');assert(!(await page.locator('#county-wrap').isVisible()));
  assert((await page.locator('#anchor-list').innerText()).includes('Disability Rights Michigan'));
  assert(await page.locator('#r-cdc-find-ei').isVisible());assert(!(await page.locator('#r-oh-help-me-grow').isVisible()));
  await page.emulateMedia({media:'print'});assert(!(await page.locator('header').isVisible()));assert(!(await page.locator('.stages').isVisible()));assert(await page.locator('#r-cdc-find-ei').isVisible());await page.emulateMedia({media:'screen'});
  await page.setViewportSize({width:1280,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);assert.deepEqual(errors,[]);
  const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}}),np=await plain.newPage();await np.goto(base);
  assert(await np.locator('noscript').first().isVisible());
  const total=JSON.parse(fs.readFileSync(path.join(root,'data/family-guide.json'),'utf8')).resources.length;
  assert.equal(await np.locator('.resource:visible').count(),total);
  console.log('PASS family guide browser: mobile/desktop width, stage and county routing, state switch, print layout, no storage and no-JS listings.');
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})();
