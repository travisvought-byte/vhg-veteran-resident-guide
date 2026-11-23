"""Build three stand-alone pages of the Veteran Resource Guide, run by scripts/build_public.py:

- mst.html: help after military sexual trauma (MST), written to the survivor.
- survivors.html: Gold Star and surviving families. DIC and Survivors Pension are already in the guide's
  surviving-spouse view, so this page links there instead of repeating them.
- es/index.html: the Ohio front page's essentials in Spanish, with hreflang links both ways and a language
  switch on the English front page (add_language_links).

Every number and rule on these pages was read on the official page named under it, on the date shown.
Names of agencies and programs stay in English on the Spanish page, with a Spanish gloss where it helps.
Corrections go to the same email as the rest of the guide (the "Report a problem" path).
"""
from html import escape
from urllib.parse import quote

BASE = 'https://guide.vethomeguard.org/'
EMAIL = 'travis@vethomeguard.org'
CHECKED = 'November 23, 2026'
CHECKED_ES = '23 de noviembre de 2026'


def e(text):
    return escape(text or '', quote=True)


def tel(display, digits=None, ext=None):
    digits = digits or ''.join(c for c in display if c.isdigit())
    href = 'tel:' + digits + (',' + ext if ext else '')
    label = display + (f', ext. {ext}' if ext else '')
    return f'<a href="{href}">{e(label)}</a>'


def src(items, checked=CHECKED, word='Source', checked_word='Checked'):
    links = '; '.join(f'<a href="{e(u)}" rel="noopener">{e(t)}</a>' for u, t in items)
    return f'<p class="small source">{word}: {links}. {checked_word} {checked}.</p>'


STYLE = '''<style>
.topic{max-width:980px}.topic section{margin-bottom:34px}
.card{background:#fff;border:1px solid var(--line);border-top:4px solid var(--gold);border-radius:8px;padding:18px 20px;margin:0 0 16px}
.card h3{margin-top:0}.card ul{padding-left:22px}.card li{margin:6px 0}
.phone-line{font-size:20px;margin:8px 0}.phone-line a[href^="tel:"]{display:inline-block;min-height:44px;line-height:44px}
.calm{background:#e8eeea;border-radius:8px;padding:14px 20px}.calm p{margin:6px 0}
.crisis-note{font-size:15px;color:#3d4f48}
table{border-collapse:collapse;width:100%;background:#fff}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.jumps{display:flex;flex-wrap:wrap;gap:8px 18px;padding:0;list-style:none}.jumps a{display:inline-block;min-height:44px;line-height:44px}
.lang-switch{margin:0 0 6px;font-size:15px}.lang-switch a{color:#fff}
.fix{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 18px;font-size:16px}
@media(max-width:700px){.topic{padding:16px}th,td{padding:6px}}
</style>'''


