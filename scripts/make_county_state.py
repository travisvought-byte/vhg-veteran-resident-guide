#!/usr/bin/env python3
"""Build a full county edition from one research sheet: data/source/states/<code>.json.

A starter edition has one statewide entry. A full edition has every county's veterans office, a matched Area
Agency on Aging and long-term-care ombudsman, Centers for Independent Living and VA housing help. The research
sheet holds what was read from official pages (and which page); this script turns it into the files the guide
reads, the same way for every state, so a new state needs research and no code (docs/ADDING-A-STATE.md).

    python3 scripts/make_county_state.py CO       write the edition's files
    python3 scripts/make_county_state.py CO --check   stop with a message if the sheet is incomplete

It writes data/public/<slug>-county-veterans-offices.json, <code>-regional-referrals.json, <code>-programs.json,
states/<code>/edition.json and adapter.js (from the Missouri edition's wording, with the state's own names),
and replaces the state's registry entry. Then run scripts/make_starter_states.py and scripts/build_public.py.
"""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = 'MO'  # the full edition whose edition.json and adapter.js are the pattern
SSVF_URL = 'https://department.va.gov/homeless/supportive-services-for-veteran-families/'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source(url, title, scope, reviewed):
    return {'url': url, 'title': title, 'reviewed_on': reviewed, 'scope': scope}


def verification(status, reviewed):
    return {'record_status': status, 'last_reviewed_on': reviewed}


STATUS = {'full': 'official_source_reviewed', 'excerpt': 'official_search_extract_only'}


def check(sheet, counties):
    """Every county has exactly one veterans office, aging agency and ombudsman; every id is the state's own."""
    problems = []
    code = sheet['code'].lower()
    if len(counties) != sheet['counties']:
        problems.append(f"sheet says {sheet['counties']} counties, offices list {len(counties)}")
    if len(set(counties)) != len(counties):
        problems.append('a county appears twice in the offices list')
    for role, rows in (('aging', sheet['aging']['regions']), ('ombudsman', sheet['ombudsman']['regions'])):
        for county in counties:
            hits = [r['id'] for r in rows if county in r['counties']]
            if len(hits) != 1:
                problems.append(f'{county}: {len(hits)} {role} matches {hits}')
        for r in rows:
            extra = set(r['counties']) - set(counties)
            if extra:
                problems.append(f"{r['id']} names counties that are not on the offices list: {sorted(extra)}")
    for r in sheet['cils']['list']:
        extra = set(r['counties']) - set(counties)
        if extra:
            problems.append(f"{r['id']} names counties that are not on the offices list: {sorted(extra)}")
    ids = [r['id'] for r in sheet['aging']['regions'] + sheet['ombudsman']['regions'] + sheet['cils']['list'] + sheet['programs']]
    if len(ids) != len(set(ids)):
        problems.append('an id is used twice')
    for i in ids:
        if not i.startswith(code + '-'):
            problems.append(f'{i} must start with {code}-')
    return problems


def build_offices(sheet):
    code, reviewed, spec = sheet['code'], sheet['reviewed_on'], sheet['offices']
    out = []
    for o in spec['list']:
        record = {
            'state': code, 'county': o['county'], 'county_type': o.get('county_type', 'county'), 'phone': o['phone'],
            'organization': o.get('organization') or f"{o['county']} County Veterans Service Office",
            'office_type': o.get('office_type', 'county'),
        }
        if o.get('other_phones'):
            record['other_phones'] = o['other_phones']
        record['address'] = o['address']
        if o.get('hours'):
            record['hours'] = o['hours']
        if o.get('other_offices'):
            record['other_offices'] = o['other_offices']
        record.update({
            'source_url': spec['source_url'], 'source_title': spec['source_title'], 'reviewed_on': reviewed,
            'contact_status': 'official_website',
            'note': (o['note'] + ' ' if o.get('note') else '') + spec['note'],
            'evidence': {'review_method': spec.get('review_method', 'full_official_page_text'), 'direct_agency_confirmation': False,
                         'county_list_source_url': spec['source_url'], 'selection': spec['selection']},
        })
        out.append(record)
    return out


