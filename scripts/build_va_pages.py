#!/usr/bin/env python3
"""One page per state listing its VA medical centers, clinics, Vet Centers, benefits offices and cemeteries.

Built from data/public/va-facilities/<st>.json, which scripts/mining/va_listings.py makes from the VA Facilities API.
A state appears here only once its file exists, so states are added one batch at a time.

Outputs:
  va-locations/index.html the states that have a VA locations page
  va-locations/<st>/index.html     every VA location in one state, grouped by kind and sorted by city
"""
import json
from pathlib import Path

from build_county_pages import BASE_URL, STYLE, e, tel, urgent, when

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'va-locations'
DATA = ROOT / 'data' / 'public' / 'va-facilities'
SECTIONS = [
    ('health', 'VA medical centers and clinics', 'Health care for enrolled veterans: primary care, mental health, '
     'specialty care and, at medical centers, emergency and hospital care.'),
    ('vet_center', 'Vet Centers', 'Free, confidential counseling for combat veterans, service members, Guard and '
     'Reserve, military sexual trauma survivors and their families. No VA health enrollment is needed.'),
    ('benefits', 'VA benefits offices', 'Help with disability claims, pension, education, home loans and Veteran '
     'Readiness and Employment. Many are satellite desks; call first.'),
    ('cemetery', 'Veterans cemeteries', 'National and state veterans cemeteries: burial eligibility, '
     'pre-need planning and gravesite locations.'),
]
NOUN = {'health': 'medical centers and clinics', 'vet_center': 'Vet Centers', 'benefits': 'benefits offices',
        'cemetery': 'cemeteries'}


def files():
    return sorted(DATA.glob('*.json')) if DATA.exists() else []


def registry():
    return {s['code']: s for s in json.loads((ROOT / 'states/registry.json').read_text())}


def card(r):
    parts = [f'<article class="office" id="{e(r["id"])}"><h3 style="margin:0 0 4px;font-size:20px">{e(r["name"])}</h3>']
    if r.get('classification'):
        parts.append(f'<p class="meta" style="margin:0">{e(r["classification"])}</p>')
    parts.append(f'<p class="phone">{tel(r["phone"])}</p>')
    if r.get('mental_health_phone'):
        parts.append(f'<p>Mental health clinic: {tel(r["mental_health_phone"])}</p>')
    parts.append(f'<p>{e(r["address"])}, {e(r["city"])}, {e(r["state"])} {e(r["zip"])}</p>')
    if r.get('hours'):
        parts.append(f'<p><strong>Hours:</strong> {e(r["hours"])}</p>')
    if r.get('notice'):
        parts.append(f'<p class="notice" style="padding:8px 12px">{e(r["notice"])}</p>')
    if r.get('website'):
        parts.append(f'<p><a href="{e(r["website"])}" rel="noopener">VA page for this location</a></p>')
    parts.append('</article>')
    return ''.join(parts)


def page(title, description, path, crumbs, hero, body, depth):
    up = '../' * depth
    canonical = BASE_URL + path.replace('index.html', '')
    trail = ' › '.join(f'<a href="{e(href)}">{e(text)}</a>' if href else e(text) for text, href in crumbs)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{e(title)}</title>\n<meta name="description" content="{e(description)}">\n'
            f'<link rel="canonical" href="{e(canonical)}">\n'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}">'
            f'<meta property="og:image" content="{BASE_URL}assets/vhg-logo.png">\n'
            f'<link rel="icon" href="{up}favicon.ico"><style>{STYLE}h3{{color:var(--navy)}}</style></head>\n'
            f'<body><header><nav aria-label="Breadcrumb" class="small">{trail}</nav>{hero}</header>\n'
            f'<main id="main">{body}</main>\n'
            '<footer><p>Free from <a href="https://www.vethomeguard.org/about.html">Veteran Home Guardians</a>, an independent '
            '501(c)(3) nonprofit (EIN 33-4637180) that visits isolated veterans and publishes free guides. It is not part of the '
            'U.S. Department of Veterans Affairs. Locations, phones and hours come from VA’s own facility data and are not '
            'telephone-confirmed. Report a change: <a href="mailto:travis@vethomeguard.org?subject=VA%20location%20correction">'
            f'travis@vethomeguard.org</a>.</p><p><a href="{up}">Veteran Resource Guide</a> · <a href="{up}{FOLDER}/">VA locations by state</a> · '
            f'<a href="{up}counties/">County veterans offices</a> · <a href="{up}privacy.html">Privacy</a></p></footer>\n'
            f'<script defer src="{up}assets/analytics.js"></script></body></html>\n')


