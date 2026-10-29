#!/usr/bin/env python3
"""Build data/public/ohio-facilities.json from two public sources.

  CMS Nursing Home Provider Information (nursing homes certified for Medicare/Medicaid)
  Ohio Department of Health Facility Listing, Residential Care or Assisted Living (state licensed)

Usage: python3 scripts/build_facilities_data.py --cms NH_ProviderInfo_<Mon><Year>.csv --odh FacilityListing-<date>.csv \
           --retrieved YYYY-MM-DD

Only public directory fields are kept (name, address, phone, county, beds, ownership, chain). Email addresses, fax
numbers and owner contacts in the ODH export are deliberately NOT published. Quality ratings, penalties and staffing
are left out: this is a finder, not a rating.
"""
import argparse, csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://data.cms.gov/provider-data/dataset/4pq5-n9py'
ODH_URL = 'https://publicapps.odh.ohio.gov/eid/reports/EID_Report_Criteria.aspx'
# Facilities Veteran Home Guardians serves; keyed by CMS certification number.
VHG_VISITING = {'366194', '366299', '366028', '365835'}

def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip()
    if s.isupper() or s.islower():
        s = s.title()
    # Whole-word replacements only, so "Drive" is never turned into "Driveive".
    for a, b in [('Of', 'of'), ('At', 'at'), ('And', 'and'), ('In', 'in'), ('Mt', 'Mt.'), ('Ctr', 'Center'), ('Hlth', 'Health'),
                 ('Als', 'ALS'), ('Llc', 'LLC'), ('Rd', 'Road'), ('Dr', 'Drive')]:
        s = re.sub(r'(?<=\s)' + a + r'\b(?!\.)', b, s)
    s = re.sub(r'\b(Nw|Ne|Sw|Se)\b', lambda m: m.group(1).upper(), s)
    s = re.sub(r'[\s,;]+$', '', s)
    if re.search(r'[,\s]\s*The$', s):
        s = 'The ' + re.sub(r'[,\s]+The$', '', s)
    return re.sub(r'[\s,;]+$', '', s)

def phone(raw):
    d = re.sub(r'\D', '', raw)
    return f'{d[:3]}-{d[3:6]}-{d[6:]}' if len(d) == 10 else ''

def build_cms(csv_path, retrieved):
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
            'facility_type': 'nursing_home',
            'reviewed_on': retrieved,
        })
    source = {
        'source_url': SOURCE_URL,
        'publisher': 'Centers for Medicare & Medicaid Services, Provider Data Catalog: Nursing Home Provider Information',
        'file': Path(csv_path).name,
        'retrieved_on': retrieved,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'ohio_rows': len(out),
        'scope': 'Medicare/Medicaid-certified nursing homes only.',
    }
    return out, source

def street_key(address, zip5):
    a = address.lower()
    for x, y in [('street', 'st'), ('road', 'rd'), ('avenue', 'ave'), ('drive', 'dr'), ('boulevard', 'blvd'), ('highway', 'hwy')]:
        a = a.replace(x, y)
    return re.sub(r'[^a-z0-9]', '', a.split(',')[0]) + zip5

def build_odh(csv_path, retrieved, nursing_homes):
    raw = Path(csv_path).read_bytes()
    text = raw.decode('utf-8-sig', errors='replace')
    # The ODH export can carry stray HTML after the data; keep only rows that have a facility ID.
    rows = [r for r in csv.DictReader(text.splitlines()) if r.get('FACID') and r.get('OPERSTDESC') == 'ACTIVE']
    campus = {street_key(n['address'], n['zip']): n['id'] for n in nursing_homes}
    out = []
    seen = set()
    for r in rows:
        # The export repeats a facility once per listed owner; keep one record per license.
        if r['FACID'] in seen:
            continue
        seen.add(r['FACID'])
        zip5 = r['FAC_ZIP'].strip()[:5]
        city = tidy(r['FAC_CITY'])
        rec = {
            'id': 'odh-' + r['FACID'],
            'license_id': r['FACID'],
            'ccn': None,
            'name': tidy(r['NAME']),
            'address': f"{tidy(r['ADDRESS'])}, {city}, OH {zip5}",
            'city': city,
            'zip': zip5,
            'county': r['CNTYNAME'].strip().title(),
            'phone': phone(r['TELEPHONE']),
            'beds': int(r['LIC_BED_TOTAL'] or 0),
            'ownership': None,
            'chain': None,
            'ohio_veterans_home': False,
            'vhg_visiting': False,
            'facility_type': 'residential_care',
            'campus_nursing_home': campus.get(street_key(tidy(r['ADDRESS']), zip5)),
            'reviewed_on': retrieved,
        }
        out.append(rec)
    source = {
        'source_url': ODH_URL,
        'publisher': 'Ohio Department of Health, Office of Health Assurance and Licensing: Health Care Provider Report and Information Extract, Facility Listing (Residential Care or Assisted Living, active, state license)',
        'file': Path(csv_path).name,
        'retrieved_on': retrieved,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'rows': len(out),
        'scope': 'Active state-licensed residential care or assisted living facilities. The export does not identify memory care units, and email, fax and owner fields in it are not published here.',
    }
    return out, source

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--cms', required=True); p.add_argument('--odh', required=True); p.add_argument('--retrieved', required=True)
    a = p.parse_args()
    nursing, cms_source = build_cms(a.cms, a.retrieved)
    care, odh_source = build_odh(a.odh, a.retrieved, nursing)
    data = sorted(nursing + care, key=lambda f: (f['facility_type'], f['name'].lower(), f['id']))
    (ROOT / 'data/public/ohio-facilities.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    (ROOT / 'data/source').mkdir(exist_ok=True)
    (ROOT / 'data/source/ohio-facilities-source.json').write_text(json.dumps({'nursing_homes': cms_source, 'residential_care': odh_source}, indent=1, ensure_ascii=False) + '\n')
    print(f"Wrote {len(nursing)} nursing homes and {len(care)} residential care/assisted living facilities; "
          f"{sum(1 for f in care if f['campus_nursing_home'])} share a campus with a nursing home")
