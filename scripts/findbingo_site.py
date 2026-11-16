"""Build FindBingo.org (findbingo-site/): bingo near you in Michigan, Indiana and neighboring states.

index.html is the whole page (markup, styles and script). The same file is uploaded to the Wix site
that serves www.findbingo.org. It loads data.json and zips.json from this folder on the guide's
GitHub Pages site, so merged list updates reach findbingo.org without a new upload. Ohio keeps its
own finder (bingo.vethomeguard.org); this page links to it rather than copying Ohio data.
"""
import json
import re
from datetime import date
from html import escape

ORDER = ['MI', 'IN', 'OH', 'KY', 'WV', 'PA', 'FL']
# First three ZIP digits for each covered state (USPS prefix ranges).
PREFIXES = {'PA': (150, 196), 'WV': (247, 268), 'FL': (320, 349), 'KY': (400, 427), 'OH': (430, 459), 'IN': (460, 479), 'MI': (480, 499)}
COVERAGE = {'times', 'licenses', 'ohio_finder', 'none'}
TIME = re.compile(r'(?:[01]\d|2[0-3]):[0-5]\d')
REPO_RAW = 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/'
# Where the page looks for data.json and zips.json, in order. The branch entry serves the Wix copy
# until this folder reaches main; it can be dropped after that merge.
DATA_SOURCES = ['', 'https://guide.vethomeguard.org/findbingo-site/', REPO_RAW + 'main/findbingo-site/',
                REPO_RAW + 'claude/findbingo-national/findbingo-site/']


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
        if s['coverage'] == 'times':
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
    ids = set()
    for v in venues:
        assert v['id'] not in ids and re.fullmatch(r'mi-[a-z0-9-]+', v['id']), v['id']
        ids.add(v['id'])
        assert v['state'] == 'MI' and _state_of_zip(v['zip']) == 'MI' and v['zip'] in zips, v['id']
        assert v['address'].endswith(', MI ' + v['zip']) and v['city'] in v['address'], v['id']
        assert v['name'] and v['county'] and v['organizations'] and v['sessions'], v['id']
        for x in v['sessions']:
            assert type(x['day']) is int and 0 <= x['day'] <= 6, v['id']
            assert TIME.fullmatch(x['start']) and TIME.fullmatch(x['end']), v['id']
            assert x['organization'] in v['organizations'], v['id']
        assert all(type(n) is str and n for n in v.get('notes', [])), v['id']
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
        'venues': [_public_record(v, ('id', 'state', 'name', 'organizations', 'address', 'city', 'zip', 'county', 'sessions', 'notes', 'reviewed_on')) for v in venues],
        'licensed': [_public_record(r, ('id', 'state', 'name', 'address', 'city', 'zip', 'county', 'license_number', 'license_type', 'license_expires', 'reviewed_on')) for r in licensed],
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    buttons = ''.join(f'<a href="?state={s["code"]}" data-state="{s["code"]}">{escape(s["name"])}</a>' for s in states)
    about = ''
    for s in states:
        pairs = []
        for url, label in ((s.get('list_url'), s.get('list_label')), (s.get('finder_url'), 'Ohio Bingo Finder'), (s['regulator_url'], s['regulator_label'])):
            if url and url not in [u for u, _ in pairs]:
                pairs.append((url, label))
        links = ' · '.join(f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a>' for u, l in pairs)
        as_of = f' (list dated {_date_label(s["list_as_of"])})' if s.get('list_as_of') else ''
        about += (f'<h3>{escape(s["name"])}</h3><p>{escape(s["about"])} {escape(s["regulator_note"])}</p>'
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

- `index.html` is the whole page. Upload it as the home page of the Wix site that serves
  https://www.findbingo.org/ (see docs/FINDBINGO.md). Upload it again only when the page itself changes.
- `data.json` (the lists) and `zips.json` (ZIP code points for the covered states) are loaded by the
  page from https://guide.vethomeguard.org/findbingo-site/, so list updates reach findbingo.org as soon
  as a pull request merges.
- Ohio games stay on the Ohio Bingo Finder at https://bingo.vethomeguard.org/.

Lists updated {_date_label(generated_on)}.
'''
    return {
        'findbingo-site/index.html': page,
        'findbingo-site/data.json': data_json + '\n',
        'findbingo-site/zips.json': json.dumps(zips, separators=(',', ':')) + '\n',
        'findbingo-site/README.md': readme,
    }
