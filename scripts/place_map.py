"""The map beside a page's list, in the style of Nina's Map (assets/map/).

assets/map/place-map.js is written into each page (so a page stays one file) and loads Leaflet and its
clustering add-on from the site itself, only once the list has places to show. The list stays the page:
every pin is a card in the list, the map box stays hidden without JavaScript, and the plain list is the fallback.

Pins come only from data the guide already has. No list here has street-level coordinates, so a card is
pinned at the middle of its ZIP code (the same ZIP code points the distance search uses), and each pin's box
says so. A card without a known ZIP code point stays in the list without a pin.
Map pictures come from OpenStreetMap; every page with a map says so beside it and in its privacy page.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Leaflet 1.9.4 and Leaflet.markercluster 1.5.3, the same files Nina's Map serves (no CDN).
VENDOR = ('leaflet.js', 'leaflet.css', 'leaflet.markercluster.js', 'markercluster.css')
TILE_HOST = 'tile.openstreetmap.org'


def vendor_files(root, prefix):
    """The Leaflet files, to be served at prefix (for example 'bingo-site/findbingo/assets/map/')."""
    return {prefix + name: (root / 'assets/map' / name).read_text() for name in VENDOR}


def script(root=ROOT):
    js = (root / 'assets/map/place-map.js').read_text()
    assert '</script' not in js.lower()
    return '<script>' + js.strip() + '</script>'


def box(list_id, base, *, title, label, legend, privacy_href, zip_table='', numbers=True, dark=False, extra_hint=''):
    """The map box, hidden until place-map.js has places to show. legend: (kind, words) pairs; 'you' is the searched ZIP code."""
    keys = ''.join(f'<li><span class="{"pm-you" if kind == "you" else "pm-pin pm-k-" + kind}" aria-hidden="true"></span>{escape(words)}</li>'
                   for kind, words in legend)
    hint = 'Tap or click a pin to call or get directions. Press Tab to move between pins and Enter to open one.'
    touch = 'Tap a pin to call or get directions. Pinch to zoom. To move the map with one finger, tap the map once first.'
    if extra_hint:
        hint, touch = hint + ' ' + extra_hint, touch + ' ' + extra_hint
    attrs = (f' data-pm-list="{escape(list_id)}" data-pm-base="{escape(base)}"'
             + (f' data-pm-zip-table="{escape(zip_table)}"' if zip_table else '')
             + ('' if numbers else ' data-pm-numbers="0"') + (' data-pm-dark="1"' if dark else ''))
    return (f'<section class="pm-box" id="map-box" hidden{attrs} aria-labelledby="map-title">'
            f'<div class="pm-head"><h2 id="map-title">{escape(title)}</h2>'
            '<button type="button" class="pm-toggle" aria-expanded="true" aria-controls="map-area">Hide the map</button></div>'
            f'<div class="pm-area" id="map-area"><div class="pm-map" role="region" aria-label="{escape(label)}"></div>'
            f'<ul class="pm-legend">{keys}</ul>'
            f'<p class="pm-hint" data-touch="{escape(touch)}" data-awake="{escape(hint)}">{escape(hint)}</p>'
            '<p class="pm-note">Pins sit in the middle of each ZIP code, not at the door, so use the address or the Directions button to get there. '
            'The map pictures come from OpenStreetMap, which sees the area you look at. '
            f'<a href="{escape(privacy_href)}" data-pm-privacy>Privacy</a></p></div></section>')


def locate_button(zip_input, form, status, zip_table, words='Use my location'):
    """A "Use my location" button for a ZIP code form: hidden without JavaScript or location support."""
    return (f'<p class="pm-locate-row"><button type="button" class="pm-locate" data-pm-locate hidden data-pm-zip-input="{escape(zip_input)}" '
            f'data-pm-form="{escape(form)}" data-pm-status="{escape(status)}" data-pm-zip-table="{escape(zip_table)}">'
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false">'
            '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>'
            f'{escape(words)}</button></p>')


LOCATION_PRIVACY = ('“Use my location” asks your browser for your location. If you say yes, the page finds the nearest ZIP code '
                    'on your own device and searches it like a typed one. Your location is not sent to us or to anyone else, and it is not kept.')
TILE_PRIVACY = ('The map pictures (tiles) come from OpenStreetMap (tile.openstreetmap.org). To draw the map, your browser asks OpenStreetMap '
                'for the pictures of the area you look at, so OpenStreetMap sees your internet (IP) address, the area on the map and which website '
                'you are on, like any website you visit. Your browser does not send it the ZIP code you typed or your location, '
                'but the area on the map is near the place you searched. ')
TILE_PRIVACY_URL = 'https://osmfoundation.org/wiki/Privacy_Policy'