def head(title, desc, path, lang='en', alternates=''):
    url = BASE + (path[:-len('index.html')] if path.endswith('/index.html') else path)
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">{alternates}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{e(url)}"><meta property="og:type" content="website">
<meta property="og:image" content="{BASE}assets/vhg-logo.png">
<link rel="stylesheet" href="{'../' if '/' in path else ''}assets/family-guide.css">
{STYLE}
<script src="{'../' if '/' in path else ''}assets/analytics.js" defer></script></head><body>
'''


def nav():
    return ('<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="mst.html">Help after MST</a>'
            '<a href="survivors.html">Gold Star and surviving families</a><a href="family-guide.html">Family Guide</a>'
            '<a href="flyers.html">Printable flyers</a></nav>')


def footer(subject):
    ask = 'mailto:' + EMAIL + '?subject=' + quote(subject)
    return (f'<footer class="topic" style="margin:auto;padding:18px 24px"><p>Free from <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, '
            'an Ohio nonprofit that visits veterans and publishes free guides. This page explains where to go; it does not decide eligibility. '
            'Numbers come from the official pages named under each card and are not telephone-confirmed. '
            f'See something wrong or out of date? <a href="{ask}">Report a problem</a> ({EMAIL}). Please do not include personal or health details.</p>'
            '<p><a href="./">Back to the Veteran Resource Guide</a> · <a href="privacy.html">Privacy</a></p></footer>\n</body></html>\n')


# ---------------------------------------------------------------- MST

VA_MST = ('https://www.va.gov/health-care/health-needs-conditions/military-sexual-trauma/', 'VA: Military sexual trauma (MST)')
VA_MST_CLAIMS = ('https://www.va.gov/resources/military-sexual-trauma-and-disability-compensation/',
                 'VA: Military sexual trauma and disability compensation')
VA_MST_COORD = ('https://www.mentalhealth.va.gov/MENTALHEALTH/msthome/vha-mst-coordinators.asp', 'VA: VHA MST Coordinators, by state')
PTSD_MST = ('https://www.ptsd.va.gov/understand/types/sexual_trauma_military.asp', 'VA National Center for PTSD: Military sexual trauma')
CFR_3304 = ('https://www.ecfr.gov/current/title-38/section-3.304', '38 CFR 3.304(f)(5)')
VET_CENTER_MST = ('https://www.vetcenter.va.gov/Military_Sexual_Trauma.asp', 'Vet Centers: Military sexual trauma')
SAFE_HELPLINE = ('https://www.safehelpline.org/', 'DoD Safe Helpline')
KURTA = ('https://www.army.mil/article/193169/dod_offers_new_policy_guidance_for_veterans_discharge_upgrade_requests',
         'Army.mil, August 30, 2017: DoD offers new policy guidance for veterans’ discharge upgrade requests')
VA_UPGRADE = ('https://www.va.gov/resources/request-a-discharge-upgrade-or-correction/', 'VA: Request a discharge upgrade or correction')

# Ohio's VA health care systems and the MST Coordinator line VA publishes for each (names change, so only the line is shown).
OHIO_MST_COORDINATORS = [
    ('Chillicothe VA Medical Center', '740-773-1141', '6310'),
    ('Cincinnati VA Medical Center', '513-475-6880', None),
    ('Louis Stokes Cleveland VA Medical Center', '216-791-3800', '66849'),
    ('Columbus: Chalmers P. Wylie VA Ambulatory Care Center', '614-257-5331', None),
    ('Dayton VA Medical Center', '937-268-6511', '3495'),
]


def mst_page(discharge_page=None):
    title = 'Help after military sexual trauma (MST): free VA care, claims and support | Veteran Resource Guide'
    desc = ('Free, private help after military sexual trauma: VA care with no disability rating needed, MST coordinators, '
            'Vet Center counseling, disability claims, discharge upgrades and support for men and women.')
    coord_rows = ''.join(f'<tr><td>{e(n)}</td><td>{tel(p, ext=x)}</td></tr>' for n, p, x in OHIO_MST_COORDINATORS)
    discharge = ('<p>The guide’s <a href="index.html?view=records">records and discharge upgrade section</a> has the forms and helpers.')
    if discharge_page:
        discharge += (f' The guide\u2019s <a href="{e(discharge_page)}">liberal consideration page</a> and '
                      '<a href="bad-paper/index.html">bad paper section</a> walk through upgrading an other than honorable discharge, step by step, with free help.')
    discharge += '</p>'
    body = f'''{head(title, desc, 'mst.html')}{nav()}
<div class="hero"><p class="eyebrow">MILITARY SEXUAL TRAUMA</p><h1>Help after military sexual trauma</h1>
<p>If something happened to you while you served, you are not alone, and it is not too late to get help. This page lays out your options in plain words. You choose what to do, and when.</p></div></header>
<main class="topic" id="main">
<p class="crisis-note">If you are in crisis right now: call {tel('988')} and press 1, or text 838255. In danger: call 911.</p>
<ul class="jumps" aria-label="On this page"><li><a href="#care">Free VA care</a></li><li><a href="#coordinator">MST coordinators</a></li><li><a href="#vet-center">Vet Centers</a></li><li><a href="#claims">Disability claims</a></li><li><a href="#discharge">Your discharge</a></li><li><a href="#men">For men</a></li><li><a href="#serving">Still serving</a></li></ul>

<section id="care"><h2>Free care from VA, even without a rating or a report</h2>
<div class="card"><h3>What VA says about MST-related care</h3><ul>
<li>VA provides free treatment for any physical or mental health condition related to MST.</li>
<li>You don’t need to have reported it at the time, or have any other proof, to get this care.</li>
<li>It is open to veterans and most former service members, including many with an other than honorable discharge. The usual length-of-service rules don’t apply.</li>
<li>You don’t need a VA disability rating (service connection).</li>
<li>You don’t have to talk about MST when you sign up for VA health care.</li>
<li>You can ask to see a clinician of a particular sex if that feels more comfortable.</li></ul>
<p>Current service members may need a referral from the Defense Department for some services.</p>
{src([VA_MST, PTSD_MST])}</div></section>

<section id="coordinator"><h2>Talk to an MST coordinator</h2>
<div class="card"><p>Every VA medical facility has an MST coordinator. They are a contact person for anything related to MST and can help you get care. You can call and simply say you would like to speak with the MST coordinator.</p>
<h3>Ohio’s VA health care systems</h3>
<table><thead><tr><th>VA health care system</th><th>MST coordinator line</th></tr></thead><tbody>{coord_rows}</tbody></table>
<p><a href="{VA_MST_COORD[0]}" rel="noopener">MST coordinators in every state</a> (VA’s list; choose your state).</p>
{src([VA_MST_COORD, VA_MST])}</div></section>

