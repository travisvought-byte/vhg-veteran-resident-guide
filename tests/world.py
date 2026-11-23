#!/usr/bin/env python3
"""Country pages (guide.vethomeguard.org/world/): every country page has an emergency number and at least
one sourced line; a country with an agency shows its agency card, and a country marked as having no national
veterans agency shows that statement in its place, plus the crisis line and the U.S.-veteran help; every number names an official https source and the date it was checked; a line that is
not a 24-hour line says so on the page; the pages carry the visit counter, are in the sitemap and are linked
from the main navigation and the homepage."""
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_world  # noqa: E402

e = build_world.e

data = json.loads((ROOT / 'data/world/countries.json').read_text(encoding='utf-8'))
today = date.today()


def checked(item, where):
    assert urlsplit(item['source_url']).scheme == 'https', (where, 'https source')
    assert item.get('source_title'), (where, 'source title')
    assert date.fromisoformat(item['checked_on']) <= today, (where, 'checked date')
    if item.get('source_date'):
        parts = [int(p) for p in item['source_date'].split('-')]
        assert date(*(parts + [1] * (3 - len(parts)))) <= today, (where, 'source date')


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tels, self.links, self.sections, self.kinds, self.partials, self.sources = [], [], [], [], 0, []
        self.no_agency = 0
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            href = a['href']
            (self.tels if href.startswith('tel:') else self.links).append(href)
            if 'data-source' in a:
                self.sources.append(href)
        if tag == 'section' and a.get('id'):
            self.sections.append(a['id'])
        if a.get('data-kind'):
            self.kinds.append(a['data-kind'])
        if 'data-partial' in a:
            self.partials += 1
        if 'data-no-agency' in a and tag == 'div':
            self.no_agency += 1
        if tag == 'script' and a.get('src'):
            self.scripts.append(a['src'])


def parse(path):
    page = Page()
    page.feed((ROOT / path).read_text(encoding='utf-8'))
    return page


def local_links_resolve(path, page):
    for href in page.links:
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (ROOT / path).parent / url.path
        assert target.is_file() or target.is_dir(), (path, 'missing local link', href)


# 1. The data: every number has an official https source and a checked date; every country has the parts.
for key in ('fmp', 'vcl', 'benefits', 'manila'):
    checked(data['us_abroad'][key], key)
checked(data['us_abroad']['fmp']['us_canada'], 'FMP U.S. and Canada')
assert len(data['us_abroad']['vcl']['regions']) == 6
slugs = [c['slug'] for c in data['countries']]
assert len(slugs) == len(set(slugs)) and 1 <= len(slugs) <= 40, slugs
for c in data['countries']:
    em = c['emergency']
    assert em['numbers'] and all(n['display'] and n['tel'] for n in em['numbers']), (c['slug'], 'emergency number')
    checked(em, c['slug'] + ' emergency')
    kinds = [line['kind'] for line in c['lines']]
    na = c.get('no_agency')
    if na:
        # No national veterans agency: a plain statement in place of the agency card, sourced where it asserts.
        assert 'agency' not in kinds, (c['slug'], 'a no-agency country cannot also list an agency')
        assert na.get('statement'), (c['slug'], 'no-agency statement')
        assert na['statement'].startswith('We found no national veterans agency') or na.get('source_url'), \
            (c['slug'], 'a statement that asserts there is no agency needs an official source; otherwise say "We found no"')
        if na.get('source_url'):
            checked(na, c['slug'] + ' no-agency statement')
        else:
            assert date.fromisoformat(na['checked_on']) <= today, (c['slug'], 'no-agency checked date')
        assert 'crisis_line' in kinds or c.get('no_crisis_line'), (c['slug'], 'crisis line or a note that none was found')
        assert set(kinds) <= {'crisis_line'}, (c['slug'], 'a no-agency page lists crisis lines only', kinds)
    else:
        assert 'agency' in kinds and 'crisis_line' in kinds, (c['slug'], kinds)
        assert 'veterans_line' in kinds or c.get('no_veterans_line') or c.get('veterans_line_note'), (c['slug'], 'veterans line or a note')
    assert c['vcl_region'] in {r['code'] for r in data['us_abroad']['vcl']['regions']}, c['slug']
    for line in c['lines']:
        where = c['slug'] + ': ' + line['name']
        assert line['numbers'] and all(n['display'] and n['tel'] for n in line['numbers']), (where, 'numbers')
        checked(line, where)
        # A line that is not around the clock must say so plainly, unless it is the agency's
        # office line marked as such or a 24-hour line.
        if not line['around_the_clock']:
            assert line.get('partial'), (where, 'a line that is not 24 hours needs a plain partial-coverage note')
        assert line.get('hours'), (where, 'hours, or that the source gives none')
