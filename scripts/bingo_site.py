"""Build the standalone Ohio Bingo Finder site published at https://bingo.vethomeguard.org/.

The finder page is generated from the same records as the guide's bingo.html, so the
guide repository stays the single source of truth. Everything is written to bingo-site/,
which the travisvought-byte/Ohio-Bingo repository mirrors and serves with GitHub Pages.
"""
import json
import re
from html import escape

SITE = 'https://bingo.vethomeguard.org'
GUIDE = 'https://guide.vethomeguard.org'
EMAIL = 'travis@vethomeguard.org'
LOGO = 'assets/vhg-logo.png'  # copied into bingo-site/assets; og:image uses SITE + '/' + LOGO
DONATE = 'https://www.vethomeguard.org/donate.html'
ABOUT_VHG = 'Veteran Home Guardians, an Ohio nonprofit that visits veterans in nursing homes'


def _replace(page, old, new, count=None):
    found = page.count(old)
    assert found and (count is None or found == count), (old, found)
    return page.replace(old, new)


def finder_stats(page):
    records = json.loads(re.search(r'const BINGO=(\[.*?\]);', page, re.S).group(1))
    listed = sum(r['category'] in ('licensed', 'charitable') for r in records)
    centers = sum(r['category'] in ('center', 'senior') for r in records)
    timed = sum(any(r.get(k) for k in ('session_days', 'session_dates', 'session_monthly')) for r in records)
    return {'total': len(records), 'counties': len({r['county'] for r in records}),
            'listed': listed, 'centers': centers, 'timed': timed}


def standalone_finder(page):
    """Turn the guide's bingo page into the root page of bingo.vethomeguard.org."""
    page = _replace(page, '<title>Ohio Bingo and Senior Centers | Veteran Home Guardians</title>',
                    '<title>Ohio Bingo Finder: bingo games and senior centers near you | Veteran Home Guardians</title>', 1)
    page = _replace(page, '<link rel="canonical" href="https://guide.vethomeguard.org/bingo.html">',
                    f'<link rel="canonical" href="{SITE}/">'
                    '<meta property="og:type" content="website"><meta property="og:site_name" content="Ohio Bingo Finder">'
                    '<meta property="og:title" content="Ohio Bingo Finder">'
                    '<meta property="og:description" content="Free: find bingo games and senior centers near you anywhere in Ohio, by ZIP code, day and time.">'
                    f'<meta property="og:url" content="{SITE}/"><meta property="og:image" content="{SITE}/{LOGO}">', 1)
    # Printed flyers name the address people should type.
    page = _replace(page, 'guide.vethomeguard.org/bingo.html<br>', 'bingo.vethomeguard.org<br>', 2)
    page = page.replace('https://guide.vethomeguard.org/bingo.html', SITE + '/')
    # The finder is now the site root.
    page = _replace(page, 'href="bingo.html?', 'href="./?')
    page = _replace(page, 'action="bingo.html"', 'action="./"', 1)
    page = _replace(page, 'href="bingo.html"', 'href="./"')
    page = _replace(page, "full='bingo.html?zip='", "full='./?zip='", 1)
    assert not re.search(r"""["'=]bingo\.html""", page), 'unconverted finder link'
    # Pages and files that stay in the guide.
    page = _replace(page, 'href="index.html?view=community"', f'href="{GUIDE}/?view=community"', 1)
    page = _replace(page, 'href="index.html"', f'href="{GUIDE}/"', 1)
    page = _replace(page, 'href="facilities.html"', f'href="{GUIDE}/facilities.html"', 1)
    page = _replace(page, 'href="data/public/', f'href="{GUIDE}/data/public/')
    page = _replace(page, '<h1>Ohio Bingo &amp; Senior Centers</h1>',
                    '<p class="site-name">Ohio Bingo Finder · bingo.vethomeguard.org</p><h1>Ohio Bingo &amp; Senior Centers</h1>', 1)
    page = _replace(page, '.source-note{', '.site-name{margin:10px 0 0;font-size:14px;letter-spacing:.04em;text-transform:uppercase;opacity:.85}.source-note{', 1)
    page = _replace(page, '</footer>', '<p><a href="partners.html">Partner with the Ohio Bingo Finder</a> · '
                    '<a href="poster.html">Print a poster</a> · '
                    f'<a href="{GUIDE}/">Veteran Resident Resource Guide</a></p></footer>', 1)
    return page.replace('</body>', '<script defer src="assets/analytics.js"></script></body>', 1)


