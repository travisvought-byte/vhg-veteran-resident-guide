"""Build one public interface from the existing source-grounded state adapters."""
import hashlib,json,re
from html import escape
import landing

BASE_URL='https://guide.vethomeguard.org/'

def section(html, ident):
    start=re.search(r'<section\b[^>]*\bid="'+ident+r'"[^>]*>',html).start()
    depth=0
    for m in re.finditer(r'</?section\b[^>]*>',html[start:]):
        depth+= -1 if m.group().startswith('</') else 1
        if depth==0:return html[start:start+m.end()]
    raise ValueError(ident)

def state_list(states):
    """Name every state while the list is short; summarize once it would crowd a preview."""
    names=[s['name'] for s in states]
    if len(names)>8:return str(len(names))+' states'
    return ', '.join(names[:-1])+' and '+names[-1] if len(names)>1 else names[0]

def count_words(n):
    return ['zero','one','two','three','four','five','six','seven','eight','nine','ten'][n] if n<=10 else str(n)

# Where each state sits on the square tile maps used elsewhere (the county and VA location hubs): (column, row)
# on an 11 by 8 grid.
TILES={'AK':(0,0),'ME':(10,0),'WI':(5,1),'VT':(9,1),'NH':(10,1),
 'WA':(0,2),'ID':(1,2),'MT':(2,2),'ND':(3,2),'MN':(4,2),'IL':(5,2),'MI':(6,2),'NY':(8,2),'MA':(9,2),
 'OR':(0,3),'NV':(1,3),'WY':(2,3),'SD':(3,3),'IA':(4,3),'IN':(5,3),'OH':(6,3),'PA':(7,3),'NJ':(8,3),'CT':(9,3),'RI':(10,3),
 'CA':(0,4),'UT':(1,4),'CO':(2,4),'NE':(3,4),'MO':(4,4),'KY':(5,4),'WV':(6,4),'VA':(7,4),'MD':(8,4),'DE':(9,4),
 'AZ':(1,5),'NM':(2,5),'KS':(3,5),'AR':(4,5),'TN':(5,5),'NC':(6,5),'SC':(7,5),'DC':(8,5),
 'OK':(3,6),'LA':(4,6),'MS':(5,6),'AL':(6,6),'GA':(7,6),
 'HI':(0,7),'TX':(3,7),'FL':(8,7)}

# The state map: real state shapes, the same map Nina's Map uses (data/map/us-states.json, from U.S. Census
# Bureau shapes). Travis asked for it on November 28, 2026 in place of the square tile map. Every state is a plain
# link, so it works before the page script loads and with the keyboard; the same links follow as a list by name,
# which is also the easier way to reach the smallest states on a phone.
from pathlib import Path
US_MAP=json.loads((Path(__file__).resolve().parent.parent/'data/map/us-states.json').read_text())

def place_map(states, current, world_count, open_map):
    """The guide's starting point: a map of every state, a list of the same states by name, then the world pages."""
    by_code={s['code']:s for s in states}
    assert set(by_code)=={m['code'] for m in US_MAP['states']},'the map and the guide cover the same states'
    def href(s):return './' if s['page']=='index.html' else s['page']
    def cur(code):return ' aria-current="page"' if code==current else ''
    shapes=''.join('<a href="'+href(by_code[m['code']])+'" data-state="'+m['code']+'"'+cur(m['code'])+' aria-label="'+escape(by_code[m['code']]['name'])+'"><title>'+escape(by_code[m['code']]['name'])+'</title><path d="'+m['d']+'"/></a>' for m in US_MAP['states'])
    svg=('<svg class="usmap" viewBox="0 0 '+str(US_MAP['width'])+' '+str(US_MAP['height'])+'" role="group" aria-labelledby="usmap-t usmap-d">'
         '<title id="usmap-t">Map of the United States</title><desc id="usmap-d">Each state is a link to its page in this guide. The same links are in the list of states after the map.</desc>'
         '<g>'+shapes+'</g></svg>')
    names=''.join('<li><a href="'+href(s)+'" data-state="'+s['code']+'"'+cur(s['code'])+'>'+escape(s['name'])+'</a></li>' for s in sorted(states,key=lambda s:s['name']))
    listing='<details class="state-list"><summary>All states by name</summary><ul class="state-tiles" aria-label="States">'+names+'</ul></details>'
    world='<p class="world-start"><a href="world/"><strong>Outside the United States</strong><span>Emergency numbers and veterans contacts in '+str(world_count)+' countries, and VA help for U.S. veterans abroad</span></a></p>'
    body=svg+listing+world
    if open_map:
        return '<section id="place-start" class="place-start" aria-labelledby="place-title"><h2 id="place-title">Where do you need help?</h2><p>Choose your state on the map, or open the list of states by name.</p>'+body+'</section>'
    return '<details id="place-start" class="place-start"><summary>Show the map of states and countries</summary>'+body+'</details>'

