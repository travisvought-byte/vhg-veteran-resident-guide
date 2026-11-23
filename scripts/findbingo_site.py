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
import place_map

# Every state and DC has an entry in bingo-states.json, in alphabetical order by name. A state we have not
# researched yet has coverage "pending": a plain "send us your games" card and page, kept out of search
# engines until it has real content.
STATES = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
ORDER = list(STATES)
# One file of organizer-published schedules per starter state (coverage "starter").
STARTER_FILES = {'PA': 'pennsylvania-bingo.json', 'NY': 'new-york-bingo.json', 'FL': 'florida-bingo.json', 'UT': 'utah-bingo.json',
                 'KY': 'kentucky-bingo.json', 'WV': 'west-virginia-bingo.json', 'WA': 'washington-bingo.json',
                 'MN': 'minnesota-bingo.json', 'IL': 'illinois-bingo.json', 'IA': 'iowa-bingo.json', 'OR': 'oregon-bingo.json', 'CO': 'colorado-bingo.json', 'AZ': 'arizona-bingo.json', 'NH': 'new-hampshire-bingo.json'}
# State lists that give each game's day and hours: Michigan's weekly bingo licenses, the Texas hall locator,
# Virginia's directory of sessions and Missouri's Find Local Bingo Games page.
TIMES_FILES = {'MI': 'michigan-weekly-bingo.json', 'TX': 'texas-bingo-halls.json', 'VA': 'virginia-bingo-sessions.json',
               'MO': 'missouri-bingo-sessions.json'}
# State lists that give a start time but no end time.
START_ONLY = {'MO'}
# State lists that name licensed groups or permitted places without game days: Indiana's annual bingo licenses,
# Mississippi's licensed bingo halls, Montana's live bingo permits, and New Mexico's groups licensed for bingo, raffles or
# pull-tabs.
LICENSE_FILES = {'IN': 'indiana-bingo-licenses.json', 'MS': 'mississippi-bingo-licenses.json',
                 'MT': 'montana-bingo-permits.json', 'NM': 'new-mexico-bingo-licenses.json'}
COVERAGE = {'times', 'licenses', 'starter', 'ohio_finder', 'none', 'pending'}
# States with a list on this site (or, for Ohio, its own finder). Every other state has a researched page that
# names who licenses bingo there and links the state's own list or finder where one is published.
LISTED = {'times', 'licenses', 'starter', 'ohio_finder'}
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
# Small line icons (calendar, map pin, phone, directions, search), written once per page and drawn with <use>.
# They always sit beside words that say the same thing, and screen readers skip them.
ICONS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
         '<symbol id="i-cal" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>'
         '<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-7-6.1-7-11.4a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.6" r="2.6"/></symbol>'
         '<symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 3.5h3.5l2 5-2.6 1.6a12 12 0 0 0 6 6l1.6-2.6 5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5.5a2 2 0 0 1 2-2z"/></symbol>'
         '<symbol id="i-route" viewBox="0 0 24 24"><path d="M12 2.5 21.5 12 12 21.5 2.5 12z"/><path d="M9 15v-2.5a2 2 0 0 1 2-2h4.5M13.5 8.5l2 2-2 2"/></symbol>'
         '<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/></symbol>'
         '</defs></svg>')
# Five bingo balls above each page's heading: decoration only, hidden from screen readers.
BALLS = '<div class="balls" aria-hidden="true"><i>B</i><i>I</i><i>N</i><i>G</i><i>O</i></div>'
# State pages are plain HTML: this marks weekly games on the visitor's own weekday with a "Today" tag.
# Lists with monthly patterns are not marked (their games may not fall this week). Without JavaScript nothing changes.
TODAY_SCRIPT = ("<script>(function(){var d=new Date().getDay();document.querySelectorAll('ul.sessions[data-weekly] li[data-day=\"'+d+'\"]').forEach(function(li){"
                "var t=document.createElement('span');t.className='today-tag';t.textContent='Today';li.className='today';"
                "li.appendChild(document.createTextNode(' '));li.appendChild(t)})})()</script>")


def _ic(name):
    return f'<svg class="ic" aria-hidden="true"><use href="#i-{name}"/></svg>'


ZIP_STATES = {}
# ZIP code points (the same ones zips.json carries), for pinning state-page cards on the map.
ZIP_POINTS = {}


def _load_zip_states(root):
    """ZIP code to state, from the state column of the ZIP centroid source (data/public/zip-states.json)."""
    table = json.loads((root / 'data/public/zip-states.json').read_text())
    assert set(table['zip3'].values()) == set(STATES) and set(table['exceptions'].values()) <= set(STATES)
    ZIP_STATES.update(zip3=table['zip3'], exceptions=table['exceptions'])


def _state_of_zip(z):
    return ZIP_STATES['exceptions'].get(z) or ZIP_STATES['zip3'].get(z[:3], '')


def validate(states, venues, licensed, zips):
    assert [s['code'] for s in states] == ORDER, 'bingo-states.json lists the covered states in order'
    for s in states:
        assert s['coverage'] in COVERAGE and s['name'] == STATES[s['code']], s['code']
        if s['coverage'] == 'pending':
            # Not researched yet: nothing is claimed about the state, so there is nothing to source.
            assert set(s) == {'code', 'name', 'coverage', 'about', 'reviewed_on'} and s['about'] and date.fromisoformat(s['reviewed_on']), s['code']
            continue
        for field in ('name', 'about', 'regulator_label', 'regulator_url', 'regulator_note', 'reviewed_on', 'sources'):
            assert s.get(field), (s['code'], field)
        assert s['regulator_url'].startswith('https://')
        assert all(x['url'].startswith('https://') and x['scope'] and date.fromisoformat(x['reviewed_on']) for x in s['sources'])
        if s['coverage'] in ('times', 'licenses') or s.get('list_url') or s.get('list_label'):
            assert s.get('list_url', '').startswith('https://') and s.get('list_label'), s['code']
        # Optional wording for a state page whose situation the standard wording would misstate (Hawaii, Tennessee).
        assert all(isinstance(s[k], str) and s[k].strip() for k in ('lead', 'description') if k in s), s['code']
        if s['coverage'] in ('times', 'starter'):
            assert s.get('hours_note'), s['code']
        # Counties the state lookup could not return yet; the page names them and links the state lookup.
        pending = s.get('pending_counties', [])
        assert pending == sorted(set(pending)) and all(type(c) is str and c for c in pending), s['code']
        if s['coverage'] == 'licenses':
            # list_as_of only when the list itself carries a date (New Mexico's page does not).
            assert s.get('license_note') and ('list_as_of' not in s or date.fromisoformat(s['list_as_of'])), s['code']
        if s['coverage'] == 'ohio_finder':
            assert s.get('finder_url', '').startswith('https://'), s['code']
        if 'halls' in s:
            # What the state's law says about the money and the ads (docs/BINGO-OPPORTUNITY.md); every claim sourced.
            h = s['halls']
            assert set(h) <= {'money', 'money_note', 'ad_note', 'sources'} and h['money'] in HALL_MONEY and h['money_note'].strip(), s['code']
            assert 'ad_note' not in h or h['ad_note'].strip(), s['code']
            # Ohio's required outside gift is what the Veteran Home Guardians partnership asks a share of; its pitch
            # lives on the Ohio finder. Other states that require a gift get the local-partner offer (HALL_PITCH).
            assert s['code'] != 'OH' or h['money'] == 'must_give', s['code']
            assert h['sources'] and all(x['url'].startswith('https://') and x['scope'] and date.fromisoformat(x['reviewed_on']) for x in h['sources']), s['code']
        if 'partner' in s:
            # A local organization doing work like ours that we ask the state's halls to consider supporting
            # (owner direction, November 22, 2026). Its ways to help are written to the state's own rule on bingo money,
            # so a partner needs that rule summarized first. Ohio's partner is Veteran Home Guardians (the Ohio finder).
            p = s['partner']
            assert s['code'] != 'OH' and s.get('halls'), s['code']
            assert set(p) <= {'name', 'the', 'url', 'donate_url', 'about', 'ways', 'note', 'since', 'sources'} and p.get('the', True) in (True, False), s['code']
            assert p['name'].strip() and p['about'].strip() and date.fromisoformat(p['since']), s['code']
            assert all(p[k].startswith('https://') for k in ('url', 'donate_url') if k in p) and 'url' in p, s['code']
            assert p['ways'] and all(isinstance(w, str) and w.strip() for w in p['ways']), s['code']
            assert 'note' not in p or p['note'].strip(), s['code']
            assert p['sources'] and all(x['url'].startswith('https://') and x['scope'] and date.fromisoformat(x['reviewed_on']) for x in p['sources']), s['code']
    pending ={(s['code'], c) for s in states for c in s.get('pending_counties', [])}
    assert not pending & {(v['state'], v['county']) for v in venues}, 'a county with listings is no longer pending'
    with_venues = {s['code'] for s in states if s['coverage'] in ('times', 'starter')}
    assert {s['code'] for s in states if s['coverage'] == 'starter'} == set(STARTER_FILES), 'each starter state has its schedule file'
    assert {s['code'] for s in states if s['coverage'] == 'times'} == set(TIMES_FILES), 'each state list with hours has its file'
    assert {s['code'] for s in states if s['coverage'] == 'licenses'} == set(LICENSE_FILES), 'each license list has its file'
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
            if code in START_ONLY:  # the state list gives the start time only
                assert TIME.fullmatch(x['start']) and 'end' not in x, v['id']
            elif code in TIMES_FILES:  # a state list gives both times
                assert TIME.fullmatch(x['start']) and TIME.fullmatch(x['end']), v['id']
            else:  # published schedules give a start time, or none ("time not posted")
                assert (x['start'] is None or TIME.fullmatch(x['start'])) and 'end' not in x, v['id']
            assert x['organization'] in v['organizations'] and x.get('label', 'x'), v['id']
        assert all(type(n) is str and n for n in v.get('notes', [])), v['id']
        assert 'phone' not in v or PHONE.fullmatch(v['phone']), v['id']
        if code not in TIMES_FILES:
            # Published-schedule listings carry their own source, phone and how far to trust the days.
            # A phone is listed when the source gives one; without it the card offers a phone lookup instead.
            assert v['kind'] in ('hall', 'senior_center') and ('phone' not in v or PHONE.fullmatch(v['phone'])), v['id']
            assert v['source_url'].startswith('https://') and v['source_label'] and v['schedule_note'], v['id']
        assert date.fromisoformat(v['reviewed_on']) and v['sources'] and all(x['url'].startswith('https://') for x in v['sources'])
    for r in licensed:
        code = r['state']
        # The id follows the license number when the list gives one (New Mexico's does not).
        assert code in LICENSE_FILES and r['id'] not in ids and re.fullmatch(code.lower() + r'-[a-z0-9-]+', r['id']), r['id']
        assert 'license_number' not in r or r['id'] == code.lower() + '-' + _slug(r['license_number']), r['id']
        ids.add(r['id'])
        assert _state_of_zip(r['zip']) == code and r['zip'] in zips, r['id']
        assert r['address'].endswith(', ' + code + ' ' + r['zip']) and r['city'] in r['address'] and r['name'] and r['county'], r['id']
        assert r['license_type'] and (code != 'IN' or r['license_type'].startswith('Annual Activity')), r['id']
        assert 'phone' not in r or PHONE.fullmatch(r['phone']), r['id']
        assert ('license_expires' not in r or date.fromisoformat(r['license_expires'])) and date.fromisoformat(r['reviewed_on']), r['id']
        assert r['sources'] and all(x['url'].startswith('https://') for x in r['sources'])


