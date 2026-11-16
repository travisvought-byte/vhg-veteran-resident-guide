#!/usr/bin/env python3
"""Link checking for the guide (scripts/check_links.py). Sorting rules shared with the OhioMom repository.

A robot cannot settle every link, so each result goes into one of four piles:

  ok        the page loaded on the site that was listed
  broken    the page is gone, the address fails, or the page looks parked or taken over
  moved     the address now sends visitors to a different website
  unchecked the site refused the robot, or turned it away at its front page too

Only "broken" and "moved" are listed link by link, because those are the ones a visitor would hit.
"unchecked" is counted by site and nobody is asked to open those by hand: many government sites
refuse every robot, and this guide corrects contacts when someone reports a problem.

    python3 scripts/linkcheck.py --probe URL [URL ...]   show how single addresses are sorted
"""
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = 'Mozilla/5.0 (compatible; Veteran Resource Guide link check; +https://guide.vethomeguard.org/)'
HEADERS = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}
# Answers that mean "this site will not talk to a robot", not "this page is gone".
REFUSED = {401, 403, 405, 406, 429, 999}
# Words in a page title that mean the address was parked, sold or taken over.
TAKEN_OVER = re.compile(
    r'for sale|buy this domain|domain (name )?(is )?(parked|parking|available)|parked (free|domain)|'
    r'\btogel\b|iontogel|\bslot\b|\bslots\b|casino|\bjudi\b|sportsbook|\bpoker\b', re.I)
# A page that loads but says it is missing.
NOT_FOUND = re.compile(r'page (was |is )?not found|page (can.?t|cannot|could not) be found|\b404\b.*not found|no posts found', re.I)
TITLE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)


def site_of(url_or_host):
    """The part of an address that names the organization: ohio.gov for jfs.ohio.gov."""
    host = urllib.parse.urlsplit(url_or_host).hostname if '//' in url_or_host else url_or_host
    labels = (host or '').lower().split('.')
    if len(labels) <= 2 or all(x.isdigit() for x in labels):
        return '.'.join(labels)
    # co.uk, state.mn.us and the like keep three labels.
    if len(labels[-1]) == 2 and len(labels[-2]) <= 3:
        return '.'.join(labels[-3:])
    return '.'.join(labels[-2:])


def _get(url, timeout=30):
    """One request. Returns (status, final_url, title) or raises."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        title = ''
        if 'html' in (resp.headers.get('Content-Type') or '').lower():
            m = TITLE.search(resp.read(65536).decode('utf-8', 'replace'))
            title = re.sub(r'\s+', ' ', m.group(1)).strip()[:120] if m else ''
        return resp.status, resp.geturl(), title


class Checker:
    def __init__(self):
        self._front = {}

    def front_page_loads(self, url):
        """Does the site's own front page load for the robot? Asked once per site."""
        parts = urllib.parse.urlsplit(url)
        root = f'{parts.scheme}://{parts.netloc}/'
        if root not in self._front:
            try:
                status, _, _ = _get(root, timeout=20)
                self._front[root] = status < 400
            except Exception:
                self._front[root] = False
        return self._front[root]

    def check(self, url):
        """Returns (pile, why, final_url)."""
        last = ''
        for _ in range(2):
            try:
                status, final, title = _get(url)
                if title and TAKEN_OVER.search(title):
                    return 'broken', f'the page looks parked or taken over: "{title}"', final
                if title and NOT_FOUND.search(title):
                    return 'broken', f'the page loads but says it is missing: "{title}"', final
                if site_of(final) != site_of(url):
                    return 'moved', f'now lands on {urllib.parse.urlsplit(final).hostname}' + (f': "{title}"' if title else ''), final
                return 'ok', str(status), final
            except urllib.error.HTTPError as exc:
                if exc.code in REFUSED:
                    return 'unchecked', f'the site refused the robot (HTTP {exc.code})', url
                last = f'HTTP {exc.code}'
                if 300 <= exc.code < 400:
                    # A redirect that never settles. Some sites do this to robots only.
                    return 'unchecked', f'the site kept redirecting the robot ({last})', url
                if exc.code < 500:
                    is_front = urllib.parse.urlsplit(url).path in ('', '/')
                    if exc.code in (404, 410) and (is_front or not self.front_page_loads(url)):
                        return 'unchecked', f'the site turned the robot away at its front page too ({last})', url
                    return 'broken', last, url
            except urllib.error.URLError as exc:
                reason = exc.reason
                last = str(reason)[:110]
                if 'timed out' in last:
                    return 'unchecked', 'timed out', url
                if isinstance(reason, ssl.SSLCertVerificationError) and 'unable to get local issuer' in last:
                    # The server left out part of its certificate chain. Browsers fetch the missing piece.
                    return 'unchecked', 'incomplete certificate chain (browsers usually accept it)', url
            except TimeoutError:
                return 'unchecked', 'timed out', url
            except Exception as exc:  # report it; a person decides what it means
                last = str(exc)[:110]
            time.sleep(2)
        return 'broken', last, url

    def check_all(self, urls, workers=4):
        def work(u):
            time.sleep(0.2)
            return u, self.check(u)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return dict(pool.map(work, spread(urls)))


