"""County for bingo hall addresses, from the U.S. Census Geocoder. Shared by the state list importers.

counties(need, state, fips, root) takes [(record, street), ...] where each record has 'id', 'city' and
'zip', and returns {id: (county, how)}. It tries the address, then another hall in the same ZIP code,
then the centre of the ZIP code; `how` says which. County names drop " County"; Virginia's independent
cities keep the Census form, "Richmond city".
"""
import collections, csv, json, subprocess, tempfile, time, urllib.parse


def _curl(*args):
    return subprocess.run(['curl', '-sS', '-m', '240', *args], capture_output=True, text=True, check=True).stdout


def _json(url, tries=4):
    # The geocoder now and then answers with an error page; ask again before giving up.
    for attempt in range(tries):
        try:
            return json.loads(_curl(url))
        except (json.JSONDecodeError, subprocess.CalledProcessError):
            if attempt == tries - 1:
                raise
            time.sleep(3 * (attempt + 1))


def _short(name):
    return name[:-7] if name.endswith(' County') else name


def counties(need, state, fips, root):
    names = {}
    for line in _curl(f'https://www2.census.gov/geo/docs/reference/codes2020/cou/st{fips}_{state.lower()}_cou2020.txt').split('\n')[1:]:
        p = line.split('|')
        if len(p) > 4:
            names[p[2]] = _short(p[4])
    rows = {}
    for start in range(0, len(need), 1000):  # the batch service takes up to 10,000; smaller batches answer faster
        part = need[start:start + 1000]
        with tempfile.NamedTemporaryFile('w', suffix='.csv', newline='') as f:
            csv.writer(f).writerows([start + i, street, rec['city'], state, rec['zip']] for i, (rec, street) in enumerate(part))
            f.flush()
            for r in csv.reader(_curl('-F', f'addressFile=@{f.name}', '-F', 'benchmark=Public_AR_Current', '-F', 'vintage=Current_Current',
                                      'https://geocoding.geo.census.gov/geocoder/geographies/addressbatch').splitlines()):
                rows[int(r[0])] = r
    found, by_zip = {}, collections.defaultdict(set)
    for i, (rec, _) in enumerate(need):
        r = rows.get(i)
        if r and r[2] == 'Match' and len(r) > 9 and r[8] == fips:
            found[rec['id']] = (names[r[9]], 'address')
            by_zip[rec['zip']].add(names[r[9]])
    centroids = json.loads((root / 'data/public/us-zip-centroids.json').read_text())
    for rec, _ in need:
        if rec['id'] in found:
            continue
        if len(by_zip[rec['zip']]) == 1:
            found[rec['id']] = (next(iter(by_zip[rec['zip']])), 'another hall in the same ZIP code')
        elif rec['zip'] in centroids:
            lat, lon = centroids[rec['zip']]
            q = urllib.parse.urlencode({'x': lon, 'y': lat, 'benchmark': 'Public_AR_Current', 'vintage': 'Current_Current', 'layers': 'Counties', 'format': 'json'})
            g = _json('https://geocoding.geo.census.gov/geocoder/geographies/coordinates?' + q)['result']['geographies']['Counties']
            if g and g[0]['STATE'] == fips:
                found[rec['id']] = (_short(g[0]['NAME']), 'the centre of the ZIP code')
    return found
