#!/usr/bin/env python3
"""Programs, grants, scholarships, events and benefits open to veterans: one page per state, local ones first.

Built from data/opportunities/<st>.json (a state's own programs and its county and regional ones) and
data/opportunities/national.json (open to veterans in every state, or worth the trip). docs/OPPORTUNITIES.md
describes the format, the evidence rule and how capacity and odds are shown.

Only listings read on the program's own page (evidence A or B) and not marked closed are published. How many a
program serves, how many apply, its places, its waitlist and the odds appear only where the program publishes them.

Outputs:
  opportunities/index.html          the states with a page, the nationwide list and how the figures are counted
  opportunities/<st>/index.html     every program open to veterans in one state: pick a county to put local ones first
  opportunities/<st>/<slug>.html    one program
  opportunities/us/index.html       open in every state, and worth the trip
  opportunities/us/<slug>.html      one nationwide or travel program
  assets/opportunities.js           the county and category picker on those pages
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from build_county_pages import BASE_URL, STYLE, e, label, slug, tel, urgent, when
from visuals import ICONS, count_bars, icon, stylesheet

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'opportunities'
DATA = ROOT / 'data' / 'opportunities'
SCRIPT = 'assets/opportunities.js'

# (key, heading, short label, icon)
CATS = [
    ('benefits', 'State and federal benefits', 'Benefits', 'clipboard'),
    ('money', 'Grants and emergency money', 'Grants and money', 'dollar'),
    ('education', 'Scholarships and school', 'Scholarships and school', 'book'),
    ('housing', 'Housing and home help', 'Housing', 'home'),
    ('jobs', 'Jobs and training', 'Jobs and training', 'building'),
    ('business', 'Starting or growing a business', 'Business', 'wallet'),
    ('health', 'Health, wellness and service dogs', 'Health and wellness', 'medical'),
    ('recreation', 'Outdoors, sports and recreation', 'Outdoors and sports', 'sprout'),
    ('tickets', 'Free tickets and discounts', 'Tickets and discounts', 'card'),
    ('events', 'Events, stand downs and Honor Flights', 'Events', 'calendar'),
    ('family', 'Families, caregivers and survivors', 'Families and survivors', 'people'),
    ('volunteer', 'Ways to serve and volunteer', 'Volunteer', 'user-plus'),
]
CAT = {k: (h, s, i) for k, h, s, i in CATS}
assert all(i in ICONS for _, _, _, i in CATS)

# Ohio's five regions, used only to put programs near a county ahead of the rest. Every county is in exactly one.
REGIONS = {
    'OH': {
        'Northwest': 'Allen Auglaize Defiance Fulton Hancock Hardin Henry Lucas Mercer Ottawa Paulding Putnam Sandusky '
                     'Seneca Van_Wert Williams Wood Wyandot',
        'Northeast': 'Ashland Ashtabula Carroll Columbiana Cuyahoga Erie Geauga Holmes Huron Lake Lorain Mahoning Medina '
                     'Portage Richland Stark Summit Trumbull Tuscarawas Wayne',
        'Central': 'Crawford Delaware Fairfield Fayette Franklin Knox Licking Madison Marion Morrow Pickaway Union',
        'Southwest': 'Adams Brown Butler Champaign Clark Clermont Clinton Darke Greene Hamilton Highland Logan Miami '
                     'Montgomery Preble Shelby Warren',
        'Southeast': 'Athens Belmont Coshocton Gallia Guernsey Harrison Hocking Jackson Jefferson Lawrence Meigs Monroe '
                     'Morgan Muskingum Noble Perry Pike Ross Scioto Vinton Washington',
    },
}

EXTRA_STYLE = (
    '.opp dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;margin:12px 0}'
    '.opp dt{font-weight:650;color:var(--navy)}.opp dd{margin:0}'
    '@media (max-width:560px){.opp dl{grid-template-columns:1fr}.opp dd{margin-bottom:8px}}'
    '.cap{background:#eaf1ec;border-left:4px solid var(--green);border-radius:6px;padding:10px 14px;margin:12px 0}'
    '.cap ul{margin:4px 0 0;padding-left:20px}.cap.none{background:#f1f1ec;border-left-color:#6f7a74}'
    '.opp .meta .vi{vertical-align:-6px;margin-right:4px}'
    'form.opp-filter{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:end;background:#fff;border:1px solid var(--line);'
    'border-radius:9px;padding:16px 18px;margin:16px 0}'
    'form.opp-filter label{display:flex;flex-direction:column;font-weight:650;color:var(--navy);gap:4px}'
    'form.opp-filter select{font:inherit;min-height:44px;padding:6px 10px;border:1px solid #8a9690;border-radius:6px;background:#fff}'
    '#opp-status{flex-basis:100%;margin:0;font-size:15px;color:#3c4a42}'
    'ul.opp-rows{padding-left:20px}ul.opp-rows li{margin:6px 0}'
    'details.opp-cat{background:#fff;border:1px solid var(--line);border-radius:9px;padding:10px 16px;margin:10px 0}'
    'details.opp-cat summary{cursor:pointer;font-weight:650;color:var(--navy);min-height:32px}'
    'details.opp-cat summary .vi{vertical-align:-6px;margin-right:6px}'
    '.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}'
    '[hidden]{display:none!important}'
)


def regions_of(code):
    out = {}
    for region, names in REGIONS.get(code, {}).items():
        for n in names.split():
            out[n.replace('_', ' ')] = region
    return out


def places(r):
    """The counties a local program names, or where a travel program is held."""
    return list(r.get('counties') or []) + list((r.get('host') or {}).get('counties', []))


def short_id(r):
    return re.sub(r'^[a-z]{2}-', '', r['id'])


def host(url):
    return (urlparse(url or '').netloc or '').removeprefix('www.')


def published(r):
    """Read on the program's own page (A or B), and not closed. Search excerpts (C) and ad leads (E) wait."""
    return r.get('evidence') in ('A', 'B') and r.get('status') != 'closed'


