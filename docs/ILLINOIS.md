# Illinois referral edition

Reviewed November 4, 2026. Illinois moves from a starter edition to a full 102-county edition. Illinois was skipped earlier in the veteran-population order; it comes after South Carolina here.

## Veterans contacts (`illinois-county-veterans-offices.json`)

Illinois has no single county veterans office network. Two kinds of office exist:

- IDVA Veteran Service Offices, run by the state.
- County Veterans Assistance Commissions (VACs).

Each county uses one primary contact:

1. **IDVA Veteran Service Office (54 counties).** Taken from the [IDVA office locator](https://veterans.illinois.gov/serviceoffices/vso-locator-countylist.html). The page loads its 84 locations from a data feed. The feed was read in the built-in browser because the page shows nothing without JavaScript.
   - Locations marked temporarily closed or unavailable are left out: Albion, Bourbonnais, Carlyle, the Danville VAMC office, East Alton and East St. Louis.
   - Mattoon CBOC is also left out because it lists no phone.
   - A full-week office comes first. Other open offices in the county appear under "Other IDVA offices."
   - The "Kendall County Itinerate" office is filed under Kane in the feed. It is listed under Kendall here, as its name says.
   - Staff names and emails are not in the feed and are not shown.
2. **County VAC (8 counties).** Used where IDVA has no open office and the VAC phone is published on the county's own website: Bond, Clinton, Grundy, Iroquois, Madison, Piatt, Tazewell and Washington.
3. **IDVA statewide line, 800-437-9824 (40 counties).** Used everywhere else, with a note.

Counties on the [IACVAC locations list](https://www.veteransbenefitsillinois.org/locations) (53) get a note that the county also has a VAC. VAC phones from non-official directories (for example Boone, Lee and Warren) were not used.

## Aging and ombudsman (`il-regional-referrals.json`)

- **Area Agencies on Aging (13, `il-aging-psa*`).**
  - Source: the Department on Aging's [Senior Centers and Focal Points directory](https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/documents/seniorcenters.pdf), updated February 25, 2025.
  - The toll-free number is the main phone where one is printed. The local number and any toll-free limits are shown as notes.
  - Cook County has two agencies: Chicago (PSA 12) and AgeOptions (PSA 13, suburban Cook).
- **Regional ombudsmen (17, `il-ombudsman-*`).** From the Department on Aging's [regional ombudsman contact list](https://ilaging.illinois.gov/programs/ltcombudsman/ltcop-regional-ombudsman-public-contact-list.html), read in full.
  - PSA 2 is split among four providers by county.
  - Cook has three programs: City of Chicago, City of Evanston, and suburban Cook (Legal Aid Chicago). The county panel lists all three.
- **Statewide records.**
  - `il-ombudsman` and `il-senior-helpline`: the Senior HelpLine, 800-252-8966.
  - Adult Protective Services hotline: 866-800-1409.

## Other records (`il-programs.json`)

- **Housing help (SSVF).** The 9 programs now use county lists from VA's FY26 intake workbook.
- **Centers for Independent Living (21 records).** Branch offices from the ILRU directory are folded into their main center and listed in its next step.
  - IICIL's Iowa counties (Clinton, Muscatine and Scott) are noted but not assigned.
  - SAIL's Decatur main office is assigned Macon County, which the ILRU listing omits. The card says so.
  - Centers whose websites are http-only point to the ILRU page and name the website.
- **Legal aid.**
  - Legal Aid Chicago, for Cook County, at 312-341-1070, from the Department of Human Rights.
  - One statewide card for Land of Lincoln (877-342-7891) and Prairie State. No counties are assigned.
- **VA health care.** One statewide card for Hines, Jesse Brown, Lovell, Danville and Marion. No counties are assigned.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Remaining gaps:

- VAC phones for the 40 counties that use the statewide line.
- Prairie State's county offices.
- The Illinois waiver and home-modification program details.
