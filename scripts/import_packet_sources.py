#!/usr/bin/env python3
"""Refresh data/packets/ohio-county-sources.json from official publications.

The printable county packets (scripts/build_packets.py) read that file. This script is run by hand
when a source publishes a new edition; the build itself never goes online.

Sources (all public, no sign-in):
  - Ohio Department of Veterans Services, County Veterans Service Offices listing (PDF)
  - Ohio Department of Job and Family Services, County Agency Directory (PDF): county JFS offices,
    which take Adult Protective Services reports
  - Alliance of Ohio Legal Aids, "Find your legal aid" county map, and each member's page for its intake line
  - VA health system "Locations" pages on va.gov (the structured list each page publishes)
    and each location's own page for its map point
  - U.S. Census Bureau 2024 Gazetteer files: county center points (and ZIP code centers as a fallback),
    used only to pick the closest VA locations to each county

Usage: python3 scripts/import_packet_sources.py [--reviewed YYYY-MM-DD]
Needs curl, pdftotext (poppler) and unzip.
"""
import argparse
import datetime
import html
import io
import json
import re
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data/packets/ohio-county-sources.json'

CVSO_URL = 'https://dam.assets.ohio.gov/image/upload/dvs.ohio.gov/cvso-resources/cvso-listing.pdf'
JFS_URL = 'https://dam.assets.ohio.gov/image/upload/jfs.ohio.gov/County/County_Directory.pdf'
LEGAL_MAP_URL = 'https://ohiolegalaids.org/find-your-legal-aid/'
LEGAL_PAGES = {
    'lasco': 'https://ohiolegalaids.org/LASCO/',
    'able-lawo': 'https://ohiolegalaids.org/able-lawo/',
    'lasclev': 'https://ohiolegalaids.org/lasclev/',
    'cla': 'https://www.communitylegalaid.org/',
    'lasso': LEGAL_MAP_URL,
}
# VA health systems whose clinics or medical centers are in Ohio or are the closest VA care for an Ohio county.
VA_SYSTEMS = ['chillicothe-health-care', 'cincinnati-health-care', 'northeast-ohio-health-care',
              'central-ohio-health-care', 'dayton-health-care', 'ann-arbor-health-care', 'huntington-health-care',
              'pittsburgh-health-care', 'clarksburg-health-care', 'northern-indiana-health-care',
              'erie-health-care', 'butler-health-care']
GAZ_COUNTIES = 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip'
GAZ_ZCTA = 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip'


def fetch(url, tries=4):
    for attempt in range(tries):
        done = subprocess.run(['curl', '-sSLf', '--retry', '3', '--retry-all-errors', url], capture_output=True)
        if done.returncode == 0:
            return done.stdout
        time.sleep(5 * (attempt + 1))
    done.check_returncode()


def pdf_text(data, layout=False):
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(data)
        f.flush()
        args = ['pdftotext'] + (['-layout'] if layout else []) + [f.name, '-']
        return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def page_text(raw):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', raw.decode('utf8', 'ignore'), flags=re.S)
    return [l.strip() for l in html.unescape(re.sub(r'<[^>]+>', '\n', t)).splitlines() if l.strip()]


def phone(s):
    """(419) 223-8522 -> 419-223-8522, keeping any extension text."""
    s = re.sub(r'\((\d{3})\)\s*(\d{3})-(\d{4})', r'\1-\2-\3', s).strip()
    return re.sub(r'(?<![\d-])1-(\d{3}-\d{3}-\d{4})', r'\1', s)


def ohio_counties():
    rows = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    return [r['county'] for r in rows]


def parse_cvso(text, counties):
    heads = {c + ' County': c for c in counties}
    blocks, current = {}, None
    for line in (l.strip() for l in text.splitlines()):
        if line in heads and heads[line] not in blocks:
            current = heads[line]
            blocks[current] = []
        elif current and line:
            blocks[current].append(line)
    out = {}
    for county in counties:
        lines = blocks.get(county)
        assert lines, 'CVSO listing: no block for ' + county
        address, phones, fax = [], [], None
        for line in lines:
            if line.startswith('Fax:'):
                fax = phone(line[4:])
                break  # every block ends with its fax line
            if re.match(r'^\(\d{3}\)', line) or (phones and phones[-1].endswith(' or')):
                phones.append(phone(line))
            else:
                address.append(line)
        # The listing wraps some street numbers onto the line before ("Coliseum 220" / "E. Fairground St.").
        for i in range(len(address) - 1):
            m = re.match(r'^(.*\D) (\d+)$', address[i])
            if m and re.match(r'^[NSEW]\. ', address[i + 1]):
                address[i], address[i + 1] = m.group(1), m.group(2) + ' ' + address[i + 1]
        joined = ' '.join(phones)
        assert re.search(r'\d{3}-\d{3}-\d{4}', joined), 'CVSO listing: no phone for ' + county
        assert any(re.search(r'OH \d{5}', a) for a in address), 'CVSO listing: no city line for ' + county
        out[county] = {'address': address, 'phone': re.sub(r'\s+', ' ', joined), 'fax': fax}
    return out