def load():
    """{'national': [...], 'OH': [...], ...}, published listings only, sorted by name."""
    out = {}
    if not DATA.exists():
        return out
    for path in sorted(DATA.glob('*.json')):
        data = json.loads(path.read_text())
        key = 'national' if path.stem == 'national' else data['state']
        out[key] = sorted((r for r in data['listings'] if published(r)), key=lambda r: r['name'].lower())
    return out


def reference_date(groups):
    """The newest date any listing was checked: 'coming up' is counted from here, so a rebuild gives the same page."""
    return max((r['checked_on'] for rows in groups.values() for r in rows), default='')


def where(r, sname=''):
    scope = r['scope']
    if scope == 'state':
        return f'Anywhere in {sname}' if sname else 'Statewide'
    if scope in ('county', 'region'):
        if r.get('counties'):
            cs = r['counties']
            return (', '.join(cs[:-1]) + ' and ' + cs[-1] if len(cs) > 1 else cs[0]) + (' counties' if len(cs) > 1 else ' County') \
                if len(cs) <= 4 else f'{len(cs)} {sname} counties'
        if r.get('regions'):
            return ' and '.join(r['regions']) + (f' {sname}' if sname else '')
        return r.get('location') or 'Local'
    if scope == 'national':
        return 'Open in every state'
    return 'Worth the trip: ' + (r.get('location') or 'location varies')


def capacity(r):
    c = r.get('capacity') or {}
    rows = [(k, c.get(f)) for k, f in (('Serves', 'served'), ('Applicants', 'applicants'), ('Places', 'slots'),
                                        ('Waitlist or wait', 'waitlist')) if c.get(f)]
    odds = r.get('odds')
    if not rows and not odds:
        return ('<p class="cap none"><strong>How many it serves and the odds of getting in:</strong> '
                'not published by the program.</p>')
    items = ''.join(f'<li><strong>{e(k)}:</strong> {e(v)}</li>' for k, v in rows)
    if odds:
        note = ' (our arithmetic from the program’s own figures)' if odds.get('basis') == 'computed' else ''
        items += f'<li><strong>Odds:</strong> {e(odds["text"])}{e(note)}</li>'
    else:
        items += '<li><strong>Odds:</strong> not published. The program does not say how many apply.</li>'
    src = ''
    if c.get('figure_source'):
        src = (f'<p class="small" style="margin:6px 0 0">Figures from <a href="{e(c["figure_source"])}" rel="noopener">'
               f'{e(host(c["figure_source"]))}</a>' + (f', {e(c["figure_date"])}' if c.get('figure_date') else '') + '.</p>')
    return f'<div class="cap"><p style="margin:0"><strong>How many it serves and the odds</strong></p><ul>{items}</ul>{src}</div>'


