#!/usr/bin/env python3
"""Rebuild data/public/missouri-bingo-sessions.json from rows read off the Missouri Gaming Commission's
"Find Local Bingo Games" page.

    python3 scripts/read_missouri_finder.py missouri-finder.json
    python3 scripts/import_missouri_bingo.py missouri-finder.json --reviewed 2026-11-19

Each row is one licensed game: the location of play (its name, street and phone), city, county, the
start time, which weeks of the month it is played ("Every", "1st & 3rd" ...) and the weekday. Rows at
one street address become one hall, as with Michigan, Texas and Virginia. The page gives no end time,
so sessions carry a start time only, and no ZIP code, so the U.S. Census Geocoder supplies it: the
street address first; when the Census cannot match the address (highway corners and the like), the
town's ZIP code from the same Midwire/GeoNames file as the site's ZIP points, with a note on the
listing. Halls already in the data file keep their ZIP code and county.
"""
import argparse, collections, csv, datetime, io, json, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/missouri-bingo-sessions.json'
FINDER = 'https://www.mgc.dps.mo.gov/BingoWebLocal/frmWebFindLocalBingoGame.aspx'
ZIP_FILE = 'https://raw.githubusercontent.com/midwire/free_zipcode_data/e00aec159e76335c3d62df70d07e7e207be8f4fc/all_us_zipcodes.csv'
ZIP_SHA256 = '808c04000fe8b1f26271ff4e8546cefdfe4daf1b1e490f507f1c5656ec903d35'
DAY_CELLS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']  # cells 5 to 11
# Towns the ZIP code file files under another post office name, with the ZIP point nearest the town.
TOWN_ZIPS = {'shrewsbury': '63119'}  # the file lists 63119 as Saint Louis; its point is about a mile from Shrewsbury
ORD = {'1': 'first', '2': 'second', '3': 'third', '4': 'fourth', '5': 'fifth'}
SCOPE = ("Missouri Gaming Commission, Find Local Bingo Games: location of play, phone, city, county, "
         "start time, weekday and which weeks of the month")
NOTE_WEEKS = ("Days and start times from the Missouri Gaming Commission's list of local bingo games. "
              "Some games are played only on certain weeks of the month. Call ahead to confirm dates.")


def _curl(*args):
    return subprocess.run(['curl', '-sS', '-m', '300', *args], capture_output=True, text=True, check=True).stdout


def _slug(text):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text.lower().replace('&', ' and ').replace("'", ''))).strip('-')


def _title(text):
    text = text.title() if text.isupper() and len(text) > 4 else text
    return re.sub(r'\b(Vfw|Vfd|Bpoe|Amvets|Usa|Kc)\b', lambda m: {'Amvets': 'AMVETS'}.get(m.group(1), m.group(1).upper()), text)


def _clock(text):
    m = re.fullmatch(r'(\d{1,2}):(\d\d) ([AP])M', text.strip())
    assert m, text
    return f'{int(m.group(1)) % 12 + (12 if m.group(3) == "P" else 0):02d}:{m.group(2)}'


def _county(text):
    # The page writes "St. Louis County" and "St. Louis City" for the two places; the rest are bare names.
    text = text.strip()
    if text == 'St. Louis City':
        return 'St. Louis city'
    return text[:-7] if text.endswith(' County') else text


def weeks_label(occur, day):
    """The page's "Occur" cell as words, or None when the game is every week."""
    t = re.sub(r'\s+', ' ', occur).strip()
    if t.lower() in ('every', day.lower()):
        return None
    if re.search(r'[A-Za-z]{4,}-|Oct|May|Sept', t):  # a seasonal note: keep the state's words
        return t.replace('&', 'and') + ' (from the state list)'
    nums = re.findall(r'([1-5])(?:st|nd|rd|th|ST|ND|RD|TH)?', re.sub(r'\b(Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day\b', '', t))
    assert nums and len(set(nums)) == len(nums), occur
    words = [ORD[n] for n in nums]
    joined = words[0] if len(words) == 1 else ', '.join(words[:-1]) + ' and ' + words[-1]
    return f'{joined[0].upper()}{joined[1:]} {day} of the month'


