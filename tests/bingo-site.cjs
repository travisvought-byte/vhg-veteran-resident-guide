// The standalone Ohio Bingo Finder (bingo-site/, served at https://bingo.vethomeguard.org/).
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..'), site = path.join(root, 'bingo-site');
const read = f => fs.readFileSync(path.join(site, f), 'utf8');
const dataOf = html => JSON.parse(html.match(/const BINGO=(\[.*?\]);/s)[1]);

assert.equal(read('CNAME'), 'bingo.vethomeguard.org\n');
const index = read('index.html'), guide = fs.readFileSync(path.join(root, 'bingo.html'), 'utf8');
assert.deepEqual(dataOf(index), dataOf(guide), 'finder data matches the guide page');
const doc = new JSDOM(index).window.document;
assert.equal(doc.querySelector('link[rel=canonical]').href, 'https://bingo.vethomeguard.org/');
assert.equal(doc.querySelector('meta[property="og:url"]').content, 'https://bingo.vethomeguard.org/');
assert(!/["'=]bingo\.html/.test(index), 'no links to the old bingo.html page');
assert(!index.includes('guide.vethomeguard.org/bingo.html'), 'printed flyers name the bingo address');
assert.equal(index.split('bingo.vethomeguard.org<br>').length - 1, 2, 'both printable flyers show the address');
assert.deepEqual([...doc.querySelectorAll('nav.quick a')].map(a => a.getAttribute('href').slice(0, 3)), ['./?', './?', './?', './?', './?']);
assert.deepEqual([...doc.querySelectorAll('nav.audience a')].map(a => a.getAttribute('href')),
  ['#submit-details', '#flyer-maker', 'https://bingo.vethomeguard.org/partners.html']);
assert(doc.querySelector('footer a[href="partners.html"]') && doc.querySelector('footer a[href="poster.html"]'));
assert(doc.querySelector('a[href="https://guide.vethomeguard.org/?view=community"]'), 'link back to the guide');
assert(index.includes('<script defer src="assets/analytics.js"></script></body>'));

// Every local link and image in the site resolves to a file in bingo-site/.
for (const page of ['index.html', 'partners.html', 'poster.html']) {
  const d = new JSDOM(read(page)).window.document;
  for (const el of d.querySelectorAll('[href],[src]')) {
    const ref = el.getAttribute('href') || el.getAttribute('src');
    if (/^(https?:|mailto:|tel:|#|\.\/(\?|#|$))/.test(ref) || ref.startsWith("'")) continue;
    assert(fs.existsSync(path.join(site, ref.split(/[?#]/)[0])), page + ' links to missing ' + ref);
  }
}

// Partner page: numbers come from the published data; routes reach the finder's tools.
const records = dataOf(index), partners = new JSDOM(read('partners.html')).window.document;
const stat = [...partners.querySelectorAll('.stat b')].map(b => Number(b.textContent));
assert.deepEqual(stat, [
  records.filter(r => ['licensed', 'charitable'].includes(r.category)).length,
  records.filter(r => ['center', 'senior'].includes(r.category)).length,
  new Set(records.map(r => r.county)).size,
  records.filter(r => ['session_days', 'session_dates', 'session_monthly'].some(k => r[k] && r[k].length)).length,
]);
for (const href of ['./#submit-details', './?organizer=1', './#flyer-maker', 'poster.html', 'https://www.vethomeguard.org/donate'])
  assert(partners.querySelector(`a[href="${href}"]`), 'partners page links to ' + href);
assert(partners.querySelector('a[href^="mailto:travis@vethomeguard.org?subject=Ohio%20Bingo%20Finder%20partnership"]'));
assert(partners.body.textContent.includes('Inclusion never depends on donations or sponsorship.'));
assert(partners.querySelector('#share-text').textContent.endsWith('bingo.vethomeguard.org'));
const poster = read('poster.html');
assert(poster.includes('<p class="url">bingo.vethomeguard.org</p>') && poster.includes('src="assets/bingo-qr.svg"'));
assert(read('sitemap.xml').includes('<loc>https://bingo.vethomeguard.org/partners.html</loc>'));
assert(read('robots.txt').includes('Sitemap: https://bingo.vethomeguard.org/sitemap.xml'));
console.log('PASS bingo site: bingo.vethomeguard.org address, data parity with the guide, printed flyer address, local links, partner numbers and routes, poster, sitemap.');
