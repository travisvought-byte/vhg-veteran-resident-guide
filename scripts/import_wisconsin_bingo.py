#!/usr/bin/env python3
"""Build data/public/wisconsin-bingo-sessions.json from the Wisconsin Department of Administration's
"Active Bingo Occasion Search" (charitable.wi.gov/bingooccasion/search).

    python3 scripts/import_wisconsin_bingo.py wi-occasions.csv --reviewed 2026-11-23 [--zip-file all_us_zipcodes.csv]

The search lists every licensed bingo occasion: the group, the place of play, its street, city and ZIP
code, the date and the start time. The page refuses automated readers from this environment's shell, so
the rows are read in a browser and saved first, as a CSV with the header
organization,location,address,city,zip,date,time (or as "ORG|LOCATION|ADDRESS|CITY|ZIP|MM/DD/YYYY|HH:MM AM" lines,
where a line "~|date|time" repeats the line above's group and place).

The state lists dated occasions, not weekly games, so this script finds the pattern: occasions at one
street address on one weekday at one start time. A pattern held on most of those weekdays in the period
the rows cover is a weekly game. One held on the same weeks of each month ("first and third Friday") gets
that label. Other patterns that recur at least three times are listed as "some weeks". Groups license
occasions in blocks of weeks or months, so each pattern is judged between its own first and last date. A date that does
not recur (a single fundraiser night) is left out. Counties come from the ZIP code (the same Midwire file,
checksum checked, as the rest of the site). No phone numbers: the state list gives none.
"""
import argparse, collections, csv, datetime, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bingo_pipeline as bp  # noqa: E402

OUT = ROOT / 'data/public/wisconsin-bingo-sessions.json'
SEARCH = 'https://charitable.wi.gov/bingooccasion/search'
SCOPE = ('Wisconsin Department of Administration, Active Bingo Occasion Search: licensed group, place of play, '
         'street address, ZIP code, date and start time of each occasion')
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
ORD = ['first', 'second', 'third', 'fourth', 'fifth']
NOTE = ("Days and start times are worked out from the dated bingo occasions the state has licensed. "
        "Some games are held only on certain weeks. Call ahead to confirm dates.")
GENERIC = re.compile(r'^(AMERICAN LEGION|LEGION|VFW|AMVETS|ELKS|EAGLES|MOOSE)?\s*(POST\s*)?(HALL|LODGE|CLUB|CLUBHOUSE|SOCIAL HALL|'
                     r'PARISH HALL|CHURCH HALL|SCHOOL|GYM|BUILDING)?$')


def _slug(text):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text.lower().replace('&', ' and ').replace("'", ''))).strip('-')


def _title(text):
    t = re.sub(r'\s+', ' ', text).strip()
    if t.isupper() and len(t) > 3:
        t = t.title()
        t = re.sub(r"'S\b", "'s", t)
        t = re.sub(r'\b(\d+)(St|Nd|Rd|Th)\b', lambda m: m.group(1) + m.group(2).lower(), t)
        t = re.sub(r'(?<=\w )(And|Of|The|At|In|On|For)\b', lambda m: m.group(1).lower(), t)
    return re.sub(r'\b(Vfw|Vfd|Amvets|Bpoe|Foe|Loom|Kc|Usa|Ii|Iii|Llc|Wi)\b',
                  lambda m: {'Amvets': 'AMVETS'}.get(m.group(1), m.group(1).upper()), t)


def _street(text):
    t = _title(text)
    # Wisconsin grid addresses ("N120 W15932 Freistadt Rd") keep their letters capitalised.
    return re.sub(r'\b([NSEW])(\d+)\b', lambda m: m.group(1).upper() + m.group(2), re.sub(r'\b([nsew]\d+)\b', lambda m: m.group(1).upper(), t))


