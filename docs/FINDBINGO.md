# FindBingo.org

FindBingo.org is the multi-state bingo finder. Players type a ZIP code (or pick a state) and see
bingo near them, closest first. It covers Michigan, Texas, Virginia, Missouri, Indiana, Mississippi, Montana
and New Mexico with state data, serves the Ohio Bingo
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
| Missouri bingo games (halls, phone, day, start time, weeks of the month) | `data/public/missouri-bingo-sessions.json`, rebuilt by `scripts/read_missouri_finder.py` then `scripts/import_missouri_bingo.py` |
| Wisconsin bingo games (place, groups, day, start time, weeks of the month) | `data/public/wisconsin-bingo-sessions.json`, rebuilt by `scripts/import_wisconsin_bingo.py` from the state's occasion search, read in a browser |
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

## Every page speaks to who lands there (added November 23, 2026)

Travis's direction: "Every landing page should be specific to who's there looking for it, so that we seem tailored to
everyone." Each page that search or a link can land someone on has its own title, description, heading, Open Graph tags
and a sentence or two written to that visitor.

- **State pages** read `data/findbingo-landing.json` (`h1`, `title`, `description`, `welcome`) for every state and DC.
  Each is written to that state's likely player and its own law and lists (Florida talks to a retiree looking for a game
  this week and gives the two-days-a-week and 18-and-older limits; Texas leads with the state Bingo Hall Locator; Montana
  says live bingo is run by licensed gambling businesses; states with no list say who to ask). `{towns}` (the most-listed
  towns, up to three), `{days}` (the weekdays with games, such as "every day of the week" or "Tuesday through Friday") and
  `{kinds}` ("halls and senior centers") are filled from the state's own listings at build time, so the words stay true as
  lists change. The welcome is the header's lead; the intro under the ZIP box names who oversees bingo there. The finder
  (ZIP box) is the first thing in every state page's main content.
- **Rules the build enforces** (`validate_landing`, `landing_words`): an entry for every state; every field different on
  every page; titles start with the state's name and "Bingo" and end "| FindBingo.org" (70 characters at most);
  descriptions 165, welcomes 330; every placeholder filled; and no counts (a number followed by halls, places, games and
  so on). Adding a state's listings never needs a copy change, but if a welcome names something the list no longer has
  (Pennsylvania names fire companies, posts and parishes; Washington names Elks and Eagles), update the welcome.
- **Ohio** (findbingo.org/ohio/) takes its title, description, heading and welcome from the same file's `OH` entry
  (`scripts/bingo_site.py`); the guide's own `bingo.html` keeps its wording.
- **Home page:** after the heading, "What brings you here?" offers four big choices that go only to pages that exist:
  Find a game near me (puts the cursor in the ZIP box), I run a bingo hall (`halls/`), I want to learn to play (`learn/`)
  and My charity wants bingo support (`halls/#partners`, which opens with a paragraph for charities). Two across on phones.
- **Other pages:** the bingo class speaks to a first-timer nervous about the unwritten rules; the halls and advertise pages
  to a hall volunteer or manager trying to fill seats (suppliers and distributors have `halls/#suppliers`); about, privacy
  and terms answer the question that brings people there. Their words live in `scripts/findbingo_site.py`.
- `tests/findbingo.cjs` checks the chooser, that every state page's heading, title, description, welcome and og:title are
  its own, that the finder comes first, and the Ohio, halls, advertise and class wording.

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

## Help for halls, state by state (added November 20, 2026)

Travis's direction: the people who run bingo are the ones who need information and advertising, and the
pitch has to match each state's own rules on bingo money.

- **State rules.** A state entry in `bingo-states.json` may carry `halls`: `money` (`must_give`, `may_give` or
  `own`), `money_note`, an optional `ad_note`, and `sources`. `must_give`: Ohio (veteran, fraternal and sporting
  groups must give part of their instant bingo profit to an outside charity, which is what the Veteran Home
  Guardians partnership asks a share of; the build requires Ohio to stay `must_give`) and Indiana (groups with at
  least 90% of receipts from gaming must donate 60% to a non-affiliated qualified recipient; outside Ohio the page
  offers help finding a local partner charity, never the VHG share). `may_give`: Virginia, Minnesota, West Virginia,
  North Dakota (we help find a local partner first). `own`: Kentucky, Michigan, Texas, Missouri, Pennsylvania, New
  York, Florida, Mississippi, New Mexico (the money stays with the group; we never ask for a share). Not yet
  summarized: New Hampshire (no clear rule found on November 21, 2026), Montana (live bingo is run by licensed
  gambling operators under a yearly permit, a different model) and the states without lists. The halls page groups
  states from this data, so adding a state's `halls` updates it. Research and figures are in
  `docs/BINGO-OPPORTUNITY.md`. Check a state's rule from its law or regulator before adding it.
