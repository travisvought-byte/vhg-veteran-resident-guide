"""Build FindBingo.org (findbingo-site/): bingo near you, state by state.

index.html is the whole page (markup, styles and script). The build also writes it to
bingo-site/findbingo/, which the Ohio-Bingo repository mirrors and Cloudflare serves at
www.findbingo.org. It loads data.json and zips.json from beside itself, then from the guide's GitHub
Pages site. The Ohio finder is built by bingo_site.py into bingo-site/findbingo/ohio/, so it is served
from the same site at findbingo.org/ohio/; this page links to it rather than copying Ohio data.
"""
import json
import re
from datetime import date
from html import escape
from urllib.parse import quote

ORDER = ['MI', 'IN', 'OH', 'KY', 'WV', 'PA', 'NY', 'FL', 'UT']
# One file of organizer-published schedules per starter state (coverage "starter").
STARTER_FILES = {'PA': 'pennsylvania-bingo.json', 'NY': 'new-york-bingo.json', 'FL': 'florida-bingo.json', 'UT': 'utah-bingo.json'}
# First three ZIP digits for each covered state (USPS prefix ranges).
PREFIXES = {'NY': (100, 149), 'PA': (150, 196), 'WV': (247, 268), 'FL': (320, 349), 'KY': (400, 427), 'OH': (430, 459), 'IN': (460, 479), 'MI': (480, 499), 'UT': (840, 847)}
COVERAGE = {'times', 'licenses', 'starter', 'ohio_finder', 'none'}
PHONE = re.compile(r'\d{3}-\d{3}-\d{4}')
TIME = re.compile(r'(?:[01]\d|2[0-3]):[0-5]\d')
REPO_RAW = 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/'
# Where the page looks for data.json and zips.json, in order: beside the page (the guide's copy),
# then GitHub Pages, then the raw file on main.
DATA_SOURCES = ['', 'https://guide.vethomeguard.org/findbingo-site/', REPO_RAW + 'main/findbingo-site/']
# Served only from bingo-site/findbingo/ (Cloudflare reads _redirects; GitHub Pages does not).
# The Ohio finder is the folder /ohio/; these catch the other ways people type it. No rule may
# match /ohio/ itself in any letter case, or the forward would loop.
REDIRECTS = ''.join(f'{src} /ohio/ 301\n' for src in ('/Ohio', '/OHIO', '/oh', '/oh/', '/OH', '/OH/'))


def _state_of_zip(z):
    p = int(z[:3])
    if p == 340:  # military mail (APO/FPO AA), not Florida
        return ''
    return next((s for s, (lo, hi) in PREFIXES.items() if lo <= p <= hi), '')


