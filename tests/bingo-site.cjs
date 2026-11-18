// The Ohio Bingo Finder (bingo-site/findbingo/ohio/, served at https://www.findbingo.org/ohio/) and the
// forwarding pages left at the retired address bingo.vethomeguard.org (the root of bingo-site/).
const assert = require('assert'), fs = require('fs'), path = require('path');
const {JSDOM} = require('jsdom');
const root = path.resolve(__dirname, '..'), old = path.join(root, 'bingo-site'), site = path.join(old, 'findbingo/ohio');
const HOME = 'https://www.findbingo.org/ohio/';
const read = f => fs.readFileSync(path.join(site, f), 'utf8');
const dataOf = html => JSON.parse(html.match(/const BINGO=(\[.*?\]);/s)[1]);

assert.equal(fs.readFileSync(path.join(old, 'CNAME'), 'utf8'), 'bingo.vethomeguard.org\n', 'GitHub Pages keeps the retired address');
// Every page that existed at the old address forwards to the same page at the new one, keeping ?zip= and #anchor.
for (const [page, to] of [['index.html', ''], ['404.html', ''], ['partners.html', 'partners.html'], ['distributions.html', 'distributions.html'], ['instant.html', 'instant.html'], ['poster.html', 'poster.html']]) {
  const html = fs.readFileSync(path.join(old, page), 'utf8');
  assert(html.includes(`location.replace("${HOME}${to}"+location.search+location.hash)`) && html.includes(`content="0;url=${HOME}${to}"`), page + ' forwards');
  assert(html.includes('content="noindex,follow"') && html.length < 1500, page + ' is only a forwarding page');
  assert(fs.existsSync(path.join(site, to || 'index.html')), page + ' forwards to a page that exists');
}
assert(!fs.existsSync(path.join(old, 'assets')) && !fs.existsSync(path.join(old, 'sitemap.xml')), 'no second copy of the site at the old address');
const index = read('index.html'), guide = fs.readFileSync(path.join(root, 'bingo.html'), 'utf8');
assert.deepEqual(dataOf(index), dataOf(guide), 'finder data matches the guide page');
const doc = new JSDOM(index).window.document;
assert.equal(doc.querySelector('link[rel=canonical]').href, HOME);
assert(!index.includes("location.hostname==='guide.vethomeguard.org'") && !index.includes('noindex'), 'the finder itself does not forward and is indexed');
assert(/rel="canonical" href="https:\/\/www\.findbingo\.org\/ohio\/"/.test(guide) && guide.includes("location.replace('https://www.findbingo.org/ohio/'+location.search+location.hash)"), 'the guide copy forwards to the finder');
assert.equal(doc.querySelector('meta[property="og:url"]').content, HOME);
assert(!index.includes('bingo.vethomeguard.org'), 'the finder never names the retired address');
assert(!/["'=]bingo\.html/.test(index), 'no links to the old bingo.html page');
assert(!index.includes('guide.vethomeguard.org/bingo.html'), 'printed flyers name the bingo address');
assert.equal(index.split('<strong>ohiobingo.org').length - 1, 2, 'both printable flyers give the short ohiobingo.org address');
assert.deepEqual([...doc.querySelectorAll('nav.quick a')].map(a => a.getAttribute('href').slice(0, 3)), ['./?', './?', './?', './?']);
assert.deepEqual([...doc.querySelectorAll('nav.audience a')].map(a => a.getAttribute('href')),
  ['#submit-details', '#flyer-maker', HOME + 'partners.html']);
assert(doc.querySelector('footer a[href="partners.html"]') && doc.querySelector('footer a[href="poster.html"]'));
assert(doc.querySelector('footer a[href="../"]'), 'link up to the national finder');
assert(doc.querySelector('a[href="https://guide.vethomeguard.org/?view=community"]'), 'link back to the guide');
assert.equal(doc.querySelector('header a.back').getAttribute('href'), 'https://www.ohiobingo.org/', 'top link returns players to ohiobingo.org');
assert(doc.querySelector('#change-zip[hidden] a[href="#bingo-nearby"]'), 'results offer a way back to the ZIP search');
assert(index.includes('<script defer src="assets/analytics.js"></script></body>'));

// Every local link and image in the site resolves to a file in bingo-site/findbingo/ohio/.
for (const page of ['index.html', 'partners.html', 'distributions.html', 'instant.html', 'poster.html']) {
  const d = new JSDOM(read(page)).window.document;
  for (const el of d.querySelectorAll('[href],[src]')) {
    const ref = el.getAttribute('href') || el.getAttribute('src');
    if (/^(https?:|mailto:|tel:|sms:|#|\.\.?\/(\?|#|$))/.test(ref) || ref.startsWith("'")) continue; // sms: is the "text 988" link in the help block
    assert(fs.existsSync(path.join(site, ref.split(/[?#]/)[0])), page + ' links to missing ' + ref);
  }
}

// Partner page: no headline counts (kept plain on purpose); routes reach the finder's tools.
const records = dataOf(index), partners = new JSDOM(read('partners.html')).window.document;
assert.equal(partners.querySelectorAll('.stat').length, 0, 'partners page shows no count band');
assert(!/\b\d{2,4} (state-listed|Ohio counties)/.test(partners.body.textContent));
for (const href of ['./#submit-details', './?organizer=1', './#flyer-maker', 'poster.html', 'distributions.html'])
  assert(partners.querySelector(`a[href="${href}"]`), 'partners page links to ' + href);
assert(partners.querySelector('a[href^="mailto:travis@vethomeguard.org?subject=Ohio%20Bingo%20Finder%3A%20community%20partner"]'));
assert(read('distributions.html').includes('https://codes.ohio.gov/ohio-revised-code/section-2915.101'));
const sitemap = fs.readFileSync(path.join(old, 'findbingo/sitemap.xml'), 'utf8');
assert(sitemap.includes('<loc>https://www.findbingo.org/</loc>') && sitemap.includes('<loc>' + HOME + '</loc>') && sitemap.includes('<loc>' + HOME + 'distributions.html</loc>'));
assert(partners.body.textContent.includes('Inclusion never depends on donations, partnership or sponsorship.'));
assert(partners.querySelector('#share-text').textContent.endsWith('ohiobingo.org'));
const poster = read('poster.html');
assert(poster.includes('<p class="url">ohiobingo.org</p>') && poster.includes('src="assets/bingo-qr.svg"'));
assert(sitemap.includes('<loc>' + HOME + 'partners.html</loc>'));
assert(fs.readFileSync(path.join(old, 'findbingo/robots.txt'), 'utf8').includes('Sitemap: https://www.findbingo.org/sitemap.xml'));

// Kinds of bingo: posts and lodges licensed for instant bingo outside games, members and guests only.
const instant = read('instant.html'), rows = JSON.parse(instant.match(/const ROWS=(\[.*?\]);/s)[1]);
const src = JSON.parse(fs.readFileSync(path.join(root, 'data/source/ohio-bingo-authorizations-2026-10-02.json'), 'utf8')).records;
const c3 = new Set(src.filter(r => r.tax_status === '501(c)(3)').map(r => r.license_number));
assert(rows.length > 900 && rows.every(r => r.county && !c3.has(r.license_number)), 'no 501(c)(3) bar locations, every row has a county');
assert(rows.every(r => r.paper || r.electronic));
assert(!rows.some(r => r.kind === 'Club' && r.electronic), 'sporting clubs cannot run electronic instant bingo');
assert(instant.includes('members and invited guests') && instant.includes('This is not a list of places open to the public.'));
assert(instant.includes('House Bill 344') && sitemap.includes('<loc>' + HOME + 'instant.html</loc>'));
const marengo = records.find(r => r.license_number === '1006-39');
assert.deepEqual(marengo.also_sold, ['instant bingo tickets (pull-tabs)'], 'Type III electronic is not shown as sold during games');
assert(!records.some(r => r.partner_since), 'no community partners are on file yet');
console.log('PASS bingo site: kinds-of-bingo page (members and guests, no 501(c)(3) bar locations), findbingo.org/ohio address, forwards from the retired bingo.vethomeguard.org, data parity with the guide, printed flyer address, local links, partner page without count band, partner routes, poster, sitemap.');
