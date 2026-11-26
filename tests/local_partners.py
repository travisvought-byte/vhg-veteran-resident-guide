#!/usr/bin/env python3
"""Featured local partners on county pages: data/local-partners.json is well formed, every county it names exists
in that state's county office file, only "featured" partners render, and the partner block is accessible (one
heading, a hidden decorative symbol, link text that names the partner, no raw HTML from the data)."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_county_pages as county  # noqa: E402

data = json.loads((ROOT / 'data/local-partners.json').read_text(encoding='utf-8'))
states = {s['code'].upper(): s for s in json.loads((ROOT / 'states/registry.json').read_text())}
ids = set()
for p in data['partners']:
    for key in county.PARTNER_KEYS:
        assert p.get(key), (p.get('id'), 'missing ' + key)
    assert p['id'] not in ids, (p['id'], 'duplicate id')
    ids.add(p['id'])
    assert p['status'] in ('proposed', 'featured'), (p['id'], p['status'])
    assert urlsplit(p['website']).scheme == 'https', (p['id'], 'https website')
    assert date.fromisoformat(p['reviewed_on']) <= date.today(), (p['id'], 'reviewed_on')
    assert '<' not in p['blurb'] and len(p['blurb']) <= 320, (p['id'], 'blurb is short plain text')
    offices = json.loads((ROOT / states[p['state'].upper()]['offices']).read_text())
    known = {r['county'].strip().lower() for r in offices}
    for name in p['counties']:
        assert name.strip().lower() in known, (p['id'], name, 'not a county in the office file')

# Rendering, on a made-up partner so the test never depends on who is featured.
sample = {'id': 'sample', 'name': 'Sample Veterans Fund & Friends', 'state': 'OH', 'counties': ['Delaware'],
          'status': 'featured', 'blurb': 'Free rides <b>and</b> visits.', 'website': 'https://example.org/',
          'phone': '740-555-0100', 'reviewed_on': '2026-11-24'}
html = county.partner_section([sample], 'Delaware County')
assert html.count('<h2') == 1 and 'Featured local partner<' in html, 'one heading, singular'
assert 'aria-hidden="true" focusable="false"' in html, 'the symbol is decorative'
assert '>Visit Sample Veterans Fund &amp; Friends</a>' in html, 'link text names the partner'
assert '&lt;b&gt;' in html and '<b>' not in html, 'data is escaped'
assert 'href="tel:+17405550100"' in html, 'phone is a tel link'
two = county.partner_section([sample, dict(sample, id='s2', name='Second')], 'Delaware County')
assert 'Featured local partners<' in two and two.count('<article') == 2, 'plural heading for two'

# Only featured partners are loaded; proposed ones never reach a page.
tmp = ROOT / 'tests' / '.tmp-partners'
(tmp / 'data').mkdir(parents=True, exist_ok=True)
(tmp / 'data/local-partners.json').write_text(json.dumps({'partners': [sample, dict(sample, id='p', status='proposed')]}))
try:
    loaded = county.load_partners(tmp)
finally:
    (tmp / 'data/local-partners.json').unlink()
    (tmp / 'data').rmdir()
    tmp.rmdir()
assert [p['id'] for p in loaded[('OH', 'delaware')]] == ['sample'], loaded

# The built pages agree with the data: every featured partner appears on each of its county pages.
pages, _ = county.outputs(ROOT)
for p in data['partners']:
    for name in p['counties']:
        matches = [k for k, v in pages.items() if k.startswith(f'counties/{p["state"].lower()}/') and
                   re.search(r'<h1>Veterans help in ' + re.escape(name), v)]
        assert matches, (p['id'], name, 'no county page')
        shown = any(f'<h3>{county.e(p["name"])}</h3>' in pages[k] for k in matches)
        assert shown == (p['status'] == 'featured'), (p['id'], name, 'shown only when featured')
print('Local partners OK:', len(data['partners']), 'entries,',
      sum(p['status'] == 'featured' for p in data['partners']), 'featured')