def validate(states, venues, licensed, zips):
    assert [s['code'] for s in states] == ORDER, 'bingo-states.json lists the covered states in order'
    for s in states:
        assert s['coverage'] in COVERAGE, s['code']
        for field in ('name', 'about', 'regulator_label', 'regulator_url', 'regulator_note', 'reviewed_on', 'sources'):
            assert s.get(field), (s['code'], field)
        assert s['regulator_url'].startswith('https://')
        assert all(x['url'].startswith('https://') and x['scope'] and date.fromisoformat(x['reviewed_on']) for x in s['sources'])
        if s['coverage'] in ('times', 'licenses'):
            assert s.get('list_url', '').startswith('https://') and s.get('list_label'), s['code']
        if s['coverage'] in ('times', 'starter'):
            assert s.get('hours_note'), s['code']
        # Counties the state lookup could not return yet; the page names them and links the state lookup.
        pending = s.get('pending_counties', [])
        assert pending == sorted(set(pending)) and all(type(c) is str and c for c in pending), s['code']
        if s['coverage'] == 'licenses':
            assert s.get('license_note') and date.fromisoformat(s['list_as_of']), s['code']
        if s['coverage'] == 'ohio_finder':
            assert s.get('finder_url', '').startswith('https://'), s['code']
    pending = {c for s in states for c in s.get('pending_counties', [])}
    assert not pending & {v['county'] for v in venues}, 'a county with listings is no longer pending'
    with_venues = {s['code'] for s in states if s['coverage'] in ('times', 'starter')}
    assert {s['code'] for s in states if s['coverage'] == 'starter'} == set(STARTER_FILES), 'each starter state has its schedule file'
    ids = set()
    for v in venues:
        code = v['state']
        assert code in with_venues and v['id'] not in ids and re.fullmatch(code.lower() + r'-[a-z0-9-]+', v['id']), v['id']
        ids.add(v['id'])
        assert _state_of_zip(v['zip']) == code and v['zip'] in zips, v['id']
        assert v['address'].endswith(', ' + code + ' ' + v['zip']) and v['city'] in v['address'], v['id']
        assert v['name'] and v['county'] and v['organizations'] and v['sessions'], v['id']
        for x in v['sessions']:
            assert type(x['day']) is int and 0 <= x['day'] <= 6, v['id']
            if code == 'MI':  # the state license list always gives both times
                assert TIME.fullmatch(x['start']) and TIME.fullmatch(x['end']), v['id']
            else:  # published schedules give a start time, or none ("time not posted")
                assert (x['start'] is None or TIME.fullmatch(x['start'])) and 'end' not in x, v['id']
            assert x['organization'] in v['organizations'] and x.get('label', 'x'), v['id']
        assert all(type(n) is str and n for n in v.get('notes', [])), v['id']
        if code != 'MI':
            # Published-schedule listings carry their own source, phone and how far to trust the days.
            # A phone is listed when the source gives one; without it the card offers a phone lookup instead.
            assert v['kind'] in ('hall', 'senior_center') and ('phone' not in v or PHONE.fullmatch(v['phone'])), v['id']
            assert v['source_url'].startswith('https://') and v['source_label'] and v['schedule_note'], v['id']
        assert date.fromisoformat(v['reviewed_on']) and v['sources'] and all(x['url'].startswith('https://') for x in v['sources'])
    for r in licensed:
        assert r['id'] not in ids and r['id'] == 'in-' + r['license_number'], r['id']
        ids.add(r['id'])
        assert r['state'] == 'IN' and _state_of_zip(r['zip']) == 'IN' and r['zip'] in zips, r['id']
        assert r['address'].endswith(', IN ' + r['zip']) and r['name'] and r['county'], r['id']
        assert r['license_type'].startswith('Annual Activity'), r['id']
        assert date.fromisoformat(r['license_expires']) and date.fromisoformat(r['reviewed_on']), r['id']
        assert r['sources'] and all(x['url'].startswith('https://') for x in r['sources'])


def _public_state(s):
    keep = ('code', 'name', 'coverage', 'about', 'hours_note', 'license_note', 'list_label', 'list_url', 'list_as_of',
            'finder_url', 'regulator_label', 'regulator_url', 'regulator_note', 'pending_counties', 'reviewed_on')
    return {k: s[k] for k in keep if k in s}


def _public_record(r, keys):
    return {k: r[k] for k in keys if k in r}


def _date_label(iso):
    d = date.fromisoformat(iso)
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


