"""Build FindBingo.org (findbingo-site/): bingo near you, state by state.

index.html is the whole page (markup, styles and script). The build also writes it to
bingo-site/findbingo/, which the Ohio-Bingo repository mirrors and Cloudflare serves at
www.findbingo.org. It loads data.json and zips.json from beside itself, then from the guide's GitHub
Pages site. The Ohio finder is built by bingo_site.py into bingo-site/findbingo/ohio/, so it is served
from the same site at findbingo.org/ohio/; this page links to it rather than copying Ohio data.
"""
import json
import re
from collections import Counter
from datetime import date
from html import escape
from urllib.parse import quote
import place_map
from visuals import locator
from bingo_edition import ohio_records

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
# Virginia's directory of sessions, Missouri's Find Local Bingo Games page and Wisconsin's Active Bingo Occasion Search.
TIMES_FILES = {'MI': 'michigan-weekly-bingo.json', 'TX': 'texas-bingo-halls.json', 'VA': 'virginia-bingo-sessions.json',
               'MO': 'missouri-bingo-sessions.json', 'WI': 'wisconsin-bingo-sessions.json'}
# State lists that give a start time but no end time.
START_ONLY = {'MO', 'WI'}
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
# The bingo class moved from /learn/ to /how-to-play-bingo/ (November 27, 2026), the words people search for.
MOVED = {'/learn': '/how-to-play-bingo/', '/learn/': '/how-to-play-bingo/'}
REDIRECTS += ''.join(f'{src} {dst} 301\n' for src, dst in MOVED.items())
# Small line icons (calendar, map pin, phone, directions, search), written once per page and drawn with <use>.
# They always sit beside words that say the same thing, and screen readers skip them.
ICONS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
         '<symbol id="i-cal" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>'
         '<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-7-6.1-7-11.4a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.6" r="2.6"/></symbol>'
         '<symbol id="i-phone" viewBox="0 0 24 24"><path d="M5 3.5h3.5l2 5-2.6 1.6a12 12 0 0 0 6 6l1.6-2.6 5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5.5a2 2 0 0 1 2-2z"/></symbol>'
         '<symbol id="i-route" viewBox="0 0 24 24"><path d="M12 2.5 21.5 12 12 21.5 2.5 12z"/><path d="M9 15v-2.5a2 2 0 0 1 2-2h4.5M13.5 8.5l2 2-2 2"/></symbol>'
         '<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/></symbol>'
         # The guides for new players (November 27, 2026): how to play, bingo words, pull tabs, and age by state.
         '<symbol id="i-book" viewBox="0 0 24 24"><path d="M3 5.5c3-1.5 6-1.5 9 .5 3-2 6-2 9-.5V19c-3-1.5-6-1.5-9 .5-3-2-6-2-9-.5z"/><path d="M12 6v13.5"/></symbol>'
         '<symbol id="i-words" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/></symbol>'
         '<symbol id="i-ticket" viewBox="0 0 24 24"><path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M14 8v2M14 12v0M14 14v2"/></symbol>'
         '<symbol id="i-id" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4M14 10h4M14 13h3"/></symbol>'
         '</defs></svg>')
# The Veteran Home Guardians logo at the top of every page (owner direction, November 28, 2026), then five bingo balls
# (decoration only, hidden from screen readers). The logo's address starts at the site root so it works at any depth:
# findbingo.org/assets/ (written below) and, for the guide's copy, the guide's own assets/vhg-logo.png.
LOGO = ('<a class="vhg-logo" href="https://www.vethomeguard.org/"><img src="/assets/vhg-logo.png" alt="Veteran Home Guardians" '
        'width="64" height="64"></a>')
BALLS = ('<div class="htop">' + LOGO
         + '<div class="balls" aria-hidden="true"><i>B</i><i>I</i><i>N</i><i>G</i><i>O</i></div></div>')
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
        if 'age' in s:
            # The youngest age to play, read only from the state's own law, rule or bingo regulator (November 27, 2026);
            # shown on /bingo-age-by-state/ and linked from the state page. States without a confirmed age leave it out.
            # min is null where the state's law sets no age: Iowa leaves it to each hall, and Utah allows no paid bingo.
            a = s['age']
            assert set(a) == {'min', 'rule', 'sources'} and (a['min'] is None or type(a['min']) is int) and a['rule'].strip() and s['coverage'] in LISTED, s['code']
            assert a['sources'] and all(set(x) == {'url', 'label', 'scope', 'reviewed_on'} and x['url'].startswith('https://') and x['label'].strip()
                                        and x['scope'].strip() and date.fromisoformat(x['reviewed_on']) for x in a['sources']), s['code']
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
    landing = load_landing(root)
    validate_landing(landing, states)
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
                       ('__UPDATED__', _date_label(generated_on)), ('__AD_HOME__', _ad_html(_ads_for(ads, 'home'), '')),
                       ('__GUIDES__', guides_panel()), ('__GUIDE_LINKS__', GUIDE_LINKS.format(up=''))):
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
    # Tell search engines what the site is and who publishes it. Event markup for weekly games is on the town
    # pages only (game_events), so the home page and the big state pages stay light.
    publisher = {'@type': 'Organization', 'name': 'Veteran Home Guardians', 'url': 'https://www.vethomeguard.org/',
                 'logo': SITE + '/ohio/assets/vhg-logo.png', 'email': EMAIL}
    page = page.replace('</head>', _json_ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Find Bingo',
                                             'alternateName': 'FindBingo.org', 'url': SITE + '/', 'inLanguage': 'en-US',
                                             'publisher': publisher}) + '\n</head>', 1)
    # Featured events have their own styles on the home page and every state page.
    page = page.replace('</style>', EVENT_CSS + '</style>', 1)
    style = re.search(r'<style>.*?</style>', page, re.S).group(0).replace('</style>', STATE_CSS + CITY_CSS + '</style>')
    # The home page's guide links (guides_panel); the guide pages get the same rules through guide_style.
    page = page.replace('</style>', GUIDE_LINKS_CSS + '</style>', 1)
    today = generated_on
    pages = {}
    groups = city_groups(venues)
    by_code = {s['code']: s for s in states}
    # Day pages (findbingo.org/texas/monday/): each state's weekdays with enough games, Monday first.
    dgroups = day_groups(venues)
    state_days = {code: [d for d in WEEK if (code, d) in dgroups] for code in {c for c, _ in dgroups}}
    for (code, town), rows in sorted(groups.items()):
        towns = sorted(t for c, t in groups if c == code)
        pages[f'{SLUGS[code]}/{_slug(town)}/index.html'] = _city_page(by_code[code], town, rows, towns, style, analytics, generated_on,
                                                                       day_pages=state_days.get(code, ()))
    for (code, d), rows in sorted(dgroups.items()):
        key = f'{SLUGS[code]}/{DAY_SLUGS[d]}/index.html'
        assert key not in pages, ('a day page would replace another page', key)
        pages[key] = _day_page(by_code[code], d, rows, {t for c, t in groups if c == code}, state_days[code], style, analytics, generated_on)
    # Ohio town and day pages sit inside the Ohio finder's folder (findbingo.org/ohio/columbus/, /ohio/monday/), which only
    # bingo-site/findbingo/ has.
    ohio_rows, ohio_as_of = ohio_venues(root)
    ohio_groups = ohio_town_groups(ohio_rows)
    ohio_dgroups = ohio_day_groups(ohio_rows)
    ohio_days_list = [d for d in WEEK if d in ohio_dgroups]
    ohio_pages = {f'ohio/{_slug(t)}/index.html': _city_page(by_code['OH'], t, rows, sorted(ohio_groups), style, analytics, ohio_as_of, ohio=True,
                                                            day_pages=ohio_days_list)
                  for t, rows in sorted(ohio_groups.items())}
    for d, rows in sorted(ohio_dgroups.items()):
        key = f'ohio/{DAY_SLUGS[d]}/index.html'
        assert key not in ohio_pages, ('an Ohio day page would replace a town page', key)
        ohio_pages[key] = _day_page(by_code['OH'], d, rows, set(ohio_groups), ohio_days_list, style, analytics, ohio_as_of, ohio=True)
    for s in states:
        if s['code'] == 'OH':
            continue
        if s['coverage'] == 'licenses':
            rows = [r for r in licensed if r['state'] == s['code'] and r.get('license_expires', today) >= today]
        else:
            rows = [v for v in venues if v['state'] == s['code']]
        pages[SLUGS[s['code']] + '/index.html'] = _state_page(s, states, rows, style, analytics, generated_on, landing, _ads_for(ads, SLUGS[s['code']]),
                                                              [e for e in upcoming_events(events, generated_on) if e['state'] == s['code']],
                                                              sorted(t for c, t in groups if c == s['code']), state_days.get(s['code'], ()))
    pages['privacy/index.html'] = _info_page('privacy', *PRIVACY, style, analytics, generated_on)
    pages['about/index.html'] = _info_page('about', *about_page(states), style, analytics, generated_on)
    pages['terms/index.html'] = _info_page('terms', *TERMS, style, analytics, generated_on)
    pages['advertise/index.html'] = _info_page('advertise', *ADVERTISE, style, analytics, generated_on)
    # The guides for new players, each linked from the home page and every footer (owner direction, November 27, 2026).
    guide_style = style.replace('</style>', GUIDE_LINKS_CSS + GUIDE_CSS + '</style>')
    learn, learn_ld = learn_page()
    pages['how-to-play-bingo/index.html'] = _info_page('how-to-play-bingo', *learn, guide_style.replace('</style>', LEARN_CSS + '</style>'),
                                                       analytics, generated_on, ld=learn_ld, icons=True)
    for slug, (words, ld) in (('bingo-terms', glossary_page()), ('pull-tabs', pull_tabs_page(states)), ('bingo-age-by-state', age_page(states))):
        pages[f'{slug}/index.html'] = _info_page(slug, *words, guide_style, analytics, generated_on, ld=ld, trail=GUIDE_TRAIL, icons=True)
    # The bingo class's old address forwards to its new one (findbingo.org answers it with a 301 too).
    pages['learn/index.html'] = moved_page('how-to-play-bingo', 'The bingo class', style, analytics, generated_on)
    pages['halls/index.html'] = _info_page('halls', *halls_page(states), style.replace('</style>', HALL_CSS + '</style>'), analytics, generated_on)
    pages['shop/index.html'] = _info_page('shop', *shop_page(load_shop(root)), style.replace('</style>', SHOP_CSS + '</style>'), analytics, generated_on)
    # Ad pictures are served beside the pages, in ads/.
    pages.update({'ads/' + a['image'].rsplit('/', 1)[1]: (root / a['image']).read_bytes() for a in ads if a.get('image')})
    site = {
        # Google Search Console ownership file for https://www.findbingo.org/ (owner direction, Nov 16, 2026).
        # Keep it: Google rechecks the file, and removing it drops verification.
        'googleae90b5079bda9bbc.html': 'google-site-verification: googleae90b5079bda9bbc.html',
        # IndexNow key for www.findbingo.org: proves the site is ours when the Ohio-Bingo repository's mirror workflow tells Bing
        # (and the other IndexNow engines) which pages changed. No account; keep it beside the Google file.
        'cd2ba11c432756dd60823a42f8614441.txt': 'cd2ba11c432756dd60823a42f8614441\n',
        'index.html': page,
        'data.json': data_json + '\n',
        'zips.json': json.dumps(zips, separators=(',', ':')) + '\n',
        # The logo in every page's header (LOGO).
        'assets/vhg-logo.png': (root / 'assets/vhg-logo.png').read_bytes(),
        **pages,
        # The map files (Leaflet), served from the site itself; place-map.js loads them only when a list has pins.
        **place_map.vendor_files(root, 'assets/map/'),
    }
    # The same three files also go into bingo-site/findbingo/, which the Ohio-Bingo repository mirrors;
    # Cloudflare serves www.findbingo.org from that folder (the Ohio finder sits beside them in ohio/).
    return {
        **{'findbingo-site/' + name: text for name, text in site.items()},
        **{'bingo-site/findbingo/' + name: text for name, text in site.items()},
        **{'bingo-site/findbingo/' + name: text for name, text in ohio_pages.items()},
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


def _venue_html(v, s, pick=None):
    """One listing's card. pick is a day page's weekday: the card shows that day's games and names the hall's other
    bingo days in a line, so a long week of sessions does not bury the day the visitor asked for."""
    many = len(v['organizations']) > 1
    sessions = ''.join(
        f'<li data-day="{x["day"]}"><strong>{DAY_NAMES[x["day"]]}</strong>, {escape(_time_range(x["start"], x.get("end")))}'
        + (f' <span class="org">· {escape(x["label"])}</span>' if x.get('label') else '')
        + (f' <span class="org">· {escape(x["organization"])}</span>' if many else '') + '</li>' for x in _on_day(v, pick))
    others = [DAY_NAMES[d] for d in WEEK if pick is not None and d != pick and any(x['day'] == d for x in v['sessions'])]
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
            + ('<p>Bingo runs here every day of the week.</p>' if len(others) == 6 else f'<p>Other bingo days here: {escape(_and(others))}.</p>' if others else '')
            + f'<p class="note">{escape(v.get("schedule_note") or s.get("hours_note") or "Call ahead to confirm before you go.")}</p></div>'
            f'<div class="big-actions">{call}<a class="outline" href="{escape(_maps(v["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("route")}Directions ↗</a></div>'
            f'<p class="address">{escape(v["address"])} · {escape(_area(v["county"]))}</p>'
            + (f'<p class="small">{escape(v["hours"])}</p>' if v.get('hours') else '')
            + (f'<p class="small">Bingo here is run by {escape(", ".join(v["organizations"]))}.</p>' if many else '')
            + f'<details class="sources"><summary>Where this comes from · checked {_date_label(v["reviewed_on"])}</summary><p>{source}</p>'
            + ''.join(f'<p>{escape(n)}</p>' for n in v.get('notes', [])) + '</details>'
            f'<p class="small-links"><a href="{escape(_report(v))}">Report a change</a></p></article>')


def _on_day(v, pick):
    """A listing's sessions, or only those on weekday pick (day pages)."""
    return [x for x in v['sessions'] if pick is None or x['day'] == pick]


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


def _map_box(up, what, nodays='Licensed, game days not posted'):
    """The map above a list. Group dots on the map show how many places they hold (owner direction, November 23, 2026);
    the page text still never states counts."""
    return place_map.box('results' if not up else 'listings', up + 'assets/map/', title='See them on a map',
                         label=f'Map of {what}. Every place on the map is also in the list.',
                         legend=(('game', 'Bingo with game days'), ('nodays', nodays)) + ((('you', 'Your ZIP code'),) if not up else ()),
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


# How Find Bingo works for halls, in Travis's words of his model (owner direction, November 27, 2026): every game is
# listed free; halls can update or claim their listing; a hall can become a community partner by naming Veteran Home
# Guardians (in Ohio) or its state's local partner as a charitable recipient of part of its bingo proceeds; and halls
# that would rather pay can ask for paid help. No prices here (they live on the Advertise page), no partner benefits,
# and no partner that is not already named on the site. The icons are decoration beside words.
def _hall_icon(path):
    return f'<span class="hall-ic" aria-hidden="true"><svg viewBox="0 0 24 24" focusable="false">{path}</svg></span>'


HALL_HOW = (
    '<section class="hall-how" aria-labelledby="how-title"><h2 id="how-title">How Find Bingo works for your hall</h2><ul class="hall-steps">'
    '<li>' + _hall_icon('<path d="M4 12.5 9.5 18 20 6.5"/>')
    + '<div><h3>Every game is listed free</h3><p>We list every bingo game we know of, for every hall, free. No hall can pay for a better listing.</p></div></li>'
    '<li>' + _hall_icon('<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>')
    + '<div><h3>Update or claim your listing</h3><p>Send us new game days, start times or a phone number for players, or claim your listing so players always see your latest details.</p>'
    '<p class="hall-links"><a href="' + escape(_mailto('Update our bingo listing', 'Hall or group name:\nState and town:\nGame days and first game time:\nPhone for players:\nWebsite or Facebook page:\n'))
    + '">Email us an update</a> · <a href="../ohio/#submit-details">Update an Ohio listing</a> · '
    '<a href="https://www.ohiobingo.org/claim.html" target="_blank" rel="noopener noreferrer">Claim an Ohio listing ↗</a></p></div></li>'
    '<li>' + _hall_icon('<path d="M12 20s-7.5-4.6-7.5-10A4.2 4.2 0 0 1 12 7.6 4.2 4.2 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>')
    + '<div><h3>Become a community partner</h3><p>In Ohio, name Veteran Home Guardians as a charitable recipient of part of your bingo proceeds. '
    'Outside Ohio, name the local partner shown on your state’s page.</p>'
    '<p class="hall-links"><a href="../ohio/partners.html#sponsors">Partnering in Ohio</a> · <a href="#partners">Local partners in other states</a></p></div></li>'
    '<li>' + _hall_icon('<path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>')
    + '<div><h3>Paid help, if you prefer</h3><p>Would your hall rather pay for help? Ask us about a game website built for your hall and kept current, '
    'a featured event in local results, or help with advertising.</p><p class="hall-links"><a href="../advertise/">See the paid options</a></p></div></li></ul>'
    '<div class="big-actions"><a class="solid" href="'
    + escape(_mailto('Help for our bingo hall', 'Hall or group name:\nState and town:\nWhat would help most:\nBest way to reach us:\n'))
    + '">Talk with us about your hall</a></div></section>')
HALL_CSS = ('.hall-steps{list-style:none;padding:0;margin:14px 0;display:grid;gap:14px}'
            '.hall-steps li{display:flex;gap:16px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 18px}'
            '.hall-ic{flex:none;display:inline-flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:50%;background:var(--green);color:#fff}'
            '.hall-ic svg{width:26px;height:26px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}'
            '.hall-steps h3{margin:2px 0 4px;font-size:21px;color:var(--head)}.hall-steps p{margin:4px 0}.hall-links{font-size:17px}')


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
                    '<p><strong>Run a charity hoping bingo can help?</strong> Here is how it works. In Ohio, where the law requires veteran, fraternal and sporting '
                    'groups to give part of their instant bingo profit to an outside charity, halls can name Veteran Home Guardians. In other states we name one local partner, '
                    'with its agreement, and ask that state’s halls to consider supporting it.</p>'
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
            + HALL_HOW +
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
            '<h2 id="suppliers">Bingo suppliers and distributors</h2><p>Paper, electronics, pull-tabs, daubers, software: if you sell to halls, you can reach them and their players here with a labeled ad. '
            '<a href="../advertise/">Advertise on Find Bingo</a></p>')
    # Written to the hall volunteer or manager trying to fill seats (owner direction, November 23, 2026).
    return ('Fill Your Bingo Hall: Free Listings and Help for Halls | FindBingo.org',
            'Run bingo for a post, lodge, fire company or parish? List your games free, reach more players, feature a special night, and see your state’s rules.',
            'Help for bingo halls: fill more seats',
            'Volunteer or manager trying to fill seats on bingo night? List your games free so people searching near you find them, then see what else can help and what your state’s rules say about bingo money and ads.',
            body)


