// FindBingo.org (findbingo-site/): ZIP search across Michigan, Indiana and neighboring states.
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..'), site = path.join(root, 'findbingo-site');
// Google AdSense (owner direction, November 27, 2026) is only in findbingo.org's copy (bingo-site/findbingo/), never in
// findbingo-site/, which the guide's host serves. Comparing the two copies leaves out that one head snippet.
const AD_HEAD = '<meta name="google-adsense-account" content="ca-pub-9220804879239310"><script>(window.adsbygoogle=window.adsbygoogle||[]).requestNonPersonalizedAds=1;</script>'
  + '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9220804879239310" crossorigin="anonymous"></script>';
function unAd(text, want = true) {
  assert.equal(text.split(AD_HEAD).length - 1, want ? 1 : 0, want ? 'findbingo.org pages load the AdSense code once' : 'no AdSense code on this page');
  return text.replace(AD_HEAD, '');
}
const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(site, 'data.json'), 'utf8'));
const zips = JSON.parse(fs.readFileSync(path.join(site, 'zips.json'), 'utf8'));
const states = JSON.parse(fs.readFileSync(path.join(root, 'data/public/bingo-states.json'), 'utf8'));
for (const f of ['index.html', 'data.json', 'zips.json'])  // the Ohio-Bingo mirror carries the same files for Cloudflare Pages
  assert.equal(f.endsWith('.html') ? unAd(fs.readFileSync(path.join(root, 'bingo-site/findbingo', f), 'utf8')) : fs.readFileSync(path.join(root, 'bingo-site/findbingo', f), 'utf8'),
    fs.readFileSync(path.join(site, f), 'utf8'), 'bingo-site/findbingo/' + f);
assert(!html.includes('adsbygoogle') && !html.includes('google-adsense-account'), 'findbingo-site/ (served on the guide) never carries AdSense');
// The Ohio finder is the folder ohio/ on the same site; other spellings forward to it.
assert(fs.existsSync(path.join(root, 'bingo-site/findbingo/ohio/index.html')), 'Ohio finder is served at findbingo.org/ohio/');
const redirects = fs.readFileSync(path.join(root, 'bingo-site/findbingo/_redirects'), 'utf8').trim().split('\n').map(l => l.split(' '));
assert(redirects.some(r => r[0] === '/oh') && !redirects.some(r => r[0] === '/ohio' || r[0] === '/ohio/'), 'spellings forward; /ohio itself is the finder');
// Short addresses for posters: /mi and /MI open the Michigan page. No rule may match its own target.
// Every state and DC has an entry, in alphabetical order by name; the address is the name in lower case with hyphens.
const SLUGS = Object.fromEntries(states.map(s => [s.code, s.name.toLowerCase().replaceAll(' ', '-')]));
assert.equal(states.length, 51);
assert.deepEqual(states.map(s => s.name), states.map(s => s.name).sort(), 'states are in alphabetical order');
assert(SLUGS.DC === 'district-of-columbia' && SLUGS.WV === 'west-virginia');
// Pages that moved forward to their new address: the bingo class went from /learn/ to /how-to-play-bingo/ (November 27, 2026).
const MOVED = {'/learn': '/how-to-play-bingo/', '/learn/': '/how-to-play-bingo/'};
for (const r of redirects) assert(r.length === 3 && r[0].startsWith('/') && (Object.values(SLUGS).some(s => r[1] === '/' + s + '/') || MOVED[r[0]] === r[1]) && r[2] === '301' && r[0].toLowerCase() !== r[1], r.join(' '));
for (const [from, to] of Object.entries(MOVED)) assert(redirects.some(r => r[0] === from && r[1] === to), from + ' forwards to ' + to);
assert(redirects.some(r => r[0] === '/mi' && r[1] === '/michigan/') && redirects.some(r => r[0] === '/FL' && r[1] === '/florida/'));
assert.equal(data.generated_on, [...states.map(s => s.reviewed_on), ...data.venues.map(v => v.reviewed_on), ...data.licensed.map(r => r.reviewed_on)].sort().pop());
assert(data.venues.length > 150 && data.licensed.length > 300, 'Michigan venues and Indiana licenses are loaded');
for (const r of [...data.venues, ...data.licensed]) assert(zips[r.zip], 'every listing can be placed by ZIP: ' + r.id);
for (const v of data.venues) {
  const order = v.sessions.map(s => (s.day + 6) % 7);
  assert.deepEqual(order, [...order].sort((a, b) => a - b), 'sessions run Monday to Sunday: ' + v.id);
}
assert(zips['49037'], 'Census point fills the ZIP missing from the centroid file');
assert(zips['90210'] && zips['99501'] && zips['96813'] && zips['20001'] && !zips['00601'] && !zips['09001'] && zips['10001'] && zips['84770'] && zips['43334'] && zips['48161'] && zips['46733'] && zips['40601'] && zips['25301'] && zips['15222'] && zips['33701'] && zips['32208']);
assert(!Object.keys(zips).some(z => z.startsWith('340')), 'military ZIP codes are not Florida');
assert(data.zip3['902'] === 'CA' && data.zip3['995'] === 'AK' && data.zip3['200'] === 'DC' && !data.zip3['006'] && data.zip_exceptions['06390'] === 'NY', 'ZIP codes map to states from the source file');
for (const z of Object.keys(zips)) assert(data.zip_exceptions[z] || data.zip3[z.slice(0, 3)], 'every published ZIP has a state: ' + z);

