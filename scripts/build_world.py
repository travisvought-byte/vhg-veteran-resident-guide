"""Build the country pages of the Veteran Resource Guide (guide.vethomeguard.org/world/).

Run by scripts/build_public.py. The canonical data is data/world/countries.json: for each country, the
national emergency number, the official veterans agency, any veterans support line and the national crisis
line, each with the official page it was read on and the date it was checked. A line that is not a 24-hour
crisis line says so on the page. The world index also carries what U.S. veterans living abroad need: the VA
Foreign Medical Program and the Veterans Crisis Line's overseas numbers, taken from va.gov and
veteranscrisisline.net.
"""
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guide.vethomeguard.org/world/'
EMAIL = 'travis@vethomeguard.org'
KINDS = [('agency', 'Official veterans agency'), ('veterans_line', 'Veterans support line'),
         ('crisis_line', 'National crisis line')]


def load():
    return json.loads((ROOT / 'data/world/countries.json').read_text(encoding='utf-8'))


def when(value):
    """2026-10-08 -> October 8, 2026; 2025-11 -> November 2025."""
    if not value:
        return ''
    parts = [int(p) for p in value.split('-')]
    if len(parts) == 2:
        return date(parts[0], parts[1], 1).strftime('%B %Y')
    d = date(*parts)
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


def e(text):
    return escape(text or '', quote=True)


def tel(number):
    return f'<a href="tel:{e(number["tel"])}">{e(number["display"])}</a>'


def source(item, prefix=''):
    url, title, dated = item[prefix + 'source_url'], item[prefix + 'source_title'], item.get(prefix + 'source_date')
    page = f', page dated {when(dated)}' if dated else ', page shows no date'
    return f'<a data-source href="{e(url)}" rel="noopener">{e(title)}</a>{page}'


def source_line(item):
    also = ''
    if item.get('also_source_url'):
        also = ' Also: ' + source(item, 'also_') + '.'
    return (f'<p class="small source">Source: {source(item)}.{also} Checked {when(item["checked_on"])}.</p>')


def numbers(items):
    return '<ul class="numbers">' + ''.join(
        f'<li>{tel(n)}<span class="small"> {e(n.get("label", ""))}</span></li>' for n in items) + '</ul>'


STYLE = '''<style>
.world{max-width:1000px}.world section{margin-bottom:34px}.card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:8px;padding:18px 20px;margin:0 0 16px}
.card h3{margin-top:0}.numbers{list-style:none;padding:0;margin:8px 0}.numbers li{padding:4px 0}.numbers a[href^="tel:"]{font-size:22px;display:inline-block;min-height:44px;line-height:44px}
.emergency{background:#fbeceb;border:2px solid #b3261e;border-radius:8px;padding:16px 20px}.emergency h2{color:#7d1a14;margin-top:0}
.partial{background:#fff1ce;color:#5b4210;border-radius:5px;padding:8px 12px;margin:10px 0}.full{background:#e3efe7;color:#21493a;border-radius:5px;padding:8px 12px;margin:10px 0}
.us-block{background:#e8eeea;border-radius:8px;padding:18px 22px}.us-block h3{margin-top:14px}
table{border-collapse:collapse;width:100%;background:#fff}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.country-list{columns:2;padding-left:20px}.country-list li{margin:6px 0;break-inside:avoid}
@media(max-width:700px){.country-list{columns:1}th,td{padding:6px}.world{padding:16px 16px}}
</style>'''


