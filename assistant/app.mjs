import {STATES,createPlan,planToEmail,isUrgent} from "./engine.mjs";

const $=id=>document.getElementById(id);
import {STATE_FILES as fileNames} from "./state-files.mjs";
const cache=new Map();let plan=null,requestVersion=0;
async function load(state){
  if(!fileNames[state])throw new Error("Unsupported state.");
  if(cache.has(state))return cache.get(state);
  const result=await Promise.all(fileNames[state].map(async file=>{
    const response=await fetch(new URL("../"+file, import.meta.url),{cache:"no-store"});
    if(!response.ok)throw new Error("Could not load the resource guide's public data.");
    return response.json();
  }));
  if(!Array.isArray(result[0])||!Array.isArray(result[1]))throw new Error("Guide data has an unexpected format.");
  cache.set(state,result);return result;
}
function textNode(name,value){const el=document.createElement(name);el.textContent=String(value||"");return el}
function para(where,value){where.append(textNode("p",value))}
function safeLink(where,title,url){
  if(!url)return;
  try{const u=new URL(url,location.href);if(!["https:","http:"].includes(u.protocol))return;
    const a=textNode("a",title);a.href=u.href;a.target="_blank";a.rel="noopener noreferrer";where.append(a);
  }catch{}
}
function phoneLink(where,phone){
  if(!phone)return;
  const a=textNode("a",phone);a.href="tel:"+phone.replace(/[^0-9+]/g,"");where.append(a);
}
async function refreshCounties(){
 const state=$("state").value,version=++requestVersion,county=$("county");
 county.replaceChildren(new Option("Loading counties…",""));county.disabled=true;
 $("feedback").textContent="Loading "+STATES[state]+" county contacts.";
 $("results").hidden=true;$("draft-container").hidden=true;$("crisis").hidden=true;
 try{
   const [,counties]=await load(state);if(version!==requestVersion)return;
   county.replaceChildren(new Option("Statewide resources only",""));
   for(const row of counties){if(!row.county)continue;county.append(new Option(row.county+" County",row.county))}
   county.disabled=false;$("feedback").textContent="Ready. Enter a general description of the need.";
 }catch(e){if(version!==requestVersion)return;$("feedback").textContent=e.message;county.replaceChildren(new Option("Unavailable",""))}
}
function showOffice(office){
 const node=$("office");node.replaceChildren();
 if(!office)return;
 const section=textNode("article","");section.className="resource";section.append(textNode("h3",office.name));
 if(office.phone){section.append(textNode("span","Published telephone: "));phoneLink(section,office.phone)}
 if(office.url){para(section,"The source below is a published office listing; confirm the current intake process.");safeLink(section,"County contact source",office.url)}
 section.append(textNode("p",office.sourceStatus));node.append(section);
}
function showChecklist(article,checklist){
 const details=document.createElement("details");details.className="preparation";
 const total=checklist.sections.reduce((n,section)=>n+section.items.length,0);
 const summary=textNode("summary","Preparation checklist — "+total+" steps");
 details.append(summary);
 para(details,"Reviewed "+checklist.reviewedOn+". Use this as a preparation reminder, not an eligibility decision or a submitted application.");
 para(details,"Checkmarks exist only on this page and reset when you change the request or reload. Do not enter private details here.");
 const status=textNode("p","0 of "+total+" steps marked ready");
 status.className="meta checklist-status";status.setAttribute("role","status");
 details.append(status);
 for(const section of checklist.sections){
   details.append(textNode("h4",section.title));
   const ul=document.createElement("ul");ul.className="checklist-items";
   for(const item of section.items){
     const li=document.createElement("li"),label=document.createElement("label");
     const checkbox=document.createElement("input");checkbox.type="checkbox";checkbox.className="prep-checkbox";
     label.append(checkbox,textNode("span",item.text));
     li.append(label,textNode("p","Responsibility: "+item.responsible+(item.condition?" • "+item.condition:"")));
     ul.append(li);
   }
   details.append(ul);
 }
 const update=()=>{const n=details.querySelectorAll(".prep-checkbox:checked").length;status.textContent=n+" of "+total+" steps marked ready";};
 details.addEventListener("change",update);
 const reset=textNode("button","Clear checkmarks");reset.type="button";reset.className="secondary";
 reset.addEventListener("click",()=>{details.querySelectorAll(".prep-checkbox").forEach(c=>c.checked=false);update();});
 details.append(reset);
 para(details,"Submission: "+checklist.submit.text);
 const sub=textNode("p","Official submission instructions: ");safeLink(sub,checklist.submit.label,checklist.submit.url);details.append(sub);
 para(details,"After submission: "+checklist.followUp);
 for(const source of checklist.sources){const el=textNode("p","Source: ");safeLink(el,"Official instructions",source);details.append(el);}
 article.append(details);
}
function showResources(items,fallback){
 const where=$("resources");where.replaceChildren();
 if(!items.length){para(where,"No sufficiently source-reviewed matching program was found. This does not mean no assistance exists. "+fallback+" ");return}
 items.forEach((item,i)=>{
   const article=textNode("article","");article.className="resource";article.dataset.programId=item.id;
   article.append(textNode("h3",(i+1)+". "+item.name));
   if(item.organization)para(article,item.organization);
   if(item.description)para(article,item.description);
   para(article,"Next step: "+item.nextStep);
   if(item.eligibilityNote)para(article,"Who this may serve: "+item.eligibilityNote);
   if(item.application){
     const row=textNode("p","Official application or intake: ");
     safeLink(row,item.application.label,item.application.url);article.append(row);
   }
   if(item.actionSteps?.length){
     article.append(textNode("h4","How to start"));
     const ol=document.createElement("ol");
     for(const step of item.actionSteps){ol.append(textNode("li",step))}
     article.append(ol);
   }
   if(item.guidanceSource){const row=textNode("p","Application guidance source: ");safeLink(row,"Official instructions",item.guidanceSource);article.append(row)}
   if(item.preparationChecklist)showChecklist(article,item.preparationChecklist);
   if(item.phone){article.append(textNode("span","Phone: "));phoneLink(article,item.phone);article.append(textNode("span","  "))}
   safeLink(article,"Official source / program website",item.url);
   para(article,"Source reviewed "+(item.reviewedOn||"date unavailable")+"; current intake not confirmed.");
   if(item.constraints?.length)para(article,"Check: "+item.constraints.join(" "));
   where.append(article);
 });
}
$("state").addEventListener("change",refreshCounties);
$("intake").addEventListener("submit",async e=>{
 e.preventDefault();const version=++requestVersion,state=$("state").value;
 $("feedback").textContent="Matching against the published guide…";
 $("results").hidden=true;$("draft-container").hidden=true;
 $("crisis").hidden=!isUrgent($("message").value);
 try{
  const [resources,counties]=await load(state);if(version!==requestVersion)return;
  plan=createPlan({state,county:$("county").value,person:$("person").value,message:$("message").value,resources,counties});
  $("crisis").hidden=!plan.urgent;
  $("summary").textContent="Published starting points for "+[plan.county&&plan.county+" County",plan.stateName].filter(Boolean).join(", ")+". Matching is automated; current availability has not been verified.";
  showOffice(plan.office);showResources(plan.recommendations,plan.fallback);
  $("results").hidden=false;$("feedback").textContent="Found "+plan.recommendations.length+" possible programs; review them below.";
  $("results").scrollIntoView({behavior:"smooth",block:"start"});
 }catch(error){$("feedback").textContent=error.message;}
});
$("draft").addEventListener("click",()=>{
 if(!plan)return;
 $("email-draft").textContent=planToEmail(plan);
 $("draft-container").hidden=false;$("copy-status").textContent="";
 $("draft-container").scrollIntoView({behavior:"smooth",block:"start"});
});
$("copy").addEventListener("click",async()=>{
 try{await navigator.clipboard.writeText($("email-draft").textContent);$("copy-status").textContent="Draft copied."}
 catch{$("copy-status").textContent="Select and copy the draft above."}
});
refreshCounties();
