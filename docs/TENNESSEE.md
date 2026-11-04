# Tennessee referral edition

Reviewed November 4, 2026. Tennessee moves from a starter edition to a full 95-county edition.

## Veterans contacts (`tennessee-county-veterans-offices.json`)

Each county uses its County Veterans Service Office from the TDVS "County and State Service Officer Contact Roster, May 2026" (Master sheet). The spreadsheet was supplied by the maintainer because tn.gov blocks automated downloads; sha256 `addaf636…ca88`.

- **One office per county.** The roster has one row per staff member. Rows are grouped by county:
  - The office's MAIN LINE is used where listed, otherwise the most common office phone.
  - Other distinct office phones are listed as "Also."
  - Address and hours are the most common values in the county's rows.
- **Left out.** Staff names and emails.
- **Phone formats.** Extensions written as "x112" are kept as extensions. Washington County's "option 1/2" numbers are shown as one number, with a note to listen for the veterans menu.
- **State offices.** Rows marked "TDVS – Region N" are state veterans services offices (for example at the VA medical centers). They appear under "State TDVS office" on that county's card.
- **Lake and Moore.** Their roster rows have no phone or address, so they use the TDVS main line (615-741-2345), with a note saying so.

## Aging and ombudsman (`tn-regional-referrals.json`)

The nine districts and their counties come from the Department of Disability and Aging (DDA) [district long-term care ombudsman page](https://www.tn.gov/disability-and-aging/disability-aging-programs/long-term-care-ombudsman/district-long-term-care-ombudsman.html), read in full. Each county is in exactly one district.

- **Aging agencies (9, `tn-aging-d*`).** Each uses the DDA statewide line, 866-836-6678, which routes callers to their Area Agency on Aging and Disability.
  - Local agency phones were not used because no official list with phones was available.
  - District 9's agency name (Aging Commission of the Mid-South) comes from a state outreach list. The ombudsman page names MIFA as the district's ombudsman host.
- **District ombudsman (9, `tn-ombudsman-d*`).** Each uses the district office phone from the ombudsman page. Memphis Delta lists only staff numbers, so it uses the statewide ombudsman line, 877-236-0013.
- **Statewide records.** `tn-ombudsman` (877-236-0013, plus the elder abuse line 888-277-8366) and `tn-aaad` (866-836-6678).

## Other records (`tn-programs.json`)

- **Housing help (SSVF).** The 6 programs now use county lists from VA's FY26 intake workbook.
- **Centers for Independent Living (6 records).** Taken from the ILRU national directory, with full page text reviewed. The directory spells Sevier as "Servier"; the card uses Sevier.
- **Legal aid.**
  - Help4TN (844-435-7486, statewide, including the senior helpline) comes from Tennessee Courts and TALS.
  - One statewide card names the four regional legal aid programs and their phones, from a DHS page. No county assignment was made because full county lists were not available.
- **VA health care.** One statewide card for Memphis, Mountain Home, Murfreesboro and Nashville. No counties are assigned.

## Limits

Contacts are published-source referrals and were not telephone-confirmed. Tennessee CHOICES waiver and home-modification program details are not yet researched.
