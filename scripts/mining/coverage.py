"""Coverage report: how much each state and country has, how strong the evidence is, and which are thinnest.

    python3 scripts/mining/coverage.py           # rewrite data/mining/coverage.json and docs/COVERAGE.md
    python3 scripts/mining/coverage.py --check   # fail if either committed file is out of date

Reads only this repository: the registered state editions, data/world/countries.json, harvest files and, when one
has been fetched, the newest VA facility-count snapshot (a benchmark, never published as listings).
"""
import argparse
import re
import sys
from collections import Counter

import common as c

STATE_NAMES = {s['code']: s['name'] for s in c.registry()}
# The VA's facility-count dataset names its columns after states, with one misspelling at the source.
COLUMN_FIXES = {'wisonson': 'wisconsin', 'districtofcolumbia': 'districtofcolumbia'}


def harvest_counties():
    """Distinct counties named per state in harvest files (a starter edition's registry counts it as one area)."""
    seen = {}
    for path in sorted((c.MINING / 'harvest').glob('*.json')):
        for row in c.read(path).get('rows', []):
            if row.get('state') and row.get('county'):
                seen.setdefault(row['state'], set()).add(row['county'])
    return {k: len(v) for k, v in seen.items()}


def va_benchmark():
    """{state code: {facility type: count}} from the newest NCVAS snapshot, or {} when none has been fetched."""
    folder = c.MINING / 'snapshots' / 'va-ncvas-state-facility-counts'
    snaps = sorted(folder.glob('*.json')) if folder.exists() else []
    if not snaps:
        return {}, None
    snap = c.read(snaps[-1])
    by_key = {re.sub(r'[^a-z]', '', name.lower()): code for code, name in STATE_NAMES.items()}
    out = {}
    for row in snap.get('rows', []):
        label = next((str(v) for k, v in row.items() if isinstance(v, str) and not re.fullmatch(r'[\d.]+', v)), 'sites')
        for col, value in row.items():
            key = re.sub(r'[^a-z]', '', col.lower())
            code = by_key.get(COLUMN_FIXES.get(key, key))
            if code and re.fullmatch(r'[\d.]+', str(value)):
                out.setdefault(code, {})[label] = int(float(value))
    return out, snap.get('retrieved_on')


def state_row(state, extra_counties, bench):
    offices, records = c.state_records(state)
    counties = max(state['counties'], extra_counties.get(state['code'], 0)) if state.get('starter') else state['counties']
    classes = Counter(c.office_class(o) for o in offices)
    local_counties = {o.get('county') for o in offices if c.office_class(o) == 'local'}
    regional_counties = {o.get('county') for o in offices if c.office_class(o) == 'regional'} - local_counties
    office_levels = Counter(c.level_of(*c.office_method(o)) for o in offices)
    record_levels = Counter(c.level_of(*c.record_method(r)) for r in records)
    roles = Counter(r.get('regional_role') or r.get('resource_role') or 'program' for r in records)
    reviews = sorted([o['reviewed_on'] for o in offices if o.get('reviewed_on')] +
                     [c.record_reviewed_on(r) for r in records if c.record_reviewed_on(r)])
    strong = sum(office_levels[l] for l in 'AB') + sum(record_levels[l] for l in 'AB')
    total = len(offices) + len(records)
    local_share = round(min(len(local_counties), counties) / counties, 3) if counties else 0
    # A regional team that names the counties it serves is a real contact, a little less direct than a county office.
    reach = min((len(local_counties) + 0.75 * len(regional_counties)) / counties, 1) if counties else 0
    return {
        'code': state['code'],
        'name': state['name'],
        'edition': 'starter' if state.get('starter') else ('base' if state.get('base') else 'county'),
        'counties': counties,
        'counties_with_local_office': len(local_counties),
        'counties_with_regional_office': len(regional_counties),
        'local_office_share': local_share,
        'local_or_regional_reach': round(reach, 3),
        'offices': {'local': classes['local'], 'regional': classes['regional'], 'statewide_fallback': classes['fallback']},
        'office_evidence': {l: office_levels[l] for l in c.LEVELS if office_levels[l]},
        'records': len(records),
        'record_evidence': {l: record_levels[l] for l in c.LEVELS if record_levels[l]},
        'aging_agencies': roles['aging_agency'],
        'ombudsman_contacts': roles['ombudsman'],
        'independent_living': roles['independent_living'],
        'housing_providers': roles['housing_provider'],
        'legal_aid': roles['legal_aid'],
        'va_health_systems': roles['va_health_system'],
        'strong_evidence_share': round(strong / total, 3) if total else 0,
        'oldest_review': reviews[0] if reviews else None,
        'va_sites_benchmark': bench.get(state['code']),
        # Lower is thinner. County reach counts most, then how much rests on a full official read.
        'thinness_score': round(0.6 * reach + 0.25 * (strong / total if total else 0) +
                                0.15 * min(len(records) / 40, 1), 3),
    }


