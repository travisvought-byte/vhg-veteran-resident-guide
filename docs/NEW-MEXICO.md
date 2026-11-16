# New Mexico referral edition

Reviewed November 16, 2026. New Mexico moves from a starter edition to a full edition covering all 33 counties. The edition is built from one research sheet, `data/source/states/nm.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`new-mexico-county-veterans-offices.json`)

New Mexico has no county veterans offices. Veteran service officers of the **New Mexico Department of Veterans' Services (NMDVS)** work from state field offices.

- **Source.** NMDVS's [Field Offices](https://www.nmdvs.org/?p=3991) page, read in full (undated). It lists 17 offices (Gallup, Grants, Farmington, Bernalillo, Las Vegas, Santa Fe, Taos, three Albuquerque offices, Belen, Clovis, Hobbs, Roswell, Las Cruces, Alamogordo and Silver City), each with its address, phones and the counties it serves.
- **Counties listed by several offices.** Many counties appear under two to four offices (for example, Catron under Gallup, Grants, Albuquerque and Belen; Eddy under Clovis, Hobbs and Roswell). Each county shows one office, the one in or nearest the county, and lists the others under "Other offices", so no listing is dropped.
- **Torrance County** is not listed by any office. Its card shows the department's toll-free line, 866-433-8387 (State Benefits page), and the Albuquerque line, 505-383-2400 (July 2025 agency summary), both search excerpts, and says why (`office_type: "statewide"`).
- **Printed details.** The page gives the Las Cruces office's ZIP code as "8801" and no ZIP for Silver City; the cards leave those ZIP codes out. The Gallup address is printed "J908 E. Buena Vista Ave."; the card shows 908. The Albuquerque Indian School Road office lists six staff lines; the card shows three. Staff names and emails are omitted.

## Aging and ombudsman (`nm-regional-referrals.json`)

- **Area Agencies on Aging (2, `nm-aaa-*`).** The Governor's Commission on Disability's resources page (search excerpt) says the Non-Metro Area Agency on Aging funds senior programs in every county except Bernalillo, which the City of Albuquerque/Bernalillo County Area Agency on Aging serves. Albuquerque's card uses the Department of Senior Affairs' information line, 505-764-6400, which the city's Area Agency on Aging page names for requesting services. The Non-Metro card notes the Indian and Navajo Area Agencies on Aging for tribal elders.
- **Statewide line (`nm-adrc`).** The Aging and Disability Resource Center, 800-432-2080.
- **Ombudsman (`nm-omb-state`, `nm-ombudsman`).** One statewide line, 866-451-2901 (ALTSD contact page, search excerpt).
- **Abuse reporting.** Adult Protective Services statewide intake, 866-654-3219, 24 hours a day.

## Other records (`nm-programs.json`)

- **Claims help (`nm-claims`).** NMDVS field offices, above; toll-free 866-433-8387.
- **Medicare counseling (`nm-ship`).** SHIP counselors through the ADRC line, 800-432-2080.
- **Centers for Independent Living (5, `nm-cil-*`).** Counties from the New Mexico SILC's list of the five centers (on the Independent Living Resource Center's site) and the 2025–2027 State Plan for Independent Living, both search excerpts: Choices (Chaves, Eddy, Lea), Independent Living Resource Center (ten central counties), New Vistas (nine northern counties), San Juan Center for Independence (McKinley, San Juan) and The Ability Center (Doña Ana, Grant, Luna, Sierra). The State Plan says Catron, Curry, Hidalgo, Quay and Roosevelt have no center; those counties show none. Three cards link to the ILRU directory because no secure (https) address for the center's own site was found.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook. The workbook spells "Dona Ana"; the builder now matches it to the edition's "Doña Ana".
- **Legal aid (`nm-legal-programs`).** The Legal Resources for the Elderly Program (55 and older, no income limits; 800-876-6657), New Mexico Legal Aid's statewide intake (833-545-4357) and the Senior Citizens' Law Office in the Albuquerque area (505-265-2300).
- **VA health care (`nm-vahealth-systems`).** VA New Mexico (Albuquerque, 505-265-1711); the Las Cruces clinic is VA El Paso's, the Clovis clinic VA Amarillo's and the Hobbs clinic VA West Texas's.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Office hours: the field offices page gives none.
- The department's mobile outreach vehicle and tribal veteran service officers.
- The ILRU directory page for New Mexico, which was not read in full for this edition.
