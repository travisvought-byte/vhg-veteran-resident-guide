import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createPlan,identifyTopics,isUrgent,planToEmail} from "../assistant/engine.mjs";

const read=file=>JSON.parse(readFileSync(new URL("../"+file,import.meta.url),"utf8"));
import {STATE_FILES as stateFiles, STATES} from "../assistant/state-files.mjs";
const registry=read("states/registry.json");
assert.equal(Object.keys(STATES).length,registry.length);
assert.deepEqual(Object.keys(stateFiles).sort(),registry.map(x=>x.code).sort());
for(const entry of registry){assert.deepEqual(stateFiles[entry.code],[entry.resources,entry.offices]);}
assert(identifyTopics("We need housing and a wheelchair ramp").includes("accessibility"));
assert(identifyTopics("We need housing and a wheelchair ramp").includes("housing"));
assert(isUrgent("I am suicidal and need help"));
assert(!isUrgent("I need a wheelchair ramp"));
assert.throws(()=>createPlan({state:"ZZ",message:"Help"}),/supported states/);
assert.throws(()=>createPlan({state:"OH",message:"Housing",county:"Madeup",counties:read(stateFiles.OH[1])}),/Choose a county/);

for(const [state,[resourceFile,countyFile]] of Object.entries(stateFiles)){
 const resources=read(resourceFile),counties=read(countyFile);
 assert(resources.length>10, state+" resources");
 assert(counties.length>20, state+" county offices");
 const sampleCounty=counties.find(x=>x.phone&&x.county);
 const plan=createPlan({state,county:sampleCounty.county,person:"veteran",message:"My father is a veteran who needs benefits and home care.",resources,counties});
 assert.equal(plan.state,state);
 assert.equal(plan.county,sampleCounty.county);
 assert.equal(plan.office.phone,sampleCounty.phone);
 assert(plan.recommendations.every(x=>x.verification.includes("Official source reviewed")));
 assert(plan.recommendations.every(x=>/^https?:\/\//.test(x.url)));
 assert(plan.recommendations.length<=5);
 assert(!planToEmail(plan).includes("undefined"));
}
const fake=[
 {program_id:"good",name:"Accessible home ramp help",official_url:"https://example.org/help",service_area:["Ohio"],needs_supported:["equipment_home_accessibility"],description:"Ramp help",next_step:"Ask for an intake appointment",verification:{record_status:"official_source_reviewed",last_reviewed_on:"2026-10-10"}},
 {program_id:"unverified",name:"Ramp",official_url:"https://example.org/other",service_area:["Ohio"],needs_supported:["equipment_home_accessibility"],verification:{record_status:"official_search_extract_only"}},
 {program_id:"wrong-state",name:"Ramp",official_url:"https://example.org/other",service_area:["New York"],needs_supported:["equipment_home_accessibility"],verification:{record_status:"official_source_reviewed"}},
 {program_id:"unsafe-url",name:"Ramp",official_url:"javascript:alert(1)",service_area:["Ohio"],needs_supported:["equipment_home_accessibility"],verification:{record_status:"official_source_reviewed"}}
];
const example=createPlan({state:"OH",message:"I need a wheelchair ramp",resources:fake});
assert.equal(example.recommendations.length,1);
assert.equal(example.recommendations[0].id,"good");
const crisis=createPlan({state:"OH",message:"I feel suicidal and I need help",resources:fake});
assert(crisis.urgent);
assert(planToEmail(crisis).includes("988"));
console.log("Assistance navigator: 13-state registry and audience-sensitive referral tests passed.");

const mk=(id,name,tags)=>({program_id:id,name,official_url:"https://example.org/"+id,
  service_area:["Ohio"],needs_supported:tags,description:name,next_step:"Contact intake",
  verification:{record_status:"official_source_reviewed",last_reviewed_on:"2026-10-19"}});
const audienceFixtures=[
  mk("va-hisa","VA Home Improvements and Structural Alterations ramp",["equipment_home_accessibility"]),
  mk("r02-dic","Dependency and Indemnity Compensation for surviving spouses",["benefits_and_funding","veteran_services"]),
  mk("r02-survivors-pension","Survivors Pension",["benefits_and_funding","veteran_services"]),
  mk("r02-va-pension","Veterans Pension benefits",["benefits_and_funding","veteran_services"]),
  mk("r02-aid-attendance-housebound","Aid and Attendance Pension additions",["benefits_and_funding","veteran_services"]),
  mk("ohio-aging-help","Ohio aging and disability benefits help",["benefits_and_funding","general_navigation"]),
  mk("county-veterans-help","County Veterans Service benefits assistance",["benefits_and_funding","veteran_services"])
];
const countyFixtures=[{county:"Morrow",phone:"555-0123",website:"https://example.org/vso"}];
const planFor=(person,message="benefits and pension assistance")=>createPlan({state:"OH",county:"Morrow",person,message,resources:audienceFixtures,counties:countyFixtures});
const ids=plan=>plan.recommendations.map(x=>x.id);
const forOther=planFor("other");
assert(!forOther.office,"Non-veteran should not be directed to a county VSO");
assert(ids(forOther).includes("ohio-aging-help"));
assert(!ids(forOther).some(id=>["va-hisa","r02-dic","r02-survivors-pension","r02-va-pension","r02-aid-attendance-housebound","county-veterans-help"].includes(id)));
const forVeteran=planFor("veteran");
assert(forVeteran.office);
assert(ids(forVeteran).includes("r02-va-pension"));
assert(!ids(forVeteran).includes("r02-dic"));
assert(!ids(forVeteran).includes("r02-survivors-pension"));
const forSurvivor=planFor("survivor");
assert(forSurvivor.office);
assert(ids(forSurvivor).includes("r02-dic"));
assert(ids(forSurvivor).includes("r02-survivors-pension"));
assert(!ids(forSurvivor).includes("r02-va-pension"));
assert(ids(planFor("caregiver_veteran")).includes("r02-va-pension"));
assert(ids(planFor("caregiver_survivor")).includes("r02-dic"));
assert(!planFor("caregiver_other").office);
assert(!planFor("caregiver").office);
assert(!ids(planFor("unknown")).includes("r02-va-pension"));
const accessibilityOther=planFor("other","wheelchair ramp and accessibility");
assert(!ids(accessibilityOther).includes("va-hisa"));
assert(!planToEmail(accessibilityOther).includes("County veterans office:"));
const noMatch=createPlan({state:"OH",county:"Morrow",person:"other",message:"wheelchair ramp",resources:[audienceFixtures[0]],counties:countyFixtures});
assert.equal(noMatch.recommendations.length,0);
assert(/aging and disability/.test(planToEmail(noMatch)));
assert(!/Start with your county veterans office/.test(planToEmail(noMatch)));

// Curated first-wave application routes: verify links, eligible audiences and no invented forms.
import {PROGRAM_GUIDANCE,getProgramGuidance} from "../assistant/program-guidance.mjs";
assert.equal(Object.keys(PROGRAM_GUIDANCE).length,12);
for(const [id,guidance] of Object.entries(PROGRAM_GUIDANCE)){
  assert(["veteran","survivor","veteran_or_survivor","any"].includes(guidance.audience),id);
  assert(guidance.audienceLabel.length>20,id);
  assert(/^https:\/\//.test(guidance.application.url),id);
  assert(/^https:\/\//.test(guidance.source),id);
  assert(guidance.steps.length>=2,id);
  assert(guidance.steps.every(step=>step.length>25),id);
}
const ohioPrograms=read(stateFiles.OH[0]);
const ohioCounties=read(stateFiles.OH[1]);
const seniorPlan=createPlan({state:"OH",county:"Morrow",person:"other",message:"wheelchair ramp home modification",resources:ohioPrograms,counties:ohioCounties});
assert(!seniorPlan.office);
assert(seniorPlan.recommendations.some(r=>r.id==="ohio-waiver-home-modifications"));
assert(seniorPlan.recommendations.every(r=>r.id!=="va-hisa"&&r.id!=="va-sah"&&r.id!=="va-sha"));
const hisaOnly=createPlan({state:"OH",person:"veteran",message:"wheelchair ramp at home",resources:ohioPrograms.filter(r=>r.program_id==="va-hisa")});
assert.equal(hisaOnly.recommendations[0].application.url,"https://www.va.gov/forms/10-0103/");
assert(hisaOnly.recommendations[0].actionSteps.some(s=>s.includes("Prosthetic")));
assert(planToEmail(hisaOnly).includes("Form 10-0103"));
const survivorPension=createPlan({state:"OH",person:"survivor",message:"Survivors Pension and benefits",resources:ohioPrograms.filter(r=>r.program_id==="r02-survivors-pension")});
assert.equal(survivorPension.recommendations[0].application.label.includes("21P-534EZ"),true);
const wrongAudience=createPlan({state:"OH",person:"other",message:"survivors pension",resources:ohioPrograms.filter(r=>r.program_id==="r02-survivors-pension")});
assert.equal(wrongAudience.recommendations.length,0);
const paPrograms=read(stateFiles.PA[0]);
const paGeneral=createPlan({state:"PA",person:"other",message:"home accessibility for an older adult",resources:paPrograms.filter(r=>r.program_id==="pa-link")});
assert.equal(paGeneral.recommendations[0].id,"pa-link");
assert(paGeneral.recommendations[0].actionSteps.length>=2);
const uncuratedPlan=createPlan({state:"OH",person:"veteran",message:"wheelchair ramp",resources:fake.filter(x=>x.program_id==="good")});
assert.equal(getProgramGuidance("good"),null);
assert.equal(uncuratedPlan.recommendations[0].application,null);
assert.deepEqual(uncuratedPlan.recommendations[0].actionSteps,[]);
console.log("Curated VA/state application steps and beneficiary filters passed.");

// Practical preparation checklists must track official-source tasks and only display on curated programs.
import {ACCESSIBILITY_CHECKLISTS,getAccessibilityChecklist} from "../assistant/accessibility-checklists.mjs";
assert.deepEqual(Object.keys(ACCESSIBILITY_CHECKLISTS).sort(),["va-hisa","va-sah","va-sha","ohio-waiver-home-modifications"].sort());
for(const [id,checklist] of Object.entries(ACCESSIBILITY_CHECKLISTS)){
  assert.equal(checklist.reviewedOn,"2026-10-19");
  assert(checklist.sections.length>=3,id);
  assert(checklist.sections.every(section=>section.items.length>0&&section.items.every(item=>item.text.length>35&&item.responsible.length>2)),id);
  assert(/^https:\/\//.test(checklist.submit.url),id);
  assert(checklist.followUp.length>30,id);
  assert(checklist.sources.every(url=>/^https:\/\//.test(url)),id);
  assert(PROGRAM_GUIDANCE[id],id+" must have separately reviewed application guidance");
}
assert(getAccessibilityChecklist("does-not-exist")===null);
assert(ACCESSIBILITY_CHECKLISTS["va-hisa"].sections.some(section=>section.items.some(item=>/itemized contractor estimate/.test(item.text))));
assert(ACCESSIBILITY_CHECKLISTS["va-hisa"].sections.some(section=>section.items.some(item=>/notarized/.test(item.text)&&item.condition==="Only if renting")));
assert(!JSON.stringify(ACCESSIBILITY_CHECKLISTS["va-sah"]).includes("contractor bid"));
assert(ACCESSIBILITY_CHECKLISTS["ohio-waiver-home-modifications"].sections.some(section=>section.items.some(item=>/property owner provides written consent/.test(item.text))));
assert(ACCESSIBILITY_CHECKLISTS["ohio-waiver-home-modifications"].submit.text.includes("no universal public application form"));
const checklistHisaPlan=createPlan({state:"OH",person:"veteran",message:"wheelchair ramp",resources:ohioPrograms.filter(x=>x.program_id==="va-hisa")});
assert.equal(checklistHisaPlan.recommendations[0].preparationChecklist.title,ACCESSIBILITY_CHECKLISTS["va-hisa"].title);
assert(planToEmail(checklistHisaPlan).includes("Preparation checklist"));
assert(planToEmail(checklistHisaPlan).includes("Responsib"));
assert(planToEmail(checklistHisaPlan).includes("After submission"));
const checklistOther=createPlan({state:"OH",person:"other",message:"wheelchair ramp",resources:ohioPrograms.filter(x=>x.program_id==="va-hisa")});
assert.equal(checklistOther.recommendations.length,0);
assert.equal(uncuratedPlan.recommendations[0].preparationChecklist,null);
console.log("Four accessible and source-linked preparation checklists passed.");

import {BENEFITS_HOUSING_CHECKLISTS,getBenefitsHousingChecklist} from "../assistant/benefits-housing-checklists.mjs";
assert.deepEqual(Object.keys(BENEFITS_HOUSING_CHECKLISTS).sort(),["r02-va-pension","r02-survivors-pension","r02-dic","r02-aid-attendance-housebound","va-housing-help","va-ssvf"].sort());
for(const [id,checklist] of Object.entries(BENEFITS_HOUSING_CHECKLISTS)){
 assert.equal(checklist.reviewedOn,"2026-10-19",id);
 assert(checklist.sections.length>=3,id);
 assert(checklist.sections.every(s=>s.items.length>=2&&s.items.every(i=>i.text.length>=32&&i.responsible)),id);
 assert(/^https:\/\//.test(checklist.submit.url),id);
 assert(checklist.sources.every(s=>/^https:\/\//.test(s)),id);
 assert(PROGRAM_GUIDANCE[id],id+" needs a reviewed guidance route");
}
assert.equal(getBenefitsHousingChecklist("nonexistent"),null);
const pensionPlan=createPlan({state:"OH",person:"veteran",message:"veterans pension benefits",resources:ohioPrograms.filter(r=>r.program_id==="r02-va-pension")});
assert.equal(pensionPlan.recommendations[0].preparationChecklist.title,BENEFITS_HOUSING_CHECKLISTS["r02-va-pension"].title);
assert(planToEmail(pensionPlan).includes("Form 21P-527EZ"));
const survivorPlan=createPlan({state:"OH",person:"survivor",message:"Survivors Pension",resources:ohioPrograms.filter(r=>r.program_id==="r02-survivors-pension")});
assert(planToEmail(survivorPlan).includes("Form 21P-534EZ"));
assert.equal(createPlan({state:"OH",person:"veteran",message:"Survivors Pension",resources:ohioPrograms.filter(r=>r.program_id==="r02-survivors-pension")}).recommendations.length,0);
assert.equal(createPlan({state:"OH",person:"other",message:"Veterans Pension",resources:ohioPrograms.filter(r=>r.program_id==="r02-va-pension")}).recommendations.length,0);
const aaPlan=createPlan({state:"OH",person:"survivor",message:"aid and attendance housebound pension",resources:ohioPrograms.filter(r=>r.program_id==="r02-aid-attendance-housebound")});
assert(aaPlan.recommendations[0].preparationChecklist.sections.some(s=>s.items.some(i=>i.text.includes("21-0779"))));
const housingPlan=createPlan({state:"OH",person:"veteran",message:"homeless housing help",resources:ohioPrograms.filter(r=>r.program_id==="va-housing-help")});
assert(housingPlan.recommendations[0].preparationChecklist.submit.text.includes("877-424-3838"));
assert.equal(createPlan({state:"OH",person:"other",message:"housing help",resources:ohioPrograms.filter(r=>r.program_id==="va-housing-help")}).recommendations.length,0);
const ssvfPlan=createPlan({state:"OH",person:"veteran",message:"homelessness housing SSVF",resources:ohioPrograms.filter(r=>r.program_id==="va-ssvf")});
assert(ssvfPlan.recommendations[0].preparationChecklist.submit.text.includes("no single national SSVF applicant form"));
console.log("Six reviewed pension, survivor and housing handoff rules passed.");
