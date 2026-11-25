"""Shared visuals for the guide's pages (November 24, 2026): line icons, step diagrams and small charts.

Travis asked for visuals on the sites "wherever feasible". Everything here is drawn for this guide (no stock art,
no icon fonts, nothing loaded from another site) and follows the guide's own colors in assets/visuals.css.

- ICONS are drawn on a 24-point grid with 2-point round strokes, the same style as the guide's other symbols.
  build_public.py writes them once to assets/visuals.svg; pages draw them with <use>, so the 3,000-plus generated
  pages carry a short reference, not the drawing. An icon always sits beside words that say the same thing, so it
  is hidden from screen readers (aria-hidden, focusable=false).
- Diagrams are HTML: the words are real text that wraps, zooms, prints and translates; the icons and connecting
  lines are drawing only. A chart is an SVG with role="img", a title and a description, and its numbers are also
  written on the page (tests/visuals.cjs checks both).
"""
from html import escape

SPRITE = 'assets/visuals.svg'
CSS = 'assets/visuals.css'

# name: the inner drawing (stroke only; the stroke color is the text color around it).
ICONS = {
    'doc': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
    'doc-check': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 14.5l2 2 4-4"/>',
    'folder': '<path d="M3 6.5A1.5 1.5 0 0 1 4.5 5H9l2 2.5h8.5A1.5 1.5 0 0 1 21 9v9.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/><path d="M3 11h18"/>',
    'review': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 21 21M7.8 10.6l2 2 3.4-3.8"/>',
    'scale': '<path d="M12 4v16M8 20h8M5 8h14"/><path d="M5 8l-3 6.5a3 3 0 0 0 6 0zM19 8l-3 6.5a3 3 0 0 0 6 0z"/>',
    'court': '<path d="M3 9l9-5 9 5zM5 9v9M9.7 9v9M14.3 9v9M19 9v9M3 20.5h18"/>',
    'flag': '<path d="M6 21V4M6 4h11l-2.2 4L17 12H6"/>',
    'stone': '<path d="M6.5 20V10a5.5 5.5 0 0 1 11 0v10M4 20h16M9.5 12h5M9.5 15.5h5"/>',
    'medical': '<rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M12 8v8M8 12h8"/>',
    'chat': '<path d="M3 6a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-4 3v-3a2 2 0 0 1-2-2z"/><path d="M16 8h3a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2v3l-4-3h-4a2 2 0 0 1-2-1.6"/>',
    'dollar': '<circle cx="12" cy="12" r="9"/><path d="M15 9.2c-.5-1-1.6-1.6-3-1.6-1.7 0-3 .9-3 2.1s1.3 1.7 3 2.1 3 .9 3 2.1-1.3 2.1-3 2.1c-1.4 0-2.6-.6-3-1.6M12 6v12"/>',
    'home': '<path d="M3 11l9-7 9 7"/><path d="M5.5 9.5V20h13V9.5M10 20v-5.5h4V20"/>',
    'building': '<path d="M4 21V4.5a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 .5.5V21M15 9.5h4.5a.5.5 0 0 1 .5.5v11M2 21h20M8 8h3M8 12h3M8 16h3"/>',
    'siren': '<path d="M6.5 17v-4.5a5.5 5.5 0 0 1 11 0V17M4 17h16v4H4zM12 2.5V4.5M3.8 5.8l1.5 1.5M20.2 5.8l-1.5 1.5"/>',
    'phone': '<path d="M5 3.5h3.5l2 5-2.6 1.6a12 12 0 0 0 6 6l1.6-2.6 5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5.5a2 2 0 0 1 2-2z"/>',
    'alert': '<path d="M10.3 4.2 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4M12 17h.01"/>',
    'pill': '<rect x="3" y="8" width="18" height="8" rx="4" transform="rotate(-45 12 12)"/><path d="M9.2 9.2l5.6 5.6"/>',
    'wallet': '<path d="M18 7V5a1 1 0 0 0-1-1H5.5A2.5 2.5 0 0 0 3 6.5v11A2.5 2.5 0 0 0 5.5 20H20a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1H5.5A2.5 2.5 0 0 1 3 4.5"/><path d="M16.5 13.5h.01"/>',
    'receipt': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    'card': '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6 15h4"/>',
    'user-plus': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M19 8v6M16 11h6"/>',
    'pen': '<path d="M4 20h4L19.5 8.5a2.1 2.1 0 0 0-3-3L5 17z"/><path d="M14.5 7.5l3 3M13 20h7"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'heart': '<path d="M12 20s-8-4.6-8-10.2A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 8 2.8C20 15.4 12 20 12 20z"/>',
    'people': '<circle cx="8.5" cy="8" r="3"/><path d="M3 20a5.5 5.5 0 0 1 11 0"/><circle cx="16.5" cy="9" r="2.5"/><path d="M15.6 14.6A4.5 4.5 0 0 1 21 19"/>',
    'clipboard': '<rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 4.5V3h6v1.5M9 10h6M9 14h6M9 18h3"/>',
    'pin': '<path d="M12 21s-7-6.1-7-11.4a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.6" r="2.6"/>',
    'book': '<path d="M12 6.5C10 5 7 4.5 3 5v13.5c4-.5 7 0 9 1.5 2-1.5 5-2 9-1.5V5c-4-.5-7 0-9 1.5zM12 6.5V20"/>',
    'sprout': '<path d="M12 21v-9M12 12c0-4-3-6.5-7.5-6.5 0 4 3 6.5 7.5 6.5zM12 14.5c0-3.5 2.5-6 7-6 0 3.5-2.5 6-7 6z"/>',
    'signpost': '<path d="M12 3v18M12 5h6.5l2.5 2.5-2.5 2.5H12M12 12.5H5.5L3 15l2.5 2.5H12"/>',
    'question': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 0 1 4.9.7c0 1.7-2.4 2.2-2.4 3.8M12 17h.01"/>',
    'lifebuoy': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M5.6 5.6l3.6 3.6M14.8 14.8l3.6 3.6M18.4 5.6l-3.6 3.6M9.2 14.8l-3.6 3.6"/>',
    'shield': '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7 5.3-5.6"/>',
    'arrow-right': '<path d="M4 12h15M13 6l6 6-6 6"/>',
}


