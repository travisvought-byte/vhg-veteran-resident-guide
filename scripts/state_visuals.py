"""Visuals for every state's guide page and the by-state hub pages (November 25, 2026).

Travis asked for "reasonable visuals everywhere, at least for the US side". Each state page (Ohio is index.html)
gets, from data the guide already has:

- "<State> at a glance": a small locator map (the guide's own equal-square tile map, so no map pictures are
  fetched) with the state marked by a dark square and a ring, and tiles with counts the guide already shows:
  its counties (one page each) and its VA locations by kind (data/public/va-facilities/<st>.json).
- "Who to call first": each common situation, an arrow, and the first contact the page already gives for it
  (988, 911, the VA housing line, the state's Adult Protective Services line, the local veterans office, VA
  locations and senior and disability support).

Both are figures with captions; every word is real text, the symbols are hidden from screen readers, and the
map is an image with a title and a description. The state picker can swap the page to another state in place,
so both carry the class vz-local and a one-line rule hides them once the page shows a different state.

The hub pages that list every state (counties/ and va-locations/) get the same tile map as a set of links.
"""
import json
from html import escape
from pathlib import Path

from visuals import icon, stylesheet, locator
from unified_guide import TILES
from build_core_care import aps_data, tel

ROOT = Path(__file__).resolve().parents[1]

# The same kinds, words and order as the VA locations pages (scripts/build_va_pages.py).
VA_KINDS = [('health', 'medical center or clinic', 'medical centers and clinics', 'medical'),
            ('vet_center', 'Vet Center', 'Vet Centers', 'chat'),
            ('benefits', 'benefits office', 'benefits offices', 'doc'),
            ('cemetery', 'veterans cemetery', 'veterans cemeteries', 'flag')]

def va_counts(code):
    path = ROOT / 'data/public/va-facilities' / (code.lower() + '.json')
    if not path.is_file():
        return {}
    counts = {}
    for r in json.loads(path.read_text())['rows']:
        counts[r['kind']] = counts.get(r['kind'], 0) + 1
    return counts


def area_words(code, contacts):
    """How the guide names a state's local areas: (count, words), such as (88, 'counties'), (64, 'parishes'),
    (133, 'counties and independent cities'), (24, 'counties, counting Baltimore City'). None for D.C."""
    if code == 'DC':
        return None
    n = len(contacts)
    if code == 'AK':
        return n, 'boroughs and census areas'
    if code == 'LA':
        return n, 'parishes'
    cities = [c['county'] for c in contacts if c.get('county_type') == 'independent_city']
    if len(cities) == 1:
        return n, 'counties, counting ' + cities[0]
    if cities:
        return n, 'counties and independent cities'
    return n, 'counties'


def glance(state, contacts):
    code, name = state['code'], state['name']
    low = code.lower()
    tiles = []
    areas = area_words(code, contacts)
    if areas:
        num, words = areas
        tiles.append(f'<li>{icon("pin")}<a href="counties/{low}/"><span class="vz-stat-n">{num}</span> '
                     f'<strong>{escape(words)}</strong></a><small>One page each, with the local veterans office and its phone</small></li>')
    else:
        tiles.append(f'<li>{icon("pin")}<a href="counties/{low}/"><strong>The District’s veterans office</strong></a>'
                     '<small>Its own page, with its phone and next steps</small></li>')
    counts = va_counts(code)
    for kind, one, many, ic in VA_KINDS:
        n = counts.get(kind)
        if n:
            tiles.append(f'<li>{icon(ic)}<a href="va-locations/{low}/#{kind}"><span class="vz-stat-n">{n}</span> '
                         f'<strong>{"" if kind == "cemetery" else "VA "}{escape(one if n == 1 else many)}</strong></a></li>')
    note = ('VA counts come from VA’s own facility data; each tile opens the list with phones and hours.'
            if counts else 'The county tile opens the list of local veterans offices.')
    return (f'<figure class="vz vz-glance vz-local" aria-labelledby="glance-cap">'
            f'<figcaption id="glance-cap"><strong>{escape(name)} at a glance</strong></figcaption>'
            f'<div class="vz-glance-row"><div class="vz-loc-wrap">{locator(code, name, "glance-map")}'
            f'<p class="vz-loc-key"><span class="vz-loc-swatch" aria-hidden="true"></span>{escape(name)} is the dark square with a ring.</p></div>'
            f'<ul class="vz-grid vz-stats">{"".join(tiles)}</ul></div><p class="vz-note">{note}</p></figure>')


def route(when_icon, when, who_icon, who_html, href=None):
    who = f'{icon(who_icon)}<span>{who_html}</span>'
    who = f'<a class="vz-who" href="{escape(href)}">{who}</a>' if href else f'<span class="vz-who">{who}</span>'
    return (f'<li><span class="vz-when">{icon(when_icon)}<span>{escape(when)}</span></span>'
            f'<span class="vz-arrow">{icon("arrow-right")}<span class="vz-vh">, first contact: </span></span>{who}</li>')


