#!/usr/bin/env python3
"""Rebuild data/public/virginia-bingo-sessions.json from Virginia's directory of bingo sessions.

The Office of Charitable and Regulatory Programs (VDACS) reissues the directory as a PDF:
https://www.vdacs.virginia.gov/pdf/bingo_events.pdf ("Registered Gaming Activity"). Download it, then:

    python3 scripts/import_virginia_bingo.py bingo_events.pdf --reviewed 2026-11-17 [--geocode]

What is kept: weekly sessions (a row whose day reads "Tuesdays", "Fridays" and so on), with the
doors-open and doors-close times. What is left out: one-day dated events, cancelled rows, and rows that
ended before the review date. Organizations that share an address become one hall.

The directory has no county. A hall already in the data file keeps its county; a new address needs
--geocode, which asks the U.S. Census Geocoder (the address, then other halls in the same ZIP code,
then the ZIP code's centre point). Independent cities are stored the Census way, "Richmond city",
and the site shows them as "City of Richmond".

Needs poppler's pdftotext. Then run python3 scripts/build_public.py and node tests/findbingo.cjs.
"""
import argparse, collections, csv, datetime, html, json, pathlib, re, subprocess, sys, tempfile, time, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/virginia-bingo-sessions.json'
PDF_URL = 'https://www.vdacs.virginia.gov/pdf/bingo_events.pdf'
DAYS = {'sundays': 0, 'mondays': 1, 'tuesdays': 2, 'wednesdays': 3, 'thursdays': 4, 'fridays': 5, 'saturdays': 6}
DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
WEEKDAYS = r'(?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)days'
SCHEDULE_NOTE = ("Usual days and door times from Virginia's directory of bingo sessions. Some dates are skipped, "
                 "especially around holidays. Call ahead before you go.")
SOCIAL_NOTE = ('The state lists a game here as held in the social quarters. Those games may be for members and their guests, '
               'so call first.')
# Mistakes in the state's directory, fixed here and explained on the listing.
ZIP_FIXES = {('8195 South 71', 'Castlewood', '23224'): ('24224', "The state's directory shows ZIP code 23224 for this address. "
                                                         "Castlewood's ZIP code is 24224, so we use that.")}
# Column positions in the PDF, in points: names and addresses, then permit dates, the day, and the two door times.
LEFT_END, DAY_START, DAY_END, CLOSE_START = 330, 450, 622, 700


