// The map beside the lists (assets/map/place-map.js), run in jsdom with a small stand-in for Leaflet:
// pins come only from cards with a known ZIP code point, Find Bingo's group dots carry no numbers, every pin's box offers
// Call, Directions and the full listing, the list gets "Show on the map" buttons, hiding the map is remembered and stops
// loading it, and "Use my location" picks the nearest ZIP code on the device.
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..');
const read = f => fs.readFileSync(path.join(root, f), 'utf8');

function fakeLeaflet(w, log) {
  class MarkerCluster {}
  const layer = () => { const items = []; return {items, clearLayers() { items.length = 0 }, addLayer(m) { items.push(m); return this }, addTo(map) { map.layers.push(this); return this }} };
  w.L = {
    Browser: {mobile: false},
    MarkerCluster,
    map(el, opts) {
      const handlers = {};
      const map = {el, opts, layers: [], views: [], fits: [],
        on(names, fn) { names.split(' ').forEach(n => (handlers[n] = handlers[n] || []).push(fn)); return map },
        fire(n, e) { (handlers[n] || []).forEach(fn => fn(e || {})) },
        setView(at, z) { map.views.push([at, z]); return map }, fitBounds(b, o) { map.fits.push([b, o]); return map },
        addLayer(l) { map.layers.push(l); return map }, invalidateSize() {}, closePopup() { map.closed = true },
        scrollWheelZoom: {on: false, enabled() { return this.on }, enable() { this.on = true }},
        dragging: {on: !opts.dragging === false, enabled() { return this.on }, enable() { this.on = true }}};
      map.dragging.on = opts.dragging;
      log.maps.push(map);
      return map;
    },
    tileLayer(url, opts) { log.tiles.push(url); return {addTo() { return this }} },
    divIcon: o => o,
    layerGroup: layer,
    markerClusterGroup(opts) { const g = layer(); g.opts = opts; g.addLayers = list => list.forEach(m => g.items.push(m)); g.zoomToShowLayer = (m, cb) => cb(); log.clusters.push(g); return g },
    marker(at, opts) {
      const m = {at, options: opts, _icon: w.document.createElement('div'),
        bindPopup(fn) { m.popup = fn; return m }, bindTooltip(t) { m.tooltip = t; return m }, addTo(l) { l.addLayer(m); return m },
        openPopup() { m.opened = m.popup(); return m }};
      m._icon.tabIndex = 0;
      return m;
    },
    latLngBounds: pts => ({pts, pad() { return this }}),
  };
  w.L.markerClusterGroup.bind(w.L);
}

function run(file, url, {storage = {}, before} = {}) {
  const log = {maps: [], tiles: [], clusters: []};
  const dom = new JSDOM(read(file), {url, runScripts: 'dangerously', pretendToBeVisual: true, beforeParse(w) {
    fakeLeaflet(w, log);
    for (const [k, v] of Object.entries(storage)) w.localStorage.setItem(k, v);
    w.HTMLElement.prototype.scrollIntoView = () => {};
    w.print = () => {};
    if (before) before(w);
  }});
  return {dom, w: dom.window, d: dom.window.document, log};
}
const settle = () => new Promise(r => setTimeout(r, 120));

