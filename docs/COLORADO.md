# Colorado referral edition

Reviewed November 15, 2026. Colorado moves from a starter edition to a full edition covering all 64 counties. The edition is built from one research sheet, `data/source/states/co.json`, by `scripts/make_county_state.py CO`; the research sheet names the page behind every contact.

## Veterans contacts (`colorado-county-veterans-offices.json`)

Colorado counties run their own County Veterans Service Offices; the Colorado Division of Veterans Affairs publishes the list. Each county uses the office the list prints for it.

- **Source.** The Division's [County Veterans Service Offices](https://vets.colorado.gov/services/county-veterans-service-offices) page, all 64 counties. The page was read in full through a text-extraction tool that condenses it, so addresses, phones and hours are as the page prints them and staff emails were dropped by the tool. The page has no printed date.
- **Hours.** Printed hours are shown on each county card.
- **Shared offices.** A few service officers cover several counties; each county keeps its own card and the note names the others.
  - Logan, Phillips and Sedgwick (Christopher Kelley, 970-520-5876).
  - Morgan and Yuma (Brian Uhrich, 970-542-3552).
  - Grand and Summit (Duane Dailey).
  - Ouray and San Miguel (Mikael Madsen, Telluride).
  - Conejos and Saguache (Donald Romero).
  - Prowers and Baca (the Lamar office).
  - Cheyenne, Kiowa, Lincoln and Washington (Glen Marcinak, Ray Odum and Maria Secrest, 719-892-4800).
- **No office phone printed.** The list prints no main phone for Clear Creek, Huerfano, Jackson, Moffat or Washington. The card shows the service officers' numbers it does print, or the shared office number it names, and says so.
  - Clear Creek and Jackson: 720-651-0583 first, 303-914-5837 as "Also."
  - Huerfano: Ray Odum, 719-924-2280.
  - Moffat: the list shows the county officer position as vacant. The card shows the nearby Routt and Rio Blanco officers' numbers it names.
  - Washington: the shared 719-892-4800 office number the list prints for the same three officers in Cheyenne, Kiowa and Lincoln.
- **Dolores.** The officer position is listed as vacant and John Trocheck is also named; the card shows the office phone and says so.
- **Fixes to printed text.** "1247 Sante Fe" in Denver is shown as "1247 Santa Fe."
- **Left out.**
  - Staff emails.
  - Glen Marcinak's personal number. It is printed as 970-616-6661 in one place and 970-617-6661 in another.
  - The Bent County number, 719-468-6406, that the list also prints under Otero.
  - A stray "494" in Otero's courthouse address.
  - The Huerfano address's parenthetical about the nursing home.

## Aging and ombudsman (`co-regional-referrals.json`)

- **Area Agencies on Aging (16, `co-aaa-*`).** From the Disability Law Colorado list of [Colorado Area Agencies on Aging](https://www.disabilitylawco.org/sites/default/files/uploads/DLC%20website%209-9-21%20AAA%20Colored%20Map%20%20LIST%202%20PAGES%20PUBLIC%20website.pdf) (county groupings and main phones for Regions 1 through 14, including 2A, 2B, 3A and 3B).
  - **Date.** The list is dated September 9, 2021. County groupings agree with the 2023 state transition-contact list. Phones were not checked against newer agency pages, except Weld, whose own materials list 970-400-6950 for the same office as 970-346-6950; the note on the Weld card shows both.
  - **Statewide card.** Aging and Disability Resources for Colorado (ADRC), 844-265-2372, is a statewide card and the senior line.
- **Regional ombudsman programs (16, `co-omb-*`).** Colorado has 16 regional programs that match the 16 aging regions.
  - No separate regional ombudsman phones were read from official pages. Each card shows its Area Agency on Aging main line, says to ask for the ombudsman, and gives the state ombudsman, 303-862-3524, as the fallback.
  - The state publications are search excerpts, so these cards carry the "search excerpt" label.
- **Abuse reporting.** The Department of Human Services page directs callers to the Adult Protective Services intake number at the county department of human services where the adult lives, and gives no statewide number. The county panel therefore shows 911 for immediate danger and says to call the county intake line for other reports. Some county pages route adult reports to the statewide child-abuse hotline, 844-264-5437; this edition does not use that number as an adult-protection line.

## Other records (`co-programs.json`)

- **Claims help.** Carried over from the starter edition (reviewed November 2, 2026), 303-914-5832.
- **Housing help (SSVF).** Two programs, Rocky Mountain Human Services (855-838-7428, with 719-323-2600 as a second intake number) and Volunteers of America Colorado Branch (720-501-3367), from VA's FY26 intake workbook. Both list all 64 counties.
- **Centers for Independent Living (9, `co-cil-*`).** From the Division of Vocational Rehabilitation [Independent Living Services](https://dvr.colorado.gov/independent-living-services) page, with counties served and phones as listed.
  - The page spells Hinsdale "Hindsdale"; it is corrected.
  - Weld is shared by two centers.
  - Several counties have more than one center; Adams and Jefferson have two.
- **Legal aid.** One statewide card for Colorado Legal Services, with the main office number, 303-837-1313. No counties are assigned.
- **VA health care.** One statewide card for the VA Eastern Colorado Health Care System (Aurora) and the VA Western Colorado Health Care System (Grand Junction). No counties are assigned.
- **Medicare counseling (SHIP).** One statewide card, 888-696-7213.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not yet researched:

- Regional ombudsman direct numbers and names.
- Current phones for the Area Agencies on Aging (the list is from 2021).
- County Adult Protective Services intake numbers.
- Two sources could not be opened: the Health Care Policy and Financing transition-contact page and the coombudsman.org site. The state ombudsman's site is linked on its card but its content was not reviewed.
- Local home-modification programs and other counties' senior-center directories.
