#!/usr/bin/env python3
"""Veteran-owned Ohio contractors (guide.vethomeguard.org/contractors/): every listing comes from the SBA VetCert
registry with its profile link and checked date, is labeled as a public registry listing and not a VHG partner, and
has a claim link and a remove link; no license or insurance mark shows without an official record; every price row
names an https source and a range that makes sense; the Ohio repair rule and the Attorney General's complaint line
are on the fair-price page; the signup never asks for a DD-214 upload; the three pages are in the sitemap and carry
the visit counter; and the Ohio chooser links the directory."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_contractors  # noqa: E402

reg = json.loads((ROOT / 'data/contractors/registry.json').read_text(encoding='utf-8'))
prices = json.loads((ROOT / 'data/contractors/prices.json').read_text(encoding='utf-8'))
assert date.fromisoformat(reg['checked_on']) <= date.today() and date.fromisoformat(prices['checked_on']) <= date.today()
trades = {t['key'] for t in reg['trades']}
listed = reg['listed']
ids = [r['id'] for r in listed]
assert len(ids) == len(set(ids)), 'duplicate listing id'
for r in listed:
    assert set(r['certs']) <= {'VOSB', 'SDVOSB', 'WOSB', 'EDWOSB', 'HUBZone', '8(a)'} and 'VOSB' in r['certs'], (r['id'], 'certification')
    assert r['sba_profile'].startswith('https://search.certifications.sba.gov/profile/'), (r['id'], 'SBA profile link')
    assert r['main_trade'] in trades and set(r['other_trades']) <= trades and r['main_trade'] not in r['other_trades'], r['id']
    assert not r['phone'] or re.fullmatch(r'\d{3}-\d{3}-\d{4}', r['phone']), (r['id'], r['phone'])
    assert not r['website'] or urlsplit(r['website']).scheme == 'https', (r['id'], r['website'])
    assert not r['zip'] or re.fullmatch(r'4[3-5]\d{3}', r['zip']), (r['id'], 'Ohio ZIP')
    # A license mark needs the official record it was read on.
    lic = r['license']
    assert lic is None or (lic.get('number') and lic.get('source_url', '').startswith('https://') and date.fromisoformat(lic['checked_on'])), r['id']

page = (ROOT / 'contractors/index.html').read_text(encoding='utf-8')
cards = re.findall(r'<article class="biz" id="biz-([a-z0-9-]+)"', page)
assert sorted(cards) == sorted(ids), 'every listing has exactly one card'
assert page.count('Not a VHG partner.') == len(listed), 'every card says it is not a VHG partner'
assert page.count('Your business? Claim it free') == len(listed) and page.count('Ask us to remove it') == len(listed), 'claim and remove links'
for m in re.finditer(r'href="(mailto:[^"]+)"', page):
    href = m.group(1).replace('&amp;', '&')
    assert href.startswith('mailto:' + build_contractors.EMAIL + '?subject='), href
assert 'VHG partner</span>' not in page and 'Community partner' not in page, 'no partner badge on registry listings'
assert 'Not checked by us yet' in page
all_ids = re.findall(r'\sid="([^"]+)"', page)
assert len(all_ids) == len(set(all_ids)), 'ids are unique on the directory page'
assert page.count('class="trade-group"') == len({r['main_trade'] for r in listed})
for rel in ('contractors/fair-prices.html', 'contractors/join.html'):
    other = re.findall(r'\sid="([^"]+)"', (ROOT / rel).read_text(encoding='utf-8'))
    assert len(other) == len(set(other)), 'ids are unique on ' + rel

fair = (ROOT / 'contractors/fair-prices.html').read_text(encoding='utf-8')
for t in prices['trades']:
    for j in t['jobs']:
        assert urlsplit(j['source']['url']).scheme == 'https', j['job']
        assert j['low'] is None or j['high'] is None or j['low'] <= j['high'], j['job']
        assert j['low'] is not None or j['typical'] is not None, j['job']
        assert build_contractors.e(j['job']) in fair, j['job']
for h in prices['hourly']:
    assert 0 < h['low'] <= h['high'] <= 650 and urlsplit(h['url']).scheme == 'https', h['trade']
for needed in ['https://codes.ohio.gov/ohio-administrative-code/rule-109:4-3-05', 'https://filecomplaint.ohioattorneygeneral.gov/',
               'tel:18002820515', 'Typical ranges, not quotes', 'Chart data', 'id="wages"']:
    assert needed in fair, needed
assert '18 outlet' not in fair.replace('$18 outlet replacement', ''), 'the Fixr outlet outlier stays out of the tables'

join = (ROOT / 'contractors/join.html').read_text(encoding='utf-8')
names = json.loads(re.search(r'<script type="application/json" id="claim-names">(.*?)</script>', join).group(1))
assert set(names) == set(ids), 'every listing can be claimed by its id'
assert 'type="file"' not in join, 'the signup never takes uploads'
assert "don’t send it in this form" in join and f'data-to="{build_contractors.EMAIL}"' in join
for p in ['contractors/index.html', 'contractors/fair-prices.html', 'contractors/join.html']:
    text = (ROOT / p).read_text(encoding='utf-8')
    assert '../assets/analytics.js' in text, (p, 'visit counter')
    assert '<link rel="canonical" href="https://guide.vethomeguard.org/' + ('contractors/' if p.endswith('index.html') else p) + '">' in text, p
    assert 'Skip to' in text and '<main' in text, (p, 'skip link and main')
sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
for u in build_contractors.pages():
    assert '<loc>https://guide.vethomeguard.org/' + u + '</loc>' in sitemap, u

chooser = json.loads((ROOT / 'data/landing/chooser.json').read_text(encoding='utf-8'))
opt = next(o for o in chooser['options'] if o['id'] == 'contractor')
assert opt['href'] == 'contractors/' and opt['states'] == ['OH']
assert 'href="contractors/" data-who="contractor"' in (ROOT / 'index.html').read_text(encoding='utf-8')
by_trade = {}
for r in listed:
    by_trade[r['main_trade']] = by_trade.get(r['main_trade'], 0) + 1
print(f'ok: {len(listed)} veteran-owned listings ({", ".join(f"{k} {v}" for k, v in sorted(by_trade.items(), key=lambda x: -x[1]))}), '
      f'{sum(len(t["jobs"]) for t in prices["trades"])} sourced price rows, signup and sitemap')
