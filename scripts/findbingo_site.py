"""Build FindBingo.org (findbingo-site/): bingo near you in Michigan, Indiana and neighboring states.

index.html is the whole page (markup, styles and script). The same file is uploaded to the Wix site
that serves www.findbingo.org. It loads data.json and zips.json from this folder on the guide's
GitHub Pages site, so merged list updates reach findbingo.org without a new upload. Ohio keeps its
own finder page at findbingo.org/ohio/, generated from the same page as bingo.vethomeguard.org (which is unchanged).
"""
import json
import re
from datetime import date
from html import escape

from bingo_edition import make_bingo
from bingo_site import SITE as OHIO_SITE, standalone_finder

ORDER = ['MI', 'IN', 'OH', 'KY', 'WV', 'PA', 'FL']
# First three ZIP digits for each covered state (USPS prefix ranges).
PREFIXES = {'PA': (150, 196), 'WV': (247, 268), 'FL': (320, 349), 'KY': (400, 427), 'OH': (430, 459), 'IN': (460, 479), 'MI': (480, 499)}
COVERAGE = {'times', 'licenses', 'starter', 'ohio_finder', 'none'}
PHONE = re.compile(r'\d{3}-\d{3}-\d{4}')
TIME = re.compile(r'(?:[01]\d|2[0-3]):[0-5]\d')
REPO_RAW = 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/'
# Where the page looks for data.json and zips.json, in order: beside the page (the guide's copy),
# then GitHub Pages, then the raw file on main.
DATA_SOURCES = ['', 'https://guide.vethomeguard.org/findbingo-site/', REPO_RAW + 'main/findbingo-site/']


OHIO_OWN_URL = 'https://www.findbingo.org/ohio/'


def ohio_copy(finder_page):
    """The Ohio finder at findbingo.org/ohio/: the same page as bingo.vethomeguard.org, with its shared
    files loaded from there and FindBingo's own address for canonical and sharing tags."""
    page = _replace(finder_page, f'<link rel="canonical" href="{OHIO_SITE}/">', f'<link rel="canonical" href="{OHIO_OWN_URL}">', 1)
    page = _replace(page, f'<meta property="og:url" content="{OHIO_SITE}/">', f'<meta property="og:url" content="{OHIO_OWN_URL}">', 1)
    # Relative files (logo, analytics, partner and instant pages) stay on the Ohio site, so /ohio/ needs no copies.
    page = re.sub(r'"assets/', f'"{OHIO_SITE}/assets/', page)
    for name in ('partners.html', 'instant.html', 'poster.html', 'distributions.html'):
        page = page.replace(f'href="{name}"', f'href="{OHIO_SITE}/{name}"')
    page = _replace(page, '</footer>', '<p><a href="https://www.findbingo.org/">Bingo in other states: FindBingo.org</a></p></footer>', 1)
    return page


def _replace(page, old, new, count):
    assert page.count(old) == count, old
    return page.replace(old, new)


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
            assert v['kind'] in ('hall', 'senior_center') and PHONE.fullmatch(v['phone']), v['id']
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
    venues += json.loads((root / 'data/public/florida-bingo.json').read_text())
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

- `index.html` is the whole page. The same files are written to `bingo-site/findbingo/`, which the
  Ohio-Bingo repository mirrors and Cloudflare Pages serves at https://www.findbingo.org/ (see
  docs/FINDBINGO.md).
- `data.json` (the lists) and `zips.json` (ZIP code points for the covered states) are loaded by the
  page from https://guide.vethomeguard.org/findbingo-site/, so list updates reach findbingo.org as soon
  as a pull request merges.
- Ohio games are on the Ohio finder at https://www.findbingo.org/ohio/, generated from the same page as
  https://bingo.vethomeguard.org/ (which is unchanged). Its data comes from the same records.

Lists updated {_date_label(generated_on)}.
'''
    site = {
        'index.html': page,
        'data.json': data_json + '\n',
        'zips.json': json.dumps(zips, separators=(',', ':')) + '\n',
    }
    ohio = ohio_copy(standalone_finder(make_bingo(root)))
    # The same three files also go into bingo-site/findbingo/, which the Ohio-Bingo repository mirrors;
    # Cloudflare Pages serves www.findbingo.org from that folder.
    return {
        **{'findbingo-site/' + name: text for name, text in site.items()},
        **{'bingo-site/findbingo/' + name: text for name, text in site.items()},
        'findbingo-site/ohio/index.html': ohio,
        'bingo-site/findbingo/ohio/index.html': ohio,
        'findbingo-site/README.md': readme,
    }
