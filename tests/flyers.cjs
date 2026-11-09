// Printable flyers: every listed flyer has a one-page PDF, a preview image and a print source,
// flyers.html is current and lists every download, and the guides link to it.
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');

const ROOT = path.join(__dirname, '..');
const read = p => fs.readFileSync(path.join(ROOT, p));
const {flyers} = JSON.parse(read('data/flyers.json'));
assert(flyers.length >= 1);
const ids = new Set();

const onePagePdf = (file, wIn, hIn) => {
  const pdf = read(file).toString('latin1');
  assert(pdf.startsWith('%PDF-'), file + ' is not a PDF');
  assert.equal((pdf.match(/\/Type\s*\/Page(?!s)/g) || []).length, 1, file + ' must be exactly one page');
  const box = pdf.match(/\/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]/);
  assert(box, file + ' has no page size');
  assert(Math.abs(box[1] / 72 - wIn) < 0.02 && Math.abs(box[2] / 72 - hIn) < 0.02, file + ' page size ' + box[1] / 72 + ' × ' + box[2] / 72 + ' in');
};

const page = read('flyers.html').toString();
for (const f of flyers) {
  assert(/^[a-z0-9-]+$/.test(f.id) && !ids.has(f.id), 'flyer ids are unique slugs');
  ids.add(f.id);
  for (const k of ['title', 'guide', 'guide_name', 'size', 'use', 'alt']) assert(f[k], f.id + ' needs ' + k);
  onePagePdf('flyers/' + f.id + '.pdf', f.width_in, f.height_in);
  if (f.two_up) onePagePdf('flyers/' + f.id + '-2up.pdf', 11, 8.5);
  assert(read('flyers/' + f.id + '.png').subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])), f.id + ' preview is a PNG');
  assert(read('flyers/' + f.id + '-thumb.png').subarray(1, 4).toString() === 'PNG', f.id + ' has a share-card thumbnail');
  assert(fs.existsSync(path.join(ROOT, f.qr)), f.id + ' QR file exists');
  const src = read('flyers/src/' + f.id + '.html').toString();
  assert(!/\{\{|\/_blob\//.test(src), f.id + ' print source has no canvas placeholders');
  assert(page.includes('href="flyers/' + f.id + '.pdf" download'), 'flyers.html offers ' + f.id + '.pdf');
  if (f.two_up) assert(page.includes('href="flyers/' + f.id + '-2up.pdf" download'));
  assert(fs.existsSync(path.join(ROOT, f.guide)), f.id + ' points to a real guide page');
}
const check = spawnSync('python3', ['scripts/build_flyers_page.py', '--check'], {cwd: ROOT, encoding: 'utf8'});
assert.equal(check.status, 0, check.stderr || check.stdout);
for (const p of ['family-guide.html', 'index.html']) assert(read(p).toString().includes('href="flyers.html"'), p + ' links to the flyers page');
console.log('PASS printable flyers: ' + flyers.length + ' flyers with one-page PDFs at their stated size, previews, print sources and a current download page linked from the guides.');
