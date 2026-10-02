# OH-SDR-S1-B01 — research return

Prepared October 2, 2026. Candidate integration batch for Claude; not a merged dataset or published directory.

## Inputs and preservation

Input: `Ohio_Senior_Disability_Directory_Starter.json`, `0.2-working-seed`, 47,042 bytes. SHA-256: `2f48972e853ed97cb0ee120339a3b685bb576d5a9c68c6ebcd564f144c2253f5`.

The seed was materialized and parsed without editing it. It contains 25 facilities, 22 existing resources, seven scenarios and three project-funding leads. The facilities, CMS CCNs, funding leads and all original review/status fields remain unchanged in that file.

Input plan: `Ohio_Directory_Project_Plan_Claude_Handoff.md`, read during the preceding retrieval; B01 follows the relayed packet. No agency contact, form submission, outreach draft, facilities research, vendor research or project-funding research was performed.

## Findings and implications

- Morrow, Knox and Marion are in District 5's service area. Delaware is in COAAA's area. Use those agency records in the matrix, with separate program criteria. Sources: [District 5 service area](https://www.aaa5ohio.org/about/our-agency/) and [COAAA service area](https://www.coaaa.org/about/our-agency/).
- Four county DD entries are identified. Morrow's public main office and SSA department provide a usable starting route, but a dedicated intake contact was not established. Delaware, Knox and Marion publish specific intake routes. These are website reviews, not responsiveness checks.
- P1 includes the packet's under-3, school-age and transition branches. A proposed preschool 3–5 subbranch closes the age gap; transition is an overlay, not an exclusive age band. The official [evaluation roadmap](https://education.ohio.gov/getattachment/Topics/Special-Education/Families-of-Students-with-Disabilities/Sections/Section-1/EvaluationRoadmap92025-5-1.pdf) routes preschool families to the parent's resident district. [State transition guidance](https://education.ohio.gov/Topics/Special-Education/Federal-and-State-Requirements/Secondary-Transition-and-Workforce-Development) places transition planning at 14 or younger if appropriate.
- P2 distinguishes DD eligibility from the non-DD Medicaid/home-care route. Navigation can start at the AAA even for younger adults. The [Ohio Home Care rule](https://codes.ohio.gov/ohio-administrative-code/rule-5160-46-02) and [request instructions](https://dam.assets.ohio.gov/image/upload/medicaid.ohio.gov/Families,%20Individuals/Programs/Waivers/HCBSWaivers/ProgramInformation/Ohio_Home_Care.pdf) support an application/assessment route, not an enrollment promise. Coverage is an additional branch; individual plan routes are not established by county alone.
- P3 distinguishes county benefits help, VA clinical/Prosthetics HISA review, and VBA adapted-housing applications. Direct VA entry is supplied through the official locator and application instructions; a county-to-VA medical catchment assignment is not inferred.

## Overlap classification

| Pathway | Best existing navigator or guide | Classification | Reason |
|---|---|---|---|
| P1 | Ohio EI coordinator/referral; DEW evaluation and transition roadmaps; county DD intake | navigation_gap_add_guidance | Proposed local age routing connects existing systems and distinguishes their decisions. |
| P2 | District 5 ADRN or COAAA consultation; statewide Ohio LTSS | navigation_gap_add_guidance | Proposed county, age and coverage guidance helps choose among existing assessment routes. |
| P3 | County VSO; VA HISA and adapted-housing guidance | navigation_gap_add_guidance | Proposed guide separates benefit types and adds a non-VA navigation fallback. |

These classifications describe a proposed presentation contribution. They are not demonstrated service gaps or claims that existing navigators fail. No user journey was tested, and no unavailable service was established. Existing-tool linkage should be retained even if testing finds no incremental benefit.

## Resource integration and seed conflicts

15 candidate resource records: eight updates and seven additions.

Updates retaining exact seed IDs: `delaware-dd-intake`, `knox-dd-intake`, `marion-dd-intake`, `district5-adrn`, `va-hisa`, `help-me-grow`, `special-education`, `ohio-ltss`.

Additions: `morrow-dd-intake`, `coaaa-navigation`, `morrow-vso`, `knox-vso`, `marion-vso`, `delaware-vso`, `va-adapted-housing`.

Morrow intake is distinct from the seed's `morrow-dd-fdr` financial-assistance program. COAAA is distinct from the seed's SourcePoint service. County VSO offices are local records under the seed's statewide VSO directory concept; they do not duplicate that directory hub.

No factual contradiction with these eight seed entries was established. The changes primarily deepen the documented routes and evidence. `help-me-grow` retains its ID but this batch's current fields cover the EI referral use case; its original broader description remains in `preserved_seed_fields`. Claude should preserve the umbrella/program relationship when splitting entities. The other 14 seed resources were not re-reviewed or replaced.

Each resource includes `batch_action`, `seed_record_id` and `preserved_seed_fields`. The latter is historical input, not freshly verified public content. Do not give its old fields the new review date. Apply current candidate fields individually, retain provenance, and leave unrelated seed records alone.

`organization_id` remains null because schema v0.3 and canonical organization IDs are Claude's task. Do not invent dangling entity links. `va-adapted-housing` is explicitly a navigation bundle: split SAH and SHA into linked program entities in v0.3 while preserving this route's identity. Program-specific financial limits are null.

## Evidence limits and unresolved questions

1. Marion VSO: the office website could not be fetched. The VA county-resource page supports the office identity/address; an indexed official Ohio DVS guide extract supports 740-387-0100. The full DVS PDF also could not be fetched. This is explicitly `official_search_extract_reviewed`, not full-page review or agency confirmation. Recheck contact currency before a stronger label. A failed fetch does not imply closure.
2. Morrow DD: main office and SSA department are supported; dedicated eligibility intake contact and age-specific document checklist remain unknown.
3. Local school/educational-agency names and contacts must be resolved from the family's residence/enrollment. County alone is insufficient; a universal four-county school contact was not invented.
4. HISA: responsible VA facility/Prosthetics unit and remaining entitlement are individual matters. The official source provides a locator route. No local PSAS phone or medical catchment was inferred.
5. SAH/SHA: the reviewed page still labels dollar limits FY2026, while this review is in FY2027. Do not carry those figures into current amount fields. Recheck current VA guidance before publishing amounts.
6. Program availability, remaining funds, payer acceptance, appointment response, waitlists and individual eligibility remain null. No installation vendor or completed referral is represented.
7. P3 fallback is a route to another navigator for screening, not a verified funded adaptation or contractor placement. A full provider/delivery chain belongs in later inventory work.

## Decisions and ownership

The relayed research packet authorizes B01 web research only. It does not resolve D-001 (VHG public project home/board action) or S0-04 (files-of-record location). Do not interpret the working VHG label as board approval or a partnership.

Claude should review the preschool subbranch and the transition/coverage overlays during integration. They remain inside P1 and P2, so the batch still contains three pathways. Travis retains organizational and public-release decisions. No approval is needed to review these candidate files; any later organizational action remains a separate decision.

## Presentation proposals

Start with county, age and need. Show school evaluation and DD supports as parallel choices. For home help, ask about existing coverage after the age/need branch. For accessibility, distinguish county benefits help from the two direct VA routes. Every result should show its source, review date and evidence depth; website-reviewed and organization-confirmed information must remain distinct.

The current batch has no organization participation or endorsement evidence. Provider feedback/confirmation and recurring re-review remain future maintenance work, not an accomplished B01 result.

## Files and validation

Created:

- `b01_resources.json` — 15 candidate records with minimum fields, source URLs, supported-field lists, review dates and published-year metadata where available.
- `b01_contact_matrix.csv` — four county rows × three route columns, all 12 populated with IDs resolving to sourced batch records.
- `b01_pathways.json` — P1–P3, branch-specific contacts, questions, next steps, decision owners and fallbacks.
- `b01_notes.md` — this return and its limitations.

Supplied unchanged: `Ohio_Senior_Disability_Directory_Starter.json` v0.2.

Validation: JSON parsed; resource count/unique IDs checked; eight update IDs matched existing seed IDs; seven new IDs checked against the seed; minimum resource fields and review-method values checked; all matrix and pathway references checked against the batch; each ordered step checked for question, expected next step and fallback; original seed bytes and SHA-256 checked unchanged. All checks passed. No external services were tested or contacted.

Recommended next assignment after Claude review: a bounded B02 for dedicated Morrow intake contact, stronger Marion VSO source confirmation, applicant-specific school/VA lookup instructions, and any other review conflicts. Full facilities reconciliation remains held until Stage 1 is accepted.
