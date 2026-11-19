# FindBingo.org

FindBingo.org is the multi-state bingo finder. Players type a ZIP code (or pick a state) and see
bingo near them, closest first. It covers Michigan and Indiana with state data, serves the Ohio Bingo
Finder at findbingo.org/ohio/, and lists organizer-published games in Pennsylvania, New York, Florida,
Utah, Kentucky and West Virginia ("starter" states). States without a list yet say so plainly. Every
listing has a "Report a change" email link, and every state has a free way for halls to send game times.

Started November 15, 2026, at Travis's direction: one national finder, neighboring states first.

## How it is built

| Piece | Where |
| --- | --- |
| State facts, regulators and sources | `data/public/bingo-states.json` |
| Michigan weekly bingo (venues, days, licensed hours) | `data/public/michigan-weekly-bingo.json` |
| Texas bingo halls (halls, phone, licensed days and times) | `data/public/texas-bingo-halls.json`, rebuilt by `scripts/read_texas_locator.py` then `scripts/import_texas_bingo.py` |
| Virginia bingo sessions (halls, days, doors-open and doors-close times) | `data/public/virginia-bingo-sessions.json`, rebuilt by `scripts/import_virginia_bingo.py` |
| Indiana groups with a current license that allows bingo | `data/public/indiana-bingo-licenses.json` |
| Mississippi halls licensed for bingo | `data/public/mississippi-bingo-licenses.json`, rebuilt by `scripts/import_mississippi_bingo.py` |
| Montana places with a live bingo permit | `data/public/montana-bingo-permits.json`, rebuilt by `scripts/import_montana_bingo.py` |
| New Mexico groups licensed for bingo, raffles or pull-tabs | `data/public/new-mexico-bingo-licenses.json`, rebuilt by `scripts/import_new_mexico_bingo.py` |
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

## Privacy, advertising and ad places (added November 19, 2026)

Travis's direction (November 19, 2026): Find Bingo may carry advertising. Listings stay free and can never
be bought; ads are labeled and never decide which games are listed or their order.

- **Privacy** is at https://www.findbingo.org/privacy/ and **Advertise** at https://www.findbingo.org/advertise/.
  Both are built by `scripts/findbingo_site.py` (`PRIVACY`, `ADVERTISE`), linked from every footer (the Ohio
  finder's too) and listed in `sitemap.xml`. If the site's setup changes (another visit counter, an ad network
  goes live, the host changes), update the privacy page in the same pull request.
- **Ads** live in `data/findbingo-ads.json`, an empty list by default. With no ad running, the pages carry no
  ad markup at all. An ad is an object with `slot` (`home`; `state` for every state page; or `state:michigan`
  for one state), `sponsor`, `text` (200 characters at most) and an `https://` `url`; optionally `image` (a file
  under `assets/`, served from `ads/`) with `alt`, and `start` and `end` dates (`YYYY-MM-DD`, Eastern time,
  both days included). A dated ad is written hidden and shown only on its dates by a small script, so a page
  built earlier never shows it on the wrong day. The build refuses two ads that could show in one place at once.
- **Placement.** The home page's ad sits below the search results and state list, before "Run a bingo game?".
  A state page's ad sits after the listings, before "Run a bingo game in ...". Never inside a list of games or
  a card, never above the main content. Ads are left out of printed lists.
- Review every ad before it runs and turn down misleading ones (the Advertise page promises this). Remove an
  ad's entry once it ends; an ad picture removed from the list is not deleted from `findbingo-site/ads/` by the build.

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

**Kentucky, West Virginia, Pennsylvania (no state list of games).** No public statewide list of games with days
and times was found: Kentucky's Office of Charitable Gaming (now part of Kentucky Horse Racing & Gaming)
publishes county totals in its annual report; West Virginia's Tax Division links no licensee list;
Pennsylvania bingo licenses are issued by each county treasurer. All three are now starter states.

**Kentucky and West Virginia (starter states, added November 17, 2026).** Files:
`data/public/kentucky-bingo.json` and `west-virginia-bingo.json`, in the same shape as Florida's. Every
listing came from the organizer's own page, read on November 17, 2026; search results and directory
sites were used only to find leads.

- Kentucky: American Legion Post 12 (Thursday, at Jackpot Charity Bingo in Richmond; the post's page says
  bingo is there, not at the post home), Frankfort VFW Post 4075 (Thursday; the page gives no separate bingo
  address, so the card says to call), Hardin Post 113 in Elizabethtown (Friday and Sunday; the first time is
  the early bird game, the notes give doors and main game) and the Campbell County Senior & Wellness Center
  in Highland Heights (Friday, from the county's November 2026 calendar).
- West Virginia: Dunbar Athletic Boosters (Saturday), the City of Charleston's Martin Luther King Jr.
  Community Center (senior bingo, 3rd Thursday), the Westside Senior Center in Westover (Wednesday; the
  street address is the one in the City of Westover page footer, which a Dominion Post senior column also
  gives for the center), the Putnam County Aging Program's Buffalo, Hometown and John Henson (Hurricane)
  centers, and the Marion County senior centers in Fairmont and Mannington (North Marion says "most"
  Mondays and Thursdays).
- Left out: Middleway Volunteer Fire Company (Saturday bingo, but its site gives only a post office box),
  Owensboro Catholic Schools at Big Blue Bingo Hall (says "each weekend" without naming the days), the
  Lafayette Band Association's Lexington games (the page gives two addresses and no ZIP code for the hall),
  St. Stanislaus (no state on the page), Lexington Parks and Recreation bingo (single dated events), the
  Brooke County Senior Center (bingo named but no day) and news or tourism listings without an organizer page.
- Next leads: Kentucky's Office of Charitable Gaming has published a licensed facility list (a June 2023
  PDF on dcg.ky.gov, with facility name, county, address and city, but no game days). A current copy would
  give Kentucky a `licenses`-style backbone like Indiana's. **Checked November 19, 2026:** the listings page
  still offers only the June 2023 files, and House Bill 904 (effective July 15, 2026) required facilities
  licensed before that date to transfer their licenses, so the 2023 list is likely out of date. Not loaded.

**ZIP codes.** The guide's GeoNames/Midwire centroids (CC BY 3.0, attributed in the footer), limited
to the covered states' ZIP prefixes (Florida's military 340 prefix excluded). ZIP 49037 (Battle Creek) is missing there; its point comes from the
U.S. Census Geocoder match for the bingo hall at 228 N 20th St.

