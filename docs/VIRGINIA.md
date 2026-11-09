# Virginia coverage and evidence

Published referral edition, reviewed October 20, 2026. Virginia is the twelfth state: **95 counties and 38 independent cities**, bringing the guide to **1,108 counties and equivalents**. [Open Virginia](https://guide.vethomeguard.org/?state=VA) · [Sharing kit](https://guide.vethomeguard.org/share-va.html).

## What is included

- Veterans contact routing for all 133 localities, using 21 researched regional DVS office listings and explicitly labeled statewide referrals for Alexandria City and Falls Church City.
- 13 statewide Virginia programs, 25 aging agencies and 22 ombudsman regions, plus 33 shared federal/national resources: **93 resource records**.
- County/city selection, caregiver copy/print handoffs, seniors and disability support, CCC Plus home-accessibility screening, and the guided-assistance navigator.

Independent cities have their own `county_type` and remain separate from counties with the same names. Fairfax City, Franklin City, Richmond City and Roanoke City never inherit the surrounding county’s routing by name. Charles City and James City remain counties. Towns and former independent cities in agency directories are not added as extra county equivalents. Aging and ombudsman service maps are separate and each covers the 133 current localities exactly once.

## Sources and review

The [Virginia.gov local-government directory](https://www.virginia.gov/local-government/) establishes the locality roster. Full [DARS aging](https://dars.virginia.gov/aging/home-community/find-local-aaa/) and [ombudsman directories](https://dars.virginia.gov/aging/ombudsman/find-your-local-ombudsman/) establish local contacts and boundaries. All 13 statewide program records have full official-source review. Current [DVS claims](https://vvs.dvs.virginia.gov/Services/DisabilityClaims-Services) and [care-center pages](https://vvs.dvs.virginia.gov/Services/CareCenters-Services) provide application navigation and the statewide DVS referral phone. The [CCC Plus page](https://www.dmas.virginia.gov/for-members/benefits-and-services/waivers/ccc-plus-waiver/) distinguishes local LTSS screening from Medicaid financial eligibility and directs managed-care members to their MCO care coordinator for adaptations.

Legacy DVS office pages denied automated access. Regional county assignments remain labeled as official search text; three owner-provided official-page screenshot spot-checks corroborate visible fields rather than establishing full-page review:

| Office | Result |
|---|---|
| Fairfax | Service area matches; screenshot phone **703-805-0177** replaces **703-359-1210** from older indexed text. Both values remain visible as a source difference. |
| Quantico | **571-697-5915 ext. 75915** and the service area match. Base access requirements remain excerpt-supported. |
| Tazewell | **276-988-3761** and Buchanan, Dickenson, Russell and Tazewell county assignments match. |

These three checks complete the owner-selected sample. Other office records are not represented as owner-checked. No agency was called or emailed; no form was submitted. The complete source inventory, source conflicts and checker output are retained in `research/returns/R-06-VA/notes.md`.

## Routing details and limits

- Twenty-one localities retain nonexclusive alternative veterans-office assignments. The ambiguous Salem/Roanoke reference to Buchanan is excluded as a Buchanan County alternative; Tazewell’s explicit county assignment is retained.
- Loudoun’s legacy office notices conflict about availability. Its proposed first contact is Fairfax, whose service area explicitly includes Loudoun. The statewide DVS line is available if routing fails.
- The Central Virginia ombudsman listing explicitly directs callers to **804-565-1600**, so the five mapped localities use that labeled state-office route rather than implying the agency general line is a staffed local ombudsman.
- Encompass’s ombudsman extension **3416** is preserved. Phone links preserve Quantico’s extension using a separate `;ext=` parameter.
- Ask installation offices about visitor access and remote help before traveling. A published number or screenshot does not confirm current staffing, intake or appointments.
- Three statewide directory/local-intake records deliberately have no single phone: aging directory, VICAP and caregiver support. Use the selected locality’s aging agency.
- Legacy care-center application downloads returned access-denied errors in this environment. Current program instructions include official assistance-request links and a clearly labeled statewide phone fallback.
- Local providers, equipment stock, available funding, bed openings, costs and individual eligibility are not comprehensively confirmed.

Virginia’s `va-` state program IDs are distinct from shared federal VA records. The assistance matcher uses record state and audience information so nonveterans can receive Virginia aging, Medicaid and disability routes while veteran-only federal programs remain restricted to appropriate beneficiaries.

## Independent living, legal aid and VA health care (2026-11-04)

20 records were added to `data/public/va-programs.json`. There are now 89 Virginia-specific resource records and 122 public resources in total.

- **Centers for Independent Living (17 records, `va-cil-*`).** Taken from the ILRU national directory for Virginia, with full page text reviewed. Branch listings are folded into their center's record, with the branch phones in the next step. The exception is Resources for Independent Living's Petersburg satellite, which has its own locality list and gets its own record. The centers cover 92 of 133 localities.
- **Normalizing the directory's locality names:**
  - "Bristol" and "Galax City" (Appalachian Independence Center) are mapped to the independent cities.
  - "Franklin" means Franklin County for DRRC (Rocky Mount) and Franklin City for Endependence Center (Norfolk).
  - ECNV's loosely worded list is read as Arlington, Fairfax County, Fairfax City, Falls Church, Loudoun and Alexandria.
- **Directory entries handled specially:**
  - LACIL lists no service area, so its card covers only Lynchburg City.
  - The Peninsula CIL entry lists only "Elizabeth City," which is not a current Virginia locality, so it was left out.
  - The directory notes that Independence Empowerment Center offers phone services only, and its card says to call first.
- **Legal aid (2 statewide records).**
  - 1-866-LEGLAID (866-534-5243) connects callers with Virginia's nine regional legal aid programs.
  - The Statewide Senior Legal Helpline (844-802-5910) serves people 60 and older.
  - Both come from DARS and VaLegalAid.org. Regional programs were not mapped to localities because no complete official county list was available.
- **VA health care (`va-vahealth-systems`).** One statewide card for the Hampton, Richmond and Salem medical centers. It also notes that some Virginia clinics belong to systems in Mountain Home TN, Martinsburg WV and Washington DC. No localities are assigned.

`tests/virginia.cjs` now expects 89 Virginia records. A check that a city and the county with the same name get different centers passed for Franklin and Richmond.