def summary(counts):
    return ', '.join(f'{counts[k]} {NOUN[k]}' for k, _, _ in SECTIONS if counts.get(k))


def outputs(root=ROOT):
    states = registry()
    out, urls, rows, links = {}, [], [], {}
    for path in files():
        data = json.loads(path.read_text())
        code = data['state']
        state = states[code]
        sname, low = state['name'], code.lower()
        counts = {}
        for r in data['rows']:
            counts[r['kind']] = counts.get(r['kind'], 0) + 1
        src = data['source']
        body = [f'<p>{e(summary(counts))}. Grouped by kind, then by city. Facilities VA lists as closed are left out.</p>']
        for kind, heading, blurb in SECTIONS:
            items = [r for r in data['rows'] if r['kind'] == kind]
            if items:
                body.append(f'<h2 id="{kind}">{e(heading)} in {e(sname)}</h2><p>{e(blurb)}</p>' + ''.join(card(r) for r in items))
        body.append('<h2>Not enrolled in VA health care?</h2><p>Call <a href="tel:+18772228387">877-222-8387</a> or apply '
                    f'with the help of a free veterans service officer: <a href="../../counties/{low}/">find your county’s '
                    'veterans office</a>.</p>')
        body.append(urgent(sname))
        body.append(f'<p class="meta">Source: U.S. Department of Veterans Affairs facility data (VA Facilities API), '
                    f'retrieved {when(src["retrieved_on"])}. Each location links to its own VA page where VA gives one. '
                    'Hours and services change; call before you go.</p>')
        body.append(f'<p><a class="button" href="../../{e(state["page"] if not state.get("base") else "")}">The full {e(sname)} veteran guide</a></p>')
        hero = (f'<small>Veteran Resource Guide · {e(sname)}</small><h1>VA locations in {e(sname)}</h1>'
                f'<p>Every VA medical center, clinic, Vet Center, benefits office and veterans cemetery in {e(sname)}, '
                'with phones, addresses and hours.</p>')
        rel = f'{FOLDER}/{low}/index.html'
        out[rel] = page(f'VA medical centers, clinics and Vet Centers in {sname} | Veteran Resource Guide',
                        f'Every VA medical center, clinic, Vet Center, benefits office and veterans cemetery in {sname}: '
                        'phones, addresses and hours from VA’s facility data.',
                        rel, [('Veteran Resource Guide', '../../'), ('VA locations', '../'), (sname, None)], hero, ''.join(body), 2)
        urls.append(BASE_URL + f'{FOLDER}/{low}/')
        rows.append(f'<li><a href="{low}/">{e(sname)}</a> <span class="meta">({len(data["rows"])})</span></li>')
        links[code] = (f'<p id="va-locations-link"><a href="{FOLDER}/{low}/">Every VA location in {e(sname)}</a>'
                       f' · {e(summary(counts))}, with phones and hours.</p>')
    if rows:
        rel = f'{FOLDER}/index.html'
        hero = ('<small>Veteran Resource Guide</small><h1>VA locations by state</h1>'
                '<p>VA medical centers, clinics, Vet Centers, benefits offices and veterans cemeteries, one state at a time.</p>')
        out[rel] = page('VA medical centers, clinics and Vet Centers by state | Veteran Resource Guide',
                        'Find VA medical centers, clinics, Vet Centers, benefits offices and veterans cemeteries by state, '
                        'with phones, addresses and hours.',
                        rel, [('Veteran Resource Guide', '../'), ('VA locations', None)], hero,
                        f'<ul class="cols">{"".join(rows)}</ul>' + urgent(''), 1)
        urls.insert(0, BASE_URL + f'{FOLDER}/')
    return out, urls, links


if __name__ == '__main__':
    pages, urls, links = outputs()
    print(len(pages), 'pages,', len(urls), 'sitemap URLs,', len(links), 'state links')
