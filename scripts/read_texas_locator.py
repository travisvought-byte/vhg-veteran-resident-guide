#!/usr/bin/env python3
"""Read every row of the Texas Bingo Hall Locator into a JSON file for import_texas_bingo.py.

The locator (https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf) is a script-driven page that
shows its results a screenful at a time, so it is read in an ordinary headless browser: one empty search,
then the results table is scrolled to the end. Needs Python Playwright and a Chrome or Chromium browser.

    python3 scripts/read_texas_locator.py texas-locator.json [--chrome /usr/bin/google-chrome]

Each row is [organization, website, location name, phone, street, city, ZIP, days and times]. The script
prints the record count the locator reports next to the rows read; identical rows count once.
"""
import argparse, asyncio, json, os, re

URL = 'https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf'
ROWS = """() => Array.from(document.querySelectorAll('tr')).map(r => Array.from(r.children).map(td => td.innerText.trim()))
              .filter(c => c.length >= 8 && / To /.test(c[7] || ''))"""


async def read(chrome):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        proxy = {'server': os.environ['HTTPS_PROXY']} if os.environ.get('HTTPS_PROXY') else None
        browser = await p.chromium.launch(executable_path=chrome, headless=True, proxy=proxy, args=['--no-sandbox'])
        page = await (await browser.new_context(viewport={'width': 1400, 'height': 1000})).new_page()
        await page.goto(URL, wait_until='networkidle', timeout=90000)
        await page.click('[id$="qryId1::search"]')
        await page.wait_for_timeout(8000)
        found = re.search(r'Records Found:\s*(\d+)', await page.evaluate('document.body.innerText'))
        scroller = await page.evaluate("""() => Array.from(document.querySelectorAll('div[id$="::scroller"]')).map(e => e.id)[0]""")
        seen, still, top = {}, 0, 0
        while still < 8:
            before = len(seen)
            for row in await page.evaluate(ROWS):
                seen[json.dumps(row[:8])] = row[:8]
            still = still + 1 if len(seen) == before else 0
            top += 600
            await page.evaluate(f'document.getElementById({json.dumps(scroller)}).scrollTop = {top}')
            await page.wait_for_timeout(1500)
        await browser.close()
        return list(seen.values()), int(found.group(1)) if found else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('out')
    ap.add_argument('--chrome', default='/usr/bin/google-chrome')
    a = ap.parse_args()
    rows, reported = asyncio.run(read(a.chrome))
    with open(a.out, 'w') as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)
    print(f'{len(rows)} rows read; the locator reported {reported} records.')


if __name__ == '__main__':
    main()
