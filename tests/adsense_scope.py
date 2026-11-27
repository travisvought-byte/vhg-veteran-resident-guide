#!/usr/bin/env python3
"""Google AdSense stays on findbingo.org and off the guide (owner direction, November 27, 2026).

HARD RULE: guide.vethomeguard.org runs Google Ad Grants, which forbids AdSense. The AdSense code and ads.txt may only
appear in bingo-site/findbingo/ (served at findbingo.org and www.findbingo.org through the Ohio-Bingo mirror), never in
a page the guide's GitHub Pages site publishes, never in findbingo-site/ (served at guide.vethomeguard.org/findbingo-site/)
and never at the guide's root. This checks the files in the repository, the build's own output, and _config.yml, which
keeps bingo-site/ out of the guide's Pages build.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import findbingo_site as f  # noqa: E402

MARKERS = ('adsbygoogle', 'googlesyndication', 'pub-9220804879239310', 'google-adsense-account')
ADS_LINE = 'google.com, pub-9220804879239310, DIRECT, f08c47fec0942fa0\n'
# Where the markers may appear: the findbingo.org folder, the code that writes it, and these checks and notes.
ALLOWED = ('bingo-site/findbingo/', 'scripts/findbingo_site.py', 'tests/', 'docs/')
SKIP_DIRS = {'.git', 'node_modules', '__pycache__'}


def repo_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath, name).relative_to(ROOT).as_posix()


def text_of(rel):
    try:
        return (ROOT / rel).read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return ''


failures = []
files = list(repo_files())

# 1. The markers appear only where they may.
for rel in files:
    text = text_of(rel)
    found = [m for m in MARKERS if m in text]
    if found and not rel.startswith(ALLOWED):
        failures.append(f'{rel}: AdSense code outside findbingo.org ({", ".join(found)})')

# 2. One ads.txt, at the findbingo.org root, with exactly the publisher line. None at the guide's root.
ads_files = sorted(rel for rel in files if rel.rsplit('/', 1)[-1] == 'ads.txt')
if ads_files != ['bingo-site/findbingo/ads.txt']:
    failures.append(f'ads.txt must exist only at bingo-site/findbingo/ads.txt, found {ads_files}')
elif (ROOT / 'bingo-site/findbingo/ads.txt').read_text() != ADS_LINE:
    failures.append('bingo-site/findbingo/ads.txt must hold exactly: ' + ADS_LINE.strip())

# 3. The guide's GitHub Pages build leaves bingo-site/ out, so its pages are never served on guide.vethomeguard.org.
config = (ROOT / '_config.yml').read_text() if (ROOT / '_config.yml').exists() else ''
excluded = re.search(r'^exclude:\s*\n((?:\s+-\s*.+\n?)+)', config, re.M)
if not excluded or 'bingo-site' not in [x.strip().strip('"\'').rstrip('/') for x in re.findall(r'-\s*(.+)', excluded.group(1))]:
    failures.append('_config.yml must exclude bingo-site from the guide\'s GitHub Pages build')
if (ROOT / '.nojekyll').exists():
    failures.append('.nojekyll at the guide root would make GitHub Pages ignore _config.yml and publish bingo-site/')

# 4. The build itself: the code lands on findbingo.org's pages (once each), and nowhere else.
from build_public import outputs  # noqa: E402

built = outputs()
pages = 0
for name, content in built.items():
    if not isinstance(content, str):
        continue
    found = [m for m in MARKERS if m in content]
    if found and not name.startswith('bingo-site/findbingo/'):
        failures.append(f'build output {name}: AdSense code outside findbingo.org')
    if name.startswith('bingo-site/findbingo/') and name.endswith('.html') and '</head>' in content:
        rel = name[len('bingo-site/findbingo/'):]
        want = 0 if rel in f.NO_ADSENSE else 1
        if content.count(f.ADSENSE_HEAD) != want or content.count('adsbygoogle.js') != want:
            failures.append(f'{name}: the AdSense code should appear {want} time(s)')
        if want and content.index(f.ADSENSE_HEAD) > content.index('</head>'):
            failures.append(f'{name}: the AdSense code belongs in <head>')
        pages += want
for name in ('index.html', 'ohio/index.html', 'ohio/columbus/index.html', 'michigan/index.html', 'texas/san-antonio/index.html', 'halls/index.html'):
    if f.ADSENSE_HEAD not in built.get('bingo-site/findbingo/' + name, ''):
        failures.append(f'findbingo.org/{name} should load the AdSense code')
for name in ('findbingo-site/index.html', 'findbingo-site/michigan/index.html', 'bingo-site/index.html', 'bingo.html', 'index.html'):
    if name in built and any(m in built[name] for m in MARKERS):
        failures.append(f'{name} must not carry AdSense (served on a vethomeguard.org host)')
if built.get('bingo-site/findbingo/ads.txt') != ADS_LINE or [n for n in built if n.endswith('ads.txt')] != ['bingo-site/findbingo/ads.txt']:
    failures.append('the build must write ads.txt only at bingo-site/findbingo/ads.txt')
if pages < 100:
    failures.append(f'expected the AdSense code on findbingo.org\'s pages, found it on {pages}')

if failures:
    print('FAIL: AdSense scope\n  ' + '\n  '.join(failures))
    sys.exit(1)
print(f'PASS: AdSense code on {pages} findbingo.org pages and ads.txt at the findbingo.org root only; none on the guide, '
      'findbingo-site/ or the guide root, and _config.yml keeps bingo-site/ out of the guide\'s Pages build.')
