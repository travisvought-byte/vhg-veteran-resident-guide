"""Utah referral edition: independent county maps and shared national resources."""
import copy
import json
import re
from pathlib import Path
from pa_edition import replace_line
from unified_guide import section


def utah_resources(root, ohio):
    ids = json.loads((root / 'data/public/federal-resource-ids.json').read_text())
    shared = [copy.deepcopy(r) for r in ohio if r['program_id'] in ids]
    for r in shared:
        r.update(service_area=['National'], state='shared')
    return shared + json.loads((root / 'data/public/ut-programs.json').read_text()) + json.loads((root / 'data/public/ut-regional-referrals.json').read_text())


def make_ut(html, resources, counties):
    # Replace data before adapting markup; never relabel another state's records.
    for name in ['DATA', 'COUNTIES']:
        html = replace_line(html, 'const '+name+'=', 'const '+name+'=[];')
    html = html.replace('Ohio', 'Utah').replace('All 88', 'All 29').replace('all 88', 'all 29')
    html = html.replace('<option value="OH">Utah</option>', '<option value="OH">Ohio</option>')
    html = html.replace("const STATE='OH';", "const STATE='UT';")
    html = html.replace('county veterans office', 'regional veterans contact').replace('county veterans offices', 'regional veterans contacts')
    html = html.replace('county office', 'regional veterans contact')
    html = html.replace('Statewide edition · Updated October 8, 2026', 'Utah edition · Updated October 14, 2026')
    # Utah keeps the shared checklist, but not Ohio law, county funds or transition programs.
    html = html.replace('Utah’s waiver rule specifies proposal and approval requirements; VA and other funders have their own processes.', 'Ask the Utah waiver administrator about assessment, written service-plan authorization and accepted providers.')
    html = html.replace('https://codes.ohio.gov/ohio-administrative-code/rule-5160-44-13', 'https://medicaid.utah.gov/medicaid-long-term-care-and-waiver-programs/')
    html = html.replace('Utah home modification authorization and provider rules', 'Utah Medicaid waiver screening and program contacts')
    html = html.replace('href="share.html"', 'href="share-ut.html"')
    html = html.replace('href="prototype-data.json"', 'href="data/public/utah-resources.json"').replace('href="data/public/ohio-county-veterans-offices.json"', 'href="data/public/utah-county-veterans-offices.json"')
    community = section(html, 'community-guide')
    html = html.replace(community, re.sub(r'<p id="ohio-bingo-link">.*?</p>', '', community))
    priority = ['ut-claims', 'ut-aging', 'ut-ship', 'ut-waiver', 'ut-ombudsman', 'ut-at', 'r02-aid-attendance-housebound', 'r02-va-pension', 'r02-survivors-pension']
    routes = dict(
        benefits=['ut-claims','ut-ship','ut-waiver','r02-va-pension','r02-aid-attendance-housebound','r02-disability-increase','r02-pension-medicaid-rule','r02-survivors-pension','r02-dic','va-accredited-help'],
        survivors=['ut-claims','r02-survivors-pension','r02-dic','r02-aid-attendance-housebound','r02-va-burial','va-accredited-help','nara-discharge-records'],
        care=['ut-waiver','ut-new-choices','ut-caregiver','ut-alternatives','r02-va-health-enrollment','va-location-finder','r02-va-cnh','r02-va-clc','r02-general-caregiver','r02-family-caregiver','r02-hospice','r02-palliative'],
        rights=['ut-ombudsman','ut-aging'], local=['ut-aging','ut-caregiver','ut-alternatives','ut-waiver','ut-new-choices','ut-at','ut-211'],
        housing=['ut-211','va-housing-help','va-location-finder','va-accredited-help','nara-discharge-records'])
    topics = dict(daily=['ut-aging','ut-caregiver','ut-alternatives','ut-waiver','ut-new-choices'],accessibility=['ut-at','ut-waiver','ut-new-choices','ut-aging'],vision=['ut-at','ut-aging'],hearing=['ut-at','ut-aging'],memory=['alz-dementia-support','ut-caregiver','ut-aging'],costs=['ut-ship','ut-waiver','ut-alternatives','ut-aging'],rights=['ut-ombudsman','ut-aging'])
    for name, value in [('priority', priority), ('routes', routes), ('seniorTopics', topics)]:
        html = replace_line(html, 'const '+name+'=', 'const '+name+'='+json.dumps(value)+';')
    html = replace_line(html, 'routes.accessibility=', "routes.accessibility=['va-hisa','va-sah','va-sha','va-tra','ut-at','ut-waiver','ut-new-choices','ut-aging','va-location-finder',...DATA.filter(x=>x.regional_role==='aging_agency').map(x=>x.program_id)];")
    html = replace_line(html, 'routes.seniors=', "routes.seniors=[...new Set(Object.values(seniorTopics).flat()),...DATA.filter(x=>x.regional_role).map(x=>x.program_id),'cms-care-compare'];")
    for line in (ROOT / 'assets/utah-adapter.js').read_text().splitlines():
        match = re.match(r'function (\w+)\(', line)
        if not match:
            continue
        name = match[1]
        if name == 'agingContactsHTML':
            html = html.replace('function officeCard(', line+'\nfunction officeCard(', 1)
        else:
            html = replace_line(html, 'function '+name+'(', line)
    for name,value in [('DATA',resources),('COUNTIES',counties)]:
        html = replace_line(html, 'const '+name+'=', 'const '+name+'='+json.dumps(value,ensure_ascii=True).replace('<','\\u003c')+';')
    return html


ROOT = Path(__file__).resolve().parents[1]