# What each state page says to the person who lands on it (owner direction, November 23, 2026: "every landing page should
# be specific to who's there looking for it"). data/findbingo-landing.json holds a heading, title, description and a short
# welcome for every state, written to that state's player and its own law. {towns}, {days} and {kinds} are filled from the
# state's listings, so the words stay true as the lists change. No counts, ever.
LANDING_FILE = 'data/findbingo-landing.json'
LANDING_KEYS = ('h1', 'title', 'description', 'welcome')
LANDING_LIMITS = {'title': 70, 'description': 165, 'welcome': 330, 'h1': 60}
# The same check tests/findbingo.cjs runs on whole pages: a number followed by a kind of place is a count.
COUNT_WORDS = re.compile(r'\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b', re.I)
KIND_WORDS = {'hall': 'halls', 'senior_center': 'senior centers'}
WEEK = (1, 2, 3, 4, 5, 6, 0)  # Monday first


def load_landing(root):
    return json.loads((root / LANDING_FILE).read_text())['states']


def _and(words):
    return ', '.join(words[:-1]) + ' and ' + words[-1] if len(words) > 1 else words[0]


def _days_phrase(days):
    """'every day of the week', 'every day but Saturday', 'Monday through Friday' or 'on Tuesdays and Fridays'."""
    days = [d for d in WEEK if d in days]
    if len(days) == 7:
        return 'every day of the week'
    at = [WEEK.index(d) for d in days]
    if len(days) >= 3 and at == list(range(at[0], at[0] + len(at))):
        return f'{DAY_NAMES[days[0]]} through {DAY_NAMES[days[-1]]}'
    if len(days) >= 5:
        return 'every day but ' + _and([DAY_NAMES[d] for d in WEEK if d not in days])
    return 'on ' + _and([DAY_NAMES[d] + 's' for d in days])


def landing_words(s, rows, landing):
    """The state's heading, title, description and welcome, with {towns}, {days} and {kinds} filled from its own listings."""
    entry = landing[s['code']]
    towns = sorted(Counter(r['city'] for r in rows).items(), key=lambda x: (-x[1], x[0]))
    fill = {'towns': _and([c for c, _ in towns[:3]]) if towns else None,
            'days': _days_phrase({x['day'] for r in rows for x in r.get('sessions', [])}) if any(r.get('sessions') for r in rows) else None,
            'kinds': _and(sorted(KIND_WORDS[k] for k in {r['kind'] for r in rows if r.get('kind')})) if any(r.get('kind') for r in rows) else None}
    out = {}
    for key in LANDING_KEYS:
        text = entry[key]
        for name in re.findall(r'\{(\w+)\}', text):
            assert key not in ('h1', 'title') and fill.get(name), (s['code'], key, name)
            text = text.replace('{' + name + '}', fill[name])
        assert '{' not in text and '}' not in text and len(text) <= LANDING_LIMITS[key], (s['code'], key, len(text))
        assert not COUNT_WORDS.search(text), (s['code'], key, 'no counts')
        out[key] = text
    return out


def validate_landing(landing, states):
    assert set(landing) == {s['code'] for s in states}, 'every state has its landing words'
    for s in states:
        e = landing[s['code']]
        assert set(e) == set(LANDING_KEYS) and all(isinstance(e[k], str) and e[k].strip() == e[k] and e[k] for k in LANDING_KEYS), s['code']
        assert e['title'].startswith(s['name'] + ' Bingo') and e['title'].endswith(' | FindBingo.org'), s['code']
        assert s['name'] in e['description'] or s['code'] == 'DC', s['code']
    for key in LANDING_KEYS:
        assert len({e[key] for e in landing.values()}) == len(landing), key + ' differs on every state page'


# Parts of the day for the week chart on state pages, by a listing's start time ('HH:MM').
DAY_PARTS = (('Morning', 'before noon', lambda h: h < 12), ('Afternoon', 'noon to 5 p.m.', lambda h: 12 <= h < 17),
             ('Evening', '5 p.m. and later', lambda h: h >= 17))


def week_chart(name, rows, hours_note=''):
    """When listed games begin in a state, by weekday and part of the day: a ball where at least one listing's time
    begins, a dash where none does. It is a real table (its own text version) and never states how many: Travis's rule
    for Find Bingo is no counts (November 16, 2026). Built only from the state's own listings."""
    sessions = [x for r in rows for x in r.get('sessions', [])]
    if not sessions:
        return ''
    parts = [(label, span, lambda x, test=test: bool(x.get('start')) and test(int(x['start'][:2]))) for label, span, test in DAY_PARTS]
    if any(not x.get('start') for x in sessions):
        parts.append(('Time not posted', '', lambda x: not x.get('start')))
    head = ''.join(f'<th scope="col"><span aria-hidden="true">{DAY_NAMES[d][:3]}</span><span class="vh">{DAY_NAMES[d]}</span></th>' for d in WEEK)
    body = ''
    for label, span, test in parts:
        cells = ''
        for d in WEEK:
            on = any(x['day'] == d and test(x) for x in sessions)
            cells += ('<td class="on"><span class="ball" aria-hidden="true"></span><span class="vh">Yes</span></td>' if on else
                      '<td class="off"><span aria-hidden="true">–</span><span class="vh">No</span></td>')
        body += f'<tr><th scope="row">{label}' + (f'<small>{span}</small>' if span else '') + f'</th>{cells}</tr>'
    days = _days_phrase({x['day'] for x in sessions})
    return (f'<section class="week" aria-labelledby="week-title"><h2 id="week-title">{_ic("cal")}Bingo days and times in {escape(name)}</h2>'
            f'<p>Listed games here run {escape(days)}. The chart shows when listed times begin.</p>'
            f'<div class="week-wrap"><table><caption class="vh">When listed bingo times begin in {escape(name)}, by day and part of the day. '
            'Yes means at least one listing begins then.</caption>'
            f'<thead><tr><td></td>{head}</tr></thead><tbody>{body}</tbody></table></div>'
            '<p class="small"><span class="ball" aria-hidden="true"></span> at least one listing begins then · – none listed. '
            # The state's own note often says to call ahead already; say it once.
            + ' '.join(x for x in (escape(hours_note), '' if 'call ahead' in hours_note.lower() else 'Call ahead before you go.') if x)
            + '</p></section>')


# ---- City pages (findbingo.org/texas/san-antonio/ and so on) ------------------------------------------------
# Owner direction, November 26, 2026: lean into Find Bingo. Search Console shows people search "bingo near me",
# "bingo tonight", a weekday ("bingo tuesday night near me") and a hall plus its town. A town with at least
# CITY_MIN listings gets its own page: the town's games day by day, then every listing. Fewer than that would
# be a thin page, so those towns stay on the state page only. Ohio's finder is built from its own records.
CITY_MIN = 3


def load_venues(root):
    """Every state list with game days (the times lists and the starter lists), in state order."""
    venues = []
    for code in ORDER:
        for files in (TIMES_FILES, STARTER_FILES):
            if code in files:
                venues += json.loads((root / 'data/public' / files[code]).read_text())
    return venues


def city_groups(venues):
    """{(state code, town): listings} for every town outside Ohio with at least CITY_MIN listings, and its slug."""
    towns = {}
    for v in venues:
        if v['state'] != 'OH':
            towns.setdefault((v['state'], v['city']), []).append(v)
    groups = {k: sorted(rows, key=lambda r: r['name']) for k, rows in towns.items() if len(rows) >= CITY_MIN}
    slugs = {}
    for code, town in groups:
        key = (code, _slug(town))
        assert key not in slugs, ('two towns share an address', code, town, slugs.get(key))
        assert key[1] not in DAY_SLUGS, ('a town page would take a day page\'s address', code, town)
        slugs[key] = town
    return groups


def indexed_city_pages(root):
    """City pages for the sitemap: 'texas/san-antonio/', 'ohio/columbus/' and so on."""
    towns = list(city_groups(load_venues(root))) + [('OH', t) for t in ohio_towns(root)]
    return tuple(f'{SLUGS[code]}/{_slug(town)}/' for code, town in sorted(towns))


def _weekly(v, x):
    """A session that runs every week on its day: no schedule note on the listing and no label such as
    'Some Fridays' or 'First and third Saturday of the month' on the session."""
    return not v.get('schedule_note') and not x.get('label')


def _street(v):
    """The street part of 'Street, Town, ST 12345', or the whole address if it does not split that way."""
    if v.get('street'):
        return v['street']
    tail = f', {v["city"]}, {v["state"]} {v["zip"]}'
    return v['address'][:-len(tail)] if v['address'].endswith(tail) else v['address']


def game_events(rows, page_url, only_day=None, town_urls=None):
    """schema.org Event markup for games that run every week, built only from the listing: the place, its address,
    the group that runs the game, the weekday and the listed hours. No price (the lists do not give one) and no
    invented dates: eventSchedule says 'every Monday, 4 to 11 p.m.', and EVENT_DATES_LD fills in the next date in the
    visitor's browser, so the date is never stale. Games that run only some weeks get no markup. only_day limits the markup to
    that weekday's games, and town_urls ({town: its page}) points each game at its town page where the town has one, so a
    game listed on a day page and on its town page is one event with one address (day pages)."""
    out = []
    for v in rows:
        for x in v['sessions']:
            if not _weekly(v, x) or not x.get('start') or (only_day is not None and x['day'] != only_day):
                continue
            day = DAY_NAMES[x['day']]
            when = f'every {day}, {_time_range(x["start"], x.get("end"))}'
            schedule = {'@type': 'Schedule', 'byDay': 'https://schema.org/' + day, 'repeatFrequency': 'P1W', 'startTime': x['start'] + ':00'}
            if x.get('end'):
                schedule['endTime'] = x['end'] + ':00'
            out.append({
                '@context': 'https://schema.org', '@type': 'Event',
                'name': f'Bingo at {v["name"]}',
                'description': f'Weekly bingo at {v["name"]} in {v["city"]}, {when}, run by {x["organization"]}. Call ahead before you go.',
                'url': f'{(town_urls or {}).get(v["city"], page_url)}#{v["id"]}',
                'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
                'eventStatus': 'https://schema.org/EventScheduled',
                'eventSchedule': schedule,
                'location': {'@type': 'Place', 'name': v['name'], 'address': {
                    '@type': 'PostalAddress', 'streetAddress': _street(v), 'addressLocality': v['city'],
                    'addressRegion': v['state'], **({'postalCode': v['zip']} if v.get('zip') else {}), 'addressCountry': 'US'}},
                'organizer': {'@type': 'Organization', 'name': x['organization']},
            })
    return out


# Fills startDate (and endDate) on each weekly game's markup with its next date, as local time at the hall: the
# next listed weekday on or after today. Search engines that run scripts see a current date; without scripts the
# markup still says "every Monday" through eventSchedule. A game that ends after midnight ends the next day.
EVENT_DATES_LD = ("<script>(function(){var el=document.getElementById('games-ld');if(!el)return;var ev=JSON.parse(el.textContent),"
                  "days=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],now=new Date(),"
                  "p=function(n){return(n<10?'0':'')+n},iso=function(d){return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())};"
                  "ev.forEach(function(e){var s=e.eventSchedule,want=days.indexOf(s.byDay.split('/').pop()),d=new Date(now.getFullYear(),now.getMonth(),now.getDate());"
                  "d.setDate(d.getDate()+((want-d.getDay()+7)%7));e.startDate=iso(d)+'T'+s.startTime;"
                  "if(s.endTime){var f=new Date(d);if(s.endTime<=s.startTime)f.setDate(f.getDate()+1);e.endDate=iso(f)+'T'+s.endTime}});"
                  "el.textContent=JSON.stringify(ev)})()</script>")

CITY_CSS = ('.by-day{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}'
            '.by-day h2{font-size:24px;margin:10px 0 6px}.by-day h3{font-size:21px;margin:16px 0 4px;color:var(--head)}'
            '.by-day ul{margin:0;padding-left:22px}.by-day li{margin:6px 0;font-size:18px}.by-day li a{font-weight:700}'
            '.towns{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}.towns h2{font-size:24px;margin:10px 0 8px}'
            '.towns ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
            '.towns a{display:inline-flex;align-items:center;min-height:48px;padding:0 14px;border:2px solid var(--accent);border-radius:24px;color:var(--accent);font-weight:700;text-decoration:none}'
            '@media print{.towns{display:none!important}}'
            # "Bingo by day" (_days_nav): the same round links as the town list; the page's own day is filled in.
            '.weekdays{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}.weekdays h2{font-size:24px;margin:10px 0 8px}'
            '.weekdays ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
            '.weekdays a{display:inline-flex;align-items:center;min-height:48px;padding:0 16px;border:2px solid var(--accent);border-radius:24px;color:var(--accent);font-weight:700;text-decoration:none}'
            '.weekdays a[aria-current]{background:var(--accent);color:var(--card)}'
            '@media (forced-colors:active){.weekdays a[aria-current]{forced-color-adjust:none;background:Highlight;color:HighlightText;border-color:Highlight}}'
            '@media print{.weekdays,.jump{display:none!important}}')


def _days_nav(s, days, up, current=None):
    """'Bingo by day': links to a state's day pages (findbingo.org/texas/monday/), only the days that have one, from its
    state page (up=''), its town pages and its day pages (up='../'). On a day page its own day is marked as the current page."""
    if not days:
        return ''
    return (f'<nav class="weekdays" aria-labelledby="days-title"><h2 id="days-title">Bingo by day in {escape(s["name"])}</h2><ul>'
            + ''.join(f'<li><a href="{up}{DAY_SLUGS[d]}/"' + (' aria-current="page"' if d == current else '') + f'>{DAY_NAMES[d]}</a></li>'
                      for d in days) + '</ul></nav>')


def _towns_nav(s, towns, up):
    """Links to a state's town pages, from its state page (up='') and from each town page (up='../')."""
    if not towns:
        return ''
    return (f'<nav class="towns" aria-labelledby="towns-title"><h2 id="towns-title">Bingo by town in {escape(s["name"])}</h2><ul>'
            + ''.join(f'<li><a href="{up}{_slug(t)}/">{escape(t)}</a></li>' for t in towns) + '</ul></nav>')


