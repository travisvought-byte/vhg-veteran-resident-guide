# South Carolina referral edition

Reviewed November 4, 2026. South Carolina moves from a starter edition to a full 46-county edition.

## Veterans contacts (`south-carolina-county-veterans-offices.json`)

Each county uses its County Veterans Affairs Office phone from the SCDVA [county offices page](https://scdva.sc.gov/county-veterans-affairs-offices), read in full.

- **Phones only.** The page lists one phone per county and no addresses or hours, so cards show the phone only.
- **More than one number.** Two counties list a second line ("803.436.2302/2303" for Sumter, "803.914.2085/2087" for Hampton), and Kershaw lists an "or" number. The first number is the main phone; the others are shown as "Also."
- **Extensions.** Saluda (ext. 2268), Williamsburg (ext. 6301) and Kershaw's second number keep their extensions.
- **Left out.** Staff names and emails.
- **Fallback.** No county needs the statewide line. The SCDVA line, 803-734-0200, is named in every card note.

## Aging (`sc-regional-referrals.json`)

The ten Area Agency on Aging / ADRC regions, their phones, toll-free numbers and counties come from the SC Department on Aging's [2025 Senior P.R.E.P. brochure](https://aging.sc.gov/sites/default/files/2025-05/2025%20Senior%20P.R.E.P%20Brochure.pdf), read in full. Each county is in exactly one region.

- **Records.** `sc-aging-r1` to `sc-aging-r10`. The toll-free number and the county it does not work from (for example "outside Greenville County") are shown as a note. Santee-Lynches lists no toll-free number.
- **Upper Savannah.** The brochure lists 864-941-8050. Some non-official directories list only the toll-free 800-922-7729. The card follows the brochure.

## Statewide records (`sc-programs.json`)

- **Ombudsman.** `sc-ombudsman` uses the Department on Aging's Long Term Care Ombudsman line, 800-868-9095.
  - Regional ombudsmen work out of the Area Agencies on Aging. No official list of their direct phones was found, so no regional ombudsman records were made.
  - Abuse of adults living in the community: SCDSS Adult Protective Services, 888-227-3487 (dss.sc.gov).
- **Department on Aging.** `sc-doa` (800-868-9095) routes callers to their regional agency.
- **Housing help (SSVF).** The 3 programs now use county lists from VA's FY26 intake workbook.
- **Centers for Independent Living (4 records).** Taken from the ILRU national directory, with full page text reviewed.
  - The directory lists Calhoun twice for Able SC Columbia; the card lists it once.
  - The Able SC Greenville listing omits Greenville County. The card includes it because the office is in Greenville, and the note says so.
  - Orangeburg is listed by both Able SC Columbia and AccessAbility.
- **Legal aid.** One statewide card for South Carolina Legal Services' LATIS intake: 888-346-5592, or 803-744-9430 in Richland and Lexington, Monday to Thursday 9 a.m. to 6 p.m.
- **VA health care.** One statewide card for the Columbia (Dorn, 803-776-4000) and Charleston (Ralph H. Johnson, 843-577-5011) systems, from VA's facility directory. No counties are assigned.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. County office addresses and hours, regional ombudsman direct lines and South Carolina waiver and home-modification program details are not yet researched.
