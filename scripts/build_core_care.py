"""Build the guide's pages for veterans in nursing homes and their families.

Five topic pages, written to the veteran in a facility, the spouse, the adult child and the facility
social worker:

  va-pension-aid-attendance.html  VA pension with Aid and Attendance or Housebound
  elder-abuse.html                Abuse, neglect and exploitation: Adult Protective Services in every state
  guardianship.html               Guardianship and the choices to try first (Ohio probate basics)
  end-of-life-burial.html         Hospice, end-of-life care and burial
  toxic-exposure.html             Agent Orange, the PACT Act and toxic exposure

Also writes a one-page print source for each (flyers/src/<id>.html, built into PDFs by
scripts/build_flyers.cjs), the pointer card that build_public.py adds to every state page
(assets/care-topics.css and assets/care-topics.js), and the facilities-page link row.

Every figure and phone number comes from an official page named in SOURCES, read on CHECKED.
Adult Protective Services routes live in data/public/adult-protective-services.json.
VA changes pension and burial figures every year (December 1 and October 1): recheck them then.

Run by scripts/build_public.py. To refresh the flyer QR codes: python3 scripts/build_core_care.py --qr
"""
import hashlib
import json
import sys
from html import escape
from pathlib import Path

import visuals
from visuals import icon

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://guide.vethomeguard.org/'
CHECKED = 'November 23, 2026'
EMAIL = 'travis@vethomeguard.org'


def aps_data():
    return json.loads((ROOT / 'data/public/adult-protective-services.json').read_text())


def tel(number):
    return f'<a href="tel:{number.replace("-", "")}">{number}</a>'