def _public_state(s):
    keep = ('code', 'name', 'coverage', 'about', 'hours_note', 'license_note', 'license_badge', 'license_heading', 'list_label', 'list_url', 'list_as_of',
            'finder_url', 'regulator_label', 'regulator_url', 'regulator_note', 'pending_counties', 'reviewed_on')
    return {k: s[k] for k in keep if k in s}


def _public_record(r, keys):
    return {k: r[k] for k in keys if k in r}


def _date_label(iso):
    d = date.fromisoformat(iso)
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


def make_findbingo(root, ads=None, events=None):
    """All Find Bingo files. ads replaces data/findbingo-ads.json and events data/findbingo-events.json (the tests pass samples)."""
    _load_zip_states(root)
    if ads is None:
        ads = json.loads((root / ADS_FILE).read_text())
    validate_ads(ads, root)
    states = json.loads((root / 'data/public/bingo-states.json').read_text())
    venues = []
    for code in ORDER:
        if code in TIMES_FILES:
            rows = json.loads((root / 'data/public' / TIMES_FILES[code]).read_text())
            assert rows and all(v['state'] == code for v in rows), TIMES_FILES[code]
            venues += rows
        if code in STARTER_FILES:
            rows = json.loads((root / 'data/public' / STARTER_FILES[code]).read_text())
            assert rows and all(v['state'] == code for v in rows), STARTER_FILES[code]
            venues += rows
    licensed = []
    for code in ORDER:
        if code in LICENSE_FILES:
            rows = json.loads((root / 'data/public' / LICENSE_FILES[code]).read_text())
            assert rows and all(r['state'] == code for r in rows), LICENSE_FILES[code]
            licensed += rows
    all_zips = json.loads((root / 'data/public/us-zip-centroids.json').read_text())
    for extra in json.loads((root / 'data/public/zip-points-supplement.json').read_text()):
        # Census Geocoder points for the few covered ZIP codes that the centroid file lacks.
        assert extra['zip'] not in all_zips and extra['source_url'].startswith('https://') and date.fromisoformat(extra['reviewed_on'])
        all_zips[extra['zip']] = [extra['lat'], extra['lon']]
    zips = {z: [round(c[0], 3), round(c[1], 3)] for z, c in sorted(all_zips.items()) if _state_of_zip(z)}
    validate(states, venues, licensed, zips)
    if events is None:
        events = load_events(root)
    validate_events(events, zips)
    generated_on = max([s['reviewed_on'] for s in states] + [r['reviewed_on'] for r in venues + licensed])
    data = {
        'generated_on': generated_on,
        # First three ZIP digits to state, plus the few ZIP codes that sit in another state.
        'zip3': ZIP_STATES['zip3'],
        'zip_exceptions': ZIP_STATES['exceptions'],
        'states': [_public_state(s) for s in states],
        'venues': [_public_record(v, ('id', 'state', 'kind', 'name', 'organizations', 'address', 'city', 'zip', 'county', 'phone', 'sessions',
                                      'audience', 'hours', 'schedule_note', 'notes', 'source_url', 'source_label', 'reviewed_on')) for v in venues],
        'licensed': [_public_record(r, ('id', 'state', 'name', 'address', 'city', 'zip', 'county', 'phone', 'license_number', 'license_type', 'license_expires', 'reviewed_on')) for r in licensed],
        # Paid featured events (owner direction, November 20, 2026), shown in their own labeled box, never in the listings.
        'events': [_public_record(e, EVENT_PUBLIC) for e in upcoming_events(events, generated_on)],
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    # Each button links to that state's own page (crawlable); with the lists loaded, the finder shows the state in place.
    def button(s):
        return f'<a href="{SLUGS[s["code"]]}/" data-state="{s["code"]}">{escape(s["name"])}</a>'
    # States with a list come first, along with states where we name a local partner, so a partner's state
    # is never hidden (owner direction, November 23, 2026). Every other state sits behind one "more states"
    # control so the page stays simple for people who struggle with websites.
    shown = [s for s in states if s['coverage'] in LISTED or s.get('partner')]
    rest = [s for s in states if s not in shown]
    buttons = ''.join(button(s) for s in shown)
    if rest:
        buttons += ('<details class="more-states"><summary>More states, A to Z</summary><div>'
                    + ''.join(button(s) for s in rest) + '</div></details>')
    about = ''
    for s in states:
        if s['coverage'] not in LISTED:
            continue
        pairs = []
        for url, label in ((s.get('list_url'), s.get('list_label')), (s.get('finder_url'), 'Ohio Bingo Finder'), (s['regulator_url'], s['regulator_label'])):
            if url and url not in [u for u, _ in pairs]:
                pairs.append((url, label))
        links = ' · '.join(f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a>' for u, l in pairs)
        as_of = f' (list dated {_date_label(s["list_as_of"])})' if s.get('list_as_of') else ''
        about += (f'<h3><a href="{SLUGS[s["code"]]}/">{escape(s["name"])}</a></h3><p>{escape(s["about"])} {escape(s["regulator_note"])}</p>'
                  f'<p class="small">Checked {_date_label(s["reviewed_on"])}{as_of}. Sources: {links}</p>')
    def named(group):
        return ', '.join(f'<a href="{SLUGS[s["code"]]}/">{escape(s["name"])}</a>' for s in group)
    researched = [s for s in states if s['coverage'] == 'none']
    waiting = [s for s in states if s['coverage'] == 'pending']
    if researched or waiting:
        about += '<h3>Every other state</h3>'
    if researched:
        about += ('<p>Each of these states has its own page. It names who licenses or oversees bingo there, links the state’s own list or finder '
                  'where there is one, shows its sources, and gives a free way to send us game times: ' + named(researched) + '.</p>')
    if waiting:
        about += ('<p>We have not built lists for these states yet. Each has its own page with a free way to send us game times: '
                  + named(waiting) + '.</p>')
    page = (root / 'templates/findbingo/index.html').read_text()
    ZIP_POINTS.clear()
    ZIP_POINTS.update(zips)
    for key, value in (('__MAP_BOX__', _map_box('', 'the bingo games listed below')),
                       ('__LOCATE__', place_map.locate_button('zip', 'zip-form', 'zip-status', 'ZIPS', 'Or use my location')),
                       ('__SOURCES__', json.dumps(DATA_SOURCES)), ('__STATE_BUTTONS__', buttons), ('__ABOUT__', about), ('__ICONS__', ICONS), ('__BALLS__', BALLS),
                       ('__UPDATED__', _date_label(generated_on)), ('__AD_HOME__', _ad_html(_ads_for(ads, 'home'), ''))):
        assert page.count(key) == 1, key
        page = page.replace(key, value)
    readme = f'''# FindBingo.org

Generated by `scripts/findbingo_site.py` from `data/public/bingo-states.json`,
`data/public/michigan-weekly-bingo.json`, `data/public/texas-bingo-halls.json`, `data/public/virginia-bingo-sessions.json`,
`data/public/missouri-bingo-sessions.json`,
`data/public/indiana-bingo-licenses.json`, `data/public/mississippi-bingo-licenses.json`, `data/public/montana-bingo-permits.json`,
`data/public/new-mexico-bingo-licenses.json` and the ZIP code
centroids. Do not edit these files by hand; run `python3 scripts/build_public.py`.

- `index.html` is the whole page. The same files are written to `bingo-site/findbingo/`, which the
  Ohio-Bingo repository mirrors and Cloudflare serves at https://www.findbingo.org/ (see
  docs/FINDBINGO.md).
- `data.json` (the lists) and `zips.json` (ZIP code points for every state and DC) are loaded by the
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
    page = page.replace('</body>', place_map.script(root) + '<script>' + analytics + '</script></body>', 1)
    # Tell search engines what the site is and who publishes it. No Event markup: the lists hold weekly
    # schedules, not dated events.
    publisher = {'@type': 'Organization', 'name': 'Veteran Home Guardians', 'url': 'https://www.vethomeguard.org/',
                 'logo': SITE + '/ohio/assets/vhg-logo.png', 'email': EMAIL}
    page = page.replace('</head>', _json_ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Find Bingo',
                                             'alternateName': 'FindBingo.org', 'url': SITE + '/', 'inLanguage': 'en-US',
                                             'publisher': publisher}) + '\n</head>', 1)
    # Featured events have their own styles on the home page and every state page.
    page = page.replace('</style>', EVENT_CSS + '</style>', 1)
    style = re.search(r'<style>.*?</style>', page, re.S).group(0).replace('</style>', STATE_CSS + '</style>')
    today = generated_on
    pages = {}
    for s in states:
        if s['code'] == 'OH':
            continue
        if s['coverage'] == 'licenses':
            rows = [r for r in licensed if r['state'] == s['code'] and r.get('license_expires', today) >= today]
        else:
            rows = [v for v in venues if v['state'] == s['code']]
        pages[SLUGS[s['code']] + '/index.html'] = _state_page(s, states, rows, style, analytics, generated_on, _ads_for(ads, SLUGS[s['code']]),
                                                              [e for e in upcoming_events(events, generated_on) if e['state'] == s['code']])
    pages['privacy/index.html'] = _info_page('privacy', *PRIVACY, style, analytics, generated_on)
    pages['about/index.html'] = _info_page('about', *ABOUT, style, analytics, generated_on)
    pages['terms/index.html'] = _info_page('terms', *TERMS, style, analytics, generated_on)
    pages['advertise/index.html'] = _info_page('advertise', *ADVERTISE, style, analytics, generated_on)
    pages['learn/index.html'] = _info_page('learn', *LEARN, style, analytics, generated_on)
    pages['halls/index.html'] = _info_page('halls', *halls_page(states), style, analytics, generated_on)
    # Ad pictures are served beside the pages, in ads/.
    pages.update({'ads/' + a['image'].rsplit('/', 1)[1]: (root / a['image']).read_bytes() for a in ads if a.get('image')})
    site = {
        # Google Search Console ownership file for https://www.findbingo.org/ (owner direction, Nov 16, 2026).
        # Keep it: Google rechecks the file, and removing it drops verification.
        'googleae90b5079bda9bbc.html': 'google-site-verification: googleae90b5079bda9bbc.html',
        'index.html': page,
        'data.json': data_json + '\n',
        'zips.json': json.dumps(zips, separators=(',', ':')) + '\n',
        **pages,
        # The map files (Leaflet), served from the site itself; place-map.js loads them only when a list has pins.
        **place_map.vendor_files(root, 'assets/map/'),
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
SLUGS = {code: name.lower().replace(' ', '-') for code, name in STATES.items()}
# Ohio's page is the Ohio Bingo Finder (built by bingo_site.py); the rest are built here.
STATE_PAGES = tuple(slug + '/' for code, slug in SLUGS.items() if code != 'OH')


def indexed_state_pages(root):
    """State pages that belong in the sitemap: every state except Ohio (listed with its finder) and pending ones."""
    states = json.loads((root / 'data/public/bingo-states.json').read_text())
    return tuple(SLUGS[s['code']] + '/' for s in states if s['code'] != 'OH' and s['coverage'] != 'pending')


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


def _area(county, short=False):
    # Virginia's independent cities are not in any county. They are stored the Census way ("Richmond city").
    if county.endswith(' city'):
        return 'City of ' + county[:-5]
    return county if short else county + ' County'


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
        f'<li data-day="{x["day"]}"><strong>{DAY_NAMES[x["day"]]}</strong>, {escape(_time_range(x["start"], x.get("end")))}'
        + (f' <span class="org">· {escape(x["label"])}</span>' if x.get('label') else '')
        + (f' <span class="org">· {escape(x["organization"])}</span>' if many else '') + '</li>' for x in v['sessions'])
    if v.get('phone'):
        call = f'<a class="solid" href="tel:{re.sub(r"[^0-9]", "", v["phone"])}">{_ic("phone")}Call {escape(v["phone"])}</a>'
    else:
        call = f'<a class="solid" href="{escape(_maps(v["name"] + " " + v["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("search")}Look up phone number ↗</a>'
    source = _out(v['source_url'], v['source_label']) if v.get('source_url') else _out(s['list_url'], s['list_label'])
    kind = 'Senior center bingo' if v.get('kind') == 'senior_center' else 'Bingo'
    days = ', '.join(dict.fromkeys(DAY_NAMES[x['day']] for x in v['sessions']))
    return (f'<article id="{escape(v["id"])}"{_pin(v, "game", kind + " · " + v["city"] + (" · " + days if days else ""))}><p><span class="badge">{kind}</span></p>'
            f'<h3>{escape(v["name"])}</h3><p class="where">{_ic("pin")}{escape(v["city"])}</p>'
            + (f'<p class="small">{escape(v["audience"])}</p>' if v.get('audience') else '')
            + f'<div class="when"><p>{_ic("cal")}<strong>Bingo days:</strong></p><ul class="sessions"{"" if v.get("schedule_note") else " data-weekly"}>{sessions}</ul>'
            f'<p class="note">{escape(v.get("schedule_note") or s.get("hours_note") or "Call ahead to confirm before you go.")}</p></div>'
            f'<div class="big-actions">{call}<a class="outline" href="{escape(_maps(v["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("route")}Directions ↗</a></div>'
            f'<p class="address">{escape(v["address"])} · {escape(_area(v["county"]))}</p>'
            + (f'<p class="small">{escape(v["hours"])}</p>' if v.get('hours') else '')
            + (f'<p class="small">Bingo here is run by {escape(", ".join(v["organizations"]))}.</p>' if many else '')
            + f'<details class="sources"><summary>Where this comes from · checked {_date_label(v["reviewed_on"])}</summary><p>{source}</p>'
            + ''.join(f'<p>{escape(n)}</p>' for n in v.get('notes', [])) + '</details>'
            f'<p class="small-links"><a href="{escape(_report(v))}">Report a change</a></p></article>')


def _licensed_html(r, s):
    return (f'<article id="{escape(r["id"])}"{_pin(r, "nodays", "Licensed for bingo, game days not posted · " + r["city"])}><p><span class="badge muted">{escape(s.get("license_badge", LICENSE_BADGE))}</span></p>'
            f'<h3>{escape(r["name"])}</h3><p class="where">{_ic("pin")}{escape(r["city"])}</p>'
            + '<div class="big-actions">' + (f'<a class="solid" href="tel:{re.sub(r"[^0-9]", "", r["phone"])}">{_ic("phone")}Call {escape(r["phone"])}</a>' if r.get('phone') else
                                             f'<a class="solid" href="{escape(_maps(r["name"] + " " + r["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("search")}Look up phone number ↗</a>')
            + f'<a class="outline" href="{escape(_maps(r["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("route")}Directions ↗</a></div>'
            f'<p class="address">{escape(r["address"])} · {escape(_area(r["county"]))}</p>'
            f'<details class="sources"><summary>Where this comes from · checked {_date_label(r["reviewed_on"])}</summary>'
            f'<p>{escape(_license_line(r, s))}</p>'
            f'<p>{_out(s["list_url"], s["list_label"])}</p></details>'
            f'<p class="small-links"><a href="{escape(_report(r))}">Send us their game days</a></p></article>')


LICENSE_BADGE = 'Licensed for bingo · game days not posted'


def _pin(r, kind, sub):
    """Map pin attributes: the middle of the card's ZIP code (from the ZIP code points), or nothing."""
    at = ZIP_POINTS.get(r.get('zip'))
    if not at:
        return ''
    return f' data-pm-lat="{at[0]}" data-pm-lon="{at[1]}" data-pm-at="zip" data-pm-kind="{kind}" data-pm-sub="{escape(sub)}"'


def _map_box(up, what):
    """The map above a list. Group dots on the map show how many places they hold (owner direction, November 23, 2026);
    the page text still never states counts."""
    return place_map.box('results' if not up else 'listings', up + 'assets/map/', title='See them on a map',
                         label=f'Map of {what}. Every place on the map is also in the list.',
                         legend=(('game', 'Bingo with game days'), ('nodays', 'Licensed, game days not posted')) + ((('you', 'Your ZIP code'),) if not up else ()),
                         privacy_href=up + 'privacy/', zip_table='ZIPS' if not up else '', numbers=True, dark=True)


def _license_line(r, s):
    if r.get('license_number'):
        line = f'{s["name"]} license {r["license_number"]} ({r["license_type"]})'
    else:
        line = f'On {s["name"]}’s list, with a {r["license_type"]}'
    return line + (f', on the state list through {_date_label(r["license_expires"])}.' if r.get('license_expires') else '.')


HALL_MONEY = ('must_give', 'may_give', 'own')


def _rule_links(h):
    return ' · '.join(_out(x['url'], x['scope'].split(': ')[0]) for x in h['sources'])


def _hall_offers(up):
    """What Find Bingo offers every hall, in every state. Prices live on the Advertise page only."""
    return ('<ul><li><strong>Your listing is free, always.</strong> No hall can pay for a better one.</li>'
            '<li><strong>Help getting the word out.</strong> Free tips, and paid advertising on Find Bingo if you want more.</li>'
            f'<li><strong>Featured events.</strong> Put a special bingo night in its own box for people searching near you. <a href="{up}advertise/">How featured events work</a></li>'
            f'<li><strong>A game site for your hall.</strong> We build it, host it and keep it current from the updates you send us, for one flat monthly fee. You get a page to put on flyers, signs and social media. <a href="{up}advertise/">Details</a></li></ul>')


# The pitch follows the state's own rule on where bingo money goes (owner direction, November 20, 2026).
HALL_PITCH = {
    'own': 'In {name} that money stays with your group for its own causes, so we never ask for a share of it. What we offer is help filling seats:',
    'may_give': 'If your group would like a partner cause, we can help you find a local one. Partnering is never required to be listed. What we offer every hall:',
    'must_give': 'If your group has to give part of its bingo money to another charity, we can help you find a local partner charity. Partnering is never required to be listed. What we offer every hall:',
}


def _send_times(s, up='../'):
    name = escape(s['name'])
    h = s.get('halls')
    body = (f'<section class="panel" id="run-a-game" aria-labelledby="run-title"><h2 id="run-title">Run a bingo game in {name}? Get it listed free</h2>'
            '<p>Send us the name of your hall, the address, the days and the time the first game starts. A phone number for players helps too. '
            'Listing is free, and we never sell or share your information.</p>'
            f'<div class="big-actions"><a class="solid" href="{escape(_mailto("Bingo game times in " + s["name"], "Hall or group name:" + chr(10) + "Address:" + chr(10) + "Days and first game time:" + chr(10) + "Phone for players:" + chr(10) + "Website or Facebook page:" + chr(10)))}">Email your game times</a></div>')
    if h:
        body += f'<h3>What {name} law says about your bingo money</h3><p id="money-rule">{escape(h["money_note"])}</p>'
        if h.get('ad_note'):
            body += f'<h3>Advertising your game in {name}</h3><p id="ad-rule">{escape(h["ad_note"])}</p>'
        body += f'<p class="small">Checked {_date_label(max(x["reviewed_on"] for x in h["sources"]))}. Sources: {_rule_links(h)}. This is a summary, not legal advice; your regulator has the final word.</p>'
        if s.get('partner'):
            body += (f'<p>We also ask every {name} hall to consider supporting our local partner, '
                     + ('the ' if s['partner'].get('the') else '') + f'<a href="#partner">{escape(s["partner"]["name"])}</a>. It is never a condition of being listed.</p>')
        body += f'<p>{escape(HALL_PITCH[h["money"]].format(name=s["name"]))}</p>'
    else:
        body += '<h3>More help for your hall</h3><p>Beyond the free listing:</p>'
    body += _hall_offers(up) + f'<p><a href="{up}halls/">Help for bingo halls, state by state</a></p></section>'
    return body


def _partner_panel(s):
    """The state's local partner and the standing ask to its halls (owner direction, November 22, 2026).

    Outside Ohio, Travis would rather bingo support go to a local group doing work like Veteran Home Guardians than
    to Ohio. The ask is standing, voluntary and written to the state's own rule on bingo money; it never touches
    which games are listed or their order."""
    p = s.get('partner')
    if not p:
        return ''
    name, who = escape(s['name']), escape(p['name'])
    called = ('the ' if p.get('the') else '') + who  # "the Mobility Independence Foundation" mid-sentence
    actions = f'<a class="solid" href="{escape(p["url"])}" target="_blank" rel="noopener noreferrer">Visit {who} ↗</a>'
    if p.get('donate_url'):
        actions += f'<a href="{escape(p["donate_url"])}" target="_blank" rel="noopener noreferrer">Give to {who} ↗</a>'
    actions += f'<a href="{escape(_mailto("Supporting " + p["name"] + " in " + s["name"], "Hall or group name:" + chr(10) + "Town:" + chr(10) + "What we did or are planning:" + chr(10)))}">Tell us what your hall did</a>'
    return (f'<section class="panel" id="partner" aria-labelledby="partner-title"><h2 id="partner-title">Our {name} partner: {who}</h2>'
            f'<p>{escape(p["about"])}</p>'
            f'<p>Find Bingo asks every {name} hall and bingo group to consider supporting {called}. It is a standing request, never a '
            'condition of being listed, and it never changes which games appear here or their order. Ways to help:</p>'
            '<ul>' + ''.join(f'<li>{escape(w)}</li>' for w in p['ways']) + '</ul>'
            + (f'<p class="note">{escape(p["note"])}</p>' if p.get('note') else '')
            + f'<div class="big-actions">{actions}</div>'
            f'<p class="small">Our partner since {_date_label(p["since"])}. Sources: {_rule_links(p)}. Follow your own license and your state’s rules; '
            f'<a href="#money-rule">what {name} law says about bingo money</a>.</p></section>')


def halls_page(states):
    """findbingo.org/halls/: the page for the people who run bingo (owner direction, November 20, 2026)."""
    checked = [s for s in states if s.get('halls')]
    rows = ''
    for s in checked:
        h = s['halls']
        link = '../ohio/' if s['code'] == 'OH' else f'../{SLUGS[s["code"]]}/#run-a-game'
        rows += (f'<h3 id="rules-{s["code"].lower()}"><a href="{link}">{escape(s["name"])}</a></h3><p>{escape(h["money_note"])}</p>'
                 + (f'<p><strong>Ads:</strong> {escape(h["ad_note"])}</p>' if h.get('ad_note') else '')
                 + f'<p class="small">Checked {_date_label(max(x["reviewed_on"] for x in h["sources"]))}. Sources: {_rule_links(h)}</p>')
    rest = ', '.join(f'<a href="../{SLUGS[s["code"]]}/#run-a-game">{escape(s["name"])}</a>' for s in states if not s.get('halls') and s['code'] != 'OH')

    with_partner = [s for s in states if s.get('partner')]
    partners = ''
    if with_partner:
        partners = ('<h2 id="partners">Local partners, state by state</h2>'
                    '<p>Outside Ohio we would rather bingo support stay close to home, with the groups already doing the work there. '
                    'In these states we name a local partner and ask halls to consider supporting it, in whatever way their own rules allow. '
                    'It is never a condition of being listed.</p><ul>'
                    + ''.join(f'<li id="partner-{s["code"].lower()}"><strong>{escape(s["name"])}:</strong> '
                              f'<a href="../{SLUGS[s["code"]]}/#partner">{escape(s["partner"]["name"])}</a></li>' for s in with_partner)
                    + '</ul><p>Know a nonprofit in your state that helps veterans, older adults or people with disabilities stay connected and independent? '
                    f'<a href="{escape(_mailto("A local partner for Find Bingo", "Organization:" + chr(10) + "State:" + chr(10) + "Website:" + chr(10) + "What they do:" + chr(10)))}">Tell us about them</a>.</p>')

    def named(money):
        names = [s['name'] for s in checked if s['halls']['money'] == money]
        return escape(', '.join(names[:-1]) + ' and ' + names[-1] if len(names) > 1 else names[0])
    body = ('<p>Players come here to find a game. Halls and the groups that run them come here to be found. Every listing is free, and '
            'the help below is shaped to what your state allows.</p>'
            '<h2>What we offer every hall</h2>' + _hall_offers('../')
            + '<div class="big-actions"><a class="solid" href="'
            + escape(_mailto('Help for our bingo hall', 'Hall or group name:\nState and town:\nWhat would help most:\nBest way to reach us:\n'))
            + '">Talk with us about your hall</a></div>'
            '<h2>Partnering with a charity, where your state’s rules allow</h2>'
            '<p>States treat bingo money in three different ways, and we only ask for what fits:</p>'
            '<ul><li><strong>The law requires some groups to give to an outside charity</strong> (' + named('must_give') + '). '
            'In Ohio, where Veteran Home Guardians works, a hall can name us as one of its recipients. We ask for a modest share of that required gift, usually 5 to 10 percent, not all of it. '
            '<a href="../ohio/partners.html#sponsors">How partnership works in Ohio</a> Elsewhere, we help you find a local partner charity first.</li>'
            '<li><strong>The law lets a group give to other causes</strong> (' + named('may_give') + '). If you want a partner cause, we help you find a local one first.</li>'
            '<li><strong>The money stays with your group</strong> (' + named('own') + '). We never ask for a share. We help you reach players instead.</li></ul>'
            + partners +
            '<h2>State rules we have checked</h2><p>Plain-language summaries with their sources. This is not legal advice; your state regulator has the final word.</p>'
            + rows
            + '<h2>Every other state</h2><p>We have not summarized these states’ rules yet. Each state page names who licenses bingo there and how to send us your game times: '
            + rest + '.</p>'
            '<h2>Bingo suppliers and distributors</h2><p>Paper, electronics, pull-tabs, daubers, software: if you sell to halls, you can reach them and their players here with a labeled ad. '
            '<a href="../advertise/">Advertise on Find Bingo</a></p>')
    return ('Help for Bingo Halls: Free Listings, Advertising and State Rules | FindBingo.org',
            'For the groups that run bingo: free listings, help reaching players, featured events, and plain-language summaries of each state’s rules on bingo money and advertising.',
            'Help for bingo halls',
            'Free listings, help reaching players, and your state’s rules on bingo money and ads, in plain language.',
            body)


STATE_COPY = {
    # coverage: (title, description, lead). {name} is the state's name.
    'times': ('{name} Bingo Near You: Weekly Bingo Halls, Days and Times | FindBingo.org',
              'Free list of weekly bingo in {name}, by county, with game days, hours, directions and a phone lookup. Type your ZIP code to see bingo near you, closest first.',
              'Weekly bingo halls in {name}, by county, with the days and hours. Call ahead before you go.'),
    'licenses': ('{name} Bingo: Licensed for Bingo, by County | FindBingo.org',
                 'Free list of {name} groups and places with a current state license or permit for bingo, by county, with directions and a phone lookup. Type your ZIP code to see bingo near you.',
                 'Groups and places in {name} with a current state license or permit for bingo, by county. The state list does not show game days, so call before you go.'),
    'starter': ('{name} Bingo: Where to Play, Days and Times | FindBingo.org',
                'Free list of bingo games in {name} from places that publish their own schedules, with days, times, phone numbers and directions. Halls can add their games free.',
                'Bingo in {name} from places that publish their own schedules. Call ahead before you go.'),
    'pending': ('{name} Bingo: Get Your Game Listed Free | FindBingo.org',
                'FindBingo.org is building a free list of bingo games in {name}. Halls and players can send game days and times to be listed free.',
                'We have not built a {name} list yet. Run a game or know of one? Send us the days and times and we will list it free.'),
    'none': ('{name} Bingo: Finding Games and Getting Your Hall Listed | FindBingo.org',
             'How to find bingo in {name}, who licenses it, and how halls can list their game days free on FindBingo.org.',
             'We are building a list of {name} bingo games. Run a game? Send us your days and times and we will list it free.'),
}


def _state_page(s, states, rows, style, analytics, generated_on, ads=(), events=()):
    code, name, slug = s['code'], s['name'], SLUGS[s['code']]
    title, description, lead = (t.format(name=name) for t in STATE_COPY[s['coverage']])
    if s['coverage'] == 'none' and s.get('list_url'):
        lead = f'{name}’s official bingo list or lookup is linked below. Run a game? Send us your days and times and we will list it free.'
    description, lead = s.get('description', description), s.get('lead', lead)
    url = f'{SITE}/{slug}/'
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Find Bingo', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': f'Bingo in {name}', 'item': url}]}
    rows = sorted(rows, key=lambda r: (r['county'], r['city'], r['name']))
    counties = sorted({r['county'] for r in rows})
    pending = s['coverage'] == 'pending'
    body = f'<p class="intro">{escape(s["about"])}' + ('' if pending else ' ' + escape(s["regulator_note"])) + '</p>'
    if s.get('pending_counties'):
        c = s['pending_counties']
        listed = ', '.join(c[:-1]) + ' and ' + c[-1] if len(c) > 1 else c[0]
        body += (f'<p class="note" id="pending-{code}">Our {escape(name)} list does not include {escape(listed)} '
                 f'{"counties" if len(c) > 1 else "County"} yet. For games there, use {_out(s["list_url"], "the state’s own lookup")}.</p>')
    if s['coverage'] == 'licenses':
        body += f'<p class="note">{escape(s["license_note"])}</p>'
    if s['coverage'] == 'none' and s.get('list_url'):
        # No list loaded here yet, but the state publishes one: lead with it.
        body += (f'<div class="big-actions" id="official-list"><a class="solid" href="{escape(s["list_url"])}" target="_blank" '
                 f'rel="noopener noreferrer">{escape(s["list_label"])} ↗</a></div>')
    # Paid featured events sit in their own labeled box, above the county list and never inside the listings.
    body += events_html(events, '../')
    if len(counties) > 1:
        body += (f'<nav class="counties" aria-labelledby="counties-title"><h2 id="counties-title">Jump to your county{" or city" if any(c.endswith(" city") for c in counties) else ""}</h2><ul>'
                 + ''.join(f'<li><a href="#county-{_slug(c)}">{escape(_area(c, short=True))}</a></li>' for c in counties) + '</ul></nav>')
    if rows:
        card = _licensed_html if s['coverage'] == 'licenses' else _venue_html
        if any(r['zip'] in ZIP_POINTS for r in rows):
            body += _map_box('../', f'the {name} bingo listed below')
        body += '<div id="listings">' + ''.join(
            f'<section aria-labelledby="county-{_slug(c)}"><h2 id="county-{_slug(c)}">{escape(_area(c))}</h2><div class="grid">'
            + ''.join(card(r, s) for r in rows if r['county'] == c) + '</div><p class="top"><a href="#top">Back to the top</a></p></section>'
            for c in counties) + '</div>'
    else:
        body += (f'<div id="listings"><p class="empty">We have not listed any {escape(name)} games yet. '
                 'If you know of one, please tell us about it below.</p></div>')
    # At most one ad place per state page: after the listings, never inside them or above them.
    body += _ad_html(ads, '../')
    body += _partner_panel(s)
    body += _send_times(s)
    pairs = []
    for u, label in ((s.get('list_url'), s.get('list_label')), (s.get('regulator_url'), s.get('regulator_label'))):
        if u and u not in [p[0] for p in pairs]:
            pairs.append((u, label))
    as_of = f' (list dated {_date_label(s["list_as_of"])})' if s.get('list_as_of') else ''
    body += (f'<section class="panel" id="about" aria-labelledby="about-title"><h2 id="about-title">Where this list comes from</h2>'
             + ('<p>Listings come from halls and players who write to us, and from schedules that organizers publish. Each listing will show its own source.</p>' if pending else
                f'<p>Checked {_date_label(s["reviewed_on"])}{as_of}. Sources: {" · ".join(_out(u, l) for u, l in pairs)}</p>') +
             '<p>Game days and hours can change, especially around holidays. Call ahead before you go, and ask about parking, steps and seating if that matters for you.</p></section>')
    others = ''.join(f'<a href="../{SLUGS[o["code"]]}/">{escape(o["name"])}</a>' for o in states if o['code'] != code)
    zip_form = ('<form class="zip-box" action="../" method="get"><div class="tools">'
                '<div><label for="zip">Type your ZIP code</label><input id="zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" pattern="[0-9]{5}" placeholder="Your 5-digit ZIP" required></div>'
                '<div><label for="radius">How far will you go?</label><select id="radius" name="radius"><option value="10">10 miles</option><option value="25" selected>25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>'
                f'<div><button class="primary" type="submit">{_ic("search")}Find bingo near me</button></div></div>'
                '<p class="small">Shows bingo near you in every state we cover, closest first.</p></form>')
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            # A page with no listings and no state research stays out of search results until it has something to say.
            + ('<meta name="robots" content="noindex,follow">\n' if pending else '')
            + f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(f"Bingo in {name}")}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n' + _json_ld(crumbs) + '\n</head>')
    weekly = 'data-weekly' in body
    return (head + f'<body id="top">{ICONS}<a class="skip" href="#listings">Skip to the bingo list</a>'
            f'<header>{BALLS}<p class="brand"><a href="../">FindBingo.org</a> · free from Veteran Home Guardians</p><h1>Bingo in {escape(name)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main>{zip_form}{body}'
            f'<nav class="states" aria-labelledby="states-title"><h2 id="states-title">Bingo in other states</h2><div class="state-buttons">{others}</div>'
            '<p class="small-links"><a href="../">Search every state by ZIP code</a></p></nav></main>'
            f'{_footer(generated_on)}{TODAY_SCRIPT if weekly else ""}{place_map.script() if "pm-box" in body else ""}<script>{analytics}</script></body></html>\n')


def _json_ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def _footer(generated_on, up='../'):
    return ('<footer><p>FindBingo.org is a free community resource from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>. '
            'Listings are free. Ads, when shown, are labeled and never decide which games are listed.</p>'
            '<p class="noprint">Need help getting to the game? <a href="https://mobilitytalk.org/states/">Mobility Talk</a> lists mobility and disability resources in every state.</p>'
            f'<p class="noprint">Questions or corrections: <a href="mailto:{EMAIL}?subject=FindBingo.org">{EMAIL}</a> · Made by <a href="https://travisvought.com/">Travis Vought</a></p>'
            f'<p class="noprint"><a href="{up}learn/">How bingo works: a free bingo class</a> · <a href="{up}about/">About and contact</a> · <a href="{up}privacy/">Privacy</a> · <a href="{up}terms/">Terms of use</a> · <a href="{up}advertise/">Advertise on Find Bingo</a> · <a href="{up}halls/">For bingo halls</a></p>'
            f'<p class="noprint">Lists updated {_date_label(generated_on)}.</p></footer>')


# Short addresses for posters and word of mouth: findbingo.org/mi and /MI open the Michigan page.
SHORT_REDIRECTS = ''.join(f'/{c} /{slug}/ 301\n/{c.lower()} /{slug}/ 301\n' for c, slug in SLUGS.items() if c != 'OH')
STATE_CSS = ('header a{color:#fff}.intro{font-size:20px;max-width:860px}'
             '.counties{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}.counties h2{font-size:24px;margin:10px 0 8px}'
             '.counties ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
             '.counties a{display:inline-flex;align-items:center;min-height:48px;padding:0 14px;border:2px solid var(--accent);border-radius:24px;color:var(--accent);font-weight:700;text-decoration:none}'
             '#listings>section>h2{font-size:28px;margin:28px 0 10px;scroll-margin-top:12px}.top{font-size:17px;margin:10px 0 0}.top a{display:inline-flex;align-items:center;min-height:44px}'
             '@media print{.counties,.top,#run-a-game,#partner{display:none!important}}')


# ---- Ads (owner direction, November 19, 2026: Find Bingo may carry advertising) -----------------------
# data/findbingo-ads.json is a list, empty by default. With no ad running for a place, the page has no ad
# markup at all. Each ad: slot ("home", "state" for every state page, or "state:michigan" for one state),
# sponsor, text, url, and optionally image (a file under assets/, served from ads/), alt (needed with an
# image), start and end (YYYY-MM-DD, Eastern time, both days included). Ads never touch the listings.
# ---- Featured bingo events (paid) -----------------------------------------------------------------------
# Owner direction, November 20, 2026: a hall or group can have a dated bingo event featured for $100. It shows
# in its own box labeled "Featured event" for ZIP searches near it, on its state's page (and Ohio's finder),
# from when it is added until the day of the event. It never adds to, removes or reorders the free listings.
# Add one to data/findbingo-events.json only after it is paid; record the payment date in paid_on.
EVENTS_FILE = 'data/findbingo-events.json'
EVENT_PRICE = 100
EVENT_KEYS = {'id', 'title', 'host', 'address', 'city', 'state', 'zip', 'date', 'start', 'end', 'details', 'url', 'phone', 'paid_on'}
EVENT_REQUIRED = ('id', 'title', 'host', 'address', 'city', 'state', 'zip', 'date', 'start', 'details', 'paid_on')
EVENT_PUBLIC = ('id', 'title', 'host', 'address', 'city', 'state', 'zip', 'date', 'start', 'end', 'details', 'url', 'phone')
EVENT_CSS = ('.featured-events{background:#fff8e6;border:2px solid #d9b45a;border-radius:14px;padding:8px 20px 16px;margin:18px 0}'
             '.featured-events[hidden]{display:none}.featured-events h2{font-size:26px;margin:6px 0 10px}'
             '.featured-events .ad-label{margin:6px 0 0;font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#6b5414}'
             '.featured-events article{background:#fff;border:1px solid #e2c98a;border-radius:12px;padding:14px 16px;margin:0 0 12px}'
             '.featured-events article[hidden]{display:none}.featured-events h3{font-size:23px;margin:4px 0}.featured-events p{margin:6px 0}')
# Hides an event once its day has passed (Eastern time), and the box once every event in it has passed.
EVENT_DATES_SCRIPT = ("<script>(function(){var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()),"
                      "g=function(t){return p.find(function(x){return x.type===t}).value},d=g('year')+'-'+g('month')+'-'+g('day');"
                      "document.querySelectorAll('.featured-events').forEach(function(s){var n=0;s.querySelectorAll('article[data-date]').forEach(function(a){"
                      "a.hidden=a.dataset.date<d;if(!a.hidden)n++});s.hidden=!n})})()</script>")


def load_events(root):
    return json.loads((root / EVENTS_FILE).read_text())


def validate_events(events, zips):
    assert isinstance(events, list), EVENTS_FILE + ' is a list'
    ids = set()
    for e in events:
        assert isinstance(e, dict) and set(e) <= EVENT_KEYS, ('unknown event field', sorted(set(e) - EVENT_KEYS))
        assert all(isinstance(e.get(k), str) and e[k].strip() for k in EVENT_REQUIRED), ('event is missing', [k for k in EVENT_REQUIRED if not e.get(k)])
        assert e['id'] not in ids, ('two events share an id', e['id'])
        ids.add(e['id'])
        assert e['state'] in STATES, e['state']
        assert e['zip'] in zips and _state_of_zip(e['zip']) == e['state'], ('event ZIP must be in its state', e['id'], e['zip'])
        for k in ('date', 'paid_on'):
            assert date.fromisoformat(e[k]).isoformat() == e[k], (k, e[k])
        for k in ('start', 'end'):
            if k in e:
                assert TIME.fullmatch(e[k]), (k, e[k])
        assert len(e['title']) <= 90 and len(e['host']) <= 90 and len(e['details']) <= 200, ('keep events short', e['id'])
        if 'url' in e:
            assert e['url'].startswith('https://'), e['url']
        if 'phone' in e:
            assert PHONE.fullmatch(e['phone']), e['phone']


def upcoming_events(events, today):
    """Events on or after today, soonest first. The pages also hide past events by the visitor's date."""
    return sorted((e for e in events if e['date'] >= today), key=lambda e: (e['date'], e['start'], e['title']))


def events_html(events, up, heading='Featured bingo events'):
    """The labeled box of paid featured events for one page, or nothing when there are none."""
    if not events:
        return ''
    cards = ''
    for e in events:
        links = [f'<a href="{escape(_maps(e["address"] + ", " + e["city"] + ", " + e["state"] + " " + e["zip"]))}" target="_blank" rel="noopener noreferrer">Directions ↗</a>']
        if e.get('phone'):
            links.append(f'<a href="tel:{escape(e["phone"])}">Call {escape(e["phone"])}</a>')
        if e.get('url'):
            links.append(f'<a href="{escape(e["url"])}" target="_blank" rel="sponsored noopener">More about this event ↗</a>')
        cards += (f'<article data-date="{e["date"]}"><h3>{escape(e["title"])}</h3>'
                  f'<p class="when"><strong>{_date_label(e["date"])}</strong>, {escape(_time_range(e["start"], e.get("end")))}</p>'
                  f'<p>{escape(e["host"])}<br>{escape(e["address"])}, {escape(e["city"])}</p><p>{escape(e["details"])}</p>'
                  f'<p>{" · ".join(links)}</p></article>')
    return (f'<section class="featured-events" aria-label="Featured events"><p class="ad-label">Featured events · paid listings</p>'
            f'<h2>{escape(heading)}</h2>{cards}<p class="small"><a href="{up}advertise/#events">Feature your bingo event</a></p></section>'
            + EVENT_DATES_SCRIPT)


ADS_FILE = 'data/findbingo-ads.json'
AD_KEYS = {'slot', 'sponsor', 'text', 'url', 'image', 'alt', 'start', 'end'}
# The bingo class, About, Privacy, Terms, Advertise and halls pages, linked from every footer and listed in the sitemap.
INFO_PAGES = ('learn/', 'about/', 'privacy/', 'terms/', 'advertise/', 'halls/')
# Dated ads are written hidden; this shows the one whose dates include today, so a page built before an ad
# starts or after it ends never shows it on the wrong day. Without JavaScript a dated ad stays hidden.
AD_DATES_SCRIPT = ("<script>(function(){var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()),"
                   "g=function(t){return p.find(function(x){return x.type===t}).value},d=g('year')+'-'+g('month')+'-'+g('day');"
                   "document.querySelectorAll('.ad-slot[data-start],.ad-slot[data-end]').forEach(function(a){"
                   "a.hidden=!((!a.dataset.start||a.dataset.start<=d)&&(!a.dataset.end||d<=a.dataset.end))})})()</script>")


def _ad_window(a):
    return a.get('start', '0000-01-01'), a.get('end', '9999-12-31')


def _ads_for(ads, place):
    """The ads for one page: 'home', or a state page's slug."""
    if place == 'home':
        return [a for a in ads if a['slot'] == 'home']
    return [a for a in ads if a['slot'] in ('state', 'state:' + place)]


def validate_ads(ads, root):
    assert isinstance(ads, list), ADS_FILE + ' is a list'
    slots = {'home', 'state'} | {'state:' + slug for code, slug in SLUGS.items() if code != 'OH'}
    for a in ads:
        assert isinstance(a, dict) and set(a) <= AD_KEYS, a
        assert a.get('slot') in slots, ('ad slot', a.get('slot'))
        assert all(isinstance(a.get(k), str) and a[k].strip() for k in ('sponsor', 'text', 'url')), a
        assert len(a['text']) <= 200 and len(a['sponsor']) <= 80, ('keep ads short', a['sponsor'])
        assert a['url'].startswith('https://'), a['url']
        if 'image' in a:
            assert a['image'].startswith('assets/') and '..' not in a['image'] and (root / a['image']).is_file(), a['image']
            assert re.search(r'\.(png|jpe?g|gif|webp|svg)$', a['image']) and a.get('alt', '').strip(), ('image needs alt text', a['image'])
        else:
            assert 'alt' not in a, a
        for k in ('start', 'end'):
            if k in a:
                assert date.fromisoformat(a[k]).isoformat() == a[k], a[k]
        start, end = _ad_window(a)
        assert start <= end, a
    # Never two ads in one place at the same time: each page has at most one ad showing.
    for place in ['home'] + [slug for code, slug in SLUGS.items() if code != 'OH']:
        here = sorted((_ad_window(a) for a in _ads_for(ads, place)))
        for (_, end), (start, _) in zip(here, here[1:]):
            assert end < start, ('two ads would show at once on', place)
    # Pictures are served from ads/ by file name, so two different files may not share one.
    pictures = {a['image'] for a in ads if a.get('image')}
    assert len(pictures) == len({x.rsplit('/', 1)[1] for x in pictures}), 'two ad pictures share a file name'


def _ad_html(ads, up):
    """The ad for one place, or nothing at all when no ad is running there."""
    out = ''
    for a in ads:
        dated = ''.join(f' data-{k}="{a[k]}"' for k in ('start', 'end') if k in a)
        img = (f'<img src="{escape(up + "ads/" + a["image"].rsplit("/", 1)[1])}" alt="{escape(a["alt"])}" loading="lazy">'
               if a.get('image') else '')
        out += (f'<aside class="ad-slot" aria-label="Advertisement"{dated}{" hidden" if dated else ""}><p class="ad-label">Advertisement</p>'
                f'<a class="ad-body" href="{escape(a["url"])}" target="_blank" rel="sponsored noopener">{img}'
                f'<span class="ad-sponsor">{escape(a["sponsor"])} ↗</span><span class="ad-text">{escape(a["text"])}</span></a></aside>')
    if any('start' in a or 'end' in a for a in ads):
        out += AD_DATES_SCRIPT
    return out


# ---- Privacy and Advertise pages ---------------------------------------------------------------------
POLICY_DATE = 'November 21, 2026'
TERMS_DATE = 'November 22, 2026'


def _info_page(slug, title, description, heading, lead, body, style, analytics, generated_on):
    url = f'{SITE}/{slug}/'
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(heading)}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n</head>')
    return (head + '<body id="top"><a class="skip" href="#main">Skip to the page</a>'
            f'<header>{BALLS}<p class="brand"><a href="../">FindBingo.org</a> · free from Veteran Home Guardians</p><h1>{escape(heading)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main id="main"><div class="info">{body}</div>'
            '<p class="small-links"><a href="../">Find bingo near you</a></p></main>'
            f'{_footer(generated_on)}<script>{analytics}</script></body></html>\n')


def _ext(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'



# The bingo class page (owner direction, November 19, 2026): how a bingo night works, the kinds of games and
# what the words mean, and the unwritten rules, for people new to bingo, many of them older. General
# practice only: state law and each hall's house rules decide the details, and the page says so.
LEARN = (
    'How bingo works: a friendly bingo class | FindBingo.org',
    'New to bingo? A plain-English class: what happens on a bingo night, early birds, specials, coverall and the other kinds of games, and the unwritten rules every regular expects.',
    'Bingo class: how a bingo night works',
    'A friendly guide for new players and anyone coming back after a long time away. Every hall has its own house rules, so treat this as a starting point and ask the hall.',
    '<p><a href="../#play">Want to warm up first? Play a free practice card.</a></p>'
    '<h2>What happens on a bingo night</h2>'
    '<ol><li><strong>Doors open early,</strong> often an hour or two before the first game. People come early to get a seat, buy their cards and have supper from the kitchen.</li>'
    '<li><strong>You buy your cards at the counter.</strong> Most halls sell a <em>pack</em> (also called a package or admission) that covers the regular games. Extra sheets and special games cost extra.</li>'
    '<li><strong>Early birds</strong> are a few warm-up games before the main session. They are usually sold separately.</li>'
    '<li><strong>The caller draws numbered balls</strong> and reads each one out, letter first: “B-7.” The number also lights up on a board or TV screens.</li>'
    '<li><strong>When you have the pattern, you shout “Bingo!”</strong> A worker comes to your seat, reads your numbers back to the caller, and pays you if it checks out.</li>'
    '<li><strong>There is usually a break</strong> halfway through, with the kitchen and other games for sale.</li>'
    '<li><strong>The night ends with the big one,</strong> often a coverall or a jackpot game.</li></ol>'
    '<h2>The card</h2>'
    '<p>An American bingo card has five columns, B, I, N, G and O, and 75 numbers in all. B holds 1 to 15, I holds 16 to 30, N holds 31 to 45, G holds 46 to 60, and O holds 61 to 75. '
    'The middle square is a <strong>free space</strong>: it counts as already marked.</p>'
    '<p>Each card is called a <strong>face</strong>. A paper <strong>sheet</strong> holds several faces, and the number of faces is said with “on”: a <strong>6-on</strong> sheet has six faces, a <strong>12-on</strong> has twelve. '
    'More faces give you more chances, and more to watch. New players do well to start with fewer faces.</p>'
    '<p>Paper cards are marked with a <strong>dauber</strong> (or dabber), a bottle of ink with a sponge tip. Halls sell them, and many players bring their own favorite color. '
    'Some halls still use <strong>hard cards</strong> (reusable cards with sliding windows or chips), and many rent <strong>electronic bingo</strong> handhelds that mark your numbers for you, which helps if your eyes or hands get tired.</p>'
    '<h2>The kinds of games, and what the words mean</h2>'
    '<dl>'
    '<dt><strong>Regular games</strong></dt><dd>The main games of the night, covered by your pack.</dd>'
    '<dt><strong>Pattern</strong></dt><dd>The shape you need to win that game. The caller always says it first, and it is often shown on the board. Listen for it every game.</dd>'
    '<dt><strong>Straight line, or “any line”</strong></dt><dd>Five in a row: across, down, or corner to corner. The free space counts.</dd>'
    '<dt><strong>Four corners, postage stamp, diamond, X, letter patterns</strong></dt><dd>Named shapes. Four corners is the four corner squares. Postage stamp is a block of four squares in a corner. A letter game like “Letter T” asks you to fill that letter on the card.</dd>'
    '<dt><strong>“Crazy” games</strong></dt><dd>The pattern can sit any way around: a crazy T may be upside down or on its side.</dd>'
    '<dt><strong>Two-part or double bingo</strong></dt><dd>You must make two patterns, or the same pattern twice, on one face.</dd>'
    '<dt><strong>Coverall, or blackout</strong></dt><dd>Every square on the face must be marked. It usually pays the most.</dd>'
    '<dt><strong>Jackpot and progressive jackpot</strong></dt><dd>A big prize game. A progressive jackpot must be won within a set number of balls; when nobody does, the prize grows for next time, and a smaller consolation prize is often paid instead.</dd>'
    '<dt><strong>Specials</strong></dt><dd>Extra games sold separately during the night, often on their own colored paper.</dd>'
    '<dt><strong>Quickies</strong></dt><dd>Fast, cheap games, sometimes played between the regular ones.</dd>'
    '<dt><strong>Wild number, or magic number</strong></dt><dd>A number drawn at the start that counts as marked, or that pays extra if someone wins on it. Each hall runs it its own way.</dd>'
    '<dt><strong>Bonanza</strong></dt><dd>Some numbers are drawn ahead of time and posted. You buy a card, mark what is already out, and the rest are called later in the night.</dd>'
    '<dt><strong>U-Pick-’Em</strong></dt><dd>You choose your own numbers on a blank card, a bit like a lottery ticket.</dd>'
    '<dt><strong>Pull-tabs, instant bingo, break-opens, tip boards and seal cards</strong></dt><dd>Paper tickets you open to see whether you won right away. Many halls sell them alongside bingo. They are a separate game from the called numbers.</dd>'
    '<dt><strong>Session</strong></dt><dd>One full set of games on one day. Some halls run an afternoon session and an evening session.</dd>'
    '<dt><strong>90-ball bingo</strong></dt><dd>The British game, with a different card of three rows. American halls almost always play 75-ball bingo.</dd>'
    '</dl>'
    '<h2>The unwritten rules every regular expects</h2>'
    '<ul>'
    '<li><strong>Ask before you sit.</strong> Regulars often sit in the same seats every week, and some halls let people hold seats while others forbid it. A friendly “Is this seat taken?” goes a long way.</li>'
    '<li><strong>Bring cash, and small bills.</strong> Many halls take cash only, for cards, the kitchen and pull-tabs.</li>'
    '<li><strong>Keep it quiet while numbers are called.</strong> Talk between games. Put your phone on silent. People are listening closely, and a missed number can cost someone a win.</li>'
    '<li><strong>Shout “Bingo!” loud and clear, and right away.</strong> At most halls you must call it before the next ball is drawn. If you sit quietly on a win (players call that a “sleeper”), you usually lose it.</li>'
    '<li><strong>Don’t touch your card after you call.</strong> Hold it still until the worker has read it back. If you called by mistake, just say so; it happens to everyone.</li>'
    '<li><strong>Stay quiet while a card is checked.</strong> The caller may ask, “Any other bingos?” If you have one too, speak up then.</li>'
    '<li><strong>Prizes are split.</strong> When two or more people win on the same ball, the prize is usually shared. That is normal, not bad luck.</li>'
    '<li><strong>Be a good sport.</strong> A groan when someone else wins is common, but say congratulations. Never grumble at the caller about the numbers.</li>'
    '<li><strong>Leave other people’s things alone.</strong> Don’t touch another player’s cards, daubers, or lucky charms. Many players take their charms very seriously.</li>'
    '<li><strong>Ask before you tip.</strong> Many charity games are run by volunteers, and some states do not allow workers to take tips. A thank-you is always welcome.</li>'
    '<li><strong>Buy from the kitchen if you can.</strong> At charity bingo, the food and drink help pay for the cause. Ask before bringing your own.</li>'
    '<li><strong>Bring a photo ID.</strong> Halls may check age, and big prizes can need ID and a tax form.</li>'
    '</ul>'
    '<h2>Help for eyes, ears and hands</h2>'
    '<ul><li>Sit where you can see the board or a screen and hear the caller well. Tell a worker if you have trouble hearing; they want you to enjoy the game.</li>'
    '<li>Start with fewer faces. You can always buy more next time.</li>'
    '<li>Ask about electronic handhelds that mark numbers for you, and about large-print cards.</li>'
    '<li>Ask about parking, steps, ramps and restrooms before you go. Our <a href="https://mobilitytalk.org/states/">Mobility Talk</a> site lists help with getting around in every state.</li></ul>'
    '<h2>What changes from state to state</h2>'
    '<p>Each state writes its own bingo law, and each hall adds its own house rules. The things that most often differ:</p>'
    '<ul><li><strong>Age.</strong> Many states require players to be 18. Some let younger people play with a parent or set another age, and a hall can set a higher one.</li>'
    '<li><strong>Who may run games.</strong> Usually charities, churches, veterans’ posts, fire companies and similar groups, and sometimes only for their members and guests.</li>'
    '<li><strong>Prize limits and how often games may run,</strong> such as a top prize per game or a number of sessions a week.</li>'
    '<li><strong>Smoking, alcohol and payment.</strong> Some halls are smoke-free, some serve alcohol, and some states do not let halls take cards for certain games.</li>'
    '<li><strong>Free bingo.</strong> Some places, such as senior centers, play just for fun or small prizes. A few states allow only free bingo.</li></ul>'
    '<p>Every state has its own page on Find Bingo that names who oversees bingo there. <a href="../">Pick your state or type your ZIP code</a> to find it, along with the games near you.</p>'
    '<h2>Ready to play?</h2>'
    '<p>Call the hall before your first visit. Ask what time doors open, how much a pack costs, whether they take cards, and whether there is anything a new player should know. '
    'Most halls are glad to see a new face.</p>'
    '<div class="big-actions"><a class="solid" href="../">Find bingo near you</a></div>'
)

ASK = _mailto('Find Bingo privacy')
PRIVACY = (
    'Privacy | FindBingo.org',
    'How FindBingo.org handles information about your visit: no accounts, no cookies for counting visits, and your ZIP code search stays on your device.',
    'Privacy',
    f'How Find Bingo handles information about your visit. Last updated {POLICY_DATE}.',
    '<h2>The short version</h2>'
    '<ul><li>There are no accounts and no sign-in. We never ask for your name.</li>'
    '<li>We count visits without cookies and without keeping personal information.</li>'
    '<li>Your ZIP code search is worked out on your own phone or computer.</li>'
    '<li>The map pictures come from OpenStreetMap, which sees your internet address and the area on the map.</li>'
    '<li>We do not sell personal information.</li></ul>'
    '<h2>Counting visits</h2>'
    '<p>We use ' + _ext('https://www.goatcounter.com/help/privacy', 'GoatCounter') + ' to count page views, so we know which pages people use. '
    'GoatCounter does not use cookies and does not store personal information. For each page view it records things like the page visited, '
    'the site that sent you here, your browser, your screen size, and an approximate country worked out from your internet (IP) address. '
    'It does not store the IP address.</p>'
    '<p>We leave out everything after the question mark in a page address, so the ZIP code you search for is never counted.</p>'
    '<h2>Your ZIP code search</h2>'
    '<p>When you search by ZIP code, the page finds bingo near you on your own device. It downloads the bingo lists and a list '
    'of ZIP code locations, then works out the distances itself. Ohio’s finder works the same way. The ZIP code is not sent to us or to anyone else to look it up, and we do not keep it.</p>'
    '<p>Your ZIP code does show in the page address (for example, findbingo.org/?zip=48161), so you can bookmark or share a search. '
    'If you search from a state page, or open Ohio’s finder with your ZIP code, your browser asks our web host for that address, '
    'the same way it asks for any web page.</p>'
    '<h2>The map and “Use my location”</h2>'
    '<p>' + place_map.TILE_PRIVACY + 'Read ' + _ext(place_map.TILE_PRIVACY_URL, 'the OpenStreetMap Foundation’s privacy policy') + '. '
    'The map code itself (Leaflet) comes from this site. If you hide the map, your browser remembers that on your device, and the map pictures stop loading.</p>'
    '<p>' + place_map.LOCATION_PRIVACY + '</p>'
    '<h2>Who serves the site</h2>'
    '<p>findbingo.org is served by Cloudflare. Some files, such as the bingo lists, can also load from GitHub Pages, where the site’s code is kept. '
    'Like any web host, Cloudflare and GitHub may keep server logs, including IP addresses, for security. '
    'Read ' + _ext('https://www.cloudflare.com/privacypolicy/', 'Cloudflare’s privacy policy') + ' and '
    + _ext('https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement', 'GitHub’s privacy statement') + '.</p>'
    '<h2>Advertising</h2>'
    '<p>This site may show ads. Every ad is labeled “Advertisement” and kept apart from the game listings. '
    'If we use an ad network such as Google AdSense, it and its partners may use cookies to show ads based on your visits to this and other sites. '
    'You can turn off personalized ads at ' + _ext('https://adssettings.google.com', 'adssettings.google.com')
    + ' and learn more at ' + _ext('https://policies.google.com/technologies/ads', 'policies.google.com/technologies/ads')
    + ', or opt out of many networks at ' + _ext('https://optout.aboutads.info', 'optout.aboutads.info') + '.</p>'
    '<p>Ads never change which games are listed or their order. <a href="../advertise/">About advertising on Find Bingo</a></p>'
    '<h2>Email, calls and directions</h2>'
    '<p>If you email us game times or a correction, we get your email address and what you write. We use it to update the listings and to reply, '
    'and we never sell or share it. The call, phone lookup and directions buttons open your phone or Google Maps, which follow their own privacy rules.</p>'
    '<h2>Children</h2>'
    '<p>Find Bingo is not directed to children under 13, and we do not knowingly collect information from them.</p>'
    '<h2>Questions</h2>'
    '<p>Find Bingo is run by <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, an Ohio nonprofit. '
    f'Questions about privacy: <a href="{escape(ASK)}">{EMAIL}</a>.</p>'
    f'<p class="small">Last updated {POLICY_DATE}.</p>')

# About and contact, and Terms of use (November 22, 2026): the pages an ad network's reviewers look for, and that
# halls and players use to see who runs the site. Plain words; no counts of halls, places or states.
CONTACT = _mailto('FindBingo.org')
ABOUT = (
    'About Find Bingo and how to reach us | FindBingo.org',
    'Who runs FindBingo.org, where the bingo listings come from, how to send a correction, and how to reach us.',
    'About Find Bingo',
    'A free, plain finder for bingo games near you, from Veteran Home Guardians.',
    '<h2>Who runs it</h2>'
    '<p>FindBingo.org is run by <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, an Ohio nonprofit that places veteran visitors in nursing homes. '
    'It is made by <a href="https://travisvought.com/">Travis Vought</a>, a Marine Corps veteran who ran and advertised bingo at his local American Legion for three years.</p>'
    '<h2>Why it exists</h2>'
    '<p>Bingo brings people out of the house and into a room full of neighbors, and many of the people who play are older. '
    'Game times are often hard to find online, so this site gathers them in one place and keeps every listing free. '
    'Halls do not pay to be listed, and an ad never changes which games are listed or their order.</p>'
    '<h2>Where the listings come from</h2>'
    '<p>Each state page names where its list comes from: the state agency that licenses bingo, a list the state publishes, '
    'or the hall’s or group’s own published schedule. Halls and players also send in game times and corrections. '
    'Listings are not confirmed by phone, and games change, so call the hall before you go.</p>'
    '<h2>Send a correction or your game times</h2>'
    '<p>Every listing has a “Report a change” link. Halls can send their game times free, and we post them. '
    '<a href="../halls/">Help for bingo halls</a></p>'
    '<h2 id="contact">Contact us</h2>'
    f'<p>Email <a href="{escape(CONTACT)}">{EMAIL}</a> for questions, corrections, advertising or partnerships. We read every message.</p>'
    '<p><a href="../privacy/">Privacy</a> · <a href="../terms/">Terms of use</a> · <a href="../advertise/">Advertise on Find Bingo</a></p>')

TERMS = (
    'Terms of use | FindBingo.org',
    'The terms for using FindBingo.org: a free bingo directory with no wagering on the site, listings to check with the hall, and labeled ads.',
    'Terms of use',
    f'The plain terms for using Find Bingo. Last updated {TERMS_DATE}.',
    '<h2>What this site is</h2>'
    '<p>FindBingo.org is a free directory of bingo games, run by Veteran Home Guardians. Using the site means you accept these terms.</p>'
    '<h2>No gambling on this site</h2>'
    '<p>Find Bingo does not run games, sell cards, take bets or pay prizes. The practice card is free, just for fun, and wins nothing. '
    'Real games are run by the halls and groups listed, under their state’s law and their own house rules. '
    'Follow the age and other rules where you play.</p>'
    '<h2>Check before you go</h2>'
    '<p>Listings come from state lists, published schedules and people who write in. We work to keep them right, but games change, '
    'and we cannot promise any listing is complete or current. Call the hall before you go. If something is wrong, tell us and we fix it.</p>'
    '<h2>Ads and featured events</h2>'
    '<p>Ads and featured events are labeled. They are paid for by the advertiser, and we do not vouch for what an advertiser offers. '
    'An ad never changes which games are listed or their order. <a href="../advertise/">How advertising works here</a></p>'
    '<h2>Other sites</h2>'
    '<p>Links to halls, state agencies, maps and other sites go to sites we do not run. They have their own terms and privacy rules.</p>'
    '<h2>No warranty</h2>'
    '<p>The site is provided as it is, without any warranty. Veteran Home Guardians is not responsible for a game that was moved, changed or cancelled, '
    'or for anything that happens at a hall.</p>'
    '<h2>Your information</h2>'
    '<p>The <a href="../privacy/">Privacy page</a> says what this site collects and what it does not.</p>'
    '<h2>Changes and questions</h2>'
    f'<p>We may update these terms and will change the date at the top when we do. Questions: <a href="{escape(CONTACT)}">{EMAIL}</a>.</p>')

# Hall game sites (owner direction, November 20, 2026): built by us, updated from what the hall sends, one flat monthly fee.
HALL_SITE_PRICE = 100

ADVERTISE = (
    'Advertise on Find Bingo | FindBingo.org',
    'Reach bingo players, families and activity staff with a labeled ad on FindBingo.org. Ads sit apart from the listings and never change them.',
    'Advertise on Find Bingo',
    'Reach people looking for bingo near them: players, their families, and the activity staff who plan outings.',
    '<h2>Who can advertise</h2>'
    '<p>Bingo halls and the groups that run games first of all, then bingo suppliers, local businesses, senior services, senior living and home care, transportation, and community events. '
    'If your business is a good fit for bingo players and their families, write to us.</p>'
    '<h2 id="events">Feature your bingo event: $' + str(EVENT_PRICE) + '</h2>'
    '<p>Running a special bingo night, a fundraiser or a holiday game? For $' + str(EVENT_PRICE) + ' we feature it in its own box, labeled “Featured event,” '
    'for people who search near your hall and on your state’s page, from the day it goes up until the day of the event.</p>'
    '<ul><li>The event must be run by a group allowed to hold bingo where it takes place.</li>'
    '<li>A featured event never adds to, removes or reorders the free game listings. Your hall’s weekly games stay listed free either way.</li>'
    '<li>Send the event name, your hall or group, the address, date and start time, a short description (up to 200 characters), and a link or phone number. '
    'We confirm the details and send an invoice.</li></ul>'
    '<div class="big-actions"><a class="solid" href="'
    + escape(_mailto('Feature a bingo event on Find Bingo', 'Event name:\nHall or group:\nAddress:\nDate and start time:\nShort description:\nLink or phone for players:\n'))
    + '">Email us about your event</a></div>'
    '<h2 id="hall-site">A game site for your hall: $' + str(HALL_SITE_PRICE) + ' a month</h2>'
    '<p>Want a website for your games that you can put on flyers, signs, Facebook and billboards? We build it for you. '
    'After that, send us your updates by email or text (new times, specials, holiday closings, flyers) and we post them.</p>'
    '<ul><li>One flat fee of $' + str(HALL_SITE_PRICE) + ' a month covers the site, its hosting and the updates you send.</li>'
    '<li>Your games stay listed free on Find Bingo whether or not you have a site with us.</li>'
    '<li>Stop any time.</li></ul>'
    '<div class="big-actions"><a class="solid" href="'
    + escape(_mailto('A game site for our bingo hall', 'Hall or group name:\nState and town:\nWhat should the site show:\nBest way to reach us:\n'))
    + '">Ask about a site for your hall</a></div>'
    '<h2>For bingo halls</h2>'
    '<p>Every hall’s listing is free, always. Beyond that, choose what fits your hall:</p>'
    '<ul><li><strong>Community partner (Ohio).</strong> In Ohio, veteran, fraternal and sporting groups must give part of their instant bingo profit to an outside charity, and can name Veteran Home Guardians as one of their recipients. '
    'We ask for a modest share, usually 5 to 10 percent of what you give, not all of it. At minimum, it should cover visits to veterans in nursing homes in your county. '
    'Anything beyond that helps us reach counties that have no local support. <a href="../ohio/partners.html#sponsors">How partnership works</a> '
    'Other states treat bingo money differently, and we only offer what fits your state’s rules. <a href="../halls/">Help for halls, state by state</a></li>'
    '<li><strong>Featured events,</strong> above.</li>'
    '<li><strong>A game site for your hall,</strong> above. Many halls would rather pay for a service than partner, and that is fine.</li>'
    '<li><strong>Advertising.</strong> Free tips on getting the word out, or paid advertising if you want more.</li></ul>'
    '<p>Every hall is different, so let’s talk.</p>'
    '<h2>Ground rules</h2>'
    '<ul><li>Every ad is labeled “Advertisement.” Every featured event is labeled “Featured event.”</li>'
    '<li>Ads sit apart from the game listings: on the home page below the search results, and on state pages after the listings. Never inside them. '
    'Featured events sit in their own box above the results, never inside them.</li>'
    '<li>Ads never add, remove, change or reorder listings. A hall cannot pay for a better listing, and every listing stays free.</li>'
    '<li>We review every ad before it runs, and we turn down ads that are misleading.</li></ul>'
    '<h2>Where the money goes</h2>'
    '<p>Ad income supports <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, the Ohio nonprofit that runs Find Bingo '
    'and visits veterans in nursing homes.</p>'
    '<h2>Get in touch</h2>'
    '<p>Tell us your business name, what you would like to advertise, and the states or towns you want to reach.</p>'
    '<div class="big-actions"><a class="solid" href="'
    + escape(_mailto('Advertising on Find Bingo', 'Business name:\nWhat we would like to advertise:\nStates or towns:\nWebsite:\nBest way to reach us:\n'))
    + f'">Email us about an ad</a></div><p class="small">Or write to {EMAIL}. '
    '<a href="../privacy/">How ads and privacy work on this site</a></p>')
