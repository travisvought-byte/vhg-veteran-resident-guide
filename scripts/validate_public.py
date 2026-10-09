#!/usr/bin/env python3
"""Validate referral essentials and local links. Does not verify remote availability."""
import json
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
regional = json.loads((ROOT / 'data/public/pa-regional-referrals.json').read_text())
ny_regional = json.loads((ROOT / 'data/public/ny-regional-referrals.json').read_text())
mi_regional = json.loads((ROOT / 'data/public/mi-regional-referrals.json').read_text())
ky_regional = json.loads((ROOT / 'data/public/ky-regional-referrals.json').read_text())
resources = (json.loads((ROOT / 'prototype-data.json').read_text())
             + json.loads((ROOT / 'data/public/pa-programs.json').read_text()) + regional
             + json.loads((ROOT / 'data/public/ny-programs.json').read_text()) + ny_regional
             + json.loads((ROOT / 'data/public/mi-programs.json').read_text()) + mi_regional
             + json.loads((ROOT / 'data/public/ky-programs.json').read_text()) + ky_regional)
for r in resources:
    for field in ['program_id', 'name', 'official_url', 'next_step']:
        assert r.get(field), (r.get('program_id'), field)
    assert urlsplit(r['official_url']).scheme == 'https', r['program_id']
    assert date.fromisoformat(r['verification']['last_reviewed_on']) <= date.today(), r['program_id']

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('src', 'href') or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            assert (ROOT / url.path).is_file(), ('Missing local file', value)

for name in ['index.html', 'bingo.html', 'pa.html', 'ny.html', 'share.html', 'share-pa.html', 'share-ny.html', 'mi.html', 'share-mi.html', 'ky.html', 'share-ky.html']:
    Links().feed((ROOT / name).read_text())
county_sets = {}
for name, state in [('ohio-county-veterans-offices.json', 'OH'), ('pennsylvania-county-veterans-offices.json', 'PA'), ('new-york-county-veterans-offices.json', 'NY'), ('michigan-county-veterans-offices.json', 'MI'), ('kentucky-county-veterans-offices.json', 'KY')]:
    counties = json.loads((ROOT / 'data/public' / name).read_text())
    for county in counties:
        assert urlsplit(county['source_url']).scheme == 'https', county['county']
        assert date.fromisoformat(county['reviewed_on']) <= date.today(), county['county']
        assert county.get('state', state) == state, county['county']
    county_sets[state] = {c['county'] for c in counties}
    assert len(county_sets[state]) == len(counties) == {'OH':88, 'PA':67, 'NY':62, 'MI':83, 'KY':120}[state], state
pa_counties = county_sets['PA']
for county in pa_counties:
    assert sum(r['regional_role'] == 'aging_agency' and county in r['service_area']
               for r in regional) == 1, ('PA aging coverage', county)
    assert sum(r['regional_role'] == 'ombudsman' and county in r['service_area']
               for r in regional) <= 1, ('Ambiguous PA ombudsman', county)
for r in regional:
    assert r['state'] == 'PA' and set(r['service_area']) <= pa_counties, r['program_id']
    assert r['public_contact']['phone'], r['program_id']
    assert r['evidence']['phone_source_url'] == r['official_url'], r['program_id']
    assert r['evidence']['direct_agency_confirmation'] is False, r['program_id']
for county in county_sets['NY']:
    assert sum(county in r['service_area'] for r in ny_regional if r['regional_role'] == 'aging_agency') == 1, ('NY aging coverage', county)
for r in ny_regional:
    assert r['state'] == 'NY' and set(r['service_area']) <= county_sets['NY'], r['program_id']
    assert r['public_contact']['phone'] and r['evidence']['page_sha256'], r['program_id']
    assert r['evidence']['phone_source_url'] == r['official_url'], r['program_id']
    assert r['evidence']['direct_agency_confirmation'] is False, r['program_id']
for county in county_sets['MI']:
    matches = [r for r in mi_regional if county in r['service_area']]
    assert len(matches) == (2 if county == 'Wayne' else 1), ('MI aging coverage', county)
    if county == 'Wayne':
        assert all(r.get('service_scope') for r in matches), 'Wayne city boundaries required'
for r in mi_regional:
    assert r['state'] == 'MI' and set(r['service_area']) <= county_sets['MI'], r['program_id']
    assert r['public_contact']['phone'] and r['evidence']['page_sha256'], r['program_id']
    assert r['evidence']['phone_source_url'] == r['official_url'], r['program_id']
    assert r['evidence']['coverage_source_sha256'], r['program_id']
    assert r['evidence']['direct_agency_confirmation'] is False, r['program_id']
for r in json.loads((ROOT / 'data/public/michigan-county-veterans-offices.json').read_text()):
    assert r['source_sha256'] and r['phone'] and r['organization'], r['county']
    assert r['evidence']['direct_agency_confirmation'] is False, r['county']
    if r['office_type'] == 'state':
        assert r['county'] == 'Ionia' and 'not a direct county office number' in r['note']
for county in county_sets['KY']:
    for role in ['aging_agency', 'ombudsman', 'supported_living']:
        assert sum(r['regional_role'] == role and county in r['service_area'] for r in ky_regional) == 1, ('KY coverage', role, county)
for r in ky_regional:
    assert r['state'] == 'KY' and set(r['service_area']) <= county_sets['KY'], r['program_id']
    assert r['public_contact']['phone'] and r['evidence']['retrieved_text_sha256'], r['program_id']
    assert r['evidence']['review_method'] == 'full_official_page_text', r['program_id']
    assert r['evidence']['phone_source_url'] == r['official_url'], r['program_id']
    assert r['evidence']['coverage_retrieved_text_sha256'] and r['evidence']['direct_agency_confirmation'] is False, r['program_id']
for r in json.loads((ROOT / 'data/public/kentucky-county-veterans-offices.json').read_text()):
    assert r['retrieved_text_sha256'] and r['office_type'] == 'regional' and r['representatives'], r['county']
    assert r['evidence']['direct_agency_confirmation'] is False, r['county']
    for rep in r['representatives']:
        assert rep['name'] and rep['phone'] and 1 <= rep['region'] <= 20, r['county']
        if rep.get('service_scope'):
            assert r['county'] == 'Christian' and rep['service_scope'] == 'Fort Campbell'
print('PASS: all five states’ referral essentials, county coverage, source dates, HTTPS sources and local sharing assets.')
