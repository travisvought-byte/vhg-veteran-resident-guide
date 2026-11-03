# Veteran housing providers (SSVF) by county

Source: VA's FY26 SSVF provider intake list (Contacts worksheet), downloaded from the [VA SSVF page](https://department.va.gov/homeless/supportive-services-for-veteran-families/). The file is [SSVF_Provider_Intake_List_FY26.xlsx](https://department.va.gov/homeless/wp-content/uploads/sites/72/2026/03/SSVF_Provider_Intake_List_FY26.xlsx), SHA-256 `311e6c32…d462`. It is the same file Ohio's housing map uses ([OHIO-HOUSING.md](OHIO-HOUSING.md)). The maintainer supplied it on 2026-11-02 because the build server cannot download from department.va.gov.

`data/public/ssvf-intake-fy26.json` keeps a compact copy: all 235 grant rows with their organizations, grant numbers, counties served and intake phones. Intake emails and comments are left out because some name staff.

## How records are made

- **Full editions:** each grant row becomes a county-limited `<st>-ssvf-<grant>` card in the housing view, listing the counties the row names in that state.
  - Multistate grants get one card per state.
  - Grants with no intake phone route through VA's National Call Center for Homeless Veterans (877-424-3838).
  - Ohio keeps its existing hand-checked records.
- **Starter editions:** `scripts/make_starter_states.py` adds one statewide-area card per grantee. The card description lists the counties served, because starter editions have no county selector.
- **Status:** every record is `official_source_reviewed` with method `full_official_spreadsheet`, and cites its worksheet row and the file hash.
- **Florida:**
  - The 14 earlier search-excerpt cards are replaced by the 11 FY26 workbook grants, which cover all 67 counties.
  - Two newer FY 2027 grantees not in the FY26 list (Hearts & Homes for Veterans and Housing for Homeless) keep their search-excerpt cards.
- **Name matching:** two defunct Virginia independent cities in the workbook are mapped to the counties that absorbed them: Bedford city → Bedford, Clifton Forge city → Alleghany. The workbook's Texas "La Salle" matches the guide's "LaSalle".

## Coverage in full editions

| State | Grants | Counties with a provider card | Counties without one |
|---|---|---|---|
| California | 29 | 55 of 58 | Alpine, Inyo, Mono |
| Florida | 11 | 67 of 67 | — |
| Indiana | 9 | 67 of 92 | Bartholomew, Brown, Crawford, Daviess, Decatur, Dubois, Greene, Harrison, Henry, Jackson, Jefferson, Jennings, Knox, Lawrence, Martin, Monroe, Orange, Owen, Perry, Pike, Ripley, Rush, Scott, Spencer, Washington |
| Kentucky | 4 | 120 of 120 | — |
| Michigan | 9 | 83 of 83 | — |
| New York | 14 | 62 of 62 | — |
| North Carolina | 6 | 91 of 100 | Camden, Chowan, Currituck, Dare, Gates, Hyde, Pasquotank, Perquimans, Tyrrell |
| Pennsylvania | 9 | 67 of 67 | — |
| Texas | 10 | 203 of 254 | Anderson, Andrews, Archer, Baylor, Borden, Brewster, Burleson, Cherokee, Clay, Cooke, Coryell, Cottle, Crane, Crockett, Culberson, Dawson, Delta, Ector, Foard, Gaines, Glasscock, Grimes, Hardeman, Hopkins, Hudspeth, Irion, Jeff Davis, Kaufman, Leon, Loving, Madison, Martin, Midland, Milam, Pecos, Presidio, Rains, Reagan, Reeves, Robertson, Rockwall, Somervell, Sterling, Terrell, Upton, Van Zandt, Walker, Ward, Wilbarger, Winkler, Young |
| Utah | 2 | 29 of 29 | — |
| Virginia | 9 | 104 of 133 | Amelia, Bath, Bland, Brunswick, Buckingham, Carroll, Charlotte, Galax City, Grayson, Greensville, Halifax, Highland, Lancaster, Lunenburg, Madison, Mathews, Mecklenburg, Middlesex, Northumberland, Nottoway, Orange, Patrick, Prince Edward, Prince George, Richmond, Smyth, Waynesboro City, Westmoreland, Wythe |
| West Virginia | 4 | 55 of 55 | — |

Counties without a card keep the national VA housing line and 211. The FY26 list is a snapshot: confirm current funding and openings when calling, and replace it with the next VA list when one is published.
