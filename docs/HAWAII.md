# Hawaii referral edition

Reviewed November 16, 2026. Hawaii moves from a starter edition to a full edition covering all five counties. The edition is built from one research sheet, `data/source/states/hi.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`hawaii-county-veterans-offices.json`)

Hawaii has no county veterans service officers. The State Office of Veterans' Services (OVS), part of the Hawaii Department of Defense, has veterans services counselors on each main island.

- **Source.** The OVS [contact page](https://dod.hawaii.gov/ovs/contact/), read in full: each office's address, phone, hours and walk-in or appointment rules. Staff names and emails are omitted.
- **Offices by county.** Honolulu: Tripler Army Medical Center (walk-ins Monday and Wednesday mornings), with the Kapolei office at the Daniel K. Akaka VA Clinic (walk-ins Thursday mornings) under "other offices". Hawaii: Hilo, with Kailua-Kona (Kealakekua) under "other offices". Kauai: Lihue. Maui: Kahului, which the page lists for Maui, Moloka‘i and Lāna‘i.
- **Kalawao County** (Kalaupapa, on Moloka‘i) shows the Maui office and says why.

## Aging and ombudsman (`hi-regional-referrals.json`)

- **Area Agencies on Aging (4, `hi-aaa-*`).** From the Executive Office on Aging's [Aging Network](https://health.hawaii.gov/eoa/?p=88) page, read in full: Elderly Affairs Division (Honolulu), Hawai‘i County Office of Aging (with its Kona line), Maui County Office on Aging and Kaua‘i Agency on Elderly Affairs. Kalawao is shown with Maui. The Maui agency's Moloka‘i and Lāna‘i lines come from the Kaua‘i agency's contact page (search excerpt). The statewide Aging and Disability Resource Center line is 808-643-2372.
- **Ombudsman (`hi-omb-state`, `hi-ombudsman`).** The Long-Term Care Ombudsman Program, 808-586-7268, statewide (search excerpt of the Executive Office on Aging home page).
- **Abuse reporting.** Adult Protective Services, 808-832-5115 statewide, 7:45 a.m. to 4:30 p.m. weekdays, with messages after hours ([June 2026 brochure](https://humanservices.hawaii.gov/ssd/files/2026/06/APS-Brochure-6-2026-FINAL-FORMATTED.pdf), read in full).

## Other records (`hi-programs.json`)

- **Claims help (`hi-claims`).** The Office of Veterans' Services, above.
- **Medicare counseling (`hi-ship`).** Hawai‘i SHIP, 808-586-7299 or 888-875-9229 (search excerpt).
- **Centers for Independent Living (2, `hi-cil-*`).** Access to Independence (Honolulu) and Aloha Independent Living Hawaii (Hawaii, Honolulu, Kauai and Maui counties), from the [ILRU directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/HI), read in full. No center lists Kalawao.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`hi-legal-programs`).** Legal Aid Society of Hawai‘i's Senior Legal Hotline (808-536-0011; neighbor islands 888-536-0011) and general intake (search excerpt of its flyer).
- **VA health care (`hi-vahealth-systems`).** VA Pacific Islands Health Care System, 808-433-0600 or 800-214-1306 (search excerpt).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- OVS outreach days on Moloka‘i and Lāna‘i; the contact page gives none.
- Island-by-island Adult Protective Services lines; the current brochure gives one statewide number.
