#!/usr/bin/env python3
"""Refresh static projections from canonical JSON; --check detects drift without writes."""
import argparse
import json
import re
from pathlib import Path
from state_registry import (load_registry, load_counties, state_resources, make_edition,
                            make_share, add_share_links, add_state_options, BASE_URL)
from bingo_edition import make_bingo
from a11y_finish import finish_all as a11y_finish_all
from bingo_site import make_bingo_site, SITE as OHIO_BINGO
from findbingo_site import make_findbingo, adsense as findbingo_adsense
from bingo_pipeline import outputs as bingo_pipeline_outputs
from facilities_edition import make_facilities
from unified_guide import unified_outputs
from build_disability_advocacy import outputs as disability_advocacy_outputs
from build_mobility_routes import outputs as mobility_route_outputs
from build_family_guide import outputs as family_guide_outputs
from build_guide_privacy import outputs as privacy_outputs
from build_world import outputs as world_outputs, pages as world_pages
from build_world_lite import outputs as world_lite_outputs
from build_packets import outputs as packet_outputs
from build_county_pages import outputs as county_outputs
from build_va_pages import outputs as va_outputs
from build_opportunities import outputs as opportunity_outputs
from build_core_care import (outputs as core_care_outputs, pages as core_care_pages,
                             add_cards as core_care_cards, add_facilities_links)
