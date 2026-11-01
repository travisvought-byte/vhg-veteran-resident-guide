#!/usr/bin/env python3
"""Validate staged legal observations, inference premises and explicit research gaps."""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'research/mobility-laws-2026-11-01'
KINDS={'current-code','current-rule','enacted-text','legislative-summary','program-manual','official-guidance'}
STATUSES={'text-reviewed','summary-only','route-only'}
def validate(d):
 errors=[]
 def need(ok,message):
  if not ok: errors.append(message)
 need(d.get('publication_status')=='research-only','Publication boundary must stay research-only')
 try: asof=date.fromisoformat(d['as_of']);need(asof<=date.today(),'Future snapshot date')
 except (ValueError,KeyError): return ['Invalid snapshot date']
 maps={}
 for group,key in [('sources','id'),('claims','id'),('states','code'),('issues','id'),('inferences','id')]:
  rows=d[group];maps[group]={r[key]:r for r in rows};need(len(rows)==len(maps[group]),'Duplicate '+group)
 for s in d['sources']:
  need(s.get('retrieval')=='content-reviewed','Source content must be reviewed')
  need(s.get('kind') in KINDS,'Unknown source kind')
  required={'current-code':'published-code','current-rule':'published-rule','enacted-text':'enacted','legislative-summary':'enacted','program-manual':'program-policy','official-guidance':'guidance'}
  need(s.get('instrument_status')==required.get(s.get('kind')),'Proposed or unknown instrument promoted to enacted law')
  u=urlparse(s.get('url',''));need(u.scheme=='https' and bool(u.netloc),'Invalid source URL')
  need(bool(s.get('locator')) and bool(s.get('version_note')),'Source lacks locator/version limits')
  try:need(date.fromisoformat(s['reviewed_on'])<=asof,'Future source review')
  except (ValueError,KeyError):errors.append('Invalid source review date')
 for c in d['claims']:
  need(c['jurisdiction'] in maps['states'] or c['jurisdiction']=='US','Unknown claim jurisdiction')
  need(c['issue'] in maps['issues'],'Unknown issue')
  need(c['status'] in STATUSES,'Unknown claim status')
  need(all(c.get(k) for k in ['statement','scope','limitations','citation','source_ids']),'Claim lacks bounded evidence')
  refs=[maps['sources'].get(i) for i in c['source_ids']];need(all(refs),'Missing source reference')
  need(all(s and s['jurisdiction']==c['jurisdiction'] for s in refs),'Cross-jurisdiction source')
  if any(s and s['kind']=='legislative-summary' for s in refs):need(c['status']=='summary-only','Summary promoted to text-reviewed law')
  need(c.get('reviewed_on')==d['as_of'],'Claim review date mismatch')
  if c.get('effective_on'):
   try:need(date.fromisoformat(c['effective_on'])<=asof,'Future rule treated as in force')
   except ValueError:errors.append('Invalid effective date')
  else:need(bool(c.get('effective_date_note')),'Unknown effective date needs explanation')
  if c.get('timing'):
   t=c['timing'];need(t.get('operator') in {'>','>=','<='} and t.get('value',0)>0 and t.get('unit') in {'days','working-days','business-days'} and bool(t.get('trigger_note')),'Timing must retain units/operator/trigger')
 expected={(s,i) for s in maps['states'] for i in maps['issues']};seen=set()
 for cell in d['state_issue_matrix']:
  pair=(cell['state'],cell['issue']);need(pair not in seen,'Duplicate state/issue cell');seen.add(pair)
  refs=[maps['claims'].get(i) for i in cell['claim_ids']]
  need(all(c and c['jurisdiction']==cell['state'] and c['issue']==cell['issue'] for c in refs),'Incorrect matrix claim')
  need({c['id'] for c in refs if c}=={c['id'] for c in d['claims'] if (c['jurisdiction'],c['issue'])==pair},'Matrix claim coverage mismatch')
  statuses={c['status'] for c in refs if c};wanted=next((s for s in ['text-reviewed','summary-only','route-only'] if s in statuses),'not-reviewed')
  need(cell['review_status']==wanted,'Unknown or limited evidence promoted')
  need(bool(cell.get('missing_question')),'Every cell needs remaining research scope')
 need(seen==expected,'Incomplete state/issue matrix')
 for inf in d['inferences']:
  need(inf.get('status')=='analyst-inference','Inference mislabeled as law')
  need(bool(inf.get('limitations')) and bool(inf.get('proposed_next_action')),'Inference needs limits/action')
  need(bool(inf['premise_claim_ids']) and all(i in maps['claims'] for i in inf['premise_claim_ids']),'Inference without evidence')
 for lead in d['existing_directory_leads']:
  need(lead.get('fresh_legal_review') is False and lead.get('status')=='existing-directory-lead','Old directory lead promoted to legal evidence')
  p=ROOT/lead['origin'];need(p.is_file(),'Missing lead origin')
  rows=json.loads(p.read_text()) if p.is_file() else []
  need(any(r.get('program_id')==lead['resource_id'] and r.get('official_url')==lead['url'] and r.get('verification',{})==lead.get('original_verification') for r in rows),'Lead identity/source mismatch')
 for attempt in d['retrieval_attempts']:
  need(bool(attempt.get('result')) and bool(attempt.get('next_step')),'Retrieval attempt lacks result/next step')
  need('reviewed_on' not in attempt,'Failed attempt cannot acquire review date')
 return errors

