# Nevada referral edition

Reviewed November 16, 2026. Nevada moves from a starter edition to a full edition covering all 17 counties (Carson City is an independent city). The edition is built from one research sheet, `data/source/states/nv.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`nevada-county-veterans-offices.json`)

Nevada's veterans service officers work for the **Nevada Department of Veterans Services (NDVS)**, not for counties.

- **Source.** NDVS's [Veterans Service Officers](https://veterans.nv.gov/benefits-and-services/veterans-service-officers) page, read in full (last modified July 7, 2026). It lists offices in North Las Vegas (at the VA Medical Center), Mesquite (in the Vet Center), Pahrump, Reno, Fallon, Elko and Winnemucca, and says intake appointments are taking about 30 to 90 days to schedule.
- **Counties with an office.** Clark (North Las Vegas, with Mesquite under "Other offices"), Washoe (Reno), Churchill (Fallon), Elko, Humboldt (Winnemucca) and Nye (Pahrump).
- **Esmeralda.** Nye County's [veterans services page](https://nyecountynv.gov/209) says the Pahrump office serves Nye and Esmeralda counties, so Esmeralda shows Pahrump and the card says why.
- **No office.** NDVS lists no office in Carson City, Douglas, Eureka, Lander, Lincoln, Lyon, Mineral, Pershing, Storey or White Pine, and publishes no county assignments. Those ten counties show the department's statewide card (`office_type: "statewide"`, badge "Nevada statewide line (no local office)") with the VSO lines 775-321-4880 (the number the page lists for its Reno, Fallon, Elko and Winnemucca offices) and 702-224-6025 (Las Vegas), and Ask a VSO. No county is assigned to an office the department does not name.
- **Phones.** The page lists two numbers for Elko (775-321-4880, 775-777-1000) and Winnemucca (775-321-4880, 775-399-2300); both are shown. The state veterans homes' service officers are not listed as county offices.

## Aging and ombudsman (`nv-regional-referrals.json`)

- **Nevada Care Connection Resource Centers (3, `nv-nvcc-*`).** Nevada has no Area Agencies on Aging. Each county shows its Nevada Care Connection Resource Center from an October 2, 2024 presentation to the Washoe County Senior Services Advisory Board, read in full: Access to Healthcare Network (877-861-1893; 12 northern counties), Lyon County Human Services (775-577-5009; Lyon) and Jewish Family Service Agency (702-732-0304; Clark, Esmeralda, Lincoln, Nye). The presentation also lists Access to Healthcare Network for Lyon; Lyon's card shows Lyon County Human Services and notes the other.
- **Statewide line (`nv-adrc`).** Dial 2-1-1 and ask for Nevada Care Connection (ADSD brochure, search excerpt).
- **Ombudsman (`nv-omb-state`, `nv-ombudsman`).** The Long Term Care Ombudsman Program is statewide; helpline 888-282-1155.
- **Abuse reporting.** Adult Protective Services: 702-486-6930 in Las Vegas and Clark County, 888-729-0571 elsewhere.

## Other records (`nv-programs.json`)

- **Claims help (`nv-claims`).** NDVS veterans service officers, above.
- **Medicare counseling (`nv-ship`).** The Medicare Assistance Program, 800-307-4444, from the same October 2024 presentation.
- **Centers for Independent Living (2, `nv-cil-*`).** From the ILRU directory (search excerpts): Northern Nevada CIL (Sparks; every county except Clark) and Southern Nevada CIL (Las Vegas and North Las Vegas; Clark). Every county has a center.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`nv-legal-programs`).** From the State Bar of Nevada's 2025 Legal Resources Directory, read in full: Nevada Legal Services' Senior Legal Helpline (877-693-2163; all counties), Legal Aid Center of Southern Nevada (702-386-1070; Clark), Volunteer Attorneys for Rural Nevadans (866-448-8276; rural counties) and the State Bar's lawyer referral line (800-789-5747).
- **VA health care (`nv-vahealth-systems`).** VA Southern Nevada (702-791-9000) and VA Sierra Nevada (775-786-7200); northeastern Nevada is served by VA Salt Lake City's clinics.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours: the NDVS page gives none.
- NDVS's rural outreach (ROVER) visit schedule; the published schedules found were years old.
- Tribal veterans programs.