def deadline_html(r):
    text = r.get('deadline') or ''
    if r.get('deadline_date') and when(r['deadline_date']) not in text:
        text = (text + ' ' if text else '') + f'({when(r["deadline_date"])})'
    return e(text)


def card(r, up, sname='', href=None, regions=None, heading='h3'):
    """One program. data-* attributes let assets/opportunities.js move and filter it; the page reads fine without."""
    cat_heading, cat_short, cat_icon = CAT[r['category']]
    counties = [slug(c) for c in r.get('counties') or []]
    counties += [slug(c) for c in (r.get('host') or {}).get('counties', [])]
    regs = set(slug(x) for x in r.get('regions') or [])
    regs |= {slug(regions[c]) for c in (r.get('counties') or []) + (r.get('host') or {}).get('counties', []) if regions and c in regions}
    attrs = (f' data-opp data-cat="{e(r["category"])}" data-scope="{e(r["scope"])}"'
             f' data-counties="|{e("|".join(counties))}|" data-regions="|{e("|".join(sorted(regs)))}|"')
    parts = [f'<article class="office opp" id="{e(short_id(r))}"{attrs}>']
    if heading:
        name = f'<a href="{e(href)}">{e(r["name"])}</a>' if href else e(r['name'])
        parts.append(f'<{heading} style="margin:0 0 4px;font-size:20px">{name}</{heading}>')
    parts.append(f'<p class="meta" style="margin:0">{icon(cat_icon, up)}{e(cat_short)} · {e(r["organization"])} · '
                 f'{e(where(r, sname) if r["scope"] != "travel" or not r.get("host") else (r.get("location") or ""))}</p>')
    parts.append(f'<p>{e(r["summary"])}</p><dl>')
    for k, v in (('Who can apply', e(r.get('eligibility'))), ('How to apply', e(r.get('how_to_apply'))),
                 ('Deadline or date', deadline_html(r)), ('Where', e(r.get('location'))), ('Travel', e(r.get('travel'))),
                 ('Cost', e(r.get('cost')))):
        if v:
            parts.append(f'<dt>{k}</dt><dd>{v}</dd>')
    if r.get('phone'):
        parts.append(f'<dt>Phone</dt><dd>{tel(r["phone"])}</dd>')
    parts.append('</dl>')
    if r.get('apply_url'):
        parts.append(f'<p><a class="button" href="{e(r["apply_url"])}" rel="noopener">Apply or learn more'
                     f'<span class="sr-only"> about {e(r["name"])}</span></a> <span class="small">on {e(host(r["apply_url"]))}</span></p>')
    parts.append(capacity(r))
    if (r.get('found_via') or '').startswith('meta_ad_library'):
        parts.append('<p class="small">First spotted in a public Facebook ad; the details come from the program’s own site.</p>')
    parts.append(f'<p class="meta">Source: <a href="{e(r["source_url"])}" rel="noopener">{e(r["source_title"])}</a>. '
                 f'Checked {when(r["checked_on"])}. Programs change; confirm on their site before you apply.</p></article>')
    return ''.join(parts)


def row(r, href, extra=''):
    dl = f' · <span class="small">{deadline_html(r)}</span>' if r.get('deadline_date') else ''
    return (f'<li data-opp data-cat="{e(r["category"])}"><a href="{e(href)}">{e(r["name"])}</a>'
            f' <span class="small">· {e(r["organization"])}{e(extra)}</span>{dl}</li>')


