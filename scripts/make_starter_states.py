#!/usr/bin/env python3
"""Generate starter state editions from data/starter-states.json.

A starter edition is for a state that has no county-level research yet. It has one
statewide locality ("All <State> counties") that routes to the state veterans agency,
plus national locators for local aging help, the long-term-care ombudsman and free
Medicare counseling (SHIP). When a state gets full county research, delete its entry
from data/starter-states.json and replace the generated files with a full edition
(docs/ADDING-A-STATE.md).

This writes, for each starter state:
  data/public/<slug>-county-veterans-offices.json, <code>-programs.json,
  <code>-regional-referrals.json, states/<code>/edition.json, states/<code>/adapter.js,
and adds or refreshes its entry in states/registry.json. Then run build_public.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# A state's "review" field says how its veterans contact was checked: "page" means the agency's own
# page was opened and read; anything else means it was matched through search excerpts of that page.
STATUS = {'page': 'official_source_reviewed'}
METHOD = {'page': 'full_official_page_text'}


def slug(name):
    return name.lower().replace(' ', '-')


def area_name(s):
    return s.get('area') or 'All ' + s['name'] + ' counties'


def record(pid, s, name, org, url, phone, needs, description, next_step, reviewed, source, role=None, area=None, constraints=None, review=None):
    r = {'program_id': pid, 'name': name, 'official_url': url, 'organization': org,
         'service_area': [area] if area else ['statewide'], 'state': s['code'],
         'needs_supported': needs, 'description': description, 'next_step': next_step,
         'constraints': constraints or [], 'public_contact': {'phone': phone},
         'verification': {'record_status': STATUS.get(review, 'official_search_extract_only'), 'last_reviewed_on': reviewed},
         'evidence': {'review_method': METHOD.get(review, 'official_search_excerpt'), 'direct_agency_confirmation': False, 'phone_source_url': source},
         'source_evidence': [{'url': source, 'title': 'Official published source', 'scope': 'Name and phone matched to the publisher’s own page on ' + reviewed + '; not direct intake confirmation.'}]}
    if role:
        r['regional_role'] = role
    return r


SSVF_PAGE = 'https://department.va.gov/homeless/supportive-services-for-veteran-families/'


def ssvf_records(s, area, reviewed):
    """Statewide-area cards for each VA SSVF grantee that serves this state, from the FY26 intake list projection."""
    src = json.loads((ROOT / 'data/public/ssvf-intake-fy26.json').read_text())
    out = []
    for g in src['records']:
        counties = [c['name'] for c in g['counties'] if c['state'] == s['code']]
        if not counties:
            continue
        phones = g['intake_phones']
        where = ', '.join(counties) if len(counties) <= 12 else ', '.join(counties[:12]) + ' and ' + str(len(counties) - 12) + ' more'
        nxt = ('Call SSVF intake' if phones else 'Ask VA’s National Call Center for Homeless Veterans (877-424-3838) to connect you') + \
              ' with your county and housing situation: whether you are homeless now or at risk of losing housing, and who lives with you.'
        if len(phones) > 1:
            nxt += ' A second intake number is listed: ' + phones[1] + '.'
        r = {'program_id': s['code'].lower() + '-ssvf-' + g['fain'].lower(), 'name': g['organization'] + ': veteran housing help (SSVF)',
             'official_url': SSVF_PAGE, 'organization': g['organization'], 'service_area': [area], 'state': s['code'],
             'resource_role': 'housing_provider', 'needs_supported': ['housing', 'veteran_services'],
             'description': 'VA-funded Supportive Services for Veteran Families (SSVF, grant ' + g['fain'] + '): case management, help keeping a home, rapid rehousing and short-term financial help for low-income veteran households. Serves: ' + where + '.',
             'next_step': nxt,
             'constraints': ['Serves only the areas listed; check that yours is included. Veteran-household, income and housing-status screening applies.',
                             'County and intake details come from VA’s FY26 SSVF provider intake list; confirm current service when calling.'],
             'public_contact': {'phone': phones[0] if phones else None, 'phone_label': 'VA-listed SSVF intake'},
             'verification': {'record_status': 'official_source_reviewed', 'last_reviewed_on': src['reviewed_on']},
             'evidence': {'review_method': 'full_official_spreadsheet', 'direct_agency_confirmation': False, 'service_area_source_url': src['source_url']},
             'source_evidence': [{'url': src['source_url'], 'title': 'VA SSVF provider intake list (FY26)', 'reviewed_on': src['reviewed_on'],
                                  'scope': 'County coverage and SSVF intake; Contacts worksheet row ' + str(g['row']), 'sheet': src['sheet'], 'row': g['row'], 'source_sha256': src['source_sha256']}]}
        out.append(r)
    return out


ADAPTER = r'''
function agingContactsHTML(county){return DATA.filter(x=>x.regional_role==='aging_agency').map(x=>'<p><strong>'+esc(x.name)+'</strong><br>'+phoneLink(x.public_contact.phone)+'</p><p>Give the ZIP code or town where help is needed. The Eldercare Locator connects you to the local aging agency and services.</p><p class="meta"><a href="'+esc(x.official_url)+'" target="_blank" rel="noopener">Search by ZIP code</a> · '+esc(x.verification.last_reviewed_on)+'</p>').join('')}
function officeCard(c){return `<article class="office-card"><span class="badge">${esc(c.county)} · statewide veterans agency</span><h2>${esc(c.organization)}</h2><p>${phoneLink(c.phone)}</p><p>${esc(c.note)}</p><p>Ask for free, accredited help with VA claims, a benefits review and the office that serves your county.</p>${c.local_url?`<p><a href="${esc(c.local_url)}" target="_blank" rel="noopener">Find a local veterans office</a></p>`:''}<p class="meta"><a href="${esc(sourceURL(c))}" target="_blank" rel="noopener">Official contact source</a> · Reviewed ${esc(c.reviewed_on)}. Starter edition: county offices are not listed here yet.</p></article>`}
function renderOfficeList(){$('office-list').innerHTML=COUNTIES.map(c=>'<div class="office-row"><button data-county="'+esc(c.county)+'">'+esc(c.county)+'</button><p>'+esc(c.organization)+' · '+phoneLink(c.phone)+'</p>'+(c.local_url?'<a href="'+esc(c.local_url)+'" target="_blank" rel="noopener">Local offices</a>':'<a href="'+esc(sourceURL(c))+'" target="_blank" rel="noopener">Contact source</a>')+'</div>').join('');document.querySelectorAll('[data-county]').forEach(b=>b.onclick=()=>{$('county').value=b.dataset.county;render();$('county-start').scrollIntoView({behavior:'smooth'})})}
function renderCounty(){$('print-handoff-status').textContent='';const c=COUNTIES.find(c=>c.county===$('county').value);$('print-county').textContent=c?'@@NAME@@ (statewide contacts)':'@@NAME@@ statewide resources';if(!c){$('county-panel').innerHTML='<p>Choose “@@AREA@@” for @@NAME@@ veterans, aging and ombudsman contacts. This starter edition lists statewide and national contacts; county offices are not listed yet.</p>';return}const omb=DATA.find(x=>x.regional_role==='ombudsman');$('county-panel').innerHTML='<div class="contact-grid">'+officeCard(c)+'<article><h2>More help in @@NAME@@</h2><h3>Aging and community support</h3>'+agingContactsHTML(c.county)+'<p>Ask about meals, transportation, caregiver support and services at home. Military service is not required.</p><h3>Long-term-care ombudsman</h3><p>'+esc(omb.organization)+'<br>'+phoneLink(omb.public_contact.phone)+'</p><p><a href="'+esc(omb.official_url)+'" target="_blank" rel="noopener">Find the @@NAME@@ ombudsman program</a></p><p>Describe the resident’s concern and wishes. Confirm intake and availability with each agency.</p></article></div>'}
function renderSeniorGuide(){const active=route==='seniors';$('seniors-guide').hidden=!active;$('community-guide').hidden=route!=='community';$('county-panel').hidden=['accessibility','seniors','community'].includes(route);if(active){$('county-title').textContent='Choose @@NAME@@';$('county-intro').textContent='Find aging and ombudsman help. Military service is not required.'}if(route==='community'){$('county-title').textContent='Find @@NAME@@ community connections';$('county-intro').textContent='Use the national post locators, or ask the local aging agency for nearby senior centers and activities.'}if(!active)return;const county=$('county').value,omb=DATA.find(x=>x.regional_role==='ombudsman');$('seniors-contact').innerHTML='<h3>Local aging help</h3>'+agingContactsHTML(county)+(omb?'<h3>Resident rights and care concerns</h3><p>'+esc(omb.name)+'<br>'+phoneLink(omb.public_contact.phone)+'</p>':'')+'<p>Medicare counseling (SHIP): '+phoneLink('@@SHIP@@')+'.</p>';const topic=$('senior-topic').value;const guidance={daily:'Ask the local aging agency about meals, transportation, personal assistance, caregiver support and in-home services. Ask which services fit the person’s living arrangement.',accessibility:'Describe the access barrier to the local aging agency and ask about assistive technology, home modification and Medicaid waiver screening. Equipment and construction funding are separate questions.',vision:'Ask the local aging agency about vision services and daily-living aids. Ask the care team for clinical assessment.',hearing:'Ask the local aging agency about hearing and communication supports. Confirm costs, availability and any assessment needed.',memory:'Ask the aging agency about caregiver support and respite, and contact the Alzheimer’s Association for dementia guidance. Seek clinical assessment for new memory concerns.',costs:'SHIP offers free Medicare counseling. Ask the aging agency about Medicaid waiver screening and other help with care costs. Separate financial and care-need rules apply.',rights:'Contact the long-term-care ombudsman for nursing home or assisted living concerns. Tell them the resident’s wishes and ask how follow-up works.'};$('senior-guidance').innerHTML='<strong>Your next step</strong><p>'+esc(guidance[topic]||'Choose the daily task or barrier, then confirm eligibility and availability with the agency.')+'</p>'}
function audience(x){if(/survivors|r02-dic/.test(x.program_id))return 'Surviving spouses and other qualifying survivors';if(/aid-attendance/.test(x.program_id))return 'Qualifying veterans and survivors who need daily help';if(/ombudsman/.test(x.program_id))return 'Residents of nursing homes and assisted living facilities';if(/nara/.test(x.program_id))return 'Veterans and eligible records requesters';return null}
function renderAccessibility(){const active=route==='accessibility';$('accessibility-guide').hidden=!active;$('county-panel').hidden=active;$('county-title').textContent=active?'Choose where help is needed':'Your first statewide contact';$('county-intro').textContent='Choose @@NAME@@ for veterans, aging and ombudsman referrals.';if(!active)return;const veteran=$('access-veteran').value,home=$('access-home').value,coverage=$('access-waiver').value,county=$('county').value,c=COUNTIES.find(c=>c.county===county),va=veteran==='yes',newHome=home==='new';const primary=coverage==='waiver'?'Your waiver case manager':va?(newHome?'VA adapted housing team':'VA Prosthetics and your care team'):'Local aging agency';const action=coverage==='waiver'?'Ask what assessment and written service-plan authorization are required.':va?(newHome?'Ask VA about SAH/SHA eligibility. HISA excludes new construction.':'Ask VA Prosthetics about clinical review and HISA.'):'Ask for an accessibility assessment referral and screening for available support.';$('access-first').innerHTML='<article class="first-call"><h3>'+esc(primary)+'</h3><p>'+esc(action)+'</p>'+(va?'<p><a href="https://www.va.gov/find-locations/?facilityType='+(newHome?'benefits':'health')+'" target="_blank" rel="noopener">Find your VA facility</a></p>':coverage==='waiver'?'<p>Use your case manager’s number from the care plan.</p>':agingContactsHTML(county))+'</article><article><h3>Help getting connected</h3>'+(c&&veteran!=='no'?'<p>'+esc(c.organization)+' '+phoneLink(c.phone)+'</p>':'')+agingContactsHTML(county)+'</article>';$('access-steps').innerHTML='<h3>Your next three steps</h3><ol><li>'+esc(action)+' Ask who handles follow-up.</li><li>'+(va&&!newHome&&coverage!=='waiver'?'For HISA, ask about the prescription, Form 10-0103, owner permission, itemized estimate and before photograph. <a href="#hisa-checklist" id="open-hisa">Open the HISA checklist</a>.':'Ask about assessment, financial and care eligibility, owner consent and estimate requirements.')+'</li><li>Confirm written approval, accepted providers and uncovered costs before arranging work.</li></ol>';const parts=['<article><h3>@@NAME@@ assessment and equipment routes</h3><p>Ask the local aging agency about Medicaid waiver screening, home modification help and the state assistive technology program. Medicaid enrollment alone does not establish adaptation coverage. Permanent ramp construction and installation are not guaranteed.</p></article>'];if(veteran!=='no')parts.push('<article><h3>Veteran housing adaptations</h3><p>Ask VA about HISA and, for qualifying service-connected disabilities, SAH/SHA. HISA excludes new construction. Temporary Residence Adaptation requires SAH or SHA eligibility and temporary residence in a family member’s home.</p></article>');if(home==='facility')parts.push('<article><h3>Returning home</h3><p>Ask the discharge planner about waiver screening and coordinate housing, care and access before discharge. A referral does not guarantee enrollment.</p></article>');if(home==='rent')parts.push('<article><h3>Rented home</h3><p>Arrange owner permission. HISA requires notarized owner permission for renters; other programs have their own requirements.</p></article>');if(home==='new')parts.push('<article><h3>Unfinished or new construction</h3><p>HISA excludes new construction. Ask each funding administrator whether the proposed project qualifies.</p></article>');$('access-routing').innerHTML=parts.join('');const link=$('open-hisa');if(link)link.onclick=()=>{$('hisa-checklist').open=true}}
'''


def edition_ops(s, ids, reviewed, ssvf_ids=()):
    code, name = s['code'], s['name']
    claims, ship, aging, omb = ids
    month = 'November 2, 2026'
    return [
        {'op': 'clear_data'},
        {'op': 'replace', 'old': 'Ohio', 'new': name},
        {'op': 'replace', 'old': 'All 88', 'new': 'All'},
        {'op': 'replace', 'old': 'all 88', 'new': 'all'},
        {'op': 'replace', 'old': '<option value="OH">' + name + '</option>', 'new': '<option value="OH">Ohio</option>'},
        {'op': 'replace', 'old': "const STATE='OH';", 'new': "const STATE='" + code + "';"},
        {'op': 'replace', 'old': 'county veterans office', 'new': 'state veterans agency'},
        {'op': 'replace', 'old': 'county office', 'new': 'state veterans agency'},
        {'op': 'replace', 'old': 'Statewide edition · Updated October 8, 2026', 'new': name + ' starter edition · Updated ' + month},
        {'op': 'replace', 'old': name + '’s waiver rule specifies proposal and approval requirements; VA and other funders have their own processes.', 'new': 'Ask the local aging agency or state Medicaid agency about waiver assessment and written approval; VA and other funders have their own processes.'},
        {'op': 'replace', 'old': 'https://codes.ohio.gov/ohio-administrative-code/rule-5160-44-13', 'new': 'https://eldercare.acl.gov/home'},
        {'op': 'replace', 'old': name + ' home modification authorization and provider rules', 'new': 'Find local aging and disability help (Eldercare Locator)'},
        {'op': 'replace', 'old': 'href="share.html"', 'new': 'href="share-' + code.lower() + '.html"'},
        {'op': 'replace', 'old': 'href="prototype-data.json"', 'new': 'href="data/public/' + slug(name) + '-resources.json"'},
        {'op': 'replace', 'old': 'href="data/public/ohio-county-veterans-offices.json"', 'new': 'href="data/public/' + slug(name) + '-county-veterans-offices.json"'},
        {'op': 'declare', 'name': 'priority', 'value': [claims, aging, ship, omb, 'r02-aid-attendance-housebound', 'r02-va-pension', 'r02-survivors-pension']},
        {'op': 'declare', 'name': 'routes', 'value': {
            'benefits': [claims, ship, 'r02-va-pension', 'r02-aid-attendance-housebound', 'r02-disability-increase', 'r02-pension-medicaid-rule', 'r02-survivors-pension', 'r02-dic', 'va-accredited-help'],
            'survivors': [claims, 'r02-survivors-pension', 'r02-dic', 'r02-aid-attendance-housebound', 'r02-va-burial', 'va-accredited-help', 'nara-discharge-records'],
            'care': [aging, 'r02-va-health-enrollment', 'va-location-finder', 'r02-va-cnh', 'r02-va-clc', 'r02-general-caregiver', 'r02-family-caregiver', 'r02-hospice', 'r02-palliative'],
            'rights': [omb, aging],
            'local': [aging, claims],
            'housing': ['va-housing-help', *ssvf_ids, 'va-location-finder', 'va-accredited-help', 'nara-discharge-records']}},
        {'op': 'declare', 'name': 'seniorTopics', 'value': {
            'daily': [aging], 'accessibility': [aging], 'vision': [aging], 'hearing': [aging],
            'memory': ['alz-dementia-support', aging], 'costs': [ship, aging], 'rights': [omb, aging]}},
        {'op': 'line', 'prefix': 'routes.accessibility=', 'new': "routes.accessibility=['va-hisa','va-sah','va-sha','va-tra','" + aging + "','va-location-finder'];"},
        {'op': 'line', 'prefix': 'routes.seniors=', 'new': "routes.seniors=[...new Set(Object.values(seniorTopics).flat()),...DATA.filter(x=>x.regional_role).map(x=>x.program_id),'cms-care-compare'];"},
        {'op': 'adapter'},
        {'op': 'embed_data'},
    ]


def write_assistant_states(registry):
    """Keep the guided-assistance state list in step with the full editions in the registry.

    Starter editions stay out: the assistant recommends only fully reviewed sources and
    needs county-level offices.
    """
    registry = [r for r in registry if not r.get('starter')]
    names = {r['code']: r['name'] for r in registry}
    files = {r['code']: [r['resources'], r['offices']] for r in registry}
    text = ('// Source: states/registry.json (full editions only). Tests prevent drift when the public guide adds a state.\n'
            '// Regenerated by scripts/make_starter_states.py.\n'
            'export const STATES=Object.freeze(' + json.dumps(names, ensure_ascii=False, indent=2) + ');\n'
            'export const STATE_FILES=Object.freeze(' + json.dumps(files, ensure_ascii=False, indent=2) + ');\n'
            'export const localityLabel=row=>row?(["independent_city","statewide"].includes(row.county_type)?row.county:row.county+" County"):"";\n')
    (ROOT / 'assistant/state-files.mjs').write_text(text)


def main():
    cfg = json.loads((ROOT / 'data/starter-states.json').read_text())
    reviewed, nat = cfg['reviewed_on'], cfg['national']
    registry_path = ROOT / 'states/registry.json'
    registry = json.loads(registry_path.read_text())
    full = [r for r in registry if not r.get('starter')]
    starters = []
    for s in cfg['states']:
        code, lc, name, area = s['code'], s['code'].lower(), s['name'], area_name(s)
        ids = (lc + '-claims', lc + '-ship', lc + '-aging', lc + '-ombudsman')
        if any(r['code'] == code for r in full):
            raise SystemExit(code + ' already has a full edition; remove it from data/starter-states.json')
        office = {'state': code, 'county': area, 'county_type': 'statewide', 'phone': s['phone'], 'organization': s['agency'],
                  'office_type': 'statewide', 'source_url': s['url'], 'source_title': s['agency'] + ' — official contact page',
                  'reviewed_on': s.get('reviewed_on', reviewed), 'contact_status': 'official_website', 'review_method': METHOD.get(s.get('review'), 'official_search_excerpt'),
                  'note': s.get('local_note') or 'Statewide contact. Ask which office serves your county.'}
        if s.get('local_url'):
            office['local_url'] = s['local_url']
        programs = [
            record(ids[0], s, name + ' veterans: accredited claims help', s['agency'], s['url'], s['phone'],
                   ['general_navigation', 'benefits_and_funding'], 'Free help with VA claims, applications and appeals for veterans and families.',
                   'Call the state veterans agency; ask for a benefits review and the office that serves your county.', reviewed, s['url'], area=area, review=s.get('review')),
            record(ids[1], s, 'Medicare counseling (SHIP) for ' + name, nat['ship']['organization'], nat['ship']['url'], nat['ship']['phone'],
                   ['benefits_and_funding'], 'Free, unbiased Medicare counseling from the State Health Insurance Assistance Program.',
                   'Call or use the locator to reach the ' + name + ' SHIP and ask for a counseling appointment.', reviewed, nat['ship']['source'], area=area)]
        referrals = [
            record(ids[2], s, 'Local aging help in ' + name + ' (Eldercare Locator)', nat['aging']['organization'], nat['aging']['url'], nat['aging']['phone'],
                   ['general_navigation', 'help_at_home'], 'A national public service that connects older adults and caregivers to their local aging agency and services.',
                   'Give the ZIP code; ask for the local aging agency, meals, transportation, caregiver support and home services.', reviewed, nat['aging']['source'],
                   role='aging_agency', area=area, constraints=['A national referral line, not a local intake office. Confirm services and eligibility with the local agency.']),
            record(ids[3], s, name + ' long-term-care ombudsman', nat['ombudsman']['organization'], nat['ombudsman']['url'], nat['ombudsman']['phone'],
                   ['resident_rights', 'general_navigation'], 'Ombudsmen advocate for residents of nursing homes and assisted living facilities.',
                   'Use the locator to find the ' + name + ' program, or ask the Eldercare Locator for the ombudsman nearest the facility.', reviewed, nat['ombudsman']['source'],
                   role='ombudsman', area=area, constraints=['Routes to the state program through a national locator; local ombudsman offices are not yet listed.'])]
        ssvf = ssvf_records(s, area, reviewed)
        programs += ssvf
        out = ROOT / 'data/public'
        (out / (slug(name) + '-county-veterans-offices.json')).write_text(json.dumps([office], ensure_ascii=False, indent=1) + '\n')
        (out / (lc + '-programs.json')).write_text(json.dumps(programs, ensure_ascii=False, indent=1) + '\n')
        (out / (lc + '-regional-referrals.json')).write_text(json.dumps(referrals, ensure_ascii=False, indent=1) + '\n')
        folder = ROOT / 'states' / lc
        folder.mkdir(exist_ok=True)
        (folder / 'edition.json').write_text(json.dumps({'ops': edition_ops(s, ids, reviewed, [r['program_id'] for r in ssvf])}, ensure_ascii=False, indent=1) + '\n')
        adapter = ADAPTER.strip().replace('@@NAME@@', name).replace('@@AREA@@', area).replace('@@SHIP@@', nat['ship']['phone'])
        (folder / 'adapter.js').write_text(adapter + '\n')
        starters.append({'code': code, 'name': name, 'starter': True, 'page': lc + '.html', 'share_page': 'share-' + lc + '.html',
                         'qr': 'assets/guide-qr-' + lc + '.svg', 'counties': 1,
                         'programs': 'data/public/' + lc + '-programs.json', 'referrals': 'data/public/' + lc + '-regional-referrals.json',
                         'offices': 'data/public/' + slug(name) + '-county-veterans-offices.json', 'resources': 'data/public/' + slug(name) + '-resources.json',
                         'statewide_area_names': [area],
                         'coverage_scope': 'Starter edition: statewide veterans agency plus national aging, ombudsman and Medicare counseling routes. County offices are not listed yet.',
                         'coverage_note': 'Starter edition. Every county uses the ' + s['agency'] + ' and national locators until county research is added. Contacts reviewed ' + reviewed + ' on official websites; not telephone-confirmed.',
                         'share_description': 'the statewide veterans agency and national routes to local aging help, the long-term-care ombudsman and Medicare counseling',
                         'share_replacements': []})
    starters.sort(key=lambda r: r['name'])
    registry_path.write_text(json.dumps(full + starters, ensure_ascii=False, indent=2) + '\n')
    write_assistant_states(full + starters)
    print('Starter editions written:', ', '.join(r['code'] for r in starters))


if __name__ == '__main__':
    main()
