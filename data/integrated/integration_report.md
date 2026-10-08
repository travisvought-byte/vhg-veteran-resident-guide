# Integration report — dataset v0.3.1 candidate

Prepared 2026-10-06 by scripts/integrate_v03.py. Internal working file; not accepted data and not for publication.

## Inputs (unchanged; hashes recorded)

- `data/seed/Ohio_Senior_Disability_Directory_Starter.json` (seed) sha256 `2f48972e853ed97cb0ee120339a3b685bb576d5a9c68c6ebcd564f144c2253f5`
- `data/batches/B01/b01_resources.json` (B01) sha256 `e9dbca19d24d4dc1a3249098545738721da5aaeb1031ba3dd14d025c944602e9`
- `research/returns/R-01/records.json` (R-01) sha256 `86252d7d6a6b03b926b75a357b0a1c281dbb0d205a1f45a70faf82cd0f541eb5`
- `research/returns/R-02/records.json` (R-02) sha256 `30becc02a908cbc5eface0faea7874aff65a76d6d21ba72b0f0772d188ff7318`
- `research/returns/R-05/records.json` (R-05) sha256 `6151502e7e16ae7535f0393029bdb7378d09785e2358b8acd83c0feea9ecf3a6`

## Result

- Organizations: 28
- Programs: 66
- Sources: 119
- Relationships: 57
- Programs with mobility tags: 10

## Record map

| ID | What happened |
|---|---|
| `morrow-dd-intake` | B01 addition |
| `delaware-dd-intake` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `knox-dd-intake` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `marion-dd-intake` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `district5-adrn` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `coaaa-navigation` | B01 addition |
| `morrow-vso` | B01 addition |
| `knox-vso` | B01 addition |
| `marion-vso` | B01 addition |
| `delaware-vso` | B01 addition |
| `va-hisa` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `va-adapted-housing` | B01 addition |
| `help-me-grow` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `special-education` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `ohio-ltss` | seed -> B01 update (seed fields kept in provenance.historical_fields) |
| `va-sah` | split from va-adapted-housing bundle |
| `va-sha` | split from va-adapted-housing bundle |
| `morrow-vso` | updated by R-01 |
| `knox-vso` | updated by R-01 |
| `marion-vso` | updated by R-01 |
| `delaware-vso` | updated by R-01 |
| `ohio-dvs-fallback` | R-01 addition |
| `org-us-va` | organization ID r02-va (R-02) mapped to canonical ID |
| `org-ohio-dvs` | organization ID r02-ohio-dvs (R-02) mapped to canonical ID |
| `org-ohio-county-vscs` | organization ID r02-county-vsc (R-02) mapped to canonical ID |
| `org-national-alliance-care-at-home` | organization ID r02-alliance (R-02) mapped to canonical ID |
| `r02-va-health-enrollment` | R-02 addition |
| `r02-va-pension` | R-02 addition |
| `r02-aid-attendance-housebound` | R-02 addition |
| `r02-survivors-pension` | R-02 addition |
| `r02-dic` | R-02 addition |
| `r02-disability-increase` | R-02 addition |
| `r02-va-clc` | R-02 addition |
| `r02-va-cnh` | R-02 addition |
| `r02-ohio-veterans-homes` | R-02 addition |
| `r02-pension-medicaid-rule` | R-02 addition |
| `r02-va-burial` | R-02 addition |
| `r02-ohio-county-burial` | R-02 addition |
| `r02-general-caregiver` | R-02 addition |
| `r02-family-caregiver` | R-02 addition |
| `r02-hospice` | R-02 addition |
| `r02-palliative` | R-02 addition |
| `r02-whv` | R-02 addition |
| `org-aaa5` | organization ID r05-district5 (R-05) mapped to canonical ID |
| `org-coaaa` | organization ID r05-coaaa (R-05) mapped to canonical ID |
| `org-helpline-delmor` | organization ID r05-helpline (R-05) mapped to canonical ID |
| `org-pathways-central-ohio` | organization ID r05-pathways (R-05) mapped to canonical ID |
| `org-morrow-dd` | organization ID r05-morrow-dd (R-05) mapped to canonical ID |
| `org-knox-dd` | organization ID r05-knox-dd (R-05) mapped to canonical ID |
| `org-marion-dd` | organization ID r05-marion-dd (R-05) mapped to canonical ID |
| `org-delaware-dd` | organization ID r05-delaware-dd (R-05) mapped to canonical ID |
| `org-morrow-jfs` | organization ID r05-morrow-jfs (R-05) mapped to canonical ID |
| `org-knox-jfs` | organization ID r05-knox-jfs (R-05) mapped to canonical ID |
| `org-marion-jfs` | organization ID r05-marion-jfs (R-05) mapped to canonical ID |
| `org-delaware-jfs` | organization ID r05-delaware-jfs (R-05) mapped to canonical ID |
| `org-easterseals-cseo` | organization ID r05-easterseals (R-05) mapped to canonical ID |
| `org-ohio-aging` | organization ID r05-aging (R-05) mapped to canonical ID |
| `org-us-cms` | organization ID r05-cms (R-05) mapped to canonical ID |
| `org-ohio-ood` | organization ID r05-ood (R-05) mapped to canonical ID |
| `org-disability-rights-ohio` | organization ID r05-dro (R-05) mapped to canonical ID |
| `district5-adrn` | updated by R-05 |
| `coaaa-navigation` | updated by R-05 |
| `helpline-211` | R-05 addition |
| `pathways-211` | R-05 addition |
| `morrow-dd-intake` | updated by R-05 |
| `knox-dd-intake` | updated by R-05 |
| `marion-dd-intake` | updated by R-05 |
| `delaware-dd-intake` | updated by R-05 |
| `morrow-jfs-medicaid` | R-05 addition |
| `morrow-aps` | R-05 addition |
| `knox-jfs-medicaid` | R-05 addition |
| `knox-aps` | R-05 addition |
| `marion-jfs-medicaid` | R-05 addition |
| `marion-aps` | R-05 addition |
| `delaware-jfs-medicaid` | R-05 addition |
| `delaware-aps` | R-05 addition |
| `district5-ombudsman` | R-05 addition |
| `delaware-regional-ombudsman` | R-05 addition |
| `ohio-state-ombudsman` | R-05 addition |
| `ohio-quality-navigator` | R-05 addition |
| `cms-care-compare` | R-05 addition |
| `ood-vocational-rehabilitation` | R-05 addition |
| `disability-rights-ohio` | R-05 addition |