STYLE = '''
:root{--navy:#183449;--green:#335947;--gold:#bb8e36;--paper:#f5f3ed;--line:#d9dfda;--ink:#20313a}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}
a{color:#215b76;text-underline-offset:3px}h1,h2{font-family:Georgia,serif;color:var(--navy);line-height:1.2}
header{background:var(--navy);color:#fff;padding:24px max(20px,calc((100vw - 1060px)/2))}header a{color:#fff}
header h1{color:#fff;font-size:clamp(28px,5vw,42px);margin:10px 0}header p{max-width:760px}
main{max-width:1060px;margin:auto;padding:24px 20px}
.brand{display:flex;align-items:center;gap:12px;font-weight:650}.brand img{width:48px;height:48px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:8px 0 28px}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:28px;color:var(--navy);font-family:Georgia,serif}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
article{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px}article h2{margin-top:0;font-size:23px}
.button{display:inline-flex;align-items:center;min-height:46px;padding:0 18px;margin:6px 10px 0 0;border-radius:24px;background:var(--green);color:#fff;text-decoration:none;font-weight:650}
.button.alt{background:#fff;color:var(--green);border:1px solid var(--green)}
.note{background:#fff8e7;border-left:4px solid var(--gold);padding:12px 16px}
.share{display:grid;grid-template-columns:180px 1fr;gap:20px;align-items:center}.share img{width:180px;height:180px;background:#fff}
textarea{width:100%;font:inherit;padding:12px;border:1px solid #abb8b1;border-radius:6px;min-height:96px}
footer{max-width:1060px;margin:0 auto;padding:20px;font-size:14px;border-top:1px solid var(--line)}
:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.grid,.share{grid-template-columns:1fr}}
'''


def _shell(title, description, path, body, extra_style=''):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}">'
            f'<link rel="canonical" href="{SITE}/{path}">'
            '<meta property="og:type" content="website"><meta property="og:site_name" content="Ohio Bingo Finder">'
            f'<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}">'
            f'<meta property="og:url" content="{SITE}/{path}"><meta property="og:image" content="{SITE}/{LOGO}">'
            f'<style>{STYLE}{extra_style}</style></head><body>{body}'
            '<script defer src="assets/analytics.js"></script></body></html>\n')


