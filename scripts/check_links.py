#!/usr/bin/env python3
"""Request every link the guide publishes and print a Markdown report.

Covers each state's resource records and veterans office contacts (states/registry.json), the
family guide (data/family-guide.json), the country pages (data/world/countries.json) and the justice page (data/justice.json): the links visitors follow and the source links shown beside them.
Bingo listings have their own weekly report (scripts/check_schedule_freshness.py).

Exit 10 when a person needs to look: a link is broken or now goes to a different website.
(Any other failure exits as Python normally does, so a crash is never mistaken for a finding.)
It never changes data. See scripts/linkcheck.py for how each answer is sorted.

    python3 scripts/check_links.py                 check everything (about 20 minutes)
    python3 scripts/check_links.py --state TX      one state and nothing else
    python3 scripts/check_links.py --list          print the links and who uses them; no requests
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import linkcheck  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NEEDS_A_PERSON = 10


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def links_in(value):
    """Every web address anywhere inside a record."""
    if isinstance(value, str):
        if value.startswith(('http://', 'https://')):
            yield value.strip()
    elif isinstance(value, dict):
        for item in value.values():
            yield from links_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from links_in(item)


def collect(only_state=None):
    """{address: {who uses it}}. A record shared by every state is named once, as shared:<id>."""
    used = {}

    def add(record, who):
        for url in links_in(record):
            used.setdefault(url, set()).add(who)

    federal = set(read('data/public/federal-resource-ids.json'))
    for state in read('states/registry.json'):
        code = state['code']
        if only_state and code != only_state:
            continue
        for record in read(state['resources']):
            shared = record.get('state') == 'shared' or (state.get('base') and record['program_id'] in federal)
            add(record, ('shared' if shared else code) + ':' + record['program_id'])
        for office in read(state['offices']):
            add(office, code + ':' + office['county'] + ' veterans office')
    if not only_state:
        family = read('data/family-guide.json')
        for key in ('resources', 'sources', 'changes'):
            for item in family[key]:
                add(item, 'family guide:' + item['id'])
        for key in ('protection_advocacy', 'early_intervention', 'parent_centers'):
            for code, item in family[key].items():
                add(item, 'family guide:' + code + ' ' + key.replace('_', ' '))
        # Country pages for veterans outside the U.S. (data/world/countries.json).
        world = read('data/world/countries.json')
        add(world['us_abroad'], 'world:us-abroad')
        add(world['region_sources'], 'world:regions')
        for country in world['countries']:
            add(country, 'world:' + country['slug'])
        # Veterans in the justice system (data/justice.json).
        justice = read('data/justice.json')
        for section in justice['sections'] + [justice['ohio']]:
            for item in section['items']:
                add(item, 'justice:' + item['id'])
    return used


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--state', help='check one state only, by two-letter code')
    parser.add_argument('--list', action='store_true', help='print the links without requesting them')
    args = parser.parse_args()
    used = collect(args.state.upper() if args.state else None)
    if args.list:
        for url in sorted(used):
            print(url, '|', ', '.join(sorted(used[url])[:4]))
        print(len(used), 'links', file=sys.stderr)
        return
    results = linkcheck.Checker().check_all(sorted(used))
    text, needs_a_person = linkcheck.report(
        results, used,
        fix_hint='Correct the record in its source file (see README, "Update and verify"), then run `python3 scripts/build_public.py`.',
        ledger=linkcheck.load_ledger())
    print(text)
    sys.exit(NEEDS_A_PERSON if needs_a_person else 0)


if __name__ == '__main__':
    main()
