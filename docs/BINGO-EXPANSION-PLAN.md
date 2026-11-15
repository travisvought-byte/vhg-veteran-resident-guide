# Bingo expansion: build and launch plan

Owner: Travis Jon Vought. Started November 15, 2026.

## Goal and scope

Extend the Ohio Bingo model into Pennsylvania, New York, Washington and Utah where Travis reports existing operations. Build all editions now; prioritize Ohio and Pennsylvania partnership research, then New York and Washington. Utah covers free recreation and community sponsorships. Revenue assumptions are not a condition of building the directories.

## Architecture and current implementation

The source repository is `travisvought-byte/vhg-veteran-resident-guide`. `Ohio-Bingo` is a generated mirror, not the place to edit code. Existing GitHub Actions mirrors `bingo-site/` every three hours. Preserve the Ohio root and domain; the shared state selector is `/states/` and new editions are `/states/pennsylvania.html`, `/states/new-york.html`, `/states/washington.html`, `/states/utah.html`. A future national domain can serve the same generated package after canonical configuration is generalized.

- `data/bingo/states.json`: state configuration, time zones and research routes.
- `data/bingo/venues.json`: source-linked records for new states. Ohio remains in its current canonical data.
- `scripts/bingo_network.py`: validation and state page generation, called by the existing bingo generator.
- `templates/bingo/`: shared accessible HTML, CSS and JavaScript.
- `scripts/import_bingo_network.py`: preview/import researched batches with conflict detection.
- `tests/bingo-network.cjs`: schedule, holiday, freshness, filter, URL and generated-page checks.

First batch: 13 source-linked venues (PA 5, NY 3, WA 2, UT 3). These are starter lists, not statewide license inventories. Source review is explicitly distinguished from organizer confirmation, licensing and accessibility verification. All listings remain free. No partners, revenue or beneficiary eligibility is asserted.

## Tonight's execution sequence

1. Shared engine and starter editions: implemented in this branch. Verify and merge through the source repository, then let the existing mirror publish.
2. Expand independent state batches using the contract below. Start with county/municipal license inventories and organizer websites. Use third-party directories as discovery leads; record facts from original sources.
3. Add pull-tab / bell-jar inventories separately from scheduled bingo. License-authorized days are not advertised game sessions. Maintain state, operator type, license ID, report date and source.
4. Import operator financial records into a separate prospect dataset. Preserve reporting year, gross receipts, prizes, operating expenses, net income, and actual external distributions as distinct fields. Do not infer one from another.
5. Rank prospects by documented giving, mission fit, proximity to operations, public contact route and evidence quality. Prepare outreach drafts; sending is a separate action.
6. Add nationwide ZIP centroid data with a documented reuse license; then bring the existing distance and print-flyer behavior to state editions. Current new-state search matches city, venue and ZIP text, not radius.
7. Add organizer confirmations, cancellations, accessibility details and date-specific exceptions. Add state-specific advertising and partnership templates only once supported by the applicable rules.

## Research sources and reuse

| State | Starting sources | Next import work |
|---|---|---|
| OH | https://charitable.ohioago.gov/Charitable-Bingo/Bingo-Financials | Match existing organizations to reported distributions; retain the established finder |
| PA | https://www.eservices.revenue.pa.gov/SGOC and county treasurer license lists | Collect club reports and county bingo/SGOC rosters separately; prioritize veterans/fraternal clubs |
| NY | https://gaming.ny.gov/2024-annual-report and municipal clerks | Bingo and bell-jar organizations, county financial targeting, original organizer schedules |
| WA | https://wsgc.wa.gov/about-us/financial-reports | Current license search plus operator quarterly receipts; distinguish commercial/nonprofit/tribal |
| UT | https://coa.washco.utah.gov/ | Free senior/community games, participation requirements, sponsorship contacts |

Existing public directories can accelerate discovery but are not necessarily open-licensed. Reuse code only with its actual license; retain notices. Link to source sites and paraphrase factual event details; do not copy their directory databases or editorial content wholesale without permission/license. No external code dependency is necessary for the first implementation.

## Batch contract for Claude or another contributor

Work from current source repository main plus this branch/PR, or branch from the merged result. Do not edit `Ohio-Bingo` or generated `bingo-site` files directly. Do not overwrite concurrent edits.

Use one JSON array per researched batch. Follow existing `data/bingo/venues.json` records. Stable IDs begin with the state abbreviation. Required fields include state, name, city, address (city-only is allowed if clearly disclosed), official URL, admission details, reviewed date, review due date, sources, verification and license status. Unknown facts stay unknown. Days use Sunday=0; monthly rules specify weekday and week-of-month. One-time events use ISO `session_dates`; closures use `excluded_dates`. Keep seasonal limits and holiday changes explicit. If season boundaries are unconfirmed, tell visitors to confirm; do not claim today's game is guaranteed.

Use `published_source` for website-reviewed facts. `organizer_confirmed` requires actual dated organizer confirmation; a regulator listing is `license_only` and does not establish session times. Records should not be treated as current after `review_due`.

Commands:

```sh
python3 scripts/import_bingo_network.py /path/to/researched-batch.json
python3 scripts/import_bingo_network.py /path/to/researched-batch.json --write
python3 scripts/build_public.py
python3 scripts/build_public.py --check
node tests/bingo-network.cjs
node tests/bingo-site.cjs
```

Use `--replace` only after checking a conflicting ID. Keep researched batch work in separate files/branches until ready to import. Validate source dates, not search-engine crawl labels. Do not invent donation commitments or treat all net proceeds as money available to VHG.

## Remaining acceptance checks

- Desktop browser navigation and search reviewed successfully; mobile visual and print layout review remain.
- Comprehensive statewide roster coverage and reconciliation, not just first venues.
- Freshness automation for new data (runtime suppresses stale day matches already).
- Radius search and nearby-state results.
- Enriched license IDs, operator classifications, actual distributions and contact data.
- Submission storage beyond the current email workflow if volume requires it.
- State-specific agreement/advertising review before offering revenue-sharing terms.

The first release is a functioning expansion foundation. It is not a completed national census or a revenue forecast.