def partners_page(stats):
    blurb = ('Looking for bingo near you? The free Ohio Bingo Finder lists bingo games and senior centers in all 88 Ohio counties. '
             'Search by ZIP code, day and time: bingo.vethomeguard.org')
    sponsor = f'mailto:{EMAIL}?subject=Ohio%20Bingo%20Finder%20partnership'
    body = f'''<header><a class="brand" href="./"><img src="{LOGO}" alt="" width="48" height="48"><span>Ohio Bingo Finder</span></a>
<h1>Partner with the Ohio Bingo Finder</h1>
<p>A free statewide finder that helps seniors, veterans, families and activity directors find bingo games and senior centers near them. It is built and kept up by {ABOUT_VHG}.</p>
<p><a class="button" href="./">Open the finder</a></p></header>
<main>
<section class="stats" aria-label="What the finder covers">
<div class="stat"><b>{stats['listed']}</b>state-listed bingo locations</div>
<div class="stat"><b>{stats['centers']}</b>senior and community centers</div>
<div class="stat"><b>{stats['counties']}</b>Ohio counties covered</div>
<div class="stat"><b>{stats['timed']}</b>with published schedules on file</div>
</section>
<p class="note">Listings are free and always will be. Inclusion never depends on donations, partnership or sponsorship.</p>
<div class="grid">
<article id="organizers"><h2>Run a bingo game?</h2>
<p>American Legion and VFW posts, booster clubs, churches, fire departments and other licensed charities: get your game in front of players and the activity staff who plan resident outings.</p>
<p>Send your game days, door and first-game times, packet prices, a public phone or Facebook page, and whether the entrance is step-free and groups are welcome.</p>
<p><a class="button" href="./#submit-details">Add or update your game</a><a class="button alt" href="./?organizer=1">Print a sign for your hall</a></p></article>
<article id="facilities"><h2>Nursing homes and senior living</h2>
<p>Activity directors and social workers can print a one-page list of games and senior centers near their building, with a QR code to the full finder. It works well on activity boards, in family packets and in resident newsletters.</p>
<p><a class="button" href="./#flyer-maker">Print a flyer for your building</a></p></article>
<article id="community"><h2>Senior centers, libraries and churches</h2>
<p>Hang the poster, link to the finder from your website or newsletter, and send us your own program schedule so it shows up for people searching nearby.</p>
<p><a class="button" href="poster.html">Print the poster</a><a class="button alt" href="mailto:{EMAIL}?subject=Ohio%20Bingo%20Finder%3A%20our%20programs">Send your schedule</a></p></article>
<article id="sponsors"><h2>Community partner halls</h2>
<p>Instant bingo halls run by veteran's, fraternal and sporting organizations must give part of their net profit to a qualifying charity. Halls that name Veteran Home Guardians as a recipient, for any share, become Community Partners.</p>
<p>Partners are recognized on this page and on their listing. We help partners stay current on the distribution rules, send updates on our work, and visit senior veterans in nursing homes in their area.</p>
<p>We do not sell advertising to halls. Every hall gets the same free listing whether it partners with us or not.</p>
<p><a class="button" href="mailto:{EMAIL}?subject=Ohio%20Bingo%20Finder%3A%20community%20partner">Become a community partner</a><a class="button alt" href="distributions.html">Read the distribution rules</a></p></article>
</div>
<section id="share-kit"><h2>Share the finder</h2>
<div class="share"><img src="assets/bingo-qr.svg" alt="QR code that opens bingo.vethomeguard.org" width="180" height="180">
<div><p><strong>bingo.vethomeguard.org</strong></p><p>Use this QR code on posters, newsletters and slides. <a href="assets/bingo-qr.svg" download>Download the QR code</a></p>
<label for="share-text"><strong>Copy for a newsletter or Facebook post</strong></label><textarea id="share-text" readonly>{escape(blurb)}</textarea></div></div>
</section>
</main>
<footer><p>Ohio Bingo Finder · A free community resource from Veteran Home Guardians · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GUIDE}/">Veteran Resident Resource Guide</a></p></footer>'''
    return _shell('Partner with the Ohio Bingo Finder | Veteran Home Guardians',
                  'Bingo halls, care facilities, senior centers and sponsors: list your game free, print flyers and posters, and partner with the free Ohio Bingo Finder.',
                  'partners.html', body)


AG_ENFORCEMENT = 'https://charitable.ohioago.gov/Charitable-Bingo/Bingo-Enforcement'
ORC_DISTRIBUTION = 'https://codes.ohio.gov/ohio-revised-code/section-2915.101'
OAC_ADJUSTMENT = 'https://codes.ohio.gov/ohio-administrative-code/rule-109:1-4-21'