from build_bad_paper import outputs as bad_paper_outputs, pages as bad_paper_pages
import landing
from build_justice import outputs as justice_outputs
from build_contractors import outputs as contractor_outputs, pages as contractor_pages
from build_topic_pages import outputs as topic_outputs, pages as topic_pages, add_language_links
import visuals
import state_visuals
import page_visuals

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
    result.update(make_bingo_site(ROOT, result['bingo.html']))
    # The Ohio finder's public home is findbingo.org/ohio. This page stays as the build source and test
    # fixture; on the live guide it forwards there (keeping the ZIP search and #anchor) and names it as canonical.
    forward = ('<link rel="canonical" href="' + OHIO_BINGO + '/"><meta name="robots" content="noindex,follow">'
               "<script data-moved>if(location.hostname==='guide.vethomeguard.org')location.replace('" + OHIO_BINGO + "/'+location.search+location.hash)</script>")
    canonical = '<link rel="canonical" href="https://guide.vethomeguard.org/bingo.html">'
    assert result['bingo.html'].count(canonical) == 1
    result['bingo.html'] = result['bingo.html'].replace(canonical, forward)
    result.update(make_findbingo(ROOT))
    result.update(findbingo_finishing(result))
    # Google AdSense on findbingo.org only (bingo-site/findbingo/); never on the guide or findbingo-site/ (Ad Grants).
    result.update(findbingo_adsense(result))
    # The bingo pipeline's normalized CSV and coverage report (docs/BINGO-PIPELINE.md) follow the lists they read.
    result.update({str(p.relative_to(ROOT)): t for p, t in bingo_pipeline_outputs().items()})
    result['facilities.html'] = make_facilities(ROOT)
    # Links to the pages for veterans in nursing homes and their families (scripts/build_core_care.py).
    result['facilities.html'] = add_facilities_links(result['facilities.html'])
    result['index.html'] = result['index.html'].replace('<h3>For posts and community groups</h3>', '<p id="ohio-bingo-link"><a href="' + OHIO_BINGO + '/"><strong>Find Ohio bingo and senior centers</strong></a> - find nearby senior centers, exercise, crafts, games, meals and bingo by ZIP code.</p><h3>For posts and community groups</h3>', 1)
    # Keep state adapter regression fixtures private to tests; the public site has one view.
    for page in [s['page'] for s in states]:
        result['tests/fixtures/'+page] = result[page]
    result.update(unified_outputs(ROOT, result, states))
    # Every state page gets the card for veterans in nursing homes, with that state's APS line.
    result.update(core_care_cards(result, states))
    result.update(core_care_outputs(states))
    result.update(disability_advocacy_outputs())
    result.update(mobility_route_outputs())
    result.update(family_guide_outputs())
    result.update(privacy_outputs())
    # Country pages for veterans outside the U.S. (data/world/countries.json); each carries the visit counter.
    result.update(world_outputs())
    # Their text-only, low-data copies (world/lite/), for slow connections, basic phones and the offline pack; not in the sitemap.
    result.update(world_lite_outputs())
    # Veterans in the justice system (data/justice.json); linked from every state page.
    result.update(justice_outputs())
    # Veteran-owned Ohio contractors, fair prices and free profiles (data/contractors/); linked from the Ohio front page.
    result.update(contractor_outputs())
    # Printable resource packets (paper handouts) and their download page; PDFs: node scripts/build_packets.cjs.
    result.update(packet_outputs())
    # One page per county veterans office (counties/<st>/<county>.html), and a link to the state's list from its guide.
    county_pages, county_urls = county_outputs(ROOT)
    result.update(county_pages)
    for s in states:
        unit = {'LA': 'parish', 'DC': 'District'}.get(s['code'], 'county')
        text = 'The District of Columbia veterans office' if s['code'] == 'DC' else f'Every {s["name"]} {unit} veterans office'
        link = (f'<p id="county-pages-link"><a href="counties/{s["code"].lower()}/">{text}</a>'
                f' · one page per {unit}, with its phone and next steps.</p>')
        assert result[s['page']].count('<section id="county-start"') == 1, s['page']
        result[s['page']] = result[s['page']].replace('<section id="county-start"', link + '<section id="county-start"', 1)
    # One page per state listing its VA locations (va-locations/<st>/), from VA facility data, linked from that state's guide.
    va_pages, va_urls, va_links = va_outputs(ROOT)
    result.update(va_pages)
    for s in states:
        if s['code'] in va_links:
            result[s['page']] = result[s['page']].replace('<section id="county-start"', va_links[s['code']] + '<section id="county-start"', 1)
    # Programs, grants, scholarships, events and benefits open to veterans (scripts/build_opportunities.py): a page per
    # state that has data, local ones first, and a nationwide page. Every state guide links to its own page, or to the
    # nationwide one until its state is added; every Ohio county office page lists the local programs that serve it.
    opp_pages, opp_urls, opp_links, opp_county = opportunity_outputs(ROOT)
    result.update(opp_pages)
    for s in states:
        link = opp_links.get(s['code'], opp_links.get('*'))
        if link:
            result[s['page']] = result[s['page']].replace('<section id="county-start"', link + '<section id="county-start"', 1)
    for page, block in opp_county.items():
        marker = '<section class="notice" aria-labelledby="now">'
        assert result[page].count(marker) == 1, page
        result[page] = result[page].replace(marker, block + marker, 1)
    # Other-than-honorable and bad-conduct discharges (templates/bad-paper/); each page carries the visit counter.
    result.update(bad_paper_outputs(result))
    # Each entry page speaks to the person most likely to land on it (data/landing/): the sharing kits to the
    # people passing the guide on, and facilities, flyers and the rest to their own visitors.
    for s in states:
        result[s['share_page']] = landing.share_page(result[s['share_page']], s)
    # Help after military sexual trauma, Gold Star and surviving families, and the Ohio essentials in Spanish
    # (scripts/build_topic_pages.py). The English front page links to the Spanish one, both ways, with hreflang.
    result.update(topic_outputs())
    result.update(landing.apply_pages(result))
    result['index.html'] = add_language_links(result['index.html'])
    # Track public landing/sharing pages once, including each state's own guide page.
    for page in ['index.html', 'bingo.html', 'facilities.html'] + [s['page'] for s in states[1:]] + [s['share_page'] for s in states]:
        result[page] = re.sub(r'<script[^>]*data-goatcounter=[^>]*></script>', '', result[page])
        result[page] = result[page].replace('<script defer src="assets/analytics.js"></script>', '')
        result[page] = result[page].replace('</body>', '<script defer src="assets/analytics.js"></script></body>')
    # The mobility and advocacy pages are canonical at mobilitytalk.org, so they stay out of this sitemap.
    # Search engines: list the public views, including each state's canonical URL.
    pages = ['', 'facilities.html', 'family-guide.html', 'justice.html', 'flyers.html', 'packets.html', 'privacy.html']
    urls = [BASE_URL + page for page in pages if page == '' or (ROOT / page).is_file() or page in result]
    # Each state's own page (ky.html); Ohio is the root. Old ?state= links still work but are not listed.
    urls += [BASE_URL + s['page'] for s in states[1:]]
    # The per-state share pages are public, each with its own title and description.
    urls += [BASE_URL + s['share_page'] for s in states]
    # Veterans outside the U.S.: the world index and one page per country.
    urls += [BASE_URL + page for page in world_pages()]
    # County veterans office pages: the all-states list, each state's list and every county.
    urls += county_urls
    # VA locations: the by-state list and each state's page.
    urls += va_urls
    # Veteran programs: the by-state list, each state's page, the nationwide page and one page per program.
    urls += opp_urls
    # Pages for veterans in nursing homes and their families.
    urls += [BASE_URL + page for page in core_care_pages()]
    # Bad paper: VA options, discharge boards, records and free help for other-than-honorable discharges.
    urls += [BASE_URL + page for page in bad_paper_pages()]
    # Help after MST, Gold Star and surviving families, and the guide in Spanish.
    urls += [BASE_URL + page for page in topic_pages()]
    # Veteran-owned Ohio contractors: the directory, fair prices and the free-profile page.
    urls += [BASE_URL + page for page in contractor_pages()]
    result['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>' + u.replace('&', '&amp;') + '</loc></url>\n' for u in urls) + '</urlset>\n'
    result['robots.txt'] = 'User-agent: *\nAllow: /\n\nSitemap: ' + BASE_URL + 'sitemap.xml\n'
    # Each state page's at-a-glance map and counts and its who-to-call-first diagram, and the tile map on the
    # by-state hub pages (scripts/state_visuals.py).
    result.update(state_visuals.add(result, editions))
    result.update(state_visuals.add_hubs(result, states))
    # Topic, hub and sharing pages: symbols, diagrams and charts from each page's own facts (scripts/page_visuals.py).
    result.update(page_visuals.add(result))
    # The guide's line icons, drawn once for every page that uses them (scripts/visuals.py).
    result[visuals.SPRITE] = visuals.sprite()
    # Last step: a skip link, a <main> target, reduced motion and link symbols on every page (scripts/a11y_finish.py).
    result.update(a11y_finish_all(result))
    return result


