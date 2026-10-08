# Statewide guide: coverage, sources and maintenance

Updated October 8, 2026.

## Coverage

- All 88 Ohio counties have a county veterans office phone and linked contact source.
- 87 county contacts were extracted from the Ohio AMVETS 2025–2026 Guidebook, physical PDF pages 67–70 (printed pages 7–10). The publication omits Lawrence County; its contact was added from the county government's departments page.
- Morrow and Knox contact sources are their office websites. Lawrence uses its county government website. The remaining entries are labeled as directory-published contacts, not direct agency confirmations.
- Statewide/federal programs appear for every county. Additional local program coverage is strongest in Morrow, Knox, Marion and Delaware and is not an exhaustive inventory elsewhere.
- There are 97 resource records in the reusable projection. Four original county office records are represented by the separate 88-office directory instead of duplicated among the 93 program/resource cards.

## Data and sources

County contact projection: `data/public/ohio-county-veterans-offices.json`. Each entry has a county name, phone, source URL and title, PDF page when applicable, review date and contact evidence status. No street address, named staff or hours were added from the directory because those can become stale independently of a phone.

County sources:

- https://www.ohamvets.org/_files/ugd/e84044_ad8aee056c3c4afcb841dfaee63d8ddb.pdf
- https://lawrencecounty.org/departments/
- https://morrowcountyveterans.com/
- https://kcvso.com/faq/

New referral routes:

- Local aging agency routing: https://compass.aging.ohio.gov/find-information?category=caregivers (official indexed excerpt; full rendered content not available to the research tool, labeled search-excerpt evidence).
- Pro Seniors legal helpline: https://www.proseniors.org/legal-services/legal-hotline/
- Service records: https://www.archives.gov/veterans/military-service-records
- Accredited claims help: https://www.va.gov/get-help-from-accredited-representative/
- VA locations: https://www.va.gov/find-locations/
- Veteran housing help: https://department.va.gov/homeless/what-is-permanent-housing/
- State ombudsman contact: https://www.cms.gov/about-cms/contact/directory/department-aging-ohio-elder-rights-unit/1553936

Pension and care wording was reviewed against VA pension, survivor compensation, long-term care, community nursing home, Community Living Center, hospice and palliative care pages. Eligibility and payment calculations are left to the relevant agency/accredited representative. Existing research records that were not re-reviewed retain their source statuses and dates.

Several Ohio Department of Veterans Services directory/guide URLs returned errors during this update. The live site therefore links the readable source publication or official office source for county contacts rather than depending on those unavailable routes.

## Interface

- Select a county at the top for its veterans office, aging agency and ombudsman phones and sources.
- Choose a common need, search or filter by resource type. Source review status is an optional filter.
- County choices retain statewide/federal routes; programs with unknown coverage do not silently become statewide.
- Share links use validated `county`, `view`, `q`, `type` and `status` query parameters. No browser storage or resident forms are used.
- County handoff printing requires a selected county and includes all three county referral contacts plus the staff guide. Full-view printing is separate.
- Corrections link to repository issues. Only public resource corrections belong there; resident information must not be submitted.

## Verification and upkeep

Checked all 88 names against the complete Ohio county set, checked unique entries and phone formats, matched source pages, and tested every county selection for a contact and statewide resources. Tested need routes, search, local coverage boundaries, share-link parsing, extensions, print gating and matching embedded/external data.

Still needed: direct confirmation of individual office hours/intake arrangements, expansion of local programs beyond the pilot, and assignment of a maintenance owner and backup. No office outreach or scheduled automation was performed.

When updating a phone, retain provenance and the review date; update the county JSON and embedded `COUNTIES` in index.html together. Program edits should keep prototype-data.json and embedded `DATA` together. Working `data/integrated` research is not silently rewritten by this presentation update.

## Regional referral research — October 8, 2026

`data/public/ohio-regional-referrals.json` holds 12 aging agency regions and 12 ombudsman regions. Both sets independently partition all 88 counties, including Paulding in region 4. These 24 records are included in the program projection and embedded site data. Four existing regional records were refreshed, including expansion of the former Delaware-only ombudsman record to the full region 6.

Sources reviewed in full:

