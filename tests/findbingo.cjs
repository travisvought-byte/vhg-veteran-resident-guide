// FindBingo.org (findbingo-site/): ZIP search across Michigan, Indiana and neighboring states.
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..'), site = path.join(root, 'findbingo-site');
const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(site, 'data.json'), 'utf8'));
const zips = JSON.parse(fs.readFileSync(path.join(site, 'zips.json'), 'utf8'));
const states = JSON.parse(fs.readFileSync(path.join(root, 'data/public/bingo-states.json'), 'utf8'));
for (const f of ['index.html', 'data.json', 'zips.json'])  // the Ohio-Bingo mirror carries the same files for Cloudflare Pages
  assert.equal(fs.readFileSync(path.join(root, 'bingo-site/findbingo', f), 'utf8'), fs.readFileSync(path.join(site, f), 'utf8'), 'bingo-site/findbingo/' + f);
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
for (const r of redirects) assert(r.length === 3 && r[0].startsWith('/') && Object.values(SLUGS).some(s => r[1] === '/' + s + '/') && r[2] === '301' && r[0].toLowerCase() !== r[1], r.join(' '));
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
const ready = states.filter(s => s.coverage !== 'pending').map(s => s.code), waiting = states.filter(s => s.coverage === 'pending').map(s => s.code);
assert.deepEqual([...static_.querySelectorAll('#state-buttons > a')].map(a => a.dataset.state), ready);
assert.deepEqual([...static_.querySelectorAll('#state-buttons details.more-states a')].map(a => a.dataset.state), waiting);
for (const c of ['FL', 'IN', 'KY', 'MI', 'NY', 'OH', 'PA', 'UT', 'WV']) assert(ready.includes(c), c + ' keeps its list');
assert.equal(static_.querySelectorAll('script[src]').length, 0, 'no outside scripts');
assert.deepEqual([...static_.querySelectorAll('#about-states h3')].map(h => h.textContent), states.filter(s => s.coverage !== 'pending').map(s => s.name).concat('Every other state'), 'sources are given for researched states; the rest are named together');
assert(static_.querySelector('footer a[href="https://creativecommons.org/licenses/by/3.0/"]'), 'ZIP data attribution');
assert(!/\b\d+ (halls|venues|locations|counties)\b/i.test(static_.querySelector('header').textContent), 'no headline counts');

