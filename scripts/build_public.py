#!/usr/bin/env python3
"""Refresh static projections from canonical JSON; --check detects drift without writes."""
import argparse
import json
import re
from pathlib import Path
from pa_edition import make_pa, pennsylvania_resources

ROOT = Path(__file__).resolve().parents[1]

def outputs():
    resources = json.loads((ROOT / 'prototype-data.json').read_text())
    counties = json.loads((ROOT / 'data/public/ohio-county-veterans-offices.json').read_text())
    html = (ROOT / 'index.html').read_text()
    for name, value in [('DATA', resources), ('COUNTIES', counties)]:
        # Escape HTML parser boundaries inside strings while retaining valid JSON.
        payload = json.dumps(value, ensure_ascii=True).replace('<', '\\u003c')
        html, n = re.subn(r'const ' + name + r'=.*?;\n', lambda _: 'const ' + name + '=' + payload + ';\n', html, count=1)
        if n != 1:
            raise ValueError('Missing embedded ' + name)
    regional = sorted((r for r in resources if r.get('regional_role')), key=lambda r: r['program_id'])
    pa_resources = pennsylvania_resources(ROOT, resources)
    pa_counties = json.loads((ROOT / 'data/public/pennsylvania-county-veterans-offices.json').read_text())
    share = (ROOT / 'share.html').read_text()
    pa_share = share.replace('Ohio', 'Pennsylvania').replace('88', '67').replace('href="index.html"', 'href="pa.html"')
    pa_share = pa_share.replace('https://travisvought-byte.github.io/vhg-veteran-resident-guide/', 'https://travisvought-byte.github.io/vhg-veteran-resident-guide/pa.html')
    pa_share = pa_share.replace('assets/guide-qr.svg', 'assets/guide-qr-pa.svg')
    pa_share = pa_share.replace('href="share.html">Pennsylvania', 'href="share.html">Ohio')
    pa_share = pa_share.replace('local veterans office, aging agency and long-term-care ombudsman contacts', 'county veterans office contacts and statewide aging, disability and ombudsman referral routes')
    return {
        'index.html': html,
        'data/public/ohio-regional-referrals.json': json.dumps(regional, indent=2, ensure_ascii=False) + '\n',
        'pa.html': make_pa(html, pa_resources, pa_counties),
        'data/public/pennsylvania-resources.json': json.dumps(pa_resources, indent=2, ensure_ascii=False) + '\n',
        'share-pa.html': pa_share,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    drift = []
    for name, text in outputs().items():
        path = ROOT / name
        if not path.is_file() or path.read_text() != text:
            drift.append(name)
            if not args.check:
                path.write_text(text)
    if args.check and drift:
        parser.exit(1, 'Out of sync: ' + ', '.join(drift) + '. Run python3 scripts/build_public.py\n')
    print('Public projections are synchronized.' if args.check else 'Updated: ' + (', '.join(drift) or 'already synchronized'))