## Conflicts (later value kept; earlier value shown for review)

| Entity | Field | Kept | Replaced | From |
|---|---|---|---|---|
| `morrow-vso` | public_contact.email | null | "vets@morrowcountyohio.gov" | R-01 |
| `knox-vso` | official_url | "https://kcvso.com/" | "https://kcvso.com/contact-us/" | R-01 |
| `marion-vso` | official_url | "https://www.marionveteranservice.com/" | "http://www.marionveteranservice.com/" | R-01 |
| `delaware-vso` | official_url | "https://veteransservice.co.delaware.oh.us/" | "https://veteransservice.co.delaware.oh.us/contact-us/" | R-01 |
| `org-ohio-dvs` | name | "Ohio Department of Veterans Services" | "Ohio Department of Veterans Services \u2014 statewide fallback" | R-02 |
| `org-aaa5` | name | "Ohio District 5 Area Agency on Aging" | "Area Agency on Aging District 5" | R-05 |
| `district5-adrn` | name | "District 5 Aging and Disability Resource Network" | "District 5 Aging & Disability Resource Network" | R-05 |
| `district5-adrn` | eligibility_summary | "Navigation for older adults, adults with disabilities and caregivers; individual services have separate rules." | "Navigation covers older or disabled adults and caregivers; individual programs have separate criteria." | R-05 |
| `district5-adrn` | eligibility_decision_owner | "Receiving program determines service eligibility." | "Relevant program assessor; Medicaid financial eligibility through designated eligibility agency; clinical/waiver decisi | R-05 |
| `district5-adrn` | application_or_referral_route | "Call ADRN; describe county, age and support need." | "Call the agency or use its published ADRN referral form." | R-05 |
| `district5-adrn` | next_step | "Call for help finding long-term services and supports." | "Describe daily support needs and ask for the appropriate assessment and payment route." | R-05 |
| `district5-adrn` | public_contact.phone_label | "ADRN / main office" | "main office" | R-05 |
| `coaaa-navigation` | name | "COAAA information and assistance" | "Central Ohio Area Agency on Aging navigation" | R-05 |
| `coaaa-navigation` | eligibility_summary | "General navigation; program-specific assessment is separate." | "Consultation has no age/income requirement; funded programs apply their own criteria." | R-05 |
| `coaaa-navigation` | eligibility_decision_owner | "Receiving program determines service eligibility." | "Program assessor; Medicaid eligibility agency and waiver/plan administrator where applicable." | R-05 |
| `coaaa-navigation` | application_or_referral_route | "Call COAAA or use its official request-help page." | "Call or complete the Request Help form." | R-05 |
| `coaaa-navigation` | next_step | "Ask for aging or disability support options in Delaware County." | "Ask for a consultation or assessment and a program matched to age, daily needs and coverage." | R-05 |
| `morrow-dd-intake` | name | "Morrow DD intake and service coordination" | "Morrow DD eligibility and service coordination" | R-05 |
| `morrow-dd-intake` | program_type | "eligibility_intake" | "navigation_service" | R-05 |
| `morrow-dd-intake` | official_url | "https://www.morrowdd.com/service-and-support-administration/" | "https://www.morrowdd.com/" | R-05 |
| `morrow-dd-intake` | eligibility_summary | "County residency and age/developmental-disability requirements are reviewed by the appropriate board or early-intervent | "County residency and Board eligibility; SSA requests begin at age 3." | R-05 |
| `morrow-dd-intake` | eligibility_decision_owner | "Morrow county board for board services; early-intervention team for under-3 services." | "Morrow County Board of Developmental Disabilities" | R-05 |
| `morrow-dd-intake` | application_or_referral_route | "Ask for an SSA eligibility request for age 3 or older; ask about the separate early-intervention route for a younger ch | "Call the main office and request eligibility intake; use Help Me Grow for under-3 early intervention." | R-05 |
| `morrow-dd-intake` | next_step | "Ask how to start an age-appropriate developmental-disability eligibility review." | "Ask what eligibility records are needed and how to request an SSA." | R-05 |
| `morrow-dd-intake` | public_contact.phone_label | "main office; ask for SSA / eligibility" | "main office" | R-05 |
| `knox-dd-intake` | program_type | "eligibility_intake" | "navigation_service" | R-05 |
| `knox-dd-intake` | eligibility_summary | "County residency and age/developmental-disability requirements are reviewed by the appropriate board or early-intervent | "Age 3+ application requires qualifying intellectual/developmental diagnosis documentation; Board decides eligibility." | R-05 |
| `knox-dd-intake` | eligibility_decision_owner | "Knox county board for board services; early-intervention team for under-3 services." | "Knox County Board of Developmental Disabilities" | R-05 |
| `knox-dd-intake` | application_or_referral_route | "Age 3+: use the board eligibility page/referral form. Under 3: eligibility page names 614-656-3322 or state referral; E | "Use secure request form or intake email for age 3+; under 3 uses early-intervention referral." | R-05 |
| `knox-dd-intake` | next_step | "Ask how to start an age-appropriate developmental-disability eligibility review." | "Return the application packet and diagnosis records; ask how SSA planning begins." | R-05 |
| `knox-dd-intake` | public_contact.phone_label | "main office; ask for eligibility" | "main office" | R-05 |
| `marion-dd-intake` | name | "Marion DD intake and service coordination" | "Marion DD enrollment and service coordination" | R-05 |
| `marion-dd-intake` | program_type | "eligibility_intake" | "navigation_service" | R-05 |
| `marion-dd-intake` | eligibility_summary | "County residency and age/developmental-disability requirements are reviewed by the appropriate board or early-intervent | "Intake reviews written information and an interview." | R-05 |
| `marion-dd-intake` | eligibility_decision_owner | "Marion county board for board services; early-intervention team for under-3 services." | "Marion County Board of Developmental Disabilities intake coordinator" | R-05 |
| `marion-dd-intake` | application_or_referral_route | "Call for intake and an eligibility interview; service coordination follows board determination." | "Call or email enrollment contact." | R-05 |
| `marion-dd-intake` | next_step | "Ask how to start an age-appropriate developmental-disability eligibility review." | "Prepare formal diagnosis, birth certificate, Social Security card and Medicaid card if applicable; intake determines el | R-05 |
| `marion-dd-intake` | public_contact.phone | "740-387-1035" | "740-375-6185" | R-05 |
| `marion-dd-intake` | public_contact.phone_label | "main office; ask for intake coordinator" | "main office" | R-05 |
| `delaware-dd-intake` | program_type | "eligibility_intake" | "navigation_service" | R-05 |
| `delaware-dd-intake` | eligibility_summary | "County residency and age/developmental-disability requirements are reviewed by the appropriate board or early-intervent | "County residency and age-specific DD eligibility assessment." | R-05 |
| `delaware-dd-intake` | eligibility_decision_owner | "Delaware county board for board services; early-intervention team for under-3 services." | "Delaware County Board of Developmental Disabilities" | R-05 |
| `delaware-dd-intake` | application_or_referral_route | "Age 3+: call intake. Under 3: page names Help Me Grow at 800-755-4769 or the state referral form." | "Age 3+: use Apply for Services on the eligibility page; under 3: Help Me Grow." | R-05 |
| `delaware-dd-intake` | next_step | "Ask how to start an age-appropriate developmental-disability eligibility review." | "Submit intake request. Ask about diagnosis/functional assessment and support coordination." | R-05 |
| `delaware-dd-intake` | public_contact.phone | "740-201-3601" | "740-201-3600" | R-05 |
| `delaware-dd-intake` | public_contact.phone_label | "Intake and Eligibility Department" | "main office" | R-05 |

