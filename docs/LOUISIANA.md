# Louisiana referral edition

Reviewed November 16, 2026. Louisiana moves from a starter edition to a full edition covering all 64 parishes. The edition is built from one research sheet, `data/source/states/la.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md). Louisiana is the first edition whose county equivalents are parishes: offices carry `county_type: "parish"`, so the guide shows "Acadia Parish", and the sheet's `locality_word`, `adapter.post_swaps`, `page_replacements` and `share_replacements` carry the parish wording into the records, the page and the sharing kit. The shared guide and the guided-assistance state list label Louisiana's picker, search box and handoffs with "parish".

## Veterans contacts (`louisiana-county-veterans-offices.json`)

Every parish is served by a **veterans service office of the Louisiana Department of Veterans Affairs (LDVA)**. LDVA staff help with VA claims at no charge; the cards are badged "LDVA parish veterans service office".

- **Source.** LDVA's [Locations](https://vetaffairs.la.gov/locations) list and the page it publishes for each office. 61 parish office pages (East and West Feliciana share one) were read in full, two of them (East Baton Rouge and St. Bernard) in the site's French-language version because the English page was not reachable. East Carroll and Sabine were read through search excerpts of their pages and carry `official_search_excerpt` as their review method.
- **Open days.** Most offices are not open every weekday; many are open one to three days a week. Each card gives the days and hours printed on its page. Parishes whose page also lists an itinerant schedule without a location (Allen, Evangeline, Grant, Red River) say so in the note.
- **Other offices.** Ascension (Donaldsonville), Jefferson (West Bank, Marrero), Jefferson Davis (fairgrounds), Lafourche (Mathews), St. Landry (Eunice), St. Tammany (Slidell), Tangipahoa (Kentwood) and Washington (Franklinton) list their second office or itinerant point. Jefferson's card shows the East Bank office first and St. Tammany's the Covington office. Webster's Springhill point is listed by LDVA as closed until further notice.
- **Shared offices.** One office in Jackson serves East and West Feliciana. Cameron Parish has no walk-in office on LDVA's site; its card gives the Calcasieu office's phone and mailing address, which the Cameron page lists.
- **Not used.** LDVA's printed *Guide to Veterans Benefits* has a parish phone list, but it is undated and several of its numbers (Avoyelles, Catahoula, Lafourche, Terrebonne, the Felicianas and others) no longer match the parish pages, so every phone comes from the office's own page.
- **Conflicts noted.** Washington Parish's page shows Monday–Wednesday hours in its table but also says the Bogalusa office opens the second, third and fourth Monday of each month; the card shows both and says to call first. LDVA's list places the Lafourche itinerant point at 4876 Louisiana 1, Raceland; the parish page says 4876 Highway 1, Mathews; the card gives both.
- **What is shown.** Address, phones and open days. Staff names and email addresses are left out.

## Aging and ombudsman (`la-regional-referrals.json`)

- **Area Agencies on Aging (34, `la-aaa-*`).** From the Governor's Office of Elderly Affairs (GOEA) [Area Agencies on Aging directory](https://goea.la.gov/agency-directory/area-agencies-on-aging-directory), read in full (undated). Three agencies serve several parishes (Cenla, 15; Capital, 10; Cajun, 8); the other 31 serve one parish each, mostly through the parish council on aging. Phones and offices come from the same directory.
- **Statewide line (`la-adrc`).** Louisiana Answers, 877-340-9100, the information, referral and assistance line for the nine Aging and Disability Resource Centers, from GOEA's April 2026 report to the Developmental Disabilities Council (search excerpt).
- **Ombudsman (7 regions, `la-omb-*`).** From GOEA's [ombudsman contact list](https://goea.louisiana.gov/media/gkmfvrto/ombudsman-flyer-and-contact-list-2026.pdf) (Rev. 06/2026), read in full: each region's host agency, phones and parishes. The state office is 866-632-0922.
- **Abuse reporting.** Elderly Protective Services, 833-577-6532, for people 60 and older (after hours 844-945-2377); Adult Protective Services, 800-898-4910, for adults 18 to 59.

## Other records (`la-programs.json`)

- **Claims help (`la-claims`).** Parish offices, above, and LDVA headquarters, 225-219-5000.
- **Medicare counseling (`la-ship`).** The Department of Insurance's Senior Health Insurance Information Program (SHIIP, also called LaSHIP), 800-259-5300. The program page prints no phone; the number is cited to the department's Medicare guide and CMS's directory (search excerpts).
- **Centers for Independent Living (3, `la-cil-*`).** From the [ILRU directory](https://www.ilru.org/cil-directory/la), read in full (undated): New Horizons (Shreveport, with Monroe and Alexandria offices; 28 parishes), New Orleans Resources for Independent Living (Kenner, with a Baton Rouge office; 23 parishes, lower St. Martin only) and the Southwest Louisiana Independence Center (Lake Charles, with Lafayette and Leesville offices; 14 parishes). ILRU lists "Jefferson" for SLIC; the Department of Health lists Jefferson Davis, so SLIC is shown there and Jefferson Parish keeps NORIL. **Caldwell and St. Mary parishes have no center listed.** New Horizons and SLIC link to the ILRU directory because no https website address for them appears in the sources read.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`la-legal-programs`).** Southeast Louisiana Legal Services (22 parishes; 844-244-7871; helps veterans with discharge upgrades, VA benefits and overpayments) and Acadiana Legal Service Corporation (42 parishes; 866-275-2572, from the WomensLaw directory listing because ALSC's own page was not read), plus the Louisiana State Bar Association's Find Legal Help portal.
- **VA health care (`la-vahealth-systems`).** Southeast Louisiana Veterans Health Care System (800-935-8387), Alexandria VA Health Care System (318-473-0010) and Overton Brooks VA Medical Center, Shreveport (318-990-5547).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Parish councils on aging in the 33 parishes served by the three multi-parish agencies; the agency card says to ask for the parish council.
- Locations of the itinerant schedules that LDVA lists without an address (Allen, Evangeline, Grant, Red River).
- Acadiana Legal Service Corporation's phone from its own website.
