"""Checks for the resource-mining pipeline (docs/MINING.md). Runs offline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'mining'))
import common as c  # noqa: E402

STATUSES = {'active', 'benchmark', 'manual', 'to_verify', 'needs_owner', 'rejected'}
CATEGORIES = {'veterans_office', 'aging_agency', 'ombudsman', 'independent_living', 'legal_aid', 'housing',
              'va_facilities', 'care_facilities', 'claims_help', 'emergency_numbers', 'crisis_line', 'program'}
ROW_KEYS = {'state', 'county', 'category', 'name', 'organization', 'phone', 'other_phones', 'address', 'hours',
            'confidence', 'note'}
problems = []


def need(ok, message):
    if not ok:
        problems.append(message)


# Helpers
need(c.digits('(501) 683-2382') == '5016832382', 'digits strips punctuation')
need(c.digits('1-800-952-9243') == '8009529243', 'digits strips a leading 1')
need(c.url_key('https://www.Example.org/a/') == 'example.org/a', 'url_key normalizes')
need(c.level_of('full_official_page_text') == 'B' and c.level_of('official_search_excerpt') == 'C', 'levels')
need(c.level_of('anything', confirmed=True) == 'A' and c.level_of(None) == 'D', 'level fallbacks')
need(c.add_days('2026-11-23', 90) == '2027-02-21', 'add_days')

# Source registry
reg = c.read(c.MINING / 'sources.json')
ids = [s['id'] for s in reg['sources']]
need(len(ids) == len(set(ids)), 'source ids are unique')
for s in reg['sources']:
    for key in ('id', 'name', 'publisher', 'scope', 'category', 'url', 'access', 'fetch', 'yields', 'evidence_level',
                'cadence_days', 'status', 'last_checked', 'notes'):
        need(key in s, f"{s.get('id')}: has {key}")
    need(s.get('status') in STATUSES, f"{s['id']}: status {s.get('status')} is known")
    need(s.get('category') in CATEGORIES, f"{s['id']}: category {s.get('category')} is known")
    need(s.get('evidence_level') in c.LEVELS, f"{s['id']}: evidence level")
    need(s.get('url') is None or s['url'].startswith('https://'), f"{s['id']}: https url")
    if s.get('fetch'):
        need(s['fetch'].get('url', '').startswith('https://'), f"{s['id']}: fetch url is https")
        need(s['access'] == 'open_dataset', f"{s['id']}: only open datasets are fetched")

# Harvest files
for path in sorted((c.MINING / 'harvest').glob('*.json')):
    h = c.read(path)
    for key in ('source_id', 'source_url', 'source_title', 'retrieved_on', 'review_method', 'how_read', 'rows'):
        need(key in h, f'{path.name}: has {key}')
    need(h.get('source_id') in ids, f'{path.name}: source {h.get("source_id")} is in the registry')
    need(path.name.startswith(h.get('source_id', '?')) and h.get('retrieved_on', '?') in path.name,
         f'{path.name}: named <source id>-<retrieved_on>.json')
    need(h.get('source_url', '').startswith('https://'), f'{path.name}: https source')
    need(h.get('review_method') in c.METHOD_LEVEL, f'{path.name}: review method is on the evidence ladder')
    for i, row in enumerate(h.get('rows', [])):
        missing = ROW_KEYS - set(row)
        need(not missing, f'{path.name} row {i}: missing {sorted(missing)}')
        need(row.get('category') in CATEGORIES, f'{path.name} row {i}: category')
        need(row.get('confidence') in ('clear', 'uncertain'), f'{path.name} row {i}: confidence')
        need(row.get('phone') or row.get('confidence') == 'uncertain', f'{path.name} row {i}: no phone means uncertain')
        need(row.get('confidence') == 'clear' or row.get('note'), f'{path.name} row {i}: an uncertain row says why')
        if row.get('phone'):
            need(len(c.digits(row['phone'])) == 10, f'{path.name} row {i}: ten-digit phone')

# The report builders run on the current published data. Their committed outputs are snapshots refreshed by the
# monthly workflow and with each harvest, so other changes to state data never fail this check.
import candidates  # noqa: E402
import coverage  # noqa: E402
import ledger  # noqa: E402

report = coverage.build()
need(len(report['states']) == len(c.registry()), 'coverage has every registered state')
need([r['thinness_rank'] for r in report['states']] == list(range(1, len(report['states']) + 1)), 'ranks are 1..n')
need(all(0 <= r['local_or_regional_reach'] <= 1 for r in report['states']), 'reach is a share')
book = ledger.build()
need(book['sources'] and all(s['url'] for s in book['sources']), 'ledger lists sources')
table = candidates.rows()
need(len({r['candidate_id'] for r in table}) == len(table), 'candidate ids are unique')
need({r['status'] for r in table} <= {'new', 'already_published', 'phone_conflict', 'uncertain', 'duplicate'},
     'candidate statuses are known')

if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('mining pipeline checks passed')
