#!/usr/bin/env python3
"""Pack the text-only country pages (world/lite/) into files people can carry where there is no internet (owner
direction, November 25, 2026: serve underserved countries and people with little or no connection).

Writes two files to dist/ (not committed; .github/workflows/offline-pack.yml publishes them on the "offline" release):
- veteran-guide-world-lite.zim: for Kiwix, the free offline reader for Android, iPhone, Windows, Mac and Linux, and for
  offline school, clinic and library servers such as Internet-in-a-Box that carry Kiwix files.
- veteran-guide-world-lite.zip: the same pages as plain HTML; unzip and open index.html in any browser.

The visit counter image is removed from the packed copies: an offline reader has nothing to count with. Links to the
full pages stay as web addresses. Needs the libzim package (pip install libzim) for the ZIM; the ZIP needs nothing.
Run after python3 scripts/build_public.py.
"""
import datetime, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LITE = ROOT / 'world/lite'
DIST = ROOT / 'dist'
NAME = 'veteran-guide-world-lite'


def pages():
    for f in sorted(LITE.glob('*.html')):
        t = f.read_text(encoding='utf-8')
        t = re.sub(r'<img src="https://vhg-guide\.goatcounter\.com/[^"]*" alt="" width="1" height="1">', '', t)
        assert '<img' not in t and '<script' not in t, f.name
        yield f.name, t


def build_zip(items):
    out = DIST / f'{NAME}.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, t in items:
            z.writestr(f'{NAME}/{name}', t)
        z.writestr(f'{NAME}/README.txt', 'Veteran Resource Guide, text-only country pages: help for veterans living outside the United States.\n'
                   'Open index.html in any web browser. Works with no internet connection; phone numbers and web links still need a phone or a connection.\n'
                   'Every number comes from an official page; each listing shows its source and the date it was checked. '
                   'Newest copy: https://guide.vethomeguard.org/world/lite/\n')
    return out


def build_zim(items):
    from libzim.writer import Creator, Item, StringProvider, Hint

    class Page(Item):
        def __init__(self, path, title, content):
            super().__init__()
            self.p, self.t, self.c = path, title, content
        def get_path(self): return self.p
        def get_title(self): return self.t
        def get_mimetype(self): return 'text/html'
        def get_contentprovider(self): return StringProvider(self.c)
        def get_hints(self): return {Hint.FRONT_ARTICLE: True}

    out = DIST / f'{NAME}.zim'
    if out.exists():
        out.unlink()
    with Creator(str(out)).config_indexing(True, 'eng') as c:
        c.set_mainpath('index.html')
        c.add_illustration((ROOT / 'assets/icon-48.png').read_bytes(), 48)
        for k, v in {'Name': 'vethomeguard_en_world-lite', 'Title': 'Veteran Resource Guide: veterans abroad',
                     'Description': 'Help for veterans outside the U.S.: emergency numbers, veterans agencies, crisis lines',
                     'Language': 'eng', 'Creator': 'Veteran Home Guardians', 'Publisher': 'Veteran Home Guardians',
                     'Date': datetime.date.today().isoformat(), 'Tags': 'veterans;health;crisis;_category:other',
                     'Source': 'https://guide.vethomeguard.org/world/lite/'}.items():
            c.add_metadata(k, v)
        for name, t in items:
            title = re.search(r'<title>(.*?)</title>', t).group(1).replace(' (text only)', '')
            c.add_item(Page(name, title, t))
    return out


if __name__ == '__main__':
    DIST.mkdir(exist_ok=True)
    items = list(pages())
    assert len(items) > 40, 'run python3 scripts/build_public.py first'
    print('Wrote', build_zip(items).name)
    if '--zip-only' not in sys.argv:
        print('Wrote', build_zim(items).name)