def spread(urls):
    """Order addresses so the same site is not asked for many pages in a row."""
    by_site = {}
    for u in sorted(urls):
        by_site.setdefault(site_of(u), []).append(u)
    out, rows = [], sorted(by_site.values(), key=len, reverse=True)
    while rows:
        out += [row.pop(0) for row in rows]
        rows = [row for row in rows if row]
    return out


def report(results, used, fix_hint='', limit=150):
    """results: {url: (pile, why, final)}; used: {url: {who uses it}}. Returns (markdown, needs_a_person).

    At most `limit` links are named in each list, so the report always fits in one GitHub issue.
    """
    piles = {'broken': [], 'moved': [], 'unchecked': []}
    for url in sorted(results):
        pile, why, _ = results[url]
        if pile != 'ok':
            piles[pile].append((url, why))

    def who(url):
        ids = sorted(used.get(url, []))
        return ', '.join(f'`{i}`' for i in ids[:5]) + (f' and {len(ids) - 5} more' if len(ids) > 5 else '')

    def rows(pile):
        named = [f'- {u} ({why}), used by {who(u)}' for u, why in piles[pile][:limit]]
        return named + ([f'- and {len(piles[pile]) - limit} more'] if len(piles[pile]) > limit else [])

    ok = len(results) - sum(len(v) for v in piles.values())
    out = [f'Checked {len(results)} links: {ok} loaded, {len(piles["broken"])} broken, {len(piles["moved"])} moved to another website, '
           f'{len(piles["unchecked"])} on sites that turn robots away.\n']
    if piles['broken']:
        out.append('## Links that are broken\n')
        out.append('A visitor who follows one of these reaches a dead end. Open it to be sure, then correct the listing.'
                   + (f' {fix_hint}' if fix_hint else '') + '\n')
        out += rows('broken')
        out.append('')
    if piles['moved']:
        out.append('## Links that now go to a different website\n')
        out.append('The organization may have renamed itself, or its old address may have been sold. '
                   'If it is still the right organization, list the new address.\n')
        out += rows('moved')
        out.append('')
    if not piles['broken'] and not piles['moved']:
        out.append('No broken or moved links were found.\n')
    if piles['unchecked']:
        by_site = {}
        for u, _ in piles['unchecked']:
            by_site[site_of(u)] = by_site.get(site_of(u), 0) + 1
        sites = sorted(by_site.items(), key=lambda kv: (-kv[1], kv[0]))
        out.append('<details><summary>Sites a robot cannot check (' + str(len(sites)) + ' sites, no action needed)</summary>\n')
        out.append('These sites refuse automated visits, so their links were not tested. Nothing here suggests a problem.\n')
        out.append(', '.join(f'{site} ({n})' for site, n in sites))
        out.append('\n</details>')
    return '\n'.join(out) + '\n', bool(piles['broken'] or piles['moved'])


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--probe':
        checker = Checker()
        for u in sys.argv[2:]:
            pile, why, final = checker.check(u)
            print(f'{pile:9} {u} -> {final if final != u else "(same address)"} | {why}')
    else:
        print(__doc__)