def distributions_page():
    body = f'''<header><a class="brand" href="./"><img src="{LOGO}" alt="" width="48" height="48"><span>Ohio Bingo Finder</span></a>
<h1>Instant bingo distributions: what Ohio law requires</h1>
<p>A plain-English summary for post commanders, finance officers and bingo volunteers. It follows <a href="{ORC_DISTRIBUTION}">Ohio Revised Code 2915.101</a>. It is not legal advice. When in doubt, ask the Ohio Attorney General&rsquo;s Charitable Law Section.</p></header>
<main>
<article><h2>Veteran&rsquo;s, fraternal and sporting organizations</h2>
<p>This applies to net profit from paper and electronic instant bingo (pull-tabs), each calendar year.</p>
<h3>Up to the threshold</h3>
<ul><li>At least <strong>25%</strong> goes to a qualifying charity (see ORC 2915.01(V)(1)) or a government agency.</li>
<li>Up to <strong>75%</strong> may be kept for the organization&rsquo;s allowed bingo expenses.</li></ul>
<p>The statute sets the threshold at $250,000 and lets the Attorney General raise it for inflation. Check <a href="{OAC_ADJUSTMENT}">OAC 109:1-4-21</a> for the current amount.</p>
<h3>Above the threshold</h3>
<ul><li>At least <strong>50%</strong> goes to a qualifying charity or a government agency.</li>
<li>Up to <strong>5%</strong> may go to the organization&rsquo;s own charitable purposes or a community action agency.</li>
<li>Up to <strong>45%</strong> may be kept for allowed expenses.</li></ul>
<p>Anything not distributed or kept for those purposes must go to a qualifying charity.</p></article>
<article><h2>Other charitable organizations</h2>
<p>Churches, schools, booster clubs and other charities that run instant bingo must give <strong>100%</strong> of net profit to a qualifying charity or a government agency.</p></article>
<article><h2>Pass-through charities</h2>
<p>The law allows a hall to give to a 501(c)(3) that makes donations to other organizations and lets donors advise where the money goes. Those donations still have to meet 501(c)(3) rules. Money that comes back to the hall for its own operations is not a charitable distribution.</p></article>
<article><h2>What gets halls in trouble</h2>
<ul><li>Paying the contracted charity less than the required amount</li>
<li>Bingo bank accounts that don&rsquo;t match the money collected</li>
<li>Paying unallowable expenses from bingo accounts</li>
<li>Missing required reports</li></ul>
<p>The Attorney General posts notices, settlements and orders on its <a href="{AG_ENFORCEMENT}">bingo enforcement page</a>. Problems are usually caught at annual inspections or license renewal.</p></article>
<article><h2>Questions</h2>
<p>Ohio Attorney General, Charitable Law Section: <a href="tel:614-466-3181">614-466-3181</a>.</p>
<p>To name Veteran Home Guardians as a recipient, or to ask how our community partnership works, email <a href="mailto:{EMAIL}?subject=Instant%20bingo%20distribution">{EMAIL}</a>. Every hall&rsquo;s listing stays free either way.</p>
<p><a class="button" href="partners.html">Community partners</a><a class="button alt" href="./">Open the finder</a></p></article>
</main>
<footer><p>Ohio Bingo Finder · A free community resource from Veteran Home Guardians · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GUIDE}/">Veteran Resident Resource Guide</a></p></footer>'''
    return _shell('Instant bingo distributions: what Ohio law requires | Ohio Bingo Finder',
                  'Plain-English guide to Ohio instant bingo distribution rules for veteran, fraternal and sporting organizations and other charities.',
                  'distributions.html', body, '\nmain article{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px;margin:0 0 18px}main article h2{margin-top:0}')