print(f'PASS: {len(slugs)} countries; every number has an official https source and a checked date.')

# 2. The built pages are current, and each country page shows an emergency number and a sourced line.
built = build_world.outputs()
for name, text in built.items():
    assert (ROOT / name).read_text(encoding='utf-8') == text, name + ' is out of date: run python3 scripts/build_public.py'
assert set(built) == {'world/index.html'} | {f'world/{s}.html' for s in slugs}
for c in data['countries']:
    path = f'world/{c["slug"]}.html'
    page = parse(path)
    html = (ROOT / path).read_text(encoding='utf-8')
    emergency = html[html.index('id="emergency"'):html.index('</section>', html.index('id="emergency"'))]
    assert re.search(r'href="tel:[^"]+"', emergency), (path, 'emergency number')
    assert 'Source: <a data-source href="https://' in emergency, (path, 'emergency source')
    na = c.get('no_agency')
    if na:
        assert page.kinds.count('agency') == 0 and page.no_agency == 1, (path, 'no-agency statement in place of the agency card')
        assert e(na['statement']) in html, (path, 'statement shown')
        if na.get('source_url'):
            block = html[html.index('id="no-agency"'):html.index('</section>', html.index('id="no-agency"'))]
            assert f'<a data-source href="{e(na["source_url"])}"' in block, (path, 'no-agency source shown')
        assert page.kinds.count('crisis_line') >= 1 or c.get('no_crisis_line'), (path, page.kinds)
    else:
        assert page.kinds.count('agency') >= 1 and page.kinds.count('crisis_line') >= 1, (path, 'agency card and crisis line', page.kinds)
        assert page.no_agency == 0 and 'id="no-agency"' not in html, (path, 'an agency country has no no-agency statement')
    assert len(page.kinds) == len(c['lines']), path
    for line in c['lines']:
        for n in line['numbers']:
            assert f'href="tel:{n["tel"]}"' in html, (path, n['display'])
        assert line['source_url'].replace('&', '&amp;') in html, (path, 'source shown', line['name'])
    expected_partials = (sum(bool(x.get('partial')) for x in c['lines']) + bool(c.get('no_veterans_line'))
                         + bool(na and c.get('no_crisis_line')))
    assert page.partials == expected_partials, (path, 'partial-coverage notes', page.partials, expected_partials)
    assert f'Checked {build_world.when(c.get("checked_on") or data["checked_on"])}' in html
    if c.get('checked_on'):
        assert date.fromisoformat(c['checked_on']) <= today, (path, 'country checked date')
    expected_sections = (['emergency', 'no-agency', 'crisis-line', 'us-veterans'] if na
                         else ['emergency', 'agency', 'veterans-line', 'crisis-line', 'us-veterans'])
    assert expected_sections == page.sections, (path, page.sections)
    # U.S. veterans living there: the Foreign Medical Program and the Veterans Crisis Line abroad.
    us = html[html.index('id="us-veterans"'):]
    assert 'Foreign Medical Program' in us and 'Veterans Crisis Line' in us and 'veteranscrisisline.net' in us, path
    region = next(r for r in data['us_abroad']['vcl']['regions'] if r['code'] == c['vcl_region'])
    assert region['display'] in us, (path, 'regional crisis number')
    assert 'VA benefits questions' in us and data['us_abroad']['benefits']['display'] in us, (path, 'VA benefits contact')
    fmp_line = next((t for t in data['us_abroad']['fmp']['toll_free'] if t['country'] == c['name']), None)
    if fmp_line:
        assert f'href="tel:{fmp_line["tel"]}"' in us, (path, 'FMP toll-free line for this country')
    assert f'<link rel="canonical" href="https://guide.vethomeguard.org/world/{c["slug"]}.html">' in html
    assert '../assets/analytics.js' in page.scripts, (path, 'visit counter')
    local_links_resolve(path, page)