def build():
    bench, bench_date = va_benchmark()
    extra = harvest_counties()
    states = sorted((state_row(s, extra, bench) for s in c.registry()), key=lambda r: (r['thinness_score'], r['code']))
    for rank, row in enumerate(states, 1):
        row['thinness_rank'] = rank
    world = c.read(c.ROOT / 'data' / 'world' / 'countries.json')
    countries = world['countries']
    return {
        'about': 'Coverage of the veteran resource guide by state and country. thinness_rank 1 is the thinnest state. '
                 'Evidence levels: A agency confirmed, B official source read in full, C official source seen only in '
                 'part (search excerpt or metadata), D secondary directory, E lead only. Generated by '
                 'scripts/mining/coverage.py; do not edit by hand.',
        'va_benchmark_retrieved_on': bench_date,
        'states': states,
        'world': {
            'countries': len(countries),
            'country_lines': sum(len(k.get('lines') or []) for k in countries),
            'checked_on': world.get('checked_on'),
            'not_yet_covered': [k['name'] for k in world.get('not_yet_covered', [])],
        },
    }


def markdown(report):
    lines = ['# Coverage', '',
             'Generated by `scripts/mining/coverage.py` from the published data. Do not edit by hand; rerun the script.',
             '', 'Thinnest first. "Local office" counts counties with an office in or for the county itself, "regional only" '
             'counts counties served by a named regional team, and "statewide line only" counts the rest. Evidence: A agency confirmed, B official source read '
             'in full, C official source seen in part, D secondary directory.', '',
             '| Rank | State | Edition | Counties with local office | Regional only | Statewide line only | Records | Strong evidence | Oldest review |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in report['states']:
        lines.append(f"| {r['thinness_rank']} | {r['name']} | {r['edition']} | {r['counties_with_local_office']} of "
                     f"{r['counties']} | {r['counties_with_regional_office']} | {r['counties'] - r['counties_with_local_office'] - r['counties_with_regional_office']} | "
                     f"{r['records']} | {round(100 * r['strong_evidence_share'])}% | {r['oldest_review'] or ''} |")
    w = report['world']
    lines += ['', '## Outside the U.S.', '',
              f"{w['countries']} country pages with {w['country_lines']} local lines, last checked {w['checked_on']}.",
              '', 'Not yet covered: ' + (', '.join(w['not_yet_covered']) or 'none') + '.']
    if report['va_benchmark_retrieved_on']:
        lines += ['', f"VA facility counts used as a benchmark were retrieved {report['va_benchmark_retrieved_on']}."]
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    import json
    report = build()
    ok = c.check_or_write(c.MINING / 'coverage.json', json.dumps(report, ensure_ascii=False, indent=1) + '\n', args.check)
    ok = c.check_or_write(c.ROOT / 'docs' / 'COVERAGE.md', markdown(report), args.check) and ok
    thin = ', '.join(f"{r['code']} ({r['counties_with_local_office']}/{r['counties']})" for r in report['states'][:8])
    print(f'Thinnest states: {thin}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