- **State pages.** "Run a bingo game in ..." (`#run-a-game`) keeps the free listing email, then, where the state
  has `halls`, shows "What [state] law says about your bingo money" (`#money-rule`), any ad rule (`#ad-rule`),
  the sources and a "not legal advice" line, and the offer that fits the rule. A state without `halls` makes no
  claim about its rules.
- **https://www.findbingo.org/halls/** (`halls_page` in the generator): what we offer every hall, the three ways
  states treat bingo money, every checked state's rules with sources, links to every other state's
  `#run-a-game`, and a line for suppliers and distributors. Linked from every footer (the Ohio finder's too) and
  in the sitemap.
- **Hall game sites: $100 a month** (`HALL_SITE_PRICE`, owner direction November 20, 2026). We build a game site
  for a hall, host it, and post the updates the hall sends by email or text, for one flat monthly fee; the hall
  can stop any time, and its free listing stays either way. The price appears only on the Advertise page
  (`#hall-site`); state pages and the halls page describe the service and link there.
- The Advertise page now names halls and the groups that run games as the first audience, and labels the
  partnership "Community partner (Ohio)".

## Local partners, state by state (added November 22, 2026)

Travis's direction: outside Ohio, bingo support should go to a local organization doing work like Veteran Home
Guardians, not into Ohio. Each state can name one partner, and Find Bingo makes a standing, voluntary ask of that
state's halls to consider supporting it. It is never a condition of being listed and never touches which games appear
or their order. The partnerships also spread the guide and highlight the groups already doing the work locally.

- **Current partners:** New York, the **Mobility Independence Foundation** (themif.org; Travis is MIF's Finance
  Officer). Washington, **Light Upon Light** (luul.org, Everett; Travis advises Ronahi Zebari on its programs, and its
  materials use "differently abled").
- **Data.** A state entry may carry `partner`: `name`, optional `the` (true to write "the Mobility Independence
  Foundation" mid-sentence), `url`, optional `donate_url`, `about`, `ways` (the ways to help, written to that state's
  rule on bingo money), optional `note`, `since` and `sources`. The build requires the state's `halls` rule first, so
  every ask is written against a checked rule, and refuses a partner for Ohio (its partner is VHG, on the Ohio finder).
- **Pages.** The state page shows "Our [state] partner" (`#partner`) after the listings and any ad, before "Run a bingo
  game"; `#run-a-game` points to it; the halls page lists every partner under "Local partners, state by state"
  (`#partners`) with a "Tell us about them" email for suggested partners. Left off printed lists.
- **Write the ask to the state's law.** New York (`own`): net proceeds go to the licensee's lawful purposes, so the
  page asks for a gift or a bingo night for the partner only where the group's license and lawful purposes allow, and
  says to ask the municipal clerk first. Washington (`own`, added the same day): RCW 9.46.0205 says no part of bingo
  proceeds may benefit anyone but the group running the game, and WAC 230-07-010 limits net income to the purposes in
  the license application (games for named recipients need prior approval). So the Washington ask is outside the game:
  announcements and flyers, gifts from money that is not bingo proceeds, members giving on their own, volunteering.
  It never asks for bingo money or a game run for the partner.
- **Adding a partner.** Only with the organization's agreement (Travis's relationship). Check the state's `halls` rule
  from its law first, then write `ways` to fit it. `tests/findbingo.cjs` checks the panel, its place, the link to the
  money rule, that no VHG share is asked, and Washington's wording.

## The map (added November 21, 2026)

