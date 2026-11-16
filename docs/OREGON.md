# Oregon referral edition

Reviewed November 16, 2026. Oregon moves from a starter edition to a full edition covering all 36 counties. The edition is built from one research sheet, `data/source/states/or.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`oregon-county-veterans-offices.json`)

Every Oregon county has a **county veterans service office**; the Oregon Department of Veterans' Affairs (ODVA) trains and certifies the officers and publishes one page per county.

- **Source.** ODVA's [County Services Directory](https://www.oregon.gov/odva/Services/Pages/County-Services.aspx) and the 36 county pages it links to. 32 pages were read in full. Four were read through search excerpts (Wasco, Washington, Wheeler and Yamhill; direct reads stopped being available partway through), and Columbia's street address also comes from an excerpt because the fetched copy of its page left it out. Those five records carry `official_search_excerpt` as their review method.
- **What is shown.** Office address, phones and hours as printed. Officers' names, email addresses and fax numbers are left out.
- **Extra offices.** Curry (Gold Beach, Port Orford), Deschutes (La Pine, Redmond), Lake (Christmas Valley), Lane (Cottage Grove, Florence), Malheur (Vale), Multnomah (Portland VA Medical Center) and Umatilla (Hermiston, Milton-Freewater) list their other offices under "Other offices".
- **Phones from county pages.** Wheeler's phone comes from Wheeler County's veterans services page and Yamhill's phone and hours from Yamhill County's directory, because the ODVA excerpts did not include them; both cards say so.
- **Tribal veterans service officers.** Where a county page lists one with a phone, the card's note names it: Coquille (Coos), Cow Creek (Douglas), Warm Springs (Jefferson) and Grand Ronde (Polk).
- **Not shown.** Umatilla's Pendleton ZIP code, which the read did not settle; the card gives the street and city.

## Aging and ombudsman (`or-regional-referrals.json`)

- **Area Agencies on Aging (16, `or-aaa-*`).** Agencies and the counties each serves come from the Department of Human Services' [Area Agencies on Aging overview](https://www.oregon.gov/odhs/providers-partners/community-services-supports/Documents/aaa-overview.pdf) (June 9, 2026), read in full. The overview prints no phones, so each agency's phone is cited to a second page, mostly the agency's 2025–2029 area plan on oregon.gov or its own county or agency site, all read as search excerpts. Harney and Malheur numbers come from a 2018 state caregiver list. No current number for Columbia County's agency (Community Action Team) was found on an official page, so its card uses the statewide ADRC line.
- **Statewide lines (`or-adrc`, `or-ship`).** The Aging and Disability Resource Connection, 855-673-2372, and SHIBA Medicare counseling, 800-722-4134.
- **Ombudsman (`or-omb-state`, `or-ombudsman`).** The Office of the Long-Term Care Ombudsman is statewide (800-522-2602), so every county shows it.
- **Abuse reporting.** The Oregon SAFEline, 855-503-SAFE (7233), 24 hours a day.

## Other records (`or-programs.json`)

- **Claims help (`or-claims`).** County offices, above, and ODVA's line, 800-692-9666.
- **Centers for Independent Living (8, `or-cil-*`).** From the state's [CIL directory](https://www.oregon.gov/odhs/aging-disability-services/Documents/cil-directory.pdf) (marked 2024), read in full. **11 counties have no center**: Benton, Clatsop, Columbia, Coos, Curry, Lincoln, Linn, Marion, Polk, Tillamook and Yamhill. EOCIL's office in The Dalles is shown for Hood River, Sherman and Wasco; the state marks it as outside the funded service areas and the card says so. Six centers link to the state directory because no https website address for them appears in the sources read.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`or-legal-programs`).** The Oregon Public Benefits Hotline (800-520-5292, with its limited hours), senior legal help through the Area Agencies on Aging, and the Oregon State Bar's Military Assistance Panel and Lawyer Referral Service (503-684-3763 or 800-452-7636).
- **VA health care (`or-vahealth-systems`).** VA Portland (503-220-8262), Roseburg (541-440-1000) and the Southern Oregon Rehabilitation Center in White City (541-826-2111).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Local Adult Protective Services phones; the card gives the statewide SAFEline.
- Tribal veterans service officers for counties whose page read did not include a phone (Lane, Lincoln, Umatilla).
- A current official phone for Columbia County's Area Agency on Aging.
