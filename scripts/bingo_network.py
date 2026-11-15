"""Build state editions from source-tracked records, without duplicating Ohio data."""
import json
import re
from datetime import date
from html import escape
from urllib.parse import quote

SITE = 'https://bingo.vethomeguard.org'

def validate(states, rows):
    codes = {s['code'] for s in states}
    ids = set()
    for r in rows:
        assert r['id'] not in ids, 'Duplicate venue ID: '+r['id']
        ids.add(r['id'])
        assert re.fullmatch(r'[a-z0-9-]+', r['id'])
        assert r['state'] in codes and r['state'] != 'OH'
        for field in ('name', 'city', 'address', 'admission', 'official_url', 'reviewed_on', 'review_due'):
            assert r.get(field), (r['id'], field)
        assert r['official_url'].startswith('https://')
        assert r['sources'] and all(s['url'].startswith('https://') for s in r['sources'])
        assert r['verification'] in ('published_source', 'organizer_confirmed', 'license_only')
        assert date.fromisoformat(r['review_due']) >= date.fromisoformat(r['reviewed_on'])
        assert all(isinstance(d,int) and 0 <= d <= 6 for d in r.get('session_days', []))
        for rule in r.get('session_monthly', []):
            assert 0 <= rule['weekday'] <= 6 and all(1 <= w <= 5 for w in rule['weeks'])
        for d in r.get('session_dates', []) + r.get('excluded_dates', []):
            date.fromisoformat(d)
        if r['state'] == 'UT':
            assert r['kind'] == 'free_recreation', 'Utah edition is free recreation only'


def card(r):
    e = escape
    contact = f'<a href="tel:{e(re.sub(r"[^+0-9]", "", r["phone"]))}">Call {e(r["phone"])}</a>' if r['phone'] else ''
    return f'''<article id="{e(r['id'])}" data-id="{e(r['id'])}"><span class="tag">{'Free recreation' if r['kind']=='free_recreation' else 'Bingo'}</span>
<h2>{e(r['name'])}</h2><p>{e(r['address'])}</p><p class="schedule">{e(r['schedule'] or 'Session schedule not yet confirmed. Check the organizer’s calendar.')}</p>
<p>{e(r['admission'])}</p><p class="small">{e(r['notes'])}</p><div class="actions"><a href="{e(r['official_url'])}">Organizer / source</a>{contact}<a href="mailto:travis@vethomeguard.org?subject={quote('Bingo correction: '+r['id'])}">Report a change</a></div>
<details><summary>Source and review details</summary><p>Published source reviewed {e(r['reviewed_on'])}. This is not direct organizer confirmation or a license check. Accessibility: ask the organizer.</p><ul>{''.join('<li><a href="'+e(s['url'])+'">'+e(s['scope'])+'</a></li>' for s in r['sources'])}</ul></details></article>'''


def outputs(root):
    states = json.loads((root/'data/bingo/states.json').read_text())
    rows = json.loads((root/'data/bingo/venues.json').read_text())
    validate(states, rows)
    template = (root/'templates/bingo/state.html').read_text()
    result = {}
    nav = ''.join(f'<a href="{("../" if s["code"]=="OH" else s["slug"]+".html")}">{escape(s["name"])}</a>' for s in states)
    for state in states:
        if state['code']=='OH':
            continue
        venues = sorted((r for r in rows if r['state']==state['code']), key=lambda r:(r['city'],r['name']))
        data = json.dumps({'state':state,'venues':venues},ensure_ascii=True).replace('<','\\u003c')
        values = {'NAME':escape(state['name']), 'SLUG':state['slug'], 'NAV':nav,
                  'NOTE':escape(state['note']), 'CARDS':''.join(card(r) for r in venues),
                  'DATA':data,'SOURCE_URL':escape(state['source_url']), 'SOURCE_LABEL':escape(state['source_label']),
                  'PARTNER':('Support free community activities through sponsorship. No gaming-proceeds arrangement is offered.' if state['code']=='UT' else 'Ask about advertising or supporting local veteran and community work. Listings are free; eligibility and any funding arrangement are reviewed separately.')}
        page = template
        for key,value in values.items():
            page=page.replace('{{'+key+'}}',value)
        result['bingo-site/states/'+state['slug']+'.html']=page
    cards=''.join(f'<article><h2>{escape(s["name"])}</h2><p>{escape(s["public_blurb"])}</p><a class="button" href="{("../" if s["code"]=="OH" else s["slug"]+".html")}">Find games in {escape(s["name"])}</a></article>' for s in states)
    result['bingo-site/states/index.html']=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Find bingo by state | Veteran Home Guardians</title><meta name="description" content="Find bingo and community activities in Ohio, Pennsylvania, New York, Washington and Utah."><link rel="canonical" href="{SITE}/states/"><link rel="stylesheet" href="../assets/bingo-network.css"></head><body><header><a href="../">Ohio Bingo Finder</a><p>Veteran Home Guardians</p><h1>Where do you want to play?</h1><p>Choose a state for local games, organizer details and community activities.</p></header><main><p class="notice">Ohio has established coverage. The other editions are growing starter lists, not complete statewide directories.</p><div class="grid">{cards}</div></main><footer>Free listings. Inclusion never depends on donations or advertising.</footer></body></html>'''
    for ext in ('js','css'):
        result['bingo-site/assets/bingo-network.'+ext]=(root/('templates/bingo/network.'+ext)).read_text()
    result['bingo-site/data/network-venues.json']=json.dumps(rows,indent=2,ensure_ascii=False)+'\n'
    result['bingo-site/data/network-states.json']=json.dumps(states,indent=2)+'\n'
    return result
