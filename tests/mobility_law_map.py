"""Protect boundaries whose failure would misstate mobility rights."""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_mobility_law_map import validate, PACKAGE
base=json.loads((PACKAGE/'map.json').read_text());assert not validate(base)
def rejects(change,expected):
 d=copy.deepcopy(base);change(d);errors=validate(d);assert any(expected in e for e in errors),errors
rejects(lambda d:d.update(publication_status='public'),'research-only')
rejects(lambda d:d['state_issue_matrix'][-1].update(review_status='no-law'),'Unknown or limited')
rejects(lambda d:d['claims'][0].update(source_ids=['ky-loaner']),'Cross-jurisdiction')
rejects(lambda d:next(c for c in d['claims'] if c['id']=='ca-repair-1').update(status='text-reviewed'),'Summary promoted')
rejects(lambda d:d['claims'][0].update(effective_on='2099-01-01'),'Future rule')
rejects(lambda d:d['sources'][0].update(instrument_status='pending-bill'),'Proposed or unknown')
rejects(lambda d:d['inferences'][0].update(status='confirmed-law'),'Inference mislabeled')
rejects(lambda d:d['inferences'][0].update(premise_claim_ids=['imaginary']),'Inference without')
rejects(lambda d:d['existing_directory_leads'][0].update(fresh_legal_review=True),'Old directory lead')
rejects(lambda d:d['claims'][1]['timing'].update(unit=''),'Timing must retain')
rejects(lambda d:d['state_issue_matrix'].pop(),'Incomplete state/issue')
rejects(lambda d:d['states'].pop(),'National matrix')
rejects(lambda d:d['advocacy_comparisons'][0].update(status='confirmed-law'),'Comparison mislabeled')
rejects(lambda d:d['advocacy_comparisons'][0].update(premise_claim_ids=['imaginary']),'Comparison without evidence')
rejects(lambda d:d['advocacy_comparisons'][0].update(states_compared=['CA']),'Comparison state/evidence')
rejects(lambda d:d['advocacy_comparisons'][0].update(issue='home'),'Comparison issue/evidence')
rejects(lambda d:d['advocacy_comparisons'][0].update(limitations=''),'Comparison needs bounded')
assert len(base['states'])==51 and len(base['state_issue_matrix'])==459
assert len({c['jurisdiction'] for c in base['claims'] if c['jurisdiction']!='US'})==51
mn=next(c for c in base['claims'] if c['id']=='mn-loaner-1');assert mn['timing']['unit']=='working-days' and mn['timing']['operator']=='>'
assert all(not c['claim_ids'] for c in base['state_issue_matrix'] if c['state']=='NJ' and c['issue'] not in {'public-access','warranty','downtime'})
assert len(base['state_baselines'])==51
rejects(lambda d:d['state_baselines'].pop(),'Minimum baseline')
rejects(lambda d:d['state_baselines'][0].update(claim_id='us-medicare-repair-1'),'Baseline needs substantive')
rejects(lambda d:d['state_baselines'][0].update(responsible_actor=''),'Baseline needs accountable')
rejects(lambda d:d['claims'][0].update(reviewed_on='2099-01-01'),'Future claim review')
assert 'donation' in next(c for c in base['claims'] if c['id']=='il-donation-1')['statement']
or_loaner=next(c for c in base['claims'] if c['id']=='or-loaner-1')
assert or_loaner['timing']['operator']=='>' and or_loaner['timing']['value']==7 and or_loaner['timing']['unit']=='days'
assert 'safety' in or_loaner['timing']['trigger_note']
mi_clock=next(c for c in base['claims'] if c['id']=='mi-remedy-clock-1');assert mi_clock['timing']['unit']=='business-days'
assert '2025' in next(s for s in base['sources'] if s['id']=='mi-wheelchair-act')['version_note']
assert next(s for s in base['sources'] if s['id']=='mi-wheelchair-act')['kind']=='historical-code'
ny=next(c for c in base['claims'] if c['id']=='ny-backup-payer-1');assert ny['effective_on']=='2026-01-01' and 'March 1' in ny['effective_date_note']
assert all(next(s for s in base['sources'] if s['id']==sid)['kind']=='program-manual' for sid in ny['source_ids'])
assert next(s for s in base['sources'] if s['id']=='nj-wheelchair-guidance')['kind']=='official-guidance'
assert not any('scdhhs.gov' in s['url'] for s in base['sources'])
print('PASS mobility map regressions: unknowns, jurisdictions, summaries, proposals, dates, inferences, lead freshness, timing, national matrix completeness and evidence-linked advocacy comparisons.')