## Review flags (human decision needed)

- `ohio-aging-compass`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `ocali-family`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `ocali-gallery`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `milestones-lifeworks`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `county-dd`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `cvso-map`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `findhelp`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `morrow-dd-fdr`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `delaware-dd-fss`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `sourcepoint-home-care`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `district5-vdc`: seed service_area kept verbatim ('District 5; confirm VA service area'); not normalized
- `district5-vdc`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `ohio-p2p`: seed service_area kept verbatim ('Statewide'); not normalized
- `ohio-p2p`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `at-ohio-library`: seed service_area kept verbatim ('Statewide'); not normalized
- `at-ohio-library`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `marion-jfs-guide`: seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review
- `knox-dd-intake`: email 'cpayne@knoxdd.com' looks like a named individual (D-006): moved to internal_contact
- `marion-dd-intake`: email 'tbutcher@marioncountydd.org' looks like a named individual (D-006): moved to internal_contact
- `marion-dd-intake`: B01 'children' has no exact enum; left out of age_life_stage pending review
- `va-hisa`: mapped to 'veteran'; schema has no active-duty value
- `va-adapted-housing`: mapped to 'veteran'; schema has no active-duty value
- `help-me-grow`: operator organization not assigned (no single operator confirmed); needs review
- `special-education`: operator organization not assigned (no single operator confirmed); needs review
- `ohio-ltss`: operator organization not assigned (no single operator confirmed); needs review