def head(title, desc, url):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="../assets/family-guide.css">
{STYLE}
<script src="../assets/analytics.js" defer></script></head><body>
<header><nav aria-label="Main"><a href="../">Veteran Resource Guide</a><a href="./">Veterans outside the U.S.</a><a href="../family-guide.html">Family Guide</a><a href="../flyers.html">Printable flyers</a></nav>'''


def footer():
    ask = 'mailto:' + EMAIL + '?subject=Veteran%20Resource%20Guide%20country%20page'
    return (f'<footer class="world" style="margin:auto;padding:18px 24px"><p>Free from Veteran Home Guardians. Numbers come from official government pages and are not '
            f'telephone-confirmed. Report a wrong number: <a href="{ask}">{EMAIL}</a>.</p>'
            '<p><a href="../">Back to the Veteran Resource Guide</a> · <a href="../privacy.html">Privacy</a></p></footer>\n</body></html>\n')


def vcl_for(data, country):
    vcl = data['us_abroad']['vcl']
    regions = {r['code']: r for r in vcl['regions']}
    r = regions[country['vcl_region']]
    how = f'call {tel(r)} off base or DSN 988 on base' if r['dsn'] else e(r['display'])
    lead = f'{e(country["name"])} is in the U.S. {e(r["label"])} region'
    if r['code'] == 'NORTHCOM':
        lead, how = 'For North America (NORTHCOM)', 'the Veterans Crisis Line lists “Dial 988 then press 1”'
    place = ''
    src = data['region_sources'].get(r['code'])
    if src:
        place = f' (<a href="{e(src["url"])}" rel="noopener">{e(src["title"])}</a>, checked {when(src["checked_on"])})'
    note = f'<p>{e(country["vcl_note"])}</p>' if country.get('vcl_note') else ''
    others = ', '.join(f'{e(x["label"])}: {tel(x) if x["dsn"] else e(x["display"])}' for x in vcl['regions'] if x['code'] not in (r['code'], 'NORTHCOM'))
    return (f'<h3>Veterans Crisis Line from {e(country["name"])}</h3>'
            f'<p>{lead}{place}: {how}.</p>{note}'
            f'<p class="small">If that does not work, the Veterans Crisis Line says to try another regional number ({others}), '
            f'or use <a href="{e(vcl["chat_url"])}" rel="noopener">online chat</a>. International charges may apply.</p>'
            f'<p class="small source">Source: {source(vcl)}. Checked {when(vcl["checked_on"])}.</p>')


def fmp_for(data, country):
    fmp = data['us_abroad']['fmp']
    line = next((t for t in fmp['toll_free'] if t['country'] == country['name']), None)
    if country['slug'] == 'canada':
        uc = fmp['us_canada']
        call = (f'<p>Call FMP at {tel(uc)} (U.S. and Canada, toll-free) or {tel({"display": uc["direct_display"], "tel": uc["direct_tel"]})}.</p>'
                f'<p class="small">{e(uc["note"])}</p><p class="small">{e(country.get("fmp_note", ""))}</p>'
                f'<p class="small source">Source: {source(uc)}. Checked {when(uc["checked_on"])}.</p>')
    elif line:
        call = (f'<p>Call FMP toll-free from {e(country["name"])}: {tel(line)}. Hours: {e(fmp["hours"])}.</p>'
                f'<p class="small source">Sources: {source(fmp)}; for the hours, <a data-source href="{e(fmp["claims_source_url"])}" rel="noopener">'
                f'{e(fmp["claims_source_title"])}</a>, page dated {when(fmp["claims_source_date"])}. Checked {when(fmp["checked_on"])}.</p>')
    else:
        uc = fmp['us_canada']
        call = (f'<p>VA lists no toll-free FMP line for {e(country["name"])}. You can reach FMP online through '
                '<a href="https://www.va.gov/contact-us/ask-va/" rel="noopener">Ask VA</a>, or call the program’s direct number, '
                f'{tel({"display": uc["direct_display"], "tel": uc["direct_tel"]})} (international charges apply).</p>'
                f'<p class="small source">Source for the direct number: {source(uc)}. Checked {when(uc["checked_on"])}.</p>')
    return (f'<h3>VA health care: the Foreign Medical Program</h3><p>{e(fmp["covers"])}</p><p>{e(fmp["letter"])}</p>{call}')


def benefits_block(data):
    b = data['us_abroad']['benefits']
    return (f'<h3>VA benefits questions</h3><p>{e(b["name"])}: {tel(b)}, {e(b["hours"])}.</p>'
            f'<p class="small source">Source: {source(b)}. Checked {when(b["checked_on"])}.</p>')


def line_card(line):
    status = (f'<p class="partial" data-partial><strong>Partial coverage:</strong> {e(line["partial"])}</p>' if line.get('partial')
              else f'<p class="full">Hours: {e(line["hours"].rstrip("."))}.</p>')
    hours = f'<p class="small">Hours: {e(line["hours"].rstrip("."))}.</p>' if line.get('partial') else ''
    extra = ''
    if line.get('email'):
        extra += f'<p class="small">Email: <a href="mailto:{e(line["email"])}">{e(line["email"])}</a></p>'
    if line.get('address'):
        extra += f'<p class="small">Address: {e(line["address"])}</p>'
    site = f'<p class="small"><a href="{e(line["website"])}" rel="noopener">Official website</a></p>' if line.get('website') else ''
    return (f'<article class="card" data-kind="{e(line["kind"])}"><h3>{e(line["name"])}</h3><p>{e(line["about"])}</p>'
            f'{numbers(line["numbers"])}{status}{hours}{extra}{site}{source_line(line)}</article>')


def country_page(data, c):
    url = BASE + c['slug'] + '.html'
    title = f'{c["name"]}: help for veterans | Veteran Resource Guide'
    desc = (f'Emergency number, official veterans agency and crisis lines in {c["name"]}, with the official source for every number. '
            f'Plus VA Foreign Medical Program and Veterans Crisis Line help for U.S. veterans living in {c["name"]}.')
    em = c['emergency']
    emergency = (f'<section id="emergency" class="emergency" aria-labelledby="em-title"><h2 id="em-title">Emergency in {e(c["name"])}</h2>'
                 f'{numbers(em["numbers"])}<p>Call for immediate danger to life.</p>{source_line(em)}</section>')
    body = ''
    for kind, heading in KINDS:
        cards = ''.join(line_card(x) for x in c['lines'] if x['kind'] == kind)
        if kind == 'veterans_line' and not cards:
            if c.get('no_veterans_line'):
                cards = '<p class="partial" data-partial>' + e(c['no_veterans_line']) + '</p>'
            else:
                cards = '<p class="full">' + e(c['veterans_line_note']) + '</p>'
        body += f'<section id="{kind.replace("_", "-")}"><h2>{heading}</h2>{cards}</section>'
    us = (f'<section id="us-veterans" class="us-block"><h2>U.S. veterans living in {e(c["name"])}</h2>'
          f'{vcl_for(data, c)}{fmp_for(data, c)}{benefits_block(data)}'
          '<p><a href="./#us-veterans-abroad">All help for U.S. veterans abroad</a></p></section>')
    hero = (f'<div class="hero"><p class="eyebrow">VETERANS OUTSIDE THE U.S.</p><h1>{e(c["name"])}</h1>'
            f'<p>Emergency, veterans and crisis contacts in {e(c["name"])}, each from an official source. Checked {when(c.get("checked_on") or data["checked_on"])}. '
            'Published numbers are not telephone-confirmed.</p></div></header>')
    return (head(title, desc, url) + hero + f'<main class="world" id="main" data-country="{e(c["slug"])}">' + emergency + body + us
            + '</main>' + footer())


def checked_range(data):
    """The dates the country pages were checked: one date, or the first and the last."""
    days = sorted({data['checked_on']} | {c['checked_on'] for c in data['countries'] if c.get('checked_on')})
    return when(days[0]) if len(days) == 1 else f'{when(days[0])} to {when(days[-1])}'


def index_page(data):
    url = BASE
    title = 'Veterans outside the U.S.: country guides | Veteran Resource Guide'
    desc = ('Emergency numbers, official veterans agencies and crisis lines in ' + str(len(data['countries'])) +
            ' countries, plus the VA Foreign Medical Program and Veterans Crisis Line numbers for U.S. veterans living abroad.')
    rows = ''.join(
        f'<tr><td><a href="{e(c["slug"])}.html">{e(c["name"])}</a></td><td>'
        + ', '.join(tel(n) for n in c['emergency']['numbers'][:2]) + '</td><td>'
        + e(next(x['name'] for x in c['lines'] if x['kind'] == 'agency')) + '</td></tr>'
        for c in data['countries'])
    countries = (f'<section id="countries"><h2>Countries covered</h2><p>{len(data["countries"])} countries so far. Each page lists the emergency number, '
                 'the official veterans agency, any veterans support line and the national crisis line, with the official page and the date we checked each number. '
                 'Where a line is not a 24-hour crisis line, the page says so.</p>'
                 f'<table><thead><tr><th>Country</th><th>Emergency</th><th>Veterans agency</th></tr></thead><tbody>{rows}</tbody></table></section>')
    a = data['us_abroad']
    vcl, fmp, uc = a['vcl'], a['fmp'], a['fmp']['us_canada']
    vcl_rows = ''.join(f'<tr><td>{e(r["label"])}</td><td>{tel(r) if r["dsn"] else e(r["display"])}'
                       + (' off base · DSN 988 on base' if r['dsn'] else '') + '</td></tr>' for r in vcl['regions'])
    notes = ''.join(f'<li>{e(n)}</li>' for n in vcl['notes'])
    fmp_rows = ''.join(f'<tr><td>{e(t["country"])}</td><td>{tel(t)}</td></tr>' for t in fmp['toll_free'])
    m = a['manila']
    us = (f'<section id="us-veterans-abroad" class="us-block"><h2>U.S. veterans living abroad</h2>'
          f'<h3>{e(vcl["name"])}</h3><table><thead><tr><th>Region</th><th>How to call</th></tr></thead><tbody>{vcl_rows}</tbody></table>'
          f'<ul>{notes}</ul><p><a href="{e(vcl["chat_url"])}" rel="noopener">Veterans Crisis Line online chat</a></p>'
          f'<p class="small source">Source: {source(vcl)}. Checked {when(vcl["checked_on"])}.</p>'
          f'<h3>{e(fmp["name"])}</h3><p>{e(fmp["covers"])}</p><p>{e(fmp["letter"])}</p><p>{e(fmp["claims"])}</p>'
          f'<p>Toll-free FMP lines from these countries ({e(fmp["hours"])}):</p>'
          f'<table><thead><tr><th>Country</th><th>FMP toll-free</th></tr></thead><tbody>{fmp_rows}</tbody></table>'
          f'<p class="small source">Sources: {source(fmp)}; <a data-source href="{e(fmp["claims_source_url"])}" rel="noopener">{e(fmp["claims_source_title"])}</a>, '
          f'page dated {when(fmp["claims_source_date"])}. Checked {when(fmp["checked_on"])}.</p>'
          f'<p>United States and Canada: {tel(uc)}. Direct: {tel({"display": uc["direct_display"], "tel": uc["direct_tel"]})}.</p>'
          f'<p class="small">{e(uc["note"])}</p><p class="small source">Source: {source(uc)}. Checked {when(uc["checked_on"])}.</p>'
          f'{benefits_block(data)}'
          f'<h3>{e(m["name"])}</h3><p>{" or ".join(tel(n) for n in m["numbers"])}. {e(m["note"])}</p>'
          f'<p class="small source">Source: {source(m)}. Checked {when(m["checked_on"])}.</p></section>')
    later = ''.join(f'<li><strong>{e(x["name"])}:</strong> {e(x["reason"])}</li>' for x in data['not_yet_covered'])
    rules = ('<section id="how-we-check"><h2>How we check</h2><p>Every number comes from a government body, a national public body, the WHO or another UN agency. '
             'A charity appears only when a government page names it, and we cite that government page. For emergency numbers we also accept the UK and '
             'Australian governments’ travel advice. We never guess a number. Each listing shows its source and the date we checked it. '
             'We did not telephone the agencies.</p>'
             f'<h3>Not yet covered</h3><ul>{later}</ul></section>')
    hero = ('<div class="hero"><p class="eyebrow">VETERANS OUTSIDE THE U.S.</p><h1>Veterans outside the United States</h1>'
            '<p>Emergency numbers, official veterans agencies and crisis lines in other countries, and the VA help U.S. veterans can use while living abroad. '
            f'Checked {checked_range(data)}.</p></div></header>')
    return head(title, desc, url) + hero + '<main class="world" id="main">' + countries + us + rules + '</main>' + footer()


def pages():
    """Published paths (world/index.html first) and the canonical address of each."""
    data = load()
    return ['world/'] + ['world/' + c['slug'] + '.html' for c in data['countries']]


def outputs():
    data = load()
    result = {'world/index.html': index_page(data)}
    for c in data['countries']:
        result['world/' + c['slug'] + '.html'] = country_page(data, c)
    return result


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text))