def _pages(pdf):
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / 'words.html'
        subprocess.run(['pdftotext', '-bbox-layout', str(pdf), str(out)], check=True)
        text = out.read_text()
    for page in re.findall(r'<page [^>]*>(.*?)</page>', text, re.S):
        yield [(float(x), float(y), html.unescape(w)) for x, y, w in
               re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">(.*?)</word>', page)]


def _lines(words, lo, hi):
    rows = []
    for x, y, w in sorted((w for w in words if lo <= w[0] < hi), key=lambda w: (w[1], w[0])):
        if rows and abs(rows[-1][0] - y) <= 2.5:
            rows[-1][1].append((x, w))
        else:
            rows.append([y, [(x, w)]])
    return [(y, sorted(ws)) for y, ws in rows]


def _clock(words):
    m = re.fullmatch(r'(\d\d):(\d\d) ([ap])m', ' '.join(w for _, w in words))
    return f'{int(m.group(1)) % 12 + (12 if m.group(3) == "p" else 0):02d}:{m.group(2)}' if m else None


def parse(pdf):
    """Return (organizations, listing date). Each organization has its name, address lines and session rows."""
    orgs, cur, locality, waiting, generated = [], None, None, [], None
    for number, words in enumerate(_pages(pdf), 1):
        m = re.search(r'Listing generated (\d\d)/(\d\d)/(\d{4})', ' '.join(w for _, _, w in words[:40]))
        if m:
            generated = f'{m.group(3)}-{m.group(1)}-{m.group(2)}'
        right = _lines(words, LEFT_END, 9999)
        headers = [y for y, ws in right if ws[0][1] == 'Bingo' and any(w == 'Doors' for _, w in ws)]
        events = [(y, 'L', ' '.join(w for _, w in ws)) for y, ws in _lines(words, 0, LEFT_END)] + [(y, 'R', ws) for y, ws in right]
        for y, kind, val in sorted(events, key=lambda e: (e[0], e[1])):
            if number == 1 and y < 80:
                continue  # the report's title block
            if kind == 'L':
                if any(-9 <= y - h <= 2.5 for h in headers):
                    # An organization's name sits beside its "Bingo ... Doors Open" header. Lines waiting since
                    # the last finished address start with the next locality heading.
                    if waiting:
                        locality = waiting[0]
                    cur = {'locality': locality, 'name': ' '.join(waiting[1:] + [val]), 'left': [], 'sessions': [], 'closed': False}
                    orgs.append(cur)
                    waiting = []
                elif cur is not None and not cur['closed']:
                    cur['left'].append(val)
                    cur['closed'] = bool(re.search(r' VA \d{5}(-\d{4})?$', val))
                else:
                    waiting.append(val)
            elif cur is not None and val[0][1] != 'Bingo':
                if re.fullmatch(r'\d\d/\d\d/\d{4}', val[0][1]) and val[0][0] < LEFT_END + 15:
                    cur['sessions'].append({'day': ' '.join(w for x, w in val if DAY_START <= x < DAY_END),
                                            'open': _clock([p for p in val if DAY_END <= p[0] < CLOSE_START]),
                                            'close': _clock([p for p in val if p[0] >= CLOSE_START])})
                elif cur['sessions'] and val[0][0] >= DAY_START:
                    cur['sessions'][-1]['day'] += ' ' + ' '.join(w for x, w in val if x < DAY_END)
    assert orgs and generated and all(o['closed'] and o['locality'] for o in orgs), 'the directory layout changed; check the column positions'
    return orgs, generated


def _date(text):
    m, d, y = (int(p) for p in text.split('/'))
    return datetime.date(y + 2000 if y < 100 else y, m, d)


def _nice(d):
    return f'{d.strftime("%B")} {d.day}'


def weekly(text, today):
    """(weekdays, labels, social quarters?) for a weekly row; None for dated events, cancelled or ended rows."""
    t = text.strip()
    social = t.startswith('[Social Quarters]')
    if social:
        t = t[len('[Social Quarters]'):].strip()
    m = re.match(rf'({WEEKDAYS})(?: (&|to) ({WEEKDAYS}))?(?= \[|$)', t)
    if not m:
        return None
    days = [DAYS[m.group(1).lower()]] + ([DAYS[m.group(3).lower()]] if m.group(2) == '&' else [])
    rest = t[m.end():]
    if re.search(r'\[Cancel+ed\]', rest):
        return None
    labels = []
    which = re.search(r'\[((?:First|Second|Third|Fourth|Last)(?: & (?:First|Second|Third|Fourth|Last))?) of Each Month\]', rest)
    if which:
        first, _, second = which.group(1).partition(' & ')
        labels.append(first + (' and ' + second.lower() if second else '') + ' {day} of the month')
    ends = [_date(d) for span in re.findall(r'\[(?:Ends|From) [^\]]*\]', rest) for d in re.findall(r'\d+/\d+/\d+', span)]
    if ends:
        if max(ends) < today:
            return None
        labels.append('through ' + _nice(max(ends)))
    begins = re.search(r'\[Begins (\d+/\d+/\d+)\]', rest)
    if begins and _date(begins.group(1)) > today:
        labels.append('starts ' + _nice(_date(begins.group(1))))
    if social:
        labels.append('in the social quarters')
    return days, labels, social


def _slug(text):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text.lower().replace('&', ' and ').replace("'", ''))).strip('-')


def venues(orgs, generated, reviewed):
    today = datetime.date.fromisoformat(reviewed)
    listing = datetime.date.fromisoformat(generated)
    halls = collections.OrderedDict()
    for o in orgs:
        m = re.match(r'^(.*) VA (\d{5})(?:-\d{4})?$', o['left'][-1])
        city, zipc, body = m.group(1).strip(), m.group(2), o['left'][:-1]
        i = next((k for k, line in enumerate(body) if re.match(r'\d', line)), len(body) - 1)
        street, before = ', '.join(body[i:]), body[:i]
        org = ' '.join([o['name']] + before[:-1])  # a long organization name wraps onto the next line
        place = before[-1] if before else org
        note = None
        if (street, city, zipc) in ZIP_FIXES:
            zipc, note = ZIP_FIXES[(street, city, zipc)]
        rows, social = [], False
        for s in o['sessions']:
            w = weekly(s['day'], today)
            if not w or not (s['open'] and s['close']):
                continue
            social = social or w[2]
            for d in w[0]:
                row = {'day': d, 'start': s['open'], 'end': s['close'], 'organization': org}
                if w[1]:
                    row['label'] = ', '.join(part.format(day=DAY_NAMES[d]) for part in w[1])
                if row not in rows:
                    rows.append(row)
        if not rows:
            continue
        hall = halls.setdefault((re.sub(r'[^a-z0-9]', '', street.lower()), zipc),
                                {'names': [], 'organizations': [], 'street': street, 'city': city, 'zip': zipc, 'sessions': [], 'notes': []})
        hall['names'].append(place)
        if org not in hall['organizations']:
            hall['organizations'].append(org)
        hall['sessions'] += [r for r in rows if r not in hall['sessions']]
        hall['notes'] += [n for n in ([SOCIAL_NOTE] if social else []) + ([note] if note else []) if n not in hall['notes']]
    out, ids = [], set()
    scope = (f'Virginia Office of Charitable and Regulatory Programs, Registered Gaming Activity (listing generated {_nice(listing)}, '
             f'{listing.year}): organization, location, weekday, and doors-open and doors-close times')
    for hall in halls.values():
        name = collections.Counter(hall['names']).most_common(1)[0][0]
        base = vid = 'va-' + _slug(name) + '-' + _slug(hall['city'])
        n = 2
        while vid in ids:
            vid, n = f'{base}-{n}', n + 1
        ids.add(vid)
        # Sessions run Monday first, as the site shows them.
        rec = {'id': vid, 'state': 'VA', 'name': name, 'organizations': hall['organizations'],
               'address': f"{hall['street']}, {hall['city']}, VA {hall['zip']}", 'city': hall['city'], 'zip': hall['zip'], 'county': None,
               'sessions': sorted(hall['sessions'], key=lambda r: ((r['day'] + 6) % 7, r['start'], r['organization'])), 'schedule_note': SCHEDULE_NOTE}
        if hall['notes']:
            rec['notes'] = hall['notes']
        rec.update({'reviewed_on': reviewed, 'sources': [{'url': PDF_URL, 'reviewed_on': reviewed, 'scope': scope}]})
        out.append((rec, hall['street']))
    return out


