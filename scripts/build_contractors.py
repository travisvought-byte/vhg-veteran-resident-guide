"""Build the Ohio veteran-owned contractor pages of the Veteran Resource Guide, run by scripts/build_public.py:

- contractors/index.html: veteran-owned Ohio businesses in home-repair trades, from the SBA's public VetCert
  registry (data/contractors/registry.json), by trade and area. Each is labeled as a public registry listing,
  not a VHG partner, with a free claim link and a remove link.
- contractors/fair-prices.html: what common home repairs cost (data/contractors/prices.json), the rights Ohio's
  repair and service rule gives you (OAC 109:4-3-05), red flags, Ohio trade wages by area, and where to complain.
- contractors/join.html: the rules a business agrees to for a free profile, and a signup that opens a filled-in
  email to VHG. Nothing goes live until a person has checked it and the owner has approved it.

Every price and rule names the page it was read on and the date. Ranges are what publishers printed, not quotes.
"""
import json
import math
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

from visuals import icon, stylesheet, count_bars

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guide.vethomeguard.org/'
EMAIL = 'travis@vethomeguard.org'
UP = '../'
SBA_SEARCH = 'https://search.certifications.sba.gov/'
LICENSE_LOOKUP = 'https://elicense4.com.ohio.gov/Lookup/LicenseLookup.aspx'
STATE_TIPS = ('https://dam.assets.ohio.gov/image/upload/com.ohio.gov/DICO/OCILB/OCILB_CPW_DIC_website.pdf',
              'Ohio Department of Commerce: Verifying licensed contractors and state inspectors')
TRADE_ICON = {'plumbing-hvac': 'wrench', 'electrical': 'bolt', 'roofing': 'home', 'remodeling': 'home', 'carpentry': 'wrench',
              'drywall': 'building', 'painting': 'brush', 'flooring': 'home', 'remediation': 'drop', 'general': 'building',
              'specialty': 'wrench'}
PRICE_ICON = {'wrench': 'wrench', 'bolt': 'bolt', 'fan': 'thermo', 'home': 'home', 'drop': 'drop', 'wall': 'building',
              'brush': 'brush', 'tool': 'wrench', 'gear': 'bolt', 'tree': 'tree'}


def load(name):
    return json.loads((ROOT / 'data/contractors' / name).read_text(encoding='utf-8'))


def e(text):
    return escape(str(text or ''), quote=True)


def when(value):
    d = date.fromisoformat(value)
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


def mailto(subject, body=''):
    return 'mailto:' + EMAIL + '?subject=' + quote(subject) + ('&body=' + quote(body) if body else '')


def money(n):
    if n is None:
        return ''
    return '${:,.2f}'.format(n) if n != int(n) else '${:,}'.format(int(n))


UNIT = {'per hour': ' an hour', 'per visit': ' a visit', 'per job': '', 'per sq ft': ' a square foot', 'per room': ' a room',
        'per tree': ' a tree', 'per stump': '', 'per permit': '', 'per mile': ' a mile'}


def price(job):
    unit = job['unit']
    if unit == 'times the normal rate':
        return f'{job["low"]:g} to {job["high"]:g} times the normal rate'
    tail = UNIT.get(unit, ' ' + unit)
    if job['low'] is None and job['high'] is None:
        return 'About ' + money(job['typical']) + tail
    text = money(job['low']) + ' to ' + money(job['high']) + tail
    if job.get('typical'):
        text += f' (most pay about {money(job["typical"])})'
    return text


