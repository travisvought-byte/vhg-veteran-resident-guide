#!/usr/bin/env python3
"""Build the low-data, text-only edition of the country pages: world/lite/index.html and world/lite/<slug>.html,
one per country and region in data/world/countries.json.

Why (owner direction, November 25, 2026: reach underserved countries and people on slow or costly connections): many
veterans and families abroad are on cheap phones, paying for every megabyte, often through Opera Mini or a zero-rated
service such as Free Basics, which only takes pages that work without JavaScript, iframes, video or large images. So
each lite page is one small HTML file: no script, no stylesheet to fetch, no pictures, nothing to download but the page.
It works on feature-phone browsers, prints on one or two sheets, and is what the offline pack
(.github/workflows/offline-pack.yml) bundles for Kiwix readers and offline school, clinic and library servers.

Each page also carries a ready-made text message (the emergency number, the crisis line, the Veterans Crisis Line for
that region and the page link) that opens in the phone's SMS app or WhatsApp, because help in these places mostly
travels person to person.

The full country page stays the one search engines index: each lite page names it as canonical, and lite pages are left
out of the sitemap. The full page links here ("Text-only, low-data version"). Built by scripts/build_public.py; do not
edit the output by hand. Every number comes from the same data, with the same source and checked date, as the full page.
"""
import re
from html import escape
from urllib.parse import quote, urlsplit

import build_world as w

BASE = 'https://guide.vethomeguard.org/world/'
LITE = BASE + 'lite/'
# Built and published by .github/workflows/offline-pack.yml.
PACK = 'https://github.com/travisvought-byte/vhg-veteran-resident-guide/releases/download/offline/veteran-guide-world-lite'
MAX_BYTES = 16000  # a country page this size loads in a few seconds on 2G (GitHub Pages sends it compressed)
MAX_INDEX = 24000
# GoatCounter as a tiny image instead of its script, so the count still works with scripts off. Same counter and
# path form as assets/analytics.js (site name, then the path).
COUNT = 'https://vhg-guide.goatcounter.com/count?p=' + quote('/guide.vethomeguard.org/world/lite/', safe='/')
CSS = ('body{font:17px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:40em;margin:0 auto;padding:12px;color:#111;background:#fff}'
       'a{color:#0b4f8a}a:focus{outline:3px solid #a07014;outline-offset:2px}h1{font-size:1.4em;line-height:1.25}'
       'h2{font-size:1.15em;margin-top:1.6em;border-top:2px solid #14303f;padding-top:.5em}h3{font-size:1em;margin:1.2em 0 .2em}p{margin:.3em 0}'
       '.em{font-size:1.1em;padding:8px;border:2px solid #a00;background:#fff5f5}.c a{display:inline-block;margin:4px 12px 4px 0;padding:6px 0;font-weight:600}'
       '.m{color:#444;font-size:.9em}ul{padding-left:1.2em}li{margin:.4em 0}')
EMAIL = w.EMAIL
e = w.e


def host(url):
    return urlsplit(url).netloc.removeprefix('www.')


def head(title, desc, canonical, path):
    top = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(canonical)}">'
           f'<style>{CSS}</style></head>\n<body>')
    return top, f'<img src="{COUNT}{e(path)}" alt="" width="1" height="1">'


def foot(full, counter, subject):
    ask = f'mailto:{EMAIL}?subject={quote(subject)}'
    return (f'<hr><p class="m">Free from Veteran Home Guardians, an independent U.S. nonprofit. Numbers come from official government pages '
            f'and are not telephone-confirmed. <a href="{ask}">Report a wrong number</a></p>'
            f'<p class="m"><a href="index.html">All countries (text only)</a> · <a href="{e(full)}">Full page</a> · '
            f'<a href="https://guide.vethomeguard.org/privacy.html">Privacy</a></p>{counter}</body></html>\n')


def checked(item):
    """Source: page title (host), checked date. The host is written out so it can be copied by hand."""
    return (f'<p class="m">Source: <a href="{e(item["source_url"])}">{e(item["source_title"])}</a> ({e(host(item["source_url"]))}). '
            f'Checked {w.when(item["checked_on"])}.</p>')