def unified_outputs(root, editions, states):
    names={s['code']:s['name'] for s in states}
    pages={s['code']:s['page'] for s in states}
    statewide={s['code']:[n.lower() for n in s.get('statewide_area_names',[])] for s in states}
    meta={s['code']:{'sharePage':s['share_page'],'files':{'offices':s['offices'],'resources':s['resources']},'coverageNote':s.get('coverage_note')} for s in states}
    base=editions['index.html']
    # Who arrives on each page and what they came for (data/landing/states.json). Ohio is the site root,
    # which is also the home page for every state, so it opens with the home landing.
    landings={}
    for s in states:
        if s.get('base'):landings[s['code']]=landing.home(root);continue
        records=json.loads((root/s['programs']).read_text())+json.loads((root/s['referrals']).read_text())
        landings[s['code']]=landing.state(s['code'],s['name'],records,root)
    assert set(landings)-{states[0]['code']}==landing.states_codes(root),'every state has landing text, and only registered states'
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
        land=landings[state]
        # Switching state in place shows that state's own heading and opening (assets/guide-runtime.js).
        land_js={'title':land['title'],'h1':land['h1'],'eyebrow':land['eyebrow'],'intro':land['intro']}
        configs.append((state,'{name:'+json.dumps(names[state])+',statewideNames:'+json.dumps(statewide[state])+',sharePage:'+json.dumps(meta[state]['sharePage'])+',files:'+json.dumps(meta[state]['files'])+',coverageNote:'+json.dumps(meta[state]['coverageNote'])+',landing:'+json.dumps(land_js)+',data:'+data+',counties:'+counties+',markup:'+json.dumps(markup)+',configure:function(){'+init+'return {priority,routes,seniorTopics,routeNames};},'+','.join(functions)+'}'))
    # Common rendering and event handling, with only genuinely state-specific routing in adapters.
    common=script[script.index('const $='):]
    begin=common.index('const priority=');end=common.index('const tel=')
    common=common[:begin]+"let DATA=[],COUNTIES=[],STATE='OH',priority=[],routes={},seniorTopics={},routeNames={},route='priority';\nconst regionalIDs=role=>DATA.filter(x=>x.regional_role===role).map(x=>x.program_id);\nconst officeLegacyIds=new Set(['morrow-vso','knox-vso','marion-vso','delaware-vso']);\n"+common[end:]
    begin=common.index('COUNTIES.forEach');end=common.index('function officeCard')
    common=common[:begin]+common[end:]
    for name in override_names:
        common=re.sub(r'^function '+name+r'\(.*$', 'function '+name+'(...args){return EDITIONS[STATE].'+name+'(...args)}',common,flags=re.M)
    # Only labels a state actually uses for statewide records count as statewide. A state
    # name alone is not enough: New York, Ohio and Utah are also county names.
    common=re.sub(r'^const national=.*$',"const national=a=>['statewide','national','federal',...EDITIONS[STATE].statewideNames].includes(a.toLowerCase());",common,flags=re.M)
    common=common.replace("'All Ohio counties'","'All '+EDITIONS[STATE].name+(STATE==='VA'?' counties and independent cities':' counties')")
    # Each state's address is its own page (ky.html); Ohio, the default edition, is the site root.
    # Share links and the address bar keep public filters only.
    assert common.count("u.search='';u.hash='';")==1,'shareURL'
    common=common.replace("u.search='';u.hash='';","u.pathname=u.pathname.replace(/[^/]*$/, STATE_PAGES[STATE]);u.search='';u.hash='';")
    common=common.replace("renderCounty();renderAccessibility();renderSeniorGuide();","renderCounty();renderAccessibility();renderSeniorGuide();renderHelper();")
    # Existing state-only details remain inside the adapter, not duplicated public pages.
    common=common[:common.index('const params=new URLSearchParams')]
    helpers=(root/'assets/guide-runtime.js').read_text()
    unified=base[:base.index('<script>')]
    unified=re.sub(r'<meta name="description"[^>]*>', lambda _: '<meta name="description" content="Help for every veteran in '+state_list(states)+': claims, VA health care, jobs, school, housing, records and long-term care. County veterans office contacts.">', unified)
    unified=re.sub(r'<title>.*?</title>','<title>Veteran Resource Guide: help for every veteran | Veteran Home Guardians</title>',unified)
    assert 'Ohio Veteran<br>Resource Guide' in unified,'guide heading'
    # The heading, the line above it and the opening paragraph are each page's own (data/landing/states.json).
    for old_text,new_text in [('<small>Veteran Home Guardians · All 88 Ohio counties</small>','<small id="guide-eyebrow"><!--eyebrow--></small>'),
                              ('<h1>Ohio Veteran<br>Resource Guide</h1>','<h1 id="guide-title"><!--h1--></h1>'),
                              ('<p>Useful contacts for veterans, surviving spouses, families and care-facility staff. Start with a county, then choose the help you need.</p>','<p id="guide-intro"><!--intro--></p>')]:
        assert unified.count(old_text)==1,old_text
        unified=unified.replace(old_text,new_text)
    unified=re.sub(r'<div class="coverage notice">.*?</div>', '', unified, flags=re.S)
    unified=unified.replace('Browse contacts for all 88 county veterans offices','Browse county contacts')
    unified=unified.replace('Most phones come from Ohio AMVETS’ 2025–2026 directory. Source links and review dates are shown. Call to confirm hours and the current intake process.','Source links and review dates are shown. Confirm hours and intake with the agency.')
    # The footer date is filled in from each state's own records (assets/guide-runtime.js), so it cannot go stale.
    updated='<p>Statewide edition · Updated October 8, 2026 · Source dates appear on each listing.</p>'
    assert unified.count(updated)==1,'footer date line'
    unified=unified.replace(updated,'<p><span id="edition-updated"></span> Each listing shows its own review date.</p>')
    unified=unified.replace('<div class="quick-links" aria-label="Common needs">','<div class="quick-links" aria-label="Common needs"><button data-route="aid" id="aid-open" hidden><strong>Veteran and aid organizations</strong><span>Local housing, legal aid, utilities and transport</span></button>')
    unified=unified.replace('assets/share-preview.png','assets/vhg-logo.png')
    for key,value in {'og:title':'Help for every veteran, in every state | VHG','twitter:title':'Help for every veteran, in every state | VHG','og:description':'Find your next contact for claims, health care, jobs, school, housing and long-term care in '+count_words(len(states))+' states. Free to use.','twitter:description':'Find your next contact for claims, health care, jobs, school, housing and long-term care in '+count_words(len(states))+' states. Free to use.','og:image:width':'715','og:image:height':'715','og:image:alt':'Veteran Home Guardians logo'}.items():
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
    unified=unified.replace('<p>Choose a need to see practical starting points. Your county selection stays in place.</p>','')
    unified=unified.replace('<p id="county-intro">County veterans offices can help you explore benefits and the right referral route. If the resident recently moved into a facility, ask which county should handle the referral.</p>','<p id="county-intro">Choose a county to find local contacts.</p>')
    unified=unified.replace('</head>','<link rel="stylesheet" href="assets/unified.css"></head>')
    unified=re.sub(r'<section id="urgent-help".*?</section>', '<section id="urgent-help" class="notice" aria-labelledby="urgent-title"><h2 id="urgent-title">Need help now?</h2><p>Crisis: <a href="tel:988">988</a> (veterans: press 1). Immediate danger: <a href="tel:911">911</a>.<br>Veteran housing help: <a href="tel:8774243838">877-424-3838</a> · 24/7.</p><p><a href="?view=crisis">Mental health support</a> · <a href="?view=housing">Housing resources</a></p><p id="world-link">Outside the United States? <a href="world/">Emergency and crisis numbers in other countries</a>, and VA help for U.S. veterans abroad.</p></section>', unified, flags=re.S)
    unified=unified.replace('<a class="jump" href="#support-vhg">Support VHG</a>', '<a class="jump" data-advocacy-route href="disability-advocacy.html">Disability rights &amp; advocacy</a><a class="jump" data-family-route href="family-guide.html">Families: autism, ADHD &amp; disabilities</a><a class="jump" href="flyers.html">Printable flyers</a><a class="jump" href="packets.html">Printable packets</a><a class="jump" href="world/">Veterans outside the U.S.</a><a class="jump" href="justice.html">Veterans in the justice system</a><a class="jump" href="https://mobilitytalk.org/states/" rel="noopener">Mobility &amp; disability resources in every state</a><a class="jump" href="#support-vhg">Support VHG</a>',1)
    # On a phone the header keeps its first four links and folds the rest behind "More guides",
    # so the state picker and the crisis numbers fit on the first screen. Wider screens show every link.
    first='<a class="jump" href="assistant/">Guided assistance (beta)</a>'
    last='<a class="jump" href="#support-vhg">Support VHG</a>'
    assert unified.count(first)==1 and unified.count(last)==1,'header links to fold'
    unified=unified.replace(first,'<button type="button" class="jump jump-toggle" id="jump-toggle" aria-expanded="false" aria-controls="jump-more" hidden>More guides</button><span class="jump-more" id="jump-more">'+first).replace(last,last+'</span>')
    # One small shared bundle plus one file per state; the base state is preloaded.
    def versioned(path, text):
        return path+'?v='+hashlib.sha256(text.encode()).hexdigest()[:10]
    result={}
    files={}
    for state,config in configs:
        path='assets/editions/'+state.lower()+'.js'
        text='(window.VHG_EDITIONS=window.VHG_EDITIONS||{})['+json.dumps(state)+']='+config+';\n'
        result[path]=text
        files[state]=versioned(path,text)
    guide=common+'\nconst EDITIONS=window.VHG_EDITIONS=window.VHG_EDITIONS||{};\nconst EDITION_FILES='+json.dumps(files)+';\nconst STATE_PAGES='+json.dumps({s:('' if p=='index.html' else p) for s,p in pages.items()})+';\n'+helpers
    result['assets/guide.js']=guide
    base=states[0]['code']
    unified=unified.replace('</select></nav>','</select><p id="edition-status" class="small" role="status" aria-live="polite"></p></nav>',1)
    # A visitor's first screen: crisis numbers, then where they need help (map, list, other countries),
    # then their county. Everything about sources and coverage comes after.
    urgent=section(unified,'urgent-help')
    picker=re.search(r'<nav class="edition-picker".*?</nav>',unified,re.S).group()
    coverage='<details id="edition-coverage" class="edition-coverage"><summary>Coverage and source checks</summary><div id="coverage-detail"></div></details>'
    for part in (urgent,picker,coverage):
        assert unified.count(part)==1,'opening part'
        unified=unified.replace(part,'')
    assert unified.count('<main>')==1,'main'
    unified=unified.replace('<main>','<main>'+urgent+'<!--who-start--><!--place-map-->'+picker+coverage,1)
    world_count=len(json.loads((root/'data/world/countries.json').read_text())['countries'])
    def with_map(text,state,open_map):
        # Right after the crisis numbers: "I'm here as..." routes each visitor to the parts of the guide that fit them.
        land=landings[state]
        text=text.replace('<!--who-start-->',landing.chooser(state,root),1)
        for key,value in (('eyebrow','Veteran Home Guardians · '+escape(land['eyebrow'],quote=False)),('h1',land['h1']),('intro',escape(land['intro'],quote=False))):
            assert text.count('<!--'+key+'-->')==1,key
            text=text.replace('<!--'+key+'-->',value)
        return text.replace('<!--place-map-->',place_map(states,state,world_count,open_map),1)
    def scripts(state):
        return '\n<script src="'+files[state]+'"></script><script src="'+versioned('assets/guide.js',guide)+'"></script></body></html>\n'
    home=landings[base]
    result['index.html']=landing.set_head(with_map(unified,base,True),home['title'],home['description'],BASE_URL,home['og_title'])+scripts(base)
    # Every other state gets the same page at its own address, so search engines can list it on its own:
    # its own title, description and canonical, with that state's records preloaded. Saved ?state= links
    # on the root keep working; the guide moves them to the state's page (assets/guide-runtime.js).
    for state,page in pages.items():
        if page=='index.html':continue
        url=BASE_URL+page;land=landings[state]
        assert unified.count('<html lang="en">')==1,'html tag'
        text=unified.replace('<html lang="en">','<html lang="en" data-home-state="'+state+'">',1)
        # Its own title, description and canonical, and Open Graph tags so a shared link previews as this state.
        text=landing.set_head(with_map(text,state,False),land['title'],land['description'],url,land['og_title'])
        result[page]=text+scripts(state)
    return result
