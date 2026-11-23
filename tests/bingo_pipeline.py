"""Checks for scripts/bingo_pipeline.py: the registry is complete, the CSV covers every list, and merge refuses bad records."""
import copy
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bingo_pipeline as bp  # noqa: E402

reg = bp.registry()
assert len(reg['states']) == 51
states, records = bp.load()
rows = list(csv.DictReader(open(ROOT / 'data/public/findbingo-games.csv')))
assert {r['list_file'] for r in rows} == {f for _, f, _ in bp._files()}, 'every bingo list reaches the CSV'
assert all(r['evidence_level'] in bp.EVIDENCE and r['source_url'].startswith('https://') for r in rows)
assert len({r['game_id'] for r in rows}) == len(rows), 'game ids are unique'
assert all(r['review_due'] > r['reviewed_on'] for r in rows if r['reviewed_on'])
cov = json.loads((ROOT / 'data/bingo-sources/coverage.json').read_text())
assert sorted(x['thin_rank'] for x in cov) == list(range(1, 52))

zips = json.loads((ROOT / 'findbingo-site/zips.json').read_text())
good = json.loads((ROOT / 'data/public/washington-bingo.json').read_text())[0]
assert bp.check_record(good, zips) == [], 'a published record passes'
bad = copy.deepcopy(good)
bad.update(zip='00000', kind='bar', source_url='http://x')
bad['sessions'][0]['day'] = 7
errs = ' '.join(bp.check_record(bad, zips))
for word in ('ZIP', 'kind', 'source_url', 'bad session'):
    assert word in errs, word
assert bp.address_key('12 Main Street, Town, WA 98000', '98000') == bp.address_key('12 Main St., Town, WA 98000', '98000')
print('bingo pipeline checks passed')