print('PASS: every country page has an emergency number, sourced lines, partial-coverage notes and the U.S. veterans block;'
      f' {sum(bool(c.get("no_agency")) for c in data["countries"])} pages state that there is no national veterans agency.')

# 2b. The builder: a no-agency country with no crisis line found shows that note, and an agency country
# still renders its agency card (fixtures built from copies of the data, not written to disk).
import copy  # noqa: E402
fixture = copy.deepcopy(data)
sample = copy.deepcopy(next(c for c in data['countries'] if c.get('no_agency')))
sample.update(slug='fixture', name='Fixture', lines=[], no_crisis_line='We did not find a national crisis line on an official source.')
html = build_world.country_page(fixture, sample)
assert 'id="no-agency"' in html and 'data-kind="agency"' not in html and 'We did not find a national crisis line' in html
assert 'id="us-veterans"' in html and 'Foreign Medical Program' in html
agency_country = copy.deepcopy(next(c for c in data['countries'] if not c.get('no_agency')))
html = build_world.country_page(fixture, agency_country)
assert 'data-kind="agency"' in html and 'id="no-agency"' not in html
print('PASS: the builder renders the no-agency style and the agency style from fixtures.')

# 3. The world index lists every country and carries the VA numbers for U.S. veterans abroad.
index = (ROOT / 'world/index.html').read_text(encoding='utf-8')
page = parse('world/index.html')
for c in data['countries']:
    row = index[index.index(f'<tr><td><a href="{c["slug"]}.html">'):]
    row = row[:row.index('</tr>')]
    if c.get('no_agency'):
        assert 'No national veterans agency' in row, (c['slug'], 'index marks the no-agency country')
    else:
        agency = next(x['name'] for x in c['lines'] if x['kind'] == 'agency')
        assert e(agency) in row and 'data-no-agency' not in row, (c['slug'], 'index names the agency')
covered = {c['name'] for c in data['countries']}
assert not covered & {x['name'] for x in data['not_yet_covered']}, 'a covered country is still listed as not yet covered'
for r in data['us_abroad']['vcl']['regions']:
    assert r['display'] in index, r['code']
for t in data['us_abroad']['fmp']['toll_free']:
    assert t['display'] in index, t['country']
assert 'www.va.gov/health-care/foreign-medical-program' in index and 'veteranscrisisline.net' in index
assert '../assets/analytics.js' in page.scripts
local_links_resolve('world/index.html', page)
print('PASS: the world index lists every country and the VA numbers for U.S. veterans abroad.')

# 4. Linked from the main navigation and the homepage, and listed in the sitemap.
home = (ROOT / 'index.html').read_text(encoding='utf-8')
assert '<a class="jump" href="world/">Veterans outside the U.S.</a>' in home, 'main navigation'
assert 'id="world-link"' in home and 'href="world/"' in home[home.index('id="urgent-help"'):], 'homepage urgent-help link'
assert '<a class="jump" href="world/">' in (ROOT / 'ky.html').read_text(encoding='utf-8'), 'state pages share the navigation'
sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
for path in build_world.pages():
    assert f'<loc>https://guide.vethomeguard.org/{path}</loc>' in sitemap, path
analytics = (ROOT / 'assets/analytics.js').read_text(encoding='utf-8')
assert 'vhg-guide.goatcounter.com' in analytics
print('PASS: the world pages are in the main navigation, on the homepage, in the sitemap and counted by GoatCounter.')
