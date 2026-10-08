#!/usr/bin/env python3
"""Refresh static projections from canonical JSON; --check detects drift without writes."""
import argparse
import json
import re
from pathlib import Path
from pa_edition import make_pa, pennsylvania_resources
from ny_edition import make_ny, new_york_resources
from mi_edition import make_mi, michigan_resources

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://travisvought-byte.github.io/vhg-veteran-resident-guide/'

def outputs():
    resources = json.loads((ROOT / 'prototype-data.json').read_text())
    counties = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    html = (ROOT / 'index.html').read_text()
    if '<option value="NY">New York</option>' not in html:
        html = html.replace('<option value="PA">Pennsylvania</option>', '<option value="PA">Pennsylvania</option><option value="NY">New York</option>')
    if '<option value="MI">Michigan</option>' not in html:
        html = html.replace('<option value="NY">New York</option>', '<option value="NY">New York</option><option value="MI">Michigan</option>')
    html = re.sub(r'^function editionURL\(state\).*$', "function editionURL(state){const pages={OH:'index.html',PA:'pa.html',NY:'ny.html',MI:'mi.html'};const u=new URL(pages[state]||pages.OH,location.href);if(route!=='priority')u.searchParams.set('view',route);return u}", html, flags=re.M)
    for name, value in [('DATA', resources), ('COUNTIES', counties)]:
        # Escape HTML parser boundaries inside strings while retaining valid JSON.
        payload = json.dumps(value, ensure_ascii=True).replace('<', '\\u003c')
        html, n = re.subn(r'const ' + name + r'=.*?;\n', lambda _: 'const ' + name + '=' + payload + ';\n', html, count=1)
        if n != 1:
            raise ValueError('Missing embedded ' + name)
    regional = sorted((r for r in resources if r.get('regional_role')), key=lambda r: r['program_id'])
    pa_resources = pennsylvania_resources(ROOT, resources)
    pa_counties = json.loads((ROOT / 'data/public/pennsylvania-county-veterans-offices.json').read_text())
    ny_resources = new_york_resources(ROOT, resources)
    ny_counties = json.loads((ROOT / 'data/public/new-york-county-veterans-offices.json').read_text())
    mi_resources = michigan_resources(ROOT, resources)
    mi_counties = json.loads((ROOT / 'data/public/michigan-county-veterans-offices.json').read_text())
    share = (ROOT / 'share.html').read_text()
    if 'href="share-ny.html"' not in share:
        share = share.replace('<a href="share-pa.html">Pennsylvania</a>', '<a href="share-pa.html">Pennsylvania</a> · <a href="share-ny.html">New York</a>')
    if 'href="share-mi.html"' not in share:
        share = share.replace('<a href="share-ny.html">New York</a>', '<a href="share-ny.html">New York</a> · <a href="share-mi.html">Michigan</a>')
    pa_share = share.replace('Ohio', 'Pennsylvania').replace('88', '67').replace('href="index.html"', 'href="pa.html"')
    pa_share = pa_share.replace('https://travisvought-byte.github.io/vhg-veteran-resident-guide/', 'https://travisvought-byte.github.io/vhg-veteran-resident-guide/pa.html')
    pa_share = pa_share.replace('assets/guide-qr.svg', 'assets/guide-qr-pa.svg')
    pa_share = pa_share.replace('href="share.html">Pennsylvania', 'href="share.html">Ohio')
    pa_share = pa_share.replace('local veterans office, aging agency and long-term-care ombudsman contacts', 'county veterans office contacts, matched local aging referrals and local or statewide ombudsman routes')
    ny_share = share.replace('Ohio', 'New York').replace('88', '62').replace('href="index.html"', 'href="ny.html"')
    ny_share = ny_share.replace(BASE_URL, BASE_URL + 'ny.html').replace('assets/guide-qr.svg', 'assets/guide-qr-ny.svg')
    ny_share = ny_share.replace('href="share.html">New York', 'href="share.html">Ohio')
    ny_share = ny_share.replace('local veterans office, aging agency and long-term-care ombudsman contacts', 'county and city veterans referrals, matched local aging contacts and statewide ombudsman routing')
    mi_share = share.replace('Ohio', 'Michigan').replace('88', '83').replace('href="index.html"', 'href="mi.html"')
    mi_share = mi_share.replace(BASE_URL, BASE_URL + 'mi.html').replace('assets/guide-qr.svg', 'assets/guide-qr-mi.svg')
    mi_share = mi_share.replace('href="share.html">Michigan', 'href="share.html">Ohio')
    mi_share = mi_share.replace('local veterans office, aging agency and long-term-care ombudsman contacts', 'county and statewide veterans referrals, regional aging contacts with Wayne County city boundaries, and statewide ombudsman routing')
    return {
        'index.html': html,
        'data/public/ohio-regional-referrals.json': json.dumps(regional, indent=2, ensure_ascii=False) + '\n',
        'pa.html': make_pa(html, pa_resources, pa_counties),
        'data/public/pennsylvania-resources.json': json.dumps(pa_resources, indent=2, ensure_ascii=False) + '\n',
        'share-pa.html': pa_share,
        'share.html': share,
        'ny.html': make_ny(html, ny_resources, ny_counties),
        'data/public/new-york-resources.json': json.dumps(ny_resources, indent=2, ensure_ascii=False) + '\n',
        'share-ny.html': ny_share,
        'mi.html': make_mi(html, mi_resources, mi_counties),
        'data/public/michigan-resources.json': json.dumps(mi_resources, indent=2, ensure_ascii=False) + '\n',
        'share-mi.html': mi_share,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    drift = []
    for name, text in outputs().items():
        path = ROOT / name
        if not path.is_file() or path.read_text() != text:
            drift.append(name)
            if not args.check:
                path.write_text(text)
    if args.check and drift:
        parser.exit(1, 'Out of sync: ' + ', '.join(drift) + '. Run python3 scripts/build_public.py\n')
    print('Public projections are synchronized.' if args.check else 'Updated: ' + (', '.join(drift) or 'already synchronized'))
