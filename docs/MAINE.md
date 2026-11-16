# Maine referral edition

Reviewed November 16, 2026. Maine moves from a starter edition to a full edition covering all 16 counties. The edition is built from one research sheet, `data/source/states/me.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`maine-county-veterans-offices.json`)

Maine has no county veterans service officers. The Maine Bureau of Veterans' Services (MBVS) has eight field offices, and each office's own page names the counties it serves.

- **Sources.** The Bureau's [locations page](https://www.maine.gov/veterans/veterans-services-offices/locations) for addresses and phones, and the Augusta, Bangor, Caribou, Lewiston, Machias, Portland and Togus office pages for service areas, hours and itinerant visits (all read in full; Springvale's service area is on the locations page; Caribou's, Aroostook, from a search excerpt of its page).
- **Offices by county.** Lewiston: Androscoggin, Franklin, Oxford and Sagadahoc. Caribou: Aroostook. Portland: Cumberland. Machias: Hancock and Washington. Augusta: Kennebec and Somerset. Togus: Lincoln (and Kennebec, listed under "other offices"). Bangor: Penobscot and Piscataquis. Springvale: York.
- **Knox and Waldo** are not named by any office page; their cards show the Bureau's central line, 207-287-7020, and say so.
- **Itinerant visits.** Ellsworth (Hancock), Lincoln and Newport (Penobscot) and Dover-Foxcroft (Piscataquis) are listed under "other offices". The Lewiston office's visits in Farmington, South Paris and Rumford are temporarily suspended; the Franklin and Oxford cards say so.
- **Two disagreements.** The locations page gives Augusta 207-287-9933 (also the Togus number); the Augusta page gives 207-287-7020, which the card uses. The locations page gives Machias 53 Prescott Drive; the Machias page gives 7 Court Street. The card shows the first and names the second.

## Aging and ombudsman (`me-regional-referrals.json`)

- **Area Agencies on Aging (5, `me-aaa-*`).** From the Office of Aging and Disability Services' [Area Agencies on Aging](https://mobile.maine.gov/dhhs/oads/get-support/older-adults-disabilities/area-agencies-on-aging) page, read in full. The agencies are also Maine's Aging and Disability Resource Centers; the statewide line is 877-353-3771. Cumberland County is Southern Maine Agency on Aging's except Brunswick and Harpswell (Spectrum Generations); the card says so.
- **Ombudsman (`me-omb-state`, `me-ombudsman`).** The Maine Long-Term Care Ombudsman Program, 800-499-0229, statewide (Attorney General's [Older Mainers](https://www.maine.gov/ag/consumer-protection/consumer-help-topics/older-mainers) page, read in full).
- **Abuse reporting.** Adult Protective Services, 800-624-8404, 24 hours a day.

## Other records (`me-programs.json`)

- **Claims help (`me-claims`).** The Bureau's field offices, above.
- **Medicare counseling (`me-ship`).** Maine SHIP through the Area Agencies on Aging, 877-353-3771 (search excerpts).
- **Center for Independent Living (`me-cil-alpha-one`).** Alpha One, Maine's one center, statewide (800-640-7200), from the Bureau of Rehabilitation Services resource guide (search excerpt).
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`me-legal-programs`).** Legal Services for Maine Elders, 800-750-5353, for people 60 and older; the Volunteer Lawyers Project for others.
- **VA health care (`me-vahealth-systems`).** VA Maine Healthcare System, 207-623-8411 (search excerpt).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Town general assistance and municipal veterans contacts.
- The Bureau's mobile veterans service officers; their pages give no phone numbers.
