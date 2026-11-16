# Kansas referral edition

Reviewed November 16, 2026. Kansas moves from a starter edition to a full edition covering all 105 counties. The edition is built from one research sheet, `data/source/states/ks.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`kansas-county-veterans-offices.json`)

Kansas has no county veterans offices. Veteran service representatives of the **Kansas Office of Veterans Services (KOVS)**, formerly the Kansas Commission on Veterans Affairs Office, work from 16 state field offices.

- **Source.** Each field office has a page on the KOVS website listing its address, phones, the counties it serves and an itinerant schedule. Fifteen pages were read in full: Atchison, Colby, Emporia, Hays, Hutchinson, Independence, Junction City, Kansas City, Lawrence, Manhattan, Overland Park, Salina, Topeka, the Wichita Vet Center office and Winfield. The office list page (eastern and western regions, toll-free 800-513-7731) and the department's facility directory were also read in full.
- **Fort Dodge.** The Fort Dodge office page was not reached. Its address and phone (714 Sheridan, Unit 87, Fort Dodge; 620-253-0403) come from the KOVS facility directory, and its 17 counties from the Kansas Commission on Disability Concerns service map ("Region 2 – Fort Dodge"), both read in full. The record's evidence says so.
- **Itinerant schedules.** Where an office page lists a visit to a town in the county (for example, Hutchinson's office in Lyons on the first Tuesday), the county's card says when and where. Counties the page lists as "by appointment" say so. Colby's page pairs towns on the same Tuesday slot (Hoxie and Dighton, Scott City and Tribune, Goodland and St. Francis); those cards ask the reader to call to confirm the date.
- **Harvey County** is listed by two offices: Hutchinson (primary card) and the Wichita Vet Center office, shown under "Other offices". Both list a fourth-Tuesday visit to Newton.
- **Winfield.** The representative's position is vacant; the page asks callers to contact the eastern-region supervisor, Trevor Willemsen, at 620-218-7967, and lists the office cell, 620-218-6028. Butler, Chautauqua, Cowley, Elk and Sumner cards show both and say so.
- **Where pages disagree.** The office pages are newer than the Commission's service map: they place Dickinson and Marion with Junction City and Ellsworth with Hays, and list Overland Park at 913-371-5968. The edition follows the office pages.
- **Phones.** Hays (785-625-8532, 785-259-0364), Salina (785-823-2862, 785-559-0066) and Manhattan (785-587-0373, 785-477-0625) each list two staff lines; both are shown. Staff names, emails and fax numbers are omitted.

## Aging and ombudsman (`ks-regional-referrals.json`)

- **Area Agencies on Aging (11, `ks-aaa-*`).** From the Kansas Commission on Disability Concerns service-provider map, read in full (text updated August 12, 2025): name, office, phone, toll-free line and counties for all eleven agencies. Johnson County's phone, 913-715-8861, is the agency's information line from Johnson County's own page (search excerpt); the map prints 913-715-8800.
- **Statewide line (`ks-adrc`).** The Kansas Aging and Disability Resource Center, 855-200-2372, operated for KDADS by Liberty Healthcare since June 2025 (search excerpts).
- **Ombudsman (8 regions, `ks-omb-*`).** From the Kansas Office of the Long-Term Care Ombudsman's regional pages, read in full: Regions 1, 2, 3, 4, 4a, 5, 6 and 7, each with its counties. Region 5's position is open and Region 4's nursing-home position is open; those cards give the state office, 785-296-3017. Region 6’s page does not print Logan, Mitchell or Norton counties; the Commission’s service map places them in Region 6, and the record cites it.
- **Abuse reporting.** Kansas Protection Report Center (Adult Protective Services), 800-922-5330, 24 hours a day; KDADS complaint hotline for adult care homes, 800-842-0078.

## Other records (`ks-programs.json`)

- **Claims help (`ks-claims`).** KOVS field offices, above.
- **Medicare counseling (`ks-ship`).** Senior Health Insurance Counseling for Kansas (SHICK), 800-860-5260 (search excerpts).
- **Centers for Independent Living (8, `ks-cil-*`).** Counties and phones from the Commission's service-provider map, read in full; websites from the Kansas Department for Children and Families' list of the state's eight centers, read in full. Every county has one center. LINK, Inc.'s card links to the DCF list because only a non-secure (http) address for its own site appears in the sources.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ks-legal-programs`).** Kansas Legal Services: application line 800-723-6953, statewide client intake 316-267-3975, and the Elder Law Hotline for Kansans 60 and older, 888-353-5337 (search excerpts).
- **VA health care (`ks-vahealth-systems`).** VA Wichita (Robert J. Dole VA Medical Center, 316-685-2221; 59 Kansas counties), VA Eastern Kansas (Topeka 785-350-3111 or 800-574-8387, and Leavenworth) and VA Kansas City's Overland Park clinic (816-861-4700).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours: the field office pages give none.
- Veterans service organization representatives (American Legion, VFW, DAV and others) at the VA medical centers and the Wichita VA regional office, listed on a separate KOVS page.
- The Topeka Independent Living Resource Center, which national directories list for Shawnee County but the state's two current lists do not.
- Tribal veterans programs.
