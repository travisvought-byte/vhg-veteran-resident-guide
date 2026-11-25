"""Visuals for the guide's topic, hub and sharing pages (November 25, 2026).

Travis asked for "reasonable visuals everywhere, at least for the US side". build_public.py runs add(result) near the end,
so every page here gets its visuals each time the site is built. Everything is drawn from the page's own words and
numbers (each figure's facts are checked against the page text below, so a page edit that drops a fact stops the
build rather than leaving a figure that no longer matches):

- symbols beside section headings, on-page tables of contents and short lists (the shared sprite, scripts/visuals.py);
- figures: at-a-glance tiles (MST care), a where-to-turn diagram (Gold Star and surviving families), a timeline of the
  places and dates VA presumes Agent Orange exposure, a chart of VA burial allowances, and the four steps of the
  mobility rights finder.

Symbols are hidden from screen readers and always sit beside words. Charts are HTML bars with their numbers written
beside them, and the same numbers are in a table on the page.
"""
import re
from html import escape

from visuals import icon, stylesheet


def _up(path):
    return '../' * path.count('/')


def _before(html, anchor, fig, where):
    """Put a figure just before anchor, once (a page read back from disk keeps the one it has)."""
    fig_id = re.search(r'aria-labelledby="([^"]+)"', fig).group(1)
    if f'id="{fig_id}"' in html:
        return html
    return _once(html, anchor, fig + anchor, where)


def _once(html, old, new, where):
    assert html.count(old) == 1, f'{where}: expected one {old[:60]!r}, found {html.count(old)}'
    return html.replace(old, new, 1)


def _css(html, path):
    link = stylesheet(_up(path))
    return html if link in html else _once(html, '</head>', link + '</head>', path)


def h2_icons(html, path, pairs):
    """pairs: (start of the heading's text, icon). The symbol goes first inside the <h2>."""
    up = _up(path)
    for start, name in pairs:
        # A page that is read back from disk may already have its symbol: replace it rather than add a second.
        pat = re.compile(r'(<h2\b[^>]*>)(?:<svg class="vi"[^>]*>(?:(?!</svg>).)*</svg>)?(?=' + re.escape(start) + ')')
        found = pat.findall(html)
        assert len(found) == 1, f'{path}: heading {start!r} found {len(found)} times'
        html = pat.sub(lambda m: m.group(1) + icon(name, up), html, count=1)
    return html


def link_icons(html, path, scope_start, pairs):
    """Symbols at the start of links (by href) inside the first block that begins with scope_start."""
    up = _up(path)
    i = html.index(scope_start)
    for href, name in pairs:
        old = f'<a href="{href}"'
        j = html.index(old, i)
        k = html.index('>', j) + 1
        if not html.startswith('<svg class="vi"', k):
            html = html[:k] + icon(name, up) + html[k:]
    return html


def item_icons(html, path, list_start, names, cls='vz-ilist'):
    """Symbols at the start of each <li> of the list that begins with list_start (a <ul ...> or <ol ...> tag).
    cls='vz-ilist' hangs them in the margin of a bulleted list; None keeps a numbered list's numbers."""
    up = _up(path)
    i = html.index(list_start)
    tag = list_start[1:3]
    end = html.index(f'</{tag}>', i)
    block = html[i:end]
    if '<svg class="vi"' in block:
        return html
    assert block.count('<li>') == len(names), f'{path}: {block.count("<li>")} items, {len(names)} symbols'
    parts = block.split('<li>')
    block = parts[0] + ''.join('<li>' + icon(n, up) + rest for n, rest in zip(names, parts[1:]))
    if cls:
        assert block.startswith(f'<{tag}>'), f'{path}: plain list expected'
        block = f'<{tag} class="{cls}">' + block[len(tag) + 2:]
    return html[:i] + block + html[end:]


def _words(html):
    text = re.sub(r'<[^>]+>', ' ', html)
    return re.sub(r'\s+', ' ', text.replace('&nbsp;', ' ').replace('&#x27;', "'").replace('&rsquo;', '’'))


def tiles(cap_id, title, note, items, up):
    lis = ''.join(f'<li>{icon(ic, up)}<strong>{escape(head)}</strong><small>{escape(more)}</small></li>' for ic, head, more in items)
    return (f'<figure class="vz" aria-labelledby="{cap_id}"><figcaption id="{cap_id}"><strong>{escape(title)}</strong>{escape(note)}</figcaption>'
            f'<ul class="vz-grid">{lis}</ul></figure>')


