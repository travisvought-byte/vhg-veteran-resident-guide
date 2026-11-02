# Seminole County, Florida: local handoff research (staged)

**Research date:** 2026-11-02  
**Status:** Source-reviewed proposal, not phone-confirmed. **No public directory data or site behavior changed.**

## Why this exists

The Florida edition already covers all 67 counties. This narrow research note proposes a more actionable Seminole County handoff for a potential Veteran Home Guardians replication partner near Altamonte Springs. It is deliberately separate from canonical data so concurrent directory work is not disturbed.

## Primary county referral

**Seminole County Veterans Services**  
520 W. Lake Mary Blvd, Suite 102, Sanford, FL 32773  
Phone: **407-665-2347**  
Email: **InfoVeterans@SeminoleCountyFL.gov**  
Official source: https://www.seminolecountyfl.gov/departments-services/community-services/veterans-services

County-published services include VA and survivor claims, healthcare assistance, education, pensions, burial allowances, and outreach visits. County-published office hours are Monday–Friday 8 a.m.–5 p.m.; walk-ins Monday, Tuesday and Thursday 8:30–11 a.m.; afternoons and Fridays by appointment. Confirm before visiting.

### Additional county outreach sites

- **Oviedo:** VFW Post 243, 491 W Broadway St, Oviedo, FL 32765. County advertises walk-in veterans services first and third Wednesdays, 10–11:30 a.m. Call 407-665-2347 to confirm.
- **Winter Springs:** VFW Post 5405, 420 N Edgemon Ave, Winter Springs, FL 32708. County advertises first Wednesday, 2–5 p.m. The published location contact is 407-327-3151. Confirm before visiting.

These are **county Veterans Services outreach sessions**, not evidence that either VFW post itself provides certified claims representation.

## Statewide routing already available in the Florida edition

- Florida Department of Veterans' Affairs county VSO lookup: https://floridavets.org/locations/county-veterans-service-officers/county-veteran-service-officers/
- County Veterans Service Officers Association of Florida: https://www.cvsoafl.org/
- Florida veteran service organization directory: https://www.floridavets.org/our-veterans/florida-veterans-service-organizations/
- Existing Florida coverage evidence: [docs/FLORIDA.md](FLORIDA.md), including Elder Helpline, aging agencies and long-term-care ombudsman routes.

## Suggested future directory improvement (not implemented)

1. Compare the existing Seminole county record with the official county page. Preserve the existing canonical phone if already correct.
2. Add a clearly labeled Seminole **local handoff / outreach** note or cards only if the current schema and UI support it, avoiding duplicate county-office cards.
3. Confirm the outreach schedule and location before publication; keep published-source review distinct from direct phone confirmation.
4. Preserve senior/nonveteran routing, surviving-spouse guidance and accessibility pathways already present in the Florida edition.
5. Run `python3 scripts/build_public.py --check`, `python3 scripts/validate_public.py`, `npm test` and relevant browser checks after any canonical data edit.

## Replication context

A local prospective partner could use the county veterans office as a first referral and relationship-building contact when exploring a Florida Veteran Home Guardians model. **No affiliation, endorsement, sponsorship, operating chapter or partnership has been established.** Do not publish personal outreach details or represent this research as an agreement.

## Concurrent-work boundary

This PR adds **only this research note**. It intentionally does not edit `states/registry.json`, `states/fl/`, `data/public/`, generated site files, navigation, or application code. Claude or another maintainer can integrate vetted records later without merging conflicting structural changes.
