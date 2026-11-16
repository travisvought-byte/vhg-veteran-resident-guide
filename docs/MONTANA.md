# Montana referral edition

Reviewed November 16, 2026. Montana moves from a starter edition to a full edition covering all 56 counties. The edition is built from one research sheet, `data/source/states/mt.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`montana-county-veterans-offices.json`)

Montana has no county veterans offices. The Montana Veterans Affairs Division (MVAD) has nine Veteran Service Offices: Belgrade, Billings, Butte, Great Falls, Havre, Helena, Kalispell, Miles City and Missoula.

- **Sources.**
  - Phones come from the division's [Veteran Services page](https://veterans.mt.gov/Veteran-Services/Veteran-Services-Program-Home), read in full.
  - Street addresses come from its [office contact sheet](https://dma.mt.gov/MVAD/MVAD-Documents/MVAD-Office-Contacts.pdf), read in full.
  - Butte's hours come from its [office page](https://dma.mt.gov/MVAD/Butte-Service-Office).
- **Offices by county.** No current official page says which counties each office serves.
  - The nine counties that hold an office show it: Gallatin, Yellowstone, Silver Bow, Cascade, Hill, Lewis and Clark, Flathead, Custer and Missoula.
  - The other 47 counties show the division's statewide line, 406-324-3742, with all nine office phones.
  - A 2015 legislative handout assigned counties to offices but is too old to use.
- **Address notes.**
  - Great Falls: another MVAD contact sheet gives a different street address, and the card says so.
  - Helena: the contact sheet does not clearly label its address, so the card says to call.

## Aging and ombudsman (`mt-regional-referrals.json`)

- **Area Agencies on Aging (9, `mt-aaa-*`).** From the DPHHS [ADRC page](https://www.dphhs.mt.gov/SLTC/aging/adrc), read in full, which gives counties and phones. Phones and addresses were checked against the [Area Agency on Aging contact list](https://prod-dphhs.mt.gov/assets/sltc/AAA/AAAContacts.pdf) (updated August 2026). The statewide line, 1-800-551-3191, rings the local agency.
- **Area III.** The ADRC page does not list Area III. Its eight counties are the ones no other agency lists: Blaine, Chouteau, Glacier, Hill, Liberty, Pondera, Teton and Toole. The state ombudsman directory from February 2024 grouped the same eight, with Cascade, as its Area III region. The card says this.
- **Ombudsman (4, `mt-omb-*`).** From the [ombudsman directory](https://dphhs.mt.gov/assets/sltc/Ombudsman/OmbudsmanDirectory.pdf), read in full (updated August 2026):
  - Regional ombudsmen cover Area I (Glendive), Area II (Edgar), and Areas IV and V (Butte).
  - The directory names no regional ombudsman for the other 16 counties, so they show the State Long-Term Care Ombudsman, 406-444-3285.
- **Abuse reporting.** Adult Protective Services, 1-844-277-9300, weekdays 8 a.m. to 5 p.m., with online reports any time at aps.mt.gov (search excerpts of DPHHS pages).

## Other records (`mt-programs.json`)

- **Claims help (`mt-claims`).** MVAD, above.
- **Medicare counseling (`mt-ship`).** Montana SHIP through the Area Agencies on Aging, 1-800-551-3191 (search excerpt).
- **Centers for Independent Living (4, `mt-cil-*`).** Each county maps to one center:
  - LIFTT: 18 counties in the south and east.
  - Ability Montana: 14 southwest and central counties.
  - North Central Independent Living Services: 17 counties along the Highline and in central Montana.
  - Summit Independent Living Center: 7 northwest counties.
  - Phones and most counties come from the [ILRU directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/MT), read in full. ILRU lists North Central only for Cascade and Valley; its 17-county area comes from the DPHHS Community Connections Directory (search excerpt).
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`mt-legal-programs`).**
  - The Montana Legal Services Association HelpLine, 1-800-666-6899, Tuesday to Thursday, 9 a.m. to 1 p.m.
  - The Office on Aging's Legal Services Developer, 800-332-2272.
  - Both are search excerpts.
- **VA health care (`mt-vahealth-systems`).** The VA Montana Health Care System at Fort Harrison, 406-442-6410 or 877-468-8387 (search excerpt).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Which MVAD office serves each county without one, and the outreach schedule. Both change; call the division.
- A regional ombudsman for Areas III, VI, VII, VIII and IX, until the state directory lists one.
