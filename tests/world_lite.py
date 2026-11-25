#!/usr/bin/env python3
"""Text-only country pages (world/lite/): one per country and region plus an index; each is small, has no script,
stylesheet, frame, video or picture but the one-pixel visit counter, names its full page as canonical, puts the
emergency number first, dials every number the full page lists, and offers an SMS and WhatsApp message with the
emergency number and the page address. Full pages link to their text-only copy, and lite pages stay out of the sitemap."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_world_lite as lite  # noqa: E402

data = json.loads((ROOT / 'data/world/countries.json').read_text(encoding='utf-8'))
items = data['countries'] + data.get('regions', [])
sitemap = (ROOT / 'sitemap.xml').read_text()
assert '/world/lite/' not in sitemap, 'lite pages stay out of the sitemap'

files = sorted((ROOT / 'world/lite').glob('*.html'))
assert len(files) == len(items) + 1, (len(files), len(items))
for f in files:
    page = f.read_text(encoding='utf-8')
    limit = lite.MAX_INDEX if f.name == 'index.html' else lite.MAX_BYTES
    assert len(page.encode()) <= limit, (f.name, len(page.encode()))
    for bad in ('<script', '<iframe', '<video', '<link rel="stylesheet"', 'family-guide.css'):
        assert bad not in page, (f.name, bad)
    imgs = re.findall(r'<img [^>]*>', page)
    assert len(imgs) == 1 and 'vhg-guide.goatcounter.com/count?p=/guide.vethomeguard.org/world/lite/' + f.name in imgs[0], (f.name, imgs)

for c in items:
    name = c['slug'] + '.html'
    page = (ROOT / 'world/lite' / name).read_text(encoding='utf-8')
    full = (ROOT / 'world' / name).read_text(encoding='utf-8')
    assert f'<link rel="canonical" href="https://guide.vethomeguard.org/world/{name}">' in page, name
    assert f'href="lite/{name}"' in full and 'data-lite-link' in full, (name, 'full page links to its text-only copy')
    em = page.index('id="emergency"')
    assert em < page.index('<h2'), (name, 'emergency number before every section')
    for n in c['emergency']['numbers']:
        assert f'href="tel:{n["tel"]}"' in page[em:em + 2000], (name, n['tel'])
    for x in c['lines'] + c.get('us_local', []):
        for n in x.get('numbers', []):
            assert f'href="tel:{n["tel"]}"' in page, (name, x['name'], n['tel'])
        assert lite.e(x['source_url']) in page, (name, x['name'], 'source')
    if c.get('no_agency'):
        assert 'No national veterans agency' in page, name
    for kind in ('sms:?&amp;body=', 'https://wa.me/?text='):
        m = re.search(re.escape(f'href="{kind}') + r'([^"]+)"', page)
        assert m, (name, kind)
        text = unquote(m.group(1))
        assert f'Emergency: {c["emergency"]["numbers"][0]["display"]}.' in text, (name, text)
        assert text.endswith(f'https://guide.vethomeguard.org/world/lite/{name}') and len(text) <= 320, (name, len(text))

index = (ROOT / 'world/lite/index.html').read_text(encoding='utf-8')
for c in items:
    assert f'href="{c["slug"]}.html"' in index, c['slug']
for r in data['us_abroad']['vcl']['regions']:
    assert r['label'] in index, r['code']
assert lite.PACK + '.zim' in index and lite.PACK + '.zip' in index
assert 'href="lite/index.html"' in (ROOT / 'world/index.html').read_text(encoding='utf-8')
print(f'PASS: {len(items)} text-only country and region pages and an index; small, script-free, sourced, shareable by SMS and WhatsApp, '
      'linked from every full page and kept out of the sitemap.')
