# Alaska referral edition

Reviewed November 16, 2026. Alaska moves from a starter edition to a full edition covering all 30 boroughs and census areas. The edition is built from one research sheet, `data/source/states/ak.json`, by `scripts/make_county_state.py`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md).

## Localities

Alaska has no counties. The edition uses the 30 county equivalents the Census Bureau uses, with their full names as written:

- **Boroughs (15).** Including Anchorage Municipality and Skagway Municipality.
- **Cities and boroughs (4).** Juneau, Sitka, Wrangell and Yakutat.
- **Census areas (11).** The parts of the Unorganized Borough, including Chugach and Copper River (split from Valdez-Cordova in 2019) and Kusilvak (formerly Wade Hampton).

The guide shows these names without adding “County”. Report links name the locality type (“Borough:”, “Census area:”, “City and borough:”).

## Veterans contacts (`alaska-county-veterans-offices.json`)

Alaska has no county or borough veterans offices. The Office of Veterans Affairs works with four veterans organizations (Veterans of Foreign Wars, American Legion, Disabled American Veterans and Vietnam Veterans of America) to provide Veteran Service Officers.

- **Source.** The office’s [Veteran Service Officers page](https://veterans.alaska.gov/vso/), read in full. It lists officers by location with phones, but no street addresses.
- **Localities with a listed officer (8).** Anchorage, Mat-Su (Wasilla), Juneau, Fairbanks North Star, Kenai Peninsula (Soldotna), Kodiak Island, and Ketchikan Gateway and Prince of Wales-Hyder (both under the page’s “Craig / Ketchikan Gateway”). Each card shows the first listed officer, with the others as extra phones.
- **The other 22.** They show the Office of Veterans Affairs, 4600 DeBarr Rd, Suite 180, Anchorage: 907-334-0874 or 888-248-3682. The card names the service officer locations and the office’s list of Tribal Veteran Representatives.

## Aging and ombudsman (`ak-regional-referrals.json`)

- **Aging and Disability Resource Centers (6, `ak-adrc-*`).** From the Division of Senior and Disabilities Services [ADRC page](https://health.alaska.gov/dsds/pages/adrc/default.aspx), read in full. The statewide number is 1-855-565-2017.
  - Anchorage: Municipality of Anchorage, 907-343-7770.
  - Mat-Su: LINKS Resource Center, Wasilla, 907-373-3632.
  - Kenai Peninsula, Kodiak Island and Valdez-Cordova: Independent Living Center, Soldotna, 907-262-6333. Valdez-Cordova is shown as Chugach and Copper River.
  - Southeast Alaska: SAIL, 800-478-7245. The page says “Southeast Alaska”; the edition assigns its ten boroughs and census areas.
  - Interior and North Slope: ADRC North at the Fairbanks Senior Center, 907-452-2551.
  - Western Alaska: Bristol Bay Native Association, 800-478-4139 or 907-842-4139.
- **Ombudsman (`ak-omb-state`).** The Office of the Long Term Care Ombudsman is statewide: 907-334-4480 or 800-730-6393 (search excerpts of the program brochure and the Alaska Commission on Aging site).
- **Abuse reporting.** Adult Protective Services, 1-800-478-9996 in Alaska or 907-269-3666, with an online report form (search excerpts of Department of Health pages).

## Other records (`ak-programs.json`)

- **Claims help (`ak-claims`).** The Office of Veterans Affairs, above.
- **Medicare counseling (`ak-ship`).** The Medicare Information Office, 1-800-478-6065 in Alaska or 907-269-3680; the Anchorage office is by appointment (search excerpts).
- **Centers for Independent Living (4, `ak-cil-*`).** From the [ILRU directory](https://www.ilru.org/cil-directory/ak), read in full. The directory uses older names, mapped to today’s:
  - Access Alaska: Anchorage, Mat-Su, the Interior, the North Slope and most of the west and the Aleutians.
  - Arctic Access: Nome and Northwest Arctic.
  - Independent Living Center: Kenai Peninsula, Kodiak Island, Chugach and Copper River.
  - SAIL: all of Southeast.
- **Housing help (SSVF).** Added by the edition builder from VA’s FY26 intake workbook. The workbook uses older census area names; the builder maps them (Valdez-Cordova to Chugach and Copper River, Wrangell-Petersburg to Wrangell and Petersburg, Skagway-Hoonah-Angoon to Skagway and Hoonah-Angoon, Wade Hampton to Kusilvak, Prince of Wales-Outer Ketchikan to Prince of Wales-Hyder).
- **Legal aid (`ak-legal-programs`).** Alaska Legal Services Corporation’s Elder Law Project, for Alaskans 60 and older without regard to income; intake 1-888-478-2572 or online (search excerpts).
- **VA health care (`ak-vahealth-systems`).** The VA Alaska Healthcare System, Anchorage VA Medical Center at 1201 North Muldoon Road, 888-353-7574 (search excerpt).

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Not covered:

- Street addresses for Veteran Service Officers. The state lists phones only; call before visiting.
- Tribal Veteran Representatives by community. The office keeps that list as a separate document.
