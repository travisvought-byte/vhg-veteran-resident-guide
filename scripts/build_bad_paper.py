"""Build the bad-paper section of the Veteran Resource Guide (guide.vethomeguard.org/bad-paper/).

Run by scripts/build_public.py. For veterans with other-than-honorable, general or bad-conduct
discharges and the family members helping them: what VA can still provide, the discharge boards and
forms, liberal consideration, records, and free help.

The page text lives in templates/bad-paper/<slug>.html; the title, description, heading and the
sources each page cites live in PAGES below. Every source is an official page (VA, the military
boards, DoD, the U.S. Code and CFR, the National Archives, Ohio's veterans department) or the
organization's own page for a program it runs. Sources were read on CHECKED.

Each state's veterans agency comes from the guide's own state records (the <state>-claims record, or
Ohio's ohio-dvs-fallback record), so the section never carries a second copy of a phone number.
The printable one-page checklist is flyers/src/bad-paper-checklist-letter.html (data/flyers.json).
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

import visuals

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guide.vethomeguard.org/bad-paper/'
EMAIL = 'travis@vethomeguard.org'
CHECKED = '2026-11-23'
FLYER = '../flyers/bad-paper-checklist-letter.pdf'

# Sources, by key. Title as the page names itself, the address, and who publishes it.
SOURCES = {
    'va-cod': ('Applying for Benefits and Your Character of Discharge', 'https://benefits.va.gov/benefits/character_of_discharge.asp', 'VA, Veterans Benefits Administration'),
    'va-2024': ('VA expands access to care and benefits for some former service members who did not receive an honorable or general discharge (April 25, 2024)', 'https://www.va.gov/wilmington-health-care/news-releases/va-expands-access-to-care-and-benefits-for-some-former-service-members-who-did-not-receive-an-honorable-or/', 'VA news release'),
    'fr-2024': ('Update and Clarify Regulatory Bars to Benefits Based on Character of Discharge (final rule)', 'https://www.federalregister.gov/documents/2024/04/26/2024-09012/update-and-clarify-regulatory-bars-to-benefits-based-on-character-of-discharge', 'Federal Register'),
    'cfr-3.12': ('38 CFR 3.12, Benefit eligibility based on character of discharge', 'https://www.ecfr.gov/current/title-38/section-3.12', 'eCFR'),
    'cfr-3.360': ('38 CFR 3.360, Service-connected health-care eligibility of certain persons administratively discharged under other than honorable conditions', 'https://www.ecfr.gov/current/title-38/section-3.360', 'eCFR'),
    'va-health-elig': ('Eligibility for VA health care', 'https://www.va.gov/health-care/eligibility/', 'VA'),
    'va-health-apply': ('How to apply for VA health care', 'https://www.va.gov/health-care/how-to-apply/', 'VA'),
    'va-file-claim': ('How to file a VA disability claim', 'https://www.va.gov/disability/how-to-file-claim/', 'VA'),
    'va-crisis-care': ('Veteran suicide prevention (emergency mental health care)', 'https://www.va.gov/health-care/health-needs-conditions/mental-health/suicide-prevention/', 'VA'),
    'vet-center': ('Vet Center Eligibility', 'https://www.vetcenter.va.gov/Eligibility.asp', 'VA'),
    'va-gibill': ('Post-9/11 GI Bill', 'https://www.va.gov/education/about-gi-bill-benefits/post-9-11/', 'VA'),
    'va-upgrade': ('Request a discharge upgrade or correction', 'https://www.va.gov/resources/request-a-discharge-upgrade-or-correction/', 'VA'),
    'va-wizard': ('Discharge upgrade instructions (answer questions to get your form and mailing address)', 'https://www.va.gov/discharge-upgrade-instructions/introduction/', 'VA'),
    'va-rep-faq': ('VA accredited representative FAQs', 'https://www.va.gov/resources/va-accredited-representative-faqs/', 'VA'),
    'va-find-rep': ('Find a VA-accredited representative or VSO', 'https://www.va.gov/get-help-from-accredited-representative/find-rep/', 'VA'),
    'usc-1553': ('10 U.S.C. 1553, Review of discharge or dismissal', 'https://www.govinfo.gov/link/uscode/10/1553', 'U.S. Code, govinfo'),
    'usc-1177': ('10 U.S.C. 1177, Members diagnosed with or reasonably asserting PTSD or TBI: medical examination required before administrative separation', 'https://www.govinfo.gov/link/uscode/10/1177', 'U.S. Code, govinfo'),
    'usc-1552': ('10 U.S.C. 1552, Correction of military records', 'https://www.govinfo.gov/link/uscode/10/1552', 'U.S. Code, govinfo'),
    'ndrb': ('Naval Discharge Review Board (NDRB)', 'https://www.secnav.navy.mil/mra/CORB/Pages/NDRB/default.aspx', 'Secretary of the Navy Council of Review Boards'),
    'ndrb-info': ('NDRB: Information for the Applicant', 'https://www.secnav.navy.mil/mra/CORB/pages/policies.aspx', 'Secretary of the Navy Council of Review Boards'),
    'bcnr': ('Board for Correction of Naval Records', 'https://www.secnav.navy.mil/mra/bcnr/Pages/default.aspx', 'Department of the Navy'),
    'bcnr-process': ('BCNR application process', 'https://www.secnav.navy.mil/mra/bcnr/Pages/ApplicationProcess.aspx', 'Department of the Navy'),
    'arba': ('Army Review Boards Agency', 'https://www.army.mil/arba', 'U.S. Army'),
    'afrba': ('Air Force Review Boards Agency portal (AFDRB and AFBCMR)', 'https://afrba-portal.cce.af.mil/', 'Department of the Air Force'),
    'cg-drb': ('Coast Guard Discharge Review Board', 'https://www.uscg.mil/Resources/Legal/DRB/', 'U.S. Coast Guard'),
    'cg-bcmr': ('Coast Guard Board for Correction of Military Records', 'https://www.uscg.mil/Resources/Legal/BCMR/', 'U.S. Coast Guard'),
    'dd293': ('DD Form 293, Application for the Review of Discharge', 'https://www.esd.whs.mil/Portals/54/Documents/DD/forms/dd/dd0293.pdf', 'DoD forms'),
    'dd149': ('DD Form 149, Application for Correction of Military Record', 'https://www.esd.whs.mil/Portals/54/Documents/DD/forms/dd/dd0149.pdf', 'DoD forms'),
    'hagel': ('Hagel memo, September 3, 2014: Supplemental Guidance to Military Boards for Correction of Military/Naval Records Considering Discharge Upgrade Requests by Veterans Claiming PTSD', 'https://afrba-portal.cce.af.mil/app/assets/2014-Hagel-SECDEF-Guidance-to-BCMRs-on-Liberal-Consideration-of-PTSD-in-Discharge-Upgrades.pdf', 'Secretary of Defense, hosted by the Air Force Review Boards Agency'),
    'carson': ('Carson memo, February 24, 2016: Consideration of Discharge Upgrade Requests by Veterans Claiming PTSD or TBI', 'https://afrba-portal.cce.af.mil/app/assets/2016-Carson-Memo-24-Feb-2016.pdf', 'Principal Deputy Under Secretary of Defense (Personnel and Readiness), hosted by the Air Force Review Boards Agency'),
    'kurta': ('Kurta memo, August 25, 2017: Clarifying Guidance to Military Discharge Review Boards and Boards for Correction of Military/Naval Records Considering Requests by Veterans for Modification of their Discharge Due to Mental Health Conditions, Sexual Assault, or Sexual Harassment', 'https://dod.defense.gov/Portals/1/Documents/pubs/Clarifying-Guidance-to-Military-Discharge-Review-Boards.pdf', 'Under Secretary of Defense (Personnel and Readiness)'),
    'wilkie': ('Wilkie memo, July 25, 2018: Guidance to Military Discharge Review Boards and Boards for Correction of Military/Naval Records Regarding Equity, Injustice, or Clemency Determinations', 'https://afrba-portal.cce.af.mil/app/assets/2018-Wilkie-Memo-25-Jul-2018-DRB-Guidance.pdf', 'Under Secretary of Defense (Personnel and Readiness), hosted by the Air Force Review Boards Agency'),
    'reading-room': ('Armed Forces Boards reading room (published, redacted board decisions)', 'https://boards.law.af.mil/', 'Department of Defense'),
    'cfr-70.8': ('32 CFR 70.8, Discharge review procedures (reconsideration)', 'https://www.ecfr.gov/current/title-32/section-70.8', 'eCFR'),
    'cfr-723.9': ('32 CFR 723.9, Reconsideration (Board for Correction of Naval Records)', 'https://www.ecfr.gov/current/title-32/section-723.9', 'eCFR'),
    'nara': ('Request Military Service Records', 'https://www.archives.gov/veterans/military-service-records', 'National Archives'),
    'evetrecs': ('eVetRecs online request', 'https://vetrecs.archives.gov/', 'National Archives'),
    'nara-sf180': ('Request Military Personnel Records Using Standard Form 180', 'https://www.archives.gov/veterans/military-service-records/standard-form-180.html', 'National Archives'),
    'sf180': ('SF-180, Request Pertaining to Military Records', 'https://www.gsa.gov/reference/forms/request-pertaining-to-military-records', 'GSA forms'),
    'nara-medical': ('Medical and Health Records', 'https://www.archives.gov/veterans/military-service-records/medical-records.html', 'National Archives'),
    'odvs': ('Ohio Department of Veterans Services', 'https://dvs.ohio.gov/', 'State of Ohio'),
    'odvs-guide': ('ODVS Benefits Resource Guide (September 2026)', 'https://dam.assets.ohio.gov/image/upload/dvs.ohio.gov/benefits/resource-guide-2026.pdf', 'Ohio Department of Veterans Services'),
    'ohio-legal-aids': ('Find your legal aid', 'https://ohiolegalaids.org/find-your-legal-aid/', 'Ohio Legal Aids'),
    'lasco': ('Veterans Resources', 'https://www.lasco.org/veterans', 'The Legal Aid Society of Columbus'),
    'nku': ('Veterans Discharge Upgrade Review Clinic', 'https://chaselaw.nku.edu/experiences/probonoservice/veterans-discharge-upgrade-review-clinic/index.html', 'Northern Kentucky University Chase College of Law'),
    'olh-vets': ('Other veteran and servicemember resources', 'https://www.ohiolegalhelp.org/topic/other-veteran-and-servicemember-resources', 'Ohio Legal Help'),
    'lsw': ('Lawyers Serving Warriors', 'https://nvlsp.org/what-we-do/lawyers-serving-warriors', 'National Veterans Legal Services Program'),
    'tvc': ('Get Help with a Discharge Upgrade', 'https://www.vetsprobono.org/dischargeupgrade/', 'The Veterans Consortium Pro Bono Program'),
    'lsc': ('Get Legal Help', 'https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help', 'Legal Services Corporation'),
}

# One entry per page: slug, short name (section menu), title, meta description, eyebrow, h1, lede, sources.
PAGES = [
    {'slug': 'index', 'nav': 'Start here',
     'title': 'Bad paper discharge? What you can still get, and how to upgrade it | Veteran Resource Guide',
     'description': 'Other-than-honorable or bad-conduct discharge? VA can still find that your service counts, emergency mental health care is open now, and military boards can upgrade it. A plain start and free help.',
     'h1': 'Bad paper is not the end of the road',
     'lede': 'Other than honorable, general or bad conduct on your DD-214? You have likely been told you get nothing. That is often wrong. Here is what is still open, how an upgrade works, and where to start this week.',
     'sources': ['va-cod', 'va-2024', 'va-health-elig', 'va-crisis-care', 'usc-1553', 'usc-1552', 'va-wizard', 'kurta', 'ndrb-info', 'cfr-3.12', 'va-gibill', 'odvs', 'odvs-guide']},
    {'slug': 'va-without-upgrade', 'nav': 'What VA can do now',
     'title': 'VA care and benefits with an other-than-honorable discharge | Veteran Resource Guide',
     'description': 'Other-than-honorable or bad-conduct discharge: how VA’s character of discharge decision works, the compelling circumstances exception, emergency mental health care, and the bars to benefits.',
     'h1': 'What VA can do without an upgrade',
     'lede': 'VA does not simply go by the box on your DD-214. For other-than-honorable and most bad-conduct discharges, VA looks at your service and decides for itself. Some care is open to you right now.',
     'sources': ['va-cod', 'va-2024', 'fr-2024', 'cfr-3.12', 'cfr-3.360', 'va-health-elig', 'va-health-apply', 'va-file-claim', 'va-crisis-care', 'vet-center', 'va-gibill']},
    {'slug': 'boards', 'nav': 'Upgrade boards and forms',
     'title': 'Discharge Review Board or Board for Correction? DD-293 and DD-149 explained | Veteran Resource Guide',
     'description': 'Which military board reviews your discharge: the 15-year Discharge Review Board window, the Army, Navy and Marine Corps, Air Force and Coast Guard Boards for Correction, and which form goes where.',
     'h1': 'Which board, which form',
     'lede': 'Two kinds of military boards can change a discharge. Which one you go to depends on how long ago you got out and what kind of discharge you have.',
     'sources': ['usc-1553', 'usc-1552', 'usc-1177', 'ndrb', 'ndrb-info', 'bcnr', 'bcnr-process', 'arba', 'afrba', 'cg-drb', 'cg-bcmr', 'dd293', 'dd149', 'wilkie', 'carson', 'va-wizard', 'cfr-3.12']},
    {'slug': 'liberal-consideration', 'nav': 'PTSD, TBI, MST and new evidence',
     'title': 'Liberal consideration for PTSD, TBI, MST and mental health in a discharge upgrade | Veteran Resource Guide',
     'description': 'What the Hagel, Carson, Kurta and Wilkie memos tell discharge boards, the four questions a board asks, evidence that counts without a diagnosis, and what new evidence means for a second try.',
     'h1': 'PTSD, TBI, MST and mental health: liberal consideration',
     'lede': 'If what happened to you in service had a part in the conduct that got you discharged, the boards are required to look at your case with liberal consideration. Here is what that means and what evidence helps.',
     'sources': ['usc-1553', 'usc-1552', 'hagel', 'carson', 'kurta', 'wilkie', 'afrba', 'ndrb-info', 'reading-room', 'cfr-70.8', 'cfr-723.9']},
    {'slug': 'records', 'nav': 'Get your records',
     'title': 'Get your DD-214, service record and medical records for a discharge upgrade | Veteran Resource Guide',
     'description': 'Request your DD-214 and your full military personnel file free from the National Archives (eVetRecs or SF-180), find where your service treatment records went, and get Ohio’s copy of discharge papers.',
     'h1': 'Get your records first',
     'lede': 'Every route here runs on paper: your DD-214, your full personnel file and your medical records. Requests take time, so order them before anything else.',
     'sources': ['nara', 'evetrecs', 'nara-sf180', 'sf180', 'nara-medical', 'ndrb', 'odvs-guide', 'usc-1177', 'cfr-70.8']},
    {'slug': 'free-help', 'nav': 'Free help',
     'title': 'Free help with a discharge upgrade or VA character of discharge | Veteran Resource Guide',
     'description': 'Free help with a bad paper discharge: county veterans service offices, accredited VSOs, legal aid, law school clinics and national pro bono programs. Ohio first, then every state. How to spot paid consultants.',
     'h1': 'Free help, and who to avoid',
     'lede': 'You can do this yourself, and many do. A trained helper who has seen these cases before makes it easier and often stronger. You should not have to pay for it.',
     'sources': ['va-rep-faq', 'va-find-rep', 'odvs', 'odvs-guide', 'lasco', 'ohio-legal-aids', 'nku', 'lsw', 'tvc', 'lsc', 'olh-vets', 'ndrb-info', 'nara']},
]

STYLE = '''<style>
.bp{max-width:1000px}.bp section{margin-bottom:36px}
.card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:8px;padding:16px 20px;margin:0 0 16px}.card h3{margin-top:0}
.steps{counter-reset:step;list-style:none;padding:0;margin:0}.steps>li{counter-increment:step;position:relative;background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px 18px 14px 62px;margin:0 0 12px}
.steps>li::before{content:counter(step);position:absolute;left:16px;top:14px;width:32px;height:32px;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}
.steps h3{margin:2px 0 6px;font-size:19px}.steps p{margin:6px 0}
.when{font-size:13px;font-weight:750;letter-spacing:1px;color:var(--green);margin:22px 0 8px}
.helping{background:#e8eeea;border-radius:8px;padding:16px 22px}.helping h2{margin-top:4px}
.keypoint{background:#fff8e6;border-left:5px solid var(--gold);border-radius:5px;padding:10px 18px;margin:14px 0}
table{border-collapse:collapse;width:100%;background:#fff;font-size:16px}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{background:#eef3f0}
.table-wrap{overflow-x:auto}
.crisis-aside{font-size:14px;line-height:1.45;color:#3d4f48;border-left:3px solid #a3412c;padding:4px 0 4px 12px;margin:0 0 18px;max-width:640px}.crisis-aside p{margin:0}
@media(min-width:900px){.crisis-aside{float:right;width:250px;margin:4px 0 16px 28px}}
.section-menu{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 18px;margin:0 0 22px}.section-menu h2{font:700 15px/1.3 system-ui,sans-serif;letter-spacing:.8px;text-transform:uppercase;color:var(--green);margin:2px 0 6px}
.section-menu ol{margin:0;padding-left:22px;columns:2;column-gap:28px}.section-menu li{margin:4px 0;break-inside:avoid}.section-menu [aria-current]{font-weight:700;color:var(--ink);text-decoration:none}
.next{display:flex;flex-wrap:wrap;gap:10px 18px;justify-content:space-between;border-top:1px solid var(--line);padding-top:14px;margin-top:10px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}.cards a{display:block;background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.cards a strong{display:block;color:var(--sky);text-decoration:underline;text-underline-offset:3px;font-size:18px}.cards a span{display:block;font-size:15px;color:#3d4f48;margin-top:4px}.cards a:hover{border-color:var(--green)}
#your-state .agency{font-size:18px}#your-state select{max-width:360px}
.sources ol{padding-left:22px;font-size:15px}.sources li{margin:6px 0}
.report{font-size:15px}
@media(max-width:700px){.section-menu ol{columns:1}.bp{padding:16px}th,td{padding:6px}.steps>li{padding-left:56px}}
@media print{header nav,.section-menu,.next,.crisis-aside,#your-state select{display:none}body{background:#fff}}
</style>'''


def e(text):
    return escape(text or '', quote=True)


def when(value):
    d = date(*[int(p) for p in value.split('-')])
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')


def tel(number):
    digits = re.sub(r'[^0-9]', '', number.split(' ext')[0])
    return f'<a href="tel:{digits}">{e(number)}</a>'


def registry():
    return json.loads((ROOT / 'states/registry.json').read_text(encoding='utf-8'))


def state_agencies(generated=None):
    """Each state's veterans agency as the guide already lists it: the <code>-claims record, or Ohio's statewide record.
    generated: files the public build has just produced, so a resource file rebuilt in the same run is read fresh."""
    out = []
    for s in registry():
        text = (generated or {}).get(s['resources']) or (ROOT / s['resources']).read_text(encoding='utf-8')
        data = json.loads(text)
        records = data if isinstance(data, list) else data.get('resources', [])
        wanted = 'ohio-dvs-fallback' if s['code'] == 'OH' else s['code'].lower() + '-claims'
        rec = next((r for r in records if r.get('program_id') == wanted), None)
        page = '../' if s['page'] == 'index.html' else '../' + s['page']
        entry = {'code': s['code'], 'name': s['name'], 'page': page}
        if rec:
            entry.update({'org': rec.get('organization') or rec.get('name'), 'url': rec.get('official_url') or '',
                          'phone': (rec.get('public_contact') or {}).get('phone') or '',
                          'reviewed': (rec.get('verification') or {}).get('last_reviewed_on') or ''})
        out.append(entry)
    return sorted(out, key=lambda x: x['name'])


def agency_html(a):
    """The agency block for one state, used in the table, the state box and the no-script fallback."""
    if not a.get('org'):
        return (f'<p class="agency">Open the <a href="{e(a["page"])}">{e(a["name"])} guide</a> and choose your county '
                'for your local veterans office.</p>')
    phone = f' · {tel(a["phone"])}' if a.get('phone') else ''
    site = f'<a href="{e(a["url"])}" rel="noopener">{e(a["org"])}</a>' if a.get('url') else e(a['org'])
    return (f'<p class="agency">{site}{phone}</p>'
            f'<p class="small">Your county veterans office: open the <a href="{e(a["page"])}">{e(a["name"])} guide</a> and choose your county.</p>')


def states_table(agencies):
    rows = []
    for a in agencies:
        if a.get('org'):
            org = f'<a href="{e(a["url"])}" rel="noopener">{e(a["org"])}</a>' if a.get('url') else e(a['org'])
            phone = tel(a['phone']) if a.get('phone') else ''
        else:
            org, phone = 'County veterans offices are listed in the state guide.', ''
        rows.append(f'<tr id="state-{a["code"].lower()}"><th scope="row">{e(a["name"])}</th><td>{org}</td><td>{phone}</td>'
                    f'<td><a href="{e(a["page"])}">{e(a["name"])} guide</a></td></tr>')
    return ('<div class="table-wrap"><table><caption class="sr">State veterans agencies</caption><thead><tr><th scope="col">State</th>'
            '<th scope="col">State veterans agency</th><th scope="col">Phone</th><th scope="col">County offices</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>')


def your_state(agencies):
    """Start page box: Ohio by default; the state's own guide page links here with ?state=XX."""
    ohio = next(a for a in agencies if a['code'] == 'OH')
    options = ''.join(f'<option value="{a["code"]}"{" selected" if a["code"] == "OH" else ""}>{e(a["name"])}</option>' for a in agencies)
    data = {a['code']: {'name': a['name'], 'html': agency_html(a)} for a in agencies}
    return (f'<section id="your-state" class="card" aria-labelledby="your-state-title"><h2 id="your-state-title">Your state’s veterans agency</h2>'
            f'<label for="bp-state">State</label><select id="bp-state">{options}</select>'
            f'<div id="bp-agency" aria-live="polite">{agency_html(ohio)}</div>'
            '<p class="small">State and county veterans offices help with VA claims, including a character of discharge request. '
            'Ask whether they also help with discharge upgrades. <a href="free-help.html#states">Every state</a> · <a href="free-help.html#ohio">Ohio help in detail</a></p>'
            '<script>(function(){var D=' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + ';'
            'var s=document.getElementById("bp-state"),box=document.getElementById("bp-agency");'
            'function show(c){if(!D[c])return;s.value=c;box.innerHTML=D[c].html}'
            'var q=(new URLSearchParams(location.search).get("state")||"").toUpperCase();if(D[q])show(q);'
            's.addEventListener("change",function(){show(s.value)})})();</script></section>')


