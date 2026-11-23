#!/usr/bin/env python3
"""Printable resource packets: paper handouts for people who do not use the internet.

Writes the HTML print view of every packet, generated only from data (never written per county):
  flyers/packets/oh/<county>.html        Ohio county packet, letter, two pages
  flyers/packets/oh-large/<county>.html  the same contacts in large print (18 pt and larger)
  flyers/packets/states/<code>.html      a packet for every other state and D.C.
  flyers/packets/cover/<audience>.html   one-page cover sheet for the staff who hand packets out
  packets.html                           the download page (pick a county or state)

Data: prototype-data.json and data/public/ (the guide's own records), data/packets/ohio-county-sources.json
(official county lists, refreshed by scripts/import_packet_sources.py) and data/packets/packet-contacts.json.

scripts/build_public.py runs this, so the print views follow every data change. The PDFs are rendered from
these views by `node scripts/build_packets.cjs`, which only re-renders packets whose view changed; the
"Rebuild printable packets" workflow runs it on every push to main that changes a view.

Usage: python3 scripts/build_packets.py          # write the print views and packets.html
       python3 scripts/build_packets.py --check  # fail if any is out of date
       python3 scripts/build_packets.py --qr     # create any missing county QR code (needs: pip install qrcode)
"""
import html
import io
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = 'https://guide.vethomeguard.org/'
SHORT = 'guide.vethomeguard.org/'
OUT = 'flyers/packets/'
REPORT_EMAIL = 'travis@vethomeguard.org'
COVERS = ['nursing-home', 'chaplain', 'jail-library']


def esc(s):
    return html.escape(str(s), quote=True)


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def date_words(iso):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    y, m, d = (int(x) for x in iso[:10].split('-'))
    return f'{months[m - 1]} {d}, {y}'


def load(path):
    return json.loads((ROOT / path).read_text())


def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def county_url(county):
    return BASE_URL + '?county=' + county.replace(' ', '+')


class Sources:
    """Numbered source list printed at the end of each packet."""

    def __init__(self):
        self.items = []

    def add(self, publisher, title, url, when=None, who=None):
        key = (publisher, title, url)
        for item in self.items:
            if item[:3] == key:
                if when and when not in item[3]:
                    item[3].append(when)
                return
        self.items.append([publisher, title, url, [when] if when else [], who or publisher])

    def html(self, cls='sources', brief=False):
        rows = []
        if brief:  # large print: who published it and where, one line each
            seen = {}
            for publisher, title, url, when, who in self.items:
                seen.setdefault(who, re.sub(r'^https?://(www\.)?', '', url).split('/')[0])
            return f'<ul class="{cls}">' + ''.join(f'<li>{esc(p)}: {esc(u)}</li>' for p, u in seen.items()) + '</ul>'
        for publisher, title, url, when, who in self.items:
            short = re.sub(r'^https?://(www\.)?', '', url).rstrip('/')
            note = ('; ' + '; '.join(when)) if when else ''
            by = esc(publisher) + ', ' if publisher else ''
            rows.append(f'<li>{by}<i>{esc(title)}</i>. {esc(short)}{esc(note)}</li>')
        return f'<ol class="{cls}">' + ''.join(rows) + '</ol>'


def record_source(sources, r):
    when = 'reviewed ' + date_words(r['verification']['last_reviewed_on']) if r.get('verification', {}).get('last_reviewed_on') else None
    ev = (r.get('source_evidence') or [None])[0]
    if ev and ev.get('url'):
        when = when or ('reviewed ' + date_words(ev['reviewed_on']) if ev.get('reviewed_on') else None)
        sources.add(None, ev.get('title') or r['name'], ev['url'].split('#')[0], when, who=r.get('organization') or r['name'])
    else:
        sources.add(r.get('organization') or r['name'], r['name'], r['official_url'], when)


def head(title, css_prefix, large=False, extra=''):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="robots" content="noindex">'
            f'<link rel="stylesheet" href="{css_prefix}packets.css">{extra}</head>'
            f'<body class="{"large" if large else "standard"}">'
            # On screen only: print and download controls. Printing hides them.
            f'<p class="toolbar"><a href="{css_prefix}../../packets.html">All packets</a>'
            '<button type="button" onclick="print()">Print</button><a data-pdf href="#">Download PDF</a></p>'
            "<script>document.querySelector('[data-pdf]').href=location.pathname.replace(/\\.html$/,'.pdf')</script>")


def crisis(vcl, large=False):
    return ('<p class="crisis"><b>In crisis?</b> Call <b>988</b>, then press <b>1</b> (Veterans Crisis Line) '
            f'or text <b>{esc(vcl["text"])}</b>. Anyone can call 988. In danger now: <b>911</b>.</p>')


def report_box(where, large=False):
    return ('<section class="report"><h2>If a number here is wrong</h2>'
            f'<p>Please tell us so we can fix it for everyone. On the website, tap <b>Report a problem</b> next to '
            f'the listing, or email <b>{REPORT_EMAIL}</b> and name the {esc(where)}. '
            'Do not include anyone’s private or medical details.</p></section>')