def page(title, description, path, crumbs, hero, body, depth, script=False):
    up = '../' * depth
    canonical = BASE_URL + path.replace('index.html', '')
    trail = ' › '.join(f'<a href="{e(href)}">{e(text)}</a>' if href else e(text) for text, href in crumbs)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{e(title)}</title>\n<meta name="description" content="{e(description)}">\n'
            f'<link rel="canonical" href="{e(canonical)}">\n'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}">'
            f'<meta property="og:image" content="{BASE_URL}assets/vhg-logo.png">\n'
            f'<link rel="icon" href="{up}favicon.ico"><style>{STYLE}h3{{color:var(--navy)}}{EXTRA_STYLE}</style>'
            + (stylesheet(up) if 'class="vi"' in body else '') + '</head>\n'
            f'<body><header><nav aria-label="Breadcrumb" class="small">{trail}</nav>{hero}</header>\n'
            f'<main id="main">{body}</main>\n'
            '<footer><p>Free from <a href="https://www.vethomeguard.org/about.html">Veteran Home Guardians</a>, an independent '
            '501(c)(3) nonprofit (EIN 33-4637180) that visits isolated veterans and publishes free guides. It is not part of the '
            'U.S. Department of Veterans Affairs and is not paid by any program listed here. Each listing comes from the '
            'program’s own page, named with the date it was read. Report a change or a program we missed: '
            '<a href="mailto:travis@vethomeguard.org?subject=Veteran%20program%20correction">travis@vethomeguard.org</a>.</p>'
            f'<p><a href="{up}">Veteran Resource Guide</a> · <a href="{up}{FOLDER}/">Veteran programs by state</a> · '
            f'<a href="{up}{FOLDER}/us/">Open in every state</a> · <a href="{up}counties/">County veterans offices</a> · '
            f'<a href="{up}privacy.html">Privacy</a></p></footer>\n'
            + (f'<script defer src="{up}{SCRIPT}"></script>' if script else '')
            + f'<script defer src="{up}assets/analytics.js"></script></body></html>\n')


def coming_up(rows, ref, href_of, limit=8):
    soon = sorted((r for r in rows if r.get('deadline_date') and r['deadline_date'] >= ref), key=lambda r: (r['deadline_date'], r['name']))
    if not soon:
        return ''
    items = ''.join(f'<li><time datetime="{e(r["deadline_date"])}">{when(r["deadline_date"])}</time>: '
                    f'<a href="{e(href_of(r))}">{e(r["name"])}</a> <span class="small">({e(r.get("deadline") or "")})</span></li>'
                    for r in soon[:limit])
    return ('<section class="notice" aria-labelledby="soon"><h2 id="soon" style="margin-top:0">Deadlines and dates coming up</h2>'
            f'<ul>{items}</ul><p class="small" style="margin:0">Dates as each program published them, read {when(ref)}.</p></section>')


def filter_form(cat_counts, counties=None, sname=''):
    """Hidden until assets/opportunities.js runs, so a reader without scripts never sees controls that do nothing."""
    parts = [f'<form class="opp-filter" id="opp-filter" data-state="{e(sname)}" hidden role="search" aria-label="Filter programs">']
    if counties:
        opts = ''.join(f'<option value="{e(slug(c))}" data-region="{e(slug(reg))}" data-region-name="{e(reg)}">{e(c)}</option>'
                       for c, reg in counties)
        parts.append(f'<label for="opp-county">Your county<select id="opp-county" name="county"><option value="">Choose a county</option>{opts}</select></label>')
    opts = ''.join(f'<option value="{k}">{e(CAT[k][1])} ({n})</option>' for k, _, _, _ in CATS if (n := cat_counts.get(k)))
    parts.append(f'<label for="opp-cat">Kind of help<select id="opp-cat" name="cat"><option value="">All kinds</option>{opts}</select></label>')
    parts.append('<p id="opp-status" role="status" aria-live="polite"></p></form>')
    return ''.join(parts)


def counts(rows):
    c = {}
    for r in rows:
        c[r['category']] = c.get(r['category'], 0) + 1
    return c