def report_link(page):
    body = '\n'.join(['Page: ' + BASE + ('' if page['slug'] == 'index' else page['slug'] + '.html'), '',
                      'What needs fixing? (wrong phone, changed rule, broken link, or something else)', '',
                      'Your role, optional (veteran, family member, service officer, attorney):', '',
                      'Please share public information only. Do not include names, service numbers or health details.'])
    href = 'mailto:' + EMAIL + '?subject=' + quote('Guide correction: bad paper · ' + page['nav']) + '&body=' + quote(body)
    return f'<a class="report" href="{e(href)}">Report a problem with this page</a>'


def section_menu(current):
    items = []
    for p in PAGES:
        href = './' if p['slug'] == 'index' else p['slug'] + '.html'
        cur = ' aria-current="page"' if p['slug'] == current else ''
        items.append(f'<li><a href="{href}"{cur}>{e(p["nav"])}</a></li>')
    items.append(f'<li><a href="{FLYER}">Printable one-page checklist (PDF)</a></li>')
    return '<nav class="section-menu" aria-labelledby="menu-title"><h2 id="menu-title">In this guide</h2><ol>' + ''.join(items) + '</ol></nav>'


def next_links(current):
    i = [p['slug'] for p in PAGES].index(current)
    href = lambda p: './' if p['slug'] == 'index' else p['slug'] + '.html'
    prev = f'<a href="{href(PAGES[i - 1])}">← {e(PAGES[i - 1]["nav"])}</a>' if i > 0 else '<span></span>'
    nxt = f'<a href="{href(PAGES[i + 1])}">{e(PAGES[i + 1]["nav"])} →</a>' if i + 1 < len(PAGES) else f'<a href="{FLYER}">Printable checklist (PDF) →</a>'
    return f'<p class="next">{prev}{nxt}</p>'


