# R-06 — State referral editions (repeating research cycle)

**Issued:** October 18, 2026. **Owner:** Travis Vought, Veteran Home Guardians.
**Cycle:** one state per cycle, taken in queue order (end of this packet) unless Travis names a different state.
**Read first:** `research/README.md` (research rules). Those rules apply to every field below.

## Objective

Produce the published-source records that let the guide add one state at the same standard as Michigan, Kentucky and Utah: every county resolves to a veterans contact, a local aging contact and a long-term-care ombudsman route, each backed by an official published source and a review date, plus the state's core senior, disability and veterans programs.

## How the work is divided

| Role | Responsibility |
|---|---|
| Researcher (you) | Find and record official published sources. Return the five files below. Flag conflicts and decisions; do not resolve them silently. |
| Integrator (Claude) | Turns an accepted return into the state's registry entry, wording and routing files; runs the full test suite. |
| Owner (Travis) | Decides open questions in `notes.md` and approves publication. |

Research only. Do not call, email or submit forms to any agency. Do not draft outreach.

## Reference material in this repository

- `docs/ADDING-A-STATE.md`: how a state is assembled and checked.
- `docs/UTAH.md` and the Utah files in `data/public/` (`utah-county-veterans-offices.json`, `ut-regional-referrals.json`, `ut-programs.json`): the most recent complete example. Match their shape.
- `data/public/michigan-county-veterans-offices.json`: example of county-level veterans offices.
- `data/public/kentucky-county-veterans-offices.json`: example of regional representatives mapped to counties.
- `scripts/check_state_return.py`: the self-check you run before returning.

## What to research

### A. The county list
The state's official list of counties and county equivalents (independent cities, parishes, boroughs, census areas), with the source. Use exact official names without the word "County". Record the total. Where a name repeats (a county and an independent city both named Richmond), keep both, distinguish them in the name ("Richmond City"), and set `county_type` (see formats).

### B. Veterans contact for every county
The county veterans service office where the state has them; otherwise the state veterans agency's published regional or field office assigned to that county. Prefer the official state directory. An association directory is acceptable when it is the best published source (label it `published_directory`). Record the office's main line, not a personal line, unless only a named representative is published (see README rule 7; Kentucky is the precedent). When a county has no published contact, map it to the state veterans agency's statewide line and say so in a `note`.

### C. Local aging contact for every county
The Area Agency on Aging (or Aging and Disability Resource Center) serving each county, from the state unit on aging's official map or directory. Record the counties each agency serves and the source that establishes that mapping. If two sources map a county differently, record both in `notes.md`.

### D. Long-term-care ombudsman
The state long-term-care ombudsman program (statewide record, always). Where the state publishes regional or local ombudsman offices with counties assigned, add one regional record per office.

### E. State programs
Record each of the following that the state operates or officially designates. If one does not exist or has no usable public page, say so in `notes.md`. Use the id shown, with your state's lowercase code in place of `xx`.

| Id | Program |
|---|---|
| `xx-claims` | State veterans agency: free accredited claims help |
| `xx-homes` | State veterans homes (long-term care for veterans) |
| `xx-adrc` | Statewide aging and disability resource line or "no wrong door" routing |
| `xx-aging-directory` | State unit on aging's directory of local aging agencies |
| `xx-ship` | State Health Insurance Assistance Program (free Medicare counseling) |
| `xx-waiver` | Medicaid home and community-based services or waiver screening for older adults and people with disabilities |
| `xx-ombudsman` | State long-term-care ombudsman program |
| `xx-caregiver` | Family caregiver support |
| `xx-at` | State assistive technology program (device loans, reuse, demonstrations) |
| `xx-rights` | Protection and advocacy organization for people with disabilities |
| `xx-blind` | Vision rehabilitation or services for the blind |
| `xx-relay` | Relay service, or the state office for deaf and hard-of-hearing people |
| `xx-211` | 211 or the state's official housing and emergency assistance route |

Optional, when well documented on an official page: home modification or ramp programs, PACE, nursing home transition, emergency assistance for veterans.

### F. Routing proposal
Which program ids answer each need in the guide (see `routing.json` below), the statewide navigation line people should call first, and the official page that explains who authorizes home modifications under Medicaid or waiver services.

### G. Name collisions and boundaries
Note any county that shares the state's name, any county split between agencies (Michigan's Wayne County is split by city), any military installation or tribal-nation boundary noted by a source, and any county the state assigns to an agency in another state.

