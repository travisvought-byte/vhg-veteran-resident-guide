# Pennsylvania edition

Published-source review: October 8, 2026. Same repository and publisher as Ohio; no new repository or separate maintenance team. Ohio remains the default homepage. Pennsylvania uses `pa.html`, with a state selector on both editions. Each page has separate canonical data and shareable county/need parameters; state switching deliberately clears county and search parameters to prevent cross-state confusion.

## Coverage and evidence

- All 67 Pennsylvania counties have a veterans office phone from PA DMVA's September 9, 2026 directory. Source publication date, review date and PDF page are retained for every contact.
- 103 resource records: 28 curated shared federal/national records, 17 Pennsylvania-specific programs and 58 local referral contacts. Shared records retain their original source dates and evidence statuses.
- Aging referrals cover all 67 counties, with exactly one matched local contact for each county. There are 54 contact records across the 52-agency network: the Huntingdon-Bedford-Fulton agency has three county office records. Separately sourced local ombudsman routes cover Allegheny, Erie, Northampton and Venango; the remaining counties use statewide routing.
- Local grants, posts, temporary ramps and contractors are not exhaustively inventoried. TechOWL reuse is a verified program route, not a promise of ramp inventory or installation.
- County phones are published contacts, not direct agency confirmations. Lycoming and Montgomery director vacancies and Wyoming's published Friday-only schedule are called out where applicable. Confirm current intake and hours before travel.

## Canonical data and generated files

Edit `data/public/pa-programs.json` for PA programs, `data/public/pa-regional-referrals.json` for aging/ombudsman contacts and `data/public/pennsylvania-county-veterans-offices.json` for veterans office contacts. Shared resources remain in `prototype-data.json`; `data/public/federal-resource-ids.json` is an explicit whitelist. Never carry Ohio-specific program records into PA by relabeling their service area.

Run `python3 scripts/build_public.py`. It uses `scripts/pa_edition.py` to generate `pa.html`, `data/public/pennsylvania-resources.json` and `share-pa.html` from the shared interface, curated shared records and PA sources. Do not hand-edit generated files. Ohio's existing links, data and QR code remain valid.

## Priority routes and limits

PA Link provides free aging/disability information and local routing. The aging network covers 52 agencies serving 67 counties. County mappings use the Pennsylvania Association of Area Agencies on Aging’s directory, cross-checked against agency and county pages. The directory’s “Huntington” entry is normalized to the official county name “Huntingdon.” Published phone sources are retained per record; 56 of 58 local records have full official source review. Carbon’s agency brochure and Lehigh’s August 2024 county referral map remain search-excerpt-only evidence and are labeled accordingly. No telephone confirmations were performed.

OPTIONS provides assessment and support for age 60+; local supplemental modifications are not universally available. Caregiver Support has category, residency, reimbursement and CHC/LIFE exclusion rules. CHC/other HCBS programs have separate financial and functional requirements; ask the service coordinator about approval rather than assuming a Medicaid card covers a ramp.

PATF offers loans requiring repayment, with limited partial grants only in conjunction with qualifying loans. PHFA ACCESS is a deferred-payment loan tied to a qualifying PHFA home purchase, not a generic existing-homeowner grant. USDA Section 504 has rural, ownership, income and credit requirements, with age 62+ for grants. Annual maxima and financing rates are intentionally omitted; verify current terms with the program.

HISA, SAH/SHA and TRA remain distinct federal routes. HISA medical review belongs with VA Prosthetics; HISA excludes new construction and portable equipment. The PA guide does not replace HISA rules with Medicaid or state-program rules.

## Sources reviewed

County directory: https://www.pa.gov/content/dam/copapwp-pagov/en/dmva/documents/veteransaffairs/documents/ma-va%20400%20county%20directors%2009.09.2026.pdf

Current directory landing page: https://www.pa.gov/agencies/dmva/pennsylvania-veterans/county-director-of-veterans-affairs

Program source URLs are recorded on every PA program. Core sources:

- https://www.pa.gov/agencies/aging/local-resources/area-agencies-on-aging-
- https://www.pa.gov/services/aging/request-aging-and-disability-resources-through-pa-link
- https://www.pa.gov/services/aging/apply-for-options-program
- https://www.pa.gov/services/aging/apply-for-the-caregiver-support-program
- https://www.pa.gov/agencies/dhs/resources/home-community-based-services-hcbs
- https://www.pa.gov/agencies/dhs/contact/long-term-care-contacts
- https://www.pa.gov/services/aging/request-assistance-from-a-long-term-care-ombudsman
- https://www.pa.gov/agencies/aging/aging-programs-and-services/pa-medi-medicare-counseling
- https://techowlpa.org/reep/
- https://techowlpa.org/library/
- https://patf.us/what-we-do/financial-loans/
- https://www.phfa.org/programs/accesshomemod.aspx
- https://www.rd.usda.gov/programs-services/single-family-housing-programs/single-family-housing-repair-loans-grants-31
- https://www.pa.gov/services/dli/request-help-from-the-bureau-of-blindness-and-visual-services
- https://www.pa.gov/services/dli/request-help-from-the-office-for-the-deaf---hard-of-hearing--odh
- https://www.disabilityrightspa.org/get-help/

PDF tables were extracted by column so work phones were not confused with fax numbers; Beaver's first work number and Potter's extension were checked visually. No named staff or personal email addresses were added. Public source details and phone numbers are provided for referrals, not endorsements.

## Validation and next steps

`node tests/pennsylvania.cjs` runs the Ohio regression checks and PA tests: all county names, matching phone records, phone extensions, vacancies, state isolation, shared URLs, state switching, seniors scoping and accessibility branches. `python3 scripts/build_public.py --check` checks generated outputs; `python3 scripts/validate_public.py` checks both editions' local links and basic data integrity. These simulated DOM tests do not establish accessibility compliance or print pagination.

Next: strengthen the two excerpt-only aging sources, map the remaining local ombudsman contacts, verify county intake arrangements and investigate county repair/reuse resources. No PA outreach, resident data collection or claim preparation was performed. Maintenance and correction contact: travis@vethomeguard.org; backup reviewer still unassigned.

## Local contact expansion: October 8, 2026

All county selections now show local aging contacts in the handoff, seniors section and home-accessibility referral panel. Aging contacts are not presented as dedicated ombudsman numbers. Local ombudsman referrals override statewide routing only where a separate program source verifies the route. The statewide PA Link number remains available for broader disability support and people who do not fit aging-program eligibility.

The build merges canonical local records into `data/public/pennsylvania-resources.json` and embeds them in `pa.html`. Tests check every county’s handoff, seniors and accessibility rendering, cross-county isolation, phone extensions, source labels and print actions.

Local county/agency sources, dates and evidence methods appear in `data/public/pa-regional-referrals.json`. Local services, intake, costs and availability remain subject to agency confirmation. The map is referral coverage, not an exhaustive local service inventory.

County mapping reference: https://p4a.org/aaas/
