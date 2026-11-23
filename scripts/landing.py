"""Landing text: each entry page speaks to the person most likely to arrive on it.

data/landing/states.json holds the home page and one entry per state: a short title hook, an intro of a
sentence or two written to that state's veterans and families, a search description and the programs the
intro names (mentions). data/landing/pages.json holds the other entry pages (facilities, flyers, sharing
kits and so on). data/landing/chooser.json is the "I'm here as..." chooser on the home and state pages.

Every program an intro names must be one of that state's own records, and intros carry no numbers, so they
cannot drift into counts of listings. Run by scripts/build_public.py through unified_guide.py and apply_pages().
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://guide.vethomeguard.org/'
LOGO = BASE_URL + 'assets/vhg-logo.png'


def _load(name, root=ROOT):
    return json.loads((root / 'data/landing' / name).read_text(encoding='utf-8'))


def e(text):
    return escape(text or '', quote=True)


def text_html(text):
    """Text between tags: apostrophes stay readable in the page source."""
    return escape(text or '', quote=False)


def _check_text(where, text, limit):
    assert text and text.strip() == text, where + ': empty or padded'
    assert len(text) <= limit, f'{where}: {len(text)} characters (limit {limit})'
    # Landing text describes who the page is for; it never states counts of listings.
    assert not re.search(r'\b\d[\d,]*\b', text), where + ': no numbers in landing text'


def home(root=ROOT):
    h = _load('states.json', root)['home']
    for key, limit in (('title', 90), ('intro', 320), ('description', 170), ('eyebrow', 70)):
        _check_text('home ' + key, h[key], limit)
    return {'title': h['title'], 'h1': e(h['h1']), 'eyebrow': h['eyebrow'], 'intro': h['intro'],
            'description': h['description'], 'og_title': h.get('og_title', h['title'])}


def state(code, name, records, root=ROOT):
    """The landing for one state's page, checked against that state's own records."""
    s = _load('states.json', root)['states'][code]
    ids = {r['program_id'] for r in records}
    missing = [m for m in s['mentions'] if m not in ids]
    assert not missing, f'{code}: landing names programs it does not list: {missing}'
    assert s['mentions'], code + ': name at least one of the state\'s own programs'
    place = 'Washington, DC' if code == 'DC' else name
    title = f'{name} Veteran Resource Guide: {s["title_hook"]}'
    for key, value, limit in (('title', title, 82), ('intro', s['intro'], 320), ('description', s['description'], 170)):
        _check_text(code + ' ' + key, value, limit)
    assert name in s['description'], code + ': description names the state'
    return {'title': title, 'h1': e(name) + ' Veteran<br>Resource Guide',
            'eyebrow': s.get('eyebrow') or f'For {name} veterans and families',
            'intro': s['intro'], 'description': s['description'], 'og_title': f'Help for {place} veterans and their families | VHG'}


def states_codes(root=ROOT):
    return set(_load('states.json', root)['states'])


def chooser(code, root=ROOT):
    """The "I'm here as..." chooser. Options for other states are kept in the page, hidden, so switching
    state in place shows the right ones (assets/guide-runtime.js)."""
    c = _load('chooser.json', root)
    items = []
    for o in c['options']:
        attrs = ''
        if o.get('view'):
            href = '?view=' + o['view'] + '#directory'
            attrs += ' data-view="' + e(o['view']) + '"'
        elif o.get('help'):
            href = '?help=1#helper-guide'
            attrs += ' data-help'
        else:
            href = o['href']
            if not href.startswith('#'):
                target = href + ('index.html' if href.endswith('/') else '')
                assert (root / target).is_file(), o['id'] + ': chooser points at a missing page ' + href
        if o.get('family'):
            attrs += ' data-family-route'
        hidden = ''
        if o.get('states'):
            attrs += ' data-states="' + e(' '.join(o['states'])) + '"'
            hidden = '' if code in o['states'] else ' hidden'
        items.append(f'<li{hidden}><a href="{e(href)}" data-who="{e(o["id"])}"{attrs}><strong>{text_html(o["label"])}</strong>'
                     f'<span>{text_html(o["hint"])}</span></a></li>')
    return ('<section id="who-start" class="who-start" aria-labelledby="who-title"><h2 id="who-title">' + text_html(c['title']) + '</h2>'
            '<ul class="who-options">' + ''.join(items) + '</ul></section>')


def set_meta(html, key, value, attr='property'):
    """Set one <meta> tag's content; add it before </head> if the page lacks it."""
    pattern = r'(<meta ' + attr + '="' + re.escape(key) + r'" content=")[^"]*(">)'
    html, n = re.subn(pattern, lambda m: m[1] + e(value) + m[2], html, count=1)
    if n == 0:
        html = html.replace('</head>', '<meta ' + attr + '="' + key + '" content="' + e(value) + '">\n</head>', 1)
    return html