def make_findbingo(root):
    states = json.loads((root / 'data/public/bingo-states.json').read_text())
    venues = json.loads((root / 'data/public/michigan-weekly-bingo.json').read_text())
    for code in ORDER:
        if code in STARTER_FILES:
            rows = json.loads((root / 'data/public' / STARTER_FILES[code]).read_text())
            assert rows and all(v['state'] == code for v in rows), STARTER_FILES[code]
            venues += rows
    licensed = json.loads((root / 'data/public/indiana-bingo-licenses.json').read_text())
    all_zips = json.loads((root / 'data/public/us-zip-centroids.json').read_text())
    for extra in json.loads((root / 'data/public/zip-points-supplement.json').read_text()):
        # Census Geocoder points for the few covered ZIP codes that the centroid file lacks.
        assert extra['zip'] not in all_zips and extra['source_url'].startswith('https://') and date.fromisoformat(extra['reviewed_on'])
        all_zips[extra['zip']] = [extra['lat'], extra['lon']]
    zips = {z: [round(c[0], 3), round(c[1], 3)] for z, c in sorted(all_zips.items()) if _state_of_zip(z)}
    validate(states, venues, licensed, zips)
    generated_on = max([s['reviewed_on'] for s in states] + [r['reviewed_on'] for r in venues + licensed])
    data = {
        'generated_on': generated_on,
        'states': [_public_state(s) for s in states],
        'venues': [_public_record(v, ('id', 'state', 'kind', 'name', 'organizations', 'address', 'city', 'zip', 'county', 'phone', 'sessions',
                                      'audience', 'hours', 'schedule_note', 'notes', 'source_url', 'source_label', 'reviewed_on')) for v in venues],
        'licensed': [_public_record(r, ('id', 'state', 'name', 'address', 'city', 'zip', 'county', 'license_number', 'license_type', 'license_expires', 'reviewed_on')) for r in licensed],
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    # Each button links to that state's own page (crawlable); with the lists loaded, the finder shows the state in place.
    buttons = ''.join(f'<a href="{SLUGS[s["code"]]}/" data-state="{s["code"]}">{escape(s["name"])}</a>' for s in states)
    about = ''
    for s in states:
        pairs = []
        for url, label in ((s.get('list_url'), s.get('list_label')), (s.get('finder_url'), 'Ohio Bingo Finder'), (s['regulator_url'], s['regulator_label'])):
            if url and url not in [u for u, _ in pairs]:
                pairs.append((url, label))
        links = ' · '.join(f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a>' for u, l in pairs)
        as_of = f' (list dated {_date_label(s["list_as_of"])})' if s.get('list_as_of') else ''
        about += (f'<h3><a href="{SLUGS[s["code"]]}/">{escape(s["name"])}</a></h3><p>{escape(s["about"])} {escape(s["regulator_note"])}</p>'
                  f'<p class="small">Checked {_date_label(s["reviewed_on"])}{as_of}. Sources: {links}</p>')
    page = (root / 'templates/findbingo/index.html').read_text()
    for key, value in (('__SOURCES__', json.dumps(DATA_SOURCES)), ('__STATE_BUTTONS__', buttons), ('__ABOUT__', about),
                       ('__UPDATED__', _date_label(generated_on))):
        assert page.count(key) == 1, key
        page = page.replace(key, value)
    readme = f'''# FindBingo.org

Generated by `scripts/findbingo_site.py` from `data/public/bingo-states.json`,
`data/public/michigan-weekly-bingo.json`, `data/public/indiana-bingo-licenses.json` and the ZIP code
centroids. Do not edit these files by hand; run `python3 scripts/build_public.py`.

- `index.html` is the whole page. The same files are written to `bingo-site/findbingo/`, which the
  Ohio-Bingo repository mirrors and Cloudflare serves at https://www.findbingo.org/ (see
  docs/FINDBINGO.md).
- `data.json` (the lists) and `zips.json` (ZIP code points for the covered states) are loaded by the
  page from https://guide.vethomeguard.org/findbingo-site/, so list updates reach findbingo.org as soon
  as a pull request merges.
- The Ohio Bingo Finder is served from the same site at https://www.findbingo.org/ohio/
  (`bingo-site/findbingo/ohio/`, built by `scripts/bingo_site.py`). Ohio halls that want to work with
  Veteran Home Guardians go to https://www.ohiobingo.org/.

Lists updated {_date_label(generated_on)}.
'''
    # Page views only, on the same counter as the Ohio finder at findbingo.org/ohio/. The code from
    # assets/analytics.js is written into the page, so index.html stays the whole page with no script files.
    assert page.count('</body>') == 1
    analytics = (root / 'assets/analytics.js').read_text().strip()
    page = page.replace('</body>', '<script>' + analytics + '</script></body>', 1)
    # Tell search engines what the site is and who publishes it. No Event markup: the lists hold weekly
    # schedules, not dated events.
    publisher = {'@type': 'Organization', 'name': 'Veteran Home Guardians', 'url': 'https://www.vethomeguard.org/',
                 'logo': SITE + '/ohio/assets/vhg-logo.png', 'email': EMAIL}
    page = page.replace('</head>', _json_ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Find Bingo',
                                             'alternateName': 'FindBingo.org', 'url': SITE + '/', 'inLanguage': 'en-US',
                                             'publisher': publisher}) + '\n</head>', 1)
    style = re.search(r'<style>.*?</style>', page, re.S).group(0).replace('</style>', STATE_CSS + '</style>')
    today = generated_on
    pages = {}
    for s in states:
        if s['code'] == 'OH':
            continue
        if s['coverage'] == 'licenses':
            rows = [r for r in licensed if r['state'] == s['code'] and r['license_expires'] >= today]
        else:
            rows = [v for v in venues if v['state'] == s['code']]
        pages[SLUGS[s['code']] + '/index.html'] = _state_page(s, states, rows, style, analytics, generated_on)
    site = {
        # Google Search Console ownership file for https://www.findbingo.org/ (owner direction, Nov 16, 2026).
        # Keep it: Google rechecks the file, and removing it drops verification.
        'googleae90b5079bda9bbc.html': 'google-site-verification: googleae90b5079bda9bbc.html',
        'index.html': page,
        'data.json': data_json + '\n',
        'zips.json': json.dumps(zips, separators=(',', ':')) + '\n',
        **pages,
    }
    # The same three files also go into bingo-site/findbingo/, which the Ohio-Bingo repository mirrors;
    # Cloudflare serves www.findbingo.org from that folder (the Ohio finder sits beside them in ohio/).
    return {
        **{'findbingo-site/' + name: text for name, text in site.items()},
        **{'bingo-site/findbingo/' + name: text for name, text in site.items()},
        'bingo-site/findbingo/_redirects': REDIRECTS + SHORT_REDIRECTS,
        'findbingo-site/README.md': readme,
    }


