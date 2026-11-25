// Checks the guide's and Find Bingo's visuals (scripts/visuals.py, assets/visuals.css, the Find Bingo week chart and steps).
// Every symbol is hidden from screen readers and sits beside words; every chart has a name and its numbers in text;
// every diagram's words are real text; Find Bingo's chart never states a count.
const fs = require('fs'), path = require('path'), assert = require('assert');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..') + '/';
const read = rel => fs.readFileSync(root + rel, 'utf8');

// The sprite: one 24-point symbol per icon, small enough to load once for every page.
const sprite = read('assets/visuals.svg');
const symbols = new Set([...sprite.matchAll(/<symbol id="(v-[a-z-]+)" viewBox="0 0 24 24"/g)].map(m => m[1]));
assert(symbols.size >= 20, 'the sprite has its icons');
assert.equal((sprite.match(/<symbol /g) || []).length, symbols.size, 'every symbol has a 24-point view box and a unique id');
assert(Buffer.byteLength(sprite) < 12000, 'the sprite stays small');
assert(!/<text\b|<image\b|href="http/.test(sprite), 'the sprite is drawing only, with nothing loaded from elsewhere');

const css = read('assets/visuals.css');
assert(css.includes('forced-colors:active') && css.includes('@media print'), 'visuals.css covers Windows high contrast and print');
assert(!/@import|url\(http/.test(css), 'visuals.css loads nothing from another site');

// Every page that draws a guide icon: hidden, unfocusable, a symbol that exists, beside words, and the stylesheet linked.
function walk(dir, out = []) {
  for (const e of fs.readdirSync(root + dir, { withFileTypes: true })) {
    const rel = dir + e.name;
    if (e.isDirectory()) { if (!/^(node_modules|tests|\.git|flyers|research|data)$/.test(e.name)) walk(rel + '/', out); }
    else if (e.name.endsWith('.html')) out.push(rel);
  }
  return out;
}
const pages = walk('');
let using = 0;
const icon = /<svg class="vi" width="24" height="24" aria-hidden="true" focusable="false"><use href="((?:\.\.\/)*)assets\/visuals\.svg#(v-[a-z-]+)"\/><\/svg>/g;
for (const rel of pages) {
  const text = read(rel);
  if (!text.includes('class="vi"')) continue;
  using++;
  const up = '../'.repeat(rel.split('/').length - 1);
  const raw = (text.match(/<svg class="vi"/g) || []).length;
  const ok = [...text.matchAll(icon)];
  assert.equal(ok.length, raw, rel + ': every guide icon is hidden from screen readers and cannot take focus');
  for (const m of ok) {
    assert(symbols.has(m[2]), rel + ': icon ' + m[2] + ' is in the sprite');
    assert.equal(m[1], up, rel + ': the icon points at the sprite from this folder');
  }
  assert(text.includes(`<link rel="stylesheet" href="${up}assets/visuals.css">`), rel + ': links assets/visuals.css');
}
assert(using > 3000, 'county pages, VA pages and the topic pages use the icons (' + using + ')');

// Pages with diagrams and charts, read whole.
const dom = rel => new JSDOM(read(rel)).window.document;
const words = el => el.textContent.replace(/\s+/g, ' ').trim();
const checked = ['bad-paper/index.html', 'bad-paper/boards.html', 'va-pension-aid-attendance.html', 'elder-abuse.html', 'guardianship.html',
  'end-of-life-burial.html', 'family-guide.html', 'es/index.html', 'va-locations/ky/index.html', 'va-locations/oh/index.html', 'counties/oh/morrow-county.html',
  'index.html', 'ak.html', 'dc.html', 'va.html', 'mst.html', 'survivors.html', 'toxic-exposure.html', 'justice.html', 'mobility-rights.html', 'privacy.html',
  'counties/index.html', 'va-locations/index.html', 'packets.html', 'bad-paper/records.html', 'share-ak.html'];
for (const rel of checked) {
  const d = dom(rel);
  const ids = [...d.querySelectorAll('[id]')].map(e => e.id);
  assert.equal(new Set(ids).size, ids.length, rel + ': ids are unique');
  for (const svg of d.querySelectorAll('svg.vi')) {
    // A step's icon sits in a round badge, and a branch's arrow in its own span; the words are beside them.
    const wrap = svg.parentElement.classList;
    const holder = wrap.contains('vz-badge') ? svg.parentElement.parentElement : svg.parentElement;
    assert(words(holder), rel + ': every icon sits beside words');
  }
  for (const fig of d.querySelectorAll('figure.vz')) {
    const cap = fig.querySelector('figcaption');
    assert(cap && fig.getAttribute('aria-labelledby') === cap.id && words(cap), rel + ': each visual is a figure named by its caption');
    assert(words(fig).length > words(cap).length + 20, rel + ': each visual carries its words as text, not only drawing');
  }
  for (const svg of d.querySelectorAll('svg[role="img"]')) {
    const names = svg.getAttribute('aria-labelledby').split(' ').map(id => d.getElementById(id));
    assert(names.length && names.every(n => n && svg.contains(n) && words(n)), rel + ': each chart has a title and description of its own');
    assert(svg.outerHTML.length < 6000, rel + ': each inline chart stays small');
  }
  // A chart's numbers are written on the page too, in a data table.
  for (const chart of d.querySelectorAll('figure.vz-chart, figure.vz-countbars')) {
    const table = chart.querySelector('details.vz-data table');
    assert(table && table.querySelector('caption') && table.querySelectorAll('tbody tr').length >= 2, rel + ': chart data table');
    for (const td of table.querySelectorAll('td')) assert(/\d/.test(td.textContent), rel + ': the table holds the numbers');
  }
  for (const flow of d.querySelectorAll('.vz-flow')) assert.equal(flow.tagName, 'OL', rel + ': steps are an ordered list');
}

// The pension example: the bar is drawn to scale from the page's own numbers.
{
  const d = dom('va-pension-aid-attendance.html');
  const fig = d.querySelector('figure.vz-chart');
  const page = words(d.querySelector('main'));
  assert(page.includes('has a maximum of $29,093') && page.includes('counts $20,000') && page.includes('the pension is $9,093 a year'), 'the example sentence stays');
  const cells = [...fig.querySelectorAll('tbody td')].map(td => Number(td.textContent.replace(/[$,]/g, '')));
  assert.deepEqual(cells, [29093, 20000, 9093], 'the chart data matches the example');
  const counted = Number(fig.querySelector('.vz-seg-counted').getAttribute('width')) + 1;
  assert(Math.abs(counted / 600 - 20000 / 29093) < 0.005, 'the bar is to scale');
  assert(fig.querySelector('pattern'), 'the counted income is hatched, not told apart by color alone');
}
// The bad paper roads and the board questions say what the page says.
{
  const roads = words(dom('bad-paper/index.html').querySelector('figure.vz'));
  assert(roads.includes('This does not change your discharge') && roads.includes('Discharged less than 15 years ago: Discharge Review Board, DD-293'), 'two roads');
  const board = dom('bad-paper/boards.html');
  const fig = words(board.querySelector('figure.vz'));
  assert(fig.includes('general court-martial') && fig.includes('less than 15 years ago') && fig.includes('DD Form 293') && fig.includes('DD Form 149'), 'which board');
  assert(board.querySelector('#which-title').parentElement.querySelector('table'), 'the table of every case stays beside the questions');
}
// VA locations: the chart's counts are the page's own summary.
{
  const d = dom('va-locations/ky/index.html');
  const summary = words(d.querySelector('main > p'));
  for (const tr of d.querySelectorAll('figure.vz-countbars tbody tr')) assert(summary.includes(tr.querySelector('td').textContent + ' '), 'VA count in summary');
  for (const a of d.querySelectorAll('figure.vz-countbars a')) assert(d.getElementById(a.getAttribute('href').slice(1)), 'each row jumps to its section');
}

// Find Bingo: the three steps and the week chart (no counts, ever: docs/FINDBINGO.md).
const COUNT = /\b\d[\d,]* (bingo )?(halls?|venues?|locations?|places?|counties|groups?|games?|listings?|senior centers?)\b/i;
for (const base of ['findbingo-site/', 'bingo-site/findbingo/']) {
  const home = new JSDOM(read(base + 'index.html')).window.document;
  const steps = home.querySelectorAll('.how ol > li');
  assert.equal(steps.length, 3, base + ': three steps');
  for (const li of steps) assert(li.querySelector('svg.ic[aria-hidden="true"]') && words(li.querySelector('strong')), base + ': each step has a hidden icon and words');
  let weeks = 0;
  for (const e of fs.readdirSync(root + base, { withFileTypes: true })) {
    if (!e.isDirectory() || !fs.existsSync(root + base + e.name + '/index.html')) continue;
    const text = read(base + e.name + '/index.html');
    if (!text.includes('class="week"')) continue;
    weeks++;
    const d = new JSDOM(text).window.document;
    const week = d.querySelector('section.week');
    assert(!COUNT.test(words(week)), base + e.name + ': the week chart states no count');
    const table = week.querySelector('table');
    assert(table.querySelector('caption') && table.querySelectorAll('thead th[scope="col"]').length === 7, base + e.name + ': seven days');
    for (const td of table.querySelectorAll('tbody td')) assert(['Yes', 'No'].includes(td.querySelector('.vh').textContent), base + e.name + ': each cell says yes or no in words');
    assert(table.querySelector('td.on .ball'), base + e.name + ': a ball marks a listed time');
    assert(week.compareDocumentPosition(d.querySelector('form.zip-box')) & 2, base + e.name + ': the finder still comes first');
  }
  assert(weeks >= 15, base + ': states with listed game times have the week chart (' + weeks + ')');
  // The bingo class: a sample card, the patterns and bingo night's steps, each with its words in text.
  const learn = new JSDOM(read(base + 'learn/index.html')).window.document;
  const lids = [...learn.querySelectorAll('[id]')].map(e => e.id);
  assert.equal(new Set(lids).size, lids.length, base + 'learn: ids are unique');
  const card = learn.querySelector('figure.bcard');
  const cardSvg = card.querySelector('svg[role="img"]');
  assert(card.getAttribute('aria-labelledby') === card.querySelector('figcaption').id, base + 'learn: the card is a figure named by its caption');
  assert(cardSvg.getAttribute('aria-labelledby').split(' ').every(id => cardSvg.querySelector('#' + id) && words(cardSvg.querySelector('#' + id))), base + 'learn: the card has a title and a description');
  assert(/1 to 15/.test(words(cardSvg.querySelector('desc'))) && cardSvg.outerHTML.length < 6000, base + 'learn: the card describes its columns and stays small');
  assert(card.compareDocumentPosition([...learn.querySelectorAll('p')].find(p => p.textContent.includes('free space'))) & 2, base + 'learn: the card follows the words that explain it');
  const pats = learn.querySelectorAll('figure.patterns li');
  assert(pats.length >= 5, base + 'learn: the common patterns');
  for (const li of pats) assert(li.querySelector('svg[aria-hidden="true"][focusable="false"]') && words(li.querySelector('strong')) && words(li.querySelector('span')), base + 'learn: each pattern is named and explained in words');
  const night = learn.querySelector('ol.night');
  assert(night && night.getAttribute('role') === 'list' && night.children.length === 7, base + 'learn: bingo night keeps its seven numbered steps');
}

// State pages (scripts/state_visuals.py): "<State> at a glance" (a locator map and counts from the data) and "Who to call first".
{
  const registry = JSON.parse(read('states/registry.json'));
  const aps = JSON.parse(read('data/public/adult-protective-services.json')).states;
  for (const s of registry) {
    const rel = s.base ? 'index.html' : s.page;
    const d = dom(rel), html = read(rel), low = s.code.toLowerCase();
    const glance = d.querySelector('figure.vz-glance.vz-local'), call = d.querySelector('figure.vz-call.vz-local');
    assert(glance && call, rel + ': both state figures');
    assert.equal(words(glance.querySelector('figcaption')), s.name + ' at a glance', rel + ': named for its state');
    const map = glance.querySelector('svg.vz-loc[role="img"]');
    assert(map && words(map.querySelector('desc')).includes(s.name + ' is the dark square with a white ring'), rel + ': the map says which square');
    assert.equal(map.querySelectorAll('rect').length, 51, rel + ': 50 states and D.C.');
    assert(words(glance).includes(s.name + ' is the dark square with a ring.'), rel + ': the map is explained in text');
    // VA tiles: the counts are VA's own facility data for this state.
    const va = fs.existsSync(root + 'data/public/va-facilities/' + low + '.json') ? JSON.parse(read('data/public/va-facilities/' + low + '.json')).rows : [];
    for (const a of glance.querySelectorAll('a[href^="va-locations/"]')) {
      const kind = a.getAttribute('href').split('#')[1];
      assert.equal(Number(a.querySelector('.vz-stat-n').textContent), va.filter(r => r.kind === kind).length, rel + ': VA ' + kind + ' count');
    }
    const area = glance.querySelector('a[href="counties/' + low + '/"]');
    assert(area && fs.existsSync(root + 'counties/' + low + '/index.html'), rel + ': the county tile opens its list');
    if (s.code !== 'DC') assert.equal(Number(area.querySelector('.vz-stat-n').textContent), s.counties, rel + ': county count');
    // Who to call first: the state's own APS line, and the rows the page gives elsewhere.
    const callText = words(call);
    for (const w of ['988', '911', '877-424-3838', 'Adult Protective Services']) assert(callText.includes(w), rel + ': who to call names ' + w);
    const phone = (aps[s.code].phones[0] || {}).number;
    if (phone) assert(callText.includes(phone) && html.includes('id="care-aps"') && words(d.getElementById('care-aps')).includes(phone), rel + ': the APS phone matches the card');
    for (const a of call.querySelectorAll('a.vz-who')) {
      const href = a.getAttribute('href');
      if (href.startsWith('#')) assert(d.getElementById(href.slice(1)), rel + ': ' + href + ' is on the page');
      else if (!/^(tel:|\?)/.test(href)) assert(fs.existsSync(root + href.split('#')[0] + (href.endsWith('/') ? 'index.html' : '')), rel + ': ' + href);
    }
    // The picker can swap the page to another state; these two figures then hide.
    assert(html.includes(`html[data-edition]:not([data-edition="${s.code}"]) .vz-local{display:none}`), rel + ': hides when another state is shown');
  }
}
// Hub pages: every state on the tile map, each opening its own list.
for (const rel of ['counties/index.html', 'va-locations/index.html']) {
  const d = dom(rel);
  const links = d.querySelectorAll('figure.vz-tilemap .vz-tiles a');
  assert(links.length >= 50, rel + ': the tile map has the states');
  for (const a of links) {
    assert(words(a.querySelector('.vz-vh')), rel + ': each square names its state');
    assert(fs.existsSync(root + path.dirname(rel) + '/' + a.getAttribute('href') + 'index.html'), rel + ': ' + a.getAttribute('href'));
  }
}
// Agent Orange timeline: each bar's dates are the page's own list, and each bar sits inside the scale.
{
  const d = dom('toxic-exposure.html');
  const fig = d.querySelector('figure.vz-tl');
  const rows = fig.querySelectorAll('.vz-tl-rows > li');
  assert.equal(rows.length, fig.querySelectorAll('tbody tr').length, 'one table row per bar');
  for (const li of rows) {
    const bar = li.querySelector('.vz-tl-bar').getAttribute('style').match(/left:([\d.]+)%;width:([\d.]+)%/);
    assert(+bar[1] >= 0 && +bar[1] + +bar[2] <= 100, 'the bar is on the scale');
    assert(/\d{4} to .*\d{4}/.test(words(li.querySelector('.vz-tl-when'))), 'the dates are written beside the bar');
  }
}
// Burial allowances: to scale, with the amounts the table states.
{
  const fig = dom('end-of-life-burial.html').querySelector('figure.vz-money');
  const widths = [...fig.querySelectorAll('.vz-cb-fill')].map(f => parseFloat(f.style.width));
  assert.deepEqual(widths, [100, 51.6, 51.6], 'the bars are to scale: $2,000, $1,032 and $1,032');
  assert(words(fig).includes('Up to $2,000') && words(fig).includes('$1,032'), 'the amounts are written beside the bars');
}
// Find Bingo: every state page shows where the state is, as an image with words (and never a count).
for (const base of ['findbingo-site/', 'bingo-site/findbingo/']) {
  let maps = 0;
  for (const e of fs.readdirSync(root + base, { withFileTypes: true })) {
    const rel = base + e.name + '/index.html';
    if (!e.isDirectory() || !fs.existsSync(root + rel) || !read(rel).includes('id="states-title"')) continue;
    const d = new JSDOM(read(rel)).window.document;
    const fig = d.querySelector('nav.states figure.where');
    if (!fig) continue;
    maps++;
    const svg = fig.querySelector('svg[role="img"]');
    const name = words(d.querySelector('figcaption')).split(' is the dark square')[0];
    assert(svg && words(svg.querySelector('desc')).includes(name + ' is the dark square'), rel + ': the map names its state');
    assert(!COUNT.test(words(fig)), rel + ': no count');
  }
  assert(maps >= 50, base + ': every state page has the map (' + maps + ')');
}
console.log('PASS: visuals (' + using + ' pages with icons), charts with data tables, diagrams in text, state maps and who-to-call diagrams, hub tile maps, Find Bingo steps, week charts, state maps and the bingo class pictures.');
