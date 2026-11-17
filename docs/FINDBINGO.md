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
| Virginia bingo sessions (halls, days, doors-open and doors-close times) | `data/public/virginia-bingo-sessions.json`, rebuilt by `scripts/import_virginia_bingo.py` |
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

1. Re-read the Michigan lookup and the Indiana list as above. For Virginia, download the state's current
   directory and run `python3 scripts/import_virginia_bingo.py bingo_events.pdf --reviewed <today> --geocode`,
   then set Virginia's `list_as_of` in `bingo-states.json` to the listing date the script prints.
2. Update the JSON files and each record's `reviewed_on`.
3. Run `python3 scripts/build_public.py` and `node tests/findbingo.cjs`, then open a pull request.

## Every state (added November 17, 2026)

Travis's direction: populate findbingo.org across the whole country. The build is top-down: every
state and DC has an entry in `data/public/bingo-states.json` (alphabetical by name), so every ZIP code
works and every state has a page and a free way to send game times.

**As of November 17, 2026 every state and DC is researched; none is `pending`.** Each entry names who
licenses or oversees bingo there (or says plainly that licensing is local, or that the state does not
license bingo), gives at least one official source, and links the state's own list, map or finder
where one is published. The tests refuse a `pending` state, so coverage cannot slip back.

| coverage | meaning |
|---|---|
| `pending` | Not researched. Only `code`, `name`, `coverage`, `about`, `reviewed_on`. Kept in the build for completeness; no state uses it now. Such a page carries `noindex` and stays out of `sitemap.xml`. |
| `none` | Researched: regulator named and sourced, no list loaded on this site. If the state publishes a list or finder, `list_url` and `list_label` point to it and the state page and the search card lead with that button. |
| `starter` | Organizer-published schedules, one file per state (`STARTER_FILES`). |
| `licenses` | A state list of licensed groups without game days (Indiana). |
| `times` | A state list with days and hours (Michigan, Virginia), one file per state (`TIMES_FILES`). |

The home page shows a button for each state with a list on the site (`LISTED` in the generator) and keeps
every other state behind "More states, A to Z". "Where these lists come from" on the home page gives
sources for the listed states only; every other state is linked there and sourced on its own page.

Two optional fields, `lead` and `description`, replace the standard wording on a state page whose
situation the standard wording would misstate. Hawaii uses both (the state does not license bingo, so
only free games are listed) and Tennessee uses `lead` (bingo only at yearly nonprofit events).

How the states fall out (all checked November 17, 2026; each entry's `sources` has the detail):

- **Licensing is local, so there is no state list:** Alabama (local constitutional amendments),
  California (city and county ordinances), Connecticut (each municipality), Maryland (county by county),
  South Dakota (notice to the county or city), Vermont (no license; nonprofits may run games of chance).
  New Jersey and Rhode Island register or approve at the state level and license locally.
- **Hawaii** does not license bingo. **Tennessee** allows it only at yearly nonprofit events.
- **Everywhere else** a state office licenses bingo and is named with its phone number where the
  office publishes one.

### Virginia (loaded November 17, 2026)

Virginia's Office of Charitable and Regulatory Programs (VDACS) publishes a directory of bingo sessions as
a PDF, "Registered Gaming Activity", grouped by locality: organization, location, address, permit dates,
the day, and the times the doors open and close. The copy read was generated September 1, 2026
(`list_as_of`). `scripts/import_virginia_bingo.py` reads it by column position and keeps the weekly
sessions. It leaves out one-day dated events, cancelled rows and rows that ended before the review date.
Organizations at one address become one hall, as with Michigan.

- **Hours are door times**, not the first game. The state note and each card say so.
- **No promised dates.** The directory lists dates each game skips, so every Virginia card shows
  "Usual bingo days" and tells people to call, instead of a next date.
- **Social quarters.** Rows the state marks "[Social Quarters]" carry that label and a note that the game
  may be for members and their guests.
- **Counties.** The directory has no county. The script asks the U.S. Census Geocoder: the address first,
  then another hall in the same ZIP code, then the centre of the ZIP code (it prints which halls used a
  fallback). Independent cities are stored the Census way ("Richmond city") and shown as "City of Richmond".
- **One correction.** The directory gives ZIP code 23224 for a Castlewood address; Castlewood is 24224.
  The fix is in `ZIP_FIXES` and explained on the listing.

### Official lists to import next

These states publish something better than we show today. Import them in this order, best first. Do
the collection for several states first, then one build and one pull request.

| state | what the state publishes | where |
|---|---|---|
| Texas | Bingo hall locator with days and times. A script-driven lookup, so it needs a browser to read. | `https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf` |
| Montana | Places offering live keno or bingo, by county and city (fiscal year 2025 report). No days. | `https://dojmt.gov/wp-content/ftp/gambling/mtR35.pdf` |
| Idaho | Licensed organizations with county, phone and license number. No days. | `https://www.idaholottery.com/charitable-gaming/licensed-organizations` |
| Kansas | Licensed bingo organizations with address and phone. PDF. No days. | `https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf` |
| Maine | Charitable gaming organizations (January 16, 2026). PDF. | linked from `https://www.maine.gov/dps/gcu/charitable-gaming` |
| North Dakota | Licensed gaming organizations and gaming sites. PDFs. Covers all charitable gaming, not only bingo. | `https://attorneygeneral.nd.gov/gaming-licensees/` |
| New Mexico | Map and contact list of bingo, raffle and pull-tab locations. | `https://www.gcb.nm.gov/bingo-raffle-pull-tab-map-locations-and-info/` |
| Mississippi | Map of charitable gaming licensees. | linked from `https://www.msgamingcommission.com/charitable_gaming` |
| Minnesota | Licensed organizations and the sites where they operate. | `https://mn.gov/gcb/` (Data) |
| District of Columbia | Calendar of licensed charitable events. | `https://dclottery.com/events?type=8&month=all&year=all` |
| Alaska, Louisiana, Washington | Permit or license lookups by name; not lists. | see each entry |

A state list with days and hours goes in `TIMES_FILES` (Michigan and Virginia). `licenses` is still
tied to Indiana's file: before a second list without days can load, give it a per-state file table like
`STARTER_FILES` and let the home page script show any `licenses` state the way it shows Indiana.

Some state sites turn away automated readers (Minnesota's Gambling Control Board, Montana's Department of
Justice pages, the Rhode Island State Police, New Jersey Consumer Affairs, Georgia's Secretary of State
and California's legislative code site). Read those in an ordinary browser. Do not try to get around the
block.

ZIP code to state comes from `data/public/zip-states.json`, built from the state column of the same
Midwire/GeoNames file as the ZIP centroids (checksum recorded there): `zip3` maps the first three digits
to a state and `exceptions` lists the few ZIP codes that sit in another state. The file covers the 50
states and DC only, so territories and military mail are not found. `zips.json` now holds every one of
those ZIP codes (about 1 MB before compression).

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
