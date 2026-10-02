# R-02 — Veteran and surviving-spouse benefits relevant to long-term care residents

**Priority:** High. Feeds the Facility Staff Guide.

## Objective
For each benefit topic below, produce a plain-language routing note: what it is in one or two sentences, who is likely worth asking about it, who decides eligibility, what form or application route the official source names, and where to send the person (normally the county office). This is routing guidance, not eligibility advice.

## Topics
1. VA health care enrollment for older veterans (application route, who decides).
2. VA pension, including Aid and Attendance and Housebound allowances.
3. Survivors Pension for surviving spouses, and Dependency and Indemnity Compensation (DIC).
4. VA disability compensation increases where a condition has worsened (routing only).
5. VA extended care: Community Living Centers, Community Nursing Home contracts, and the application for extended care benefits. Identify the official form and who to contact.
6. State Veterans Homes in Ohio: names, locations, operator, official admission route.
7. Interaction between VA pension and Medicaid-funded nursing home care. Find the official federal source describing any reduced pension amount for Medicaid nursing home residents and state it exactly as the source does, with the effective period.
8. Burial and memorial benefits (VA and Ohio), and the role of the county office.
9. VA Caregiver Support Program (who it serves; route).
10. Hospice and palliative care for veterans, including any VA-recognized program for community hospices.

## Rules specific to this task
- Dollar amounts only if the official source states them for the current period; otherwise write "see current VA rates" and link.
- For each topic, record the deciding authority and the official application or contact route.
- Flag any topic where the official guidance is ambiguous or outdated.

## Output
`records.json` (program records per schema), `routing_notes.md` (one block per topic, readable by facility staff), `notes.md`.

## Acceptance checks
- Every topic has an official source or is marked unresolved.
- No sentence states or implies that a resident qualifies.
- Each topic ends with "Next step: contact your County Veterans Service Office" or the officially named route.
