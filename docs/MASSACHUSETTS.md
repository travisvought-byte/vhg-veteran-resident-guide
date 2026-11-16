# Massachusetts referral edition

Reviewed November 16, 2026. Massachusetts moves from a starter edition to a full edition covering its 14 counties. The edition is built from one research sheet, `data/source/states/ma.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Why every county card points to local offices

Massachusetts law puts a Veterans Service Officer in each of its 351 cities and towns, and aging services are organized by city and town. So no single office serves a county. Each county card gives the state's route to the resident's local office and lists what is truly statewide or county-level.

## Veterans contacts (`massachusetts-county-veterans-offices.json`)

- **What every county card shows.**
  - The Executive Office of Veterans Services: 617-210-5480, toll-free 888-844-2838, weekdays 8:45 a.m. to 5 p.m.
  - How to find the local VSO: the state's Find Your Local VSO search, the town hall, or that line.
- **Sources.**
  - The [Local Veterans' Service Officers page](https://www.mass.gov/info-details/local-veterans-service-officers), read in full.
  - The Find Your Local VSO page and the office locations page, both search excerpts.
- **Chapter 115.** Benefits are applied for through the local VSO. The card and the claims record say so.

## Aging and ombudsman (`ma-regional-referrals.json`)

- **Aging help (`ma-massoptions`).** MassOptions, 1-800-243-4636, connects callers to the Aging Services Access Point and Area Agency on Aging for their city or town (Executive Office of Aging & Independence pages, search excerpts). Every county shows it.
- **Ombudsman (`ma-omb-state`).** The Long-Term Care Ombudsman Program, 617-222-7495, connects callers to the local program for the facility's city or town (search excerpt).
- **Abuse reporting.** The Elder Abuse Hotline, 800-922-2275, 24 hours a day (search excerpt).

## Other records (`ma-programs.json`)

- **Claims help (`ma-claims`).** Local VSOs and the Executive Office of Veterans Services, above.
- **Medicare counseling (`ma-ship`).** SHINE, 800-243-4636 (search excerpt).
- **Centers for Independent Living (11, `ma-cil-*`).** From the [ILRU Massachusetts directory](https://www.ilru.org/cil-directory/ma), read in full.
  - Every county has at least one center, and several have more.
  - ILRU's "Briston" for MetroWest is read as Bristol.
  - The Multi-Cultural ILC of Boston lists neighborhoods, which are mapped to Suffolk and Norfolk.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ma-legal-programs`).** The Massachusetts Senior Legal Helpline, 800-342-5297, for residents 60 and older (search excerpts).
- **VA health care (`ma-vahealth-systems`).** VA Boston (800-865-3384), Bedford (781-687-2000) and Central Western Massachusetts (413-584-4040) (search excerpts). The record notes that some southeastern communities are closer to Providence.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Each city and town's own Veterans Service Officer. There are 351, and the state's search tool is the current source.
- Each city and town's Aging Services Access Point. MassOptions refers callers to theirs.