def dial(numbers):
    return '<p class="c">' + ''.join(
        f'<a href="tel:{e(n["tel"])}">{e(n["display"])}</a>' + (f' <span class="m">{e(n["label"])}</span> ' if n.get('label') else '')
        for n in numbers) + '</p>'


def line(x):
    out = [f'<h3>{e(x["name"])}</h3><p>{e(x["about"])}</p>', dial(x['numbers'])]
    if x.get('partial'):
        hours = '' if x['hours'].rstrip('.') in x['partial'] else f' Hours: {e(x["hours"].rstrip("."))}.'
        out.append(f'<p><strong>Partial coverage:</strong> {e(x["partial"])}{hours}</p>')
    else:
        out.append(f'<p>Hours: {e(x["hours"].rstrip("."))}.</p>')
    if x.get('email'):
        out.append(f'<p>Email: <a href="mailto:{e(x["email"])}">{e(x["email"])}</a></p>')
    if x.get('address'):
        out.append(f'<p>Address: {e(x["address"])}</p>')
    if x.get('website'):
        out.append(f'<p>Website: <a href="{e(x["website"])}">{e(host(x["website"]))}</a></p>')
    out.append(checked(x))
    return ''.join(out)


def office(x):
    out = [f'<h3>{e(x["name"])}</h3><p>{e(x["about"])}</p>']
    if x.get('numbers'):
        out.append(dial(x['numbers']))
    for key, label in (('address', 'Address'), ('hours', 'Hours')):
        if x.get(key):
            out.append(f'<p>{label}: {e(x[key].rstrip("."))}.</p>')
    if x.get('other_contact'):
        out.append(f'<p>{e(x["other_contact"])}</p>')
    if x.get('email'):
        out.append(f'<p>Email: <a href="mailto:{e(x["email"])}">{e(x["email"])}</a></p>')
    out.append(checked(x))
    return ''.join(out)


def vcl_region(data, c):
    return {r['code']: r for r in data['us_abroad']['vcl']['regions']}[c['vcl_region']]


def us_help(data, c):
    """The Veterans Crisis Line for this region, the VA Foreign Medical Program line and the VA benefits line."""
    a = data['us_abroad']
    vcl, fmp, uc, b = a['vcl'], a['fmp'], a['fmp']['us_canada'], a['benefits']
    r = vcl_region(data, c)
    if r['code'] == 'NORTHCOM':
        how = 'Dial 988, then press 1.'
    else:
        how = f'Call <a href="tel:{e(r["tel"])}">{e(r["display"])}</a> off base, or DSN 988 on base. International charges may apply.'
    note = f'<p>{e(c["vcl_note"])}</p>' if c.get('vcl_note') else ''
    out = [f'<h2 id="us-veterans">U.S. veterans living in {e(c["name"])}</h2>',
           f'<h3>Veterans Crisis Line: {e(r["label"])}</h3><p>{how}</p>{note}',
           f'<p>If that number does not work, use <a href="{e(vcl["chat_url"])}">online chat</a> or another regional number '
           f'on the <a href="index.html#us-abroad">list of all regions</a>.</p>', checked(vcl)]
    parent = w.parent_of(data, c)
    place = parent or c
    toll = next((t for t in fmp['toll_free'] if t['country'] == place['name']), None)
    out.append('<h3>VA health care abroad: the Foreign Medical Program</h3>'
               '<p>Pays for care abroad for a VA-rated, service-connected condition. Get your FMP benefits letter on VA.gov under Letters.</p>')
    if place['slug'] == 'canada':
        out.append(f'<p>Call FMP at <a href="tel:{e(uc["tel"])}">{e(uc["display"])}</a> (TTY: 711) and select 3.</p>{checked(uc)}')
    elif toll:
        out.append(f'<p>Toll-free from {e(place["name"])}: <a href="tel:{e(toll["tel"])}">{e(toll["display"])}</a>. Hours: {e(fmp["hours"])}.</p>{checked(fmp)}')
    else:
        out.append(f'<p>VA lists no toll-free FMP line from {e(place["name"])}. Use <a href="https://www.va.gov/contact-us/ask-va/">Ask VA</a> online, '
                   f'or call <a href="tel:{e(uc["direct_tel"])}">{e(uc["direct_display"])}</a> and select 3 '
                   '(a U.S. number that may not connect from abroad; charges may apply).</p>' + checked(uc))
    out.append(f'<h3>VA benefits questions</h3><p><a href="tel:{e(b["tel"])}">{e(b["display"])}</a>, {e(b["hours"])}.</p>{checked(b)}')
    return ''.join(out)


