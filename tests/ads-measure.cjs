// assets/ads-measure.js loads Google's tag only for ad visitors and counts one local-office call per visit.
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(__dirname + '/../assets/ads-measure.js', 'utf8');

function run(search, stored) {
  const store = Object.assign({}, stored || {});
  const appended = [];
  const listeners = [];
  const window = {};
  const document = {
    head: {appendChild: (el) => appended.push(el)},
    createElement: () => ({}),
    addEventListener: (type, fn) => listeners.push(fn),
  };
  const sessionStorage = {getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }};
  vm.runInNewContext(code, {window, document, location: {search}, sessionStorage, Date});
  const click = (href) => listeners.forEach((fn) => fn({target: {closest: () => ({getAttribute: () => href})}}));
  const conversions = () => (window.dataLayer || []).filter((a) => a[0] === 'event' && a[1] === 'conversion');
  return {appended, click, conversions, store, window};
}

let page = run('?view=housing');
assert.strictEqual(page.appended.length, 0, 'ordinary visitors never load Google code');
assert.strictEqual(page.window.dataLayer, undefined);

page = run('?gclid=abc123');
assert.strictEqual(page.appended.length, 1, 'an ad visitor loads the Google tag');
assert.ok(page.appended[0].src.endsWith('gtag/js?id=AW-18593576535'));
assert.strictEqual(page.store['vhg-ad-visit'], '1', 'the visit is remembered in this tab');
page.click('tel:988');
page.click('tel:911');
page.click('tel:+18774243838');
assert.strictEqual(page.conversions().length, 0, 'national lines are not counted as a local office');
page.click('tel:+17408332010');
page.click('tel:+17408332010');
assert.strictEqual(page.conversions().length, 1, 'one local-office call counts once');
assert.strictEqual(page.conversions()[0][2].send_to, 'AW-18593576535/rqT3CMn14L4dENfsjaJF');

page = run('', {'vhg-ad-visit': '1'});
assert.strictEqual(page.appended.length, 1, 'later pages in the same ad visit keep measuring');

console.log('PASS: Google ad measurement loads only for ad visitors and counts one local office call.');