# ---- One page per state (findbingo.org/michigan/ and so on) ------------------------------------------
# The finder above is one page that draws its lists with JavaScript, so search engines see no listings and
# no state names in titles. Each state also gets a plain page with a real title, description and heading,
# and its listings written out as HTML, so "bingo in Michigan" searches can land on Michigan's list.
# Travis's rule (November 16, 2026): never state counts of halls, locations or counties on the site.
SITE = 'https://www.findbingo.org'
SLUGS = {'MI': 'michigan', 'IN': 'indiana', 'OH': 'ohio', 'KY': 'kentucky', 'WV': 'west-virginia',
         'PA': 'pennsylvania', 'NY': 'new-york', 'FL': 'florida', 'UT': 'utah'}
# Ohio's page is the Ohio Bingo Finder (built by bingo_site.py); the rest are built here.
STATE_PAGES = tuple(slug + '/' for code, slug in SLUGS.items() if code != 'OH')
DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
EMAIL = 'travis@vethomeguard.org'


def _clock(t):
    h, m = map(int, t.split(':'))
    if (h, m) == (12, 0):
        return 'noon'
    if (h, m) == (0, 0):
        return 'midnight'
    return str(h % 12 or 12) + (f':{m:02d}' if m else '') + (' a.m.' if h < 12 else ' p.m.')


def _time_range(a, b=None):
    """The same wording as timeRange() in the finder: '4 to 11 p.m.', 'noon to 4 p.m.', 'time not posted'."""
    if not a:
        return 'time not posted'
    if not b:
        return _clock(a)
    x, y = _clock(a), _clock(b)
    if x.endswith('.m.') and x[-4:] == y[-4:] and 'noon' not in x + y and 'midnight' not in x + y:
        return x[:-5] + ' to ' + y
    return x + ' to ' + y


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def _maps(q):
    return 'https://www.google.com/maps/search/?api=1&query=' + quote(q, safe='')


def _mailto(subject, body=''):
    return f'mailto:{EMAIL}?subject=' + quote(subject, safe='') + ('&body=' + quote(body, safe='') if body else '')


