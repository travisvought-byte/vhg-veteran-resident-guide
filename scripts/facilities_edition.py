"""Build the self-contained Ohio nursing homes and rehab facilities page from reviewed public records."""
import json, re
from bingo_edition import TEMPLATE as _BINGO

STYLE = re.search(r'<style>(.*?)</style>', _BINGO, re.S).group(1)

def make_facilities(root):
    records = json.loads((root / 'data/public/ohio-facilities.json').read_text())
    counties = json.loads((root / 'data/public/ohio-county-veterans-offices.json').read_text())
    source = json.loads((root / 'data/source/ohio-facilities-source.json').read_text())
    known = {c['county'] for c in counties}
    ids = set()
    for r in records:
        assert r['county'] in known, r['id']
        assert r['id'] not in ids, r['id']
        ids.add(r['id'])
        assert re.fullmatch(r'\d{5}', r['zip']) and r['name'] and r['address'], r['id']
    kinds = {k: sum(r['facility_type'] == k for r in records) for k in ('nursing_home', 'residential_care')}
    assert kinds['nursing_home'] == source['nursing_homes']['ohio_rows'] and kinds['residential_care'] == source['residential_care']['rows']
    assert len(records) == sum(kinds.values())
    by_id = {r['id']: r for r in records}
    for r in records:
        assert r['facility_type'] in kinds, r['id']
        assert not r.get('campus_nursing_home') or by_id[r['campus_nursing_home']]['facility_type'] == 'nursing_home', r['id']
        assert not any('mail' in k or 'fax' in k for k in r), r['id']
    all_zips = json.loads((root / 'data/public/us-zip-centroids.json').read_text())
    used = {r['zip'] for r in records}
    zips = {z: c for z, c in all_zips.items() if z in used or z.startswith(('43', '44', '45'))}
    options = ''.join('<option>' + c['county'] + '</option>' for c in counties)
    payload = json.dumps(records, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    page = (TEMPLATE.replace('__STYLE__', STYLE).replace('__DATA__', payload).replace('__COUNTIES__', options)
            .replace('__ZIPDATA__', json.dumps(zips, separators=(',', ':')))
            .replace('__RETRIEVED__', source['nursing_homes']['retrieved_on'])
            .replace('__CMS_URL__', source['nursing_homes']['source_url']).replace('__ODH_URL__', source['residential_care']['source_url'])
            .replace('__NH_COUNT__', str(kinds['nursing_home'])).replace('__AL_COUNT__', str(kinds['residential_care'])))
    return page

TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ohio Nursing Homes, Rehab and Assisted Living | Veteran Home Guardians</title>
<meta name="description" content="Find Ohio nursing homes, rehabilitation facilities and assisted living or residential care communities by name, county or ZIP code, with phone numbers and nearby bingo games and activities.">
<link rel="canonical" href="https://travisvought-byte.github.io/vhg-veteran-resident-guide/facilities.html">
<style>__STYLE__
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.vhg{background:#e0ecdf;border:1px solid #9bbd9a}.state-home{background:#e7e9f3;border:1px solid #aab1d6}.facts{font-size:15px;margin:6px 0}
</style></head><body><a class="skip" href="#listings">Skip to listings</a>
<header class="page-only"><a href="index.html?view=seniors">&larr; Ohio Veteran Resident Resource Guide</a><p><img src="assets/vhg-logo.png" alt="Veteran Home Guardians" width="64" height="64"></p><h1>Ohio Nursing Homes, Rehab &amp; Assisted Living</h1><p>Find a nursing home, rehabilitation facility or assisted living community by name, county or ZIP code, then see the bingo games, senior centers and activities near it.</p></header>
<main class="page-only"><p class="notice"><strong>What this list is.</strong> It has all __NH_COUNT__ Medicare- and Medicaid-certified nursing homes in Ohio (federal Provider Data Catalog) and __AL_COUNT__ active, state-licensed residential care or assisted living facilities (Ohio Department of Health), both retrieved __RETRIEVED__. It does not identify memory care units and does not include adult day services. It does not rate or recommend any facility. Confirm services, admission and visiting rules by phone, and check the state&rsquo;s <a href="https://aging.ohio.gov/navigator" target="_blank" rel="noopener noreferrer">Nursing Home Quality Navigator</a> for nursing home quality information.</p>
<form id="fac-nearby"><div class="tools"><div><label for="fac-zip">Your ZIP code</label><input id="fac-zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" pattern="[0-9]{5}" placeholder="e.g. 43334"></div><div><label for="fac-radius">Within</label><select id="fac-radius"><option value="10">10 miles</option><option value="25" selected>25 miles</option><option value="50">50 miles</option><option value="all">Any distance</option></select></div><div class="nearby-action"><button type="submit">Find nearby facilities</button></div></div></form><p id="fac-status" class="small" role="status" aria-live="polite">Distances are approximate straight-line miles.</p>
<div class="tools"><div><label for="fac-type">Type of facility</label><select id="fac-type"><option value="">Nursing homes and assisted living</option><option value="nursing_home">Nursing homes and rehab</option><option value="residential_care">Assisted living and residential care</option></select></div><div><label for="fac-search">Search by name, town or company</label><input id="fac-search" type="search" placeholder="e.g. Marion, Trilogy, Pointe"></div></div><div class="tools"><div><label for="fac-county">County</label><select id="fac-county"><option value="">All Ohio counties</option>__COUNTIES__</select></div><div><label for="fac-own">Ownership (nursing homes)</label><select id="fac-own"><option value="">Any</option><option>Non profit</option><option>For profit</option><option>Government</option></select></div></div>
<div class="actions"><button id="fac-reset" type="button">Clear filters</button><button id="fac-print" type="button">Print this list</button></div>
<p id="fac-count" role="status" aria-live="polite"></p><section id="listings" aria-label="Nursing homes, rehab and assisted living facilities"></section>
<section class="submission"><h2>Correct or add a facility</h2><p>Spot a wrong phone number, a closed facility or a missing one? Every card has an &ldquo;Update this listing&rdquo; link that opens a prefilled email. Please share public facility information only, never resident or health details.</p><p>Activity or social services staff: <a href="bingo.html?organizer=1">tell us which games your residents attend</a>.</p></section>
<footer><p>Sources: <a href="__CMS_URL__" target="_blank" rel="noopener noreferrer">CMS Provider Data Catalog, Nursing Home Provider Information</a> and the <a href="__ODH_URL__" target="_blank" rel="noopener noreferrer">Ohio Department of Health Facility Listing</a>, retrieved __RETRIEVED__; public directory fields only. Contact: <a href="mailto:travis@vethomeguard.org?subject=Ohio%20nursing%20home%20listing">travis@vethomeguard.org</a>.</p><p><a href="data/public/ohio-facilities.json">Download facility data</a> &middot; <a href="bingo.html">Ohio Bingo &amp; Senior Centers</a> &middot; <a href="index.html">Return to benefits and support referrals</a></p></footer></main>
<script>
const FAC=__DATA__;
const ZIPS=__ZIPDATA__;
let activeZip='';
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
function miles(a,b){const r=x=>x*Math.PI/180,la=r(b[0]-a[0]),lo=r(b[1]-a[1]),h=Math.sin(la/2)**2+Math.cos(r(a[0]))*Math.cos(r(b[0]))*Math.sin(lo/2)**2;return 3958.7613*2*Math.atan2(Math.sqrt(h),Math.sqrt(Math.max(0,1-h)))}
function nearbyFacilities(rows,zip,radius){const o=ZIPS[zip];if(!o)return null;return rows.flatMap(f=>{const c=ZIPS[f.zip];if(!c)return[];const d=miles(o,c);return d<=radius?[{...f,distanceMiles:d}]:[]}).sort((a,b)=>a.distanceMiles-b.distanceMiles||a.name.localeCompare(b.name))}
function filteredFacilities(county,own,q,type=''){q=q.toLowerCase().trim();return FAC.filter(f=>(!county||f.county===county)&&(!own||f.ownership===own)&&(!type||f.facility_type===type)&&(!q||[f.name,f.city,f.chain,f.county,f.zip].join(' ').toLowerCase().includes(q)))}
function gamesLink(f){return 'bingo.html?zip='+f.zip+'&radius=25&kind=bingo'}
function updateEmail(f){const u=new URL('mailto:travis@vethomeguard.org');u.searchParams.set('subject','Facility listing: '+f.name);u.searchParams.set('body',['Facility: '+f.name,'Address: '+f.address,(f.ccn?'CMS number: '+f.ccn:'Ohio license: '+f.license_id),'','What should be corrected or added (public facility information only):',''].join('\n'));return u.href.replaceAll('+','%20')}
function card(f){const chips=(f.vhg_visiting?'<span class="badge vhg">Veteran Home Guardians visits here</span> ':'')+(f.ohio_veterans_home?'<span class="badge state-home">Ohio Veterans Home</span> ':'')+'<span class="badge">'+(f.facility_type==='residential_care'?'Assisted living / residential care':'Nursing home')+'</span>'+(f.ownership?' <span class="badge">'+esc(f.ownership)+'</span>':'')+(f.chain?' <span class="badge">'+esc(f.chain)+'</span>':'')+(f.campus_nursing_home?' <span class="badge">Same campus as a nursing home</span>':'');
return '<article id="'+esc(f.id)+'"><div class="chips">'+chips+'</div><h2>'+esc(f.name)+'</h2>'+(Number.isFinite(f.distanceMiles)?'<p class="badge">About '+f.distanceMiles.toFixed(1)+' miles away</p>':'')+'<p>'+esc(f.address)+'<br><strong>'+esc(f.county)+' County</strong></p><p class="facts">'+f.beds+(f.facility_type==='residential_care'?' licensed beds':' certified beds')+'</p><div class="actions">'+(f.phone?'<a href="tel:'+f.phone.replace(/\D/g,'')+'">'+esc(f.phone)+'</a>':'')+'<a href="https://www.google.com/maps/search/?api=1&amp;query='+encodeURIComponent(f.address)+'" target="_blank" rel="noopener noreferrer">Directions &#8599;</a><a href="'+esc(gamesLink(f))+'">Games and activities near here</a><a class="report" href="'+esc(updateEmail(f))+'">Update this listing</a></div></article>'}
function render(){const county=$('fac-county').value,own=$('fac-own').value,q=$('fac-search').value,type=$('fac-type').value,base=filteredFacilities(county,own,q,type),radius=$('fac-radius').value==='all'?Infinity:Number($('fac-radius').value);
const rows=activeZip?nearbyFacilities(base,activeZip,radius):[...base].sort((a,b)=>(b.vhg_visiting-a.vhg_visiting)||a.name.localeCompare(b.name));
$('fac-count').textContent=rows.length+(activeZip?' facilities'+($('fac-radius').value==='all'?'':' within '+$('fac-radius').value+' miles')+' of '+activeZip+' · closest first':' of '+FAC.length+' facilities')+(county?' in '+county+' County':'');
$('listings').innerHTML=rows.length?'<div class="grid">'+rows.map(card).join('')+'</div>':'<p class="empty">No facilities match these filters. Try a larger distance or clear filters.</p>';
const u=new URL(location.href);u.search='';if(county)u.searchParams.set('county',county);if(own)u.searchParams.set('own',own);if(type)u.searchParams.set('type',type);if(q)u.searchParams.set('q',q);if(activeZip){u.searchParams.set('zip',activeZip);u.searchParams.set('radius',$('fac-radius').value)}history.replaceState(null,'',u)}
function applyNearby(){const zip=$('fac-zip').value.trim();if(!zip){activeZip='';$('fac-status').textContent='Distances are approximate straight-line miles.';render();return}if(!/^[0-9]{5}$/.test(zip)||!ZIPS[zip]){activeZip='';$('fac-status').textContent='Enter a valid five-digit Ohio ZIP code.';render();return}activeZip=zip;$('fac-status').textContent='Distances are approximate straight-line miles.';render()}
$('fac-nearby').onsubmit=e=>{e.preventDefault();applyNearby()};$('fac-radius').addEventListener('change',()=>{if(activeZip)render()});
const params=new URLSearchParams(location.search);if([...$('fac-county').options].some(o=>o.value===params.get('county')))$('fac-county').value=params.get('county');if(['Non profit','For profit','Government'].includes(params.get('own')))$('fac-own').value=params.get('own');if(['nursing_home','residential_care'].includes(params.get('type')))$('fac-type').value=params.get('type');$('fac-search').value=params.get('q')||'';$('fac-zip').value=params.get('zip')||'';$('fac-radius').value=['10','25','50','all'].includes(params.get('radius'))?params.get('radius'):'25';if(/^[0-9]{5}$/.test($('fac-zip').value)&&ZIPS[$('fac-zip').value])activeZip=$('fac-zip').value;
['fac-county','fac-own','fac-type'].forEach(id=>$(id).addEventListener('change',render));$('fac-search').addEventListener('input',render);
$('fac-reset').onclick=()=>{['fac-county','fac-own','fac-type','fac-search','fac-zip'].forEach(id=>$(id).value='');activeZip='';$('fac-radius').value='25';$('fac-status').textContent='Distances are approximate straight-line miles.';render()};$('fac-print').onclick=()=>window.print();render();
</script></body></html>'''
