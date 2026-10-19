# Indiana coverage and evidence

Indiana is the seventh referral edition. Official published sources reviewed October 19, 2026 support all 92 county veterans contacts, 15 aging agencies serving 16 planning areas, 18 ombudsman referral records and 13 statewide programs. Shared federal resources remain available throughout the edition. The original five-file research return and complete source/conflict inventory are in `research/returns/R-06-IN/`.

## County boundaries and conflicts

Indiana DVA's [county directory](https://www.in.gov/dva/home/cvso-locate/) publishes veterans contacts for all counties. The [official state county directory](https://www.in.gov/counties/) supplies the matching 92-county list. Union's only published phone is a role cell; publication was approved by the owner. Staff names and `internal_contact` metadata are excluded from canonical public data and generated bundles. County names include Ohio; it stays county-limited.

The [FSSA aging directory](https://www.in.gov/fssa/ddars/bba/area-agencies-on-aging/) supplies all agency phones and county assignments. LifeStream is one agency serving Areas 6 and 9; both county lists and the common toll-free number are retained. Every county has exactly one aging agency.

The [state ombudsman directory](https://www.in.gov/ombudsman/long-term-care-ombudsman/contact-information/) contains unresolved differences between its county panels and legend. County and caregiver views use the statewide 800-622-4484 contact first for Randolph, Boone, Areas 10/11 and Area 14, with published local alternatives and differences available in the county panel. Randolph appears in both Area 6 and Area 9 source assignments; both remain in resource data with explicit constraints. The return does not choose which source section is newer.

Marion has a published subcounty split: NE, SW, E and SE use 317-631-9424; NW uses 463-237-9348, also listed for Boone. Both routes and their scope notes are shown. The caregiver flow routes Marion through the statewide office to identify the exact facility assignment. Lawrence uses its separately published Area 15 contact; Crawford, Orange and Washington use another. Vanderburgh has the separate VOICES ombudsman route. Area 12 publishes the statewide number, not a distinct local line.

## Indiana programs and home accessibility

The 13 requested programs cover claims assistance, the Indiana Veterans' Home, AAA/ADRC navigation, the aging directory, SHIP, Medicaid HCBS screening, the state ombudsman, caregiver support, INDATA, Disability Rights, vision services, deaf/hard-of-hearing services and Indiana 211. Each retains official URLs, review dates, review methods and per-source field scope. All direct-agency-confirmation flags are false.

The accessibility and senior views distinguish existing PathWays members' health-plan service coordination from new aging-agency screening and separate BDS disability waiver application routes. PathWays generally serves people 60 and older with exceptions; Health and Wellness serves people 59 and younger with a disability. Program-specific eligibility and authorization apply. Medicaid enrollment does not establish modification coverage.

The [PathWays provider manual](https://www.in.gov/medicaid/providers/files/modules/ompp-hcbs-waiver.pdf), published June 15, 2026 with policies as of August 1, 2025, requires prior waiver approval for home modifications, service-plan documentation and appropriate providers (printed pages 68–72). Those requirements are not automatically attributed to other waivers. No funding amount or current availability is promised. INDATA supports device trials, lending and reuse; permanent ramp construction and installation are not guaranteed.

## Maintenance and validation

Canonical records are `data/public/indiana-county-veterans-offices.json`, `in-programs.json` and `in-regional-referrals.json`. Configuration is in `states/in/` and `states/registry.json`. The shared builder creates the on-demand Indiana bundle, combined resource download, `in.html` redirect and `share-in.html`; its QR points to `?state=IN`.

Run all checks in `docs/ADDING-A-STATE.md`. Registry tests check all 92 county panels and county isolation; `tests/indiana.cjs` additionally checks ombudsman conflicts, Marion scope, Union publication boundaries and Indiana-specific pathways. Local providers, tribal or installation boundaries, phone reachability, current intake, equipment inventory and funding availability were not directly confirmed. No agency was contacted.
