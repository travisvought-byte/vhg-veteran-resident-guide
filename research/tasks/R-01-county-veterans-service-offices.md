# R-01 — County Veterans Service Offices: verification and referral practice

**Priority:** Critical path. Complete before any handoff sheet is drafted.
**Counties:** Morrow, Knox, Marion, Delaware.

## Objective
Produce one complete, sourced record per county office, resolve known address conflicts, and document how each office prefers to receive residents of long-term care facilities.

## Inputs
- `data/batches/B01/` records `morrow-vso`, `knox-vso`, `marion-vso`, `delaware-vso`
- Known conflicts:
  - Delaware: B01 lists 91 North Sandusky St.; VA Central Ohio county page lists 149 N. Sandusky St.
  - Knox: B01 lists 105 East Chestnut St.; VA Central Ohio county page lists 411 Pittsburgh Ave.
  - Marion: phone supported only by a search extract; office website could not be fetched.

## Questions
For each county office:
1. Current official name, street address, mailing address if different, main phone, office email or web form, hours. Record every official source that states each value and whether they agree.
2. Walk-in or appointment; whether the office publishes home, hospital or facility visits for veterans who cannot travel.
3. What a veteran or surviving spouse is told to bring (e.g., DD-214, ID, insurance cards, income information), only where the office or Ohio DVS publishes it.
4. Services the office publishes: VA claims assistance, emergency financial assistance, transportation to VA appointments, burial/memorial assistance, help obtaining DD-214. Record only what is published.
5. Whether the office publishes guidance for families of deceased veterans (surviving-spouse benefits).
6. Nearest VA clinic (CBOC) or medical center published for the county, with the official source. Do not infer catchment.
7. Statewide fallbacks: Ohio DVS main line and the official statewide county-office directory URL.

## Also produce
`call_script.md`: a neutral confirmation script Travis (or a designee) can use, under 2 minutes, asking the office to confirm address, phone, hours, visit options, preferred way to receive facility referrals, and whether they want to review their entry before publication. **Draft only. Do not send or call.**

## Maximum size
4 county office records, 1 statewide fallback record, 1 script.

## Acceptance checks
- Every address and phone shows all supporting sources and any conflict.
- No field stronger than its evidence; search extracts labeled.
- Nothing labeled confirmed by the agency.
- Services listed only where the office itself publishes them.