<section id="vet-center"><h2>Counseling at a Vet Center</h2>
<div class="card"><p>Vet Centers are small community counseling centers, separate from VA hospitals. They offer counseling for any veteran or service member who experienced MST, including National Guard and Reserve members, whenever they served.</p>
<p class="phone-line">Vet Center Call Center: {tel('877-927-8387')}, any hour</p>
<p>Ask to talk with someone about MST-related counseling, or to be connected with the Vet Center nearest you.</p>
{src([VET_CENTER_MST, VA_MST])}</div></section>

<section id="claims"><h2>Disability compensation for conditions related to MST</h2>
<div class="card"><p>If MST left you with a condition such as PTSD, depression or a physical injury, you can file a VA disability claim. Many people never reported what happened, and VA knows that.</p>
<h3>Evidence VA can use (the “markers”)</h3>
<p>Besides service and personnel records, Defense Department reports and investigations, VA accepts evidence from other sources, for example:</p>
<ul><li>Statements from a chaplain, counselor, family member or fellow service member, or from a rape crisis center</li>
<li>Civilian police or medical records, and personal journals or diaries</li>
<li>Signs that things changed after the event: a request for a transfer, a drop in work performance, relationship trouble, more drinking or drug use, panic attacks or depression</li>
<li>Records such as pregnancy tests or tests for sexually transmitted infections</li></ul>
<p>VA says this indirect evidence doesn’t need to show a clear cause. Before VA turns down a PTSD claim based on an assault, the rule requires it to tell you about these other kinds of evidence so you can send them.</p>
<h3>Help with the claim</h3>
<ul><li>Every VA regional office has a male and a female MST outreach coordinator who can help you file, and claim processors get specialized training.</li>
<li>You can ask for a male or a female examiner for your claim exam.</li>
<li>A free accredited representative, such as a county veterans service officer, can file with you. <a href="index.html?view=claims">Find claims help in your state</a>.</li>
<li>If a claim was denied before, you can ask for a decision review.</li></ul>
{src([VA_MST_CLAIMS, CFR_3304])}</div></section>

<section id="discharge"><h2>If MST affected your discharge</h2>
<div class="card"><p>Sometimes what happened led to trouble in service and a discharge that doesn’t reflect who you are. Since 2017 the Defense Department has told its discharge review boards to give <strong>liberal consideration</strong> to upgrade requests involving mental health conditions, including those from sexual assault or sexual harassment. You can give the board evidence of a diagnosis, or evidence that you experienced the assault or harassment.</p>
<p>Remember: you can get MST-related care from VA now, while you wait, even with an other than honorable discharge.</p>
<p>VA’s discharge upgrade tool asks a few questions and tells you which form and board to use. Questions: {tel('800-827-1000')}, Monday to Friday, 8 a.m. to 9 p.m. ET.</p>
{discharge}
{src([KURTA, VA_UPGRADE, VA_MST])}</div></section>

<section id="men"><h2>For men</h2>
<div class="card"><p>MST happens to men as well as women, and many of the veterans who tell VA about MST are men. Everything on this page is for you too: the free care, the counselors, the claims help and the privacy.</p>
<ul><li>You can ask for a male or a female clinician, and a male or a female claim examiner.</li>
<li>Every VA regional office has a male MST outreach coordinator.</li>
<li>The MST coordinators and Vet Centers above serve every veteran who experienced MST.</li></ul>
{src([PTSD_MST, VA_MST_CLAIMS, VA_MST])}</div></section>

<section id="serving"><h2>Still serving</h2>
<div class="card"><p><strong>DoD Safe Helpline</strong> offers anonymous support to members of the military community affected by sexual assault, by phone or online chat.</p>
<p class="phone-line">{tel('877-995-5247')} · <a href="https://online.safehelpline.org/" rel="noopener">Chat online</a></p>
{src([SAFE_HELPLINE])}</div>
<div class="card"><p><strong>Women Veterans Call Center</strong>: {tel('855-829-6636')}. Women veterans can call, text or chat with a trained woman about VA care and benefits.</p>
{src([('https://www.womenshealth.va.gov/wvcc.asp', 'VA: Women Veterans Call Center')], 'November 17, 2026')}</div></section>