def _curl(*args):
    return subprocess.run(['curl', '-sS', '-m', '240', *args], capture_output=True, text=True, check=True).stdout


def _json(url, tries=4):
    # The geocoder now and then answers with an error page; ask again before giving up.
    for attempt in range(tries):
        try:
            return json.loads(_curl(url))
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))


def geocode(need):
    """County for each (record, street) in need, from the U.S. Census Geocoder. Returns {id: (county, how)}."""
    names = {}
    for line in _curl('https://www2.census.gov/geo/docs/reference/codes2020/cou/st51_va_cou2020.txt').split('\n')[1:]:
        p = line.split('|')
        if len(p) > 4:
            names[p[2]] = p[4][:-7] if p[4].endswith(' County') else p[4]
    with tempfile.NamedTemporaryFile('w', suffix='.csv', newline='') as f:
        csv.writer(f).writerows([i, street, rec['city'], 'VA', rec['zip']] for i, (rec, street) in enumerate(need))
        f.flush()
        rows = {int(r[0]): r for r in csv.reader(_curl('-F', f'addressFile=@{f.name}', '-F', 'benchmark=Public_AR_Current', '-F', 'vintage=Current_Current',
                                                       'https://geocoding.geo.census.gov/geocoder/geographies/addressbatch').splitlines())}
    found, by_zip = {}, collections.defaultdict(set)
    for i, (rec, _) in enumerate(need):
        r = rows.get(i)
        if r and r[2] == 'Match' and r[8] == '51':
            found[rec['id']] = (names[r[9]], 'address')
            by_zip[rec['zip']].add(names[r[9]])
    centroids = json.loads((ROOT / 'data/public/us-zip-centroids.json').read_text())
    for rec, _ in need:
        if rec['id'] in found:
            continue
        if len(by_zip[rec['zip']]) == 1:
            found[rec['id']] = (next(iter(by_zip[rec['zip']])), 'another hall in the same ZIP code')
        elif rec['zip'] in centroids:
            lat, lon = centroids[rec['zip']]
            q = urllib.parse.urlencode({'x': lon, 'y': lat, 'benchmark': 'Public_AR_Current', 'vintage': 'Current_Current', 'layers': 'Counties', 'format': 'json'})
            g = _json('https://geocoding.geo.census.gov/geocoder/geographies/coordinates?' + q)['result']['geographies']['Counties'][0]
            if g['STATE'] == '51':
                found[rec['id']] = (g['NAME'][:-7] if g['NAME'].endswith(' County') else g['NAME'], 'the centre of the ZIP code')
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('pdf')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    ap.add_argument('--geocode', action='store_true', help='look up the county for new addresses with the U.S. Census Geocoder')
    a = ap.parse_args()
    orgs, generated = parse(a.pdf)
    built = venues(orgs, generated, a.reviewed)
    known = {v['address']: v['county'] for v in json.loads(OUT.read_text())} if OUT.exists() else {}
    for rec, _ in built:
        rec['county'] = known.get(rec['address'])
    need = [(rec, street) for rec, street in built if not rec['county']]
    if need and a.geocode:
        for rec_id, (county, how) in geocode(need).items():
            rec = next(r for r, _ in need if r['id'] == rec_id)
            rec['county'] = county
            if how != 'address':
                print(f'county from {how}: {rec["address"]} -> {county}')
    missing = [rec['address'] for rec, _ in built if not rec['county']]
    if missing:
        sys.exit('No county yet (run with --geocode, or check the address):\n  ' + '\n  '.join(missing))
    records = sorted((rec for rec, _ in built), key=lambda r: (r['county'], r['city'], r['name'], r['id']))
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1) + '\n')
    print(f'{OUT.relative_to(ROOT)}: listing generated {generated}, reviewed {a.reviewed}. Set list_as_of to {generated} in bingo-states.json.')


if __name__ == '__main__':
    main()