- Ohio Association of Area Agencies on Aging, February 2026 directory, page 1: https://www.ohioaging.org/aws/O4A/asset_manager/get_file/943016?ver=0
- Ohio Department of Aging Regional Ombudsman Contact Map, page 2: https://dam.assets.ohio.gov/image/upload/aging.ohio.gov/Regional_Ombudsman_Contact_Map.pdf

Phones are directory-published, not telephone-confirmed. The map does not state its publication date; the review date records when its contents were checked. Agency addresses, hours and staff were not added. Source links point to the exact directory pages because several provider deep links have moved or failed. Region 9 uses the map’s regional ombudsman number (800-967-0615), while Direction Home’s website also provides the agency-wide line (800-421-7277). Region 11’s ombudsman number is distinct from its aging intake number. An annual-report text extraction associated phones with the wrong rows, so it was rejected in favor of visual inspection of the original contact map.

Selecting a county shows all three contacts. Aging agencies appear among useful starting points and home/community support; ombudsmen appear in care concerns/rights. A referral area does not establish eligibility for every program operated by the agency.

## Accessibility application pathway — October 8, 2026

The “Ramps and home accessibility” route provides suggested agency contacts based on military service, living arrangement and Medicaid/waiver support. It does not determine eligibility or suppress the underlying funding directory based on those choices. Choices stay in memory only, are excluded from share URLs, and no names, diagnoses, documents or identifiers are collected. County selection supplies the veterans office and aging agency; VA clinical referrals use the official facility locator because county boundaries do not reliably identify a treating VA facility.

Added TRA, Ohio waiver home modifications, DD waiver adaptations, USDA Section 504 and HOME Choice records. Refreshed HISA/SAH/SHA instructions. HISA is routed to VA Prosthetics and the clinical team, with Form 10-0103, prescription, owner permission, itemized estimate, photographs and inspection questions. SAH/SHA use Form 26-4555 and VA’s application instructions. The printable plan contains contact guidance, expanded checklists and a blank project/follow-up tracker. It uses the browser print dialog and can be saved as PDF by the reader.

Sources reviewed:

- https://www.rehab.va.gov/PROSTHETICS/psas/HISA2.asp
- https://www.va.gov/forms/10-0103/
- https://www.va.gov/housing-assistance/disability-housing-grants/
- https://www.va.gov/housing-assistance/disability-housing-grants/how-to-apply/
- https://www.va.gov/forms/26-4555/
- https://codes.ohio.gov/ohio-administrative-code/rule-5160-44-13 (effective April 17, 2026)
- https://codes.ohio.gov/ohio-administrative-code/rule-5123-9-23 (effective July 1, 2026)
- https://www.rd.usda.gov/programs-services/single-family-housing-programs/single-family-housing-repair-loans-grants-26
- https://homechoice.medicaid.ohio.gov/

VA’s published housing page still shows FY2026 amounts as of this review, while October 8 falls in FY2027. Annual dollar figures were therefore omitted; readers are asked to confirm current maxima and prior use with VA. Do not equate VA disability rating, Medicaid enrollment, a county referral, or a diagnosis with program approval. HISA excludes portable ramps and new construction; equipment and qualifying adapted-housing routes should be discussed separately.

Next research phase: verified temporary ramp/reuse programs and local gap funding, followed by contractors’ counties, accessibility experience, funder/provider requirements, estimate practices, insurance/licensing where applicable, and verified contact dates. No contractor network has yet been populated.

Functional verification: all 88 county mappings and synchronized data; accessibility branches for non-veterans, temporary family residence, new construction, renting and discharge planning; shared-link privacy; route visibility; print actions. Run `node tests/accessibility.cjs`. Browser review verifies the live page separately; these simulated DOM checks do not test print pagination.

Accessibility usability pass: matched first-call contacts now precede the routing questions. An existing waiver case manager is prioritized when selected; new construction points veterans toward adapted housing rather than HISA. Three next steps remain visible; alternative routes and the paper tracker are expandable and expand for printing. County contact cards are hidden in this view to avoid duplication, and choosing the pathway scrolls to its heading.

VHG support section: optional donation and sponsorship invitations appear after the resource directory. The donation link uses VHG’s published donation page; sponsorship opens a draft email to the published organizational address. No message is sent automatically. No prices, guaranteed outcomes, unverified impact totals or payment fields were added. Resource access remains free, and the appeal is omitted from printed referral sheets.
