#!/usr/bin/env python3
"""Suicide and homelessness help on every page (owner direction, November 17, 2026).

One short "Need help now?" block goes directly above the footer of every page a visitor reads, on
the guide (guide.vethomeguard.org) and on FindBingo.org and its Ohio finder. Pages that only forward
somewhere else do not carry it: they send the visitor on at once. The block does not print, so
handoffs, flyers and posters come out exactly as before.

Each line was read on its source page on November 17, 2026:
- 988lifeline.org: call or text 988, 24 hours a day, free and confidential.
- veteranscrisisline.net: dial 988, then press 1.
- hud.gov/contactus: dial 2-1-1 and press 6 for homeless services; the Find Shelter tool.
- usa.gov/emergency-housing: National Call Center for Homeless Veterans, 1-877-424-3838,
  24 hours a day.

`scripts/build_public.py` adds the block to every page it builds, and `scripts/build_flyers_page.py`
to the flyers page. The few pages written by hand get it from this script:

    python3 scripts/help_now.py          # add or refresh the block on the hand-kept pages
    python3 scripts/help_now.py --check  # exit 1 if a hand-kept page is missing it or out of date
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each link is underlined and bold so it stands out on any page's own styling. Short links never
# break across lines; the longer Find Shelter link may wrap, so the block fits a narrow screen.
_WRAP = ' style="color:#0b4f6c;font-weight:700;text-decoration:underline"'
_LINK = ' style="color:#0b4f6c;font-weight:700;text-decoration:underline;white-space:nowrap"'
BLOCK = ('<aside class="help-now" aria-label="Need help now?" style="box-sizing:border-box;width:calc(100% - 32px);max-width:960px;'
         'margin:24px auto;padding:12px 16px;border:1px solid #b9c2bd;border-left:6px solid #7a1f1f;border-radius:6px;'
         'background:#fff;color:#1b1b1b;font:400 16px/1.5 system-ui,sans-serif;text-align:left">'
         '<strong>Need help now?</strong> Thinking about suicide, or in any crisis: '
         '<a href="tel:988"' + _LINK + '>call</a> or <a href="sms:988"' + _LINK + '>text 988</a>, any time. '
         'Veterans: dial 988, then press 1. No safe place to sleep tonight: '
         '<a href="tel:211"' + _LINK + '>dial 211</a> and press 6 for homeless services, or use '
         '<a href="https://www.hud.gov/findshelter"' + _WRAP + '>HUD’s Find Shelter tool</a>. Veterans: '
         '<a href="tel:8774243838"' + _LINK + '>1-877-424-3838</a>, 24 hours a day.</aside>')
# The print rule lives in the head so the page stays valid HTML.
PRINT_RULE = '<style>@media print{.help-now{display:none!important}}</style>'
HEAD = '<!--help-now-css-->' + PRINT_RULE + '<!--/help-now-css-->'
BODY = '<!--help-now-->' + BLOCK + '<!--/help-now-->'

# Pages written by hand. build_public.py and build_flyers_page.py add the block to the pages they build.
HAND_KEPT = ('assistant/index.html', 'mobility-independence.html', 'november-campaign.html')


def is_forward(text: str) -> bool:
    """A page that only sends the visitor somewhere else."""
    return 'http-equiv="refresh"' in text or (len(text) < 2500 and 'location.replace' in text)


def wants_help(name: str, text: str) -> bool:
    """True for a page a visitor reads: not a test fixture, a forwarding page or a search-engine ownership file."""
    if not name.endswith('.html') or not isinstance(text, str):
        return False
    base = name.rsplit('/', 1)[-1]
    if name.startswith('tests/') or re.fullmatch(r'google[0-9a-f]{16}\.html', base):
        return False
    return not is_forward(text)


def strip_help(text: str) -> str:
    text = re.sub(r'<!--help-now-css-->.*?<!--/help-now-css-->', '', text, flags=re.S)
    return re.sub(r'<!--help-now-->.*?<!--/help-now-->', '', text, flags=re.S)


def add_help(text: str, name: str = 'page') -> str:
    """Put the block directly above the page's footer, or at the end of the page when it has no footer. Safe to repeat."""
    text = strip_help(text)
    if 'class="help-now"' in text:
        raise ValueError(f'{name}: carries a help block this script did not add')
    if text.count('</head>') != 1:
        raise ValueError(f'{name}: expected one </head>')
    text = text.replace('</head>', HEAD + '</head>', 1)
    at = text.rfind('<footer')
    if at < 0:
        at = text.rfind('</main>')
    if at < 0:
        at = text.rfind('</body>')
    if at < 0:
        raise ValueError(f'{name}: no footer, </main> or </body> to put the help block above')
    return text[:at] + BODY + text[at:]


def check_pages(root: Path = ROOT) -> int:
    """Every page a visitor reads carries the block once, directly above its footer. No other page carries it."""
    outside = {'.git', 'node_modules', 'tests', 'templates', 'research'}
    count = 0
    for path in sorted(root.rglob('*.html')):
        name = path.relative_to(root).as_posix()
        if outside & set(name.split('/')[:-1]) or name.startswith('flyers/src/'):
            continue  # not published pages: fixtures, templates, staged research and flyer print sources
        text = path.read_text(encoding='utf-8')
        if not wants_help(name, text):
            assert 'class="help-now"' not in text, f'{name}: a forwarding or ownership page should not carry the help block'
            continue
        assert text.count(BODY) == 1 and text.count('class="help-now"') == 1, f'{name}: needs the help block exactly once'
        assert text.count(HEAD) == 1 and text.index(HEAD) < text.index('</head>'), f'{name}: needs the print rule once, in the head'
        after = text[text.index(BODY) + len(BODY):]
        if '<footer' in text:
            assert after.startswith('<footer') and '<footer' not in after[1:], f'{name}: the help block sits directly above the footer'
        else:
            assert after.startswith(('</main>', '</body>')), f'{name}: the help block closes the page'
        for link in ('href="tel:988"', 'href="sms:988"', 'href="tel:211"', 'href="https://www.hud.gov/findshelter"', 'href="tel:8774243838"'):
            assert BLOCK.count(link) == 1, link
        count += 1
    assert count >= 160, f'expected the guide, sharing and bingo pages; found {count}'
    return count


def main(argv):
    check = '--check' in argv
    stale = []
    for name in HAND_KEPT:
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        new = add_help(text, name)
        if new != text:
            stale.append(name)
            if not check:
                path.write_text(new, encoding='utf-8')
    if check and stale:
        sys.exit('Help block missing or out of date: ' + ', '.join(stale) + '. Run python3 scripts/help_now.py')
    print('Help block is current on the hand-kept pages.' if not stale else 'Updated: ' + ', '.join(stale))


if __name__ == '__main__':
    main(sys.argv[1:])
