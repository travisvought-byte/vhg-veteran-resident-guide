# Nebraska referral edition

Reviewed November 16, 2026. Nebraska moves from a starter edition to a full edition covering all 93 counties. The edition is built from one research sheet, `data/source/states/ne.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`nebraska-county-veterans-offices.json`)

Every Nebraska county has a county veterans service officer (CVSO), appointed by the county under state law and certified by the Nebraska Department of Veterans' Affairs (NDVA).

- **Source.** NDVA's [County Veterans Service Office Listing](https://veterans.nebraska.gov/sites/default/files/CVSODirectory.pdf), the PDF linked from its [CVSO page](https://veterans.nebraska.gov/cvso), read in full. The listing says it was updated October 1, 2024; the edition says so in its phone note.
- **What each card shows.** The office phone, the office location with the mailing address where they differ, and the hours as printed. Officers' names, emails, fax numbers, websites and home phone numbers are omitted.
- **Shared officers.** Some officers serve two to four counties (for example, Hall with Howard, Nance and Sherman; Arthur, Keith and Garden; Logan, McPherson and Thomas). Each county shows the listing printed for it, which may be the neighboring county's office, and says which other counties the officer serves.
- **Cell phones.** Where the listing gives only the officer's cell (Arthur, Keith and Garden; Garfield; Hooker; Sioux), the card shows it and says so. For Hayes, the listing asks callers to use the cell, which is shown first. Garfield's and Boyd's home phones are omitted.
- **Red Willow** prints no phone; it shares the McCook office with Furnas County, so the card shows Furnas's number and says why.
- **Lincoln County**'s listing gives extension 4268; the county's own page gives 4267. The card shows the main number and the directory's extension.
- **State Service Office.** NDVA's State Service Office in Lincoln (402-420-4021) also files claims; it is on the statewide claims card.

## Aging and ombudsman (`ne-regional-referrals.json`)

- **Area Agencies on Aging (8, `ne-aaa-*`).** Counties from the Nebraska Judicial Branch's Office of Public Guardian list, read in full. That list omits Thomas County; DHHS's Area Agencies on Aging directory map places it with West Central Nebraska, and the record cites the map. Phones and offices come from the DHHS State Unit on Aging page, read in full; the two lists give different street addresses for several agencies, and the edition follows DHHS.
- **Statewide line (`ne-adrc`).** The Aging and Disability Resource Center, 844-843-6364 (DHHS page, search excerpt).
- **Ombudsman (`ne-omb-state`, `ne-ombudsman`).** The state's contact map (MAP-93, Rev. 10/2026), read in full, names regional ombudsmen for six regions, but its county boundaries are drawn on the map and are not in its text. Every county therefore shows the state office, 402-802-5541, which connects callers to the regional ombudsman.
- **Abuse reporting.** 800-652-1999, for children and vulnerable adults (DHHS State Unit on Aging page).

## Other records (`ne-programs.json`)

- **Claims help (`ne-claims`).** County veterans service officers, above, and NDVA's State Service Office.
- **Medicare counseling (`ne-ship`).** Nebraska SHIP, part of the Department of Insurance, 800-234-7119 (search excerpts).
- **Centers for Independent Living (4, `ne-cil-*`).** From the ILRU directory, read in full: Independence Rising (50 central and western counties; Grand Island office, with the others listed) and the League of Human Dignity's Lincoln, Norfolk and Omaha centers. Every county has one center. ILRU writes some county names loosely ("Box Bute", "Duel", "Morril", "Scottsbluff"); the edition uses the correct names.
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`ne-legal-programs`).** Legal Aid of Nebraska's AccessLine, 877-250-2016, and Elder AccessLine for people 60 and older, 800-527-7249 (NDVA resource listings and ENOA, search excerpts).
- **VA health care (`ne-vahealth-systems`).** VA Nebraska-Western Iowa (Omaha, 402-346-8800); in the Panhandle, VA Black Hills runs the Scottsbluff clinic and Cheyenne VA the Sidney clinic.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Phone or hour changes since the directory's October 2024 update.
- Regional ombudsman assignments by county (the state office routes callers).
- Tribal veterans service offices; NDVA's site lists a "County & Tribal" directory, but the PDF lists none.