def chart(c, title, up):
    rows = [(CAT[k][1], c[k], f'?cat={k}#opp-list', CAT[k][2]) for k, _, _, _ in CATS if c.get(k)]
    return count_bars(rows, 'opp-kinds', title, 'Programs', up) if rows else ''


def national_rows(rows, href_of, heading_id, open_first=False):
    parts = []
    for k, heading, short, ic in CATS:
        items = [r for r in rows if r['category'] == k]
        if items:
            parts.append(f'<details class="opp-cat" data-group><summary>{icon(ic, "../../")}{e(heading)} '
                         f'<span class="small">({len(items)})</span></summary><ul class="opp-rows">'
                         + ''.join(row(r, href_of(r)) for r in items) + '</ul></details>')
    return ''.join(parts)


def section(tier, heading, intro, inner, hidden=False):
    return (f'<section id="tier-{tier}" data-tier="{tier}" aria-labelledby="tier-{tier}-h"{" hidden" if hidden else ""}>'
            f'<h2 id="tier-{tier}-h">{heading}</h2>' + (f'<p data-intro>{intro}</p>' if intro else '')
            + f'<div data-list>{inner}</div></section>')


def state_page(state, rows, national, ref, offices):
    code, sname, low = state['code'], state['name'], state['code'].lower()
    regions = regions_of(code)
    local = [r for r in rows if r['scope'] in ('county', 'region')]
    statewide = [r for r in rows if r['scope'] == 'state']
    hosted = [r for r in national if (r.get('host') or {}).get('state') == code]
    order = list(REGIONS.get(code, {}))

    def region_rank(r):
        names = [regions.get(c) for c in places(r)] + list(r.get('regions') or [])
        return min((order.index(n) for n in names if n in order), default=len(order))
    local_all = sorted(local + hosted, key=lambda r: (region_rank(r), r['name'].lower()))
    nat = [r for r in national if r['scope'] == 'national']
    trav = [r for r in national if r['scope'] == 'travel' and r not in hosted]
    own = statewide + local_all
    total = len(own) + len(nat) + len(trav)
    href_own = lambda r: f'{short_id(r)}.html' if r in rows else f'../us/{short_id(r)}.html'
    href_us = lambda r: f'../us/{short_id(r)}.html'
    up = '../../'
    county_opts = None
    if regions:
        county_opts = sorted((r['county'], regions[r['county']]) for r in offices)
        assert len(county_opts) == len(regions), f'{code}: every county needs a region'
    c_all = counts(own + nat + trav)
    body = [f'<p>{total} programs, grants, scholarships, events and benefits open to {e(sname)} veterans and families: '
            f'{len(statewide)} statewide, '
            + (f'{len(local_all)} local or regional, ' if local_all else '')
            + f'{len(nat)} open in every state and {len(trav)} worth the trip. '
            + ('Choose your county to put the ones near you first. ' if county_opts else '')
            + 'How many each program serves and the odds of getting in are shown wherever the program publishes them.</p>']
    body.append(filter_form(c_all, county_opts, sname))
    body.append(chart(c_all, f'Programs open to {sname} veterans, by kind of help', up))
    body.append(coming_up(own + nat + trav, ref, href_own))
    body.append('<div id="opp-list">')
    body.append(section('yours', 'Serves your county', '', '', hidden=True))
    body.append(section('nearby', 'In your part of the state', 'Programs in nearby counties or serving your region.', '', hidden=True))
    body.append(section('state', f'Anywhere in {e(sname)}', f'Open to veterans across {e(sname)}.',
                        ''.join(card(r, up, sname, href_own(r), regions) for r in statewide)))
    if local_all:
        body.append(section('local', 'County and regional programs',
                            'Sorted by region' + (' (Northwest, Northeast, Central, Southwest, Southeast)' if regions else '')
                            + '. Many are open to any veteran who can get there.',
                            ''.join(card(r, up, sname, href_own(r), regions) for r in local_all)))
    body.append(section('national', 'Open to veterans in every state',
                        f'Apply from anywhere. Each links to its full listing. <a href="../us/">See them all on one page</a>.',
                        national_rows(nat, href_us, 'national')))
    body.append(section('travel', 'Worth the trip',
                        'Retreats, games and programs held in another state. Some pay travel; each listing says what is covered.',
                        '<ul class="opp-rows">' + ''.join(row(r, href_us(r), ' · ' + (r.get('location') or '')) for r in trav) + '</ul>'))
    body.append('</div>')
    body.append(urgent(sname))
    body.append('<h2>How these are checked</h2><p>Every listing links to the program’s own page and shows the date we read it. '
                'Figures for how many a program serves, how many apply, its places and its waitlist are shown only when the '
                'program publishes them, with the year they cover. We never estimate odds. '
                f'<a href="../#how">How we count</a>.</p>')
    body.append(f'<p><a class="button" href="../../{e(state["page"] if not state.get("base") else "")}">The full {e(sname)} veteran guide</a>'
                + (f' <a href="../../counties/{low}/">Your county veterans office</a>' if offices else '') + '</p>')
    hero = (f'<small>Veteran Resource Guide · {e(sname)}</small><h1>Veteran programs, grants and events in {e(sname)}</h1>'
            f'<p>Scholarships, grants, free tickets, retreats, Honor Flights, stand downs and state benefits, '
            f'local ones first, with who can apply, deadlines and published odds.</p>')
    rel = f'{FOLDER}/{low}/index.html'
    html = page(f'Veteran programs, grants and events in {sname} | Veteran Resource Guide',
                f'{total} programs, grants, scholarships, events and benefits open to {sname} veterans, local ones first, '
                'with who can apply, how to apply, deadlines, and how many each serves where published.',
                rel, [('Veteran Resource Guide', '../../'), ('Veteran programs', '../'), (sname, None)], hero, ''.join(body), 2, script=True)
    return rel, html, total, len(own)


