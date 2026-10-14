# Ohio bingo: coverage, evidence and statewide expansion

Updated October 9, 2026. Canonical venue records: `data/public/ohio-bingo.json`. Generated page: `bingo.html`, rebuilt by `scripts/build_public.py` through `scripts/bingo_edition.py`. The Ohio community section links to it; other states do not inherit Ohio venues. Bingo records remain separate from benefits resources and their counts.

## Six initial venues

Three charitable sessions: Marengo Legion 710, Cardington Legion 97 and Northmor Music Boosters at Hope Cabins (Morrow). Three senior-center programs: SourcePoint (Delaware), Station Break (Knox) and Marion Senior Center (Marion).

Travis confirmed Cardington and Marengo bingo activity from firsthand attendance/involvement. This confirms the activity exists, not the current schedule, prices, license or accessibility. Cardington's Saturday 6 p.m. time comes from Ohio Bingo Bugle and remains marked for confirmation. No Cardington public phone was invented.

Official organizer sources establish the other activities. Northmor's earlier full school page listed Tuesday 7 p.m.; the later page renders without this text. The venue still confirms Tuesday bingo, but the start time remains a recheck. SourcePoint's full Fall 2026 flyer was reviewed in the earlier research; later retrieval failed. Preserve its stated quarter and holiday inconsistency, and recheck before January 2, 2027. All six venues have unverified accessibility. Marion offers bingo but no current session time was established.

## Statewide source

Source: https://charitable.ohioago.gov/Charitable-Bingo/View-Authorized-Bingo-Locations

The user supplied the readable official 545-page report printed October 2, 2026. It is extracted with source hash, page and row provenance. All location and type entries reconcile; the Type I subset is public. Three existing charitable listings now include matching license information. See BINGO-REPORT-PARSING.md for validation and preserved source errors.

Type definitions: https://codes.ohio.gov/ohio-administrative-code/rule-109:1-4-08

- Type I: traditional bingo.
- Type II: instant/electronic instant games at bingo sessions; do not count as an additional traditional venue.
- Type III: instant/electronic instant games outside sessions; do not infer a traditional session.

Authorized days are licensing fields, not a confirmed current event calendar. Add organizer schedule links, admission, costs and accessibility separately. Senior-center activities remain separately categorized; this project has not assessed their individual licensing requirements.

## Next work

1. Add organizer details to state-listed locations as they become available.
2. Confirm Cardington session time, public contact, costs and attendance rules.
3. Resolve Marengo's conflicting door times and SourcePoint's holiday date inconsistency.
4. Confirm Northmor's current start time and Marion's session schedule.
5. Ask venues about step-free entry, accessible restrooms/parking, companions and group registration.

No agency or venue outreach was sent in this update. Inclusion is independent of VHG donations or sponsorships.

## Validation limits

Functional checks cover county/category/search boundaries, generated-data synchronization, unknown accessibility and license labels, firsthand scope, correction links and isolation from other state editions. Browser rendering and print pagination could not be reviewed in this environment: Chromium was absent and its download failed. The new page uses responsive single/two-column cards and keeps sources visible in print; visual QA remains a follow-up.

## Statewide Type I coverage

Added all 717 Type I entries from the October 2, 2026 official report. Three match existing researched venues and are shown once, giving 720 displayed records including three senior-center activities. State-listed days are labeled separately from organizer schedules; blank prices remain unknown. Listings remain separate from benefits/support resource counts. See BINGO-REPORT-PARSING.md for extraction checks and source limitations.

## Visitor details and schedule enrichment

Visitors can submit venue, county, schedule/prices, public source URL (including Facebook) and optional reply contact through a form. Each card prefills venue/county. Submission opens an email draft to travis@vethomeguard.org; it does not send automatically or require a server.

October 9: Ohio Bingo Bugle supplies updated Cardington/Northmor times and recurring schedules for Mansfield Firefighters, Tyger Boosters, Wyandot County Humane Society and WCAP. Early-bird times remain identified separately. Repeated unknown-field cautions are removed; sources and license information are collapsed, with one schedule-change note above the list. A session-time filter finds enriched cards.

## ZIP distance browsing

ZIP and radius are the primary search controls, with nearest-first results and distance on each card. Supported radii: 10, 25, 50, 100 and 200 miles, or any distance. County remains optional. ZIP/radius filters persist in shareable URLs and reset together. Distance uses ZIP centroids and the haversine formula; it is approximate straight-line mileage, not driving distance. Locations without a usable ZIP remain in the statewide list and are omitted from distance results.

ZIP lookup data is bundled in the page, so searches require no geocoding API or browser location permission. Coordinate source, hash, upstream commit and attribution are recorded in data/public/us-zip-centroids-source.json. Refresh with scripts/build_bingo_zip_data.py using upstream all_us_zipcodes.csv. Data attribution: GeoNames via Midwire free_zipcode_data, CC BY 3.0.