def parse_jfs(text, counties):
    out = {}
    for page in text.split('\f'):
        m = re.search(r'^\s*([A-Z][A-Za-z\. ]+?) County - \d\d\s*$', page, flags=re.M)
        if not m:
            continue
        county = m.group(1).strip()
        block = re.search(r'CDJFS[^\n]*\n(.*?)(?:\n\s*\n|CSEA|PCSA|OMJ)', page, flags=re.S)
        lines = [l.strip() for l in block.group(1).split('\n') if l.strip()]
        phone_line = next(l for l in lines if l.startswith('Phone/Ext:'))
        first = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', phone_line).group(0)
        address = lines[1] if len(lines) > 1 and not lines[1].startswith('Phone') else ''
        website = next((l.split(':', 1)[1].strip() for l in lines if l.startswith('Website:')), None)
        out[county] = {'address': address, 'phone': phone(first), 'website': website}
    missing = [c for c in counties if c not in out]
    assert not missing, 'JFS directory missing ' + ', '.join(missing)
    return out


def parse_legal_map(raw, counties):
    pairs = re.findall(r'"title":"([A-Za-z \.]+)","type":"poly".{0,600}?"link":"([^"]+)"', raw.decode('utf8'))
    ids = {'lasco': 'lasco', 'able-lawo': 'able-lawo', 'lasclev': 'lasclev', 'lasso': 'lasso', 'cla': 'cla'}
    out = {}
    for county, link in pairs:
        slug = link.replace('\\/', '/').rstrip('/').rsplit('/', 1)[-1].lower()
        out[county] = ids[slug]
    missing = [c for c in counties if c not in out]
    assert not missing, 'Legal aid map missing ' + ', '.join(missing)
    return {c: out[c] for c in counties}


def legal_programs(reviewed):
    lasco = page_text(fetch(LEGAL_PAGES['lasco']))
    able = page_text(fetch(LEGAL_PAGES['able-lawo']))
    clev = page_text(fetch(LEGAL_PAGES['lasclev']))
    cla = fetch(LEGAL_PAGES['cla']).decode('utf8', 'ignore')
    find = page_text(fetch(LEGAL_MAP_URL))

    def after(lines, label):
        i = next(i for i, l in enumerate(lines) if l.startswith(label))
        return next(l for l in lines[i:] if re.search(r'\d{3}-\d{3}-\d{4}', l))

    help_line = re.search(r'Call our HelpLine at\s*(?:<[^>]+>\s*)*\(?(\d{3})\)?[ -](\d{3}-\d{4})', cla)
    assert help_line, 'Community Legal Aid HelpLine not found'
    cincy = after(find, 'Legal Aid Line:')
    lucas = after(able, '• Lucas County')
    rest = after(able, '• All other counties')
    return {
        'lasco': {'name': 'Legal Aid of Southeast and Central Ohio (LASCO)', 'phone': phone(after(lasco, 'Apply by phone')),
                  'url': LEGAL_PAGES['lasco']},
        'able-lawo': {'name': 'Legal Aid of Western Ohio (LAWO) and ABLE', 'phone': phone(rest),
                      'phone_lucas': phone(lucas), 'url': LEGAL_PAGES['able-lawo']},
        'lasclev': {'name': 'The Legal Aid Society of Cleveland', 'phone': phone(after(clev, 'Apply by phone')),
                    'url': LEGAL_PAGES['lasclev']},
        'cla': {'name': 'Community Legal Aid', 'phone': help_line.group(1) + '-' + help_line.group(2),
                'url': LEGAL_PAGES['cla']},
        'lasso': {'name': 'Legal Aid Society of Greater Cincinnati and Legal Aid Society of Southwest Ohio',
                  'phone': ' or '.join(phone(p) for p in re.findall(r'\d{3}-\d{3}-\d{4}', cincy)),
                  'url': LEGAL_MAP_URL},
    }


