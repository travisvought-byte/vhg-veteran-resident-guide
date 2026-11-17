#!/usr/bin/env python3
"""Rebuild data/public/new-mexico-bingo-licenses.json from the New Mexico Gaming Control Board's list.

The board's page "Bingo, Raffle, & Pull-Tab Map Locations and Info" shows a map and, below it, each licensed
group by town with its address and phone:
https://www.gcb.nm.gov/bingo-raffle-pull-tab-map-locations-and-info/

    python3 scripts/import_new_mexico_bingo.py --reviewed 2026-11-17 [--page saved.html]

The page does not say which of bingo, raffles or pull-tabs each group holds, and gives no license number,
end date or game days, so the site says exactly that. The town comes from the page's own town headings
(one address line misspells Alamogordo). Counties come from the U.S. Census Geocoder (bingo_counties.py).
"""
import argparse, datetime, html, json, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bingo_counties import counties  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/new-mexico-bingo-licenses.json'
URL = 'https://www.gcb.nm.gov/bingo-raffle-pull-tab-map-locations-and-info/'


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def parse(page):
    text = html.unescape(re.sub(r'[ \t]+', ' ', re.sub(r'<[^>]+>', '\n', re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S))))
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    rest = lines[next(k for k, l in enumerate(lines) if 'Scroll past map' in l) + 1:]
    rows, town, k = [], None, 0
    while k < len(rest):
        m = re.fullmatch(r'(.+?), ?NM (\d{5})(?:-\d{4})?', rest[k + 2]) if k + 2 < len(rest) else None
        if m:
            row = {'name': rest[k], 'street': rest[k + 1].replace('Streer', 'Street'), 'town': town, 'zip': m.group(2)}
            k += 3
            if k < len(rest) and re.fullmatch(r'\d{3}-\d{3}-\d{4}', rest[k]):
                row['phone'] = rest[k]
                k += 1
            rows.append(row)
        elif len(rest[k]) > 40 or rest[k] in ('Contact Us',):
            break
        else:
            town = rest[k]
            k += 1
    assert rows and all(r['town'] for r in rows), 'the page layout changed'
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    ap.add_argument('--page', help='a saved copy of the page; otherwise it is downloaded')
    a = ap.parse_args()
    page = pathlib.Path(a.page).read_text() if a.page else subprocess.run(['curl', '-sS', '-m', '60', '-L', URL], capture_output=True, text=True, check=True).stdout
    known = {r['address']: r['county'] for r in json.loads(OUT.read_text())} if OUT.exists() else {}
    recs, ids = [], set()
    for r in parse(page):
        rid = 'nm-' + _slug(r['name'] + ' ' + r['town'])
        assert rid not in ids, rid
        ids.add(rid)
        rec = {'id': rid, 'state': 'NM', 'name': r['name'], 'address': f"{r['street']}, {r['town']}, NM {r['zip']}", 'city': r['town'], 'zip': r['zip'], 'county': None}
        if r.get('phone'):
            rec['phone'] = r['phone']
        rec.update({'license_type': 'bingo, raffle or pull-tab license', 'reviewed_on': a.reviewed,
                    'sources': [{'url': URL, 'reviewed_on': a.reviewed,
                                 'scope': 'New Mexico Gaming Control Board, Bingo, Raffle and Pull-Tab Map Locations and Info: group, address and phone, by town'}]})
        rec['county'] = known.get(rec['address'])
        recs.append(rec)
    need = [(rec, rec['address'].split(', ')[0]) for rec in recs if not rec['county']]
    if need:
        for rid, (county, how) in counties(need, 'NM', '35', ROOT).items():
            rec = next(x for x in recs if x['id'] == rid)
            rec['county'] = county
            if how != 'address':
                print(f'county from {how}: {rec["address"]} -> {county}')
    missing = [r['address'] for r in recs if not r['county']]
    if missing:
        sys.exit('No county found for:\n  ' + '\n  '.join(missing))
    OUT.write_text(json.dumps(sorted(recs, key=lambda r: (r['county'], r['city'], r['name'])), ensure_ascii=False, indent=1) + '\n')
    print(f'{OUT.relative_to(ROOT)} written, reviewed {a.reviewed}.')


if __name__ == '__main__':
    main()