def report(d):
 sources={s['id']:s for s in d['sources']};issues={i['id']:i['label'] for i in d['issues']}
 lines=['# Mobility issues and state laws: first research pass','',f"As of {d['as_of']}. Research only: {len(d['states'])} states, {len(d['claims'])} observations, {len(d['sources'])} reviewed primary-publisher sources, eight issue families. Federal observations are separate. No public action letters or state-program records changed.",'','A reviewed cell means at least one bounded observation, not a complete legal review. Missing evidence means not reviewed, never no right. Legislative summaries and program gateways retain weaker labels. Existing-program leads are not new legal evidence.','', '## Barrier first, then responsible actor','', '| Barrier | Logic for the next route (analyst proposal) |','| --- | --- |', '| Parts/software withheld | Check device scope and manufacturer-access duties. Separate independent repair from warranty and insurance. |', '| Repeated defect | Check device age, warranty and statutory remedy triggers; manufacturer/dealer route may come before a new-law request. |', '| No usable chair during repair | Check warranty loaner/rental duties, payer reimbursement and supplier obligations separately. |', '| Approval or payment denied | Identify payer and plan type first; review the denial and applicable authorization/appeal process. |', '| Cannot enter/use home | Check program eligibility, modifications approval and housing duties separately. |', '| Vehicle adaptation needed | Check specific funding/program and vehicle rules; a benefit listing is not universal approval. |', '| Transit cannot be used | Identify transit mode/provider and local process; distinguish access rights from availability of a ride. |', '| Cannot remain in community | Check state services and federal integration conditions; do not promise a waiver slot. |','', '## State comparison','', '| State | Observations and scope | Remaining work |','| --- | --- |']
 for st in d['states']:
  cs=[c for c in d['claims'] if c['jurisdiction']==st['code']]
  refs=list(dict.fromkeys(i for c in cs for i in c['source_ids']))
  detail=st['summary']+' '+' '.join(f'[{s}]('+sources[s]['url']+')' for s in refs)
  lines.append(f"| {st['name']} ({st['role']}) | {detail} | Definitions, later amendments and implementation remain; see claim limitations and matrix gaps. |")
 lines+=['','## Federal layer','']
 for c in d['claims']:
  if c['jurisdiction']=='US':lines.append(f"- **{issues[c['issue']]}:** {c['statement']} {c['limitations']} "+' '.join(f'[{s}]('+sources[s]['url']+')' for s in c['source_ids']))
 lines+=['','## Inference ledger','']
 for inf in d['inferences']:
  lines += [f"### {inf['id']}",'',f"**Inference:** {inf['statement']}",f"**Premises:** {', '.join(inf['premise_claim_ids'])}.",f"**Next action:** {inf['proposed_next_action']}",f"**Limit:** {inf['limitations']}",'']
 lines+=['## Coverage matrix','', 'T = text reviewed; S = legislative summary only; R = program gateway only; U = not reviewed. These are research-status codes, not legal yes/no answers.','', '| State | '+ ' | '.join(issues)+' |','| --- | '+ ' | '.join('---' for _ in issues)+' |']
 lookup={(c['state'],c['issue']):c for c in d['state_issue_matrix']};codes={'text-reviewed':'T','summary-only':'S','route-only':'R','not-reviewed':'U'}
 for st in d['states']:lines.append('| '+st['code']+' | '+' | '.join(codes[lookup[(st['code'],i)]['review_status']] for i in issues)+' |')
 populated=sum(bool(c['claim_ids']) for c in d['state_issue_matrix']);lines+=['',f'{populated} of {len(d["state_issue_matrix"])} state/issue cells have some evidence. This is not a completeness percentage. Deep repair/warranty work is ahead of home, vehicle, transit and community-service research.','', '## Next research queue','']
 lines+=['- '+q for q in d['open_questions']]
 lines+=['',f"The JSON also preserves {len(d['existing_directory_leads'])} leads from existing state resource records for follow-on research. Their URLs were not all freshly retrieved; original resource IDs and origin files are retained. No lead is treated as law.",'','## Source version and retrieval limits','']
 for s in d['sources']:lines.append(f"- **{s['id']}**: [{s['title']}]({s['url']}); {s['kind']}; locator {s['locator']}; reviewed {s['reviewed_on']}. {s['version_note']}")
 lines+=['','## Failed or alternate retrievals','']
 for a in d['retrieval_attempts']:lines.append(f"- {a['url']}: {a['result']}. Next: {a['next_step']}")
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();d=json.loads((PACKAGE/'map.json').read_text());errors=validate(d)
 if errors:raise SystemExit('\n'.join(errors))
 expected=report(d);out=PACKAGE/'README.md'
 if args.write:out.write_text(expected)
 elif not out.exists() or out.read_text()!=expected:raise SystemExit('Stale research report; run with --write')
 print(f"PASS mobility law research: {len(d['states'])} states, {len(d['claims'])} observations, {len(d['inferences'])} bounded inferences; evidence and unknowns preserved.")