def _city_page(s, town, rows, towns, style, analytics, generated_on, ohio=False, day_pages=()):
    """A town's page. ohio=True builds an Ohio town page (findbingo.org/ohio/columbus/) from ohio_venues(): the same
    layout, with each Ohio card (_ohio_card), the days on a hall's state license where it has posted no times, and the
    ZIP box opening the Ohio finder. day_pages: the weekdays with a day page in the state, linked under "Bingo by day"."""
    code, name, slug = s['code'], s['name'], SLUGS[s['code']]
    url = f'{SITE}/{slug}/{_slug(town)}/'
    sessions = [x for r in rows for x in r['sessions']]
    days = {x['day'] for x in sessions}
    heading = f'Bingo in {town}, {name}'
    title = f'Bingo in {town}, {code}: days and times | FindBingo.org'
    if len(title) > 70:
        title = f'Bingo in {town}, {code} | FindBingo.org'
    if ohio:
        # Most Ohio halls are known from the state's license list, which gives days but not times, so the words promise
        # times only where they are posted.
        by_day = _ohio_by_day(rows)
        description = (f'Bingo in {town}, Ohio: game days, start times where posted, phone numbers and directions for halls '
                       'licensed by the state. Free, with a source for every listing.')
        if len(description) > 165:
            description = f'Bingo in {town}, Ohio: game days, phone numbers and directions for every listing. Free.'
        lead = (f'Looking for bingo in {town}? Here is every place we know of, with game times where they are posted. '
                + ('Pick your day below, then call ahead before you go.' if by_day else 'Call ahead before you go.'))
    else:
        description = (f'Bingo in {town}, {name}, {_days_phrase(days)}: halls, game days, start times, phone numbers and directions. '
                       'Free, with a source for every listing.')
        if len(description) > 165:
            description = f'Bingo in {town}, {name}: halls, game days, start times, phone numbers and directions. Free.'
        lead = (f'Looking for bingo in {town}? Games here run {_days_phrase(days)}. '
                'Pick your day below to see where and when, then call ahead before you go.')
    assert len(title) <= 70 and len(description) <= 165 and not COUNT_WORDS.search(title + description + lead), (code, town)
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Find Bingo', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': f'Bingo in {name}', 'item': f'{SITE}/{slug}/'},
        {'@type': 'ListItem', 'position': 3, 'name': f'Bingo in {town}', 'item': url}]}
    events = game_events(rows, url)
    # Bingo by day: each weekday, the places with a game that day and its listed hours, linking to the listing.
    if not ohio:  # Ohio's day-by-day list is built above (_ohio_by_day)
        by_day = ''
        for d in WEEK:
            items = [(r, x) for r in rows for x in r['sessions'] if x['day'] == d]
            if not items:
                continue
            by_day += (f'<h3 id="{DAY_NAMES[d].lower()}">{DAY_NAMES[d]}</h3><ul class="sessions" data-weekly>'
                       + ''.join(f'<li{f" data-day={chr(34)}{d}{chr(34)}" if _weekly(r, x) else ""}><a href="#{escape(r["id"])}">{escape(r["name"])}</a>, {escape(_time_range(x["start"], x.get("end")))}'
                                 + ('' if _weekly(r, x) else f' <span class="org">· {escape(x.get("label") or "some weeks only, call ahead")}</span>') + '</li>'
                                 for r, x in items) + '</ul>')
    pick = ('Pick your day. Games that run only some weeks say so, and halls with no posted times show the days on their state '
            'license. Call ahead before you go.' if ohio else 'Pick your day. Games that run only some weeks say so. Call ahead before you go.')
    body = (f'<p class="intro">{escape(s["regulator_note"])}</p>'
            + week_chart(town, rows, s.get('hours_note', ''))
            + (f'<section class="by-day" aria-labelledby="by-day-title"><h2 id="by-day-title">{_ic("cal")}Bingo in {escape(town)}, day by day</h2>'
               + f'<p>{pick}</p>{by_day}</section>' if by_day else ''))
    if any(r['zip'] in ZIP_POINTS for r in rows):
        body += _map_box('../../', f'the {town} bingo listed below', *(('Licensed, game times not posted',) if ohio else ()))
    body += (f'<div id="listings"><h2 id="list-title">Every bingo listing in {escape(town)}</h2><div class="grid">'
             + ''.join((_ohio_card if ohio else _venue_html)(r, s) for r in rows) + '</div></div>')
    body += _days_nav(s, day_pages, '../')
    body += _towns_nav(s, [t for t in towns if t != town], '../')
    body += (f'<p class="small-links"><a href="../">All bingo in {escape(name)}</a> · <a href="../../">Search every state by ZIP code</a></p>'
             + (_ohio_send() if ohio else _send_times(s, '../../')))
    # Ohio's town pages search the Ohio finder (one folder up); the others search the national finder.
    zip_form = (f'<form class="zip-box" action="{"../" if ohio else "../../"}" method="get"><div class="tools">'
                '<div><label for="zip">Type your ZIP code</label><input id="zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" pattern="[0-9]{5}" placeholder="Your 5-digit ZIP" required></div>'
                '<div><label for="radius">How far will you go?</label><select id="radius" name="radius"><option value="10">10 miles</option><option value="25" selected>25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>'
                f'<div><button class="primary" type="submit">{_ic("search")}Find bingo near me</button></div></div>'
                f'<p class="small">Shows bingo near you, closest first, including towns around {escape(town)}.</p></form>')
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(heading)}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n' + _json_ld(crumbs)
            + ('\n<script type="application/ld+json" id="games-ld">' + json.dumps(events, ensure_ascii=False).replace('</', '<\\/') + '</script>' if events else '')
            + '\n</head>')
    return (head + f'<body id="top">{ICONS}<a class="skip" href="#listings">Skip to the bingo list</a>'
            f'<header>{BALLS}<p class="brand"><a href="../../">FindBingo.org</a> · <a href="../">{escape(name)}</a> · free from Veteran Home Guardians</p>'
            f'<h1>{escape(heading)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main>{zip_form}{body}</main>'
            f'{_footer(generated_on, "../../")}{TODAY_SCRIPT}{EVENT_DATES_LD if events else ""}{place_map.script() if "pm-box" in body else ""}<script>{analytics}</script></body></html>\n')


# ---- Ohio town pages (findbingo.org/ohio/columbus/ and so on) ------------------------------------------------
# Owner direction, November 27, 2026: Ohio is Find Bingo's core market, so its towns get pages like the other states'.
# They are built from the Ohio finder's own records (bingo_edition.ohio_records), not a state list file. Most Ohio halls
# are known only from the state's list of authorized bingo days, which gives days but no times, so a town page shows
# posted game times where a hall or organizer published them and otherwise the days on the hall's license. Halls
# licensed only for set dates (one-off fundraisers) and senior centers without bingo are left to the Ohio finder.
OHIO_TOWN = re.compile(r',\s*([^,]+),\s*OH\b')
OHIO_ZIP = re.compile(r'\bOH\s+(\d{5})\b')
OHIO_LICENSE_DAY = re.compile(r'\b(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b')
# Words in a posted schedule that mean the game does not run every week.
SOME_WEEKS = re.compile(r'\b(not every|some weeks|some \w+days|most \w+days|every other|alternate|alternating|varies|vary|monthly|of the month|seasonal)\b'
                        r'|\b(first|second|third|fourth|last|1st|2nd|3rd|4th)(\s*(and|&|,)\s*(first|second|third|fourth|last|1st|2nd|3rd|4th))*\s+'
                        r'(Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)days?\b', re.I)
# The state's report sometimes leaves a placeholder after a group's name ('… Church N/A').
NAME_PLACEHOLDER = re.compile(r'\s+(N/A|n/a|—|–|-|no|none)$')
# A clock time in a posted schedule, as the finder reads them (gameTimes in bingo_edition.py).
GAME_TIME = re.compile(r'(\bnoon\b|(\d{1,2})(?::(\d{2}))?\s*(a\.m\.|p\.m\.|am\b|pm\b))', re.I)
# '6 to 9 p.m.' and '2:30–4:30 p.m.': only the first time is a start.
RANGE_END = re.compile(r'(\d{1,2}(?::\d\d)?\s*(?:a\.m\.|p\.m\.|am\b|pm\b)?|\bnoon\b)\s*(?:[–-]|\bto\b)\s*(?:\d{1,2}(?::\d\d)?\s*(?:a\.m\.|p\.m\.|am\b|pm\b)|noon\b)', re.I)
NOT_A_GAME = re.compile(r'doors|instant|dinner|lunch|breakfast|meal|kitchen|concession|packet|sales|ticket|open', re.I)
OHIO_DEFAULT_ADMISSION = 'Confirm public attendance and age rules with the organizer.'
OHIO_CLAIM = 'https://www.ohiobingo.org/claim.html'


def _game_times(text):
    """Start times ('HH:MM') of the games in a posted schedule, leaving out doors, meals and ticket sales."""
    text = text or ''
    # Keep each range's first time and its a.m. or p.m.: '2:30–4:30 p.m.' becomes '2:30 p.m.'.
    def first(m):
        start = m.group(1)
        if not re.search(r'(a\.m\.|p\.m\.|am|pm|noon)$', start, re.I):
            start += ' ' + re.search(r'(a\.m\.|p\.m\.|am|pm|noon)\s*$', m.group(0), re.I).group(1)
        return start
    text = RANGE_END.sub(first, text)
    times = []
    for m in GAME_TIME.finditer(text):
        before = re.split(r'[;,:.\n]', text[max(0, m.start() - 32):m.start()])[-1]
        if NOT_A_GAME.search(before):
            continue
        if m.group(1).lower() == 'noon':
            times.append('12:00')
            continue
        h, mins = int(m.group(2)) % 12, int(m.group(3) or 0)
        if m.group(4).lower().startswith('p'):
            h += 12
        if h < 24 and mins < 60:
            times.append(f'{h:02d}:{mins:02d}')
    return list(dict.fromkeys(times))


DAY_GROUP = re.compile(r'((?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)days?(?:\s*(?:,|and|&)\s*(?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)days?)*)\s*:')


def _start_times(schedule, days):
    """{weekday: start 'HH:MM' or None}. A schedule split by day ('Tuesday and Friday: ... 7 p.m. Sunday: ... 6:30 p.m.')
    is read part by part. A start is kept only where the text gives exactly one game time, so 'early birds 5:30/6/6:30 p.m.;
    bingo 7 p.m.' or a game with lightning and series times shows no single time (the card has the whole schedule)."""
    def one(text):
        times = _game_times(text)
        return times[0] if len(times) == 1 else None
    parts = list(DAY_GROUP.finditer(schedule))
    if not parts:
        start = one(schedule)
        return {d: start for d in days}
    out = {d: None for d in days}
    for i, m in enumerate(parts):
        text = schedule[m.end():parts[i + 1].start() if i + 1 < len(parts) else len(schedule)]
        for name in OHIO_LICENSE_DAY.findall(re.sub(r'days\b', 'day', m.group(1))):
            d = DAY_NAMES.index(name)
            if d in out:
                out[d] = one(text)
    return out


def _ohio_town(address):
    m = OHIO_TOWN.search(address)
    if not m:
        return ''
    town = m.group(1).strip()
    half = len(town) // 2
    if len(town) % 2 == 0 and town[:half] == town[half:]:  # 'ToledoToledo' in the state's report
        town = town[:half]
    return '' if town.upper() == 'OH' else town


def _week_order(days):
    return sorted(set(days), key=WEEK.index)


def ohio_venues(root):
    """(rows, as_of): every Ohio record a town page lists, shaped like the other states' listings (id, name, city, zip,
    address, county, phone, kind, sessions) with the Ohio record kept under 'oh'. as_of is the newest review date, so
    the build gives the same pages on any day."""
    records, _ = ohio_records(root)
    as_of = max(r['reviewed_on'] for r in records)
    rows = []
    for r in records:
        if r['category'] == 'center' and not r.get('offers_bingo'):
            continue
        recurring = bool(r.get('session_days') or r.get('session_monthly')) and not r.get('session_dates')
        posted = recurring and bool(r.get('schedule')) and (r.get('schedule_valid_until') or as_of) >= as_of
        license_days = _week_order(DAY_NAMES.index(d) for d in OHIO_LICENSE_DAY.findall(r.get('authorized_days') or ''))
        if r['category'] == 'licensed' and not posted and not license_days:
            continue  # licensed only for set dates, or no days at all: the Ohio finder still lists it
        town = _ohio_town(r['address'])
        if not town:
            continue
        zip_code = OHIO_ZIP.search(r['address'])
        m = OHIO_TOWN.search(r['address'])
        sessions = []
        if posted:
            days = _week_order(r.get('session_days') or [])
            starts = _start_times(r['schedule'], days + [x['weekday'] for x in r.get('session_monthly') or []])
            label = ''
            if SOME_WEEKS.search(r['schedule']):
                label = 'some weeks, call ahead'
            elif r.get('schedule_valid_until'):
                label = 'through ' + _date_label(r['schedule_valid_until'])
            for d in days:
                sessions.append({'day': d, 'start': starts[d], 'organization': r['name'], **({'label': label} if label else {})})
            for rule in r.get('session_monthly') or []:
                weeks = _and([('1st', '2nd', '3rd', '4th', '5th')[w - 1] for w in rule['weeks']])
                sessions.append({'day': rule['weekday'], 'start': starts[rule['weekday']], 'organization': r['name'],
                                 'label': f'{weeks} {DAY_NAMES[rule["weekday"]]} of the month'})
            sessions.sort(key=lambda x: WEEK.index(x['day']))
        phone = r.get('phone') if r.get('phone') and (r.get('phone_valid_until') or as_of) >= as_of else None
        row = {'id': r['id'], 'state': 'OH', 'name': NAME_PLACEHOLDER.sub('', (r.get('advertised_name') if posted else None) or r['name']), 'city': town,
               'zip': zip_code.group(1) if zip_code else '', 'address': r['address'], 'street': r['address'][:m.start()].strip(),
               'county': r['county'], 'phone': phone, 'kind': 'senior_center' if r.get('is_center') or r['category'] == 'senior' else 'hall',
               'sessions': sessions, 'reviewed_on': r['reviewed_on'], 'posted': posted, 'oh': r}
        if not posted and license_days:
            row['license_days'] = license_days
        if posted and (r.get('schedule_source') or r.get('enforcement')):
            # A schedule copied from a newspaper or listing site, or a hall with a state licensing notice: no Event markup.
            row['schedule_note'] = 'Call to confirm before you go.'
        rows.append(row)
    # One spelling per town: the state's report writes some towns in capitals or lower case.
    spellings = {}
    for row in rows:
        spellings.setdefault(row['city'].lower(), Counter())[row['city']] += 1
    names = {}
    for key, seen in spellings.items():
        mixed = [t for t, _ in sorted(seen.items(), key=lambda kv: (-kv[1], kv[0])) if not t.isupper() and not t.islower()]
        names[key] = mixed[0] if mixed else ' '.join(w.capitalize() for w in key.split())
    for row in rows:
        row['city'] = names[row['city'].lower()]
    return rows, as_of


def ohio_town_groups(rows):
    """{town: listings} for every Ohio town with at least CITY_MIN listings."""
    towns = {}
    for row in rows:
        towns.setdefault(row['city'], []).append(row)
    groups = {t: sorted(rs, key=lambda r: (not r['posted'], r['name'].lower())) for t, rs in towns.items() if len(rs) >= CITY_MIN}
    slugs = {}
    for t in groups:
        assert _slug(t) not in slugs and _slug(t) not in ('assets',) + DAY_SLUGS, ('two Ohio towns share an address', t, slugs.get(_slug(t)))
        slugs[_slug(t)] = t
    return groups


def ohio_towns(root):
    """The Ohio towns with a page, A to Z."""
    return sorted(ohio_town_groups(ohio_venues(root)[0]))


def _day_attr(v, x):
    """data-day on a game that runs every week, so the page can mark today's games."""
    return ' data-day="%d"' % x['day'] if _weekly(v, x) else ''


def _ohio_by_day(rows):
    """Each weekday: places with a posted game that day (and its time), then halls whose state license names that day."""
    seen = Counter(r['name'] for r in rows)
    def name(r):  # the street too, where one group runs games at more than one place in town
        return escape(r['name'] + (f' ({r["street"]})' if seen[r['name']] > 1 and r.get('street') else ''))
    out = ''
    for d in WEEK:
        posted = [(r, x) for r in rows for x in r['sessions'] if x['day'] == d]
        licensed = [r for r in rows if d in r.get('license_days', ())]
        if not posted and not licensed:
            continue
        items = ''.join(
            f'<li{_day_attr(r, x)}><a href="#{escape(r["id"])}">{name(r)}</a>, '
            + (escape(_time_range(x['start'])) if x.get('start') else 'see the listing for times')
            + (f' <span class="org">· {escape(x["label"])}</span>' if x.get('label') else '') + '</li>' for r, x in posted)
        items += ''.join(f'<li><a href="#{escape(r["id"])}">{name(r)}</a> <span class="org">· on its state license; call for game times</span></li>'
                         for r in licensed)
        out += f'<h3 id="{DAY_NAMES[d].lower()}">{DAY_NAMES[d]}</h3><ul class="sessions" data-weekly>{items}</ul>'
    return out


def _ohio_notice(o):
    """The state licensing notice or settlement on a hall, in brief, as the Ohio finder shows it."""
    e = o.get('enforcement')
    if not e:
        return ''
    if e['status'] == 'settlement':
        text = f'On {_date_label(e["settlement_date"])} this organization signed a settlement agreement with the Ohio Attorney General.'
        label = 'Read the agreement'
    else:
        text = f'On {_date_label(e["notice_date"])} the Ohio Attorney General notified this organization that it {e["action"]}. This is not a final decision.'
        label = 'Read the notice'
    return (f'<p class="note"><strong>State licensing {"settlement" if e["status"] == "settlement" else "notice"}:</strong> {escape(text)} '
            f'Confirm games are running before you go. {_out(e["url"], label)}</p>')


