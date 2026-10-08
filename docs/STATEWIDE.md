# Statewide guide: coverage, sources and maintenance

Updated October 8, 2026.

## Coverage

- All 88 Ohio counties have a county veterans office phone and linked contact source.
- 87 county contacts were extracted from the Ohio AMVETS 2025–2026 Guidebook, physical PDF pages 67–70 (printed pages 7–10). The publication omits Lawrence County; its contact was added from the county government's departments page.
- Morrow and Knox contact sources are their office websites. Lawrence uses its county government website. The remaining entries are labeled as directory-published contacts, not direct agency confirmations.
- Statewide/federal programs appear for every county. Additional local program coverage is strongest in Morrow, Knox, Marion and Delaware and is not an exhaustive inventory elsewhere.
- There are 72 resource records in the reusable projection. Four original county office records are represented by the separate 88-office directory instead of duplicated among the 68 program/resource cards.

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

- Select a county at the top for its office phone, source and intake questions.
- Choose a common need, search or filter by resource type. Source review status is an optional filter.
- County choices retain statewide/federal routes; programs with unknown coverage do not silently become statewide.
- Share links use validated `county`, `view`, `q`, `type` and `status` query parameters. No browser storage or resident forms are used.
- County handoff printing requires a selected county and includes its office contact plus the staff guide. Full-view printing is separate.
- Corrections link to repository issues. Only public resource corrections belong there; resident information must not be submitted.

## Verification and upkeep

Checked all 88 names against the complete Ohio county set, checked unique entries and phone formats, matched source pages, and tested every county selection for a contact and statewide resources. Tested need routes, search, local coverage boundaries, share-link parsing, extensions, print gating and matching embedded/external data.

Still needed: direct confirmation of individual office hours/intake arrangements, expansion of local programs beyond the pilot, and assignment of a maintenance owner and backup. No office outreach or scheduled automation was performed.

When updating a phone, retain provenance and the review date; update the county JSON and embedded `COUNTIES` in index.html together. Program edits should keep prototype-data.json and embedded `DATA` together. Working `data/integrated` research is not silently rewritten by this presentation update.
