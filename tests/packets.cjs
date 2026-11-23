// Printable resource packets: every Ohio county has a two-page packet and a large-print packet, every other
// state and D.C. has a packet, each staff cover sheet is one page, the print views match the data
// (scripts/build_packets.py --check), each packet carries the crisis line, the correction route and a working
// QR code, and the download page is linked from the guide.
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');

const ROOT = path.join(__dirname, '..');
const read = p => fs.readFileSync(path.join(ROOT, p));
const exists = p => fs.existsSync(path.join(ROOT, p));
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function pdf(file, maxPages) {
  const text = read(file).toString('latin1');
  assert(text.startsWith('%PDF-'), file + ' is not a PDF');
  const pages = (text.match(/\/Type\s*\/Page(?!s)/g) || []).length;
  assert(pages >= 1 && pages <= maxPages, file + ' has ' + pages + ' pages (at most ' + maxPages + ')');
  const box = text.match(/\/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]/);
  assert(box && Math.abs(box[1] / 72 - 8.5) < 0.02 && Math.abs(box[2] / 72 - 11) < 0.02, file + ' is letter size');
  return pages;
}

function view(file) {
  const html = read(file).toString();
  const dir = path.dirname(file);
  assert(html.includes('988') && html.includes('838255'), file + ' has the crisis line');
  assert(html.includes('travis@vethomeguard.org') && html.includes('Report a problem'), file + ' explains how to report a wrong number');
  assert(!/unverified|not verified/i.test(html), file + ' carries no "unverified" warning');
  assert(/<ol class="sources">|<ul class="sources">/.test(html), file + ' lists its sources');
  for (const [, src] of html.matchAll(/<img src="([^"]+)"/g)) assert(exists(path.join(dir, src)), file + ' image ' + src + ' exists');
  return html;
}

const sources = JSON.parse(read('data/packets/ohio-county-sources.json'));
const counties = JSON.parse(read('data/public/ohio-county-veterans-offices.json')).map(c => c.county);
assert.deepEqual(Object.keys(sources.counties).sort(), counties.slice().sort(), 'packet sources cover every Ohio county');
for (const county of counties) {
  const s = slug(county);
  const html = view('flyers/packets/oh/' + s + '.html');
  const c = sources.counties[county];
  assert(html.includes(c.cvso.phone.split(' ')[0]), county + ': the ODVS veterans office phone is on the packet');
  for (const need of ['Area Agency on Aging', 'Ombudsman', 'Adult Protective Services', 'Free legal help', 'VA health care'])
    assert(html.includes(need), county + ' packet covers ' + need);
  assert(html.includes('guide.vethomeguard.org/?county=' + county.replace(/ /g, '+')), county + ' packet has its short URL');
  const qr = read('flyers/packets/qr/oh-' + s + '.svg').toString();
  assert(qr.startsWith('<?xml') && qr.includes('<svg'), county + ' QR code is an SVG');
  pdf('flyers/packets/oh/' + s + '.pdf', 2);
  view('flyers/packets/oh-large/' + s + '.html');
  pdf('flyers/packets/oh-large/' + s + '.pdf', 6);
}
const states = JSON.parse(read('states/registry.json')).slice(1);
for (const st of states) {
  const code = st.code.toLowerCase();
  const html = view('flyers/packets/states/' + code + '.html');
  assert(html.includes('guide.vethomeguard.org/' + st.page), st.code + ' packet points to its guide page');
  pdf('flyers/packets/states/' + code + '.pdf', 40);
}
for (const v of ['nursing-home', 'chaplain', 'jail-library']) {
  view('flyers/packets/cover/' + v + '.html');
  pdf('flyers/packets/cover/' + v + '.pdf', 1);
}
// Large print: the stylesheet sets no large-print size below 18 points (the renderer also measures every line).
const css = read('flyers/packets/packets.css').toString();
for (const [, rule] of css.matchAll(/\.large[^{]*\{([^}]*)\}/g))
  for (const [, pt] of rule.matchAll(/font(?:-size)?:[^;]*?([\d.]+)pt/g)) assert(+pt >= 18, 'large print sizes are 18 pt or more: ' + rule);

const check = spawnSync('python3', ['scripts/build_packets.py', '--check'], {cwd: ROOT, encoding: 'utf8'});
assert.equal(check.status, 0, check.stderr || check.stdout);
const page = read('packets.html').toString();
for (const county of counties) assert(page.includes('flyers/packets/oh/' + slug(county) + '.pdf'), 'packets.html offers ' + county);
assert(read('index.html').toString().includes('href="packets.html"'), 'the guide home page (Ohio) links to the packets page');
// A PDF older than its print view is rebuilt by the "Rebuild printable packets" workflow after the push;
// report it here without failing, so a data change never blocks on a local Chrome.
const stale = spawnSync('node', ['scripts/build_packets.cjs', '--check'], {cwd: ROOT, encoding: 'utf8'});
if (stale.status !== 0) console.log('NOTE ' + (stale.stderr || stale.stdout).trim());
console.log('PASS printable packets: Ohio county packets (two pages) and large print, state packets, one-page cover sheets, current print views and a linked download page.');