def _ohio_card(v, s, pick=None):
    """One Ohio listing on a town or day page, from the Ohio finder's record. pick is a day page's weekday: the list of
    bingo days shows that day only (the posted schedule below it still gives the whole week)."""
    o = v['oh']
    center = v['kind'] == 'senior_center'
    if v['posted']:
        badge, pin = f'<span class="badge">{"Senior center bingo" if center else "Bingo"}</span>', 'game'
    elif center:
        badge, pin = '<span class="badge">Senior center bingo</span>', 'game'
    else:
        badge, pin = '<span class="badge muted">Licensed for bingo · game times not posted</span>', 'nodays'
    days = ', '.join(dict.fromkeys(DAY_NAMES[x['day']] for x in v['sessions'])) or ', '.join(DAY_NAMES[d] for d in v.get('license_days', ()))
    sub = ('Senior center bingo' if center else 'Bingo' if v['posted'] else 'Licensed for bingo, game times not posted') + ' · ' + v['city'] + (' · ' + days if days else '')
    if v['posted']:
        sessions = ''.join(
            f'<li{_day_attr(v, x)}><strong>{DAY_NAMES[x["day"]]}</strong>'
            + (f', {escape(_time_range(x["start"]))}' if x.get('start') else '')
            + (f' <span class="org">· {escape(x["label"])}</span>' if x.get('label') else '') + '</li>' for x in _on_day(v, pick))
        if o.get('schedule_source'):
            note = f'This schedule comes from {o["schedule_source"]}. Please call to confirm before you go.'
        elif o.get('schedule_valid_until'):
            note = f'Published dates through {_date_label(o["schedule_valid_until"])}. Call ahead to confirm before you go.'
        else:
            note = 'Call ahead to confirm before you go.'
        when = (f'<div class="when"><p>{_ic("cal")}<strong>Bingo days:</strong></p><ul class="sessions"{"" if v.get("schedule_note") else " data-weekly"}>{sessions}</ul>'
                f'<p><strong>{"Bingo" if center else "When"}:</strong> {escape(o["schedule"])}</p><p class="note">{escape(note)}</p></div>')
    elif v.get('license_days'):
        when = (f'<div class="when"><p>{_ic("cal")}<strong>Days on the state license:</strong> {escape(_and([DAY_NAMES[d] for d in v["license_days"]]))}.</p>'
                '<p class="note">The state lists the days this group may hold bingo, not its game times. Call to ask when games are played.</p></div>')
    elif o.get('schedule'):
        when = f'<div class="when"><p class="note">Bingo dates change here. <a href="../#{escape(v["id"])}">See the dates on the Ohio finder</a> or call ahead.</p></div>'
    else:
        when = '<div class="when"><p class="note">Ask the center when bingo is played.</p></div>'
    price = o.get('cost') if v['posted'] and o.get('cost') and not o.get('price_valid_until') else ''
    if v.get('phone'):
        call = f'<a class="solid" href="tel:{re.sub(r"[^0-9]", "", v["phone"])}">{_ic("phone")}Call {escape(v["phone"])}</a>'
    else:
        call = f'<a class="solid" href="{escape(_maps(o["name"] + " " + v["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("search")}Look up phone number ↗</a>'
    sources = ''.join(f'<li>{_out(x["url"], x["scope"])}</li>' for x in o.get('sources', []) if x.get('url', '').startswith('https://'))
    claim = '' if center else (f' · <a href="{escape(OHIO_CLAIM + "?hall=" + quote(v["name"], safe="") + "&town=" + quote(v["city"], safe=""))}" '
                               'target="_blank" rel="noopener noreferrer">Run this game? Claim it ↗</a>')
    return (f'<article id="{escape(v["id"])}"{_pin(v, pin, sub)}><p>{badge}</p>'
            f'<h3>{escape(v["name"])}</h3><p class="where">{_ic("pin")}{escape(v["city"])}</p>'
            + _ohio_notice(o) + when
            + (f'<p><strong>Price:</strong> {escape(price)}</p>' if price else '')
            + (f'<p class="small"><strong>Who can come:</strong> {escape(o["admission"])}</p>' if o.get('admission') and o['admission'] != OHIO_DEFAULT_ADMISSION else '')
            + f'<div class="big-actions">{call}<a class="outline" href="{escape(_maps(v["address"]))}" target="_blank" rel="noopener noreferrer">{_ic("route")}Directions ↗</a></div>'
            f'<p class="address">{escape(v["address"])} · {escape(_area(v["county"]))}</p>'
            f'<details class="sources"><summary>Where this comes from · checked {_date_label(v["reviewed_on"])}</summary>'
            + (f'<p>Ohio bingo license {escape(o["license_number"])}' + (f' ({escape(o["license_type"])})' if o.get('license_type') else '') + '</p>' if o.get('license_number') else '')
            + ''.join(f'<p>{escape(n)}</p>' for n in o.get('notes', []))
            + (f'<ul>{sources}</ul>' if sources else '') + '</details>'
            f'<p class="small-links"><a href="../#{escape(v["id"])}">See it on the Ohio finder</a> · <a href="{escape(_report(v))}">Report a change</a>{claim}</p></article>')


def _ohio_send():
    """The last panel on an Ohio town page: every game is listed free, and halls can update or claim their listing."""
    return ('<section class="panel" id="run-a-game" aria-labelledby="run-title"><h2 id="run-title">Run a bingo game in Ohio? Get it listed free</h2>'
            '<p>Every game is listed free, for every hall. Send us your game days and the time the first game starts, or claim your '
            'listing so players always see your latest times.</p>'
            '<div class="big-actions"><a class="solid" href="../#submit-details">Add or update your game</a>'
            f'<a class="outline" href="{OHIO_CLAIM}" target="_blank" rel="noopener noreferrer">Claim your listing ↗</a></div>'
            '<p><a href="../../halls/">How Find Bingo works for bingo halls</a> · <a href="../partners.html">Partner with the Ohio Bingo Finder</a></p></section>')


# ---- Day pages (findbingo.org/texas/monday/, findbingo.org/ohio/friday/ and so on) -----------------------------------
# Owner direction, November 27, 2026: older players search "bingo tonight", "monday night bingo near me" and "bingo on
# sunday in <state>". A state gets a page for a weekday when at least DAY_MIN of its listings have a game that day. The
# page lists every such game, town by town (A to Z), earliest start first, with the town pages' cards and the same Event
# markup rules (weekly games only, built from the listing, next date filled in the browser). Ohio's day pages are built
# from the Ohio finder's records and list games with a posted schedule; halls known only from the state's license list
# have no game times, so they stay on the town pages and the finder. No counts anywhere (Travis's rule).
DAY_MIN = 3
DAY_SLUGS = tuple(n.lower() for n in DAY_NAMES)


def _first_start(v, d):
    """A listing's earliest start time on weekday d, for sorting; games with no posted time sort last."""
    return min((x['start'] for x in v['sessions'] if x['day'] == d and x.get('start')), default='99:99')


def _by_weekday(rows):
    out = {}
    for r in rows:
        for d in {x['day'] for x in r['sessions']}:
            out.setdefault(d, []).append(r)
    return {d: rs for d, rs in out.items() if len(rs) >= DAY_MIN}


def day_groups(venues):
    """{(state code, weekday): listings with a game that weekday}, outside Ohio, where at least DAY_MIN listings have one."""
    states = {}
    for v in venues:
        if v['state'] != 'OH':
            states.setdefault(v['state'], []).append(v)
    return {(code, d): rs for code, rows in states.items() for d, rs in _by_weekday(rows).items()}


def ohio_day_groups(rows):
    """{weekday: Ohio listings with a posted game that weekday} (ohio_venues rows), where at least DAY_MIN have one."""
    return _by_weekday(rows)


def ohio_days(root):
    """The weekdays with an Ohio day page, Monday first."""
    groups = ohio_day_groups(ohio_venues(root)[0])
    return [d for d in WEEK if d in groups]


def indexed_day_pages(root):
    """Day pages for the sitemap: 'texas/monday/', 'ohio/friday/' and so on."""
    pages = [(SLUGS[code], d) for code, d in day_groups(load_venues(root))] + [(SLUGS['OH'], d) for d in ohio_days(root)]
    return tuple(f'{slug}/{DAY_SLUGS[d]}/' for slug, d in sorted(pages, key=lambda p: (p[0], WEEK.index(p[1]))))


def _day_page(s, d, rows, town_pages, day_pages, style, analytics, generated_on, ohio=False):
    """A state's page for one weekday: every listing with a game that day, by town, earliest first. town_pages: the
    state's towns with their own page (each town links to it); day_pages: the weekdays with a day page, for "Bingo by day"."""
    code, name, slug = s['code'], s['name'], SLUGS[s['code']]
    day = DAY_NAMES[d]
    url = f'{SITE}/{slug}/{DAY_SLUGS[d]}/'
    heading = f'{day} bingo in {name}'
    title = next(t for t in (f'{heading}: games, times and places | Find Bingo', f'{heading}: games and times | Find Bingo',
                             f'{heading} | Find Bingo') if len(t) <= 70)
    if ohio:
        # Many Ohio schedules give days without a single start time, so the words promise times only where posted.
        description = f'{day} bingo in Ohio, town by town: game times where posted, phone numbers and directions. Free, with a source for every listing.'
        lead = f'Looking for {day} bingo in Ohio? Here is every {day} game with a posted schedule, town by town, earliest first. Call ahead before you go.'
    else:
        description = (f'{day} bingo in {name}, town by town: start times, phone numbers and directions for every game we list. '
                       'Free, with a source for every listing.')
        if len(description) > 165:
            description = f'{day} bingo in {name}, town by town: start times, phone numbers and directions. Free.'
        lead = f'Looking for {day} bingo in {name}? Here is every {day} game we list, town by town, earliest first. Call ahead before you go.'
    assert len(title) <= 70 and len(description) <= 165 and not COUNT_WORDS.search(title + description + lead), (code, day)
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Find Bingo', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': f'Bingo in {name}', 'item': f'{SITE}/{slug}/'},
        {'@type': 'ListItem', 'position': 3, 'name': heading, 'item': url}]}
    towns = {}
    for r in rows:
        towns.setdefault(r['city'], []).append(r)
    order = sorted(towns, key=lambda t: (t.lower(), t))
    for t in order:
        towns[t].sort(key=lambda r: (_first_start(r, d), r['name'].lower(), r['id']))
    rows = [r for t in order for r in towns[t]]
    events = game_events(rows, url, only_day=d, town_urls={t: f'{SITE}/{slug}/{_slug(t)}/' for t in order if t in town_pages})
    card = _ohio_card if ohio else _venue_html
    body = f'<p class="intro">{escape(s["regulator_note"])}</p>'
    if ohio:
        body += ('<p class="note">Many other Ohio halls are licensed by the state for bingo but have not posted game times. '
                 'The <a href="../?all=1">Ohio Bingo Finder</a> and the town pages list them too.</p>')
    body += _days_nav(s, day_pages, '../', current=d)
    if len(order) > 4:
        body += (f'<nav class="counties jump" aria-labelledby="jump-title"><h2 id="jump-title">Jump to your town</h2><ul>'
                 + ''.join(f'<li><a href="#town-{_slug(t)}">{escape(t)}</a></li>' for t in order) + '</ul></nav>')
    if any(r['zip'] in ZIP_POINTS for r in rows):
        body += _map_box('../../', f'the {day} bingo listed below')
    body += ('<div id="listings">' + ''.join(
        f'<section aria-labelledby="town-{_slug(t)}"><h2 id="town-{_slug(t)}">{escape(t)}</h2><div class="grid">'
        + ''.join(card(r, s, pick=d) for r in towns[t]) + '</div><p class="top">'
        + (f'<a href="../{_slug(t)}/">All bingo in {escape(t)}, day by day</a> · ' if t in town_pages else '')
        + '<a href="#top">Back to the top</a></p></section>' for t in order) + '</div>')
    body += (f'<p class="small-links"><a href="../">All bingo in {escape(name)}</a> · <a href="../../">Search every state by ZIP code</a></p>'
             + (_ohio_send() if ohio else _send_times(s, '../../')))
    # The ZIP box carries the day, so the finder opens on this day's games near the ZIP code (Ohio's on the Ohio finder).
    zip_form = (f'<form class="zip-box" action="{"../" if ohio else "../../"}" method="get"><input type="hidden" name="day" value="{d}"><div class="tools">'
                '<div><label for="zip">Type your ZIP code</label><input id="zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" pattern="[0-9]{5}" placeholder="Your 5-digit ZIP" required></div>'
                '<div><label for="radius">How far will you go?</label><select id="radius" name="radius"><option value="10">10 miles</option><option value="25" selected>25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>'
                f'<div><button class="primary" type="submit">{_ic("search")}Find {day} bingo near me</button></div></div>'
                f'<p class="small">Shows {day} bingo near you, closest first.</p></form>')
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(heading)}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n' + _json_ld(crumbs)
            + ('\n<script type="application/ld+json" id="games-ld">' + json.dumps(events, ensure_ascii=False).replace('</', '<\\/') + '</script>' if events else '')
            + '\n</head>')
    return (head + f'<body id="top">{ICONS}<a class="skip" href="#listings">Skip to the bingo list</a>'
            f'<header>{BALLS}<p class="brand"><a href="../../">FindBingo.org</a> · <a href="../">{escape(name)}</a> · free from Veteran Home Guardians</p>'
            f'<h1>{escape(heading)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main>{zip_form}{body}</main>'
            f'{_footer(generated_on, "../../")}{TODAY_SCRIPT}{EVENT_DATES_LD if events else ""}{place_map.script() if "pm-box" in body else ""}<script>{analytics}</script></body></html>\n')


def _state_page(s, states, rows, style, analytics, generated_on, landing, ads=(), events=(), towns=(), day_pages=()):
    code, name, slug = s['code'], s['name'], SLUGS[s['code']]
    words = landing_words(s, rows, landing)
    title, description, lead, heading = words['title'], words['description'], words['welcome'], words['h1']
    url = f'{SITE}/{slug}/'
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Find Bingo', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': f'Bingo in {name}', 'item': url}]}
    rows = sorted(rows, key=lambda r: (r['county'], r['city'], r['name']))
    counties = sorted({r['county'] for r in rows})
    pending = s['coverage'] == 'pending'
    # The welcome in the header already tells this state's story (data/findbingo-landing.json), so the intro under the
    # finder names who oversees bingo there rather than repeating it.
    body = f'<p class="intro">{escape(s["about"] if pending else s["regulator_note"])}</p>' + newbie_line(s)
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
    body += week_chart(name, rows, s.get('hours_note', ''))
    body += _days_nav(s, day_pages, '')
    body += _towns_nav(s, towns, '')
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
            + f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(title.rsplit(" | ", 1)[0])}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + '\n' + _json_ld(crumbs) + '\n</head>')
    weekly = 'data-weekly' in body
    return (head + f'<body id="top">{ICONS}<a class="skip" href="#listings">Skip to the bingo list</a>'
            f'<header>{BALLS}<p class="brand"><a href="../">FindBingo.org</a> · free from Veteran Home Guardians</p><h1>{escape(heading)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main>{zip_form}{body}'
            f'<nav class="states" aria-labelledby="states-title"><h2 id="states-title">Bingo in other states</h2>'
            # Where this state sits, on the guide's equal-square tile map (November 25, 2026); no counts, only a place.
            f'<figure class="where" aria-labelledby="where-cap">{locator(code, name, "where-map")}'
            f'<figcaption id="where-cap">{escape(name)} is the dark square with a ring. Choose another state below.</figcaption></figure>'
            f'<div class="state-buttons">{others}</div>'
            '<p class="small-links"><a href="../">Search every state by ZIP code</a></p></nav></main>'
            f'{_footer(generated_on)}{TODAY_SCRIPT if weekly else ""}{place_map.script() if "pm-box" in body else ""}<script>{analytics}</script></body></html>\n')


def _json_ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def _footer(generated_on, up='../'):
    return ('<footer><p>FindBingo.org is a free community resource from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>. '
            'Listings are free. Ads, when shown, are labeled and never decide which games are listed.</p>'
            '<p class="noprint">Giving Tuesday is December 1: <a href="https://www.zeffy.com/en-US/donation-form/giving-tuesday-no-veteran-left-isolated">give to Veteran Home Guardians</a>.</p>'
            '<p class="noprint">Need help getting to the game? <a href="https://mobilitytalk.org/states/">Mobility Talk</a> lists mobility and disability resources in every state.</p>'
            f'<p class="noprint">Questions or corrections: <a href="mailto:{EMAIL}?subject=FindBingo.org">{EMAIL}</a> · Made by <a href="https://travisvought.com/">Travis Vought</a></p>'
            f'<p class="noprint">{GUIDE_LINKS.format(up=up)}</p>'
            f'<p class="noprint"><a href="{up}about/">About and contact</a> · <a href="{up}privacy/">Privacy</a> · <a href="{up}terms/">Terms of use</a> · <a href="{up}advertise/">Advertise on Find Bingo</a> · <a href="{up}halls/">For bingo halls</a> · <a href="{up}shop/">Bingo gear and gifts</a></p>'
            f'<p class="noprint">Lists updated {_date_label(generated_on)}.</p></footer>')


# Short addresses for posters and word of mouth: findbingo.org/mi and /MI open the Michigan page.
SHORT_REDIRECTS = ''.join(f'/{c} /{slug}/ 301\n/{c.lower()} /{slug}/ 301\n' for c, slug in SLUGS.items() if c != 'OH')
STATE_CSS = ('header a{color:#fff}.intro{font-size:20px;max-width:860px}'
             # The newcomer line under the intro (newbie_line): links to how to play, the words and the state's age.
             '.newbie{display:flex;gap:10px;align-items:flex-start;font-size:18px;max-width:860px;margin:0 0 14px}.newbie .ic{color:var(--accent);margin-top:.15em}'
             '@media print{.newbie{display:none}}'
             # The locator map in "Bingo in other states" (visuals.locator): a dark square with a ring marks this state.
             '.where{margin:4px 0 16px;max-width:300px}.where svg{display:block;width:100%;height:auto}.where figcaption{font-size:17px;margin-top:6px}'
             '@media (prefers-color-scheme:dark){.vz-loc rect{fill:#26343c;stroke:#8fa39a}.vz-loc .vz-loc-cur{fill:#9fd0ef}.vz-loc-ring{stroke:#10181d}}'
             '@media (forced-colors:active){.where svg{forced-color-adjust:none}.vz-loc rect{fill:Canvas;stroke:CanvasText}.vz-loc .vz-loc-cur{fill:CanvasText}.vz-loc-ring{stroke:Canvas}}'
             '@media print{.where{display:none}}'
             '.counties{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 14px;margin:18px 0}.counties h2{font-size:24px;margin:10px 0 8px}'
             '.counties ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
             '.counties a{display:inline-flex;align-items:center;min-height:48px;padding:0 14px;border:2px solid var(--accent);border-radius:24px;color:var(--accent);font-weight:700;text-decoration:none}'
             '#listings>section>h2{font-size:28px;margin:28px 0 10px;scroll-margin-top:12px}.top{font-size:17px;margin:10px 0 0}.top a{display:inline-flex;align-items:center;min-height:44px}'
             '@media print{.counties,.top,#run-a-game,#partner{display:none!important}}'
             # The week chart (week_chart): a ball where listed games begin, a dash where none do; never a count.
             '.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}'
             '.week{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 20px 12px;margin:18px 0}'
             '.week h2{font-size:24px;margin:10px 0 6px;display:flex;align-items:center;gap:10px}.week h2 .ic{color:var(--accent)}.week>p{margin:6px 0}'
             '.week-wrap{overflow-x:auto}.week table{border-collapse:collapse;width:100%;max-width:640px;margin:8px 0;font-size:17px}'
             '.week th,.week td{text-align:center;padding:6px 2px;border-bottom:1px solid var(--line)}.week thead th{font-weight:700;color:var(--head)}'
             '.week tbody th{text-align:left;font-weight:700;padding-right:8px;color:var(--head);line-height:1.2}.week tbody th small{display:block;font-weight:400;font-size:14px;color:inherit;opacity:.85}'
             '.week .off{color:#5b6b64}.ball{display:inline-block;width:22px;height:22px;border-radius:50%;background:var(--accent);border:3px solid var(--accent);'
             'box-shadow:inset 0 0 0 3px var(--card);vertical-align:middle}.week p.small .ball{width:16px;height:16px;border-width:2px;box-shadow:inset 0 0 0 2px var(--card)}'
             '@media (prefers-color-scheme:dark){.week .off{color:#a9b8b1}}'
             '@media (forced-colors:active){.ball{forced-color-adjust:none;background:CanvasText;border-color:CanvasText;box-shadow:inset 0 0 0 3px Canvas}}'
             '@media(max-width:420px){.week{padding:6px 12px 10px}.week table{font-size:15px}.ball{width:18px;height:18px}}'
             '@media print{.week{border:1px solid #999}.ball{-webkit-print-color-adjust:exact;print-color-adjust:exact}}')


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
# The bingo class, About, Privacy, Terms, Advertise, halls and shop pages, linked from every footer and listed in the sitemap.
INFO_PAGES = ('how-to-play-bingo/', 'bingo-terms/', 'pull-tabs/', 'bingo-age-by-state/', 'about/', 'privacy/', 'terms/', 'advertise/', 'halls/', 'shop/')
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
POLICY_DATE = 'November 27, 2026'
TERMS_DATE = 'November 22, 2026'


