// FindBingo.org (findbingo-site/): ZIP search across Michigan, Indiana and neighboring states.
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..'), site = path.join(root, 'findbingo-site');
const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(site, 'data.json'), 'utf8'));
const zips = JSON.parse(fs.readFileSync(path.join(site, 'zips.json'), 'utf8'));
const states = JSON.parse(fs.readFileSync(path.join(root, 'data/public/bingo-states.json'), 'utf8'));
assert.equal(data.generated_on, [...states.map(s => s.reviewed_on), ...data.venues.map(v => v.reviewed_on), ...data.licensed.map(r => r.reviewed_on)].sort().pop());
assert(data.venues.length > 150 && data.licensed.length > 300, 'Michigan venues and Indiana licenses are loaded');
for (const r of [...data.venues, ...data.licensed]) assert(zips[r.zip], 'every listing can be placed by ZIP: ' + r.id);
for (const v of data.venues) {
  const order = v.sessions.map(s => (s.day + 6) % 7);
  assert.deepEqual(order, [...order].sort((a, b) => a - b), 'sessions run Monday to Sunday: ' + v.id);
}
assert(zips['49037'], 'Census point fills the ZIP missing from the centroid file');
assert(!zips['10001'] && zips['43334'] && zips['48161'] && zips['46733'] && zips['40601'] && zips['25301'] && zips['15222'] && zips['33701'] && zips['32208']);
assert(!Object.keys(zips).some(z => z.startsWith('340')), 'military ZIP codes are not Florida');

const static_ = new JSDOM(html).window.document;
assert.equal(static_.querySelector('link[rel=canonical]').href, 'https://www.findbingo.org/');
assert.deepEqual([...static_.querySelectorAll('#state-buttons a')].map(a => a.dataset.state), ['MI', 'IN', 'OH', 'KY', 'WV', 'PA', 'FL']);
assert.equal(static_.querySelectorAll('script[src]').length, 0, 'no outside scripts');
assert.deepEqual([...static_.querySelectorAll('#about-states h3')].map(h => h.textContent), states.map(s => s.name));
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
assert.equal(w0.stateOfZip('48161') + w0.stateOfZip('46733') + w0.stateOfZip('43334') + w0.stateOfZip('40601') + w0.stateOfZip('25301') + w0.stateOfZip('15222') + w0.stateOfZip('33701') + w0.stateOfZip('34001') + w0.stateOfZip('10001'), 'MIINOHKYWVPAFL');
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
assert.match(p.groups[0], /^Bingo with game days \(\d+\)$/);
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
assert.equal(p.d.querySelector('#state-OH a.solid').href, 'https://bingo.vethomeguard.org/?zip=43604&radius=25#count');
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
assert.equal(p.count, fl.length + ' Florida bingo places with game days');
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
assert.equal(p.cards[0], 'state-PA');
assert(p.cards.includes('state-OH') && p.cards.includes('state-WV'), 'Pittsburgh is near Ohio and West Virginia');

// ZIP mistakes get plain-language help.
p = await open('?zip=12345');
assert.match(p.status, /We could not find ZIP code 12345 in Michigan, Indiana, Ohio, Kentucky, West Virginia, Pennsylvania or Florida/);
assert.equal(p.cards.length, 0);
p = await open('?zip=4816');
assert.match(p.status, /Please type the five numbers of your ZIP code/);

// State and county browsing.
p = await open('?state=MI&county=Macomb');
const macomb = data.venues.filter(v => v.county === 'Macomb').length;
assert.equal(p.count, macomb + ' Michigan bingo halls with game days in Macomb County');
assert.equal(p.d.getElementById('county-wrap').hidden, false);
assert.equal(p.d.querySelector('#state-buttons a[data-state="MI"]').getAttribute('aria-current'), 'true');
p = await open('?state=IN');
assert.equal(p.count, data.licensed.length + ' Indiana groups licensed for bingo');
p = await open('?state=OH');
assert.deepEqual(p.cards, ['state-OH']);
assert.equal(p.d.querySelector('#state-OH a.solid').href, 'https://bingo.vethomeguard.org/');
p = await open('?state=WV');
assert.deepEqual(p.cards, ['state-WV']);

// Names are shown as text, never as markup.
p = await open('?state=MI&county=Ingham');
assert(p.d.getElementById('results').textContent.includes('F & AM 70'));

console.log('FindBingo.org checks passed.');
})().catch(e => { console.error(e); process.exit(1); });
