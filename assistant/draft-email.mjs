#!/usr/bin/env node
// Email-draft adapter for testing, not connected to an inbox or mail-sending API.
// Usage: printf '%s' '{"state":"OH","county":"Muskingum","message":"A veteran needs a ramp."}' | node assistant/draft-email.mjs
import {readFileSync} from "node:fs";
import {stdin,stdout,stderr} from "node:process";
import {createPlan,planToEmail} from "./engine.mjs";
const paths={
  OH:["prototype-data.json","data/public/ohio-county-veterans-offices.json"],
  PA:["data/public/pennsylvania-resources.json","data/public/pennsylvania-county-veterans-offices.json"],
  NY:["data/public/new-york-resources.json","data/public/new-york-county-veterans-offices.json"],
  MI:["data/public/michigan-resources.json","data/public/michigan-county-veterans-offices.json"],
  KY:["data/public/kentucky-resources.json","data/public/kentucky-county-veterans-offices.json"]
};
let body="";
stdin.setEncoding("utf8");
for await(const part of stdin){body+=part;if(body.length>10000){stderr.write("Input too large.\n");process.exit(1)}}
try{
  const request=JSON.parse(body),state=String(request.state||"").toUpperCase();
  if(!paths[state])throw Error("Unsupported or missing state. Use OH, PA, NY, MI or KY.");
  const [resPath,countyPath]=paths[state];
  const load=path=>JSON.parse(readFileSync(new URL("../"+path,import.meta.url),"utf8"));
  const plan=createPlan({...request,state,resources:load(resPath),counties:load(countyPath)});
  stdout.write(planToEmail(plan)+"\n");
}catch(e){stderr.write("Could not prepare a draft: "+e.message+"\n");process.exitCode=1}