def first_crisis(c):
    return next((x for x in c['lines'] if x['kind'] == 'crisis_line'), None)


def share_text(data, c):
    em = c['emergency']['numbers'][0]
    t = f'Veteran help in {w.in_place(c)}. Emergency: {em["display"]}.'
    crisis = first_crisis(c)
    if crisis:
        name = crisis['name'] if len(crisis['name']) <= 45 else 'Crisis line'
        t += f' {name}: {crisis["numbers"][0]["display"]}.'
    r = vcl_region(data, c)
    t += ' U.S. Veterans Crisis Line: ' + ('dial 988 then 1' if r['code'] == 'NORTHCOM' else r['display']) + '.'
    return t + f' More: {LITE}{c["slug"]}.html'


def share(data, c):
    t = quote(share_text(data, c), safe='')
    # "sms:?&body=" opens the messages app with the text filled in on both Android and iPhone.
    return ('<h2 id="share">Send this to someone</h2><p>Opens a message with the emergency number, the crisis lines and this page’s address. '
            'Nothing is sent until you press send.</p>'
            f'<p class="c"><a href="sms:?&amp;body={t}">Text message (SMS)</a><a href="https://wa.me/?text={t}">WhatsApp</a></p>')


def emergency(c):
    em = c['emergency']
    nums = ', '.join(f'<a href="tel:{e(n["tel"])}">{e(n["display"])}</a> ({e(n["label"])})' for n in em['numbers'])
    note = f' {e(em["note"])}' if em.get('note') else ''
    return f'<p class="em" id="emergency"><strong>Emergency in {e(w.in_place(c))}:</strong> call {nums}.{note}</p>{checked(em)}'


def country_page(data, c):
    place = w.in_place(c)
    full = BASE + c['slug'] + '.html'
    region = c.get('parent')
    if region:
        parent = w.parent_of(data, c)
        title = f'U.S. veterans on {c["name"]} (text only)'
        desc = f'Low-data, text-only page for U.S. veterans on {c["name"]}, {w.lower_first(c["kind_label"])}: emergency numbers, crisis lines, local offices and VA help.'
        h1 = f'U.S. veterans on {e(c["name"])}'
    else:
        title = f'Veterans in {place} (text only)'
        desc = f'Low-data, text-only page for veterans living in {place}: emergency number, veterans agency, crisis lines and VA help for U.S. veterans.'
        h1 = f'Veterans in {e(place)}'
    top, counter = head(title, desc, full, c['slug'] + '.html')
    body = [f'<p class="m"><a href="#share">Send to someone</a> · <a href="{e(full)}">Full page</a> · <a href="index.html">Other countries</a></p>',
            f'<main id="main"><h1>{h1}</h1>', emergency(c)]
    if region:
        body.append(f'<p>{e(c["name"])} is a {e(w.lower_first(c["kind_label"]))}. See also <a href="{e(parent["slug"])}.html">{e(parent["name"])}</a>.</p>')
    else:
        subs = w.regions_of(data, c)
        if subs:
            body.append('<p>Has its own page: ' + ', '.join(f'<a href="{e(r["slug"])}.html">{e(r["name"])}</a>' for r in subs) + '.</p>')
    if c.get('no_agency'):
        na = c['no_agency']
        body.append(f'<h2 id="agency">No national veterans agency</h2><p>{e(na["statement"])}</p>'
                    + (checked(na) if na.get('source_url') else f'<p class="m">Checked {w.when(na["checked_on"])}.</p>'))
    for kind, heading in w.KINDS:
        lines = [x for x in c['lines'] if x['kind'] == kind]
        if kind == 'agency' and (c.get('no_agency') or region):
            continue
        if kind == 'veterans_line' and region:
            continue
        if not lines:
            gap = {'veterans_line': c.get('no_veterans_line') or c.get('veterans_line_note'), 'crisis_line': c.get('no_crisis_line')}.get(kind)
            if gap:
                body.append(f'<h2 id="{kind.replace("_", "-")}">{heading}</h2><p>{e(gap)}</p>')
            continue
        body.append(f'<h2 id="{kind.replace("_", "-")}">{heading}</h2>' + ''.join(line(x) for x in lines))
    if region:
        body.append(f'<h2 id="us-local">Offices for U.S. veterans and retirees on {e(c["name"])}</h2>' + ''.join(office(x) for x in c['us_local']))
    body.append(us_help(data, c))
    body.append(share(data, c))
    body.append('</main>')
    return top + ''.join(body) + foot(full, counter, f'Veteran Resource Guide text-only page: {c["name"]}')


