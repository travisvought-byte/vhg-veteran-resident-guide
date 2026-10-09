#!/usr/bin/env python3
"""Refresh static projections from canonical JSON; --check detects drift without writes."""
import argparse
import json
import re
from pathlib import Path
from pa_edition import make_pa, pennsylvania_resources
from ny_edition import make_ny, new_york_resources
from mi_edition import make_mi, michigan_resources
from ky_edition import make_ky, kentucky_resources
from bingo_edition import make_bingo
from unified_guide import unified_outputs

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://travisvought-byte.github.io/vhg-veteran-resident-guide/'

def outputs():
    resources = json.loads((ROOT / 'prototype-data.json').read_text())
    counties = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    html = (ROOT / 'templates/guide.html').read_text()
    html = re.sub(r'<p id="ohio-bingo-link">.*?</p>', '', html)
    html = re.sub(r'<section id="urgent-help".*?</section>', '', html, flags=re.S)
    html = re.sub(r'^routes.aid=.*\n', '', html, flags=re.M)
    html = re.sub(r'<p id="ohio-aid-link">.*?</p>', '', html)
    html = re.sub(r'^routes.crisis=.*\n', '', html, flags=re.M)
    if '<option value="NY">New York</option>' not in html:
        html = html.replace('<option value="PA">Pennsylvania</option>', '<option value="PA">Pennsylvania</option><option value="NY">New York</option>')
    if '<option value="MI">Michigan</option>' not in html:
        html = html.replace('<option value="NY">New York</option>', '<option value="NY">New York</option><option value="MI">Michigan</option>')
    if '<option value="KY">Kentucky</option>' not in html:
        html = html.replace('<option value="MI">Michigan</option>', '<option value="MI">Michigan</option><option value="KY">Kentucky</option>')
    html = re.sub(r'^function editionURL\(state\).*$', "function editionURL(state){const pages={OH:'index.html',PA:'pa.html',NY:'ny.html',MI:'mi.html',KY:'ky.html'};const u=new URL(pages[state]||pages.OH,location.href);if(route!=='priority')u.searchParams.set('view',route);return u}", html, flags=re.M)
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
    ky_resources = kentucky_resources(ROOT, resources)
    ky_counties = json.loads((ROOT / 'data/public/kentucky-county-veterans-offices.json').read_text())
    share = (ROOT / 'share.html').read_text()
    if 'href="share-ny.html"' not in share:
        share = share.replace('<a href="share-pa.html">Pennsylvania</a>', '<a href="share-pa.html">Pennsylvania</a> · <a href="share-ny.html">New York</a>')
    if 'href="share-mi.html"' not in share:
        share = share.replace('<a href="share-ny.html">New York</a>', '<a href="share-ny.html">New York</a> · <a href="share-mi.html">Michigan</a>')
    if 'href="share-ky.html"' not in share:
        share = share.replace('<a href="share-mi.html">Michigan</a>', '<a href="share-mi.html">Michigan</a> · <a href="share-ky.html">Kentucky</a>')
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
    ky_share = share.replace('Ohio', 'Kentucky').replace('88', '120').replace('href="index.html"', 'href="ky.html"')
    ky_share = ky_share.replace(BASE_URL, BASE_URL + 'ky.html').replace('assets/guide-qr.svg', 'assets/guide-qr-ky.svg')
    ky_share = ky_share.replace('href="share.html">Kentucky', 'href="share.html">Ohio')
    ky_share = ky_share.replace('local veterans office, aging agency and long-term-care ombudsman contacts', 'KDVA regional veterans representatives, matched aging contacts, district ombudsmen and Hart-Supported Living coordinators')
    ky_share = ky_share.replace('county veterans offices', 'KDVA regional veterans representatives')
    result = {
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
        'ky.html': make_ky(html, ky_resources, ky_counties),
        'data/public/kentucky-resources.json': json.dumps(ky_resources, indent=2, ensure_ascii=False) + '\n',
        'share-ky.html': ky_share,
    }


    editions = [
        ('index.html', 'Ohio', resources, counties, 'Statewide referral backbone; local program research is strongest in Morrow, Knox, Marion and Delaware.'),
        ('pa.html', 'Pennsylvania', pa_resources, pa_counties, 'Initial referral edition. County veterans and aging routes are mapped; four counties have dedicated local ombudsman contacts, with statewide routing elsewhere.'),
        ('ny.html', 'New York', ny_resources, ny_counties, 'Initial referral edition. County, city and state veterans routes and local aging contacts are mapped; ombudsman routing is statewide.'),
        ('mi.html', 'Michigan', mi_resources, mi_counties, 'Initial referral edition. County or regional veterans and aging routes are mapped; Ionia uses statewide veterans routing and Wayne has two aging service areas. Ombudsman routing is statewide.'),
        ('ky.html', 'Kentucky', ky_resources, ky_counties, 'Initial referral edition. Regional veterans representatives, aging, district ombudsmen and supported-living routes are mapped; veterans contacts are regional rather than separate county offices.'),
    ]
    for page, state, records, contacts, scope in editions:
        pending = sum(r.get('verification', {}).get('record_status') != 'official_source_reviewed' for r in records)
        excerpts = sum(r.get('verification', {}).get('record_status') == 'official_search_extract_only' for r in records)
        notice = ('<section id="edition-coverage" class="edition-coverage notice" aria-label="Coverage and verification">'
                  f'<strong>{state}: coverage and verification</strong><p>{scope}</p>'
                  f'<p>Referral routes cover {len(contacts)} counties. This is not a complete local service inventory. '
                  f'{pending} resource records need further verification, including {excerpts} supported only by search excerpts. '
                  'Source status appears on each resource card. Published contacts are not telephone-confirmed; confirm intake and availability with the agency.</p></section>')
        result[page] = re.sub(r'<section id="urgent-help".*?</section>', '', result[page], flags=re.S)
        urgent = '<section id="urgent-help" class="notice" aria-labelledby="urgent-title"><h2 id="urgent-title">Need help now?</h2><p><strong>Suicide or emotional crisis:</strong> Call <a href="tel:988?oai_link_source=model_response_hotline">988</a> or <a href="sms:988?oai_link_source=model_response_hotline">text 988</a>. Veterans-specific support is available through the call service. <a href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">Online crisis chat</a>. For immediate danger, call 911 or go to the nearest emergency department.</p><p><strong>Homeless or facing housing loss:</strong> Call <a href="tel:8774243838">877-424-3838</a> for free, confidential VA housing referrals, 24/7. Family members and supporters may call too.</p><p><a href="?view=crisis">Mental health and suicide-prevention resources</a> · <a href="?view=housing">Housing and homelessness resources</a></p></section>'
        result[page] = result[page].replace('<section id="county-start"', urgent + '<section id="county-start"', 1)
        extras = "routes.crisis=['crisis-988','va-mental-health','va-location-finder'];routes.housing.push(...['va-ssvf','va-hud-vash','va-crrc'].filter(id=>!routes.housing.includes(id)));routeNames.crisis='Mental health and suicide prevention';"
        result[page] = re.sub(r'^routes.crisis=.*\n', '', result[page], flags=re.M)
        result[page] = result[page].replace("const STATE=", extras + "\nconst STATE=", 1)
        result[page] = re.sub(r'<section id="edition-coverage".*?</section>', '', result[page], flags=re.S)
        result[page] = result[page].replace('</nav>', '</nav>' + notice, 1)
    housing_count = len({county for r in resources if r.get('resource_role') == 'housing_provider' for county in r['service_area']})
    aid = "routes.aid=DATA.filter(x=>['aid_organization','housing_provider'].includes(x.resource_role)).map(x=>x.program_id);routeNames.aid='Ohio veteran and aid organizations';routes.benefits.push('ohio-legion-claims');routes.rights.push('ohio-legal-aid');routes.housing.push('ohio-legal-aid','ohio-utility-assistance',...DATA.filter(x=>x.resource_role==='housing_provider').map(x=>x.program_id));routes.care.push('ohio-dav-transport');routes.local.push('ohio-utility-assistance');"
    result['index.html'] = result['index.html'].replace('const STATE=', aid + '\nconst STATE=', 1)
    result['index.html'] = result['index.html'].replace('<section id="county-start"', f'<p id="ohio-aid-link"><a href="?view=aid"><strong>Ohio veteran and aid organizations</strong></a> · Housing providers, claims help, legal aid, utility assistance and medical transportation. Local veteran housing providers are mapped for {housing_count} of {len(counties)} counties; other counties retain VA referral routes. For emergency financial assistance, choose your county below and ask its veterans office about eligibility and current programs.</p><section id="county-start"', 1)
    result['bingo.html'] = make_bingo(ROOT)
    result['index.html'] = result['index.html'].replace('<h3>For posts and community groups</h3>', '<p id="ohio-bingo-link"><a href="bingo.html"><strong>Explore Ohio bingo and community activities</strong></a> - charitable sessions and senior-center activities, with sources and details to confirm before attending.</p><h3>For posts and community groups</h3>', 1)
    # Keep state adapter regression fixtures private to tests; the public site has one view.
    for page in ['index.html','pa.html','ny.html','mi.html','ky.html']:
        result['tests/fixtures/'+page] = result[page]
    result.update(unified_outputs(ROOT, result))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--test-fixtures', action='store_true')
    args = parser.parse_args()
    drift = []
    for name, text in outputs().items():
        if name.startswith('tests/fixtures/') and not args.test_fixtures:
            continue
        path = ROOT / name
        if not path.is_file() or path.read_text() != text:
            drift.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    if args.check and drift:
        parser.exit(1, 'Out of sync: ' + ', '.join(drift) + '. Run python3 scripts/build_public.py\n')
    print('Public projections are synchronized.' if args.check else 'Updated: ' + (', '.join(drift) or 'already synchronized'))
