"""Turn harvest files into one normalized, deduplicated candidates table, matched against what is published.

    python3 scripts/mining/candidates.py           # rewrite data/mining/candidates.csv
    python3 scripts/mining/candidates.py --check   # fail if the committed table is out of date

A harvest file (data/mining/harvest/<source id>-<date>.json) records what one source said, row by row, with how it
was read. This step gives each row a stable id, an evidence level and a status:

  new               nothing published matches it yet; ready to be added to a state edition
  already_published its phone is already on a published record for that state
  phone_conflict    the state already lists a different phone for that county and kind; a person decides which holds
  uncertain         the source itself is unclear (no phone, or a value not tied to the row); never published as is
  duplicate         the same county, kind and phone appeared earlier in the harvest; kept for the record only

It reads only files in this repository.
"""
import argparse
import csv
import hashlib
import io
import sys

import common as c

COLUMNS = ['candidate_id', 'status', 'state', 'county', 'country', 'category', 'name', 'organization', 'phone',
           'other_phones', 'address', 'hours', 'website', 'evidence_level', 'review_method', 'confidence',
           'source_id', 'source_url', 'source_title', 'retrieved_on', 'dedupe_key', 'published_match', 'note']


def published_index():
    """Per state: phone digits -> where published, and (county, kind) -> published phones."""
    phones, by_county = {}, {}
    for state in c.registry():
        offices, records = c.state_records(state)
        code = state['code']
        for o in offices:
            nums = [o.get('phone')] + list(o.get('other_phones') or [])
            for n in nums:
                if c.digits(n):
                    phones.setdefault(code, {}).setdefault(c.digits(n), f"office:{o.get('county')}")
            if c.office_class(o) != 'fallback':
                by_county.setdefault(code, {}).setdefault((o.get('county'), 'veterans_office'), set()).update(
                    c.digits(n) for n in nums if c.digits(n))
        for r in records:
            n = (r.get('public_contact') or {}).get('phone')
            if c.digits(n):
                phones.setdefault(code, {}).setdefault(c.digits(n), f"record:{r.get('program_id')}")
    return phones, by_county


def rows():
    phones, by_county = published_index()
    seen = set()
    out = []
    for path in sorted((c.MINING / 'harvest').glob('*.json')):
        h = c.read(path)
        for row in h['rows']:
            state, county, kind = row.get('state'), row.get('county'), row['category']
            key = '|'.join([state or row.get('country') or '', county or '', kind, c.digits(row.get('phone'))])
            cid = hashlib.sha256('|'.join([h['source_id'], key, row.get('name') or '']).encode()).hexdigest()[:16]
            match = phones.get(state, {}).get(c.digits(row.get('phone'))) if row.get('phone') else None
            listed = by_county.get(state, {}).get((county, kind))
            if key in seen:
                status = 'duplicate'
            elif row.get('confidence') == 'uncertain' or not row.get('phone'):
                status = 'uncertain'
            elif match:
                status = 'already_published'
            elif listed and c.digits(row['phone']) not in listed:
                status = 'phone_conflict'
            else:
                status = 'new'
            seen.add(key)
            out.append({
                'candidate_id': cid, 'status': status, 'state': state or '', 'county': county or '',
                'country': row.get('country') or ('US' if state else ''), 'category': kind,
                'name': row.get('name') or '', 'organization': row.get('organization') or '',
                'phone': row.get('phone') or '', 'other_phones': '; '.join(row.get('other_phones') or []),
                'address': row.get('address') or '', 'hours': row.get('hours') or '', 'website': row.get('website') or '',
                'evidence_level': c.level_of(row.get('review_method') or h['review_method']),
                'review_method': row.get('review_method') or h['review_method'],
                'confidence': row.get('confidence') or '', 'source_id': h['source_id'],
                'source_url': row.get('source_url') or h['source_url'], 'source_title': h['source_title'],
                'retrieved_on': h['retrieved_on'], 'dedupe_key': key, 'published_match': match or '',
                'note': row.get('note') or '',
            })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    table = rows()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator='\n')
    w.writeheader()
    w.writerows(table)
    ok = c.check_or_write(c.MINING / 'candidates.csv', buf.getvalue(), args.check)
    counts = {}
    for r in table:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'{len(table)} candidate rows: ' + ', '.join(f'{v} {k}' for k, v in sorted(counts.items())))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