def index_page(data):
    items = sorted(data['countries'] + data.get('regions', []), key=lambda c: c['name'])
    top, counter = head('Veterans outside the U.S. (text only)',
                        f'Low-data, text-only help for veterans in {len(data["countries"])} countries: emergency numbers, veterans agencies, crisis lines and VA help abroad.',
                        BASE, 'index.html')
    rows = ''.join(f'<li><a href="{e(c["slug"])}.html">{e(c["name"])}</a> · emergency '
                   + ', '.join(f'<a href="tel:{e(n["tel"])}">{e(n["display"])}</a>' for n in c['emergency']['numbers'][:2]) + '</li>'
                   for c in items)
    vcl = data['us_abroad']['vcl']
    regions = ''.join(f'<li>{e(r["label"])}: ' + (f'<a href="tel:{e(r["tel"])}">{e(r["display"])}</a> off base, DSN 988 on base' if r['dsn'] else e(r['display'])) + '</li>'
                      for r in vcl['regions'])
    return (top + '<main id="main"><h1>Veterans outside the United States, text only</h1>'
            '<p>Small pages that load on slow connections and basic phones, with no pictures or scripts. '
            f'Choose the country you live in for its emergency number, veterans agency and crisis lines. <a href="{BASE}">Full version</a></p>'
            f'<h2>Countries</h2><ul>{rows}</ul>'
            f'<h2 id="us-abroad">Veterans Crisis Line from outside the U.S.</h2><p>For U.S. veterans, by region. If your number does not work, try another, '
            f'or use <a href="{e(vcl["chat_url"])}">online chat</a>. International charges may apply.</p><ul>{regions}</ul>{checked(vcl)}'
            '<h2>Use it with no internet</h2><p>Download every country at once: '
            f'<a href="{PACK}.zim">Kiwix file</a> (open it in the free Kiwix app on a phone or computer) or '
            f'<a href="{PACK}.zip">zip of plain pages</a> (unzip and open index.html). Schools, clinics and libraries with offline servers can load the Kiwix file.</p>'
            '<h2>In the United States</h2><p>Every state has its own guide: <a href="https://guide.vethomeguard.org/">guide.vethomeguard.org</a></p></main>'
            + foot(BASE, counter, 'Veteran Resource Guide text-only pages'))


def check(name, page):
    size, limit = len(page.encode()), MAX_INDEX if name.endswith('index.html') else MAX_BYTES
    assert size <= limit, f'{name} is {size} bytes; keep it under {limit}'
    for bad in ('<script', '<iframe', '<video', '<link rel="stylesheet"'):
        assert bad not in page, f'{name} has {bad}'
    assert len(re.findall(r'<img ', page)) == 1, f'{name}: only the counter image is allowed'


def pages():
    data = w.load()
    return ['world/lite/index.html'] + [f'world/lite/{c["slug"]}.html' for c in data['countries'] + data.get('regions', [])]


def outputs():
    data = w.load()
    out = {'world/lite/index.html': index_page(data)}
    for c in data['countries'] + data.get('regions', []):
        out[f'world/lite/{c["slug"]}.html'] = country_page(data, c)
    for name, page in out.items():
        check(name, page)
    return out


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text.encode()))