STYLE = '''<style>
.con{max-width:1060px}.con section{margin-bottom:36px}
.box{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:8px;padding:16px 20px;margin:0 0 16px}
.box h3{margin-top:0}.steps{padding-left:24px}.steps li{margin:8px 0}
.notice{background:#eef3f0;border-left:5px solid var(--green);border-radius:6px;padding:12px 18px}
.warn{background:#fff;border-left:5px solid #a3412c;border-radius:6px;padding:12px 18px}
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:4px 18px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 18px}
.filters input{font:inherit;width:100%;min-height:48px;border:1px solid #6f8078;border-radius:5px;padding:10px 12px;margin:6px 0}
.count{font-weight:650}.biz-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.biz{background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px 16px;overflow-wrap:anywhere}
.biz h3{margin:0 0 4px;font-size:19px}.biz p{margin:6px 0}.biz dl{margin:8px 0;display:grid;grid-template-columns:max-content 1fr;gap:2px 10px}
.biz dt{font-weight:650}.biz dd{margin:0}.dba{color:#3d4f48;font-size:15px}
.mark{display:inline-flex;gap:6px;align-items:center;background:#e9f1eb;color:#20402f;border:1px solid #7f9c8b;border-radius:14px;padding:2px 10px;font-size:14px;font-weight:650}
.mark .vi{width:18px;height:18px}.biz .more{font-size:15px}.biz .more a{display:inline-block;min-height:32px}
.trade-h{display:flex;gap:10px;align-items:center}.trade-h .vi{width:30px;height:30px;color:var(--navy)}
.price-table{border-collapse:collapse;width:100%;background:#fff;font-size:16px}
.price-table th,.price-table td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.price-table caption{text-align:left;font-weight:650;padding:6px 0}.scroll{overflow-x:auto}
.rb{list-style:none;margin:0;padding:0}.rb>li{display:grid;grid-template-columns:minmax(10em,1fr) minmax(0,2fr);gap:4px 14px;align-items:center;padding:8px 0;border-top:1px solid #e3e8e5}
.rb>li:first-child{border-top:0}.rb-track{position:relative;display:block;height:22px;border:1px solid #6f8078;border-radius:3px;background:#f3f5f4}
.rb-n,.rb-a{position:absolute;top:2px;bottom:2px;display:block}.rb-n{background:#335947}
.rb-a{background:repeating-linear-gradient(45deg,#b4892c 0 4px,#fff4d8 4px 8px);border:1px solid #7a5b14}
.rb-text{grid-column:2;font-size:15px}.rb-key{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;padding:0;font-size:15px}
.rb-key span{display:inline-block;width:22px;height:14px;vertical-align:middle;margin-right:6px;border:1px solid #6f8078}
.rb-key .k-n{background:#335947}.rb-key .k-a{background:repeating-linear-gradient(45deg,#b4892c 0 4px,#fff4d8 4px 8px)}
.rules{counter-reset:r;list-style:none;padding:0}.rules>li{counter-increment:r;background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px 18px 14px 58px;margin:0 0 12px;position:relative}
.rules>li::before{content:counter(r);position:absolute;left:16px;top:14px;width:30px;height:30px;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;text-align:center;line-height:30px}
.rules h3{margin:0 0 6px}.rules ul{padding-left:20px}
form.join{background:#fff;border:1px solid var(--line);border-top:5px solid var(--gold);border-radius:8px;padding:18px 22px}
form.join input[type=text],form.join input[type=email],form.join input[type=tel],form.join input[type=url],form.join textarea{font:inherit;width:100%;min-height:48px;border:1px solid #6f8078;border-radius:5px;padding:10px 12px;margin:4px 0 10px}
form.join textarea{min-height:96px}form.join fieldset{border:1px solid var(--line);border-radius:6px;padding:8px 14px;margin:10px 0}
form.join legend{font-weight:650;padding:0 6px}.hint{font-size:15px;color:#3d4f48;margin:0 0 4px}
.claiming{background:#e9f1eb;border-radius:6px;padding:10px 14px}
.jumps{display:flex;flex-wrap:wrap;gap:4px 18px;padding:0;list-style:none}.jumps a{display:inline-block;min-height:44px;line-height:44px}
@media(forced-colors:active){.rb-n{background:CanvasText}.rb-a{background:Canvas;border:2px dashed CanvasText}.rb-key .k-n{background:CanvasText}.rb-key .k-a{background:Canvas;border:2px dashed CanvasText}}
@media print{.filters,form.join,.biz .more{display:none}}
@media(max-width:600px){.rb>li{grid-template-columns:1fr}.rb-text{grid-column:1}.biz dl{grid-template-columns:1fr}}
</style>'''


def head(title, desc, path, extra=''):
    url = BASE + (path[:-len('index.html')] if path.endswith('index.html') else path)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="website">