def sprite():
    """assets/visuals.svg: every icon as a <symbol>, drawn with the color of the text around it."""
    symbols = ''.join(
        f'<symbol id="v-{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{d}</symbol>\n' for name, d in ICONS.items())
    return ('<svg xmlns="http://www.w3.org/2000/svg">\n<!-- Veteran Resource Guide line icons, drawn for the guide '
            '(scripts/visuals.py). Decoration beside words; generated, do not edit by hand. -->\n' + symbols + '</svg>\n')


def icon(name, up=''):
    """One icon, hidden from screen readers. width/height keep it small if the stylesheet fails to load."""
    assert name in ICONS, name
    return (f'<svg class="vi" width="24" height="24" aria-hidden="true" focusable="false">'
            f'<use href="{up}{SPRITE}#v-{name}"/></svg>')


def stylesheet(up=''):
    return f'<link rel="stylesheet" href="{up}{CSS}">'


def money(n):
    return '${:,}'.format(n)


def payment_chart(maximum, counted, chart_id, title, max_label, counted_label, pension_label, monthly):
    """VA pension: the yearly maximum split into the income VA counts and the pension that fills the gap.

    The bar is drawn to scale. The words stay in HTML (heading, legend, table); the SVG holds the two shapes only.
    Meaning never rests on color: the counted income is hatched and the pension is solid, and each has a label."""
    pension = maximum - counted
    w = 600
    cw = round(w * counted / maximum, 1)
    t, d = chart_id + '-t', chart_id + '-d'
    svg = (f'<svg class="vz-bar" viewBox="0 0 {w} 56" width="{w}" height="56" preserveAspectRatio="none" role="img" '
           f'aria-labelledby="{t} {d}"><title id="{t}">{escape(title)}</title>'
           f'<desc id="{d}">{escape(max_label)}: {money(maximum)}. {escape(counted_label)}: {money(counted)}. '
           f'{escape(pension_label)}: {money(pension)} a year.</desc>'
           f'<defs><pattern id="{chart_id}-hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           f'<rect class="vz-hatch-bg" width="10" height="10"/><path class="vz-hatch" d="M0 0v10" stroke-width="4"/></pattern></defs>'
           f'<rect class="vz-seg-counted" x="1" y="4" width="{cw - 1}" height="48" fill="url(#{chart_id}-hatch)"/>'
           f'<rect class="vz-seg-pension" x="{cw}" y="4" width="{w - cw - 1}" height="48"/>'
           f'<rect class="vz-bar-frame" x="1" y="4" width="{w - 2}" height="48"/></svg>')
    share = round(100 * counted / maximum, 1)
    return (f'<figure class="vz vz-chart" aria-labelledby="{chart_id}-cap">'
            f'<figcaption id="{chart_id}-cap"><strong>{escape(title)}</strong></figcaption>'
            f'<p class="vz-span">{escape(max_label)}: <strong>{money(maximum)}</strong></p>'
            f'<div class="vz-bar-wrap">{svg}'
            f'<div class="vz-bar-labels" style="grid-template-columns:{share}fr {round(100 - share, 1)}fr" aria-hidden="true">'
            f'<span>{escape(counted_label)}</span><span>{escape(pension_label)}</span></div></div>'
            f'<ul class="vz-legend"><li><span class="vz-key vz-key-counted" aria-hidden="true"></span>{escape(counted_label)}: '
            f'<strong>{money(counted)}</strong></li><li><span class="vz-key vz-key-pension" aria-hidden="true"></span>'
            f'{escape(pension_label)}: <strong>{money(pension)} a year</strong> ({escape(monthly)})</li></ul>'
            f'<details class="vz-data"><summary>Chart data</summary><table><caption>{escape(title)}</caption>'
            f'<thead><tr><th scope="col">Part</th><th scope="col">Yearly amount</th></tr></thead><tbody>'
            f'<tr><th scope="row">{escape(max_label)}</th><td>{money(maximum)}</td></tr>'
            f'<tr><th scope="row">{escape(counted_label)}</th><td>{money(counted)}</td></tr>'
            f'<tr><th scope="row">{escape(pension_label)}</th><td>{money(pension)}</td></tr></tbody></table></details></figure>')


