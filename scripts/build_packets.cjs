// Renders the printable packets' PDFs from their HTML print views (written by scripts/build_packets.py).
// Only packets whose print view or stylesheet changed are rendered again; data/packets/rendered.json records
// what each PDF was made from, so unchanged PDFs stay byte-for-byte the same.
//   node scripts/build_packets.cjs          # render new or changed packets
//   node scripts/build_packets.cjs --all    # render every packet
//   node scripts/build_packets.cjs --only=morrow  # just the packets whose path contains 'morrow'
//   node scripts/build_packets.cjs --check  # fail if any PDF is missing or older than its print view
// Uses Playwright's Chromium; set PLAYWRIGHT_CHROMIUM_EXECUTABLE to use a locally installed Chrome instead.
// Each packet is checked before it is saved: fonts and images load, nothing runs off the page, Ohio county
// packets fit on two pages, cover sheets on one, and large-print text is 18 points or larger.
'use strict';
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DIR = path.join(ROOT, 'flyers/packets');
const LEDGER = path.join(ROOT, 'data/packets/rendered.json');
const KINDS = {oh: {max: 2}, 'oh-large': {max: 6, minPt: 18}, states: {max: 40}, cover: {max: 1}};

const sha = (...parts) => crypto.createHash('sha256').update(parts.join('\0')).digest('hex').slice(0, 16);
const pageCount = file => (fs.readFileSync(file, 'latin1').match(/\/Type\s*\/Page(?!s)/g) || []).length;

function packets() {
  const css = fs.readFileSync(path.join(DIR, 'packets.css'), 'utf8');
  const out = [];
  for (const kind of Object.keys(KINDS)) {
    const dir = path.join(DIR, kind);
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir).filter(n => n.endsWith('.html')).sort()) {
      const html = path.join(dir, name);
      const rel = path.relative(ROOT, html);
      out.push({kind, html, rel, pdf: html.replace(/\.html$/, '.pdf'), hash: sha(fs.readFileSync(html, 'utf8'), css)});
    }
  }
  return out;
}

async function main() {
  const args = process.argv.slice(2);
  const ledger = fs.existsSync(LEDGER) ? JSON.parse(fs.readFileSync(LEDGER, 'utf8')) : {};
  const all = packets();
  const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);  // e.g. --only=morrow, for a quick look
  const stale = all.filter(p => (!only || p.rel.includes(only)) && (args.includes('--all') || ledger[p.rel] !== p.hash || !fs.existsSync(p.pdf)));
  if (args.includes('--check')) {
    if (stale.length) {
      console.error(stale.length + ' packet PDF(s) are missing or out of date, e.g. ' + stale.slice(0, 3).map(p => p.rel).join(', ') + '. Run node scripts/build_packets.cjs');
      process.exit(1);
    }
    console.log('All ' + all.length + ' packet PDFs match their print views.');
    return;
  }
  // Drop ledger entries for packets that no longer exist, and their PDFs.
  for (const rel of Object.keys(ledger)) {
    if (!all.some(p => p.rel === rel)) {
      delete ledger[rel];
      const pdf = path.join(ROOT, rel.replace(/\.html$/, '.pdf'));
      if (fs.existsSync(pdf)) fs.unlinkSync(pdf);
    }
  }
  if (!stale.length) {
    console.log('Packet PDFs already match their print views.');
    fs.writeFileSync(LEDGER, JSON.stringify(sortKeys(ledger), null, 1) + '\n');
    return;
  }
  const {chromium} = require('playwright');
  const browser = await chromium.launch({executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined});
  const problems = [];
  let done = 0;
  const queue = stale.slice();
  async function worker() {
    const page = await browser.newPage({viewport: {width: 816, height: 1056}});
    await page.emulateMedia({media: 'print'});
    while (queue.length) {
      const p = queue.shift();
      const rule = KINDS[p.kind];
      await page.goto('file://' + p.html);
      await page.evaluate(() => document.fonts.ready);
      const found = await page.evaluate(minPt => {
        const out = [];
        for (const face of document.fonts) if (face.status === 'error') out.push('font did not load: ' + face.family);
        for (const img of document.images) if (!img.complete || !img.naturalWidth) out.push('image missing: ' + img.getAttribute('src'));
        const sheet = document.querySelector('.sheet').getBoundingClientRect();
        for (const el of document.querySelectorAll('.sheet *')) {
          const r = el.getBoundingClientRect();
          if (r.width && r.right > sheet.right + 1) out.push(el.tagName + ' runs off the page: ' + (el.textContent || '').trim().slice(0, 40));
          if (minPt && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {
            const pt = parseFloat(getComputedStyle(el).fontSize) * 0.75;
            if (pt < minPt - 0.01) out.push('text smaller than ' + minPt + ' pt (' + pt + ' pt): ' + el.textContent.trim().slice(0, 40));
          }
        }
        return out;
      }, rule.minPt || 0);
      await page.pdf({path: p.pdf, preferCSSPageSize: true, printBackground: true});
      const pages = pageCount(p.pdf);
      if (pages > rule.max) found.push(pages + ' pages; the limit for this kind of packet is ' + rule.max);
      if (found.length) problems.push(p.rel + ':\n  ' + found.join('\n  '));
      else ledger[p.rel] = p.hash;
      done++;
      if (done % 25 === 0) console.log('Rendered ' + done + ' of ' + stale.length);
    }
    await page.close();
  }
  await Promise.all([worker(), worker(), worker(), worker()]);
  await browser.close();
  fs.writeFileSync(LEDGER, JSON.stringify(sortKeys(ledger), null, 1) + '\n');
  if (problems.length) {
    console.error(problems.join('\n'));
    process.exit(1);
  }
  console.log('Rendered ' + done + ' packet PDF(s).');
}

function sortKeys(o) {
  return Object.fromEntries(Object.keys(o).sort().map(k => [k, o[k]]));
}

main().catch(e => { console.error(e.message || e); process.exit(1); });
