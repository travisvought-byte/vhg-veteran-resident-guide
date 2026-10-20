# Guided Assistance: MVP acceptance checklist

## What counts as the MVP

The **referral MVP** is already public: someone can choose an available state and county, identify the beneficiary type, find source-reviewed assistance contacts, and copy or print a handoff. This does not guarantee eligibility or current funding.

The **application-assistance MVP** adds concrete, source-linked preparation, application routing, responsibility and follow-up for prioritized programs. It deliberately does not store cases, handle uploaded claims, file benefits or automatically contact agencies. Those are optional future services, not MVP prerequisites.

## Feature gates (October 19, 2026)

| Gate | Acceptance test | Status |
| --- | --- | --- |
| Public availability | Website reachable, linked from main guide, page deployment green | **Met** on main |
| State and county navigation | Published editions, review-status filters, office contact, beneficiary-specific matching | **Met with coverage caveats**: 11 states; local detail varies |
| Official application routes | A supported program identifies the right official starting point | **Met for 12 curated programs** |
| Step-by-step preparation | Paperwork, submitting authority, responsible person and follow-up provided | **10 program routes after this wave**; breadth remains limited |
| Printer-ready referral | One US Letter page with direct source links, no typed story, and no private form values | **Automated checks for 10 after this wave**; physical printing not yet tested |
| Privacy | No storage or transmission of entered cases and checkmarks by the static navigator | **Met for current browser-only architecture** |
| Technical quality | Source synchronization, role boundaries, 11 state tests, mobile and browser printing | **Automated CI**; verify each release |
| Real-world usability | A veteran, survivor, nonveteran and facility worker can complete representative scenarios without coaching | **Not yet independently tested** |
| Content maintenance | Owner and source-recheck cadence, corrections log and response expectations | **Partially met** |
| Human follow-up | Clear options for questions, incorrect matches, unavailable programs and urgent housing intake | **Partially met**; no staffed VHG case-management channel or service guarantee |

## Manual pilot needed to claim a validated application-assistance MVP

Recruit at least five opt-in test users / helpers (including a veteran, surviving spouse, senior/nonveteran and nursing home caregiver). For each scenario, observe whether they can:
1. Set the correct county and eligibility context.
2. Understand the distinction between a potential starting point and confirmed eligibility.
3. Find the correct official form/intake, document list and receiving authority.
4. Print or copy a safe handoff and identify what happens next.
5. Report a wrong, inaccessible or out-of-date link.

Record only anonymized outcomes and fix blockers. Do not collect names, medical details, claim IDs or case documents in GitHub, analytics or public issues. Define success thresholds before testing.

## Release sequencing

1. Add pension, surviving family and housing preparation checklists, and validate all ten printable handoffs.
2. Run the supervised five-user practical pilot. Resolve misleading routing, inaccessible links and confusing submission instructions.
3. Document content ownership, a 90-day link and instruction recheck, and clear correction/escalation responsibility.

## Honest project status

A **usable referral MVP is live today**. A **validated application-assistance MVP is not yet complete**; automated tests alone do not establish that residents or nursing-home staff can use the output without assistance. Fully automated email, AI chat, stored case tracking and electronic VA filing are **outside the agreed minimum viable scope**.
