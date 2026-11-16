# Delaware referral edition

Reviewed November 16, 2026. Delaware moves from a starter edition to a full edition covering all three counties. The edition is built from one research sheet, `data/source/states/de.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`delaware-county-veterans-offices.json`)

Delaware has no county veterans service officers. The Office of Veterans Services, in the Department of State, has Veteran Service Officers who help with claims.

- **Source.** The Office of Veterans Services [contact page](https://vets.delaware.gov/contact), read in full: address, phone and email. Staff names are omitted.
- **Offices by county.** The page says the service office is reached through the Dover headquarters (Robbins Building, 802 Silver Lake Blvd., Suite 100; 302-739-2792) and serves all three counties, so Kent, New Castle and Sussex all show the Dover office.
- **Not used.** An older preview of the state site lists a Veteran Service Officer line for each county. The current contact page does not, so those lines are left out.

## Aging and ombudsman (`de-regional-referrals.json`)

- **Aging (`de-adrc-state`).** The Delaware Aging & Disability Resource Center, 1-800-223-9074 (TDD only 302-424-7141), run statewide by the Division of Services for Aging and Adults with Physical Disabilities. From the division's [contact page](https://dhss.delaware.gov/dsaapd/contact), read in full. One record covers all three counties, and the edition calls it the Aging & Disability Resource Center rather than an Area Agency on Aging.
- **Ombudsman (`de-omb-state`, `de-ombudsman`).** The Long-Term Care Ombudsman Program hotline, 1-855-773-1002, statewide, with anonymous complaints by phone ([program page](https://dhss.delaware.gov/office-of-the-secretary/long-term-care-ombudsman-program/), read in full).
- **Abuse reporting.** Adult Protective Services, 1-888-277-4302 (Delaware Relay 711). For nursing home or assisted living residents, the Division of Health Care Quality line, 1-877-453-0012, is open 24/7. Both are from the division's contact page.

## Other records (`de-programs.json`)

- **Claims help (`de-claims`).** The Office of Veterans Services, above.
- **Medicare counseling (`de-ship`).** The Delaware Medicare Assistance Bureau, 1-800-336-9500 or 302-674-7364 ([Department of Insurance page](https://insurance.delaware.gov/consumer/dmab), read in full; modified November 6, 2026).
- **Centers for Independent Living (2, `de-cil-*`).** Independent Resources, Inc. (offices in Wilmington, Dover and Milford; all three counties) and The Freedom Center for Independent Living (Middletown; New Castle County), from the [ILRU directory](https://www.ilru.org/cil-directory/de), read in full. The directory prints two street addresses for the Milford office; the card says so.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`de-legal-programs`).** Community Legal Aid Society, Inc. (CLASI): the Elder Law Program, 302-575-0666, for anyone 60 or older with no income test, and the county offices in Wilmington, Dover and Georgetown ([contact page](https://www.declasi.org/?p=455), read in full).
- **VA health care (`de-vahealth-systems`).** VA Wilmington Healthcare System: the Wilmington VA Medical Center, 302-994-2511, primary care at 800-461-8262 (select 2), clinics in Kent and Sussex counties, and Vet Centers in Wilmington and Georgetown (search excerpts).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office of Veterans Services hours and any outreach days outside Dover; the contact page gives none.
- Clinic street addresses; two sources give different addresses for the Sussex County clinic.
