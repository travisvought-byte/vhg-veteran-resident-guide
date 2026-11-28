"""Build the help-at-home section of the Veteran Resource Guide, run by scripts/build_public.py (November 28, 2026).

Travis asked for help at home inside the guide, so a veteran looking for a handyman or a caregiver uses the same
guide as one looking for benefits. Three pages, from data/help-at-home/help-at-home.json:

- help-at-home/index.html: find help by kind (home repairs, accessibility changes, caregiving, yard and snow) and by
  county (Morrow and Knox first; a county added to the data shows up in the filter). Each kind shows what it usually
  costs (data/contractors/prices.json, shared with the fair-price page), which programs may pay, and the providers
  who have accepted a listing. Until the first one accepts, each kind says first providers are coming.
- help-at-home/who-pays.html: the VA programs and other help that can pay, matched to each kind of help, with the
  amounts printed on each official page and the date it was read.
- help-at-home/join.html: the one-page provider signup. It opens a filled-in email to VHG, like the contractor
  signup; nothing goes live until a person has checked it and the provider has approved the listing.

How the list works, in Travis's words: veterans vouch for the providers, people call providers directly (nobody sells
leads), published price ranges are a reference and never set anyone's prices, and feedback comes from real jobs.
"""
import json
from datetime import date
from pathlib import Path
from urllib.parse import quote

from build_contractors import STYLE, e, money, price, when
from visuals import icon, stylesheet

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guide.vethomeguard.org/'
EMAIL = 'travis@vethomeguard.org'
UP = '../'
NOOPENER = ' rel="noopener"'
PAYS = {'yes': 'Yes', 'some': 'Some', 'any': 'Cash you choose how to spend'}
EXTRA = '''<style>
.svc{background:#fff;border:1px solid var(--line);border-top:4px solid var(--navy);border-radius:8px;padding:16px 20px;margin:0 0 18px}
.svc h2{margin-top:0}.svc h3{font-size:18px;margin:16px 0 6px}.svc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:4px 26px}
.empty{background:#f8f3e6;border:1px dashed #8a6a1f;border-radius:6px;padding:10px 14px;margin:8px 0}
.pay{list-style:none;padding:0;margin:0}.pay li{margin:4px 0}.tag{display:inline-block;font-size:14px;font-weight:650;border:1px solid #6f8078;border-radius:12px;padding:0 8px;margin-left:6px;color:#20402f;background:#eef3f0}
.calls{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.calls li{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 16px}.calls strong{display:block}.calls a[href^="tel:"]{display:inline-block;min-height:44px;line-height:44px;font-weight:650}
.matrix th,.matrix td{text-align:left}.matrix td{white-space:normal}.matrix .no{color:#4d5c56}
.prog{scroll-margin-top:12px}.prog dl{display:grid;grid-template-columns:minmax(9em,max-content) 1fr;gap:6px 14px;margin:8px 0}.prog dt{font-weight:650}.prog dd{margin:0}
.from{font-size:15px;color:#3d4f48;margin:0 0 6px}.trade-h .vi{flex:none}
@media(max-width:600px){.prog dl{grid-template-columns:1fr}}
</style>'''


def load():
    data = json.loads((ROOT / 'data/help-at-home/help-at-home.json').read_text(encoding='utf-8'))
    prices = json.loads((ROOT / 'data/contractors/prices.json').read_text(encoding='utf-8'))
    return data, prices


def mailto(subject, body=''):
    return 'mailto:' + EMAIL + '?subject=' + quote(subject) + ('&body=' + quote(body) if body else '')


def head(title, desc, path):
    url = BASE + (path[:-len('index.html')] if path.endswith('index.html') else path)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="website">
