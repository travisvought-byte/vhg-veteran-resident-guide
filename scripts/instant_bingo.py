"""Separate Ohio's kinds of charitable bingo, using the Attorney General's authorization report.

Type I: bingo games (sessions). Type II: instant bingo tickets or electronic instant bingo
sold during those games. Type III: instant bingo outside games. Veteran's, fraternal and
sporting organizations may sell Type III only on their own premises, to members and invited
guests (ORC 2915.13); 501(c)(3) charities sell Type III paper tickets through bars and other
businesses (ORC 2915.093). Only veteran's and fraternal organizations may run electronic
instant bingo (ORC 2915.14).

Public output: the members-and-guests page for posts and lodges. The 501(c)(3) bar locations
are not published. `python3 scripts/instant_bingo.py --prospects OUT.csv` writes the internal
partner-outreach list; it is not part of the public build.
"""
import argparse
import csv
import json
import math
from html import escape
from pathlib import Path

SOURCE = 'data/source/ohio-bingo-authorizations-2026-10-02.json'
PARTNERS = 'data/public/ohio-bingo-partners.json'
REPORT_DATE = 'October 2, 2026'
LAW_CHECKED = 'November 12, 2026'
KINDS = {'501(c)(19)': 'Veterans organization', '501(c)(8)': 'Fraternal organization',
         '501(c)(10)': 'Fraternal organization', '501(c)(7)': 'Club', '501(c)(4)': 'Organization'}
ORC_2915_13 = 'https://codes.ohio.gov/ohio-revised-code/section-2915.13'
ORC_2915_14 = 'https://codes.ohio.gov/ohio-revised-code/section-2915.14'
HB_344 = 'https://www.legislature.ohio.gov/legislation/136/hb344'


# Two source rows have no usable county; corrected from the city (report flags: unrecognized_county_in_source).
COUNTY_FIX = {('Riverside', '45431'): 'Montgomery', ('East Liverpool', '43920'): 'Columbiana'}


def _county(r):
    return r['county_normalized'] or COUNTY_FIX[(r['city'], r['zip'])]


def _norm(text):
    return ' '.join((text or '').lower().replace('.', '').replace(',', ' ').split())


def load_source(root):
    return json.loads((Path(root) / SOURCE).read_text())['records']


def load_partners(root):
    path = Path(root) / PARTNERS
    partners = json.loads(path.read_text()) if path.is_file() else []
    for p in partners:
        assert p['license_number'] and p['partner_since'][:4].isdigit(), p
    return {p['license_number']: p for p in partners}


def _types(record):
    return {a['bingo_type'] for a in record['authorizations']}


def session_extras(root):
    """Map (license, street, city) of each Type I location to what else is sold at its games."""
    extras = {}
    for r in load_source(root):
        types = _types(r)
        if 'Type I' not in types:
            continue
        sold = []
        if any(t.startswith('Type II (Paper') for t in types):
            sold.append('instant bingo tickets (pull-tabs)')
        if any(t.startswith('Type II (') and 'Electronic' in t for t in types):
            sold.append('electronic instant bingo')
        extras[(r['license_number'], _norm(r['street_address']), _norm(r['city']))] = sold
    # A license with one bingo-game location matches even when the address is written differently.
    by_license = {}
    for (lic, _, _), sold in extras.items():
        by_license.setdefault(lic, []).append(sold)
    extras.update({lic: v[0] for lic, v in by_license.items() if len(v) == 1})
    return extras


def add_session_extras(root, records):
    """Attach `also_sold` to finder records whose license and address match a Type I location."""
    extras = session_extras(root)
    for r in records:
        if not r.get('license_number') or not r.get('address'):
            continue
        parts = [p.strip() for p in r['address'].split(',')]
        key = (r['license_number'], _norm(parts[0]), _norm(parts[1])) if len(parts) >= 2 else None
        sold = extras.get(key) or extras.get(r['license_number'])
        if sold:
            r['also_sold'] = sold
    return records


def members_records(root):
    """Posts and lodges licensed for instant bingo outside games (members and invited guests)."""
    partners = load_partners(root)
    seen, rows = set(), []
    for r in load_source(root):
        if r['tax_status'] == '501(c)(3)':
            continue
        type3 = sorted(t for t in _types(r) if t.startswith('Type III'))
        if not type3:
            continue
        key = (r['license_number'], _norm(r['street_address']), _norm(r['city']))
        if key in seen:
            continue
        seen.add(key)
        days = next((a['authorized_days'] for a in r['authorizations'] if a['bingo_type'].startswith('Type III')), '')
        row = {
            'id': 'oh-instant-' + r['license_number'] + '-' + str(r['source_page']) + '-' + str(r['source_row_on_page']),
            'name': r['organization_display'],
            'kind': KINDS.get(r['tax_status'], 'Organization'),
            'license_number': r['license_number'],
            'address': f"{r['street_address']}, {r['city']}, OH {r['zip']}",
            'city': r['city'], 'zip': r['zip'], 'county': _county(r),
            'paper': any('Paper' in t for t in type3),
            'electronic': any('Electronic' in t for t in type3),
            'days': days,
            'games_too': 'Type I' in _types(r),
            'source_page': r['source_page'],
        }
        if r['license_number'] in partners:
            row['partner_since'] = partners[r['license_number']]['partner_since']
        rows.append(row)
    rows.sort(key=lambda x: (x['county'], x['city'], x['name']))
    return rows