## Return: five files

Place them in `research/returns/R-06-<CODE>/` (for example `R-06-IN/`). If you cannot write to the repository, give Travis the five files as downloads.

### 1. `<slug>-county-veterans-offices.json` (slug: lowercase state name with hyphens, e.g. `west-virginia`)

One object per county, in alphabetical order:

```json
{
  "state": "UT",
  "county": "Beaver",
  "county_type": "county",
  "phone": "435-218-5128",
  "organization": "Utah Department of Veterans and Military Affairs — Southern Utah",
  "office_type": "regional",
  "source_url": "https://veterans.utah.gov/regional-offices/",
  "source_title": "UDVMA Regional Offices — published county assignments and regional managers",
  "reviewed_on": "2026-10-14",
  "contact_status": "official_website",
  "note": "Regional contact serving this county; not a separate county office.",
  "evidence": {
    "review_method": "full_official_page_text",
    "direct_agency_confirmation": false,
    "selection": "Published regional phone; county mapping from the same official directory."
  }
}
```

- `county_type`: `county`, `independent_city`, `parish`, `borough`, `census_area` or `city_and_county`. Omit only when every entry is a county.
- `office_type`: `county`, `regional`, `city` or `state`. Regional and state entries need a `note`.
- `contact_status`: `official_website` (government page) or `published_directory` (association or other published directory).
- Phones are written `555-555-5555`, with ` ext. 12` when published.
- Optional: `representatives` as `[{"name": "...", "phone": "...", "region": 12}]` only where the source's only route is named representatives; flag it in `notes.md`.

### 2. `<code>-regional-referrals.json`

One object per aging agency and per regional ombudsman office:

```json
{
  "program_id": "ut-aging-bear-river",
  "name": "Bear River Area Agency on Aging",
  "organization": "Bear River Area Agency on Aging",
  "official_url": "https://daas.utah.gov/locations/",
  "state": "UT",
  "service_area": ["Box Elder", "Cache", "Rich"],
  "regional_role": "aging_agency",
  "needs_supported": ["general_navigation", "help_at_home"],
  "description": "A regional starting contact for aging and community support.",
  "next_step": "Give your county; ask about meals, transportation, caregiver support, home services and local senior centers.",
  "constraints": ["Confirm intake, service eligibility and availability. Published agency numbers may be general routing lines."],
  "public_contact": {"phone": "435-752-6962"},
  "verification": {"record_status": "official_source_reviewed", "last_reviewed_on": "2026-10-14"},
  "evidence": {
    "review_method": "full_official_page_text",
    "direct_agency_confirmation": false,
    "phone_source_url": "https://daas.utah.gov/locations/",
    "county_mapping_source": "https://ucoa.utah.edu/area-agencies-on-aging.php"
  }
}
```

- `regional_role`: `aging_agency` or `ombudsman` (`supported_living` only for a state-designated regional disability coordinator, as in Kentucky).
- `service_area`: exact county names from file 1. Regional records always list counties, never "statewide".

### 3. `<code>-programs.json`

Same fields as file 2, without `regional_role`. Statewide programs use `"service_area": ["statewide"]`. Never use the state's name as a service area.

`needs_supported` values: `general_navigation`, `help_at_home`, `equipment_home_accessibility`, `benefits_and_funding`, `care_facilities`, `resident_rights`, `veteran_services`, `caregiver_support`, `housing`, `dd_intake_service_coordination`.

`verification.record_status`: `official_source_reviewed` only when you reviewed the full official page or PDF; `official_search_extract_only` when only a search excerpt supports the record (these are flagged for follow-up).

`evidence.review_method`: `full_official_page_text`, `full_official_page`, `full_official_pdf`, `full_association_directory_page` or `official_search_excerpt`. `direct_agency_confirmation` is always `false`.

Writing standard for `description`, `next_step` and `constraints`: plain language a family member or facility staff member can act on. Say what to ask for. Never state that someone is eligible, that funds are available, or how long anything takes.

### 4. `routing.json`