def parse(rows):
    games = []
    for cells in rows:
        assert len(cells) == 12, cells
        lines = [x.strip() for x in cells[0].split('\n') if x.strip()]
        phone = None
        if lines and re.fullmatch(r'\(\s*\)\s*-?', lines[-1]):  # an empty phone shows as "() -"
            lines.pop()
        if lines and re.fullmatch(r'\(\d{3}\) \d{3}-\d{4}', lines[-1]):
            phone = re.sub(r'\((\d{3})\) (\d{3})-(\d{4})', r'\1-\2-\3', lines.pop())
        assert len(lines) == 2, cells  # name, street
        days = [i for i, c in enumerate(cells[5:]) if c.strip()]
        assert len(days) == 1 and cells[5 + days[0]].strip() == DAY_CELLS[days[0]], cells
        day = days[0]
        games.append({'name': _title(re.sub(r'\s+', ' ', lines[0])), 'street': re.sub(r'\s+', ' ', lines[1]),
                      'phone': phone, 'city': _title(cells[1].strip()), 'county': _county(cells[2]),
                      'day': day, 'start': _clock(cells[3]), 'label': weeks_label(cells[4], DAY_CELLS[day])})
    return games


def _town(name):
    # "DeSoto" and "De Soto", "St. Robert" and "Saint Robert" are the same town.
    return re.sub(r'[^a-z]', '', re.sub(r'^(st|saint)\.?\s', 'st', name.lower()))


def _zip_towns():
    import hashlib
    text = _curl(ZIP_FILE)
    assert hashlib.sha256(text.encode()).hexdigest() == ZIP_SHA256, 'the ZIP code file changed'
    towns = collections.defaultdict(list)
    for r in csv.DictReader(io.StringIO(text)):
        if r['state'] == 'MO':
            towns[_town(r['city'])].append((r['code'], r['county'].title()))
    return towns


def geocode(halls):
    """{key: (zip, county from Census or None, how)} for halls given as {key: (street, city)}."""
    rows = {}
    keys = list(halls)
    with tempfile.NamedTemporaryFile('w', suffix='.csv', newline='') as f:
        csv.writer(f).writerows([i, street, city, 'MO', ''] for i, (street, city) in enumerate(halls[k] for k in keys))
        f.flush()
        for r in csv.reader(_curl('-F', f'addressFile=@{f.name}', '-F', 'benchmark=Public_AR_Current', '-F', 'vintage=Current_Current',
                                  'https://geocoding.geo.census.gov/geocoder/geographies/addressbatch').splitlines()):
            rows[int(r[0])] = r
    names = {}
    for line in _curl('https://www2.census.gov/geo/docs/reference/codes2020/cou/st29_mo_cou2020.txt').split('\n')[1:]:
        p = line.split('|')
        if len(p) > 4:
            names[p[2]] = p[4][:-7] if p[4].endswith(' County') else p[4]
    found = {}
    for i, k in enumerate(keys):
        r = rows.get(i)
        if r and r[2] == 'Match' and len(r) > 9 and r[8] == '29':
            m = re.search(r', (\d{5})$', r[4])
            if m:
                found[k] = (m.group(1), names.get(r[9]), 'address')
    return found