def _info_page(slug, title, description, heading, lead, body, style, analytics, generated_on, ld=(), trail=(), icons=False):
    """An information page at findbingo.org/<slug>/. ld: extra JSON-LD objects for the head (breadcrumbs, questions);
    trail: (label, address) pairs shown between FindBingo.org and the publisher in the header's brand line."""
    url = f'{SITE}/{slug}/'
    head = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(title)}</title>\n<meta name="description" content="{escape(description)}">\n<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Find Bingo"><meta property="og:title" content="{escape(heading)}">'
            f'<meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/ohio/assets/vhg-logo.png">\n'
            + style + ''.join('\n' + _json_ld(x) for x in ld) + '\n</head>')
    brand = '<a href="../">FindBingo.org</a> · ' + ''.join(f'<a href="{escape(href)}">{escape(label)}</a> · ' for label, href in trail)
    return (head + f'<body id="top">{ICONS if icons else ""}<a class="skip" href="#main">Skip to the page</a>'
            f'<header>{BALLS}<p class="brand">{brand}free from Veteran Home Guardians</p><h1>{escape(heading)}</h1><p class="lead">{escape(lead)}</p></header>'
            f'<main id="main"><div class="info">{body}</div>'
            '<p class="small-links"><a href="../">Find bingo near you</a></p></main>'
            f'{_footer(generated_on)}<script>{analytics}</script></body></html>\n')


def _ext(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'



# The bingo class page (owner direction, November 19, 2026): how a bingo night works, the kinds of games and
# what the words mean, and the unwritten rules, for people new to bingo, many of them older. General
# practice only: state law and each hall's house rules decide the details, and the page says so.
# Pictures for the bingo class (November 24, 2026): original SVG in the site's own colors. Each one's words are on the page
# as text too: the card is described in the paragraph above it, and every pattern is named and explained beside its picture.
BALL_RINGS = ('#2f6fb5', '#c8382c', '#8a8f96', '#2f8a4d', '#e08a1e')  # the header balls' colors
SAMPLE_CARD = ((7, 22, 34, 52, 68), (12, 18, 41, 47, 71), (3, 29, None, 60, 63), (14, 16, 38, 55, 75), (9, 25, 45, 49, 66))


def card_figure():
    """A sample card: the five letters as balls, each column's numbers, and the free space."""
    heads = ''.join(f'<circle cx="{38 + 56 * c}" cy="28" r="24" fill="{ring}"/><circle class="bc-in" cx="{38 + 56 * c}" cy="28" r="15"/>'
                    f'<text class="bc-l" x="{38 + 56 * c}" y="34">{l}</text>' for c, (l, ring) in enumerate(zip('BINGO', BALL_RINGS)))
    ranges = ''.join(f'<text class="bc-r" x="{38 + 56 * c}" y="80">{15 * c + 1}–{15 * c + 15}</text>' for c in range(5))
    cells = ''
    for r, row in enumerate(SAMPLE_CARD):
        for c, n in enumerate(row):
            x, y = 10 + 56 * c, 92 + 56 * r
            cells += (f'<rect class="bc-free" x="{x}" y="{y}" width="56" height="56"/><text class="bc-f" x="{x + 28}" y="{y + 33}">FREE</text>' if n is None
                      else f'<rect x="{x}" y="{y}" width="56" height="56"/><text x="{x + 28}" y="{y + 36}">{n}</text>')
    return ('<figure class="bcard" aria-labelledby="bcard-cap">'
            '<svg viewBox="0 0 300 384" width="300" height="384" role="img" aria-labelledby="bcard-t bcard-d">'
            '<title id="bcard-t">A sample bingo card</title>'
            '<desc id="bcard-d">Five columns headed B, I, N, G and O. B holds 1 to 15, I 16 to 30, N 31 to 45, G 46 to 60 and O 61 to 75. '
            'Each column shows five numbers from its own range, except that the middle square of the N column is the free space.</desc>'
            f'<g class="bc-head">{heads}</g><g class="bc-ranges">{ranges}</g><g class="bc-grid">{cells}</g></svg>'
            '<figcaption id="bcard-cap">A sample card. Each letter’s column holds numbers from its own range of 15, '
            'and the middle square is free.</figcaption></figure>')


# Named patterns, as the squares they need (row, column), counted from the top left.
PATTERNS = (
    ('Straight line', 'Five in a row. This one runs across the middle, through the free space.', [(2, c) for c in range(5)]),
    ('Four corners', 'The four corner squares.', [(0, 0), (0, 4), (4, 0), (4, 4)]),
    ('Postage stamp', 'A block of four squares in a corner.', [(0, 3), (0, 4), (1, 3), (1, 4)]),
    ('Letter X', 'Both lines from corner to corner.', sorted({(i, i) for i in range(5)} | {(i, 4 - i) for i in range(5)})),
    ('Coverall, or blackout', 'Every square on the face.', [(r, c) for r in range(5) for c in range(5)]),
)


def _pattern_svg(squares):
    grid = ''.join(f'<rect x="{5 + 20 * c}" y="{5 + 20 * r}" width="20" height="20"/>' for r in range(5) for c in range(5))
    daubs = ''.join(f'<circle cx="{15 + 20 * c}" cy="{15 + 20 * r}" r="7.5"/>' for r, c in squares)
    return (f'<svg viewBox="0 0 110 110" width="110" height="110" aria-hidden="true" focusable="false">'
            f'<g class="pt-grid">{grid}</g><g class="pt-daub">{daubs}</g></svg>')


def patterns_figure():
    """Common patterns, each a small card with a dot on every square it needs, named and explained in words."""
    items = ''.join(f'<li>{_pattern_svg(sq)}<strong>{escape(name)}</strong><span>{escape(words)}</span></li>' for name, words, sq in PATTERNS)
    return ('<figure class="patterns" aria-labelledby="patterns-cap"><figcaption id="patterns-cap">Some common patterns. '
            'A dot marks each square the pattern needs.</figcaption>'
            f'<ul>{items}</ul></figure>')


LEARN_CSS = (
    # The sample card (card_figure) and the patterns (patterns_figure) on the bingo class page.
    '.bcard{margin:14px 0 6px}.bcard svg{display:block;width:100%;max-width:300px;height:auto;aspect-ratio:300/384}'
    '.bcard figcaption,.patterns figcaption{font-size:17px;max-width:620px}'
    '.bc-in{fill:#fff}.bc-l{font:800 20px system-ui,sans-serif;fill:#183449;text-anchor:middle}'
    '.bc-r{font:700 16px system-ui,sans-serif;fill:var(--ink);text-anchor:middle}'
    '.bc-grid rect{fill:var(--card);stroke:var(--ink);stroke-width:2}.bc-grid rect.bc-free{fill:var(--today)}'
    '.bc-grid text{font:700 22px system-ui,sans-serif;fill:var(--ink);text-anchor:middle}.bc-grid text.bc-f{font-size:14px;letter-spacing:.06em}'
    '.patterns{margin:14px 0 6px}.patterns ul{list-style:none;padding:0;margin:8px 0 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}'
    '.patterns li{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;line-height:1.3}'
    '.patterns svg{display:block;width:96px;height:96px;margin:0 0 6px}.patterns strong{display:block;color:var(--head)}.patterns span{display:block;font-size:16px}'
    '.pt-grid rect{fill:none;stroke:#6f8078;stroke-width:1.5}.pt-daub circle{fill:var(--accent)}'
    # Bingo night, step by step: the list keeps its numbers, drawn as bingo balls.
    '.info ol.night{list-style:none;padding:0;counter-reset:night}.night li{counter-increment:night;position:relative;padding-left:56px;min-height:44px}'
    '.night li::before{content:counter(night);content:counter(night) / "";position:absolute;left:0;top:-2px;width:40px;height:40px;border-radius:50%;'
    'display:flex;align-items:center;justify-content:center;font:800 18px/1 system-ui,sans-serif;color:#183449;'
    'background:radial-gradient(circle,#fff 0 54%,var(--c,#2f6fb5) 56% 100%)}'
    '.night li:nth-child(5n+2){--c:#c8382c}.night li:nth-child(5n+3){--c:#8a8f96}.night li:nth-child(5n+4){--c:#2f8a4d}.night li:nth-child(5n){--c:#e08a1e}'
    '.night li:not(:last-child)::after{content:"";position:absolute;left:19px;top:40px;bottom:-10px;width:2px;background:#6f8078}'
    '@media (prefers-color-scheme:dark){.pt-grid rect{stroke:#8fa39b}.night li:not(:last-child)::after{background:#8fa39b}}'
    '@media (forced-colors:active){.bcard svg,.patterns svg{forced-color-adjust:none}.bcard circle{fill:Canvas;stroke:CanvasText;stroke-width:2}'
    '.bcard text{fill:CanvasText}.bc-grid rect,.bc-grid rect.bc-free{fill:Canvas;stroke:CanvasText}.pt-grid rect{stroke:CanvasText}.pt-daub circle{fill:CanvasText}'
    '.night li::before{background:Canvas;color:CanvasText;border:2px solid CanvasText}.night li:not(:last-child)::after{background:CanvasText}}'
    '@media print{.bcard,.patterns li{break-inside:avoid}.bcard svg,.patterns svg,.night li::before{-webkit-print-color-adjust:exact;print-color-adjust:exact}}')


# ---- Guides for new players (owner direction for the search push, November 27, 2026) -------------------------------
# What people search before their first hall night: how to play (the bingo class, moved here from /learn/ so its address
# matches the search), the words, pull tabs, and how old you have to be in each state. General how-to needs no source;
# every rule or legal fact names its source. Each page links the others, and every footer and the home page link them all.
GUIDE_LINKS = ('New to bingo? <a href="{up}how-to-play-bingo/">How to play bingo</a> · <a href="{up}bingo-terms/">Bingo terms, A to Z</a> · '
               '<a href="{up}pull-tabs/">Pull tabs explained</a> · <a href="{up}bingo-age-by-state/">Bingo age by state</a>')
GUIDE_TRAIL = (('How to play bingo', '../how-to-play-bingo/'),)


def _crumbs(*pairs):
    """BreadcrumbList for an information page: Find Bingo first, then (name, path) pairs."""
    items = [('Find Bingo', SITE + '/')] + [(name, f'{SITE}/{path}') for name, path in pairs]
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n, 'item': u} for i, (n, u) in enumerate(items, 1)]}


def _questions(faq):
    """Common questions, written on the page and given to search engines as FAQPage markup with the very same words."""
    html = ('<section class="faq" aria-labelledby="faq-title"><h2 id="faq-title">Common questions</h2>'
            + ''.join(f'<h3>{escape(q)}</h3><p>{escape(a)}</p>' for q, a in faq) + '</section>')
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}
    return html, ld


def _toc(items):
    return ('<nav class="toc" aria-labelledby="toc-title"><h2 id="toc-title">On this page</h2><ul>'
            + ''.join(f'<li><a href="#{i}">{escape(label)}</a></li>' for i, label in items) + '</ul></nav>')


GUIDES = (('how-to-play-bingo', 'book', 'How to play bingo', 'A bingo night, step by step'),
          ('bingo-terms', 'words', 'Bingo terms, A to Z', 'What the words mean'),
          ('pull-tabs', 'ticket', 'Pull tabs explained', 'The paper tickets sold beside bingo'),
          ('bingo-age-by-state', 'id', 'Bingo age by state', 'How old you have to be to play'))


def _guide_list(up, skip=(), practice=''):
    """The guides as large links with an icon and a line each; practice: an extra link to the free practice game."""
    return ('<ul class="guide-links">'
            + ''.join(f'<li><a href="{up}{slug}/">{_ic(icon)}<strong>{escape(label)}</strong><span>{escape(sub)}</span></a></li>'
                      for slug, icon, label, sub in GUIDES if slug not in skip)
            + (f'<li><a href="{practice}">{_ic("search")}<strong>Practice hall bingo</strong><span>Free faces and a new pattern every game</span></a></li>' if practice else '')
            + '</ul>')


def _more(*skip):
    """The other guides, at the foot of each guide page."""
    return '<h2 id="keep-learning">Keep learning</h2>' + _guide_list('../', skip, practice='../#play')


def guides_panel():
    """The home page's panel for first-timers, under the practice game."""
    return ('<section class="panel" id="new-to-bingo" aria-labelledby="new-title"><h2 id="new-title">New to hall bingo?</h2>'
            '<p>What to expect on your first night, what the words mean, and how old you have to be, in plain words.</p>'
            + _guide_list('') + '</section>')


# The guide links (on the home page and at the foot of each guide) and the newcomer line on state pages.
GUIDE_LINKS_CSS = (
    '.guide-links{list-style:none;padding:0;margin:10px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}'
    '.guide-links li{margin:0}.guide-links a{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;align-items:center;min-height:64px;padding:10px 14px;'
    'background:var(--card);border:2px solid var(--line);border-radius:12px;text-decoration:none;color:var(--ink)}'
    '.guide-links a:hover,.guide-links a:focus-visible{border-color:var(--accent)}.guide-links .ic{grid-row:span 2;width:30px;height:30px;margin:0;color:var(--accent)}'
    '.guide-links strong{color:var(--link);font-size:19px;text-decoration:underline}.guide-links span{font-size:16px}'
    '@media (forced-colors:active){.guide-links a{border-color:CanvasText}}@media print{.guide-links{display:none}}')
GUIDE_CSS = (
    '.toc{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:4px 18px 10px;margin:14px 0}.toc h2{font-size:20px;margin:10px 0 4px}'
    '.toc ul{columns:2 230px;margin:0;padding-left:20px}.toc li{margin:4px 0;break-inside:avoid}.toc a{display:inline-block;min-height:32px;padding:4px 0}'
    '.faq h3{font-size:20px;color:var(--head);margin:18px 0 4px}'
    '.info ol.steps li{margin:8px 0}'
    '.alpha{margin:12px 0}.alpha ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}'
    '.alpha a{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:50%;border:3px solid var(--accent);'
    'color:var(--head);font-weight:800;text-decoration:none;background:var(--card)}.alpha a:hover,.alpha a:focus-visible{background:var(--today)}'
    '.letter{font-size:30px;margin:26px 0 0;border-bottom:2px solid var(--line);scroll-margin-top:12px}.info dt{scroll-margin-top:12px}'
    '.see{font-size:16px}'
    'table.ages{border-collapse:collapse;width:100%;margin:10px 0;font-size:18px}.ages caption{text-align:left;font-weight:700;color:var(--head);padding:4px 0 8px}'
    '.ages th,.ages td{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid var(--line)}.ages thead th{color:var(--head)}'
    '.ages tbody th{width:28%;scroll-margin-top:12px}.ages tbody th:target,.ages tbody th:target+td{background:var(--today)}.ages .src{display:block;font-size:15px;margin-top:4px}'
    '.ptab{margin:14px 0}.ptab svg{display:block;width:100%;max-width:360px;height:auto}.ptab figcaption{font-size:17px;max-width:620px}'
    '.pt-paper{fill:#f3e3b3;stroke:#7a5712;stroke-width:2}.pt-tab{fill:#d9b45a;stroke:#7a5712;stroke-width:1.5}.pt-open{fill:#fff;stroke:#7a5712;stroke-width:1.5}'
    '.pt-perf{fill:none;stroke:#7a5712;stroke-width:1.5;stroke-dasharray:4 3}.pt-word{font:700 14px system-ui,sans-serif;fill:#3b2f12;text-anchor:middle}'
    '.pt-sym{font:800 24px system-ui,sans-serif;fill:#c8382c;text-anchor:middle}.pt-head{font:800 16px system-ui,sans-serif;fill:#3b2f12;text-anchor:middle}'
    '@media (forced-colors:active){.ptab svg{forced-color-adjust:none}.pt-paper,.pt-tab,.pt-open{fill:Canvas;stroke:CanvasText}.pt-perf{stroke:CanvasText}'
    '.pt-word,.pt-sym,.pt-head{fill:CanvasText}.alpha a{border-color:CanvasText}}'
    '@media print{.toc,.alpha{display:none}.ptab svg{-webkit-print-color-adjust:exact;print-color-adjust:exact}}')


# The bingo class (owner direction, November 19, 2026; written to the first-timer nervous about the unwritten rules,
# November 23): how a bingo night works, from buying in to claiming a win, what to bring and the manners regulars expect.
# General practice only: state law and each hall's house rules decide the details, and the page says so.
LEARN_FAQ = (
    ('How much does it cost to play bingo at a hall?',
     'It depends on the hall. Most start you with a pack that covers the regular games, and extras such as early birds and specials cost more. '
     'Call ahead or check the hall’s flyer for prices, and bring cash.'),
    ('What happens if two people get bingo at the same time?',
     'When two or more players bingo on the same ball, the prize is split evenly between them. Each hall’s house rules say exactly how a split works.'),
    ('Do I have to shout “Bingo!” out loud?',
     'Yes. At most halls you must call it out before the next ball is drawn. Even with an electronic unit that tells you that you have won, '
     'plan to call out unless the hall tells you otherwise.'),
    ('Can I bring my own dauber?',
     'Yes, at almost every hall. Halls sell them at the counter too, and many regulars bring a favorite color.'),
)


