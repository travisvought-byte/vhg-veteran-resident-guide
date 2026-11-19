#!/usr/bin/env python3
"""Read every row of the Missouri Gaming Commission's "Find Local Bingo Games" page into a JSON file.

    python3 scripts/read_missouri_finder.py missouri-finder.json

The page is a script-driven grid that shows ten rows at a time, so it is read in a headless browser
(Python Playwright and Chrome), clicking "Next" until the last page. Each row is the cells as shown:
location of play (name, street and phone on separate lines), city, county, start time, occurrence,
then one cell per weekday, Sunday first, holding the day's name when the game is played that day.
"""
import json, re, sys
from playwright.sync_api import sync_playwright

URL = 'https://www.mgc.dps.mo.gov/BingoWebLocal/frmWebFindLocalBingoGame.aspx'
ROWS_JS = """() => [...document.querySelectorAll('tr[id*="DXDataRow"]')]
                   .map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.trim()))"""
PAGER_JS = r"() => (document.body.innerText.match(/Page (\d+) of (\d+) \((\d+) items\)/) || []).slice(1).map(Number)"


def main():
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', args=['--no-sandbox'])
        page = browser.new_page()
        page.goto(URL, timeout=90000, wait_until='networkidle')
        while True:
            rows = page.evaluate(ROWS_JS)
            at, last, total = page.evaluate(PAGER_JS)
            print(f'page {at} of {last}: {len(rows)} rows', file=sys.stderr)
            out.extend(rows)
            if at == last:
                break
            page.locator('a.dxp-button:has(img[alt="Next"])').first.click()
            for _ in range(120):  # wait for the grid to show the next page
                page.wait_for_timeout(500)
                if page.evaluate(PAGER_JS)[0] == at + 1 and page.evaluate(ROWS_JS)[:1] != rows[:1]:
                    break
            else:
                sys.exit(f'the grid did not move past page {at}')
        browser.close()
    assert len(out) == total, f'read {len(out)} rows, the page reports {total}'
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print(f'{len(out)} rows written to {sys.argv[1]}')


if __name__ == '__main__':
    main()
