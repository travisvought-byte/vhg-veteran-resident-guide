#!/usr/bin/env node
// Email-draft adapter for testing, not connected to an inbox or mail-sending API.
// Usage: printf '%s' '{"state":"OH","county":"Muskingum","message":"A veteran needs a ramp."}' | node assistant/draft-email.mjs
import {readFileSync} from "node:fs";
import {stdin,stdout,stderr} from "node:process";
import {createPlan,planToEmail} from "./engine.mjs";
import {STATE_FILES as paths} from "./state-files.mjs";
let body="";
stdin.setEncoding("utf8");
for await(const part of stdin){body+=part;if(body.length>10000){stderr.write("Input too large.\n");process.exit(1)}}
try{
  const request=JSON.parse(body),state=String(request.state||"").toUpperCase();
  if(!paths[state])throw Error("Unsupported or missing state. Use one of the 12 published state codes.");
  const [resPath,countyPath]=paths[state];
  const load=path=>JSON.parse(readFileSync(new URL("../"+path,import.meta.url),"utf8"));
  const plan=createPlan({...request,state,resources:load(resPath),counties:load(countyPath)});
  stdout.write(planToEmail(plan)+"\n");
}catch(e){stderr.write("Could not prepare a draft: "+e.message+"\n");process.exitCode=1}
