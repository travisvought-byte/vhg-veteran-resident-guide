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
  const homePage=fs.readFileSync(path.join(root,"index.html"),"utf8");
  const sourceTemplate=fs.readFileSync(path.join(root,"templates/guide.html"),"utf8");
  assert(homePage.includes('<a class="jump" href="assistant/">Guided assistance (beta)</a>'));
  assert(sourceTemplate.includes('<a class="jump" href="assistant/">Guided assistance (beta)</a>'));
  await page.goto("http://127.0.0.1:"+server.address().port+"/assistant/");
  await page.waitForFunction(()=>document.querySelector("#feedback").textContent.includes("Ready"));
  assert.equal(await page.locator("#state").inputValue(),"OH");
  assert.equal(await page.locator("#county option").count(),89);
  assert.equal(await page.locator("#state option").count(),11);
  await page.selectOption("#person","veteran");
  await page.selectOption("#county","Muskingum");
  await page.fill("#message","Disabled veteran needs a wheelchair ramp and housing assistance.");
  await page.click("#find");await page.locator("#results").waitFor({state:"visible"});
  assert((await page.locator("#office").textContent()).includes("Muskingum"));
  assert((await page.locator("#resources").textContent()).includes("Source reviewed"));
  assert((await page.locator("#resources").textContent()).includes("Official application or intake:"));
  assert((await page.locator("#resources").textContent()).includes("How to start"));
  assert(await page.locator("#resources a[href^='https://']").count()>0);
  await page.fill("#message","HISA home improvements structural alterations ramp accessibility SecretInputMarker7849");
  await page.click("#find");await page.locator("#results").waitFor({state:"visible"});
  const hisaCard=page.locator('#resources article[data-program-id="va-hisa"]');
  assert(await hisaCard.count()===1,"Expected HISA among relevant results");
  await hisaCard.locator("summary").click();
  const hisaStatus=hisaCard.locator(".checklist-status");
  assert((await hisaStatus.textContent()).startsWith("0 of "));
  await hisaCard.locator(".prep-checkbox").first().check();
  assert((await hisaStatus.textContent()).startsWith("1 of "));
  await hisaCard.getByRole("button",{name:"Clear checkmarks"}).click();
  assert((await hisaStatus.textContent()).startsWith("0 of "));
  assert((await hisaCard.textContent()).includes("Submit the HISA application package"));
  // The print button must build an isolated, non-persistent, one-page document.
  await page.evaluate(()=>{window.print=()=>{document.body.dataset.printInvoked="true"}});
  await hisaCard.getByRole("button",{name:"Print one-page handoff"}).click();
  assert.equal(await page.locator("body").getAttribute("data-print-invoked"),"true");
  assert.equal(await page.locator("#print-handoff .handoff-sheet").count(),1);
  assert((await page.locator("#print-handoff").textContent()).includes("Form 10-0103"));
  assert(!(await page.locator("#print-handoff").textContent()).includes("SecretInputMarker7849"));
  const printPageCount=async()=>{
    const pdf=await page.pdf({format:"Letter",preferCSSPageSize:true,printBackground:true});
    return (pdf.toString("latin1").match(/\/Type\s*\/Page\b/g)||[]).length;
  };
  assert.equal(await printPageCount(),1,"HISA must print to one letter page");
  // Rebuild all four program handoffs from actual published records.
  for(const [program,who,query] of [
    ["va-hisa","veteran","wheelchair ramp"],
    ["va-sah","veteran","special adapted housing ramp"],
    ["va-sha","veteran","special housing adaptation ramp"],
    ["ohio-waiver-home-modifications","other","wheelchair ramp home modification"]
  ]){
    const details=await page.evaluate(async ({program,who,query})=>{
      const [{createPlan},{buildHandoff}]=await Promise.all([
        import("/assistant/engine.mjs"),import("/assistant/handoff.mjs")
      ]);
      const resources=await (await fetch("/prototype-data.json")).json();
      const plan=createPlan({state:"OH",county:"Morrow",person:who,message:query,
        resources:resources.filter(r=>r.program_id===program),
        counties:await(await fetch("/data/public/ohio-county-veterans-offices.json")).json()
      });
      if(plan.recommendations.length!==1)return {hasResource:false};
      const sheet=buildHandoff(document,plan,plan.recommendations[0]);
      document.getElementById("print-handoff").replaceChildren(sheet);
      return {
        hasResource:true,
        steps:sheet.querySelectorAll(".handoff-task").length,
        name:sheet.querySelector("h1").textContent,
        urls:sheet.querySelectorAll("a[href^='https://']").length,
        containsTypedMessage:sheet.textContent.includes(query),
        state:sheet.textContent.includes("Morrow County")
      };
    },{program,who,query});
    assert(details.hasResource,program+" should match the sample query");
    assert(details.steps>=6,program+" should have substantive checklist");
    assert(details.urls>=2,program+" should link to official applications and sources");
    assert(details.state,program+" location should be in handoff");
    assert(!details.containsTypedMessage,program+" must omit typed request text");
    assert.equal(await printPageCount(),1,program+" must print to one US Letter page");
  }
  await page.click("#draft");await page.locator("#draft-container").waitFor({state:"visible"});
  assert((await page.locator("#email-draft").textContent()).includes("Muskingum County"));
  await page.selectOption("#person","other");
  await page.fill("#message","Need veteran benefits and a wheelchair ramp.");
  await page.click("#find");await page.locator("#results").waitFor({state:"visible"});
  assert.equal((await page.locator("#office").textContent()).trim(),"");
  assert(!(await page.locator("#resources").textContent()).includes("VA Home Improvements and Structural Alterations"));
  await page.selectOption("#state","PA");
  await page.waitForFunction(()=>document.querySelector("#feedback").textContent.includes("Ready"));
  assert.equal(await page.locator("#county option").count(),68);
  assert(await page.locator("#results").isHidden());
  await page.selectOption("#person","unknown");
  await page.fill("#message","I am suicidal and I need help.");
  await page.click("#find");await page.locator("#crisis").waitFor({state:"visible"});
  assert((await page.locator("#crisis").textContent()).includes("988"));
  await page.selectOption("#state","CA");
  await page.waitForFunction(()=>document.querySelector("#feedback").textContent.includes("Ready"));
  assert.equal(await page.locator("#county option").count(),59);
  await page.setViewportSize({width:375,height:812});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  console.log("Assistance browser pilot: OH/PA, draft, urgent guidance, responsive layout passed.");
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.error(e);process.exitCode=1});