<div class="calm"><p>You can go at your own pace. It is okay to start with one phone call, or just to bookmark this page for later.</p></div>
</main>
{footer('Veteran Resource Guide: MST page')}'''
    return body


# ---------------------------------------------------------------- Gold Star and surviving families

TAPS = ('https://taps.org/helpline', 'TAPS National Military Survivor Helpline')
MOS_REPS = ('https://militaryonesource.mil/casualty-assistance/survivor-support/gold-star-and-surviving-family-member-representatives',
            'Military OneSource: Gold Star and surviving family member representatives')
MOS_HONOR = ('https://www.militaryonesource.mil/casualty-mortuary-affairs/bereavement-grief/honoring-gold-star-families/',
             'Military OneSource: Honoring Gold Star families')
ARMY_SOS = ('https://www.usar.army.mil/ARFP/SOS/', 'U.S. Army Reserve: Survivor Outreach Services')
ARMY_SOS2 = ('https://armymwr.com/programs-and-services/personal-assistance/survivor-outreach', 'Army MWR: Survivor Outreach Services')
NAVY = ('https://www.mynavyhr.navy.mil/Support-Services/Casualty/LTAP/Survivor-Resources/', 'MyNavy HR: Survivor resources')
DD3 = ('https://www.esd.whs.mil/Portals/54/Documents/DD/forms/dd/dd0003.pdf', 'DD Form 3')
FRY = ('https://www.va.gov/family-and-caregiver-benefits/education-and-careers/fry-scholarship/', 'VA: Fry Scholarship')
DEA = ('https://www.va.gov/family-and-caregiver-benefits/education-and-careers/dependents-education-assistance/',
       'VA: Survivors’ and Dependents’ Educational Assistance (DEA, Chapter 35)')
WOS = ('https://dam.assets.ohio.gov/image/upload/highered.ohio.gov/sgs/wos/WOS-Application.pdf',
       'Ohio Department of Higher Education: War Orphans Scholarship application')
ODVS_GUIDE = ('https://dam.assets.ohio.gov/image/upload/dvs.ohio.gov/benefits/resource-guide-2026.pdf',
              'Ohio Department of Veterans Services: Benefits Resource Guide 2026')
OSO = ('https://dam.assets.ohio.gov/image/upload/highered.ohio.gov/sgs/guidance-memos/FA27-006.pdf',
       'Ohio Department of Higher Education: Ohio Safety Officers College Memorial Fund, guidance memo FA 27-006 (July 2, 2026)')
ORC_PLATES = ('https://codes.ohio.gov/ohio-revised-code/section-4503.546', 'Ohio Revised Code 4503.546 (Gold Star Family license plates)')
ORC_HOMESTEAD = ('https://codes.ohio.gov/ohio-revised-code/section-323.152/1-1-2026', 'Ohio Revised Code 323.152 (homestead reduction)')

BRANCHES = [
    ('Army', 'Survivor Outreach Services (SOS)', '833-313-1960', None, 'https://www.usar.army.mil/ARFP/SOS/'),
    ('Marine Corps', 'Long Term Assistance Program', '866-210-3421', '2', 'https://www.hqmc.marines.mil/Agencies/Casualty-MFPC/Longterm/'),
    ('Navy', 'Long Term Assistance Program', '901-874-0083', None, 'https://www.mynavyhr.navy.mil/Support-Services/Casualty/'),
    ('Navy', 'Navy Gold Star Program', '888-509-8759', None, 'https://www.mynavyhr.navy.mil/Support-Services/Casualty/LTAP/Survivor-Resources/'),
    ('Air Force and Space Force', 'Air Force Families Forever', '703-693-0683', None, 'https://www.afpc.af.mil/Military-and-Family/Air-Force-Families-Forever/'),
    ('Coast Guard', 'Casualty Matters Office', '202-795-6637', None, 'https://www.dcms.uscg.mil/PSD/fs/Casualty-Matters/'),
]


def survivors_page():
    title = 'Gold Star and surviving military families: TAPS, survivor benefits and school help | Veteran Resource Guide'
    desc = ('For families who lost a service member or veteran: TAPS, casualty and survivor support by branch, Gold Star lapel buttons, '
            'the Fry Scholarship and DEA, and Ohio survivor benefits.')
    rows = ''.join(f'<tr><td>{e(b)}</td><td><a href="{e(u)}" rel="noopener">{e(p)}</a></td><td>{tel(n, ext=x)}</td></tr>'
                   for b, p, n, x, u in BRANCHES)
    return f'''{head(title, desc, 'survivors.html')}{nav()}
<div class="hero"><p class="eyebrow">GOLD STAR AND SURVIVING FAMILIES</p><h1>For families who have lost a service member or veteran</h1>
<p>We are so sorry for your loss. Here is the help that exists for you, starting with people who understand. Take what you need, when you need it.</p></div></header>
<main class="topic" id="main">
<ul class="jumps" aria-label="On this page"><li><a href="#talk">Someone to talk to</a></li><li><a href="#money">Monthly payments</a></li><li><a href="#branch">Help from the branch</a></li><li><a href="#buttons">Gold Star lapel buttons</a></li><li><a href="#school">School</a></li><li><a href="#ohio">Ohio survivor benefits</a></li><li><a href="#states">Other states</a></li></ul>

