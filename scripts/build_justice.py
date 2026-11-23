"""Build justice.html, "Veterans in the justice system" (guide.vethomeguard.org/justice.html).

Run by scripts/build_public.py. The canonical data is data/justice.json: VA Veterans Justice Outreach (VJO) and
Health Care for Re-entry Veterans (HCRV), veterans treatment courts, what incarceration does to VA compensation and
pension (38 CFR 3.665 and 3.666), how family members apply for an apportionment of the withheld amount, restoring
benefits after release, the DD-214 and ID, housing (SSVF and HUD-VASH), and an Ohio section. Every item names the
official page or rule it was read on; the whole page carries one checked date. Every state page of the guide links
here from its list of needs (templates/guide.html) and its header (scripts/unified_guide.py).
"""
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://guide.vethomeguard.org/justice.html'
EMAIL = 'travis@vethomeguard.org'
TITLE = 'Veterans in jail, prison or court: VA help, VA pay and family benefits'
DESC = ('A veteran arrested, jailed or coming home? VA justice and re-entry help, veterans treatment courts, '
        'what happens to VA pay, and how family can claim part of it.')


def load():
    return json.loads((ROOT / 'data/justice.json').read_text(encoding='utf-8'))


def e(text):
    return escape(text or '', quote=True)


def when(value):
    d = date.fromisoformat(value)
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


STYLE = '''<style>
.justice{max-width:900px;margin:auto;padding:22px 20px 34px}.justice section{margin-bottom:30px}
.justice h2{margin:26px 0 10px}.card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:8px;padding:16px 18px;margin:0 0 14px;overflow-wrap:anywhere}
.card h3{margin:0 0 8px}.card p{margin:8px 0}.ask{background:#e8eeea;border-radius:6px;padding:10px 12px}
.links{list-style:none;padding:0;margin:10px 0 4px}.links li{margin:6px 0}.links a{display:inline-block;min-height:32px;line-height:1.4;font-weight:650}
.phone a{font-size:20px;font-weight:700}.start{background:#fff;border:1px solid var(--line);border-left:6px solid var(--green);border-radius:8px;padding:12px 18px 12px 34px}.start li{margin:8px 0}
.source{color:#4b5a61}.ohio{background:#f0ede3;border-radius:10px;padding:4px 16px 8px}.toc{display:flex;flex-wrap:wrap;gap:6px 16px;padding:0;list-style:none}
.toc a{display:inline-block;min-height:32px}.quiet{font-size:15px;color:#4b5a61}
@media(max-width:600px){.justice{padding:16px 14px 28px}.card{padding:14px}}
</style>'''


def links(items):
    if not items:
        return ''
    return '<ul class="links">' + ''.join(f'<li><a href="{e(i["url"])}" rel="noopener">{e(i["label"])}</a></li>' for i in items) + '</ul>'


def sources(items, checked):
    parts = '; '.join(f'<a data-source href="{e(s["url"])}" rel="noopener">{e(s["title"])}</a>' for s in items)
    return f'<p class="small source">Source: {parts}. Checked {when(checked)}.</p>'


def report(title):
    subject = 'Veteran Resource Guide justice page: ' + title
    href = 'mailto:' + EMAIL + '?subject=' + subject.replace(' ', '%20').replace(':', '%3A')
    return f'<p class="small"><a href="{e(href)}">Report a problem</a> with this listing.</p>'


def card(item, checked):
    out = [f'<article class="card" id="{e(item["id"])}"><h3>{e(item["title"])}</h3>']
    out += [f'<p>{e(p)}</p>' for p in item.get('text', [])]
    if item.get('phone'):
        ph = item['phone']
        out.append(f'<p class="phone"><a href="tel:{e(ph["tel"])}">{e(ph["display"])}</a> <span class="small">{e(ph["label"])}</span></p>')
    if item.get('emails'):
        out.append('<ul class="links">' + ''.join(
            f'<li>{e(m["label"])}: <a href="mailto:{e(m["email"])}">{e(m["email"])}</a></li>' for m in item['emails']) + '</ul>')
    if item.get('ask'):
        out.append(f'<p class="ask"><strong>What to do:</strong> {e(item["ask"])}</p>')
    out.append(links(item.get('links')))
    out.append(sources(item['sources'], checked))
    out.append(report(item['title']))
    out.append('</article>')
    return ''.join(out)


