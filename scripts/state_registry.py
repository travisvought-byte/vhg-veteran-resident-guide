"""State registry and the shared state-edition builder.

Every state is listed once in states/registry.json. A non-base state also has:

  states/<code>/edition.json  ordered text, routing and markup operations applied
                              to the shared guide template
  states/<code>/adapter.js    state-specific interface functions, one per line

Adding a state takes its three canonical data files, one registry entry, and the
two files above. No Python changes are needed. See docs/ADDING-A-STATE.md.
"""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://travisvought-byte.github.io/vhg-veteran-resident-guide/'


def replace_line(html, prefix, new):
    """Replace the single template line that starts with prefix."""
    html, n = re.subn(r'^' + re.escape(prefix) + r'.*$', lambda _: new, html, count=1, flags=re.M)
    if n != 1:
        raise ValueError('Missing template section: ' + prefix)
    return html


def load_registry(root=ROOT):
    """Return registered states in menu order, each with its edition operations."""
    states = json.loads((root / 'states/registry.json').read_text())
    codes = [s['code'] for s in states]
    if len(set(codes)) != len(codes):
        raise ValueError('Duplicate state code in registry')
    if sum(bool(s.get('base')) for s in states) != 1 or not states[0].get('base'):
        raise ValueError('The first registry entry must be the single base edition')
    for state in states:
        if state.get('base'):
            continue
        folder = root / 'states' / state['code'].lower()
        state['ops'] = json.loads((folder / 'edition.json').read_text())['ops']
        state['adapter'] = [line for line in (folder / 'adapter.js').read_text().splitlines() if line.strip()]
    return states


def load_counties(root, state):
    return json.loads((root / state['offices']).read_text())


def state_resources(root, base_resources, state):
    """Shared federal records first, then the state's programs and regional referrals."""
    ids = json.loads((root / 'data/public/federal-resource-ids.json').read_text())
    by_id = {r['program_id']: r for r in base_resources}
    shared = []
    for program_id in ids:
        record = copy.deepcopy(by_id[program_id])
        record.update(service_area=['National'], state='shared')
        shared.append(record)
    return (shared + json.loads((root / state['programs']).read_text())
            + json.loads((root / state['referrals']).read_text()))


def _payload(value):
    # Escape HTML parser boundaries inside strings while retaining valid JSON.
    return json.dumps(value, ensure_ascii=True).replace('<', '\\u003c')


def _apply_adapter(html, lines):
    for line in lines:
        name = re.match(r'function (\w+)\(', line).group(1)
        if re.search(r'^function ' + re.escape(name) + r'\(', html, flags=re.M):
            html = replace_line(html, 'function ' + name + '(', line)
        else:
            # Helper functions the template lacks are added just before officeCard.
            html = html.replace('function officeCard(', line + '\nfunction officeCard(', 1)
    return html


def make_edition(html, state, resources, counties):
    """Apply a state's operations to the shared template, then embed its data."""
    for op in state['ops']:
        kind = op['op']
        if kind == 'clear_data':
            # Remove base payloads before adapting text: state data must never be relabeled.
            html = replace_line(html, 'const DATA=', 'const DATA=[];')
            html = replace_line(html, 'const COUNTIES=', 'const COUNTIES=[];')
        elif kind == 'replace':
            html = html.replace(op['old'], op['new'], op.get('count', -1))
        elif kind == 'regex':
            flags = (re.S if op.get('dotall') else 0) | (re.M if op.get('multiline') else 0)
            html = re.sub(op['pattern'], op['new'], html, count=op.get('count', 0), flags=flags)
        elif kind == 'line':
            html = replace_line(html, op['prefix'], op['new'])
        elif kind == 'declare':
            html = replace_line(html, 'const ' + op['name'] + '=', 'const ' + op['name'] + '=' + json.dumps(op['value']) + ';')
        elif kind == 'adapter':
            html = _apply_adapter(html, state['adapter'])
        elif kind == 'embed_data':
            html = replace_line(html, 'const DATA=', 'const DATA=' + _payload(resources) + ';')
            html = replace_line(html, 'const COUNTIES=', 'const COUNTIES=' + _payload(counties) + ';')
        else:
            raise ValueError(state['code'] + ': unknown edition operation ' + kind)
    return html


def make_share(share, state):
    """Derive a state's sharing kit from the base sharing page."""
    page = state['page']
    out = share.replace('Ohio', state['name']).replace('88', str(state['counties'])).replace('href="index.html"', 'href="' + page + '"')
    out = out.replace(BASE_URL, BASE_URL + page).replace('assets/guide-qr.svg', state['qr'])
    out = out.replace('href="share.html">' + state['name'], 'href="share.html">Ohio')
    out = out.replace('local veterans office, aging agency and long-term-care ombudsman contacts', state['share_description'])
    for old, new in state.get('share_replacements', []):
        out = out.replace(old, new)
    return out


def add_share_links(share, states):
    """Make sure the base sharing page links every state's sharing kit, in menu order."""
    previous = None
    for state in states:
        if state.get('base'):
            continue
        link = '<a href="' + state['share_page'] + '">' + state['name'] + '</a>'
        if 'href="' + state['share_page'] + '"' not in share and previous:
            share = share.replace(previous, previous + ' · ' + link)
        previous = link
    return share


def add_state_options(html, states):
    """Make sure the template's state menu lists every registered state, in order."""
    previous = None
    for state in states:
        option = '<option value="' + state['code'] + '">' + state['name'] + '</option>'
        if option not in html and previous:
            html = html.replace(previous, previous + option)
        previous = option
    pages = ','.join(s['code'] + ":'" + s['page'] + "'" for s in states)
    return replace_line(html, 'function editionURL(state)',
                        "function editionURL(state){const pages={" + pages + "};const u=new URL(pages[state]||pages.OH,location.href);if(route!=='priority')u.searchParams.set('view',route);return u}")
