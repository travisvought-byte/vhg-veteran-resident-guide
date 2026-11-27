#!/usr/bin/env python3
"""Veteran programs pages (guide.vethomeguard.org/opportunities/, scripts/build_opportunities.py, docs/OPPORTUNITIES.md).

The data: every listing has the fields the pages need, an https source and a checked date. Capacity, applicants,
places, waitlists and odds appear only with the program's own figure and its source; computed odds use the program's
published numbers. Search excerpts (evidence C), ad leads (E) and closed programs never get a page.
The pages: one per published listing, each with its source and checked date; the state pages, the nationwide page and
the hub are in the sitemap; every state guide links to its state's page or the nationwide one; every Ohio county
office page lists its local programs; Ohio's regions cover its 88 counties once; and no ad code.
Business funding (listings with an award): equity is true, false or null (not stated); the business funding page
lists every published one, open ones first, in a captioned table and as cards, and the hub, the nationwide page and
every state page link to it."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_opportunities as bo  # noqa: E402

FIELDS = ['id', 'name', 'organization', 'category', 'summary', 'eligibility', 'how_to_apply', 'apply_url', 'scope',
          'state', 'counties', 'capacity', 'odds', 'source_url', 'source_title', 'checked_on', 'evidence', 'status']
CATS = {k for k, _, _, _ in bo.CATS}
registry = {s['code']: s for s in json.loads((ROOT / 'states/registry.json').read_text())}
sitemap = (ROOT / 'sitemap.xml').read_text()

ids, published = set(), []
for path in sorted(bo.DATA.glob('*.json')):
    data = json.loads(path.read_text())
    national = path.stem == 'national'
    assert national or data['state'] in registry, path
    for r in data['listings']:
        for f in FIELDS:
            assert f in r, (r.get('id'), f)
        assert r['id'] not in ids, ('duplicate id', r['id'])
        ids.add(r['id'])
        prefix = 'us' if national else data['state'].lower()
        assert r['id'].startswith(prefix + '-'), r['id']
        assert r['category'] in CATS, (r['id'], r['category'])
        assert r['scope'] in (('national', 'travel') if national else ('state', 'county', 'region')), (r['id'], r['scope'])
        assert r['evidence'] in 'ABCDE' and r['status'] in ('open', 'closed', 'paused', 'rolling'), r['id']
        assert date.fromisoformat(r['checked_on']) <= date.today(), r['id']
        for url in (r['source_url'], r['apply_url']):
            assert url is None or urlsplit(url).scheme == 'https', (r['id'], url)
        assert r['source_url'] and r['source_title'], r['id']
        if r.get('deadline_date'):
            date.fromisoformat(r['deadline_date'])
        if r['scope'] in ('county', 'region'):
            assert r['counties'] or r.get('regions'), (r['id'], 'a local program names its counties or region')
            known = {x['county'] for x in json.loads((ROOT / registry[data['state']]['offices']).read_text())}
            assert set(r['counties']) <= known, (r['id'], set(r['counties']) - known)
        if 'award' in r or 'equity' in r:
            assert r['category'] == 'business' and 'award' in r and 'equity' in r, (r['id'], 'funding needs award and equity')
            assert isinstance(r['award'], str) and r['award'].strip(), r['id']
            assert r['equity'] in (True, False, None), (r['id'], 'equity is true, false or null when not stated')
        assert r.get('invite_only', True) is True, (r['id'], 'invite_only is true or left out')
        for text in [r.get('award'), r.get('unconfirmed')]:
            assert text is None or ('<' not in text and text.strip()), (r['id'], 'plain text')
        for text in (r['name'], r['summary'], r['eligibility'], r['how_to_apply']):
            assert '<' not in text and text.strip(), (r['id'], 'plain text')
        c = r['capacity']
        figures = [c.get(k) for k in ('served', 'applicants', 'slots', 'waitlist')]
        if any(figures):
            assert c.get('figure_source', '').startswith('https://') and c.get('figure_date'), (r['id'], 'a figure needs its source and date')
        if r['odds']:
            assert r['odds']['basis'] in ('published', 'computed') and r['odds']['text'], r['id']
            assert any(figures), (r['id'], 'odds need the published figures behind them')
            if r['odds']['basis'] == 'computed':
                nums = {n.replace(',', '') for n in re.findall(r'\d[\d,]*', ' '.join(str(f) for f in figures if f))}
                used = {n.replace(',', '') for n in re.findall(r'\d[\d,]*\d|\d', r['odds']['text'].split(':')[0])}
                assert used & nums, (r['id'], 'computed odds start from the published numbers')
        folder = prefix
        page = ROOT / bo.FOLDER / folder / (bo.short_id(r) + '.html')
        if bo.published(r):
            published.append(r)
            html = page.read_text()
            assert r['source_url'].replace('&', '&amp;') in html and 'Checked ' in html, r['id']
            assert ('not published by the program' in html) != bool(any(figures) or r['odds']), (r['id'], 'capacity line')
            assert bo.BASE_URL + f'{bo.FOLDER}/{folder}/{bo.short_id(r)}.html' in sitemap, (r['id'], 'sitemap')
        else:
            assert not page.exists(), (r['id'], 'search excerpts, ad leads and closed programs get no page')
            assert r['id'] not in (ROOT / bo.FOLDER / folder / 'index.html').read_text() if (ROOT / bo.FOLDER / folder / 'index.html').exists() else True

assert len(published) > 200, len(published)
for rel in ['', 'us/', 'business/'] + [p.stem + '/' for p in bo.DATA.glob('*.json') if p.stem != 'national']:
    assert f'<loc>{bo.BASE_URL}{bo.FOLDER}/{rel}</loc>' in sitemap, rel

# Ohio's regions: every county once.
regions = bo.regions_of('OH')
ohio = {x['county'] for x in json.loads((ROOT / registry['OH']['offices']).read_text())}
assert set(regions) == ohio and len(ohio) == 88, set(regions) ^ ohio
assert sum(len(v.split()) for v in bo.REGIONS['OH'].values()) == 88

# Every state guide links to programs; every Ohio county office page lists them and links to Ohio's page with it chosen.
for code, s in registry.items():
    html = (ROOT / s['page']).read_text()
    assert html.count('id="opportunities-link"') == 1, s['page']
    want = f'{bo.FOLDER}/{code.lower()}/' if (bo.DATA / f'{code.lower()}.json').exists() else f'{bo.FOLDER}/us/'
    assert f'href="{want}"' in html, (s['page'], want)
for path in (ROOT / 'counties/oh').glob('*-county.html'):
    html = path.read_text()
    assert 'id="opps"' in html and f'{bo.FOLDER}/oh/?county=' in html, path.name

# The pages: the picker script, no ad code, every program page in reach of its state page.
for path in (ROOT / bo.FOLDER).rglob('*.html'):
    html = path.read_text()
    assert 'adsbygoogle' not in html and 'googlesyndication' not in html, path
    assert '<h1>' in html and 'Need help now?' in html, path
oh = (ROOT / bo.FOLDER / 'oh/index.html').read_text()
assert 'assets/opportunities.js' in oh and 'id="opp-county"' in oh and oh.count('<option value=') > 88
for r in published:
    if r['state'] == 'OH' or r['scope'] in ('national', 'travel'):
        assert f'{bo.short_id(r)}.html' in oh, (r['id'], 'listed on the Ohio page')
# Business funding: every published grant or prize on one page, open ones first, award and equity side by side.
fund = [r for r in published if bo.funding(r)]
biz = (ROOT / bo.FOLDER / 'business/index.html').read_text()
assert len(fund) >= 12, len(fund)
assert '<caption' in biz and biz.count('<th scope="col">') == 4 and 'tabindex="0"' in biz
table = biz.split('<tbody>')[1].split('</tbody>')[0]
order = [g for g, _, _ in bo.FUNDING_GROUPS]
seen = [r for r in sorted(fund, key=lambda r: table.index(f'href="#{bo.short_id(r)}"'))]
assert [order.index(bo.funding_group(r)) for r in seen] == sorted(order.index(bo.funding_group(r)) for r in seen), 'open ones first'
dated = [r['deadline_date'] for r in seen if bo.funding_group(r) == 'open' and r.get('deadline_date')]
assert dated == sorted(dated), 'nearest deadline first'
for r in fund:
    assert f'id="{bo.short_id(r)}"' in biz and f'href="#{bo.short_id(r)}"' in biz, (r['id'], 'on the business page')
    want = {True: 'Yes', False: 'No. The program says it takes no equity.', None: 'Not stated by the program'}[r['equity']]
    assert want in biz, (r['id'], 'equity line')
    if r.get('invite_only'):
        assert 'By invitation only.' in biz.split(f'id="{bo.short_id(r)}"')[1].split('</article>')[0], r['id']
assert 'href="business/"' in (ROOT / bo.FOLDER / 'index.html').read_text()
assert 'href="../business/"' in (ROOT / bo.FOLDER / 'us/index.html').read_text()
for path in bo.DATA.glob('*.json'):
    if path.stem != 'national':
        assert 'href="../business/"' in (ROOT / bo.FOLDER / path.stem / 'index.html').read_text(), path.stem
print('opportunities:', len(published), 'published listings,', len(fund), 'business funding: ok')