// Run the page on Monday, November 16, 2026 at 10 a.m. Data requests are answered from this folder.
const sources = JSON.parse(html.match(/const DATA_SOURCES=(\[.*?\]);/)[1]);
assert.deepEqual(sources, ['', 'https://guide.vethomeguard.org/findbingo-site/', 'https://raw.githubusercontent.com/travisvought-byte/vhg-veteran-resident-guide/main/findbingo-site/']);
async function open(query, {served = ['https://www.findbingo.org/'], requests = [], served_data = data} = {}) {
  const dom = new JSDOM(html, {url: 'https://www.findbingo.org/' + query, runScripts: 'dangerously', beforeParse(w) {
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
  assert(!data.venues.some(v => pending.includes(v.county)));
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
assert(p.groups[0].startsWith('Licensed for bingo, game days not posted'));
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
p = await open('?zip=40601');
assert.equal(p.count, 'No bingo games listed yet within 25 miles of 40601.');
assert(!p.d.getElementById('pending-MI'), 'the Michigan note stays with Michigan searches');
assert.equal(p.cards[0], 'state-KY');
assert.match(p.d.getElementById('state-KY').textContent, /Office of Charitable Gaming/);
assert(p.d.querySelector('#state-KY a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Kentucky"]'));
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
assert.equal(p.cards[0], 'pa-collinsburg-volunteer-fire-company-west-newton', 'Pittsburgh searches lead with the nearest Pennsylvania game');
assert(p.cards.includes('state-PA'), 'and still offer the way to send Pennsylvania game times');
assert(p.cards.includes('state-OH') && p.cards.includes('state-WV'), 'Pittsburgh is near Ohio and West Virginia');

// Pennsylvania, New York and Utah starter lists: organizer-published schedules, each with its own source.
for (const [code, name, min] of [['PA', 'Pennsylvania', 4], ['NY', 'New York', 3], ['UT', 'Utah', 3]]) {
  const rows = data.venues.filter(v => v.state === code);
  assert(rows.length >= min && rows.every(v => v.kind && v.source_url && v.schedule_note), name + ' starter list');
  p = await open('?state=' + code);
  assert.equal(p.count, name + ' bingo places with game days');
  assert.equal(p.cards[p.cards.length - 1], 'state-' + code, name + ' ends with the way to send game times');
  for (const v of rows) assert(p.d.querySelector('#' + v.id + ' a[href^="mailto:travis@vethomeguard.org?subject=FindBingo.org%20correction"]'), v.id + ' has a report link');
}
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

// A state we have not researched yet: every ZIP code still works, and the card asks for game times
// without claiming anything about the state.
p = await open('?zip=30303');
assert.equal(p.cards[0], 'state-GA');
assert.match(p.d.getElementById('state-GA').textContent, /We have not built a Georgia bingo list yet/);
assert(p.d.querySelector('#state-GA a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Georgia"]'));
assert(!p.d.querySelector('#state-GA a[target]'), 'no regulator is named for a state we have not researched');
// A researched state without a loaded list names its regulator, and Texas points to the state's own hall finder.
p = await open('?zip=75201');
assert.match(p.d.getElementById('state-TX').textContent, /state runs its own bingo hall finder/);
assert.equal(p.d.querySelector('#state-TX a[target]').href, 'https://www.txbingo.org/');
for (const slug of ['texas', 'missouri', 'massachusetts']) assert(fs.readFileSync(path.join(root, 'bingo-site/findbingo/sitemap.xml'), 'utf8').includes(`<loc>https://www.findbingo.org/${slug}/</loc>`), slug + ' is researched, so it is in the sitemap');
p = await open('?state=AK');
assert.equal(p.count, 'Alaska: no game list yet');
const ga = new JSDOM(fs.readFileSync(path.join(site, 'georgia/index.html'), 'utf8')).window.document;
assert.equal(ga.querySelector('meta[name=robots]').content, 'noindex,follow', 'a page with nothing to say yet stays out of search results');
assert(ga.querySelector('#run-a-game a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Georgia"]'));
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
p = await open('?state=WV');
assert.deepEqual(p.cards, ['state-WV']);

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
for (const s of states) {
  const slug = SLUGS[s.code];
  assert.equal(home.querySelector(`#state-buttons a[data-state="${s.code}"]`).getAttribute('href'), slug + '/', 'state buttons link to the state page');
  assert.equal(sitemap.includes(`<loc>https://www.findbingo.org/${slug}/</loc>`), s.coverage !== 'pending', slug + ' is in the sitemap once it has content');
  if (s.code === 'OH') continue;  // Ohio's page is the Ohio Bingo Finder
  const file = path.join(root, 'bingo-site/findbingo', slug, 'index.html'), text = fs.readFileSync(file, 'utf8');
  assert.equal(text, fs.readFileSync(path.join(site, slug, 'index.html'), 'utf8'), slug + ' copies match');
  const d = new JSDOM(text).window.document;
  assert.equal(d.querySelector('link[rel=canonical]').href, `https://www.findbingo.org/${slug}/`);
  assert(d.title.startsWith(s.name + ' Bingo') && d.title.endsWith('| FindBingo.org'), d.title);
  assert(d.querySelector('meta[name=description]').content.includes(s.name));
  assert.equal(d.querySelector('h1').textContent, 'Bingo in ' + s.name);
  assert.equal(JSON.parse(d.querySelector('script[type="application/ld+json"]').textContent)['@type'], 'BreadcrumbList');
  assert(text.includes("vhg-guide.goatcounter.com/count"), slug + ' counts page views');
  assert.equal(d.querySelectorAll('script[src]').length, 0, 'no outside scripts');
  assert(!countWords.test(d.body.textContent), slug + ': no counts on the site');
  const form = d.querySelector('form.zip-box');
  assert.equal(form.getAttribute('action'), '../');
  assert(form.querySelector('input[name=zip]') && form.querySelector('select[name=radius]'), 'the ZIP search opens the finder');
  assert.equal(d.querySelectorAll('.state-buttons a').length, states.length - 1, 'links to every other state');
  for (const a of d.querySelectorAll('a[href^="../"]')) {
    const target = path.join(root, 'bingo-site/findbingo', slug, a.getAttribute('href'));
    assert(fs.existsSync(target.endsWith('/') ? path.join(target, 'index.html') : target) || fs.existsSync(path.join(target, 'index.html')), a.getAttribute('href'));
  }
  const ids = [...d.querySelectorAll('#listings article')].map(a => a.id);
  const today = data.generated_on;
  const expected = s.coverage === 'licenses' ? data.licensed.filter(r => r.state === s.code && r.license_expires >= today) : data.venues.filter(v => v.state === s.code);
  assert.deepEqual(ids.sort(), expected.map(r => r.id).sort(), slug + ' lists every record');
  if (['none'].includes(s.coverage)) assert(d.querySelector('#listings .empty'));
  for (const c of new Set(expected.map(r => r.county))) assert(d.querySelector(`#listings h2`) && [...d.querySelectorAll('#listings h2')].some(h => h.textContent === c + ' County'), c);
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

console.log('FindBingo.org checks passed.');
})().catch(e => { console.error(e); process.exit(1); });