def routes(cap_id, title, note, rows, up):
    lis = []
    for when_icon, when, who_icon, who, href in rows:
        inner = f'{icon(who_icon, up)}<span>{escape(who)}</span>'
        who_html = f'<a class="vz-who" href="{escape(href)}">{inner}</a>' if href else f'<span class="vz-who">{inner}</span>'
        lis.append(f'<li><span class="vz-when">{icon(when_icon, up)}<span>{escape(when)}</span></span>'
                   f'<span class="vz-arrow">{icon("arrow-right", up)}<span class="vz-vh">, turn to: </span></span>{who_html}</li>')
    return (f'<figure class="vz vz-turn" aria-labelledby="{cap_id}"><figcaption id="{cap_id}"><strong>{escape(title)}</strong>{escape(note)}</figcaption>'
            f'<ul class="vz-routes">{"".join(lis)}</ul></figure>')


def flow(cap_id, title, note, steps, up):
    lis = ''.join(f'<li><span class="vz-badge">{icon(ic, up)}</span><a href="{escape(href)}"><strong>{escape(head)}</strong></a>'
                  f'<span class="vz-more">{escape(more)}</span></li>' for ic, head, more, href in steps)
    return (f'<figure class="vz" aria-labelledby="{cap_id}"><figcaption id="{cap_id}"><strong>{escape(title)}</strong>{escape(note)}</figcaption>'
            f'<ol class="vz-flow">{lis}</ol></figure>')


# ---------------------------------------------------------------- Agent Orange: where and when VA presumes exposure
# (place, start, end, words exactly as the page has them). Dates as (year, month, day).
EXPOSURE = [
    ('Vietnam, inland waterways and offshore', (1962, 1, 9), (1975, 5, 7), 'from January 9, 1962, to May 7, 1975'),
    ('Thailand bases', (1962, 1, 9), (1976, 6, 30), 'January 9, 1962, to June 30, 1976'),
    ('Laos', (1965, 12, 1), (1969, 9, 30), 'December 1, 1965, to September 30, 1969'),
    ('Cambodia: Mimot or Krek', (1969, 4, 16), (1969, 4, 30), 'April 16 to April 30, 1969'),
    ('Guam or American Samoa', (1962, 1, 9), (1980, 7, 31), 'January 9, 1962, to July 31, 1980'),
    ('Johnston Atoll', (1972, 1, 1), (1977, 9, 30), 'January 1, 1972, to September 30, 1977'),
    ('Korean DMZ', (1967, 9, 1), (1971, 8, 31), 'September 1, 1967, to August 31, 1971'),
]
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def _year(d):
    y, m, day = d
    return y + (m - 1) / 12 + (day - 1) / 365


def _date(d):
    return f'{MONTHS[d[1] - 1][:3]} {d[2]}, {d[0]}'


def exposure_timeline(up):
    lo, hi = 1962, 1981
    span = hi - lo
    rows, table = [], []
    for place, a, b, _ in EXPOSURE:
        left = round(100 * (_year(a) - lo) / span, 2)
        width = round(100 * (_year(b) - _year(a)) / span, 2)
        when = f'{_date(a)} to {_date(b)}'
        rows.append(f'<li><span class="vz-tl-label">{escape(place)}</span><span class="vz-tl-track" aria-hidden="true">'
                    f'<span class="vz-tl-bar" style="left:{left}%;width:{width}%"></span></span><span class="vz-tl-when">{escape(when)}</span></li>')
        table.append(f'<tr><th scope="row">{escape(place)}</th><td>{escape(_date(a))}</td><td>{escape(_date(b))}</td></tr>')
    ticks = ''.join(f'<span style="left:{round(100 * (y - lo) / span, 2)}%">{y}</span>' for y in (1962, 1965, 1970, 1975, 1980))
    return ('<figure class="vz vz-tl" aria-labelledby="tl-cap"><figcaption id="tl-cap"><strong>When and where VA presumes exposure</strong>'
            'Each bar runs from the first to the last date in the list above, on one scale from 1962 to 1981. '
            'The dates are written beside each bar.</figcaption>'
            f'<div class="vz-tl-axis" aria-hidden="true"><span></span><span class="vz-tl-ticks">{ticks}</span><span></span></div>'
            f'<ul class="vz-tl-rows">{"".join(rows)}</ul>'
            '<details class="vz-data"><summary>Chart data</summary><table><caption>Presumed exposure periods</caption>'
            '<thead><tr><th scope="col">Place</th><th scope="col">From</th><th scope="col">To</th></tr></thead>'
            f'<tbody>{"".join(table)}</tbody></table></details></figure>')


