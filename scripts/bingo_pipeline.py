#!/usr/bin/env python3
"""FindBingo.org data pipeline: see what we have, what is due for a recheck, and add new games safely.

The lists themselves stay where the site reads them (data/public/*bingo*.json, wired in scripts/findbingo_site.py).
This script sits on top of them:

  python3 scripts/bingo_pipeline.py build              write the normalized CSV and the coverage report
  python3 scripts/bingo_pipeline.py check              fail if those files are out of date (CI runs this)
  python3 scripts/bingo_pipeline.py queue [--today D]  what to recheck now, and which states to grow next
  python3 scripts/bingo_pipeline.py dupes              places that look listed twice (same street and ZIP)
  python3 scripts/bingo_pipeline.py merge BATCH.json   add researched games to a state's organizer-schedule file

How to run a sourcing round cold, the evidence levels and the review policy are in docs/BINGO-PIPELINE.md.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import findbingo_site as fb  # noqa: E402  (the site's own file wiring, so the pipeline never disagrees with the build)

PUBLIC = ROOT / 'data/public'
REGISTRY = ROOT / 'data/bingo-sources/registry.json'
CSV_OUT = PUBLIC / 'findbingo-games.csv'
COVERAGE_JSON = ROOT / 'data/bingo-sources/coverage.json'
COVERAGE_MD = ROOT / 'docs/BINGO-COVERAGE.md'
ZIP_FILE = 'https://raw.githubusercontent.com/midwire/free_zipcode_data/e00aec159e76335c3d62df70d07e7e207be8f4fc/all_us_zipcodes.csv'
# Ohio is served by its own finder (scripts/bingo_site.py); its two lists are counted here too.
OHIO_FILES = {'ohio-bingo.json': 'organizer_schedule', 'ohio-bingo-authorized.json': 'state_license'}

# How far to trust a listing, from where its days came. Mirrors the cannabis directory's evidence tiers.
EVIDENCE = {
    'state_schedule': "A state regulator's list that gives each game's day and time (Michigan, Texas, Virginia, Missouri).",
    'organizer_schedule': "The group's own published schedule: its website, its lodge or post page, or a city or senior-center calendar.",
    'state_license': 'A state list of licensed groups or permitted places, without game days (call to ask when they play).',
}
# Review policy, in days. Organizer schedules change often and are rechecked page by page (a full review).
# State lists are refreshed whole from the regulator (a routine verification). A reported closure, a license action
# or a correction from a hall or player means an immediate recheck, whatever the date.
REVIEW_DAYS = {'organizer_schedule': 90, 'state_schedule': 180, 'state_license': 180}
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
CSV_FIELDS = ['game_id', 'state', 'county', 'city', 'place', 'organization', 'address', 'zip', 'kind', 'day', 'start', 'end',
              'schedule', 'evidence_level', 'source_url', 'reviewed_on', 'review_due', 'list_file']
SOURCE_KINDS = {'times_list', 'license_list', 'lookup', 'calendar', 'regulator', 'organizer_network'}
SOURCE_STATUS = {'loaded', 'held_out', 'not_usable', 'lead_only', 'blocked', 'to_check'}


def _files():
    """(state code, file name, evidence level) for every bingo list the site carries."""
    out = [(c, f, 'organizer_schedule') for c, f in fb.STARTER_FILES.items()]
    out += [(c, f, 'state_schedule') for c, f in fb.TIMES_FILES.items()]
    out += [(c, f, 'state_license') for c, f in fb.LICENSE_FILES.items()]
    out += [('OH', f, e) for f, e in OHIO_FILES.items()]
    return sorted(out)


def load(root=ROOT):
    states = json.loads((root / 'data/public/bingo-states.json').read_text())
    records = []
    for code, name, level in _files():
        for r in json.loads((root / 'data/public' / name).read_text()):
            records.append((code, name, level, r))
    return states, records


def _city(r):
    if r.get('city'):
        return r['city']
    m = re.search(r',\s*([^,]+),\s*[A-Z]{2}\s+\d{5}', r.get('address') or '')
    return m.group(1).strip() if m else ''


def _zip(r):
    if r.get('zip'):
        return r['zip']
    m = re.search(r'\b(\d{5})(?:-\d{4})?\s*$', r.get('address') or '')
    return m.group(1) if m else ''


def _when(r, level):
    reviewed = r.get('reviewed_on') or ''
    due = (date.fromisoformat(reviewed) + timedelta(days=REVIEW_DAYS[level])).isoformat() if reviewed else ''
    return reviewed, due


def rows(records):
    """One row per game (place, organization, weekday). A licensed place with no game days is one row with no day."""
    out = []
    for code, name, level, r in records:
        reviewed, due = _when(r, level)
        src = r.get('source_url') or (r.get('sources') or [{}])[0].get('url', '')
        base = dict(state=code, county=r.get('county') or '', city=_city(r), place=r['name'], address=r.get('address') or '',
                    zip=_zip(r), kind=r.get('kind') or ('hall' if level != 'state_license' else 'licensed'),
                    evidence_level=level, source_url=src, reviewed_on=reviewed, review_due=due, list_file=name)
        sessions = r.get('sessions') or []
        if not sessions:
            sched = r.get('schedule') or r.get('authorized_days') or ''
            out.append(dict(base, game_id=r['id'], organization=', '.join(r.get('organizations') or []) or r['name'],
                            day='', start='', end='', schedule=str(sched)))
            continue
        for i, s in enumerate(sessions, 1):
            label = s.get('label') or ('Every ' + DAYS[s['day']])
            out.append(dict(base, game_id=f"{r['id']}#{i}",
                            organization=s['organization'], day=DAYS[s['day']], start=s.get('start') or '', end=s.get('end') or '',
                            schedule=label))
    out.sort(key=lambda x: (x['state'], x['county'], x['city'], x['place'], x['game_id']))
    return out


def _slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


ABBR = {'street': 'st', 'avenue': 'ave', 'road': 'rd', 'drive': 'dr', 'boulevard': 'blvd', 'highway': 'hwy', 'lane': 'ln',
        'north': 'n', 'south': 's', 'east': 'e', 'west': 'w', 'route': 'rt', 'court': 'ct', 'place': 'pl', 'parkway': 'pkwy',
        'county': 'co', 'saint': 'st', 'mount': 'mt', 'suite': '', 'ste': ''}


def address_key(address, zip5):
    """Street line and ZIP, lower case, with common words shortened, so '12 Main Street' and '12 Main St.' match."""
    street = (address or '').split(',')[0].lower()
    words = [ABBR.get(w, w) for w in re.findall(r'[a-z0-9]+', street)]
    return ' '.join(w for w in words if w) + ' ' + (zip5 or '')


def dupes(records):
    """Places in one state with the same street and ZIP. Several licensed groups sharing one hall is normal on the
    state license lists (Indiana, Ohio), so a group made only of license-list records is not reported."""
    groups = defaultdict(list)
    for code, name, level, r in records:
        groups[(code, address_key(r.get('address'), _zip(r)))].append((name, level, r['id']))
    return {k: v for k, v in groups.items() if len(v) > 1 and any(lv != 'state_license' for _, lv, _ in v)}


def registry():
    reg = json.loads(REGISTRY.read_text())
    codes = [s['code'] for s in reg['states']]
    assert codes == fb.ORDER, 'registry lists every state and DC, in the site order'
    assert set(reg['evidence_levels']) == set(EVIDENCE) and reg['review_days'] == REVIEW_DAYS
    for s in reg['states']:
        assert type(s['counties']) is int and s['counties'] > 0, s['code']
        for x in s['sources']:
            assert x['kind'] in SOURCE_KINDS and x['status'] in SOURCE_STATUS and x['label'], (s['code'], x)
            assert x['url'].startswith('https://') and date.fromisoformat(x['checked_on']), (s['code'], x['url'])
            assert x['status'] != 'loaded' or x.get('script') or x['kind'] == 'regulator', (s['code'], x['label'])
            assert x['status'] not in ('held_out', 'not_usable', 'blocked') or x.get('note'), (s['code'], x['label'])
        assert isinstance(s.get('next', ''), str)
    for n in reg['organizer_networks']:
        assert n['name'] and n['how'] and ('url' not in n or n['url'].startswith('https://')), n
    return reg


def coverage(states, records, reg):
    by_state = {s['code']: s for s in states}
    regs = {s['code']: s for s in reg['states']}
    places, games, counties, sources, first_due = Counter(), Counter(), defaultdict(set), defaultdict(set), {}
    with_days = Counter()
    for code, name, level, r in records:
        places[code] += 1
        n = len(r.get('sessions') or [])
        games[code] += n
        if n or r.get('schedule'):
            with_days[code] += 1
        if r.get('county'):
            counties[code].add(r['county'])
        sources[code].add(r.get('source_url') or (r.get('sources') or [{}])[0].get('url', ''))
        _, due = _when(r, level)
        if due and (code not in first_due or due < first_due[code]):
            first_due[code] = due
    out = []
    for code in fb.ORDER:
        s, g = by_state[code], regs[code]
        total = g['counties']
        out.append(dict(code=code, name=s['name'], coverage=s['coverage'], places=places[code], places_with_days=with_days[code],
                        games=games[code], counties_listed=len(counties[code]), counties_total=total,
                        county_share=round(len(counties[code]) / total, 3), sources_used=len(sources[code]),
                        next_review_due=first_due.get(code, ''),
                        statewide=[f"{x['label']}: {x['status']}" for x in g['sources'] if x['kind'] != 'regulator'],
                        next=g.get('next', '')))
    # Thinnest first: fewest places with known game days, then the smallest share of counties.
    thin = sorted(out, key=lambda x: (x['places_with_days'], x['county_share'], x['code']))
    for i, x in enumerate(thin, 1):
        x['thin_rank'] = i
    return out


def coverage_md(cov):
    lines = ['# Find Bingo coverage', '',
             'Generated by `python3 scripts/bingo_pipeline.py build` from the lists in `data/public/` and the source registry',
             '(`data/bingo-sources/registry.json`). Do not edit by hand. How to grow it: `docs/BINGO-PIPELINE.md`.', '',
             f"- Places listed: {sum(x['places'] for x in cov)}; places with known game days: {sum(x['places_with_days'] for x in cov)}; "
             f"game sessions: {sum(x['games'] for x in cov)}.",
             f"- States and DC with a list on the site: {sum(1 for x in cov if x['places'])} of {len(cov)}.", '',
             '## Thinnest first', '',
             'Ranked by places with known game days, then by the share of counties with any listing.', '',
             '| rank | state | list type | places (with days) | games | counties listed | next review due | statewide sources | next step |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for x in sorted(cov, key=lambda x: x['thin_rank']):
        lines.append(f"| {x['thin_rank']} | {x['name']} | {x['coverage']} | {x['places']} ({x['places_with_days']}) | {x['games']} | "
                     f"{x['counties_listed']} of {x['counties_total']} | {x['next_review_due'] or '-'} | "
                     f"{'; '.join(x['statewide']) or '-'} | {x['next'] or '-'} |")
    return '\n'.join(lines) + '\n'


def outputs(root=ROOT):
    states, records = load(root)
    reg = registry()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator='\n')
    w.writeheader()
    w.writerows(rows(records))
    cov = coverage(states, records, reg)
    return {CSV_OUT: buf.getvalue(), COVERAGE_JSON: json.dumps(cov, indent=1) + '\n', COVERAGE_MD: coverage_md(cov)}


def cmd_build(_):
    for path, text in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print('wrote', path.relative_to(ROOT))


def cmd_check(_):
    stale = [p for p, t in outputs().items() if not p.exists() or p.read_text() != t]
    for p in stale:
        print('out of date:', p.relative_to(ROOT), file=sys.stderr)
    if stale:
        sys.exit('run: python3 scripts/bingo_pipeline.py build')
    print('bingo pipeline outputs are current')


def cmd_queue(a):
    today = a.today or date.today().isoformat()
    states, records = load()
    due = defaultdict(list)
    for code, name, level, r in records:
        _, d = _when(r, level)
        if d and d <= today:
            key = (code, level, r.get('source_url') or name)
            due[key].append(r['id'])
    print(f'# Due for recheck on {today}\n')
    if not due:
        print('Nothing is past its review date.')
    for (code, level, src), ids in sorted(due.items()):
        what = 'recheck the page' if level == 'organizer_schedule' else 'refresh the state list'
        print(f'- {code} {level}: {what} {src} ({len(ids)} listing{"s" if len(ids) > 1 else ""})')
    cov = coverage(states, records, registry())
    print('\n# Grow next (thinnest first)\n')
    for x in sorted(cov, key=lambda x: x['thin_rank'])[:a.top]:
        print(f"- {x['name']}: {x['places_with_days']} places with days, {x['counties_listed']}/{x['counties_total']} counties. "
              f"{x['next'] or 'Research organizer schedules (docs/BINGO-PIPELINE.md, step 2).'}")


def cmd_dupes(_):
    _, records = load()
    found = dupes(records)
    for (code, key), v in sorted(found.items()):
        print(f'{code} {key}:', '; '.join(f'{i} ({n})' for n, _, i in v))
    print(f'{len(found)} possible duplicates')


def zip_counties(path=None):
    raw = Path(path).read_bytes() if path else subprocess.run(['curl', '-sSL', ZIP_FILE], capture_output=True, check=True).stdout
    meta = json.loads((PUBLIC / 'us-zip-centroids-source.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == meta['source_sha256'], 'ZIP file checksum'
    return {r['code']: (r['state'], r['county'].title()) for r in csv.DictReader(io.StringIO(raw.decode())) if r['county']}


SESSION_KEYS = {'day', 'start', 'organization', 'label'}
RECORD_KEYS = {'id', 'state', 'kind', 'name', 'organizations', 'address', 'city', 'zip', 'county', 'phone', 'sessions',
               'schedule_note', 'notes', 'source_url', 'source_label', 'reviewed_on', 'sources'}


def check_record(r, zips):
    """The same rules the site build enforces for an organizer-schedule listing, so a bad batch fails here first."""
    code = r['state']
    errs = []
    if set(r) - RECORD_KEYS:
        errs.append('unknown fields ' + ', '.join(sorted(set(r) - RECORD_KEYS)))
    if not re.fullmatch(code.lower() + r'-[a-z0-9-]+', r.get('id', '')):
        errs.append('id must be "<state>-<slug>"')
    if r.get('kind') not in ('hall', 'senior_center'):
        errs.append('kind is hall or senior_center')
    if r.get('zip') not in zips:
        errs.append(f"ZIP {r.get('zip')} is not in findbingo-site/zips.json")
    if not r.get('address', '').endswith(f", {code} {r.get('zip')}") or r.get('city', '?') not in r.get('address', ''):
        errs.append('address must end ", ST ZIP" and contain the city')
    if not (r.get('name') and r.get('organizations') and r.get('sessions') and r.get('schedule_note')):
        errs.append('name, organizations, sessions and schedule_note are required')
    for s in r.get('sessions', []):
        if set(s) - SESSION_KEYS or type(s.get('day')) is not int or not 0 <= s['day'] <= 6:
            errs.append(f'bad session {s}')
        elif not (s.get('start') is None or fb.TIME.fullmatch(s['start'])):
            errs.append(f"start must be HH:MM or null: {s.get('start')}")
        elif s.get('organization') not in r.get('organizations', []):
            errs.append(f"session organization {s.get('organization')!r} is not in organizations")
    if 'phone' in r and not fb.PHONE.fullmatch(r['phone']):
        errs.append('phone must be NNN-NNN-NNNN')
    if not r.get('source_url', '').startswith('https://') or not r.get('source_label'):
        errs.append('source_url (https) and source_label are required')
    if not r.get('sources') or not all(x.get('url', '').startswith('https://') and x.get('scope') and x.get('reviewed_on') for x in r['sources']):
        errs.append('each source needs an https url, a scope and reviewed_on')
    try:
        date.fromisoformat(r.get('reviewed_on', ''))
    except ValueError:
        errs.append('reviewed_on must be a date')
    if any(not isinstance(n, str) or not n.strip() for n in r.get('notes', [])):
        errs.append('notes must be non-empty strings')
    return errs


def cmd_merge(a):
    batch = json.loads(Path(a.batch).read_text())
    codes = {r['state'] for r in batch}
    assert len(codes) == 1, 'one state per batch'
    code = codes.pop()
    target = PUBLIC / (fb.STARTER_FILES.get(code) or (_slug(fb.STATES[code]) + '-bingo.json'))
    zips = json.loads((ROOT / 'findbingo-site/zips.json').read_text())
    fb._load_zip_states(ROOT)
    county_of = zip_counties(a.zip_file) if any(not r.get('county') for r in batch) else {}
    existing = json.loads(target.read_text()) if target.exists() else []
    _, records = load()
    taken_ids = {r['id'] for _, _, _, r in records}
    taken_addr = {address_key(r.get('address'), _zip(r)): r['id'] for c, _, _, r in records if c == code}
    added, failed = [], 0
    for r in batch:
        if not r.get('county') and r.get('zip') in county_of and county_of[r['zip']][0] == code:
            r['county'] = county_of[r['zip']][1]
            print(f"{r['id']}: county {r['county']} from its ZIP code")
        errs = check_record(r, zips) + ([] if r.get('county') else ['county unknown'])
        if fb._state_of_zip(r.get('zip', '')) not in ('', code):
            errs.append('ZIP belongs to another state')
        if r['id'] in taken_ids:
            errs.append('id already listed')
        k = address_key(r.get('address'), r.get('zip'))
        if k in taken_addr:
            errs.append(f'same street and ZIP as {taken_addr[k]}: add its sessions there instead')
        if errs:
            failed += 1
            print(f"SKIP {r.get('id')}: " + '; '.join(errs))
            continue
        taken_ids.add(r['id'])
        taken_addr[k] = r['id']
        # The site lists a place's games Monday first, then by start time.
        r['sessions'].sort(key=lambda s: ((s['day'] + 6) % 7, s.get('start') or ''))
        added.append(r)
    out = sorted(existing + added, key=lambda r: (r['county'], r['city'], r['name'], r['id']))
    if a.dry_run:
        print(f'dry run: would add {len(added)} to {target.name}; {failed} skipped')
        return
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    print(f'added {len(added)} to {target.relative_to(ROOT)} ({len(out)} now); {failed} skipped')
    if code not in fb.STARTER_FILES:
        print(f"\n{fb.STATES[code]} is not a starter state yet. To publish it:\n"
              f"  1. scripts/findbingo_site.py: add '{code}': '{target.name}' to STARTER_FILES\n"
              f"  2. data/public/bingo-states.json: set {code} coverage to \"starter\" and add an hours_note\n"
              f"  3. data/bingo-sources/registry.json: update {code}'s next step\n"
              f"  4. python3 scripts/build_public.py && python3 scripts/bingo_pipeline.py build && node tests/findbingo.cjs")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('build').set_defaults(f=cmd_build)
    sub.add_parser('check').set_defaults(f=cmd_check)
    q = sub.add_parser('queue')
    q.add_argument('--today', help='YYYY-MM-DD (default: today)')
    q.add_argument('--top', type=int, default=10)
    q.set_defaults(f=cmd_queue)
    sub.add_parser('dupes').set_defaults(f=cmd_dupes)
    m = sub.add_parser('merge')
    m.add_argument('batch', help='JSON list of researched listings for one state (docs/BINGO-PIPELINE.md)')
    m.add_argument('--zip-file', help='a local copy of the Midwire ZIP file, for filling counties offline')
    m.add_argument('--dry-run', action='store_true')
    m.set_defaults(f=cmd_merge)
    a = p.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
