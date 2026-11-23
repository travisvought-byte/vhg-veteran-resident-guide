"""Checks for the resource-mining pipeline (docs/MINING.md). Runs offline."""
import re
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
        keyed = s['access'] == 'api_key_required'
        need(s['access'] == 'open_dataset' or (keyed and s['fetch'].get('key_env')),
             f"{s['id']}: only open datasets, or a keyed API whose key comes from the environment, are fetched")

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

# The keyed VA fetcher: skipped cleanly with no key, and with a stub in place of the network it pages through each
# state, falls back to the other host when the configured one refuses the key, and never puts the key in a URL.
import io  # noqa: E402
import json as _json  # noqa: E402
import os  # noqa: E402
import urllib.error  # noqa: E402
import fetch_open_data as fod  # noqa: E402

va_rule = next(s['fetch'] for s in reg['sources'] if s['id'] == 'va-facilities-api')
saved_key = os.environ.pop(va_rule['key_env'], None)
try:
    fod.fetch_va_facilities_api(va_rule, getter=lambda *a, **k: b'{}', pause=0)
    need(False, 'VA fetcher without a key is skipped')
except fod.Skipped:
    pass
os.environ[va_rule['key_env']] = 'test-key-not-real'
seen = []


def stub(url, headers=None):
    seen.append(url)
    need(headers == {'apikey': 'test-key-not-real'} and 'test-key-not-real' not in url, 'key only in the header')
    if url.startswith(va_rule['url']):  # the configured host refuses the key in this stub
        raise urllib.error.HTTPError(url, 401, 'refused', {}, io.BytesIO(b''))
    page = int(url.rsplit('page=', 1)[1])
    item = {'id': f'vha_{page}', 'attributes': {'name': 'Clinic', 'facilityType': 'va_health_facility',
                                                'address': {'physical': {'city': 'Little Rock', 'state': 'AR'}},
                                                'phone': {'main': '501-257-1000'}}}
    return _json.dumps({'data': [item], 'meta': {'pagination': {'totalPages': 2}}}).encode()


try:
    _, va_rows, va_base = fod.fetch_va_facilities_api(va_rule, getter=stub, pause=0)
finally:
    os.environ.pop(va_rule['key_env'], None)
    if saved_key is not None:
        os.environ[va_rule['key_env']] = saved_key
need(va_base == va_rule['fallback_url'], 'VA fetcher falls back to the other host once')
need(len(va_rows) == 2 * len(fod.VA_STATES), 'VA fetcher reads every page of every state')
need(va_rows[0]['phone'] == '501-257-1000' and va_rows[0]['city'] == 'Little Rock', 'VA rows are slimmed')
need(sum(u.startswith(va_rule['url']) for u in seen) == 1, 'the refused host is tried once, not per state')
need(fod.va_environment(va_rule['url']) == 'sandbox' and fod.va_environment(va_rule['fallback_url']) == 'production',
     'VA environment is recorded')
os.environ[va_rule['base_env']] = 'https://example.invalid/override'
need(fod.va_hosts(va_rule)[0] == 'https://example.invalid/override', 'VA_FACILITIES_API_BASE overrides the host')
os.environ.pop(va_rule['base_env'], None)
need(fod.va_hosts(va_rule)[0] == va_rule['url'], 'the registry url is the default host')

# Published VA locations (data/public/va-facilities/<st>.json, from scripts/mining/va_listings.py).
for path in sorted((c.ROOT / 'data' / 'public' / 'va-facilities').glob('*.json')):
    va = c.read(path)
    need(path.stem == va['state'].lower(), f'{path.name}: named for its state')
    need(va['source']['id'] == 'va-facilities-api' and va['source']['retrieved_on'], f'{path.name}: source and date')
    need(len({r['id'] for r in va['rows']}) == len(va['rows']), f'{path.name}: facility ids are unique')
    for r in va['rows']:
        need(r['state'] == va['state'], f'{path.name} {r["id"]}: in its state')
        main = re.split(r'\s*(?:x|ext|/)', r['phone'], flags=re.I)[0]
        need(len(c.digits(main)) == 10, f'{path.name} {r["id"]}: ten-digit phone, extension allowed')
        need(r['kind'] in ('health', 'vet_center', 'benefits', 'cemetery'), f'{path.name} {r["id"]}: kind')
        need(r['source_url'].startswith('https://') and r['retrieved_on'], f'{path.name} {r["id"]}: cited')
        need('closed' not in (r.get('notice') or '').lower(), f'{path.name} {r["id"]}: no closed facility')
    need((c.ROOT / 'va' / path.stem / 'index.html').is_file(), f'{path.name}: its page is built')

if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('mining pipeline checks passed')