def a(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'


# The five topics, in the order they appear in cards and menus.
TOPICS = [
    {'slug': 'va-pension-aid-attendance.html', 'flyer': 'va-pension-letter', 'short': 'VA pension and Aid and Attendance',
     'line': 'Monthly help paying for care; the $90 Medicaid rule'},
    {'slug': 'elder-abuse.html', 'flyer': 'elder-abuse-letter', 'short': 'Abuse, neglect or money taken',
     'line': 'Adult Protective Services in every state'},
    {'slug': 'guardianship.html', 'flyer': 'guardianship-letter', 'short': 'Guardianship and the choices to try first',
     'line': 'Powers of attorney, health care agents, VA fiduciaries'},
    {'slug': 'end-of-life-burial.html', 'flyer': 'end-of-life-letter', 'short': 'Hospice and burial',
     'line': 'VA hospice, burial allowances, national cemeteries'},
    {'slug': 'toxic-exposure.html', 'flyer': 'toxic-exposure-letter', 'short': 'Agent Orange and the PACT Act',
     'line': 'Conditions VA presumes, screening, survivor benefits'},
]

CSS = '''
.topic{max-width:900px;margin:auto;padding:22px 24px}.topic h2{margin:34px 0 8px}.topic h3{margin:22px 0 6px}
.topic li{margin:6px 0}.checked{font-size:15px;color:#e2eaed;margin-top:-4px}.crisis-line{font-size:15px;color:#3d4f48;margin:0 0 14px}
.toc{background:#eef3f0;border-radius:6px;padding:12px 20px;margin:6px 0 10px}.toc ul{margin:6px 0;padding-left:20px}.toc li{margin:6px 0}
.box{background:#fff;border:1px solid var(--line);border-left:5px solid var(--green);border-radius:6px;padding:14px 18px;margin:14px 0}
.box.warn{border-left-color:#a3412c}.box h3{margin-top:2px}
table{width:100%;border-collapse:collapse;margin:12px 0;background:#fff;font-size:16px}th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:#edf2ef}
.roles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.roles div{background:#fff;border:1px solid var(--line);border-radius:6px;padding:12px 16px}.roles h3{margin:0 0 4px;font-size:18px}.roles p{margin:4px 0}
.aps-list{list-style:none;padding:0;margin:10px 0}.aps-list li{background:#fff;border:1px solid var(--line);border-radius:6px;padding:12px 16px;margin:10px 0;scroll-margin-top:12px}
.aps-list h3{margin:0 0 4px;font-size:19px}.aps-list p{margin:4px 0}.aps-list li:target{box-shadow:0 0 0 3px #e3c57d}
.sources li{font-size:15px;overflow-wrap:anywhere}.related{list-style:none;padding:0}.related li{margin:8px 0}
.sheet{display:inline-flex;align-items:center;min-height:44px}.table-wrap{overflow-x:auto;max-width:100%}
@media(max-width:760px){.roles{grid-template-columns:minmax(0,1fr)}table{font-size:15px}th,td{padding:6px}}
@media print{.toc,.sheet,.report{display:none}.box,.roles div,.aps-list li{break-inside:avoid}.checked{color:#000}}
'''


def related(current):
    items = ''.join(f'<li><a href="{t["slug"]}"><strong>{escape(t["short"])}</strong></a> · {escape(t["line"])}</li>'
                    for t in TOPICS if t['slug'] != current)
    return f'<h2 id="related">More for veterans in care and their families</h2><ul class="related">{items}</ul>'


def roles(veteran, spouse, child, worker):
    cells = [('If you are the veteran', veteran, 'user'), ('If you are the spouse', spouse, 'heart'),
             ('If you are an adult son or daughter', child, 'people'), ('If you are a social worker or facility staff', worker, 'clipboard')]
    # A small symbol for each reader beside the heading that names them (decoration; the heading says it).
    return ('<h2 id="next-steps">What to do next</h2><div class="roles">'
            + ''.join(f'<div><h3>{icon(ic)} {escape(h)}</h3><p>{p}</p></div>' for h, p, ic in cells) + '</div>')


def sources(items):
    lis = ''.join(f'<li>{a(u, label)}</li>' for label, u in items)
    return (f'<h2 id="sources">Sources</h2><p class="small">Each fact on this page comes from one of these official pages, read on {CHECKED}. '
            'Agencies change their figures and phone numbers; the linked page is the final word.</p><ul class="sources">' + lis + '</ul>')


def report_link(title):
    subject = 'Guide correction: ' + title
    body = ('Page: ' + title + '\nWhat looks wrong or out of date:\n\nWhere you saw the correct information (link):\n\n'
            'Please do not include any resident\'s name or health details.')
    from urllib.parse import quote
    href = 'mailto:' + EMAIL + '?subject=' + quote(subject) + '&body=' + quote(body)
    return f'<p><a class="report" href="{escape(href)}">Report a problem with this page</a></p>'


def page(t, title, description, h1, intro, body, toc):
    slug = t['slug']
    toc_html = '<nav class="toc" aria-label="On this page"><strong>On this page</strong><ul>' + ''.join(
        f'<li><a href="#{i}">{escape(label)}</a></li>' for i, label in toc) + '</ul></nav>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{BASE_URL}{slug}">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(h1)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{BASE_URL}{slug}">
<meta property="og:image" content="{BASE_URL}assets/vhg-logo.png">
<link rel="stylesheet" href="assets/family-guide.css">
{visuals.stylesheet()}
<style>{CSS}</style>
<script src="assets/analytics.js" defer></script></head><body>
<a class="skip" href="#main">Skip to the page</a>
<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="#related">Other topics for families</a><a href="flyers.html">Printable flyers</a></nav>
<div class="hero"><p class="eyebrow">FOR VETERANS IN CARE AND THEIR FAMILIES</p><h1>{escape(h1)}</h1><p>{intro}</p><p class="checked">Facts checked against official sources on {CHECKED}.</p></div></header>
<main class="topic" id="main">
<p class="crisis-line">Danger right now: call {tel('911')}. Veterans Crisis Line: {tel('988')}, then press 1.</p>
{toc_html}
<p><a class="sheet" href="flyers/{t["flyer"]}.pdf">Print the one-page sheet (PDF)</a></p>
{body}
{related(slug)}
{report_link(h1)}
</main>
<footer class="topic"><p>Free from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, an independent 501(c)(3) nonprofit (EIN 33-4637180) that visits veterans in Ohio nursing homes. We are not the U.S. Department of Veterans Affairs. This page gives general information and referral routes. It does not decide eligibility, give legal advice or represent anyone in a claim. Nothing you read or click here is saved.</p>
<p><a href="./">Veteran Resource Guide</a> · <a href="facilities.html">Ohio nursing homes and assisted living</a> · <a href="flyers.html">Printable flyers</a> · <a href="privacy.html">Privacy</a></p></footer>
</body></html>
'''


# ---------------------------------------------------------------- VA pension
# The worked example on the pension page, drawn to scale (VA's Aid and Attendance maximum for a veteran with no
# spouse or child, minus an example of the income VA counts). The page's own sentence states the same numbers.
EXAMPLE_MAX, EXAMPLE_COUNTED = 29093, 20000


def payment_chart():
    return visuals.payment_chart(EXAMPLE_MAX, EXAMPLE_COUNTED, 'pay-chart', 'How the example payment is figured',
                                 'Yearly maximum with Aid and Attendance (veteran, no spouse or child)',
                                 'Income VA counts', 'Pension', 'about $757 a month')


def forms_grid():
    """The forms the page says usually go together for a nursing home resident, as a row of documents."""
    forms = [('VA Form 21P-527EZ or 21P-534EZ', 'The pension application: 21P-527EZ for veterans, 21P-534EZ for surviving spouses', None),
             ('VA Form 21-2680', 'The exam', ('user', 'A medical examiner completes it')),
             ('VA Form 21-0779', 'The nursing home form', ('building', 'The nursing home completes it')),
             ('VA Form 21P-8416', 'The medical expense report', None)]
    tiles = ''.join(f'<li>{icon("doc")}<strong>{escape(n)}</strong><small>{escape(w)}</small>'
                    + (f'<span class="vz-by">{icon(b[0])}{escape(b[1])}</span>' if b else '') + '</li>' for n, w, b in forms)
    return ('<figure class="vz" aria-labelledby="forms-cap"><figcaption id="forms-cap"><strong>The forms that usually go together '
            'for a nursing home resident</strong></figcaption><ul class="vz-grid">' + tiles + '</ul></figure>')


def pension_page():
    t = TOPICS[0]
    body = f'''
<h2 id="what">What this benefit is</h2>
<p>VA pension is a monthly payment for wartime veterans, and for their surviving spouses, who have limited income and savings. Aid and Attendance and Housebound are extra amounts added to the pension for people who need help with daily life or who cannot leave home. VA bases the payment on the gap between a yearly limit set by Congress and the income VA counts.</p>
<p>For someone in a nursing home or assisted living, the cost of care is often subtracted from income. That is why many families who think they earn too much still qualify.</p>

<h2 id="who">Who can qualify</h2>
<h3>The veteran</h3>
<ul><li>Was not dishonorably discharged.</li>
<li>Served during a wartime period: at least 90 days of active duty with at least 1 day in wartime if service began before September 8, 1980. Later enlisted service generally needs 24 months, or the full period called to duty, with at least 1 day in wartime.</li>
<li>And at least one of these is true: age 65 or older; permanent and total disability; <strong>a patient in a nursing home for long-term care because of a disability</strong>; or receiving Social Security Disability Insurance or Supplemental Security Income.</li>
<li>Family income and net worth are under the limits below.</li></ul>
<p>Wartime periods VA uses: World War II (December 7, 1941, to December 31, 1946); Korean conflict (June 27, 1950, to January 31, 1955); Vietnam War era (November 1, 1955, to May 7, 1975, for service in the Republic of Vietnam; August 5, 1964, to May 7, 1975, for service anywhere else); Gulf War (August 2, 1990, to a date not yet set). Earlier periods are on VA's eligibility page.</p>
<h3>The surviving spouse</h3>
<ul><li>Has not remarried since the veteran died.</li>
<li>Lived with the veteran from marriage until death. VA can accept time apart for health, work or the veteran's misconduct.</li>
<li>The veteran's service meets the wartime rule above and the discharge was not dishonorable.</li>
<li>Income and net worth are under the limits.</li></ul>
<h3>Aid and Attendance or Housebound</h3>
<p><strong>Aid and Attendance</strong> can be added if at least one is true: the person needs another person's help with daily activities such as bathing, eating or dressing; must stay in bed, or spend much of the day in bed, because of illness; is in a nursing home because of lost mental or physical abilities related to a disability; or has very limited eyesight (5/200 or less in both eyes, or a visual field of 5 degrees or less).</p>
<p><strong>Housebound</strong> can be added if the person spends most of the time at home because of a permanent disability. A person cannot get both.</p>

<h2 id="limits">The limits and rates (as of {CHECKED})</h2>
<p><strong>Net worth limit: $163,699</strong> for December 1, 2025, to November 30, 2026. VA adjusts its limits and rates every December 1; check VA's rates page after that date for the new figures.</p>
<p>Net worth is everything owned, minus debts, <strong>plus</strong> yearly income. It does not include the home where the person lives most of the time, the car, or basic household items. A married veteran's net worth includes the spouse's.</p>
<p>The yearly maximum, called the Maximum Annual Pension Rate, effective December 1, 2025:</p>
<div class="table-wrap"><table><caption class="sr">VA pension yearly maximums effective December 1, 2025</caption>
<thead><tr><th scope="col">Who</th><th scope="col">Pension only</th><th scope="col">With Housebound</th><th scope="col">With Aid and Attendance</th></tr></thead>
<tbody><tr><th scope="row">Veteran, no spouse or child</th><td>$17,441</td><td>$21,313</td><td>$29,093</td></tr>
<tr><th scope="row">Veteran with 1 dependent (spouse or child)</th><td>$22,839</td><td>$26,710</td><td>$34,488</td></tr>
<tr><th scope="row">Surviving spouse, no child</th><td>$11,699</td><td>$14,298</td><td>$18,697</td></tr>
<tr><th scope="row">Surviving spouse with 1 child</th><td>$15,311</td><td>$17,902</td><td>$22,304</td></tr></tbody></table></div>
<p class="small">Two veterans married to each other, and families with more dependents, have their own amounts on VA's rate tables.</p>
<p><strong>How the payment is figured:</strong> the yearly maximum minus the income VA counts. Example using VA's table: a veteran with no spouse or child who qualifies for Aid and Attendance has a maximum of $29,093. If VA counts $20,000 of yearly income after medical costs are subtracted, the pension is $9,093 a year, paid monthly (about $757 a month).</p>
{{PAYMENT_CHART}}

<h2 id="care-costs">How nursing home and care costs count</h2>
<p>VA subtracts <strong>medical expenses you pay yourself and are not paid back for</strong> from the income it counts. Only the part above 5% of the yearly maximum is subtracted: $872 for a veteran with no dependents, $1,141 for a veteran with 1 dependent, $584 for a surviving spouse with no child.</p>
<ul><li><strong>Nursing homes:</strong> payments to a nursing home count as medical expenses, including the meals and lodging the home charges.</li>
<li><strong>Assisted living and other care facilities:</strong> payments for care count. Meals and lodging also count when the facility provides or arranges health care or custodial care for the person, or when a physician, physician assistant or nurse practitioner states in writing that the person needs to live in that kind of setting to receive care.</li>
<li><strong>Home care:</strong> paid help with daily activities can count, with rules about who the aide is.</li>
<li><strong>Insurance premiums</strong>, including Medicare Part B and Part D and long-term care insurance, count.</li>
<li>Whatever Medicaid, insurance or anyone else pays does <strong>not</strong> count. Only out-of-pocket costs do.</li></ul>
<p><strong>Forms that usually go together for a nursing home resident:</strong> the pension application (VA Form 21P-527EZ for veterans; 21P-534EZ for surviving spouses); VA Form 21-2680, the exam a medical examiner completes; VA Form 21-0779, which the nursing home completes; and VA Form 21P-8416, the medical expense report.</p>
{{FORMS_GRID}}

<div class="box" id="medicaid"><h3>If Medicaid pays for the nursing home: the $90 rule</h3>
<p>A veteran with no spouse or dependent child, or a surviving spouse with no child, who is in a <strong>Medicaid-covered nursing home</strong> receives no more than <strong>$90 a month</strong> in VA pension, starting after the month Medicaid payments begin.</p>
<p>The nursing home <strong>cannot count that $90 toward the cost of care</strong>. The resident keeps it for personal needs. In some states it is more than the personal spending money Medicaid allows.</p>
<p>This can matter even for someone who already gets VA disability compensation or Dependency and Indemnity Compensation (DIC). If the facility takes most of that payment for care, applying for pension can leave more spending money: when VA finds a person eligible for both, it pays pension at the $90 rate instead. Tell VA when Medicaid begins paying.</p>
<p>A veteran with a spouse or dependent child is not limited to $90 by this rule. Before changing any benefit, ask an accredited representative and the facility's business office to look at VA and Medicaid together.</p></div>

<h2 id="lookback">The 3-year look-back on gifts and transfers</h2>
<p>When someone files, VA reviews assets given away or sold for less than they were worth in the <strong>3 years before the claim</strong>. If those assets would have put net worth over the limit, VA can set a <strong>penalty period of up to 5 years</strong> with no pension. VA's penalty rate is $2,874. The look-back never reaches back before October 18, 2018.</p>
<p>Medicaid has its own, separate look-back. A transfer that seems to help with one program can hurt with the other.</p>

<h2 id="help">Get free, accredited help</h2>
<p>Only people VA has accredited may help prepare a VA claim. Free help comes from accredited Veterans Service Organization representatives and county veterans service officers. Accredited attorneys and claims agents may charge a fee only after VA has decided the first claim, and only with a signed fee agreement on file with VA.</p>
<ul><li>{a('https://www.va.gov/get-help-from-accredited-representative/find-rep/', 'Find a VA-accredited representative')} on VA.gov.</li>
<li><a href="./#county-start">Find your county veterans office</a> in this guide.</li>
<li>VA benefits line: {tel('800-827-1000')}.</li></ul>

<div class="box warn" id="warning"><h3>Be careful with pension “advisors”</h3>
<p>VA's Inspector General warns about “pension poaching.” Be wary of anyone who:</p>
<ul><li>promises the person will qualify;</li>
<li>tells you to move money into a trust, buy an annuity, or leave out income or expenses so the person qualifies;</li>
<li>charges an upfront fee or a percentage of the benefit to file a claim (free help is available from accredited helpers);</li>
<li>presses for bank or credit card details; or</li>
<li>wants VA deposits sent to an account that does not belong to the veteran or spouse.</li></ul>
<p>These sales often happen at senior centers and assisted living communities. Moving assets can trigger VA's penalty period and Medicaid's. Report a pension scheme to the VA Office of Inspector General: {tel('800-488-8244')} or {a('https://www.vaoig.gov/hotline', 'online')}. Someone who is not accredited and is helping with VA claims can be reported to VA's Office of General Counsel.</p></div>

{roles('Ask the social worker or your county veterans office to check whether you qualify. Bring your DD214 or tell them it is missing; they can request it.',
       'If your spouse is in care and you are at home, VA counts you as a dependent, so the higher yearly maximum for a veteran with a dependent is used; your income and savings count too. Ask before you sell or move anything.',
       'Gather the DD214, a list of income and savings, and a year of nursing home bills. Do not move money or sign up with a paid advisor until an accredited representative has looked.',
       'Complete VA Form 21-0779 when asked. Flag residents who are wartime veterans or surviving spouses with private-pay or Medicaid stays, and refer them to the county veterans office. For Medicaid residents with no spouse, ask about the $90 rate.')}
{sources([
    ('VA: Eligibility for Veterans Pension', 'https://www.va.gov/pension/eligibility/'),
    ('VA: Current Veterans Pension rates, net worth limit, look-back and penalty rate', 'https://www.va.gov/pension/veterans-pension-rates/'),
    ('VA: Survivors Pension', 'https://www.va.gov/pension/survivors-pension/'),
    ('VA: Survivors Pension rates', 'https://www.va.gov/pension/survivors-pension-rates/'),
    ('VA: Aid and Attendance benefits and Housebound allowance', 'https://www.va.gov/pension/aid-attendance-housebound/'),
    ('VA: $90 pension rate in a Medicaid-covered nursing facility', 'https://www.va.gov/resources/90-va-pension-rate-if-youre-in-a-medicaid-covered-nursing-facility/'),
    ('38 CFR 3.551(i): pension during Medicaid-covered nursing home care', 'https://www.ecfr.gov/current/title-38/section-3.551'),
    ('38 CFR 3.278: deductible medical expenses', 'https://www.ecfr.gov/current/title-38/section-3.278'),
    ('VA: How to apply for a pension (VA Form 21P-527EZ)', 'https://www.va.gov/pension/how-to-apply/'),
    ('VA Form 21P-8416, Medical Expense Report', 'https://www.va.gov/find-forms/about-form-21p-8416/'),
    ('VA: Accredited representative FAQs and fees', 'https://www.va.gov/resources/va-accredited-representative-faqs/'),
    ('VA Office of Inspector General: Protect Veterans from Pension Poaching (June 2025)', 'https://www.vaoig.gov/sites/default/files/document/2025-06/pension_poaching_fraud_alert_june_2025_final_to_50p.pdf'),
    ('VA Office of Inspector General hotline', 'https://www.vaoig.gov/hotline'),
])}'''
    toc = [('what', 'What this benefit is'), ('who', 'Who can qualify'), ('limits', 'The limits and rates'),
           ('care-costs', 'How care costs count'), ('medicaid', 'If Medicaid pays: the $90 rule'), ('lookback', 'The 3-year look-back'),
           ('help', 'Free, accredited help'), ('warning', 'Pension “advisors”'), ('next-steps', 'What to do next'), ('sources', 'Sources')]
    assert '$29,093' in body and '$20,000' in body and '$9,093' in body and EXAMPLE_MAX - EXAMPLE_COUNTED == 9093
    body = body.replace('{PAYMENT_CHART}', payment_chart()).replace('{FORMS_GRID}', forms_grid())
    return page(t, 'VA Pension, Aid and Attendance and Housebound for Nursing Home Families | VHG',
                'Wartime veterans and surviving spouses in a nursing home may qualify for VA pension with Aid and Attendance. Current limits, how care costs count, the $90 Medicaid rule and free accredited help.',
                'VA pension with Aid and Attendance or Housebound',
                'A monthly VA payment for wartime veterans and surviving spouses with limited income and savings. For someone in a nursing home, the cost of care often lowers the income VA counts.',
                body, toc)


# ---------------------------------------------------------------- Elder abuse
def report_routes():
    """Where to report, by where the person lives or what happened: the three cases listed under it, in short."""
    rows = [('home', 'The person lives at home or with family', 'shield', 'Adult Protective Services in that state'),
            ('building', 'The person lives in a nursing home or assisted living', 'people', 'The administrator and the long-term care ombudsman'),
            ('dollar', 'Money was stolen or a crime happened', 'siren', 'Also the local police')]
    items = ''.join(f'<li><span class="vz-when">{icon(a)}<span>{escape(w)}</span></span><span class="vz-arrow">{icon("arrow-right")}<span class="vz-vh">, call: </span></span>'
                    f'<span class="vz-who">{icon(b)}<span>{escape(who)}</span></span></li>' for a, w, b, who in rows)
    return ('<figure class="vz" aria-labelledby="routes-cap"><figcaption id="routes-cap"><strong>Who to call, at a glance</strong>'
            'The details for each case are in the list below.</figcaption><ul class="vz-routes">' + items + '</ul></figure>')


def money_signs():
    """The warning signs the page lists for money or benefits being taken, one tile each."""
    signs = [('receipt', 'Unpaid nursing home bills', 'when income should cover them'),
             ('user-plus', 'New “friends” or helpers handling money', ''),
             ('card', 'Missing checks, cards or valuables', ''),
             ('pen', 'Sudden changes to a will, deed or bank account', ''),
             ('wallet', 'A resident with no spending money', '')]
    tiles = ''.join(f'<li>{icon(i)}<strong>{escape(t)}</strong>' + (f'<small>{escape(x)}</small>' if x else '') + '</li>' for i, t, x in signs)
    return ('<figure class="vz" aria-labelledby="signs-cap"><figcaption id="signs-cap"><strong>Warning signs</strong></figcaption>'
            '<ul class="vz-grid">' + tiles + '</ul></figure>')


def aps_item(code, name, page, rec):
    phones = ''.join(f'<p><strong>{tel(p["number"])}</strong> · {escape(p["label"])}</p>' for p in rec['phones'])
    how = f'<p>{escape(rec["how"])}</p>' if rec.get('how') else ''
    scope = f'<p class="small">{escape(rec["scope"])}</p>' if rec.get('scope') else ''
    facility = ''
    if rec.get('facility'):
        f = rec['facility']
        facility = f'<p>{escape(f["label"])}: {tel(f["number"])}</p>'
    page_link = name
    rights = ('./' if page == 'index.html' else page) + '?view=rights'
    return (f'<li id="aps-{code.lower()}"><h3>{escape(name)}</h3><p class="small">{escape(rec["agency"])}</p>{scope}{phones}{how}{facility}'
            f'<p>{a(rec["page"], "Official reporting page")} · <a href="{rights}">Ombudsman and resident rights in {escape(page_link)}</a></p></li>')


def abuse_page(states):
    t = TOPICS[1]
    data = aps_data()['states']
    names = {s['code']: s['name'] for s in states}
    pages_by_code = {s['code']: s['page'] for s in states}
    assert set(data) == set(names), 'APS data must cover exactly the registered states'
    order = sorted(data, key=lambda c: names[c])
    items = ''.join(aps_item(c, names[c], pages_by_code[c], data[c]) for c in order)
    jump = ' · '.join(f'<a href="#aps-{c.lower()}">{escape(names.get(c, c))}</a>' for c in order)
    oh = data['OH']
    body = f'''
<h2 id="what">What counts, and who can report</h2>
<p>Anyone can report. You do not need proof, only a real concern. Many states, including Ohio, let you report without giving your name.</p>
<ul class="vz-ilist"><li>{icon('alert')}<strong>Abuse:</strong> hitting, rough handling, threats, yelling, sexual contact without consent, or keeping someone locked in or isolated.</li>
<li>{icon('pill')}<strong>Neglect:</strong> a caregiver not providing food, medicine, hygiene or needed care, or a person no longer able to care for themselves (self-neglect).</li>
<li>{icon('dollar')}<strong>Exploitation:</strong> money, property, a pension or VA benefit taken, misused or signed away under pressure.</li></ul>

<h2 id="where">Where to report</h2>
{report_routes()}
<ul><li><strong>The person lives at home or with family:</strong> call Adult Protective Services (APS) in that state. <a href="#states">Find your state below.</a></li>
<li><strong>The person lives in a nursing home or assisted living:</strong> tell the administrator, and call the long-term care ombudsman, a free advocate for residents. The state health or licensing agency also takes complaints about care, and in some states APS takes reports about care settings too; the state pages below say where to call. This guide lists each state's ombudsman under “Concerns about care or rights”: <a href="./?view=rights">Ohio</a>, or choose your state from the list below.</li>
<li><strong>Money was stolen or a crime happened:</strong> also call the local police.</li></ul>
<p>Not sure where to start? The Eldercare Locator, run by the U.S. Administration for Community Living, can connect you to local help: {tel('800-677-1116')}.</p>

<div class="box" id="ohio"><h3>In Ohio</h3>
<p><strong>Ohio Adult Protective Services: {tel('855-644-6277')}</strong> (855-OHIO-APS), or report online at {a('https://aps.jfs.ohio.gov/', 'aps.jfs.ohio.gov')}. To report anonymously, call. The Ohio Department of Job and Family Services oversees APS for adults 60 and older, and each county department of job and family services must take reports 24 hours a day, 7 days a week.</p>
<p><strong>Abuse or neglect in a nursing home or other care facility:</strong> the Ohio Attorney General takes reports of patient abuse and neglect {a('https://www.ohioattorneygeneral.gov/ReportPatientAbuse', 'online')}. For quality-of-care problems, the Attorney General's page points to the Ohio Department of Health: {tel(oh['facility']['number'])}.</p>
<p><strong>Resident rights and care concerns:</strong> see the ombudsman contacts in <a href="./?view=rights">this guide's Ohio section</a>; choose a county there for the local ombudsman.</p></div>

<h2 id="money">When money or benefits are being taken</h2>
{money_signs()}
<ul><li>Signs: unpaid nursing home bills when income should cover them; new “friends” or helpers handling money; missing checks, cards or valuables; sudden changes to a will, deed or bank account; a resident with no spending money.</li>
<li>Call the bank's fraud line, report to APS, and call the police if money was stolen.</li>
<li>Pressure to move assets so someone “qualifies” for VA pension is a known scheme. See <a href="va-pension-aid-attendance.html#warning">the warning on the pension page</a>.</li></ul>
<div class="box warn" id="fiduciary"><h3>If a VA fiduciary is misusing VA benefits</h3>
<p>When VA decides a beneficiary cannot manage VA payments, it appoints a fiduciary to handle those payments only. VA oversees fiduciaries with field exams, accountings and onsite reviews.</p>
<p>If you believe a fiduciary is misusing the money, call the <strong>VA Fiduciary program: {tel('888-407-0144')}</strong>, and report it to the <strong>VA Office of Inspector General: {tel('800-488-8244')}</strong> or {a('https://www.vaoig.gov/hotline', 'online')}. The Inspector General also asks people to report anyone trying to redirect VA deposits to an account controlled by a caregiver, power of attorney or claims helper. You can report to APS as well.</p></div>

<h2 id="states">Adult Protective Services in every state</h2>
<p>Each listing shows what the state's official page said on {CHECKED}. Where a state takes reports through its counties and has no single number, the state page lists the county numbers.</p>
<p class="small">{jump}</p>
<ul class="aps-list">{items}</ul>

{roles('You have the right to be safe and to control your own money. You can call APS yourself, or ask the ombudsman to help you raise a concern without your name attached.',
       'If you think your spouse is being harmed in a facility, write down what you saw, the date and who was there. Then call the ombudsman and the state number below.',
       'If a sibling, friend or new helper controls the money and bills are going unpaid, report it. A power of attorney does not allow anyone to take money for themselves.',
       'State law often requires care staff to report suspected abuse. Follow your facility policy and your state law, and do not wait for proof.')}
{sources([
    ('Ohio Adult Protective Services (ODJFS)', 'https://aps.jfs.ohio.gov/'),
    ('Ohio Revised Code 5101.63: reporting abuse, neglect or exploitation of an adult', 'https://codes.ohio.gov/ohio-revised-code/section-5101.63'),
    ('Ohio Attorney General: Report patient abuse or neglect', 'https://www.ohioattorneygeneral.gov/ReportPatientAbuse'),
    ('Eldercare Locator (U.S. Administration for Community Living)', 'https://eldercare.acl.gov/'),
    ('VA: Fiduciary help', 'https://www.va.gov/resources/fiduciary-help/'),
    ('VA Fiduciary program contact information', 'https://department.va.gov/vba/fiduciary/'),
    ('VA Office of Inspector General hotline', 'https://www.vaoig.gov/hotline'),
    ('VA Office of Inspector General: Protect Veterans from Pension Poaching', 'https://www.vaoig.gov/sites/default/files/document/2025-06/pension_poaching_fraud_alert_june_2025_final_to_50p.pdf'),
    ('Each state’s official APS page, linked in its listing above; the full list with sources is in this guide’s data file', BASE_URL + 'data/public/adult-protective-services.json'),
])}'''
    toc = [('what', 'What counts'), ('where', 'Where to report'), ('ohio', 'In Ohio'), ('money', 'Money or benefits taken'),
           ('fiduciary', 'VA fiduciary misuse'), ('states', 'APS in every state'), ('next-steps', 'What to do next'), ('sources', 'Sources')]
    return page(t, 'Report Elder Abuse, Neglect or Exploitation: Adult Protective Services in Every State | VHG',
                'Where to report abuse, neglect or financial exploitation of a veteran or older adult: Adult Protective Services numbers for every state, nursing home concerns, and VA fiduciary misuse.',
                'Abuse, neglect or money being taken: where to report',
                'If a veteran or older adult is being hurt, neglected, or robbed of money or benefits, you can report it. Every state has Adult Protective Services. Find your state below.',
                body, toc)


# ---------------------------------------------------------------- Guardianship
def least_restrictive():
    """The choices on the guardianship page, from the papers a person signs themselves to a court guardian."""
    cols = [('pen', 'Papers the person signs while they can', ['Financial power of attorney', 'Health care power of attorney and living will',
                                                               'Supported decision-making: the person decides, with trusted helpers']),
            ('court', 'Limited guardian, from the probate court', ['Only the powers the person needs', 'The person keeps every right the order does not cover']),
            ('court', 'Guardian, from the probate court', ['Of the person, the estate (money and property), or both',
                                                         'After a hearing, on clear and convincing evidence'])]
    ends = {0: 'Least restrictive', len(cols) - 1: 'Most restrictive'}
    items = ''.join(f'<li>' + (f'<span class="vz-end-tag" aria-hidden="true">{ends[n]}</span>' if n in ends else '')
                    + f'{icon(i)}<strong>{escape(t)}</strong><ul>' + ''.join(f'<li>{escape(x)}</li>' for x in xs) + '</ul></li>'
                    for n, (i, t, xs) in enumerate(cols))
    return ('<figure class="vz" aria-labelledby="least-cap"><figcaption id="least-cap"><strong>From the least restrictive choice to the most</strong>'
            'A court guardianship takes decisions away from a person. Many families can handle money and medical choices without going to court.</figcaption>'
            '<p class="vz-scale-axis" aria-hidden="true"><span>Least restrictive</span><span>Most restrictive</span></p><div class="vz-axis-line" aria-hidden="true"></div>'
            '<ol class="vz-steps">' + items + '</ol>'
            f'<p class="vz-aside">{icon("dollar")}<span><strong>Separate: the VA fiduciary.</strong> VA decides on its own whether a person can manage VA payments. '
            'A fiduciary handles VA benefits only and does not take away the right to manage other money, to vote or to sign legal documents.</span></p></figure>')


def guardianship_page():
    t = TOPICS[2]
    body = f'''
<h2 id="first">Start with the least restrictive choice</h2>
<p>A court guardianship takes decisions away from a person, often for the rest of their life. Ohio law requires a probate court to consider evidence of a less restrictive alternative before appointing a guardian. Many families can handle money and medical choices without going to court, especially if papers are signed while the person can still understand them.</p>
{least_restrictive()}

<h2 id="plan">Papers to sign while the person can</h2>
<h3>Financial power of attorney</h3>
<p>Names an agent to handle money and property. In Ohio, the law is Revised Code Chapter 1337, and section 1337.60 has a standard form with a checklist of powers. An Ohio power of attorney is presumed to be durable, which means it keeps working if the person later loses capacity, unless it says otherwise. It can start right away or only when something happens, such as incapacity.</p>
<p>Know the limits: the agent must act in the person's best interest, but there are few safeguards against misuse, and banks or nursing homes sometimes refuse a power of attorney, especially one that only starts on incapacity. A power of attorney covering real estate must be recorded with the county recorder.</p>
<h3>Health care power of attorney and living will</h3>
<p>A health care power of attorney names someone to make medical decisions when the person cannot. A living will states wishes about life-sustaining treatment. In Ohio, a health care power of attorney can be revoked at any time and in any manner.</p>
<p>For veterans who get care from VA, VA has its own form: {a('https://www.va.gov/find-forms/about-form-10-0137/', 'VA Form 10-0137, VA Advance Directive: Durable Power of Attorney for Health Care and Living Will')}. It tells VA providers who may make decisions and what care the veteran wants.</p>
<h3>Supported decision-making</h3>
<p>The person keeps the right to decide, and chooses trusted people to help them understand options and communicate. Releases of information, direct deposit and automatic bill paying can support this. The Ohio Developmental Disabilities Council's guide, {a('https://dam.assets.ohio.gov/image/upload/ddc.ohio.gov/SDMandGuardianship_Sept2023_web2.pdf', 'Supported Decision Making and Guardianship')}, explains the options.</p>
<h3>Other tools</h3>
<p>Ohio also has trusts, an additional signer on a bank account, and conservatorship, a court arrangement a person who is still competent can choose for themselves. Adding someone as a joint owner of an account is risky: a joint owner has no duty to the person, and the change can affect eligibility for government benefits.</p>

<h2 id="va-fiduciary">VA benefits: the VA fiduciary</h2>
<p>VA makes its own decision about whether a veteran or survivor can manage VA payments. If VA decides they cannot, it says so in the decision letter, waits 60 days so the person can ask for a hearing or send more evidence, and then refers the case to the VA Fiduciary Program.</p>
<ul><li>VA considers the person's choice. A spouse, relative or trusted friend who serves without a fee can be the fiduciary if they meet VA's requirements; otherwise VA appoints a professional fiduciary.</li>
<li>A fiduciary manages VA benefits only. It does not take away the right to manage non-VA money, to vote, or to sign legal documents.</li>
<li>The person can ask for a decision review within 1 year of the letter, and can later ask VA to end the fiduciary when they can manage again.</li>
<li>VA Fiduciary program: {tel('888-407-0144')}. Misuse: see <a href="elder-abuse.html#fiduciary">how to report it</a>.</li></ul>

<h2 id="ohio-guardianship">When guardianship is needed: Ohio probate court</h2>
<ul><li>The <strong>probate court</strong> of the county where the person lives appoints guardians. A guardian can be named for the person (care and daily decisions), the estate (money and property), or both.</li>
<li>The court must hold a hearing. Incompetency must be proven by <strong>clear and convincing evidence</strong>, and evidence of a less restrictive alternative must be considered when it is offered.</li>
<li>The person has the right to their own lawyer, to have a friend or family member present, and to an independent expert evaluation. If they cannot afford a lawyer or evaluator, they can ask the court to appoint one at court expense.</li>
<li>The court can appoint a <strong>limited guardian</strong> with only the powers needed; the person keeps every right the order does not cover. In an emergency, the court can appoint an emergency guardian for up to 72 hours.</li>
<li>Guardians of adults must complete court education: a one-time six-hour fundamentals course and three hours of continuing education each following year. The Supreme Court of Ohio offers free courses.</li>
<li>When a guardianship is mainly to handle money awarded by VA, Ohio law says no court costs are charged unless the estate, including the VA award, is worth more than $1,500.</li></ul>
<p>In other states, contact the probate or county court where the person lives. For free legal help for people 60 and older, ask the local Area Agency on Aging (Eldercare Locator: {tel('800-677-1116')}). In Ohio, people 60 and older can also call the {a('https://www.proseniors.org/legal-services/legal-hotline/', 'Pro Seniors legal hotline')}: {tel('800-488-6070')}.</p>

{roles('If you can still decide for yourself, sign a health care power of attorney and a financial power of attorney now, and tell your family where they are. Ask the social worker for VA Form 10-0137 if you use VA care.',
       'Being married does not give you authority over your spouse’s accounts or medical care in every situation. Check what papers exist and whether the bank and the facility will accept them.',
       'Before filing for guardianship, find out what your parent already signed. A limited guardianship, or no guardianship, may be enough.',
       'Keep copies of powers of attorney and advance directives in the chart. If an agent or guardian seems to be misusing money, report it to APS and the probate court.')}
{sources([
    ('Ohio Revised Code 2111.02: appointment of guardian, limited and emergency guardians, hearing rights', 'https://codes.ohio.gov/ohio-revised-code/section-2111.02'),
    ('Ohio Revised Code Chapter 2111: guardians and conservatorships', 'https://codes.ohio.gov/ohio-revised-code/chapter-2111'),
    ('Supreme Court of Ohio: Alternatives to adult guardianship (APS toolkit)', 'https://www.supremecourt.ohio.gov/JCS/CFC/resources/APSToolkit/7_AlternativesGuardianship.pdf'),
    ('Supreme Court of Ohio: Adult guardianship education', 'https://www.supremecourt.ohio.gov/education/ohio-adult-guardianship-education-program/'),
    ('Ohio Developmental Disabilities Council: Supported Decision Making and Guardianship', 'https://dam.assets.ohio.gov/image/upload/ddc.ohio.gov/SDMandGuardianship_Sept2023_web2.pdf'),
    ('VA Form 10-0137: VA Advance Directive', 'https://www.va.gov/find-forms/about-form-10-0137/'),
    ('VA: Fiduciary help', 'https://www.va.gov/resources/fiduciary-help/'),
    ('VA Fiduciary program contact information', 'https://department.va.gov/vba/fiduciary/'),
    ('Eldercare Locator', 'https://eldercare.acl.gov/'),
    ('Pro Seniors legal hotline (Ohio, age 60 and older)', 'https://www.proseniors.org/legal-services/legal-hotline/'),
])}'''
    toc = [('first', 'Least restrictive first'), ('plan', 'Papers to sign now'), ('va-fiduciary', 'VA fiduciary'),
           ('ohio-guardianship', 'Ohio probate guardianship'), ('next-steps', 'What to do next'), ('sources', 'Sources')]
    return page(t, 'Guardianship and Its Alternatives for Veterans and Older Adults (Ohio Probate Basics) | VHG',
                'Before guardianship: powers of attorney, health care agents, supported decision-making and VA fiduciaries. How Ohio probate guardianship works, with the rights of the person and costs for VA cases.',
                'Guardianship and the choices to try first',
                'When a veteran or older adult can no longer handle money or medical choices, families often hear “get guardianship.” Many people need less than that.',
                body, toc)


# ---------------------------------------------------------------- End of life
def end_of_life_page():
    t = TOPICS[3]
    body = f'''
<h2 id="hospice">VA hospice care</h2>
<p>Hospice is comfort care for a veteran with a terminal condition and less than 6 months to live who is no longer seeking treatment other than comfort care. It can be given at home, in a clinic or in an inpatient setting, including a VA Community Living Center. The team plans care with the veteran and family and offers grief support to the family afterward.</p>
<ul><li>Every veteran enrolled in VA health care is eligible if they have the clinical need.</li>
<li><strong>There are no copays for hospice care</strong>, whether VA provides it or a hospice under contract with VA.</li>
<li>VA works closely with community and home hospice agencies to provide care at home.</li></ul>
<p>Ask the veteran's doctor or VA social worker for a hospice referral.</p>
<h3>Palliative care</h3>
<p>Palliative care eases symptoms and suffering at any stage of a serious illness, and can be combined with treatment aimed at a cure. Enrolled veterans with the clinical need are eligible; copays may apply.</p>
<h3>We Honor Veterans</h3>
<p>{a('https://www.wehonorveterans.org/', 'We Honor Veterans')} was created by VA and the National Hospice and Palliative Care Organization to help community hospices care for veterans. When choosing a hospice, ask whether it takes part and how it supports veterans and their families.</p>
<p>Write down the veteran's wishes while they can share them. See <a href="guardianship.html#plan">health care powers of attorney and VA's advance directive</a>.</p>

<h2 id="burial-allowance">VA burial allowances (as of {CHECKED})</h2>
<p>VA helps pay burial and funeral costs if the veteran was not dishonorably discharged and, for example, was receiving VA pension or compensation at death, died while in VA care or a VA-contracted facility, or died from a service-connected disability.</p>
<div class="table-wrap"><table><caption class="sr">VA burial allowance amounts</caption>
<thead><tr><th scope="col">Situation</th><th scope="col">Amount</th></tr></thead>
<tbody><tr><th scope="row">Service-connected death on or after September 11, 2001</th><td>Up to $2,000</td></tr>
<tr><th scope="row">Death not service connected, on or after October 1, 2026</th><td>$1,032 burial allowance and $1,032 for a plot</td></tr></tbody></table></div>
<ul><li>The spouse, child, parent, executor, a family member or friend, or a funeral home or cemetery that paid the costs can apply, using VA Form 21P-530EZ or online.</li>
<li>A surviving spouse listed on the veteran's VA record usually does not need to apply: VA pays a set amount automatically after it learns of the death.</li>
<li>Time limit: when the death was not service connected, apply within 2 years of burial, with exceptions (no limit for plot, interment or transportation allowance, or when the veteran died under VA care).</li>
<li>VA can also pay back the cost of transporting the veteran's remains for burial in a VA national cemetery.</li></ul>

<h2 id="cemeteries">National and state veterans cemeteries in Ohio</h2>
<p>Burial in a VA national cemetery is open to veterans who met the minimum active duty requirement and were not dishonorably discharged. A spouse, a minor child and, in some cases, an unmarried adult child with a disability may also be eligible.</p>
<ul><li><strong>Ohio Western Reserve National Cemetery</strong>, 10175 Rawiga Road, Seville, OH 44273 · {tel('330-335-3069')}</li>
<li><strong>Dayton National Cemetery</strong>, 4400 West Third Street, Dayton, OH 45428 · {tel('937-268-2221')}</li>
<li><strong>Ohio Veterans Home Cemetery</strong>, 3416 Columbus Ave, Sandusky, OH 44870 · {tel('419-625-2454')} · Ohio's state veterans cemetery, built with VA grant funds</li></ul>
<p>To schedule a burial in a national cemetery at the time of need, the family or funeral home faxes the discharge papers to the National Cemetery Scheduling Office at 866-900-6417 and calls {tel('800-535-1117')}. Outside Ohio, {a('https://www.cem.va.gov/find-cemetery/', 'find a national or state veterans cemetery')}.</p>
<p>Ohio counties also have a duty to help: the county veterans service commission arranges a decent burial for an Ohio veteran, or the veteran's spouse, surviving spouse or parent, who dies without the means to pay. Ask the <a href="./#county-start">county veterans office</a>.</p>

<h2 id="pre-need">Plan ahead: pre-need eligibility</h2>
<p>A veteran or family member can ask VA ahead of time whether they are eligible for burial in a VA national cemetery. A decision in advance saves the family a step later.</p>
<ul><li>Apply online, or by mail or fax with VA Form 40-10007. By mail: NCA Evidence Intake Center, PO Box 5237, Janesville, WI 53547.</li>
<li>Include the DD214 if you have it. Someone applying for a person who cannot sign, such as a caregiver, a spouse, a court-appointed representative, someone with durable power of attorney or the head of the care facility, needs supporting papers and VA Form 21-22 or 21-22a.</li>
<li>Name a preferred national cemetery. VA cannot guarantee it, but will help the family choose another if needed.</li>
<li>State, territory and tribal veterans cemeteries have their own pre-need programs; contact the cemetery.</li></ul>

<h2 id="unclaimed">When no family claims the veteran's remains</h2>
<p>An unclaimed veteran can be buried in a VA national cemetery or a VA-funded state or tribal veterans cemetery, and whoever handles the burial can get help with the costs:</p>
<ul><li><strong>Casket or urn allowance:</strong> $1,394 for a casket or $161 for an urn that meets VA's standards, for burial in a national cemetery or a VA-funded state or tribal veterans cemetery when the veteran had no identifiable next of kin and not enough resources. Use VA Form 40-10088.</li>
<li><strong>Burial allowance, plot allowance and transportation</strong> to a national cemetery: VA Form 21P-530, marked “unclaimed remains.”</li></ul>
<p>The {a('https://www.miap.us/', 'Missing in America Project')}, a nonprofit veterans organization, works with private, state and federal partners to locate, identify and inter the unclaimed cremated remains of veterans.</p>

{roles('You can apply now for a pre-need decision and tell your family which cemetery you want. If hospice is right for you, it costs nothing in copays through VA.',
       'Keep the DD214 and marriage certificate where you can find them. If your spouse received VA pension or compensation, VA usually pays the burial amount to you automatically.',
       'Ask the funeral home to schedule a national cemetery burial and to file for the allowance. Ask the county veterans office about county burial help.',
       'Ask early whether the resident is enrolled in VA health care and has a pre-need decision. If a veteran dies with no family, tell the funeral home about VA’s unclaimed-veteran benefits and the Missing in America Project.')}
{sources([
    ('VA: Hospice care', 'https://www.va.gov/geriatrics/pages/Hospice_Care.asp'),
    ('VA: Palliative care', 'https://www.va.gov/geriatrics/pages/Palliative_Care.asp'),
    ('VA Geriatrics fact sheet (We Honor Veterans)', 'https://www.va.gov/Geriatrics/docs/PHCFactSheet.pdf'),
    ('VA: Veterans burial allowance and transportation benefits', 'https://www.va.gov/burials-memorials/veterans-burial-allowance/'),
    ('VA: Pre-need eligibility for burial in a VA national cemetery', 'https://www.va.gov/burials-memorials/pre-need-eligibility/'),
    ('VA National Cemetery Administration: Ohio Western Reserve National Cemetery', 'https://www.cem.va.gov/cems/nchp/ohiowesternreserve.asp'),
    ('VA National Cemetery Administration: Dayton National Cemetery', 'https://www.cem.va.gov/cems/nchp/dayton.asp'),
    ('VA National Cemetery Administration: Ohio cemeteries, including state veterans cemeteries', 'https://www.cem.va.gov/find-cemetery/state.asp?STATE=OH'),
    ('VA National Cemetery Administration: Unclaimed veteran remains', 'https://www.cem.va.gov/burial-memorial-benefits/unclaimed-Veteran-remains.asp'),
    ('Ohio Revised Code 5901.25: county burial of a veteran who dies without means', 'https://codes.ohio.gov/ohio-revised-code/section-5901.25'),
    ('Missing in America Project', 'https://www.miap.us/'),
])}'''
    toc = [('hospice', 'VA hospice and palliative care'), ('burial-allowance', 'Burial allowances'), ('cemeteries', 'Cemeteries in Ohio'),
           ('pre-need', 'Pre-need eligibility'), ('unclaimed', 'Unclaimed veterans'), ('next-steps', 'What to do next'), ('sources', 'Sources')]
    return page(t, 'Hospice, End-of-Life Care and Burial Benefits for Veterans | VHG',
                'VA hospice has no copays. Current VA burial allowances, Ohio’s national and state veterans cemeteries, pre-need eligibility, and burial help when a veteran’s remains are unclaimed.',
                'Hospice, end-of-life care and burial for veterans',
                'Comfort care, honor and a resting place: what VA provides at the end of a veteran’s life, and how families plan ahead.',
                body, toc)


# ---------------------------------------------------------------- Toxic exposure
def toxic_page():
    t = TOPICS[4]
    body = f'''
<h2 id="why">Why this matters in nursing homes</h2>
<p>Many veterans now in long-term care served in the Vietnam era. Several serious illnesses, including Parkinson's disease, ischemic heart disease, type 2 diabetes, high blood pressure and some cancers, are on VA's Agent Orange list. When a condition is “presumptive,” the veteran does not have to prove service caused it. They only need to meet the service requirement.</p>
<p>A veteran who has never filed, or was denied before, may now qualify for disability compensation. A surviving spouse may qualify for Dependency and Indemnity Compensation if the veteran died of one of these conditions.</p>

<h2 id="agent-orange">Agent Orange: conditions VA presumes</h2>
<p><strong>Cancers:</strong> bladder cancer; chronic B-cell leukemia; Hodgkin's disease; multiple myeloma; non-Hodgkin's lymphoma; prostate cancer; respiratory cancers, including lung cancer; some soft tissue sarcomas.</p>
<p><strong>Other illnesses:</strong> AL amyloidosis; chloracne; type 2 diabetes; high blood pressure (hypertension); hypothyroidism; ischemic heart disease; monoclonal gammopathy of undetermined significance (MGUS); Parkinsonism; Parkinson's disease; early-onset peripheral neuropathy; porphyria cutanea tarda. (Chloracne, early-onset peripheral neuropathy and porphyria cutanea tarda must have been at least 10% disabling within a year of exposure.)</p>
<p>High blood pressure and MGUS were added by the PACT Act. A condition not on the list can still be claimed with more evidence.</p>

<h2 id="where">Where VA presumes exposure</h2>
<ul><li>The Republic of Vietnam, any length of time, from January 9, 1962, to May 7, 1975, including aboard a U.S. military vessel in the inland waterways, or on a vessel no more than 12 nautical miles offshore of Vietnam and Cambodia (“Blue Water Navy”).</li>
<li>Any U.S. or Royal Thai military base in Thailand, January 9, 1962, to June 30, 1976.</li>
<li>Laos, December 1, 1965, to September 30, 1969.</li>
<li>Cambodia at Mimot or Krek, Kampong Cham Province, April 16 to April 30, 1969.</li>
<li>Guam or American Samoa or their territorial waters, January 9, 1962, to July 31, 1980.</li>
<li>Johnston Atoll, or a ship that called there, January 1, 1972, to September 30, 1977.</li>
<li>In or near the Korean Demilitarized Zone, September 1, 1967, to August 31, 1971.</li>
<li>Certain Air Force units with C-123 aircraft, and anyone who transported, tested or stored Agent Orange.</li></ul>
<div class="box"><h3>Denied before?</h3><p>A Blue Water Navy veteran denied in the past can file a Supplemental Claim based on the change in law. Anyone denied for a condition VA now presumes can also file a Supplemental Claim. A survivor can submit a new DIC application.</p></div>

<h2 id="pact">The PACT Act, burn pits and Gulf War service</h2>
<p>The PACT Act expanded VA health care and benefits for veterans exposed to burn pits, Agent Orange and other toxic substances. It added more than 20 presumptive conditions, including many cancers and breathing conditions, for veterans who served in the Gulf War or after September 11, 2001, in the countries VA lists, and added radiation cleanup and response efforts to VA's radiation list. Veterans who served in the Vietnam War, the Gulf War, Iraq, Afghanistan or another post-9/11 combat zone, or who were exposed to toxins in service, can enroll in VA health care without first applying for disability benefits.</p>
<p>PACT Act questions: {tel('800-698-2411')}.</p>

<h2 id="screening">The toxic exposure screening</h2>
<p>Every veteran enrolled in VA health care gets an initial toxic exposure screening and a follow-up at least once every 5 years. It asks about burn pits and other airborne hazards, Gulf War exposures, Agent Orange, radiation, Camp Lejeune water and other exposures, then points to benefits, registry exams and care. Ask for it at the next VA appointment, or ask the VA medical center for the toxic exposure screening navigator.</p>
<p>VA also offers a free Agent Orange Registry health exam for veterans who meet the service requirements. It is not a claim exam and is not needed to get benefits.</p>

<h2 id="how">How to file</h2>
<ul><li>Gather the DD214 or other separation papers showing where and when the veteran served, and a medical record showing the diagnosis. The facility's doctor or medical records office can provide the diagnosis.</li>
<li>Submit an intent to file to protect the start date while you gather records.</li>
<li>Get free help from an accredited representative: <a href="./#county-start">your county veterans office</a> or {a('https://www.va.gov/get-help-from-accredited-representative/find-rep/', 'VA’s representative search')}. See <a href="va-pension-aid-attendance.html#help">who may charge fees</a>.</li></ul>

{roles('If you served in Vietnam, Thailand, Korea near the DMZ or on a ship offshore, and you have one of the conditions above, ask your county veterans office to file for you.',
       'If your spouse died of a condition on this list, you may qualify for DIC, even if VA denied a claim before.',
       'Ask the facility for a current list of diagnoses and compare it with the list above. Find the DD214 or ask the county veterans office to request it.',
       'Ask veterans about service dates and places at admission. A resident with Parkinson’s disease, ischemic heart disease or diabetes who served in Vietnam is worth a referral to the county veterans office.')}
{sources([
    ('VA: Agent Orange exposure and disability compensation', 'https://www.va.gov/disability/eligibility/hazardous-materials-exposure/agent-orange/'),
    ('VA: The PACT Act and your VA benefits (including toxic exposure screenings)', 'https://www.va.gov/resources/the-pact-act-and-your-va-benefits/'),
    ('Public Law 116-23, Blue Water Navy Vietnam Veterans Act of 2019', 'https://www.congress.gov/bill/116th-congress/house-bill/299'),
    ('VA: Find a VA-accredited representative', 'https://www.va.gov/get-help-from-accredited-representative/find-rep/'),
])}'''
    toc = [('why', 'Why it matters in nursing homes'), ('agent-orange', 'Agent Orange conditions'), ('where', 'Where exposure is presumed'),
           ('pact', 'The PACT Act'), ('screening', 'Toxic exposure screening'), ('how', 'How to file'), ('next-steps', 'What to do next'), ('sources', 'Sources')]
    return page(t, 'Agent Orange, Blue Water Navy and PACT Act Help for Veterans and Survivors | VHG',
                'Agent Orange presumptive conditions and locations, Blue Water Navy, the PACT Act and VA’s toxic exposure screening, written for Vietnam-era veterans in nursing homes and their families.',
                'Agent Orange, the PACT Act and toxic exposure',
                'Many veterans in nursing homes served in the Vietnam era. VA now presumes many of their illnesses were caused by service, which can mean new benefits for the veteran or the surviving spouse.',
                body, toc)


# ---------------------------------------------------------------- Print sheets
FLYER_CSS = '''@font-face{font-family:'Atkinson Hyperlegible';font-weight:400;src:url(fonts/atkinson-hyperlegible-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Atkinson Hyperlegible';font-weight:700;src:url(fonts/atkinson-hyperlegible-latin-700-normal.woff2) format('woff2')}
@page{size:8.5in 11.0in;margin:0}
html,body{margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:816px;height:1056px;box-sizing:border-box;display:flex;flex-direction:column;background:#fff;font-family:'Atkinson Hyperlegible',system-ui,sans-serif;color:#18242c;overflow:hidden}
.top{background:#183449;color:#fff;padding:30px 48px 24px;display:flex;gap:24px;align-items:center}
.top .words{flex:1;min-width:0}.tag{display:inline-block;background:#e3c57d;color:#183449;font-size:13px;font-weight:700;letter-spacing:.08em;padding:6px 12px;border-radius:999px}
.top h1{margin:10px 0 8px;font-size:40px;line-height:1.06}.top p{margin:0;font-size:17px;line-height:1.4;color:#dfe8ec}
.qr{flex:none;background:#fff;border-radius:10px;padding:8px;text-align:center;color:#183449;font-size:13px;font-weight:700}.qr img{display:block;width:132px;height:132px}
.body{flex:1;padding:18px 48px 0;display:flex;flex-direction:column;gap:10px}
.body h2{margin:6px 0 0;font-size:21px;color:#183449}.body p,.body li{font-size:15.5px;line-height:1.4;margin:0}.body ul{margin:0;padding-left:22px}.body li{margin:3px 0}
.call{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.call div{border:2px solid #183449;border-radius:10px;padding:8px 12px}.call b{display:block;font-size:22px}.call span{font-size:13.5px;line-height:1.3;display:block}
.note{background:#f3efe3;border-left:5px solid #a07014;padding:8px 12px;border-radius:4px}
.foot{margin:10px 48px 0;padding:10px 0 20px;border-top:2px solid #183449;font-size:12.5px;line-height:1.4;color:#33434c;display:flex;gap:14px;align-items:center}.foot img{width:56px;height:56px;flex:none}'''


def flyer(t, title, lead, sections, calls):
    calls_html = '<div class="call">' + ''.join(f'<div><b>{escape(n)}</b><span>{escape(l)}</span></div>' for n, l in calls) + '</div>'
    url = BASE_URL.replace('https://', '') + t['slug']
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)} (one-page sheet)</title>
<!-- Print source for flyers/{t["flyer"]}.pdf, written by scripts/build_core_care.py. Rebuild with: node scripts/build_flyers.cjs {t["flyer"]} -->
<style>
{FLYER_CSS}
</style>
</head>
<body>
<div class="sheet">
<div class="top"><div class="words"><span class="tag">FOR VETERANS IN CARE AND THEIR FAMILIES</span><h1>{escape(title)}</h1><p>{escape(lead)}</p></div>
<div class="qr"><img src="qr-{t["flyer"]}.svg" alt="QR code that opens {escape(url)}">Scan for the full page</div></div>
<div class="body">
{sections}
{calls_html}
</div>
<div class="foot"><img src="vhg-logo-print.png" alt="Veteran Home Guardians logo"><div>Full page with sources: <b>{escape(url)}</b>. Facts checked {CHECKED}; agencies change figures, so confirm with them. Free from Veteran Home Guardians, an Ohio 501(c)(3) nonprofit. We are not VA and do not decide eligibility. Danger now: 911. Veterans Crisis Line: 988, press 1.</div></div>
</div>
</body>
</html>
'''


def flyers():
    out = {}
    t = TOPICS[0]
    out[t['flyer']] = flyer(t, 'VA pension with Aid and Attendance', 'Monthly help for wartime veterans and surviving spouses who need care and have limited income and savings.', '''
<h2>Who may qualify</h2><ul><li>Wartime service (World War II, Korea, Vietnam era, Gulf War) and not dishonorably discharged, or the surviving spouse of such a veteran.</li><li>Age 65 or older, disabled, or in a nursing home for long-term care because of a disability.</li><li>Net worth (savings and property, not the home or car, plus yearly income) under $163,699 (through November 30, 2026).</li></ul>
<h2>Why care costs matter</h2><ul><li>Out-of-pocket nursing home costs, including meals and lodging, are subtracted from the income VA counts. That can raise the payment.</li><li>Yearly maximum with Aid and Attendance: $29,093 for a veteran alone; $34,488 with a spouse; $18,697 for a surviving spouse (from December 1, 2025).</li></ul>
<div class="note"><b>Medicaid pays the nursing home?</b> A resident with no spouse or dependent child gets $90 a month in VA pension, and the facility cannot take it for the cost of care. Ask before changing any benefit.</div>
<h2>Use only free, accredited help</h2><ul><li>Gifts or transfers in the 3 years before applying can stop the pension for up to 5 years.</li><li>Walk away from anyone who promises you will qualify, sells trusts or annuities to qualify, or charges a fee to file.</li></ul>''',
        [('800-827-1000', 'VA benefits line'), ('800-488-8244', 'VA Inspector General: report a pension scheme'), ('County veterans office', 'Free help filing: find yours in the guide'), ('VA.gov', 'Search “find a VA accredited representative”')])
    t = TOPICS[1]
    out[t['flyer']] = flyer(t, 'Abuse, neglect or money being taken', 'You can report a concern about a veteran or older adult. You do not need proof. Many states let you report without giving your name.', '''
<h2>What to report</h2><ul><li><b>Abuse:</b> hitting, rough handling, threats, sexual contact without consent, isolation.</li><li><b>Neglect:</b> missing food, medicine, hygiene or care, or a person who can no longer care for themselves.</li><li><b>Exploitation:</b> money, property, a pension or VA benefit taken or signed away under pressure.</li></ul>
<h2>Where to call</h2><ul><li><b>At home:</b> Adult Protective Services (APS) in that state. Every state's reporting route is on the full page.</li><li><b>In a nursing home or assisted living:</b> the administrator and the long-term care ombudsman, a free advocate for residents.</li><li><b>Money stolen or a crime:</b> also call the police.</li></ul>
<div class="note"><b>A VA fiduciary misusing VA benefits?</b> Call the VA Fiduciary program at 888-407-0144 and the VA Inspector General at 800-488-8244.</div>''',
        [('855-644-6277', 'Ohio Adult Protective Services (855-OHIO-APS), or aps.jfs.ohio.gov'), ('800-677-1116', 'Eldercare Locator: local help in any state'), ('888-407-0144', 'VA Fiduciary program'), ('800-488-8244', 'VA Office of Inspector General')])
    t = TOPICS[2]
    out[t['flyer']] = flyer(t, 'Guardianship and the choices to try first', 'A court guardianship takes rights away. Many families can manage with less, especially if papers are signed early.', '''
<h2>Sign while the person can</h2><ul><li><b>Financial power of attorney:</b> an agent for money and property. In Ohio it keeps working after incapacity unless it says otherwise.</li><li><b>Health care power of attorney and living will:</b> who decides, and what care the person wants. VA patients can use VA Form 10-0137.</li><li><b>Supported decision-making:</b> the person decides, with trusted helpers.</li></ul>
<h2>VA money: the VA fiduciary</h2><ul><li>VA decides if a beneficiary can manage VA payments. A fiduciary handles VA benefits only; the person keeps the right to vote, sign papers and manage other money.</li></ul>
<h2>If guardianship is needed in Ohio</h2><ul><li>The county probate court decides after a hearing, on clear and convincing evidence, and must consider less restrictive options offered as evidence.</li><li>The person may have a lawyer, a family member or friend present and an independent evaluation. A limited guardianship can leave other rights in place.</li></ul>''',
        [('800-488-6070', 'Pro Seniors legal hotline (Ohio, age 60+)'), ('888-407-0144', 'VA Fiduciary program'), ('800-677-1116', 'Eldercare Locator: legal help in any state'), ('Probate court', 'In the county where the person lives')])
    t = TOPICS[3]
    out[t['flyer']] = flyer(t, 'Hospice and burial for veterans', 'Comfort care, honor and a resting place: what VA provides, and how families plan ahead.', '''
<h2>VA hospice and palliative care</h2><ul><li>Enrolled veterans with the clinical need are eligible. <b>No copays for hospice</b>, from VA or a hospice under contract with VA.</li><li>Ask the doctor or VA social worker. Ask hospices whether they take part in We Honor Veterans.</li></ul>
<h2>Burial benefits (as of November 2026)</h2><ul><li>Service-connected death: up to $2,000. Other deaths on or after October 1, 2026: $1,032 burial and $1,032 plot allowance. Form 21P-530EZ.</li><li><b>Plan ahead:</b> apply for a pre-need eligibility decision (VA Form 40-10007).</li><li><b>No family?</b> VA buries unclaimed veterans with honor and helps with casket, urn and transport costs.</li></ul>
<h2>Ohio veterans cemeteries</h2><ul><li>Ohio Western Reserve National Cemetery, Seville: 330-335-3069</li><li>Dayton National Cemetery: 937-268-2221</li><li>Ohio Veterans Home Cemetery, Sandusky (state): 419-625-2454</li></ul>''',
        [('800-535-1117', 'National Cemetery Scheduling Office'), ('800-827-1000', 'VA benefits line (burial allowance)'), ('County veterans office', 'Burial help for Ohio veterans without means'), ('miap.us', 'Missing in America Project: unclaimed remains')])
    t = TOPICS[4]
    out[t['flyer']] = flyer(t, 'Agent Orange and the PACT Act', 'Many nursing home veterans served in the Vietnam era. VA now presumes many of their illnesses came from service.', '''
<h2>Conditions VA presumes from Agent Orange</h2><p>Parkinson's disease and Parkinsonism; ischemic heart disease; type 2 diabetes; high blood pressure; hypothyroidism; MGUS; AL amyloidosis; bladder, prostate and respiratory cancers; multiple myeloma; Hodgkin's and non-Hodgkin's lymphoma; chronic B-cell leukemia; some soft tissue sarcomas; and others on the full page.</p>
<h2>Where exposure is presumed</h2><ul><li>Vietnam 1962 to 1975, including inland waterways and ships within 12 nautical miles offshore (Blue Water Navy).</li><li>Thai bases 1962 to 1976; Laos; parts of Cambodia; Guam and American Samoa; Johnston Atoll; the Korean DMZ 1967 to 1971.</li></ul>
<div class="note"><b>Denied before?</b> File a Supplemental Claim. A surviving spouse may qualify for DIC if the veteran died of a listed condition.</div>
<h2>Screening</h2><ul><li>Every veteran in VA health care gets a toxic exposure screening, repeated at least every 5 years. Ask at the next VA visit.</li></ul>''',
        [('800-698-2411', 'VA PACT Act line'), ('800-827-1000', 'VA benefits line'), ('County veterans office', 'Free help filing a claim'), ('DD214', 'Bring separation papers and a list of diagnoses')])
    return out


# ---------------------------------------------------------------- State card and facilities row
CARD_CSS = '''.care-topics{background:#fff;border:1px solid var(--line,#d9dfda);border-top:4px solid var(--green,#335947);border-radius:9px;padding:20px 22px;margin:22px 0}
.care-topics h2{margin:0 0 6px}.care-topics>p{margin:6px 0 12px}.care-aps{background:#edf2ef;border-radius:6px;padding:10px 14px}
.care-aps a[href^="tel:"]{font-weight:700;white-space:nowrap}.care-links{list-style:none;padding:0;margin:12px 0 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.care-links a{display:block;min-height:44px;padding:10px 12px;border:1px solid #6f8078;border-radius:6px;text-decoration:none}.care-links a:hover{background:#edf2ef}
.care-links strong{display:block}.care-links span{display:block;font-size:15px;color:#3d4f48}
@media(max-width:760px){.care-links{grid-template-columns:minmax(0,1fr)}}@media print{.care-topics{display:none}}
'''


def aps_line(code, name, rec):
    """Plain HTML for a state's APS line, shared by the static card and the script."""
    lead = 'Worried about abuse, neglect or money being taken? '
    where = f'<a href="elder-abuse.html#aps-{code.lower()}">How to report in {escape(name)}</a>'
    if rec['phones']:
        p = rec['phones'][0]
        return lead + f'<strong>{escape(name)} Adult Protective Services:</strong> {tel(p["number"])} · {where}'
    return lead + f'<strong>Report to {escape(name)} Adult Protective Services.</strong> {where}'


def card(code, name):
    rec = aps_data()['states'][code]
    links = ''.join(f'<li><a href="{t["slug"]}"><strong>{escape(t["short"])}</strong><span>{escape(t["line"])}</span></a></li>' for t in TOPICS)
    return ('<section id="care-topics" class="care-topics" aria-labelledby="care-topics-title"><h2 id="care-topics-title">For veterans in nursing homes and their families</h2>'
            '<p>Plain answers for the veteran, the spouse, the adult children and the facility social worker.</p>'
            f'<p class="care-aps" id="care-aps" data-state="{code}">{aps_line(code, name, rec)}</p><ul class="care-links">{links}</ul></section>')


def card_script(states):
    data = aps_data()['states']
    lines = {s['code']: aps_line(s['code'], s['name'], data[s['code']]) for s in states if s['code'] in data}
    return ('// Keeps the "For veterans in nursing homes" card on the guide pages showing the chosen state\'s\n'
            '// Adult Protective Services line when the visitor changes state. Written by scripts/build_core_care.py.\n'
            '(function(){var L=' + json.dumps(lines, ensure_ascii=True).replace('<', '\\u003c') + ';\n'
            'function show(){var s=document.getElementById(\'edition-state\'),p=document.getElementById(\'care-aps\');'
            'if(!s||!p||!L[s.value]||p.dataset.state===s.value)return;p.dataset.state=s.value;p.innerHTML=L[s.value]}\n'
            'function start(){var s=document.getElementById(\'edition-state\'),c=document.getElementById(\'coverage-detail\');'
            'if(s)s.addEventListener(\'change\',show);if(c&&window.MutationObserver)new MutationObserver(show).observe(c,{childList:true});show()}\n'
            'if(document.readyState===\'loading\')document.addEventListener(\'DOMContentLoaded\',start);else start()})();\n')


def versioned(path, text):
    return path + '?v=' + hashlib.sha256(text.encode()).hexdigest()[:10]


def add_cards(result, states):
    """Add the pointer card to every state page (Ohio is index.html), before "What help do you need?"."""
    script = card_script(states)
    out = {'assets/care-topics.css': CARD_CSS, 'assets/care-topics.js': script}
    head = f'<link rel="stylesheet" href="{versioned("assets/care-topics.css", CARD_CSS)}">'
    tail = f'<script defer src="{versioned("assets/care-topics.js", script)}"></script>'
    for s in states:
        page = s['page']
        html = result[page]
        anchor = '<section id="directory"'
        assert html.count(anchor) == 1, page + ': directory section'
        html = html.replace(anchor, card(s['code'], s['name']) + anchor, 1)
        html = html.replace('</head>', head + '</head>', 1)
        html = html.replace('</body>', tail + '</body>', 1)
        out[page] = html
    return out


def add_facilities_links(html):
    anchor = '<p class="notice"><strong>What this list is.</strong>'
    assert html.count(anchor) == 1, 'facilities notice'
    links = ' '.join(f'<a href="{t["slug"]}">{escape(t["short"])}</a>' for t in TOPICS)
    row = ('<h2 id="residents-families">For residents and families</h2>'
           '<p>Help for veterans in care and the people around them. To report abuse or neglect in Ohio, call Adult Protective Services at '
           + tel('855-644-6277') + '.</p><nav class="quick" aria-label="Help for residents and families">' + links + '</nav>')
    return html.replace(anchor, row + anchor, 1)


def pages():
    return [t['slug'] for t in TOPICS]


def outputs(states):
    result = {
        TOPICS[0]['slug']: pension_page(),
        TOPICS[1]['slug']: abuse_page(states),
        TOPICS[2]['slug']: guardianship_page(),
        TOPICS[3]['slug']: end_of_life_page(),
        TOPICS[4]['slug']: toxic_page(),
    }
    # Full Open Graph and Twitter tags for shared links (scripts/landing.py); titles stay as written here.
    import landing
    result = {k: landing.complete_social(v) for k, v in result.items()}
    for fid, html in flyers().items():
        result['flyers/src/' + fid + '.html'] = html
    return result


def make_qr():
    import io
    import qrcode
    import qrcode.image.svg
    for t in TOPICS:
        target = ROOT / 'flyers/src' / ('qr-' + t['flyer'] + '.svg')
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4,
                             image_factory=qrcode.image.svg.SvgPathImage)
        code.add_data(BASE_URL + t['slug'])
        code.make(fit=True)
        buffer = io.BytesIO()
        code.make_image().save(buffer)
        target.write_bytes(buffer.getvalue())
        print('wrote', target.relative_to(ROOT))


if __name__ == '__main__':
    if '--qr' in sys.argv:
        make_qr()
