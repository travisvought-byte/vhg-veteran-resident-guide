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
p = await open('?zip=50309');
assert.equal(p.count, 'No bingo games listed yet within 25 miles of 50309.');
assert(!p.d.getElementById('pending-MI'), 'the Michigan note stays with Michigan searches');
assert.equal(p.cards[0], 'state-IA');
assert.match(p.d.getElementById('state-IA').textContent, /Charitable Gambling/);
assert(p.d.querySelector('#state-IA a[href^="mailto:travis@vethomeguard.org?subject=Bingo%20game%20times%20in%20Iowa"]'));
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
assert.equal(p.cards[0], 'pa-collinsburg-volunteer-fire-company-west-newton', 'Pittsburgh searches lead with the nearest Pennsylvania game');
assert(p.cards.includes('state-PA'), 'and still offer the way to send Pennsylvania game times');
assert(p.cards.includes('state-OH') && p.cards.includes('state-WV'), 'Pittsburgh is near Ohio and West Virginia');

// Pennsylvania, New York, Utah, Kentucky and West Virginia starter lists: organizer-published schedules, each with its own source.
for (const [code, name, min] of [['PA', 'Pennsylvania', 4], ['NY', 'New York', 3], ['UT', 'Utah', 3], ['KY', 'Kentucky', 4], ['WV', 'West Virginia', 6]]) {
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
p = await open('?state=IA');
assert.deepEqual(p.cards, ['state-IA']);
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
  // Hall and group names can hold numbers ("Elks Lodge 1229 Hall B"), so they are left out of this check.
  const plain = d.body.cloneNode(true);
  for (const e of plain.querySelectorAll('#listings article h3, #listings .org, #listings .small, #listings .address')) e.remove();
  assert(!countWords.test(plain.textContent), slug + ': no counts on the site');
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
  assert.equal(fs.readFileSync(path.join(findbingo, f), 'utf8'), fs.readFileSync(path.join(site, f), 'utf8'), f + ' copies match');
const privacy = new JSDOM(fs.readFileSync(path.join(site, 'privacy/index.html'), 'utf8')).window.document;
assert.equal(privacy.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/privacy/');
assert.equal(privacy.querySelector('h1').textContent, 'Privacy');
const privacyText = privacy.querySelector('main').textContent;
for (const words of ['November 19, 2026', 'GoatCounter does not use cookies', 'It does not store the IP address', 'on your own device',
  'The ZIP code is not sent to us or to anyone else to look it up', 'Cloudflare', 'GitHub', 'This site may show ads. Every ad is labeled “Advertisement” and kept apart from the game listings.',
  'We do not sell personal information', 'not directed to children under 13'])
  assert(privacyText.includes(words), 'privacy page says: ' + words);
assert(!/ads (are|run) (now|on this site)/i.test(privacyText), 'the privacy page does not claim ads are running');
for (const href of ['https://adssettings.google.com', 'https://policies.google.com/technologies/ads', 'https://optout.aboutads.info',
  'https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement', '../advertise/'])
  assert(privacy.querySelector(`main a[href="${href}"]`), 'privacy page links ' + href);
assert(privacy.querySelector('main a[href^="mailto:travis@vethomeguard.org"]'), 'privacy questions go to the site’s existing contact address');
// The ZIP search really does run in the browser: the finder fetches only whole files, never a ZIP lookup.
assert(!/fetch\([^)]*zip=/i.test(html) && /getJSON\(/.test(html), 'no ZIP code is sent to a lookup service');
const advertise = new JSDOM(fs.readFileSync(path.join(site, 'advertise/index.html'), 'utf8')).window.document;
const advertiseText = advertise.querySelector('main').textContent;
for (const words of ['Every ad is labeled “Advertisement.”', 'Never inside them', 'Ads never add, remove, change or reorder listings',
  'We review every ad before it runs', 'misleading', 'Ad income supports Veteran Home Guardians'])
  assert(advertiseText.includes(words), 'advertise page says: ' + words);
assert(!/\$\s?\d/.test(advertiseText), 'no prices on the advertise page');
assert(advertise.querySelector('main a[href^="mailto:travis@vethomeguard.org?subject=Advertising%20on%20Find%20Bingo"]'));
assert(sitemap.includes('<loc>https://www.findbingo.org/privacy/</loc>') && sitemap.includes('<loc>https://www.findbingo.org/advertise/</loc>'));
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
  const rel = path.relative(findbingo, file), text = fs.readFileSync(file, 'utf8');
  assert(!noAdsPromise.test(text), rel + ': no promise against ads');
  // Every page with a footer links Privacy and Advertise (the poster is a print-only page with no footer).
  const d = new JSDOM(text).window.document;
  if (!d.querySelector('footer')) { assert.equal(rel, path.join('ohio', 'poster.html'), rel + ' has a footer'); continue; }
  const up = path.dirname(rel) === '.' ? '' : '../';
  assert(d.querySelector(`footer a[href="${up}privacy/"]`) && d.querySelector(`footer a[href="${up}advertise/"]`), rel + ': footer links Privacy and Advertise');
  // With the default (empty) ad list there is no ad markup at all.
  assert(!d.querySelector('.ad-slot, .ad-label, [rel~="sponsored"]') && !text.includes('class="ad-slot'), rel + ': no ad markup when no ad is running');
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

console.log('FindBingo.org checks passed.');
})().catch(e => { console.error(e); process.exit(1); });
