"""Fetch every open dataset in data/mining/sources.json that has a fetch rule, and save a dated snapshot.

    python3 scripts/mining/fetch_open_data.py             # fetch all
    python3 scripts/mining/fetch_open_data.py --only ID   # fetch one source

This is the only pipeline step that uses the network. It runs in GitHub Actions (.github/workflows/mine-sources.yml),
whose runners can reach public sites. A snapshot is saved to data/mining/snapshots/<source id>/<date>.json with the
exact URL, the retrieval date and a sha256 of the bytes received, so every later step can be traced to it.

Rules: public, open data only. No keys, accounts or sign-ins. A source that refuses the request, asks for a bot
check or answers with an error is recorded as failed and skipped; it is never retried another way.
"""
import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import date

import common as c

USER_AGENT = 'vhg-veteran-resource-guide-mining/1.0 (open data; github.com/travisvought-byte/vhg-veteran-resident-guide)'


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_socrata_json(rule):
    url = rule['url']
    sep = '&' if '?' in url else '?'
    body = get(url + sep + urllib.parse.urlencode({'$limit': 50000}))
    return body, json.loads(body)


FETCHERS = {'socrata_json': fetch_socrata_json}


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
            body, rows = FETCHERS[kind](src['fetch'])
        except Exception as exc:  # recorded, never worked around
            results.append({'source_id': src['id'], 'ok': False, 'error': f'{type(exc).__name__}: {exc}'[:300]})
            continue
        snap = {
            'source_id': src['id'],
            'source_url': src['url'],
            'download_url': src['fetch']['url'],
            'retrieved_on': args.today,
            'sha256': hashlib.sha256(body).hexdigest(),
            'row_count': len(rows) if isinstance(rows, list) else None,
            'rows': rows,
        }
        c.write_json(c.MINING / 'snapshots' / src['id'] / f'{args.today}.json', snap)
        results.append({'source_id': src['id'], 'ok': True, 'rows': snap['row_count'], 'sha256': snap['sha256']})
    c.write_json(c.MINING / 'snapshots' / 'last-run.json', {'run_on': args.today, 'results': results})
    for r in results:
        print(('ok    ' if r['ok'] else 'FAILED ') + r['source_id'] + ('' if r['ok'] else '  ' + r['error']))
    # One failed source is reported, not fatal; the run fails only when nothing could be fetched.
    sys.exit(1 if picked and not any(r['ok'] for r in results) else 0)


if __name__ == '__main__':
    main()
