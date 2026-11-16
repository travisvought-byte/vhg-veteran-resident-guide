"""Checks for scripts/linkcheck.py and scripts/check_links.py.

Every request goes to a small server started here; nothing leaves the machine.
"""
import importlib.util
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

root = Path(__file__).resolve().parents[1]
# The test servers are on this machine; never send those requests through a proxy.
os.environ['NO_PROXY'] = os.environ['no_proxy'] = '127.0.0.1,localhost'


def load(name):
    spec = importlib.util.spec_from_file_location(name, root / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


linkcheck = load('linkcheck')
check_links = load('check_links')


def make_server(routes):
    """routes: {path: (status, headers, body)}; any other path answers routes['*'] or 404."""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, headers, body = routes.get(self.path, routes.get('*', (404, {}, 'gone')))
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            if 'Content-Type' not in headers:
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def page(title):
    return f'<!doctype html><html><head><title>{title}</title></head><body>x</body></html>'


# 1. How single answers are sorted.
other = make_server({'/': (200, {}, page('Another organization'))})
normal = make_server({
    '/': (200, {}, page('A real site')),
    '/ok': (200, {}, page('County Veterans Service Office')),
    '/refused': (403, {}, 'no robots'),
    '/parked': (200, {}, page('example.org is for sale | Buy now')),
    '/gambling': (200, {}, page('Iontogel: Masuk Via Website')),
    '/soft404': (200, {}, page('Page not found | State Department')),
    '/moved': (302, {'Location': f'http://localhost:{other.server_port}/'}, ''),
    '/same-site': (302, {'Location': '/ok'}, ''),
    '/loop': (307, {'Location': '/loop'}, ''),
    '/error': (500, {}, 'server error'),
})
turns_away = make_server({'*': (404, {}, 'not for robots')})
base, away = f'http://127.0.0.1:{normal.server_port}', f'http://127.0.0.1:{turns_away.server_port}'
linkcheck.time.sleep = lambda seconds: None  # no waiting between tries in tests


def pile(url):
    return linkcheck.Checker().check(url)[0]


assert pile(base + '/ok') == 'ok' and pile(base + '/same-site') == 'ok'
assert pile(base + '/gone') == 'broken', 'a missing page on a working site is broken'
assert pile(base + '/error') == 'unchecked', 'a server error may be a firewall turning the robot away, so it is not called broken'
assert pile(away + '/veterans/contact') == 'unchecked' and pile(away + '/') == 'unchecked', 'a site that turns robots away everywhere is not called broken'
assert pile(base + '/refused') == 'unchecked'
assert pile(base + '/loop') == 'unchecked', 'a redirect that never settles is a robot trap, not a dead page'
assert pile(base + '/parked') == 'broken' and pile(base + '/gambling') == 'broken', 'a parked or taken-over address is broken even though it loads'
assert pile(base + '/soft404') == 'broken', 'a page that loads but says not found is broken'
moved = linkcheck.Checker().check(base + '/moved')
assert moved[0] == 'moved' and 'localhost' in moved[1]
assert moved[1] == f'now lands on http://localhost:{other.server_port}/ ("Another organization")', 'the new address is spelled out so it can be pasted into the record'
# Failures before any answer: only a dead name or a bad certificate is called broken.
import ssl
cert = lambda text: ssl.SSLCertVerificationError(1, text)
assert linkcheck.sort_failure(cert('certificate verify failed: certificate has expired'), 'certificate verify failed: certificate has expired')[0] == 'broken'
assert linkcheck.sort_failure(cert("Hostname mismatch, certificate is not valid for 'www.example.org'"), "Hostname mismatch, certificate is not valid for 'www.example.org'")[0] == 'broken'
assert linkcheck.sort_failure(cert('unable to get local issuer certificate'), 'unable to get local issuer certificate')[0] == 'unchecked'
for text in ('[Errno 104] Connection reset by peer', 'Remote end closed connection without response', '[Errno 101] Network is unreachable',
             '[Errno 113] No route to host', '[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name', 'EOF occurred in violation of protocol', 'timed out'):
    assert linkcheck.sort_failure(OSError(text), text)[0] == 'unchecked', text
assert linkcheck.sort_failure(OSError('x'), '[Errno -2] Name or service not known') is None, 'a name that does not resolve gets one more try before it is called broken'
assert linkcheck.NO_SUCH_SITE.search('[Errno -2] Name or service not known') and linkcheck.NO_SUCH_SITE.search('Temporary failure in name resolution')
assert linkcheck.site_of('https://dvs.ohio.gov/') == linkcheck.site_of('https://aging.ohio.gov/x') == 'ohio.gov'
assert linkcheck.site_of('https://health.state.mn.us/') == 'state.mn.us'
assert linkcheck.site_of('https://www.va.gov/') != linkcheck.site_of('https://www.cms.gov/')
for server in (other, normal, turns_away):
    server.shutdown()

# 2. The same site is not asked for many pages in a row.
order = linkcheck.spread(['https://a.gov/1', 'https://a.gov/2', 'https://a.gov/3', 'https://b.org/1', 'https://c.org/1'])
assert sorted(order) == ['https://a.gov/1', 'https://a.gov/2', 'https://a.gov/3', 'https://b.org/1', 'https://c.org/1']
assert [linkcheck.site_of(u) for u in order[:3]] == ['a.gov', 'b.org', 'c.org'], order

# 3. The report lists broken and moved links one by one, and only counts the sites a robot cannot check.
results = {
    'https://ok.example/': ('ok', '200', 'https://ok.example/'),
    'https://dead.example/x': ('broken', 'HTTP 404', 'https://dead.example/x'),
    'https://old.example/': ('moved', 'now lands on new.example', 'https://new.example/'),
    'https://quiet.ohio.gov/a': ('unchecked', 'the site refused the robot (HTTP 403)', 'https://quiet.ohio.gov/a'),
    'https://other.ohio.gov/b': ('unchecked', 'the site refused the robot (HTTP 403)', 'https://other.ohio.gov/b'),
}
used = {u: {'OH:example'} for u in results}
used['https://dead.example/x'] = {'TX:tx-one', 'TX:tx-two', 'shared:r02-va-pension'}
text, needs = linkcheck.report(results, used, fix_hint='Fix the record.')
assert needs
assert text.startswith('Checked 5 links: 1 loaded, 1 broken, 1 moved to another website, 2 on sites that turn robots away.'), text
assert '- https://dead.example/x (HTTP 404), used by `TX:tx-one`, `TX:tx-two`, `shared:r02-va-pension`' in text
assert '- https://old.example/ (now lands on new.example), used by `OH:example`' in text
assert 'ohio.gov (2)' in text and 'https://quiet.ohio.gov/a' not in text, 'unchecked links are counted by site, never listed'
assert 'https://ok.example/' not in text and 'Fix the record.' in text
many = {f'https://dead.example/{n}': ('broken', 'HTTP 404', '') for n in range(400)}
long_report, _ = linkcheck.report(many, {u: {'TX:tx-' + str(i) for i in range(9)} for u in many})
assert '- and 250 more' in long_report and len(long_report) < 60000, 'a very long list still fits in one GitHub issue'
quiet, needs = linkcheck.report({k: results[k] for k in ('https://ok.example/', 'https://quiet.ohio.gov/a')}, used)
assert not needs and 'No broken or moved links were found.' in quiet, 'sites that refuse robots never raise an issue on their own'

# 4. The real data: every state and the family guide are covered, and shared federal records are named once.
links = check_links.collect()
registry = check_links.read('states/registry.json')
who = {w for names in links.values() for w in names}
assert len(links) > 1000, len(links)
for state in registry:
    assert any(w.startswith(state['code'] + ':') for w in who), state['code'] + ' has no links to check'
assert any(w.startswith('family guide:') for w in who) and any(w.startswith('shared:') for w in who)
assert not any(w.endswith(':r02-va-pension') and not w.startswith('shared:') for w in who), 'a shared record is listed once, not once per state'
assert all(u.startswith('https://') or u.startswith('http://') for u in links)
texas = check_links.collect('TX')
assert texas and all(w.startswith(('TX:', 'shared:')) for names in texas.values() for w in names)
assert len(texas) < len(links)
print('PASS: link check sorting, polite ordering, report wording and coverage of ' + str(len(registry)) + ' states plus the family guide (' + str(len(links)) + ' links).')
