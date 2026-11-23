"""Shared helpers for the resource-mining pipeline (docs/MINING.md).

Everything here reads the repository only. Nothing in this module touches the network.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MINING = ROOT / 'data' / 'mining'

# Evidence ladder, strongest first. Every mined row and every published record maps to one level, so a
# coverage report can say how strong a state's listings are, not only how many there are.
#   A  the agency itself confirmed the contact (phone call, email reply) and the confirmation is recorded
#   B  the official source itself was read in full: page text, PDF, spreadsheet or open dataset
#   C  an official source seen only through a search excerpt, page metadata or a partial read
#   D  a secondary published directory (an association guidebook, a national directory)
#   E  a lead only: social posts, AI output, unofficial aggregators. Never published.
LEVELS = 'ABCDE'
METHOD_LEVEL = {
    'full_official_page_text': 'B', 'full_official_pdf': 'B', 'full_official_spreadsheet': 'B',
    'official_dataset': 'B', 'official_pdf_text_extract': 'B', 'page_text_reviewed': 'B', 'full_official_page': 'B',
    'official_source_reviewed': 'B',
    'official_search_excerpt': 'C', 'official_search_extract_only': 'C', 'official_page_metadata': 'C',
    'partial_official_page_text': 'C', 'official_website': 'C', 'needs_recheck': 'C',
    'published_directory': 'D', 'secondary_directory': 'D', 'full_association_directory_page': 'D',
    'lead_only': 'E', 'imported_unverified': 'E',
}

# How often each kind of published record is due for another look (docs/MAINTENANCE.md, review priorities).
CADENCE_DAYS = {'veterans_office': 90, 'aging_agency': 90, 'ombudsman': 90, 'program': 180, 'country_line': 180}

# Office types that count as a contact in or for the county itself, a regional team, or a statewide fallback.
LOCAL_OFFICE = {None, 'county', 'city', 'independent_city', 'borough', 'census_area', 'parish', 'state_field_office'}
REGIONAL_OFFICE = {'regional'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def digits(phone):
    """Ten-digit U.S. phone key ('(501) 683-2382' -> '5016832382'); other lengths are kept as written."""
    d = re.sub(r'\D', '', phone or '')
    return d[1:] if len(d) == 11 and d.startswith('1') else d


def url_key(url):
    """Scheme-, www- and trailing-slash-insensitive URL key."""
    u = (url or '').strip().lower()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    return u.rstrip('/')


def level_of(method, confirmed=False):
    if confirmed:
        return 'A'
    return METHOD_LEVEL.get(method or '', 'C' if method else 'D')


def office_class(office):
    t = office.get('office_type')
    if t in REGIONAL_OFFICE:
        return 'regional'
    if t in LOCAL_OFFICE:
        return 'local'
    return 'fallback'  # 'statewide', 'state': the county shows the state agency's statewide line


def registry():
    return read(ROOT / 'states' / 'registry.json')


def state_records(state):
    """(offices, records) published for one registered state. Records are its own programs and regional referrals
    (shared federal records are left out, so every state is measured on its own research)."""
    offices = read(ROOT / state['offices'])
    if state.get('base'):
        records = [r for r in read(ROOT / state['resources']) if r.get('state') not in ('shared',)]
    else:
        records = read(ROOT / state['programs']) + read(ROOT / state['referrals'])
    return offices, records


def days_since(iso, today=None):
    if not iso:
        return None
    try:
        y, m, d = (int(x) for x in iso[:10].split('-'))
        return ((today or date.today()) - date(y, m, d)).days
    except ValueError:
        return None


def office_method(office):
    """(review_method, confirmed) for a published veterans-office record."""
    ev = office.get('evidence') if isinstance(office.get('evidence'), dict) else {}
    method = ev.get('review_method') or office.get('review_method') or office.get('contact_status')
    return method, bool(ev.get('direct_agency_confirmation') or office.get('direct_agency_confirmation'))


def record_method(record):
    """(review_method, confirmed) for a published program or referral record."""
    ev = record.get('evidence') if isinstance(record.get('evidence'), dict) else {}
    method = ev.get('review_method') or (record.get('verification') or {}).get('record_status')
    return method, bool(ev.get('direct_agency_confirmation'))


def record_reviewed_on(record):
    return (record.get('verification') or {}).get('last_reviewed_on')


def office_sources(office):
    """Every source URL an office record rests on."""
    ev = office.get('evidence') if isinstance(office.get('evidence'), dict) else {}
    urls = [office.get('source_url'), office.get('details_source_url')]
    urls += [v for k, v in ev.items() if k.endswith('source_url') and isinstance(v, str)]
    return [u for u in dict.fromkeys(urls) if u]


def record_sources(record):
    """Every source URL a program or referral record rests on; its own website when it names no other."""
    ev = record.get('evidence') if isinstance(record.get('evidence'), dict) else {}
    urls = [v for k, v in ev.items() if k.endswith('source_url') and isinstance(v, str)]
    urls += [e.get('url') for e in (record.get('source_evidence') or []) if isinstance(e, dict)]
    urls = [u for u in dict.fromkeys(urls) if u]
    return urls or [u for u in [record.get('official_url')] if u]


def add_days(iso, days):
    from datetime import timedelta
    y, m, d = (int(x) for x in iso[:10].split('-'))
    return (date(y, m, d) + timedelta(days=days)).isoformat()


def check_or_write(path, text, check):
    """Write a generated file, or with check=True report whether the committed copy is current."""
    path = Path(path)
    if check:
        current = path.read_text(encoding='utf-8') if path.exists() else None
        if current != text:
            print(f'{path.relative_to(ROOT)} is out of date. Run the script without --check and commit the result.')
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return True
