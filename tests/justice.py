#!/usr/bin/env python3
"""Veterans in the justice system (guide.vethomeguard.org/justice.html): every item names at least one official
https source and a "Report a problem" link; the page carries the 38 CFR 3.665 and 3.666 rules, the apportionment
form, VJO, HCRV, SSVF and HUD-VASH, an Ohio section, the visit counter and one checked date; it is in the sitemap;
every state page links to it; record clearing points to the cannabis site's Ohio walkthrough; and the Ohio section
points to Abuse of Office's Ohio rights page."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_justice  # noqa: E402

data = json.loads((ROOT / 'data/justice.json').read_text(encoding='utf-8'))
assert date.fromisoformat(data['checked_on']) <= date.today(), 'checked date'
items = [i for s in data['sections'] for i in s['items']] + data['ohio']['items']
ids = [i['id'] for i in items]
assert len(ids) == len(set(ids)), 'duplicate item id'
for item in items:
    assert item['sources'], (item['id'], 'source')
    for s in item['sources'] + item.get('links', []):
        url = s['url']
        assert url == './' or urlsplit(url).scheme == 'https', (item['id'], url)
    for text in item.get('text', []) + [item.get('ask', '')]:
        assert '<' not in text, (item['id'], 'plain text only')
    if item.get('phone'):
        digits = re.sub(r'\D', '', item['phone']['display'])
        assert item['phone']['tel'].endswith(digits), (item['id'], 'phone link matches the printed number')

# Other free guides an Ohio reader is pointed to (November 28, 2026): plain text around one https link.
for s in data['ohio'].get('see_also', []):
    assert urlsplit(s['url']).scheme == 'https' and '<' not in s['before'] + s['label'] + s['after'], s
page = (ROOT / 'justice.html').read_text(encoding='utf-8')
landing = json.loads((ROOT / 'data/landing/pages.json').read_text(encoding='utf-8'))['pages']['justice.html']
assert f'<title>{build_justice.e(landing["title"])}</title>' in page, 'justice.html is out of date: run python3 scripts/build_public.py'
chooser = json.loads((ROOT / 'data/landing/chooser.json').read_text(encoding='utf-8'))
assert any(o.get('href') == 'justice.html' for o in chooser['options']), 'the home chooser offers the justice page'
for needed in ['section-3.665', 'section-3.666', 'about-form-21-0788', 'veterans-justice-outreach/vjo-contacts',
               'hcrv/hcrv-contacts-2', 'section-62.11', '2024-17957', 'section-341.43', 'SpecializedDocketsList',
               'https://the-reefer.com/expungement.html', 'https://abuseofoffice.org/rights.html', 'assets/analytics.js', 'id="ohio"', '<link rel="canonical" href="https://guide.vethomeguard.org/justice.html">']:
    assert needed in page, needed
assert page.count('Report a problem') >= len(items), 'every listing has Report a problem'
assert '<meta name="description" content="' in page and '<title>' in page
assert 'https://guide.vethomeguard.org/justice.html' in (ROOT / 'sitemap.xml').read_text(encoding='utf-8'), 'sitemap'

registry = json.loads((ROOT / 'states/registry.json').read_text(encoding='utf-8'))
for state in registry:
    text = (ROOT / state['page']).read_text(encoding='utf-8')
    assert 'href="justice.html"' in text and 'data-justice-route' in text, (state['page'], 'justice link')
print(f'ok: justice page, {len(items)} sourced items, linked from {len(registry)} state pages')
