# Wisconsin referral edition

Reviewed November 15, 2026. Wisconsin moves from a starter edition to a full edition covering all 72 counties. The edition is built from one research sheet, `data/source/states/wi.json`, by `scripts/make_county_state.py WI`; the sheet names the page behind every contact.

## Veterans contacts (`wisconsin-county-veterans-offices.json`)

Wisconsin law puts a County Veterans Service Officer in every county, and the Wisconsin Department of Veterans Affairs (WDVA) points veterans to them. The department's own pages send readers to the County Veterans Service Officers Association of Wisconsin for the local list.

- **Source.** The association's [Locate your CVSO/TVSO](https://wicvso.org/locate-your-cvso-tvso/) page, read in full through a text-extraction tool. It lists all 72 counties, plus 11 tribal offices. The page is labeled as an association directory.
- **What is shown.** County, street or box address and phone. Staff names, emails and the tribal offices were left out. The page prints no office hours, so the cards print none and tell readers to call first.
- **Two offices.** Winnebago (Oshkosh and Neenah-Menasha) and Wood (Wisconsin Rapids and Marshfield) each have two offices. The first is the main card; the second is listed as another office.
- **Door County.** A toll-free number, 888-743-1844 ext. 2226, is shown as another number.
- **Post office boxes.** Menominee, Oneida and Waushara print only a post office box. Their notes say so; for Menominee and Waushara the note also gives the street address the state's ADRC listing shows for the county human services building.
- **Normalized text.** Iowa County's "303 Chapel – Suite 1300" is shown as 303 W. Chapel St., Suite 1300, matching the state's ADRC listing for the same building. Barron's address typo ("Monroe ve.") is corrected to "Ave.".
- **Milwaukee.** An older City of Milwaukee page lists 414-382-1727; the association's 414-266-1235 is shown.
- **Statewide line.** The Wisconsin Veterans Benefits and Resource Center, 1-800-WIS-VETS (800-947-8387), and the WDVA Claims Assistance Office, 833-494-7256, come from WDVA pages and a 2025 WDVA brochure (search excerpts).

## Aging and ombudsman (`wi-regional-referrals.json`)

- **Aging and Disability Resource Centers (57, `wi-adrc-*`).** Wisconsin's local aging contact is the ADRC, not an Area Agency on Aging, so the cards and the guide's wording say "Aging and Disability Resource Center." Forty-nine centers serve one county and eight serve several: Barron and Rusk; Buffalo and Pepin; Central Wisconsin (Langlade, Lincoln, Marathon, Wood); Eagle Country (Crawford, Juneau, Richland); Northwest Wisconsin (Burnett, Polk); the Lakeshore (Kewaunee, Manitowoc); the North (Ashland, Bayfield, Iron, Price, Sawyer); and the Wolf River Region (Menominee, Oconto, Shawano). The groupings come from the Department of Health Services' county map (P-02356, January 2026). Each county has exactly one center.
  - **Evidence level.** The state's [ADRC contact list](https://www.dhs.wisconsin.gov/adrc/contacts.htm) is paginated and the fetch tool returned only part of each page. Names and phones for all 68 entries (57 ADRCs and 11 tribal partners) came from the list's summary; many street addresses came from other pages of the same listing. All 57 cards are therefore labeled search-excerpt evidence, and ADRCs whose address was not visible show a phone only.
  - **Monroe County.** The summary list prints 888-339-7854; the entry's own listing prints 800-339-7854, which is shown.
  - **Statewide card (`wi-adrc`).** 844-WIS-ADRC (844-947-2372), which the state's page gives for finding a local center or Tribal aging and disability resource specialist.
- **Ombudsman (`wi-omb-boaltc`, `wi-ombudsman`).** The Board on Aging and Long Term Care runs the program. It says ombudsmen serve statewide, are assigned by region, and in Milwaukee County by ZIP code, and gives one toll-free line, 800-815-0015. The state's county-by-county coverage table could not be read in full, so the edition shows the statewide line for every county rather than naming an ombudsman. The program serves residents age 60 and older; the Department of Health Services says a separate program for ages 18–59 is run by Disability Rights Wisconsin (800-928-8778, from a State Bar resource list). Search-excerpt level.
- **Abuse reporting.** The Wisconsin Elder Abuse Hotline, 833-586-0107, for age 60 and over, from the Department of Health Services' Adult Protective Services contact list and reporting flyer. Each county also has its own agency; the edition shows the statewide hotline.

## Other records (`wi-programs.json`)

- **Claims help (`wi-claims`).** WDVA's Veterans Benefits and Resource Center and Claims Assistance Office, plus the county office list. Search-excerpt level.
- **Medicare counseling (`wi-ship`).** The Medigap Helpline, 800-242-1060, which the Board on Aging and Long Term Care describes as Wisconsin's statewide State Health Insurance Assistance Program helpline, and the Part D and prescription drug helpline, 855-677-2783 (residents 60 and over). Search excerpts.
- **Centers for Independent Living (8, `wi-cil-*`).** Addresses, phones, websites and counties come from the Department of Health Services' *Independent Living Centers Serving Wisconsin* (P-02357), read in full; the department's "Find an Independent Living Center" page, read in full, is cited as a second source for counties. The 72 counties split exactly across the eight centers: indiGO (8), Compass IL (10), Midstate Independent Living Choices (11), Independent Living Resources (13), Options for Independent Living (17), Access to Independence (4), IndependenceFirst (4) and Society's Assets (5). Compass IL was formerly the Center for Independent Living for Western Wisconsin, and Midstate's address changed from 3262 Church Street to 1101 Brilowski Road; the newer state listings are used.
- **Housing help (SSVF).** Four providers from VA's FY26 intake workbook, added by the edition builder: Community Action Coalition for South Central Wisconsin, Indianhead Community Action Agency, Transitional Living Services and the Center for Veterans Issues.
- **Legal aid (`wi-legal-programs`).** Legal Action of Wisconsin, intake 855-947-2529, serves the southern 39 counties and has staff for veterans; Judicare Legal Aid, 800-472-1638, serves the 33 northern counties. The card does not assign counties to each agency because the state sources name regions, not county lists. Search-excerpt level.
- **VA health care (`wi-vahealth-systems`).** One statewide card: Zablocki (Milwaukee), Tomah, Middleton (Madison), and the Iron Mountain, Michigan, and Minneapolis medical centers the state names, with phones for the three Wisconsin hospitals from VA's facility directory. No counties are assigned. Search-excerpt level.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours for county veterans offices; the association prints none.
- Street addresses for about 20 ADRCs, which were not visible in the fetched pages.
- Which regional ombudsman serves which county, and county-level Adult Protective Services numbers.
- Tribal Veterans Service Offices and Tribal aging and disability resource specialists, which are not on county cards.
- Which legal aid agency serves each county.
- Dates for the association's list; the page prints none.