def poster_page(stats):
    style = '''
.poster{max-width:8.5in;margin:24px auto;background:#fff;border:1px solid var(--line);padding:.6in .7in;text-align:center}
.poster h1{font-size:60px;margin:.1in 0 .15in}.poster .lead{font-size:24px;margin:0 auto .25in;max-width:6.4in}
.poster .qr{width:3.4in;height:3.4in;margin:.1in auto}.poster .url{font-size:34px;font-weight:700;color:var(--navy);margin:.05in 0 .2in}
.poster .facts{font-size:19px;max-width:6.4in;margin:0 auto .2in}.poster .small{font-size:14px;color:#555}
.screen-only{max-width:8.5in;margin:16px auto 0;display:flex;gap:12px;flex-wrap:wrap}
@media print{body{background:#fff}.screen-only{display:none}.poster{border:0;margin:0;padding:0;max-width:none}@page{size:letter;margin:.5in}}
'''
    body = f'''<div class="screen-only"><button type="button" class="button" onclick="window.print()">Print this poster</button><a class="button alt" href="partners.html">Back to partners</a></div>
<section class="poster">
<p class="brand" style="justify-content:center"><img src="{LOGO}" alt="" width="48" height="48"><span>Veteran Home Guardians</span></p>
<h1>Find a bingo game near you</h1>
<p class="lead">Free Ohio Bingo Finder. Search by ZIP code, day and time.</p>
<img class="qr" src="assets/bingo-qr.svg" alt="QR code that opens bingo.vethomeguard.org">
<p class="url">bingo.vethomeguard.org</p>
<p class="facts">{stats['listed']} state-listed bingo locations and {stats['centers']} senior centers in all {stats['counties']} Ohio counties.<br>Run a game? List it free at the same address.</p>
<p class="small">A free community resource from {ABOUT_VHG}.</p>
</section>'''
    return _shell('Ohio Bingo Finder poster | Veteran Home Guardians',
                  'A printable poster for the free Ohio Bingo Finder at bingo.vethomeguard.org.',
                  'poster.html', body, style)


def not_found_page():
    body = f'''<header><a class="brand" href="/"><img src="{LOGO}" alt="" width="48" height="48"><span>Ohio Bingo Finder</span></a><h1>Page not found</h1></header>
<main><p>That page doesn't exist. <a class="button" href="/">Find a bingo game near you</a></p></main>'''
    page = _shell('Page not found | Ohio Bingo Finder', 'Find bingo games and senior centers near you in Ohio.', '404.html', body)
    return page.replace('src="assets/', 'src="/assets/')


README = '''# Ohio Bingo Finder

Live at **https://bingo.vethomeguard.org/**. A free finder for bingo games and senior centers across Ohio, from Veteran Home Guardians.

Every file in this folder is **generated**. Do not edit it here. The source of truth is
[vhg-veteran-resident-guide](https://github.com/travisvought-byte/vhg-veteran-resident-guide):
`scripts/bingo_site.py` builds `bingo-site/` from the same records as the guide's `bingo.html`
(`python3 scripts/build_public.py`). The Ohio-Bingo repository mirrors `bingo-site/` and serves it with GitHub Pages.
'''


def make_bingo_site(root, finder_page):
    stats = finder_stats(finder_page)
    files = {
        'bingo-site/index.html': standalone_finder(finder_page),
        'bingo-site/partners.html': partners_page(stats),
        'bingo-site/distributions.html': distributions_page(),
        'bingo-site/poster.html': poster_page(stats),
        'bingo-site/404.html': not_found_page(),
        'bingo-site/CNAME': 'bingo.vethomeguard.org\n',
        'bingo-site/.nojekyll': '',
        'bingo-site/README.md': README,
        'bingo-site/robots.txt': f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n',
        'bingo-site/sitemap.xml': ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                   + ''.join(f'  <url><loc>{SITE}/{p}</loc></url>\n' for p in ('', 'partners.html', 'distributions.html', 'poster.html'))
                                   + '</urlset>\n'),
        'bingo-site/assets/analytics.js': (root / 'assets/analytics.js').read_text(),
        'bingo-site/assets/vhg-logo.png': (root / 'assets/vhg-logo.png').read_bytes(),
        'bingo-site/assets/bingo-qr.svg': (root / 'assets/bingo-site-qr.svg').read_text(),
        'bingo-site/assets/bingo-submit-qr.svg': (root / 'assets/bingo-site-submit-qr.svg').read_text(),
    }
    return files
