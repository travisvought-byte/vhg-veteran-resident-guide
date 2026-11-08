#!/usr/bin/env python3
"""Build the family guide for children with autism, ADHD and other disabilities.

Canonical data: data/family-guide.json. Ohio county names come from the county
veterans office file; pilot-county DD intake contacts come from prototype-data.json,
so both stay single-sourced.
"""
import html
import json
from datetime import date
from pathlib import Path
from build_mobility_routes import STATES

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {'US': 'National', 'OH': 'Ohio', 'MIL': 'Military & veteran families'}
CORRECTIONS = 'travis@vethomeguard.org'


def esc(value):
    return html.escape(str(value), quote=True)


def tel(phone):
    return 'tel:' + ''.join(ch for ch in phone if ch.isdigit())


def validate(data):
    assert data['publication_status'] == 'published-source-snapshot'
    reviewed = date.fromisoformat(data['reviewed_on'])
    assert reviewed <= date.today()
    sources = {s['id']: s for s in data['sources']}
    assert len(sources) == len(data['sources'])
    for s in data['sources']:
        assert s['url'].startswith('https://') and s['title'] and s['publisher'], s['id']
        assert date.fromisoformat(s['reviewed_on']) <= reviewed, s['id']
    stages = {s['id'] for s in data['stages']}
    needs = {n['id'] for n in data['needs']} | {'any'}
    ids = [r['id'] for r in data['resources']]
    assert len(ids) == len(set(ids))
    for r in data['resources']:
        assert r['scope'] in SCOPES, r['id']
        assert r['name'] and r['org'] and r['what'] and r['how'], r['id']
        assert r['url'].startswith('https://'), r['id']
        assert r['stages'] and set(r['stages']) <= stages, r['id']
        assert r['needs'] and set(r['needs']) <= needs, r['id']
        assert r['sources'] and all(s in sources for s in r['sources']), r['id']
        for state, replacement in r.get('state_replacements', {}).items():
            assert r['scope'] == 'US' and state in STATES and replacement in ids, r['id']
    pa = data['protection_advocacy']
    assert set(pa) == set(STATES), set(STATES) ^ set(pa)
    for code, agency in pa.items():
        assert agency['name'] and agency['url'].startswith('https://') and agency['phone'], code
    for change in data['changes']:
        assert all(s in sources for s in change['sources']), change['id']
    return data


def ohio_counties():
    counties = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    programs = json.loads((ROOT / 'prototype-data.json').read_text())
    intake = {}
    for p in programs:
        if p['program_id'].endswith('-dd-intake') and p.get('public_contact', {}).get('phone'):
            for county in p['service_area']:
                intake[county] = {'name': p['name'], 'phone': p['public_contact']['phone'],
                                  'url': p['official_url'],
                                  'reviewed_on': p['verification'].get('last_reviewed_on')}
    names = sorted(c['county'] for c in counties)
    assert len(names) == 88
    assert set(intake) <= set(names)
    return [{'county': n, 'dd': intake.get(n)} for n in names]


def card(r, sources, stage_names):
    phone = ''
    if r['phone']:
        label = f' <span class="small">({esc(r["phone_label"])})</span>' if r['phone_label'] else ''
        phone = f'<p class="contact"><a href="{tel(r["phone"])}">{esc(r["phone"])}</a>{label}</p>'
    cites = ''.join(
        f'<li><a href="{esc(sources[s]["url"])}" target="_blank" rel="noopener">{esc(sources[s]["title"])}</a>'
        f' · {esc(sources[s]["publisher"])} · checked {esc(sources[s]["reviewed_on"])}</li>'
        for s in r['sources'])
    stage_text = ' · '.join(stage_names[s] for s in r['stages'])
    replaced = ' '.join(f'{k}:{v}' for k, v in r.get('state_replacements', {}).items())
    return (
        f'<article class="resource" id="r-{esc(r["id"])}" data-id="{esc(r["id"])}" data-scope="{r["scope"]}"'
        f' data-stages="{" ".join(r["stages"])}" data-needs="{" ".join(r["needs"])}"'
        + (f' data-replaced="{esc(replaced)}"' if replaced else '') + '>'
        f'<p class="eyebrow"><span class="scope scope-{r["scope"].lower()}">{SCOPES[r["scope"]]}</span> {esc(r["org"])}</p>'
        f'<h3>{esc(r["name"])}</h3><p>{esc(r["what"])}</p>'
        f'<p class="next"><strong>Next step:</strong> {esc(r["how"])}</p>{phone}'
        f'<p><a class="visit" href="{esc(r["url"])}" target="_blank" rel="noopener">Visit website<span class="sr"> for {esc(r["name"])}</span> (new tab)</a></p>'
        f'<p class="small stage-list">For: {esc(stage_text)}</p>'
        f'<details><summary>Sources</summary><ul>{cites}</ul></details>'
        f'<p class="small"><a class="report" data-report="{esc(r["id"])}" href="mailto:{CORRECTIONS}?subject='
        f'{esc("Family guide correction: " + r["id"])}">Report a problem with this listing</a></p></article>')