def _report(r):
    return _mailto(f'FindBingo.org correction: {r["name"]} ({r["id"]})',
                   'What should change? Fill in only what is different.\n\nBingo days:\nFirst game starts at:\nPhone for players:\nAddress:\nAnything else:\n')


def _out(url, label):
    return f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(label)} ↗</a>'


def _venue_html(v, s):
    many = len(v['organizations']) > 1
    sessions = ''.join(
        f'<li><strong>{DAY_NAMES[x["day"]]}</strong>, {escape(_time_range(x["start"], x.get("end")))}'
        + (f' <span class="org">· {escape(x["label"])}</span>' if x.get('label') else '')
        + (f' <span class="org">· {escape(x["organization"])}</span>' if many else '') + '</li>' for x in v['sessions'])
    if v.get('phone'):
        call = f'<a class="solid" href="tel:{re.sub(r"[^0-9]", "", v["phone"])}">Call {escape(v["phone"])}</a>'
    else:
        call = f'<a class="solid" href="{escape(_maps(v["name"] + " " + v["address"]))}" target="_blank" rel="noopener noreferrer">Look up phone number ↗</a>'
    source = _out(v['source_url'], v['source_label']) if v.get('source_url') else _out(s['list_url'], s['list_label'])
    return (f'<article id="{escape(v["id"])}"><p><span class="badge">{"Senior center bingo" if v.get("kind") == "senior_center" else "Bingo"}</span></p>'
            f'<h3>{escape(v["name"])}</h3><p class="where">{escape(v["city"])}</p>'
            + (f'<p class="small">{escape(v["audience"])}</p>' if v.get('audience') else '')
            + f'<div class="when"><p><strong>Bingo days:</strong></p><ul class="sessions">{sessions}</ul>'
            f'<p class="note">{escape(v.get("schedule_note") or s.get("hours_note") or "Call ahead to confirm before you go.")}</p></div>'
            f'<div class="big-actions">{call}<a class="outline" href="{escape(_maps(v["address"]))}" target="_blank" rel="noopener noreferrer">Directions ↗</a></div>'
            f'<p class="address">{escape(v["address"])} · {escape(v["county"])} County</p>'
            + (f'<p class="small">{escape(v["hours"])}</p>' if v.get('hours') else '')
            + (f'<p class="small">Bingo here is run by {escape(", ".join(v["organizations"]))}.</p>' if many else '')
            + f'<details class="sources"><summary>Where this comes from · checked {_date_label(v["reviewed_on"])}</summary><p>{source}</p>'
            + ''.join(f'<p>{escape(n)}</p>' for n in v.get('notes', [])) + '</details>'
            f'<p class="small-links"><a href="{escape(_report(v))}">Report a change</a></p></article>')


def _licensed_html(r, s):
    return (f'<article id="{escape(r["id"])}"><p><span class="badge muted">Licensed for bingo · game days not posted</span></p>'
            f'<h3>{escape(r["name"])}</h3><p class="where">{escape(r["city"])}</p>'
            f'<div class="big-actions"><a class="solid" href="{escape(_maps(r["name"] + " " + r["address"]))}" target="_blank" rel="noopener noreferrer">Look up phone number ↗</a>'
            f'<a class="outline" href="{escape(_maps(r["address"]))}" target="_blank" rel="noopener noreferrer">Directions ↗</a></div>'
            f'<p class="address">{escape(r["address"])} · {escape(r["county"])} County</p>'
            f'<details class="sources"><summary>Where this comes from · checked {_date_label(r["reviewed_on"])}</summary>'
            f'<p>{escape(s["name"])} license {escape(r["license_number"])} ({escape(r["license_type"])}), on the state list through {_date_label(r["license_expires"])}.</p>'
            f'<p>{_out(s["list_url"], s["list_label"])}</p></details>'
            f'<p class="small-links"><a href="{escape(_report(r))}">Send us their game days</a></p></article>')