def detail_page(r, state, siblings, folder):
    sname = state['name'] if state else ''
    cat_heading = CAT[r['category']][0]
    up = '../../'
    regions = regions_of(state['code']) if state else {}
    body = [card(r, up, sname, None, regions, heading=None)]
    like = [x for x in siblings if x['category'] == r['category'] and x['id'] != r['id']][:6]
    if like:
        body.append(f'<h2>More {e(cat_heading.lower())}</h2><ul class="opp-rows">'
                    + ''.join(f'<li><a href="{e(short_id(x))}.html">{e(x["name"])}</a> <span class="small">· {e(where(x, sname))}</span></li>' for x in like)
                    + '</ul>')
    if state:
        body.append(f'<p><a class="button" href="./">Every program open to {e(sname)} veterans</a></p>')
    else:
        body.append('<p><a class="button" href="./">Every program open in every state</a> '
                    '<a href="../">Find your state’s programs</a></p>')
    body.append(urgent(sname))
    place = sname or 'every state'
    hero = (f'<small>Veteran Resource Guide · {e(sname or "Nationwide")}</small><h1>{e(r["name"])}</h1>'
            f'<p>{e(r["organization"])} · {e(where(r, sname))}</p>')
    rel = f'{FOLDER}/{folder}/{short_id(r)}.html'
    desc = r['summary'] if len(r['summary']) <= 155 else r['summary'][:152].rsplit(' ', 1)[0] + '…'
    crumbs = [('Veteran Resource Guide', '../../'), ('Veteran programs', '../'),
              (sname or 'Open in every state', './'), (r['name'], None)]
    return rel, page(f'{r["name"]} | Veteran programs in {place} | Veteran Resource Guide', desc, rel, crumbs, hero, ''.join(body), 2)


