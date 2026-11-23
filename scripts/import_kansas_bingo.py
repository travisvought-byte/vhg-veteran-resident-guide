"""Kansas organizations licensed for bingo, from the Department of Revenue's list (data/public/kansas-bingo-licenses.json).

The Kansas Department of Revenue publishes "Bingo Organizations" (https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf):
one block per licensed organization, five lines each: the license number (BNG...), the organization, the street, "City, KS ZIP"
and the phone. The list has no date, no county, no game days and no end date for the licenses.

Usage: pdftotext BingoOrganizations.pdf kansas.txt
       python3 scripts/import_kansas_bingo.py kansas.txt --reviewed 2026-11-23

- A post office box is not a place to go: a block whose street is only a box is left out, and a box written beside a street
  ("7500 W 75th St PO Box 370") is dropped from the address used for directions (`listed_address` keeps the state's wording).
- A block with two different addresses (BNG000422 lists the same street with two ZIP codes) is left out.
- A street that starts with two numbers ("3381 326 N Kansas Ave": a council number run into the street) is left out rather
  than guessed, as is a block whose ZIP code is not a Kansas ZIP code with a point on the map (one block gives a Missouri ZIP).
- The county comes from the ZIP code, in the same Midwire/GeoNames file as the site's ZIP points (checksum checked).
"""
import argparse, csv, hashlib, io, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST_URL = 'https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf'
ZIP_FILE = 'https://raw.githubusercontent.com/midwire/free_zipcode_data/e00aec159e76335c3d62df70d07e7e207be8f4fc/all_us_zipcodes.csv'
SCOPE = ('Kansas Department of Revenue, Bingo Organizations (undated list linked from the bingo page): license number, '
         'organization, address and phone')
LICENSE = re.compile(r'BNG\d+')
CITY_LINE = re.compile(r'(.+?),\s*KS\s+(\d{5})(?:-\d{4})?$')
PHONE = re.compile(r'\d{3}-\d{3}-\d{4}')
BOX = re.compile(r',?\s*(?:P\.?\s*O\.?\s*Box|PO Box)\s+\d+\s*,?', re.I)


def blocks(text):
    """Each block starts at a license number line; the lines after it, up to the next license number, belong to it."""
    out, cur = [], None
    for line in text.splitlines():
        line = ' '.join(line.split())
        if not line or line == 'BINGO ORGANIZATIONS':
            continue
        if LICENSE.fullmatch(line):
            cur = [line]
            out.append(cur)
        elif cur is not None:
            cur.append(line)
    return out


def zip_counties(path=None):
    raw = Path(path).read_bytes() if path else subprocess.run(['curl', '-sSL', ZIP_FILE], capture_output=True, check=True).stdout
    meta = json.loads((ROOT / 'data/public/us-zip-centroids-source.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == meta['source_sha256'], 'ZIP file checksum'
    return {r['code']: r['county'].title() for r in csv.DictReader(io.StringIO(raw.decode())) if r['state'] == 'KS' and r['county']}


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('text', type=Path, help='pdftotext output of the state list')
    p.add_argument('--reviewed', required=True)
    p.add_argument('--zip-file', help='a local copy of the Midwire ZIP file')
    args = p.parse_args()
    counties = zip_counties(args.zip_file)
    points = json.loads((ROOT / 'data/public/us-zip-centroids.json').read_text())
    rows, left_out = [], []
    for b in blocks(args.text.read_text()):
        number = b[0]
        phone = b[-1] if PHONE.fullmatch(b[-1]) else None
        body = b[1:-1] if phone else b[1:]
        m = CITY_LINE.match(body[-1]) if len(body) >= 3 else None
        if not m:
            left_out.append((number, 'no "City, KS ZIP" line'))
            continue
        name, lines = body[0], body[1:-1]
        city, zip5 = m.group(1).strip(), m.group(2)
        listed = ', '.join(lines)
        streets = [s for s in (BOX.sub('', x).strip(' ,') for x in lines) if s]
        if not streets:
            left_out.append((number, 'post office box only'))
            continue
        if len(streets) > 1:
            left_out.append((number, f'more than one address: {listed}'))
            continue
        street = streets[0]
        if not re.match(r'\d', street) or re.match(r'\d+ \d+ ', street):
            left_out.append((number, f'street unclear: {listed}'))
            continue
        if zip5 not in points or zip5 not in counties:
            left_out.append((number, f'ZIP code {zip5} is not a Kansas ZIP code with a map point'))
            continue
        r = {'id': 'ks-' + slug(number), 'state': 'KS', 'name': name, 'address': f'{street}, {city}, KS {zip5}'}
        if street != listed:
            r['listed_address'] = f'{listed}, {city}, KS {zip5}'
        r.update(city=city, zip=zip5, county=counties[zip5])
        if phone:
            r['phone'] = phone
        r.update(license_number=number, license_type='bingo license', reviewed_on=args.reviewed,
                 sources=[{'url': LIST_URL, 'reviewed_on': args.reviewed, 'scope': SCOPE}])
        rows.append(r)
    rows.sort(key=lambda r: (r['county'], r['city'], r['name'], r['id']))
    (ROOT / 'data/public/kansas-bingo-licenses.json').write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n')
    print(f'Kansas: {len(rows)} licensed organizations written; left out:')
    for number, why in left_out:
        print(' ', number, why)


if __name__ == '__main__':
    main()