def build_regional(sheet):
    code, name, reviewed = sheet['code'], sheet['name'], sheet['reviewed_on']
    low, aging, omb = code.lower(), sheet['aging'], sheet['ombudsman']
    out = []
    word = aging.get('region_word', 'Region')  # '' when the state's agencies are known by name, not number
    for r in aging['regions']:
        src = r.get('source_url') or aging['source_url']
        out.append({
            'program_id': r['id'], 'name': r['name'], 'organization': f"{r['name']} ({word} {r['label']})" if word else r['name'],
            'official_url': src, 'state': code, 'service_area': r['counties'],
            'needs_supported': ['general_navigation', 'help_at_home'], 'regional_role': 'aging_agency',
            'description': 'The Area Agency on Aging for this county: information and assistance, home-delivered and congregate meals, in-home services, transportation, caregiver support and senior legal assistance.',
            'next_step': 'Call and describe what is hard right now. Ask for information and assistance. ' + aging['next_step_extra'] + ' Military service is not required.',
            'constraints': ['Many services focus on people age 60 and older and adults with disabilities; eligibility and waitlists vary by program.'] + r.get('notes', []),
            'public_contact': {'phone': r['phone'], 'phone_label': f"Area Agency on Aging, {word} {r['label']}" if word else f"Area Agency on Aging ({r['label']})"},
            'verification': verification(STATUS['full'], reviewed),
            'evidence': {'review_method': aging['review_method'], 'direct_agency_confirmation': False,
                         'service_area_source_url': src, 'phone_source_url': src},
            'source_evidence': [source(src, aging['source_title'], aging['source_scope'], reviewed)],
        })
    for r in omb['regions']:
        src = r['source_url']
        full = r.get('review', 'full') == 'full'
        out.append({
            'program_id': r['id'], 'name': r['name'], 'organization': r['name'], 'official_url': src, 'state': code,
            'service_area': r['counties'], 'needs_supported': ['resident_rights', 'general_navigation'], 'regional_role': 'ombudsman',
            'description': 'The regional long-term care ombudsman for this county: advocacy for residents of nursing homes, assisted living and residential care facilities.',
            'next_step': 'Call the regional ombudsman program. Give the facility name and county. For immediate danger, call 911.',
            'constraints': ['The ombudsman acts with the resident’s permission and is not a licensing or enforcement agency.'] + r.get('notes', []),
            'public_contact': {'phone': r['phone'], 'phone_label': 'Regional ombudsman program'},
            'verification': verification(STATUS['full' if full else 'excerpt'], reviewed),
            'evidence': {'review_method': r['review_method'], 'direct_agency_confirmation': False,
                         'service_area_source_url': aging['source_url'], 'phone_source_url': src},
            'source_evidence': [source(src, r['source_title'], r['source_scope'], reviewed),
                                source(aging['source_url'], aging['source_title'], 'Counties in each aging region.', reviewed)]
                               + [source(s['url'], s['title'], s['scope'], reviewed) for s in r.get('extra_sources', [])],
        })
    return out


