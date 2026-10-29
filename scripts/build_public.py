#!/usr/bin/env python3
"""Refresh static projections from canonical JSON; --check detects drift without writes."""
import argparse
import json
import re
from pathlib import Path
from state_registry import (load_registry, load_counties, state_resources, make_edition,
                            make_share, add_share_links, add_state_options, BASE_URL)
from bingo_edition import make_bingo
from facilities_edition import make_facilities
from unified_guide import unified_outputs

ROOT = Path(__file__).resolve().parents[1]

def outputs():
    resources = json.loads((ROOT / 'prototype-data.json').read_text())
    counties = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    html = (ROOT / 'templates/guide.html').read_text()
    html = re.sub(r'<p id="ohio-bingo-link">.*?</p>', '', html)
    html = re.sub(r'<section id="urgent-help".*?</section>', '', html, flags=re.S)
    html = re.sub(r'^routes.aid=.*\n', '', html, flags=re.M)
    html = re.sub(r'<p id="ohio-aid-link">.*?</p>', '', html)
    html = re.sub(r'^routes.crisis=.*\n', '', html, flags=re.M)
    states = load_registry(ROOT)
    html = add_state_options(html, states)
    for name, value in [('DATA', resources), ('COUNTIES', counties)]:
        # Escape HTML parser boundaries inside strings while retaining valid JSON.
        payload = json.dumps(value, ensure_ascii=True).replace('<', '\\u003c')
        html, n = re.subn(r'const ' + name + r'=.*?;\n', lambda _: 'const ' + name + '=' + payload + ';\n', html, count=1)
        if n != 1:
            raise ValueError('Missing embedded ' + name)
    regional = sorted((r for r in resources if r.get('regional_role')), key=lambda r: r['program_id'])
    share = add_share_links((ROOT / 'share.html').read_text(), states)
    result = {
        'index.html': html,
        'data/public/ohio-regional-referrals.json': json.dumps(regional, indent=2, ensure_ascii=False) + '\n',
        'share.html': share,
    }
    editions = [(states[0], resources, counties)]
    for state in states[1:]:
        records = state_resources(ROOT, resources, state)
        contacts = load_counties(ROOT, state)
        if len(contacts) != state['counties']:
            raise ValueError(f"{state['code']}: registry expects {state['counties']} counties, data has {len(contacts)}")
        result[state['page']] = make_edition(html, state, records, contacts)
        result[state['resources']] = json.dumps(records, indent=2, ensure_ascii=False) + '\n'
        result[state['share_page']] = make_share(share, state)
        editions.append((state, records, contacts))


    for state_entry, records, contacts in editions:
        page, state, scope = state_entry['page'], state_entry['name'], state_entry['coverage_scope']
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
    result['facilities.html'] = make_facilities(ROOT)
    result['index.html'] = result['index.html'].replace('<h3>For posts and community groups</h3>', '<p id="ohio-bingo-link"><a href="bingo.html"><strong>Find Ohio bingo and senior centers</strong></a> - find nearby senior centers, exercise, crafts, games, meals and bingo by ZIP code.</p><h3>For posts and community groups</h3>', 1)
    # Keep state adapter regression fixtures private to tests; the public site has one view.
    for page in [s['page'] for s in states]:
        result['tests/fixtures/'+page] = result[page]
    result.update(unified_outputs(ROOT, result, states))
    # Track public landing/sharing pages once; state redirects count at destination.
    for page in ['index.html', 'bingo.html', 'facilities.html'] + [s['share_page'] for s in states]:
        result[page] = re.sub(r'<script[^>]*data-goatcounter=[^>]*></script>', '', result[page])
        result[page] = result[page].replace('<script defer src="assets/analytics.js"></script>', '')
        result[page] = result[page].replace('</body>', '<script defer src="assets/analytics.js"></script></body>')
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
