# Minnesota referral edition

Reviewed November 15, 2026. Minnesota moves from a starter edition to a full edition covering all 87 counties. The edition is built from one research sheet, `data/source/states/mn.json`, by `scripts/make_county_state.py MN`; the sheet names the page behind every contact.

## Veterans contacts (`minnesota-county-veterans-offices.json`)

Every Minnesota county has a County Veterans Service Officer (CVSO). The Minnesota Department of Veterans Affairs (MDVA) points veterans to them, and the Minnesota Association of County Veterans Service Officers publishes the county directory.

- **Source.** The association's [Find a CVSO](https://www.macvso.org/find-a-cvso.html) directory. The page is a county menu and could not be fetched whole, so each county's page was read as a search excerpt and every office record is labeled search-excerpt evidence.
- **What is shown.** Phone, hours where printed and a street address. Staff names and emails were left out. Where the association's page showed no street address, the address comes from the Minnesota Attorney General's veterans handbook ([chapter 6](https://www.ag.state.mn.us/consumer/Handbooks/VetHnbk/CH6.asp)), which prints no date; the card's note says so for each of those counties.
- **Nobles and Stevens.** The association's pages were not among those read, so phone and address both come from the handbook, no hours are shown, and the cards say so.
- **Several offices.** St. Louis (Duluth, Hibbing, Ely, Virginia), Stearns (Waite Park, Melrose) and Otter Tail (Fergus Falls, New York Mills) list their other offices. The Ely address is from the handbook and the Virginia address from the National Association of County Veterans Service Officers; the state handbook prints an older Virginia address and phone.
- **Conflicts shown in notes.** Beltrami's staff page prints "Minnesota Ave." where the handbook prints "America Avenue NW"; Isanti's staff pages print two Cambridge addresses. The notes tell readers to confirm when they call.
- **Part-time and appointment offices.** Lake of the Woods is part time; Red Lake is by appointment; Kittson, Lincoln, Mahnomen, Pope, Roseau and Wadena print partial weeks. Hours are shown as printed.
- **Statewide line.** MDVA's 1-888-LinkVet (888-546-5838), seven days a week, with the St. Paul (612-970-5662) and Fargo (701-451-4640, northwest Minnesota) claims offices, from MDVA's pages (search excerpts).

## Aging and ombudsman (`mn-regional-referrals.json`)

- **Area Agencies on Aging (6, `mn-aaa-*`).** Arrowhead (Duluth), Central Minnesota Council on Aging (St. Cloud), Dancing Sky (Warren), Metropolitan, which does business as Trellis (Minneapolis), Minnesota River (Mankato) and Southeastern Minnesota (Rochester). Each of the 87 counties has exactly one. The Board on Aging's [area agencies page](https://mn.gov/board-on-aging/about-us/area-agencies/) supplies names, cities, phones and counties; the Metropolitan agency's phone comes from the state's Aging and Disability Resources directory because the excerpt of the board page garbled it. Search-excerpt level.
- **Tribal agency.** The Minnesota Indian Area Agency on Aging serves the state's tribal nations rather than counties and is not shown on county cards.
- **Statewide line (`mn-adrc`, `mn-ship`).** Minnesota Aging Pathways (formerly the Senior LinkAge Line), 800-333-2433, is the aging and disability resource line and the State Health Insurance Assistance Program.
- **Ombudsman (`mn-omb-ooltc`, `mn-ombudsman`).** The Office of Ombudsman for Long-Term Care publishes one statewide line, 800-657-3591 (651-431-2555 in the metro), answered 8:00 a.m.–4:00 p.m. weekdays and routed regionally. It does not publish a county table, so every county shows the statewide line. It serves nursing home, boarding care, assisted living, customized living, foster care and home care recipients. Search-excerpt level.
- **Abuse reporting.** The Minnesota Adult Abuse Reporting Center, 844-880-1574, 24 hours a day, from the Department of Human Services' adult protection pages.

## Other records (`mn-programs.json`)

- **Claims help (`mn-claims`).** MDVA and the county offices, above.
- **Centers for Independent Living (8, `mn-cil-*`).** Access North, Freedom Resource Center, Independent Lifestyles, the Metropolitan Center for Independent Living, Options Interstate, SMILES, Southeastern Minnesota (SEMCIL) and Southwestern (SWCIL). Addresses, phones and counties come from the ILRU Minnesota [directory](https://www.ilru.org/cil-directory/mn), read in full. That page lists several centers twice with different county lists and mistypes some county names (for example "Tasca"); the rows were reconciled to the eight centers. No center's county list names **Big Stone, Chippewa, Lac qui Parle, Renville or Swift**, so those counties show no independent living center.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`mn-legal-programs`).** The Minnesota Assistance Council for Veterans' Vetlaw program, 651-200-4750, and LawHelpMN. Vetlaw attorneys advise on Minnesota law only. Search-excerpt level.
- **VA health care (`mn-vahealth-systems`).** Minneapolis VA Health Care System (612-725-2000) and St. Cloud VA Health Care System (320-252-1670 or 800-247-1739). No counties are assigned. Search-excerpt level.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- A county table for the ombudsman or county-level adult protection numbers.
- Tribal Veterans Service Officers and the Minnesota Indian Area Agency on Aging, which are not on county cards.
- Independent living centers for five counties (above).
- Dates for the association's directory and the Attorney General's handbook; neither prints one.
- A full read of each county's page: phone and hours came from search excerpts.
