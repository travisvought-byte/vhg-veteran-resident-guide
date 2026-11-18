"""Build flyers.html, the printable-flyers download page, from data/flyers.json.

Usage: python3 scripts/build_flyers_page.py          # write flyers.html
       python3 scripts/build_flyers_page.py --check  # fail if flyers.html is out of date
To add a flyer: put its print source in flyers/src/<id>.html, add an entry to data/flyers.json,
run `node scripts/build_flyers.cjs` (PDFs and previews), then this script.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def esc(s):
    return html.escape(str(s), quote=True)


def card(f):
    fid = f['id']
    links = [f'<a class="button" href="flyers/{fid}.pdf" download>Download PDF<span class="sr"> of the {esc(f["title"])}</span></a>']
    if f.get('two_up'):
        links.append(f'<a class="button secondary" href="flyers/{fid}-2up.pdf" download>Two per letter page (PDF)<span class="sr">, {esc(f["title"])}</span></a>')
    links.append(f'<a href="{esc(f["guide"])}">Open the {esc(f["guide_name"])}</a>')
    return (f'<article class="flyer" id="{fid}">'
            f'<a class="preview" href="flyers/{fid}.pdf"><img src="flyers/{fid}.png" alt="{esc(f["alt"])}" '
            f'width="{round(f["width_in"] * 96)}" height="{round(f["height_in"] * 96)}" loading="lazy"></a>'
            f'<div><h2>{esc(f["title"])}</h2><p class="size">{esc(f["size"])}</p><p>{esc(f["use"])}</p>'
            f'<p class="links">{" ".join(links)}</p></div></article>')


def page():
    data = json.loads((ROOT / 'data/flyers.json').read_text())
    for f in data['flyers']:
        for name in [f['id'] + '.pdf', f['id'] + '.png'] + ([f['id'] + '-2up.pdf'] if f.get('two_up') else []):
            assert (ROOT / 'flyers' / name).is_file(), 'missing flyers/' + name + ' (run node scripts/build_flyers.cjs)'
        assert (ROOT / 'flyers/src' / (f['id'] + '.html')).is_file(), 'missing print source for ' + f['id']
    cards = '\n'.join(card(f) for f in data['flyers'])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Printable flyers | Veteran Resident Resource Guide</title>
<meta name="description" content="Free printable flyers from Veteran Home Guardians. Download, print and post them so families can find help.">
<link rel="canonical" href="https://guide.vethomeguard.org/flyers.html">
<link rel="stylesheet" href="assets/family-guide.css">
<style>
.flyers{{max-width:1160px;margin:auto;padding:24px}}
.flyer{{display:grid;grid-template-columns:minmax(0,240px) minmax(0,1fr);gap:24px;align-items:start;padding:22px 0;border-bottom:1px solid var(--line)}}
.flyer h2{{margin:0 0 4px}}.flyer .size{{margin:0 0 10px;font-weight:650;color:var(--green)}}
.preview img{{display:block;width:100%;height:auto;border:1px solid var(--line);box-shadow:0 1px 4px rgba(0,0,0,.12)}}
.links{{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center}}
.button.secondary{{background:var(--navy)}}
.tips{{background:#eef3f0;border-radius:6px;padding:12px 20px;margin-top:22px}}
@media (max-width:640px){{.flyer{{grid-template-columns:minmax(0,1fr)}}.preview img{{max-width:280px}}}}
</style>
<script src="assets/analytics.js" defer></script></head><body>
<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="family-guide.html">Family Guide</a><a href="disability-advocacy.html">Disability rights &amp; advocacy</a></nav>
<div class="hero"><p class="eyebrow">FREE TO PRINT AND SHARE</p><h1>Printable flyers</h1><p>Post or hand these out so families can find help. Every flyer has a QR code that opens the guide on a phone.</p></div></header>
<main class="flyers" id="main">
{cards}
<section class="tips" aria-labelledby="tips-title"><h2 id="tips-title">Printing tips</h2><ul>
<li>Print at <strong>100%</strong> or <strong>Actual size</strong>, not "Fit to page," so the QR code stays sharp.</li>
<li>Turn on <strong>Background graphics</strong> (or "Print backgrounds") to keep the colors.</li>
<li>Black and white works too. The QR code and phone numbers stay readable.</li>
</ul></section>
</main>
<footer class="flyers"><p>Free from Veteran Home Guardians. You may print, copy and share these flyers. Questions or a flyer you need: <a href="mailto:travis@vethomeguard.org?subject=Printable%20flyers">travis@vethomeguard.org</a></p></footer>
</body></html>
'''


if __name__ == '__main__':
    out = page()
    target = ROOT / 'flyers.html'
    if '--check' in sys.argv:
        if not target.is_file() or target.read_text() != out:
            sys.exit('flyers.html is out of date: run python3 scripts/build_flyers_page.py')
        print('flyers.html is up to date.')
    else:
        target.write_text(out)
        print('Built flyers.html with', out.count('<article'), 'flyers.')