Every list on Find Bingo has a map above it, in the style of Nina's Map: the home page after a ZIP code or state search,
each state page, and the Ohio finder at findbingo.org/ohio/. The same map sits on the guide's nursing home and assisted
living page (`facilities.html`). Source: `assets/map/place-map.js` (written into each page by `scripts/place_map.py`) and
Leaflet 1.9.4 with Leaflet.markercluster 1.5.3 in `assets/map/`, served from the site itself, never from a CDN.

- The list stays the page. The map shows exactly the cards in the list and follows it as the list changes; every card with a
  pin gets a "Show on the map" button, and every pin's box has Call (or the phone lookup), Directions and "See the full listing".
- No list has street-level coordinates, so each card is pinned at the middle of its ZIP code, using the same ZIP code points
  as the distance search (`zips.json`). Each pin's box and the note under the map say so. A card whose ZIP code has no point
  stays in the list without a pin. No coordinates are made up.
- Nearby pins gather under a group dot that shows how many places it holds, as on the guide's facilities page and Nina's Map
  (owner direction, November 23, 2026; until then the dots were plain). The page text still never states counts.
- "Use my location" (beside the ZIP code box) finds the nearest ZIP code on the visitor's device and searches it.
- Big buttons and text, one-finger page scrolling on phones until the map is tapped, no scroll-wheel zoom until the map is
  clicked, Tab and Enter on pins and groups, dark mode on findbingo.org, and a "Hide the map" button that is remembered
  on the device (a hidden map loads nothing). Without JavaScript the map stays hidden and the plain list is the page.