## October 9 nearby schedule update

Added organizer-published sessions for Delaware VFW Reed-Miller Post 3297 (Sunday 2 p.m., doors noon, public attendance) and Crawford Humane Society (Wednesday 6:30 p.m., doors 4 p.m., $29/$41 packets). The Crawford dedicated bingo page and October state report agree on PAWS Center; homepage mentions Wynford, retained as a location discrepancy in source details. State-authorized days remain separate and unchanged. Delaware Eagles gains a contact for Wednesday session questions; no start time was inferred. Twelve total listings now have session times.

## Full Bingo Bugle pull: October 2026

Retrieved the complete public web game directory and 28-page October 2026 issue on October 9. Visually reviewed raster advertisements, not just PDF text. Source snapshot: `data/source/ohio-bingo-bugle-2026-10-09.json`; includes retrieval hashes, per-row matching outcomes, issue metadata and conflicts. No publisher PDF or page images are republished.

All 34 web rows are accounted for: 28 matched rows, one shared Valley Street hall listing explicitly naming three operators, three identity/location review rows, and two instant-ticket-hour rows. The printed directory additionally lists Fisher Catholic. The finder now has 38 entries with times (including three separate Valley Street authorizations), not 38 distinct halls.

Important corrections: Northmor’s October ad limits play to October 6 and 20; Vermilion’s ad gives November 4 and December 2 after October 7; Children’s Toy Fund closes October 31. Published date limits appear on cards. October-only Grove City prices carry an end date. Preserve state-authorized days separately. Massillon Knights, St. Clement and Tri-County remain in the source review queue due to license/address conflicts; do not publish a fuzzy match.

Monthly routine: download the public directory and full issue; run `python3 scripts/extract_bingo_bugle.py DIRECTORY.html --output CANDIDATES.json --reviewed-on YYYY-MM-DD`. The extractor handles malformed TH/TD rows but deliberately does not apply fuzzy matches. Check issue month, review ads visually, match licenses/addresses, compare existing provider information, record exceptions/offer expiry, and rerun validation before publication. Extracting a new issue does not automatically prove an old schedule has continued.


## Published-session day filter

October 9: added Bingo day (Today, Tomorrow, or a weekday) beside the activity filter. It combines with ZIP/radius, county and search, and is preserved in shareable links. Day matching uses `session_days` (Sunday=0 through Saturday=6) or exact ISO `session_dates`, never `authorized_days`. Every record with a published schedule requires one of these fields. `session_excluded_dates` records closures; `session_exceptions` supplies changed-time text on a selected date. SourcePoint November 25 shows the earlier-session exception instead of its usual start time.

Dated schedules with no upcoming dates, and schedules after `schedule_valid_until`, leave the day/session-time results. Expired `price_valid_until` offers are hidden. Venues remain in the full directory, with a short request for upcoming dates; source records remain intact for review. Dates use the visitor's local calendar day. A weekday result displays its next eligible date; Today and Tomorrow match only that exact date. Northmor October 6/20 and Vermilion November 4/December 2 remain date-specific. Children's Toy Fund October 31 closure is excluded. SourcePoint Fall schedule ends January 2, 2027. This change adds no new venues or inferred session times.

## October 11 usability update

Added shortcuts for published session times, today, tomorrow and senior centers. Cards show the next published date even without a day filter. Statewide bingo cards put upcoming published dates first; ZIP results retain distance ordering. Ohio's Eastern timezone controls Today/Tomorrow. Fixed future one-off sessions leaking into exact-date filters.

Added VHG branding, the existing donation page and a sponsorship inquiry link, plus an operator invitation to provide public session details. GoatCounter now uses the dedicated `vhg-guide` endpoint for page views, shared with the VHG guide. Bingo appears under `/vhg-veteran-resident-guide/bingo.html`. URL queries and fragments are excluded, including search and ZIP filters; no submission or contact events are sent. Dashboard totals require signed-in verification. Venue review dates and source records are unchanged.

## October 11 game research — two passes

Added published schedules to 16 existing state-listed entries and expanded ACO to include Thursday. The combined page now has 54 entries with schedule details, up from 38; total venue/entry count remains 732. All new additions came from full organizer pages matched to the state-listed organization and location. See `research/bingo-session-review-2026-10-11.json` for per-record changes, source URLs and deferred leads.

Pass 1: Willoughby South Boosters, Three Pits and a Lady (Circleville), Tiffin Moose, Saint Isidore at Sacred Heart of Mary (Louisville), St. Elizabeth Ann Seton (Milford), St. Mary School (Marietta), Saint Ambrose (Brunswick), Delphos Knights Council 1362 and Brightside (Salem). Pass 2: Massillon Knights Foundation, St. Teresa of Avila (Cincinnati), Lisbon Lions, Little Flower (Toledo), Bazetta Cortland Optimist, St. Lawrence (Cincinnati), St. Clement (Navarre) and ACO (Parma).

