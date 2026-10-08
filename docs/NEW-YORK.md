# New York edition: coverage and sources

Published-source review: October 8, 2026. This is a referral guide from Veteran Home Guardians, not a claim that VHG operates visitation services throughout New York.

## Initial coverage

- 62 county selections with veterans referral contacts. County offices serve most selections. NYC uses citywide Department of Veterans' Services intake for Bronx, Kings/Brooklyn, New York/Manhattan, Queens and Richmond/Staten Island. Essex uses the NYS DVS Elizabethtown benefits office. Clinton uses the county veterans agency.
- 57 local aging office records, with exactly one geographic referral for each county. NYC has one aging office for all five boroughs. Warren and Hamilton share one office. The official directory also includes tribal aging programs; these remain accessible through the directory rather than being presented as the general county contact.
- 102 resources: 28 shared federal/national records, 17 New York programs and 57 aging offices. Source statuses and review dates remain visible. Shared records retain their previous evidence rather than receiving a new verification date.
- Senior support, disability needs, caregiver referrals, Medicare counseling, resident rights, home accessibility and transition screening.
- Statewide ombudsman routing. Dedicated local ombudsman contacts, local post contacts and contractors are not yet mapped.
- Printable county handoffs, accessibility planning tools, a state-specific sharing kit and QR code.

## Contact evidence and conflicts

Veterans directory: https://veterans.ny.gov/office-locations

Aging directory: https://aging.ny.gov/local-offices

The full paginated directories and individual office pages were retrieved. Selected state-directory source HTML hashes are retained for the published veterans contacts and all 57 aging contacts. Each contact includes its source and review date. A source review is not a phone call or confirmation of current intake, hours or availability.

Two state-directory veterans phone conflicts were resolved using county-owned sources:

| County | State directory phone not used | Published phone | Controlling contact source |
|---|---|---|---|
| Chemung | 845-486-2067 | 607-737-5445 | https://www.chemungcountyny.gov/187/Veterans-Affairs |
| Chenango | 845-486-2066 | 607-337-1775 | https://www.chenangocountyny.gov/m/directory/department?did=36 |

Conflict evidence remains in the canonical records. Chenango and Clinton advise appointments for service-officer meetings. No named staff or personal contact details are needed for these referrals.

NYC veterans intake is sourced from https://www.nyc.gov/site/veterans/contact/contact.page. The aging state-directory page lists 311 within NYC and 212-244-6469 outside the five boroughs. The full number supports families and care teams calling from elsewhere; the county handoff and senior guide also explain the local 311 option.

## Program boundaries

NY Connects routes people of all ages and disabilities. Many aging services focus on age 60+. EISEP has assessed home-support needs and restrictions on duplicating Medicaid services; costs and local availability require screening. HIICAP is Medicare counseling, not an insurance plan or approval for care.

Access to Home, Access to Home for Heroes and RESTORE use funded local administrators. Residents cannot apply directly to HCR. Disability, income, primary-residence and owner requirements vary. The guide does not promise current grants, project approval, ramp stock, construction completion or installation. TRAID offers device loans and demonstrations; confirm equipment and terms with the regional center.

NHTD screening starts with the Regional Resource Development Center for the intended community county. Medicaid eligibility, care needs, age/disability criteria and approval apply. The NHTD record and Independent Living Center directory retain search-excerpt-only labels because full source retrieval was unavailable. Other 15 New York program records received full primary-source review, including the official ombudsman brochure and provider contact pages. The brochure's older publication label remains recorded, with the state Department of Health directory as additional indexed corroboration.

The Commission for the Blind referral uses an official NYC311 page publishing the statewide service number. The guide asks for the appropriate district office and eligibility assessment; it does not assume every vision impairment qualifies.

## Canonical records and build

Edit these source files, then run `python3 scripts/build_public.py`:

- `data/public/new-york-county-veterans-offices.json`
- `data/public/ny-programs.json`
- `data/public/ny-regional-referrals.json`

`scripts/ny_edition.py` generates the New York edition from the shared interface and a curated federal whitelist. It overrides state routes and referral guidance instead of relabeling Ohio or Pennsylvania programs. New York programs use an explicit `statewide` service area: the county named New York must refer only to Manhattan, never the whole state.

Generated outputs are `ny.html`, `data/public/new-york-resources.json` and `share-ny.html`. The state selector and sharing-kit navigation connect all three editions. State switching preserves the selected view and clears county filters. Borough alias links normalize to canonical county names. Private accessibility choices are not included in shared URLs.

## Validation and next work

Run `python3 scripts/build_public.py --check`, `node tests/new-york.cjs` and `python3 scripts/validate_public.py`. Checks cover all 217 county selections across the three editions, New York county isolation, corrected phones, extensions, borough aliases, non-veteran senior routing, accessibility branches, print actions and local sharing assets.

The simulated DOM checks do not establish WCAG compliance or visual print pagination. Browser and print review remain pending. Next research: stronger evidence for the two excerpt-only state routes, dedicated local ombudsman contacts, local HCR administrators and device reuse contacts. No agency outreach or resident information collection was performed. Corrections and maintenance: travis@vethomeguard.org.