(async () => {
  // Find Bingo's Michigan page: plain HTML cards, each pinned at the middle of its ZIP code.
  let p = run('findbingo-site/michigan/index.html', 'https://www.findbingo.org/michigan/');
  await settle();
  const box = p.d.getElementById('map-box');
  const pinned = [...p.d.querySelectorAll('#listings article[data-pm-lat]')];
  assert(!box.hidden, 'the map shows once its files are loaded');
  assert.equal(p.log.maps.length, 1);
  assert.deepEqual(p.log.tiles, ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], 'map pictures from OpenStreetMap only');
  const cluster = p.log.clusters[0];
  assert.equal(cluster.items.length, pinned.length, 'one pin for each card with a ZIP code point');
  assert.deepEqual(cluster.items.map(m => m.at), pinned.map(a => [Number(a.dataset.pmLat), Number(a.dataset.pmLon)]));
  const dot = cluster.opts.iconCreateFunction({getChildCount: () => 12});
  assert(dot && !/\d/.test(dot.html), 'Find Bingo groups show a plain dot with no number');
  assert.equal(p.d.querySelectorAll('#listings .pm-show').length, pinned.length, 'each pinned card has a Show on the map button');
  // The pin's box: the name, the ZIP code note, Call or a phone lookup, Directions and the full listing.
  const first = pinned[0], pop = cluster.items[0].popup();
  assert.equal(pop.querySelector('strong').textContent, first.querySelector('h3').textContent.trim());
  assert.match(pop.textContent, /middle of the ZIP code/);
  assert.match(pop.textContent, /Directions/);
  assert.equal([...pop.querySelectorAll('a')].find(a => /Directions/.test(a.textContent)).href,
    [...first.querySelectorAll('a')].find(a => /Directions/.test(a.textContent)).href, 'Directions go to the listed address');
  if (first.querySelector('a[href^="tel:"]')) assert.equal(pop.querySelector('a.pm-call').getAttribute('href'), first.querySelector('a[href^="tel:"]').getAttribute('href'));
  assert(!/\b\d+ (halls|games|places|locations|counties)\b/i.test(pop.textContent), 'no counts in a pin box');
  // Show on the map opens that card's pin; See the full listing goes back to the card.
  p.d.querySelector('#listings .pm-show').click();
  assert(cluster.items[0].opened, 'Show on the map opens the pin');
  cluster.items[0].opened.querySelector('button').click();
  assert.equal(p.d.activeElement, first.querySelector('h3'), 'See the full listing moves to the card');
  // Every pin and group has a name for screen readers.
  const map = p.log.maps[0];
  map.fire('layeradd', {layer: cluster.items[0]});
  assert.equal(cluster.items[0]._icon.getAttribute('aria-label'), first.querySelector('h3').textContent.trim());
  const group = Object.assign(new p.w.L.MarkerCluster(), {_icon: p.d.createElement('div')});
  map.fire('layeradd', {layer: group});
  assert(/zoom in/.test(group._icon.getAttribute('aria-label')) && !/\d/.test(group._icon.getAttribute('aria-label')));
  // The page does not scroll-zoom or drag-trap until the map is used.
  assert.equal(map.opts.scrollWheelZoom, false);
  map.fire('click');
  assert(map.scrollWheelZoom.enabled());
  // Hiding the map is remembered, and a later visit loads no map at all.
  p.d.querySelector('#map-box .pm-toggle').click();
  assert(p.d.getElementById('map-area').hidden && p.d.querySelector('#map-box .pm-toggle').getAttribute('aria-expanded') === 'false');
  assert([...p.d.querySelectorAll('.pm-show')].every(b => b.hidden), 'Show on the map buttons go with the map');
  assert.equal(p.w.localStorage.getItem('pm-hidden:/michigan/'), '1');
  p = run('findbingo-site/michigan/index.html', 'https://www.findbingo.org/michigan/', {storage: {'pm-hidden:/michigan/': '1'}});
  await settle();
  assert(!p.d.getElementById('map-box').hidden && p.d.getElementById('map-area').hidden && p.log.maps.length === 0, 'a hidden map is not loaded');
  p.d.querySelector('#map-box .pm-toggle').click();
  await settle();
  assert.equal(p.log.maps.length, 1, 'Show the map loads it');

  // A page without places keeps the box hidden (Find Bingo's home page before a search).
  p = run('findbingo-site/index.html', 'https://www.findbingo.org/', {before(w) { w.fetch = () => new Promise(() => {}) }});
  await settle();
  assert(p.d.getElementById('map-box').hidden && p.log.maps.length === 0, 'no map until there are places');

  // Facilities: the map follows the list as it changes; groups show numbers here; the searched ZIP code is marked.
  p = run('facilities.html', 'https://guide.vethomeguard.org/facilities.html?zip=43334&radius=25');
  await settle();
  let cards = [...p.d.querySelectorAll('#listings article[data-pm-zip]')];
  const zips = p.w.eval('ZIPS');
  assert(cards.length && cards.length === p.d.querySelectorAll('#listings article').length);
  assert.deepEqual(p.log.clusters[0].items.map(m => m.at), cards.map(a => zips[a.dataset.pmZip]), 'facilities pinned at their ZIP codes');
  assert.equal(p.log.clusters[0].opts.iconCreateFunction, undefined, 'the guide shows group counts, like Nina’s Map');
  const you = p.log.maps[0].layers.find(l => l.items && l.items.some(m => m.tooltip));
  assert(you && /43334/.test(you.items[0].tooltip), 'the searched ZIP code is marked');
  p.d.getElementById('fac-county').value = 'Knox';
  p.d.getElementById('fac-county').dispatchEvent(new p.w.Event('change'));
  await settle();
  cards = [...p.d.querySelectorAll('#listings article[data-pm-zip]')];
  assert.equal(p.log.clusters[0].items.length, cards.length, 'the map follows a new list');

  // Use my location: the nearest ZIP code is found on the device and searched like a typed one.
  p = run('facilities.html', 'https://guide.vethomeguard.org/facilities.html', {before(w) {
    Object.defineProperty(w.navigator, 'geolocation', {value: {getCurrentPosition(ok) { ok({coords: {latitude: 40.552, longitude: -82.83}}) }}});
  }});
  await settle();
  const locate = p.d.querySelector('[data-pm-locate]');
  assert(!locate.hidden);
  locate.click();
  await settle();
  const expected = p.w.PlaceMap.nearestZip(p.w.eval('ZIPS'), [40.552, -82.83]).zip;
  assert.equal(p.d.getElementById('fac-zip').value, expected);
  assert.equal(new URL(p.w.location.href).searchParams.get('zip'), expected, 'the page searched that ZIP code');
  // Without location support the button stays hidden.
  p = run('facilities.html', 'https://guide.vethomeguard.org/facilities.html', {before(w) { Object.defineProperty(w.navigator, 'geolocation', {value: undefined}) }});
  await settle();
  assert(p.d.querySelector('[data-pm-locate]').hidden);

  // The Ohio finder: bingo and senior centers pinned at their ZIP codes, with the searched ZIP code marked.
  p = run('bingo.html', 'https://example.org/bingo.html?zip=43334&radius=25');
  await settle();
  cards = [...p.d.querySelectorAll('#listings article[data-pm-zip]')];
  const centroids = p.w.eval('ZIP_CENTROIDS');
  assert(cards.length, 'Ohio cards near 43334 are pinned');
  for (const a of cards) assert.equal(a.dataset.pmZip, a.querySelector('.address').textContent.match(/OH (\d{5})/)[1], a.id + ' pinned at the ZIP code in its address');
  assert.deepEqual(p.log.clusters[0].items.map(m => m.at), cards.map(a => centroids[a.dataset.pmZip]));
  assert(!/\d/.test(p.log.clusters[0].opts.iconCreateFunction().html), 'plain group dots on the Ohio finder');
  assert(cards.every(a => ['game', 'center', 'nodays'].includes(a.dataset.pmKind)));
  // The Ohio finder on findbingo.org: map files from findbingo.org/assets/map/, Find Bingo's privacy page, plain group dots.
  const ohio = new JSDOM(read('bingo-site/findbingo/ohio/index.html')).window.document.getElementById('map-box');
  assert.equal(ohio.dataset.pmBase, '../assets/map/');
  assert.equal(ohio.dataset.pmNumbers, '0');
  assert(ohio.querySelector('a[href="../privacy/"]'));
  console.log('PASS place map: pins only at known ZIP code points, plain group dots on Find Bingo, pin boxes with call, directions and the listing, list buttons, keyboard names, remembered hiding, the map following the list, and Use my location.');
})().catch(e => { console.error(e); process.exit(1); });