<section id="talk"><h2>Someone to talk to, any hour</h2>
<div class="card"><h3>TAPS (Tragedy Assistance Program for Survivors)</h3>
<p>TAPS supports people grieving someone who served in the military. Its helpline is answered at any hour, and it offers casework, grief counseling, education support, suicide loss support, peer mentors, and programs for children and young adults.</p>
<p class="phone-line">{tel('800-959-8277')} (800-959-TAPS), any hour</p>
{src([TAPS, NAVY])}</div>
<div class="card"><h3>Military OneSource</h3><p>Free support for surviving families, including help sorting out benefits.</p>
<p class="phone-line">{tel('800-342-9647')} · En español: {tel('877-888-0727')}</p>
{src([MOS_HONOR, NAVY])}</div></section>

<section id="money"><h2>Monthly payments: DIC and Survivors Pension</h2>
<div class="card"><p>Two VA payments may help a surviving spouse, children or parents: Dependency and Indemnity Compensation (DIC) and Survivors Pension. The guide’s <a href="index.html?view=survivors">surviving spouse section</a> explains them and how to get free help applying.</p></div></section>

<section id="branch"><h2>Help from the service branch, for as long as you need it</h2>
<div class="card"><p>Each branch has people whose job is to support surviving families long after the funeral, whatever the cause and wherever the death happened. They can help with benefits questions, and they are also the people to call if you are not satisfied with the casualty assistance you received.</p>
<table><thead><tr><th>Branch</th><th>Program</th><th>Phone</th></tr></thead><tbody>{rows}</tbody></table>
<p>The Army’s Survivor Outreach Services supports families of fallen soldiers regardless of component, duty status, location or manner of death, for as long as they want support.</p>
<p>If a branch liaison can’t resolve a problem, the Defense Department’s Casualty, Mortuary Affairs and Military Funeral Honors office can help: {tel('571-372-5319')}.</p>
{src([MOS_REPS, ARMY_SOS, ARMY_SOS2, NAVY])}</div></section>

<section id="buttons"><h2>Gold Star lapel buttons</h2>
<div class="card"><ul>
<li><strong>Gold Star Lapel Button:</strong> for the next of kin of members who died in combat or other qualifying hostile circumstances, including terrorist attacks and certain peacekeeping operations. Next of kin includes spouses (remarried or not), parents and stepparents, children and stepchildren, and brothers and sisters, including half and step siblings.</li>
<li><strong>Next of Kin of Deceased Personnel Lapel Button:</strong> for families of service members who died in a duty status and are not eligible for the Gold Star button.</li></ul>
<p>The buttons are normally presented without any application. If you are eligible and never received one, or need a replacement, send <a href="{DD3[0]}" rel="noopener">DD Form 3</a> to the military department listed on the form.</p>
<p>Gold Star Mother’s and Family’s Day is the last Sunday in September, and Gold Star Spouses Day is April 5.</p>
{src([MOS_HONOR, DD3])}</div></section>

<section id="school"><h2>School for children and spouses</h2>
<div class="card"><h3>Fry Scholarship</h3><p>For the child or surviving spouse of a service member or member of the Selected Reserve who died on or after September 11, 2001, in the line of duty or in other qualifying ways. It can pay up to 36 months of tuition and fees, housing, and books and supplies.</p>
{src([FRY])}</div>
<div class="card"><h3>Survivors’ and Dependents’ Educational Assistance (DEA, Chapter 35)</h3><p>For the child or spouse of a service member who died in the line of duty, or of a veteran who is permanently and totally disabled because of a service-connected disability, among other situations.</p>
{src([DEA])}</div>
<div class="card"><h3>Applying</h3><p>Both use the same form, VA Form 22-5490, online or by mail. Tell the school’s certifying official that you applied. If you qualify for both, VA’s Fry page explains how they can be combined and the limits.</p>
{src([FRY, DEA])}</div></section>

