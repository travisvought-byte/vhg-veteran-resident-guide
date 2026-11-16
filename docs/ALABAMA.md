# Alabama referral edition

Reviewed November 15, 2026. Alabama moves from a starter edition to a full edition covering all 67 counties. The edition is built from one research sheet, `data/source/states/al.json`, by `scripts/make_county_state.py AL`; the sheet names the page behind every contact.

## Veterans contacts (`alabama-county-veterans-offices.json`)

The Alabama Department of Veterans Affairs (ADVA) publishes the list of county Veterans Service Offices. Many offices serve more than one county, and several keep limited hours, so hours are printed on every card.

- **Source.** The department's [Veterans Service Offices](https://va.alabama.gov/service-officer) page. It was read through a text-extraction tool and carries no printed date. Addresses, phones and hours are as the page prints them; staff names and emails were left out.
- **Shared offices.** Where the list groups counties under one office, each county keeps its own card and the note names the office that serves it: Autauga and Lowndes (Prattville); Bibb and Hale (Centreville); Bullock and Montgomery (Montgomery); Dallas and Perry (Selma); Marengo and Wilcox (Linden); Coosa and Tallapoosa (Alexander City); Clarke and Washington (Grove Hill).
  - Colbert and Lauderdale are served from two offices, Tuscumbia and Florence. Each county shows its nearer office first and the other under "Other offices."
  - Coosa also lists itinerant service at Goodwater, Jefferson an office at Bessemer, and Washington the Grove Hill office in Clarke County.
- **Montgomery.** Sources differ and the card follows the newer one.
  - The list and other pages differ on the street number (100 or 102 Dexter Avenue); the department's March 2026 newsletter prints 100 and the card shows it.
  - The list shows shorter Friday hours; the March 2026 newsletter says Monday through Friday, 8 a.m. to 5 p.m. The card shows the newsletter's hours and the note says the list differs.
  - A second Montgomery County office at the Alabama National Guard Joint Force Headquarters is shown under "Other offices."
- **Covington.** The county office moved in April 2026 to the County Health Department building, 23989 Highway 55, Andalusia, per the department's announcement. The list still printed the old street number. The card shows the announced address.
- **Houston.** The list also marks Friday as by appointment only; the card says to call ahead.
- **Pickens.** The list prints the same phone numbers for Pickens and Tuscaloosa Counties. Both are shown as printed and the Pickens note says so. Pickens hours are the first Tuesday of the month.
- **Shelby.** The list shows an Alabaster office (205-624-3162) as temporarily closed, so the card shows the main office and mentions Alabaster in the note.
- **Macon.** The office is inside the Central Alabama Veterans Health Care System campus at Tuskegee; the note says so.
- **Gaps.** The Colbert County courthouse address in Tuscumbia prints no ZIP code on the list, and none was added.

## Aging and ombudsman (`al-regional-referrals.json`)

- **Area Agencies on Aging (13, `al-aaa-*`).** From the Alabama Department of Senior Services page [Area Agencies on Aging and Aging & Disability Resource Centers](https://alabamaageline.gov/?p=2206), read in full: agency, counties, main phones, street addresses and websites for all 13. Each county has exactly one agency. Alabama does not number its regions on that page, so cards show the agency's name rather than a region number.
  - Eight of the 13 list a toll-free number; the card note shows it.
  - United Way Area Agency on Aging of Jefferson County is marked on the page as Older Americans Act services only; the card says so.
  - South Alabama Regional Planning Commission's own senior directories print 251-706-4680 instead of the department's 251-433-6541. The department's number is shown and the note names the other.
  - Statewide card: Alabama AGELINE, 800-243-5463, which connects callers to the agency for their county.
- **Regional ombudsman programs (13, `al-omb-*`).** Alabama delivers the ombudsman program through 13 regional programs hosted by the same 13 agencies.
  - The state ombudsman page (334-242-5753) lists no regional contacts. Each card shows the host agency's main line from the department's list and says to ask for the regional long-term care ombudsman, with the state office as the fallback.
  - The host agencies and their counties match the National Consumer Voice directory of Alabama ombudsman programs, an association page with no printed date, which is cited as a second source on every card.
  - Two cards name a different number in their notes: the directory and the agency's own brochure print 256-389-0530 for the Northwest Alabama program (the card shows the agency main line, 256-389-0500), and the directory prints 334-682-4234 or 888-617-0500 for the Tombigbee program (the card shows 334-682-5206).
- **Abuse reporting.** The Department of Human Resources Adult Protective Services page lists the Adult Abuse Hotline, 800-458-7214. That source is a search excerpt. The county panel shows it as open 24 hours a day, 7 days a week.

## Other records (`al-programs.json`)

- **Claims help (`al-claims`).** Phone 334-242-5077, from the department's own page, matched on November 2, 2026 as name and phone only (a search excerpt). It sends callers to the county Veterans Service Office first.
- **Alabama AGELINE (`al-adrc`).** 800-243-5463, from the Senior Services page (a search excerpt).
- **Housing help (SSVF).** Three providers from VA's FY26 intake workbook: Housing First, Inc. (Baldwin and Mobile Counties, 251-450-3345, with 251-303-8058 as a second intake number), Volunteers of America Southeast, Inc. (9 counties, 205-945-7172) and United Way of Central Alabama (65 counties, 866-460-3827). These cards are added by the edition builder, not by the research sheet.
- **Centers for Independent Living (4, `al-cil-*`).** Four centers whose county lists together cover all 67 counties: Disability Rights & Resources (Birmingham, 20 counties), Disability Resource Network (Huntsville, 13), Independent Rights & Resources (Montgomery, 18) and the Independent Living Center of Mobile (16).
  - The first three come from the Alabama centers directory published by Disability Rights & Resources, which is a member-center page, not a state agency page; their cards carry the association-directory label.
  - The Mobile center's address, phone and counties come from the ILRU national directory, because a peer directory lists an older Mobile address (5301 Moffett Road).
- **Legal aid (`al-legal-programs`).** Legal Services Alabama, 866-456-4995 (Spanish 888-835-3505), Monday through Friday, 8:30 a.m. to 4:30 p.m. A VA-funded program helps veterans who are homeless or at risk of homelessness. Not criminal defense; applicants are screened.
- **VA health care (`al-vahealth-systems`).** One statewide card for the Birmingham VA Health Care System, the Central Alabama Veterans Health Care System (Montgomery and Tuskegee campuses) and the Tuscaloosa VA Medical Center. VA publishes no county lists for these systems in the pages read, so no counties are assigned. The VA directory pages are search excerpts, except the Central Alabama contact page, which was read in full.
- **Medicare counseling (`al-ship`).** 800-243-5463, from the Senior Services SHIP page, read in full.
- **State ombudsman (`al-ombudsman`).** 334-242-5753, from the Senior Services ombudsman page, read in full.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Direct numbers and names for the regional ombudsmen (cards show each host agency's main line).
- The date of the Veterans Service Offices page and of the ombudsman directory; neither prints one.
- County Adult Protective Services intake numbers; the edition uses the statewide hotline.
- Veterans whose care is at a VA system outside the three listed, such as the Gulf Coast system based in Biloxi.
- Housing-assistance providers, home-modification programs and senior-center directories.