def _send_times(s):
    return (f'<section class="panel" id="run-a-game" aria-labelledby="run-title"><h2 id="run-title">Run a bingo game in {escape(s["name"])}? Get it listed free</h2>'
            '<p>Send us the name of your hall, the address, the days and the time the first game starts. A phone number for players helps too. '
            'Listing is free, and we never sell or share your information.</p>'
            f'<div class="big-actions"><a class="solid" href="{escape(_mailto("Bingo game times in " + s["name"], "Hall or group name:" + chr(10) + "Address:" + chr(10) + "Days and first game time:" + chr(10) + "Phone for players:" + chr(10) + "Website or Facebook page:" + chr(10)))}">Email your game times</a></div></section>')


STATE_COPY = {
    # coverage: (title, description, lead). {name} is the state's name.
    'times': ('{name} Bingo Near You: Weekly Bingo Halls, Days and Times | FindBingo.org',
              'Free list of weekly bingo in {name}, by county, with game days, licensed hours, directions and a phone lookup. Type your ZIP code to see bingo near you, closest first.',
              'Weekly bingo halls in {name}, by county, with the days and hours. Call ahead before you go.'),
    'licenses': ('{name} Bingo: Groups Licensed for Bingo, by County | FindBingo.org',
                 'Free list of {name} groups with a current state license to hold bingo, by county, with directions and a phone lookup. Type your ZIP code to see bingo near you.',
                 'Groups in {name} with a current license to hold bingo, by county. The state list does not show game days, so call before you go.'),
    'starter': ('{name} Bingo: Where to Play, Days and Times | FindBingo.org',
                'Free list of bingo games in {name} from places that publish their own schedules, with days, times, phone numbers and directions. Halls can add their games free.',
                'Bingo in {name} from places that publish their own schedules. Call ahead before you go.'),
    'none': ('{name} Bingo: Finding Games and Getting Your Hall Listed | FindBingo.org',
             'How to find bingo in {name}, who licenses it, and how halls can list their game days free on FindBingo.org.',
             'We are building a list of {name} bingo games. Run a game? Send us your days and times and we will list it free.'),
}


