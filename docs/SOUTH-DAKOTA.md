# South Dakota referral edition

Reviewed November 16, 2026. South Dakota moves from a starter edition to a full edition covering all 66 counties. The edition is built from one research sheet, `data/source/states/sd.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`south-dakota-county-veterans-offices.json`)

State law directs every county commission to employ a county veterans service officer, and tribes may appoint tribal veterans service officers.

- **Source.** The South Dakota Department of Veterans Affairs' [2026 Veterans Service Officers Directory](https://vetaffairs.sd.gov/veteransserviceofficers/VSO%20Publications/2026%20VSO%20Directory.pdf) (updated September 15, 2026), read in full and its phone list read a second time to check every number. It lists all 66 county offices with address, phone and hours, and eight tribal veterans service offices.
- **What each card shows.** The office phone, address and hours. Officers' names and emails are omitted. Many rural offices are open one or two days a week or a few days a month, so hours matter.
- **Shared officers.** Brule, Buffalo, Lyman and Jones share one officer; so do Davison, Hanson, Jerauld and Sanborn; Charles Mix and Douglas; Haakon and Jackson; and Hand and Hyde. Hughes, Stanley and Sully share the Pierre office, and Codington and Hamlin the Watertown office. Each card says so.
- **Vacancies.** The directory lists the officer position as vacant in Butte, Mellette and Potter; those cards say so and give the department's line, 605-773-3269.
- **McPherson.** The listed number is the officer's cell phone, by appointment; the card shows the Eureka office and the Leola courthouse.
- **Tribal offices.** Each tribal veterans service office is listed under "other offices" for the county it is in: Cheyenne River (Dewey, and Ziebach, which the reservation also covers), Crow Creek (Buffalo), Lower Brule (Lyman), Oglala Sioux (Oglala Lakota), Rosebud (Todd), Sisseton-Wahpeton (Roberts), Standing Rock (Corson; the office is in Fort Yates, North Dakota) and Yankton Sioux (Charles Mix).
- **Hours typos.** Faulk's Monday hours and Mellette's hours print "12:00a" and "1:00a"; the cards show them as afternoon hours.

## Aging and ombudsman (`sd-regional-referrals.json`)

- **No Area Agencies on Aging.** South Dakota's Division of Long Term Services and Supports performs that role, so every county shows **Dakota at Home**, the statewide Aging and Disability Resource Center, 833-663-9673 (press 1; 8 a.m. to 5 p.m. Central, Monday to Friday). Source: the [Dakota at Home listing](https://dakotaathome.sd.gov/search/84901553-f7f9-557c-a9a6-5c3d6640cc78) for the division, read in full (updated September 15, 2026).
- **Ombudsman (`sd-omb-state`, `sd-ombudsman`).** One statewide program; reports go to the same line during business hours.
- **Abuse reporting.** Dakota at Home during business hours; after hours, local law enforcement.

## Other records (`sd-programs.json`)

- **Claims help (`sd-claims`).** County and tribal veterans service officers, above; the department, 605-773-3269; and its state veterans service officers and claims office in Sioux Falls, 605-333-6869.
- **Medicare counseling (`sd-ship`).** SHIINE: eastern 800-536-8197, central 877-331-4834, western 877-286-9072 (Department of Social Services brochure; search excerpt).
- **Centers for Independent Living (12, `sd-cil-*`).** Nine Independent Living Choices offices and three Western Resources for Independent Living offices from the [ILRU directory](https://www.ilru.org/cil-directory/sd), read in full. The directory prints "Duel" for Deuel and "Fall River Jones" for two counties, and lists the Martin office for "Lakota, Oglala, Pine Ridge", shown as Oglala Lakota County. Charles Mix, Douglas and Gregory are not listed by any office, so those counties show none; the state's independent living plan says every county is covered, so ask the nearest office.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`sd-legal-programs`).** [SD Law Help's office list](https://sdlawhelp.org/node/9/our-offices), read in full: East River Legal Services for the 33 eastern counties, Dakota Plains Legal Services' seven offices for the western counties and tribal nations, and Access to Justice statewide.
- **VA health care (`sd-vahealth-systems`).** Sioux Falls VA Health Care System (605-336-3230) and VA Black Hills (Fort Meade 605-347-2511, Hot Springs 605-745-2000), from va.gov search excerpts.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- The Division of Long Term Services and Supports' local offices; the division routes everyone through Dakota at Home.
- Which VA system serves each county; the card points to VA's locator.