def learn_page():
    faq_html, faq_ld = _questions(LEARN_FAQ)
    body = (
        '<p><a href="../#play">Want to warm up first? Practice free, with hall-style faces and a new pattern every game.</a></p>'
        + _toc((('night', 'What happens on a bingo night'), ('buying-in', 'Buying in: packs, paper and electronics'), ('card', 'The card'),
                ('games', 'The games in a night'), ('calling', 'How the numbers are called'), ('claiming', 'How to claim a win'),
                ('splitting', 'When prizes are split'), ('bring', 'What to bring'), ('rules', 'The unwritten rules'),
                ('help', 'Help for eyes, ears and hands'), ('age', 'How old you have to be'), ('states', 'What changes from state to state'),
                ('faq-title', 'Common questions')))
        + '<h2 id="night">What happens on a bingo night</h2>'
        '<ol class="night" role="list"><li><strong>Doors open early,</strong> often an hour or more before the first game. Regulars come early to get a seat, buy their paper and have supper from the kitchen.</li>'
        '<li><strong>You buy in at the counter.</strong> Most halls start you with a <em>pack</em> (also called a package or admission) that covers the regular games. Extra sheets and special games cost extra.</li>'
        '<li><strong>Early birds</strong> are a few warm-up games before the main session. They are usually sold separately.</li>'
        '<li><strong>The caller draws numbered balls</strong> and reads each one out, letter first: “B-7.” The number also lights up on a board or TV screens.</li>'
        '<li><strong>When you have the pattern, you shout “Bingo!”</strong> A worker comes to your seat, reads your numbers back to the caller, and you are paid if it checks out.</li>'
        '<li><strong>There is usually a break</strong> halfway through, with the kitchen open and other games, such as pull tabs, for sale.</li>'
        '<li><strong>The night ends with the big one,</strong> often a coverall or a jackpot game.</li></ol>'
        '<h2 id="buying-in">Buying in: packs, paper and electronics</h2>'
        '<p>At most halls you start by buying a <strong>pack</strong>. It is the least you can buy to play that night, and it covers the regular games. '
        'The hall’s price board or flyer lists what each pack holds and what it costs.</p>'
        '<p>After the pack, the rest is up to you: extra sheets to play more faces, early birds, specials, a bonanza or a jackpot game. '
        'Many halls sell these together as a bundle, and some ask you to buy the pack before anything else. Bring cash, in small bills: many halls take nothing else.</p>'
        '<h3>Paper</h3><p>Paper bingo comes in <strong>sheets</strong> of several faces, often a different color for each game, so the caller can say “game six is on the green paper.” '
        'A set of sheets for the whole night is sometimes sold as a <strong>packet</strong>. You mark paper with a <strong>dauber</strong> (or dabber), a bottle of ink with a sponge tip. '
        'Halls sell them, and many players bring their own favorite color.</p>'
        '<h3>Electronic bingo</h3><p>Many halls rent <strong>electronic bingo</strong> units for the session. The unit holds your cards, marks every number as it is called, '
        'and shows when you are one number away or have a bingo. It makes playing many faces easy, and it helps if your eyes or hands get tired. '
        'Ask the counter how the hall wants you to call a win from one.</p>'
        '<h3>Hard cards</h3><p>Some halls and senior centers still use <strong>hard cards</strong>: reusable cards with sliding windows or chips to mark the numbers.</p>'
        '<h2 id="card">The card</h2>'
        '<p>An American bingo card has five columns, B, I, N, G and O, and 75 numbers in all. B holds 1 to 15, I holds 16 to 30, N holds 31 to 45, G holds 46 to 60, and O holds 61 to 75. '
        'The middle square is a <strong>free space</strong>: it counts as already marked.</p>'
        + card_figure() +
        '<p>Each card is called a <strong>face</strong>. A paper <strong>sheet</strong> holds several faces, and the number of faces is said with “on”: a <strong>6-on</strong> sheet has six faces, a <strong>12-on</strong> has twelve. '
        'More faces give you more chances, and more to watch. New players do well to start with fewer faces.</p>'
        '<h2 id="games">The games in a night</h2>'
        '<p>Every game has a <strong>pattern</strong>, the shape you need to win. The caller says it before the first ball, and it is often shown on the board. '
        'Listen for it every game: four corners does not win a game that needs a coverall.</p>'
        + patterns_figure() +
        '<dl>'
        '<dt><strong>Early birds</strong></dt><dd>Short games before the main session, usually sold separately. A good way to settle in.</dd>'
        '<dt><strong>Regular games</strong></dt><dd>The main games of the night, covered by your pack. Each pays a set prize.</dd>'
        '<dt><strong>Specials</strong></dt><dd>Extra games sold separately, often on their own colored paper, usually for bigger prizes.</dd>'
        '<dt><strong>Progressive jackpot</strong></dt><dd>A big prize that must be won within a set number of balls. When nobody wins in time, a smaller consolation prize is usually paid, '
        'and the jackpot grows for next time, often with one more ball allowed.</dd>'
        '<dt><strong>Coverall, or blackout</strong></dt><dd>Every square on the face must be marked. It usually pays the most and often ends the night.</dd>'
        '</dl>'
        '<p>More words you will hear, from bonanza to sleeper, are in <a href="../bingo-terms/">our bingo terms glossary</a>. '
        'The paper tickets many halls sell between games are a separate game: <a href="../pull-tabs/">how pull tabs work</a>.</p>'
        '<h2 id="calling">How the numbers are called</h2>'
        '<p>The caller draws balls from a machine that mixes them with air, called a <strong>blower</strong>, or from a random number generator at halls that use one. '
        'Each number is read out letter first, “N-34,” and lit up on the <strong>flashboard</strong>, a big board with every number from 1 to 75. '
        'Many halls also show the last number called, and the pattern, on TV screens around the room.</p>'
        '<p>Callers keep a steady pace, a few seconds between balls. If you miss one, look at the board: it shows every number called so far in that game. '
        'When someone calls bingo, the caller stops until the card is checked.</p>'
        '<h2 id="claiming">How to claim a win</h2>'
        '<ol class="steps"><li><strong>Call out “Bingo!”</strong> loud and clear as soon as the last number you need is called, before the next ball is drawn.</li>'
        '<li><strong>Hold up your card</strong> or raise your hand so a floor worker can find you.</li>'
        '<li><strong>Leave your card as it is.</strong> The worker reads the number printed on your face and the numbers in your pattern back to the caller, who checks them against the balls drawn.</li>'
        '<li><strong>If it is good,</strong> the caller says so and closes the game. You are paid at your seat or at the counter, often in cash.</li>'
        '<li><strong>If it was a mistake,</strong> just say so. It happens to everyone, and the game goes on.</li></ol>'
        '<p>If you have a bingo and say nothing until the next ball is drawn, players call that a <strong>sleeper</strong>, and at most halls it is lost. '
        'Big prizes can need a photo ID and a tax form, so bring your ID.</p>'
        '<h2 id="splitting">When prizes are split</h2>'
        '<p>When two or more players bingo on the same ball, the prize is <strong>split</strong> evenly. If two players win a $100 prize on the same ball, each gets $50. '
        'That is normal, not bad luck. Each hall’s house rules say how a split works, including how it rounds the money. A bingo called late, after the next ball, usually does not share in the prize.</p>'
        '<h2 id="bring">What to bring</h2>'
        '<ul><li><strong>Cash, in small bills,</strong> for your pack, extras, the kitchen and pull tabs.</li>'
        '<li><strong>A photo ID.</strong> Halls may check age, and big prizes can need ID.</li>'
        '<li><strong>Daubers,</strong> if you have a favorite color. Halls sell them too.</li>'
        '<li><strong>Reading glasses,</strong> if you use them.</li>'
        '<li><strong>A sweater.</strong> Big halls can be cool, even in summer.</li>'
        '<li><strong>A seat cushion</strong> for a long night on folding chairs.</li>'
        '<li><strong>Your lucky charm.</strong> Plenty of regulars have one.</li></ul>'
        '<h2 id="rules">The unwritten rules every regular expects</h2>'
        '<ul>'
        '<li><strong>Ask before you sit.</strong> Regulars often sit in the same seats every week, and some halls let people hold seats while others forbid it. A friendly “Is this seat taken?” goes a long way.</li>'
        '<li><strong>Keep it quiet while numbers are called.</strong> Talk between games. Put your phone on silent. People are listening closely, and a missed number can cost someone a win.</li>'
        '<li><strong>Shout “Bingo!” loud and clear, and right away.</strong> At most halls you must call it before the next ball is drawn.</li>'
        '<li><strong>Don’t touch your card after you call.</strong> Hold it still until the worker has read it back.</li>'
        '<li><strong>Stay quiet while a card is checked.</strong> The caller may ask, “Any other bingos?” If you have one too, speak up then.</li>'
        '<li><strong>Be a good sport.</strong> A groan when someone else wins is common, but say congratulations. Never grumble at the caller about the numbers.</li>'
        '<li><strong>Leave other people’s things alone.</strong> Don’t touch another player’s cards, daubers, or lucky charms. Many players take their charms very seriously.</li>'
        '<li><strong>Ask before you tip.</strong> Many charity games are run by volunteers, and some states do not allow workers to take tips. A thank-you is always welcome.</li>'
        '<li><strong>Buy from the kitchen if you can.</strong> At charity bingo, the food and drink help pay for the cause. Ask before bringing your own.</li>'
        '</ul>'
        '<h2 id="help">Help for eyes, ears and hands</h2>'
        '<ul><li>Sit where you can see the board or a screen and hear the caller well. Tell a worker if you have trouble hearing; they want you to enjoy the game.</li>'
        '<li>Start with fewer faces. You can always buy more next time.</li>'
        '<li>Ask about electronic handhelds that mark numbers for you, and about large-print cards.</li>'
        '<li>Ask about parking, steps, ramps and restrooms before you go. Our <a href="https://mobilitytalk.org/states/">Mobility Talk</a> site lists help with getting around in every state.</li></ul>'
        '<h2 id="age">How old you have to be</h2>'
        '<p>It depends on the state. In most states where Find Bingo lists games, charity bingo is for players 18 and older. Missouri lets players start at 16, '
        'and several states let younger players play beside a parent or guardian. Some halls keep children out even where the law allows them. '
        '<a href="../bingo-age-by-state/">See the age for each state, with the law it comes from</a>.</p>'
        '<h2 id="states">What changes from state to state</h2>'
        '<p>Each state writes its own bingo law, and each hall adds its own house rules. The things that most often differ:</p>'
        '<ul><li><strong>Age.</strong> See <a href="../bingo-age-by-state/">bingo age by state</a>.</li>'
        '<li><strong>Who may run games.</strong> Usually charities, churches, veterans’ posts, fire companies and similar groups, and sometimes only for their members and guests.</li>'
        '<li><strong>Prize limits and how often games may run,</strong> such as a top prize per game or a number of sessions a week.</li>'
        '<li><strong>Pull tabs and instant tickets.</strong> Whether halls may sell them, and to whom. See <a href="../pull-tabs/">pull tabs explained</a>.</li>'
        '<li><strong>Smoking, alcohol and payment.</strong> Some halls are smoke-free, some serve alcohol, and some states do not let halls take cards for certain games.</li>'
        '<li><strong>Free bingo.</strong> Some places, such as senior centers, play just for fun or small prizes. A few states allow only free bingo.</li></ul>'
        '<p>Every state has its own page on Find Bingo that names who oversees bingo there. <a href="../">Pick your state or type your ZIP code</a> to find it, along with the games near you.</p>'
        + faq_html +
        '<h2 id="ready">Ready to play?</h2>'
        '<p>Call the hall before your first visit. Ask what time doors open, how much a pack costs, whether they take cards, and whether there is anything a new player should know. '
        'Most halls are glad to see a new face.</p>'
        '<div class="big-actions"><a class="solid" href="../">Find bingo near you</a></div>'
        + _more('how-to-play-bingo'))
    return (
        'How to Play Bingo: A Friendly Class for First-Timers | FindBingo.org',
        'How to play bingo at a hall: buying in, packs and electronics, early birds, specials, claiming a win, splitting prizes and the unwritten rules regulars expect.',
        'How to play bingo at a hall',
        'Nervous about the unwritten rules? Most first-timers are. Here is how a bingo night works, from buying in to calling your win, plus what to bring and the manners regulars expect. Every hall has its own house rules, so ask at the counter too.',
        body), (_crumbs(('How to play bingo', 'how-to-play-bingo/')), faq_ld)


# Bingo words, A to Z: one entry per word, each with its own address (#term-dauber), grouped under letter headings.
# A "see" entry points to the word that explains it.
GLOSSARY = (
    ('Admission', 'Another word for the pack you buy to play the regular games. Some halls call it a package.', None),
    ('Any line', None, 'Straight line'),
    ('Ball', 'Each of the 75 numbered balls the caller draws. Balls also count the draws: a progressive jackpot “in 50 balls” must be won by the 50th number called.', None),
    ('Blackout', None, 'Coverall'),
    ('Blower', 'The machine that mixes the balls with air and pushes one up at a time for the caller.', None),
    ('Bonanza', 'A game where some numbers are drawn ahead of time and posted. You mark what is already out, and the rest are called later in the night.', None),
    ('Break-open', 'Another name for a pull tab ticket.', None),
    ('Caller', 'The person who draws the balls and reads out each number, letter first.', None),
    ('Card', 'The grid of numbers you play, with five columns under the letters B, I, N, G and O. One card on a paper sheet is called a face.', None),
    ('Consolation prize', 'The smaller prize paid when nobody wins a progressive jackpot within its set number of balls.', None),
    ('Coverall', 'Every square on the face marked. Also called a blackout. It usually pays the most of any game in the night.', None),
    ('Crazy', 'A pattern that may sit any way around. A crazy T can be upside down or on its side; a crazy kite can point into any corner.', None),
    ('Dauber', 'A bottle of ink with a sponge tip, for marking paper. Also spelled dabber.', None),
    ('Double bingo', 'Two patterns, or the same pattern twice, on one face. Also called a two-part game.', None),
    ('Early birds', 'Warm-up games before the main session, usually sold separately.', None),
    ('Electronic bingo', 'A handheld or tabletop unit, rented for the session, that holds your cards and marks each number as it is called.', None),
    ('Face', 'One card’s grid of numbers. A paper sheet holds several faces.', None),
    ('Flare', 'The display card for a box of pull tab tickets. It shows the winning symbols and the prize for each.', None),
    ('Flashboard', 'The big board that lights up each number as it is called. Also called the board.', None),
    ('Floor worker', 'A worker who checks winning cards, pays prizes and sells extras on the floor. Some halls say runner.', None),
    ('Free space', 'The middle square of the card. It counts as already marked.', None),
    ('Good bingo', 'What the caller says when a winning card checks out. The game is then closed.', None),
    ('Hard card', 'A reusable card with sliding windows or chips, used instead of paper.', None),
    ('Hard way', 'A bingo made without using the free space. Some games pay more for a win made the hard way.', None),
    ('House rules', 'The hall’s own rules, on things like saving seats, splitting prizes and calling a win. Look for them posted near the counter, or ask.', None),
    ('Instant bingo', 'Another name for pull tab tickets in some states.', None),
    ('Jackpot', 'A big prize game, often near the end of the night.', None),
    ('Letter games', 'Patterns shaped like a letter, such as a T, an L or an X.', None),
    ('Magic number', 'A number drawn at the start of a game that counts as marked on every card, or that pays extra if a win comes on it. Also called a wild number. Each hall runs it its own way.', None),
    ('Ninety-ball bingo', 'The British game, with a card of three rows. American halls almost always play 75-ball bingo.', None),
    ('On', 'How the faces on a sheet are counted. A 6-on sheet has six faces; a 12-on has twelve.', None),
    ('Pack', 'What you buy to play the regular games, and at most halls the least you can buy. Also called a package or admission.', None),
    ('Packet', 'A set of paper with the sheets for each game of the night.', None),
    ('Pattern', 'The shape you need to win a game. The caller announces it before the first ball.', None),
    ('Perm', 'The number printed on a paper face, which the floor worker reads to check a win. Also called the card number.', None),
    ('Postage stamp', 'A block of four squares in a corner of the card.', None),
    ('Progressive jackpot', 'A prize that must be won within a set number of balls. When nobody does, it grows for next time.', None),
    ('Pull tab', 'A paper ticket with tabs you pull open to see right away whether you won. A separate game from the called numbers.', None),
    ('Quickie', 'A fast, cheap game, sometimes played between the regular games. Also called a speed game.', None),
    ('Regular games', 'The main games of the night, covered by your pack.', None),
    ('Runner', None, 'Floor worker'),
    ('Seal card', 'A pull tab game where some winners are decided later, when a seal on the display card is opened.', None),
    ('Session', 'One full set of games. Some halls run an afternoon session and an evening session.', None),
    ('Sheet', 'One piece of bingo paper, holding several faces.', None),
    ('Sleeper', 'A winning card nobody called. At most halls it is lost once the next ball is drawn.', None),
    ('Specials', 'Extra games sold separately, often on their own colored paper.', None),
    ('Split', 'When two or more players win on the same ball, they share the prize evenly.', None),
    ('Straight line', 'Five in a row across, down or corner to corner. The free space counts. Also called any line.', None),
    ('Tip board', 'A board of pull tab tickets with a sealed winning name or number, opened once the board sells out.', None),
    ('Two-part game', None, 'Double bingo'),
    ('U-Pick-’Em', 'You choose your own numbers on a blank card, a bit like a lottery ticket.', None),
    ('Wild number', None, 'Magic number'),
)
GLOSSARY_LINKS = {'Pull tab': ('../pull-tabs/', 'How pull tabs work'), 'Seal card': ('../pull-tabs/#kinds', 'Pull tab games'),
                  'Tip board': ('../pull-tabs/#kinds', 'Pull tab games'), 'Break-open': ('../pull-tabs/', 'How pull tabs work'),
                  'Instant bingo': ('../pull-tabs/', 'How pull tabs work'), 'Flare': ('../pull-tabs/#how', 'Reading a pull tab'),
                  'Pattern': ('../how-to-play-bingo/#games', 'Common patterns, with pictures'),
                  'Card': ('../how-to-play-bingo/#card', 'A sample card'), 'Split': ('../how-to-play-bingo/#splitting', 'When prizes are split'),
                  'Sleeper': ('../how-to-play-bingo/#claiming', 'How to claim a win'), 'Pack': ('../how-to-play-bingo/#buying-in', 'Buying in')}


