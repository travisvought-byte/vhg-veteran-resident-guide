import importlib.util, sys
from datetime import date
from pathlib import Path
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fresh', root / 'scripts/check_schedule_freshness.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
today = date(2026, 10, 29)
base = dict(county='Marion', phone='740-000-0000', reviewed_on='2026-10-20')
records = [
 dict(id='weekly', name='Weekly Hall', schedule='Tuesday 7 p.m.', session_days=[2], **base),
 dict(id='ended', name='Ended Event', schedule='Oct 18', session_dates=['2026-10-18'], **base),
 dict(id='soon', name='Soon Event', schedule='Nov 5', session_dates=['2026-11-05'], **base),
 dict(id='valid', name='Valid Until Past', schedule='Fall', session_days=[3], schedule_valid_until='2026-10-01', **base),
 dict(id='stale', name='Stale Hall', schedule='Friday', session_days=[5], **{**base, 'reviewed_on': '2026-08-01'}),
 dict(id='monthly', name='Monthly', schedule='First Thursday', session_monthly=[{'weekday': 4, 'weeks': [1]}], **base),
 dict(id='none', name='No Schedule', schedule=None, **base),
 dict(id='offer', name='Old Offer', schedule='Mon', session_days=[1], cost='$20', price_valid_until='2026-10-10', **base),
]
expired, soon, stale, offers = m.classify(records, today)
assert {r['id'] for r, _ in expired} == {'ended', 'valid'}, expired
assert {r['id'] for r, _ in soon} == {'soon'}
assert {r['id'] for r, _ in stale} == {'stale'}
assert {r['id'] for r, _ in offers} == {'offer'}
# Open-ended weekly and monthly schedules are never "ended", and a record with no schedule is ignored.
assert 'weekly' not in {r['id'] for r, _ in expired + soon} and 'monthly' not in {r['id'] for r, _ in expired + soon}
text = m.report(records, today)
assert '7 listings have a published schedule. 2 have ended, 1 end within 14 days, 1 were last reviewed more than 30 days ago.' in text, text
assert '**Stale Hall** (Marion) last reviewed 89 days ago. 740-000-0000' in text
# The real data loads and produces a report without error.
real = m.report(m.load(), today)
assert real.startswith('Bingo schedule freshness, 2026-10-29') and '## Ended' in real
print('PASS: schedule freshness report classifies ended, ending soon, stale and expired offers.')