def set_head(html, title, description, url, og_title=None, image=LOGO, image_alt='Veteran Home Guardians logo', square=True):
    """Title, description, canonical and the Open Graph and Twitter tags that shared links read."""
    html, n = re.subn(r'<title>.*?</title>', lambda _: '<title>' + e(title) + '</title>', html, count=1, flags=re.S)
    assert n == 1, 'title'
    html, n = re.subn(r'(<meta name="description" content=")[^"]*(">)', lambda m: m[1] + e(description) + m[2], html, count=1)
    if n == 0:
        html = html.replace('</title>', '</title>\n<meta name="description" content="' + e(description) + '">', 1)
    if url:
        html, n = re.subn(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m[1] + e(url) + m[2], html, count=1)
        if n == 0:
            html = html.replace('</head>', '<link rel="canonical" href="' + e(url) + '">\n</head>', 1)
    og_title = og_title or title
    for key, value in (('og:type', 'website'), ('og:site_name', 'Veteran Home Guardians'), ('og:title', og_title),
                       ('og:description', description), ('og:url', url), ('og:image', image), ('og:image:alt', image_alt)):
        if value:
            html = set_meta(html, key, value)
    if image == LOGO:
        html = set_meta(html, 'og:image:width', '715')
        html = set_meta(html, 'og:image:height', '715')
    for key, value in (('twitter:card', 'summary' if square else 'summary_large_image'), ('twitter:title', og_title),
                       ('twitter:description', description), ('twitter:image', image)):
        html = set_meta(html, key, value, 'name')
    return html


def set_hero(html, h1=None, intro=None):
    """Replace the page's first heading and the paragraph right after it."""
    m = re.search(r'(<h1\b[^>]*>)(.*?)(</h1>)(\s*)(<p\b[^>]*>)(.*?)(</p>)', html, flags=re.S)
    assert m, 'hero heading and paragraph'
    new = m[1] + (h1 if h1 is not None else m[2]) + m[3] + m[4] + m[5] + (text_html(intro) if intro is not None else m[6]) + m[7]
    return html[:m.start()] + new + html[m.end():]


def apply_pages(result, root=ROOT):
    """Tailor the other entry pages from data/landing/pages.json. Pages built elsewhere in this run are
    taken from result; committed pages that no script builds are read from disk."""
    pages = _load('pages.json', root)['pages']
    out = {}
    for path, p in pages.items():
        if path.startswith('_'):
            continue
        html = result.get(path)
        if html is None:
            if not (root / path).is_file():
                continue
            html = (root / path).read_text(encoding='utf-8')
        out[path] = apply_page(html, path, root)
    return out


def apply_page(html, path, root=ROOT):
    """One page's landing from data/landing/pages.json. Builders that write their own page (such as
    scripts/build_flyers_page.py) call this too, so their output and the build agree."""
    p = _load('pages.json', root)['pages'][path]
    for key, limit in (('title', 90), ('description', 170)):
        assert len(p[key]) <= limit, f'{path}: {key} too long'
    url = p.get('url', BASE_URL + path)
    html = set_head(html, p['title'], p['description'], url, p.get('og_title'))
    if p.get('h1') or p.get('intro'):
        _check_text(path + ' intro', p.get('intro', 'x'), 360)
        html = set_hero(html, p.get('h1'), p.get('intro'))
    return html


def article(word):
    return 'an' if word[:1] in 'AEIOU' else 'a'


def share_page(html, st):
    """A state's sharing kit speaks to the person passing the guide on: staff, posts, clergy, neighbors."""
    name = 'Washington, DC' if st['code'] == 'DC' else st['name']
    page = st['share_page']
    guide = BASE_URL + ('' if st['page'] == 'index.html' else st['page'])
    what = st.get('share_description') or 'county veterans office, aging agency and long-term-care ombudsman contacts'
    what = re.sub(r' (across|in) ' + re.escape(st['name']) + '$', '', what)
    title = f'Share the {name} Veteran Resource Guide: free QR flyer | VHG'
    desc = f'Print a free QR flyer and newsletter blurb so {name} veterans and families can find {what[:1].lower() + what[1:]}.'
    if len(desc) > 170:
        # Too long to show whole in search results: the state's own short summary instead.
        hook = _load('states.json')['states'][st['code']]['title_hook']
        desc = f'Print a free QR flyer and newsletter blurb pointing {name} veterans and families to {hook}.'
    assert len(desc) <= 170, page
    heading = f'Help {article(name)} {name} veteran find their first call'
    html = set_head(html, title, desc, BASE_URL + page, heading)
    intro = (f'For anyone who meets {name} veterans and their families: admissions and social services staff, discharge planners, '
             f'post members, clergy and neighbors. Print the flyer, leave it where people wait, or copy the short write-up for a newsletter.')
    m = re.search(r'(<div class="screen-only"><h1>)(.*?)(</h1><p>)(.*?)(</p>)', html, flags=re.S)
    assert m, page + ' sharing kit heading'
    html = html[:m.start()] + m[1] + text_html(heading) + m[3] + text_html(intro) + m[5] + html[m.end():]
    assert guide.startswith(BASE_URL)
    return html
