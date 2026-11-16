# District of Columbia referral edition

Reviewed November 16, 2026. The District of Columbia moves from a starter edition to a full edition. The District is one county-equivalent, so the edition has one locality. It is built from one research sheet, `data/source/states/dc.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contact (`district-of-columbia-county-veterans-offices.json`)

- **Source.** The [Mayor's Office of Veterans Affairs (MOVA) page](https://communityaffairs.dc.gov/mova), read in full. The office is at One Judiciary Square, 441 4th St NW, Suite 707 North, Washington, DC 20001. It is open weekdays 9 a.m. to 5 p.m. at 202-724-5454.
- **Who helps.** District Veteran Service Officers help with federal VA claims and benefits.
- **Address used.** The page's footer also shows 1350 Pennsylvania Avenue NW, Suite 332. The card uses the address listed under "Contact Us."
- **Display.** The locality is labeled "District of Columbia." Wording swaps keep the page from saying "District of Columbia County" or "Choose a county."

## Aging and ombudsman (`dc-regional-referrals.json`)

- **Aging (`dc-dacl`).** The DC Department of Aging and Community Living (DACL), the District's aging agency and Aging and Disability Resource Center. It is at 500 K Street NE: 202-724-5626, TTY 711, weekdays 9:30 a.m. to 4:30 p.m. Source: DACL's [agency contact page](https://dacl.dc.gov/agency/department-aging-and-community-living-0) (search excerpt).
- **Ombudsman (`dc-omb`, `dc-ombudsman`).** The Office of the D.C. Long-Term Care Ombudsman at Legal Counsel for the Elderly, 202-434-2190 ([program page](https://www.aarp.org/legal-counsel-for-elderly/what-we-do/info-2017/dc-long-term-care-ombudsman.html), read in full; updated July 15, 2024). The Attorney General's 2023 elder justice brochure lists 202-434-2140. The card names both numbers and uses the program's own.
- **Abuse reporting.** Adult Protective Services, 202-541-3950, 24 hours a day (DACL and the Attorney General's brochure, search excerpts).

## Other records (`dc-programs.json`)

- **Claims help (`dc-claims`).** MOVA, above.
- **Medicare counseling (`dc-ship`).** DC SHIP at DACL, 202-727-8370 or ship.dacl@dc.gov (search excerpts of DACL's SHIP page and its 2026 fact sheet).
- **Centers for Independent Living (1, `dc-cil-dccil`).** The DC Center for Independent Living. Its main office is at 2600 12th Street NE (202-388-0033), with offices on 14th Street NW and in Anacostia.
  - Phones come from the [ILRU directory](https://ilru.org/projects/cil-net/cil-center-and-association-directory-results/DC), read in full.
  - Addresses come from ILRU's map directory (search excerpt).
  - The directory lists the District as "Washington" county.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`dc-legal-programs`).** Legal Counsel for the Elderly, 202-434-2120 (search excerpts).
- **VA health care (`dc-vahealth-systems`).** The Washington DC VA Medical Center, 202-745-8000 (search excerpt).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- DACL's ward-based Senior Service Network lead agencies. They are organized by ward, which the county model does not divide.