def footer(reviewed):
    return ('<footer class="foot"><p>Free from <b>Veteran Home Guardians</b>, an Ohio 501(c)(3) nonprofit that visits '
            'veterans in long-term care. You may copy and share this packet. Listing an office does not mean it '
            f'endorses or partners with us. Contacts last checked against the listed sources on {date_words(reviewed)}.</p></footer>')


def contact(label, org, phone=None, lines=(), note=None, extra=''):
    out = f'<div class="contact"><p class="org">{esc(org)}</p>'
    if phone:
        out += f'<p class="phone">{esc(phone)}</p>'
    for line in lines:
        out += f'<p class="addr">{esc(line)}</p>'
    if note:
        out += f'<p class="note">{note}</p>'
    return out + extra + '</div>'


def card(title, body, cls=''):
    return f'<section class="card {cls}"><h2>{title}</h2>{body}</section>'


# ---------------------------------------------------------------- Ohio county packets

def ohio_context():
    records = {r['program_id']: r for r in load('prototype-data.json')}
    src = load('data/packets/ohio-county-sources.json')
    extra = load('data/packets/packet-contacts.json')
    return records, src, extra['contacts']


def regional(records, role, county):
    return next((r for r in records.values() if r.get('regional_role') == role and county in r.get('service_area', [])), None)


def nearest_va(src, county):
    center = src['counties'][county]['center']
    # Community Resource and Referral Centers are walk-in homeless services, not a clinic to be assigned to.
    places = sorted((f for f in src['va_facilities'] if 'Community Resource' not in f['street']),
                    key=lambda f: miles(center, (f['lat'], f['lon'])))
    clinic = places[0]
    center_place = next(f for f in places if f['kind'] == 'medical_center')
    return [clinic] if clinic is center_place else [clinic, center_place]


def ohio_county_data(county, records, src, extra):
    """Everything one county packet shows, with its sources. Shared by the regular and large-print packets."""
    c = src['counties'][county]
    s = Sources()
    S = src['sources']
    out = {'county': county, 'sources': s}
    out['cvso'] = {'org': f'{county} County Veterans Service Office', 'phone': c['cvso']['phone'], 'lines': c['cvso']['address']}
    s.add(S['cvso']['publisher'], S['cvso']['title'], S['cvso']['url'], S['cvso']['edition'] + ', read ' + date_words(src['reviewed_on']))
    out['va'] = []
    for f in nearest_va(src, county):
        kind = 'VA medical center (hospital)' if f['kind'] == 'medical_center' else 'Closest VA clinic'
        place = f['city'] + ('' if f['state'] == 'OH' else ', ' + {'WV': 'West Virginia', 'PA': 'Pennsylvania', 'MI': 'Michigan', 'IN': 'Indiana', 'KY': 'Kentucky'}.get(f['state'], f['state']))
        out['va'].append({'kind': kind, 'org': f['name'], 'phone': f['phone'], 'lines': [f['street'] + ', ' + place]})
        s.add(S['va']['publisher'], f['name'], f['url'], 'read ' + date_words(src['reviewed_on']))
    enroll = records['r02-va-health-enrollment']
    out['va_enroll'] = enroll['public_contact']['phone']
    record_source(s, enroll)
    aging = regional(records, 'aging_agency', county)
    out['aging'] = {'org': aging['organization'], 'phone': aging['public_contact']['phone']}
    record_source(s, aging)
    omb = regional(records, 'ombudsman', county)
    state_omb = records['ohio-state-ombudsman']
    out['ombudsman'] = {'org': omb['name'], 'by': omb['organization'], 'phone': omb['public_contact']['phone'],
                        'state_phone': state_omb['public_contact']['phone']}
    record_source(s, omb)
    record_source(s, state_omb)
    # Adult Protective Services: the county's own APS record where the guide has researched one, otherwise
    # the county Job and Family Services office from the ODJFS directory (county JFS offices take APS reports).
    aps = records.get(slug(county) + '-aps')
    jfs = c['jfs']
    if aps:
        out['aps'] = {'org': aps['organization'], 'phone': aps['public_contact']['phone'], 'lines': [jfs['address']]}
        record_source(s, aps)
    else:
        out['aps'] = {'org': f'{county} County Job and Family Services', 'phone': jfs['phone'], 'lines': [jfs['address']]}
    s.add(S['jfs']['publisher'], S['jfs']['title'], S['jfs']['url'], S['jfs']['edition'] + ', read ' + date_words(src['reviewed_on']))
    hotline = extra['ohio-aps-hotline']
    out['aps_hotline'] = hotline
    s.add(hotline['source']['publisher'], hotline['source']['title'], hotline['source']['url'], 'read ' + date_words(hotline['source']['reviewed_on']))
    la = src['legal_aid'][c['legal_aid']]
    phone = la['phone_lucas'] if county == 'Lucas' and la.get('phone_lucas') else la['phone']
    out['legal'] = {'org': la['name'], 'phone': phone}
    s.add(S['legal']['publisher'], S['legal']['title'], la['url'], 'read ' + date_words(src['reviewed_on']))
    pro = records['pro-seniors-legal']
    out['legal_60'] = {'org': pro['organization'], 'phone': pro['public_contact']['phone']}
    record_source(s, pro)
    more = []
    for rid, label in [('va-disability-compensation', 'VA benefits questions'),
                       ('va-housing-help', 'Veteran about to lose housing or homeless (24 hours)'),
                       ('ohio-oshiip', 'Medicare questions (OSHIIP)'),
                       ('disability-rights-ohio', 'Disability Rights Ohio'),
                       ('nara-discharge-records', 'Lost DD214 or military records'),
                       ('ohio-relay', 'Ohio Relay, for callers who are deaf or hard of hearing')]:
        r = records[rid]
        more.append((label, r['public_contact']['phone']))
        record_source(s, r)
    out['more'] = more
    vcl = extra['veterans-crisis-line']
    out['vcl'] = vcl
    s.add(vcl['source']['publisher'], vcl['source']['title'], vcl['source']['url'], 'read ' + date_words(vcl['source']['reviewed_on']))
    out['reviewed'] = src['reviewed_on']
    return out


