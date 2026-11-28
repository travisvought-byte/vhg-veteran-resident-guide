#!/usr/bin/env python3
"""One static page per county veterans office, so each county has its own address.

Search engines and Google Ad Grants ads need a page that answers "[county] veterans service office" on
its own, without choosing from a menu. Every page is built from the same county office files the state
guides use (states/registry.json -> data/public/*-county-veterans-offices.json), so a correction to a
county's data changes its page on the next build. Nothing here is new research.

Outputs:
  counties/index.html                every state, linking to its county list
  counties/<st>/index.html           every county in one state
  counties/<st>/<county>.html        one county's office, with crisis and housing lines and next steps
"""
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urljoin

from visuals import icon, stylesheet

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://guide.vethomeguard.org/'
FOLDER = 'counties'
# Sister guides, linked from every county page so each county's help sits one click apart across the family of sites.
# Yoga Mom Talk builds a page for (nearly) every county with the same slug; Mobility Talk and Find Bingo have state pages.
YMT_ROOT = 'https://www.yogamomtalk.com/states/'
MOBILITY_ROOT = 'https://mobilitytalk.org/states/'
FINDBINGO_ROOT = 'https://www.findbingo.org/'
BINGO_LISTED = {'times', 'licenses', 'starter', 'ohio_finder'}


def e(text):
    return html.escape(str(text or ''), quote=True)


def slug(name):
    s = name.lower().replace('&', ' and ').replace('’', '').replace("'", '').replace('.', '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def label(record):
    """The county's full name as people search for it: Delaware County, Acadia Parish, Alexandria City."""
    name, kind = record['county'].strip(), record.get('county_type', 'county')
    if kind == 'parish':
        return name if name.endswith('Parish') else name + ' Parish'
    if kind in ('borough', 'census_area', 'city_and_county', 'independent_city', 'statewide'):
        return name
    if re.search(r'\b(County|City|Borough|Parish)$', name):
        return name
    return name + ' County'


def tel(number):
    digits = re.sub(r'\D', '', number.split('x')[0].split('ext')[0])
    if len(digits) == 10:
        digits = '1' + digits
    return f'<a href="tel:+{digits}">{e(number)}</a>' if len(digits) == 11 else e(number)


def when(iso):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
              'October', 'November', 'December']
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', iso or '')
    return f'{months[int(m[2]) - 1]} {int(m[3])}, {m[1]}' if m else e(iso)


STYLE = (':root{--navy:#183449;--green:#335947;--paper:#f5f3ed;--line:#d9dfda;--gold:#bb8e36}*{box-sizing:border-box}'
         'body{margin:0;background:var(--paper);color:#20313a;font:17px/1.55 system-ui,sans-serif}'
         'header{background:var(--navy);color:#fff;padding:32px max(24px,calc((100vw - 960px)/2))}'
         'header a{color:#fff}header small{color:#e7cc88;letter-spacing:2px;text-transform:uppercase}'
         'h1{font:700 clamp(28px,5vw,42px)/1.15 Georgia,serif;margin:10px 0}header p{color:#e3eaed;max-width:760px}'
         'main{max-width:1008px;margin:auto;padding:24px}h2{font:700 24px/1.25 Georgia,serif;color:var(--navy);margin:26px 0 10px}'
         'a{color:#215b76;text-underline-offset:3px}article{background:#fff;border:1px solid var(--line);border-radius:9px;padding:22px;margin:14px 0}'
         '.office{border-top:4px solid var(--gold)}.phone{font-size:22px;font-weight:700;margin:6px 0}.meta,.small{font-size:14px;color:#52665c}'
         '.notice{background:#fff4dc;border:1px solid #e8cf93;border-radius:9px;padding:16px 20px}'
         '.button{display:inline-block;background:var(--green);color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:650}'
         'ul.cols{columns:3 220px;padding-left:18px}ul.cols li{margin:4px 0;break-inside:avoid}'
         'footer{max-width:1008px;margin:auto;padding:12px 24px 40px;font-size:14px;color:#52665c}'
         ':focus-visible{outline:3px solid #ca9f48;outline-offset:3px}')