def sources_block(keys):
    items = []
    for k in keys:
        title, url, who = SOURCES[k]
        items.append(f'<li><a href="{e(url)}" rel="noopener">{e(title)}</a>. {e(who)}.</li>')
    return (f'<section class="sources" aria-labelledby="sources-title"><h2 id="sources-title">Sources</h2>'
            f'<p class="small">Official pages and the organizations’ own pages, read {when(CHECKED)}. Rules change; the board or agency has the final word.</p>'
            '<ol>' + ''.join(items) + '</ol></section>')


CRISIS = ('<aside class="crisis-aside" aria-label="Crisis support"><p><strong>Rough night?</strong> Call <a href="tel:988">988</a> and press 1, '
          'or text <a href="sms:838255">838255</a>. A VA medical center will see you in an emergency whatever your discharge.</p></aside>')


def page_html(p, body):
    url = BASE if p['slug'] == 'index' else BASE + p['slug'] + '.html'
    head = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p["title"])}</title>
<meta name="description" content="{e(p["description"])}">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(p["title"])}"><meta property="og:description" content="{e(p["description"])}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="article">
<link rel="stylesheet" href="../assets/family-guide.css">
{visuals.stylesheet("../")}
{STYLE}
<script src="../assets/analytics.js" defer></script></head><body>
<header><nav aria-label="Main"><a href="../">Veteran Resource Guide</a><a href="./">Bad paper discharges</a><a href="free-help.html">Free help</a><a href="{FLYER}">Printable checklist</a></nav>
<div class="hero"><p class="eyebrow">OTHER-THAN-HONORABLE, GENERAL AND BAD-CONDUCT DISCHARGES</p><h1>{e(p["h1"])}</h1><p>{e(p["lede"])}</p></div></header>
<main class="bp" id="main">{CRISIS}'''
    foot = (f'{next_links(p["slug"])}{sources_block(p["sources"])}</main>'
            '<footer class="bp" style="margin:auto;padding:18px 24px"><p>Free from <a href="https://www.vethomeguard.org/about.html">Veteran Home Guardians</a>, '
            'an Ohio 501(c)(3) nonprofit (EIN 33-4637180) that visits veterans in long-term care and publishes free guides. This guide explains public rules and points to official '
            'sources and free help. It is not legal advice and does not decide eligibility; the board or agency decides.</p>'
            f'<p>{report_link(p)} · <a href="../">Back to the Veteran Resource Guide</a> · <a href="../privacy.html">Privacy</a></p></footer>\n</body></html>\n')
    return head + section_menu(p['slug']) + body + foot


def fill(body, agencies):
    body = body.replace('{{YOUR_STATE}}', your_state(agencies))
    body = body.replace('{{STATES_TABLE}}', states_table(agencies))
    body = body.replace('{{FLYER}}', FLYER)
    # {{ICON:name}}: a line icon from assets/visuals.svg beside the words of a diagram (scripts/visuals.py).
    body = re.sub(r'\{\{ICON:([a-z-]+)\}\}', lambda m: visuals.icon(m.group(1), '../'), body)
    assert '{{' not in body, 'unfilled placeholder'
    return body


def pages():
    """Published paths, start page first."""
    return ['bad-paper/'] + ['bad-paper/' + p['slug'] + '.html' for p in PAGES[1:]]


def outputs(generated=None):
    agencies = state_agencies(generated)
    result = {}
    for p in PAGES:
        for k in p['sources']:
            assert k in SOURCES, 'unknown source ' + k
        body = (ROOT / 'templates/bad-paper' / (p['slug'] + '.html')).read_text(encoding='utf-8')
        # Full Open Graph and Twitter tags for shared links (scripts/landing.py); titles stay as written here.
        import landing
        result['bad-paper/' + p['slug'] + '.html'] = landing.complete_social(page_html(p, fill(body, agencies)))
    return result


if __name__ == '__main__':
    for name, text in outputs().items():
        print(name, len(text))