# FindBingo.org (bingo-site/findbingo/, served by Cloudflare): a site icon on every page, so browser tabs,
# bookmarks and search results do not show a blank icon, and a "page not found" page with a way back.
FINDBINGO_ICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#c8382c"/>'
                  '<circle cx="32" cy="32" r="18" fill="#ffffff"/><text x="32" y="41" text-anchor="middle" '
                  'font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="25" fill="#183449">B</text></svg>\n')
def findbingo_icon_link(prefix):
    return f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">'
FINDBINGO_404 = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                 # Served at whatever address was not found, so every link resolves from the site root.
                 '<base href="/"><title>Page not found | FindBingo.org</title><meta name="robots" content="noindex">' + findbingo_icon_link('') +
                 '<style>body{font:20px/1.5 system-ui,sans-serif;margin:3rem auto;max-width:34rem;padding:0 1rem;color:#1f2f38}'
                 'a{color:#183449;font-weight:700}footer{margin-top:2.5rem;font-size:17px}'
                 '@media (prefers-color-scheme:dark){:root{color-scheme:dark}body{background:#10181d;color:#e4ecef}a{color:#9fd0ef}}'
                 '</style></head><body><main id="main"><h1>We could not find that page</h1>'
                 '<p>The link may be old or mistyped.</p><p><a href="./">Find bingo near you</a></p>'
                 '<p><a href="ohio/">Ohio Bingo Finder</a></p></main>'
                 '<footer><p>FindBingo.org is a free community resource from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>. '
                 '<a href="about/">About and contact</a> · <a href="privacy/">Privacy</a> · <a href="terms/">Terms of use</a> · <a href="advertise/">Advertise on Find Bingo</a></p></footer>'
                 # Page views on the same counter as every other Find Bingo page (assets/analytics.js, written in).
                 '<script>' + (ROOT / 'assets/analytics.js').read_text().strip() + '</script></body></html>\n')


def findbingo_finishing(result):
    # findbingo-site/ is the same site's copy on the guide (the finder's data source); the two stay identical.
    out = {'bingo-site/findbingo/favicon.svg': FINDBINGO_ICON, 'findbingo-site/favicon.svg': FINDBINGO_ICON,
           'bingo-site/findbingo/404.html': FINDBINGO_404}
    for name, text in result.items():
        base = next((b for b in ('bingo-site/findbingo/', 'findbingo-site/') if name.startswith(b)), None)
        if (base and name.endswith('.html') and isinstance(text, str)
                and '</head>' in text and 'favicon.svg' not in text):
            depth = name[len(base):].count('/')
            out[name] = text.replace('</head>', findbingo_icon_link('../' * depth) + '</head>', 1)
    return out

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
        binary = isinstance(text, bytes)
        if not path.is_file() or (path.read_bytes() if binary else path.read_text()) != text:
            drift.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(text) if binary else path.write_text(text)
    if args.check and drift:
        parser.exit(1, 'Out of sync: ' + ', '.join(drift) + '. Run python3 scripts/build_public.py\n')
    print('Public projections are synchronized.' if args.check else 'Updated: ' + (', '.join(drift) or 'already synchronized'))