def page(title, description, path, crumbs, hero, body, depth, robots='', head=''):
    up = '../' * depth
    canonical = BASE_URL + path
    trail = ' › '.join(f'<a href="{e(href)}">{e(text)}</a>' if href else e(text) for text, href in crumbs)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{e(title)}</title>\n<meta name="description" content="{e(description)}">\n'
            f'<link rel="canonical" href="{e(canonical)}">\n'
            + (f'<meta name="robots" content="{e(robots)}">\n' if robots else '')
            + 
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}">'
            f'<meta property="og:image" content="{BASE_URL}assets/vhg-logo.png">\n'
            f'<link rel="icon" href="{up}favicon.ico"><style>{STYLE}</style>{head}'
            + (stylesheet(up) if 'class="vi"' in body else '') + '</head>\n'
            f'<body><header><nav aria-label="Breadcrumb" class="small">{trail}</nav>{hero}</header>\n'
            f'<main id="main">{body}</main>\n'
            '<footer><p>Free from <a href="https://www.vethomeguard.org/about.html">Veteran Home Guardians</a>, an independent '
            '501(c)(3) nonprofit (EIN 33-4637180) that visits isolated veterans and publishes free guides. It is not part of the '
            'U.S. Department of Veterans Affairs. Contacts come from the official or published sources named on each page and are '
            'not telephone-confirmed. Report a change: <a href="mailto:travis@vethomeguard.org?subject=County%20veterans%20office%20correction">'
            f'travis@vethomeguard.org</a>.</p><p><a href="{up}">Veteran Resource Guide</a> · <a href="{up}{FOLDER}/">All states</a> · '
            f'<a href="{up}privacy.html">Privacy</a></p></footer>\n'
            f'<script defer src="{up}assets/analytics.js"></script></body></html>\n')


def urgent(state_name):
    return ('<section class="notice" aria-labelledby="now"><h2 id="now" style="margin-top:0">Need help now?</h2>'
            '<p><strong>Crisis:</strong> call <a href="tel:988">988</a> and press 1 for the Veterans Crisis Line, or text '
            '<a href="sms:838255">838255</a>. In immediate danger, call <a href="tel:911">911</a>.</p>'
            '<p><strong>Homeless or about to lose housing:</strong> call <a href="tel:+18774243838">877-424-3838</a>, the VA '
            'National Call Center for Homeless Veterans, any time, day or night.</p></section>')


def office_card(r, name):
    org = r.get('organization') or f'{name} veterans service office'
    parts = [f'<article class="office"><h2 style="margin-top:0">{e(org)}</h2>']
    parts.append(f'<p class="phone">{tel(r["phone"])}</p>')
    for other in r.get('other_phones') or []:
        parts.append(f'<p>Also: {tel(other)}</p>')
    if r.get('address'):
        parts.append(f'<p>{e(r["address"])}</p>')
    if r.get('hours'):
        parts.append(f'<p><strong>Hours:</strong> {e(r["hours"])}</p>')
    if r.get('email'):
        parts.append(f'<p>Email: <a href="mailto:{e(r["email"])}">{e(r["email"])}</a></p>')
    if r.get('website'):
        parts.append(f'<p><a href="{e(r["website"])}" rel="noopener">Office website</a></p>')
    if r.get('note'):
        parts.append(f'<p class="small">{e(r["note"])}</p>')
    parts.append(f'<p class="meta">Source: <a href="{e(r["source_url"])}" rel="noopener">{e(r["source_title"])}</a>. '
                 f'Checked {when(r.get("details_reviewed_on") or r["reviewed_on"])}. Published numbers are not telephone-confirmed.</p></article>')
    return ''.join(parts)


def county_title(place, r):
    """A title that fits in a search result (60 characters), naming what people look for on the page."""
    base = f'{place} veterans service office'
    extras = ([': phone and hours', ': phone, hours'] if r.get('hours') else []) + (
        [': phone and address'] if r.get('address') else []) + [': phone number', '']
    return next((base + x for x in extras if len(base + x) <= 60), base)


