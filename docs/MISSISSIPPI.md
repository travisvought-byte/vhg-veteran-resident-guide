# Mississippi referral edition

Reviewed November 16, 2026. Mississippi moves from a starter edition to a full edition covering all 82 counties. The edition is built from one research sheet, `data/source/states/ms.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`mississippi-county-veterans-offices.json`)

Every Mississippi county has a county veterans service officer, certified each year by the Mississippi State Veterans Affairs Board (Miss. Code § 35-3-21).

- **Source.** Mississippi Veterans Affairs' [Service Officers](https://www.msva.ms.gov/serviceofficers) page, read in full. It lists all 82 county offices with address and phone, and the department's Veterans Benefits Specialist offices.
- **What each card shows.** The office phone and address, with the mailing address where different. Officers' names and emails are omitted.
- **Several locations.** Chickasaw (Houston and Okolona), Jefferson Davis (Prentiss and Bassfield), Lamar (Purvis, Hattiesburg's Oak Grove Senior Center and Sumrall), Monroe (Aberdeen and Amory), Neshoba (Philadelphia and the Mississippi Band of Choctaw Indians in Choctaw), Tallahatchie (Glendora and Charleston) and Wilkinson (Woodville and Centreville) show the first location and list the others. Carroll lists separate Carrollton and Vaiden numbers; both are shown.
- **No phone printed.** Sunflower (fax only), Walthall and Wilkinson list no office phone. Their cards show the county office's address with the department's main office number, 601-576-4850, and say so.
- **Humphreys County.** The page prints the ZIP code as "3903"; the card shows no ZIP code.

## Aging and ombudsman (`ms-regional-referrals.json`)

- **Area Agencies on Aging (10, `ms-aaa-*`).** From the contact page of the Mississippi Department of Human Services' State Plan on Aging (FFY 2023 update, approved September 27, 2022), read in full: each agency's phones and counties. The newer 2027–2030 plan refers to a map but prints no county lists. Central Mississippi's seven counties, including Copiah, are confirmed by its fiscal year 2027 request for proposals.
- **Statewide line (`ms-adrc`).** Mississippi Access to Care (MAC), 844-822-4622.
- **Ombudsman (`ms-omb-state`, `ms-ombudsman`).** The department's ombudsman page, read in full, gives one statewide help line, 888-844-0041, and no local numbers; every county shows it. The state's administrative code places the ten local programs in the ten Planning and Development Districts.
- **Abuse reporting.** Adult Protective Services, 844-437-6282, 24 hours a day.

## Other records (`ms-programs.json`)

- **Claims help (`ms-claims`).** County veterans service officers, above, and the department's main office.
- **Medicare counseling (`ms-ship`).** SHIP, 844-822-4622 (the same number as MAC).
- **Centers for Independent Living (6, `ms-cil-*`).** The six offices of LIFE of Mississippi from the ILRU directory, read in full. Calhoun, Choctaw, Union and Webster are not listed by any office, so those counties show none. The directory files the Indianola office as "Greenwood"; the card says so.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ms-legal-programs`).** The department's Legal Assistance Help Guide, read in full: Mississippi Center for Legal Services and North Mississippi Rural Legal Services, with 800-498-1804 listed for most offices.
- **VA health care (`ms-vahealth-systems`).** VA Jackson (G.V. (Sonny) Montgomery VA Medical Center, 601-362-4471, and seven clinics) and VA Gulf Coast (Biloxi, 228-523-5000).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours: the Service Officers page gives none.
- The department's Veterans Benefits Specialist offices are on the claims card, not assigned to counties; the page does not give their service areas.
- Which VA system serves the northernmost counties; the card points to VA's locator.