SUFFIX = {'road': 'rd', 'street': 'st', 'avenue': 'ave', 'drive': 'dr', 'boulevard': 'blvd', 'highway': 'hwy',
          'lane': 'ln', 'court': 'ct', 'parkway': 'pkwy', 'county': 'cty', 'north': 'n', 'south': 's', 'east': 'e', 'west': 'w'}


def _street_key(text):
    words = re.findall(r'[a-z0-9]+', text.lower())
    return ''.join(SUFFIX.get(w, w) for w in words)


def _clock(text):
    m = re.fullmatch(r'(\d{1,2}):(\d\d) ?([AP])M', text.strip().upper())
    assert m, text
    return f'{int(m.group(1)) % 12 + (12 if m.group(3) == "P" else 0):02d}:{m.group(2)}'


def read_rows(paths):
    rows = []
    for path in paths:
        text = pathlib.Path(path).read_text()
        if text.startswith(('org,', 'organization,')):
            rows += [dict(r, org=r.get('org') or r['organization']) for r in csv.DictReader(text.splitlines())]
            continue
        last = None
        for line in text.splitlines():
            p = [x.strip() for x in line.split('|')]
            if len(p) == 3 and p[0] == '~':
                assert last, line
                rows.append(dict(last, date=p[1], time=p[2]))
            elif len(p) == 7:
                last = dict(zip(('org', 'location', 'address', 'city', 'zip'), p[:5]))
                rows.append(dict(last, date=p[5], time=p[6]))
            elif line.strip():
                raise SystemExit(f'cannot read line: {line}')
    seen, out = set(), []
    for r in rows:  # the same occasion read twice (overlapping pages) counts once
        k = (r['org'].upper(), r['address'].upper(), r['date'], r['time'])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def label_for(dates, day):
    """None for a weekly game, a label for a monthly pattern, '' to leave the pattern out."""
    first, last = dates[0], dates[-1]
    possible = sum(1 for i in range((last - first).days + 1) if (first + datetime.timedelta(i)).weekday() == (day - 1) % 7)
    if len(dates) >= 4 and len(dates) >= 0.75 * possible:
        return None
    months = {(d.year, d.month) for d in dates}
    weeks = sorted({(d.day - 1) // 7 for d in dates})
    if len(months) >= 2 and len(dates) >= 2 and len(weeks) <= 2 and len(dates) >= len(months) * len(weeks) * 0.6:
        words = [ORD[w] for w in weeks]
        joined = words[0] if len(words) == 1 else ' and '.join(words)
        return f'{joined[0].upper()}{joined[1:]} {DAYS[day]} of the month'
    if len(dates) >= 3:
        return f'Some {DAYS[day]}s; dates vary, see the state list'
    return ''


def build(rows, reviewed, counties, zips, towns):
    dates = [datetime.datetime.strptime(r['date'], '%m/%d/%Y').date() for r in rows]
    first, last = min(dates), max(dates)
    halls = collections.OrderedDict()
    for r, d in zip(rows, dates):
        zipc = r['zip'][:5]
        key = (_street_key(r['address']), zipc)
        h = halls.setdefault(key, {'r': r, 'zip': zipc, 'locs': collections.Counter(),
                                   'pat': collections.defaultdict(set),
                                   'who': collections.defaultdict(collections.Counter)})
        h['locs'][r['location'].strip()] += 1
        day = (d.weekday() + 1) % 7  # Sunday 0
        h['pat'][(day, _clock(r['time']))].add(d)
        h['who'][(day, _clock(r['time']))][r['org'].strip()] += 1

    out, ids, skipped = [], set(), collections.Counter()
    for key, h in halls.items():
        sessions, shared, kept = [], set(), collections.Counter()
        for (day, start), ds in h['pat'].items():
            groups = [_title(o) for o, _ in h['who'][(day, start)].most_common()]
            org = groups[0]  # groups that share a weekly slot take turns; the record's notes name them all
            if len(groups) > 1:
                shared.add((day, start))
            lab = label_for(sorted(ds), day)
            if lab == '':
                skipped['one-off dates'] += len(ds)
                continue
            kept.update(h['who'][(day, start)])
            row = {'day': day, 'start': start, 'organization': org}
            if lab:
                row['label'] = lab
            sessions.append(row)
        if not sessions:
            skipped['places with no repeating game'] += 1
            continue
        zipc, notes = h['zip'], []
        if zipc not in zips:  # a post-office-box ZIP code: use the town's ZIP code that the map knows
            alt = sorted(z for z in towns.get(_title(h['r']['city']).lower(), []) if z in zips)
            if alt:
                zipc = alt[0]
                notes.append(f"ZIP code: the state list gives {h['zip']}, which has no map point, so this listing uses the "
                             f"town's ZIP code {zipc}. Distances are approximate.")
        if zipc not in zips or counties.get(zipc, ('', ''))[0] != 'WI':
            skipped['ZIP code not on the site map'] += 1
            print(f'skip: {h["r"]["address"]}, {h["r"]["city"]} {zipc}: ZIP not usable', file=sys.stderr)
            continue
        loc = h['locs'].most_common(1)[0][0]
        org = kept.most_common(1)[0][0]
        name = _title(org if not loc or (GENERIC.match(loc.upper()) and loc.upper().strip()) else loc)
        city = _title(h['r']['city'])
        base = vid = 'wi-' + _slug(name) + '-' + _slug(city)
        n = 2
        while vid in ids:
            vid, n = f'{base}-{n}', n + 1
        ids.add(vid)
        orgs = [_title(o) for o, _ in kept.most_common()]
        rec = {'id': vid, 'state': 'WI', 'name': name, 'organizations': list(dict.fromkeys(orgs)),
               'address': f"{_street(h['r']['address'])}, {city}, WI {zipc}", 'city': city, 'zip': zipc,
               'county': counties[zipc][1].removesuffix(' County')}
        rec['sessions'] = sorted(sessions, key=lambda s: ((s['day'] + 6) % 7, s['start'], s['organization']))
        if any(s.get('label') for s in rec['sessions']):
            rec['schedule_note'] = NOTE
        if shared:
            notes.insert(0, 'Several groups hold games here and take turns: ' + ', '.join(rec['organizations']) + '.')
        if notes:
            rec['notes'] = notes
        rec.update({'reviewed_on': reviewed, 'sources': [{'url': SEARCH, 'reviewed_on': reviewed, 'scope': SCOPE}]})
        out.append(rec)
    print(f'rows cover {first} to {last}; left out: {dict(skipped)}', file=sys.stderr)
    return sorted(out, key=lambda v: (v['county'], v['city'], v['name']))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('rows', nargs='+')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    ap.add_argument('--zip-file', help='local copy of the Midwire ZIP code file (checksum checked)')
    ap.add_argument('--out', default=str(OUT))
    a = ap.parse_args()
    rows = read_rows(a.rows)
    zips = json.loads((ROOT / 'findbingo-site/zips.json').read_text())
    raw = pathlib.Path(a.zip_file).read_text() if a.zip_file else None
    counties = bp.zip_counties(a.zip_file)  # checks the file's checksum
    towns = collections.defaultdict(list)
    for r in csv.DictReader((raw or bp.subprocess.run(['curl', '-sSL', bp.ZIP_FILE], capture_output=True, text=True,
                                                      check=True).stdout).splitlines()):
        if r['state'] == 'WI':
            towns[r['city'].lower()].append(r['code'])
    halls = build(rows, a.reviewed, counties, zips, towns)
    pathlib.Path(a.out).write_text(json.dumps(halls, indent=1, ensure_ascii=False) + '\n')
    games = sum(len(h['sessions']) for h in halls)
    print(f'{len(rows)} occasions -> {games} games at {len(halls)} places written to {a.out}')


if __name__ == '__main__':
    main()
