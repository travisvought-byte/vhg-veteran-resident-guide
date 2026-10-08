# Current repair status — October 6, 2026

The current candidate is v0.3.1. It uses the corrected R-01 input, repairs the 14 earlier claim-path issues, supplies three sourced state agency/sponsor assignments, renumbers integration decisions, retains full conflict values in integration_audit.json, and rejects fatal structural/reference errors. Scope D-017 excludes individual care-facility listings; the original facility seed remains available for separate outreach. This resolves the technical blockers below, not the factual acceptance work. Four office confirmations, 14 imported-resource reviews, six wording comparisons and maintenance/boundary review remain pending. No publication or agency contact occurred.

The October 2 review below is preserved as historical context.

---

# Integration review and merge recommendation

Veteran Resident Resource Guide · Internal working draft · 2026-10-02

## Review status

The four supplied attachments were read directly and checked against current Drive copies of the five integration inputs and schema. The dataset independently contains 66 programs/resources, 25 organizations, 116 sources and 54 relationships. Record statuses match the supplied summary: 43 official-source-reviewed, 5 extract-only, 4 needs_recheck and 14 imported/unverified. Program, organization and source IDs are unique. The project's limited schema checker passes; this is not a complete evidence or acceptance check.

### Acceptance blockers and implementation findings

- **14 claim-field paths fail:** 12 claims still point at B01 `geography`; one points at `service_description`; one at `public_contact.address`. Those fields are absent from the final entity. Map supported geography/description claims to the correct v0.3 fields. Retire or retain privately any overwritten address claim that no longer describes the public contact. Do not simply map a disputed old address to a new public field.
- **Stale R-01 input:** Four input hashes match current Drive. R-01 does not: candidate hash `c2f56a52f7a58eb3d0d23cc429032a7493f541fa7194a9cdcb60879f1e419ac6`; current Drive hash `86252d7d6a6b03b926b75a357b0a1c281dbb0d205a1f45a70faf82cd0f541eb5`. Candidate Delaware program and organization identity remain `official_source_reviewed`; current R-01 corrected them to `official_search_extract_only`. Regenerate from current input rather than editing the recorded fingerprint.
- **Three operator errors:** The supplied integration checker reports Help Me Grow, Ohio LTSS and special education as errors; 14 seed-only missing operators are reported as pending. The supplied report already lists these three errors. Passing the original research-packet checks is not evidence that the merged candidate meets its operator rule.
- **Decision-ID collision:** Both the script's generated dataset and rules reuse D-016 for precedence, but current docs/decisions.md already uses it for the private ChatGPT/Drive home.
- **Report truncation:** Conflict values are truncated to 120 characters by the report writer. Long values are not fully recoverable from that report alone. Retain full values in a machine-readable audit or provenance.
- **Check limits:** The integration checker tests whether claim entities exist, but does not test whether each claim-field path resolves. It also returns success from main even when validation errors exist. Make these acceptance checks explicit in a later repair.

Detailed results are saved alongside this memo in `validation_results.json`. The supplied packet is staged unchanged as a private candidate; no acceptance, public release or source re-review is implied.

## Recommended wording rule

Merge navigation instructions field by field. Keep the most specific instruction supported by applicable, current evidence. Preserve the simpler wording as a summary and retain both versions, their source references, review dates and selection reason in provenance. Packet order alone does not establish freshness: B01 and R-05 both show a 2026-10-02 review date.

If two instructions are compatible, combine the useful detail without inventing requirements. If they conflict, prefer demonstrably stronger or more current evidence; otherwise flag for review rather than silently select. Retaining an earlier instruction does not give it a new review date or verification level.

For a schema that only permits `next_step`, keep the chosen guidance there and store the alternative in an existing provenance/history field. Do not introduce a new public field without reconciling the schema and export rules. Sources must support the selected field, not merely the same organization.

Document lists belong to their published application or assessment stage. Do not turn them into requirements before someone can make an initial call. Facility staff and VHG should not receive or store a resident's documents through this project.

## Six records affected