def qr_box(src, url_text, large=False, caption='Scan for the full guide'):
    return (f'<div class="qr"><img src="{src}" alt="QR code that opens {esc(url_text)}">'
            f'<p>{esc(caption)}</p></div>')


def ohio_standard(d):
    county = d['county']
    va = ''.join(contact('', v['org'], v['phone'], v['lines'], esc(v['kind'])) for v in d['va'])
    cards = [
        card('Veterans benefits and paperwork',
             contact('', d['cvso']['org'], d['cvso']['phone'], d['cvso']['lines'],
                     'Free help applying for VA disability, pension, survivor and burial benefits. Ask about '
                     'emergency financial help for veterans and their families.'), 'first'),
        card('VA health care', va + f'<p class="note">Sign up for VA health care: <b>{esc(d["va_enroll"])}</b>. '
             'The veteran’s own VA clinic may be a different one; ask VA.</p>'),
        card('Help at home, meals and caregivers',
             contact('', d['aging']['org'], d['aging']['phone'],
                     note='Area Agency on Aging. Ask for an assessment: meals, rides, help at home, caregiver '
                          'support and help paying for care. Military service is not required.')),
        card('Problems with care in a nursing home or assisted living',
             contact('', d['ombudsman']['org'] + ' (' + d['ombudsman']['by'] + ')', d['ombudsman']['phone'],
                     note='The ombudsman works for the resident, for free. The resident decides what happens next. '
                          f'Ohio’s state ombudsman office: <b>{esc(d["ombudsman"]["state_phone"])}</b>.')),
        card('Abuse, neglect or someone taking money',
             contact('', d['aps']['org'], d['aps']['phone'], d['aps']['lines'],
                     'Ask for <b>Adult Protective Services</b>.') +
             f'<p class="note">Or call Ohio’s Adult Protective Services hotline: <b>{esc(d["aps_hotline"]["phone"])}</b> '
             f'({esc(d["aps_hotline"]["phone_words"])}). You can report without giving your name. If someone is in danger now, call 911.</p>'),
        card('Free legal help',
             contact('', d['legal']['org'], d['legal']['phone'],
                     note='For problems like eviction, benefits, debt, family and protection orders. Not for criminal cases.') +
             f'<p class="note">Age 60 or older, any income: {esc(d["legal_60"]["org"])} legal helpline <b>{esc(d["legal_60"]["phone"])}</b>.</p>'),
    ]
    more = ''.join(f'<tr><td>{esc(label)}</td><td class="num">{esc(phone)}</td></tr>' for label, phone in d['more'])
    track = ''.join('<tr><td></td><td></td><td></td></tr>' for _ in range(5))
    url = SHORT + '?county=' + county.replace(' ', '+')
    return (head(f'{county} County, Ohio: help for veterans and older adults (printable packet)', '../') +
            '<main class="sheet">'
            '<header class="band"><div class="title"><p class="badge">Free · Keep this</p>'
            f'<h1>Help for veterans and older adults</h1><p class="place">{esc(county)} County, Ohio</p>'
            '<p class="lede">The first offices to call, on paper. Asking for help costs nothing. Before you call, have the '
            'person’s name, date of birth and, for a veteran, the DD214 or service dates.</p></div>'
            + qr_box(f'../qr/oh-{slug(county)}.svg', url) +
            f'<p class="url">Online: <b>{esc(url)}</b></p></header>'
            + crisis(d['vcl']) +
            '<div class="grid">' + ''.join(cards) + '</div>'
            '<section class="more"><h2>More free help lines</h2><table>' + more + '</table></section>'
            '<section class="track"><h2>Keep track of your calls</h2><table><thead><tr><th>Date</th><th>Who I talked to</th>'
            '<th>What happens next</th></tr></thead><tbody>' + track + '</tbody></table></section>'
            + report_box(f'county ({county} County, Ohio) and the office') +
            '<section class="cite"><h2>Where this information comes from</h2>' + d['sources'].html() + '</section>'
            + footer(d['reviewed']) + '</main></body></html>\n')


