// Builds the printable flyers listed in data/flyers.json.
// For each flyer: flyers/<id>.pdf (exact page size, fonts embedded), flyers/<id>.png (preview),
// and, when two_up is set, flyers/<id>-2up.pdf (two copies on one landscape letter page, with a cut line).
// Run after editing a source in flyers/src/:  node scripts/build_flyers.cjs
// Uses Playwright's Chromium; set PLAYWRIGHT_CHROMIUM_EXECUTABLE to use a locally installed Chrome instead.
'use strict';
const fs = require('fs');
const path = require('path');
const {chromium} = require('playwright');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'flyers');
const {flyers} = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/flyers.json'), 'utf8'));
const PX = 96;

(async () => {
  const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined;
  const browser = await chromium.launch({executablePath});
  for (const f of flyers) {
    const src = path.join(OUT, 'src', f.id + '.html');
    const w = Math.round(f.width_in * PX), h = Math.round(f.height_in * PX);
    const page = await browser.newPage({viewport: {width: w, height: h}, deviceScaleFactor: 2});
    await page.goto('file://' + src);
    await page.evaluate(() => document.fonts.ready);
    // Guard against clipped content: every element must sit inside the page, and no box may overflow.
    const problems = await page.evaluate(([W, H]) => {
      const out = [];
      if (!document.fonts.check('700 16px "Atkinson Hyperlegible"')) out.push('flyer font did not load');
      for (const el of document.body.querySelectorAll('*')) {
        const r = el.getBoundingClientRect();
        if (r.width && (r.bottom > H + 0.5 || r.right > W + 0.5)) out.push(el.tagName + ' ends outside the page: ' + (el.textContent || '').trim().slice(0, 40));
        if (el.scrollHeight > el.clientHeight + 1 && getComputedStyle(el).overflow === 'hidden') out.push(el.tagName + ' content is cut off: ' + (el.textContent || '').trim().slice(0, 40));
      }
      for (const img of document.images) if (!img.complete || !img.naturalWidth) out.push('image missing: ' + img.getAttribute('src'));
      return out;
    }, [w, h]);
    if (problems.length) throw new Error(f.id + ':\n  ' + problems.join('\n  '));
    await page.pdf({path: path.join(OUT, f.id + '.pdf'), width: f.width_in + 'in', height: f.height_in + 'in', printBackground: true, pageRanges: '1'});
    await page.screenshot({path: path.join(OUT, f.id + '.png'), clip: {x: 0, y: 0, width: w, height: h}});
    if (f.two_up) {
      // Two copies side by side on landscape letter (11 × 8.5 in), with a dashed cut line between them.
      const two = await browser.newPage({viewport: {width: 1056, height: 816}});
      await two.goto('file://' + src);
      await two.evaluate(() => document.fonts.ready);
      await two.evaluate(([W, H]) => {
        const flyer = document.body.firstElementChild;
        const sheet = document.createElement('div');
        sheet.style.cssText = 'width:1056px;height:816px;display:flex;align-items:center;justify-content:center;position:relative';
        sheet.append(flyer.cloneNode(true), flyer.cloneNode(true));
        const cut = document.createElement('div');
        cut.style.cssText = 'position:absolute;left:528px;top:0;bottom:0;border-left:1px dashed #8a8a8a';
        sheet.append(cut);
        document.body.replaceChildren(sheet);
        const style = document.createElement('style');
        style.textContent = '@page{size:11in 8.5in;margin:0}';
        document.head.append(style);
      }, [w, h]);
      await two.pdf({path: path.join(OUT, f.id + '-2up.pdf'), width: '11in', height: '8.5in', printBackground: true, pageRanges: '1'});
      await two.screenshot({path: '/tmp/' + f.id + '-2up-check.png'});
      await two.close();
    }
    await page.close();
    console.log('Built ' + f.id);
  }
  await browser.close();
})().catch(e => { console.error(e.message || e); process.exit(1); });
