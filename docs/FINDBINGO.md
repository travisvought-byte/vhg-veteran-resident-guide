# FindBingo.org

FindBingo.org is the multi-state bingo finder. Players type a ZIP code (or pick a state) and see
bingo near them, closest first. It covers Michigan and Indiana with state data, sends Ohio players
to the Ohio Bingo Finder, and tells Kentucky, West Virginia, Pennsylvania and Florida players plainly
that no public list exists yet, with a free way for halls to send game times.

Started November 15, 2026, at Travis's direction: one national finder, neighboring states first.

## How it is built

| Piece | Where |
| --- | --- |
| State facts, regulators and sources | `data/public/bingo-states.json` |
| Michigan weekly bingo (venues, days, licensed hours) | `data/public/michigan-weekly-bingo.json` |
| Indiana groups with a current license that allows bingo | `data/public/indiana-bingo-licenses.json` |
| ZIP code points the centroid file lacks | `data/public/zip-points-supplement.json` |
| Page template | `templates/findbingo/index.html` |
| Generator and validation | `scripts/findbingo_site.py` (run by `scripts/build_public.py`) |
| Generated site | `findbingo-site/index.html`, `data.json`, `zips.json` |
| Tests | `tests/findbingo.cjs` (part of `npm test`) |

`findbingo-site/index.html` is the whole page. It is uploaded to the Wix site **Find Bingo**
(site ID `9b3c0c21-b49d-45fa-9cb7-26a1a440afdf`), which is where www.findbingo.org connects. The
page loads `data.json` and `zips.json` from https://guide.vethomeguard.org/findbingo-site/, so list
updates go live on findbingo.org as soon as a pull request merges. Upload `index.html` to Wix again
only when the page itself changes. Because the Wix page reads the lists from `main`, a page change
that needs new data (a new state, for example) shows only after its pull request merges; until then
the page hides state buttons the loaded data does not have.

Ohio data is not copied here. Ohio searches hand off to https://bingo.vethomeguard.org/ with the
same ZIP code and distance, so Ohio has one source of truth.

## Sources and how they were read (November 15, 2026)

**Michigan.** The Michigan Lottery's Charitable Gaming Division publishes
[Find a Weekly Bingo](https://www.michigan.gov/cg/panel-links-and-change-forms/links/find-a-weekly-bingo).
The page's own lookup (a POST to `/api-proxy/CG-FindABingo-Reverse-Proxy` with a county name) was
read for every county in its list. Each row gives the licensed organization, location, day and
licensed begin and end time. Rows were grouped by street address into venues; each session keeps
its organization. The page tells players that hours come from the license list and to call ahead
for the first game time. The state lookup refuses some requests: it throttles bursts, and it returns
"Unable to process your request" for Clinton County every time (also when searched by city), so a
county that fails should be retried later rather than stopping the whole run. Counties not loaded
yet are listed in `pending_counties` in `bingo-states.json`, and the page names them and links the
state lookup. Two typos in the state list are fixed in the data with a note on the record (a
Manistique hall listed with Mason's ZIP code, and a street number written "1o1"). To finish them, read those counties the same way, add their venues and
remove them from `pending_counties` (the build refuses a county that is both listed and pending).

**Indiana.** The Indiana Gaming Commission's
[current licenses list](https://secure.in.gov/igc/charity-gaming/qualifiedorganizationswithcurrentlicenses)
(included as of November 13, 2026) was filtered to annual licenses whose allowed activities include
bingo, one record per license number with the latest expiration. Post office boxes are removed from
the address used for directions; `listed_address` keeps the state's wording. The list has no game days,
times or phone numbers, so these listings say so, offer a phone lookup and directions, and stay
behind a "Show them too" button wherever halls with game days are nearby. Licenses past their
expiration date drop off automatically.

**Florida.** Florida does not license bingo statewide: section 849.0931 lets charitable, nonprofit
and veterans' organizations (and some homeowners' and mobile home park associations) run bingo, sets
limits (two days a week, $250 jackpots, players 18 and older) and names no state license. Some
counties license it locally (Pinellas through Consumer Protection, Marion through its County
Administrator), but neither publishes a list. Florida therefore gets the "no list yet" card for now.
Building a Florida list means hall-by-hall research from organizer pages and dated city calendars
(Jacksonville's senior centers, for example, post monthly calendars with bingo days and times).

**Kentucky, West Virginia, Pennsylvania.** No public statewide list of games or halls was found:
Kentucky's Office of Charitable Gaming (now part of Kentucky Horse Racing & Gaming) publishes county
totals only; West Virginia's Tax Division links no licensee list; Pennsylvania bingo licenses are
issued by each county treasurer. These states get an honest "no list yet" card, the regulator, and
an email link for halls to send game times.

**ZIP codes.** The guide's GeoNames/Midwire centroids (CC BY 3.0, attributed in the footer), limited
to the covered states' ZIP prefixes (Florida's military 340 prefix excluded). ZIP 49037 (Battle Creek) is missing there; its point comes from the
U.S. Census Geocoder match for the bingo hall at 228 N 20th St.

## Refreshing the lists

1. Re-read the Michigan lookup and the Indiana list as above.
2. Update the JSON files and each record's `reviewed_on`.
3. Run `python3 scripts/build_public.py` and `node tests/findbingo.cjs`, then open a pull request.

## Connecting the domain (Travis)

In Wix, open the **Find Bingo** site dashboard
(https://manage.wix.com/dashboard/9b3c0c21-b49d-45fa-9cb7-26a1a440afdf), choose a Premium plan that
allows a custom domain, then connect `findbingo.org` under Settings → Domains. If the domain was
bought through Wix it can be assigned directly; if it was bought elsewhere, Wix shows the DNS records
to add at that registrar.

## Related work

Open draft PR #116 (`codex/bingo-multistate`) adds starter pages for Pennsylvania, New York,
Washington and Utah under bingo.vethomeguard.org/states/. It does not overlap these files. If it is
merged, its Pennsylvania records can be folded into FindBingo.org so there is one national finder.