def _term_id(word):
    return 'term-' + _slug(word.replace('’', ''))


def glossary_page():
    words = [w for w, _, _ in GLOSSARY]
    assert words == sorted(words, key=str.lower) and len(set(words)) == len(words), 'glossary is A to Z, each word once'
    assert all(see in words and dict((w, d) for w, d, _ in GLOSSARY)[see] for _, _, see in GLOSSARY if see), 'every see points to a defined word'
    letters = sorted({w[0].upper() for w in words})
    nav = ('<nav class="alpha" aria-labelledby="alpha-title"><h2 id="alpha-title" class="vh">Jump to a letter</h2><ul>'
           + ''.join(f'<li><a href="#letter-{l.lower()}"><span class="vh">Words starting with </span>{l}</a></li>' for l in letters) + '</ul></nav>')
    body = ''
    for l in letters:
        body += f'<h2 class="letter" id="letter-{l.lower()}">{l}</h2><dl>'
        for word, meaning, see in GLOSSARY:
            if word[0].upper() != l:
                continue
            if see:
                body += f'<dt id="{_term_id(word)}"><strong>{escape(word)}</strong></dt><dd>See <a href="#{_term_id(see)}">{escape(see.lower() if see != "Pack" else see)}</a>.</dd>'
            else:
                extra = GLOSSARY_LINKS.get(word)
                body += (f'<dt id="{_term_id(word)}"><strong>{escape(word)}</strong></dt><dd>{escape(meaning)}'
                         + (f' <a class="see" href="{extra[0]}">{escape(extra[1])}</a>' if extra else '') + '</dd>')
        body += '</dl>'
    body = ('<p>Here is what the words mean, A to Z. For how they fit together on a bingo night, read <a href="../how-to-play-bingo/">how to play bingo</a>.</p>'
            + nav + body + '<p class="top"><a href="#top">Back to the top</a></p>' + _more('bingo-terms'))
    return ('Bingo Terms and Slang: A Glossary of Hall Bingo Words | FindBingo.org',
            'What do coverall, early birds, dauber, sleeper and 6-on mean? A plain A to Z glossary of the words you will hear at a bingo hall, for first-timers.',
            'Bingo terms, A to Z',
            'Hearing words like coverall, sleeper and early birds and nodding along? You are not alone. Here is what every word you are likely to hear at a bingo hall means, in plain English.',
            body), (_crumbs(('How to play bingo', 'how-to-play-bingo/'), ('Bingo terms', 'bingo-terms/')),)


def pull_tab_figure():
    """The back of a pull tab ticket: three tabs, the top one pulled open to show three sevens. Words on the page say the same."""
    rows = ''
    for i, sym in enumerate(('7', None, None)):
        y = 52 + 46 * i
        if sym:
            rows += (f'<rect class="pt-open" x="34" y="{y}" width="190" height="36" rx="4"/>'
                     + ''.join(f'<text class="pt-sym" x="{74 + 55 * k}" y="{y + 27}">7</text>' for k in range(3))
                     + f'<path class="pt-tab" d="M224 {y}h70v36h-70z"/><text class="pt-word" x="259" y="{y + 23}">OPEN</text>')
        else:
            rows += (f'<rect class="pt-tab" x="34" y="{y}" width="190" height="36" rx="4"/><path class="pt-perf" d="M34 {y + 18}h190"/>'
                     f'<text class="pt-word" x="129" y="{y + 23}">PULL</text>')
    return ('<figure class="ptab" aria-labelledby="ptab-cap"><svg viewBox="0 0 320 200" width="320" height="200" role="img" aria-labelledby="ptab-t ptab-d">'
            '<title id="ptab-t">The back of a pull tab ticket</title>'
            '<desc id="ptab-d">A paper ticket with three tabs in a row. The top tab has been pulled open and shows three sevens. The other two tabs are still closed and say pull.</desc>'
            '<rect class="pt-paper" x="14" y="12" width="292" height="178" rx="10"/><text class="pt-head" x="160" y="38">PULL ALL TABS</text>'
            + rows + '</svg><figcaption id="ptab-cap">The back of a pull tab ticket. Pull each tab to see the symbols underneath. '
            'A line that matches a winning line on the flare, like these three sevens might, is a winner.</figcaption></figure>')


PULL_TAB_FAQ = (
    ('Are pull tabs the same as bingo?',
     'No. Pull tabs are paper tickets you open to see right away whether you won. Bingo is played on cards while a caller draws numbers. Many halls sell both.'),
    ('How do I know if my pull tab won?',
     'Pull every tab and compare the symbols to the winning lines printed on the flare, the display card for that box of tickets. '
     'If a line matches, take the ticket to the counter or a floor worker to be paid.'),
    ('Can I buy pull tabs at every bingo hall?',
     'No. Whether a hall may sell them depends on the state’s law and the hall’s license, so call ahead and ask.'),
)


def pull_tabs_page(states):
    by = {s['code']: s for s in states}
    va, mn = by['VA']['age']['sources'][0], by['MN']['age']['sources'][0]
    faq_html, faq_ld = _questions(PULL_TAB_FAQ)
    body = (
        '<h2 id="what">What is a pull tab?</h2>'
        '<p>A pull tab is a small paper ticket sold for a set price. The back has a row of tabs, each sealed over a line of symbols. '
        'Pull the tabs open, and if a line matches a winning line, you win right away. No numbers are called: it is a separate game from bingo, '
        'and many halls sell tickets before the games, at the break and between games.</p>'
        + pull_tab_figure() +
        '<p>They go by many names, depending on where you are: pull tabs, instant bingo, break-opens, jar tickets, tip boards and charity game tickets, among others.</p>'
        '<h2 id="how">How to play one</h2>'
        '<ol class="steps"><li><strong>Buy tickets</strong> at the counter, from a floor worker, or from a ticket machine where the hall has one.</li>'
        '<li><strong>Look at the flare,</strong> the display card for that box of tickets. It shows each winning line and its prize.</li>'
        '<li><strong>Pull every tab</strong> on the back of each ticket. A winner can be on the last line.</li>'
        '<li><strong>Compare each line to the flare</strong> for the box you bought from. Prizes differ from box to box.</li>'
        '<li><strong>Take a winner to the counter</strong> or a floor worker to be paid. Keep it whole: a torn or marked ticket can be hard to check.</li></ol>'
        '<h2 id="kinds">Other kinds you may see</h2>'
        '<dl><dt><strong>Seal cards</strong></dt><dd>Some tickets win the right to a seal prize. Hold on to them: the winner is found when the seal on the display card is opened, '
        'usually once the box sells out.</dd>'
        '<dt><strong>Tip boards</strong></dt><dd>A board of tickets with a sealed winning name or number, opened once the board sells out.</dd>'
        '<dt><strong>Event tickets</strong></dt><dd>Tickets whose winner depends on a number called in the bingo game. Keep them until that game ends.</dd>'
        '<dt><strong>Electronic pull tabs</strong></dt><dd>In some places you will see versions played on a screen instead of paper.</dd></dl>'
        '<h2 id="where">Do bingo halls sell them? It depends on the state</h2>'
        '<p>Each state’s law decides whether charities may sell pull tabs at all, where and when, and who may buy them. '
        'Some halls sell them all session, some only at certain times, and some not at all. To know what a hall near you offers, call ahead, '
        'or open <a href="../">your state’s page on Find Bingo</a>, which names the office that oversees bingo there.</p>'
        '<h2 id="age">How old you have to be</h2>'
        '<p>Even where children may play bingo beside a parent, pull tabs are often for adults only. Virginia, for example, lets younger players play bingo '
        f'with a parent or legal guardian, but no one under 18 may play paper instant bingo, pull tabs or seal cards ({_ext(va["url"], "Virginia Administrative Code, 11VAC20-20-60")}). '
        f'Minnesota bars anyone under 18 from playing pull tabs and tipboards ({_ext(mn["url"], "Minnesota Statutes, section 349.181")}). '
        'Both checked November 27, 2026. <a href="../bingo-age-by-state/">See the bingo age for each state</a>.</p>'
        '<h2 id="tips">Tips for new players</h2>'
        '<ul><li>Pull every tab before you decide a ticket lost.</li>'
        '<li>Check each ticket against the flare for its own box.</li>'
        '<li>Hold on to seal card and event tickets until the seal is opened or the game ends.</li>'
        '<li>Set a spending limit before you start, as you would for any night out.</li>'
        '<li>Ask a floor worker if you are not sure whether a ticket won. They check tickets all night.</li></ul>'
        + faq_html + _more('pull-tabs'))
    return ('Pull Tabs and Instant Bingo Tickets: How They Work | FindBingo.org',
            'What pull tabs are, how to read one, how to tell if you won, and why whether a bingo hall sells them depends on the state. A plain guide for new players.',
            'Pull tabs, explained',
            'Seen people at the bingo hall tearing open little paper tickets? Those are pull tabs. Here is how they work, how to tell if you won, and why not every hall sells them.',
            body), (_crumbs(('How to play bingo', 'how-to-play-bingo/'), ('Pull tabs', 'pull-tabs/')), faq_ld)


AGE_CHECKED = '2026-11-27'
AGE_FAQ = (
    ('How old do you have to be to play bingo?',
     'It depends on the state. In most states with games on Find Bingo, you must be 18 to play charity bingo on your own, and Missouri allows players from 16. '
     'Iowa sets no state minimum and leaves it to each hall. Utah allows no paid bingo at all, so its law sets no age. '
     'Find your state on this page for its rule and its source.'),
    ('Can children play bingo with a parent?',
     'In some states, yes, when a parent, guardian or adult relative is with them. Other states allow no one under 18 to play at all. Each state’s entry on this page says which.'),
    ('Can a bingo hall set a higher age than the law?',
     'Yes, in many places. Texas and Mississippi law, for example, let a hall post a notice keeping everyone under 18 out. Call ahead before you bring a child.'),
    ('Is the age different for pull tabs?',
     'Often, yes. Virginia lets younger players play bingo with a parent or legal guardian, but allows instant bingo, pull tabs and seal cards only for players 18 and older.'),
)


def age_page(states):
    """Bingo age by state: only states with listings on Find Bingo whose age was read from the state's own law, rule or regulator."""
    rows = [s for s in states if s.get('age')]
    for s in rows:
        a = s['age']
        assert s['coverage'] in LISTED and a['min'] in (16, 18, None) and a['rule'].startswith(f'{a["min"]} and older' if a['min'] else 'No '), s['code']
        assert a['sources'] and all(x['url'].startswith('https://') and x['label'] and x['scope'] and x['reviewed_on'] == AGE_CHECKED for x in a['sources']), s['code']
    youngest = min(s['age']['min'] for s in rows if s['age']['min'])
    assert [s['code'] for s in rows if s['age']['min'] == youngest] == ['MO'], 'the lead and questions name Missouri as the one state starting at 16'
    assert [s['code'] for s in rows if s['age']['min'] is None] == ['IA', 'UT'], 'the lead and questions name Iowa and Utah as the states whose law sets no age'
    by = {s['code']: s for s in rows}
    assert all(c in by for c in ('TX', 'MS', 'VA')), 'the questions name Texas, Mississippi and Virginia'
    missing = [s for s in states if s['coverage'] in LISTED and not s.get('age')]
    faq_html, faq_ld = _questions(AGE_FAQ)
    table = ('<table class="ages"><caption>Minimum age to play charity bingo, by state, checked November 27, 2026</caption>'
             '<thead><tr><th scope="col">State</th><th scope="col">Who may play</th></tr></thead><tbody>'
             + ''.join(f'<tr><th scope="row" id="{SLUGS[s["code"]]}"><a href="../{SLUGS[s["code"]]}/">{escape(s["name"])}</a></th>'
                       f'<td>{escape(s["age"]["rule"])}<span class="src">Source: '
                       + ' and '.join(_ext(x['url'], x['label']) for x in s['age']['sources']) + '</span></td></tr>' for s in rows)
             + '</tbody></table>')
    names = [s['name'] for s in missing]
    unconfirmed = ('<h2 id="unconfirmed">States we have not confirmed yet</h2>'
                   f'<p>We also list games in {_and(names)}, but have not yet confirmed a minimum age from {"each state’s" if len(names) > 1 else "the state’s"} own law. '
                   'Ask the hall before you bring a child.</p>') if missing else ''
    body = ('<p class="note">Checked November 27, 2026, from each state’s own law, rules or bingo regulator. A hall may set a higher age, and some keep children out entirely. '
            'This is a plain summary, not legal advice: the linked source has the full wording.</p>'
            + table + unconfirmed
            + '<h2 id="before">Before you bring a younger player</h2>'
            '<ul><li>Call the hall and ask whether children may play, and at what age. House rules can be stricter than the law.</li>'
            '<li>Bring a photo ID for yourself. Some halls check.</li>'
            '<li>Expect pull tabs and other instant games to be for adults only in many states. See <a href="../pull-tabs/">pull tabs explained</a>.</li></ul>'
            + faq_html + _more('bingo-age-by-state'))
    return ('Bingo Age by State: How Old to Play Charity Bingo | FindBingo.org',
            'How old do you have to be to play bingo? The minimum age for charity bingo in each state with games on Find Bingo, from each state’s own law.',
            'How old do you have to be to play bingo?',
            'Bringing a grandchild, or turning 18 soon? In most states with games on Find Bingo, charity bingo is for players 18 and older. '
            'Missouri starts at 16, Iowa leaves it to each hall, and several states let younger players play beside a parent or guardian.',
            body), (_crumbs(('How to play bingo', 'how-to-play-bingo/'), ('Bingo age by state', 'bingo-age-by-state/')), faq_ld)


def moved_page(new_slug, label, style, analytics, generated_on):
    """A forwarding page left at an old address (findbingo.org also answers it with a 301 in _redirects)."""
    url = f'{SITE}/{new_slug}/'
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{escape(label)} has moved | FindBingo.org</title>\n<link rel="canonical" href="{url}">\n<meta name="robots" content="noindex,follow">\n'
            f'<meta http-equiv="refresh" content="0; url=../{new_slug}/">\n' + style + '\n</head>'
            f'<body id="top"><a class="skip" href="#main">Skip to the page</a><header>{BALLS}<p class="brand"><a href="../">FindBingo.org</a> · free from Veteran Home Guardians</p>'
            f'<h1>{escape(label)} has a new address</h1></header>'
            f'<main id="main"><div class="info"><p><a href="../{new_slug}/">Go to {escape(label.lower())}</a>.</p></div></main>'
            f'{_footer(generated_on)}<script>{analytics}</script></body></html>\n')


def newbie_line(s, up='../', icon=True):
    """A state page's one line for first-timers: how a night works, the words, and the state's age when it is confirmed.
    icon=False for pages without the icon sprite (the Ohio finder)."""
    words = 'How old you must be in' if (s.get('age') or {}).get('min') else 'Bingo age rules in'  # Iowa and Utah set no age
    age = (f' · <a href="{up}bingo-age-by-state/#{SLUGS[s["code"]]}">{words} {escape(s["name"])}</a>' if s.get('age') else '')
    return (f'<p class="newbie">{_ic("book") if icon else ""}<span>New to hall bingo? <a href="{up}how-to-play-bingo/">How a bingo night works</a> · '
            f'<a href="{up}bingo-terms/">Bingo words, A to Z</a>{age}</span></p>')