def state_slug(name):
    return slug(name.replace('U.S.', 'U S'))


YMT_SLUG = {('tx', 'lasalle-county'): 'la-salle-county', ('il', 'dewitt-county'): 'de-witt-county', 'obrien-county': 'o-brien-county',
            'do-a-ana-county': 'dona-ana-county', 'charles-city': 'charles-city-county', 'james-city': 'james-city-county',
            'prince-georges-county': 'prince-george-s-county', 'queen-annes-county': 'queen-anne-s-county',
            'st-marys-county': 'st-mary-s-county'}


def nearby(code, sname, s, name, bingo):
    """Links to the same county or state on the sister guides: family help, disability help, bingo nights."""
    family = (f'{YMT_ROOT}{code}.html' if code == 'ct' else f'{YMT_ROOT}{code}/{YMT_SLUG.get((code, s), YMT_SLUG.get(s, s))}.html')
    where = e(sname) if code == 'ct' else e(name)
    items = [f'<li><a href="{family}">Help for moms and families in {where}</a> '
             '<span class="small">(Yoga Mom Talk: food, child care, health and baby supplies)</span></li>',
             f'<li><a href="{MOBILITY_ROOT}{state_slug(sname)}.html">Disability and mobility help in {e(sname)}</a> '
             '<span class="small">(Mobility Talk: equipment, home changes, rides and benefits)</span></li>']
    if bingo:
        items.append(f'<li><a href="{FINDBINGO_ROOT}{state_slug(sname)}/">Bingo nights in {e(sname)}</a> '
                     '<span class="small">(Find Bingo: many games are run by veterans posts)</span></li>')
    return f'<h2>More free help near {e(name)}</h2><ul>{"".join(items)}</ul>'


def structured(crumbs, path, org, r, place):
    """Breadcrumb and office details for search engines, from the same record the page shows."""
    here = BASE_URL + path
    trail = [{'@type': 'ListItem', 'position': i + 1, 'name': text, 'item': urljoin(here, href) if href else here}
             for i, (text, href) in enumerate(crumbs)]
    office = {'@context': 'https://schema.org', '@type': 'GovernmentOffice', 'name': org, 'telephone': r['phone'],
              'areaServed': place, 'url': here}
    if r.get('address'):
        office['address'] = r['address']
    if r.get('website'):
        office['sameAs'] = r['website']
    data = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': trail}, office]
    return ''.join('<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'
                   for d in data)


def guide_link(state, county):
    target = '' if state.get('base') else state['page']
    return f'{target}?county={quote(county)}'


