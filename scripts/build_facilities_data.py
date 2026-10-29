#!/usr/bin/env python3
"""Build data/public/ohio-facilities.json from the CMS Nursing Home Provider Information CSV.

Usage: python3 scripts/build_facilities_data.py NH_ProviderInfo_<Mon><Year>.csv --retrieved YYYY-MM-DD
Only Ohio rows are kept, and only public directory fields (name, address, phone, beds, ownership, chain).
Quality ratings, penalties and staffing are deliberately left out: this is a finder, not a rating.
"""
import argparse, csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://data.cms.gov/provider-data/dataset/4pq5-n9py'
# Facilities Veteran Home Guardians serves; keyed by CMS certification number.
VHG_VISITING = {'366194', '366299', '366028', '365835'}

def tidy(s):
    s = s.strip()
    if s.isupper() or s.islower():
        s = s.title()
    for a, b in [(' Of ', ' of '), (' At ', ' at '), (' And ', ' and '), (' In ', ' in '), ('Mt ', 'Mt. '), (' Ctr', ' Center'),
                 (' Hlth ', ' Health '), ('Hlth ', 'Health '), ('Als ', 'ALS '), (' Llc', ' LLC'), (' Rd', ' Road'), (' Dr', ' Drive')]:
        s = s.replace(a, b)
    s = re.sub(r'\b(Nw|Ne|Sw|Se)\b', lambda m: m.group(1).upper(), s)
    if s.endswith(' The'):
        s = 'The ' + s[:-4]
    return s

def phone(raw):
    d = re.sub(r'\D', '', raw)
    return f'{d[:3]}-{d[3:6]}-{d[6:]}' if len(d) == 10 else ''

def build(csv_path, retrieved):
    raw = Path(csv_path).read_bytes()
    rows = [r for r in csv.DictReader(raw.decode('utf-8-sig').splitlines()) if r['State'] == 'OH']
    out = []
    for r in rows:
        ccn = r['CMS Certification Number (CCN)']
        name = tidy(r['Provider Name'])
        zip5 = r['ZIP Code'].strip()[:5]
        out.append({
            'id': 'cms-' + ccn,
            'ccn': ccn,
            'name': name,
            'address': f"{tidy(r['Provider Address'])}, {tidy(r['City/Town'])}, OH {zip5}",
            'city': tidy(r['City/Town']),
            'zip': zip5,
            'county': r['County/Parish'].strip(),
            'phone': phone(r['Telephone Number']),
            'beds': int(r['Number of Certified Beds'] or 0),
            'ownership': r['Ownership Type'].split(' - ')[0],
            'chain': tidy(r['Chain Name']) if r['Chain Name'].strip() else None,
            'ohio_veterans_home': 'veterans home' in name.lower(),
            'vhg_visiting': ccn in VHG_VISITING,
            'facility_type': 'Nursing home (Medicare/Medicaid certified)',
            'reviewed_on': retrieved,
        })
    out.sort(key=lambda f: (f['name'].lower(), f['ccn']))
    source = {
        'source_url': SOURCE_URL,
        'publisher': 'Centers for Medicare & Medicaid Services, Provider Data Catalog: Nursing Home Provider Information',
        'file': Path(csv_path).name,
        'retrieved_on': retrieved,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'ohio_rows': len(out),
        'scope': 'Medicare/Medicaid-certified nursing homes only. Assisted living, residential care, memory care and adult day services are not in this source.',
    }
    return out, source

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('csv'); p.add_argument('--retrieved', required=True)
    a = p.parse_args()
    data, source = build(a.csv, a.retrieved)
    (ROOT / 'data/public/ohio-facilities.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    (ROOT / 'data/source').mkdir(exist_ok=True)
    (ROOT / 'data/source/ohio-facilities-source.json').write_text(json.dumps(source, indent=1, ensure_ascii=False) + '\n')
    print(f"Wrote {len(data)} Ohio facilities; source sha256 {source['sha256'][:12]}")
