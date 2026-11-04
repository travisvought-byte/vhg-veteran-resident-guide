# Georgia referral edition

Reviewed November 4, 2026. Georgia moves from a starter edition to a full 159-county edition. Each county gets a Georgia Department of Veterans Service (GDVS) veterans contact, a matched Area Agency on Aging and the statewide long-term-care ombudsman route.

## Veterans contacts (`georgia-county-veterans-offices.json`)

GDVS runs state Veterans Field Service Offices, not county offices.

- **Office list.** The [field office list](https://veterans.georgia.gov/field-offices) was read in full. It gives each of the 57 offices' address and the counties it serves.
- **Office pages.** Phones, hours and notices come from each office's own GDVS page, which was read for every office used as a county's first contact (43 offices). Staff names and emails on those pages were not published.
- **Choosing a county's first office.** Where several offices serve a county, the first one in the list becomes the primary contact. Offices on military bases, at the war veterans homes, at technical colleges and at Gwinnett resource centers are not chosen as primary when the county has another office. The others appear under "Other GDVS offices" on the county card.
- **Spelling.** The list spells Glascock as "Glasscock"; it is mapped to Glascock County.
- **Counties with no assigned office.** The list assigns no office to Elbert, Lincoln or Wilkes. Those counties use the GDVS main line (404-656-2300), with a note saying so.
- **Brunswick.** The Brunswick CBOC office (Glynn, McIntosh) is temporarily closed. Its page sends veterans to Hinesville, Glennville, St. Marys or Waycross. Glynn uses St. Marys, McIntosh uses Hinesville, and all four alternatives are listed on the card.
- **Office pages not under `/locations/`.** Six pages were read at other GDVS addresses (node or short URLs): Augusta-VAMC, Augusta-DHS, GWVH-Milledgeville, Decatur-VAMC, Rock Spring (LaFayette) and the Cobb Multi-Specialty VA Clinic. The Cobb clinic page is a staff contact page; only its phone and address are used.
- **Liberty County** uses Hinesville, the office inside the county, rather than the first-listed Glennville office.
- **Zebulon** (Lamar, Pike, Talbot, Upson) is temporarily closed. It is left out of those counties' alternatives, and their cards say so; they keep Griffin or Macon as their main office.
- **Office notices shown on cards:**
  - St. Marys has no in-person service on Fridays.
  - Albany is temporarily relocated during renovations.
  - Rome asks people to call before visiting.
  - LaGrange has moved.

## Aging and ombudsman

- **Aging agencies (12 records, `ga-aging-*` in `ga-regional-referrals.json`).** Taken from the contact pages of the DHS Division of Aging Services [2024–2027 State Plan on Aging](https://aging.georgia.gov/document/document/das-state-plan-2024-2027/download). Each county is covered by exactly one agency.
- **Ombudsman (`ga-ombudsman`).** The statewide program at 866-552-4464, option 5. Community ombudsman programs are reached through that line or the Area Agency on Aging.
- **ADRC (`ga-adrc`).** The statewide counseling line, 866-552-4464, option 2.

## Other records (`ga-programs.json`)

- **Housing help (SSVF).** The 7 programs now use county lists from VA's FY26 intake workbook instead of a single statewide card.
- **Centers for Independent Living (9 records, `ga-cil-*`).** Taken from the ILRU national directory, with full page text reviewed. They cover 142 of 159 counties. The 17 uncovered counties are Appling, Bacon, Brantley, Candler, Carroll, Charlton, Crisp, Dooly, Heard, Long, Macon, Pierce, Schley, Sumter, Troup, Ware and Wayne; they rely on the ADRC and the aging agency.
  - Disability Connections' Dublin and Pitts offices are folded into the Macon record, since they share its phone.
  - The Disability Resource Center Gainesville listing is folded into the Demorest record.
  - Two directory misspellings were corrected: "Treultlen" to Treutlen and "Bullock" to Bulloch.
  - Websites the directory lists only as http are given in the next step, and the card links to the ILRU page.
- **Legal aid.**
  - Georgia Legal Services Program (833-457-7529) covers the 154 counties outside metro Atlanta.
  - Atlanta Legal Aid Society (404-524-5811) covers Clayton, Cobb, DeKalb, Fulton and Gwinnett.
  - The Georgia Senior Legal Hotline (888-257-9519) is statewide, for age 60 and older.
- **VA health care (`ga-vahealth-systems`).** One statewide card for the Atlanta, Augusta and Dublin medical centers. No counties are assigned.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Office hours and temporary closures change, so confirm before traveling. Georgia waiver, home-modification and state program details beyond the ADRC, aging agencies, independent living centers and legal aid are not yet researched.