def ohio_large(d):
    county = d['county']
    blocks = [
        ('Veterans benefits and paperwork', [(d['cvso']['org'], d['cvso']['phone'], d['cvso']['lines'])],
         'Free help with VA benefits for veterans and their families.'),
        ('VA health care', [(v['org'], v['phone'], v['lines'] + [v['kind']]) for v in d['va']],
         f'Sign up for VA health care: {d["va_enroll"]}'),
        ('Help at home, meals and caregivers', [(d['aging']['org'], d['aging']['phone'], [])],
         'Military service is not required.'),
        ('Problems with care in a nursing home', [(d['ombudsman']['org'], d['ombudsman']['phone'], [])],
         'The ombudsman works for the resident, for free.'),
        ('Abuse, neglect or someone taking money', [(d['aps']['org'] + ': ask for Adult Protective Services', d['aps']['phone'], []),
                                                    ('Ohio Adult Protective Services hotline', d['aps_hotline']['phone'], [])],
         'In danger now: call 911.'),
        ('Free legal help', [(d['legal']['org'], d['legal']['phone'], []),
                             (d['legal_60']['org'] + ', age 60 or older', d['legal_60']['phone'], [])],
         'Not for criminal cases.'),
    ]
    body = ''
    for title, items, note in blocks:
        body += f'<section class="block"><h2>{esc(title)}</h2>'
        for org, phone, lines in items:
            body += f'<p class="org">{esc(org)}</p><p class="phone">{esc(phone)}</p>' + ''.join(f'<p class="addr">{esc(l)}</p>' for l in lines)
        body += f'<p class="note">{esc(note)}</p></section>'
    more = ''.join(f'<p class="org">{esc(label)}</p><p class="phone">{esc(phone)}</p>' for label, phone in d['more'][:2])
    url = SHORT + '?county=' + county.replace(' ', '+')
    return (head(f'{county} County, Ohio: help for veterans and older adults (large print)', '../', large=True) +
            '<main class="sheet">'
            f'<header class="band"><p class="badge">Large print · Free</p><h1>Help for veterans and older adults</h1>'
            f'<p class="place">{esc(county)} County, Ohio</p></header>'
            + crisis(d['vcl'], large=True) + body +
            '<section class="block"><h2>More help</h2>' + more + '</section>'
            '<section class="block web">' + qr_box(f'../qr/oh-{slug(county)}.svg', url, large=True) +
            f'<p>The full guide is online at:<br><b>{esc(url)}</b></p></section>'
            + report_box(f'county ({county} County, Ohio)', large=True) +
            '<section class="cite"><h2>Where this comes from</h2><p>The regular-print packet lists every source and date.</p>'
            + d['sources'].html(brief=True) + '</section>'
            + footer(d['reviewed']) + '</main></body></html>\n')


# ---------------------------------------------------------------- state packets

STATE_ROLES = [
    ('claims', 'Veterans benefits and paperwork', ['-claims'], 'Free help applying for VA benefits. The table below lists the veterans contact for each {area}.'),
    ('va', 'VA health care', ['-vahealth-systems'], 'Ask which VA medical center or clinic serves your {area}.'),
    ('aging', 'Help at home, meals and caregivers', ['-adrc', '-aging-directory', '-options', '-aging', '-daas', '-aaad', '-doa',
                                                      '-senior-helpline', '-senior-resource-line', '-connects', '-link'],
     'Ask for an assessment: meals, rides, help at home and caregiver support. Military service is not required.'),
    ('ombudsman', 'Problems with care in a nursing home or assisted living', ['-ombudsman'],
     'The long-term care ombudsman works for the resident, for free.'),
    ('ship', 'Medicare questions', ['-ship'], 'Free, unbiased Medicare counseling.'),
    ('rights', 'Disability rights', ['-rights', '-disability-rights'], 'The state’s protection and advocacy agency.'),
]


