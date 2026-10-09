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
