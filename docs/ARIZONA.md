# Arizona referral edition

Reviewed November 4, 2026. Arizona moves from a starter edition to a full 15-county edition.

## Veterans contacts (`arizona-county-veterans-offices.json`)

The Arizona Department of Veterans' Services (ADVS) does not publish county offices.

- **What ADVS publishes.** Its [Veteran Benefits Counselor page](https://dvs.az.gov/services/veteran-benefits-counselors-vbcs) lists remote service and the four Arizona State Veteran Homes. The [February 2025 locations PDF](https://dvs.az.gov/sites/default/files/2025-02/ADVS-Office-Locations-2025-2-21.pdf), read in full, lists the homes, cemeteries and headquarters plus one appointment line, 602-535-1215.
- **What each county gets.** Every county uses that appointment line. The card is labeled as a statewide line and says to ask for the counselor serving the county.
- **County veterans services.** Some Arizona counties run their own veterans services. These were not added because no official list was found.

## Aging and ombudsman

- **Aging agencies (6 records, `az-aging-region-*`).** Taken from DES Division of Aging and Adult Services contact lists (des.az.gov files 13016 and 15697, as search excerpts). Each county is in exactly one region.
  - Region Three serves only non-reservation residents of Apache and Navajo counties, and the card says so.
  - Every aging card names the Navajo Nation Division of Aging and Long-Term Care Support (928-871-6869) and the Inter Tribal Council of Arizona Area Agency on Aging, Region Eight (602-258-4822).
- **Ombudsman (`az-ombudsman`).** County cards send people to the Area Agency on Aging for the local ombudsman, or to the state office (602-542-6454).
  - The state office phone comes from the National Long-Term Care Ombudsman Resource Center listing.
  - The DES ombudsman page needed approval to open and could not be read this session. Confirming the phone from that page is still open.
- **State unit on aging (`az-daas`).** DES Division of Aging and Adult Services, 602-542-4446.

## Other records (`az-programs.json`)

- **Housing help (SSVF).** The 6 programs now use county lists from VA's FY26 intake workbook.
- **Centers for Independent Living (5 records).** Taken from the ILRU national directory, with full page text reviewed. They cover all 15 counties.
  - Ability360's listing says "parts of Pinal," and its card asks people to confirm.
  - ASSIST! to Independence serves Apache County within the Navajo Nation.
- **Legal aid.** County lists come from 211 Arizona and phones from AZ Court Help.
  - Community Legal Services: La Paz, Maricopa, Mohave, Yavapai and Yuma.
  - Southern Arizona Legal Aid: nine counties, including the non-Navajo Nation part of Navajo County.
  - DNA People's Legal Services: Apache and Coconino counties and the Navajo Nation.
- **VA health care.** One statewide card for the Phoenix, Southern Arizona (Tucson) and Northern Arizona (Prescott) systems. No counties are assigned.

## Test change

`tests/assistant.mjs` used to require more than 20 county rows for every full edition. It now checks each state's row count against the registry, which fits Arizona's 15 counties and is stricter.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Arizona waiver (ALTCS) and home-modification program details are not yet researched.
