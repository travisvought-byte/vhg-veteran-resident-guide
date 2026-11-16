# Oklahoma referral edition

Reviewed November 15, 2026. Oklahoma moves from a starter edition to a full edition covering all 77 counties. The edition is built from one research sheet, `data/source/states/ok.json`, by `scripts/make_county_state.py OK`; the sheet names the page behind every contact.

## Veterans contacts (`oklahoma-county-veterans-offices.json`)

Oklahoma has **no county veterans service offices**. The Oklahoma Department of Veterans Affairs (ODVA) assigns state service officers to four regional teams, and each team's county map page lists the counties it serves. Every county card therefore shows its team's central contact and is marked as a regional contact (`office_type: regional`), not a county office.

- **Source.** ODVA's service-locations [county map](https://oklahoma.gov/veterans/veterans-services/service-locations/county-map/oklahoma.html). The Northwest, Northeast, Southeast and Southwest team lists were read in full from the Oklahoma, Okfuskee, Choctaw and Kiowa county pages.
- **What is shown.** The central office, 405-523-4000 (toll-free 855-701-6382), with the central office address, 2132 NE 36th Street, Oklahoma City. For counties served by the Northeast, Southeast or Southwest teams the card's note adds the Muskogee office (P.O. Box 769, 918-781-7766) that those teams' pages list; Southwest counties add 580-354-4193, the number the Southwest team's page prints for its staff. Officers' names and direct lines were left out. No hours are printed on the pages, so none are shown.
- **Counties listed under two teams (12).** Canadian (Northwest and Southwest), Lincoln and Oklahoma (Northwest and Northeast), Carter, Garvin and McClain (Southeast and Southwest), and McIntosh, Muskogee, Okfuskee, Ottawa, Pottawatomie and Sequoyah (Northeast and Southeast). The card names both teams and tells the reader to ask which officer is assigned to them. The card's source link is the first team's page.
- **Cimarron and Texas.** The Northwest team's county list does not name them, but their own county pages show the Northwest team's officers and phones, so they are assigned to that team and the card says so. Cimarron's page was read in full; Texas's as a search excerpt.
- **Statewide line.** ODVA's central office, above.

## Aging and ombudsman (`ok-regional-referrals.json`)

- **Area Agencies on Aging (11, `ok-aaa-*`).** Areawide Aging Agency (Oklahoma City), ASCOG (Duncan), COEDD (Shawnee), EODD (Muskogee), EODD as interim administrator for the eight-county northwest area, Grand Gateway (Big Cabin), INCOG (Tulsa), KEDDO (Wilburton), the Long Term Care Authority of Enid, SODA (Durant) and SWODA (Burns Flat). Each of the 77 counties has exactly one. Names, addresses, phones and counties come from Oklahoma Human Services publication [91-27](https://oklahoma.gov/content/dam/ok/en/okdhs/documents/okdhs-publication-library/91-27.pdf), revised August 2022, read in full.
- **A caution on that list.** Oklahoma Human Services' draft FFY 2027–2030 state plan says eleven areas are now overseen by nine agencies. The publication is four years old, so the record's scope says so and points readers to the statewide line, 800-211-2116, which routes to the right agency.
- **Statewide line (`ok-adrc`, `ok-ship`).** The Aging and Disability Info-Line, 800-211-2116, and the Oklahoma Insurance Department's Medicare Assistance Program, 800-763-2828 (405-521-6628), which runs SHIP and the Senior Medicare Patrol.
- **Ombudsman (`ok-omb-state`, `ok-ombudsman`).** The state long-term care ombudsman publishes one complaint line, 800-211-2116, which routes to the area agency's ombudsman supervisor; the State Ombudsman's office is 405-521-6734. It publishes no county table, so every county shows the statewide line. The page now sits under the Attorney General's site. Search-excerpt level.
- **Abuse reporting.** The Abuse and Neglect Hotline, 800-522-3511, 24 hours a day, and OKHotline.org, from Oklahoma Human Services pages.

## Other records (`ok-programs.json`)

- **Claims help (`ok-claims`).** ODVA's service officers, above.
- **Centers for Independent Living (5, `ok-cil-*`).** Ability Resources (Tulsa), Dynamic Independence (Bartlesville), Oklahomans for Independent Living (McAlester), Progressive Independence (Norman) and the Sandra Beasley Independent Living Center (Enid). Addresses, phones and counties come from the ILRU Oklahoma [directory](https://www.ilru.org/cil-directory/ok), read in full. Together they name 18 counties; **59 counties are not named by any center** and show no center. Dynamic Independence and the Sandra Beasley center have no website in the directory, and the directory prints only insecure (http) addresses for Oklahomans for Independent Living and Progressive Independence, so those four cards link to the Oklahoma Department of Rehabilitation Services resource guide instead (the center's own entry, or its list of independent living centers for Progressive Independence); that directory prints 580-237-8561 for the Sandra Beasley center where ILRU prints 580-237-8508, and the card's note says so.
- **Housing help (SSVF, 2).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ok-legal-programs`).** Legal Aid Services of Oklahoma (888-534-5243, Monday–Thursday), OK-SPLASH for people 60 and older (855-488-6814) and the Oklahoma Bar Association's Lawyers for America's Heroes program. Search-excerpt level.
- **VA health care (`ok-vahealth-systems`).** Oklahoma City VA Health Care System (405-456-1000, toll-free 866-835-5273) and the Eastern Oklahoma VA Health Care System in Muskogee (888-397-8387). No counties are assigned. Search-excerpt level.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- County-level phones for the ombudsman or adult protection.
- The service officers' outreach schedules (days and places where officers meet veterans); the current county pages print none, so the cards tell readers to ask.
- Independent living centers for 59 counties (above).
- A date for the independent living directory, which prints none.
- Generic guidance shared by every edition still says "county veterans office" in a few places (for example the burial and records tips); in Oklahoma read that as the state service-officer team.