def us_page(national, ref):
    nat = [r for r in national if r['scope'] == 'national']
    trav = [r for r in national if r['scope'] == 'travel']
    up = '../../'
    href = lambda r: f'{short_id(r)}.html'
    c_all = counts(national)
    body = [f'<p>{len(nat)} programs any veteran can apply to from any state, and {len(trav)} retreats, games and programs '
            'worth the trip. Your own state’s programs are on its page, local ones first.</p>']
    body.append(filter_form(c_all))
    body.append(chart(c_all, 'Programs open in every state, by kind of help', up))
    body.append(coming_up(national, ref, href))
    body.append('<div id="opp-list">')
    for k, heading, short, ic in CATS:
        items = [r for r in nat if r['category'] == k]
        if items:
            body.append(section(f'cat-{k}', e(heading), '', ''.join(card(r, up, '', href(r)) for r in items)))
    body.append(section('travel', 'Worth the trip', 'Held in one place. Each listing says what travel costs are covered, if any.',
                        ''.join(card(r, up, '', href(r)) for r in trav)))
    body.append('</div>')
    body.append(urgent(''))
    hero = ('<small>Veteran Resource Guide · Nationwide</small><h1>Veteran programs open in every state</h1>'
            '<p>Scholarships, grants, service dogs, housing, retreats, training and events any veteran can apply for, '
            'with who can apply, deadlines and published odds.</p>')
    rel = f'{FOLDER}/us/index.html'
    return rel, page('Veteran grants, scholarships and programs open in every state | Veteran Resource Guide',
                     f'{len(national)} grants, scholarships, retreats, service dog programs, training and events open to veterans '
                     'nationwide, with eligibility, deadlines and how many each serves where published.',
                     rel, [('Veteran Resource Guide', '../../'), ('Veteran programs', '../'), ('Open in every state', None)],
                     hero, ''.join(body), 2, script=True)


def hub(state_rows, n_national, ref):
    up = '../'
    lis = ''.join(f'<li><a href="{low}/">{e(name)}</a> <span class="small">({n} programs, {own} of them in {e(name)})</span></li>'
                  for name, low, n, own in state_rows)
    body = ('<p>One list per state of the programs, grants, scholarships, events and benefits open to veterans and their '
            'families, local ones first. Each listing says who can apply, how and where to apply, the deadline, '
            'how far you would travel, and how many it serves when the program publishes that.</p>'
            f'<h2>States with a page</h2><ul class="cols">{lis}</ul>'
            f'<p><a class="button" href="us/">Open to veterans in every state ({n_national})</a></p>'
            '<p>Your state not listed yet? Everything on the nationwide page is open to you, and your state’s full guide '
            'lists its veterans offices and benefits. More states are being added, starting with those that publish '
            'their programs most completely.</p>'
            '<h2 id="how">How we count</h2><ul>'
            '<li>Every listing comes from the program’s own page, linked, with the date we read it.</li>'
            '<li>How many a program serves, how many apply, its places and its waitlist appear only when the program '
            'publishes them, with the year they cover. When a figure is not published, the listing says so.</li>'
            '<li>Odds of getting in are the program’s own figure, or simple arithmetic from its published applicants and '
            'awards, marked as ours. We never estimate.</li>'
            '<li>Programs we found only in a search result or a Facebook ad are held back until we read the program’s own '
            'site.</li><li>Closed programs are taken off. Programs change; confirm on their site before you apply.</li></ul>'
            f'<p class="small">Last checked {when(ref)}.</p>' + urgent(''))
    hero = ('<small>Veteran Resource Guide</small><h1>Veteran programs, grants and events by state</h1>'
            '<p>Everything open to veterans in one place: local first, then statewide, nationwide and worth the trip.</p>')
    rel = f'{FOLDER}/index.html'
    return rel, page('Veteran programs, grants, scholarships and events by state | Veteran Resource Guide',
                     'Find programs, grants, scholarships, events and benefits open to veterans in your state, local ones first, '
                     'with deadlines and how many each serves where published.',
                     rel, [('Veteran Resource Guide', '../'), ('Veteran programs', None)], hero, body, 1)


