# New Hampshire referral edition

Reviewed November 16, 2026. New Hampshire moves from a starter edition to a full edition covering all 10 counties. The edition is built from one research sheet, `data/source/states/nh.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`new-hampshire-county-veterans-offices.json`)

New Hampshire has no county veterans service officers. The NH Division of Veterans Services' officers are state employees who work from one office in Manchester and meet veterans by appointment at visitation sites.

- **Source.** The Division's [VSOs and Sites](https://dmavs.nh.gov/veterans-services/vsos-and-sites) page, read in full: the Manchester office (603-624-9230; 800-622-9230 toll-free in New Hampshire) and eleven visitation sites, all booked through the Division's line.
- **What each card shows.** The Division's line and office, with the county's visitation sites listed under "other offices". The page names each site by town; the cards place them by county (the "Berlin" site is the Vet Center in Gorham, Coos County; Hooksett is in Merrimack County).
- **Statewide cards.** Belknap and Strafford have no visitation site, and Sullivan's (Claremont) is temporarily on hold; those cards say so.

## Aging and ombudsman (`nh-regional-referrals.json`)

- **Aging and Disability Resource Centers (10, `nh-adrc-*`).** The county centers, formerly ServiceLink, from New Hampshire Family Voices' [list](https://nhfv.org/?p=31156), read in full. The Carroll, Cheshire and Manchester numbers match the Department of Health and Human Services' own location pages. Grafton (Littleton and Lebanon), Hillsborough (Manchester and Nashua) and Rockingham (Stratham and Atkinson) have two offices; each card shows both. The statewide line is 866-634-9412.
- **Ombudsman (`nh-omb-state`, `nh-ombudsman`).** The Office of the Long-Term Care Ombudsman, 800-442-5640 or 603-271-4375, statewide.
- **Abuse reporting.** Adult Protective Services at the Bureau of Elderly and Adult Services, 800-949-0470 or 603-271-7014, 8 a.m. to 4:30 p.m. weekdays; reports about a nursing or assisted living facility go to the ombudsman; after hours, 911 or local police ([DHHS](https://www.dhhs.nh.gov/report-concern/adult-abuse), read in full).

## Other records (`nh-programs.json`)

- **Claims help (`nh-claims`).** The Division of Veterans Services, above.
- **Medicare counseling (`nh-ship`).** NH SHIP, through the Aging and Disability Resource Centers, 866-634-9412 (CMS contact directory, read in full).
- **Center for Independent Living (`nh-cil-gsil`).** Granite State Independent Living, the state's one center, statewide, from the [ILRU directory](https://www.ilru.org/cil-directory/nh), read in full.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`nh-legal-programs`).** 603 Legal Aid (603-224-3333) and New Hampshire Legal Assistance's Senior Citizens Law Project (888-353-9944), from search excerpts.
- **VA health care (`nh-vahealth-systems`).** VA Manchester (603-624-4366) and VA White River Junction (802-295-9363), which serves four New Hampshire counties and has clinics in Keene and Littleton; search excerpts.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Town welfare officers and municipal veterans contacts.
- Which four counties VA White River Junction serves; the card points to VA's locator.