- Map pictures come from OpenStreetMap (tile.openstreetmap.org), which sees visitors' IP addresses and the area shown; the
  privacy pages (findbingo.org/privacy/ and the guide's privacy.html) say so. `tests/place-map.cjs` checks the behavior.

## Practice card and bingo class (added November 19, 2026)

Travis's direction: give people a reason to come and look around, and a bingo class for new and older players.

- **Practice card** (home page, `#play`, in `templates/findbingo/index.html`). A just-for-fun 75-ball card:
  "Call a ball" draws a ball, shows its traditional nickname when it has one ("Legs eleven") or a short cheer,
  and marks the card unless "Mark my card for me" is turned off. A new card shows a clean bingo joke. Five in a
  row ends the game and points to the ZIP search. Nothing is stored or sent, it is left off printed lists,
  and it sits below the search so the search stays first. The header links to it and to the class.
- **Bingo class** at https://www.findbingo.org/learn/ (`LEARN` in `scripts/findbingo_site.py`): what happens
  on a bingo night, the card, the kinds of games and what the words mean, the unwritten rules, help for eyes,
  ears and hands, and what changes from state to state. It speaks in general terms and sends people to their
  state page and the hall for specifics. Linked from every footer (the Ohio finder's too) and in the sitemap.

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
  (two American Legion posts, two fire companies). Added November 19, 2026, each from the fire company's own
  bingo page unless noted: Library VFC (Wednesday), Broughton VFD (Monday and Thursday) and Holiday Park VFD
  (Thursday) around Pittsburgh; Stockdale VFD (Tuesday, from its own bingo-night posts through January 2026);
  Bushkill Township VFC near Nazareth (Wednesday; the street address is from the fire company's own site
  footer); and the Carmichaels & Cumberland Township VFC (Tuesday, from a Greene County event page first
  posted in 2023, which its card says). Library VFC's page gives only a volunteer's personal phone, so its
  card offers a phone lookup. Left out: games known only from newspaper calendars (Klecknersville Rangers,
  Northampton Banquet Center, Pitcairn Hose Company, Castle Shannon VFD), a borough page that no longer
  mentions bingo (Conway VFD), and a 2021 township page (Riverside VFC, Johnstown).
- New York: a group gets a bingo identification number from the State Gaming Commission's Division of
  Charitable Gaming and its license from the city, town or village clerk; no public list of games was
  found. Three listings. Gates Center Bingo's page gives no phone, so its card offers a phone lookup
  (a phone is optional for starter listings).
- Utah: state law prohibits gambling (Utah Code 76-9-1402), so only free bingo is listed: three
  Washington County Council on Aging senior centers.
- November 23, 2026, first pipeline batch (`scripts/bingo_pipeline.py merge`): Minnesota 6, Illinois 4, Iowa 5,
  Oregon 6, Colorado 3, Arizona 8 and New Hampshire 8 listings, mostly senior and community centers plus a few
  Elks and Legion games, each from the group's or city's own page. Left out: games found only on
  recreation-registration sites (Denver College View, Commerce City, Glen Ellyn), and Elks lodges whose pages
  don't say the game is open to the public (Victor CO, Prescott #330, Sierra Vista #2065). Leads and next steps
  are in `data/bingo-sources/registry.json`.
- "1st and 3rd Thursday" style schedules use the session `label`; the card says so in its note. The day
  filter still treats them as weekly.
- Left out for now: Irishtown Fire Company (a single December date), and both Washington State venues
  from that research (no regular day published). Their source pages could not be read on November 16.

Travis's rule for these lists (November 16, 2026): use the best information available and make it easy
for people to send corrections. Listings are not held back for phone confirmation.

**Pennsylvania, more listings (added November 23, 2026).** No county treasurer checked publishes a list of bingo licensees
(Allegheny, Montgomery, Berks, Westmoreland, Cumberland, Butler and Monroe were read; each gives only applications and the
law), so Pennsylvania stays a starter state. Added from each organizer's own page, read November 23: Washington Township VFC
102 (Apollo, Friday), St. Bartholomew Parish in Crabtree (Sunday; the start time changes with the season, so the card gives
no single time), Marion VFC 8 and Franklin Fire Company in Chambersburg (Tuesday and Wednesday), West Deer Township VFC No. 3
(Gibsonia, Saturday), West View VFD at the West View Banquet Hall (Sunday), Our Lady of Hope Parish's St. Valentine Frawley
Hall (Bethel Park, Tuesday) and St. Gabriel Church Hall (Pittsburgh, first and third Thursday), and Our Lady of Perpetual
Help Parish's St. Ursula Social Hall (Allison Park, Tuesday). ZIP 17202 had no point; its point is the Census Geocoder match
for the Marion VFC 8 address. Left out: Saint Mark Parish (Cranberry Township; dated registrations, not a weekly game) and
pages that would not load (Archangel Gabriel Parish, St. John XXIII Parish, Safety First VFC).
Later the same day, from each organizer's or government's own page: the Borough of Folcroft's bingo at the Ethan Joner
Community Center (second Tuesday of the month, 11 a.m.), Circleville VFD in North Huntingdon (Friday Night Bingo; the
street is the one the page gives for the department's hall) and Portland Hook & Ladder Co. #1 at the William Pensyl Social
Hall (the Borough of Portland's page says every Tuesday night and gives no time, so the card gives none). The Portland page
gives no ZIP code; the ZIP is the U.S. Census Bureau geocoder's match for the street, and the record cites that match.
Left out: a family-center bingo that is partly online, and leads seen only on news, event or aggregator sites.

**Florida, New York, Utah, more listings (added November 23, 2026).** From government pages: the City of Palm Bay's page
for the Greater Palm Bay Senior Activity Center (Wednesday 11:30 a.m. and Friday 6 p.m.), the Town of Saugerties calendar
for bingo at St. Joseph's Church Hall in Glasco (Thursdays, calling 6:45 p.m.; the calendar names no organizer or phone),
and Salt Lake County's November 2026 calendars for the Magna Kennecott (Monday, Wednesday, Friday 12:30 p.m.) and Eddie P.
Mayne Kearns (Wednesday and Friday 1:30 p.m.) senior centers. Left out: Hillsborough County's monthly bingo at the Brandon
Rec Center (within 25 miles of the St. Petersburg test ZIP, and monthly), the Taylorsville Senior Center calendar (bingo
days could not be tied to dates), Kentucky's 2023 list of licensed charitable gaming facilities (its licenses ran out in
2023 and 2024 and it has no ZIP codes), and a New Windsor fire company bingo that turned out to be in Maryland.

**Second organizer pass (November 23, 2026).** Each from the organizer's own page, read November 23:
Pennsylvania: Cherryhill Township VFC (Penn Run, Wednesday and Saturday), Granville Fire Company Event Center (last Sunday
of the month), American Legion Post 26 (Dillsburg, Wednesday; members and their signed-in guests), Our Lady of the Valley
Parish at Holy Family Social Hall (New Brighton, Wednesday), Archangel Gabriel Parish at Weirauch Hall (Coraopolis,
Monday), Denver Fire Company Social Hall (Thursday) and Fairfield Fire Hall (Thursdays and the first Friday; no start
time posted). West Virginia: Middleway VFC (Saturday). Kentucky: Kosair Shriners at Charity Hall Bingo (Louisville, Friday
and Sunday afternoons) and the Lafayette Band Association's Lex Go Bingo (Lexington, Thursday, Friday and Sunday; its page
gives two Sunday times, so the card gives none). New York: Shawnee VFC (Sanborn, Thursday). Where a page gave a street
without a ZIP code (Granville, Holy Family, Lex Go Bingo), the ZIP is the U.S. Census Bureau geocoder's match and the
record cites it. Left out: St. John XXIII Parish (its site shows a bot check), Resurrection Parish (page not found), a
Butler County Historical Society bingo (one dated night), Duncansville's monthly bingo (event page from 2025 only), the
American Saddlebred Legacy Foundation (no street), Bushkill Township VFC (no street), and fire companies that turned out to
be in Maryland or Virginia (Halfway, Glen Burnie, Dunn Loring).

**Kentucky, West Virginia, Pennsylvania (no state list of games).** No public statewide list of games with days
and times was found: Kentucky's Office of Charitable Gaming (now part of Kentucky Horse Racing & Gaming)
publishes county totals in its annual report; West Virginia's Tax Division links no licensee list;
Pennsylvania bingo licenses are issued by each county treasurer. All three are now starter states.

**Washington (starter state, added November 23, 2026).** File: `data/public/washington-bingo.json`. The
Washington State Gambling Commission's licensee lookup (public, on its MyAccount site) can filter by a bingo
license type and city or county, but gives no addresses or game times, so it is a lead list only. Every listing
came from the organizer's own page, read November 23, 2026: Olympia and Shoreline Elks (Elks' Washington
lodge calendar, dated into 2027), Oak Harbor and Kelso-Longview Elks (lodge pages and their November
2026 calendars), Wenatchee Eagles Aerie #204 (public Sunday bingo) and Mid-City Concerns in Spokane (November and
December 2026 calendars). Wenatchee's county is Chelan, the county the city sits in. Left out: Bellingham Elks #194 (Tuesday 5 p.m. on the Elks calendar; its ZIP 98229 has no map point yet), Sequim Elks and Port
Orchard Eagles (no current dated schedule), Burlington Senior Center (newest newsletter August 2026), Yakima's
Harman Center (its own brochures disagree on the day), Lake Chelan and Burien Eagles (members and invited guests
only), Manson Grange (season ended November 19) and games published only on Facebook. Washington's partner panel
(Light Upon Light) is unchanged; partner states now sit with the listed states on the home page.

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