ASK = _mailto('Find Bingo privacy')
PRIVACY = (
    'Privacy: No Accounts, No Sign-In | FindBingo.org',
    'How FindBingo.org handles information about your visit: no accounts, no cookies for counting visits, and your ZIP code search stays on your device.',
    'Privacy',
    f'Wondering what we keep about you? Very little: there is no account or sign-in, visits are counted without cookies, and your ZIP code search is worked out on your own device. Last updated {POLICY_DATE}.',
    '<h2>The short version</h2>'
    '<ul><li>There are no accounts and no sign-in. We never ask for your name.</li>'
    '<li>We count visits without cookies and without keeping personal information.</li>'
    '<li>Your ZIP code search is worked out on your own phone or computer.</li>'
    '<li>The map pictures come from OpenStreetMap, which sees your internet address and the area on the map.</li>'
    '<li>Google AdSense may show ads here and set cookies.</li>'
    '<li>We do not sell personal information.</li></ul>'
    '<h2>Counting visits</h2>'
    '<p>We use ' + _ext('https://www.goatcounter.com/help/privacy', 'GoatCounter') + ' to count page views, so we know which pages people use. '
    'GoatCounter does not use cookies and does not store personal information. For each page view it records things like the page visited, '
    'the site that sent you here, your browser, your screen size, and an approximate country worked out from your internet (IP) address. '
    'It does not store the IP address.</p>'
    '<p>We leave out everything after the question mark in a page address, so the ZIP code you search for is never counted. The one exception is the name of an ad or campaign that sent you here (its utm tags).</p>'
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
    '<p>Find Bingo uses Google AdSense, so Google may show ads on this site and set cookies. We ask Google for non-personalized ads, '
    'which are chosen from the page you are on and your general location, not from your visits to other sites. Google’s ad code can still '
    'set its own cookies, for example to limit how often you see the same ad and to stop fraud.</p>'
    '<p>You can manage Google’s ad settings at ' + _ext('https://adssettings.google.com', 'adssettings.google.com')
    + ', read how Google uses information from sites that show its ads at ' + _ext('https://policies.google.com/technologies/ads', 'policies.google.com/technologies/ads')
    + ', or opt out of many ad networks at ' + _ext('https://optout.aboutads.info', 'optout.aboutads.info') + '.</p>'
    '<p>Ads are kept apart from the game listings, and they never change which games are listed or their order. '
    '<a href="../advertise/">About advertising on Find Bingo</a></p>'
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
ABOUT_PAGE = (
    'About Find Bingo: Who Runs It and How to Reach Us | FindBingo.org',
    'Who runs FindBingo.org: Veteran Home Guardians, an Ohio nonprofit, with a Marine veteran who ran his Legion’s bingo. Where listings come from and how to reach us.',
    'About Find Bingo',
    'Wondering who is behind this site? Find Bingo is a free finder from Veteran Home Guardians, an Ohio nonprofit, made by a Marine Corps veteran who ran and advertised bingo at his American Legion for three years.',
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
    '__OPEN_DATA__'
    '<h2 id="contact">Contact us</h2>'
    f'<p>Email <a href="{escape(CONTACT)}">{EMAIL}</a> for questions, corrections, advertising or partnerships. We read every message.</p>'
    '<p><a href="../privacy/">Privacy</a> · <a href="../terms/">Terms of use</a> · <a href="../advertise/">Advertise on Find Bingo</a></p>')

# Open data and other bingo finders (owner direction, November 24, 2026): the listings are open data under the
# repository's LICENSE, and the official lists and other finders are named, so nobody has to collect the same
# games twice. Ohio's and Missouri's links come from bingo-states.json; the Texas open dataset is not in it.
DATA_ATTRIBUTION = 'Veteran Resident Resource Guide, created by Travis Vought and shared by Veteran Home Guardians.'
REPO_URL = 'https://github.com/travisvought-byte/vhg-veteran-resident-guide'
TEXAS_OPEN_DATA = ('https://catalog.data.gov/dataset/bingo-conductor-locations', 'Texas bingo conductor locations')


def _open_data(states):
    by = {s['code']: s for s in states}
    finders = ((by['OH']['regulator_url'], by['OH']['regulator_label'], 'the official list of licensed bingo locations in Ohio.'),
               (by['MO']['list_url'], by['MO']['list_label'], 'the state’s own search of licensed games, with days and start times.'),
               (*TEXAS_OPEN_DATA, 'every licensed Texas bingo conductor by playing location, as open data.'))
    items = ''.join(f'<li>{_out(url, label)}: {escape(note)}</li>' for url, label, note in finders)
    return ('<h2 id="open-data">Open data and other bingo finders</h2>'
            '<p>Find Bingo’s listings are open data under the '
            + _out('https://creativecommons.org/licenses/by/4.0/', 'Creative Commons Attribution 4.0 license (CC BY 4.0)')
            + f'. Anyone may copy and reuse them, in their own finder too, with this credit: “{escape(DATA_ATTRIBUTION)}” '
            'Reuse them with that credit so nobody has to collect the same games twice.</p>'
            '<p><a href="../data.json" download>Download the listings (data.json)</a>, or get every list and the code that builds this site from '
            + _out(REPO_URL, 'the Find Bingo data on GitHub') + '.</p>'
            '<h3>Official sources and other finders</h3>'
            f'<ul>{items}</ul>'
            f'<p>Run a bingo finder or keep a list of games? Write to us at <a href="{escape(_mailto("Linking bingo finders"))}">{EMAIL}</a> '
            'and we’ll link to each other.</p>')


def about_page(states):
    """findbingo.org/about/: who runs the site, where listings come from, open data and other finders."""
    *head, body = ABOUT_PAGE
    assert body.count('__OPEN_DATA__') == 1
    return (*head, body.replace('__OPEN_DATA__', _open_data(states)))


TERMS = (
    'Terms of Use: A Free Bingo Directory | FindBingo.org',
    'The terms for using FindBingo.org: a free bingo directory with no wagering on the site, listings to check with the hall, and labeled ads.',
    'Terms of use',
    f'The short of it: Find Bingo is a free directory. It runs no games and takes no bets, so check game details with the hall before you go. Last updated {TERMS_DATE}.',
    '<h2>What this site is</h2>'
    '<p>FindBingo.org is a free directory of bingo games, run by Veteran Home Guardians. Using the site means you accept these terms.</p>'
    '<h2>No gambling on this site</h2>'
    '<p>Find Bingo does not run games, sell cards, take bets or pay prizes. The practice game is free, just for fun, and wins nothing. '
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
    # Written to the hall volunteer or manager trying to fill seats, then suppliers and local businesses (November 23, 2026).
    'Advertise on Find Bingo: Reach Local Bingo Players | FindBingo.org',
    'Fill seats on bingo night: feature a special game, get a game site for your hall, or place a labeled ad near players. Ads never change the free listings.',
    'Advertise on Find Bingo',
    'Trying to fill seats on bingo night, or reach the players and families who come? Feature your event, get a game site for your hall, or put a labeled ad in front of people searching for bingo near you.',
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
    '<ul><li>Every ad we sell is labeled “Advertisement.” Every featured event is labeled “Featured event.” Ads from Google AdSense carry Google’s own ad label.</li>'
    '<li>Ads we sell sit apart from the game listings: on the home page below the search results, and on state pages after the listings. Never inside them. '
    'Featured events sit in their own box above the results, never inside them.</li>'
    '<li>Ads never add, remove, change or reorder listings. A hall cannot pay for a better listing, and every listing stays free.</li>'
    '<li>We review every ad we sell before it runs, and we turn down ads that are misleading. Google reviews its ads under its own policies.</li></ul>'
    '<h2>Where the money goes</h2>'
    '<p>Ad income supports <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, the Ohio nonprofit that runs Find Bingo '
    'and visits veterans in nursing homes.</p>'
    '<h2>Get in touch</h2>'
    '<p>Tell us your business name, what you would like to advertise, and the states or towns you want to reach.</p>'
    '<div class="big-actions"><a class="solid" href="'
    + escape(_mailto('Advertising on Find Bingo', 'Business name:\nWhat we would like to advertise:\nStates or towns:\nWebsite:\nBest way to reach us:\n'))
    + f'">Email us about an ad</a></div><p class="small">Or write to {EMAIL}. '
    '<a href="../privacy/">How ads and privacy work on this site</a></p>')


# ---- Shop: bingo gear and gifts (DRAFT, owner direction, November 25, 2026) ------------------------------
# Travis wants a store area for bingo supplies, gifts and apparel that earns for Veteran Home Guardians.
# data/findbingo-shop.json holds the picks (chosen for high ratings from many buyers; see its _about). Each
# link goes to a store search for the item. No affiliate ID is set until Travis signs up for a program and
# fills in AFFILIATE_TAGS. Rules the page keeps:
# - It says plainly that links may earn a commission, at no extra cost (FTC disclosure).
# - It never ties a purchase to a donation (Amazon's operating agreement bars offering anything, a charity
#   gift included, for using its links). A tagged link is marked rel="sponsored"; until then links are plain.
# - It shows no prices or star ratings: both change, and Amazon's terms limit showing its ratings.
# - Bingo paper and cages for a licensed game must come from a licensed distributor in most states, so the
#   home and party picks say they are for home and fun games, and halls are pointed to their state's rules.
# - No brand is named as a partner or "featured" until it has agreed (Travis, November 25, 2026).
SHOP_FILE = 'data/findbingo-shop.json'
SHOP_STORES = {
    'Amazon': 'https://www.amazon.com/s?k=',
    'Walmart': 'https://www.walmart.com/search?q=',
    'Etsy': 'https://www.etsy.com/search?q=',
}
# Filled in only after Travis joins a program, for example {'Amazon': ('tag', 'findbingo-20')}. Empty: plain links.
AFFILIATE_TAGS = {}
SHOP_ICONS = {
    'dauber': '<path d="M9 3h6v4H9z"/><path d="M8 7h8l1 3v9a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-9z"/><circle cx="12" cy="15" r="2.5"/>',
    'bag': '<path d="M4 8h16l-1.5 12.5H5.5z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/><path d="M8.5 12v4M12 12v4M15.5 12v4"/>',
    'hand': '<path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V11M11 10.5V4a1.5 1.5 0 0 1 3 0v7M14 10.5V5.5a1.5 1.5 0 0 1 3 0V14a7 7 0 0 1-7 7h-.5A6 6 0 0 1 5 18.5l-2-3.5a1.5 1.5 0 0 1 2.6-1.5L8 16"/>',
    'cage': '<circle cx="12" cy="11" r="7"/><path d="M5 11h14M12 4v14M7 5.8l10 10.4M17 5.8 7 16.2"/><path d="M8 18l-2 3h12l-2-3"/>',
    'clover': '<circle cx="9" cy="9" r="3.2"/><circle cx="15" cy="9" r="3.2"/><circle cx="9" cy="15" r="3.2"/><circle cx="15" cy="15" r="3.2"/><path d="M15 15l5 6"/>',
    'shirt': '<path d="M8 3 3 6l2 5 2-1v11h10V10l2 1 2-5-5-3a3 3 0 0 1-8 0z"/>',
}
SHOP_CSS = ('.shop-note{background:#fff8e6;border:2px solid #d9b45a;border-radius:12px;padding:10px 16px;margin:12px 0}.shop-note p{margin:6px 0}'
            '.shop-jump{list-style:none;padding:0;margin:10px 0;display:flex;flex-wrap:wrap;gap:8px}'
            '.shop-jump a{display:inline-flex;align-items:center;gap:8px;min-height:48px;padding:0 14px;border:2px solid var(--accent);border-radius:24px;color:var(--accent);font-weight:700;text-decoration:none}'
            '.shop-group h2{display:flex;align-items:center;gap:12px;scroll-margin-top:12px}'
            '.shop-ic{flex:none;width:44px;height:44px;padding:7px;border-radius:50%;background:var(--accent);color:#fff;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}'
            '.shop-jump .shop-ic{width:30px;height:30px;padding:5px}'
            '.picks{list-style:none;padding:0;margin:8px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}'
            '.picks li{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column}'
            '.picks h3{font-size:20px;margin:2px 0 6px;color:var(--head)}.picks p{margin:0 0 10px;flex:1}'
            '.picks a{display:flex;align-items:center;justify-content:center;min-height:52px;padding:4px 12px;border-radius:10px;background:var(--green);color:#fff;font-size:18px;font-weight:700;text-decoration:none;text-align:center}'
            '.picks a:focus-visible,.shop-jump a:focus-visible{outline:3px solid #ffbf47;outline-offset:3px}'
            '@media (forced-colors:active){.shop-ic{forced-color-adjust:none;background:Canvas;color:CanvasText;border:2px solid CanvasText}.picks a{border:2px solid ButtonText}}'
            '@media print{.picks a{background:none;color:#000;border:1px solid #000}.shop-jump{display:none}}')


def load_shop(root):
    shop = json.loads((root / SHOP_FILE).read_text())
    validate_shop(shop)
    return shop


def validate_shop(shop):
    assert date.fromisoformat(shop['checked_on']).isoformat() == shop['checked_on'], 'checked_on is a date'
    ids = set()
    for g in shop['groups']:
        assert set(g) == {'id', 'icon', 'title', 'intro', 'items'}, g.get('id')
        assert g['icon'] in SHOP_ICONS and re.fullmatch(r'[a-z]+', g['id']) and g['id'] not in ids, g['id']
        ids.add(g['id'])
        assert g['items'], ('a shop group with no picks', g['id'])
        for it in g['items']:
            assert set(it) == {'name', 'why', 'store', 'search'}, it
            assert it['store'] in SHOP_STORES, ('unknown store', it['store'])
            assert all(it[k].strip() for k in it) and len(it['why']) <= 120, it['name']
            # No prices or ratings on the page: they change, and Amazon's terms limit showing its ratings.
            assert not re.search(r'\$\s?\d|\bstars?\b|\d[\d,]* (ratings|reviews)', it['name'] + ' ' + it['why'], re.I), it['name']


def _shop_url(item):
    url = SHOP_STORES[item['store']] + quote(item['search'])
    if item['store'] in AFFILIATE_TAGS:
        k, v = AFFILIATE_TAGS[item['store']]
        url += '&' + quote(k) + '=' + quote(v)
    return url


def _shop_icon(name):
    return f'<svg class="shop-ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{SHOP_ICONS[name]}</svg>'


def shop_page(shop):
    """findbingo.org/shop/: hand-picked bingo gear and gifts, each a plain link to the store."""
    jump = ''.join(f'<li><a href="#{g["id"]}">{_shop_icon(g["icon"])}{escape(g["title"])}</a></li>' for g in shop['groups'])
    groups = ''
    for g in shop['groups']:
        picks = ''.join(
            f'<li><h3>{escape(it["name"])}</h3><p>{escape(it["why"])}</p>'
            f'<a href="{escape(_shop_url(it))}" target="_blank" rel="{"sponsored noopener" if it["store"] in AFFILIATE_TAGS else "noopener"}">See it on {escape(it["store"])}'
            f'<span class="vh"> (opens a new tab)</span></a></li>' for it in g['items'])
        groups += (f'<section class="shop-group" aria-labelledby="{g["id"]}"><h2 id="{g["id"]}">{_shop_icon(g["icon"])}{escape(g["title"])}</h2>'
                   f'<p>{escape(g["intro"])}</p><ul class="picks" role="list">{picks}</ul>'
                   '<p class="small"><a href="#top">Back to the top</a></p></section>')
    body = (
        '<div class="shop-note"><p><strong>How this page works.</strong> We picked these because buyers rate them highly. '
        'Each button opens the store’s own page in a new tab, where you see today’s price and reviews. '
        'If you buy through a link here, Find Bingo may earn a small commission. It costs you nothing extra.</p></div>'
        f'<nav aria-label="Shop sections"><ul class="shop-jump" role="list">{jump}</ul></nav>'
        + groups +
        '<h2>Running a licensed game?</h2>'
        '<p>The home and party picks above are for family games and fun nights. In most states, bingo paper, cards and cages for a licensed charity game '
        'must come from a licensed distributor. <a href="../halls/">See your state’s rules on our page for halls</a>.</p>'
        '<h2>Sell bingo gear?</h2>'
        '<p>Bingo suppliers and makers can ask about a place on this page. Anything paid for is labeled, and it never changes the free game listings.</p>'
        '<div class="big-actions"><a class="solid" href="'
        + escape(_mailto('Bingo gear on Find Bingo', 'Business name:\nWhat you make or sell:\nWebsite:\nBest way to reach you:\n'))
        + '">Email us about your products</a></div>'
        f'<p class="small">Picks checked {_date_label(shop["checked_on"])}. Something you love that belongs here? <a href="'
        + escape(_mailto('A bingo gear idea for Find Bingo')) + '">Tell us</a>.</p>')
    return ('Bingo Supplies, Gifts and Sweatshirts Players Love | FindBingo.org',
            'Hand-picked bingo daubers, bags, large-print cards, home bingo sets, lucky charms and bingo sweatshirts, chosen because buyers rate them highly.',
            'Bingo gear and gifts',
            'Looking for a new dauber, a bag that holds it all, or a gift for the bingo lover in your life? These are the things players rate best.',
            body)


# ---- Google AdSense, on findbingo.org only (owner direction, November 27, 2026) ------------------------------
# HARD RULE: guide.vethomeguard.org runs Google Ad Grants, which forbids AdSense, so Google's ad code and ads.txt go
# only into bingo-site/findbingo/, which the Ohio-Bingo repository mirrors and Cloudflare serves at findbingo.org (and
# www.findbingo.org). findbingo-site/ is served on the guide's host (guide.vethomeguard.org/findbingo-site/, the
# finder's data source) and never carries either; _config.yml keeps bingo-site/ out of the guide's GitHub Pages build.
# tests/adsense_scope.py enforces both. Auto ads: the code sits in <head> and Google places the ads; non-personalized
# ads are asked for before the code loads, as on Mobility Talk. No visible ad slot is added here.
ADSENSE_CLIENT = 'ca-pub-9220804879239310'
ADSENSE_HEAD = (f'<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">'
                '<script>(window.adsbygoogle=window.adsbygoogle||[]).requestNonPersonalizedAds=1;</script>'
                f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>')
ADS_TXT = 'google.com, pub-9220804879239310, DIRECT, f08c47fec0942fa0\n'
ADSENSE_BASE = 'bingo-site/findbingo/'
# Pages that never load the ad code: page not found, the print-only poster, the privacy, terms and about pages, and the
# forwarding page left at the bingo class's old address.
# learn/ is only a forwarding page now: the bingo class moved to how-to-play-bingo/ (November 27, 2026).
NO_ADSENSE = ('404.html', 'ohio/poster.html', 'privacy/index.html', 'terms/index.html', 'about/index.html', 'learn/index.html')


def adsense(result):
    """ads.txt at the findbingo.org root and the AdSense code in the head of findbingo.org's pages (bingo-site/findbingo/)."""
    out = {ADSENSE_BASE + 'ads.txt': ADS_TXT}
    for name, text in result.items():
        rel = name[len(ADSENSE_BASE):]
        if (not name.startswith(ADSENSE_BASE) or not name.endswith('.html') or not isinstance(text, str) or rel in NO_ADSENSE
                or rel.startswith('google') or '</head>' not in text):
            continue
        assert ADSENSE_CLIENT not in text and text.count('</head>') == 1, name
        out[name] = text.replace('</head>', ADSENSE_HEAD + '</head>', 1)
    assert not any(n.startswith('findbingo-site/') for n in out)
    return out
