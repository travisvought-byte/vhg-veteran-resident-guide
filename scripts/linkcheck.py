#!/usr/bin/env python3
"""Link checking for the guide (scripts/check_links.py). Sorting rules shared with the OhioMom repository.

A robot cannot settle every link, so each result goes into one of four piles:

  ok        the page loaded on the site that was listed
  broken    the page is gone (404 or 410), no website answers at the address, its security certificate
            has expired or does not match, or the page looks parked or taken over
  moved     the address now sends visitors to a different website
  unchecked the site refused the robot, cut the connection, answered with a server error, or turned
            the robot away at its front page too: a robot cannot tell these from a working page

Only "broken" and "moved" are listed link by link, because those are the ones a visitor would hit.
"unchecked" is counted by site and nobody is asked to open those by hand: many government sites
refuse every robot, and this guide corrects contacts when someone reports a problem.

A few sites answer a robot as if a good page were missing. When a person has opened such a link in a
browser and it is fine, add it to data/link-checks.json with the date. The check then leaves it alone
until that date is older than max_age_days, so the monthly issue lists only what is new.

    python3 scripts/linkcheck.py --probe URL [URL ...]   show how single addresses are sorted
"""
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / 'data' / 'link-checks.json'

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
# The connection ended before any page came back. Firewalls do this to robots, so it proves nothing.
CUT_OFF = re.compile(r'connection reset|remote end closed|network is unreachable|no route to host|connection refused|'
                     r'unexpected_eof|eof occurred|unrecognized_name|handshake|wrong_version|alert', re.I)
# The name itself no longer leads anywhere.
NO_SUCH_SITE = re.compile(r'name or service not known|nodename nor servname|no address associated|name resolution', re.I)


def sort_failure(reason, text):
    """A request that failed before any answer came back: (pile, why), or None when it is worth one more try."""
    if 'timed out' in text:
        return 'unchecked', 'timed out'
    if isinstance(reason, ssl.SSLCertVerificationError):
        if 'unable to get local issuer' in text:
            # The server left out part of its certificate chain. Browsers fetch the missing piece.
            return 'unchecked', 'incomplete certificate chain (browsers usually accept it)'
        if 'expired' in text:
            return 'broken', 'the site\'s security certificate has expired, so browsers show a warning'
        if 'mismatch' in text.lower() or 'not valid for' in text:
            return 'broken', 'the security certificate does not match this address, so browsers show a warning'
        return 'broken', 'security certificate problem: ' + text
    if CUT_OFF.search(text) and not NO_SUCH_SITE.search(text):
        return 'unchecked', 'the connection was cut off before a page came back'
    return None


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
                title = html.unescape(title)
                if title and TAKEN_OVER.search(title):
                    return 'broken', f'the page looks parked or taken over: "{title}"', final
                if title and NOT_FOUND.search(title):
                    return 'broken', f'the page loads but says it is missing: "{title}"', final
                if site_of(final) != site_of(url):
                    return 'moved', f'now lands on {final}' + (f' ("{title}")' if title else ''), final
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
                last = str(exc.reason)[:110]
                sorted_as = sort_failure(exc.reason, last)
                if sorted_as:
                    return sorted_as + (url,)
            except TimeoutError:
                return 'unchecked', 'timed out', url
            except Exception as exc:  # anything else: try once more, then leave it for a person
                last = str(exc)[:110]
                sorted_as = sort_failure(exc, last)
                if sorted_as:
                    return sorted_as + (url,)
            time.sleep(2)
        if NO_SUCH_SITE.search(last):
            return 'broken', 'no website answers at this address', url
        if last.startswith('HTTP 5'):
            # A server error can be a real outage or a firewall's way of turning a robot away.
            return 'unchecked', f'the server answered with an error ({last})', url
        return 'unchecked', 'could not be requested: ' + last, url

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


def load_ledger():
    if not LEDGER.exists():
        return {'max_age_days': 180, 'opened_in_browser': {}}
    return json.loads(LEDGER.read_text(encoding='utf-8'))


def confirmed(url, ledger, today=None):
    """Has a person opened this link in a browser recently and found it working?"""
    entry = ledger.get('opened_in_browser', {}).get(url)
    if not entry:
        return False
    try:
        age = ((today or date.today()) - date.fromisoformat(entry['opened'])).days
    except (KeyError, ValueError):
        return False
    return 0 <= age <= ledger.get('max_age_days', 180)


def report(results, used, fix_hint='', limit=150, ledger=None, today=None):
    """results: {url: (pile, why, final)}; used: {url: {who uses it}}. Returns (markdown, needs_a_person).

    At most `limit` links are named in each list, so the report always fits in one GitHub issue.
    A link a person has opened recently (the ledger) is counted and not listed.
    """
    ledger = ledger or {}
    piles = {'broken': [], 'moved': [], 'unchecked': []}
    quiet = 0
    for url in sorted(results):
        pile, why, _ = results[url]
        if pile == 'ok':
            continue
        if pile in ('broken', 'moved') and confirmed(url, ledger, today):
            quiet += 1
            continue
        piles[pile].append((url, why))

    def who(url):
        ids = sorted(used.get(url, []))
        return ', '.join(f'`{i}`' for i in ids[:5]) + (f' and {len(ids) - 5} more' if len(ids) > 5 else '')

    def rows(pile):
        named = [f'- {u} ({why}), used by {who(u)}' for u, why in piles[pile][:limit]]
        return named + ([f'- and {len(piles[pile]) - limit} more'] if len(piles[pile]) > limit else [])

    ok = len(results) - sum(len(v) for v in piles.values()) - quiet
    out = [f'Checked {len(results)} links: {ok} loaded, {len(piles["broken"])} look broken, {len(piles["moved"])} moved to another website, '
           f'{len(piles["unchecked"])} on sites that turn robots away.\n']
    if piles['broken']:
        out.append('## Links that look broken\n')
        out.append('Open each one to be sure. If it is a dead end, correct the listing.' + (f' {fix_hint}' if fix_hint else '')
                   + ' If it loads in a browser, add it to `data/link-checks.json` with today\'s date and it will not be listed again until that date is old.\n')
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
    if quiet:
        out.append(f'{quiet} link{"s" if quiet != 1 else ""} a robot cannot load {"were" if quiet != 1 else "was"} opened by a person in the last '
                   f'{ledger.get("max_age_days", 180)} days and {"are" if quiet != 1 else "is"} not listed.\n')
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