## Refreshing the lists

1. Re-read the Michigan lookup and the Indiana list as above. For Virginia, download the state's current
   directory and run `python3 scripts/import_virginia_bingo.py bingo_events.pdf --reviewed <today> --geocode`,
   then set Virginia's `list_as_of` in `bingo-states.json` to the listing date the script prints.
   For Mississippi, run `python3 scripts/import_mississippi_bingo.py --reviewed <today>` (opens the map in a
   headless browser), then set `list_as_of` to the map date it prints.
   For Montana, download the current list and run `python3 scripts/import_montana_bingo.py mtR35.pdf --reviewed <today>`,
   then set `list_as_of` to the date it prints.
   For New Mexico, run `python3 scripts/import_new_mexico_bingo.py --reviewed <today>` (it downloads the page).
   For Texas, run `python3 scripts/read_texas_locator.py texas-locator.json` (needs Python Playwright
   and Chrome), then `python3 scripts/import_texas_bingo.py texas-locator.json --reviewed <today> --geocode`.
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
| `licenses` | A state list of licensed groups or permitted places without game days (Indiana, Mississippi, Montana, New Mexico), one file per state (`LICENSE_FILES`). |
| `times` | A state list with days and hours (Michigan, Texas, Virginia), one file per state (`TIMES_FILES`). |

The home page shows a button for each state with a list on the site (`LISTED` in the generator) and keeps
every other state behind "More states, A to Z". "Where these lists come from" on the home page gives
sources for the listed states only; every other state is linked there and sourced on its own page.

Kentucky and West Virginia are `starter` states (November 17, 2026): neither publishes a list of games with
days and times, so their files hold schedules that halls and organizers publish themselves.

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

### Texas (loaded November 17, 2026)

