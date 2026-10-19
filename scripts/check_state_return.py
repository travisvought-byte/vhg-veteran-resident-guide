#!/usr/bin/env python3
"""Check a state research return before integration (research packet R-06).

Standalone: needs only Python 3.8+ and the return folder, so a researcher can run it
anywhere. Applies the same coverage, source and isolation rules as tests/states.cjs.

    python3 check_state_return.py research/returns/R-06-IN --state IN --name Indiana --counties 92

Exit code 0 means no errors. Warnings are listed for the integrator and owner to review.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Shared federal records every state receives automatically (data/public/federal-resource-ids.json).
FEDERAL_IDS = {
    'cms-care-compare', 'r02-aid-attendance-housebound', 'r02-dic', 'r02-disability-increase',
    'r02-family-caregiver', 'r02-general-caregiver', 'r02-hospice', 'r02-palliative',
    'r02-pension-medicaid-rule', 'r02-survivors-pension', 'r02-va-burial', 'r02-va-clc', 'r02-va-cnh',
    'r02-va-health-enrollment', 'r02-va-pension', 'r02-whv', 'va-hisa', 'va-sah', 'va-sha',
    'nara-discharge-records', 'va-accredited-help', 'va-location-finder', 'va-housing-help', 'va-tra',
    'alz-dementia-support', 'american-legion-post-locator', 'amvets-post-locator', 'vfw-post-locator',
    'crisis-988', 'va-mental-health', 'va-ssvf', 'va-hud-vash', 'va-crrc',
}
REGISTERED = {'oh', 'pa', 'ny', 'mi', 'ky', 'ut'}
NEEDS = {
    'general_navigation', 'help_at_home', 'equipment_home_accessibility', 'benefits_and_funding',
    'care_facilities', 'resident_rights', 'veteran_services', 'caregiver_support', 'housing',
    'dd_intake_service_coordination',
}
RECORD_STATUS = {'official_source_reviewed', 'official_search_extract_only'}
CONTACT_STATUS = {'official_website', 'published_directory'}
OFFICE_TYPES = {'county', 'regional', 'city', 'state'}
COUNTY_TYPES = {'county', 'independent_city', 'parish', 'borough', 'census_area', 'city_and_county'}
REGIONAL_ROLES = {'aging_agency', 'ombudsman', 'supported_living'}
ROUTES = {'benefits', 'survivors', 'care', 'rights', 'local', 'housing', 'accessibility'}
TOPICS = {'daily', 'accessibility', 'vision', 'hearing', 'memory', 'costs', 'rights'}
STATEWIDE = {'statewide'}
PHONE = re.compile(r'^(\d{3}-\d{3}-\d{4}( ext\. \d{1,5})?|\d{3})$')
DATE = re.compile(r'^20\d\d-\d\d-\d\d$')


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load(folder, pattern, report, required=True):
    matches = sorted(folder.glob(pattern))
    if len(matches) != 1:
        if required or matches:
            report.error(f'expected exactly one file matching {pattern}, found {len(matches)}')
        return None
    try:
        return json.loads(matches[0].read_text(encoding='utf-8')), matches[0].name
    except json.JSONDecodeError as exc:
        report.error(f'{matches[0].name}: not valid JSON ({exc})')
        return None


def https(value):
    return isinstance(value, str) and value.startswith('https://')


def check_offices(rows, code, expected, report):
    counties = []
    if not isinstance(rows, list) or not rows:
        report.error('offices: must be a non-empty list')
        return counties
    for i, o in enumerate(rows):
        where = f"offices[{i}] {o.get('county', '?')}"
        if o.get('state') != code:
            report.error(f'{where}: state must be "{code}"')
        county = o.get('county')
        if not county or not isinstance(county, str):
            report.error(f'{where}: county name missing')
            continue
        if county.lower().endswith(' county'):
            report.error(f'{where}: write the name without the word "County"')
        counties.append(county)
        if 'county_type' in o and o['county_type'] not in COUNTY_TYPES:
            report.error(f'{where}: county_type must be one of {sorted(COUNTY_TYPES)}')
        phones = [o.get('phone')] + [r.get('phone') for r in o.get('representatives', [])]
        if not any(phones):
            report.error(f'{where}: no veterans contact phone')
        for p in filter(None, phones):
            if not PHONE.match(p):
                report.error(f'{where}: phone "{p}" must look like 555-555-5555 or 555-555-5555 ext. 12')
        if not https(o.get('source_url')):
            report.error(f'{where}: source_url must be an https link')
        if not o.get('source_title'):
            report.error(f'{where}: source_title missing')
        if not DATE.match(str(o.get('reviewed_on', ''))):
            report.error(f'{where}: reviewed_on must be YYYY-MM-DD')
        if o.get('contact_status') not in CONTACT_STATUS:
            report.error(f'{where}: contact_status must be one of {sorted(CONTACT_STATUS)}')
        if o.get('office_type') not in OFFICE_TYPES:
            report.error(f'{where}: office_type must be one of {sorted(OFFICE_TYPES)}')
        if not o.get('organization'):
            report.error(f'{where}: organization missing')
        ev = o.get('evidence') or {}
        if not ev.get('review_method'):
            report.error(f'{where}: evidence.review_method missing')
        if ev.get('direct_agency_confirmation') is not False:
            report.error(f'{where}: evidence.direct_agency_confirmation must be false (research does not contact agencies)')
        if o.get('office_type') == 'regional' and not o.get('note'):
            report.warn(f'{where}: regional contact without a note explaining it is not a separate county office')
    if len(set(counties)) != len(counties):
        dupes = sorted({c for c in counties if counties.count(c) > 1})
        report.error(f'offices: duplicate counties {dupes}')
    if expected and len(counties) != expected:
        report.error(f'offices: {len(counties)} counties, expected {expected}')
    if code.lower() in {c.lower() for c in counties}:
        report.warn(f'a county shares the state code; check routing carefully')
    return counties


def check_records(rows, kind, code, counties, report):
    ids = []
    if not isinstance(rows, list) or not rows:
        report.error(f'{kind}: must be a non-empty list')
        return ids
    names = set(counties)
    prefix = code.lower() + '-'
    for i, r in enumerate(rows):
        pid = r.get('program_id', '')
        where = f'{kind}[{i}] {pid or "?"}'
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)+$', pid):
            report.error(f'{where}: program_id must be lowercase words joined by hyphens')
        elif not pid.startswith(prefix):
            report.error(f'{where}: program_id must start with "{prefix}"')
        if any(pid.startswith(other + '-') for other in REGISTERED - {code.lower()}):
            report.error(f'{where}: program_id starts with another state\'s code')
        if pid in FEDERAL_IDS:
            report.error(f'{where}: reuses a shared federal id')
        ids.append(pid)
        if r.get('state') != code:
            report.error(f'{where}: state must be "{code}"')
        for field in ('name', 'organization', 'description', 'next_step'):
            if not r.get(field):
                report.error(f'{where}: {field} missing')
        if not https(r.get('official_url')):
            report.error(f'{where}: official_url must be an https link')
        if not isinstance(r.get('constraints'), list):
            report.error(f'{where}: constraints must be a list (empty if none)')
        needs = r.get('needs_supported')
        if not needs or not isinstance(needs, list):
            report.error(f'{where}: needs_supported must be a non-empty list')
        else:
            for n in needs:
                if n not in NEEDS:
                    report.error(f'{where}: unknown need "{n}"; allowed: {sorted(NEEDS)}')
        area = r.get('service_area')
        if not area or not isinstance(area, list):
            report.error(f'{where}: service_area must be a non-empty list')
        else:
            for a in area:
                if a not in names and a.lower() not in STATEWIDE:
                    report.error(f'{where}: service_area "{a}" is not a county in the offices file or "statewide"')
        phone = (r.get('public_contact') or {}).get('phone')
        if phone and not PHONE.match(phone):
            report.error(f'{where}: phone "{phone}" must look like 555-555-5555')
        if kind == 'referrals':
            if r.get('regional_role') not in REGIONAL_ROLES:
                report.error(f'{where}: regional_role must be one of {sorted(REGIONAL_ROLES)}')
            if not phone:
                report.error(f'{where}: regional referrals need a published phone')
        elif not phone:
            report.warn(f'{where}: no phone; confirm the official page offers another clear route')
        v = r.get('verification') or {}
        if v.get('record_status') not in RECORD_STATUS:
            report.error(f'{where}: verification.record_status must be one of {sorted(RECORD_STATUS)}')
        elif v['record_status'] == 'official_search_extract_only':
            report.warn(f'{where}: supported only by a search excerpt')
        if not DATE.match(str(v.get('last_reviewed_on', ''))):
            report.error(f'{where}: verification.last_reviewed_on must be YYYY-MM-DD')
        ev = r.get('evidence') or {}
        if not ev.get('review_method'):
            report.error(f'{where}: evidence.review_method missing')
        if ev.get('direct_agency_confirmation') is not False:
            report.error(f'{where}: evidence.direct_agency_confirmation must be false')
        if phone and not https(ev.get('phone_source_url')):
            report.error(f'{where}: evidence.phone_source_url must be the https page that publishes the phone')
    if len(set(ids)) != len(ids):
        report.error(f'{kind}: duplicate program_id values')
    return ids


def check_coverage(counties, programs, referrals, report):
    statewide_ombudsman = any('ombudsman' in r.get('program_id', '') and
                              any(a.lower() in STATEWIDE for a in r.get('service_area', []))
                              for r in programs + referrals)
    for c in counties:
        if not any(r.get('regional_role') == 'aging_agency' and c in r.get('service_area', []) for r in referrals):
            report.error(f'{c}: no aging agency lists this county in service_area')
        scoped = any(r.get('regional_role') == 'ombudsman' and c in r.get('service_area', []) for r in referrals)
        if not scoped and not statewide_ombudsman:
            report.error(f'{c}: no ombudsman route (county-mapped or a statewide "ombudsman" program)')
    for role in ('aging_agency', 'ombudsman'):
        for r in referrals:
            if r.get('regional_role') == role and any(a.lower() in STATEWIDE for a in r.get('service_area', [])):
                report.error(f"{r.get('program_id')}: regional {role} records list counties, not statewide")


def check_routing(routing, ids, program_ids, report):
    known = set(ids) | FEDERAL_IDS
    if not isinstance(routing, dict):
        report.error('routing.json: must be an object')
        return
    def ids_in(label, value):
        if not isinstance(value, list) or not value:
            report.error(f'routing.json {label}: must be a non-empty list of program ids')
            return
        for pid in value:
            if pid not in known:
                report.error(f'routing.json {label}: "{pid}" is not in this return or the shared federal list')
    ids_in('priority', routing.get('priority'))
    routes = routing.get('routes') or {}
    for key in sorted(ROUTES):
        ids_in('routes.' + key, routes.get(key))
    for key in set(routes) - ROUTES:
        report.error(f'routing.json routes.{key}: unknown route; allowed {sorted(ROUTES)}')
    topics = routing.get('seniorTopics') or {}
    for key in sorted(TOPICS):
        ids_in('seniorTopics.' + key, topics.get(key))
    for key in set(topics) - TOPICS:
        report.error(f'routing.json seniorTopics.{key}: unknown topic; allowed {sorted(TOPICS)}')
    nav = routing.get('statewide_navigation') or {}
    if not nav.get('name') or not nav.get('phone') or not https(nav.get('source_url')):
        report.error('routing.json statewide_navigation: needs name, phone and https source_url')
    mod = routing.get('home_modification') or {}
    if not https(mod.get('url')) or not mod.get('label') or not mod.get('guidance'):
        report.error('routing.json home_modification: needs url, label and guidance')
    used = {p for v in [routing.get('priority') or []] + list(routes.values()) + list(topics.values()) if isinstance(v, list) for p in v}
    for pid in sorted(set(program_ids) - used):
        report.warn(f'{pid}: state program not used in any route or topic, so visitors will only find it by search')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('folder', type=Path)
    parser.add_argument('--state', required=True, help='two-letter code, e.g. IN')
    parser.add_argument('--name', required=True, help='state name, e.g. Indiana')
    parser.add_argument('--counties', type=int, help='expected county count, including equivalents')
    args = parser.parse_args()
    code = args.state.upper()
    report = Report()
    folder = args.folder
    if not folder.is_dir():
        sys.exit(f'{folder} is not a folder')
    offices = load(folder, '*-county-veterans-offices.json', report)
    programs = load(folder, f'{code.lower()}-programs.json', report)
    referrals = load(folder, f'{code.lower()}-regional-referrals.json', report)
    routing = load(folder, 'routing.json', report)
    if not (folder / 'notes.md').is_file():
        report.error('notes.md missing')
    counties = check_offices(offices[0], code, args.counties, report) if offices else []
    program_ids = check_records(programs[0], 'programs', code, counties, report) if programs else []
    referral_ids = check_records(referrals[0], 'referrals', code, counties, report) if referrals else []
    if set(program_ids) & set(referral_ids):
        report.error(f'ids used in both programs and referrals: {sorted(set(program_ids) & set(referral_ids))}')
    if offices and programs and referrals:
        check_coverage(counties, programs[0], referrals[0], report)
    if routing:
        check_routing(routing[0], program_ids + referral_ids, program_ids, report)
    if args.name.lower() in {c.lower() for c in counties}:
        report.warn(f'"{args.name}" is also a county name. Use "statewide" for statewide records, never the state name.')
    print(f'{args.name} ({code}): {len(counties)} counties, {len(program_ids)} programs, {len(referral_ids)} regional referrals')
    for w in report.warnings:
        print('WARNING', w)
    for e in report.errors:
        print('ERROR  ', e)
    print(f'{len(report.errors)} errors, {len(report.warnings)} warnings')
    sys.exit(1 if report.errors else 0)


if __name__ == '__main__':
    main()
