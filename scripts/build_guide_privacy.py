"""Build privacy.html, the Veteran Resource Guide's privacy page (guide.vethomeguard.org/privacy.html).

Run by scripts/build_public.py. Keep it in plain words and true to what the pages do: page views are
counted by GoatCounter without cookies (assets/analytics.js drops everything after the "?"), choices stay
in the page address, drafts and checklists stay in the browser, and corrections go by email. Visitors who come
from one of VHG's Google ads also load Google's ad measurement (assets/ads-measure.js); every guide page loads Google Tag Manager.
"""
from html import escape
import place_map

UPDATED = 'November 24, 2026'
EMAIL = 'travis@vethomeguard.org'


def _a(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'


def page():
    ask = 'mailto:' + EMAIL + '?subject=Veteran%20Resource%20Guide%20privacy'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Privacy | Veteran Resource Guide</title>
<meta name="description" content="How the free Veteran Resource Guide from Veteran Home Guardians handles information about your visit: no accounts, no cookies for counting visits, nothing you choose or type is sent to us.">
<link rel="canonical" href="https://guide.vethomeguard.org/privacy.html">
<link rel="stylesheet" href="assets/family-guide.css">
<style>
.privacy{{max-width:860px;margin:auto;padding:24px}}.privacy h2{{margin:28px 0 6px}}.privacy li{{margin:6px 0}}
</style>
<script src="assets/analytics.js" defer></script></head><body>
<header><nav aria-label="Main"><a href="./">Veteran Resource Guide</a><a href="family-guide.html">Family Guide</a><a href="flyers.html">Printable flyers</a></nav>
<div class="hero"><p class="eyebrow">PRIVACY</p><h1>Privacy</h1><p>How the Veteran Resource Guide handles information about your visit. Last updated {UPDATED}.</p></div></header>
<main class="privacy" id="main">
<h2>The short version</h2>
<ul><li>There are no accounts and no sign-in. We never ask for your name.</li>
<li>We count visits without cookies and without keeping personal information.</li>
<li>Google Tag Manager loads on the guide so our free nonprofit Google ads can be measured. If you came from one of those ads, Google also learns whether you then called a local veterans office.</li>
<li>The state, county and help you choose stay on your own device and in the page address.</li>
<li>The maps’ pictures come from OpenStreetMap, which sees your internet address and the area on the map.</li>
<li>We do not sell personal information.</li></ul>
<h2>Counting visits</h2>
<p>We use {_a('https://www.goatcounter.com/help/privacy', 'GoatCounter')} to count page views, so we know which pages people use. GoatCounter does not use cookies and does not store personal information. For each page view it records things like the page visited, the site that sent you here, your browser, your screen size, and an approximate country worked out from your internet (IP) address. It does not store the IP address.</p>
<p>We leave out everything after the question mark in a page address, so your county and the help you chose are never counted. The one exception is the name of an ad or campaign that sent you here (its utm tags). We also count when someone taps a link to a donation page.</p>
<h2>What you choose and type</h2>
<p>The guide works in your browser. When you pick a state, a county or a kind of help, the page shows it from lists that download with the page; nothing is sent to us. Your choices show in the page address so you can bookmark or share them.</p>
<p>Letters you write on the advocacy pages, checklists you tick and drafts in the guided assistance stay in your browser. We do not store or send them. You copy, print or send them yourself.</p>
<h2>Maps and “Use my location”</h2>
<p>The nursing home and assisted living page shows its list on a map. {escape(place_map.TILE_PRIVACY)}Read {_a(place_map.TILE_PRIVACY_URL, 'the OpenStreetMap Foundation’s privacy policy')}. The map code itself (Leaflet) comes from this site. If you hide the map, your browser remembers that on your device, and the map pictures stop loading.</p>
<p>{escape(place_map.LOCATION_PRIVACY)}</p>
<h2>Who hosts the site</h2>
<p>The guide is hosted on GitHub Pages. GitHub may keep server logs, including IP addresses, for security. Read {_a('https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement', 'GitHub’s privacy statement')}. A few pages show a logo from a partner’s website, which receives an ordinary request for that picture.</p>
<h2>Our Google ads</h2>
<p>Veteran Home Guardians runs free Google search ads through Google’s nonprofit program, so more veterans find the guide. To measure them, every guide page loads Google Tag Manager, a Google script, and Google may set cookies and see your internet address and the page you are on, like any site that uses it.</p>
<p>Guide pages also load Google’s ad tag, so Google Ads can confirm our measurement is installed. If you arrive by clicking one of our ads, Google adds a code to the page address, and for the rest of that visit, in that browser tab, the guide watches for a call to a local office. If you then tap a local office’s phone number, Google Ads counts that an ad led to a call. It is not told the number, your county or anything you chose or typed, and we ask Google not to use it to personalize ads. Read {_a('https://policies.google.com/technologies/partner-sites', 'how Google uses information from sites that use its services')}.</p>
<h2>Advertising on the guide</h2>
<p>The guide does not show ads and has no affiliate links. When a business or group sponsors a guide to help keep it free, its spot is labeled “Sponsored”, and sponsorship never changes the free listings or their order.</p>
<h2>Email and corrections</h2>
<p>If you email us a correction, we get your email address and what you write. We use it to fix the guide and to reply, and we never sell or share it. Please send public resource information only, never a resident’s personal or health details.</p>
<h2>Children</h2>
<p>The guide is not directed to children under 13, and we do not knowingly collect information from them.</p>
<h2>Questions</h2>
<p>The guide is shared by {_a('https://www.vethomeguard.org/', 'Veteran Home Guardians')}, an Ohio nonprofit. Questions about privacy: <a href="{ask}">{EMAIL}</a>.</p>
<p>Last updated {UPDATED}.</p>
</main>
<footer class="privacy"><p>Free from Veteran Home Guardians. <a href="./">Back to the Veteran Resource Guide</a></p></footer>
</body></html>
'''


def outputs():
    return {'privacy.html': page()}
