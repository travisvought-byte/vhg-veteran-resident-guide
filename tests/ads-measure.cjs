// assets/ads-measure.js loads Google's tag on every page so Google Ads can confirm it, and sends one local-office call ping per page.
// Google Ads itself only counts the ping when the visitor came from an ad click.
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
assert.strictEqual(page.appended.length, 1, 'every page loads the Google tag so Google Ads can verify it');
assert.ok(page.appended[0].src.endsWith('gtag/js?id=AW-18593576535'));
page.click('tel:988');
page.click('tel:911');
page.click('tel:+18774243838');
assert.strictEqual(page.conversions().length, 0, 'national lines are not counted as a local office');
page.click('tel:+17408332010');
page.click('tel:+17408332010');
assert.strictEqual(page.conversions().length, 1, 'a local-office call sends one ping per page, which Google matches to an ad click or ignores');
assert.strictEqual(page.conversions()[0][2].send_to, 'AW-18593576535/rqT3CMn14L4dENfsjaJF');
assert.deepStrictEqual(Object.keys(page.conversions()[0][2]).sort(), ['send_to', 'transport_type'], 'nothing about the number or county is sent');

page = run('?gclid=abc123');
assert.strictEqual(page.appended.length, 1, 'an ad visitor loads the Google tag');
page.click('tel:+17408332010');
assert.strictEqual(page.conversions().length, 1, 'an ad visitor sends the same single ping');
assert.deepStrictEqual(page.store, {}, 'nothing is kept in the browser');

const analytics = require('fs').readFileSync(require('path').join(__dirname, '..', 'assets', 'analytics.js'), 'utf8');
const gtmBlock = analytics.slice(analytics.lastIndexOf('GTM-PGHMBBZK') - 600, analytics.lastIndexOf('GTM-PGHMBBZK') + 40);
assert.ok(/location\.hostname === 'guide\.vethomeguard\.org'/.test(gtmBlock), 'Tag Manager loads on the guide only, not on the bingo sites that share this script');
assert.ok(!/conversion/.test(analytics.replace(/\/\/.*$/gm, '')), 'analytics.js sends no conversions, so calls are never counted twice');

console.log('PASS: the Google tag loads on every guide page; a local office call sends one ping (Google counts only ad visits); Tag Manager stays on the guide.');
