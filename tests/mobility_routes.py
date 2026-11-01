"""Reject unsafe public-source promotions before page generation."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_mobility_routes import validate
base=json.loads((ROOT/'data/mobility-routes.json').read_text());validate(base)
def rejects(change):
 d=copy.deepcopy(base);change(d)
 try:validate(d)
 except (AssertionError,ValueError,KeyError):return
 raise AssertionError('Unsafe public source mutation accepted')
rejects(lambda d:d.update(publication_status='research-only'))
rejects(lambda d:d['claims'][0].update(source_ids=['ky-loaner']))
rejects(lambda d:next(c for c in d['claims'] if c['id']=='ca-repair-1').update(status='text-reviewed'))
rejects(lambda d:d['claims'][0].update(effective_on='2099-01-01'))
rejects(lambda d:d['provenance']['approved_claim_ids'].pop())
rejects(lambda d:d.update(existing_directory_leads=[{'fresh_legal_review':False}]))
rejects(lambda d:d['inferences'][0].update(status='confirmed-law'))
print('PASS public mobility snapshot: approval boundary, source jurisdiction, summary labels, dates, excluded leads and inference status.')