def state_packet(state, records_fed, extra):
    progs = load(state['programs'])
    refs = load(state['referrals'])
    offices = load(state['offices'])
    s = Sources()
    code = state['code'].lower()

    def pick(suffixes):
        for suf in suffixes:
            for p in progs:
                if p['program_id'] == code + suf and (p.get('public_contact') or {}).get('phone'):
                    return p
        for suf in suffixes:
            for p in progs:
                if p['program_id'] == code + suf:
                    return p
        return None

    label = {'LA': 'Parish', 'AK': 'Borough or area', 'VA': 'County or city', 'DC': 'District'}.get(state['code'], 'County')
    cards = []
    for key, title, suffixes, note in STATE_ROLES:
        note = note.format(area=label.lower())
        p = pick(suffixes) if key != 'va' else next((x for x in progs if x.get('resource_role') == 'va_health_system'), None)
        if not p:
            continue
        phone = (p.get('public_contact') or {}).get('phone')
        web = re.sub(r'^https?://(www\.)?', '', p['official_url']).split('#')[0].rstrip('/')
        body = contact('', p.get('organization') or p['name'], phone,
                       [] if phone else ['Online: ' + web], esc(note))
        cards.append(card(esc(title), body))
        record_source(s, p)
    legal = [p for p in progs if p.get('resource_role') == 'legal_aid' and (p.get('public_contact') or {}).get('phone')][:3]
    if legal:
        body = ''.join(contact('', p.get('organization') or p['name'], p['public_contact']['phone']) for p in legal)
        cards.append(card('Free legal help', body + '<p class="note">For problems like eviction, benefits and debt. Not for criminal cases.</p>'))
        for p in legal:
            record_source(s, p)
    eld, fraud = extra['eldercare-locator'], extra['elder-fraud-hotline']
    cards.append(card('Abuse, neglect or someone taking money',
                      contact('', eld['name'], eld['phone'], note='Call or text. Ask for Adult Protective Services where the person lives.') +
                      contact('', fraud['name'], fraud['phone'], note=esc(fraud['hours']) + '.') +
                      '<p class="note">If someone is in danger now, call 911.</p>'))
    s.add(eld['source']['publisher'], eld['source']['title'], eld['source']['url'], 'read ' + date_words(eld['source']['reviewed_on']))
    more = []
    for rid, line in [('va-disability-compensation', 'VA benefits questions'),
                       ('r02-va-health-enrollment', 'Sign up for VA health care'),
                       ('va-housing-help', 'Veteran about to lose housing or homeless (24 hours)'),
                       ('nara-discharge-records', 'Lost DD214 or military records')]:
        r = records_fed[rid]
        more.append(f'<tr><td>{esc(line)}</td><td class="num">{esc(r["public_contact"]["phone"])}</td></tr>')
        record_source(s, r)
    vcl = extra['veterans-crisis-line']
    s.add(vcl['source']['publisher'], vcl['source']['title'], vcl['source']['url'], 'read ' + date_words(vcl['source']['reviewed_on']))
    # County table: veterans contact, aging agency and ombudsman for every county or equivalent.
    rows = []
    for o in sorted(offices, key=lambda o: o['county']):
        name = o['county']
        aging = [r for r in refs if r.get('regional_role') == 'aging_agency' and name in r.get('service_area', [])]
        omb = [r for r in refs if r.get('regional_role') == 'ombudsman' and name in r.get('service_area', [])]
        ph = lambda rs: ' / '.join(dict.fromkeys((r.get('public_contact') or {}).get('phone') or '' for r in rs if (r.get('public_contact') or {}).get('phone')))
        rows.append(f'<tr><th scope="row">{esc(name)}</th><td>{esc(o.get("phone") or "")}</td><td>{esc(ph(aging))}</td><td>{esc(ph(omb))}</td></tr>')
    have_omb = any('<td></td></tr>' not in r for r in rows)
    office_sources = {}
    for o in offices:
        if o.get('source_url'):
            office_sources.setdefault((o.get('source_title') or 'County veterans contacts', o['source_url']), o.get('reviewed_on'))
    for (title, url), when in list(office_sources.items())[:6]:
        s.add(state['name'] + ' veterans contacts', title, url, 'reviewed ' + date_words(when) if when else None)
    ref_sources = {}
    for r in refs:
        ev = (r.get('source_evidence') or [None])[0]
        url = (ev or {}).get('url') or r.get('official_url')
        if url:
            ref_sources.setdefault(((ev or {}).get('title') or r.get('organization') or r['name'], url.split('#')[0]),
                                   ((ev or {}).get('reviewed_on') or r.get('verification', {}).get('last_reviewed_on')))
    for (title, url), when in list(ref_sources.items())[:6]:
        s.add(state['name'] + ' aging and ombudsman contacts', title, url, 'reviewed ' + date_words(when) if when else None)
    reviewed = max([o.get('reviewed_on') or '' for o in offices] + [extra_reviewed(extra)])
    qr = '../../../' + state['qr']
    url = SHORT + state['page']
    table = ('<section class="counties"><h2>Contacts by ' + label.lower() + '</h2>'
             '<p class="note">Find the ' + label.lower() + ' where the person lives. Some veterans numbers are regional '
             'or statewide offices that serve that ' + label.lower() + '.</p>'
             '<table><thead><tr><th>' + label + '</th><th>Veterans service</th><th>Aging agency</th>'
             + ('<th>Ombudsman</th>' if have_omb else '') + '</tr></thead><tbody>'
             + ''.join(rows if have_omb else [r.replace('<td></td></tr>', '</tr>') for r in rows]) + '</tbody></table></section>')
    return (head(f'{state["name"]}: help for veterans and older adults (printable packet)', '../') +
            '<main class="sheet">'
            '<header class="band"><div class="title"><p class="badge">Free · Keep this</p>'
            f'<h1>Help for veterans and older adults</h1><p class="place">{esc(state["name"])}</p>'
            '<p class="lede">The first offices to call, on paper. Asking for help costs nothing. Before you call, have the '
            'person’s name, date of birth and, for a veteran, the DD214 or service dates.</p></div>'
            + qr_box(qr, url) + f'<p class="url">Online: <b>{esc(url)}</b></p></header>'
            + crisis(vcl) +
            '<div class="grid">' + ''.join(cards) + '</div>'
            '<section class="more"><h2>National lines for veterans</h2><table>' + ''.join(more) + '</table></section>'
            + table + report_box(f'state ({state["name"]}), the county and the office') +
            '<section class="cite"><h2>Where this information comes from</h2>' + s.html() + '</section>'
            + footer(reviewed) + '</main></body></html>\n')