STYLE = '''
.kinds{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:0 0 24px}
.kinds article,.rules{background:#fff;border:1px solid var(--line);border-radius:10px;padding:20px}
.kinds h2{font-size:21px;margin-top:0}.rules{margin:0 0 24px}
.filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:end;margin:8px 0 16px}
.filters label{display:block;font-weight:650;margin-bottom:4px}
.filters input,.filters select{width:100%;min-height:46px;font:inherit;padding:8px;border:1px solid #abb8b1;border-radius:6px;background:#fff}
.check{display:flex;gap:8px;align-items:center;min-height:46px}.check input{width:22px;height:22px}
.list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.list article{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px}
.list h3{margin:6px 0;font-family:Georgia,serif;color:var(--navy);font-size:20px}
.tag{display:inline-block;font-size:13px;font-weight:650;padding:2px 9px;border-radius:12px;background:#eef2f5;color:var(--navy);margin:0 6px 4px 0}
.tag.partner{background:#e6f2ea;color:#1f5a36;border:1px solid #9cc5ab}
.small{font-size:15px;color:#4a5a63}
@media(max-width:820px){.kinds,.filters,.list{grid-template-columns:1fr}}
'''


def instant_page(root, logo, email, guide, shell):
    rows = members_records(root)
    electronic = sum(r['electronic'] for r in rows)
    counties = sorted({r['county'] for r in rows})
    data = json.dumps(rows, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    options = ''.join(f'<option>{escape(c)}</option>' for c in counties)
    body = f'''<header><a class="brand" href="./"><img src="{logo}" alt="" width="48" height="48"><span>Ohio Bingo Finder</span></a>
<h1>Instant and electronic bingo at Ohio posts and lodges</h1>
<p>Ohio has three kinds of charitable bingo. This page explains them and lists the {len(rows)} veterans posts, fraternal lodges and clubs licensed to sell instant bingo to their members and guests.</p>
<p><a class="button" href="./">Find a bingo game</a></p></header>
<main>
<section class="kinds" aria-label="Kinds of bingo">
<article><h2>Bingo games</h2><p>Numbers called in a hall, played on paper or card-minders. Most games are open to the public. Find them in the <a href="./">bingo finder</a>.</p></article>
<article><h2>Instant bingo tickets</h2><p>Paper pull-tabs with a set prize structure. Sold during bingo games, and at some posts and lodges outside games.</p></article>
<article><h2>Electronic instant bingo</h2><p>The same game on a terminal. Only veterans and fraternal organizations may offer it. {electronic} locations below are licensed for it.</p></article>
</section>
<section class="rules"><h2>Who can play here</h2>
<p>Outside of bingo games, these posts and lodges may sell instant bingo only on their own premises, to their own members and invited guests, for up to 12 hours a day between 10 a.m. and 2 a.m. (<a href="{ORC_2915_13}">ORC 2915.13</a>; electronic games also follow <a href="{ORC_2915_14}">ORC 2915.14</a>). Players must be 18 or older.</p>
<p><strong>This is not a list of places open to the public.</strong> If you are a veteran or want to join a post or lodge, call or visit and ask how to become a member. Many posts welcome new members and their families.</p>
<p class="small">Charities also sell paper instant bingo tickets through bars and other businesses. Those locations are not listed here.</p>
<p class="small">Proposed changes: House Bill 344 would let 501(c)(3) charities run electronic instant bingo at bars and restaurants and allow posts and lodges to sell up to 16 hours a day starting at 8 a.m. As of {LAW_CHECKED}, it remains in the House Finance Committee and is not law (<a href="{HB_344}">bill page</a>). The 2025 state budget left the bingo hours and distribution rules unchanged.</p></section>
<section aria-labelledby="list-title"><h2 id="list-title">Licensed posts and lodges</h2>
<div class="filters"><div><label for="f-county">County</label><select id="f-county"><option value="">All counties</option>{options}</select></div>
<div><label for="f-q">Town, ZIP or name</label><input id="f-q" placeholder="Example: Marion"></div>
<div class="check"><input type="checkbox" id="f-e"><label for="f-e">Electronic instant bingo only</label></div></div>
<p id="count" role="status" aria-live="polite"></p><div class="list" id="list"></div>
<noscript><p>Turn on JavaScript to search this list.</p></noscript></section>
<section class="rules" id="partners"><h2>Community partner halls</h2>
<p>Posts and lodges must give part of their instant bingo net profit to a qualifying charity. Halls that name Veteran Home Guardians as a recipient, for any share, are Community Partners and are marked on this list and in the bingo finder. Every listing is free either way.</p>
<p><a class="button" href="partners.html#sponsors">How partnership works</a><a class="button alt" href="distributions.html">The distribution rules</a></p></section>
<p class="small">Source: Ohio Attorney General authorized bingo locations report, {REPORT_DATE}. Licensed days come from the state report and are not a schedule. Corrections: <a href="mailto:{email}?subject=Instant%20bingo%20listing">{email}</a>.</p>
</main>
<footer><p>Ohio Bingo Finder · A free community resource from Veteran Home Guardians · <a href="partners.html">Partners</a> · <a href="{guide}/">Veteran Resident Resource Guide</a></p></footer>
<script>
const ROWS={data};
const $=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]);
function card(r){{const tags=[r.kind,r.paper?'Instant bingo tickets':'',r.electronic?'Electronic instant bingo':'',r.games_too?'Also licensed for bingo games':''].filter(Boolean).map(t=>'<span class="tag">'+esc(t)+'</span>').join('');
return '<article>'+(r.partner_since?'<span class="tag partner">&#10003; Community partner since '+esc(r.partner_since.slice(0,4))+'</span>':'')+tags+'<h3>'+esc(r.name)+'</h3><p>'+esc(r.address)+'<br>'+esc(r.county)+' County</p>'+(r.days?'<p class="small">Days on the state license: '+esc(r.days)+'</p>':'')+'<p class="small">Members and invited guests, 18+. Ask here about membership.</p><p><a href="https://www.google.com/maps/search/?api=1&amp;query='+encodeURIComponent(r.address)+'" target="_blank" rel="noopener noreferrer">Directions &#8599;</a></p></article>'}}
function draw(){{const c=$('f-county').value,q=$('f-q').value.toLowerCase().trim(),e=$('f-e').checked;
const rows=ROWS.filter(r=>(!c||r.county===c)&&(!e||r.electronic)&&(!q||[r.name,r.city,r.zip,r.address].join(' ').toLowerCase().includes(q))).sort((a,b)=>(!!b.partner_since-!!a.partner_since)||0);
$('count').textContent=rows.length+(rows.length===1?' location':' locations')+(c?' in '+c+' County':'');
$('list').innerHTML=rows.map(card).join('')||'<p>No locations match. Try another county or search.</p>'}}
['f-county','f-q','f-e'].forEach(id=>$(id).addEventListener('input',draw));
const p=new URLSearchParams(location.search);if(p.get('county'))$('f-county').value=p.get('county');draw();
</script>'''
    return shell('Instant and electronic bingo at Ohio posts and lodges | Ohio Bingo Finder',
                 'The kinds of charitable bingo in Ohio, who can play, and the veterans posts and fraternal lodges licensed for instant and electronic instant bingo.',
                 'instant.html', body, STYLE)


def _miles(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def prospects(root, home_zip='43334'):
    """Every non-501(c)(3) location licensed for instant bingo (Type II or III): these organizations
    owe a charity distribution under ORC 2915.101. Internal outreach use only."""
    zips = json.loads((Path(root) / 'data/public/us-zip-centroids.json').read_text())
    home = zips.get(home_zip)
    partners = load_partners(root)
    seen, rows = set(), []
    for r in load_source(root):
        types = _types(r)
        if r['tax_status'] == '501(c)(3)' or not any(t.startswith(('Type II', 'Type III')) for t in types):
            continue
        key = (r['license_number'], _norm(r['street_address']), _norm(r['city']))
        if key in seen:
            continue
        seen.add(key)
        z = zips.get(r['zip'])
        rows.append({
            'organization': r['organization_display'], 'license': r['license_number'], 'tax_status': r['tax_status'],
            'kind': KINDS.get(r['tax_status'], 'Organization'),
            'street': r['street_address'], 'city': r['city'], 'zip': r['zip'], 'county': _county(r),
            'miles_from_' + home_zip: round(_miles(home, z)) if home and z else '',
            'bingo_games': 'yes' if 'Type I' in types else '',
            'instant_at_games': 'yes' if any(t.startswith('Type II (') for t in types) else '',
            'instant_outside_games': 'yes' if any(t.startswith('Type III') for t in types) else '',
            'electronic': 'yes' if any('Electronic' in t for t in types) else '',
            'type_iii_days': next((a['authorized_days'] for a in r['authorizations'] if a['bingo_type'].startswith('Type III')), ''),
            'partner': 'yes' if r['license_number'] in partners else '',
            'report_page': r['source_page'],
        })
    col = 'miles_from_' + home_zip
    rows.sort(key=lambda x: (x[col] if x[col] != '' else 9999, x['county'], x['organization']))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prospects', required=True, help='CSV path for the internal outreach list')
    parser.add_argument('--home-zip', default='43334')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rows = prospects(root, args.home_zip)
    with open(args.prospects, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'locations written to', args.prospects)
