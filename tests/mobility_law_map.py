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
print('PASS mobility map regressions: unknowns, jurisdictions, summaries, proposals, dates, inferences, lead freshness, timing and matrix completeness.')
