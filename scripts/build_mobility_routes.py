#!/usr/bin/env python3
"""Build the mobility route finder from an explicitly reviewed public snapshot."""
import html
import json
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
STATE_NAMES='AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|DE:Delaware|DC:District of Columbia|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|WI:Wisconsin|WY:Wyoming'
STATES=dict(s.split(':',1) for s in STATE_NAMES.split('|'))
# Plain-language source labels shown to visitors; keep in sync with assets/mobility-routes.js.
LABELS={'text-reviewed':'from the law or rule text','summary-only':'from an official summary of the law','route-only':'official program page'}
def validate(data):
 assert data['publication_status']=='reviewed-information-snapshot'
 assert date.fromisoformat(data['reviewed_on'])<=date.today()
 sources={s['id']:s for s in data['sources']};issues={i['id'] for i in data['issues']}
 assert len(sources)==len(data['sources'])
 assert set(data['provenance']['approved_claim_ids'])=={c['id'] for c in data['claims']}
 assert len(data['claims'])==len(set(data['provenance']['approved_claim_ids']))
 for c in data['claims']:
  assert c['jurisdiction'] in {*STATES,'US'} and c['issue'] in issues
  assert c['status'] in {'text-reviewed','summary-only','route-only'}
  assert c['title'] and c['plain'] and c['scope'] and c['limitations'] and c['citation'] and c['source_ids']
  for sid in c['source_ids']:
   s=sources[sid];assert s['jurisdiction']==c['jurisdiction'] and s['retrieval']=='content-reviewed'
   assert s['url'].startswith('https://')
   assert date.fromisoformat(s['reviewed_on'])<=date.fromisoformat(data['reviewed_on'])
   if s['kind']=='legislative-summary':assert c['status']=='summary-only' and s['instrument_status']=='enacted'
  if c['effective_on']:assert date.fromisoformat(c['effective_on'])<=date.fromisoformat(data['reviewed_on'])
  else:assert c['effective_date_note']
 for inf in data['inferences']:
  assert inf['status']=='analyst-inference' and inf['limitations']
  assert all(i in data['provenance']['approved_claim_ids'] for i in inf['premise_claim_ids'])
 assert not {'existing_directory_leads','retrieval_attempts'} & data.keys()
 return data

def outputs():
 data=validate(json.loads((ROOT/'data/mobility-routes.json').read_text()));sources={s['id']:s for s in data['sources']}
 escape=lambda x:html.escape(x,quote=True)
 state_options=''.join(f'<option value="{code}"'+(' selected' if code=='OH' else '')+f'>{name}</option>' for code,name in STATES.items())
 issue_options=''.join(f'<option value="{i["id"]}">{escape(i["label"])}</option>' for i in data['issues'])
 fallback=[]
 for st in data['states']:
  records=[]
  for c in data['claims']:
   if c['jurisdiction']!=st['code']:continue
   links=' · '.join(f'<a target="_blank" rel="noopener" href="{escape(sources[s]["url"])}">{escape(sources[s]["title"])}</a>' for s in c['source_ids'])
   records.append(f'<article><h4>{escape(c["title"])}</h4><p>{escape(c["plain"])}</p><p class="small">Source: {escape(c["citation"])} ({LABELS[c["status"]]}) · {links} · checked {c["reviewed_on"]}</p><details><summary>Fine print</summary><p>{escape(c["statement"])}</p><p><strong>Who it covers:</strong> {escape(c["scope"])}</p><p>{escape(c["limitations"])}</p></details></article>')
  fallback.append(f'<details><summary>{escape(st["name"])}</summary>'+''.join(records)+'</details>')
 data['state_names']=STATES
 page=(ROOT/'templates/mobility-rights.html').read_text().replace('__STATES__',state_options).replace('__ISSUES__',issue_options).replace('__FALLBACK__','\n'.join(fallback)).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c'))
 return {'mobility-rights.html':page}
if __name__=='__main__':
 for path,text in outputs().items():(ROOT/path).write_text(text)
 print('Built source-linked mobility route finder.')
