// VHG Assistance Pilot. Pure, deterministic matching against the existing public guide.
// No requests, personal data storage, AI model calls or outgoing email happen here.
export const STATES = Object.freeze({
  OH:"Ohio", PA:"Pennsylvania", NY:"New York", MI:"Michigan", KY:"Kentucky"
});
const TOPICS = Object.freeze({
  housing:{
    words:["homeless","homelessness","housing","shelter","eviction","evicted","rent","landlord","mortgage","living in my car","no place to stay","unhoused","utilities","electric bill"],
    tags:["general_navigation","benefits_and_funding"], phrases:["housing","ssvf","shelter","homeless","rent","utility","eviction"]
  },
  accessibility:{
    words:["wheelchair","ramp","accessible","accessibility","home modification","bathroom modification","grab bar","stairs","mobility","assistive equipment","walker"],
    tags:["equipment_home_accessibility"], phrases:["ramp","accessib","equipment","hisa","adapted housing","mobility"]
  },
  care:{
    words:["nursing home","assisted living","home health","caregiver","care at home","respite","long term care","memory care","daily living","older adult"],
    tags:["care_facilities","help_at_home","caregiver_respite"],phrases:["nursing","care","aging","respite","home health","ombudsman"]
  },
  benefits:{
    words:["benefits","disability compensation","va claim","claims","pension","surviving spouse","widow","service connected","appeal","vso","va benefits"],
    tags:["benefits_and_funding","veteran_services"],phrases:["benefit","claims","pension","veterans service","compensation","accredit"]
  },
  food:{
    words:["food","groceries","hungry","meal","meals","snap","food pantry"],
    tags:["general_navigation","help_at_home"],phrases:["food","meal","nutrition","snap"]
  },
  transport:{
    words:["transportation","ride","driving","get to appointment","medical appointment","travel to doctor","bus"],
    tags:["veteran_services","help_at_home"],phrases:["transport","ride","travel","vehicle"]
  },
  legal:{
    words:["legal","lawyer","eviction notice","tenant rights","discrimination","court","appeal denial","consumer rights"],
    tags:["general_navigation"],phrases:["legal","rights","law","ombudsman","advocacy"]
  },
  finances:{
    words:["money","financial","bills","utility bill","emergency assistance","can't afford","cant afford","debt","income","behind on payments"],
    tags:["benefits_and_funding"],phrases:["emergency","financial","payment","utility","grant","assistance"]
  }
});
// The form identifies the person receiving assistance, not just the person filling it in.
// Ambiguous caregiver/unknown roles intentionally do not unlock veteran-only programs.
export function beneficiaryRole(person){
  const value=clean(person).toLowerCase();
  if(value==="veteran"||value==="caregiver_veteran")return "veteran";
  if(value==="survivor"||value==="caregiver_survivor")return "survivor";
  if(value==="other"||value==="caregiver_other")return "other";
  return "unknown";
}
const SURVIVOR_ONLY=new Set(["r02-dic","r02-survivors-pension"]);
const VETERAN_OR_SURVIVOR=new Set(["r02-aid-attendance-housebound","r02-va-burial","r02-ohio-county-burial"]);
const UNIVERSAL_RESOURCES=new Set(["crisis-988"]);
function intendedAudience(item){
  const id=String(item.program_id||"").toLowerCase();
  if(UNIVERSAL_RESOURCES.has(id))return "any";
  if(SURVIVOR_ONLY.has(id))return "survivor";
  if(VETERAN_OR_SURVIVOR.has(id))return "veteran_or_survivor";
  const title=String(item.name||"");
  const org=String(item.organization||"");
  const tags=item.needs_supported||[];
  const url=String(item.official_url||"");
  // Conservative heuristic until the published data has explicit audience fields.
  // Veteran-only services can have generic tags such as home accessibility.
  if(id.startsWith("va-")||id.startsWith("r02-va-")||id.startsWith("r02-veteran")||
     tags.includes("veteran_services")|| /\b(?:va|veterans?)\b/i.test(title+" "+org)||
     /^https?:\/\/(?:[^/]+\.)?va\.gov\//i.test(url))return "veteran";
  return "any";
}
function audienceMatches(item,role){
  const audience=intendedAudience(item);
  if(audience==="any")return true;
  if(audience==="survivor")return role==="survivor";
  if(audience==="veteran_or_survivor")return role==="veteran"||role==="survivor";
  return role==="veteran";
}
const CRISIS=/\b(suicid(?:e|al)|kill myself|end my life|hurt myself|self.harm|want to die|overdose)\b/i;
const DANGER=/\b(immediate danger|life.threatening|violence right now|medical emergency)\b/i;
function clean(s){return String(s??"").trim().replace(/\s+/g," ")}
function wordsMatch(hay,phrase){return new RegExp("(^|[^a-z0-9])"+phrase.replace(/[.*+?^${}()|[\]\\]/g,"\\$&").replace(/ /g,"\\s+")+"(?=$|[^a-z0-9])","i").test(hay)}
export function identifyTopics(message){
  const text=clean(message).toLowerCase(); const found=Object.entries(TOPICS).filter(([,topic])=>topic.words.some(w=>wordsMatch(text,w))).map(([topic])=>topic);
  return found.length?found:["navigation"];
}
export function isUrgent(message){return CRISIS.test(clean(message))||DANGER.test(clean(message))}
function isAllowedURL(url){try{const u=new URL(url);return u.protocol==="https:"||u.protocol==="http:"}catch{return false}}
function areaMatch(item,state,county){
  const names=[STATES[state],state,"Statewide","National","Federal","USA","US"];
  const areas=item.service_area||[];
  if(!Array.isArray(areas)||!areas.length)return false;
  const normalized=areas.map(x=>String(x).toLowerCase());
  return names.some(x=>normalized.includes(x.toLowerCase()))|| Boolean(county&&normalized.some(x=>x===county.toLowerCase()||x===county.toLowerCase()+" county"));
}
function scoredResource(item,topics,county){
  const tags=item.needs_supported||[];
  const hay=[item.name,item.description,item.next_step,item.organization].filter(Boolean).join(" ").toLowerCase();
  let score=0;
  for(const topic of topics){
    const config=TOPICS[topic];
    if(!config){if(tags.includes("general_navigation"))score+=2;continue}
    if(config.tags.some(tag=>tags.includes(tag)))score+=1;
    for(const phrase of config.phrases){if(hay.includes(phrase))score+=4}
  }
  if(county&&(item.service_area||[]).some(x=>String(x).toLowerCase()===county.toLowerCase()))score+=2;
  if(item.regional_role)score+=1;
  return score;
}
export function createPlan({state="OH",county="",message="",person="veteran",resources=[],counties=[]}={}){
  const code=String(state).toUpperCase(),location=STATES[code];
  if(!location)throw new Error("Choose one of the supported states.");
  const rawCounty=clean(county).replace(/ county$/i,"");
  const countyItem=counties.find(x=>String(x.county).toLowerCase()===rawCounty.toLowerCase()||(x.county_aliases||[]).some(y=>String(y).toLowerCase()===rawCounty.toLowerCase()));
  if(rawCounty&&!countyItem)throw new Error("Choose a county listed for this state.");
  const selectedCounty=countyItem?.county||"";
  const request=clean(message).slice(0,2000);
  if(!request)throw new Error("Describe what kind of help is needed.");
  const urgent=isUrgent(request),topics=identifyTopics(request),role=beneficiaryRole(person);
  const eligible=resources.filter(x=>x?.verification?.record_status==="official_source_reviewed"&&
     isAllowedURL(x.official_url)&&areaMatch(x,code,selectedCounty)&&audienceMatches(x,role));
  const candidates=eligible.map(x=>({resource:x,score:scoredResource(x,topics,selectedCounty)}))
    .filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.resource.name.localeCompare(b.resource.name));
  const picks=[];const used=new Set();
  for(const c of candidates){const key=c.resource.program_id||c.resource.name;if(used.has(key))continue;used.add(key);picks.push(c.resource);if(picks.length>=5)break}
  const office=(role==="veteran"||role==="survivor")&&selectedCounty&&countyItem?{
    name:selectedCounty+" County Veterans Service Office",
    phone:clean(countyItem.phone),url:isAllowedURL(countyItem.website)?countyItem.website:isAllowedURL(countyItem.source_url)?countyItem.source_url:null,
    sourceStatus:"Published directory contact; verify directly",reviewedOn:countyItem.reviewed_on||null
  }:null;
  return {
    state:code,stateName:location,county:selectedCounty,person:clean(person),beneficiary:role,topics,
    urgent,office,
    recommendations:picks.map(x=>({
      id:x.program_id||"",name:x.name,organization:x.organization||"",
      description:x.description||"",nextStep:x.next_step||"Contact the organization to ask about available services.",
      phone:x.public_contact?.phone||"",email:x.public_contact?.email||"",
      url:x.official_url,reviewedOn:x.verification?.last_reviewed_on||null,
      verification:"Official source reviewed, not agency-confirmed intake",
      constraints:Array.isArray(x.constraints)?x.constraints.slice(0,2):[]
    })),
    fallback:role==="other"?"Start with the state or regional aging and disability agencies listed in the main guide.":
      role==="unknown"?"Clarify whether the person needing assistance is a veteran, surviving spouse or another senior/person with a disability; meanwhile use the main guide for general aging and disability services.":
      "Contact the county or regional veterans service representative if listed; otherwise use the main guide's state veterans referral route.",
    disclaimer:"This is a referral starting point, not an eligibility decision. Confirm current services, application rules and availability directly with each organization. VHG does not provide emergency response or accredited VA claims representation."
  };
}
export function planToEmail(plan){
  const location=[plan.county&&plan.county+" County",plan.stateName].filter(Boolean).join(", ");
  const lines=["Subject: VHG resource guidance for "+location,"",
    "Thanks for reaching out to Veteran Home Guardians. Here are some possible starting points for assistance in "+location+".",
    ""];
  if(plan.urgent)lines.push("URGENT: If anyone is in immediate danger, call 911. For suicidal thoughts or emotional crisis, call 988 and press 1 for the Veterans Crisis Line, or text 838255.","");
  if(plan.office)lines.push("County veterans office: "+plan.office.name+" — "+(plan.office.phone||"confirm contact")+(plan.office.url?" ("+plan.office.url+")":""),"");
  if(!plan.recommendations.length)lines.push("We could not find a sufficiently source-reviewed program for this request in the current guide. "+plan.fallback,"");
  for(const [i,x] of plan.recommendations.entries()){
    lines.push((i+1)+". "+x.name+(x.organization?" — "+x.organization:""),x.description,
      "Next step: "+x.nextStep,"Contact: "+[x.phone,x.url].filter(Boolean).join(" | "),
      "Source reviewed: "+(x.reviewedOn||"date not recorded")+"; current intake not confirmed.","");
  }
  lines.push("Please confirm eligibility, service availability and current contact information directly. Avoid emailing Social Security numbers, diagnoses, benefits IDs or financial documents. If this is an emergency, do not wait for an email reply.","",
    "Veteran Home Guardians","A Voice for All Veterans");
  return lines.join("\n");
}
