# Idaho referral edition

Reviewed November 16, 2026. Idaho moves from a starter edition to a full edition covering all 44 counties. The edition is built from one research sheet, `data/source/states/id.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`idaho-county-veterans-offices.json`)

Idaho's accredited state service officers work for the Idaho Division of Veterans Services' Office of Veterans Advocacy in seven offices. The division publishes no county assignments.

- **Source.** The division's [Office of Veterans Advocacy](https://veterans.idaho.gov/advocacy/) page (last updated May 7, 2026), read in full: the seven offices with addresses and phones, office hours (Monday to Friday, 8 a.m. to 4:30 p.m.; messages 24 hours a day) and the Central Support Office, 208-780-1300. The [Service Officers](https://veterans.idaho.gov/advocacy/service-officers/) page (last updated May 15, 2026), also read in full, lists officers by office.
- **Counties with an office (7).** Ada (Boise main office), Canyon (Caldwell), Elmore (Mountain Home), Twin Falls, Bannock (Pocatello), Nez Perce (Lewiston) and Kootenai (Post Falls) show their office.
- **Two offices with a second number.** The page prints 208-559-8315 for Mountain Home but its dialing link calls 208-580-2001, and the Service Officers page gives the Boise line, 208-780-1380. The page prints 208-244-3873 for Pocatello but links 208-782-3800. Each card shows the printed number first and the others under "Also".
- **The other 37 counties** show the division's statewide card: no state office in the county, the Central Support Office and Boise lines, and a pointer to the county courthouse. Bingham County's [veterans page](https://web.binghamid.gov/clerk/veterans.html) says most Idaho counties have a county veterans service officer; there is no current statewide list of them, so they are not on the cards.

## Aging and ombudsman (`id-regional-referrals.json`)

- **Area Agencies on Aging (6, `id-aaa-*`).** From the Idaho Commission on Aging's [Contact Us](https://aging.idaho.gov/contact) page (last updated July 20, 2026), read in full: each agency's counties and its local and toll-free phones.
- **Statewide line (`id-adrc`).** The Idaho Commission on Aging, 877-471-2777, and 2-1-1.
- **Ombudsman (6, `id-omb-*`).** The Commission's [ombudsman page](https://aging.idaho.gov/ombudsman-program/) (last updated October 20, 2026) says local ombudsmen work at the Area Agencies on Aging, so each county shows its agency's phone. The National Consumer Voice's Idaho list, read in full, adds a direct line for Area 4 (208-933-2397) and an extension for Area 5 (804). The state ombudsman line is the Commission's, 877-471-2777.
- **Abuse reporting.** The Commission's [Adult Protective Services](https://aging.idaho.gov/adult-protective-services/) page says to report to the local Area Agency on Aging. Cards show the Commission's line, 877-471-2777, and point to the agency above.

## Other records (`id-programs.json`)

- **Claims help (`id-claims`).** The Office of Veterans Advocacy, above.
- **Medicare counseling (`id-ship`).** SHIBA, the Idaho Department of Insurance's Medicare counseling program, 800-247-4422 ([page](https://doi.idaho.gov/SHIBA) read in full; last updated September 25, 2026).
- **Centers for Independent Living (10, `id-cil-*`).** Disability Action Center NW (Moscow, Post Falls, Lewiston), LINC (Boise, Caldwell, Twin Falls) and LIFE (Pocatello, Blackfoot, Burley, Idaho Falls). Counties served come from the [ILRU directory](https://www.ilru.org/cil-directory/id), read in full; every county is listed by at least one office, and a county listed by a main office and a satellite shows both. Current addresses come from the Idaho State Independent Living Council's [centers page](https://silc.idaho.gov/idaho-centers-for-independent-living/) (last updated September 28, 2026), which names towns rather than counties. The council page prints Caldwell's ZIP code as 83705 (a Boise code); the card uses the directory's address, 703 S. Kimball Avenue, Caldwell, ID 83607.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`id-legal-programs`).** Idaho Legal Aid Services' [Legal Advice Line](https://idaholegalaid.org/Legal-Advice-Line) page, read in full: 208-746-7541, phone intake Monday to Wednesday, 10 a.m. to 1:30 p.m. Mountain Time, for people 60 and older and for public benefits questions.
- **VA health care (`id-vahealth-systems`).** VA Boise (Boise VA Medical Center, 208-422-1000), VA Spokane (northern Idaho), VA Walla Walla (Lewiston VA Clinic) and VA Salt Lake City (clinics including Pocatello), from va.gov search excerpts.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- County veterans service officers. Several counties have one (Bonner and Bingham, for example), but the division's pages do not list them and the most recent statewide list found is the division's 2021 resource directory.
- Which Office of Veterans Advocacy office serves each county; the division does not say.
- VA Spokane, Walla Walla and Salt Lake City phone numbers; the card points to VA's locator.