## Check results

All structural and reference checks passed.

## Seed-only records awaiting review (expected; not errors)

These came from the v0.2 seed and no research packet has re-reviewed them yet. They need an operator, type, needs and ages before acceptance.

- at-ohio-library: no operator organization (allowed only for existing_directory / lookup_instruction)
- county-dd: no operator organization (allowed only for existing_directory / lookup_instruction)
- cvso-map: no operator organization (allowed only for existing_directory / lookup_instruction)
- delaware-dd-fss: no operator organization (allowed only for existing_directory / lookup_instruction)
- district5-vdc: no operator organization (allowed only for existing_directory / lookup_instruction)
- findhelp: no operator organization (allowed only for existing_directory / lookup_instruction)
- marion-jfs-guide: no operator organization (allowed only for existing_directory / lookup_instruction)
- milestones-lifeworks: no operator organization (allowed only for existing_directory / lookup_instruction)
- morrow-dd-fdr: no operator organization (allowed only for existing_directory / lookup_instruction)
- ocali-family: no operator organization (allowed only for existing_directory / lookup_instruction)
- ocali-gallery: no operator organization (allowed only for existing_directory / lookup_instruction)
- ohio-aging-compass: no operator organization (allowed only for existing_directory / lookup_instruction)
- ohio-p2p: no operator organization (allowed only for existing_directory / lookup_instruction)
- sourcepoint-home-care: no operator organization (allowed only for existing_directory / lookup_instruction)

## Notes

- morrow-dd-intake.public_contact.email: ordinary unknown null in R-05 retained earlier sourced value; no new review date implied.
- Facilities held: 25 seed facilities remain in the seed file only (excluded from guide scope under D-017; available for separate outreach). Pathways from B01 not yet converted.
- Seed funding leads and scenarios not carried into this candidate; they remain in the seed file.

## Not done in this pass

- No phone confirmations; no record is `agency_confirmed`.
- Facilities, pathways, funding leads and scenarios not converted (see Notes).
- Mobility tags are derived proposals (rules M-3a–d); each carries `derived_by` and its source IDs.
