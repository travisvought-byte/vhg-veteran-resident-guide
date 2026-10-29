# Ohio nursing homes, rehab and assisted living facilities

Canonical records: `data/public/ohio-facilities.json` (924 records). Generated page: `facilities.html`, built by `scripts/facilities_edition.py` through `scripts/build_public.py`. Entry point: the "Nursing Homes & Rehab Facilities" card under "What help do you need?" in the Ohio edition. The card is hidden in other state editions (`ohio-only`).

## Sources and scope

Two public sources, recorded with file name, retrieval date and SHA-256 in `data/source/ohio-facilities-source.json`:

- **Nursing homes (924):** Centers for Medicare & Medicaid Services, Provider Data Catalog, Nursing Home Provider Information (https://data.cms.gov/provider-data/dataset/4pq5-n9py). Medicare/Medicaid-certified nursing homes in all 88 counties.
- **Assisted living and residential care (817):** Ohio Department of Health, Office of Health Assurance and Licensing, Health Care Provider Report and Information Extract, Facility Listing, provider type "Residential Care or Assisted Living", status Active (https://publicapps.odh.ohio.gov/eid/reports/EID_Report_Criteria.aspx). State-licensed facilities in 82 counties. Morrow County has none.

The ODH export does not identify memory care units, and the page says so. Adult day services and home health are not included. A residential care record with the same street address and ZIP as a nursing home carries `campus_nursing_home` (186 records) and shows a "Same campus as a nursing home" badge, because the two are separately licensed levels of care on one campus. They are not merged and not counted twice.

Only public directory fields are published: name, address, phone, county, beds (certified for nursing homes, licensed for residential care), ownership and chain (nursing homes). **The ODH export includes a facility email address, fax and owner contacts. None of that is published or stored in `data/public`.** `tests/facilities.cjs` fails if any email address appears in the public data. Quality ratings, penalties and staffing are deliberately left out: the page is a finder, not a rating, and points to the state's Nursing Home Quality Navigator (https://aging.ohio.gov/navigator) for nursing home quality.

The ODH report repeats a facility once per listed owner; the builder keeps one record per license (5 repeats were dropped on October 29, 2026).

## Flags

- `vhg_visiting` (nursing homes): the four facilities Veteran Home Guardians serves (Bennington Glen, Centerburg Pointe, Woodside Village, Morrow Manor). Keyed by CMS number in `scripts/build_facilities_data.py`; add a facility there when a new one is served. These sort first.
- `ohio_veterans_home`: Ohio Veterans Home (Sandusky) and Ohio Veterans Home, Georgetown.

## Links to the bingo finder

Each card links to `bingo.html?zip=<facility ZIP>&radius=25&kind=bingo`, so activity staff land on games and senior centers near that facility. Activity staff are also pointed to the organizer form to report which games residents attend.

## Refresh

Download the latest Nursing Home Provider Information CSV from CMS (monthly). For the state list, open the ODH report page, choose FACILITY LISTING, Provider Type "Residential Care or Assisted Living", Active, all counties, run it, then use "Select Alternate File Type" to export Comma Delimited Text. The export may end with stray HTML; the builder ignores it. Then:

    python3 scripts/build_facilities_data.py --cms NH_ProviderInfo_<Mon><Year>.csv --odh FacilityListing-<date>.csv --retrieved YYYY-MM-DD
    python3 scripts/build_public.py

Review the diff for closed or renamed facilities and run `node tests/facilities.cjs`. Changed record counts are expected over time; update the counts in the test, and the page copy follows the data.

## Not included, on purpose

No contact people or email addresses are published, including the facility emails in the ODH export. Outreach contacts live outside this repository.
