// A single, print-only, source-linked handoff, built from the selected vetted referral.
// No intake narrative, checkbox state, names or medical/financial details are transferred.
const DESTINATIONS=Object.freeze({
  "va-hisa":"VA care team / Prosthetic and Sensory Aids Service",
  "va-sah":"VA regional office or accredited veterans service officer",
  "va-sha":"VA regional office or accredited veterans service officer",
  "ohio-waiver-home-modifications":"Waiver case manager / authorizing agency"
});
const make=(document,tag,value,className)=>{
  const node=document.createElement(tag);
  if(className)node.className=className;
  if(value!==undefined&&value!==null)node.textContent=String(value);
  return node;
};
function safeLink(document,label,url){
  if(typeof url!=="string")return null;
  try{
    const u=new URL(url);
    if(u.protocol!=="https:")return null;
    const a=make(document,"a",label);
    a.href=u.href;a.rel="noopener noreferrer";
    return a;
  }catch{return null;}
}
function linkedLine(document,label,url){
  const wrap=make(document,"div",null,"handoff-link");
  const a=safeLink(document,label,url);
  if(a)wrap.append(a,make(document,"span",url,"handoff-url"));
  return wrap;
}
export function buildHandoff(document,plan,resource){
  const checklist=resource?.preparationChecklist;
  if(!checklist||!DESTINATIONS[resource.id])throw new Error("No printable handoff for this referral.");
  const sheet=make(document,"section",null,"handoff-sheet");
  sheet.dataset.programId=resource.id;
  sheet.append(make(document,"div","VETERAN HOME GUARDIANS  •  A Voice for All Veterans","handoff-brand"));
  sheet.append(make(document,"h1",checklist.title));
  const location=[plan.county&&plan.county+" County",plan.stateName].filter(Boolean).join(", ")||"Location not selected";
  sheet.append(make(document,"p","RESOURCE HANDOFF  |  "+location+"  |  Source review: "+checklist.reviewedOn,"handoff-meta"));
  sheet.append(make(document,"p","For: "+DESTINATIONS[resource.id],"handoff-destination"));
  if(resource.eligibilityNote)sheet.append(make(document,"p","Possible audience: "+resource.eligibilityNote,"handoff-eligibility"));
  if(plan.office&&resource.id!=="ohio-waiver-home-modifications"){
    const office=make(document,"p","Additional veterans referral: "+plan.office.name+(plan.office.phone?"  •  "+plan.office.phone:""),"handoff-office");
    sheet.append(office);
  }
  const workflow=make(document,"div",null,"handoff-workflow");
  for(const section of checklist.sections){
    const group=make(document,"section",null,"handoff-group");
    group.append(make(document,"h2",section.title));
    const list=make(document,"ul");
    for(const item of section.items){
      const li=make(document,"li");
      li.append(make(document,"span","□","handoff-square"));
      const content=make(document,"div",null,"handoff-task");
      content.append(make(document,"span",item.text));
      content.append(make(document,"small","Who: "+item.responsible+(item.condition?"  •  "+item.condition:"")));
      li.append(content);list.append(li);
    }
    group.append(list);workflow.append(group);
  }
  sheet.append(workflow);
  const tail=make(document,"div",null,"handoff-bottom");
  const submission=make(document,"section",null,"handoff-submit");
  submission.append(make(document,"h2","Where to submit"));
  submission.append(make(document,"p",checklist.submit.text));
  submission.append(linkedLine(document,checklist.submit.label,checklist.submit.url));
  submission.append(make(document,"h2","After submitting"));
  submission.append(make(document,"p",checklist.followUp));
  tail.append(submission);
  const questions=make(document,"section",null,"handoff-questions");
  questions.append(make(document,"h2","Ask at the handoff"));
  for(const q of [
    "What documents are missing, and who can provide them?",
    "Who receives the application or proposal, and how?",
    "Who confirms receipt, approval and the next follow-up?"
  ])questions.append(make(document,"p","□ "+q));
  questions.append(make(document,"p","Contact / next date: __________________________________","handoff-notes"));
  tail.append(questions);
  sheet.append(tail);
  const sources=make(document,"div",null,"handoff-sources");
  sources.append(make(document,"strong","Official sources: "));
  for(const [i,url] of [...new Set(checklist.sources)].entries()){
    const a=safeLink(document,"Source "+(i+1),url);
    if(a)sources.append(a,make(document,"span",url,"handoff-source-url"));
  }
  sheet.append(sources);
  sheet.append(make(document,"p","Preparation guide only; not a filled application or eligibility determination. Confirm instructions and availability with the receiving agency. No personal information is collected by this handoff.","handoff-disclaimer"));
  return sheet;
}
