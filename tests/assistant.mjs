import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createPlan,identifyTopics,isUrgent,planToEmail} from "../assistant/engine.mjs";

const read=file=>JSON.parse(readFileSync(new URL("../"+file,import.meta.url),"utf8"));
import {STATE_FILES as stateFiles, STATES} from "../assistant/state-files.mjs";
const registry=read("states/registry.json");
assert.equal(Object.keys(STATES).length,11);
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
console.log("Assistance navigator: 11-state registry and audience-sensitive referral tests passed.");

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
