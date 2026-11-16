# FindBingo.org

FindBingo.org is the multi-state bingo finder. Players type a ZIP code (or pick a state) and see
bingo near them, closest first. It covers Michigan and Indiana with state data, serves the Ohio Bingo
Finder at findbingo.org/ohio/, lists organizer-published games in Pennsylvania, New York, Florida
and Utah ("starter" states), and tells Kentucky and West Virginia players plainly that no public list
exists yet. Every listing has a "Report a change" email link, and every state has a free way for halls
to send game times.

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
| Generated site | `findbingo-site/index.html`, `data.json`, `zips.json`, and one page per state (`michigan/index.html` and so on) |
| Tests | `tests/findbingo.cjs` (part of `npm test`) |

`findbingo-site/index.html` is the whole page; it loads `data.json` and `zips.json` from beside
itself. The build writes the same three files to `bingo-site/findbingo/`. The Ohio-Bingo repository
mirrors `bingo-site/` every three hours, and **Cloudflare serves findbingo.org from the `findbingo`
folder of the Ohio-Bingo repository** (see "The domain" below), so list updates reach findbingo.org
within a few hours of a merge. A preview copy also runs on the Wix
site **Find Bingo** (site ID `9b3c0c21-b49d-45fa-9cb7-26a1a440afdf`); it reads the lists from
https://guide.vethomeguard.org/findbingo-site/. Upload `index.html` to Wix again
only when the page itself changes. Because the Wix page reads the lists from `main`, a page change
that needs new data (a new state, for example) shows only after its pull request merges; until then
the page hides state buttons the loaded data does not have.

**State pages (added November 16, 2026).** The finder draws its lists with JavaScript, so search engines
saw one page with no listings. Each covered state (except Ohio, whose page is the Ohio finder at /ohio/) now
also has a plain page, for example https://www.findbingo.org/michigan/, with its own title, description,
canonical address and heading, a ZIP search box that opens the finder, and every listing written out as
HTML by county with "Jump to your county" links. Indiana's page lists licenses current on the lists' date.
The home page's state buttons link to these pages (with the lists loaded, the finder still shows the state
in place), they are in `sitemap.xml`, and short addresses such as findbingo.org/mi or /FL forward to them
(`_redirects`). The home page carries WebSite markup naming Veteran Home Guardians as publisher; state
pages carry breadcrumb markup. There is no Event markup, because the lists hold weekly schedules, not
dated events.

**No counts.** Travis's rule (November 16, 2026): never state how many halls, places, groups or counties
are listed, anywhere on the site. `tests/findbingo.cjs` checks the state pages and the finder's wording.

Ohio data is not copied into the national page. Ohio searches hand off to https://www.findbingo.org/ohio/
with the same ZIP code and distance, so Ohio has one source of truth.

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
Administrator), but neither publishes a list. Florida is a "starter" state: listings come from
places that publish their own schedules, kept in `data/public/florida-bingo.json`, each with its own
source, phone and a note on how far to trust the days.