def extra_reviewed(extra):
    return max(c['source']['reviewed_on'] for c in extra.values())


# ---------------------------------------------------------------- cover sheets for staff

COVER_TEXT = {
    'nursing-home': {
        'title': 'For nursing home and assisted living staff',
        'who': 'Social workers, activity directors, admissions and nursing staff',
        'steps': [
            ('Ask about military service.', 'At admission and at care conferences, ask whether the resident or a late spouse served. Survivors may qualify for help too.'),
            ('Print the packet for the resident’s county.', 'Use the county where the resident lives now. Large print is available for residents with low vision.'),
            ('Make the first call together.', 'For benefits, start with the County Veterans Service Office. It is free and can help apply for VA pension, including help paying for care.'),
            ('Write it down.', 'Use the “Keep track of your calls” box on page 2 so the next shift and the family can follow up.'),
            ('Leave copies where people look.', 'Social services office, activity room, family lounge and the admission folder.'),
        ],
        'extra': ('Residents’ rights', 'The long-term care ombudsman in the packet is independent and works for the resident. Residents and families can call without asking staff.'),
    },
    'chaplain': {
        'title': 'For chaplains and spiritual care volunteers',
        'who': 'Facility, hospice, hospital and community chaplains',
        'steps': [
            ('Ask about service as part of the person’s story.', 'Veterans and surviving spouses may qualify for benefits they have not applied for.'),
            ('At the end of life, involve the veterans office early.', 'The County Veterans Service Office can help families with burial benefits, a headstone or marker, a flag and survivor benefits.'),
            ('Listen for care concerns.', 'If the person describes a problem with their care, the ombudsman in the packet works for the resident and follows the resident’s wishes.'),
            ('Give the packet to the family as well.', 'Families often handle the calls. The packet works without a computer.'),
            ('Know the crisis line.', 'Veterans, families and friends can call 988 and press 1, or text 838255, at any hour.'),
        ],
        'extra': ('Counseling for veterans and families', 'VA Vet Centers offer counseling at no cost to eligible veterans, service members and their families: 877-927-8387.'),
    },
    'jail-library': {
        'title': 'For jail, prison and law library staff',
        'who': 'Library and law library staff, reentry coordinators, chaplains and case managers',
        'steps': [
            ('Ask people whether they served.', 'Veterans in custody can still ask the County Veterans Service Office for free help with VA claims.'),
            ('Print the packet for the person’s home county or state.', 'Ohio county packets include street addresses for writing to the veterans office and county Job and Family Services.'),
            ('Explain the 60-day rule.', None),
            ('Plan for release early.', 'VA’s Veterans Justice Outreach and Health Care for Re-entry Veterans staff work with veterans in jails, courts and prisons. Before release, ask about VA health care enrollment and housing help: 877-424-3838, 24 hours.'),
            ('Civil cases only.', 'The legal aid offices in the packet handle civil problems such as housing, benefits and family. For a criminal case, the person should ask the court or the public defender.'),
        ],
        'extra': ('Calls from inside', 'If phone access is limited, staff can help a person send a letter or arrange an approved call. The crisis line is 988, then press 1.'),
    },
}


def nowrap_phones(text):
    return re.sub(r'\b(\d{3}-\d{3}-\d{4})\b', r'<span class="nw">\1</span>', text)


def cover(variant, extra, reviewed, records):
    t = COVER_TEXT[variant]
    s = Sources()
    steps = ''
    for i, (lead, text) in enumerate(t['steps'], 1):
        if text is None:  # the incarceration rule, quoted from its regulation
            rule = extra['incarcerated-compensation-rule']
            text = rule['use'] + ' The County Veterans Service Office can help the family ask for their share.'
            s.add(rule['source']['publisher'], rule['source']['title'], rule['source']['url'], 'read ' + date_words(rule['source']['reviewed_on']))
        steps += f'<li><b>{esc(lead)}</b> {nowrap_phones(esc(text))}</li>'
    if variant == 'chaplain':
        record_source(s, records['va-vet-centers'])
    if variant == 'jail-library':
        record_source(s, records['va-housing-help'])
        vjo = extra['va-justice-outreach']
        s.add(vjo['source']['publisher'], vjo['source']['title'], vjo['source']['url'], 'read ' + date_words(vjo['source']['reviewed_on']))
    vcl = extra['veterans-crisis-line']
    s.add(vcl['source']['publisher'], vcl['source']['title'], vcl['source']['url'], 'read ' + date_words(vcl['source']['reviewed_on']))
    head_title, head_text = t['extra']
    url = SHORT + 'packets.html'
    return (head('How to use the resource packets: ' + t['title'], '../') +
            '<main class="sheet cover">'
            '<header class="band"><div class="title"><p class="badge">For staff · Free to copy</p>'
            f'<h1>How to use these resource packets</h1><p class="place">{esc(t["title"])}</p>'
            f'<p class="lede">For {esc(t["who"].lower())}.</p></div>'
            + qr_box('../qr/packets.svg', url, caption='Scan to print more') + f'<p class="url">Print more: <b>{esc(url)}</b></p></header>'
            + crisis(vcl) +
            '<div class="cols"><section><h2>What the packet is</h2>'
            '<p>A free paper list of the first offices that help veterans, surviving spouses, older adults and people with '
            'disabilities: the county veterans office, VA health care, the Area Agency on Aging, the long-term care '
            'ombudsman, Adult Protective Services, free legal help and crisis lines. It is made for people who do not use '
            'the internet or a smartphone.</p>'
            '<h2>Which packet to print</h2><ul>'
            '<li><b>Ohio:</b> one packet for each county, two pages.</li>'
            '<li><b>Large print:</b> the same Ohio county contacts in 18-point type or larger.</li>'
            '<li><b>Other states and D.C.:</b> statewide contacts plus a county-by-county table.</li></ul>'
            f'<p>Get them at <b>{esc(url)}</b>, or scan the code above.</p>'
            f'<h2>{esc(head_title)}</h2><p>{nowrap_phones(esc(head_text))}</p></section>'
            f'<section><h2>How to use it</h2><ol class="steps">{steps}</ol></section></div>'
            '<section class="privacy"><h2>Privacy</h2><p>The packet asks for nothing and records nothing. Veteran Home Guardians '
            'never sees who receives a packet. Each office explains its own rules when you call.</p></section>'
            + report_box('packet and the office') +
            '<section class="cite"><h2>Sources</h2>' + s.html() + '</section>'
            + footer(reviewed) + '</main></body></html>\n')


