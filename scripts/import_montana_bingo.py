#!/usr/bin/env python3
"""Rebuild data/public/montana-bingo-permits.json from Montana's list of places offering live keno or bingo.

The Department of Justice, Gambling Control Division, publishes "Establishments Offering Live Keno and/or
Bingo", ordered by county and city: https://dojmt.gov/wp-content/ftp/gambling/mtR35.pdf. Download it, then:

    python3 scripts/import_montana_bingo.py mtR35.pdf --reviewed 2026-11-17

Kept: places whose permit covers bingo (rows marked "Bingo" or "Keno/Bingo"). Left out: keno-only places,
and places whose listed address is a post office box or in another town or state, because the address on
the list is then a mailing address, not the door to walk in. A live bingo or keno permit is annual and
expires June 30 (Montana Code 23-5-407; the division's FAQ), so a permit on the fiscal year 2027 list runs
through June 30, 2027. The list gives no game days and no phone.

Needs poppler's pdftotext. Then run python3 scripts/build_public.py and node tests/findbingo.cjs, and set
Montana's list_as_of in bingo-states.json to the date printed at the top of the list.
"""
import argparse, datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/montana-bingo-permits.json'
PDF_URL = 'https://dojmt.gov/wp-content/ftp/gambling/mtR35.pdf'
SMALL = {'and', 'of', 'the', 'at', 'on', 'in', 'a', 'for'}
KEEP_UPPER = {'VFW', 'LLC', 'II', 'III', 'IV', 'BPOE', 'AMVETS', 'MT', 'US', 'NE', 'NW', 'SE', 'SW', 'BBQ', 'KOA'}


def words(text):
    """Write a name or street from the list's capitals in ordinary title case."""
    def one(m):
        w = m.group(0)
        if w.upper() in KEEP_UPPER:
            return w.upper()
        if w.lower() in SMALL and m.start() > 0:
            return w.lower()
        if w.upper().startswith('MC') and len(w) > 3:
            return 'Mc' + w[2].upper() + w[3:].lower()
        return w[0].upper() + w[1:].lower()
    out = re.sub(r"[A-Za-z][A-Za-z']*", one, re.sub(r'\s+', ' ', text.strip()))
    return re.sub(r'(\d)(St|Nd|Rd|Th)\b', lambda m: m.group(1) + m.group(2).lower(), out)


def parse(pdf):
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    as_of = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    year = re.search(r'For Fiscal Year:\s*(\d{4})', text)
    assert as_of and year, 'the list layout changed'
    rows, county, city, cur = [], None, None, None
    for line in text.split('\n'):
        s = re.sub(r'\s*Page\s+\d+\s+of\s+\d+\s*', ' ', line).strip()  # page footers share a line with the text
        if not s or re.search(r'Department of Justice|Establishments Offering|Order by County|For Fiscal Year|^\d+/\d+/\d{4}$|^Page \d', s):
            continue
        m = re.match(r'County:\s*(.*)', s)
        if m:
            county = m.group(1).strip() or None
            continue
        m = re.match(r'City:\s*(.*)', s)
        if m:
            city = m.group(1).strip() or None
            continue
        m = re.match(r'(\d{7}-\d{3}-[A-Z]+)\s+(.*)', s)
        if m:
            cur = {'license': m.group(1), 'name': [m.group(2)], 'county': county, 'city': city, 'address': None, 'type': None}
            rows.append(cur)
        elif cur is not None and cur['type'] is None:
            if re.search(r' [A-Z]{2} \d{5}(-\d{4})?$', s):
                cur['address'] = s
            elif cur['address'] is None:
                cur['name'].append(s)
            else:
                cur['type'] = s
    listed = datetime.date(int(as_of.group(3)), int(as_of.group(1)), int(as_of.group(2)))
    return rows, listed, int(year.group(1))


def records(rows, year, reviewed, listed):
    out, left_out = [], []
    for r in rows:
        if r['type'] not in ('Bingo', 'Keno/Bingo'):
            continue
        m = re.match(r'^(.*) MT (\d{5})(?:-\d{4})?$', r['address'] or '')
        if not (m and r['city'] and r['county'] and m.group(1).endswith(' ' + r['city']) and not m.group(1).startswith('PO BOX')):
            left_out.append(' '.join(r['name']) + ' | ' + str(r['address']))
            continue
        street = m.group(1)[:-len(r['city'])].strip()
        city, zipc = words(r['city']), m.group(2)
        rec = {'id': 'mt-' + r['license'].lower(), 'state': 'MT', 'name': words(' '.join(r['name'])),
               'address': f'{words(street)}, {city}, MT {zipc}', 'city': city, 'zip': zipc, 'county': words(r['county']),
               'license_number': r['license'],
               'license_type': 'live keno and bingo permit' if r['type'] == 'Keno/Bingo' else 'live bingo permit',
               'license_expires': f'{year}-06-30', 'reviewed_on': reviewed,
               'sources': [{'url': PDF_URL, 'reviewed_on': reviewed,
                            'scope': f'Montana Gambling Control Division, Establishments Offering Live Keno and/or Bingo, fiscal year {year} '
                                     f'(dated {listed.strftime("%B")} {listed.day}, {listed.year}): place, address, county and city, and whether the permit covers bingo'}]}
        out.append(rec)
    return sorted(out, key=lambda r: (r['county'], r['city'], r['name'], r['id'])), left_out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('pdf')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    rows, listed, year = parse(a.pdf)
    recs, left_out = records(rows, year, a.reviewed, listed)
    OUT.write_text(json.dumps(recs, ensure_ascii=False, indent=1) + '\n')
    print(f'{OUT.relative_to(ROOT)} written. List dated {listed}, fiscal year {year}. Set list_as_of to {listed}.')
    if left_out:
        print('Left out (mailing address, not the place):\n  ' + '\n  '.join(left_out))


if __name__ == '__main__':
    sys.exit(main())