<section id="ohio"><h2>Ohio survivor benefits</h2>
<div class="card"><h3>Ohio War Orphans and Severely Disabled Veterans’ Children Scholarship</h3>
<p>Helps pay general and instructional fees at Ohio colleges for children of certain veterans who died, are missing in action or prisoners of war, or are severely disabled (for example, a service-connected rating of 60% or more). Students apply between their 16th and 25th birthdays. The application lists the service and Ohio residency rules. The current application must be postmarked by May 15, 2027.</p>
<p class="phone-line">Ohio Department of Higher Education: {tel('614-752-9528')}</p>
{src([WOS])}</div>
<div class="card"><h3>Ohio Safety Officers College Memorial Fund</h3><p>Helps pay undergraduate and certificate tuition for the children and spouses of service members killed in the line of duty in Operation Enduring Freedom, Operation Iraqi Freedom or a combat zone designated by the President. The student must live in Ohio now (not necessarily when the death happened) and not qualify for the War Orphans Scholarship. Ask the college’s financial aid office about it.</p>
{src([OSO])}</div>
<div class="card"><h3>Your county veterans service office</h3><p>Every Ohio county has a veterans service office. Its accredited service officers help veterans, dependents and surviving spouses file VA claims, can provide temporary emergency financial help, and point you to other local and state resources. Their help is free.</p>
<p class="phone-line">Ohio Department of Veterans Services: {tel('877-644-6838')} (877-OHIO-VET) · <a href="./#county-start">Find your county office in this guide</a></p>
{src([ODVS_GUIDE])}</div>
<div class="card"><h3>Property tax and license plates</h3><ul>
<li>If your late spouse was a veteran with a total disability rating from VA, you may qualify for Ohio’s homestead exemption on the home you own and live in. Apply with your county auditor.</li>
<li>Immediate family of a service member who died in a combat zone (spouse, parents and stepparents, brothers and sisters, children and stepchildren, and grandparents) can get Gold Star Family license plates from the Ohio BMV, free of the usual registration taxes and fees.</li></ul>
{src([ORC_HOMESTEAD, ORC_PLATES, ODVS_GUIDE])}</div></section>

<section id="states"><h2>Other states</h2>
<div class="card"><p>Every state has its own survivor benefits, such as college tuition help, property tax relief and license plates. Open your state in this guide and choose <strong>Help for a surviving spouse</strong>, or call your county or state veterans office and ask, “What survivor benefits does our state offer?”</p>
<p><a href="index.html?view=survivors">Survivor help in your state</a></p></div></section>
</main>
{footer('Veteran Resource Guide: survivors page')}'''


# ---------------------------------------------------------------- Spanish: the Ohio front page's essentials

ES_NEEDS = [
    ('Para todos los veteranos', [
        ('claims', 'Pagos por discapacidad y reclamos', 'Presentar un reclamo, pedir una revisión, encontrar a un representante acreditado'),
        ('health', 'Atención médica del VA y exposición a tóxicos', 'Inscripción, evaluación de la ley PACT y veteranas'),
        ('crisis', 'Consejería y salud mental', 'Vet Centers, la línea de crisis y salud mental del VA'),
        ('education', 'Estudios y el GI Bill', 'Beneficios de educación y capacitación'),
        ('jobs', 'Empleo y capacitación', 'American Job Centers y ayuda de empleo del VA'),
        ('housing', 'Vivienda, préstamos hipotecarios y personas sin hogar', 'Ayuda con vivienda, préstamos del VA y proveedores locales'),
        ('records', 'Documentos, tarjetas de identificación y mejora de la baja', 'DD214, identificación de veterano y corrección de una baja'),
        ('newvet', 'Acaba de salir del servicio', 'Las primeras llamadas del VA y por dónde empezar'),
    ]),
    ('Personas mayores, cuidadores y cuidado a largo plazo', [
        ('benefits', 'Ayuda para pagar el cuidado', 'Pensión, beneficios y preguntas sobre Medicaid'),
        ('care', 'Atención del VA y apoyo para cuidadores', 'Inscripción, cuidado de enfermería y equipos de atención'),
        ('survivors', 'Ayuda para un cónyuge sobreviviente', 'Beneficios para sobrevivientes y entierro'),
        ('rights', 'Problemas con el cuidado o los derechos', 'Ombudsman (defensor), derechos de las personas con discapacidad y ayuda legal'),
        ('accessibility', 'Rampas y accesibilidad en el hogar', 'Formas de pago, lista de HISA y planificación del proyecto'),
    ]),
]


def spanish_alternates(es_path='es/'):
    return (f'\n<link rel="alternate" hreflang="en" href="{BASE}">'
            f'\n<link rel="alternate" hreflang="es" href="{BASE}{es_path}">'
            f'\n<link rel="alternate" hreflang="x-default" href="{BASE}">')


def es_card(title, body, phone=None, sources=(), checked=CHECKED_ES):
    out = f'<div class="card"><h3>{title}</h3>{body}'
    if phone:
        out += f'<p class="phone-line">{phone}</p>'
    if sources:
        out += src(sources, checked, 'Fuente', 'Revisado el')
    return out + '</div>'


def spanish_page():
    title = 'Guía de recursos para veteranos de Ohio, en español | Veteran Home Guardians'
    desc = ('Ayuda gratis para veteranos de Ohio y sus familias: línea de crisis, intérprete gratis del VA, oficina de veteranos '
            'del condado, reclamos, atención médica, vivienda y cuidado a largo plazo.')
    needs = ''
    for group, items in ES_NEEDS:
        needs += f'<h3>{e(group)}</h3><ul>' + ''.join(
            f'<li><a href="../index.html?view={k}" hreflang="en"><strong>{e(t)}</strong></a><br><span class="small">{e(s)}</span></li>'
            for k, t, s in items) + '</ul>'
    fix = ('mailto:' + EMAIL + '?subject=' + quote('Guía para veteranos en español: corrección') +
           '&body=' + quote('Página: guide.vethomeguard.org/es/\nQué debe corregirse:\n\n(Por favor, no incluya datos personales ni de salud.)'))
    va_lang = ('https://www.va.gov/resources/how-to-get-free-language-assistance-from-va/', 'VA: How to get free language assistance')
    va_es = ('https://www.va.gov/asistencia-y-recursos-en-espanol/', 'VA: Asistencia y recursos del VA en español')
    return f'''{head(title, desc, 'es/index.html', 'es', spanish_alternates())}<header><nav aria-label="Principal"><a href="./">Guía en español</a><a href="../" hreflang="en" lang="en">English</a><a href="../mst.html" hreflang="en">Trauma sexual militar (MST)</a><a href="../survivors.html" hreflang="en">Familias Gold Star y sobrevivientes</a></nav>
