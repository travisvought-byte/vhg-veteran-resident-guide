# Connecticut referral edition

Reviewed November 16, 2026. Connecticut moves from a starter edition to a full edition covering its eight counties. The edition is built from one research sheet, `data/source/states/ct.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Why counties

Connecticut has no county government, and the Census Bureau now uses nine planning regions as county equivalents. The edition still uses the eight historical counties for two reasons: residents know them, and VA's SSVF list uses them. Services in Connecticut are organized by town, so each county card shows the office that serves most of its towns and names the towns served by another office.

## Veterans contacts (`connecticut-county-veterans-offices.json`)

The Department of Veterans Affairs' Office of Advocacy and Assistance has five district offices, one per congressional district. Phones and addresses come from its [district offices page](https://portal.ct.gov/DVA/advocacy-and-assistance), read in full. Its main line is 860-616-3685.

- **Town to district.** From the department's [Where to Get Help page](https://portal.ct.gov/dva/pages/where-to-get-help), read in full.
- **Town to county.** From the [State Library's town list](https://portal.ct.gov/csl/research/ct-towns-counties), read in full.
- **How counties map.**
  - New London, Tolland and Windham towns all use District 2 (Norwich).
  - Fairfield, Hartford, Litchfield, Middlesex and New Haven are split between districts. Each card shows the main district. The other districts appear as other offices, with their towns named.
- **Gaps and conflicts.**
  - The town list does not show Greenwich, Shelton or Windsor; those county cards say to call the main line.
  - Goshen appears twice, under Districts 4 and 5; it is shown with District 5, like its neighbors.

## Aging and ombudsman (`ct-regional-referrals.json`)

- **Area Agencies on Aging (5, `ct-aaa-*`).** Town lists come from the Department of Aging and Disability Services' [2024 CHOICES training flyer](https://portal.ct.gov/-/media/aginganddisability/agingservices/choices/2024-choices-training-flyer.pdf?rev=aad5e43b928140189ce0785d77811736&hash=7255911F1BC3A8345F7A8FBC008578DA), read in full. Addresses and phones come from its [Additional Resources page](https://portal.ct.gov/ads/additional-resources), read in full.
  - The flyer omits Meriden. The 2022 CHOICES brochure lists Meriden with South Central (search excerpt).
  - Each county shows the agency serving most of its towns:
    - Senior Resources: Middlesex, New London and Windham.
    - North Central: Hartford and Tolland.
    - South Central: New Haven.
    - Southwestern: Fairfield.
    - Western: Litchfield.
  - Town exceptions are listed on each card, such as Tolland County towns served by Senior Resources, Danbury-area towns served by Western, and Plymouth served by North Central.
- **Ombudsman (`ct-omb-state`).** The Long Term Care Ombudsman Program, 1-866-388-1888, from the [program page](https://portal.ct.gov/ltcop/ombudsman), read in full. Regional ombudsmen are assigned by town and share the program number 860-424-5200.
- **Abuse reporting.** Protective Services for the Elderly, 1-888-385-4225, weekdays; after hours, 2-1-1 (DSS page, search excerpt).

## Other records (`ct-programs.json`)

- **Claims help (`ct-claims`).** The Office of Advocacy and Assistance, above.
- **Aging line and Medicare counseling (`ct-adrc`, `ct-ship`).** CHOICES, 1-800-994-9422 (2022 brochure, search excerpt).
- **Centers for Independent Living (5, `ct-cil-*`).** From the [ILRU Connecticut directory](https://www.ilru.org/cil-directory/ct), read in full. Every county is covered by at least one center.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ct-legal-programs`).** Statewide Legal Services, 1-800-453-3320 (search excerpts).
- **VA health care (`ct-vahealth-systems`).** VA Connecticut Healthcare System: West Haven 203-932-5711, Newington 860-666-6951, appointments 866-808-7921 (search excerpts).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Municipal Veterans Representatives by town. The department's page lists them; the claims record points to them.
- Office hours for the district offices. The department's page lists none.