```json
{
  "priority": ["ut-claims", "ut-aging", "ut-ship", "ut-waiver", "ut-ombudsman", "ut-at", "r02-aid-attendance-housebound", "r02-va-pension", "r02-survivors-pension"],
  "routes": {
    "benefits": ["ut-claims", "ut-ship", "ut-waiver", "r02-va-pension", "r02-aid-attendance-housebound", "va-accredited-help"],
    "survivors": ["ut-claims", "r02-survivors-pension", "r02-dic", "r02-va-burial", "va-accredited-help"],
    "care": ["ut-waiver", "ut-caregiver", "r02-va-health-enrollment", "va-location-finder", "r02-va-cnh", "r02-va-clc"],
    "rights": ["ut-ombudsman", "ut-aging"],
    "local": ["ut-aging", "ut-caregiver", "ut-waiver", "ut-at", "ut-211"],
    "housing": ["ut-211", "va-housing-help", "va-location-finder", "va-accredited-help"],
    "accessibility": ["va-hisa", "va-sah", "va-sha", "va-tra", "ut-at", "ut-waiver", "ut-aging"]
  },
  "seniorTopics": {
    "daily": ["ut-aging", "ut-caregiver", "ut-waiver"],
    "accessibility": ["ut-at", "ut-waiver", "ut-aging"],
    "vision": ["ut-at", "ut-aging"],
    "hearing": ["ut-at", "ut-aging"],
    "memory": ["alz-dementia-support", "ut-caregiver", "ut-aging"],
    "costs": ["ut-ship", "ut-waiver", "ut-aging"],
    "rights": ["ut-ombudsman", "ut-aging"]
  },
  "statewide_navigation": {"name": "...", "phone": "...", "source_url": "https://..."},
  "home_modification": {"url": "https://...", "label": "...", "guidance": "Ask the waiver administrator about assessment, written service-plan authorization and accepted providers."}
}
```

Every route and topic needs at least one id. Use your state's ids plus shared federal ids (listed in `data/public/federal-resource-ids.json`; `r02-…`, `va-…`, `cms-care-compare`, `alz-dementia-support`, `nara-discharge-records`, `crisis-988` and others).

### 5. `notes.md`

1. **Sources:** a table of every source used (URL, what it supports, date reviewed, published or revised date if shown).
2. **County boundaries:** how veterans, aging and ombudsman maps differ, splits, collisions (section G).
3. **Conflicts:** both values, both sources, both dates.
4. **Owner decisions needed:** anything Travis must decide, such as publishing a named representative.
5. **Draft coverage statement:** one sentence describing what this edition covers, in the style of the existing editions ("Initial referral edition. Four veterans regions, 12 aging agencies and 11 ombudsman regions cover all 29 counties.").
6. **Draft sharing description:** one phrase completing "Find … for every county", e.g. "regional veterans referrals, county-matched aging agencies and long-term-care ombudsmen".
7. **Self-check output:** paste the final output of the checker.
8. **Could not confirm:** a short list.

## Self-check before returning

```sh
python3 scripts/check_state_return.py research/returns/R-06-IN --state IN --name Indiana --counties 92
```

The checker needs only Python. Return only when it reports **0 errors**. Explain any warnings in `notes.md`.

## Acceptance checks

- Every county in the official list appears exactly once, with a veterans phone and source.
- Every county is served by at least one aging agency record; every county has a county-mapped or statewide ombudsman route.
- Every record has an https official link, a review date and a review method; no field is stronger than its evidence.
- Nothing is described as confirmed by an agency.
- Ids use the state's code and are unique; no service area uses the state's name.
- `notes.md` records conflicts and decisions instead of resolving them silently.

## Out of scope

Local service providers, veterans posts, senior centers, street addresses, hours, wait times, funding amounts, telephone confirmation and outreach. These come after the referral edition is published.

## Queue

Confirm each county count against the state's official list; record the official count if it differs.

| # | State | Code | Counties and equivalents | Things to check |
|---|---|---|---|---|
| 1 | Indiana | IN | 92 | Whether the state veterans agency publishes county service officers for every county |
| 2 | West Virginia | WV | 55 | Whether veterans contacts are county offices or state field offices covering several counties |
| 3 | Texas | TX | 254 | County service officers versus state veterans commission offices; scale (plan two return batches if needed) |
| 4 | Florida | FL | 67 | County veteran service officers and the state agency directory |
| 5 | California | CA | 58 | County veterans service offices; aging agencies that serve several counties |
| 6 | Virginia | VA | 133 (95 counties, 38 independent cities) | Independent cities as separate entries with `county_type`; repeated names |
| 7 | North Carolina | NC | 100 | County veterans service offices and regional state offices |
| 8 | Georgia | GA | 159 | State field offices assigned to counties; scale |

Later states follow in the order Travis sets.
