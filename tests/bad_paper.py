"""Bad paper section (bad-paper/): every page is current, findable and sourced, and the guide links to it.

Run: python3 tests/bad_paper.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_bad_paper import PAGES, SOURCES, outputs, pages  # noqa: E402
from a11y_finish import finish_named  # noqa: E402

# build_public.py finishes every page last (skip link, link symbols); compare with that.
built = {name: finish_named(name, text) for name, text in outputs().items()}
titles, descs = set(), set()
for p in PAGES:
    path = 'bad-paper/' + p['slug'] + '.html'
    html = (ROOT / path).read_text(encoding='utf-8')
    assert html == built[path], path + ' is out of date: run python3 scripts/build_public.py'
    title = re.search(r'<title>(.*?)</title>', html).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
    assert title not in titles and desc not in descs, path + ' needs its own title and description'
    titles.add(title); descs.add(desc)
    assert 50 <= len(desc) <= 230, path + ' description length ' + str(len(desc))
    canonical = 'https://guide.vethomeguard.org/bad-paper/' + ('' if p['slug'] == 'index' else p['slug'] + '.html')
    assert f'<link rel="canonical" href="{canonical}">' in html, path + ' canonical'
    assert html.count('<h1>') == 1, path + ' has one heading'
    assert '../assets/analytics.js' in html, path + ' counts visits'
    assert 'Report a problem with this page' in html and 'mailto:travis@vethomeguard.org' in html, path + ' report path'
    assert 'class="crisis-aside"' in html and 'tel:988' in html, path + ' small crisis line'
    assert 'id="sources-title"' in html, path + ' lists sources'
    for key in p['sources']:
        assert SOURCES[key][1].replace('&', '&amp;') in html, path + ' cites ' + key
    assert not re.search(r'unverified|needs verification', html, re.I), path + ' shows no unverified warnings'
    # Every internal link resolves to a built page, an anchor on it, or a file in the repository.
    for href in re.findall(r'href="([^"]+)"', html):
        if re.match(r'(https?:|mailto:|tel:|sms:)', href):
            continue
        target, _, anchor = href.partition('#')
        if not target:
            file = path
        else:
            target = target.split('?')[0]
            resolved = (ROOT / 'bad-paper' / target).resolve()
            if resolved.is_dir():
                resolved = resolved / 'index.html'
            file = str(resolved.relative_to(ROOT))
            assert resolved.is_file(), path + ' links to missing ' + href
        if anchor and file.startswith('bad-paper/'):
            assert f'id="{anchor}"' in (ROOT / file).read_text(encoding='utf-8'), path + ' links to missing anchor ' + href

# Every registered state appears in the agency table and the start page's state box.
states = json.loads((ROOT / 'states/registry.json').read_text())
help_page = (ROOT / 'bad-paper/free-help.html').read_text()
start = (ROOT / 'bad-paper/index.html').read_text()
for s in states:
    assert f'id="state-{s["code"].lower()}"' in help_page, s['code'] + ' agency row'
    assert f'<option value="{s["code"]}"' in start, s['code'] + ' in the state box'
assert 'Ohio Department of Veterans Services' in start, 'Ohio first'

# Findable: sitemap, home page and every state page, and listings that mention discharge upgrades.
sitemap = (ROOT / 'sitemap.xml').read_text()
for page in pages():
    assert 'https://guide.vethomeguard.org/' + page in sitemap, page + ' in sitemap'
for s in states:
    html = (ROOT / s['page']).read_text()
    assert 'data-bad-paper href="bad-paper/"' in html, s['page'] + ' has the bad-paper card'
guide = (ROOT / 'assets/guide.js').read_text()
assert "a.href='bad-paper/?state='+state" in guide, 'the card opens on the visitor\'s state'
assert 'Bad paper guide: VA options' in guide, 'discharge-upgrade listings link to the section'

# Printable checklist in the flyer system.
flyers = json.loads((ROOT / 'data/flyers.json').read_text())['flyers']
assert any(f['id'] == 'bad-paper-checklist-letter' and f['guide'] == 'bad-paper/' for f in flyers), 'checklist flyer listed'
assert (ROOT / 'flyers/bad-paper-checklist-letter.pdf').is_file()
print('PASS bad paper: ' + str(len(PAGES)) + ' pages current, sourced and linked from the guide, the state pages and the sitemap.')