<meta property="og:image" content="{BASE}assets/vhg-logo.png">
<link rel="stylesheet" href="{UP}assets/family-guide.css">{stylesheet(UP)}
{STYLE}{extra}
<script src="{UP}assets/analytics.js" defer></script></head><body>
'''


def nav(eyebrow, h1, intro):
    return ('<header><nav aria-label="Main"><a href="../">Veteran Resource Guide</a><a href="./">Find a contractor</a>'
            '<a href="fair-prices.html">Fair prices</a><a href="join.html">List your business</a>'
            '<a href="../family-guide.html">Family Guide</a></nav>'
            f'<div class="hero"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(h1)}</h1><p>{intro}</p></div></header>\n')


def footer(subject):
    return (f'<footer class="con" style="margin:auto;padding:18px 24px"><p>Free from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, '
            'an Ohio nonprofit that visits veterans and publishes free guides. Listings and prices come from the public sources named on each page, '
            f'read on the dates shown. See something wrong? <a href="{e(mailto(subject))}">Email us</a> ({EMAIL}).</p>'
            '<p><a href="../">Back to the Veteran Resource Guide</a> · <a href="../privacy.html">Privacy</a></p></footer>\n</body></html>\n')


# ---------------------------------------------------------------- directory

def cert_label(certs):
    if 'SDVOSB' in certs:
        return 'SBA-certified service-disabled veteran-owned'
    return 'SBA-certified veteran-owned'


def card(r, labels, checked):
    trades = ' '.join([r['main_trade']] + r['other_trades'])
    area = r['area'] or 'none'
    out = [f'<article class="biz" id="biz-{e(r["id"])}" data-trade="{e(trades)}" data-area="{e(area)}" data-name="{e((r["name"] + " " + r["dba"] + " " + r["city"]).lower())}">',
           f'<h3>{e(r["name"])}</h3>']
    if r['dba']:
        out.append(f'<p class="dba">Also does business as {e(r["dba"])}</p>')
    out.append(f'<p><span class="mark">{icon("shield", UP)}{e(cert_label(r["certs"]))}</span></p><dl>')
    out.append(f'<dt>Main trade</dt><dd>{e(labels[r["main_trade"]])}</dd>')
    if r['other_trades']:
        out.append(f'<dt>Also registered for</dt><dd>{e(", ".join(labels[k] for k in r["other_trades"]))}</dd>')
    if r['city']:
        place = r['city'] + (f' ({r["area"]} area)' if r['area'] and r['area'] != r['city'] else '')
        out.append(f'<dt>Based in</dt><dd>{e(place)}. Ask whether they work in your town.</dd>')
    if r['phone']:
        digits = r['phone'].replace('-', '')
        out.append(f'<dt>Phone</dt><dd><a href="tel:{digits}">{e(r["phone"])}</a></dd>')
    if r['website']:
        shown = r['website'].split('://', 1)[1].rstrip('/')
        out.append(f'<dt>Website</dt><dd><a href="{e(r["website"])}" rel="noopener nofollow">{e(shown)}</a></dd>')
    out.append('<dt>License and insurance</dt><dd>Not checked by us yet</dd></dl>')
    if not r['phone'] and not r['city']:
        out.append('<p class="small">This business shares no phone or town on its SBA profile.</p>')
    updated = f' The owner last updated it {when(r["sba_updated"])}.' if r['sba_updated'] else ''
    out.append(f'<p class="small">Public listing from the SBA VetCert registry, read {when(checked)}.{updated} Not a VHG partner.</p>')
    out.append(f'<p class="more"><a href="{e(r["sba_profile"])}" rel="noopener">SBA profile</a> · '
               f'<a href="join.html?claim={e(r["id"])}#apply">Your business? Claim it free</a> · '
               f'<a href="{e(mailto("Remove contractor listing: " + r["name"], "Please remove this listing from the Veteran Resource Guide contractor directory: " + r["name"] + " (" + r["id"] + ")."))}">Ask us to remove it</a> · '
               f'<a href="{e(mailto("Contractor listing problem: " + r["name"], "Listing: " + r["name"] + " (" + r["id"] + ")" + chr(10) + "What happened or what is wrong:" + chr(10)))}">Report a problem</a></p>')
    out.append('</article>')
    return ''.join(out)


SCRIPT_DIR = '''<script>
(function(){var t=document.getElementById('f-trade'),a=document.getElementById('f-area'),q=document.getElementById('f-q'),n=document.getElementById('shown');
if(!t)return;var cards=[].slice.call(document.querySelectorAll('.biz')),groups=[].slice.call(document.querySelectorAll('.trade-group'));
var p=new URLSearchParams(location.search);if(p.get('trade'))t.value=p.get('trade');if(p.get('area'))a.value=p.get('area');
function run(){var tv=t.value,av=a.value,qv=q.value.trim().toLowerCase(),c=0;
cards.forEach(function(el){var ok=(!tv||el.dataset.trade.split(' ').indexOf(tv)>-1)&&(!av||el.dataset.area===av)&&(!qv||el.dataset.name.indexOf(qv)>-1);el.hidden=!ok;if(ok)c++});
groups.forEach(function(g){g.hidden=!g.querySelector('.biz:not([hidden])')});
n.textContent=c===1?'Showing 1 business':'Showing '+c+' businesses';
var u=new URL(location.href);u.search='';if(tv)u.searchParams.set('trade',tv);if(av)u.searchParams.set('area',av);history.replaceState(null,'',u)}
[t,a].forEach(function(el){el.addEventListener('change',run)});q.addEventListener('input',run);run()})();
</script>'''


def directory(reg):
    checked = reg['checked_on']
    labels = {t['key']: t['label'] for t in reg['trades']}
    listed = reg['listed']
    by_main = {k: [r for r in listed if r['main_trade'] == k] for k in labels}
    # Businesses with no phone or town go last in their trade.
    for k in by_main:
        by_main[k].sort(key=lambda r: (not (r['phone'] or r['city']), r['name'].lower()))
    areas = sorted({r['area'] for r in listed if r['area']})
    no_place = sum(1 for r in listed if not r['area'])
    rows = [(labels[k], len(v), '#trade-' + k, TRADE_ICON[k]) for k, v in by_main.items() if v]
    chart = count_bars(rows, 'by-trade', 'Veteran-owned businesses listed, by main trade', 'Businesses', UP)
    trade_opts = ''.join(f'<option value="{e(k)}">{e(labels[k])}</option>' for k in labels if any(k == r['main_trade'] or k in r['other_trades'] for r in listed))
    area_opts = ''.join(f'<option value="{e(a)}">{e(a)} area</option>' for a in areas) + (f'<option value="none">No town shared</option>' if no_place else '')
    groups = ''
    for k, items in by_main.items():
        if not items:
            continue
        groups += (f'<section class="trade-group" id="trade-{e(k)}" aria-labelledby="trade-{e(k)}-h"><h2 class="trade-h" id="trade-{e(k)}-h">'
                   f'{icon(TRADE_ICON[k], UP)}{e(labels[k])} <span class="small">({len(items)})</span></h2>'
                   f'<div class="biz-grid">{"".join(card(r, labels, checked) for r in items)}</div></section>')
    side = reg['side_trade_only']['count']
    src = reg['source']
    title = 'Veteran-owned contractors in Ohio: plumbers, electricians, roofers and more | Veteran Resource Guide'
    desc = (f'{len(listed)} veteran-owned Ohio businesses in home-repair trades, from the SBA VetCert registry, '
            'with fair price ranges and your rights under Ohio law. Free.')
    intro = (f'{len(listed)} veteran-owned businesses in Ohio that do plumbing, heating, electrical, roofing, remodeling and other home work. '
             'Each one is certified veteran-owned by the U.S. Small Business Administration. Free to use, free to be listed.')
    return (head(title, desc, 'contractors/index.html') + nav('Home repair help', 'Find a veteran-owned contractor in Ohio', e(intro)) +
            '<main class="con" id="main">'
            '<section id="start" aria-labelledby="start-h"><h2 id="start-h">Start here</h2><ol class="steps">'
            '<li>Pick your trade and area below, then call two or three businesses.</li>'
            '<li>On the call, ask what the trip or service fee is and what it covers. Ohio law says they must tell you at the first contact.</li>'
            '<li>Before work starts, ask for a written estimate. Under Ohio law the bill can’t go more than 10 percent over it (or $5, whichever is more) without your OK.</li>'
            '<li>Check the quote against the <a href="fair-prices.html">fair price ranges</a>.</li></ol>'
            '<p class="notice"><strong>What the listing does and doesn’t tell you.</strong> These are public registry listings, not VHG partners or endorsements. '
            'SBA has certified that each business is veteran-owned. We have not checked their work, prices, licenses or insurance yet, '
            'and many mostly do commercial or government jobs. Some “electrical” firms do data and phone wiring, not house wiring. '
            'Ask whether they take home jobs in your area. Ohio licenses only commercial electrical, HVAC, plumbing, hydronics and refrigeration contractors; '
            f'for home work, your city or county building department can tell you what registration and permits apply (<a href="{STATE_TIPS[0]}" rel="noopener">Ohio Department of Commerce</a>).</p>'
            f'{chart}</section>'
            '<section id="find" aria-labelledby="find-h"><h2 id="find-h">Find a contractor</h2>'
            '<div class="filters" role="search" aria-label="Filter the list">'
            f'<div><label for="f-trade">Trade</label><select id="f-trade"><option value="">All trades</option>{trade_opts}</select></div>'
            f'<div><label for="f-area">Area (by ZIP code)</label><select id="f-area"><option value="">All of Ohio</option>{area_opts}</select></div>'
            '<div><label for="f-q">Business name or town</label><input id="f-q" type="search" autocomplete="off"></div></div>'
            f'<p class="count" id="shown" role="status" aria-live="polite">Showing {len(listed)} businesses</p>'
            '<p class="small">A trade filter also shows businesses that list it as a second trade. Areas follow ZIP codes, so a town near a line may sit in the next area.</p></section>'
            f'{groups}'
            '<section id="more" aria-labelledby="more-h"><h2 id="more-h">More veteran-owned businesses</h2>'
            f'<p>Another {side} veteran-owned Ohio businesses list a home trade as a side line; their main work is something else. '
            f'You can search all of them on the <a href="{SBA_SEARCH}" rel="noopener">SBA Small Business Search</a>: choose Ohio, then VOSB or SDVOSB.</p>'
            '<p>Own a veteran-owned business that does home work in Ohio? <a href="join.html">List it free</a>. Profiles that join show rates, license and insurance, and follow our no-surprise pricing rules.</p></section>'
            '<section id="how" aria-labelledby="how-h"><h2 id="how-h">Where this list comes from</h2>'
            f'<p class="small">Source: <a href="{e(src["url"])}" rel="noopener">{e(src["title"])}</a>, read {when(checked)}. '
            f'Filters: {e(src["filters"])}. The main trade is the one each business lists first; “also registered for” comes from the other industry codes it lists, '
            'which are not a promise that it does that work. Towns and areas come from the address on the SBA profile. Phone numbers are as printed there and not telephone-confirmed.</p></section>'
            '</main>' + SCRIPT_DIR + footer('Veteran Resource Guide contractor directory'))


# ---------------------------------------------------------------- fair prices

def range_bars(hourly):
    top = 650
    items, rows = [], []
    for h in hourly:
        def seg(lo, hi, cls):
            left = round(100 * lo / top, 1)
            width = max(round(100 * (hi - lo) / top, 1), 1)
            return f'<span class="{cls}" style="left:{left}%;width:{width}%"></span>'
        bars = seg(h['low'], h['high'], 'rb-n')
        text = f'{money(h["low"])} to {money(h["high"])} an hour'
        after = ''
        if h.get('after_hours'):
            a = h['after_hours']
            bars += seg(a['low'], a['high'], 'rb-a')
            text += f'; after hours {money(a["low"])} to {money(a["high"])}'
            after = f'{money(a["low"])} to {money(a["high"])}'
        items.append(f'<li><strong>{e(h["trade"])}</strong><span class="rb-track" aria-hidden="true">{bars}</span>'
                     f'<span class="rb-text">{e(text)} ({e(h["source"])})</span></li>')
        rows.append(f'<tr><th scope="row">{e(h["trade"])}</th><td>{money(h["low"])} to {money(h["high"])}</td><td>{after or "Not published"}</td>'
                    f'<td><a href="{e(h["url"])}" rel="noopener">{e(h["source"])}</a></td></tr>')
    return ('<figure class="vz" aria-labelledby="hourly-cap"><figcaption id="hourly-cap"><strong>Published hourly rates, normal and after hours</strong> '
            'The bars run from $0 to $650 an hour.</figcaption>'
            '<ul class="rb-key"><li><span class="k-n" aria-hidden="true"></span>Normal hours</li><li><span class="k-a" aria-hidden="true"></span>After hours, where published</li></ul>'
            f'<ul class="rb">{"".join(items)}</ul>'
            '<details class="vz-data"><summary>Chart data</summary><div class="scroll"><table class="price-table"><caption>Published hourly rates</caption>'
            '<thead><tr><th scope="col">Trade</th><th scope="col">Normal hours</th><th scope="col">After hours</th><th scope="col">Source</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></details></figure>')


def price_section(t):
    rows = ''
    for j in t['jobs']:
        note = f'<br><span class="small">{e(j["note"])}</span>' if j.get('note') else ''
        where = 'Columbus' if j['area'] == 'Columbus' else ('Ohio' if j['area'] == 'Ohio' else 'U.S. average')
        rows += (f'<tr><th scope="row">{e(j["job"])}</th><td>{e(price(j))}{note}</td><td>{where}</td>'
                 f'<td><a href="{e(j["source"]["url"])}" rel="noopener">{e(j["source"]["publisher"])}</a></td></tr>')
    return (f'<section id="price-{e(t["key"])}" aria-labelledby="price-{e(t["key"])}-h"><h2 class="trade-h" id="price-{e(t["key"])}-h">{icon(PRICE_ICON[t["icon"]], UP)}{e(t["label"])}</h2>'
            f'<div class="scroll" role="region" aria-labelledby="price-{e(t["key"])}-h" tabindex="0"><table class="price-table"><caption>{e(t["label"])}: published price ranges</caption>'
            '<thead><tr><th scope="col">Job</th><th scope="col">Typical range</th><th scope="col">Where</th><th scope="col">Source</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')


def wages_table(w):
    areas = w['areas']
    head_row = ''.join(f'<th scope="col">{e(a)}</th>' for a in areas)
    body = ''
    for o in w['occupations']:
        cells = ''.join(f'<td>{money(o["median"][a]) if a in o["median"] else "Not published"}</td>' for a in areas)
        body += f'<tr><th scope="row"><a href="{e(o["url"])}" rel="noopener">{e(o["name"])}</a></th>{cells}</tr>'
    return ('<div class="scroll" role="region" aria-labelledby="wages-h" tabindex="0"><table class="price-table">'
            f'<caption>Median hourly pay by area, {e(w["release"])}</caption><thead><tr><th scope="col">Trade</th>{head_row}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def rights_tiles(law):
    items = [
        ('doc-check', 'Your choice of estimate', 'For a repair over $25, after meeting you in person, they must let you pick a written estimate, an oral one, or none, before work starts.'),
        ('receipt', 'No more than 10% over', 'The bill can’t go over the estimate by more than $5 or 10 percent, whichever is more, unless you OK it.'),
        ('phone', 'Fees up front', 'Trip, service and diagnostic charges must be told to you at the first contact.'),
        ('clipboard', 'An itemized bill', 'Each part and its cost, new or used, the labor charge, and who did the work.'),
    ]
    lis = ''.join(f'<li>{icon(ic, UP)}<strong>{e(h)}</strong><small>{e(m)}</small></li>' for ic, h, m in items)
    return ('<figure class="vz" aria-labelledby="rights-cap"><figcaption id="rights-cap"><strong>Your rights under Ohio law</strong> '
            f'From Ohio’s rule on repairs and services, <a href="{e(law["url"])}" rel="noopener">Ohio Administrative Code {e(law["cite"].replace("OAC ", ""))}</a>.</figcaption>'
            f'<ul class="vz-grid">{lis}</ul></figure>')


def fair_prices(prices, reg):
    checked = prices['checked_on']
    hourly = prices['hourly']
    plumber = next(h for h in hourly if h['trade'].startswith('Plumber'))
    water = next(t for t in prices['trades'] if t['key'] == 'water')
    w = {j['job']: j for j in water['jobs']}
    small = w['Small area, part of one room (Class 1)']
    base = w['Flooded basement, 500 sq ft, clean water']
    toc = ''.join(f'<li><a href="#price-{e(t["key"])}">{e(t["label"])}</a></li>' for t in prices['trades'])
    law, c = prices['law'], prices['complaint']
    title = 'What home repairs cost in Ohio: fair price ranges and your rights | Veteran Resource Guide'
    desc = ('Typical prices for plumbers, electricians, HVAC, roofing, water damage and more in Ohio, hourly rates, '
            'red flags, and your rights to an estimate under Ohio law.')
    gap = math.ceil(max(max(o['median'].values()) - min(o['median'].values()) for o in prices['wages']['occupations']))
    intro = ('What plumbers, electricians, roofers and other trades usually charge, from published cost guides, '
             'and the rights Ohio law gives you before anyone starts work. Typical ranges, not quotes.')
    return (head(title, desc, 'contractors/fair-prices.html') + nav('Fair prices', 'What home repairs should cost in Ohio', e(intro)) +
            '<main class="con" id="main">'
            f'<section id="rights" aria-labelledby="rights-h"><h2 id="rights-h">Before anyone comes to your house</h2>{rights_tiles(law)}'
            '<div class="box"><h3>Ask these on the first call</h3><ol class="steps">'
            '<li>What is your trip or service fee, and what does it cover? Many include the first hour of work.</li>'
            '<li>What is your hourly rate, and your after-hours rate?</li>'
            '<li>Is the price you’re giving me on the phone a range or a firm price?</li>'
            '<li>Will you give me a written estimate before you start?</li>'
            '<li>Are you licensed or registered here, and insured? Can I see proof?</li></ol></div></section>'
            '<section id="red-flags" aria-labelledby="flags-h"><h2 id="flags-h">Red flags</h2><div class="warn"><ul>'
            '<li>A firm price on the phone for damage nobody has seen yet.</li>'
            '<li>A trip fee you only hear about when the bill comes. Ohio law says it must be told up front.</li>'
            '<li>Travel time billed as labor on top of a trip fee that already covers it.</li>'
            '<li>An hourly rate far above the ranges below, with no reason given.</li>'
            '<li>Pressure to decide right now, or a large payment up front. The state warns about both.</li>'
            '<li>A bill well over the estimate that you never agreed to.</li></ul></div>'
            f'<p class="small">Trip fees told up front and bills over the estimate: <a href="{e(law["url"])}" rel="noopener">{e(law["cite"])}</a>. '
            f'Pressure and large payments up front: <a href="{STATE_TIPS[0]}" rel="noopener">{e(STATE_TIPS[1])}</a>.</p></section>'
            '<section id="hourly" aria-labelledby="hourly-h"><h2 id="hourly-h">Hourly rates</h2>'
            f'<p>Is $650 an hour fair for a plumber? No published rate we found goes that high. In Columbus, plumbers charge '
            f'{money(plumber["low"])} to {money(plumber["high"])} an hour in normal hours, and up to {money(plumber["after_hours"]["high"])} '
            'for holiday emergency calls (Angi).</p>'
            f'{range_bars(hourly)}'
            '<p class="small">Pay for the worker is lower than the rate a company bills: the rate also covers the truck, insurance, licenses, office and profit. '
            '<a href="#wages">What tradespeople earn in Ohio</a> is further down.</p></section>'
            '<section id="water-quote" aria-labelledby="water-quote-h"><h2 id="water-quote-h">Water damage: why nobody can price it on the phone</h2>'
            f'<p>Cleanup depends on how much is wet and what kind of water it is. A small area in part of one room runs {money(small["low"])} to {money(small["high"])} '
            f'({e(small["source"]["publisher"])}). A whole 500-square-foot basement of clean water runs {money(base["low"])} to {money(base["high"])} '
            f'({e(base["source"]["publisher"])}). So a $2,500 price can be fair for a flooded basement and far too high for a wet corner. '
            'Ask them to look first, then give a written estimate.</p></section>'
            f'<nav aria-label="Price tables"><h2>Prices by trade</h2><ul class="jumps">{toc}</ul></nav>'
            + ''.join(price_section(t) for t in prices['trades']) +
            '<section id="wages" aria-labelledby="wages-h"><h2 id="wages-h">What tradespeople earn in Ohio</h2>'
            f'<p>Median pay for workers, by area. For every trade, the highest-paid area is less than {money(gap)} an hour above the lowest, '
            'so where you live doesn’t explain a price far above the ranges.</p>'
            f'{wages_table(prices["wages"])}'
            f'<p class="small">Source: {e(prices["wages"]["source"]["title"])}. Each trade links to its page. Pay for workers, not prices to customers.</p></section>'
            '<section id="complain" aria-labelledby="complain-h"><h2 id="complain-h">If you were overcharged</h2>'
            f'<p>Ask the business for the itemized bill Ohio law requires. If you can’t settle it, file a complaint with the {e(c["agency"])}: '
            f'<a href="{e(c["form_url"])}" rel="noopener">file online</a> or call <a href="tel:{c["phone"].replace("-", "")}">{e(c["phone"])}</a> '
            f'(<a href="{e(c["url"])}" rel="noopener">Attorney General’s complaint page</a>).</p>'
            f'<p>If the business is in <a href="./">our directory</a>, tell us too: <a href="{e(mailto("Contractor complaint"))}">email us</a>. '
            'Profiles that break our rules come down.</p></section>'
            '<section id="method" aria-labelledby="method-h"><h2 id="method-h">How these ranges were put together</h2>'
            f'<p class="small">Read {when(checked)} from the cost-guide pages linked in each row (Angi, HomeGuide, HomeAdvisor, Housecall Pro, Fixr). '
            'Columbus figures are used where the publisher printed them, and U.S. averages otherwise; no publisher printed figures for other Ohio cities. '
            'Each row is one publisher’s range as printed, not a blend. We left out a few figures that looked wrong, such as an $18 outlet replacement '
            'that leaves out the service-call minimum. Prices change, and your job may differ: use these to spot a quote that is far out of line, not as a quote.</p></section>'
            '</main>' + footer('Veteran Resource Guide fair prices page'))


# ---------------------------------------------------------------- join

SCRIPT_JOIN = '''<script>
(function(){var f=document.getElementById('join-form');if(!f)return;var names=JSON.parse(document.getElementById('claim-names').textContent);
var id=new URLSearchParams(location.search).get('claim'),box=document.getElementById('claiming');
if(id&&names[id]){f.elements.business.value=names[id];f.elements.claim.value=id;box.hidden=false;document.getElementById('claim-name').textContent=names[id]}
f.addEventListener('submit',function(ev){ev.preventDefault();var el=f.elements,lines=[],t=[];
[].forEach.call(f.querySelectorAll('input[name=trade]:checked'),function(c){t.push(c.value)});
function add(label,v){lines.push(label+': '+(v||'').trim())}
add('Business name',el.business.value);if(el.claim.value)add('Claiming listing',el.claim.value);add('Owner name',el.owner.value);add('Phone',el.phone.value);
add('Email',el.email.value);add('Website',el.site.value);add('Town and ZIP',el.town.value);add('Trades',t.join(', '));add('Towns or counties served',el.serve.value);
add('How to confirm veteran ownership',(f.querySelector('input[name=proof]:checked')||{}).value);add('SBA VetCert profile link',el.vetcert.value);
add('License or registration numbers',el.license.value);add('Insurance company',el.insurer.value);add('Normal hourly rate',el.rate.value);
add('Trip or service fee and what it covers',el.trip.value);add('After-hours rate',el.after.value);lines.push('Three common jobs and price ranges:');lines.push(el.jobs.value.trim());
add('Agrees to the rules',el.agree.checked?'Yes':'No');
var body=lines.join('\\n');location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent('Contractor profile request: '+el.business.value.trim())+'&body='+encodeURIComponent(body);
document.getElementById('sent').hidden=false})})();
</script>'''


def join(reg):
    names = {r['id']: r['name'] for r in reg['listed']}
    labels = [t for t in reg['trades'] if t['key'] not in ('specialty',)]
    trade_boxes = ''.join(f'<label class="check"><input type="checkbox" name="trade" value="{e(t["label"])}"> {e(t["label"])}</label>' for t in labels)
    trade_boxes += '<label class="check"><input type="checkbox" name="trade" value="Handyman"> Handyman</label>'
    trade_boxes += '<label class="check"><input type="checkbox" name="trade" value="Other"> Other (say which in the jobs box)</label>'
    names_json = json.dumps(names, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    title = 'List your veteran-owned business free: Ohio contractor directory | Veteran Resource Guide'
    desc = ('Free profiles for veteran-owned Ohio contractors who publish their rates, show their license and insurance, '
            'and follow no-surprise pricing rules.')
    intro = ('Free profiles for veteran-owned Ohio businesses that do home work. In return you publish your rates and follow a few plain rules, '
             'so people can call you without bracing for the bill.')
    rules = [
        ('Veteran-owned, checked privately',
         '<p>At least half the business is owned and run by a veteran. Show us your SBA VetCert profile, or show us your DD-214 in a way we agree on together. '
         'We write down only that we checked it and when. We never publish your DD-214 or keep a copy.</p>'),
        ('Licensed and insured, and we show it',
         '<p>Give us your state license number if your trade needs one (Ohio licenses commercial electrical, HVAC, plumbing, hydronics and refrigeration work), '
         'any city or county registration, and your general liability insurance certificate. Your profile shows each one with the date we checked it.</p>'),
        ('Your rates, in public',
         '<p>Publish your normal hourly rate, your trip or service fee and what it covers, your after-hours rate, and price ranges for three common jobs. '
         'You set your prices, not us. Customers just see them before they call.</p>'),
        ('No surprises',
         '<ul><li>Say your trip, service or diagnostic fee on the first call. Ohio law already requires it.</li>'
         '<li>Phone prices are ranges. The firm price comes in writing after you’ve seen the job.</li>'
         '<li>Give a written estimate before work starts.</li>'
         '<li>Get the customer’s OK before the bill goes more than 10 percent (or $5) over the estimate.</li>'
         '<li>Your trip fee covers travel. Don’t bill the drive again as labor.</li>'
         '<li>Give an itemized bill: parts, new or used, labor, and who did the work.</li></ul>'),
        ('Complaints are taken seriously',
         '<p>Customers can tell us about a problem. We send it to you and ask how you made it right. Breaking these rules, or a pattern of complaints '
         'that aren’t made right, takes your profile down.</p>'),
        ('Free',
         '<p>A profile costs nothing. Businesses we list from the public SBA registry stay labeled “public registry listing” until the owner claims them and agrees to these rules.</p>'),
    ]
    rules_html = ''.join(f'<li><h3>{e(h)}</h3>{body}</li>' for h, body in rules)
    form = (f'<form class="join" id="join-form" data-to="{EMAIL}">'
            '<p id="claiming" class="claiming" hidden>You’re claiming the listing for <strong id="claim-name"></strong>. Fill in the rest and we’ll get in touch.</p>'
            '<input type="hidden" name="claim" value="">'
            '<label for="j-business">Business name</label><input id="j-business" name="business" type="text" autocomplete="organization" required>'
            '<label for="j-owner">Your name</label><input id="j-owner" name="owner" type="text" autocomplete="name" required>'
            '<label for="j-phone">Business phone</label><input id="j-phone" name="phone" type="tel" autocomplete="tel">'
            '<label for="j-email">Email</label><input id="j-email" name="email" type="email" autocomplete="email">'
            '<label for="j-site">Website (if any)</label><input id="j-site" name="site" type="url" autocomplete="url">'
            '<label for="j-town">Town and ZIP code you work from</label><input id="j-town" name="town" type="text">'
            f'<fieldset><legend>Trades</legend>{trade_boxes}</fieldset>'
            '<label for="j-serve">Towns or counties you serve</label><input id="j-serve" name="serve" type="text">'
            '<fieldset><legend>How we can confirm veteran ownership</legend>'
            '<label class="check"><input type="radio" name="proof" value="SBA VetCert profile"> My business is SBA VetCert certified</label>'
            '<label class="check"><input type="radio" name="proof" value="DD-214, arrange privately"> I’ll show my DD-214 privately (don’t send it in this form)</label></fieldset>'
            '<label for="j-vetcert">SBA VetCert profile link (if certified)</label><input id="j-vetcert" name="vetcert" type="url">'
            '<label for="j-license">License or registration numbers (state, city or county)</label><input id="j-license" name="license" type="text">'
            '<label for="j-insurer">Insurance company</label><input id="j-insurer" name="insurer" type="text">'
            '<label for="j-rate">Normal hourly rate</label><input id="j-rate" name="rate" type="text">'
            '<label for="j-trip">Trip or service fee, and what it covers</label><input id="j-trip" name="trip" type="text">'
            '<label for="j-after">After-hours rate</label><input id="j-after" name="after" type="text">'
            '<label for="j-jobs">Three common jobs and your price range for each</label><p class="hint" id="j-jobs-hint">For example: replace a toilet, $250 to $450.</p>'
            '<textarea id="j-jobs" name="jobs" aria-describedby="j-jobs-hint"></textarea>'
            '<label class="check"><input type="checkbox" name="agree" required> I’ve read the rules above and my business will follow them.</label>'
            '<p><button type="submit">Open my email to send this</button></p>'
            '<p class="small">This opens your email app with your answers filled in, addressed to us. Nothing is sent until you press Send there, and nothing goes on the site '
            f'until we’ve checked it and you’ve approved your profile. No email app? Send the same details to <a href="{e(mailto("Contractor profile request"))}">{EMAIL}</a>.</p>'
            '<p id="sent" class="notice" role="status" hidden>Your email app should open now. Press Send there to reach us.</p></form>'
            f'<script type="application/json" id="claim-names">{names_json}</script>')
    return (head(title, desc, 'contractors/join.html') + nav('For veteran-owned businesses', 'List your veteran-owned business free', e(intro)) +
            '<main class="con" id="main">'
            '<section id="how" aria-labelledby="how-h"><h2 id="how-h">How it works</h2><ol class="steps">'
            '<li>Send us the form below.</li><li>We confirm veteran ownership privately, and check your license and insurance.</li>'
            '<li>We send you your profile to approve.</li><li>It goes live in the <a href="./">directory</a>, ahead of registry-only listings.</li></ol></section>'
            f'<section id="rules" aria-labelledby="rules-h"><h2 id="rules-h">The rules</h2><ol class="rules">{rules_html}</ol></section>'
            f'<section id="apply" aria-labelledby="apply-h"><h2 id="apply-h">Ask for a free profile</h2>{form}</section>'
            '</main>' + SCRIPT_JOIN + footer('Veteran Resource Guide contractor profiles'))


def outputs():
    reg, prices = load('registry.json'), load('prices.json')
    return {'contractors/index.html': directory(reg), 'contractors/fair-prices.html': fair_prices(prices, reg),
            'contractors/join.html': join(reg)}


def pages():
    return ['contractors/', 'contractors/fair-prices.html', 'contractors/join.html']


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text))