The data pipeline (`scripts/bingo_pipeline.py`, `docs/BINGO-PIPELINE.md`) shows what is due for a recheck and
which states are thinnest (`docs/BINGO-COVERAGE.md`), and checks a researched batch before it is merged.

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
   For Missouri, run `python3 scripts/read_missouri_finder.py missouri-finder.json` (needs Python Playwright
   and Chrome), then `python3 scripts/import_missouri_bingo.py missouri-finder.json --reviewed <today>`.
   For Wisconsin, read the Department of Administration's Active Bingo Occasion Search
   (https://charitable.wi.gov/bingooccasion/search) in a browser. A blank organization filter is refused, so
   search by letters of the group name (each vowel, plus "VFW" and "#"), set 200 rows a page, and save every row as
   `organization,location,address,city,zip,date,time`; check each filter's row count against the site's. The
   shell proxy refuses the host, so this step is done in a browser. Then run
   `python3 scripts/import_wisconsin_bingo.py wi-occasions.csv --reviewed <today>`. It groups the dated
   occasions by street address, weekday and start time: a pattern held on most of those weekdays between its
   first and last date is weekly, one held on the same weeks of each month gets that label, other repeats are
   "some weeks", and single dates are left out.
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
| `times` | A state list with days and hours (Michigan, Texas, Virginia, Missouri), one file per state (`TIMES_FILES`). |

The home page shows a button for each state with a list on the site (`LISTED` in the generator) and keeps
every other state behind "More states, A to Z". "Where these lists come from" on the home page gives
sources for the listed states only; every other state is linked there and sourced on its own page.

Kentucky and West Virginia are `starter` states (November 17, 2026): neither publishes a list of games with
days and times, so their files hold schedules that halls and organizers publish themselves.

Each state page's heading, title, description and opening come from `data/findbingo-landing.json` (see
"Every page speaks to who lands there" below), so no state needs special wording in `bingo-states.json`.

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

