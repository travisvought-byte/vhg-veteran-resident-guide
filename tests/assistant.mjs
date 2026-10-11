import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createPlan,identifyTopics,isUrgent,planToEmail} from "../assistant/engine.mjs";

const read=file=>JSON.parse(readFileSync(new URL("../"+file,import.meta.url),"utf8"));
const stateFiles={
 OH:["prototype-data.json","data/public/ohio-county-veterans-offices.json"],
 PA:["data/public/pennsylvania-resources.json","data/public/pennsylvania-county-veterans-offices.json"],
 NY:["data/public/new-york-resources.json","data/public/new-york-county-veterans-offices.json"],
 MI:["data/public/michigan-resources.json","data/public/michigan-county-veterans-offices.json"],
 KY:["data/public/kentucky-resources.json","data/public/kentucky-county-veterans-offices.json"]
};
assert(identifyTopics("We need housing and a wheelchair ramp").includes("accessibility"));
assert(identifyTopics("We need housing and a wheelchair ramp").includes("housing"));
assert(isUrgent("I am suicidal and need help"));
assert(!isUrgent("I need a wheelchair ramp"));
assert.throws(()=>createPlan({state:"CA",message:"Help"}),/supported states/);
assert.throws(()=>createPlan({state:"OH",message:"Housing",county:"Madeup",counties:read(stateFiles.OH[1])}),/Choose a county/);

for(const [state,[resourceFile,countyFile]] of Object.entries(stateFiles)){
 const resources=read(resourceFile),counties=read(countyFile);
 assert(resources.length>10, state+" resources");
 assert(counties.length>20, state+" county offices");
 const sampleCounty=counties.find(x=>x.phone&&x.county);
 const plan=createPlan({state,county:sampleCounty.county,message:"My father is a veteran who needs benefits and home care.",resources,counties});
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
console.log("Assistance pilot: passed matching, urgent support, source status, five-state and email draft checks.");