def outputs():
    data = validate(json.loads((ROOT / 'data/family-guide.json').read_text()))
    sources = {s['id']: s for s in data['sources']}
    stage_names = {s['id']: s['label'] for s in data['stages']}
    counties = ohio_counties()
    page_data = dict(data, ohio_counties=counties, states=STATES)
    cards = [card(r, sources, stage_names) for r in data['resources'] if r['scope'] != 'MIL']
    military = [card(r, sources, stage_names) for r in data['resources'] if r['scope'] == 'MIL']
    state_options = ''.join(f'<option value="{c}"' + (' selected' if c == 'OH' else '') + f'>{esc(n)}</option>'
                            for c, n in STATES.items())
    county_options = '<option value="">Choose a county</option>' + ''.join(
        f'<option value="{esc(c["county"])}">{esc(c["county"])} County</option>' for c in counties)
    stage_buttons = '<button type="button" class="stage" data-stage="all" aria-pressed="true"><strong>Show everything</strong><span>All ages and topics</span></button>' + ''.join(
        f'<button type="button" class="stage" data-stage="{s["id"]}" aria-pressed="false"><strong>{esc(s["label"])}</strong><span>{esc(s["ages"])} · {esc(s["summary"])}</span></button>'
        for s in data['stages'])
    need_boxes = ''.join(
        f'<label class="check"><input type="checkbox" name="need" value="{n["id"]}"> {esc(n["label"])}</label>'
        for n in data['needs'])
    changes = ''.join(
        f'<article><h3>{esc(c["title"])}</h3><p>{esc(c["text"])}</p><p class="small">Sources: '
        + ' · '.join(f'<a href="{esc(sources[s]["url"])}" target="_blank" rel="noopener">{esc(sources[s]["title"])}</a>' for s in c['sources'])
        + '</p></article>' for c in data['changes'])
    oh = data['protection_advocacy']['OH']
    anchors = (
        f'<li><strong>Parent center:</strong> <a href="https://www.ocecd.org/" target="_blank" rel="noopener">OCECD</a> · <a href="tel:8443825452">844-382-5452</a></li>'
        f'<li><strong>Disability rights and legal help:</strong> <a href="{esc(oh["url"])}" target="_blank" rel="noopener">{esc(oh["name"])}</a> · <a href="{tel(oh["phone"])}">{esc(oh["phone"])}</a></li>'
        f'<li><strong>Under age 3:</strong> Help Me Grow Early Intervention · <a href="tel:8007554769">800-755-4769</a></li>'
        f'<li><strong>County developmental disability services:</strong> <a href="https://www.oacbdd.org/familyresources" target="_blank" rel="noopener">find your county board of DD</a> · <a href="tel:8006176733">800-617-6733</a></li>')
    page = (ROOT / 'templates/family-guide.html').read_text()
    for key, value in {
        '__STATES__': state_options, '__COUNTIES__': county_options, '__STAGES__': stage_buttons,
        '__NEEDS__': need_boxes, '__CARDS__': '\n'.join(cards), '__MILITARY__': '\n'.join(military),
        '__CHANGES__': changes, '__ANCHORS__': anchors, '__REVIEWED__': data['reviewed_on'],
        '__COUNT__': str(len(cards)),
        '__DATA__': json.dumps(page_data, ensure_ascii=False).replace('<', '\\u003c'),
    }.items():
        assert key in page, key
        page = page.replace(key, value)
    return {'family-guide.html': page}


if __name__ == '__main__':
    for path, text in outputs().items():
        (ROOT / path).write_text(text)
    print('Built family guide: stages, needs, national/Ohio/military resources and 51 rights agencies.')