def page(data):
    checked = data['checked_on']
    toc = ''.join(f'<li><a href="#{e(s["id"])}">{e(s["title"])}</a></li>' for s in data['sections'])
    toc += '<li><a href="#ohio">In Ohio</a></li>'
    start = '<ol class="start">' + ''.join(f'<li>{e(s)}</li>' for s in data['start']) + '</ol>'
    body = ''
    for s in data['sections']:
        body += f'<section id="{e(s["id"])}" aria-labelledby="{e(s["id"])}-title"><h2 id="{e(s["id"])}-title">{e(s["title"])}</h2>'
        body += ''.join(card(i, checked) for i in s['items']) + '</section>'
    oh = data['ohio']
    body += ('<section id="ohio" class="ohio" aria-labelledby="ohio-title"><h2 id="ohio-title">In Ohio</h2>'
             f'<p>{e(oh["intro"])}</p>' + ''.join(card(i, checked) for i in oh['items']) + '</section>')
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'WebPage', 'name': TITLE, 'description': DESC,
                     'url': URL, 'inLanguage': 'en', 'dateModified': checked,
                     'isPartOf': {'@type': 'WebSite', 'name': 'Veteran Resource Guide', 'url': 'https://guide.vethomeguard.org/'}},
                    ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(TITLE)} | Veteran Resource Guide</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="{e(TITLE)}"><meta property="og:description" content="{e(DESC)}"><meta property="og:url" content="{URL}"><meta property="og:type" content="website">
<meta property="og:image" content="https://guide.vethomeguard.org/assets/share-preview.png">
<link rel="stylesheet" href="assets/family-guide.css">
{STYLE}
<script type="application/ld+json">{ld}</script>
<script src="assets/analytics.js" defer></script></head><body>
<a class="skip" href="#main">Skip to the guide</a>
<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="family-guide.html">Family Guide</a><a href="world/">Veterans outside the U.S.</a><a href="flyers.html">Printable flyers</a></nav>
<div class="hero"><p class="eyebrow">Veterans in the justice system</p><h1>A veteran in jail, prison or court</h1>
<p>For the veteran and for the family: who at VA can help now, what happens to VA pay, how family can claim part of it, and what to do before and after release. Free, from official sources.</p></div></header>
<main class="justice" id="main">
<section id="start" aria-labelledby="start-title"><h2 id="start-title">Start here</h2>{start}
<nav aria-label="On this page"><ul class="toc">{toc}</ul></nav></section>
{body}
<p class="quiet">This page explains VA and Ohio rules in general. It is not legal advice and does not decide eligibility. A defense lawyer, legal aid or an accredited representative can tell you how they apply to you.</p>
<p class="quiet">Veterans Crisis Line: dial <a href="tel:988">988</a>, then press 1. In danger: <a href="tel:911">911</a>.</p>
</main>
<footer class="justice" style="margin:auto;padding:18px 24px"><p>Free from <a href="https://www.vethomeguard.org/about.html">Veteran Home Guardians</a>, an independent U.S. 501(c)(3) nonprofit (EIN 33-4637180) that visits isolated veterans and publishes free guides. Rules and contacts come from official pages, read on the date shown; phone numbers are not telephone-confirmed. Something wrong? Use "Report a problem" on the listing, or email <a href="mailto:{EMAIL}?subject=Veteran%20Resource%20Guide%20justice%20page">{EMAIL}</a>.</p>
<p><a href="./">Back to the Veteran Resource Guide</a> · <a href="privacy.html">Privacy</a></p></footer>
</body></html>
'''


def outputs():
    return {'justice.html': page(load())}


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text))
