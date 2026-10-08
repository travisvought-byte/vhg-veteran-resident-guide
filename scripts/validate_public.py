#!/usr/bin/env python3
"""Validate referral essentials and local links. Does not verify remote availability."""
import json
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
regional = json.loads((ROOT / 'data/public/pa-regional-referrals.json').read_text())
resources = (json.loads((ROOT / 'prototype-data.json').read_text())
             + json.loads((ROOT / 'data/public/pa-programs.json').read_text()) + regional)
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

for name in ['index.html', 'pa.html', 'share.html', 'share-pa.html']:
    Links().feed((ROOT / name).read_text())
for name, state in [('ohio-county-veterans-offices.json', 'OH'), ('pennsylvania-county-veterans-offices.json', 'PA')]:
    counties = json.loads((ROOT / 'data/public' / name).read_text())
    for county in counties:
        assert urlsplit(county['source_url']).scheme == 'https', county['county']
        assert date.fromisoformat(county['reviewed_on']) <= date.today(), county['county']
        assert county.get('state', state) == state, county['county']
pa_counties = {c['county'] for c in counties}
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
print('PASS: both states’ resource essentials, county source dates, HTTPS sources and local sharing assets.')