### Missouri (loaded November 19, 2026)

The Missouri Gaming Commission's [Find Local Bingo Games](https://www.mgc.dps.mo.gov/BingoWebLocal/frmWebFindLocalBingoGame.aspx)
page lists each licensed game: the location of play with its street and phone, city, county, start time, the
weekday, and which weeks of the month it is played ("Every", "1st & 3rd" and so on). Use the `www.` address:
`mgc.dps.mo.gov` without it fails certificate checks. The page is a script-driven grid ten rows at a time, so
`scripts/read_missouri_finder.py` reads it in a headless browser, clicking Next to the last page and checking
the row total the page reports. On November 19 it read every row.

`scripts/import_missouri_bingo.py` makes one hall per street address, keeps the hall's phone, and turns the
weeks column into a session `label` ("First and third Saturday of the month"). A hall with any such game carries
a `schedule_note`, so its card shows "Usual bingo days" instead of promising a next date; weekly-only halls show
the next bingo day, as Texas does.

- **Start times only.** The page gives no end time, so Missouri is in `START_ONLY` in the generator and its
  sessions have no `end`. The state note says the times are start times.
- **ZIP codes.** The page gives none. The U.S. Census Geocoder supplies the ZIP code from the street address.
  Where it cannot match the address (highway corners, county roads, and some town streets), the importer uses
  the town's ZIP code from the same Midwire/GeoNames file as the site's ZIP points (checksum checked), and the
  listing says so. A town filed in that file under another post office name goes in `TOWN_ZIPS` with a reason
  (Shrewsbury: 63119). Halls already in the data file keep their ZIP code on a refresh.
- **Counties** come from the state page itself ("St. Louis City" is stored the Census way, "St. Louis city").
  Michigan's pending-county check is per state now, because Missouri also has a Clinton County.

### Kansas (ready, held out November 23, 2026)