The first Florida listings are City of Jacksonville senior centers, read from the city's November
2026 monthly calendars
(https://www.jacksonville.gov/departments/parks-and-recreation/senior-services/senior-center-calendars).
Only centers with bingo on the same weekday most weeks are listed; one-off events (music bingo,
outings) are left out. The cards say the days come from the November calendar and can change month
to month. To refresh, read the newest month's calendars the same way. Next candidates: senior
centers and posts in the Tampa Bay, Orlando, Southwest and Southeast Florida areas, from organizer
pages or dated calendars only.

**Pennsylvania, New York, Utah (starter states, added November 16, 2026).** These came from the research
in the closed pull request #116 (branch `codex/bingo-multistate`, `data/bingo/venues.json`). Each
organizer's own page was read again on November 16, 2026 before listing; only places whose page gave a
regular day were kept. Files: `data/public/pennsylvania-bingo.json`, `new-york-bingo.json`,
`utah-bingo.json`, in the same shape as Florida's.

- Pennsylvania: bingo is licensed by each county treasurer, so there is no state list. Four listings
  (two American Legion posts, two fire companies).
- New York: a group gets a bingo identification number from the State Gaming Commission's Division of
  Charitable Gaming and its license from the city, town or village clerk; no public list of games was
  found. Three listings. Gates Center Bingo's page gives no phone, so its card offers a phone lookup
  (a phone is optional for starter listings).
- Utah: state law prohibits gambling (Utah Code 76-9-1402), so only free bingo is listed: three
  Washington County Council on Aging senior centers.
- "1st and 3rd Thursday" style schedules use the session `label`; the card says so in its note. The day
  filter still treats them as weekly.
- Left out for now: Irishtown Fire Company (a single December date), and both Washington State venues
  from that research (no regular day published). Their source pages could not be read on November 16.

Travis's rule for these lists (November 16, 2026): use the best information available and make it easy
for people to send corrections. Listings are not held back for phone confirmation.

**Kentucky, West Virginia, Pennsylvania (no state list).** No public statewide list of games or halls was found:
Kentucky's Office of Charitable Gaming (now part of Kentucky Horse Racing & Gaming) publishes county
totals only; West Virginia's Tax Division links no licensee list; Pennsylvania bingo licenses are
issued by each county treasurer. Kentucky and West Virginia get an honest "no list yet" card, the
regulator, and an email link for halls to send game times; Pennsylvania now has a starter list (above).

**ZIP codes.** The guide's GeoNames/Midwire centroids (CC BY 3.0, attributed in the footer), limited
to the covered states' ZIP prefixes (Florida's military 340 prefix excluded). ZIP 49037 (Battle Creek) is missing there; its point comes from the
U.S. Census Geocoder match for the bingo hall at 228 N 20th St.

## Refreshing the lists

1. Re-read the Michigan lookup and the Indiana list as above.
2. Update the JSON files and each record's `reviewed_on`.
3. Run `python3 scripts/build_public.py` and `node tests/findbingo.cjs`, then open a pull request.

## The domain

findbingo.org is registered and hosted on Cloudflare (set up November 16, 2026). The Cloudflare
project is the Worker **ohio-bingo** (static assets only), connected to the Ohio-Bingo repository:
production branch `main`, no build command, root directory `/`, and the deploy command

    npx wrangler deploy --name ohio-bingo --assets ./findbingo --compatibility-date 2026-11-13

so only the `findbingo` folder is published (the national page, and the Ohio finder in `ohio/`). `findbingo.org` and `www.findbingo.org` are attached
under the Worker's **Domains** tab, and Cloudflare creates the DNS records for them.

## Ohio: one finder, one front door

Travis's direction (November 16, 2026): findbingo.org holds every finder, state by state, and
ohiobingo.org is the Ohio front door where Veteran Home Guardians operates.

- The Ohio Bingo Finder is served at https://www.findbingo.org/ohio/ from `bingo-site/findbingo/ohio/`
  (built by `scripts/bingo_site.py`). `_redirects` forwards /oh, /OH and /Ohio to it. No rule matches
  `/ohio/` itself, because that would loop.
- https://www.ohiobingo.org/ (Wix) is for halls, claims, Ohio law and partnering with Veteran Home
  Guardians. Its "Find a Game" links go to findbingo.org/ohio/.
- bingo.vethomeguard.org is retired. GitHub Pages still answers there from the root of the Ohio-Bingo
  repository, but every page is a forwarding page that keeps the ZIP search and #anchor, so printed
  posters and QR codes still work. The `CNAME` file and the DNS record are what keep those forwards
  answering.
- The guide's `bingo.html` is the build source and test fixture. On guide.vethomeguard.org it forwards
  to findbingo.org/ohio/ and names it as canonical; it is not in the guide's sitemap.
- Other states are plain directories. Partnerships there are meant for local organizations in each
  state, not Veteran Home Guardians.

## Related work

Open draft PR #116 (`codex/bingo-multistate`) adds starter pages for Pennsylvania, New York,
Washington and Utah under bingo.vethomeguard.org/states/. It does not overlap these files. If it is
merged, its Pennsylvania records can be folded into FindBingo.org so there is one national finder.