def outputs(root=ROOT):
    states = json.loads((root / 'states/registry.json').read_text())
    bingo = {s['code'] for s in json.loads((root / 'data/public/bingo-states.json').read_text()) if s['coverage'] in BINGO_LISTED}
    out, urls, state_rows = {}, [], []
    for state in sorted(states, key=lambda s: s['name']):
        code, sname = state['code'].lower(), state['name']
        records = json.loads((root / state['offices']).read_text())
        rows, used = [], set()
        # A number several counties share is a regional or statewide office: those pages say the same thing with a
        # different county name, so they stay up for visitors and ads but are kept out of search (noindex, no sitemap).
        shared = Counter(r['phone'] for r in records)
        for r in sorted(records, key=lambda r: label(r)):
            name = label(r)
            s = slug(name)
            if s in used:
                raise ValueError(f'{code}: two counties share the address {s}')
            used.add(s)
            path = f'{FOLDER}/{code}/{s}.html'
            place = name if r.get('county_type') == 'statewide' else f'{name}, {sname}'
            title = county_title(place, r)
            desc = (f'Free help for veterans and families in {place}: the local veterans service office phone'
                    + (', address' if r.get('address') else '') + (' and hours' if r.get('hours') else '')
                    + ', plus help with VA claims, pension and Aid and Attendance for care at home, survivor benefits, health care and housing.')
            hero = (f'<small>Veteran Resource Guide · {e(sname)}</small><h1>Veterans help in {e(place)}</h1>'
                    f'<p>The veterans service office for {e(name)} helps veterans, survivors and families apply for the benefits '
                    'they have earned, at no charge.</p>')
            body = (office_card(r, name)
                    + '<h2>What the office can help with</h2><ul class="vz-ilist">'
                    f'<li>{icon("doc-check", "../../")}Filing a VA disability compensation claim, or an increase, and gathering the records it needs</li>'
                    f'<li>{icon("dollar", "../../")}VA pension, including Aid and Attendance for veterans and survivors who need help with daily care</li>'
                    f'<li>{icon("flag", "../../")}Survivor benefits, burial and memorial benefits</li>'
                    f'<li>{icon("folder", "../../")}Getting military records, including a copy of the DD214</li>'
                    f'<li>{icon("medical", "../../")}Signing up for VA health care and finding local veterans programs</li></ul>'
                    '<p>Call ahead to confirm hours and what to bring. A veterans service office will never charge you to file a VA claim.</p>'
                    + urgent(sname)
                    + f'<h2>More help in {e(sname)}</h2><p>The full guide for {e(sname)} lists state veterans programs, VA health care, '
                    'aging and caregiver support, long-term care and housing help, with this county already chosen.</p>'
                    f'<p><a class="button" href="../../{e(guide_link(state, r["county"]))}">Open the {e(sname)} guide for {e(name)}</a></p>'
                    + nearby(code, sname, s, name, state['code'] in bingo)
                    + f'<p><a href="./">Every county in {e(sname)}</a></p>')
            crumbs = [('Veteran Resource Guide', '../../'), ('All states', '../'), (sname, './'), (name, None)]
            own = shared[r['phone']] == 1
            org = r.get('organization') or f'{name} veterans service office'
            out[path] = page(title, desc, path, crumbs, hero, body, 2, robots='' if own else 'noindex,follow',
                             head=structured(crumbs, path, org, r, place))
            if own:
                urls.append(BASE_URL + path)
            rows.append(f'<li><a href="{e(s)}.html">{e(name)}</a></li>')
        kind = 'parishes' if code == 'la' else 'counties and areas' if code in ('ak', 'va') else 'counties'
        path = f'{FOLDER}/{code}/index.html'
        hero = (f'<small>Veteran Resource Guide</small><h1>Veterans service offices in {e(sname)}</h1>'
                f'<p>Choose your {"parish" if code == "la" else "county"} for its local veterans office phone and next steps.</p>')
        body = (f'<h2>{e(sname)} {kind}</h2><ul class="cols">{"".join(rows)}</ul>'
                f'<p><a href="../../{e("" if state.get("base") else state["page"])}">The full {e(sname)} veteran guide</a></p>' + urgent(sname))
        out[path] = page(f'{sname} county veterans service offices | Veteran Resource Guide',
                         f'Local veterans service office contacts for every {kind[:-1] if kind.endswith("s") else kind} in {sname}, with free help on VA claims, pension, survivor benefits and housing.',
                         path, [('Veteran Resource Guide', '../../'), ('All states', '../'), (sname, None)], hero, body, 2)
        urls.append(BASE_URL + f'{FOLDER}/{code}/')
        state_rows.append(f'<li><a href="{code}/">{e(sname)}</a></li>')
    path = f'{FOLDER}/index.html'
    hero = ('<small>Veteran Resource Guide</small><h1>Find your county veterans service office</h1>'
            '<p>Every state and the District of Columbia. Choose a state, then your county.</p>')
    out[path] = page('County veterans service offices in every state | Veteran Resource Guide',
                     'Find the local veterans service office for any county in the United States: free help with VA claims, pension, survivor benefits and housing.',
                     path, [('Veteran Resource Guide', '../'), ('All states', None)], hero,
                     f'<ul class="cols">{"".join(state_rows)}</ul>' + urgent(''), 1)
    urls.insert(0, BASE_URL + f'{FOLDER}/')
    return out, urls


if __name__ == '__main__':
    pages, urls = outputs()
    print(len(pages), 'pages,', len(urls), 'sitemap URLs')