def build_programs(sheet):
    code, name, reviewed = sheet['code'], sheet['name'], sheet['reviewed_on']
    out = []
    for p in sheet['programs']:
        full = p.get('review', 'excerpt') == 'full'
        when = p.get('reviewed', reviewed)
        record = {
            'program_id': p['id'], 'name': p['name'], 'official_url': p['url'], 'organization': p['organization'],
            'service_area': p.get('area', ['statewide']), 'state': code,
        }
        if p.get('role'):
            record['resource_role'] = p['role']
        record.update({
            'needs_supported': p['needs'], 'description': p['description'], 'next_step': p['next_step'],
            'constraints': p.get('constraints', []),
            'public_contact': {'phone': p['phone'], **({'phone_label': p['phone_label']} if p.get('phone_label') else {})},
            'verification': verification(STATUS['full' if full else 'excerpt'], when),
            'evidence': {'review_method': p.get('method', 'full_official_page_text' if full else 'official_search_excerpt'),
                         'direct_agency_confirmation': False, 'phone_source_url': p['phone_source']},
        })
        if p.get('sources'):
            record['source_evidence'] = [source(s['url'], s['title'], s['scope'], when) for s in p['sources']]
        out.append(record)
    # Centers for Independent Living
    cils = sheet['cils']
    for c in cils['list']:
        # A center may name its own source, review depth and phone wording; otherwise the list's apply.
        src_url, full = c.get('source_url', cils['source_url']), c.get('review', 'full') == 'full'
        out.append({
            'program_id': c['id'], 'name': c['name'], 'organization': c['organization'], 'official_url': c['url'],
            'service_area': c['counties'], 'state': code, 'resource_role': 'independent_living',
            'needs_supported': ['help_at_home', 'general_navigation', 'equipment_home_accessibility'],
            'description': 'A Center for Independent Living: disability-led help with daily living skills, peer support, advocacy, assistive technology referrals and moving from a nursing home back to the community. Any age and any disability; military service is not required.',
            'next_step': 'Call with your county and goals. Ask about intake, home access, independent living skills or help leaving a facility.',
            'constraints': ['A Center for Independent Living is a community support organization, not a residential care facility. Services depend on assessment and availability.'] + c.get('notes', []),
            'public_contact': {'phone': c['phone'], 'phone_label': c.get('phone_label', cils.get('phone_label', 'Local phone listed in the ILRU national directory'))},
            'verification': verification(STATUS['full' if full else 'excerpt'], reviewed),
            'evidence': {'review_method': c.get('method', 'full_official_page_text' if full else 'official_search_excerpt'),
                         'direct_agency_confirmation': False, 'phone_source_url': src_url, 'service_area_source_url': src_url},
            'source_evidence': [source(src_url, c.get('source_title', cils['source_title']),
                                       c.get('scope', cils.get('scope', 'Center offices, local phones, websites and counties served as listed.')), reviewed)]
                               + [source(e['url'], e['title'], e['scope'], reviewed) for e in c.get('extra_sources', [])],
        })
    # VA housing help (SSVF) from the FY26 intake list already in the repository.
    ssvf = read('data/public/ssvf-intake-fy26.json')
    for row in ssvf['records']:
        if code not in row['states']:
            continue
        # Independent cities keep their name ('Baltimore city' becomes 'Baltimore City'); other suffixes are dropped.
        counties = [c['name'][:-5] + ' City' if c['name'].endswith(' city') else re.sub(r' (County|Parish|Borough|Municipality|Census Area)$', '', c['name'])
                    for c in row['counties'] if c['state'] == code]
        phones = row['intake_phones']
        if not phones:  # a card without a phone number would not help anyone; the omission is documented per state
            continue
        pid = f"{code.lower()}-ssvf-{row['fain'].lower()}"
        out.append({
            'program_id': pid, 'name': f"{row['organization']}: veteran housing help (SSVF)", 'official_url': SSVF_URL,
            'organization': row['organization'], 'service_area': counties, 'state': code, 'resource_role': 'housing_provider',
            'needs_supported': ['housing', 'veteran_services'],
            'description': f"VA-funded Supportive Services for Veteran Families (SSVF, grant {row['fain']}): case management, help keeping a home, rapid rehousing and short-term financial help for low-income veteran households.",
            'next_step': 'Call SSVF intake with your county and housing situation: whether you are homeless now or at risk of losing housing, and who lives with you.'
                         + (f" A second intake number is listed: {phones[1]}." if len(phones) > 1 else ''),
            'constraints': ['Serves only the areas listed; check that yours is included. Veteran-household, income and housing-status screening applies.',
                            'County and intake details come from VA’s FY26 SSVF provider intake list; confirm current service when calling.'],
            'public_contact': {'phone': phones[0], 'phone_label': 'VA-listed SSVF intake'},
            'verification': verification(STATUS['full'], ssvf['reviewed_on']),
            'evidence': {'review_method': 'full_official_spreadsheet', 'direct_agency_confirmation': False, 'service_area_source_url': ssvf['source_url']},
            'source_evidence': [{'url': ssvf['source_url'], 'title': 'VA SSVF provider intake list (FY26)', 'reviewed_on': ssvf['reviewed_on'],
                                 'scope': f"County coverage and SSVF intake; {ssvf['sheet']} worksheet row {row['row']}", 'sheet': ssvf['sheet'],
                                 'row': row['row'], 'source_sha256': ssvf['source_sha256']}],
        })
    return out


def program_ids(sheet, programs):
    """The ids the edition's route lists name, grouped by what they are."""
    by = lambda role: [p['program_id'] for p in programs if p.get('resource_role') == role]
    stat = {p['id'].split('-', 1)[1]: p['id'] for p in sheet['programs']}
    return {'cils': by('independent_living'), 'ssvf': by('housing_provider'), 'stat': stat}


