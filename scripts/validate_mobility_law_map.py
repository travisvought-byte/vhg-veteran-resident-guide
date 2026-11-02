#!/usr/bin/env python3
"""Validate staged legal observations, inference premises and explicit research gaps."""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from build_mobility_routes import STATES
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
 need(set(maps['states'])==set(STATES),'National matrix must track all 50 states and DC')
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
  try:need(date.fromisoformat(c['reviewed_on'])<=asof,'Future claim review')
  except (ValueError,KeyError):errors.append('Invalid claim review date')
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
 comparisons=d.get('advocacy_comparisons',[])
 need(len({c['id'] for c in comparisons})==len(comparisons),'Duplicate advocacy comparison')
 for comparison in comparisons:
  need(comparison.get('status')=='analyst-comparison','Comparison mislabeled as established law')
  need(comparison.get('issue') in maps['issues'],'Unknown comparison issue')
  refs=[maps['claims'].get(i) for i in comparison.get('premise_claim_ids',[])]
  need(bool(refs) and all(refs),'Comparison without evidence')
  need({c['jurisdiction'] for c in refs if c}==set(comparison.get('states_compared',[])),'Comparison state/evidence mismatch')
  need(all(c and c['issue']==comparison.get('issue') for c in refs),'Comparison issue/evidence mismatch')
  need(all(comparison.get(k) for k in ['title','disparity','proposed_change','decision_makers','limitations']),'Comparison needs bounded findings and policy action')
 baselines=d.get('state_baselines',[])
 need(len(baselines)==len(maps['states']) and {b.get('state') for b in baselines}==set(maps['states']),'Minimum baseline must cover every jurisdiction exactly once')
 need(bool(d.get('minimum_coverage_definition')),'Minimum coverage needs a definition')
 for b in baselines:
  c=maps['claims'].get(b.get('claim_id'))
  need(bool(c) and c['jurisdiction']==b.get('state') and c['status']!='route-only','Baseline needs substantive state evidence')
  need(b.get('status')=='minimum-evidence-baseline' and all(b.get(k) for k in ['responsible_actor','advocacy_question','completion_note']),'Baseline needs accountable actor, question and limits')
  need(bool(c) and b.get('reviewed_on')==c.get('reviewed_on'),'Baseline review must match evidence')
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
 observed={c['jurisdiction'] for c in d['claims'] if c['jurisdiction']!='US'}
 lines=['# State-by-state disability advocacy research matrix','',f"As of {d['as_of']}. Research pass {d.get('research_pass',1)}: 50 states and DC tracked; selected evidence for {len(observed)} states; {len(d['claims'])} observations and {len(d['sources'])} reviewed primary-publisher sources. {len(d['issues'])} issue families; federal observations remain separate. Public site content is unchanged.",'','This matrix supports advocacy: compare protections, exclusions and accountability, then identify policy changes. It does not route individual service requests. A reviewed cell means at least one bounded observation, not a complete legal review. Unknown never means no right. Source types and version limits remain visible.','', '## Advocacy comparisons to develop','', 'These are bounded analyst comparisons, not state rankings or proof of real-world outcomes. Priority order is not scored: population affected, lived experience and enforcement data still need collection.','', '| Issue | States | Documented difference | Policy direction | Evidence |','| --- | --- | --- | --- | --- |']
 claims={c['id']:c for c in d['claims']}
 for c in d.get('advocacy_comparisons',[]):
  refs='; '.join(f"[{cid}]({sources[claims[cid]['source_ids'][0]]['url']})" for cid in c['premise_claim_ids'])
  lines.append(f"| {c['title']} | {', '.join(c['states_compared'])} | {c['disparity']} | {c['proposed_change']} | {refs} |")
 for c in d.get('advocacy_comparisons',[]):
  lines += ['',f"**{c['title']}:** Decision-makers: {c['decision_makers']}. Limits: {c['limitations']}"]
 lines+=['','## Advocacy questions by issue','','| Issue | What to establish before choosing a campaign |','| --- | --- |']
 questions={'repair-access':'Who can access parts, tools and software, for which devices, on what terms?','warranty':'Which devices, consumers, transfers and donated equipment qualify; what remedies are enforceable?','downtime':'What triggers response, parts ordering, temporary equipment and completion duties; who pays?','payer':'Which payer covers repair and backup mobility; what exclusions create discontinuity?','home':'Which housing and modification duties apply; how do eligibility and funding exclusions affect independence?','vehicle':'Which adaptation rights, approval restrictions and maintenance responsibilities apply?','transit':'What accessibility duties, service exclusions and accountability mechanisms apply?','community':'What supports community choice; what service limits and enforcement gaps remain?','public-access':'Which public places and services are covered, what exclusions apply, and who enforces access duties?'}
 for i,label in issues.items():lines.append(f"| {label} | {questions[i]} |")
 lines+=['','## Minimum national baseline','',d['minimum_coverage_definition'],'','| State | Evidence | Responsible actor | Advocacy question |','| --- | --- | --- | --- |']
 for b in d['state_baselines']:
  c=claims[b['claim_id']];source=sources[c['source_ids'][0]]
  lines.append(f"| {b['state']} | [{c['id']}]({source['url']}) — {c['status']}, reviewed {b['reviewed_on']} | {b['responsible_actor']} | {b['advocacy_question']} |")
 lines+=['','## State comparison','','| State | Observations and scope | Remaining work |','| --- | --- | --- |']
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
 populated=sum(bool(c['claim_ids']) for c in d['state_issue_matrix']);lines+=['',f'{populated} of {len(d["state_issue_matrix"])} state/issue cells have some evidence. This is not a completeness percentage. The matrix tracks all jurisdictions, but substantive repair/warranty research remains ahead of home, vehicle, transit and community-service research. A filled cell is not a finding that protections are adequate.','', '## Next research queue','']
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
