#!/usr/bin/env python3
"""Rebuild data/public/mississippi-bingo-licenses.json from the Mississippi Gaming Commission's licensee map.

The commission's Charitable Gaming page links "Locate Charitable Gaming Licensees", a Mapline map:
https://www.msgamingcommission.com/charitable_gaming. The map's data (each licensee's charity, bingo hall,
physical address, license number and expiration, and games played) loads from Mapline's own service when
the map opens, so it is read in a headless browser:

    python3 scripts/import_mississippi_bingo.py --reviewed 2026-11-17            # opens the map (Playwright + Chrome)
    python3 scripts/import_mississippi_bingo.py --saved map-layer.json --reviewed 2026-11-17

Kept: licensees whose games include bingo, with a Mississippi street address and a license still current on
the review date. Distributors and manufacturers (out-of-state addresses) drop out on their own. Left out on
purpose: the contact person, email and phone, which sit together on the map and may be personal; cards offer
a phone lookup instead. Counties come from the U.S. Census Geocoder (bingo_counties.py).
"""
import argparse, asyncio, datetime, json, os, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bingo_counties import counties  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/public/mississippi-bingo-licenses.json'
MAP = 'https://app.mapline.com/map/map_707213b0/K3l2SldYemdVcnJSYkF4c0RUWWE2YzRubkZmR2IrRnNWYjJqel'
PAGE = 'https://www.msgamingcommission.com/charitable_gaming'


async def _read_map(chrome):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        proxy = {'server': os.environ['HTTPS_PROXY']} if os.environ.get('HTTPS_PROXY') else None
        browser = await p.chromium.launch(executable_path=chrome, headless=True, proxy=proxy, args=['--no-sandbox'])
        page = await (await browser.new_context()).new_page()
        found = []

        async def keep(resp):
            if '/layers/' in resp.url and 'DataSource' in resp.url:
                try:
                    found.append(json.loads(await resp.text()))
                except Exception:
                    pass
        page.on('response', keep)
        await page.goto(MAP, wait_until='networkidle', timeout=90000)
        await page.wait_for_timeout(4000)
        await browser.close()
    assert found, 'the map did not load its data'
    return found[0]


def rows(layer):
    ds = layer['DataSource']
    names = {h['Id']: h['Name'] for h in ds['Headers']}
    cols = [names.get(c, c) for c in ds['Records']['0'].split(',')]
    recs = [dict(zip(cols, r)) for r in ds['Records']['1']]
    modified = max(datetime.datetime.strptime(r['DateModified'].split(' ')[0], '%m/%d/%Y').date() for r in recs)
    return recs, modified


def _date(text):
    m, d, y = (int(x) for x in text.split('/'))
    return datetime.date(y + 2000 if y < 100 else y, m, d)


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def build(recs, reviewed, modified):
    today = datetime.date.fromisoformat(reviewed)
    out, ids, skipped = [], set(), []
    for r in recs:
        if 'bingo' not in (r.get('Games Played') or '').lower():
            continue
        lic = r.get('License Number and Expiration') or ''
        num = re.search(r'\b(\d\d-\d{5}|\d{5})\b', lic)
        exp = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', lic)
        addr = re.sub(r'\s*,\s*', ', ', (r.get('Physical Address') or '').strip())
        m = re.fullmatch(r'(.+), ([^,]+), ?MS (\d{5})(?:-\d{4})?', addr)
        name = (r.get('Bingo Hall') or r.get('Charity') or '').strip()
        if not (num and exp and m and name) or _date(exp.group(1)) < today:
            skipped.append(f'{name or r.get("Charity")} | {addr or "no address"} | {lic or "no license"}')
            continue
        rid = 'ms-' + _slug(num.group(1))
        if rid in ids:
            skipped.append(f'{name} | duplicate license {num.group(1)}')
            continue
        ids.add(rid)
        city = m.group(2).strip()
        out.append({'id': rid, 'state': 'MS', 'name': name, 'organizations': [r['Charity'].strip()] if r.get('Charity') else [],
                    'address': f'{m.group(1).strip()}, {city}, MS {m.group(3)}', 'city': city, 'zip': m.group(3), 'county': None,
                    'license_number': num.group(1), 'license_type': 'charitable bingo license', 'license_expires': _date(exp.group(1)).isoformat(),
                    'reviewed_on': reviewed,
                    'sources': [{'url': PAGE, 'reviewed_on': reviewed,
                                 'scope': f'Mississippi Gaming Commission, Locate Charitable Gaming Licensees map (last updated {modified.strftime("%B")} {modified.day}, {modified.year}): '
                                          'charity, bingo hall, physical address, license number and expiration, and games played'}]})
    return out, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--saved', help='a saved copy of the map layer JSON; otherwise the map is opened in a browser')
    ap.add_argument('--chrome', default='/usr/bin/google-chrome')
    ap.add_argument('--reviewed', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    layer = json.loads(pathlib.Path(a.saved).read_text()) if a.saved else asyncio.run(_read_map(a.chrome))
    recs, modified = rows(layer)
    built, skipped = build(recs, a.reviewed, modified)
    known = {r['address']: r['county'] for r in json.loads(OUT.read_text())} if OUT.exists() else {}
    for r in built:
        r['county'] = known.get(r['address'])
    need = [(r, r['address'].split(', ')[0]) for r in built if not r['county']]
    if need:
        for rid, (county, how) in counties(need, 'MS', '28', ROOT).items():
            rec = next(x for x in built if x['id'] == rid)
            rec['county'] = county
            if how != 'address':
                print(f'county from {how}: {rec["address"]} -> {county}')
    missing = [r['address'] for r in built if not r['county']]
    if missing:
        sys.exit('No county found for:\n  ' + '\n  '.join(missing))
    OUT.write_text(json.dumps(sorted(built, key=lambda r: (r['county'], r['city'], r['name'])), ensure_ascii=False, indent=1) + '\n')
    print(f'{OUT.relative_to(ROOT)} written. Map last updated {modified}; set list_as_of to it.')
    if skipped:
        print('Left out:\n  ' + '\n  '.join(skipped))


if __name__ == '__main__':
    main()