def edition(sheet, programs, regional):
    """The template state's operations with this state's names, dates and route lists."""
    code, name, slug = sheet['code'], sheet['name'], sheet['slug']
    tpl = read(f'states/{TEMPLATE.lower()}/edition.json')['ops']
    tpl_code = TEMPLATE
    reg = {r['code']: r for r in read('states/registry.json')}
    t = reg[TEMPLATE]
    ids = program_ids(sheet, programs)
    s = ids['stat']
    cils, ssvf = ids['cils'], ids['ssvf']
    count = sheet['counties']
    senior = sheet['senior_line_id']
    review_day = sheet['month_label']

    def swap(text):
        text = text.replace(t['name'], name).replace(t['name'].lower().replace(' ', ''), slug)
        text = text.replace(f'All {t["counties"]}', f'All {count}').replace(f'all {t["counties"]}', f'all {count}')
        text = text.replace(f"const STATE='{tpl_code}';", f"const STATE='{code}';").replace(f'share-{tpl_code.lower()}.html', f'share-{code.lower()}.html')
        return text.replace(sheet['template_date'], review_day)

    ops = []
    for op in tpl:
        op = copy.deepcopy(op)
        if op['op'] in ('replace', 'regex'):
            op = {k: (swap(v) if isinstance(v, str) else v) for k, v in op.items()}
            if op.get('new', '').startswith('Veterans Service Office phones come from'):
                op['new'] = sheet['phones_sentence']
        ops.append(op)
    claims, ship, omb, legal, va = s['claims'], s['ship'], s['ombudsman'], s['legal-programs'], s['vahealth-systems']
    priority = [claims, senior, ship, omb, legal, 'r02-aid-attendance-housebound', 'r02-va-pension', 'r02-survivors-pension', 'r02-va-health-enrollment', 'va-accredited-help']
    routes = {
        'benefits': [claims, ship, 'r02-va-pension', 'r02-aid-attendance-housebound', 'r02-disability-increase', 'r02-pension-medicaid-rule', 'r02-survivors-pension', 'r02-dic', 'va-accredited-help', senior],
        'survivors': [claims, 'r02-survivors-pension', 'r02-dic', 'r02-aid-attendance-housebound', 'r02-va-burial', 'va-accredited-help', 'nara-discharge-records'],
        'care': ['r02-va-health-enrollment', 'va-location-finder', 'r02-va-cnh', 'r02-va-clc', 'r02-general-caregiver', 'r02-family-caregiver', 'r02-hospice', 'r02-palliative', senior, *cils, va],
        'rights': [omb, legal],
        'local': [claims, senior, *cils, legal, va],
        'housing': ['va-housing-help', *ssvf, 'va-location-finder', 'va-accredited-help', 'nara-discharge-records', legal],
    }
    topics = {'daily': [senior, *cils], 'accessibility': [senior, *cils], 'vision': [senior], 'hearing': [senior],
              'memory': ['alz-dementia-support', senior], 'costs': [ship, senior, legal], 'rights': [omb, legal]}
    declared = {'priority': priority, 'routes': routes, 'seniorTopics': topics}
    for op in ops:
        if op['op'] == 'declare':
            op['value'] = declared[op['name']]
        elif op['op'] == 'line' and op['prefix'] == 'routes.accessibility=':
            ids_js = ','.join(f"'{i}'" for i in ['va-hisa', 'va-sah', 'va-sha', 'va-tra', senior, *cils, 'va-location-finder'])
            op['new'] = f"routes.accessibility=[{ids_js},...DATA.filter(x=>x.regional_role==='aging_agency').map(x=>x.program_id)];"
    return {'ops': ops}