def _state_page(s, states, rows, style, analytics, generated_on):
    code, name, slug = s['code'], s['name'], SLUGS[s['code']]
    title, description, lead = (t.format(name=name) for t in STATE_COPY[s['coverage']])
    url = f'{SITE}/{slug}/'
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Find Bingo', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': f'Bingo in {name}', 'item': url}]}
    rows = sorted(rows, key=lambda r: (r['county'], r['city'], r['name']))
    counties = sorted({r['county'] for r in rows})
    body = f'<p class="intro">{escape(s["about"])} {escape(s["regulator_note"])}</p>'
    if s.get('pending_counties'):
        c = s['pending_counties']
        listed = ', '.join(c[:-1]) + ' and ' + c[-1] if len(c) > 1 else c[0]
        body += (f'<p class="note" id="pending-{code}">Our {escape(name)} list does not include {escape(listed)} '
                 f'{"counties" if len(c) > 1 else "County"} yet. For games there, use {_out(s["list_url"], "the state’s own lookup")}.</p>')
    if s['coverage'] == 'licenses':
        body += f'<p class="note">{escape(s["license_note"])}</p>'
    if len(counties) > 1:
        body += ('<nav class="counties" aria-labelledby="counties-title"><h2 id="counties-title">Jump to your county</h2><ul>'
                 + ''.join(f'<li><a href="#county-{_slug(c)}">{escape(c)}</a></li>' for c in counties) + '</ul></nav>')
    if rows:
        card = _licensed_html if s['coverage'] == 'licenses' else _venue_html
        body += '<div id="listings">' + ''.join(
            f'<section aria-labelledby="county-{_slug(c)}"><h2 id="county-{_slug(c)}">{escape(c)} County</h2><div class="grid">'
            + ''.join(card(r, s) for r in rows if r['county'] == c) + '</div><p class="top"><a href="#top">Back to the top</a></p></section>'
            for c in counties) + '</div>'
    else:
        body += (f'<div id="listings"><p class="empty">We have not listed any {escape(name)} games yet. '
                 'If you know of one, please tell us about it below.</p></div>')
    body += _send_times(s)
    pairs = []
    for u, label in ((s.get('list_url'), s.get('list_label')), (s['regulator_url'], s['regulator_label'])):
        if u and u not in [p[0] for p in pairs]:
            pairs.append((u, label))
    as_of = f' (list dated {_date_label(s["list_as_of"])})' if s.get('list_as_of') else ''
    body += (f'<section class="panel" id="about" aria-labelledby="about-title"><h2 id="about-title">Where this list comes from</h2>'
             f'<p>Checked {_date_label(s["reviewed_on"])}{as_of}. Sources: {" · ".join(_out(u, l) for u, l in pairs)}</p>'
             '<p>Game days and hours can change, especially around holidays. Call ahead before you go, and ask about parking, steps and seating if that matters for you.</p></section>')
    others = ''.join(f'<a href="../{SLUGS[o["code"]]}/">{escape(o["name"])}</a>' for o in states if o['code'] != code)
    zip_form = ('<form class="zip-box" action="../" method="get"><div class="tools">'
                '<div><label for="zip">Type your ZIP code</label><input id="zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" pattern="[0-9]{5}" placeholder="Your 5-digit ZIP" required></div>'
                '<div><label for="radius">How far will you go?</label><select id="radius" name="radius"><option value="10">10 miles</option><option value="25" selected>25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>'
                '<div><button class="primary" type="submit">Find bingo near me</button></div></div>'
                '<p class="small">Shows bingo near you in every state we cover, closest first.</p></form>')
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(f"Bingo in {name}")}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n' + _json_ld(crumbs) + '\n</head>')
    return (head + '<body id="top"><a class="skip" href="#listings">Skip to the bingo list</a>'
            f'<header><p class="brand"><a href="../">FindBingo.org</a> · free from Veteran Home Guardians</p><h1>Bingo in {escape(name)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main>{zip_form}{body}'
            f'<nav class="states" aria-labelledby="states-title"><h2 id="states-title">Bingo in other states</h2><div class="state-buttons">{others}</div>'
            '<p class="small-links"><a href="../">Search every state by ZIP code</a></p></nav></main>'
            f'{_footer(generated_on)}<script>{analytics}</script></body></html>\n')


def _json_ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def _footer(generated_on):
    return ('<footer><p>FindBingo.org is a free community resource from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>. '
            'Listings are free and never depend on donations or advertising.</p>'
            '<p class="noprint">Need help getting to the game? <a href="https://mobilitytalk.org/states/">Mobility Talk</a> lists mobility and disability resources in every state.</p>'
            f'<p class="noprint">Questions or corrections: <a href="mailto:{EMAIL}?subject=FindBingo.org">{EMAIL}</a> · Made by <a href="https://travisvought.com/">Travis Vought</a></p>'
            f'<p class="noprint">Lists updated {_date_label(generated_on)}.</p></footer>')


# Short addresses for posters and word of mouth: findbingo.org/mi and /MI open the Michigan page.
SHORT_REDIRECTS = ''.join(f'/{c} /{slug}/ 301\n/{c.lower()} /{slug}/ 301\n' for c, slug in SLUGS.items() if c != 'OH')
STATE_CSS = ('header a{color:#fff}.intro{font-size:20px;max-width:860px}'
             '.counties{background:#fff;border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}.counties h2{font-size:24px;margin:10px 0 8px}'
             '.counties ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
             '.counties a{display:inline-flex;align-items:center;min-height:48px;padding:0 14px;border:2px solid var(--green);border-radius:24px;color:var(--green);font-weight:700;text-decoration:none}'
             '#listings>section>h2{font-size:28px;margin:28px 0 10px;scroll-margin-top:12px}.top{font-size:17px;margin:10px 0 0}.top a{display:inline-flex;align-items:center;min-height:44px}'
             '@media print{.counties,.top,#run-a-game{display:none!important}}')
