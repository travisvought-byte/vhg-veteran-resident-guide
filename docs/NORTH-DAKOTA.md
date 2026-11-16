# North Dakota referral edition

Reviewed November 16, 2026. North Dakota moves from a starter edition to a full edition covering all 53 counties. The edition is built from one research sheet, `data/source/states/nd.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`north-dakota-county-veterans-offices.json`)

North Dakota law has each county board appoint a county veterans' service officer. The North Dakota Department of Veterans Affairs publishes a page for each county, linked from its [Veteran Service Officers page](https://www.veterans.nd.gov/about/find-a-service-officer).

- **Source.** Each county's page, read in full. Each card links to its own county page.
- **What the card shows.** The office address, phone and hours. Officers' names, emails, cell phones and home phones are left out.
- **Shared offices.**
  - The Billings, Golden Valley, Grant, Hettinger and Mercer pages send veterans to the Stark County office in Dickinson, so those five counties show it.
  - Ransom and Sargent share an officer.
  - The LaMoure and Oliver officers' work phones are the Barnes and Morton county office numbers; the cards show them as extra phones.
- **Special cases.**
  - Dickey has a second office in Oakes, shown as another office.
  - Slope's page lists no office phone, so its card shows the officer's work phone, which is also the Bowman County office number.
  - Sheridan's county page lists no office, so its card uses the department's [Sheridan office page](https://www.veterans.nd.gov/sheridan-county-veterans-service-office), read in full.
  - McLean, Pierce and Sargent phones have extensions, given in the card notes.
  - Renville's mailing address is left out because its ZIP code does not match the town.
- **Rides to VA appointments.** Where a county page says which office schedules free van rides, the card says so: Bottineau for McHenry, Pierce and Renville; McKenzie for Dunn; Sheridan for McLean and Wells.
- **Tribal veterans service officers.** The department also lists officers for Fort Berthold, Lake Traverse, Spirit Lake, Standing Rock and Turtle Mountain. Sioux County's office is in the Standing Rock tribal building in Fort Yates and shares its number.

## Aging and ombudsman (`nd-regional-referrals.json`)

- **Aging help (`nd-adrl`).** North Dakota has no Area Agencies on Aging. Health and Human Services runs one statewide line, the Aging & Disability Resource LINK, 1-855-462-5465. The source is the [Adults and Aging Services page](https://hhs.nd.gov/node/1832), read in full. Callers press 1 for the Resource LINK (2023 handout, search excerpt).
- **Ombudsman (`nd-omb-state`).** The State Long-Term Care Ombudsman in Bismarck, 701-328-4617, or 1-855-462-5465 and press 3. The source is the program's [December 2023 brochure](https://www.hhs.nd.gov/sites/www/files/documents/New%20LTCOP%20Brochure%202023%20v4%20(1).pdf), read in full. It lists no regional ombudsmen, so every county shows the state office.
- **Abuse reporting.** Vulnerable Adult Protective Services, 1-855-462-5465 and press 2, weekdays 8 a.m. to 5 p.m., or online (search excerpts of HHS pages).

## Other records (`nd-programs.json`)

- **Claims help (`nd-claims`).** County and tribal veterans service officers, the department at 701-239-7165, and the national service officers at the Fargo VA Regional Office.
- **Medicare counseling (`nd-ship`).** The Insurance Department's State Health Insurance Counseling program (SHIC), 1-888-575-6611 (CMS directory, search excerpt).
- **Centers for Independent Living (4, `nd-cil-*`).** From the [ILRU North Dakota directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/ND), read in full. Each county maps to one center:
  - Dakota Center for Independent Living: 18 western and central counties.
  - Freedom Resource Center: 10 southeastern counties.
  - Independence, Inc.: 11 northwestern counties.
  - Options Interstate Resource Center: 14 northeastern counties. ILRU lists it in its [Minnesota directory](https://www.ilru.org/cil-directory/mn), read in full, because its office is in East Grand Forks.

  The Fargo listing for Freedom mixes North Dakota and Minnesota counties; its "Grant" is Grant County, Minnesota.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`nd-legal-programs`).** Legal Services of North Dakota: 1-866-621-9886 for callers 60 and older, 1-800-634-5263 for everyone else. Dakota Plains Legal Services also serves the state. Both come from the North Dakota Courts self-help page (search excerpt).
- **VA health care (`nd-vahealth-systems`).** The Fargo VA Health Care System, 701-239-3700 or 800-410-9723, with clinics around the state (search excerpts).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Tribal veterans service officer contacts. Their pages were not read for this edition; the claims record names them and points to the department.
- Outreach days in towns other than the county seat, beyond those printed on a county page.
