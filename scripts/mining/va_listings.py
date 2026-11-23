"""Turn a VA Facilities API snapshot into published per-state listings of VA locations.

    python3 scripts/mining/va_listings.py --snapshot PATH --states AZ,MA,WY
    python3 scripts/mining/va_listings.py --snapshot PATH --states all

The snapshot comes from the monthly mining run (fetch_open_data.py, source va-facilities-api), which pushes it to a
mining/run-<date> review branch. Fetch that branch and pass the snapshot file. Each chosen state is written to
data/public/va-facilities/<st>.json, which scripts/build_va_pages.py turns into va-locations/<st>/index.html.

What goes in:
  - every VA medical center, clinic, Vet Center, benefits office and cemetery whose street address is in the state
  - left out: facilities VA marks CLOSED or TEMPORARY_CLOSURE, and any row without a U.S. phone (overseas sites)
  - a website is linked only when it is https; otherwise the row cites VA's facility locator
  - other VA notices (limited services, temporary location, notice) are kept and shown, with "call first"

Dedupe: rows are unique by VA facility id, and a second row with the same name, street address and phone is dropped.
A row whose phone already appears in the state's published guide records is kept (these are separate pages) and
marked `also_in_guide`, so a reviewer can see the overlap.

Each row carries its source (the facility's own VA page when VA gives one), the date retrieved, the environment that
answered (sandbox or production) and evidence level B (an official dataset read in full).
"""
import argparse
import re
import sys

import common as c

OUT = c.ROOT / 'data' / 'public' / 'va-facilities'
LEFT_OUT = {'CLOSED', 'TEMPORARY_CLOSURE'}
KINDS = {'va_health_facility': 'health', 'vet_center': 'vet_center', 'va_benefits_facility': 'benefits',
         'va_cemetery': 'cemetery'}
NOTICES = {
    'LIMITED': 'VA lists limited services here. Call before you go.',
    'NOTICE': 'VA has posted a notice for this location. Call before you go.',
    'TEMPORARY_LOCATION': 'VA says this location is operating from a temporary site. Call before you go.',
    'VIRTUAL_CARE': 'VA lists this as virtual care. Call to set up a visit.',
    'COMING_SOON': 'VA lists this location as coming soon. Call before you go.',
}
LOCATOR = 'https://www.va.gov/find-locations/'
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def clock(text):
    """'700AM-430PM' -> '7:00 AM-4:30 PM'; anything else is kept as VA wrote it."""
    return re.sub(r'\b(\d{1,2})(\d{2})\s?(AM|PM)\b', lambda m: f'{int(m[1])}:{m[2]} {m[3]}', text, flags=re.I)


def main_number(phone):
    """The main number without an extension or a second line: '843-228-5642/5470' -> '843-228-5642'."""
    return re.split(r'\s*(?:x|ext|/)', phone or '', flags=re.I)[0]


def hours_text(hours):
    """Collapse VA's day-by-day hours into a short line: 'Mon-Fri 800AM-430PM; Sat-Sun Closed'."""
    if not isinstance(hours, dict):
        return ''
    vals = [(d, clock((hours.get(d) or '').strip())) for d in DAYS]
    if not any(v for _, v in vals):
        return ''
    groups = []
    for d, v in vals:
        if groups and groups[-1][2] == v:
            groups[-1][1] = d
        else:
            groups.append([d, d, v])
    return '; '.join((a[:3].title() if a == b else f'{a[:3].title()}-{b[:3].title()}') + ' ' + (v or 'not listed')
                     for a, b, v in groups)


def published_phones(code):
    state = next((s for s in c.registry() if s['code'] == code), None)
    if not state:
        return set()
    offices, records = c.state_records(state)
    nums = set()
    for o in offices:
        nums.update(c.digits(n) for n in [o.get('phone')] + list(o.get('other_phones') or []) if c.digits(n))
    for r in records:
        n = c.digits((r.get('public_contact') or {}).get('phone'))
        if n:
            nums.add(n)
    return nums


def listings(snapshot, code):
    phones = published_phones(code)
    seen_ids, seen_keys, rows, left_out = set(), set(), [], {'closed': 0, 'no_us_phone': 0, 'duplicate': 0}
    for f in snapshot['rows']:
        if f.get('state') != code:
            continue
        if f.get('operating_status') in LEFT_OUT:
            left_out['closed'] += 1
            continue
        if len(c.digits(main_number(f.get('phone')))) != 10:
            # No phone, or a number outside the U.S. (VA files some overseas pre-discharge sites under a state).
            left_out['no_us_phone'] += 1
            continue
        site = f.get('website') if (f.get('website') or '').startswith('https://') else ''
        key = ((f.get('name') or '').lower(), (f.get('address1') or '').lower(), c.digits(f.get('phone')))
        if f['id'] in seen_ids or key in seen_keys:
            left_out['duplicate'] += 1
            continue
        seen_ids.add(f['id'])
        seen_keys.add(key)
        street = ', '.join(x for x in [f.get('address1'), f.get('address2')] if x)
        rows.append({
            'id': f['id'],
            'kind': KINDS.get(f.get('facility_type'), 'other'),
            'name': f.get('name'),
            'classification': f.get('classification') or '',
            'address': street,
            'city': f.get('city') or '',
            'state': code,
            'zip': (f.get('zip') or '')[:5],
            'phone': f.get('phone'),
            'mental_health_phone': f.get('mental_health_phone') or '',
            'hours': hours_text(f.get('hours')),
            'website': site,
            'notice': NOTICES.get(f.get('operating_status'), ''),
            'lat': f.get('lat'),
            'long': f.get('long'),
            'also_in_guide': c.digits(f.get('phone')) in phones,
            'source_url': site or LOCATOR,
            'source_title': 'VA facility page' if site else 'VA facility locator',
            'retrieved_on': snapshot['retrieved_on'],
        })
    rows.sort(key=lambda r: (list(KINDS.values()).index(r['kind']) if r['kind'] in KINDS.values() else 9,
                             r['city'], r['name']))
    return rows, left_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', required=True)
    ap.add_argument('--states', required=True, help='comma-separated state codes, or all')
    args = ap.parse_args()
    snap = c.read(args.snapshot)
    if snap.get('source_id') != 'va-facilities-api':
        sys.exit('not a VA Facilities API snapshot')
    codes = sorted({f['state'] for f in snap['rows'] if f.get('state')} & {s['code'] for s in c.registry()}) \
        if args.states == 'all' else [x.strip().upper() for x in args.states.split(',')]
    for code in codes:
        rows, left_out = listings(snap, code)
        c.write_json(OUT / f'{code.lower()}.json', {
            'about': 'VA medical centers, clinics, Vet Centers, benefits offices and cemeteries in this state, from the '
                     'VA Facilities API. Facilities VA marks closed are left out. Generated by '
                     'scripts/mining/va_listings.py; do not edit by hand.',
            'state': code,
            'source': {'id': 'va-facilities-api', 'publisher': 'U.S. Department of Veterans Affairs',
                       'url': snap['source_url'], 'api': snap['download_url'], 'environment': snap.get('environment'),
                       'retrieved_on': snap['retrieved_on'], 'snapshot_sha256': snap['sha256']},
            'evidence_level': 'B',
            'review_method': 'official_dataset',
            'left_out': left_out,
            'rows': rows,
        })
        overlap = sum(r['also_in_guide'] for r in rows)
        print(f'{code}: {len(rows)} listings ({overlap} phones already in the guide); left out {left_out}')


if __name__ == '__main__':
    main()
