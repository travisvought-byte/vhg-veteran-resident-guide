# Maryland referral edition

Reviewed November 15, 2026. Maryland moves from a starter edition to a full edition covering all 24 jurisdictions: 23 counties and Baltimore City. The edition is built from one research sheet, `data/source/states/md.json`, by `scripts/make_county_state.py MD`; the sheet names the page behind every contact. Baltimore City is its own jurisdiction, shown as "Baltimore City" and kept apart from Baltimore County.

## Veterans contacts (`maryland-county-veterans-offices.json`)

The Maryland Department of Veterans and Military Families (DVMF) runs the state's veterans service offices, called Service Program offices.

- **Source.** The department's [How To Apply For Benefits](https://veterans.maryland.gov/Benefits/HowToApplyForBenefits) page, read in full through a text-extraction tool; it prints no date. It lists 16 DVMF offices plus one local county program. Offices are open Monday through Friday, 8:00 a.m. to 4:00 p.m., by appointment only. Staff names and emails were left out.
- **No county coverage is printed.** The page does not say which counties each office serves. The edition does not guess coverage. Each county shows:
  - a DVMF office located in that county, where the page lists one: Allegany (Cumberland), Anne Arundel (Annapolis, with Glen Burnie as a second office), Baltimore City (the Baltimore regional office), Baltimore County (Rosedale), Cecil (Elkton), Charles (Waldorf), Frederick, Harford (Bel Air), Howard (Laurel), Montgomery (Gaithersburg), Prince George's (Camp Springs), St. Mary's (Charlotte Hall), Talbot (Easton), Washington (Hagerstown) and Wicomico (Salisbury); or
  - for Calvert, Caroline, Dorchester, Garrett, Kent, Queen Anne's, Somerset and Worcester, which have no listed office, the statewide service line, 800-446-4926 ext. 6450, which the page gives for the Baltimore regional office. The card says to ask which office serves the county and lists the nearest offices in neighboring counties under "Other offices." Which offices are nearest is a geographic judgment from the office addresses, not a department statement.
- **Carroll County.** The page lists the Carroll County Veterans Services Program (125 Stoner Avenue, Westminster, 410-386-3800, "call for information on hours") and says it is supported by the department but is not a department service office. The card shows it as a county office.
- **Rosedale.** This office is at the VA clinic in Rosedale and is open Wednesdays 9:00 a.m. to 1:00 p.m., excluding federal holidays. The Baltimore regional office is listed as the other office.
- **Phones and addresses.**
  - Annapolis and Gaithersburg each list two phone numbers; the second is shown as another number.
  - Bel Air lists a benefits specialist line, 410-638-6501, and an office secretary line that prints with a repeated "638" (410-638-638-6507). Only the first is shown.
  - The Camp Springs ZIP code prints as 20746 in the extracted text; the same building's address prints 20748 on the Department of Aging directory, and 20748 is shown.
  - Older state pages print 29431 Charlotte Hall Road; the current page prints 29449 and that is shown.
- **Not included.** The department's County Veterans Commissions and Data page lists local commissions and points of contact in some counties. They are advisory bodies rather than service offices and are not on the cards.

## Aging and ombudsman (`md-regional-referrals.json`)

- **Area Agencies on Aging (19, `md-aaa-*`).** From the Department of Aging's [directory](https://aging.prod.maryland.gov/media/42/download), read in full and undated: agency, counties, street address and phone. Two agencies serve several counties: Upper Shore Aging, Inc. (Caroline, Kent and Talbot) and MAC, Inc. (Dorchester, Somerset, Wicomico and Worcester). Each county has exactly one agency. The department's agency page prints each county heading with no entries under it in the extracted text, so the directory it links to is the source.
  - Queen Anne's County's line is 410-758-0848 with option 2 for the agency; the card says to press option 2.
  - Statewide card: Maryland Access Point, 1-844-627-5465 (1-844-MAP-LINK, or dial 211), from the Department of Aging contact page, read in full.
- **Local ombudsman programs (19, `md-omb-*`).** Maryland's program has a state office and 19 local programs located at the area agencies.
  - The Department of Aging's ombudsman page lists a phone for every jurisdiction under "Contact your Local Ombudsman." A direct fetch returned the heading with no list, so the numbers come from search excerpts of that page, checked against the department's mdoa.maryland.gov copy of it, which prints all 24 in one table. The cards are labelled as search-excerpt evidence.
  - The National Consumer Voice directory of Maryland ombudsman programs (undated, read in full, no phones) is cited as a second source for addresses and areas served.
  - The Carroll County ombudsman card shows 410-386-3810 from the state page; the county's own page prints 410-386-3800, the Bureau of Aging and Disabilities main line, and the note says so.
  - The state page prints no separate state ombudsman phone. The cards use the Department of Aging toll-free line, 800-243-3425, as the fallback.
- **Abuse reporting.** Adult Protective Services, 800-332-6347, from the Maryland Access Point "End Abuse" page (a search excerpt). County pages also list local numbers; the edition uses the statewide one.

## Other records (`md-programs.json`)

- **Claims help (`md-claims`).** The statewide service line above, from the department's office page and contact page.
- **Medicare counseling (`md-ship`).** 800-243-3425, from the Department of Aging's SHIP page, read in full. The page is undated; the same toll-free number is on the department's current contact page.
- **Centers for Independent Living (7, `md-cil-*`).** Addresses, phones and websites come from the ILRU national directory, read in full. Counties come from the Maryland Department of Disabilities' 2024 Home Modifications Directory, which is cited as a second source on each card. The two disagree in places:
  - Resources for Independence: ILRU lists Allegany only; the state lists Garrett, Allegany and Washington, which is used.
  - Bay Area Center for Independent Living: ILRU lists Wicomico only; the state says all 8 Eastern Shore counties from Somerset to Kent, which is used. Cecil County is not on that list, so it has no center card.
  - The IMAGE Center: ILRU lists Baltimore and Harford Counties; the state also lists Baltimore City, which is used.
  - Accessible Resources for Independence: ILRU prints 443-713-3914 and the state prints 410-636-2274; the ILRU number is shown and the note names the other.
  - The state's directory says seven centers but prints eight entries, with one listed twice.
  - The Southern Maryland center's website is printed with http in both directories; the card links its https address.
- **Housing help (SSVF).** Eight providers from VA's FY26 intake workbook, added by the edition builder. Project PLASE, Inc. (Anne Arundel, Baltimore City and Baltimore County) lists no intake phone in the workbook and is left out.
- **Legal aid (`md-legal-programs`).** Maryland Legal Aid, central intake 888-465-2468, and the Joining Forces hotline for low-income veterans, 443-863-4040, Tuesdays 3:00 to 7:00 p.m. and Thursdays 9:30 a.m. to 1:30 p.m. The hotline hours come from a bar-association directory and may change. All of these are search excerpts.
- **VA health care (`md-vahealth-systems`).** One statewide card for the VA Maryland Health Care System (Baltimore, Perry Point and Loch Raven), with the Washington DC and Martinsburg medical centers the state names for Southern and Western Maryland. The state's page names regions rather than counties, so no counties are assigned. Search-excerpt level.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Which DVMF office serves which county, because the department does not print it.
- The dates of the office list, the aging directory and the ombudsman directory; none prints one.
- Direct names and numbers for local ombudsmen beyond the phone each county page lists.
- County-level Adult Protective Services numbers.
- Veterans receiving care through the Wilmington VA system in Delaware.
- Home-modification programs and senior-center directories.