**Not published.** Kansas stays `none` (link to the state's PDF only). An earlier note (November 17) recorded that the
posted list dates from July 2022, so its licenses would have lapsed, and nothing on November 23 showed it is current. The
importer and the checks below are kept so Kansas can be loaded once the list is confirmed current: add
`'KS': 'kansas-bingo-licenses.json'` to `LICENSE_FILES`, run the importer on a fresh download, set the state entry to
`licenses` with a `license_note` that says the list is undated, and add the Kansas checks back to `tests/findbingo.cjs`.

The Department of Revenue's "Bingo Organizations" PDF (https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf, linked from
https://www.ksrevenue.gov/bustaxtypesbingo.html) gives one block per licensed organization: license number (BNG...), name,
street, city and ZIP, and phone. It carries no date, county, game days or license end date; the bingo page says the license
year runs July 1 to June 30, but the list does not say which year, so no end date is shown. `scripts/import_kansas_bingo.py`
reads `pdftotext` output of the PDF. It leaves out a block whose street is only a post office box, drops a box written beside
a street (the state's wording stays in `listed_address`), and leaves out a street it cannot read without guessing
("3381 326 N Kansas Ave") and a block with a Missouri ZIP code. The county comes from the ZIP code's county in the same
Midwire/GeoNames file as the site's ZIP points (checksum checked). The addresses are the ones the state lists for each
organization, which may not be where it plays, so the state note must say to call. On November 23 the PDF host refused this
session's downloader, so the list was read through a page reader, then every one of the 181 blocks was checked against the
PDF field by field (name, street, city, ZIP, phone) and the first page by eye. Two blocks run to six lines: BNG000219 puts its
post office box on its own line (kept, box dropped), and BNG000422 gives the same street with two ZIP codes (left out). The
next refresh should run the importer on a fresh download.

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

Which states to build first, by how much money charitable gaming raises there, is in
`docs/BINGO-OPPORTUNITY.md` (November 20, 2026).

These states publish something better than we show today. Import them in this order, best first. Do
the collection for several states first, then one build and one pull request.

| state | what the state publishes | where |
|---|---|---|
| Idaho | A search box over charitable gaming licenses, read only in a browser. Each result gives name, game type (Bingo, Raffle or both), street, county, phone, license number and renewal date, but no city or ZIP. **Not loaded (November 23, 2026):** the County, City and Zip boxes match exactly (a partial ZIP finds nothing), so a city and ZIP from the state's own data would take one search per candidate ZIP for each county. | `https://www.idaholottery.com/charitable-gaming/licensed-organizations` |
| Kansas | Licensed bingo organizations with address and phone. PDF. No days, no date. **Held out (November 23, 2026):** the November 17 check found the file is from July 2022, and Kansas licenses run July to June, so the licenses on it may have lapsed. The document shows no date and the host refused this session's downloader. `scripts/import_kansas_bingo.py` is ready (all 181 blocks were checked against the PDF on November 23); load it once the state's list is confirmed current. | `https://www.ksrevenue.gov/pdf/BingoOrganizations.pdf` |
| Maine | Charitable gaming organizations (January 16, 2026). PDF. **Not loaded (November 23, 2026):** an NPO on the list is authorized for bingo, raffles and games of chance together, so the list cannot say which groups hold bingo, unlike New Mexico's bingo licenses; many addresses are post office boxes, and the PDF would not load on November 23. | linked from `https://www.maine.gov/dps/gcu/charitable-gaming` |
| North Dakota | Licensed gaming organizations and gaming sites. PDFs. **Not loaded (checked November 19, 2026):** the sites list (August 2026) is mostly bars and restaurants where organizations sell pull-tabs, with no column for the games played, so it is not a list of places to play bingo. | `https://attorneygeneral.nd.gov/gaming-licensees/` |
| Minnesota | Licensed organizations and the sites where they operate ("Find Gaming Sites", with a tab-separated download dated November 2026). **Not loaded (read in a browser November 23, 2026):** the site list has site, organization, city, county, license and site numbers and address, but no column for the games played, and most sites are bars selling pull-tabs. Per-site game types are only in the Power BI "Site Financial Data" tool, one site at a time. | `https://mn.gov/gcb/data/` |
| District of Columbia | Calendar of licensed charitable events. | `https://dclottery.com/events?type=8&month=all&year=all` |
| Alaska, Louisiana, Washington | Permit or license lookups by name; not lists. | see each entry |

A state list with days and hours goes in `TIMES_FILES` (Michigan, Texas, Virginia and Missouri); one that gives
start times only is also in `START_ONLY` (Missouri). A list of
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

## Featured bingo events ($100)

Owner direction, November 20, 2026. A hall or group can have a dated bingo event (a special bingo night, a
fundraiser, a holiday game) featured for $100. It shows in its own box labeled "Featured events · paid listings":

- on the home page, for ZIP searches within the chosen distance of the event and when its state is picked;
- on its state's page, above the county list;
- on the Ohio finder (findbingo.org/ohio/) for Ohio events.

It shows from the day it is added until the day of the event (Eastern time), then hides itself. It never adds
to, removes or reorders the free listings, and the event's own link is marked `rel="sponsored"`.

To add one, after it is paid: add an entry to `data/findbingo-events.json`, then run
`python3 scripts/build_public.py`.

```json
{"id": "oh-marengo-fire-dec", "title": "Fire Department Fundraiser Bingo", "host": "Marengo Volunteer Fire Department",
 "address": "1 Firehouse Road", "city": "Marengo", "state": "OH", "zip": "43334", "date": "2026-12-05",
 "start": "18:30", "end": "21:00", "details": "Early bird at 6 p.m. Proceeds buy new turnout gear.",
 "phone": "419-555-0100", "url": "https://example.org/event", "paid_on": "2026-11-20"}
```

Required: `id`, `title` (90 characters at most), `host`, `address`, `city`, `state`, `zip` (in that state),
`date`, `start` (24-hour HH:MM), `details` (200 characters at most) and `paid_on`. Optional: `end`, `phone`
(555-555-5555 form) and `url` (https). `paid_on` stays in this file and is not published. The event must be run by a
group allowed to hold bingo where it takes place. `tests/findbingo-events.cjs` checks all of this.
