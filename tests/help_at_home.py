#!/usr/bin/env python3
"""Help at home (guide.vethomeguard.org/help-at-home/): no provider shows without having accepted a listing, and each
kind of help says first providers are coming until one has; every program names an https official page and the date
it was read; every kind of help shows a price from the shared fair-price data and the programs that may pay; the signup
mails VHG, never takes uploads, never sets anyone's prices and asks for a veteran who vouches; the three pages carry
the visit counter, a skip link and their canonical address and are in the sitemap; the covered counties' office pages
and the Ohio chooser link the section; and accessibility changes and caregiving link to Mobility Talk."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_help_at_home as b  # noqa: E402

data, prices = b.load()
read = lambda rel: (ROOT / rel).read_text(encoding='utf-8')  # noqa: E731
assert date.fromisoformat(data['checked_on']) <= date.today()
service_keys = [s['key'] for s in data['services']]
assert service_keys == ['repairs', 'accessibility', 'caregiving', 'yard'], 'the four kinds of help Travis named'
county_keys = [c['key'] for c in data['counties']]
assert county_keys[:2] == ['morrow', 'knox'], 'Morrow and Knox first'

# Providers: only people who accepted, never from a registry or search.
for p in data['providers']:
    assert date.fromisoformat(p['accepted_on']) <= date.today(), (p['id'], 'accepted_on')
    assert set(p['services']) <= set(service_keys) and set(p['counties']) <= set(county_keys), p['id']
    assert p.get('vouched_by'), (p['id'], 'a veteran vouches for every provider')
    assert not p.get('phone') or re.fullmatch(r'\d{3}-\d{3}-\d{4}', p['phone']), p['id']

# Programs: an official https page each, and every kind of help has at least one.
for p in data['programs']:
    assert urlsplit(p['source']['url']).scheme == 'https', p['key']
    assert set(p['pays']) <= set(service_keys) and set(p['pays'].values()) <= set(b.PAYS), p['key']
    for a in p.get('amounts', []):
        assert isinstance(a['amount'], int) and a['amount'] > 0, p['key']
for k in service_keys:
    assert b.programs_for(k, data['programs']), k + ' has a program that may pay'

index = read('help-at-home/index.html')
who = read('help-at-home/who-pays.html')
join = read('help-at-home/join.html')
for s in data['services']:
    sec = re.search(r'<section class="svc" id="svc-' + s['key'] + r'".*?</section>', index, re.S).group(0)
    assert b.e(b.typical(s, prices)) in sec, s['key'] + ' shows a price from the fair-price data'
    assert 'who-pays.html#prog-' in sec and 'who-pays.html#kind-' + s['key'] in sec, s['key']
    has = [p for p in data['providers'] if s['key'] in p['services']]
    if not has:
        assert 'First providers coming.' in sec, s['key'] + ' says first providers are coming'
    assert sec.count('class="biz"') == len(has), s['key'] + ' shows only accepted providers'
    href = s['prices_href']
    if '#' in href:
        assert 'id="' + href.split('#')[1] + '"' in read('contractors/fair-prices.html'), href
assert 'Mobility Talk' in index and 'https://mobilitytalk.org/home-modifications.html' in index and 'https://mobilitytalk.org/paid-family-caregiver.html' in index
for c in data['counties']:
    assert f'<option value="{c["key"]}">' in index, c['key']
    for x in c['call_first']:
        assert 'tel:' + x['phone'].replace('-', '') in index and urlsplit(x['url']).scheme == 'https', x['name']
    page = read(c['page'])
    assert f'href="../../help-at-home/?county={c["key"]}#find"' in page, c['page'] + ' links help at home'

for p in data['programs']:
    assert f'id="prog-{p["key"]}"' in who and b.e(p['source']['url']) in who, p['key']
    for a in p.get('amounts', []):
        assert b.money(a['amount']) in who, (p['key'], a['label'])
assert who.count('read ' + b.when(data['checked_on'])) >= len(data['programs']), 'each program says when it was read'
assert '$133,042' in who and '$26,654' in who and '$6,800' in who, 'FY 2027 adapted housing and HISA amounts'
assert 'No program pays for routine yard work' not in who and 'No VA program pays for routine yard work' in who, 'honest about yard work'

assert 'You set your prices, not us.' in join and 'type="file"' not in join, 'never sets prices, never takes uploads'
assert f'data-to="{b.EMAIL}"' in join and 'name="voucher"' in join, 'mails VHG and asks for a veteran who vouches'
for rel, text in [('help-at-home/index.html', index), ('help-at-home/who-pays.html', who), ('help-at-home/join.html', join)]:
    ids = re.findall(r'\sid="([^"]+)"', text)
    assert len(ids) == len(set(ids)), rel + ': ids are unique'
    for m in re.finditer(r'href="(mailto:[^"]+)"', text):
        assert m.group(1).replace('&amp;', '&').startswith('mailto:' + b.EMAIL + '?subject='), m.group(1)
    for m in re.finditer(r'href="#([^"]+)"', text):
        assert f'id="{m.group(1)}"' in text, rel + ': jump to #' + m.group(1)
    assert '../assets/analytics.js' in text, rel + ': visit counter'
    canon = 'https://guide.vethomeguard.org/' + ('help-at-home/' if rel.endswith('index.html') else rel)
    assert f'<link rel="canonical" href="{canon}">' in text, rel
    assert 'Skip to' in text and '<main' in text, rel + ': skip link and main'
    assert 'Crisis Line' not in text and 'tel:988' not in text and 'Need help now' not in text, rel + ': a normal guide page, no crisis banner'
for rel, target in [('help-at-home/index.html', 'who-pays.html#kind-'), ('help-at-home/who-pays.html', './?service=')]:
    assert target in read(rel)
for m in re.finditer(r'href="who-pays\.html#([^"]+)"', index):
    assert f'id="{m.group(1)}"' in who, '#' + m.group(1)

# A provider card, once someone accepts, shows what they agreed to and a feedback link.
sample = {'id': 'sample', 'name': 'Sample Handyman', 'services': ['repairs', 'yard'], 'counties': ['knox'], 'phone': '740-555-0100',
          'veteran': True, 'vouched_by': 'a Knox County veteran he did a porch repair for', 'accepted_on': '2026-11-28', 'rates': '$60 an hour'}
card = b.provider_card(sample, data['services'], data['counties'])
assert 'Veteran-owned' in card and 'Listed November 28, 2026' in card and 'Tell us how a job went' in card and 'data-county="knox"' in card
try:
    b.provider_card(dict(sample, accepted_on=None), data['services'], data['counties'])
    raise SystemExit('a provider without accepted_on must not render')
except AssertionError:
    pass

sitemap = read('sitemap.xml')
for u in b.pages():
    assert '<loc>https://guide.vethomeguard.org/' + u + '</loc>' in sitemap, u
chooser = json.loads(read('data/landing/chooser.json'))
opt = next(o for o in chooser['options'] if o['id'] == 'home-help')
assert opt['href'] == 'help-at-home/' and opt['states'] == ['OH']
assert 'href="help-at-home/" data-who="home-help"' in read('index.html')
assert 'href="../help-at-home/"' in read('contractors/index.html'), 'contractor pages link help at home'
print(f'ok: help at home, {len(service_keys)} kinds of help in {len(county_keys)} counties, {len(data["programs"])} sourced programs, '
      f'{len(data["providers"])} accepted providers, signup, county links and sitemap')