def county_block(county, code, sname, local, statewide_n, total):
    """For counties/<st>/<county>-county.html: the local programs that serve this county or its region, and a link
    to the state list with this county chosen."""
    regions = regions_of(code)
    reg = regions.get(county)
    mine = [r for r in local if county in (r.get('counties') or []) or county in (r.get('host') or {}).get('counties', [])]
    near = [r for r in local if r not in mine and (reg in (r.get('regions') or [])
                                                     or any(regions.get(c) == reg for c in (r.get('counties') or []) + (r.get('host') or {}).get('counties', [])))]
    href = lambda r: f'../../{FOLDER}/{code.lower()}/{short_id(r)}.html' if r['id'][:2] != 'us' else f'../../{FOLDER}/us/{short_id(r)}.html'
    li = lambda r: (f'<li><a href="{e(href(r))}">{e(r["name"])}</a> <span class="small">· {e(where(r, sname))}</span></li>')
    parts = [f'<section aria-labelledby="opps"><h2 id="opps">Programs, grants and events for {e(county)} County veterans</h2>']
    if mine:
        parts.append(f'<p>These name {e(county)} County:</p><ul class="opp-rows">{"".join(li(r) for r in mine)}</ul>')
    if near:
        parts.append(f'<p>Nearby in {e(reg)} {e(sname)}:</p><ul class="opp-rows">{"".join(li(r) for r in near[:8])}</ul>')
    if not mine and not near:
        parts.append(f'<p>No local program in our list names {e(county)} County yet. {statewide_n} statewide programs and '
                     'many nationwide ones are open to you.</p>')
    parts.append(f'<p><a class="button" href="../../{FOLDER}/{code.lower()}/?county={e(slug(county))}#opp-list">'
                 f'All {total} programs open to {e(county)} County veterans, local first</a></p></section>')
    return ''.join(parts)


def outputs(root=ROOT):
    """(pages, sitemap urls, {state code or '*': link for the state guide}, {county page path: block})"""
    states = {s['code']: s for s in json.loads((root / 'states/registry.json').read_text())}
    groups = load()
    out, urls, links, county = {}, [], {}, {}
    national = groups.get('national', [])
    if not groups:
        return out, urls, links, county
    ref = reference_date(groups)
    out[SCRIPT] = (ROOT / 'scripts' / 'opportunities.js').read_text()
    state_rows = []
    for code in sorted(k for k in groups if k != 'national'):
        state = states[code]
        rows = groups[code]
        offices = json.loads((root / state['offices']).read_text()) if state.get('offices') else []
        rel, html, total, own = state_page(state, rows, national, ref, offices)
        out[rel] = html
        low = code.lower()
        urls.append(BASE_URL + f'{FOLDER}/{low}/')
        for r in rows:
            p, h = detail_page(r, state, rows, low)
            out[p] = h
            urls.append(BASE_URL + p)
        state_rows.append((state['name'], low, total, own))
        links[code] = (f'<p id="opportunities-link"><a href="{FOLDER}/{low}/"><strong>{e(state["name"])} veteran programs, grants and events</strong></a>'
                       f' · {total} open to {e(state["name"])} veterans, local ones first, with deadlines and published odds.</p>')
        if code in REGIONS:
            local = [r for r in rows if r['scope'] in ('county', 'region')] + [r for r in national if (r.get('host') or {}).get('state') == code]
            statewide_n = sum(1 for r in rows if r['scope'] == 'state')
            for r in offices:
                path = f'counties/{low}/{slug(label(r))}.html'
                county[path] = county_block(r['county'], code, state['name'], local, statewide_n, total)
    if national:
        rel, html = us_page(national, ref)
        out[rel] = html
        urls.append(BASE_URL + f'{FOLDER}/us/')
        for r in national:
            p, h = detail_page(r, None, national, 'us')
            out[p] = h
            urls.append(BASE_URL + p)
        links['*'] = (f'<p id="opportunities-link"><a href="{FOLDER}/us/"><strong>Veteran grants, scholarships and programs open in every state</strong></a>'
                      f' · {len(national)} programs, with who can apply, deadlines and published odds.</p>')
    rel, html = hub(state_rows, len(national), ref)
    out[rel] = html
    urls.insert(0, BASE_URL + f'{FOLDER}/')
    return out, urls, links, county


if __name__ == '__main__':
    pages, urls, links, county = outputs()
    print(len(pages), 'pages,', len(urls), 'sitemap URLs,', len(links), 'state links,', len(county), 'county blocks')