def who_first(state):
    code, name = state['code'], state['name']
    low = code.lower()
    rec = aps_data()['states'][code]
    office = {'DC': 'The District’s veterans office', 'LA': 'Your parish veterans office'}.get(code, 'Your local veterans office')
    rows = [
        route('lifebuoy', 'A crisis, or thoughts of suicide', 'phone', 'Call 988 (veterans press 1)', 'tel:988'),
        route('siren', 'Someone is in immediate danger', 'phone', 'Call 911', 'tel:911'),
        route('home', 'Losing housing, or already homeless', 'phone', 'VA housing line, 877-424-3838, any hour', 'tel:8774243838'),
    ]
    if rec['phones']:
        num = rec['phones'][0]['number']
        rows.append(route('alert', 'Abuse, neglect or money being taken', 'shield',
                          f'{escape(name)} Adult Protective Services, {escape(num)}', 'tel:' + num.replace('-', '')))
    else:
        rows.append(route('alert', 'Abuse, neglect or money being taken', 'shield',
                          f'{escape(name)} Adult Protective Services: how to report', f'elder-abuse.html#aps-{low}'))
    rows.append(route('doc', 'VA claims, pension or survivor benefits', 'user', escape(office) + ', free', '#county-start'))
    if va_counts(code):
        rows.append(route('medical', 'VA health care or counseling', 'building',
                          f'A VA medical center, clinic or Vet Center in {escape(name)}', f'va-locations/{low}/'))
    rows.append(route('heart', 'Help at home, meals or caregiving; no military service needed', 'people',
                      'Senior and disability support', '?view=seniors#directory'))
    return ('<figure class="vz vz-call vz-local" aria-labelledby="call-cap"><figcaption id="call-cap"><strong>Who to call first</strong>'
            'Find the line that fits, then use the contact beside it. Each one is a phone number or a part of this guide.</figcaption>'
            f'<ul class="vz-routes">{"".join(rows)}</ul></figure>')


def add(result, editions):
    """editions: (state, records, contacts) for every state, Ohio first."""
    out = {}
    for state, _records, contacts in editions:
        page = state['page']
        html = result[page]
        for anchor in ('<p id="county-pages-link">', '<section id="helper-guide"', '</head>'):
            assert html.count(anchor) == 1, f'{page}: {anchor}'
        html = html.replace('<p id="county-pages-link">', glance(state, contacts) + '<p id="county-pages-link">', 1)
        html = html.replace('<section id="helper-guide"', who_first(state) + '<section id="helper-guide"', 1)
        # Shown only while the page shows this state; the picker can swap in another state without a new page.
        hide = f'<style>html[data-edition]:not([data-edition="{state["code"]}"]) .vz-local{{display:none}}</style>'
        if stylesheet() not in html:
            html = html.replace('</head>', stylesheet() + hide + '</head>', 1)
        else:
            html = html.replace('</head>', hide + '</head>', 1)
        out[page] = html
    return out


def tile_nav(states, href, label, extra=None, up='../'):
    """Every state as a link on the equal-square tile map. href(state) gives its link; extra(state) optional small text."""
    items = []
    for s in sorted(states, key=lambda s: (TILES[s['code']][1], TILES[s['code']][0])):
        col, row = TILES[s['code']]
        more = extra(s) if extra else ''
        more = f'<small aria-hidden="true">{escape(more)}</small>' if more else ''
        items.append(f'<li style="grid-column:{col + 1};grid-row:{row + 1}"><a href="{escape(href(s))}">'
                     f'<abbr title="{escape(s["name"])}" aria-hidden="true">{s["code"]}</abbr>{more}'
                     f'<span class="vz-vh">{escape(s["name"])}</span></a></li>')
    return (f'<figure class="vz vz-tilemap" aria-labelledby="tilemap-cap"><figcaption id="tilemap-cap"><strong>{escape(label)}</strong>'
            'Each square is a state, placed roughly where it sits on a map. The full list follows.</figcaption>'
            f'<ul class="vz-tiles">{"".join(items)}</ul></figure>')


def add_hubs(result, states):
    """The tile map at the top of the counties/ and va-locations/ hub pages."""
    out = {}
    hub = 'counties/index.html'
    if hub in result:
        html = result[hub]
        assert html.count('<main id="main">') == 1
        nav = tile_nav(states, lambda s: s['code'].lower() + '/', 'Choose a state on the map')
        html = html.replace('<main id="main">', '<main id="main">' + nav, 1)
        out[hub] = html.replace('</head>', stylesheet('../') + '</head>', 1) if stylesheet('../') not in html else html
    hub = 'va-locations/index.html'
    if hub in result:
        html = result[hub]
        totals = {s['code']: sum(va_counts(s['code']).values()) for s in states}
        have = [s for s in states if totals[s['code']]]
        nav = tile_nav(have, lambda s: s['code'].lower() + '/', 'Choose a state on the map',
                       extra=lambda s: str(totals[s['code']]))
        nav = nav.replace('The full list follows.</figcaption>',
                          'The number under each state is its count of VA locations. The full list follows.</figcaption>', 1)
        html = html.replace('<main id="main">', '<main id="main">' + nav, 1)
        out[hub] = html.replace('</head>', stylesheet('../') + '</head>', 1) if stylesheet('../') not in html else html
    return out