Saint Ambrose uses only its five published upcoming regular Friday dates. Brightside uses its five dated October–December events, including separate start times and prices for October 29 and December 3; generic fourth-Thursday wording is not treated as a recurrence. Massillon's 6:30 p.m. organizer time conflicts with Bugle's 7 p.m., and ACO's Tuesday early-bird time differs by 15 minutes; each discrepancy is disclosed. License authorization days were not converted into sessions.

Deferred: Hocking's address mismatch, St. Martin's explicitly expired 2025 recurrence, Fairborn's search-only organizer evidence, and an Arizona venue returned by search. No outreach was sent.

## October 11 game research — third pass

Six more existing listings now have organizer-published schedules: Holy Trinity Lutheran (Parma), St. Boniface (Piqua), Sylvania Bingo/Alano Step One, Belpre VFD, Greentown Athletic Club and St. Martin of Tours (Cheviot/Cincinnati). The directory now holds 60 schedule-bearing entries; 732 total records remain. Eight records were updated in this batch, with primary-source evidence in `research/bingo-session-review-2026-10-11-pass3.json`.

Added Saint Ambrose's October 24 Neon Bingo: doors 5:15 p.m., game 7:15 p.m., at Hilkert Hall. It remains a one-off dated exception. Canton St. Joan of Arc gains an organizer link and parish phone/package confirmation. Belpre's October 30 Monster Mash start is 7 p.m.; no package price is inferred from its reservation credit. Belpre's Friday schedule applies only to its VFD organizer, not every charity licensed at the address.

St. Martin's current homepage publishes Wednesday bingo, resolving the earlier deferred 2025 event page. Sylvania lists Wednesday/Thursday/Sunday, but only the Wednesday section supplies times; unknown days are labeled for a phone check. Greentown's 6 p.m. is labeled early birds. Genoa's monthly pattern remains deferred because the full newspaper PDF could not be retrieved. Search results from four other states were excluded.

## October 12 fourth research pass

Eight existing listings gained game schedules: Harrison Legion 199, Logan Elm boosters in Circleville, Hamilton Elks 93, Junior Achievement in Girard, Union County Humane Society in Marysville, Ovarian Cancer Alliance in Hilliard, Middletown Knights 1610, and Ontario boosters at Fairhaven Hall. North Lawrence VFD gained organizer package prices and attendance details. The directory now has 68 schedule-bearing entries and 732 total records. Evidence and deferred leads are recorded in `research/bingo-session-review-2026-10-12-pass4.json`.

Selected-date events expire after their last published date. Middletown's second/fourth-Wednesday description is not extrapolated beyond October 14 and 28; Fairhaven uses the four explicit November dates. Conflicting Delta recurrence and older Bellevue information remain unconfirmed. The next research checkpoint is 100 schedule-bearing listings, prioritizing underserved counties and full organizer calendars.

## October 12 fifth research pass

Three existing listings gained schedules: Lebanon Legion 186's October 18 calendar session, Ravenna VFW1055's first/third Thursday game, and Mantua St. Joseph's Council 3766 December 19 announcement (times/prices still TBD). Total: 71 schedule-bearing records, 732 venues. Three other listings gained organizer visitor/contact evidence, including Children's Toy Fund ramp and ground-level entrance descriptions. See `research/bingo-session-review-2026-10-12-pass5.json` for six updates and deferred leads.

`session_monthly` stores weekday plus ordinal weeks (1–5) separately from weekly `session_days` and explicit `session_dates`. Filters compute only matching monthly dates and honor closures and expiry; tests cover month rollover and fifth-week gaps. The badge now says published schedule rather than claiming that every announced event has a start time.

## October 14: five-listing research batch

Research batches now cover exactly five selected venues, including inconclusive results. Promotion focuses on advertised games supported by full-source review and a matched Ohio venue. Batch 1 reviewed Portsmouth’s 17th Street Bingo, Celina American Legion 210, Van Wert Council on Aging, Georgetown Legion 180 and West Alexandria Firemen. See `research/bingo-session-review-2026-10-14-batch1.json`.

Two games were added: Portsmouth’s organizer-published Wednesday/Thursday sessions at the 17th Street address, and Celina Lake Festival’s November 8 Designer Purse Bingo as reported in WCSM’s dated chamber announcement. The latter date matches the existing state authorization; its source attribution and ticket-contact scope are explicit. Only these two receive advertised game titles. Celina’s one-off date and ticket offer expire after November 8.

Van Wert and West Alexandria gained public inquiry routes. Van Wert’s 2025 public-event dates, separate senior penny/nickel activities, Georgetown’s undated directory times and West Alexandria’s old winter lead are not promoted as upcoming licensed games. No outreach or paid advertising was sent. Counts remain 732 venues and 717 Type I entries; 73 records now contain published schedules.
