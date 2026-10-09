"""Build one public interface from the existing source-grounded state adapters."""
import json,re

def section(html, ident):
    start=re.search(r'<section\b[^>]*\bid="'+ident+r'"[^>]*>',html).start()
    depth=0
    for m in re.finditer(r'</?section\b[^>]*>',html[start:]):
        depth+= -1 if m.group().startswith('</') else 1
        if depth==0:return html[start:start+m.end()]
    raise ValueError(ident)

def unified_outputs(root, editions):
    names={'OH':'Ohio','PA':'Pennsylvania','NY':'New York','MI':'Michigan','KY':'Kentucky'}
    pages={'OH':'index.html','PA':'pa.html','NY':'ny.html','MI':'mi.html','KY':'ky.html'}
    base=editions['index.html']
    script=re.search(r'<script>(.*?)</script>',base,re.S).group(1)
    configs=[]
    override_names=['officeCard','renderCounty','renderOfficeList','audience','renderAccessibility','renderSeniorGuide']
    for state,page in pages.items():
        html=editions[page]; js=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
        data=re.search(r'^const DATA=(.*);$',js,re.M).group(1)
        counties=re.search(r'^const COUNTIES=(.*);$',js,re.M).group(1)
        init=js[js.index('const priority='):js.index('const STATE=')]
        functions=[]
        for name in override_names+['veteransContactsHTML','agingContactsHTML']:
            m=re.search(r'^function '+name+r'\(.*$',js,re.M)
            if m:functions.append(re.sub(r'function (\w+)\(',lambda match: match[1]+':function(',m.group()).replace(' function', ',function').replace('} countyContactsHTML:', '},countyContactsHTML:'))
        markup={k:section(html,k) for k in ['seniors-guide','community-guide','accessibility-guide','staff-guide']}
        configs.append(json.dumps(state)+':{name:'+json.dumps(names[state])+',data:'+data+',counties:'+counties+',markup:'+json.dumps(markup)+',configure:function(){'+init+'return {priority,routes,seniorTopics,routeNames};},'+','.join(functions)+'}')
    # Common rendering and event handling, with only genuinely state-specific routing in adapters.
    common=script[script.index('const $='):]
    begin=common.index('const priority=');end=common.index('const tel=')
    common=common[:begin]+"let DATA=[],COUNTIES=[],STATE='OH',priority=[],routes={},seniorTopics={},routeNames={},route='priority';\nconst regionalIDs=role=>DATA.filter(x=>x.regional_role===role).map(x=>x.program_id);\nconst officeLegacyIds=new Set(['morrow-vso','knox-vso','marion-vso','delaware-vso']);\n"+common[end:]
    begin=common.index('COUNTIES.forEach');end=common.index('function officeCard')
    common=common[:begin]+common[end:]
    for name in override_names:
        common=re.sub(r'^function '+name+r'\(.*$', 'function '+name+'(...args){return EDITIONS[STATE].'+name+'(...args)}',common,flags=re.M)
    common=re.sub(r'^const national=.*$',"const national=a=>['statewide','national','federal',EDITIONS[STATE].name.toLowerCase()].includes(a.toLowerCase());",common,flags=re.M)
    common=common.replace("'All Ohio counties'","'All '+EDITIONS[STATE].name+' counties'")
    # Use a single canonical URL for every state and preserve public filters only.
    common=common.replace("u.search='';u.hash='';","u.pathname=u.pathname.replace(/[^/]*$/, '');u.search='';u.hash='';u.searchParams.set('state',STATE);")
    common=common.replace("renderCounty();renderAccessibility();renderSeniorGuide();","renderCounty();renderAccessibility();renderSeniorGuide();renderHelper();")
    # Existing state-only details remain inside the adapter, not duplicated public pages.
    common=common[:common.index('const params=new URLSearchParams')]
    helpers=(root/'assets/guide-runtime.js').read_text()
    unified=base[:base.index('<script>')]
    unified=re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="Find veteran, senior and disability support in Ohio, Pennsylvania, New York, Michigan and Kentucky. County contacts and caregiver handoffs.">', unified)
    unified=re.sub(r'<title>.*?</title>','<title>Veteran Resident Resource Guide | Veteran Home Guardians</title>',unified)
    unified=unified.replace('Ohio Veteran Resident<br>Resource Guide','Veteran Resident<br>Resource Guide').replace('Veteran Home Guardians · All 88 Ohio counties','Veteran Home Guardians')
    unified=unified.replace('Useful contacts for veterans, surviving spouses, families and care-facility staff. Start with a county, then choose the help you need.','Find support for yourself or someone you care for.')
    unified=re.sub(r'<div class="coverage notice">.*?</div>', '', unified, flags=re.S)
    unified=unified.replace('Browse contacts for all 88 county veterans offices','Browse county contacts')
    unified=unified.replace('Most phones come from Ohio AMVETS’ 2025–2026 directory. Source links and review dates are shown. Call to confirm hours and the current intake process.','Source links and review dates are shown. Confirm hours and intake with the agency.')
    unified=unified.replace('Statewide edition · Updated October 8, 2026','Updated October 9, 2026')
    unified=unified.replace('<div class="quick-links" aria-label="Common needs">','<div class="quick-links" aria-label="Common needs"><button data-route="aid" id="aid-open" hidden><strong>Veteran and aid organizations</strong><span>Local housing, legal aid, utilities and transport</span></button>')
    unified=unified.replace('assets/share-preview.png','assets/vhg-logo.png')
    for key,value in {'og:title':'Support for veterans, seniors and families | VHG','twitter:title':'Support for veterans, seniors and families | VHG','og:description':'Find your next contact for benefits, care, housing and support in five states. Free to use.','twitter:description':'Find your next contact for benefits, care, housing and support in five states. Free to use.','og:image:width':'715','og:image:height':'715','og:image:alt':'Veteran Home Guardians logo'}.items():
        unified=re.sub(r'(<meta (?:property|name)="'+re.escape(key)+r'" content=")[^"]*(">)',lambda m:m[1]+value+m[2],unified)
    unified=unified.replace('<a class="jump" href="#staff-guide">Staff handoff guide</a>','<a class="jump" href="#helper-guide" id="helper-header">I’m helping someone</a>')
    unified=unified.replace('<p>Use the edition for the state where help is needed.</p>','').replace('aria-label="State edition"','aria-label="Location"')
    coverage=section(unified,'edition-coverage')
    unified=unified.replace(coverage,'<details id="edition-coverage" class="edition-coverage"><summary>Coverage and source checks</summary><div id="coverage-detail"></div></details>')
    unified=re.sub(r'<p id="ohio-aid-link">.*?</p>','',unified)
    unified=unified.replace('<label for="county">Choose an Ohio county</label>','<label for="county">County</label>')
    unified=unified.replace('<div class="quick-links" aria-label="Common needs">','<div class="quick-links" aria-label="Common needs"><button id="helper-open"><strong>I’m helping someone</strong><span>For family, caregivers and facility staff</span></button>')
    helper=(root/'templates/helper.html').read_text()
    unified=unified.replace('<section id="directory"',helper+'<section id="directory"',1)
    unified=unified.replace('Housing or missing service records','Housing and homelessness')
    unified=unified.replace('<p>Choose a need to see practical starting points. Your county selection stays in place.</p>','')
    unified=unified.replace('<p id="county-intro">County veterans offices can help you explore benefits and the right referral route. If the resident recently moved into a facility, ask which county should handle the referral.</p>','<p id="county-intro">Choose a county to find local contacts.</p>')
    unified=unified.replace('</head>','<link rel="stylesheet" href="assets/unified.css"></head>')
    unified=re.sub(r'<section id="urgent-help".*?</section>', '<section id="urgent-help" class="notice" aria-labelledby="urgent-title"><h2 id="urgent-title">Need help now?</h2><p>Crisis: <a href="tel:988">988</a> (veterans: press 1). Immediate danger: <a href="tel:911">911</a>.<br>Veteran housing help: <a href="tel:8774243838">877-424-3838</a> · 24/7.</p><p><a href="?view=crisis">Mental health support</a> · <a href="?view=housing">Housing resources</a></p></section>', unified, flags=re.S)
    unified+='\n<script src="assets/guide.js"></script></body></html>\n'
    result={'index.html':unified,'assets/guide.js':common+'\nconst EDITIONS={'+','.join(configs)+'};\n'+helpers}
    for state,page in pages.items():
        if state=='OH':continue
        result[page]='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+names[state]+' Veteran Resource Guide</title><link rel="canonical" href="https://travisvought-byte.github.io/vhg-veteran-resident-guide/?state='+state+'"><p><a href="./?state='+state+'">Open the '+names[state]+' guide</a></p><script>const u=new URL("./",location.href);u.search=location.search;u.searchParams.set("state","'+state+'");u.hash=location.hash;location.replace(u.href);</script></html>\n'
    return result
