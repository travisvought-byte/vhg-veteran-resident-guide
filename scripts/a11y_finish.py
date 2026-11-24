"""Accessibility finishing pass for every generated page (November 24, 2026).

build_public.py runs every public page through finish() as its last step, so new pages get it too.
Where a page does not already have them, it adds:

- a "Skip to main content" link as the first thing in <body>, pointing at the page's <main>
  (WCAG 2.4.1), and an id on <main> for it to land on;
- a small shared stylesheet: the skip link, hidden until a keyboard user reaches it; less motion
  for visitors who ask their device for less (smooth scrolling and animations turned off); and
  small symbols beside phone, text-message and email links in the page body.

The symbols are line drawings from Lucide (ISC license, https://lucide.dev), drawn in the text
color with CSS masks so they follow dark mode, print nothing, and show in Windows high contrast.
They are decoration only: the words beside them carry the meaning, and screen readers skip them.
"""
import re
from urllib.parse import quote

# Lucide icon drawings (24x24, 2px round strokes), ISC license.
ICONS = {
    'phone': '<path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384"/>',
    'message-square': '<path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/>',
    'mail': '<path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/><rect x="2" y="4" width="20" height="16" rx="2"/>',
}


def icon_url(inner):
    """A Lucide drawing as a CSS url() for a mask, in the same form as assets/unified.css."""
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' "
           "stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>" + inner.replace('"', "'") + '</svg>')
    return 'url("data:image/svg+xml,' + quote(svg, safe=" /:='.,-") + '")'


LINK_ICONS = (('tel:', 'phone'), ('sms:', 'message-square'), ('mailto:', 'mail'))
# Links that already show their own symbol, or are drawn as buttons, keep their look.
_LINK_SKIP = ':not(.phone):not(.button):not(.btn):not(:has(svg,img))'

MARK = '/* a11y-base */'
CSS = (MARK +
         # Skip link: off screen until it has keyboard focus, then a high-contrast box at the top left.
         '.a11y-skip{position:absolute;left:8px;top:-200px;z-index:10000;background:#fff;color:#14303f;'
         'padding:10px 14px;border:2px solid #14303f;border-radius:6px;font:700 17px/1.3 system-ui,sans-serif;'
         'text-decoration:underline}.a11y-skip:focus{top:8px;outline:3px solid #a07014;outline-offset:2px}'
         # Less motion for visitors whose device asks for it.
         '@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}'
         '*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;'
         'transition-duration:.01ms!important;scroll-behavior:auto!important}}'
         # Symbols beside phone, text and email links in the page body.
         + ','.join(f'main a[href^="{p}"]{_LINK_SKIP}::before' for p, _ in LINK_ICONS) +
         '{content:"";display:inline-block;width:1em;height:1em;margin-right:.3em;vertical-align:-.13em;'
         'background:currentColor;-webkit-mask:var(--a11y-icon) center/contain no-repeat;'
         'mask:var(--a11y-icon) center/contain no-repeat}'
         + ''.join(f'main a[href^="{p}"]{_LINK_SKIP}::before{{--a11y-icon:{icon_url(ICONS[name])}}}'
                   for p, name in LINK_ICONS) +
         '@media print{.a11y-skip{display:none!important}' + ','.join(f'main a[href^="{p}"]::before' for p, _ in LINK_ICONS) +
         '{display:none!important}}'
         '@media (forced-colors:active){' + ','.join(f'main a[href^="{p}"]::before' for p, _ in LINK_ICONS) +
         '{background:LinkText;forced-color-adjust:none}}')

_SKIP_HINT = re.compile(r'skip|jump to|main content|ir al contenido|saltar', re.I)


def _has_skip_link(body):
    """True if one of the first few links jumps within the page to the content (any wording)."""
    for m in list(re.finditer(r'<a\b([^>]*)>(.*?)</a>', body, re.S))[:4]:
        attrs, text = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2))
        if re.search(r'href="#', attrs) and (_SKIP_HINT.search(text) or re.search(r'class="[^"]*skip', attrs)):
            return True
    return False


def finish(html):
    """Return the page with a skip link, a <main> target and the shared accessibility styles."""
    if '</head>' not in html or not re.search(r'<body\b', html):
        return html
    body = re.search(r'<body\b[^>]*>', html)
    main = re.compile(r'<main\b([^>]*)>').search(html, body.end())
    if main is None:
        return html  # Forwarding stubs and verification files have no content to skip to.
    if MARK not in html:
        # Added to the end of the page's last style block in <head> (a page keeps the number of style
        # blocks other build steps expect), or as a new block when the page has none.
        head_end = html.index('</head>')
        last = html.rfind('</style>', 0, head_end)
        html = (html[:last] + CSS + html[last:]) if last >= 0 else html.replace('</head>', '<style>' + CSS + '</style></head>', 1)
    body = re.search(r'<body\b[^>]*>', html)
    if not _has_skip_link(html[body.end():]):
        main = re.compile(r'<main\b([^>]*)>').search(html, body.end())
        found = re.search(r'\bid="([^"]+)"', main.group(1))
        if found:
            target = found.group(1)
        else:
            target = 'main-content'
            html = html[:main.start()] + '<main id="main-content"' + main.group(1) + '>' + html[main.end():]
        lang = re.search(r'<html\b[^>]*\blang="es', html)
        label = 'Saltar al contenido principal' if lang else 'Skip to main content'
        body = re.search(r'<body\b[^>]*>', html)
        html = html[:body.end()] + f'<a class="a11y-skip" href="#{target}">{label}</a>' + html[body.end():]
    return html


def finish_named(name, text):
    """Finish one generated file by its published path. Test fixtures stay exactly as their tests expect,
    and the printable flyer and packet views stay as they are, so their PDFs are not all rebuilt for no
    visible change. Scripts that also write pages on their own (build_flyers_page.py, build_packets.py)
    call this too, so their --check agrees with build_public.py."""
    if name.endswith('.html') and isinstance(text, str) and not name.startswith(('tests/', 'flyers/')):
        return finish(text)
    return text


def finish_all(result):
    """The finished pages of a build's outputs, by name (only those that changed)."""
    out = {}
    for name, text in result.items():
        done = finish_named(name, text)
        if done is not text and done != text:
            out[name] = done
    return out