def build(games, reviewed, old):
    by_addr = collections.OrderedDict()
    for g in games:
        key = (re.sub(r'[^a-z0-9]', '', g['street'].lower()), g['city'].lower())
        hall = by_addr.setdefault(key, {'names': [], 'phones': [], 'street': g['street'], 'city': g['city'],
                                        'counties': [], 'organizations': [], 'sessions': []})
        hall['names'].append(g['name'])
        hall['counties'].append(g['county'])
        if g['name'] not in hall['organizations']:
            hall['organizations'].append(g['name'])
        if g['phone']:
            hall['phones'].append(g['phone'])
        row = {'day': g['day'], 'start': g['start'], 'organization': g['name']}
        if g['label']:
            row['label'] = g['label']
        if row not in hall['sessions']:
            hall['sessions'].append(row)

    old_by_key = {}
    for v in old:
        street = v['address'].rsplit(', ', 2)[0]
        old_by_key[(re.sub(r'[^a-z0-9]', '', street.lower()), v['city'].lower())] = v
    need = {k: (h['street'], h['city']) for k, h in by_addr.items() if k not in old_by_key}
    found = geocode(need) if need else {}
    towns = _zip_towns() if len(found) < len(need) else {}

    out, ids, report = [], set(), collections.Counter()
    for key, h in by_addr.items():
        county = collections.Counter(h['counties']).most_common(1)[0][0]
        notes = []
        if key in old_by_key:
            zipc, how = old_by_key[key]['zip'], 'kept'
            notes = [n for n in old_by_key[key].get('notes', []) if n.startswith('ZIP code')]
        elif key in found:
            zipc, census_county, how = found[key]
            if census_county and census_county != county:
                print(f'note: {h["street"]}, {h["city"]}: state list says {county}, Census says {census_county}; keeping the state list',
                      file=sys.stderr)
        else:
            cands = sorted({z for z, c in towns.get(_town(h['city']), []) if c == county.replace(' city', '').title()}
                           or {z for z, _ in towns.get(_town(h['city']), [])})
            cands = cands or ([TOWN_ZIPS[_town(h['city'])]] if _town(h['city']) in TOWN_ZIPS else [])
            assert cands, f'no ZIP code for {h["city"]}: add it to TOWN_ZIPS'
            zipc, how = cands[0], 'town'
            notes.append("ZIP code: the state list gives no ZIP code and the street address could not be matched, so this is the "
                         f"town's ZIP code{' (the first of several)' if len(cands) > 1 else ''}. Distances are approximate.")
        report[how] += 1
        name = collections.Counter(h['names']).most_common(1)[0][0]
        base = vid = 'mo-' + _slug(name) + '-' + _slug(h['city'])
        n = 2
        while vid in ids:
            vid, n = f'{base}-{n}', n + 1
        ids.add(vid)
        rec = {'id': vid, 'state': 'MO', 'name': name, 'organizations': h['organizations'],
               'address': f"{h['street']}, {h['city']}, MO {zipc}", 'city': h['city'], 'zip': zipc, 'county': county}
        if h['phones']:
            rec['phone'] = collections.Counter(h['phones']).most_common(1)[0][0]
        rec['sessions'] = sorted(h['sessions'], key=lambda r: ((r['day'] + 6) % 7, r['start'], r['organization']))
        if any(s.get('label') for s in rec['sessions']):
            rec['schedule_note'] = NOTE_WEEKS
        if notes:
            rec['notes'] = notes
        rec.update({'reviewed_on': reviewed, 'sources': [{'url': FINDER, 'reviewed_on': reviewed, 'scope': SCOPE}]})
        out.append(rec)
    print('ZIP codes:', dict(report), file=sys.stderr)
    return sorted(out, key=lambda v: (v['county'], v['city'], v['name']))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('rows')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    ap.add_argument('--out', default=str(OUT))
    a = ap.parse_args()
    games = parse(json.load(open(a.rows)))
    out_path = pathlib.Path(a.out)
    old = json.loads(out_path.read_text()) if out_path.exists() else []
    halls = build(games, a.reviewed, old)
    out_path.write_text(json.dumps(halls, indent=1, ensure_ascii=False) + '\n')
    print(f'{len(games)} games at {len(halls)} halls written to {out_path}')


if __name__ == '__main__':
    main()