def gazetteer(url, key):
    with zipfile.ZipFile(io.BytesIO(fetch(url))) as z:
        text = z.read(z.namelist()[0]).decode('latin-1')
    rows = [l.split('\t') for l in text.splitlines()]
    head = [h.strip() for h in rows[0]]
    return [dict(zip(head, (c.strip() for c in r))) for r in rows[1:]]


def va_facilities():
    zips = {r['GEOID']: (float(r['INTPTLAT']), float(r['INTPTLONG'])) for r in gazetteer(GAZ_ZCTA, 'GEOID')}
    out = []
    for system in VA_SYSTEMS:
        url = f'https://www.va.gov/{system}/locations/'
        raw = fetch(url).decode('utf8')
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, flags=re.S):
            data = json.loads(block)
            if data.get('@type') != 'ItemList':
                continue
            for item in data['itemListElement']:
                p, a = item['item'], item['item']['address']
                if 'Mobile Medical Unit' in p['name']:
                    continue  # moves between sites; not a place to send someone
                # Each location's own page publishes its map point; the ZIP code center is a fallback.
                geo = re.search(r'"geo":\{"@type":"GeoCoordinates","latitude":([-\d.]+),"longitude":([-\d.]+)\}',
                                fetch(p['url']).decode('utf8', 'ignore'))
                z = a['postalCode'][:5]
                if geo:
                    point = (float(geo.group(1)), float(geo.group(2)))
                elif z in zips:
                    point = zips[z]
                else:
                    continue
                kind = 'medical_center' if 'Medical Center' in p['name'] and 'Fort Thomas' not in p['name'] else 'clinic'
                out.append({'name': p['name'], 'kind': kind, 'street': a['streetAddress'], 'city': a['addressLocality'],
                            'state': a['addressRegion'], 'zip': a['postalCode'], 'phone': p.get('telephone'),
                            'url': p['url'], 'system_url': url, 'lat': point[0], 'lon': point[1]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    args = ap.parse_args()
    counties = ohio_counties()
    centers = {r['NAME'].replace(' County', ''): [float(r['INTPTLAT']), float(r['INTPTLONG'])]
               for r in gazetteer(GAZ_COUNTIES, 'GEOID') if r['USPS'] == 'OH'}
    cvso = parse_cvso(pdf_text(fetch(CVSO_URL)), counties)
    jfs = parse_jfs(pdf_text(fetch(JFS_URL), layout=True), counties)
    legal_map = parse_legal_map(fetch(LEGAL_MAP_URL), counties)
    data = {
        'note': 'Generated by scripts/import_packet_sources.py from the official sources below. Do not edit by hand; '
                'fix the source or the importer. Read by scripts/build_packets.py.',
        'reviewed_on': args.reviewed,
        'sources': {
            'cvso': {'title': 'County Veterans Service Offices listing', 'publisher': 'Ohio Department of Veterans Services',
                     'url': CVSO_URL, 'edition': 'Revised August 2026'},
            'jfs': {'title': 'County Agency Directory', 'publisher': 'Ohio Department of Job and Family Services',
                    'url': JFS_URL, 'edition': 'Updated February 6, 2023'},
            'legal': {'title': 'Find your legal aid (county map) and member pages', 'publisher': 'Alliance of Ohio Legal Aids',
                      'url': LEGAL_MAP_URL},
            'va': {'title': 'VA health system location pages', 'publisher': 'U.S. Department of Veterans Affairs',
                   'url': 'https://www.va.gov/find-locations/'},
            'census': {'title': '2024 Gazetteer files (county and ZIP code center points)', 'publisher': 'U.S. Census Bureau',
                       'url': 'https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html'},
        },
        'legal_aid': legal_programs(args.reviewed),
        'counties': {c: {'center': centers[c], 'cvso': cvso[c], 'jfs': jfs[c], 'legal_aid': legal_map[c]} for c in counties},
        'va_facilities': va_facilities(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    print(f'Wrote {OUT.relative_to(ROOT)}: {len(data["counties"])} counties, {len(data["va_facilities"])} VA locations')


if __name__ == '__main__':
    main()
