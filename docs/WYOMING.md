# Wyoming referral edition

Reviewed November 16, 2026. Wyoming moves from a starter edition to a full edition covering all 23 counties. The edition is built from one research sheet, `data/source/states/wy.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`wyoming-county-veterans-offices.json`)

Wyoming has no county veterans offices. The Wyoming Veterans Commission's veterans service officers cover the state.

- **Sources.**
  - The Commission's [site](https://wyomingveteranscommission.com/), read in full: office at 5800 Central Ave., Cheyenne; mailing address 5410 Bishop Blvd., Cheyenne, WY 82009; main number 800-833-5987. It does not list service officers by county.
  - The Department of Health's [veterans resources page](https://health.wyo.gov/aging/veteranshome/veterans-resources/) (search excerpt) says to call the Wyoming Veterans Hotline, 1-800-833-5987, to meet with a service officer.
- **Offices by county.** Every county shows that statewide line as a statewide card.
- **Not used.** County-by-county service officer maps posted by a veterans organization date from 2020 and are not official.

## Aging and ombudsman (`wy-regional-referrals.json`)

- **Senior centers (23, `wy-aging-*`).** The Department of Health's Aging Division funds senior centers in each county, and people apply for services through the senior center.
  - Source: the division's [services-by-county page](https://health.wyo.gov/aging/communityliving/service-area-maps/), read in full; updated October 20, 2026.
  - Each card leads with the senior center in the county seat. In Big Horn County, which has no center in the seat, it leads with the center offering the most programs.
  - Each card lists the county's other providers: more senior centers, meals on wheels, transit, Wyoming Home Services and caregiver support. Foster Grandparent and Senior Companion volunteer programs are left out.
  - The edition calls these "senior center" rather than Area Agency on Aging.
- **Crook County.** The services-by-county page lists Goshen County's providers under Crook County. Crook therefore shows the Aging Division's statewide line, 1-800-442-2766, with a note.
- **Ombudsman (3, `wy-omb-*`).** Regional offices in Riverton, Casper and Cheyenne, each with its counties.
  - Source: the [Long-Term Care Ombudsman page](https://health.wyo.gov/aging/long-term-care-ombudsman/), read in full; updated April 17, 2026.
  - The State Long-Term Care Ombudsman's number is 307-287-7757.
- **Abuse reporting.**
  - The Department of Family Services says to report to your local DFS office, where an on-call caseworker is available 24 hours a day, or to law enforcement.
  - The Judicial Branch lists Adult Protective Services at 307-777-3602.
  - Both sources are search excerpts.

## Other records (`wy-programs.json`)

- **Claims help (`wy-claims`).** The Veterans Commission, above.
- **Medicare counseling (`wy-ship`).** The Wyoming State Health Insurance Information Program (WSHIIP), 1-800-856-4398 (search excerpts).
- **Centers for Independent Living (2, `wy-cil-*`).** From the [ILRU directory](https://ilru.org/projects/cil-net/cil-center-and-association-directory-results/WY), read in full:
  - Wyoming Independent Living (Casper, Cheyenne, Laramie and Sheridan) for the 13 eastern counties.
  - Wyoming Services for Independent Living (Cody, Lander and Rock Springs) for the 10 western counties.
  - The directory spells Uinta County "Unita"; the edition uses Uinta.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`wy-legal-programs`).** Legal Aid of Wyoming. Its offices in Cheyenne, Casper, Gillette and Lander are on the Aging Division's services-by-county page as supportive services providers.
- **VA health care (`wy-vahealth-systems`).** The Cheyenne VA Medical Center (307-778-7550) and the Sheridan VA Medical Center (307-672-3473), from search excerpts.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Which state veterans service officer covers each county. Call the statewide line.
- Crook County senior services, until the state's page is corrected.
- One discrepancy for Campbell County: a search excerpt of the services-by-county page showed a Newcastle address beside the Campbell County Senior Center. The full read gives Gillette and 307-686-0804, which the card uses.