def burial_bars(up):
    rows = [('Service-connected death', 2000, 'Up to $2,000', 'medical'),
            ('Burial allowance, death not service connected', 1032, '$1,032', 'stone'),
            ('Plot allowance, death not service connected', 1032, '$1,032', 'pin')]
    top = max(n for _, n, _, _ in rows)
    lis = ''.join(f'<li><span class="vz-cb-name">{icon(ic, up)}<span>{escape(label)}</span></span>'
                  f'<span class="vz-cb-track"><span class="vz-cb-fill" style="width:{round(100 * n / top, 1)}%"></span></span>'
                  f'<span class="vz-cb-money">{escape(words)}</span></li>' for label, n, words, ic in rows)
    return ('<figure class="vz vz-money" aria-labelledby="burial-cap"><figcaption id="burial-cap"><strong>VA burial allowances side by side</strong>'
            'Drawn to scale from the table below. For a death that is not service connected, the burial and plot allowances are separate amounts.</figcaption>'
            f'<ul class="vz-cb">{lis}</ul></figure>')


def _check(html, path, facts):
    text = _words(html)
    for fact in facts:
        assert fact in text, f'{path}: the visual says "{fact}", which the page no longer says'


def add(result):
    out = {}

    def page(path, fn):
        if path in result:
            html = fn(result[path], path)
            out[path] = _css(html, path)

    # Help after military sexual trauma.
    def mst(html, path):
        _check(html, path, ['VA provides free treatment for any physical or mental health condition related to MST.',
                            'have reported it at the time, or have any other proof',
                            'including many with an other than honorable discharge',
                            'You don’t need a VA disability rating (service connection).',
                            'You don’t have to talk about MST when you sign up for VA health care.',
                            'You can ask to see a clinician of a particular sex'])
        up = _up(path)
        fig = tiles('care-glance', 'MST-related VA care, at a glance', 'From what VA says, listed in full just below.', [
            ('medical', 'Free', 'Treatment for any physical or mental health condition related to MST'),
            ('doc-check', 'No report or proof needed', 'You don’t need to have reported it at the time'),
            ('check', 'No disability rating needed', 'Service connection is not required'),
            ('people', 'Open to most former service members', 'Including many with an other than honorable discharge'),
            ('user', 'Your choice', 'You don’t have to talk about MST when you sign up, and you can ask for a clinician of a particular sex'),
        ], up)
        html = _before(html, '<div class="card"><h3>What VA says about MST-related care</h3>', fig, path)
        icons = [('#care', 'medical'), ('#coordinator', 'phone'), ('#vet-center', 'chat'), ('#claims', 'doc'),
                 ('#discharge', 'signpost'), ('#men', 'user'), ('#serving', 'shield')]
        html = link_icons(html, path, '<ul class="jumps"', icons)
        return h2_icons(html, path, [('Free care from VA', 'medical'), ('Talk to an MST coordinator', 'phone'),
                                     ('Counseling at a Vet Center', 'chat'), ('Disability compensation', 'doc'),
                                     ('If MST affected your discharge', 'signpost'), ('For men', 'user'), ('Still serving', 'shield')])
    page('mst.html', mst)

    # Gold Star and surviving families.
    def survivors(html, path):
        _check(html, path, ['Its helpline is answered at any hour', '800-959-8277', 'Free support for surviving families, including help sorting out benefits.',
                            '800-342-9647', 'Dependency and Indemnity Compensation (DIC) and Survivors Pension',
                            'Each branch has people whose job is to support surviving families'])
        up = _up(path)
        fig = routes('turn-cap', 'Where to turn first', 'Each line names who to contact and links to the number or the part of this page.', [
            ('heart', 'Grief, at any hour', 'phone', 'TAPS helpline, 800-959-8277', 'tel:8009598277'),
            ('flag', 'Casualty help and long-term support', 'people', 'The service branch’s survivor program', '#branch'),
            ('dollar', 'Monthly payments: DIC and Survivors Pension', 'doc', 'The guide’s surviving spouse section', 'index.html?view=survivors'),
            ('chat', 'Help sorting out benefits', 'phone', 'Military OneSource, 800-342-9647', 'tel:8003429647'),
            ('book', 'School for children and spouses', 'book', 'School benefits on this page', '#school'),
        ], up)
        html = _before(html, '<section id="talk">', fig, path)
        html = link_icons(html, path, '<ul class="jumps"', [('#talk', 'phone'), ('#money', 'dollar'), ('#branch', 'flag'),
                                                            ('#buttons', 'heart'), ('#school', 'book'), ('#ohio', 'pin'), ('#states', 'signpost')])
        return h2_icons(html, path, [('Someone to talk to', 'phone'), ('Monthly payments', 'dollar'), ('Help from the service branch', 'flag'),
                                     ('Gold Star lapel buttons', 'heart'), ('School for children', 'book'), ('Ohio survivor benefits', 'pin'),
                                     ('Other states', 'signpost')])
    page('survivors.html', survivors)

    # Veterans in the justice system.
    def justice(html, path):
        html = item_icons(html, path, '<ol class="start">', ['court', 'dollar', 'home'], cls=None)
        html = link_icons(html, path, '<ul class="toc">', [('#arrested', 'court'), ('#prison', 'building'), ('#va-pay', 'dollar'),
                                                          ('#family', 'people'), ('#coming-home', 'home'), ('#ohio', 'pin')])
        return h2_icons(html, path, [('Start here', 'signpost'), ('Arrested, in jail', 'court'), ('In prison', 'building'),
                                     ('What jail or prison does to VA pay', 'dollar'), ('For the family', 'people'),
                                     ('Coming home', 'home'), ('In Ohio', 'pin')])
    page('justice.html', justice)

    # Agent Orange and the PACT Act.
    def toxic(html, path):
        _check(html, path, [w for _, _, _, w in EXPOSURE])
        up = _up(path)
        html = _before(html, '<div class="box"><h3>Denied before?</h3>', exposure_timeline(up), path)
        i = html.index('<h2 id="how">')
        j = html.index('<ul>', i)
        html = html[:j] + item_icons(html[j:], path, '<ul>', ['folder', 'calendar', 'user'])
        return h2_icons(html, path, [('Why this matters', 'building'), ('Agent Orange: conditions', 'medical'), ('Where VA presumes', 'pin'),
                                     ('The PACT Act', 'flag'), ('The toxic exposure screening', 'review'), ('How to file', 'doc')])
    page('toxic-exposure.html', toxic)

    # Hospice and burial.
    def burial(html, path):
        _check(html, path, ['Service-connected death on or after September 11, 2001 Up to $2,000',
                            'Death not service connected, on or after October 1, 2026 $1,032 burial allowance and $1,032 for a plot'])
        up = _up(path)
        anchor = '<div class="table-wrap"><table><caption class="sr">VA burial allowance amounts</caption>'
        html = _before(html, anchor, burial_bars(up), path)
        return h2_icons(html, path, [('VA hospice care', 'heart'), ('VA burial allowances', 'dollar'), ('National and state veterans cemeteries', 'flag'),
                                     ('Plan ahead', 'calendar'), ('When no family claims', 'stone')])
    page('end-of-life-burial.html', burial)

    # Families: autism, ADHD and disabilities (headings the language switcher does not rewrite).
    page('family-guide.html', lambda html, path: h2_icons(html, path, [
        ('Military and veteran families', 'flag'), ('Words you', 'book'), ('What\'s changing', 'calendar'),
        ('Disability rights agencies', 'scale'), ('Good to know', 'question')]))

    # Ohio nursing homes and assisted living: the links for residents and families.
    def facilities(html, path):
        html = link_icons(html, path, '<nav class="quick" aria-label="Help for residents and families">', [
            ('va-pension-aid-attendance.html', 'dollar'), ('elder-abuse.html', 'alert'), ('guardianship.html', 'scale'),
            ('end-of-life-burial.html', 'heart'), ('toxic-exposure.html', 'medical')])
        return h2_icons(html, path, [('For residents and families', 'people'), ('Correct or add a facility', 'pen')])
    page('facilities.html', facilities)

    # Disability rights and advocacy, mobility rights and mobility independence (their newer home is Mobility Talk).
    page('disability-advocacy.html', lambda html, path: h2_icons(html, path, [
        ('What is getting in your way?', 'signpost'), ('1. Choose your request', 'pen'), ('Writing without JavaScript', 'doc'),
        ('Help someone else speak up', 'people'), ('Five ways to speak up', 'chat'), ('Need a service, appeal', 'scale')]))

    def mobility_rights(html, path):
        up = _up(path)
        steps = flow('steps-cap', 'Four steps on this page', 'Each step opens its part of the page.', [
            ('signpost', '1. Tell us where to start', 'Your state and what is in the way', '#finder-title'),
            ('pin', '2. Your starting point', 'Who to contact first', '#result-title'),
            ('pen', '3. Prepare your message', 'Words you can use or change', '#route-compose-title'),
            ('clipboard', '4. Keep an action record', 'Who you contacted and what comes next', '#record-title')], up)
        _check(html, path, ['1. Tell us where to start', '2. Your starting point', '3. Prepare your message', '4. Keep an action record',
                            'Write down who you contacted and what comes next'])
        if 'id="steps-cap"' not in html:
            i = html.index('<h2 id="finder-title">')
            s = html.rindex('<section', 0, i)
            html = html[:s] + steps + html[s:]
        return h2_icons(html, path, [('1. Tell us where to start', 'signpost'), ('2. Your starting point', 'pin'), ('3. Prepare your message', 'pen'),
                                     ('4. Keep an action record', 'clipboard'), ('Help someone find', 'people'), ('State source summaries', 'book')])
    page('mobility-rights.html', mobility_rights)

    page('mobility-independence.html', lambda html, path: h2_icons(html, path, [
        ('Start here. A few minutes can help.', 'signpost'), ('Repair it. Adapt it.', 'sprout'), ('Put it in your own words', 'pen'),
        ('Need help with equipment now?', 'lifebuoy')]))

    # November retail campaign.
    def november(html, path):
        up = _up(path)
        for name, ic in (('Round up', 'dollar'), ('Top up', 'card'), ('Store-funded donation', 'building')):
            if f'<h3>{name}</h3>' in html:
                html = _once(html, f'<h3>{name}</h3>', f'<h3>{icon(ic, up)}{name}</h3>', path)
        return h2_icons(html, path, [('Choose a way your store can help', 'signpost'), ('Make November count', 'calendar'),
                                     ('Start with a quick conversation', 'chat')])
    page('november-campaign.html', november)

    # Privacy.
    def privacy(html, path):
        i = html.index('The short version</h2>')
        j = html.index('<ul>', i)
        html = html[:j] + item_icons(html[j:], path, '<ul>', ['user', 'clipboard', 'review', 'home', 'pin', 'shield'])
        return h2_icons(html, path, [('The short version', 'shield'), ('Counting visits', 'clipboard'), ('What you choose and type', 'pen'),
                                     ('Maps and', 'pin'), ('Who hosts the site', 'building'), ('Our Google ads', 'review'),
                                     ('Advertising on the guide', 'signpost'), ('Email and corrections', 'chat'), ('Children', 'people'),
                                     ('Questions', 'question')])
    page('privacy.html', privacy)

    # Sharing kits (Ohio's share.html and one per state): the QR code is the picture; symbols on the headings.
    for path in [p for p in result if re.fullmatch(r'share(-[a-z]{2})?\.html', p)]:
        page(path, lambda html, path: h2_icons(html, path, [('Scan to find your first call', 'phone'), ('Full-page flyers to print', 'doc'),
                                                            ('Ready-to-use newsletter introduction', 'book'),
                                                            ('Send people directly to the help they need', 'signpost')]))

    return out


# Pages whose own builders are checked by their own tests call these directly.
def packets(html, path='packets.html'):
    html = h2_icons(html, path, [('Ohio: pick a county', 'pin'), ('Other states and Washington', 'signpost'),
                                 ('Cover sheets', 'clipboard'), ('Printing tips', 'doc')])
    return _css(html, path)


def bad_paper(html, path):
    """Symbols on the "In this guide" list on every page of the bad paper section."""
    html = link_icons(html, path, 'In this guide</h2><ol>', [
        ('./', 'signpost'), ('va-without-upgrade.html', 'medical'), ('boards.html', 'court'), ('liberal-consideration.html', 'scale'),
        ('records.html', 'folder'), ('free-help.html', 'people'), ('../flyers/bad-paper-checklist-letter.pdf', 'clipboard')])
    return _css(html, path)
