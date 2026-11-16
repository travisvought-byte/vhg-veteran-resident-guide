# Iowa referral edition

Reviewed November 16, 2026. Iowa moves from a starter edition to a full edition covering all 99 counties. The edition is built from one research sheet, `data/source/states/ia.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`iowa-county-veterans-offices.json`)

Every Iowa county has a county commission of veteran affairs with an accredited County Veteran Service Officer. The Iowa Department of Veterans Affairs publishes a page for each office, listed on its [locations map](https://dva.iowa.gov/find-veteran-services).

- **Source.** All 99 office pages, each read in full. Each card links to its own page.
- **What the card shows.** The office address and phone as printed. The pages list no hours, so cards say to call ahead. Officers' names and emails are left out.
- **Page errors handled.**
  - The Allamakee and Boone pages name the wrong county under "Areas Served"; each office is shown for its own county.
  - Wapello's page misspells Ottumwa; the town name is corrected.
- **Notes on cards.**
  - Adair and Adams list the same phone number, and both cards say so.
  - Winnebago's page prints the same street address as the Webster County office in Fort Dodge, so its card says to call before visiting.
  - The Dickinson and Pocahontas extensions and Taylor's after-hours number are on their cards.

## Aging and ombudsman (`ia-regional-referrals.json`)

- **Area Agencies on Aging (6, `ia-aaa-*`).** County lists, toll-free phones and offices come from the state's [SFY 2025 Area Plan synopsis](https://hhs.iowa.gov/media/13553/download), prepared for the Iowa Commission on Aging meeting of June 10, 2025 and read in full.
  - Elderbridge: 29 northern and western counties.
  - Northeast Iowa: 18 counties.
  - Aging Resources of Central Iowa: 8 counties.
  - Heritage: 7 counties around Cedar Rapids and Iowa City.
  - Milestones: 17 southeastern counties.
  - Connections: 20 southwestern and western counties. The synopsis prints "ADS" in this list; Ida County is the one county otherwise unassigned, and the card says so.

  LifeLong Links, 866-468-7887, connects callers to the right agency (Iowa Attorney General and HHS pages, search excerpts).
- **Ombudsman (`ia-omb-state`).** The Office of the State Long-Term Care Ombudsman, 866-236-1430. The same number reaches local ombudsmen. The source is the [HHS ombudsman page](https://hhs.iowa.gov/health-prevention/aging-services/ltcombudsman), read in full (updated September 30, 2026). Local ombudsmen appear only on a map image, so every county shows the toll-free line.
- **Abuse reporting.** The Iowa HHS dependent adult abuse hotline, 800-362-2178, 24 hours a day. Abuse in a licensed facility goes to the Department of Inspections, Appeals and Licensing, 877-686-0027 (search excerpts).

## Other records (`ia-programs.json`)

- **Claims help (`ia-claims`).** County Veteran Service Officers, and the department at 515-252-4698 or 800-838-4692 (Iowa Administrative Code, search excerpt).
- **Medicare counseling (`ia-ship`).** SHIIP, 800-351-4664 (CMS directory, search excerpt).
- **Centers for Independent Living (5, `ia-cil-*`).** From the [ILRU Iowa directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/IA), read in full.
  - The five centers cover 29 counties.
  - The directory lists no center for the other 70 counties, so those cards show none.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ia-legal-programs`).** The Legal Hotline for Older Iowans, 800-992-8161, and Iowa Legal Aid, 800-532-1503 (search excerpts).
- **VA health care (`ia-vahealth-systems`).** VA Central Iowa (Des Moines) and Iowa City VA health care systems (search excerpts). The record notes that some western counties are closer to the VA systems in Omaha and Sioux Falls.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours. The department's pages list none.
- Centers for Independent Living for 70 counties. The national directory lists none for them.
