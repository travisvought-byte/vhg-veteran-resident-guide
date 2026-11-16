# Rhode Island referral edition

Reviewed November 16, 2026. Rhode Island moves from a starter edition to a full edition covering all five counties. The edition is built from one research sheet, `data/source/states/ri.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`rhode-island-county-veterans-offices.json`)

Rhode Island has no county veterans service officers. The Rhode Island Office of Veterans Services (RIVETS) runs one statewide Veterans Resource Center.

- **Sources.**
  - The RIVETS [About Us](https://vets.ri.gov/about-us) page, read in full: services, eligibility and the resource center at 560 Jefferson Boulevard, Warwick. It lists no phone or hours.
  - The phone, 401-921-2119, comes from the office's [2021 statement](https://vets.ri.gov/press-releases/rivets-statement-services-and-supports-vets-military-families) (search excerpt).
  - The suite number comes from the Division of Motor Vehicles' [veteran contacts](https://dmv.ri.gov/node/881) (search excerpt).
- **Offices by county.** All five counties show the Warwick center, with a note that it is the state's one veterans office. The office records are labeled search excerpt because the phone was not read on a full page.

## Aging and ombudsman (`ri-regional-referrals.json`)

- **Aging (`ri-point-state`).** The Point, Rhode Island's Aging and Disability Resource Center, 401-462-4444, answered 24/7 ([Office of Healthy Aging page](https://www.oha.ri.gov/point), read in full). TTY 401-462-4445 or 2-1-1. The Office of Healthy Aging also has six regional Point offices, but each serves a group of towns rather than a county, so every county shows the statewide line. The edition calls it the Aging and Disability Resource Center rather than an Area Agency on Aging.
- **Ombudsman (`ri-omb-state`, `ri-ombudsman`).** The Office of the Rhode Island State Long Term Care Ombudsman, 401-785-3340 or toll-free 888-351-0808, statewide ([Office of Healthy Aging page](https://oha.ri.gov/what-we-do/protect/ltco), read in full).
- **Abuse reporting.** The Office of Healthy Aging's Adult Protective Services, 401-462-0555, takes reports any time for people 60 and older, and reports can be anonymous (search excerpts of Office of Healthy Aging pages).

## Other records (`ri-programs.json`)

- **Claims help (`ri-claims`).** RIVETS, above.
- **Medicare counseling (`ri-ship`).** Rhode Island SHIP, 1-888-884-8721, with its partner agencies listed ([Office of Healthy Aging Medicare page](https://oha.ri.gov/Medicare), read in full).
- **Centers for Independent Living (1, `ri-cil-oscil`).** Ocean State Center for Independent Living. The [ILRU directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/RI), read in full, lists two offices: Warwick (Kent County) and Pawtucket (Providence County). No center lists Bristol, Newport or Washington counties.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ri-legal-programs`).** The Office of Healthy Aging's [legal assistance page](https://oha.ri.gov/what-we-do/connect/legal-assistance), read in full, lists two programs for people 60 and older:
  - Rhode Island Legal Services: free help for lower-income adults with public-assistance problems. Phone 401-274-2652 or 800-662-5034, from its Help RI Law site (search excerpt).
  - The Rhode Island Bar Association: sliding-scale fees.
- **VA health care (`ri-vahealth-systems`).** VA Providence Healthcare System, 401-273-7100, and the Warwick Vet Center (search excerpts).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- The six regional Point offices and the towns each serves; town-level routing is not in the county model.
- RIVETS hours; no current official page lists them.
- A Center for Independent Living for Bristol, Newport and Washington counties; the ILRU directory lists none.