<meta property="og:image" content="{BASE}assets/vhg-logo.png">
<link rel="stylesheet" href="{UP}assets/family-guide.css">{stylesheet(UP)}
{STYLE}{EXTRA}
<script src="{UP}assets/analytics.js" defer></script></head><body>
'''


def nav(eyebrow, h1, intro):
    return ('<header><nav aria-label="Main"><a href="../">Veteran Resource Guide</a><a href="./">Find help at home</a>'
            '<a href="who-pays.html">Who pays</a><a href="join.html">Providers sign up</a>'
            '<a href="../contractors/fair-prices.html">Fair prices</a></nav>'
            f'<div class="hero"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(h1)}</h1><p>{intro}</p></div></header>\n')


def footer(subject):
    return (f'<footer class="con" style="margin:auto;padding:18px 24px"><p>Free from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, '
            'an Ohio nonprofit that visits veterans and publishes free guides. Program details and prices come from the sources named on each page, '
            f'read on the dates shown. See something wrong? <a href="{e(mailto(subject))}">Email us</a> ({EMAIL}).</p>'
            '<p><a href="../">Back to the Veteran Resource Guide</a> · <a href="../privacy.html">Privacy</a></p></footer>\n</body></html>\n')


def county_words(counties):
    names = [c['name'].replace(' County', '') for c in counties]
    return (', '.join(names[:-1]) + ' and ' + names[-1] if len(names) > 1 else names[0]) + (' counties' if len(names) > 1 else ' County')


def typical(service, prices):
    """One line on what this kind of help usually costs, from the shared fair-price data."""
    key = service['price_key']
    if key.startswith('hourly:'):
        h = next(x for x in prices['hourly'] if x['trade'] == key.split(':', 1)[1])
        return f'{h["trade"]}: {money(h["low"])} to {money(h["high"])} an hour ({h["source"]})'
    trade = next(t for t in prices['trades'] if t['key'] == key)
    j = trade['jobs'][0]
    text = price(j)
    if text.endswith(')') and ' (most pay about ' in text:
        text = text[:-1].replace(' (most pay about ', ', most pay about ')
    where = 'Columbus' if j['area'] == 'Columbus' else ('Ohio' if j['area'] == 'Ohio' else 'U.S. average')
    return f'{j["job"]}: {text} ({j["source"]["publisher"]}, {where})'


def programs_for(service_key, programs):
    return [p for p in programs if service_key in p['pays']]


FEEDBACK_BODY = ('Provider:\nDate of the job:\nWhat they did:\nWhat they quoted, and what you paid:\nHow it went:\n'
                 'Your name and phone, so we can check with you (we never publish them):\n')
RECOMMEND_BODY = ('Their name or business:\nTheir phone:\nWhat kind of help (repairs, accessibility changes, caregiving, yard and snow):\n'
                  'Towns or counties they work in:\nHow you know their work (a job they did for you, or work you did together):\n'
                  'Your name and phone, so we can check with you:\nAre you a veteran?\n')


def provider_card(p, services, counties):
    """A provider who has accepted a listing. Shown only with accepted_on set; the data holds none until they accept."""
    assert p.get('accepted_on'), p.get('id')
    label = {s['key']: s['label'] for s in services}
    where = {c['key']: c['name'] for c in counties}
    out = [f'<article class="biz" id="pro-{e(p["id"])}" data-county="{e(" ".join(p["counties"]))}">', f'<h3>{e(p["name"])}</h3>']
    if p.get('veteran'):
        out.append(f'<p><span class="mark">{icon("flag", UP)}Veteran-owned</span></p>')
    out.append('<dl>')
    does = ", ".join(label[k] for k in p["services"]) + (f' ({p["trade"]})' if p.get('trade') else '')
    out.append(f'<dt>Does</dt><dd>{e(does)}</dd>')
    if p.get('contact'):
        out.append(f'<dt>Ask for</dt><dd>{e(p["contact"])}</dd>')
    out.append(f'<dt>Works in</dt><dd>{e(", ".join(where[k] for k in p["counties"]))}</dd>')
    if p.get('phone'):
        out.append(f'<dt>Phone</dt><dd><a href="tel:{e(p["phone"].replace("-", ""))}">{e(p["phone"])}</a></dd>')
    if p.get('town'):
        out.append(f'<dt>Based in</dt><dd>{e(p["town"])}</dd>')
    if p.get('rates'):
        out.append(f'<dt>Their rates</dt><dd>{e(p["rates"])}</dd>')
    if p.get('license'):
        out.append(f'<dt>License</dt><dd>{e(p["license"])}</dd>')
    if p.get('insurance'):
        out.append(f'<dt>Insurance</dt><dd>{e(p["insurance"])}</dd>')
    if p.get('va_work'):
        out.append(f'<dt>Takes VA-paid work</dt><dd>{e(p["va_work"])}</dd>')
    out.append('</dl>')
    if p.get('vouched_by'):
        out.append(f'<p class="small">Vouched for by {e(p["vouched_by"])}.</p>')
    out.append(f'<p class="small">Listed {when(p["accepted_on"])}, with their OK. They pay nothing to be listed and nothing per call.</p>')
    out.append(f'<p class="more"><a href="{e(mailto("Help at home feedback: " + p["name"], FEEDBACK_BODY.replace("Provider:", "Provider: " + p["name"])))}">Tell us how a job went</a></p>')
    out.append('</article>')
    return ''.join(out)


def how_tiles():
    items = [
        ('people', 'Veterans vouch for them', 'Every provider here is recommended by a veteran who has hired them or worked beside them, and we check with that veteran.'),
        ('phone', 'You call them directly', 'No middleman. Providers pay nothing to be listed or per call, and nobody sells your name or number.'),
        ('receipt', 'Fair-price ranges', 'Published ranges for common jobs, so you can tell when a quote is far out of line. Providers set their own prices.'),
        ('review', 'Feedback from real jobs', 'Tell us how a job went, with the date and the work done. We check it with the provider. No anonymous star ratings.'),
    ]
    lis = ''.join(f'<li>{icon(ic, UP)}<strong>{e(h)}</strong><small>{e(m)}</small></li>' for ic, h, m in items)
    return ('<figure class="vz" aria-labelledby="how-cap"><figcaption id="how-cap"><strong>How this list works</strong> '
            'Built the way a veteran would want it built, not the way lead websites work.</figcaption>'
            f'<ul class="vz-grid">{lis}</ul></figure>')


SCRIPT_FIND = '''<script>
(function(){var c=document.getElementById('f-county'),s=document.getElementById('f-service'),n=document.getElementById('shown');if(!c||!s)return;
function has(sel,v){return [].some.call(sel.options,function(o){return o.value===v})}
var p=new URLSearchParams(location.search);if(has(c,p.get('county')))c.value=p.get('county');if(has(s,p.get('service')))s.value=p.get('service');
function run(){var cv=c.value,sv=s.value;
[].forEach.call(document.querySelectorAll('[data-service]'),function(el){el.hidden=!!sv&&el.dataset.service!==sv});
[].forEach.call(document.querySelectorAll('[data-county]'),function(el){el.hidden=!!cv&&el.dataset.county.split(' ').indexOf(cv)<0});
n.textContent='Showing '+(sv?s.options[s.selectedIndex].text.toLowerCase():'every kind of help')+' in '+(cv?c.options[c.selectedIndex].text:'all counties we cover');
var u=new URL(location.href);u.search='';if(cv)u.searchParams.set('county',cv);if(sv)u.searchParams.set('service',sv);history.replaceState(null,'',u)}
c.addEventListener('change',run);s.addEventListener('change',run);run()})();
</script>'''


def service_section(s, data, prices):
    counties, programs = data['counties'], data['programs']
    pros = [p for p in data['providers'] if s['key'] in p['services']]
    examples = ''.join(f'<li>{icon("check", UP)}{e(x)}</li>' for x in s['examples'])
    pays = ''.join(f'<li><a href="who-pays.html#prog-{e(p["key"])}">{e(p["short"])}</a><span class="tag">{e(PAYS[p["pays"][s["key"]]])}</span>'
                   f' <span class="small">({e(p["from"])})</span></li>' for p in programs_for(s['key'], programs))
    if pros:
        listing = '<div class="biz-grid">' + ''.join(provider_card(p, data['services'], counties) for p in pros) + '</div>'
    else:
        listing = ''
    # Shown for every county the filter offers that has nobody yet, so a county with providers never says "coming".
    empty_in = [c['key'] for c in counties if not any(c['key'] in p['counties'] for p in pros)]
    if empty_in:
        listing += (f'<p class="empty" data-county="{e(" ".join(empty_in))}"><strong>First providers coming.</strong> '
                    f'We’re asking veterans who they trust for {e(s["label"].lower())} near them. '
                    f'<a href="{e(mailto("Help at home: I recommend a provider", RECOMMEND_BODY))}">Recommend someone good</a>, '
                    'or, if you do this work, <a href="join.html">sign up here</a>.</p>')
    also = ''.join(f'<li><a href="{e(a["href"])}"{NOOPENER if a["href"].startswith("http") else ""}>{e(a["text"])}</a></li>' for a in s['also'])
    also_html = f'<h3>More help</h3><ul>{also}</ul>' if also else ''
    k = e(s['key'])
    return (f'<section class="svc" id="svc-{k}" data-service="{k}" aria-labelledby="svc-{k}-h">'
            f'<h2 class="trade-h" id="svc-{k}-h">{icon(s["icon"], UP)}{e(s["label"])}</h2><p>{e(s["short"])}</p>'
            f'<div class="svc-grid"><div><h3>For example</h3><ul class="vz-ilist">{examples}</ul></div>'
            f'<div><h3>Who may pay</h3><ul class="pay">{pays}</ul><p class="small"><a href="who-pays.html#kind-{k}">What each one covers</a></p></div></div>'
            f'<h3>What it usually costs</h3><p>{e(typical(s, prices))}. <a href="{e(s["prices_href"])}">More price ranges</a>. '
            'A guide to spot a quote far out of line, not a price anyone has to charge.</p>'
            f'<h3>Providers</h3>{listing}{also_html}</section>')


def call_first(data):
    blocks = ''
    for c in data['counties']:
        lis = ''.join(f'<li><strong><a href="{e(x["url"])}" rel="noopener">{e(x["name"])}</a></strong>'
                      f'<a href="tel:{e(x["phone"].replace("-", ""))}">{e(x["phone"])}</a><br><span class="small">{e(x["for"])}</span></li>'
                      for x in c['call_first'])
        blocks += (f'<div data-county="{e(c["key"])}"><h3>{e(c["name"])}</h3><ul class="calls">{lis}</ul>'
                   f'<p class="small"><a href="../{e(c["page"])}">Everything else for {e(c["name"])} veterans</a></p></div>')
    line = data['caregiver_line']
    return ('<section id="call-first" aria-labelledby="call-first-h"><h2 id="call-first-h">Not sure where to start? Call one of these</h2>'
            '<p>Free, and they know what’s available where you live.</p>' + blocks +
            f'<p>Caring for a veteran at home, anywhere in the U.S.? The <a href="{e(line["url"])}" rel="noopener">{e(line["name"])}</a> is at '
            f'<a href="tel:{e(line["phone"].replace("-", ""))}">{e(line["phone"])}</a>.</p></section>')


def index(data, prices):
    counties, services = data['counties'], data['services']
    where = county_words(counties)
    county_opts = ''.join(f'<option value="{e(c["key"])}">{e(c["name"])}</option>' for c in counties)
    service_opts = ''.join(f'<option value="{e(s["key"])}">{e(s["label"])}</option>' for s in services)
    title = f'Help at home for veterans in {where}, Ohio: repairs, ramps, caregiving, yard and snow | Veteran Resource Guide'
    desc = (f'Find help at home in {where}, Ohio: repairs, accessibility changes, caregiving, and yard and snow work, '
            'with fair price ranges and the VA programs that may pay. Providers recommended by veterans. Free.')
    intro = (f'Repairs, accessibility changes, caregiving, and yard and snow work for veterans in {e(where)}, Ohio: what it usually costs, '
             '<a href="who-pays.html">who may pay for it</a>, and providers recommended by veterans, who you call directly. Free to use.')
    return (head(title, desc, 'help-at-home/index.html') + nav('Help at home', 'Find help at home', intro) +
            '<main class="con" id="main">'
            f'<section id="how" aria-labelledby="how-h"><h2 id="how-h">A different kind of list</h2>{how_tiles()}'
            '<p>Lead websites sell the same request to several businesses at once, so the price of every job carries the cost of the leads. '
            'Here, providers are people veterans already trust, and the call goes straight to them.</p></section>'
            '<section id="find" aria-labelledby="find-h"><h2 id="find-h">Find help</h2>'
            '<div class="filters" role="search" aria-label="Choose your county and the help you need">'
            f'<div><label for="f-county">County</label><select id="f-county"><option value="">All counties we cover</option>{county_opts}</select></div>'
            f'<div><label for="f-service">Kind of help</label><select id="f-service"><option value="">Every kind of help</option>{service_opts}</select></div></div>'
            f'<p class="count" id="shown" role="status" aria-live="polite">Showing every kind of help in all counties we cover</p>'
            f'<p class="small">We cover {e(where)} for now and add a county as providers there sign up.</p></section>'
            + ''.join(service_section(s, data, prices) for s in services) +
            call_first(data) +
            '<section id="feedback" aria-labelledby="feedback-h"><h2 id="feedback-h">Tell us how a job went</h2>'
            '<p>Hired someone from this page? Tell us the date, what they did, what they quoted and what you paid, and how it went. '
            'We check with the provider and ask how they made any problem right. What we can confirm goes on their listing; '
            'a pattern of problems that aren’t made right takes a listing down.</p>'
            f'<p><a class="button" href="{e(mailto("Help at home feedback", FEEDBACK_BODY))}">Email us about a job</a></p>'
            f'<p class="small">This opens your email app, addressed to us. Or write to {EMAIL}.</p></section>'
            '<section id="elsewhere" aria-labelledby="elsewhere-h"><h2 id="elsewhere-h">Somewhere else in Ohio?</h2>'
            '<p>For repairs, the <a href="../contractors/">veteran-owned contractor directory</a> covers all of Ohio. '
            'For everything else, your <a href="../counties/oh/">county veterans service office</a> is the place to start, '
            'and <a href="who-pays.html">who pays</a> applies wherever you live.</p></section>'
            '</main>' + SCRIPT_FIND + footer('Veteran Resource Guide help at home'))


def matrix(data):
    services, programs = data['services'], data['programs']
    head_row = ''.join(f'<th scope="col">{e(s["label"])}</th>' for s in services)
    rows = ''
    for p in programs:
        cells = ''
        for s in services:
            v = p['pays'].get(s['key'])
            cells += f'<td>{e(PAYS[v])}</td>' if v else '<td class="no">No</td>'
        rows += f'<tr><th scope="row"><a href="#prog-{e(p["key"])}">{e(p["short"])}</a><br><span class="small">{e(p["from"])}</span></th>{cells}</tr>'
    return ('<figure class="vz" aria-labelledby="matrix-cap"><figcaption id="matrix-cap"><strong>Which program pays for which kind of help</strong> '
            '“Some” means only certain jobs, explained below each program. “Cash you choose how to spend” is a monthly VA payment you can put toward any of it.</figcaption>'
            '<div class="scroll" role="region" aria-labelledby="matrix-cap" tabindex="0"><table class="price-table matrix">'
            f'<caption>Programs and the kinds of help they pay for</caption><thead><tr><th scope="col">Program</th>{head_row}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div></figure>')


def steps():
    items = [
        ('medical', 'Enroll in VA health care', 'HISA, home health aides, Veteran-Directed Care and respite all start with VA health care.'),
        ('chat', 'Ask your VA social worker or doctor', 'Say what’s hard at home. They decide what you qualify for.'),
        ('doc-check', 'Get the prescription or assessment', 'A HISA grant needs a VA prescription; aides and respite start with a look at what you need.'),
        ('user-plus', 'Get the work done', 'VA approves the estimate or the agency. With Veteran-Directed Care, you hire the helpers yourself.'),
    ]
    lis = ''.join(f'<li><span class="vz-badge">{icon(ic, UP)}</span><strong>{e(h)}</strong><span class="vz-more">{e(m)}</span></li>' for ic, h, m in items)
    return ('<figure class="vz" aria-labelledby="steps-cap"><figcaption id="steps-cap"><strong>Getting VA to pay for help at home</strong> '
            'The usual order for the VA health care programs.</figcaption>'
            f'<ol class="vz-flow">{lis}</ol></figure>')


KIND_TEXT = {
    'repairs': 'VA doesn’t pay for routine repairs such as a new roof or furnace. A USDA loan or grant can, if you live in a rural area and your income is low; '
               'Ohio Medicaid’s chore help covers minor repairs for people on its home care programs; and a VA pension or disability payment is yours to spend on repairs.',
    'accessibility': 'This is where VA pays the most. A HISA grant covers changes your VA doctor prescribes, and the adapted housing grants cover bigger projects '
                     'for certain severe service-connected disabilities. You can get both.',
    'caregiving': 'VA can send an aide, give you a budget to hire your own helpers (family and neighbors included), pay for a break for the caregiver, '
                  'or pay the family caregiver a monthly stipend.',
    'yard': 'No VA program pays for routine yard work. Ohio Medicaid’s chore help covers yard work that isn’t routine, including snow removal, when it keeps someone safe at home. '
            'Otherwise, Aid and Attendance or another VA payment you receive can cover a mowing or snow service.',
}


def kind_sections(data):
    out = ''
    for s in data['services']:
        lis = ''.join(f'<li><a href="#prog-{e(p["key"])}">{e(p["name"])}</a><span class="tag">{e(PAYS[p["pays"][s["key"]]])}</span></li>'
                      for p in programs_for(s['key'], data['programs']))
        k = e(s['key'])
        out += (f'<section id="kind-{k}" aria-labelledby="kind-{k}-h"><h3 class="trade-h" id="kind-{k}-h">{icon(s["icon"], UP)}{e(s["label"])}</h3>'
                f'<p>{e(KIND_TEXT[s["key"]])}</p><ul class="pay">{lis}</ul>'
                f'<p class="small"><a href="./?service={k}#svc-{k}">Find help with {e(s["label"].lower())}</a></p></section>')
    return out


def program_card(p, checked):
    rows = [('What it pays for', e(p['what']))]
    if p.get('not'):
        rows.append(('What it doesn’t', e(p['not'])))
    rows.append(('Who can get it', e(p['who'])))
    if p.get('amounts'):
        trs = ''.join(f'<tr><th scope="row">{e(a["label"])}</th><td>{money(a["amount"])}</td></tr>' for a in p['amounts'])
        rows.append(('How much', f'<div class="scroll"><table class="price-table"><caption>{e(p["amounts_caption"])}</caption>'
                                 f'<thead><tr><th scope="col">Grant</th><th scope="col">Up to</th></tr></thead><tbody>{trs}</tbody></table></div>'))
    start = e(p['start'])
    if p.get('guide_href'):
        start += f' <a href="{e(p["guide_href"])}">{e(p["guide_text"])}</a>'
    rows.append(('How to start', start))
    dl = ''.join(f'<dt>{h}</dt><dd>{v}</dd>' for h, v in rows)
    src = p['source']
    return (f'<article class="box prog" id="prog-{e(p["key"])}" aria-labelledby="prog-{e(p["key"])}-h">'
            f'<h3 class="trade-h" id="prog-{e(p["key"])}-h">{icon(p["icon"], UP)}{e(p["name"])}</h3><p class="from">From {e(p["from"])}</p><dl>{dl}</dl>'
            f'<p class="small">Source: <a href="{e(src["url"])}" rel="noopener">{e(src["title"])}</a>, read {when(checked)}.</p></article>')


def who_pays(data):
    checked = data['checked_on']
    sah = next(p for p in data['programs'] if p['key'] == 'sah')
    sah_max = money(sah['amounts'][0]['amount'])
    title = 'Who pays for help at home: VA grants, aides, caregiver pay and more | Veteran Resource Guide'
    desc = ('Which VA programs and other help pay for home repairs, accessibility changes, caregiving, and yard and snow work: '
            f'HISA, adapted housing grants up to {sah_max}, home health aides, Veteran-Directed Care, respite and more.')
    intro = ('The VA programs and other help that can pay for repairs, accessibility changes, caregiving, and yard and snow work, '
             f'matched to each kind of help. Amounts are from each official page, read {when(checked)}.')
    counties = data['counties']
    vso = ''.join(f'<li><a href="../{e(c["page"])}">{e(c["name"])} veterans service office</a>: '
                  f'<a href="tel:{e(c["call_first"][0]["phone"].replace("-", ""))}">{e(c["call_first"][0]["phone"])}</a></li>' for c in counties)
    line = data['caregiver_line']
    return (head(title, desc, 'help-at-home/who-pays.html') + nav('Help at home', 'Who pays for help at home', e(intro)) +
            '<main class="con" id="main">'
            f'<section id="glance" aria-labelledby="glance-h"><h2 id="glance-h">At a glance</h2>{matrix(data)}{steps()}</section>'
            f'<section id="by-kind" aria-labelledby="by-kind-h"><h2 id="by-kind-h">By kind of help</h2>{kind_sections(data)}</section>'
            '<section id="programs" aria-labelledby="programs-h"><h2 id="programs-h">The programs</h2>'
            + ''.join(program_card(p, checked) for p in data['programs']) +
            '<p class="small">More on home changes and VA grants, written for people with disabilities and their families: '
            '<a href="https://mobilitytalk.org/home-modifications.html" rel="noopener">Mobility Talk</a>.</p></section>'
            '<section id="paperwork" aria-labelledby="paperwork-h"><h2 id="paperwork-h">Free help with the paperwork</h2>'
            '<p>A county veterans service officer will fill out VA forms with you and file them, free. Nobody should charge you to apply for VA benefits.</p>'
            f'<ul>{vso}<li><a href="../counties/oh/">Every Ohio county veterans service office</a></li>'
            f'<li><a href="{e(line["url"])}" rel="noopener">{e(line["name"])}</a>: <a href="tel:{e(line["phone"].replace("-", ""))}">{e(line["phone"])}</a></li></ul></section>'
            '</main>' + footer('Veteran Resource Guide who pays for help at home'))


SCRIPT_JOIN = '''<script>
(function(){var f=document.getElementById('join-form');if(!f)return;
f.addEventListener('submit',function(ev){ev.preventDefault();var el=f.elements,lines=[];
function picked(name){var v=[];[].forEach.call(f.querySelectorAll('input[name='+name+']:checked'),function(c){v.push(c.value)});return v.join(', ')}
function add(label,v){lines.push(label+': '+(v||'').trim())}
add('Your name',el.owner.value);add('Business name',el.business.value);add('Phone',el.phone.value);add('Email',el.email.value);
add('Town and ZIP',el.town.value);add('Counties',[picked('county'),el.county_other.value.trim()].filter(Boolean).join(', '));
add('Kinds of help',picked('service'));add('Veteran-owned',(f.querySelector('input[name=veteran]:checked')||{}).value);
add('Veteran who vouches for you',el.voucher.value);add('Their phone',el.voucher_phone.value);add('How they know your work',el.voucher_how.value);
add('Rates',el.rates.value);add('Takes VA-paid work',picked('va'));add('License or registration numbers',el.license.value);add('Insurance',el.insurer.value);
add('Agrees to the rules',el.agree.checked?'Yes':'No');
location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent('Help at home listing request: '+(el.business.value.trim()||el.owner.value.trim()))+'&body='+encodeURIComponent(lines.join('\\n'));
document.getElementById('sent').hidden=false})})();
</script>'''


def join(data):
    counties, services = data['counties'], data['services']
    where = county_words(counties)
    county_boxes = ''.join(f'<label class="check"><input type="checkbox" name="county" value="{e(c["name"])}"> {e(c["name"])}</label>' for c in counties)
    service_boxes = ''.join(f'<label class="check"><input type="checkbox" name="service" value="{e(s["label"])}"> {e(s["label"])}</label>' for s in services)
    va_boxes = ''.join(f'<label class="check"><input type="checkbox" name="va" value="{e(v)}"> {e(v)}</label>' for v in
                       ['Accessibility jobs paid by a VA HISA or adapted housing grant', 'Work as a VA-approved home care agency',
                        'Being hired by a veteran on Veteran-Directed Care', 'Ohio Medicaid chore work (approved provider)'])
    title = 'Providers: sign up for a free help-at-home listing | Veteran Resource Guide'
    desc = (f'A free listing for people and businesses who help veterans at home in {where}, Ohio: repairs, accessibility changes, '
            'caregiving, and yard and snow work. A veteran vouches for you; customers call you directly.')
    intro = (f'A free listing for people and businesses who help veterans at home in {e(where)}: repairs, accessibility changes, caregiving, '
             'and yard and snow work. A veteran vouches for you, customers call you directly, and you never pay for a lead.')
    rules = [
        ('A veteran vouches for you',
         '<p>Name a veteran who has hired you or worked beside you. We call them to hear about your work before anything goes up. '
         'You don’t have to be a veteran yourself; if your business is veteran-owned, your listing says so.</p>'),
        ('Direct contact, never lead fees',
         '<p>Customers call you. The listing is free, there is no fee per call or per job, and we never sell or share anyone’s name or number.</p>'),
        ('Your rates, in public',
         '<p>Publish your normal rate, any trip or service fee and what it covers, and price ranges for two or three common jobs. '
         'You set your prices, not us. Our <a href="../contractors/fair-prices.html">fair-price ranges</a> are a reference for customers, not a cap.</p>'),
        ('No surprises',
         '<ul><li>Say what you charge before you start, including any trip fee. For repairs, Ohio law already requires it.</li>'
         '<li>For repair and remodeling work, give a written estimate before you start, and get the customer’s OK before the bill goes more than 10 percent (or $5) over it.</li>'
         '<li>Give an itemized bill or receipt.</li><li>Only take work you’re trained, licensed and insured to do.</li></ul>'),
        ('Feedback from real jobs',
         '<p>Customers tell us how a job went, with the date and the work done. We send it to you and ask how you made any problem right. '
         'What we can confirm goes on your listing. A pattern of problems that aren’t made right takes it down.</p>'),
        ('Licensed and insured where the work needs it',
         '<p>Give us any state license or city or county registration your work needs, and your insurance. Your listing shows what we checked and when.</p>'),
    ]
    rules_html = ''.join(f'<li><h3>{e(h)}</h3>{body}</li>' for h, body in rules)
    form = (f'<form class="join" id="join-form" data-to="{EMAIL}">'
            '<label for="h-owner">Your name</label><input id="h-owner" name="owner" type="text" autocomplete="name" required>'
            '<label for="h-business">Business name (if you have one)</label><input id="h-business" name="business" type="text" autocomplete="organization">'
            '<label for="h-phone">Phone customers should call</label><input id="h-phone" name="phone" type="tel" autocomplete="tel" required>'
            '<label for="h-email">Email</label><input id="h-email" name="email" type="email" autocomplete="email">'
            '<label for="h-town">Town and ZIP code you work from</label><input id="h-town" name="town" type="text">'
            f'<fieldset><legend>Counties you work in</legend>{county_boxes}'
            '<label for="h-county-other">Other counties</label><input id="h-county-other" name="county_other" type="text"></fieldset>'
            f'<fieldset><legend>Kinds of help you offer</legend>{service_boxes}</fieldset>'
            '<fieldset><legend>Is your business veteran-owned?</legend>'
            '<label class="check"><input type="radio" name="veteran" value="Yes"> Yes</label>'
            '<label class="check"><input type="radio" name="veteran" value="No"> No</label></fieldset>'
            '<label for="h-voucher">A veteran who can vouch for your work</label><input id="h-voucher" name="voucher" type="text" required>'
            '<label for="h-voucher-phone">Their phone</label><input id="h-voucher-phone" name="voucher_phone" type="tel">'
            '<label for="h-voucher-how">How they know your work</label><input id="h-voucher-how" name="voucher_how" type="text">'
            '<label for="h-rates">Your rates</label><p class="hint" id="h-rates-hint">Your normal rate, any trip fee, and two or three common jobs with a price range. '
            'For example: mowing a quarter acre, $35 to $50.</p><textarea id="h-rates" name="rates" aria-describedby="h-rates-hint"></textarea>'
            f'<fieldset><legend>Work paid by a program (if you take it)</legend>{va_boxes}</fieldset>'
            '<label for="h-license">License or registration numbers, if your work needs them</label><input id="h-license" name="license" type="text">'
            '<label for="h-insurer">Insurance company</label><input id="h-insurer" name="insurer" type="text">'
            '<label class="check"><input type="checkbox" name="agree" required> I’ve read the rules above and will follow them.</label>'
            '<p><button type="submit">Open my email to send this</button></p>'
            '<p class="small">This opens your email app with your answers filled in, addressed to us. Nothing is sent until you press Send there, and nothing goes on the site '
            f'until we’ve talked with the veteran who vouched for you and you’ve approved your listing. No email app? Send the same details to '
            f'<a href="{e(mailto("Help at home listing request"))}">{EMAIL}</a>.</p>'
            '<p id="sent" class="notice" role="status" hidden>Your email app should open now. Press Send there to reach us.</p></form>')
    return (head(title, desc, 'help-at-home/join.html') + nav('For providers', 'Providers sign up here', intro) +
            '<main class="con" id="main">'
            '<section id="steps" aria-labelledby="steps-h"><h2 id="steps-h">How it works</h2><ol class="steps">'
            '<li>Send us the form below.</li><li>We call the veteran who vouched for you, and check any license and insurance.</li>'
            '<li>We send you your listing to approve.</li><li>It goes live on <a href="./">Find help at home</a>. Nothing goes up before you approve it.</li></ol>'
            '<p>Repair contractor anywhere in Ohio? The <a href="../contractors/join.html">veteran-owned contractor directory</a> lists you statewide, too.</p></section>'
            f'<section id="rules" aria-labelledby="rules-h"><h2 id="rules-h">The rules</h2><ol class="rules">{rules_html}</ol></section>'
            f'<section id="apply" aria-labelledby="apply-h"><h2 id="apply-h">Ask for a free listing</h2>{form}</section>'
            '<section id="recommend" aria-labelledby="recommend-h"><h2 id="recommend-h">Know someone good?</h2>'
            '<p>A veteran who knows a provider worth listing can tell us about them, and we’ll ask whether they want to join. '
            f'<a href="{e(mailto("Help at home: I recommend a provider", RECOMMEND_BODY))}">Recommend a provider</a>.</p></section>'
            '</main>' + SCRIPT_JOIN + footer('Veteran Resource Guide help-at-home listings'))


def county_blocks():
    """A short section on each covered county's veterans office page, linking to help at home filtered to that county."""
    data, _ = load()
    out = {}
    for c in data['counties']:
        out[c['page']] = (f'<section aria-labelledby="home-help"><h2 id="home-help">Help at home in {e(c["name"])}</h2>'
                          '<p>Repairs, accessibility changes, caregiving, and yard and snow work: what it usually costs, which VA programs may pay, '
                          'and providers recommended by local veterans.</p>'
                          f'<p><a class="button" href="../../help-at-home/?county={e(c["key"])}#find">Find help at home in {e(c["name"])}</a> '
                          '<a href="../../help-at-home/who-pays.html">Who pays for it</a></p></section>')
    return out


def outputs():
    data, prices = load()
    assert date.fromisoformat(data['checked_on'])
    return {'help-at-home/index.html': index(data, prices), 'help-at-home/who-pays.html': who_pays(data),
            'help-at-home/join.html': join(data)}


def pages():
    return ['help-at-home/', 'help-at-home/who-pays.html', 'help-at-home/join.html']


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text))