<div class="hero"><p class="lang-switch">Idioma: <strong>Español</strong> · <a href="../" hreflang="en" lang="en">English</a></p><p class="eyebrow">VETERAN HOME GUARDIANS</p><h1>Guía de recursos para veteranos de Ohio</h1>
<p>Ayuda gratis para veteranos, cónyuges sobrevivientes, personas mayores y sus familias en Ohio. Aquí está lo esencial en español. Las guías detalladas están en inglés; puede pedir un intérprete gratis en cada llamada.</p></div></header>
<main class="topic" id="main">
<section aria-labelledby="ahora"><h2 id="ahora">¿Necesita ayuda ahora?</h2>
<div class="card"><p>Crisis: llame al {tel('988')} y oprima 1 (Veterans Crisis Line, línea de crisis para veteranos), o envíe un mensaje de texto al 838255. Peligro inmediato: llame al 911.</p>
<p>Veteranos sin hogar o a punto de perder su vivienda: {tel('877-424-3838')}, las 24 horas (National Call Center for Homeless Veterans).</p>
{src([VA_MST, ('https://www.va.gov/homeless/nationalcallcenter.asp', 'VA: National Call Center for Homeless Veterans')], CHECKED_ES, 'Fuente', 'Revisado el')}</div></section>

<section aria-labelledby="interprete"><h2 id="interprete">Pida un intérprete gratis</h2>
{es_card('El VA ofrece intérpretes sin costo', '<p>El VA ofrece intérpretes y otra ayuda con el idioma, gratis, a veteranos y familiares. Llame a MyVA411, la línea principal de información del VA, oprima 0 y diga al agente que desea un intérprete de español. En un centro médico del VA, solo dígale a un empleado que desea un intérprete.</p>', f'MyVA411: {tel("800-698-2411")}, las 24 horas, todos los días', [va_lang, va_es])}</section>

<section aria-labelledby="local"><h2 id="local">Su primer contacto local: la oficina de veteranos del condado</h2>
{es_card('County Veterans Service Office (oficina de servicios para veteranos del condado)', '<p>Cada condado de Ohio tiene una oficina de servicios para veteranos. Sus representantes acreditados ayudan gratis a veteranos, dependientes y cónyuges sobrevivientes con los reclamos del VA y la ayuda económica temporal de emergencia, y les indican otros recursos locales y del estado.</p><p><a href="../index.html#county-start" hreflang="en">Busque la oficina de su condado</a> (la lista está en inglés).</p>', f'Ohio Department of Veterans Services: {tel("877-644-6838")} (877-OHIO-VET)', [ODVS_GUIDE])}</section>

<section aria-labelledby="necesita"><h2 id="necesita">¿Qué ayuda necesita?</h2>
<p>Cada enlace abre esa parte de la guía, en inglés, con los contactos de Ohio.</p>
<div class="card">{needs}</div></section>