const static_ = new JSDOM(html).window.document;
assert.equal(static_.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/');
// States with a list or state research are the main buttons; the rest sit behind one "more states" control.
// States with a list on the site are one tap away; every other state sits behind one "more states" control.
const LISTED = ['times', 'licenses', 'starter', 'ohio_finder'];
const listed = states.filter(s => LISTED.includes(s.coverage)), rest = states.filter(s => !LISTED.includes(s.coverage));
const ready = states.filter(s => s.coverage !== 'pending').map(s => s.code), waiting = states.filter(s => s.coverage === 'pending').map(s => s.code);
assert.deepEqual([...static_.querySelectorAll('#state-buttons > a')].map(a => a.dataset.state), listed.map(s => s.code));
assert.deepEqual([...static_.querySelectorAll('#state-buttons details.more-states a')].map(a => a.dataset.state), rest.map(s => s.code));
for (const c of ['FL', 'IN', 'MI', 'MO', 'MS', 'MT', 'NM', 'NY', 'OH', 'PA', 'TX', 'UT', 'VA']) assert(listed.some(s => s.code === c), c + ' keeps its list');
for (const c of ['KY', 'WV']) assert(ready.includes(c), c + ' stays researched');
assert.deepEqual(waiting, [], 'every state and DC has been researched: each names who licenses or oversees bingo, with a source');
assert.equal(states.length, 51);
assert.equal(static_.querySelectorAll('script[src]').length, 0, 'no outside scripts');
assert.deepEqual([...static_.querySelectorAll('#about-states h3')].map(h => h.textContent), listed.map(s => s.name).concat('Every other state'), 'sources are given on the home page for states with a list; the rest are named together and sourced on their own pages');
assert.deepEqual([...static_.querySelectorAll('#about-states h3:last-of-type ~ p a')].map(a => a.getAttribute('href')), rest.map(s => SLUGS[s.code] + '/'), 'every other state is linked from the home page');
assert(static_.querySelector('footer a[href="https://creativecommons.org/licenses/by/3.0/"]'), 'ZIP data attribution');
assert(!/\b\d+ (halls|venues|locations|counties)\b/i.test(static_.querySelector('header').textContent), 'no headline counts');
// The map (November 21, 2026): hidden until the list has pins, group dots without numbers, map files from this site, privacy linked.
const mapBox = static_.getElementById('map-box');
assert(mapBox && mapBox.hidden && mapBox.dataset.pmList === 'results' && mapBox.dataset.pmBase === 'assets/map/' && mapBox.dataset.pmNumbers === undefined, 'home map box (group dots show how many places they hold)');
assert(!/\d/.test(mapBox.textContent), 'no numbers in the map box');
assert(mapBox.querySelector('a[href="privacy/"]') && /OpenStreetMap/.test(mapBox.textContent), 'the map names its picture source and links Privacy');
assert(static_.querySelector('#zip-form [data-pm-locate][hidden]'), 'Use my location stays hidden without JavaScript');
{
  const mapScript = [...static_.querySelectorAll('script')].find(s => s.textContent.includes('Place map:')).textContent;
  assert.deepEqual([...new Set(mapScript.match(/https:\/\/[a-z.]+/g))].sort(), ['https://tile.openstreetmap.org', 'https://www.openstreetmap.org'], 'the map loads its code from this site; only the map pictures come from OpenStreetMap');
}
for (const dir of ['findbingo-site', 'bingo-site/findbingo'])
  for (const f of ['leaflet.js', 'leaflet.css', 'leaflet.markercluster.js', 'markercluster.css'])
    assert.equal(fs.readFileSync(path.join(root, dir, 'assets/map', f), 'utf8'), fs.readFileSync(path.join(root, 'assets/map', f), 'utf8'), dir + ' serves ' + f);
// State pages pin each card at the middle of its ZIP code, from zips.json: never a made-up point.
{
  const mi = new JSDOM(fs.readFileSync(path.join(site, 'michigan/index.html'), 'utf8')).window.document;
  const box = mi.getElementById('map-box');
  assert(box && box.hidden && box.dataset.pmList === 'listings' && box.dataset.pmBase === '../assets/map/' && box.querySelector('a[href="../privacy/"]'), 'Michigan map box');
  const pinned = [...mi.querySelectorAll('#listings article[data-pm-lat]')];
  assert(pinned.length, 'Michigan cards have pins');
  for (const a of pinned) {
    const v = data.venues.find(x => x.id === a.id);
    assert.deepEqual([Number(a.dataset.pmLat), Number(a.dataset.pmLon)], zips[v.zip], a.id + ' is pinned at its ZIP code');
  }
  assert.equal(pinned.length, mi.querySelectorAll('#listings article').length - [...mi.querySelectorAll('#listings article')].filter(a => !zips[(data.venues.find(x => x.id === a.id) || {}).zip]).length, 'every card with a known ZIP code is pinned');
}

// Run the page on Monday, November 16, 2026 at 10 a.m. Data requests are answered from this folder.
const sources = JSON.parse(html.match(/const DATA_SOURCES=(\[.*?\]);/)[1]);
assert.deepEqual(sources, ['', 'https://guide.vethomeguard.org/findbingo-site/', 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/main/findbingo-site/']);
// Pages checked in a loop are parsed into scratch windows, closed before the next page, so the run stays within memory.
const scratchWindows = [];
function scratch(text) { const w = new JSDOM(text).window; scratchWindows.push(w); return w.document; }
function freeScratch() { for (const w of scratchWindows.splice(0)) w.close(); }
// Each open() loads the whole finder with its lists; close the previous one so a long run stays within memory.
let lastDom = null;
async function open(query, {served = ['https://www.findbingo.org/'], requests = [], served_data = data} = {}) {
  if (lastDom) lastDom.window.close();
  const dom = lastDom = new JSDOM(html, {url: 'https://www.findbingo.org/' + query, runScripts: 'dangerously', beforeParse(w) {
    const RealDate = w.Date;
    w.Date = class extends RealDate { constructor(...a) { super(...(a.length ? a : [2026, 10, 16, 10, 0])) } static now() { return new RealDate(2026, 10, 16, 10, 0).getTime() } };
    w.HTMLElement.prototype.scrollIntoView = () => {};
    w.print = () => {};
    w.fetch = url => {
      const abs = new URL(url, 'https://www.findbingo.org/').href;
      requests.push(abs);
      const base = served.find(b => abs === b + 'data.json' || abs === b + 'zips.json');
      if (!base) return Promise.resolve({ok: false, status: 404, json: () => Promise.reject(new Error('404'))});
      return Promise.resolve({ok: true, status: 200, json: () => Promise.resolve(JSON.parse(JSON.stringify(abs.endsWith('data.json') ? served_data : zips)))});
    };
  }});
  assert.equal(dom.window.document.getElementById('count').textContent, 'Loading the bingo list…');
  const ok = await dom.window.fbReady;
  const d = dom.window.document;
  return {ok, w: dom.window, d, count: d.getElementById('count').textContent, groups: [...d.querySelectorAll('#results h2')].map(h => h.textContent),
    cards: [...d.querySelectorAll('#results article')].map(a => a.id), status: d.getElementById('zip-status').textContent};
}
(async () => {
// Copies outside the guide (the Wix site) read the lists from GitHub Pages; a failed load says so plainly.
const requests = [];
let p = await open('?zip=48066', {served: ['https://guide.vethomeguard.org/findbingo-site/'], requests});
assert(p.ok && p.cards.length, 'loads from GitHub Pages when the page is hosted elsewhere');
assert.deepEqual(requests.slice(0, 2), ['https://www.findbingo.org/data.json', 'https://www.findbingo.org/zips.json']);
for (const a of p.d.querySelectorAll('#results article[id]:not(.state-card)')) {
  const r = data.venues.concat(data.licensed).find(x => x.id === a.id);
  assert.equal(a.dataset.pmZip, zips[r.zip] ? r.zip : undefined, a.id + ' carries its ZIP code for the map');
  assert(!a.dataset.pmSub || !/\b\d+ (halls|games|places|locations|counties)\b/i.test(a.dataset.pmSub), 'no counts in the pin box');
}
p = await open('?zip=48066', {served: []});
assert.equal(p.ok, false);
assert.equal(p.count, 'Sorry, the bingo list did not load.');
assert.match(p.d.getElementById('results').textContent, /check your internet connection/);
// A page newer than the published lists hides the states the lists do not have yet.
p = await open('', {served_data: {...data, states: data.states.filter(s => s.code !== 'FL')}});
assert.equal(p.d.querySelector('#state-buttons a[data-state="FL"]').hidden, true);
assert.equal(p.d.querySelector('#state-buttons a[data-state="MI"]').hidden, false);
p = await open('?state=FL', {served_data: {...data, states: data.states.filter(s => s.code !== 'FL')}});
assert.equal(p.count, 'Type your ZIP code above, or pick a state.');
const w0 = (await open('')).w;
assert.equal(w0.timeRange('16:00', '23:00'), '4 to 11 p.m.');
assert.equal(w0.timeRange('09:00', '15:00'), '9 a.m. to 3 p.m.');
assert.equal(w0.timeRange('12:00', '16:00'), 'noon to 4 p.m.');
assert.equal(w0.timeRange('16:00', '00:00'), '4 p.m. to midnight');
assert.equal(w0.timeRange('21:31', '02:00'), '9:31 p.m. to 2 a.m.');
assert.equal(w0.timeRange('10:30', '14:30'), '10:30 a.m. to 2:30 p.m.');
assert.equal(w0.stateOfZip('48161') + w0.stateOfZip('46733') + w0.stateOfZip('43334') + w0.stateOfZip('40601') + w0.stateOfZip('25301') + w0.stateOfZip('15222') + w0.stateOfZip('33701') + w0.stateOfZip('34001') + w0.stateOfZip('10001') + w0.stateOfZip('84770') + w0.stateOfZip('90210') + w0.stateOfZip('06390') + w0.stateOfZip('00601'), 'MIINOHKYWVPAFLNYUTCANY');
const fake = {sessions: [{day: 1, start: '09:00', end: '11:00'}, {day: 3, start: '16:00', end: '00:00'}]};
assert.equal(w0.nextGame(fake, '', '2026-11-16', 600), '2026-11-16', 'still on this morning');
assert.equal(w0.nextGame(fake, '', '2026-11-16', 700), '2026-11-18', 'this morning is over, so Wednesday');
assert.equal(w0.nextGame(fake, 'today', '2026-11-16', 700), null);
assert.equal(w0.nextGame(fake, 'tomorrow', '2026-11-17', 700), '2026-11-18');
assert.equal(w0.nextGame(fake, 'tomorrow', '2026-11-16', 700), null);
assert.equal(w0.nextGame(fake, '3', '2026-11-16', 700), '2026-11-18');
assert.equal(w0.nextGame({sessions: [{day: 1, start: '09:00', end: '11:00'}]}, '', '2026-11-16', 700), '2026-11-23', 'a weekly game that ended today comes back next week');
assert.equal(w0.nextGame({sessions: [{day: 1, start: '21:31', end: '02:00'}]}, '', '2026-11-16', 1430), '2026-11-16', 'overnight game still running');
assert.equal(w0.licenseCurrent({license_expires: '2026-11-15'}, '2026-11-16'), false, 'expired licenses drop off');
assert.equal(w0.timeRange('10:00'), '10 a.m.');
assert.equal(w0.timeRange(null), 'time not posted');
assert.equal(w0.nextGame({sessions: [{day: 1, start: '10:00'}]}, '', '2026-11-16', 770), '2026-11-16', 'a start-only game counts as on for three hours');
assert.equal(w0.nextGame({sessions: [{day: 1, start: '10:00'}]}, '', '2026-11-16', 790), '2026-11-23');
assert.equal(w0.nextGame({sessions: [{day: 1, start: null}]}, '', '2026-11-16', 1000), '2026-11-16', 'no posted time: on until 5 p.m.');
assert.equal(w0.nextGame({sessions: [{day: 1, start: null}]}, '', '2026-11-16', 1030), '2026-11-23');
assert.equal(w0.document.getElementById('narrow').hidden, true, 'filters wait for a search');
assert.equal(w0.document.getElementById('count').textContent, 'Type your ZIP code above, or pick a state.');

// Michigan ZIP: nearby halls with game days, closest first.
p = await open('?zip=48066&radius=10');
assert.equal(p.count, 'Bingo within 10 miles of 48066 · closest first');
assert.equal(p.cards[0], 'mi-rosemack-bingo-roseville');
assert.equal(p.groups[0], 'Bingo with game days', 'no counts on the site');
const rosemack = p.d.getElementById('mi-rosemack-bingo-roseville');
assert.match(rosemack.querySelector('.when').textContent, /Next bingo day: Today/);
assert.match(rosemack.querySelector('.sessions').textContent, /Monday, 4:30 to 10 p\.m\. · Gesu School/);
assert.match(rosemack.querySelector('.note').textContent, /Michigan's weekly bingo license list/);
assert.equal(rosemack.querySelector('.big-actions a.outline').href, 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent('20789 E 13 Mile Road, Roseville, MI 48066'));
assert.equal(p.d.getElementById('narrow').hidden, false);
assert(!p.cards.some(id => id.startsWith('state-')), 'no Ohio or no-list cards this far from those states');

// Counties the state lookup has not returned yet are named, with the state's own lookup.
const pending = states.find(s => s.code === 'MI').pending_counties || [];
if (pending.length) {
  assert.match(p.d.getElementById('pending-MI').textContent, new RegExp(pending[pending.length - 1]));
  assert.equal(p.d.querySelector('#pending-MI a').href, states.find(s => s.code === 'MI').list_url);
  assert(!data.venues.some(v => v.state === 'MI' && pending.includes(v.county)));
}

// A day filter keeps only halls with a game that day.
p = await open('?zip=48066&radius=10&day=2');
assert(p.cards.length > 0 && p.cards.every(id => data.venues.find(v => v.id === id).sessions.some(s => s.day === 2)));

// Ohio ZIP: hand off to the Ohio Bingo Finder first, then nearby Michigan games.
p = await open('?zip=43604&radius=25');
assert.equal(p.groups[0], 'Ohio bingo');
assert.equal(p.d.querySelector('#state-OH a.solid').href, 'https://www.findbingo.org/ohio/?zip=43604&radius=25#count');
assert(p.cards.some(id => id.startsWith('mi-')), 'Toledo searches include Monroe County, Michigan');
p = await open('?zip=43334');
assert.equal(p.count, 'Bingo near 43334 is on the Ohio bingo finder');
assert.deepEqual(p.cards, ['state-OH']);

// Indiana ZIP with no posted game days: show the licensed groups right away.
p = await open('?zip=46733&radius=10');
assert.equal(p.count, 'Bingo within 10 miles of 46733 · closest first');
assert(p.groups[0].startsWith('Licensed groups, game days not posted'));
assert(p.cards.includes('in-000114'));
assert.match(p.d.getElementById('in-000114').textContent, /Indiana's license list shows this group can hold bingo, but not when/);
assert.match(p.d.getElementById('in-000114').textContent, /license 000114 \(Annual Activity\), on the state list through Oct 31, 2027/);

// Where Michigan halls and Indiana licenses mix, licensed groups wait behind a button.
p = await open('?zip=49120&radius=25');
const more = p.d.querySelector('#more-note button[data-more="1"]');
assert(p.cards.some(id => id.startsWith('mi-')) && more, 'Niles, Michigan: Michigan games plus nearby Indiana licenses');
assert(!p.cards.some(id => id.startsWith('in-')));
more.click();
assert(p.d.querySelector('#results article[id^="in-"]'), 'Show them too reveals the Indiana groups');
assert(p.d.querySelector('#more-note button[data-more="0"]'));
assert(!/\d/.test(p.d.getElementById('more-note').textContent), 'no counts on the site');

// States without a public list: say so, and invite halls to send game times.
p = await open('?zip=68102');
assert.equal(p.count, 'No bingo games listed yet within 25 miles of 68102.');
assert(!p.d.getElementById('pending-MI'), 'the Michigan note stays with Michigan searches');
assert.equal(p.cards[0], 'state-NE');
assert.match(p.d.getElementById('state-NE').textContent, /Charitable Gaming/);
assert(p.d.querySelector('#state-NE a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Nebraska"]'));
// Missouri: the Gaming Commission's Find Local Bingo Games page gives start times only, and which weeks of the month.
const moRows = data.venues.filter(v => v.state === 'MO');
assert.equal(states.find(s => s.code === 'MO').coverage, 'times');
assert(moRows.length && moRows.every(v => v.sessions.every(x => x.start && !('end' in x))), 'Missouri sessions have a start time and no end time');
assert(moRows.every(v => !!v.schedule_note === v.sessions.some(x => x.label)), 'only halls with monthly games say "usual bingo days"');
p = await open('?zip=65101');
assert.equal(p.count, 'Bingo within 25 miles of 65101 · closest first');
assert(p.cards.includes('mo-basinger-sone-memorial-vfw-post-1003-jefferson-city'));
assert.match(p.d.getElementById('mo-basinger-sone-memorial-vfw-post-1003-jefferson-city').querySelector('.when').textContent, /Next bingo day:.*Friday, 6:30 p\.m\./s);
p = await open('?zip=65265');
const legion = p.d.getElementById('mo-james-bledsoe-post-26-american-legion-mexico');
assert.match(legion.querySelector('.when').textContent, /Usual bingo days:.*Saturday, 6:30 p\.m\. · First and third Saturday of the month/s);
assert(!/Next bingo day/.test(legion.textContent), 'no promised date when some games skip weeks');
// Kentucky's starter list: Frankfort finds the VFW post's Thursday game, then the way to send more game times.
p = await open('?zip=40601');
assert.equal(p.count, 'Bingo within 25 miles of 40601 · closest first');
assert.equal(p.cards[0], 'ky-vfw-post-4075-frankfort');
assert.match(p.d.getElementById('ky-vfw-post-4075-frankfort').querySelector('.sessions').textContent, /Thursday, 6:30 p\.m\./);
assert(p.cards.includes('state-KY') && p.d.querySelector('#state-KY a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Kentucky"]'));
// Florida: no state list, so the Florida card leads with how to send game times.
p = await open('?zip=33701');
assert.equal(p.count, 'No bingo games listed yet within 25 miles of 33701.');
assert.equal(p.cards[0], 'state-FL');
assert.match(p.d.getElementById('state-FL').textContent, /does not license bingo statewide/);
assert.equal(p.d.querySelector('#state-FL a[target]').href, 'https://www.flsenate.gov/Laws/Statutes/2025/849.0931');
// Florida's starter list: Jacksonville senior centers from the city's dated monthly calendars.
const fl = data.venues.filter(v => v.state === 'FL');
assert(fl.length >= 5 && fl.every(v => v.kind && v.phone && v.source_url && v.schedule_note));
p = await open('?state=FL');
assert.equal(p.count, 'Florida bingo places with game days');
assert.deepEqual(p.cards, [...fl].sort((a, b) => a.county.localeCompare(b.county) || a.city.localeCompare(b.city) || a.name.localeCompare(b.name)).map(v => v.id).concat('state-FL'));
p = await open('?zip=32208&radius=10');
assert.equal(p.count, 'Bingo within 10 miles of 32208 · closest first');
assert(p.cards.includes('fl-carvill-senior-center-jacksonville') && p.cards.indexOf('state-FL') > p.cards.indexOf('fl-carvill-senior-center-jacksonville'), 'Florida results first, then the help card');
const carvill = p.d.getElementById('fl-carvill-senior-center-jacksonville');
assert.match(carvill.querySelector('.badge').textContent, /Senior center bingo/);
assert.equal(carvill.querySelector('.big-actions a.solid').getAttribute('href'), 'tel:9042556650');
assert.match(carvill.querySelector('.big-actions a.solid').textContent, /Call 904-255-6650/);
assert.match(carvill.querySelector('.sessions').textContent, /Tuesday, 10 a\.m\./);
assert.match(carvill.querySelector('.note').textContent, /November 2026 calendar/);
assert(/Usual bingo days/.test(carvill.querySelector('.when').textContent) && !/Next bingo day/.test(carvill.querySelector('.when').textContent), 'monthly calendars give usual days, not a promised date');
assert.equal(carvill.querySelector('details a').href, 'https://www.jacksonville.gov/departments/parks-and-recreation/senior-services/senior-center-calendars');
assert.match(p.d.getElementById('fl-charlie-t-joseph-senior-center-jacksonville').querySelector('.sessions').textContent, /Monday, time not posted/);
p = await open('?zip=32246&radius=10');
assert.match(p.d.getElementById('fl-southside-senior-center-jacksonville').querySelector('.sessions').textContent, /Thursday, 10 a\.m\. · Loteria \(Spanish bingo\)/);
p = await open('?zip=15222&radius=50');
assert(p.cards[0].startsWith('pa-'), 'Pittsburgh searches lead with Pennsylvania games');
for (const id of ['pa-broughton-volunteer-fire-department-pittsburgh', 'pa-library-volunteer-fire-company-library', 'pa-holiday-park-volunteer-fire-department-plum', 'pa-collinsburg-volunteer-fire-company-west-newton']) assert(p.cards.includes(id), id + ' is within 50 miles of downtown Pittsburgh');
assert.match(p.d.getElementById('pa-broughton-volunteer-fire-department-pittsburgh').querySelector('.sessions').textContent, /Monday, 7 p\.m\..*Thursday, 7 p\.m\./s);
assert(p.cards.includes('state-PA'), 'and still offer the way to send Pennsylvania game times');
assert(p.cards.includes('state-OH') && p.cards.includes('state-WV'), 'Pittsburgh is near Ohio and West Virginia');

// Pennsylvania, New York, Utah, Kentucky and West Virginia starter lists: organizer-published schedules, each with its own source.
for (const [code, name, min] of [['PA', 'Pennsylvania', 10], ['NY', 'New York', 3], ['UT', 'Utah', 3], ['KY', 'Kentucky', 4], ['WV', 'West Virginia', 6]]) {
  const rows = data.venues.filter(v => v.state === code);
  assert(rows.length >= min && rows.every(v => v.kind && v.source_url && v.schedule_note), name + ' starter list');
  p = await open('?state=' + code);
  assert.equal(p.count, name + ' bingo places with game days');
  assert.equal(p.cards[p.cards.length - 1], 'state-' + code, name + ' ends with the way to send game times');
  for (const v of rows) assert(p.d.querySelector('#' + v.id + ' a[href^="mailto:travis@vethomeguard.org?subject=FindBingo.org%20correction"]'), v.id + ' has a report link');
}
p = await open('?state=WV');
assert.match(p.d.getElementById('wv-martin-luther-king-jr-community-center-charleston').querySelector('.sessions').textContent, /Thursday, 1:30 p\.m\. · 3rd Thursday of the month/);
assert.match(p.d.getElementById('wv-john-henson-senior-center-hurricane').querySelector('.badge').textContent, /Senior center bingo/);
p = await open('?state=PA');
assert.match(p.d.getElementById('pa-penbrook-american-legion-post-730-harrisburg').querySelector('.sessions').textContent, /Thursday, 6 p\.m\. · 1st and 3rd Thursday of the month/);
assert.match(decodeURIComponent(p.d.querySelector('#pa-tylersport-fire-company-tylersport .small-links a').getAttribute('href')), /Bingo days:\nFirst game starts at:\nPhone for players:/, 'the correction email is ready to fill in');
p = await open('?zip=14624&radius=10');
const gates = p.d.getElementById('ny-gates-center-bingo-patriot-hall-rochester');
assert.match(gates.querySelector('.big-actions a.solid').textContent, /Look up phone number/, 'a listing without a published phone offers a lookup');
assert.match(gates.querySelector('.sessions').textContent, /Wednesday, 7 p\.m\./);
p = await open('?zip=84770&radius=50');
assert(p.cards.includes('ut-st-george-senior-citizen-center-st-george') && p.cards.includes('ut-hurricane-senior-citizen-center-hurricane'));
assert.match(p.d.getElementById('state-UT').textContent, /free bingo at senior centers/);
assert.match(p.d.getElementById('ut-st-george-senior-citizen-center-st-george').querySelector('.badge').textContent, /Senior center bingo/);

// Every state is researched. A ZIP code in a state without a list on this site names who licenses bingo there
// and still asks for game times.
p = await open('?zip=30303');
assert.equal(p.cards[0], 'state-GA');
assert.match(p.d.getElementById('state-GA').textContent, /Secretary of State took over bingo licensing/);
assert(p.d.querySelector('#state-GA a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Georgia"]'));
assert.equal(p.d.querySelector('#state-GA a[target]').href, 'https://sos.ga.gov/how-to-guide/how-guide-charity-bingo', 'the regulator is named and linked');
assert.equal(p.d.querySelector('#state-GA .big-actions a').className, 'solid', 'with no official list to point to, sending game times is the main action');
// Where the state publishes its own list or finder, the card leads with it.
p = await open('?zip=67202');
assert.equal(p.cards[0], 'state-KS');
assert.equal(p.d.querySelector('#state-KS .big-actions a.official').href, 'https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf');
assert.equal(p.d.querySelector('#state-KS p.small a[target]').href, 'https://www.ksrevenue.gov/bustaxtypesbingo.html');
assert(p.d.querySelector('#state-KS .big-actions a.outline[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Kansas"]'));
// Texas: the state's Bingo Hall Locator, with licensed days and times and the hall's phone.
const txRows = data.venues.filter(v => v.state === 'TX');
assert.equal(states.find(s => s.code === 'TX').coverage, 'times');
assert(txRows.length && txRows.every(v => v.sessions.every(x => x.start && x.end) && !v.schedule_note), 'every Texas session has licensed hours');
// Montana: places with a state permit for live bingo, no game days, and only where the list gives the place's own street address.
const mtRows = data.licensed.filter(r => r.state === 'MT');
assert(mtRows.length && mtRows.every(r => r.license_type.includes('bingo') && r.license_expires === '2027-06-30' && !/PO Box/i.test(r.address)));
assert(!mtRows.some(r => /Page \d/.test(r.name)), 'page footers stay out of names');
p = await open('?state=MT');
assert.equal(p.count, 'Montana places with a live bingo permit');
assert.match(p.d.querySelector('#results .note').textContent, /mailing address/);
assert.deepEqual(p.cards, [...mtRows].sort((a, b) => a.county.localeCompare(b.county) || a.city.localeCompare(b.city) || a.name.localeCompare(b.name)).map(r => r.id));
const blacktail = p.d.getElementById('mt-4040442-008-lgt');
assert.match(blacktail.textContent, /Blacktail Station/);
assert.match(blacktail.textContent, /Montana license 4040442-008-LGT \(live bingo permit\), on the state list through Jun 30, 2027/);
assert.match(blacktail.querySelector('.address').textContent, /26 S Montana St, Dillon, MT 59725 · Beaverhead County$/);
p = await open('?zip=59725&radius=10');
assert(p.cards.includes('mt-4040442-008-lgt'), 'with no game days nearby, licensed places show');
// New Mexico: the board's list of groups licensed for bingo, raffles or pull-tabs, with phones; it does not say which.
const nmRows = data.licensed.filter(r => r.state === 'NM');
assert(nmRows.length && nmRows.every(r => r.phone && !r.license_number && !r.license_expires));
p = await open('?state=NM');
assert.equal(p.count, 'New Mexico groups licensed for bingo, raffles or pull-tabs');
const post13 = p.d.getElementById('nm-american-legion-post-13-albuquerque');
assert.match(post13.querySelector('.badge').textContent, /Licensed for bingo, raffles or pull-tabs/);
assert.equal(post13.querySelector('.big-actions a.solid').getAttribute('href'), 'tel:5052431901');
assert.match(post13.textContent, /On New Mexico’s list, with a bingo, raffle or pull-tab license\./);
assert(!/through/.test(post13.querySelector('details').textContent), 'no end date is claimed');
assert(data.licensed.find(r => r.address.startsWith('29 South Florida')).city === 'Alamogordo', 'the town comes from the list headings');
const nmPage = new JSDOM(fs.readFileSync(path.join(site, 'new-mexico/index.html'), 'utf8')).window.document;
assert(!/list dated/.test(nmPage.querySelector('#about').textContent), 'the page has no list date to show');
// Mississippi: halls on the Gaming Commission's licensee map whose games include bingo and whose license is current.
const msRows = data.licensed.filter(r => r.state === 'MS');
assert(msRows.length && msRows.every(r => r.license_type === 'charitable bingo license' && r.license_expires >= '2026-11-17' && !r.phone));
assert(!msRows.some(r => /Big Dog Bingo/.test(r.name)), 'a license past its end date on the map is not shown');
p = await open('?state=MS');
assert.equal(p.count, 'Mississippi halls licensed for bingo');
assert.match(p.d.querySelector('#results .note').textContent, /passed its end date are not shown/);
assert.match(p.d.getElementById('ms-23-00047').textContent, /Mississippi license 23-00047 \(charitable bingo license\), on the state list through Mar 31, 2027/);
assert.match(p.d.getElementById('ms-23-00047').querySelector('.big-actions a.solid').textContent, /Look up phone number/, 'contact phones on the map are not republished');
p = await open('?zip=38837&radius=10');
assert(p.cards.some(id => id.startsWith('ms-')), 'the Burnsville ZIP code has a map point');
p = await open('?zip=78572&radius=10');
assert(p.cards.includes('tx-the-bingo-ranch-mission') && !p.cards.includes('state-TX'));
const ranch = p.d.getElementById('tx-the-bingo-ranch-mission');
assert.equal(ranch.querySelector('.big-actions a.solid').getAttribute('href'), 'tel:9565190074');
assert.match(ranch.querySelector('.address').textContent, /Mission, TX 78572 · Hidalgo County$/);
assert.equal(ranch.querySelector('details a').href, 'https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf');
p = await open('?state=TX&county=Dallas');
assert.equal(p.count, 'Texas bingo halls with game days in Dallas County');
assert(p.cards.includes('tx-strike-it-rich-bingo-inc-dallas') && p.cards.every(id => txRows.find(v => v.id === id).county === 'Dallas'));
p = await open('?zip=83702');
assert.equal(p.cards[0], 'state-ID');
assert.equal(p.d.querySelector('#state-ID .big-actions a.official').href, 'https://www.idaholottery.com/charitable-gaming/licensed-organizations');
// Virginia: the state's directory of bingo sessions, with the days and the hours the doors are open.
const vaRows = data.venues.filter(v => v.state === 'VA');
assert(vaRows.length && vaRows.every(v => v.schedule_note && v.sessions.every(x => x.start && x.end)), 'every Virginia session has door times');
assert.equal(states.find(s => s.code === 'VA').coverage, 'times');
p = await open('?zip=23224&radius=10');
assert.equal(p.count, 'Bingo within 10 miles of 23224 · closest first');
assert(p.cards.includes('va-pops-bingo-world-richmond') && !p.cards.includes('state-VA'), 'a state with its list loaded needs no help card');
const pops = p.d.getElementById('va-pops-bingo-world-richmond');
assert.match(pops.querySelector('.sessions').textContent, /Sunday, 2 to 9 p\.m\./);
assert(/Usual bingo days/.test(pops.querySelector('.when').textContent) && !/Next bingo day/.test(pops.querySelector('.when').textContent), 'the directory skips some dates, so no date is promised');
assert.match(pops.querySelector('.address').textContent, /Richmond, VA 23224 · City of Richmond$/, 'an independent city is not called a county');
assert.equal(pops.querySelector('details a').href, 'https://www.vdacs.virginia.gov/pdf/bingo_events.pdf');
p = await open('?state=VA');
assert.equal(p.count, 'Virginia bingo halls with game days');
assert.deepEqual(p.cards, [...vaRows].sort((a, b) => a.county.localeCompare(b.county) || a.city.localeCompare(b.city) || a.name.localeCompare(b.name)).map(v => v.id));
assert.equal(p.d.querySelector('#county option[value="Richmond city"]').textContent, 'City of Richmond');
assert.match(p.d.getElementById('va-appomattox-moose-lodge-975-loyal-order-of-moose-inc-appomattox').textContent, /First Sunday of the month, in the social quarters/);
assert.match(p.d.getElementById('va-appomattox-moose-lodge-975-loyal-order-of-moose-inc-appomattox').textContent, /may be for members and their guests/);
p = await open('?state=VA&county=' + encodeURIComponent('Richmond city'));
assert.equal(p.count, 'Virginia bingo halls with game days in City of Richmond');
assert(p.cards.length && p.cards.every(id => vaRows.find(v => v.id === id).county === 'Richmond city'));
for (const slug of ['texas', 'missouri', 'massachusetts', 'georgia', 'alaska', 'hawaii']) assert(fs.readFileSync(path.join(root, 'bingo-site/findbingo/sitemap.xml'), 'utf8').includes(`<loc>https://www.findbingo.org/${slug}/</loc>`), slug + ' is researched, so it is in the sitemap');
p = await open('?state=AK');
assert.equal(p.count, 'Alaska: no game list yet');
assert.equal(p.d.querySelector('#state-buttons details.more-states a[data-state="AK"]').getAttribute('aria-current'), 'true');
const ga = new JSDOM(fs.readFileSync(path.join(site, 'georgia/index.html'), 'utf8')).window.document;
assert(!ga.querySelector('meta[name=robots]'), 'a researched page is open to search engines');
assert(ga.querySelector('#run-a-game a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Georgia"]'));
assert(ga.querySelector('#about a[href="https://sos.ga.gov/how-to-guide/how-guide-charity-bingo"]'));
assert(!ga.getElementById('official-list'), 'no official-list button without an official list');
const idaho = new JSDOM(fs.readFileSync(path.join(site, 'idaho/index.html'), 'utf8')).window.document;
assert.equal(idaho.querySelector('#official-list a.solid').href, 'https://www.idaholottery.com/charitable-gaming/licensed-organizations', 'a state page leads with the official list');
assert(idaho.querySelector('#official-list').compareDocumentPosition(idaho.getElementById('listings')) & 4, 'the official list comes before the empty list');
const va = new JSDOM(fs.readFileSync(path.join(site, 'virginia/index.html'), 'utf8')).window.document;
assert(!va.getElementById('official-list') && va.querySelectorAll('#listings article').length === vaRows.length, 'Virginia shows its own list now');
assert([...va.querySelectorAll('#listings h2')].some(h => h.textContent === 'City of Richmond') && [...va.querySelectorAll('#listings h2')].some(h => h.textContent === 'Henrico County'));
assert.match(va.getElementById('va-copper-creek-moccasin-volunteer-fire-department-castlewood').textContent, /Castlewood, VA 24224 · Russell County/);
assert.match(va.querySelector('#about').textContent, /list dated September 1, 2026/);
// Hawaii does not license bingo and Tennessee allows it only at yearly events, so their pages say so in their own words.
const hi = new JSDOM(fs.readFileSync(path.join(site, 'hawaii/index.html'), 'utf8')).window.document;
assert.match(hi.querySelector('.lead').textContent, /^Hawaii does not license bingo\./);
assert.match(hi.querySelector('meta[name=description]').content, /^Hawaii does not license bingo\./);
assert.match(new JSDOM(fs.readFileSync(path.join(site, 'tennessee/index.html'), 'utf8')).window.document.querySelector('.lead').textContent, /only at yearly nonprofit fundraising events/);
assert(!new JSDOM(fs.readFileSync(path.join(site, 'michigan/index.html'), 'utf8')).window.document.querySelector('meta[name=robots]'));

// ZIP mistakes get plain-language help.
p = await open('?zip=00601');
assert.match(p.status, /We could not find ZIP code 00601\. Please check the five numbers\./);
assert.equal(p.cards.length, 0);
p = await open('?zip=4816');
assert.match(p.status, /Please type the five numbers of your ZIP code/);

// State and county browsing.
p = await open('?state=MI&county=Macomb');
assert.equal(p.count, 'Michigan bingo halls with game days in Macomb County');
assert.deepEqual(p.cards.sort(), data.venues.filter(v => v.county === 'Macomb').map(v => v.id).sort());
assert.equal(p.d.getElementById('county-wrap').hidden, false);
assert.equal(p.d.querySelector('#state-buttons a[data-state="MI"]').getAttribute('aria-current'), 'true');
p = await open('?state=IN');
assert.equal(p.count, 'Indiana groups licensed for bingo');
p = await open('?state=OH');
assert.deepEqual(p.cards, ['state-OH']);
assert.equal(p.d.querySelector('#state-OH a.solid').href, 'https://www.findbingo.org/ohio/');
p = await open('?state=NE');
assert.deepEqual(p.cards, ['state-NE']);
p = await open('?state=MO&county=Greene');
assert.deepEqual(p.cards.sort(), data.venues.filter(v => v.state === 'MO' && v.county === 'Greene').map(v => v.id).sort());

// Names are shown as text, never as markup.
p = await open('?state=MI&county=Ingham');
assert(p.d.getElementById('results').textContent.includes('F & AM 70'));

// One plain page per state, for search engines and people without JavaScript: a real title, description,
// canonical address and heading, and the state's listings written out as HTML, by county. Never counts.
const sitemap = fs.readFileSync(path.join(root, 'bingo-site/findbingo/sitemap.xml'), 'utf8');
const home = static_;
const ld = JSON.parse(home.querySelector('script[type="application/ld+json"]').textContent);
assert.equal(ld['@type'], 'WebSite');
assert.equal(ld.url, 'https://www.findbingo.org/');
assert.equal(ld.publisher.name, 'Veteran Home Guardians');
assert(home.querySelector('footer a[href="https://mobilitytalk.org/states/"]') && home.querySelector('footer a[href="https://travisvought.com/"]'));
const countWords = /\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b/i;
const seen = {h1: new Set(), title: new Set(), description: new Set(), welcome: new Set(), og: new Set()};
for (const s of states) {
  freeScratch(); await new Promise(r => setImmediate(r));
  const slug = SLUGS[s.code];
  assert.equal(home.querySelector(`#state-buttons a[data-state="${s.code}"]`).getAttribute('href'), slug + '/', 'state buttons link to the state page');
  assert.equal(sitemap.includes(`<loc>https://www.findbingo.org/${slug}/</loc>`), s.coverage !== 'pending', slug + ' is in the sitemap once it has content');
  if (s.code === 'OH') continue;  // Ohio's page is the Ohio Bingo Finder
  const file = path.join(root, 'bingo-site/findbingo', slug, 'index.html'), text = unAd(fs.readFileSync(file, 'utf8'));
  assert.equal(text, fs.readFileSync(path.join(site, slug, 'index.html'), 'utf8'), slug + ' copies match');
  const d = scratch(text);
  assert.equal(d.querySelector('link[rel=canonical]').href, `https://www.findbingo.org/${slug}/`);
  assert(d.title.startsWith(s.name + ' Bingo') && d.title.endsWith('| FindBingo.org'), d.title);
  assert(d.querySelector('meta[name=description]').content.includes(s.code === 'DC' ? 'DC' : s.name));
  // Each page speaks to the person who lands on it: its own heading, title, description and opening (November 23, 2026).
  const said = {h1: d.querySelector('h1').textContent, title: d.title, description: d.querySelector('meta[name=description]').content,
                welcome: d.querySelector('header .lead').textContent, og: d.querySelector('meta[property="og:title"]').content};
  assert(said.h1.includes(s.code === 'DC' ? 'DC' : s.name), said.h1);
  assert.equal(said.og, said.title.replace(' | FindBingo.org', ''));
  assert.equal(d.querySelector('meta[property="og:description"]').content, said.description);
  assert(!/[{}]/.test(Object.values(said).join(' ')), slug + ': every placeholder is filled');
  for (const [k, v] of Object.entries(said)) { assert(!seen[k].has(v), slug + ': ' + k + ' is its own'); seen[k].add(v) }
  assert(d.querySelector('main > form.zip-box') === d.querySelector('main').firstElementChild, slug + ': the finder comes first');
  assert.equal(JSON.parse(d.querySelector('script[type="application/ld+json"]').textContent)['@type'], 'BreadcrumbList');
  assert(text.includes("vhg-guide.goatcounter.com/count"), slug + ' counts page views');
  assert.equal(d.querySelectorAll('script[src]').length, 0, 'no outside scripts');
  // Hall and group names can hold numbers ("Elks Lodge 1229 Hall B"), so they are left out of this check.
  const plain = d.body.cloneNode(true);
  for (const e of plain.querySelectorAll('#listings article h3, #listings .org, #listings .small, #listings .address')) e.remove();
  assert(!countWords.test(plain.textContent), slug + ': no counts on the site');
  const form = d.querySelector('form.zip-box');
  assert.equal(form.getAttribute('action'), '../');
  assert(form.querySelector('input[name=zip]') && form.querySelector('select[name=radius]'), 'the ZIP search opens the finder');
  assert.equal(d.querySelectorAll('.state-buttons a').length, states.length - 1, 'links to every other state');
  for (const a of d.querySelectorAll('a[href^="../"]')) {
    // A link may open a place on the page (../bingo-age-by-state/#ohio): the page must exist and hold that id.
    const [href, hash] = a.getAttribute('href').split('#');
    const target = path.join(root, 'bingo-site/findbingo', slug, href);
    const file = [target.endsWith('/') ? path.join(target, 'index.html') : target, path.join(target, 'index.html')].find(f => fs.existsSync(f));
    assert(file, a.getAttribute('href'));
    if (hash) assert(fs.readFileSync(file, 'utf8').includes(`id="${hash}"`), a.getAttribute('href'));
  }
  const ids = [...d.querySelectorAll('#listings article')].map(a => a.id);
  const today = data.generated_on;
  const expected = s.coverage === 'licenses' ? data.licensed.filter(r => r.state === s.code && (r.license_expires || today) >= today) : data.venues.filter(v => v.state === s.code);
  assert.deepEqual(ids.sort(), expected.map(r => r.id).sort(), slug + ' lists every record');
  if (['none'].includes(s.coverage)) assert(d.querySelector('#listings .empty'));
  for (const c of new Set(expected.map(r => r.county))) assert(d.querySelector(`#listings h2`) && [...d.querySelectorAll('#listings h2')].some(h => h.textContent === (c.endsWith(' city') ? 'City of ' + c.slice(0, -5) : c + ' County')), c);
  for (const a of d.querySelectorAll('.counties a')) assert(d.getElementById(a.getAttribute('href').slice(1)), 'county jump ' + a.getAttribute('href'));
}
const mi = new JSDOM(fs.readFileSync(path.join(site, 'michigan/index.html'), 'utf8')).window.document;
const rose = mi.getElementById('mi-rosemack-bingo-roseville');
assert.match(rose.querySelector('.sessions').textContent, /Monday, 4:30 to 10 p\.m\. · Gesu School/, 'the same time wording as the finder');
assert.match(rose.querySelector('.note').textContent, /Michigan's weekly bingo license list/);
assert.equal(rose.querySelector('.big-actions a.outline').href, 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent('20789 E 13 Mile Road, Roseville, MI 48066'));
assert.match(decodeURIComponent(rose.querySelector('.small-links a').getAttribute('href')), /^mailto:travis@vethomeguard\.org\?subject=FindBingo\.org correction: .*\(mi-rosemack-bingo-roseville\)/);
if (pending.length) assert.match(mi.getElementById('pending-MI').textContent, new RegExp(pending[pending.length - 1]));
assert(mi.body.textContent.includes('F & AM 70'), 'names are text');
const fla = new JSDOM(fs.readFileSync(path.join(site, 'florida/index.html'), 'utf8')).window.document;
assert.equal(fla.querySelector('#fl-carvill-senior-center-jacksonville .big-actions a.solid').getAttribute('href'), 'tel:9042556650');
assert.match(fla.querySelector('#fl-charlie-t-joseph-senior-center-jacksonville .sessions').textContent, /Monday, time not posted/);
const ind = new JSDOM(fs.readFileSync(path.join(site, 'indiana/index.html'), 'utf8')).window.document;
assert.match(ind.getElementById('in-000114').textContent, /license 000114 \(Annual Activity\), on the state list through October 31, 2027/);
const ky = new JSDOM(fs.readFileSync(path.join(site, 'kentucky/index.html'), 'utf8')).window.document;
assert(ky.querySelector('#run-a-game a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Kentucky"]'));
assert(ky.querySelector('#about a[href="https://dcg.ky.gov/"]'));

// Privacy and Advertise pages (November 19, 2026): one each, linked from every footer and in the sitemap.
const findbingo = path.join(root, 'bingo-site/findbingo');
for (const f of ['privacy/index.html', 'advertise/index.html'])
  assert.equal(unAd(fs.readFileSync(path.join(findbingo, f), 'utf8'), f === 'advertise/index.html'), fs.readFileSync(path.join(site, f), 'utf8'), f + ' copies match');
const privacy = new JSDOM(fs.readFileSync(path.join(site, 'privacy/index.html'), 'utf8')).window.document;
assert.equal(privacy.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/privacy/');
assert.equal(privacy.querySelector('h1').textContent, 'Privacy');
const privacyText = privacy.querySelector('main').textContent;
for (const words of ['November 27, 2026', 'GoatCounter does not use cookies', 'It does not store the IP address', 'on your own device',
  'The ZIP code is not sent to us or to anyone else to look it up', 'Cloudflare', 'GitHub', 'Google AdSense may show ads here and set cookies.',
  'Find Bingo uses Google AdSense, so Google may show ads on this site and set cookies.', 'We ask Google for non-personalized ads',
  'Ads are kept apart from the game listings, and they never change which games are listed or their order.',
  'We do not sell personal information', 'not directed to children under 13'])
  assert(privacyText.includes(words), 'privacy page says: ' + words);
for (const href of ['https://adssettings.google.com', 'https://policies.google.com/technologies/ads', 'https://optout.aboutads.info',
  'https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement', '../advertise/'])
  assert(privacy.querySelector(`main a[href="${href}"]`), 'privacy page links ' + href);
assert(privacy.querySelector('main a[href^="mailto:travis@vethomeguard.org"]'), 'privacy questions go to the site’s existing contact address');
// Map (November 21, 2026): the privacy page names OpenStreetMap as the source of the map pictures, and what it sees.
for (const words of ['OpenStreetMap (tile.openstreetmap.org)', 'sees your internet (IP) address', 'Your location is not sent to us or to anyone else'])
  assert(privacyText.includes(words), 'privacy page says: ' + words);
assert(privacy.querySelector('main a[href="https://osmfoundation.org/wiki/Privacy_Policy"]'), 'privacy page links OpenStreetMap’s privacy policy');
// The ZIP search really does run in the browser: the finder fetches only whole files, never a ZIP lookup.
assert(!/fetch\([^)]*zip=/i.test(html) && /getJSON\(/.test(html), 'no ZIP code is sent to a lookup service');
const advertise = new JSDOM(fs.readFileSync(path.join(site, 'advertise/index.html'), 'utf8')).window.document;
const advertiseText = advertise.querySelector('main').textContent;
for (const words of ['Every ad we sell is labeled “Advertisement.”', 'Ads from Google AdSense carry Google’s own ad label.', 'Never inside them', 'Ads never add, remove, change or reorder listings',
  'We review every ad we sell before it runs', 'misleading', 'Ad income supports Veteran Home Guardians'])
  assert(advertiseText.includes(words), 'advertise page says: ' + words);
// Prices on the page: the featured event's $100 and the hall game site's $100 a month (owner direction, November 20, 2026); ads have no listed price.
assert.deepEqual(advertiseText.match(/\$\s?\d[\d,]*/g), ['$100', '$100', '$100', '$100'], 'only the featured event and hall site prices');
assert(advertise.getElementById('events').textContent.includes('$100'), 'the price sits with featured events');
assert(advertise.getElementById('hall-site').textContent.includes('$100 a month') && advertiseText.includes('Your games stay listed free'), 'hall site price, and listings stay free');
assert(advertise.querySelector('main a[href^="mailto:travis@vethomeguard.org?subject=Advertising%20on%20Find%20Bingo"]'));
assert(sitemap.includes('<loc>https://www.findbingo.org/privacy/</loc>') && sitemap.includes('<loc>https://www.findbingo.org/advertise/</loc>'));
// About and contact, and Terms of use (November 22, 2026): what an ad network's reviewers look for.
for (const f of ['about/index.html', 'terms/index.html'])
  assert.equal(unAd(fs.readFileSync(path.join(findbingo, f), 'utf8'), false), fs.readFileSync(path.join(site, f), 'utf8'), f + ' copies match');
const aboutDoc = new JSDOM(fs.readFileSync(path.join(site, 'about/index.html'), 'utf8')).window.document;
assert.equal(aboutDoc.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/about/');
assert(aboutDoc.getElementById('contact') && aboutDoc.querySelector('main a[href^="mailto:travis@vethomeguard.org"]'), 'About names a contact address');
assert(!/\b\d[\d,]* (halls|places|games|states|counties|listings)\b/i.test(aboutDoc.querySelector('main').textContent), 'About states no counts');
const termsDoc = new JSDOM(fs.readFileSync(path.join(site, 'terms/index.html'), 'utf8')).window.document;
const termsText = termsDoc.querySelector('main').textContent;
assert.equal(termsDoc.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/terms/');
for (const words of ['does not run games, sell cards, take bets or pay prizes', 'Call the hall before you go', 'Ads and featured events are labeled'])
  assert(termsText.includes(words), 'terms say: ' + words);
assert(sitemap.includes('<loc>https://www.findbingo.org/about/</loc>') && sitemap.includes('<loc>https://www.findbingo.org/terms/</loc>'), 'About and Terms are in the sitemap');
// Help for halls (owner direction, November 20, 2026): the pitch follows each state's own rule on bingo money.
const hallsDoc = new JSDOM(fs.readFileSync(path.join(site, 'halls/index.html'), 'utf8')).window.document;
const hallsText = hallsDoc.querySelector('main').textContent;
assert(sitemap.includes('<loc>https://www.findbingo.org/halls/</loc>'), 'halls page is in the sitemap');
for (const s of states.filter(x => x.halls)) assert(hallsDoc.getElementById('rules-' + s.code.toLowerCase()), 'halls page summarizes ' + s.name);
assert(hallsText.includes('not legal advice') && hallsText.includes('Bingo suppliers and distributors'));
// How Find Bingo works for halls, in Travis's words of his model (November 27, 2026): free listings, update or claim,
// community partner, paid help. Plain words beside decorative icons; no prices and no counts.
{
  const how = hallsDoc.querySelector('section.hall-how');
  assert(how && how === hallsDoc.querySelector('main section'), 'the model comes first on the halls page');
  assert.deepEqual([...how.querySelectorAll('.hall-steps h3')].map(h => h.textContent),
    ['Every game is listed free', 'Update or claim your listing', 'Become a community partner', 'Paid help, if you prefer']);
  const howText = how.textContent;
  for (const words of ['for every hall, free', 'claim your listing', 'name Veteran Home Guardians as a charitable recipient of part of your bingo proceeds',
    'name the local partner shown on your state’s page', 'a game website built for your hall and kept current', 'a featured event in local results', 'help with advertising'])
    assert(howText.includes(words), 'halls page says: ' + words);
  assert(!/\$|\d/.test(howText), 'no prices or numbers in the model');
  for (const icon of how.querySelectorAll('.hall-ic')) {
    assert.equal(icon.getAttribute('aria-hidden'), 'true', 'hall icons are decoration');
    assert(icon.nextElementSibling.querySelector('h3').textContent.trim(), 'every icon sits beside words');
  }
  for (const href of ['../ohio/#submit-details', 'https://www.ohiobingo.org/claim.html', '../ohio/partners.html#sponsors', '#partners', '../advertise/'])
    assert(how.querySelector(`a[href="${href}"]`), 'the model links ' + href);
  assert(how.querySelector('a[href^="mailto:travis@vethomeguard.org?subject=Update%20our%20bingo%20listing"]') && how.querySelector('a.solid[href^="mailto:travis@vethomeguard.org"]'), 'halls reach us at the existing address');
}
assert(!hallsText.includes('$' + 100) && !kyDocText().includes('$' + 100), 'our prices live on the Advertise page; dollar figures elsewhere are legal limits');
function kyDocText() { return ky.getElementById('run-a-game').textContent; }
const kyRun = kyDocText();
assert(kyRun.includes('never ask for a share') && !kyRun.includes('5 to 10') && ky.getElementById('money-rule') && ky.getElementById('ad-rule'),
  'Kentucky groups keep their money, so no share is asked');
const inRun = new JSDOM(fs.readFileSync(path.join(site, 'indiana/index.html'), 'utf8')).window.document.getElementById('run-a-game').textContent;
assert(inRun.includes('local partner charity') && !inRun.includes('5 to 10') && !inRun.includes('Veteran Home Guardians as one'),
  'outside Ohio a required gift gets the local-partner offer, never the Ohio share');
const gaRun = ga.getElementById('run-a-game');
assert(!gaRun.querySelector('#money-rule') && !gaRun.textContent.includes('5 to 10') && gaRun.querySelector('a[href="../halls/"]'),
  'a state whose rules are not summarized makes no claim about them');
assert(advertiseText.includes('Community partner (Ohio)') && advertise.querySelector('main a[href="../halls/"]'), 'the partnership is offered where the law fits it');
// Local partners (owner direction, November 22, 2026): outside Ohio, a standing, voluntary ask for a local group doing the work.
const partnered = states.filter(x => x.partner);
assert(partnered.some(x => x.code === 'NY' && x.partner.name === 'Mobility Independence Foundation')
  && partnered.some(x => x.code === 'WA' && x.partner.name === 'Light Upon Light'), 'New York and Washington name their partners');
for (const s of partnered) {
  const doc = new JSDOM(fs.readFileSync(path.join(site, s.code === 'NY' ? 'new-york' : s.name.toLowerCase().replace(/ /g, '-'), 'index.html'), 'utf8')).window.document;
  const panel = doc.getElementById('partner');
  assert(panel && panel.textContent.includes(s.partner.name) && panel.textContent.includes('never a condition of being listed'), s.name + ' shows its partner and the ask');
  assert(panel.compareDocumentPosition(doc.getElementById('run-a-game')) & 4, s.name + ': the partner sits after the listings, before Run a bingo game');
  assert(doc.querySelector('#run-a-game a[href="#partner"]') && doc.getElementById('money-rule'), s.name + ': the ask points at the state rule on bingo money');
  assert(!panel.textContent.includes('Veteran Home Guardians') && !panel.textContent.includes('5 to 10'), s.name + ': the ask is for the local partner, never a VHG share');
  assert(hallsDoc.querySelector(`#partner-${s.code.toLowerCase()} a[href$="/#partner"]`), 'halls page lists the ' + s.name + ' partner');
}
const waPanel = new JSDOM(fs.readFileSync(path.join(site, 'washington/index.html'), 'utf8')).window.document.getElementById('partner').textContent;
assert(waPanel.includes('not bingo proceeds') && !/bingo night for them/i.test(waPanel), 'Washington keeps bingo proceeds with the group, so no benefit game is asked');
assert(!ky.getElementById('partner') && !ga.getElementById('partner'), 'states without a partner show no partner panel');
const allPages = [];
(function walk(dir) {
  for (const e of fs.readdirSync(dir, {withFileTypes: true})) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p); else if (e.name.endsWith('.html') && !e.name.startsWith('google')) allPages.push(p);
  }
})(findbingo);
assert(allPages.length > 50);
const noAdsPromise = /never depends? on (donations or )?advertising|(do not|don['’]t|never) (sell|show|run|carry|accept) (any )?(ads|advertising)|\bno (ads|advertising)\b|ad-free|without (ads|advertising)/i;
for (const file of allPages) {
  freeScratch(); await new Promise(r => setImmediate(r));
  const rel = path.relative(findbingo, file), text = fs.readFileSync(file, 'utf8');
  assert(!noAdsPromise.test(text), rel + ': no promise against ads');
  // Every page with a footer links Privacy and Advertise (the poster is a print-only page with no footer).
  const d = scratch(text);
  if (!d.querySelector('footer')) { assert.equal(rel, path.join('ohio', 'poster.html'), rel + ' has a footer'); continue; }
  // Pages sit at the top (''), one folder down (state pages, '../') or two (town pages, '../../').
  const up = path.dirname(rel) === '.' ? '' : '../'.repeat(path.dirname(rel).split(path.sep).length);
  assert(d.querySelector(`footer a[href="${up}privacy/"]`) && d.querySelector(`footer a[href="${up}advertise/"]`), rel + ': footer links Privacy and Advertise');
  assert(d.querySelector(`footer a[href="${up}about/"]`) && d.querySelector(`footer a[href="${up}terms/"]`), rel + ': footer links About and Terms');
  // With the default (empty) ad list there is no ad markup at all.
  // Shop picks (.picks) are store links, not ads; once an affiliate tag is set they carry rel="sponsored" too.
  assert(!d.querySelector('.ad-slot, .ad-label') && ![...d.querySelectorAll('[rel~="sponsored"]')].some(a => !a.closest('.picks'))
    && !text.includes('class="ad-slot'), rel + ': no ad markup when no ad is running');
}
assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, 'data/findbingo-ads.json'), 'utf8')), [], 'no ads by default');
assert(/Ads, when shown, are labeled and never decide which games are listed\./.test(home.querySelector('footer').textContent));

// A sample ad, built with the real builder: labeled, rel="sponsored", outside the listings, one place per page.
const {spawnSync} = require('child_process');
function buildWith(ads, pages) {
  const code = 'import json,sys;from pathlib import Path;sys.path.insert(0,"scripts");import findbingo_site as f;'
    + 'out=f.make_findbingo(Path("."),json.loads(sys.argv[1]));want=json.loads(sys.argv[2]);'
    + 'print(json.dumps({"files":sorted(out),"pages":{k:out["findbingo-site/"+k] for k in want}}))';
  const r = spawnSync('python3', ['-c', code, JSON.stringify(ads), JSON.stringify(pages)], {cwd: root, encoding: 'utf8', maxBuffer: 1 << 28});
  return r.status === 0 ? JSON.parse(r.stdout) : {error: r.stderr};
}
const sample = [
  {slot: 'home', sponsor: 'Sample Senior Rides', text: 'Rides to the bingo hall and back.', url: 'https://example.org/rides', image: 'assets/vhg-logo.png', alt: 'Sample Senior Rides logo'},
  {slot: 'state:michigan', sponsor: 'Sample Daubers', text: 'Bingo supplies, shipped free.', url: 'https://example.org/daubers'},
  {slot: 'state:florida', sponsor: 'Sample Diner', text: 'Breakfast before the early bird game.', url: 'https://example.org/diner', start: '2026-12-01', end: '2026-12-31'},
];
const built = buildWith(sample, ['index.html', 'michigan/index.html', 'florida/index.html', 'texas/index.html']);
assert(!built.error, built.error);
assert(built.files.includes('findbingo-site/ads/vhg-logo.png') && built.files.includes('bingo-site/findbingo/ads/vhg-logo.png'), 'ad pictures are served from ads/');
function checkAd(d, where) {
  const ads = d.querySelectorAll('aside.ad-slot');
  assert.equal(ads.length, 1, where + ': one ad place');
  const ad = ads[0];
  assert.equal(ad.getAttribute('aria-label'), 'Advertisement');
  assert.equal(ad.firstElementChild.className, 'ad-label');
  assert.equal(ad.firstElementChild.textContent, 'Advertisement', where + ': the label is on top');
  for (const a of ad.querySelectorAll('a')) assert.deepEqual(a.rel.split(' ').sort(), ['noopener', 'sponsored'], where + ': sponsored link');
  assert(!ad.closest('article, #results, #listings, .grid, .sessions'), where + ': never inside the listings');
  assert(!d.querySelector('article .ad-slot, #results .ad-slot, #listings .ad-slot'));
  return ad;
}
let ad = checkAd(new JSDOM(built.pages['index.html']).window.document, 'home');
const homeDoc = ad.ownerDocument;
assert(homeDoc.getElementById('results').compareDocumentPosition(ad) & 4, 'home ad comes after the results');
assert(homeDoc.getElementById('state-buttons').compareDocumentPosition(ad) & 4, 'home ad comes after the state list');
assert(ad.compareDocumentPosition(homeDoc.getElementById('run-a-game')) & 4, 'home ad sits before the panels below');
assert.equal(ad.querySelector('img').getAttribute('src'), 'ads/vhg-logo.png');
assert.equal(ad.querySelector('img').alt, 'Sample Senior Rides logo');
assert(!ad.hidden && ad.textContent.includes('Sample Senior Rides') && ad.querySelector('a').href === 'https://example.org/rides');
ad = checkAd(new JSDOM(built.pages['michigan/index.html']).window.document, 'michigan');
assert(ad.ownerDocument.getElementById('listings').compareDocumentPosition(ad) & 4, 'state ad comes after the listings');
assert(!(ad.compareDocumentPosition(ad.ownerDocument.querySelector('main form.zip-box')) & 4), 'never above the main content');
assert(!built.pages['texas/index.html'].includes('class="ad-slot'), 'a state with no ad has no ad markup');
// A dated ad shows only on its dates (Eastern time), and stays hidden without JavaScript.
function at(page, when) {
  return new JSDOM(page, {runScripts: 'dangerously', beforeParse(w) {
    const RealDate = w.Date;
    w.Date = class extends RealDate { constructor(...a) { super(...(a.length ? a : when)) } static now() { return new RealDate(...when).getTime() } };
  }}).window.document.querySelector('aside.ad-slot');
}
const flAd = built.pages['florida/index.html'];
assert(new JSDOM(flAd).window.document.querySelector('aside.ad-slot').hidden, 'hidden without JavaScript');
assert(at(flAd, [2026, 10, 16, 10, 0]).hidden, 'not shown before it starts');
assert(!at(flAd, [2026, 11, 5, 10, 0]).hidden, 'shown on its dates');
assert(at(flAd, [2027, 0, 2, 10, 0]).hidden, 'not shown after it ends');
// Two ads can never show in one place at once, and a bad ad stops the build.
assert(buildWith([sample[0], {...sample[0], sponsor: 'Second'}], []).error, 'two home ads at once are refused');
assert(buildWith([{slot: 'state', sponsor: 'All states', text: 'x', url: 'https://example.org/'}, sample[1]], []).error, 'a state ad and an every-state ad at once are refused');
assert(buildWith([{...sample[1], url: 'http://example.org/'}], []).error, 'ad links use https');
assert(buildWith([{...sample[0], alt: ''}], []).error, 'a picture needs alt text');
assert(buildWith([{...sample[1], slot: 'sidebar'}], []).error, 'only known places');

// Practice card (November 19, 2026): a just-for-fun card on the home page, nothing sent or stored.
{
  const p = await open('');
  const d = p.d, cells = [...d.querySelectorAll('#card-body button')];
  assert.equal(cells.length, 25);
  assert.equal(cells[12].textContent, 'FREE');
  const nums = cells.filter((_, i) => i !== 12).map(b => +b.textContent);
  assert.equal(new Set(nums).size, 24, 'no number twice on a card');
  cells.forEach((b, i) => { if (i !== 12) { const col = i % 5, n = +b.textContent; assert(n > col * 15 && n <= col * 15 + 15, 'each column holds its own fifteen numbers') } });
  assert(d.querySelector('header .teaser a[href="#play"]') && d.querySelector('header .chooser a[href="how-to-play-bingo/"]'), 'the header invites people to play and to take the class');
  // The home page asks who is there and sends each person to a page that already exists (owner direction, November 23, 2026).
  assert.deepEqual([...d.querySelectorAll('header .chooser a')].map(a => [a.textContent, a.getAttribute('href')]),
    [['Find a game near me', '#zip-form'], ['I run a bingo hall', 'halls/'], ['I want to learn to play', 'how-to-play-bingo/'], ['My charity wants bingo support', 'halls/#partners'], ['I want bingo gear or a gift', 'shop/']]);
  d.getElementById('choose-find').click();
  assert.equal(d.activeElement, d.getElementById('zip'), 'finding a game puts the cursor in the ZIP box');
  let calls = 0;
  while (!d.getElementById('play').classList.contains('win') && calls < 75) { d.getElementById('call-ball').click(); calls++; }
  assert(d.getElementById('play').classList.contains('win'), 'marking for you reaches a bingo by the last ball');
  assert.match(d.getElementById('call-line').textContent, /^[BINGO]-\d+/);
  assert(d.getElementById('call-ball').disabled, 'no more calls after a bingo');
  assert.equal(d.getElementById('play-find').getAttribute('href'), '#zip-form', 'a win points to the real search');
  d.getElementById('new-card').click();
  assert(!d.getElementById('play').classList.contains('win') && !d.getElementById('call-ball').disabled, 'a new card starts fresh');
  d.getElementById('auto-mark').checked = false;
  const first = d.querySelector('#card-body button:not(.free)');
  first.click();
  assert.match(d.getElementById('play-msg').textContent, /hasn.t been called yet/, 'you can only mark numbers that were called');
  assert(fs.readFileSync(path.join(site, 'index.html'), 'utf8').includes('@media print{#play,'), 'the practice card stays off printed lists');
}
// The guides for new players (November 27, 2026): how to play (the bingo class, moved from /learn/), bingo terms, pull tabs
// and bingo age by state. Each is on findbingo.org with AdSense, in the sitemap, linked from the home page, every footer and
// the other guides, with breadcrumbs, and with question markup only for questions written on the page in the same words.
{
  const GUIDES = {
    'how-to-play-bingo/': ['How to Play Bingo: A Friendly Class for First-Timers | FindBingo.org', 'How to play bingo at a hall'],
    'bingo-terms/': ['Bingo Terms and Slang: A Glossary of Hall Bingo Words | FindBingo.org', 'Bingo terms, A to Z'],
    'pull-tabs/': ['Pull Tabs and Instant Bingo Tickets: How They Work | FindBingo.org', 'Pull tabs, explained'],
    'bingo-age-by-state/': ['Bingo Age by State: How Old to Play Charity Bingo | FindBingo.org', 'How old do you have to be to play bingo?'],
  };
  const guide = {};
  assert(home.querySelector('#new-to-bingo h2').textContent === 'New to hall bingo?', 'the home page has a panel for first-timers');
  assert(home.getElementById('play').compareDocumentPosition(home.getElementById('new-to-bingo')) & 4, 'the guides follow the practice card');
  for (const [p, [title, h1]] of Object.entries(GUIDES)) {
    freeScratch(); await new Promise(r => setImmediate(r));
    const text = unAd(fs.readFileSync(path.join(root, 'bingo-site/findbingo', p, 'index.html'), 'utf8'));
    assert.equal(text, fs.readFileSync(path.join(site, p, 'index.html'), 'utf8'), p + ' copies match, apart from AdSense on findbingo.org');
    guide[p] = text;
    const d = scratch(text);
    assert.equal(d.title, title);
    assert.equal(d.querySelector('h1').textContent, h1);
    assert.equal(d.querySelectorAll('h1').length, 1, p + ': one main heading');
    assert.equal(d.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/' + p);
    assert(d.querySelector('meta[name=description]').content.length > 80, p + ': a real description');
    assert(sitemap.includes(`<loc>https://www.findbingo.org/${p}</loc>`), p + ' is in the sitemap');
    // Headings never skip a level, so screen reader users can move through the page by heading.
    let level = 1;
    for (const h of d.querySelectorAll('h1, h2, h3, h4')) { const n = +h.tagName[1]; assert(n <= level + 1, p + ': heading order at ' + h.textContent); level = n; }
    const ids = [...d.querySelectorAll('[id]')].map(e => e.id);
    assert.equal(new Set(ids).size, ids.length, p + ': ids are unique');
    for (const a of d.querySelectorAll('a[href^="#"]')) assert(a.getAttribute('href') === '#' + 'top' || d.getElementById(a.getAttribute('href').slice(1)), p + ': in-page link ' + a.getAttribute('href'));
    const lds = [...d.querySelectorAll('script[type="application/ld+json"]')].map(x => JSON.parse(x.textContent));
    const crumbs = lds.find(x => x['@type'] === 'BreadcrumbList');
    assert.equal(crumbs.itemListElement[0].item, 'https://www.findbingo.org/');
    assert.equal(crumbs.itemListElement.at(-1).item, 'https://www.findbingo.org/' + p, p + ': breadcrumbs end at the page');
    const faq = lds.find(x => x['@type'] === 'FAQPage');
    if (p === 'bingo-terms/') assert(!faq && !d.querySelector('section.faq'), 'no question markup where no questions are written');
    else {
      const shown = [...d.querySelectorAll('section.faq h3')].map(h => [h.textContent, h.nextElementSibling.textContent]);
      assert(shown.length >= 3, p + ': common questions on the page');
      assert.deepEqual(faq.mainEntity.map(q => [q.name, q.acceptedAnswer.text]), shown, p + ': question markup matches the page word for word');
    }
    // Linked from the home page, every footer and the other guides.
    assert(home.querySelector(`#new-to-bingo .guide-links a[href="${p}"]`), p + ' is linked from the home page');
    assert(home.querySelector(`footer a[href="${p}"]`), p + ' is in the home page footer');
    for (const other of Object.keys(GUIDES)) {
      assert(d.querySelector(`footer a[href="../${other}"]`), p + ': footer links ' + other);
      if (other !== p) assert(d.querySelector(`main a[href^="../${other}"]`), p + ' links ' + other);
    }
    assert(d.querySelector('header .brand a[href="../"]') && d.querySelector('main a[href="../"]'), p + ': a way back to the finder');
  }
  // How to play: the bingo class, written to a nervous first-timer, covering a whole night.
  const learn = guide['how-to-play-bingo/'];
  assert(learn.includes('Nervous about the unwritten rules?'), 'the class speaks to a nervous first-timer');
  for (const term of ['Buying in', 'Paper', 'Electronic bingo', 'Early birds', 'Regular games', 'Specials', 'Progressive jackpot', 'Coverall, or blackout',
    'How the numbers are called', 'How to claim a win', 'When prizes are split', 'What to bring', 'The unwritten rules', 'Shout “Bingo!”', 'What changes from state to state', 'how pull tabs work'])
    assert(learn.includes(term) || learn.toLowerCase().includes(term.toLowerCase()), term);
  // The old address forwards: a 301 on findbingo.org and a small page that points to the new one, out of search and without ads.
  const moved = fs.readFileSync(path.join(root, 'bingo-site/findbingo/learn/index.html'), 'utf8');
  assert.equal(moved, fs.readFileSync(path.join(site, 'learn/index.html'), 'utf8'), 'the forwarding page has no AdSense on either copy');
  assert(moved.includes('<meta name="robots" content="noindex,follow">') && moved.includes('<link rel="canonical" href="https://www.findbingo.org/how-to-play-bingo/">')
    && moved.includes('url=../how-to-play-bingo/') && moved.includes('href="../how-to-play-bingo/"'), 'learn/ forwards to how-to-play-bingo/');
  assert(!sitemap.includes('/learn/'), 'the old address leaves the sitemap');
  // Bingo terms: A to Z, each word with its own address, every "see" pointing to a word on the page.
  {
    const d = scratch(guide['bingo-terms/']);
    const words = [...d.querySelectorAll('.info dl dt')].map(dt => dt.textContent);
    assert.deepEqual(words, [...words].sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : 1), 'the glossary is A to Z');
    for (const w of ['Coverall', 'Dauber', 'Early birds', 'Flashboard', 'Pack', 'Progressive jackpot', 'Pull tab', 'Sleeper', 'Split']) assert(words.includes(w), 'glossary: ' + w);
    for (const dt of d.querySelectorAll('.info dl dt')) assert(dt.id.startsWith('term-'), dt.textContent + ' has its own address');
    for (const a of d.querySelectorAll('.alpha a')) assert(d.getElementById(a.getAttribute('href').slice(1)).tagName === 'H2', 'letter links open their letter');
  }
  // Pull tabs: what they are, and that whether a hall sells them depends on the state; age examples are sourced.
  {
    const d = scratch(guide['pull-tabs/']);
    assert.match(d.getElementById('where').textContent, /depends on the state/);
    const age = d.getElementById('age').nextElementSibling;
    for (const c of ['VA', 'MN']) assert(age.querySelector(`a[href="${states.find(s => s.code === c).age.sources[0].url}"]`), 'pull tab age example cites ' + c);
    assert(age.textContent.includes('checked November 27, 2026'));
    assert(d.querySelector('figure.ptab svg[role="img"] title') && d.querySelector('figure.ptab svg desc').textContent.length > 40, 'the ticket picture is named and described');
  }
  // Bingo age by state: only states with listings here, each age from the state's own law, rule or regulator, with the source.
  {
    const d = scratch(guide['bingo-age-by-state/']);
    const withAge = states.filter(s => s.age);
    const rows = [...d.querySelectorAll('table.ages tbody tr')];
    assert.deepEqual(rows.map(r => r.querySelector('th').textContent), withAge.map(s => s.name), 'one row for each state with a confirmed age, A to Z');
    assert(d.querySelector('table.ages caption').textContent.endsWith('checked November 27, 2026'));
    withAge.forEach((s, i) => {
      assert(LISTED.includes(s.coverage), s.name + ' has games on Find Bingo');
      assert.equal(rows[i].querySelector('th').id, SLUGS[s.code], s.name + ': each row has its own address');
      assert(rows[i].querySelector('td').textContent.startsWith(s.age.rule) && /^(16|18) and older/.test(s.age.rule), s.name + ': the rule, in plain words');
      assert.deepEqual([...rows[i].querySelectorAll('.src a')].map(a => a.getAttribute('href')), s.age.sources.map(x => x.url), s.name + ': every source is linked');
      assert(s.age.sources.every(x => x.url.startsWith('https://') && x.reviewed_on === '2026-11-27' && x.label && x.scope), s.name + ': sources are https and checked November 27, 2026');
    });
    const unconfirmed = states.filter(s => LISTED.includes(s.coverage) && !s.age);
    for (const s of unconfirmed) assert(d.getElementById('unconfirmed').nextElementSibling.textContent.includes(s.name), s.name + ' is named as not yet confirmed');
    assert(!states.some(s => s.age && !LISTED.includes(s.coverage)), 'no age for a state without games here');
  }
  // Every state page carries a line for first-timers, with the state's own age when it is confirmed.
  for (const s of states) {
    const t = s.code === 'OH' ? fs.readFileSync(path.join(root, 'bingo-site/findbingo/ohio/index.html'), 'utf8') : fs.readFileSync(path.join(site, SLUGS[s.code], 'index.html'), 'utf8');
    const line = (t.match(/<p class="newbie">.*?<\/p>/) || [''])[0];
    assert(line.includes('New to hall bingo?') && line.includes('href="../how-to-play-bingo/"') && line.includes('href="../bingo-terms/"'), s.name + ': a line for first-timers');
    assert.equal(line.includes(`href="../bingo-age-by-state/#${SLUGS[s.code]}"`), Boolean(s.age), s.name + ': links its age when it is confirmed');
  }
  // The other entry pages speak to who lands there too: halls trying to fill seats, a charity, suppliers, the Ohio player.
  const lead = f => new JSDOM(fs.readFileSync(path.join(root, f), 'utf8')).window.document;
  const halls = lead('findbingo-site/halls/index.html'), adv = lead('findbingo-site/advertise/index.html');
  assert.match(halls.querySelector('header .lead').textContent, /trying to fill seats on bingo night/);
  assert.match(halls.getElementById('partners').nextElementSibling.textContent, /^Run a charity hoping bingo can help\?/);
  assert(halls.getElementById('suppliers'), 'suppliers and distributors have their own place on the halls page');
  assert.match(adv.querySelector('header .lead').textContent, /^Trying to fill seats on bingo night/);
  const landing = JSON.parse(fs.readFileSync(path.join(root, 'data/findbingo-landing.json'), 'utf8')).states;
  const ohio = lead('bingo-site/findbingo/ohio/index.html');
  assert.equal(ohio.title, landing.OH.title);
  assert.equal(ohio.querySelector('header .lead').textContent, landing.OH.welcome);
  assert.equal(ohio.querySelector('meta[name=description]').content, landing.OH.description);
  const titles = ['', ...Object.keys(GUIDES), 'about/', 'privacy/', 'terms/', 'advertise/', 'halls/'].map(p => lead('findbingo-site/' + p + 'index.html').title);
  assert.equal(new Set([...titles, ...Object.values(landing).map(e => e.title)]).size, titles.length + 51, 'every entry page has its own title');
  for (const f of ['findbingo-site/index.html', 'findbingo-site/michigan/index.html', 'findbingo-site/texas/houston/index.html', 'findbingo-site/privacy/index.html', 'bingo-site/findbingo/ohio/index.html'])
    assert(fs.readFileSync(path.join(root, f), 'utf8').includes('how-to-play-bingo/">How to play bingo</a>'), f + ' links the guides');
}

// Visual pass (November 20, 2026): dark mode, small icons beside words, a "Today" tag on weekly games. No counts anywhere.
{
  // WCAG contrast of the color tokens, light and dark: text pairs need 4.5:1.
  const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];
  const vars = block => Object.fromEntries([...block.matchAll(/--([a-z]+):(#[0-9a-f]{3,6})/gi)].map(m => [m[1], m[2]]));
  const light = vars(css.match(/:root\{--navy[^}]*\}/)[0]);
  const dark = {...light, ...vars(css.match(/:root\{color-scheme:dark;[^}]*\}/)[0])};
  const lum = hex => { const n = hex.length === 4 ? hex.slice(1).split('').map(c => c + c).join('') : hex.slice(1);
    const [r, g, b] = [0, 2, 4].map(i => parseInt(n.slice(i, i + 2), 16) / 255).map(c => c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
  for (const [mode, c] of [['light', light], ['dark', dark]]) {
    for (const [fg, bg] of [['ink', 'paper'], ['ink', 'card'], ['ink', 'today'], ['head', 'card'], ['head', 'paper'], ['accent', 'card'], ['accent', 'paper'], ['link', 'card'], ['link', 'paper']])
      assert(ratio(c[fg], c[bg]) >= 4.5, `${mode}: ${fg} on ${bg} is ${ratio(c[fg], c[bg]).toFixed(2)}:1`);
    for (const bg of ['green', 'navy']) assert(ratio('#ffffff', c[bg]) >= 4.5, `${mode}: white on ${bg}`);
    assert(ratio(c.gold, c.paper) >= 3, `${mode}: focus and today marks stand out`);
  }
  assert(ratio('#1d1606', dark.gold) >= 4.5, 'dark: Today tag text');
  assert(/@media screen and \(prefers-color-scheme:dark\)/.test(css) && /@media\(prefers-reduced-motion:reduce\)/.test(css), 'dark mode and reduced motion');
  assert(/behavior:window\.matchMedia\?\.\('\(prefers-reduced-motion: reduce\)'\)\?\.matches\?'auto':'smooth'/.test(html), 'no smooth scrolling for people who ask for less motion');
  // Every Find Bingo page: dark mode, page counter, icons hidden from screen readers and drawn from symbols on the same page,
  // and no counts of halls, games, places or counties in the page's own words.
  for (const file of allPages) {
    freeScratch(); await new Promise(r => setImmediate(r));
    const rel = path.relative(findbingo, file), text = fs.readFileSync(file, 'utf8');
    assert(/goatcounter|assets\/analytics\.js/.test(text), rel + ': counts page views');
    if (rel.startsWith('ohio' + path.sep)) continue;  // the Ohio finder is built by bingo_site.py with its own styles
    assert(text.includes('prefers-color-scheme:dark'), rel + ': dark mode');
    const d = scratch(text);
    for (const svg of d.querySelectorAll('svg.ic')) {
      assert.equal(svg.getAttribute('aria-hidden'), 'true', rel + ': icons are hidden from screen readers');
      const id = svg.querySelector('use').getAttribute('href');
      assert(d.querySelector(id), rel + ': icon ' + id + ' is on the page');
      assert(svg.parentElement.textContent.trim(), rel + ': every icon sits beside words');
    }
    const plain = d.body.cloneNode(true);
    // Hall names can hold numbers ("777 Bingo Hall"): leave out names on listing cards and in a town's day-by-day list.
    for (const e of plain.querySelectorAll('script, article h3, .by-day li a, .org, .small, .address')) e.remove();
    assert(!countWords.test(plain.textContent), rel + ': no counts on the site');
  }
  // The finder (Monday 10 a.m.): today's weekly games carry a "Today" tag in words, not color alone; monthly patterns never do.
  const p = await open('?zip=48066&radius=10');
  const today = [...p.d.querySelectorAll('#results .sessions li.today')];
  assert(today.length && today.every(li => /^Monday,/.test(li.textContent) && li.querySelector('.today-tag').textContent === 'Today'));
  assert.match(p.d.querySelector('#mi-rosemack-bingo-roseville .sessions li.today').textContent, /Monday, 4:30 to 10 p\.m\. · Gesu School Today$/);
  assert(!p.d.querySelector('#mi-rosemack-bingo-roseville .sessions li:not(.today) .today-tag'));
  const buttons = [...p.d.querySelectorAll('#mi-rosemack-bingo-roseville .big-actions a')].map(a => a.textContent);
  assert(/^(Call \d{3}-\d{3}-\d{4}|Look up phone number ↗)$/.test(buttons[0]) && buttons[1] === 'Directions ↗', 'icons add no words to the buttons');
  const fl = await open('?zip=32208&radius=10');
  assert(!fl.d.querySelector('#fl-carvill-senior-center-jacksonville .today-tag'), 'a monthly calendar never says Today');
  // State pages: the same tag, added by a few lines of script on the visitor's own weekday.
  const runAt = (file, when) => new JSDOM(fs.readFileSync(path.join(site, file), 'utf8'), {runScripts: 'dangerously', beforeParse(w) {
    const RealDate = w.Date;
    w.Date = class extends RealDate { constructor(...a) { super(...(a.length ? a : when)) } static now() { return new RealDate(...when).getTime() } };
  }}).window.document;
  const miMon = runAt('michigan/index.html', [2026, 10, 16, 10, 0]);
  const miToday = [...miMon.querySelectorAll('#listings li.today')];
  assert(miToday.length && miToday.every(li => li.dataset.day === '1' && li.closest('ul').hasAttribute('data-weekly') && li.querySelector('.today-tag').textContent === 'Today'));
  assert(!runAt('florida/index.html', [2026, 10, 16, 10, 0]).querySelector('#fl-carvill-senior-center-jacksonville .today-tag'), 'monthly calendars are not marked');
  assert(!mi.querySelector('.today-tag'), 'without JavaScript the page is unchanged');
}

// Shop: bingo gear and gifts (draft, November 25, 2026). Plain store links, a commission disclosure, no prices,
// ratings or donation-for-purchase wording, sponsored marking once tagged, and in every footer and the sitemap.
{
  const shopHtml = fs.readFileSync(path.join(site, 'shop/index.html'), 'utf8');
  assert.equal(shopHtml, unAd(fs.readFileSync(path.join(root, 'bingo-site/findbingo/shop/index.html'), 'utf8')), 'shop copies match');
  const shop = new JSDOM(shopHtml).window.document;
  const text = shop.querySelector('main').textContent;
  assert.equal(shop.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/shop/');
  assert(text.includes('Find Bingo may earn a small commission. It costs you nothing extra.'), 'the shop discloses commissions');
  assert(!/\$\s?\d|\bstars?\b|\d[\d,]* (ratings|reviews)/i.test(text), 'no prices or star ratings on the shop page');
  assert(!/donat/i.test(text), 'buying is never tied to a donation');
  const buy = [...shop.querySelectorAll('.picks a')];
  assert(buy.length > 0);
  for (const a of buy) {
    assert.match(a.href, /^https:\/\/www\.(amazon|walmart|etsy)\.com\//, a.href);
    // Plain links until an affiliate tag is set; a tagged link is marked sponsored.
    assert.equal(a.getAttribute('rel'), /[?&]tag=/.test(a.href) ? 'sponsored noopener' : 'noopener', a.href);
    assert(a.querySelector('.vh') && /opens a new tab/.test(a.textContent), 'new-tab links say so');
  }
  for (const svg of shop.querySelectorAll('main svg')) assert.equal(svg.getAttribute('aria-hidden'), 'true', 'shop icons are decoration');
  assert(shop.querySelectorAll('.shop-group h2').length === shop.querySelectorAll('.shop-jump a').length, 'every section has a jump link');
  assert(text.includes('must come from a licensed distributor'), 'halls are pointed to their state rules for game supplies');
  assert(sitemap.includes('<loc>https://www.findbingo.org/shop/</loc>'), 'the shop is in the sitemap');
  assert(home.querySelector('.chooser a[href="shop/"]') && home.querySelector('footer a[href="shop/"]'), 'the home page links the shop');
}

// Day pages (findbingo.org/texas/monday/) share the state folders with the town pages: a folder named for a weekday is a
// day page, never a town (the builder refuses a town that would take a weekday's address).
const WEEKDAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const DAY_SLUGS = WEEKDAY_NAMES.map(n => n.toLowerCase());
const DAY_ORDER = [1, 2, 3, 4, 5, 6, 0].map(d => DAY_SLUGS[d]);  // Monday first, as the pages list them
const dayPagesOf = dir => DAY_ORDER.filter(x => fs.existsSync(path.join(dir, x, 'index.html')));
const townSlug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

// Town pages (owner direction, November 26, 2026): a town with at least three listings gets its own page, linked
// from its state page and listed in the sitemap, with its games day by day and Event markup for weekly games.
{
  const sitemapText = fs.readFileSync(path.join(root, 'bingo-site/findbingo/sitemap.xml'), 'utf8');
  const townDirs = [];
  for (const s of states) {
    const dir = path.join(site, SLUGS[s.code]);
    if (!fs.existsSync(dir)) continue;
    for (const t of fs.readdirSync(dir)) if (!DAY_SLUGS.includes(t) && fs.existsSync(path.join(dir, t, 'index.html'))) townDirs.push([s, t]);
  }
  assert(townDirs.length >= 20, 'town pages are built');
  const COUNT = /\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b/i;
  let marked = 0;
  for (const [s, t] of townDirs) {
    freeScratch(); await new Promise(r => setImmediate(r));
    const file = path.join(site, SLUGS[s.code], t, 'index.html'), text = fs.readFileSync(file, 'utf8');
    assert.equal(unAd(fs.readFileSync(path.join(root, 'bingo-site/findbingo', SLUGS[s.code], t, 'index.html'), 'utf8')), text, 'mirror copy of ' + t);
    const url = `https://www.findbingo.org/${SLUGS[s.code]}/${t}/`;
    assert(sitemapText.includes(`<loc>${url}</loc>`), 'town page in the sitemap: ' + url);
    const doc = scratch(text);
    assert.equal(doc.querySelector('link[rel=canonical]').href, url);
    const title = doc.title, h1 = doc.querySelector('h1').textContent, lead = doc.querySelector('header .lead').textContent;
    const desc = doc.querySelector('meta[name=description]').content;
    assert(title.startsWith('Bingo in ') && title.endsWith(' | FindBingo.org') && title.length <= 70, title);
    assert(desc.length <= 165 && h1.startsWith('Bingo in '), t);
    assert(!COUNT.test(title + desc + h1 + lead), 'no counts in the words written for ' + t);
    assert(!/\.\./.test(lead), 'no doubled period: ' + t);
    assert(doc.querySelectorAll('#listings article').length >= 3, 'a town page has at least three listings: ' + t);
    assert(doc.querySelector('.by-day h3'), 'games day by day: ' + t);
    assert(doc.querySelector(`header a[href="../"]`) && doc.querySelector('a[href="../../"]'), 'links up to the state and the finder: ' + t);
    assert(/gc\.zgo\.at|goatcounter/.test(text), 'visit counter on ' + t);
    const statePage = scratch(fs.readFileSync(path.join(site, SLUGS[s.code], 'index.html'), 'utf8'));
    assert(statePage.querySelector(`nav.towns a[href="${t}/"]`), 'the state page links ' + t);
    assert.deepEqual([...doc.querySelectorAll('nav.weekdays a')].map(a => a.getAttribute('href')), dayPagesOf(path.join(site, SLUGS[s.code])).map(x => `../${x}/`),
      'a town page links its state\'s day pages, and only those: ' + t);
    const ld = doc.getElementById('games-ld');
    if (!ld) continue;
    const events = JSON.parse(ld.textContent);
    assert(Array.isArray(events) && events.length);
    for (const e of events) {
      marked++;
      assert.equal(e['@type'], 'Event');
      assert(e.name && e.location && e.location.address && e.location.address.postalCode && e.organizer && e.organizer.name, e.name);
      assert(!e.startDate && !e.offers, 'no fixed date or price is written into the page: ' + e.name);
      assert(/^https:\/\/schema\.org\/(Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day$/.test(e.eventSchedule.byDay) && /^\d\d:\d\d:00$/.test(e.eventSchedule.startTime), e.name);
      const id = e.url.split('#')[1];
      assert(doc.getElementById(id), 'event points at a listing on the page: ' + id);
    }
  }
  freeScratch(); await new Promise(r => setImmediate(r));
  assert(marked > 100, 'weekly games carry Event markup');
  // The date script fills the next date for each weekly game, local to the hall, on or after today.
  const sa = fs.readFileSync(path.join(site, 'texas/san-antonio/index.html'), 'utf8');
  const dom = new JSDOM(sa, {runScripts: 'dangerously'});
  const filled = JSON.parse(dom.window.document.getElementById('games-ld').textContent);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  for (const e of filled) {
    assert(/^\d{4}-\d\d-\d\dT\d\d:\d\d:00$/.test(e.startDate), e.startDate);
    const d = new Date(e.startDate.slice(0, 10) + 'T00:00:00');
    assert(d >= today && (d - today) / 864e5 < 7, 'the next date, within a week: ' + e.startDate);
    assert.equal(names[d.getDay()], e.eventSchedule.byDay.split('/').pop(), 'the date falls on the listed weekday');
    if (e.endDate) assert(e.endDate > e.startDate, 'ends after it starts: ' + e.name);
  }
}

// Ohio town pages (owner direction, November 27, 2026): built from the Ohio finder's own records into its folder
// (findbingo.org/ohio/columbus/), linked from the finder's "Bingo by town" list and back, listed in the sitemap, with
// the same layout and Event markup rules as the other town pages. Only bingo-site/findbingo/ has the ohio/ folder.
{
  const ohioDir = path.join(root, 'bingo-site/findbingo/ohio');
  const sitemapText = fs.readFileSync(path.join(root, 'bingo-site/findbingo/sitemap.xml'), 'utf8');
  const finderHtml = fs.readFileSync(path.join(ohioDir, 'index.html'), 'utf8');
  const finder = scratch(finderHtml);
  const ids = new Set(JSON.parse(/const BINGO=(\[.*?\]);/s.exec(finderHtml)[1]).map(r => r.id));
  const towns = fs.readdirSync(ohioDir).filter(t => !DAY_SLUGS.includes(t) && fs.existsSync(path.join(ohioDir, t, 'index.html')));
  assert(towns.length >= 20, 'Ohio town pages are built');
  const ohioDays = dayPagesOf(ohioDir);
  assert.deepEqual([...finder.querySelectorAll('nav.towns a')].map(a => a.getAttribute('href')).sort(), towns.map(t => t + '/').sort(), 'the Ohio finder links every town page');
  assert(!/\d/.test(finder.querySelector('nav.towns').textContent), 'no counts in the town list');
  assert(!fs.readFileSync(path.join(root, 'bingo.html'), 'utf8').includes('class="towns"'), 'the guide copy of the finder has no town list');
  // "Bingo by day" on the finder: plain links to the day pages; the finder's own "Which day?" filter stays as it was.
  assert.deepEqual([...finder.querySelectorAll('nav.weekdays a')].map(a => a.getAttribute('href')), ohioDays.map(x => x + '/'), 'the Ohio finder links every day page');
  assert(finder.querySelector('select#bingo-day') && finder.querySelector('nav.weekdays').compareDocumentPosition(finder.querySelector('nav.towns')) & 4, 'day links sit beside the town list');
  assert(!fs.readFileSync(path.join(root, 'bingo.html'), 'utf8').includes('class="weekdays"'), 'the guide copy of the finder has no day links');
  const COUNT = /\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b/i;
  let marked = 0;
  for (const t of towns) {
    freeScratch(); await new Promise(r => setImmediate(r));
    const text = fs.readFileSync(path.join(ohioDir, t, 'index.html'), 'utf8');
    assert(!fs.existsSync(path.join(site, 'ohio', t)), 'Ohio town pages are not copied into findbingo-site: ' + t);
    const url = `https://www.findbingo.org/ohio/${t}/`;
    assert(sitemapText.includes(`<loc>${url}</loc>`), 'Ohio town page in the sitemap: ' + url);
    const doc = scratch(text);
    assert.equal(doc.querySelector('link[rel=canonical]').href, url);
    const title = doc.title, h1 = doc.querySelector('h1').textContent, lead = doc.querySelector('header .lead').textContent;
    const desc = doc.querySelector('meta[name=description]').content;
    assert(title.startsWith('Bingo in ') && title.includes(', OH') && title.endsWith(' | FindBingo.org') && title.length <= 70, title);
    assert(desc.length <= 165 && h1.startsWith('Bingo in ') && h1.endsWith(', Ohio'), t);
    assert(!COUNT.test(title + desc + h1 + lead), 'no counts in the words written for ' + t);
    const plain = doc.body.cloneNode(true);
    for (const e of plain.querySelectorAll('script, article, .by-day li a')) e.remove();
    assert(!COUNT.test(plain.textContent), 'no counts on the Ohio town page outside the listings: ' + t);
    const cards = [...doc.querySelectorAll('#listings article')];
    assert(cards.length >= 3, 'an Ohio town page has at least three listings: ' + t);
    for (const a of cards) {
      assert(ids.has(a.id), 'every listing is an Ohio finder record: ' + a.id);
      assert(a.querySelector(`a[href="../#${a.id}"]`), 'every listing links to its card on the Ohio finder: ' + a.id);
    }
    assert(doc.querySelector('.by-day h3'), 'games day by day: ' + t);
    assert(doc.querySelector('header a[href="../"]') && doc.querySelector('header a[href="../../"]'), 'links up to the Ohio finder and Find Bingo: ' + t);
    assert.equal(doc.querySelector('form.zip-box').getAttribute('action'), '../', 'the ZIP box searches the Ohio finder: ' + t);
    assert(doc.querySelector('#run-a-game a[href="../#submit-details"]') && doc.querySelector('#run-a-game a[href="https://www.ohiobingo.org/claim.html"]'), 'halls can update or claim a listing: ' + t);
    assert(/Every game is listed free, for every hall\./.test(doc.getElementById('run-a-game').textContent), t);
    for (const a of doc.querySelectorAll('nav.towns a')) assert(towns.includes(a.getAttribute('href').replace(/^\.\.\/|\/$/g, '')), 'links another Ohio town page: ' + a.getAttribute('href'));
    assert.deepEqual([...doc.querySelectorAll('nav.weekdays a')].map(a => a.getAttribute('href')), ohioDays.map(x => `../${x}/`), 'an Ohio town page links the Ohio day pages: ' + t);
    assert(/gc\.zgo\.at|goatcounter/.test(text), 'visit counter on ' + t);
    const ld = doc.getElementById('games-ld');
    if (!ld) continue;
    for (const e of JSON.parse(ld.textContent)) {
      marked++;
      assert.equal(e['@type'], 'Event');
      assert(e.name && e.location.address.postalCode && e.location.address.addressRegion === 'OH' && e.organizer.name, e.name);
      assert(!e.startDate && !e.offers, 'no fixed date or price is written into the page: ' + e.name);
      assert(/^https:\/\/schema\.org\/(Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day$/.test(e.eventSchedule.byDay) && /^\d\d:\d\d:00$/.test(e.eventSchedule.startTime), e.name);
      const card = doc.getElementById(e.url.split('#')[1]);
      assert(card && !card.querySelector('.badge.muted'), 'Event markup only for a listing with posted times: ' + e.name);
    }
  }
  freeScratch(); await new Promise(r => setImmediate(r));
  assert(marked > 10, 'weekly Ohio games with a posted start time carry Event markup');
}

// Day pages (owner direction, November 27, 2026): findbingo.org/<state>/<weekday>/ lists every game that runs that weekday in
// the state, town by town (A to Z), earliest start first, for each weekday with at least three listings. Linked from the
// state page (for Ohio, the Ohio finder), every town page and the other day pages; in the sitemap; no counts; the same cards
// as the town pages, showing that day's games; Event markup only for that day's weekly games. Ohio's day pages are built
// from the Ohio finder's records, list games with a posted schedule, and exist only in bingo-site/findbingo/ohio/.
{
  const fbDir = path.join(root, 'bingo-site/findbingo');
  const sitemapText = fs.readFileSync(path.join(fbDir, 'sitemap.xml'), 'utf8');
  const COUNT = /\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b/i;
  const byId = new Map(data.venues.map(v => [v.id, v]));
  const ohioIds = new Set(JSON.parse(/const BINGO=(\[.*?\]);/s.exec(fs.readFileSync(path.join(fbDir, 'ohio/index.html'), 'utf8'))[1]).map(r => r.id));
  const firstStart = (v, d) => v.sessions.filter(x => x.day === d && x.start).map(x => x.start).sort()[0] || '99:99';
  let pages = 0, marked = 0;
  for (const s of states) {
    const slug = SLUGS[s.code], ohio = s.code === 'OH', have = dayPagesOf(path.join(fbDir, slug));
    if (!ohio) {
      const want = DAY_ORDER.filter(x => data.venues.filter(v => v.state === s.code && v.sessions.some(y => y.day === DAY_SLUGS.indexOf(x))).length >= 3);
      assert.deepEqual(have, want, s.name + ': a day page for each weekday with at least three listings, and no other');
      assert.deepEqual(dayPagesOf(path.join(site, slug)), have, s.name + ': findbingo-site has the same day pages');
    } else {
      assert(!fs.existsSync(path.join(site, 'ohio')), 'Ohio day pages are not copied into findbingo-site');
    }
    if (!have.length) continue;
    freeScratch(); await new Promise(r => setImmediate(r));
    const statePage = scratch(fs.readFileSync(path.join(fbDir, slug, 'index.html'), 'utf8'));
    assert.deepEqual([...statePage.querySelectorAll('nav.weekdays a')].map(a => a.getAttribute('href')), have.map(x => x + '/'), s.name + ': the state page links its day pages');
    assert(!/\d/.test(statePage.querySelector('nav.weekdays').textContent), s.name + ': no counts in the day links');
    for (const x of have) {
      freeScratch(); await new Promise(r => setImmediate(r));
      pages++;
      const d = DAY_SLUGS.indexOf(x), day = WEEKDAY_NAMES[d], rel = path.join(slug, x, 'index.html');
      const raw = fs.readFileSync(path.join(fbDir, rel), 'utf8'), text = unAd(raw);  // findbingo.org's copy loads AdSense once
      if (!ohio) assert.equal(text, fs.readFileSync(path.join(site, rel), 'utf8'), 'mirror copy of ' + rel);
      const url = `https://www.findbingo.org/${slug}/${x}/`;
      assert(sitemapText.includes(`<loc>${url}</loc>`), 'day page in the sitemap: ' + url);
      const doc = scratch(text);
      assert.equal(doc.querySelector('link[rel=canonical]').href, url);
      const title = doc.title, h1 = doc.querySelector('h1').textContent, lead = doc.querySelector('header .lead').textContent;
      const desc = doc.querySelector('meta[name=description]').content;
      assert.equal(h1, `${day} bingo in ${s.name}`);
      assert(title.startsWith(h1) && title.endsWith(' | Find Bingo') && title.length <= 70, title);
      assert(desc.length <= 165 && desc.startsWith(h1), desc);
      assert(!COUNT.test(title + desc + h1 + lead), 'no counts in the words written for ' + rel);
      const plain = doc.body.cloneNode(true);
      for (const e of plain.querySelectorAll(ohio ? 'script, article' : 'script, article h3, .org, .small, .address')) e.remove();
      assert(!COUNT.test(plain.textContent), 'no counts on ' + rel);
      // Every card shows this day's games only, and outside Ohio the page holds exactly the listings with a game that day.
      const cards = [...doc.querySelectorAll('#listings article')];
      assert(cards.length >= 3, 'a day page has at least three listings: ' + rel);
      for (const a of cards) {
        const lis = [...a.querySelectorAll('ul.sessions li')];
        assert(lis.length && lis.every(li => li.textContent.startsWith(day)), 'the card shows the day\'s games: ' + a.id);
        if (ohio) {
          assert(ohioIds.has(a.id) && a.querySelector(`a[href="../#${a.id}"]`), 'an Ohio finder record, linked to its card on the finder: ' + a.id);
          assert(!a.querySelector('.badge.muted'), 'Ohio day pages list games with a posted schedule only: ' + a.id);
        }
      }
      if (!ohio) {
        const want = data.venues.filter(v => v.state === s.code && v.sessions.some(y => y.day === d)).map(v => v.id).sort();
        assert.deepEqual(cards.map(a => a.id).sort(), want, 'every ' + day + ' listing in ' + s.name + ', once');
      }
      // Town by town, A to Z, earliest start first; a town with its own page links to it.
      const sections = [...doc.querySelectorAll('#listings > section')];
      const towns = sections.map(sec => sec.querySelector('h2').textContent);
      for (let i = 1; i < towns.length; i++) assert(towns[i - 1].toLowerCase() <= towns[i].toLowerCase(), 'towns A to Z: ' + towns[i - 1] + ', ' + towns[i]);
      if (towns.length > 4) assert.deepEqual([...doc.querySelectorAll('nav.jump a')].map(a => a.getAttribute('href')), sections.map(sec => '#' + sec.querySelector('h2').id), 'jump to your town: ' + rel);
      for (const sec of sections) {
        const t = sec.querySelector('h2').textContent, page = path.join(fbDir, slug, townSlug(t), 'index.html');
        assert.equal(!!sec.querySelector(`p.top a[href="../${townSlug(t)}/"]`), fs.existsSync(page) && !DAY_SLUGS.includes(townSlug(t)), 'the town links its own page where it has one: ' + t);
        if (!ohio) {
          const starts = [...sec.querySelectorAll('article')].map(a => firstStart(byId.get(a.id), d));
          assert.deepEqual(starts, [...starts].sort(), 'earliest start first in ' + t + ' on ' + rel);
        }
      }
      assert.deepEqual([...doc.querySelectorAll('nav.weekdays a')].map(a => [a.getAttribute('href'), a.getAttribute('aria-current')]),
        have.map(y => [`../${y}/`, y === x ? 'page' : null]), 'the day links, with this day marked as the current page: ' + rel);
      assert(doc.querySelector('header a[href="../"]') && doc.querySelector('header a[href="../../"]') && doc.querySelector('main a[href="../"]'), 'links up to the state and Find Bingo: ' + rel);
      const form = doc.querySelector('form.zip-box');
      assert(form.getAttribute('action') === (ohio ? '../' : '../../') && form.querySelector('input[type=hidden][name=day]').value === String(d), 'the ZIP box searches this day: ' + rel);
      assert(/gc\.zgo\.at|goatcounter/.test(text), 'visit counter on ' + rel);
      const ld = doc.getElementById('games-ld');
      if (!ld) continue;
      for (const e of JSON.parse(ld.textContent)) {
        marked++;
        assert.equal(e['@type'], 'Event');
        assert(e.name && e.location.address.addressRegion === s.code && e.organizer.name, e.name);
        assert(!e.startDate && !e.offers, 'no fixed date or price is written into the page: ' + e.name);
        assert.equal(e.eventSchedule.byDay, 'https://schema.org/' + day, 'only this day\'s games carry markup: ' + e.name);
        const [base, id] = e.url.split('#'), card = doc.getElementById(id);
        assert(card && card.tagName === 'ARTICLE' && !card.querySelector('.badge.muted'), 'event points at a listing on the page: ' + id);
        // A game whose town has its own page points there, so it is one event with one address on both pages.
        const town = card.closest('section').querySelector('h2').textContent, townPage = `https://www.findbingo.org/${slug}/${townSlug(town)}/`;
        assert.equal(base, fs.existsSync(path.join(fbDir, slug, townSlug(town), 'index.html')) ? townPage : url, 'event address: ' + e.name);
      }
    }
  }
  freeScratch(); await new Promise(r => setImmediate(r));
  assert(pages >= 40 && fs.existsSync(path.join(fbDir, 'ohio/monday/index.html')) && fs.existsSync(path.join(fbDir, 'texas/friday/index.html')), 'day pages are built');
  assert(marked > 100, 'weekly games on day pages carry Event markup');
  // The date script fills each game's next date on the page's own weekday.
  const dom = new JSDOM(fs.readFileSync(path.join(site, 'michigan/monday/index.html'), 'utf8'), {runScripts: 'dangerously'});
  const today = new Date(); today.setHours(0, 0, 0, 0);
  for (const e of JSON.parse(dom.window.document.getElementById('games-ld').textContent)) {
    const when = new Date(e.startDate.slice(0, 10) + 'T00:00:00');
    assert(when.getDay() === 1 && when >= today && (when - today) / 864e5 < 7, 'the next Monday: ' + e.startDate);
  }
  dom.window.close();
}

console.log('FindBingo.org checks passed.');
})().catch(e => { console.error(e); process.exit(1); });
