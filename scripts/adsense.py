"""Google AdSense on the guide: the publisher, the head block and ads.txt.

The code goes only on the public guide pages (the Ohio home page, each state's page and share page, the
facilities page and the country pages for veterans abroad), asking for non-personalized ads before it loads.
The privacy, family guide, flyers, bingo, mobility and advocacy pages and the assistant never carry it.
Set CLIENT to '' to take the code and ads.txt off everywhere.
"""
import html
import re

CLIENT = 'ca-pub-9220804879239310'
assert CLIENT == '' or re.fullmatch(r'ca-pub-\d{16}', CLIENT), 'CLIENT must look like ca-pub-1234567890123456'
BLOCK = re.compile(r'<!--adnet-->.*?<!--/adnet-->', re.S)


def head(client=CLIENT):
    if not client:
        return ''
    c = html.escape(client, quote=True)
    return (f'<!--adnet--><meta name="google-adsense-account" content="{c}">'
            '<script data-adnet>(window.adsbygoogle=window.adsbygoogle||[]).requestNonPersonalizedAds=1;</script>'
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={c}" '
            'crossorigin="anonymous"></script><!--/adnet-->')


def place(text, client=CLIENT):
    """The page with any earlier ad code taken out and the current code put back before </head>. Idempotent."""
    text = BLOCK.sub('', text)
    block = head(client)
    if not block:
        return text
    assert text.count('</head>') == 1, 'a page with ad code needs exactly one </head>'
    return text.replace('</head>', block + '</head>', 1)


def ads_txt(client=CLIENT):
    return f'google.com, pub-{client[len("ca-pub-"):]}, DIRECT, f08c47fec0942fa0\n' if client else ''
