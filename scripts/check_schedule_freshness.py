#!/usr/bin/env python3
"""Report bingo schedules that have expired, are about to, or have not been rechecked recently.

Usage: python3 scripts/check_schedule_freshness.py [--today YYYY-MM-DD] [--stale-days 30] [--soon-days 14]

Prints a Markdown report. It never changes data. The page already hides expired schedules at display time;
this report tells the maintainer which listings need a fresh look so the directory does not quietly decay.
"""
import argparse, json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load():
    seen, out = set(), []
    for name in ('ohio-bingo-authorized.json', 'ohio-bingo.json', 'ohio-community-centers.json'):
        for r in json.loads((ROOT / 'data/public' / name).read_text()):
            if r['id'] not in seen:
                seen.add(r['id'])
                out.append(r)
    return out

def last_date(r):
    """Last date a published schedule runs through, or None for open-ended weekly schedules."""
    ends = []
    if r.get('schedule_valid_until'):
        ends.append(r['schedule_valid_until'])
    if r.get('session_dates') and not r.get('session_days') and not r.get('session_monthly'):
        ends.append(max(r['session_dates']))
    return min(ends) if ends else None

def classify(records, today, stale_days=30, soon_days=14):
    expired, soon, stale, offers = [], [], [], []
    for r in records:
        if not r.get('schedule'):
            continue
        end = last_date(r)
        if end and end < today.isoformat():
            expired.append((r, end))
            continue
        if end and end <= (today + timedelta(days=soon_days)).isoformat():
            soon.append((r, end))
        age = (today - date.fromisoformat(r['reviewed_on'])).days
        if age > stale_days:
            stale.append((r, age))
    for r in records:
        if r.get('price_valid_until') and r['price_valid_until'] < today.isoformat() and r.get('cost'):
            offers.append((r, r['price_valid_until']))
    return expired, soon, stale, offers

def line(r, note):
    contact = r.get('phone') or r.get('official_url') or 'no public contact'
    return f"- **{r['name'][:70]}** ({r['county']}) {note}. {contact}"

def report(records, today, stale_days=30, soon_days=14):
    expired, soon, stale, offers = classify(records, today, stale_days, soon_days)
    total = sum(1 for r in records if r.get('schedule'))
    lines = [f"Bingo schedule freshness, {today.isoformat()}", '',
             f"{total} listings have a published schedule. {len(expired)} have ended, {len(soon)} end within {soon_days} days, "
             f"{len(stale)} were last reviewed more than {stale_days} days ago.", '']
    for title, items, fmt in [
        ('Ended: the page already hides these; they need a new schedule or removal of the old text', expired, lambda e: f"ended {e}"),
        (f'Ending within {soon_days} days', soon, lambda e: f"ends {e}"),
        (f'Not reviewed in over {stale_days} days: recheck the organizer page or call', sorted(stale, key=lambda x: -x[1]), lambda e: f"last reviewed {e} days ago"),
        ('Price offers that have ended', offers, lambda e: f"offer ended {e}")]:
        lines.append(f"## {title} ({len(items)})")
        lines.extend(line(r, fmt(e)) for r, e in items) if items else lines.append('None.')
        lines.append('')
    return '\n'.join(lines)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--today', default=date.today().isoformat())
    p.add_argument('--stale-days', type=int, default=30)
    p.add_argument('--soon-days', type=int, default=14)
    a = p.parse_args()
    print(report(load(), date.fromisoformat(a.today), a.stale_days, a.soon_days))
