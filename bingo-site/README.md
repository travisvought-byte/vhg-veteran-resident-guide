# Ohio Bingo Finder

Live at **https://www.findbingo.org/ohio/**. A free finder for bingo games and senior centers across Ohio, from Veteran Home Guardians.

Every file in this folder is **generated**. Do not edit it here. The source of truth is
[vhg-veteran-resident-guide](https://github.com/travisvought-byte/vhg-veteran-resident-guide):
`scripts/bingo_site.py` builds `bingo-site/` from the same records as the guide's `bingo.html`
(`python3 scripts/build_public.py`), and the Ohio-Bingo repository mirrors `bingo-site/`.

- `findbingo/ohio/` is the Ohio finder. Cloudflare serves it at https://www.findbingo.org/ohio/.
- The files in this folder's root are forwarding pages for the retired address
  bingo.vethomeguard.org (GitHub Pages), so printed posters and QR codes still land on the finder.

- `findbingo/` is FindBingo.org (https://www.findbingo.org/), the multi-state finder, built by
  `scripts/findbingo_site.py` in the same guide repository. Cloudflare serves this folder (the
  `ohio-bingo` project; see docs/FINDBINGO.md in the guide).
