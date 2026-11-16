# New Jersey referral edition

Reviewed November 16, 2026. New Jersey moves from a starter edition to a full edition covering all 21 counties. The edition is built from one research sheet, `data/source/states/nj.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`new-jersey-county-veterans-offices.json`)

The New Jersey Department of Veterans Affairs (DVA, formerly part of the Department of Military and Veterans Affairs) runs a state **Veterans Service Office in every county**; the last seven opened in 2024. Each county shows its state office, marked as a state office.

- **Source.** DVA's [Veterans Service Offices](https://nj.gov/dva/veterans/services/vso/) page, read in full; the page was last updated November 10, 2026.
- **What is shown.** Office address, phones and hours as printed. Officers' names, email addresses and fax numbers are left out. Most offices are open Monday–Friday, 8:00 a.m.–4:00 p.m., and close on alternate Fridays; Hudson (8:30 a.m. start) and Sussex (Monday, Wednesday and Thursday) differ, and each card shows its own hours.
- **Extra offices.** Essex County has three more locations with shorter hours (the Newark Liaison Office at the VA Newark Regional Office, Newark City Hall, and the East Orange VA Medical Center), and Burlington County has a Wednesday-only office in Bordentown. They appear under "Other offices" on those cards.
- **Same phone in two counties.** The page prints 609-671-3571 for both the Morris and Sussex offices; both cards say so.
- **Statewide lines.** The toll-free Veterans Service Offices line, 844-671-1019, connects callers to their county's office. The NJ Veterans Benefits Hotline, 888-865-8387, answers questions about state benefits.
- **County-run veterans offices.** Many county governments also run their own veterans services. They are not listed: the only statewide list found (on a Department of State page) is undated and contains an Essex County, New York address, so it was not used.

## Aging and ombudsman (`nj-regional-referrals.json`)

- **County offices on aging (21, `nj-aaa-*`).** One per county, from the Division of Aging Services' [County Offices on Aging](https://www.nj.gov/humanservices/doas/assistance/county-offices) page, read in full (page metadata August 11, 2026). Each is the county's Area Agency on Aging and Aging and Disability Resource Connection.
- **Statewide line (`nj-adrc`, `nj-ship`).** The Aging and Disability Resource Connection, 877-222-3737, and SHIP Medicare counseling, 800-792-8820, with counseling sites in every county.
- **Ombudsman (`nj-omb-state`, `nj-ombudsman`).** The Office of the Long-Term Care Ombudsman is one statewide office (877-582-6995, option 1 for complaints), so every county shows it. Complaints about licensed facilities can also go to the Department of Health, 800-792-9770.
- **Abuse reporting.** Adult Protective Services, 855-TELL-APS (855-835-5277), from a Division of Aging Services flyer. Adult Protective Services is run county by county; the state's flyer gives this one toll-free number for reports.

## Other records (`nj-programs.json`)

- **Claims help (`nj-claims`).** DVA's Veterans Service Offices, above.
- **Centers for Independent Living (15, `nj-cil-*`).** The Division of Disability Services [list](https://www.nj.gov/humanservices/dds/resources/centersforlivingindex.shtml) names a center under every county (page metadata October 5, 2026), read in full and checked against the ILRU [New Jersey directory](https://www.ilru.org/cil-directory/nj). Every county has at least one center. Where the two lists disagree on a suite number or street address (Camden City, hip Hudson, MOCEANS Long Branch, PCIL Mercer), the card's note gives both. Cape May County is listed by the state under Resources for Independent Living's Burlington office; ILRU names no center for Cape May. DIAL and PCIL publish only http website addresses, so their cards link to the state list.
- **Housing help (SSVF, 5).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`nj-legal-programs`).** Legal Services of New Jersey's LSNJLAW Hotline (888-576-5529, Monday–Friday, 8:00 a.m.–5:30 p.m.) and Volunteer Lawyers for Justice's Veterans Legal Program (973-645-1955).
- **VA health care (`nj-vahealth-systems`).** VA New Jersey Health Care System (East Orange 973-676-1000; Lyons 908-647-0180), with South Jersey also served by the Philadelphia (215-823-5800) and Wilmington (302-994-2511) VA medical centers.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- County-run veterans services offices (above).
- County-level Adult Protective Services phones; the card gives the statewide number.
- A date for the ILRU directory, which prints none.
- The Volunteer Lawyers for Justice phone comes from a 2022 VA event listing; the program page itself was read only as a search excerpt.