<section aria-labelledby="salud"><h2 id="salud">Atención médica, consejería y veteranas</h2>
{es_card('VA health care (atención médica del VA)', '<p>Para inscribirse en la atención médica del VA o hacer preguntas sobre la inscripción.</p>', tel('877-222-8387'), [('https://www.va.gov/health-care/how-to-apply/', 'VA: How to apply for VA health care')])}
{es_card('Vet Centers (centros comunitarios de consejería)', '<p>Consejería individual, de grupo, de pareja y familiar, sin costo, para veteranos y miembros del servicio que califican, incluidos la Guardia Nacional y la Reserva, y sus familias.</p>', f'Vet Center Call Center: {tel("877-927-8387")}, a cualquier hora', [('https://www.vetcenter.va.gov/', 'Vet Centers')], '17 de noviembre de 2026')}
{es_card('Women Veterans Call Center (línea para veteranas)', '<p>Las veteranas pueden llamar, enviar un mensaje de texto o chatear con una mujer capacitada sobre la atención y los beneficios del VA.</p>', tel('855-829-6636'), [('https://www.womenshealth.va.gov/wvcc.asp', 'VA: Women Veterans Call Center')], '17 de noviembre de 2026')}
{es_card('Después del trauma sexual militar (MST)', '<p>El VA ofrece tratamiento gratis para afecciones relacionadas con el trauma sexual militar. No necesita haberlo reportado en su momento ni tener una calificación de discapacidad. <a href="../mst.html" hreflang="en">Lea la guía completa</a> (en inglés).</p>', None, [VA_MST])}</section>

<section aria-labelledby="mayores"><h2 id="mayores">Personas mayores y cuidado a largo plazo</h2>
{es_card('Area Agency on Aging (agencia local para personas mayores)', '<p>Ayuda en casa, comidas, transporte, apoyo para cuidadores y preguntas sobre Medicaid. No hace falta ser veterano.</p>', f'Ohio Department of Aging: {tel("866-243-5678")}', [('https://compass.aging.ohio.gov/find-information?category=caregivers', 'Ohio Aging Compass')])}
{es_card('Long-Term Care Ombudsman (defensor de residentes de hogares de cuidado)', '<p>Si tiene problemas con el cuidado en un hogar de ancianos, una residencia asistida o con servicios en casa, el ombudsman le ayuda gratis y de forma confidencial.</p>', tel('800-282-1206'), [('https://www.cms.gov/about-cms/contact/directory/department-aging-ohio-elder-rights-unit/1553936', 'CMS: Ohio Department of Aging, Elder Rights Unit')])}</section>

<section aria-labelledby="familias"><h2 id="familias">Familias que perdieron a un ser querido</h2>
{es_card('Familias Gold Star y sobrevivientes', '<p>Apoyo a cualquier hora de TAPS (Tragedy Assistance Program for Survivors), pagos del VA para sobrevivientes (DIC y Survivors Pension), becas como la Fry Scholarship y beneficios de Ohio. <a href="../survivors.html" hreflang="en">Lea la guía completa</a> (en inglés).</p>', f'TAPS: {tel("800-959-8277")}, a cualquier hora · Military OneSource en español: {tel("877-888-0727")}', [TAPS, NAVY])}</section>

<section aria-labelledby="mas"><h2 id="mas">Más en español</h2>
<p><a href="{va_es[0]}" rel="noopener">Asistencia y recursos del VA en español</a>: formularios, beneficios para sobrevivientes y derechos civiles, del propio VA.</p></section>

<p class="fix">¿Ve algo que deba corregirse, en la traducción o en un dato? <a href="{e(fix)}">Escríbanos</a> a {EMAIL} y lo arreglaremos.</p>
</main>
<footer class="topic" style="margin:auto;padding:18px 24px"><p>Gratis, de parte de <a href="https://www.vethomeguard.org/">Veteran Home Guardians</a>, una organización sin fines de lucro de Ohio. Esta página indica a dónde acudir; no decide quién califica. Los números vienen de las páginas oficiales indicadas en cada tarjeta.</p>
<p><a href="../" hreflang="en" lang="en">English</a> · <a href="../privacy.html" hreflang="en">Privacidad (en inglés)</a></p></footer>
</body></html>
'''


def add_language_links(index_html):
    """The English front page: hreflang links in the head and a small language switch in the header."""
    if 'hreflang="es"' not in index_html:
        index_html = index_html.replace(f'<link rel="canonical" href="{BASE}">',
                                        f'<link rel="canonical" href="{BASE}">' + spanish_alternates(), 1)
    switch = ('<p class="lang-link" style="margin:0 0 10px;text-align:right;font-size:15px">'
              '<a href="es/" hreflang="es" lang="es" style="color:#fff">Español</a></p>')
    if switch not in index_html:
        index_html = index_html.replace('<header><div class="brand-header">', '<header>' + switch + '<div class="brand-header">', 1)
    return index_html


def outputs(discharge_page='bad-paper/liberal-consideration.html'):
    return {'mst.html': mst_page(discharge_page), 'survivors.html': survivors_page(), 'es/index.html': spanish_page()}


def pages():
    return ['mst.html', 'survivors.html', 'es/']