def count_bars(rows, chart_id, title, unit_words, up=''):
    """Small horizontal bar chart of counts, one row per kind: (label, count, href, icon). Drawn to scale against the
    largest count. The count is written as text beside each bar, and the same numbers are in a data table."""
    top = max(c for _, c, _, _ in rows) or 1
    items = []
    for label, count, href, ic in rows:
        pct = round(100 * count / top, 1)
        items.append(f'<li><a href="{escape(href)}">{icon(ic, up)}<span class="vz-cb-label">{escape(label)}</span></a>'
                     f'<span class="vz-cb-track"><span class="vz-cb-fill" style="width:{pct}%"></span></span>'
                     f'<span class="vz-cb-n">{count}</span></li>')
    rows_html = ''.join(f'<tr><th scope="row">{escape(label)}</th><td>{count}</td></tr>' for label, count, _, _ in rows)
    return (f'<figure class="vz vz-countbars" aria-labelledby="{chart_id}-cap"><figcaption id="{chart_id}-cap">'
            f'<strong>{escape(title)}</strong></figcaption><ul class="vz-cb">{"".join(items)}</ul>'
            f'<details class="vz-data"><summary>Chart data</summary><table><caption>{escape(title)}</caption>'
            f'<thead><tr><th scope="col">Kind</th><th scope="col">{escape(unit_words)}</th></tr></thead>'
            f'<tbody>{rows_html}</tbody></table></details></figure>')
