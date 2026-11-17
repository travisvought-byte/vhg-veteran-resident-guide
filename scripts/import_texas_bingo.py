#!/usr/bin/env python3
"""Rebuild data/public/texas-bingo-halls.json from rows read off the Texas Bingo Hall Locator.

    python3 scripts/read_texas_locator.py texas-locator.json
    python3 scripts/import_texas_bingo.py texas-locator.json --reviewed 2026-11-17 --geocode

The locator lists each licensed organization with its hall and its licensed days and times. Organizations
at one address become one hall, as with Michigan and Virginia. The hall's phone is kept when the locator
gives one. The locator has no county: a hall already in the data file keeps its county, and new addresses
need --geocode (U.S. Census Geocoder, see bingo_counties.py).
"""
import argparse, collections, datetime, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bingo_counties import counties  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/texas-bingo-halls.json'
LOCATOR = 'https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf'
DAYS = {'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6}


def _clock(text):
    h, m = int(text[:2]), text[3:5]
    return f'{h % 12 + (12 if text.endswith("PM") else 0):02d}:{m}'


def _slug(text):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text.lower().replace('&', ' and ').replace("'", ''))).strip('-')


def _title(text):
    # The locator writes most names in title case already; fix names written all in capitals, and the
    # short forms people know in capitals.
    text = text.title() if text.isupper() and len(text) > 4 else text
    return re.sub(r'\b(Vfw|Vfd|Kc|Bpoe|Amvets|Usa)\b', lambda m: {'Amvets': 'AMVETS'}.get(m.group(1), m.group(1).upper()), text)


def halls(rows, reviewed):
    by_addr = collections.OrderedDict()
    for org, _site, place, phone, street, city, zipc, times in rows:
        org, place, street, city = (re.sub(r'\s+', ' ', x).strip() for x in (org, place, street, city))
        zipc = re.sub(r'\D', '', zipc)[:5]
        hall = by_addr.setdefault((re.sub(r'[^a-z0-9]', '', street.lower()), zipc),
                                  {'names': [], 'organizations': [], 'phones': [], 'street': street, 'city': _title(city), 'zip': zipc, 'sessions': []})
        hall['names'].append(place or org)
        if org not in hall['organizations']:
            hall['organizations'].append(org)
        if phone:
            hall['phones'].append(re.sub(r'\((\d{3})\) (\d{3})-(\d{4})', r'\1-\2-\3', phone))
        for line in times.split('\n'):
            m = re.fullmatch(r'(SUN|MON|TUE|WED|THU|FRI|SAT) (\d\d:\d\d [AP]M) To (\d\d:\d\d [AP]M)', line.strip())
            assert m, line
            row = {'day': DAYS[m.group(1)], 'start': _clock(m.group(2)), 'end': _clock(m.group(3)), 'organization': org}
            if row not in hall['sessions']:
                hall['sessions'].append(row)
    out, ids = [], set()
    for hall in by_addr.values():
        name = _title(collections.Counter(hall['names']).most_common(1)[0][0])
        base = vid = 'tx-' + _slug(name) + '-' + _slug(hall['city'])
        n = 2
        while vid in ids:
            vid, n = f'{base}-{n}', n + 1
        ids.add(vid)
        rec = {'id': vid, 'state': 'TX', 'name': name, 'organizations': hall['organizations'],
               'address': f"{hall['street']}, {hall['city']}, TX {hall['zip']}", 'city': hall['city'], 'zip': hall['zip'], 'county': None}
        phones = collections.Counter(hall['phones'])
        if phones:
            rec['phone'] = phones.most_common(1)[0][0]
        # Monday first, as the site shows them.
        rec['sessions'] = sorted(hall['sessions'], key=lambda r: ((r['day'] + 6) % 7, r['start'], r['organization']))
        rec.update({'reviewed_on': reviewed, 'sources': [{'url': LOCATOR, 'reviewed_on': reviewed,
                    'scope': 'Texas Bingo Hall Locator (Texas Department of Licensing and Regulation): licensed organization, hall, phone, address, and licensed days and times'}]})
        out.append((rec, hall['street']))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('rows')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    ap.add_argument('--geocode', action='store_true')
    a = ap.parse_args()
    built = halls(json.loads(pathlib.Path(a.rows).read_text()), a.reviewed)
    known = {v['address']: v['county'] for v in json.loads(OUT.read_text())} if OUT.exists() else {}
    for rec, _ in built:
        rec['county'] = known.get(rec['address'])
    need = [(rec, street) for rec, street in built if not rec['county']]
    if need and a.geocode:
        for rec_id, (county, how) in counties(need, 'TX', '48', ROOT).items():
            rec = next(r for r, _ in need if r['id'] == rec_id)
            rec['county'] = county
            if how != 'address':
                print(f'county from {how}: {rec["address"]} -> {county}')
    missing = [rec['address'] for rec, _ in built if not rec['county']]
    if missing:
        sys.exit('No county yet (run with --geocode, or check the address):\n  ' + '\n  '.join(missing))
    records = sorted((rec for rec, _ in built), key=lambda r: (r['county'], r['city'], r['name'], r['id']))
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')
    print(f'{OUT.relative_to(ROOT)} written, reviewed {a.reviewed}.')


if __name__ == '__main__':
    main()