These are comparisons of the existing research packets, not new reviews of the agencies' websites. Check source support and current applicability before restoring detail into the candidate.

| Record ID | B01 detail worth evaluating | R-05 treatment |
|---|---|---|
| morrow-dd-intake | Ask what eligibility records are needed and how to request service and support administration (SSA). | General eligibility question; age 3+ versus early intervention is more explicit in the referral route. |
| knox-dd-intake | Return application and diagnosis records; ask how SSA planning begins. | General eligibility question; retain age-specific routing and make application-stage requirements separate from the first contact. |
| marion-dd-intake | Diagnosis, birth certificate, Social Security card and Medicaid card if applicable; intake eligibility then SSA assignment. | General eligibility question. Keep any supported checklist with the correct stage and ask intake what is needed before collecting documents. |
| delaware-dd-intake | Intake request, diagnosis/functional assessment and support coordination. | General eligibility question; referral route adds age 3+ intake versus under-3 Help Me Grow. |
| district5-adrn | Describe daily needs; ask for assessment and payment route. | General long-term support navigation. Retain useful assessment questions without suggesting that the navigator guarantees program eligibility. |
| coaaa-navigation | Ask for consultation/assessment matched to age, daily needs and coverage. | General aging/disability navigation. Preserve the useful question if the cited service source still supports it. |

## Contact roles

- R-05 labels Delaware DD 740-201-3601 as the Intake and Eligibility Department; B01 lists 740-201-3600 as a public contact without a role label. Preserve a supported intake/main distinction instead of treating the numbers as necessarily contradictory. The main-line role needs explicit supporting evidence before being exported as such.
- R-05 labels Marion DD 740-387-1035 as the main office, with an instruction to ask for the intake coordinator. B01 lists 740-375-6185 without a role label and also includes a named staff email. Keep the older number historical/pending confirmation; do not invent its role or publish the personal email.
- Preserve deliberate suppression of a disputed contact, including the Morrow email, until the conflict is resolved. Do not automatically repopulate it from an earlier packet.

## Earlier rules requiring reconciliation

1. **Decision IDs:** Existing D-016 already records ChatGPT/Drive as the private working home. The earlier integration rules also call precedence D-016. Give the integration proposal an unused ID only after reading the complete current decision log; do not overwrite the existing decision. Reconcile mobility-rule IDs at the same time.
2. **Null semantics:** Distinguish unknown/not researched from intentionally suppressed/conflicted. An ordinary later null should not erase an earlier supported value; an explicit conflict suppression should override the public field, retaining the old value privately in provenance.
3. **Evidence retention:** Selecting an earlier detailed step must also preserve its actual sources, field-level support and verification limits. Combining sources into one list must not upgrade weaker claims.
4. **Canonical identity:** Retain seed/program IDs and the proposed single organization ID with an alias map; verify all relationships and foreign keys against that map. The revised rules and script were read; both retain the D-016 collision and packet-order precedence.
5. **Verification:** Check that current R-01 Delaware office/program identity remains official-search-extract-only and all four county offices remain needs_recheck. No call or successful referral has been recorded.

## Repair and validation before acceptance

- Stage the supplied files as a private candidate; preserve the input research files and their fingerprints.
- Use current Drive inputs, including the latest R-01 corrections; preserve the supplied candidate as a reproducible earlier run. Correct source claim-field mapping and strengthen validation before generating a replacement.
- Apply the evidence-first wording rule, check the six records above, and regenerate the candidate and report.
- Validate schema, ID uniqueness, organization aliases, foreign keys, source-to-field claims, null suppression, historical dates and public export exclusions for personal contacts.
- Recount verification categories and compare the resulting report with the claimed totals; do not assume a count match proves correctness.
- Hold facilities, pathways and funding leads until the candidate is explicitly accepted. No publication, sharing change or agency contact is part of this review.

## Files changed in this review

The four supplied files are stored at the requested Drive paths, replacing the earlier rules file in place. This memo, validation_results.json and the workspace index are added/updated. Supplied attachment bytes, research inputs and the decision log are unchanged. The proposed wording policy is not yet applied to the script or candidate.

