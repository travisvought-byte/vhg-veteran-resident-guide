"""The family of free guides: a "More free guides" line in the footer of every page (November 28, 2026).

Owner direction, November 28, 2026: guides link to each other by how visitors identify, and the sites promote
each other as fully as they can. Every generated page of the Veteran Resource Guide, and every Find Bingo page
built here, ends its footer with one line naming every other guide in the family and who it is for. The line
sits between <!--related--> and <!--/related--> so a rebuild replaces it instead of adding a second one.

a11y_finish.finish_named() calls add() for every generated page, so build_public.py and the scripts that write
their own pages (build_flyers_page.py, build_packets.py) agree. Left out on purpose: the printable flyer and
packet sources (flyers/, kept as their PDFs show them), the text-only country pages (world/lite/, kept as small
as possible for slow connections; their full pages carry the line), test fixtures, and forwarding stubs with no
<main>. The Spanish page gets the line in Spanish.

The identity-based "More help made for you" list is in data/landing/chooser.json (scripts/landing.py), and the
links inside topic pages are in their own data (data/justice.json, templates/family-guide.html,
scripts/build_county_pages.py).
"""
import re
from html import escape
from urllib.parse import urlsplit

# Every guide in the family, in the order the footers list them: key, name, live address, who it is for.
GUIDES = [
    ('vets', 'Veteran Resource Guide', 'https://guide.vethomeguard.org/', 'veterans and their families'),
    ('mob', 'Mobility Talk', 'https://mobilitytalk.org/', 'disability and mobility help'),
    ('ymt', 'Yoga Mom Talk', 'https://www.yogamomtalk.com/', 'moms, parents and families'),
    ('nina', "Nina's Map", 'https://ninas-map.com/', 'Native and Indigenous people'),
    # Abuse of Office covers Ohio only, so a national site says so.
    ('aoo', 'Abuse of Office', 'https://abuseofoffice.org/', 'rights with police, jails and courts in Ohio'),
    ('reefer', 'The Reefer', 'https://the-reefer.com/', 'cannabis laws and help in every state'),
    ('earth', 'Earth Rules', 'https://earthrules.org/', 'everyday adult know-how'),
    ('bingo', 'Find Bingo', 'https://www.findbingo.org/', 'bingo games and senior centers near you'),
]
# The same line in Spanish, for the Spanish page. The guides themselves are in English, and the line says so.
SPANISH = {
    'vets': 'veteranos y sus familias',
    'mob': 'ayuda con la discapacidad y la movilidad',
    'ymt': 'mamás, papás y familias',
    'nina': 'personas nativas e indígenas',
    'aoo': 'derechos ante la policía, las cárceles y los tribunales de Ohio',
    'reefer': 'leyes del cannabis y ayuda en cada estado',
    'earth': 'consejos prácticos para la vida adulta',
    'bingo': 'bingo y centros para personas mayores cerca de usted',
}
# Other real sites of the family, linked only in context (not in the footer line): OhioWeed (Ohio cannabis guide).
CONTEXT = [('ohioweed', 'OhioWeed', 'https://ohioweed.org/', 'the Ohio cannabis guide')]
# Every site a "More help made for you" option may point at.
HOSTS = {urlsplit(url).netloc for _, _, url, _ in GUIDES + CONTEXT}
OPEN, CLOSE = '<!--related-->', '<!--/related-->'
_OLD = re.compile(re.escape(OPEN) + '.*?' + re.escape(CLOSE), re.S)

# Pages built here that belong to Find Bingo (findbingo.org): their line names the Veteran Resource Guide and
# leaves out Find Bingo. bingo.html is the Ohio finder's build source; on the live guide it forwards to Find Bingo.
FINDBINGO = ('bingo-site/', 'findbingo-site/')
SKIP = ('tests/', 'flyers/', 'world/lite/')


def site_of(name):
    """Which guide a generated page belongs to, by its published path."""
    return 'bingo' if name.startswith(FINDBINGO) or name == 'bingo.html' else 'vets'


def line(site='vets', lang='en', extra_class=''):
    """The "More free guides" line for one site's pages: every other guide, in order, with who it is for."""
    parts = []
    for key, name, url, who in GUIDES:
        if key == site:
            continue
        who = SPANISH[key] if lang == 'es' else who
        parts.append(f'<a href="{escape(url)}">{escape(name, quote=False)}</a> ({escape(who, quote=False)})')
    lead = 'Más guías gratuitas (en inglés): ' if lang == 'es' else 'More free guides: '
    cls = ('related ' + extra_class).strip()
    return f'{OPEN}<p class="{cls}">{lead}{" · ".join(parts)}</p>{CLOSE}'


def add(name, html):
    """One page with the line at the end of its footer (or, on a page with no footer, at the end of <main>)."""
    if not (name.endswith('.html') and isinstance(html, str)) or name.startswith(SKIP):
        return html
    if not re.search(r'<main\b', html):
        return html  # Forwarding stubs and verification files: nothing to add to.
    site = site_of(name)
    lang = 'es' if re.search(r'<html\b[^>]*\blang="es', html) else 'en'
    stripped = _OLD.sub('', html)
    end = stripped.rfind('</footer>')
    if end >= 0:
        # Find Bingo's footer lines are kept off paper; so is this one.
        extra = 'noprint' if site == 'bingo' and 'class="noprint"' in stripped else ''
        return stripped[:end] + line(site, lang, extra) + stripped[end:]
    end = stripped.rfind('</main>')
    if end < 0 or name.endswith('poster.html'):
        return html  # The bingo poster is a print-only page.
    # Pages with no footer (the sharing kits, the assistance tool): the same line in the page's own small-print
    # style, kept off the printed flyer where the page has a screen-only class.
    small = next((c for c in ('note', 'meta') if re.search(r'\.' + c + r'\s*\{', stripped)), '')
    screen = 'screen-only' if re.search(r'\.screen-only\s*\{', stripped) else ''
    return stripped[:end] + line(site, lang, ' '.join(c for c in (small, screen) if c)) + stripped[end:]