# ---------------------------------------------------------------- download page

def packets_page(counties, states):
    opts = ''.join(f'<option value="{slug(c)}">{esc(c)} County</option>' for c in counties)
    sopts = ''.join(f'<option value="{s["code"].lower()}">{esc(s["name"])}</option>' for s in states)
    county_list = ''.join(
        f'<li><b>{esc(c)}</b>: <a href="{OUT}oh/{slug(c)}.pdf" download>PDF</a> · '
        f'<a href="{OUT}oh-large/{slug(c)}.pdf" download>large print PDF</a> · <a href="{OUT}oh/{slug(c)}.html">print view</a></li>'
        for c in counties)
    state_list = ''.join(
        f'<li><b>{esc(s["name"])}</b>: <a href="{OUT}states/{s["code"].lower()}.pdf" download>PDF</a> · '
        f'<a href="{OUT}states/{s["code"].lower()}.html">print view</a></li>' for s in states)
    covers = ''.join(
        f'<article class="cover-card"><h3>{esc(COVER_TEXT[v]["title"])}</h3><p>{esc(COVER_TEXT[v]["who"])}.</p>'
        f'<p class="links"><a class="button" href="{OUT}cover/{v}.pdf" download>Download PDF</a> '
        f'<a href="{OUT}cover/{v}.html">Print view</a></p></article>' for v in COVERS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Printable resource packets | Veteran Resident Resource Guide</title>
<meta name="description" content="Free printable resource packets for veterans, older adults and people with disabilities: every Ohio county (regular and large print) and every other state. For people who do not use the internet.">
<link rel="canonical" href="{BASE_URL}packets.html">
<link rel="stylesheet" href="assets/family-guide.css">
<style>
.packets{{max-width:1160px;margin:auto;padding:24px}}
.pick{{background:#fff;border:1px solid var(--line);border-top:5px solid var(--gold);border-radius:8px;padding:20px 24px;margin-bottom:28px}}
.pick .links,.cover-card .links{{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-top:12px}}
.pick select{{max-width:420px}}
.covers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.cover-card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:16px 20px}}
.cover-card h3{{margin-top:0}}
details ul{{columns:2;column-gap:32px}}details li{{break-inside:avoid;margin-bottom:6px}}
.tips{{background:#eef3f0;border-radius:6px;padding:12px 20px;margin-top:22px}}
@media (max-width:640px){{details ul{{columns:1}}}}
</style>
<script src="assets/analytics.js" defer></script></head><body>
<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="flyers.html">Printable flyers</a><a href="family-guide.html">Family Guide</a></nav>
<div class="hero"><p class="eyebrow">FREE TO PRINT AND HAND OUT</p><h1>Printable resource packets</h1><p>Paper lists of the first offices to call, for people who do not use the internet: nursing home residents, older adults without a smartphone, and people in jail or prison. For social workers, activity directors, chaplains, County Veterans Service Offices, libraries and jail law libraries.</p></div></header>
<main class="packets" id="main">
<section class="pick" aria-labelledby="oh-title"><h2 id="oh-title">Ohio: pick a county</h2>
<p>Each county packet is two letter-size pages: the county veterans office, the closest VA care, the Area Agency on Aging, the long-term care ombudsman, Adult Protective Services, free legal help and crisis lines, with a QR code to the online guide.</p>
<label for="oh-county">County</label><select id="oh-county"><option value="">Choose a county</option>{opts}</select>
<p class="links" id="oh-links" hidden><a class="button" id="oh-pdf" download>Download packet (PDF)</a><a class="button secondary" id="oh-large" download>Large print (PDF)</a><a id="oh-view">Print view</a></p>
<details><summary>All Ohio county packets</summary><ul>{county_list}</ul></details></section>
<section class="pick" aria-labelledby="st-title"><h2 id="st-title">Other states and Washington, D.C.</h2>
<p>Statewide contacts on the first page, then a table with the veterans office, aging agency and ombudsman for every county.</p>
<label for="st-state">State</label><select id="st-state"><option value="">Choose a state</option>{sopts}</select>
<p class="links" id="st-links" hidden><a class="button" id="st-pdf" download>Download packet (PDF)</a><a id="st-view">Print view</a></p>
<details><summary>All state packets</summary><ul>{state_list}</ul></details></section>
<section aria-labelledby="cover-title"><h2 id="cover-title">Cover sheets for the people who hand these out</h2>
<p>One page that explains what the packet is and how to use it with a resident or someone in custody.</p>
<div class="covers">{covers}</div></section>
<section class="tips" aria-labelledby="tips-title"><h2 id="tips-title">Printing tips</h2><ul>
<li>Print at <strong>100%</strong> or <strong>Actual size</strong>. Black and white is fine.</li>
<li>County packets are two pages: print both sides of one sheet if you can.</li>
<li>A number is wrong? Use <strong>Report a problem</strong> in the guide, or email <a href="mailto:{REPORT_EMAIL}?subject=Printable%20packet%20correction">{REPORT_EMAIL}</a>. Please do not include anyone’s private details.</li>
</ul></section>
</main>
<footer class="packets"><p>Free from Veteran Home Guardians. You may print, copy and share these packets. · <a href="privacy.html">Privacy</a></p></footer>
<script>
(function(){{
  var base='{OUT}';
  function wire(sel,box,pairs){{
    var s=document.getElementById(sel),b=document.getElementById(box);
    function go(){{var v=s.value;b.hidden=!v;if(!v)return;pairs.forEach(function(p){{document.getElementById(p[0]).href=base+p[1]+v+p[2]}})}}
    s.addEventListener('change',go);go();
  }}
  wire('oh-county','oh-links',[['oh-pdf','oh/','.pdf'],['oh-large','oh-large/','.pdf'],['oh-view','oh/','.html']]);
  wire('st-state','st-links',[['st-pdf','states/','.pdf'],['st-view','states/','.html']]);
  var q=new URLSearchParams(location.search).get('county');
  if(q){{var o=document.getElementById('oh-county');o.value=q.toLowerCase().replace(/[^a-z0-9]+/g,'-');o.dispatchEvent(new Event('change'))}}
}})();
</script>
</body></html>
'''


# ---------------------------------------------------------------- outputs

def outputs():
    records, src, extra = ohio_context()
    states = json.loads((ROOT / 'states/registry.json').read_text())
    counties = list(src['counties'])
    result = {}
    for county in counties:
        qr = ROOT / OUT / 'qr' / f'oh-{slug(county)}.svg'
        if not qr.is_file():
            raise SystemExit(f'Missing {qr.relative_to(ROOT)}: run python3 scripts/build_packets.py --qr')
        d = ohio_county_data(county, records, src, extra)
        result[f'{OUT}oh/{slug(county)}.html'] = ohio_standard(d)
        d = ohio_county_data(county, records, src, extra)  # fresh source list for the large-print copy
        result[f'{OUT}oh-large/{slug(county)}.html'] = ohio_large(d)
    for state in states[1:]:
        result[f'{OUT}states/{state["code"].lower()}.html'] = state_packet(state, records, extra)
    reviewed = max(src['reviewed_on'], extra_reviewed(extra))
    for v in COVERS:
        result[f'{OUT}cover/{v}.html'] = cover(v, extra, reviewed, records)
    # Open Graph and Twitter tags so a shared link previews properly (scripts/landing.py); the text stays as written.
    import landing
    result['packets.html'] = landing.complete_social(packets_page(counties, states[1:]))
    return result


def make_qr():
    import qrcode
    import qrcode.image.svg
    src = load('data/packets/ohio-county-sources.json')
    targets = {f'oh-{slug(c)}.svg': county_url(c) for c in src['counties']}
    targets['packets.svg'] = BASE_URL + 'packets.html'
    made = []
    for name, url in targets.items():
        path = ROOT / OUT / 'qr' / name
        if path.exists():
            continue  # printed codes must keep working, so existing files are never replaced
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4,
                             image_factory=qrcode.image.svg.SvgPathImage)
        code.add_data(url)
        code.make(fit=True)
        buf = io.BytesIO()
        code.make_image().save(buf)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(buf.getvalue())
        made.append(name)
    print('Created QR codes: ' + (', '.join(made) if made else 'none needed'))


if __name__ == '__main__':
    if '--qr' in sys.argv:
        make_qr()
        sys.exit()
    drift = []
    for name, text in outputs().items():
        path = ROOT / name
        if not path.is_file() or path.read_text() != text:
            drift.append(name)
            if '--check' not in sys.argv:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    if '--check' in sys.argv:
        if drift:
            sys.exit('Packets out of date: ' + ', '.join(drift[:5]) + (' …' if len(drift) > 5 else '') + '. Run python3 scripts/build_packets.py')
        print('Printable packets are up to date.')
    else:
        print(f'Updated {len(drift)} packet files.' if drift else 'Packets already up to date.')
