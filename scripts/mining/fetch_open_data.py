"""Fetch every open dataset in data/mining/sources.json that has a fetch rule, and save a dated snapshot.

    python3 scripts/mining/fetch_open_data.py             # fetch all
    python3 scripts/mining/fetch_open_data.py --only ID   # fetch one source

This is the only pipeline step that uses the network. It runs in GitHub Actions (.github/workflows/mine-sources.yml),
whose runners can reach public sites. A snapshot is saved to data/mining/snapshots/<source id>/<date>.json with the
exact URL, the retrieval date and a sha256 of the bytes received, so every later step can be traced to it.

Rules: public data only. No accounts or sign-ins. The one keyed source, the VA Facilities API, uses a key the owner
registered and stored as the repository secret VA_FACILITIES_API_KEY; the workflow passes it in as an environment
variable. The key travels only in a request header and is never printed, logged or saved. With no key set, that
source is recorded as skipped and the rest of the run goes on. A source that refuses the request, asks for a bot
check or answers with an error is recorded as failed and skipped; it is never retried another way.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

import common as c

USER_AGENT = 'vhg-veteran-resource-guide-mining/1.0 (open data; github.com/travisvought-byte/vhg-veteran-resident-guide)'


class Skipped(Exception):
    """The source cannot run in this environment (for example, its key is not set). Not a failure."""


def get(url, timeout=60, headers=None):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json', **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_socrata_json(rule):
    url = rule['url']
    sep = '&' if '?' in url else '?'
    body = get(url + sep + urllib.parse.urlencode({'$limit': 50000}))
    return body, json.loads(body)


# States, DC and the territories the VA lists facilities in.
VA_STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
             'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH',
             'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'PR', 'GU', 'VI',
             'AS', 'MP']
VA_PAUSE_SECONDS = 1.1  # the VA allows about 60 requests a minute per key


def slim_facility(item):
    """Keep what the guide can use: name, kind, address, phone, website, hours and location."""
    a = item.get('attributes') or {}
    phys = (a.get('address') or {}).get('physical') or {}
    phone = a.get('phone') or {}
    return {
        'id': item.get('id'), 'name': a.get('name'), 'facility_type': a.get('facilityType'),
        'classification': a.get('classification'), 'website': a.get('website'),
        'address1': phys.get('address1'), 'address2': phys.get('address2'), 'city': phys.get('city'),
        'state': phys.get('state'), 'zip': phys.get('zip'),
        'phone': phone.get('main'), 'after_hours_phone': phone.get('afterHours'),
        'mental_health_phone': phone.get('mentalHealthClinic'), 'hours': a.get('hours'),
        'lat': a.get('lat'), 'long': a.get('long'), 'mobile': a.get('mobile'),
        'operating_status': (a.get('operatingStatus') or {}).get('code'),
    }


def va_hosts(rule):
    """The base URL to use, then the one to try if it refuses the key.

    The registry's fetch rule sets `url` (now the sandbox, since the owner's key is a sandbox key) and `fallback_url`.
    The repository variable VA_FACILITIES_API_BASE, when set, overrides `url`, so moving to production is one setting.
    """
    first = os.environ.get(rule.get('base_env') or '', '').strip() or rule['url']
    return [h for h in dict.fromkeys([first, rule.get('fallback_url')]) if h]


def va_environment(base):
    return 'sandbox' if 'sandbox' in (base or '') else 'production'


def fetch_va_facilities_api(rule, getter=None, pause=VA_PAUSE_SECONDS):
    key = os.environ.get(rule['key_env'], '').strip()
    if not key:
        raise Skipped(f"{rule['key_env']} is not set")
    getter = getter or get
    headers = {'apikey': key}
    hosts = va_hosts(rule)
    base, digest, rows = None, hashlib.sha256(), []
    for state in VA_STATES:
        page = 1
        while True:
            query = urllib.parse.urlencode({'state': state, 'per_page': 1000, 'page': page})
            if base is None:
                # Try the configured host, then the other one, once; keep whichever accepts the key.
                for host in hosts:
                    try:
                        body = getter(f'{host}?{query}', headers=headers)
                        base = host
                        break
                    except urllib.error.HTTPError as exc:
                        if exc.code not in (401, 403):
                            raise
                else:
                    raise PermissionError('the key was refused by every VA Facilities API host')
            else:
                body = getter(f'{base}?{query}', headers=headers)
            digest.update(body)
            data = json.loads(body)
            rows.extend(slim_facility(item) for item in data.get('data') or [])
            pages = (((data.get('meta') or {}).get('pagination') or {}).get('totalPages')) or 1
            if pause:
                time.sleep(pause)
            if page >= pages:
                break
            page += 1
    return digest, rows, base


def fetch_va_facilities_snapshot(rule):
    digest, rows, base = fetch_va_facilities_api(rule)
    return digest.hexdigest(), rows, base


FETCHERS = {'socrata_json': fetch_socrata_json, 'va_facilities_api': fetch_va_facilities_snapshot}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--today', default=date.today().isoformat())
    args = ap.parse_args()
    sources = c.read(c.MINING / 'sources.json')['sources']
    picked = [s for s in sources if s.get('fetch') and s['status'] in ('active', 'benchmark')
              and (not args.only or s['id'] == args.only)]
    results = []
    for src in picked:
        kind = src['fetch']['kind']
        try:
            body, rows, *rest = FETCHERS[kind](src['fetch'])
        except Skipped as exc:
            results.append({'source_id': src['id'], 'ok': False, 'skipped': True, 'error': f'skipped: {exc}'})
            continue
        except Exception as exc:  # recorded, never worked around
            results.append({'source_id': src['id'], 'ok': False, 'error': f'{type(exc).__name__}: {exc}'[:300]})
            continue
        snap = {
            'source_id': src['id'],
            'source_url': src['url'],
            'download_url': rest[0] if rest and rest[0] else src['fetch']['url'],
            'retrieved_on': args.today,
            'sha256': body if isinstance(body, str) else hashlib.sha256(body).hexdigest(),
            'row_count': len(rows) if isinstance(rows, list) else None,
            'environment': va_environment(rest[0]) if rest and rest[0] else None,
            'rows': rows,
        }
        c.write_json(c.MINING / 'snapshots' / src['id'] / f'{args.today}.json', snap)
        results.append({'source_id': src['id'], 'ok': True, 'rows': snap['row_count'], 'sha256': snap['sha256'],
                        'host': snap['download_url'], 'environment': snap['environment']})
    c.write_json(c.MINING / 'snapshots' / 'last-run.json', {'run_on': args.today, 'results': results})
    for r in results:
        label = 'ok     ' if r['ok'] else ('SKIPPED ' if r.get('skipped') else 'FAILED ')
        print(label + r['source_id'] + ('' if r['ok'] else '  ' + r['error']))
    # One failed source is reported, not fatal; the run fails only when nothing it tried could be fetched.
    tried = [r for r in results if not r.get('skipped')]
    sys.exit(1 if tried and not any(r['ok'] for r in tried) else 0)


if __name__ == '__main__':
    main()
