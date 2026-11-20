// FindBingo.org featured events ($100, owner direction November 20, 2026): a dated bingo event shown in its own
// labeled box near the searcher, on its state page and on Ohio's finder. It never touches the free listings.
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const {spawnSync} = require('child_process');
const root = path.resolve(__dirname, '..');

assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, 'data/findbingo-events.json'), 'utf8')), [], 'no featured events by default');
const data = JSON.parse(fs.readFileSync(path.join(root, 'findbingo-site/data.json'), 'utf8'));
assert.deepEqual(data.events, [], 'the published lists carry no events by default');
for (const f of ['findbingo-site/michigan/index.html', 'bingo-site/findbingo/ohio/index.html'])
  assert(!fs.readFileSync(path.join(root, f), 'utf8').includes('class="featured-events"'), f + ': no event box without events');

const sample = [
  {id: 'mi-holiday', title: 'Holiday Designer Bag Bingo', host: 'Sample Legion Post 1', address: '100 Main Street', city: 'Monroe', state: 'MI', zip: '48161',
   date: '2026-12-12', start: '18:00', end: '21:00', details: 'Doors open at 5 p.m. Twelve games, prizes and a bake sale.', url: 'https://example.org/bag-bingo', paid_on: '2026-11-20'},
  {id: 'oh-fundraiser', title: 'Fire Department Fundraiser Bingo', host: 'Sample Volunteer Fire Department', address: '1 Firehouse Road', city: 'Marengo', state: 'OH', zip: '43334',
   date: '2026-12-05', start: '18:30', details: 'Early bird at 6 p.m. Proceeds buy new turnout gear.', phone: '419-555-0100', paid_on: '2026-11-20'},
  {id: 'mi-past', title: 'Old Event', host: 'Sample Hall', address: '2 Main Street', city: 'Monroe', state: 'MI', zip: '48161',
   date: '2026-01-10', start: '18:00', details: 'Already happened.', paid_on: '2026-01-01'},
];
function run(code, ...args) {
  const r = spawnSync('python3', ['-c', 'import json,sys;from pathlib import Path;sys.path.insert(0,"scripts");' + code, ...args], {cwd: root, encoding: 'utf8', maxBuffer: 1 << 28});
  return r.status === 0 ? JSON.parse(r.stdout) : {error: r.stderr};
}
const built = run('import findbingo_site as f;out=f.make_findbingo(Path("."),None,json.loads(sys.argv[1]));'
  + 'print(json.dumps({k:out["findbingo-site/"+k] for k in ("index.html","data.json","michigan/index.html","texas/index.html","advertise/index.html")}))', JSON.stringify(sample));
assert(!built.error, built.error);

// The published data carries upcoming events only, without the payment record.
const events = JSON.parse(built['data.json']).events;
assert.deepEqual(events.map(e => e.id), ['oh-fundraiser', 'mi-holiday'], 'upcoming events, soonest first; past events dropped');
assert(events.every(e => !('paid_on' in e)), 'the payment date is not published');

// Michigan's page: one labeled box above the listings, never inside them; links to the advertise page.
const mi = new JSDOM(built['michigan/index.html']).window.document;
const box = mi.querySelector('section.featured-events');
assert(box && mi.querySelectorAll('section.featured-events').length === 1, 'one event box');
assert.equal(box.querySelector('.ad-label').textContent, 'Featured events · paid listings', 'labeled as paid');
assert(!box.closest('#listings, article, .grid') && !mi.querySelector('#listings .featured-events'), 'never inside the listings');
assert(box.compareDocumentPosition(mi.getElementById('listings')) & 4, 'above the listings');
assert.deepEqual([...box.querySelectorAll('article')].map(a => a.dataset.date), ['2026-12-12'], 'only Michigan, only upcoming');
assert(box.textContent.includes('December 12, 2026') && box.textContent.includes('6 to 9 p.m.'));
assert.equal(box.querySelector('a[rel~="sponsored"]').href, 'https://example.org/bag-bingo', 'the event link is marked sponsored');
assert(box.querySelector('a[href="../advertise/#events"]'), 'links to how to feature an event');
assert(!built['texas/index.html'].includes('class="featured-events"'), 'a state with no events has no box');
// Listings are the same with or without events.
const plain = new JSDOM(fs.readFileSync(path.join(root, 'findbingo-site/michigan/index.html'), 'utf8')).window.document;
assert.equal(mi.getElementById('listings').outerHTML, plain.getElementById('listings').outerHTML, 'events never change the listings');
// After the event's day (Eastern time) the card, and then the box, hide.
function at(page, when) {
  return new JSDOM(page, {runScripts: 'dangerously', beforeParse(w) {
    const RealDate = w.Date;
    w.Date = class extends RealDate { constructor(...a) { super(...(a.length ? a : when)) } static now() { return new RealDate(...when).getTime() } };
  }}).window.document.querySelector('section.featured-events');
}
assert(!at(built['michigan/index.html'], [2026, 11, 12, 20, 0]).hidden, 'shown on the day of the event');
assert(at(built['michigan/index.html'], [2026, 11, 13, 9, 0]).hidden, 'hidden the day after');

