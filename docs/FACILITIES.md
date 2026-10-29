# Ohio nursing homes and rehab facilities

Canonical records: `data/public/ohio-facilities.json` (924 records). Generated page: `facilities.html`, built by `scripts/facilities_edition.py` through `scripts/build_public.py`. Entry point: the "Nursing Homes & Rehab Facilities" card under "What help do you need?" in the Ohio edition. The card is hidden in other state editions (`ohio-only`).

## Source and scope

Source: Centers for Medicare & Medicaid Services, Provider Data Catalog, Nursing Home Provider Information (https://data.cms.gov/provider-data/dataset/4pq5-n9py). The file used is recorded in `data/source/ohio-facilities-source.json` with its SHA-256, retrieval date and Ohio row count. Ohio has 924 certified nursing homes in 88 counties; every county is represented.

Scope is Medicare/Medicaid-certified nursing homes only. Assisted living, residential care, memory care, adult day services and home health are not in this source and are not on the page. The state's Department of Health licenses residential care facilities; add them as a separate record type with their own source, never mixed into this count.

Only public directory fields are kept: name, address, phone, county, certified beds, ownership and chain. Star ratings, penalties, staffing and deficiency data are deliberately excluded. The page is a finder, not a rating, and says so; it points to the state's Nursing Home Quality Navigator (https://aging.ohio.gov/navigator) for quality information.

## Flags

- `vhg_visiting`: the four facilities Veteran Home Guardians serves (Bennington Glen, Centerburg Pointe, Woodside Village, Morrow Manor). Keyed by CMS number in `scripts/build_facilities_data.py`; add a facility there when a new one is served. These sort first.
- `ohio_veterans_home`: Ohio Veterans Home (Sandusky) and Ohio Veterans Home, Georgetown.

## Links to the bingo finder

Each card links to `bingo.html?zip=<facility ZIP>&radius=25&kind=bingo`, so activity staff land on games and senior centers near that facility. Activity staff are also pointed to the organizer form to report which games residents attend.

## Refresh

Download the latest Nursing Home Provider Information CSV (monthly), then:

    python3 scripts/build_facilities_data.py NH_ProviderInfo_<Mon><Year>.csv --retrieved YYYY-MM-DD
    python3 scripts/build_public.py

Review the diff for closed or renamed facilities and run `node tests/facilities.cjs`. A changed record count is expected over time; update the count in the test and the page copy follows the data.

## Not included, on purpose

No contact people or email addresses are published. Outreach contacts live outside this repository.