The Texas Department of Licensing and Regulation runs the
[Bingo Hall Locator](https://bsc.txbingo.org/bsp/faces/bspBingoHallLocator.jsf). Each row is a licensed
organization with its hall, the hall's phone, the address and the licensed days and times. The page is
script-driven and shows a screenful of results at a time, so `scripts/read_texas_locator.py` reads it in
a headless browser: one empty search, then the results table is scrolled to the end. On November 17 it
read every row but three of those the locator reported; identical rows count once.

`scripts/import_texas_bingo.py` makes one hall per address (the organizations that share it are listed
with their own times), keeps the hall's phone, writes names in capitals only where the locator does
or for short forms such as VFW, and finds counties with the shared Census helper
(`scripts/bingo_counties.py`), which Virginia's importer uses too. Hours are licensed times, so Texas
cards show the next bingo day, as Michigan's do.

### Montana (loaded November 17, 2026)

Montana's Gambling Control Division publishes "Establishments Offering Live Keno and/or Bingo" by county
and city (fiscal year 2027, dated October 30, 2026). `scripts/import_montana_bingo.py` keeps places whose
permit covers bingo. It leaves out places whose listed address is a post office box or in another town or
state: the list then shows a mailing address, not the door to walk in, and the state note on the site
says so. A live bingo or keno permit is annual and expires June 30 (Montana Code 23-5-407 and the
division's FAQ), so the fiscal year 2027 permits show as current through June 30, 2027. The list has no
game days and no phones, so Montana is a `licenses` state like Indiana.

### New Mexico (loaded November 17, 2026)

The Gaming Control Board's "Bingo, Raffle, & Pull-Tab Map Locations and Info" page lists each licensed
group by town with its address and phone, below the map. It does not say which of bingo, raffles or
pull-tabs a group holds, and gives no license number, end date or list date. So New Mexico cards say
"Licensed for bingo, raffles or pull-tabs · call to ask about bingo" (`license_badge`), the results
heading says the same (`license_heading`), and no end date or list date is shown. The town comes from
the page's town headings, because one address line misspells Alamogordo.

### Mississippi (loaded November 17, 2026)

The Gaming Commission's "Locate Charitable Gaming Licensees" map (a Mapline map linked from its Charitable
Gaming page) loads each licensee's charity, bingo hall, physical address, license number and expiration,
and games played. `scripts/import_mississippi_bingo.py` opens the map in a headless browser, keeps
licensees whose games include bingo, and leaves out any whose license on the map has passed its end date
(ten on November 17, which may have renewed without the map catching up; the state note says such halls
are not shown). The contact person, email and phone are not republished: they sit together on the map
and may be personal, so cards offer a phone lookup. The map was last updated September 29, 2026.

### Official lists to import next

These states publish something better than we show today. Import them in this order, best first. Do
the collection for several states first, then one build and one pull request.

| state | what the state publishes | where |
|---|---|---|
| Idaho | A search box over charitable gaming licenses (bingo and raffles together), read only in a browser. Not a list of places to play. | `https://www.idaholottery.com/charitable-gaming/licensed-organizations` |
| Kansas | Licensed bingo organizations with address and phone. PDF. No days. **Not loaded:** the file is from July 2022 and Kansas licenses run July to June, so every license on it has lapsed. Load it only when the state posts a current list. | `https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf` |
| Maine | Charitable gaming organizations (January 16, 2026). PDF. Covers raffles and games of chance too, and many addresses are post office boxes, so it is not a list of places to play. | linked from `https://www.maine.gov/dps/gcu/charitable-gaming` |
| North Dakota | Licensed gaming organizations and gaming sites. PDFs. **Not loaded (checked November 19, 2026):** the sites list (August 2026) is mostly bars and restaurants where organizations sell pull-tabs, with no column for the games played, so it is not a list of places to play bingo. | `https://attorneygeneral.nd.gov/gaming-licensees/` |
| Minnesota | Licensed organizations and the sites where they operate ("Find Gaming Sites"). **Not loaded:** the site sends automated readers to a captcha page (November 19, 2026). Read it in an ordinary browser, and check whether it says which sites run bingo before loading it. | `https://mn.gov/gcb/data/` |
| District of Columbia | Calendar of licensed charitable events. | `https://dclottery.com/events?type=8&month=all&year=all` |
| Alaska, Louisiana, Washington | Permit or license lookups by name; not lists. | see each entry |

A state list with days and hours goes in `TIMES_FILES` (Michigan, Texas and Virginia). A list of
licensed groups or permitted places without days goes in `LICENSE_FILES` (Indiana, Mississippi,
Montana and New Mexico); each record needs `license_type` and may carry `license_number`, `license_expires` and `phone`.
A state may set `license_badge` and `license_heading` when "licensed for bingo" would overstate its list.

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
