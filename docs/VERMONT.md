# Vermont referral edition

Reviewed November 16, 2026. Vermont moves from a starter edition to a full edition covering all 14 counties. The edition is built from one research sheet, `data/source/states/vt.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Veterans contacts (`vermont-county-veterans-offices.json`)

Vermont has no county veterans service officers. The Vermont Office of Veterans Affairs has Veteran Service Officers in Montpelier who serve the whole state.

- **Source.** The Office of Veterans Affairs [contact page](https://veterans.vermont.gov/node/83), read in full: address, main line (802-828-3379), toll-free line within Vermont (888-666-9844), and hours (weekdays 7:30 a.m. to 4 p.m.).
- **Offices by county.** Every county shows the Montpelier office. Washington County's card notes that the office is in that county.
- **Other service officers.** The same page lists certified Veteran Service Officers from the American Legion (802-296-5166), VFW (802-296-5168) and DAV (802-296-5167). It says they help any veteran, and membership is not required. Every card names them.

## Aging and ombudsman (`vt-regional-referrals.json`)

- **Area Agencies on Aging (5, `vt-aaa-*`).** Sources:
  - The state's Older Americans Act snapshot with its [Area Agency on Aging map](https://asd.vermont.gov/sites/asd/files/documents/Older%20American%20Act%202023%20Snapshot%20with%20AAA%20Map.pdf), read in full. It is dated February 15, 2019, though its title refers to 2023 data.
  - The Department for Children and Families' [Area Agencies on Aging page](https://dcf.vermont.gov/contacts/partners/aaa), read in full, which gives the same service areas.
  - Agencies by county:
    - Age Well: Addison, Chittenden, Franklin and Grand Isle.
    - Southwestern Vermont Council on Aging: Bennington and Rutland.
    - Northeast Kingdom Council on Aging: Caledonia, Essex and Orleans.
    - Central Vermont Council on Aging: Lamoille, Orange and Washington.
    - Senior Solutions: Windham and Windsor.
- **Towns across county lines.** Some towns are served by a neighboring county's agency. Each card names the exceptions in its county:
  - Granville and Hancock (Addison), Pittsfield (Rutland), and Bethel, Rochester, Royalton, Sharon and Stockbridge (Windsor) go to Central Vermont.
  - Readsboro, Searsburg and Winhall (Bennington) and Thetford (Orange) go to Senior Solutions.
  - The statewide Senior HelpLine, 1-800-642-5119, reaches every agency.
- **Ombudsman (`vt-omb-state`, `vt-ombudsman`).** The Vermont Long-Term Care Ombudsman Project at Vermont Legal Aid, 1-800-889-2047 ext. 3, statewide ([project page](https://vtlegalaid.org/legal-projects/long-term-care-ombudsman), read in full). The extension is printed in the card text, not in the phone link.
- **Abuse reporting.** Adult Protective Services, 1-800-564-1612. The Attorney General's Elder Protection Initiative also says to call local or state police (search excerpt).

## Other records (`vt-programs.json`)

- **Claims help (`vt-claims`).** The Office of Veterans Affairs and the three veterans organizations' service officers, above.
- **Medicare counseling (`vt-ship`).** Vermont SHIP through the Area Agencies on Aging. Call the Senior HelpLine, 1-800-642-5119 (search excerpts).
- **Centers for Independent Living (1, `vt-cil-vcil`).** The Vermont Center for Independent Living. Its main office is in Montpelier, with offices in Burlington, Morrisville, Bennington, Brattleboro, Newport and Rutland, and it serves all 14 counties ([ILRU directory](https://www.ilru.org/projects/cil-net/cil-center-and-association-directory-results/VT), read in full).
- **Housing help (SSVF).** Added by the edition builder from VA's FY26 intake workbook.
- **Legal aid (`vt-legal-programs`).** Vermont Legal Aid's Elder Law Project, for Vermonters 60 and older, through the statewide helpline, 1-800-889-2047 (search excerpts).
- **VA health care (`vt-vahealth-systems`).** The White River Junction VA Medical Center, 802-295-9363 or 866-687-8387 (search excerpts).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Street addresses for the Area Agencies on Aging. The state snapshot is from 2019, so the cards give phones and the statewide HelpLine only.
- Where the American Legion, VFW and DAV service officers work; the state page gives their phones only.
