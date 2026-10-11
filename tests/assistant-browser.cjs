const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),http=require("node:http");
const {chromium}=require("playwright");
(async()=>{
 const root=path.resolve(__dirname,"..");
 const server=http.createServer((req,res)=>{
   let requested=decodeURIComponent(new URL(req.url,"http://localhost").pathname);
   if(requested.endsWith("/"))requested+="index.html";
   const target=path.resolve(root,"."+requested);
   if(!target.startsWith(root+path.sep)){res.writeHead(403);return res.end()}
   const ct=target.endsWith(".mjs")||target.endsWith(".js")?"text/javascript":target.endsWith(".json")?"application/json":target.endsWith(".html")?"text/html":"text/plain";
   try{res.setHeader("Content-Type",ct);res.end(fs.readFileSync(target))}
   catch{res.writeHead(404);res.end()}
 });
 await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage();const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto("http://127.0.0.1:"+server.address().port+"/assistant/");
  await page.waitForFunction(()=>document.querySelector("#feedback").textContent.includes("Ready"));
  assert.equal(await page.locator("#state").inputValue(),"OH");
  assert.equal(await page.locator("#county option").count(),89);
  await page.selectOption("#county","Muskingum");
  await page.fill("#message","Disabled veteran needs a wheelchair ramp and housing assistance.");
  await page.click("#find");await page.locator("#results").waitFor({state:"visible"});
  assert((await page.locator("#office").textContent()).includes("Muskingum"));
  assert((await page.locator("#resources").textContent()).includes("Source reviewed"));
  await page.click("#draft");await page.locator("#draft-container").waitFor({state:"visible"});
  assert((await page.locator("#email-draft").textContent()).includes("Muskingum County"));
  await page.selectOption("#state","PA");
  await page.waitForFunction(()=>document.querySelector("#feedback").textContent.includes("Ready"));
  assert.equal(await page.locator("#county option").count(),68);
  assert(await page.locator("#results").isHidden());
  await page.fill("#message","I am suicidal and I need help.");
  await page.click("#find");await page.locator("#crisis").waitFor({state:"visible"});
  assert((await page.locator("#crisis").textContent()).includes("988"));
  await page.setViewportSize({width:375,height:812});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  console.log("Assistance browser pilot: OH/PA, draft, urgent guidance, responsive layout passed.");
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.error(e);process.exitCode=1});
