# R-05 — General aging and disability link layer (four counties)

**Priority:** Medium. Supersedes the open B02 task if B02 has not been run; if B02 has been returned, build on it.

## Objective
One verified entry per county for each general route, with one line of guidance, so the handoff sheet and directory can point to existing help for any disability or age.

## Route types (per county unless statewide)
1. Area Agency on Aging / Aging and Disability Resource Network front door.
2. 211 or local helpline serving the county.
3. County board of developmental disabilities intake (reuse B01; resolve Morrow intake contact and the Knox early-intervention phone question).
4. County Job and Family Services (Medicaid applications) and Adult Protective Services.
5. Regional Long-Term Care Ombudsman covering the county, plus the state ombudsman line.
6. Ohio Department of Aging Long-Term Care Consumer Guide / quality navigator; CMS Care Compare.
7. Opportunities for Ohioans with Disabilities (vocational rehabilitation) — statewide entry route.
8. Disability Rights Ohio (protection and advocacy) — statewide entry route.

## Carry-over fixes from B01 review
- Replace named-staff emails with office or role contacts; move named contacts to `internal_contact`.
- Remove all session-specific retrieval references.
- Record-level status may not exceed the weakest source behind a published contact field.

## Output
`records.json` per schema, `link_matrix.csv` (county × route type), `notes.md`.

## Maximum size
Up to 32 county entries plus up to 6 statewide entries. Reuse B01 records where valid.

## Acceptance checks
- Every matrix cell holds a sourced record or an `UNRESOLVED` reason.
- One plain-language guidance line per record (what to call them for).
- No availability, waitlist or eligibility outcome inferred.