// The advertise page names the price and the rules.
const adv = new JSDOM(built['advertise/index.html']).window.document;
assert(adv.getElementById('events') && /\$100/.test(adv.getElementById('events').textContent));
assert(/never adds to, removes or reorders the free game listings/.test(adv.body.textContent));
assert(/usually 5 to 10 percent/.test(adv.body.textContent), 'partnership asks for a modest share');

// Ohio's finder shows Ohio events above its results.
const oh = run('import bingo_site as b;page=open("bingo-site/findbingo/ohio/index.html").read();'
  + 'print(json.dumps(b.ohio_events(Path("."),page,json.loads(sys.argv[1]))))', JSON.stringify(sample));
assert(!oh.error, oh.error);
const ohd = new JSDOM(oh).window.document;
assert.deepEqual([...ohd.querySelectorAll('section.featured-events article')].map(a => a.querySelector('h3').textContent), ['Fire Department Fundraiser Bingo']);
assert(ohd.querySelector('section.featured-events').compareDocumentPosition(ohd.getElementById('count')) & 4, 'above the Ohio results');

// The home page's ZIP search: the box appears for searches near the event, outside #results.
(async () => {
  const html = built['index.html'], served = JSON.parse(built['data.json']);
  const zips = JSON.parse(fs.readFileSync(path.join(root, 'findbingo-site/zips.json'), 'utf8'));
  async function open(query) {
    const dom = new JSDOM(html, {url: 'https://www.findbingo.org/' + query, runScripts: 'dangerously', beforeParse(w) {
      const RealDate = w.Date;
      w.Date = class extends RealDate { constructor(...a) { super(...(a.length ? a : [2026, 10, 20, 10, 0])) } static now() { return new RealDate(2026, 10, 20, 10, 0).getTime() } };
      w.HTMLElement.prototype.scrollIntoView = () => {};
      w.fetch = url => Promise.resolve({ok: true, status: 200, json: () => Promise.resolve(JSON.parse(JSON.stringify(String(url).endsWith('data.json') ? served : zips)))});
    }});
    await dom.window.fbReady;
    return dom.window.document;
  }
  let d = await open('?zip=48161&radius=25');
  let near = d.querySelector('#featured section.featured-events');
  assert(near && !d.querySelector('#results .featured-events'), 'home: event box sits outside the results');
  assert.deepEqual([...near.querySelectorAll('h3')].map(h => h.textContent), ['Holiday Designer Bag Bingo'], 'home: only events within the distance');
  assert(near.textContent.includes('near you'));
  d = await open('?zip=90210&radius=25');
  assert.equal(d.getElementById('featured').innerHTML, '', 'home: no box far from any event');
  d = await open('?state=OH');
  assert.deepEqual([...d.querySelectorAll('#featured h3')].map(h => h.textContent), ['Fire Department Fundraiser Bingo'], 'home: a state shows its events');
  console.log('PASS findbingo featured events: labeled box near the searcher, on state pages and Ohio’s finder, never inside or changing the listings, hidden after the day, $100 and partnership terms on the advertise page.');
})().catch(e => { console.error(e); process.exit(1); });
