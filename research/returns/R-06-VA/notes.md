# R-06 Virginia — research intake (2026-10-19)

**Status: IN PROGRESS; NOT A VALIDATED STATE RETURN; NOT APPROVED FOR PUBLICATION.**

Virginia has **95 counties and 38 independent cities (133 county-equivalents)**. Source: Virginia Department of Social Services https://www.dss.virginia.gov/les/ and Virginia Association of Counties https://www.vaco.org/virginia-counties/. Treat cities separately (for example Richmond City versus Richmond County). Note: the Census Bureau's older 2010 reference lists 39 cities, so use the current 38-city state list for the 2026 edition; do not silently import the historical count.

## Verified starting point: veterans services

Virginia Department of Veterans Services publishes a searchable statewide office directory, currently stating **38 offices**. It is a regional/field office network, not 133 separate county offices. Directory: https://www.dvs.virginia.gov/benefits-services/find-a-dvs-office-near-you . DVS benefits page https://www.dvs.virginia.gov/benefits-services says benefits consultations are free and provides statewide intake **844-838-7838**. Until an official county-to-office mapping is found, use that published statewide number as a **clearly marked fallback** rather than assigning a geographically nearby office without proof.

## Source leads and decisions still needed

- **County equivalents:** reconcile exactly 95 county names and 38 independent city names with a current official state list. https://www.dss.virginia.gov/les/ lists the independent cities.
- **Veterans contact:** map every one of 133 county equivalents to a published DVS office or statewide fallback. The official 2025 DVS guide lists offices but is not proof of county assignments: https://online.flippingbook.com/view/870605682/ .
- **Aging:** find official Virginia Department for Aging and Rehabilitative Services Area Agency on Aging county service-area mapping; cite each mapping, including city/county collisions.
- **Ombudsman:** identify statewide and published regional Long-Term Care Ombudsman assignments from the state aging network.
- **Programs:** complete the thirteen required `va-...` records from R-06 (claims, homes, ADRC, aging directory, SHIP, waiver, ombudsman, caregiver, AT, rights, blind, relay, 211) with primary-source evidence.
- **Routing:** supply `routing.json` and an official Medicaid home-modification authorization source.
- **Validation:** generate the five R-06 files, run `scripts/check_state_return.py` until 0 errors, paste exact checker output into `notes.md`, then submit for integration/review.

## Current evidence and limitations

Reviewed official pages and government sources on 2026-10-19; no agencies contacted. The 38-office count is a state-level directory count, **not** a verified count of local veterans contacts. The county-to-office mapping, aging regions, ombudsman assignments and program records are **not yet researched or verified**. No synthetic records, invented phones, or unverified state routing should be published.

## What could not yet be confirmed

The full 133-jurisdiction contact coverage; agency-specific regional assignments; thirteen state program source records; all five validated return files.