def adapter(sheet):
    """The template state's adapter with this state's names, sources and phone numbers."""
    code, name = sheet['code'], sheet['name']
    text = (ROOT / 'states' / TEMPLATE.lower() / 'adapter.js').read_text(encoding='utf-8')
    a = sheet['adapter']
    old_badge = "c.office_type==='state_field_office'?'MVC Veterans Service Office':'MVC statewide line'"
    new_badge = f"c.office_type==='county'?'{a['badge_county']}':c.office_type==='state_field_office'?'{a['badge_state']}':'{a['badge_statewide']}'"
    pairs = [
        (old_badge, new_badge),
        ('Other MVC offices for ', 'Other offices for '),
        ('Published in the Missouri Veterans Commission benefits guide', a['published_in']),
        ('<a href="https://veteranbenefits.mo.gov/" target="_blank" rel="noopener noreferrer">MVC benefits portal ↗</a>',
         f'<a href="{sheet["agency"]["url"]}" target="_blank" rel="noopener noreferrer">{a["agency_link"]} ↗</a>'),
        ('Missouri Veterans Commission Veterans Service Officers can', a['officers_can']),
        ("county==='St. Louis City'?county:county+' County'", (json.dumps(a['independent_cities']) + ".includes(county)?county:county+' County'") if a.get('independent_cities') else "county+' County'"),
        ("'mo-ombudsman'", f"'{code.lower()}-ombudsman'"),
        ('800-309-3282', sheet['ombudsman']['state_phone']),
        ("phoneLink('800-392-0210')+' (Adult Abuse and Neglect Hotline, 7 a.m. to 8 p.m. daily)'",
         f"phoneLink('{a['abuse_phone']}')+' ({a['abuse_label']})'"),
        (', MO', f', {code}'),
        ('Missouri', name),
    ]
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f'adapter template no longer contains: {old[:60]}')
        text = text.replace(old, new)
    leftovers = [w for w in ('MVC', 'Missouri', 'mo-', "St. Louis") if w in text]
    if leftovers:
        raise SystemExit(f'adapter still has template wording: {leftovers}')
    return text


def registry_entry(sheet):
    code, name, slug = sheet['code'], sheet['name'], sheet['slug']
    low = code.lower()
    return {
        'code': code, 'name': name, 'page': f'{low}.html', 'share_page': f'share-{low}.html', 'qr': f'assets/guide-qr-{low}.svg',
        'counties': sheet['counties'], 'programs': f'data/public/{low}-programs.json', 'referrals': f'data/public/{low}-regional-referrals.json',
        'offices': f'data/public/{slug}-county-veterans-offices.json', 'resources': f'data/public/{slug}-resources.json',
        'statewide_area_names': [], 'coverage_scope': sheet['coverage_scope'], 'coverage_note': sheet['coverage_note'],
        'share_description': sheet['share_description'],
        'share_replacements': [['Updated October 8, 2026', 'Updated ' + sheet['month_label']]],
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    code = sys.argv[1].upper()
    sheet = read(f'data/source/states/{code.lower()}.json')
    counties = [o['county'] for o in sheet['offices']['list']]
    problems = check(sheet, counties)
    if problems:
        raise SystemExit('The research sheet is not ready:\n  ' + '\n  '.join(problems))
    if '--check' in sys.argv:
        print(f"{sheet['name']}: {len(counties)} counties, every one with a veterans office, one aging agency and one ombudsman.")
        return
    low, slug = code.lower(), sheet['slug']
    offices, regional, programs = build_offices(sheet), build_regional(sheet), build_programs(sheet)
    write(f'data/public/{slug}-county-veterans-offices.json', offices)
    write(f'data/public/{low}-regional-referrals.json', regional)
    write(f'data/public/{low}-programs.json', programs)
    (ROOT / 'states' / low).mkdir(exist_ok=True)
    write(f'states/{low}/edition.json', edition(sheet, programs, regional))
    (ROOT / 'states' / low / 'adapter.js').write_text(adapter(sheet), encoding='utf-8')

    registry = read('states/registry.json')
    entry = registry_entry(sheet)
    kept = [r for r in registry if r['code'] != code]
    last_full = max(i for i, r in enumerate(kept) if not r.get('starter'))
    kept.insert(last_full + 1, entry)
    write('states/registry.json', kept)

    starters = read('data/starter-states.json')
    starters['states'] = [s for s in starters['states'] if s['code'] != code]
    write('data/starter-states.json', starters)
    print(f"{sheet['name']}: {len(offices)} offices, {len(regional)} aging and ombudsman records, {len(programs)} state programs written.")
    print('Next: python3 scripts/make_starter_states.py && python3 scripts/build_public.py')


if __name__ == '__main__':
    main()
