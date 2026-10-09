# Veteran Resident Resource Guide: Ohio, Pennsylvania, New York, Michigan and Kentucky

A free Veteran Home Guardians (VHG) guide for veterans, surviving spouses, seniors, people with disabilities, families and care teams. It helps people find their first contact and prepare a useful referral.

**Live guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/

**Pennsylvania guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/pa.html

**Pennsylvania sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share-pa.html

**New York guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/ny.html

**New York sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share-ny.html

**Michigan guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/mi.html

**Michigan sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share-mi.html

**Kentucky guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/ky.html

**Kentucky sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share-ky.html

**Ohio sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share.html

**Publisher and project owner:** Travis Vought, Founder & Chair, Veteran Home Guardians. Contact: travis@vethomeguard.org.

## Coverage and verification

All five state editions are published referral backbones, not complete inventories of local services. Ohio local research is strongest in the four pilot counties; Pennsylvania, New York, Michigan and Kentucky are initial referral editions. The state picker switches between separate datasets rather than suggesting identical depth of coverage.

Each edition displays its county coverage and automatically calculated verification totals near the state picker. Every resource card shows its source status without requiring an expansion. Search-excerpt, imported and recheck records carry a visible verification notice, including in printed resource lists. A published source review does not mean an agency confirmed its current intake or availability.

## Ohio scope

- Veterans office contacts for all 88 Ohio counties, plus matched aging agency and long-term-care ombudsman contacts.
- 115 resource records, displayed as 111 cards after removing four duplicate legacy county office cards.
- Veterans benefits, surviving-spouse support, care, housing and resident rights routes.
- Ramps and home accessibility: HISA, adapted housing, Ohio waiver routes, rural repair and discharge coordination, with an application checklist and paper follow-up tracker.
- A dedicated seniors and disability section without a military-service requirement.
- Official American Legion, AMVETS and VFW locators. Individual county post contacts and a contractor network are not yet populated.
- Printable county handoffs, audience-specific share links, a one-page QR flyer and newsletter introduction.

Statewide referral coverage is not an exhaustive statewide inventory of local services. Local program research remains strongest in Morrow, Knox, Marion and Delaware. Most county phones come from a source publication; hours, intake and availability must be confirmed with the office. See [coverage and evidence](docs/STATEWIDE.md).

## Pennsylvania expansion

The state selector opens a separate Pennsylvania edition in this repository. It contains all 67 county veterans contacts from PA DMVA’s September 2026 directory, 17 PA-specific program/referral records, 33 shared federal/national records and 58 local referral records, for 108 resources. Every PA county now has a local aging referral phone; four counties have separately sourced local ombudsman routes, with statewide routing elsewhere. Of the 58 local records, 56 have full official source review and two are labeled search excerpt only. See [Pennsylvania coverage and sources](docs/PENNSYLVANIA.md). Ohio remains the default, preserving its published links and QR code.

## New York expansion

New York has veterans referral contacts and exactly one matched aging office for all 62 counties, including NYC's five boroughs. NYC veterans intake is citywide, Essex uses a state benefits office, and the shared Warren/Hamilton aging office is mapped to both counties. The edition contains 107 resources: 33 shared federal/national records, 17 New York programs and 57 local aging offices. Ombudsman support uses statewide routing. Borough aliases work in county links and office search. Chemung and Chenango phones use county-owned sources to resolve conflicting state directory entries. See [New York coverage and sources](docs/NEW-YORK.md).

## Michigan expansion

Michigan has veterans referral routes and aging contacts for all 83 counties. It includes 82 county or regional veterans contacts plus a labeled MVAA statewide referral for Ionia's new office. Of the 83 routes, 77 use the county counselors' association directory and six use official agency pages. Sixteen aging agencies cover the state; Wayne County shows both regional agencies with their city boundaries. The edition contains 63 resources: 33 shared federal/national records, 14 Michigan programs and 16 aging contacts. MI Options handles care and Medicare counseling; the ombudsman route is statewide. See [Michigan coverage and evidence](docs/MICHIGAN.md).

## Kentucky expansion

Kentucky has KDVA regional benefits representatives, aging contacts, district ombudsmen and Hart-Supported Living coordinators for all 120 counties. The service maps are kept separate, with multiple veterans representatives and the Fort Campbell assignment preserved. The edition contains 86 resources: 33 shared federal/national records, 17 Kentucky programs, 15 aging contacts, 15 district ombudsmen and six supported-living coordinators. It includes HCB waiver screening, Homecare, Medicare counseling, vision/hearing support and temporary RampUp! KY loans. See [Kentucky coverage and evidence](docs/KENTUCKY.md).

## Bingo and urgent support

The [Ohio bingo section](https://travisvought-byte.github.io/vhg-veteran-resident-guide/bingo.html) starts with six researched venues in Morrow, Knox, Delaware and Marion. Charitable sessions and senior-center activities have separate filters. Cardington and Marengo activity are firsthand-confirmed by Travis; schedules, prices, licenses and accessibility retain their own limits. No statewide bingo inventory is claimed. See [bingo evidence and expansion](docs/BINGO.md).

All five editions have a prominent urgent-help section, crisis and mental-health resources, and expanded homelessness pathways: the VA national call center, SSVF community providers, HUD-VASH and VA Community Resource and Referral Centers. Local shelter beds, individual provider intake and availability are not comprehensively mapped.

## Corrections from users

Every listing and county panel has a “Report a problem” link. It opens an email to travis@vethomeguard.org with the state, record ID and county already filled in, plus a reminder not to include resident details. Corrections go to email rather than public GitHub issues so nothing a user writes is published. The sharing kits invite facility staff and partners to use it.

## Operating boundaries

The guide routes people to agencies; it does not decide eligibility, prepare claims or promise funding. Claims assistance belongs with accredited representatives. No resident records or application information are collected. Keep personal information out of GitHub issues. Listing an organization does not imply a partnership or endorsement.

## Update and verify

Ohio canonical public program data lives in `prototype-data.json`; canonical county contacts live in `data/public/ohio-county-veterans-offices.json`. Edit those sources, preserve evidence and review dates, then run:

```sh
python3 scripts/build_public.py
python3 scripts/build_public.py --check
python3 scripts/validate_public.py
node tests/feedback.cjs
```

PA canonical programs live in `data/public/pa-programs.json`, with local aging/ombudsman records in `data/public/pa-regional-referrals.json`, separate county veterans contacts and an explicit shared-resource whitelist. The build updates Ohio embedded data and its regional projection, then generates `pa.html`, the combined PA resource JSON and `share-pa.html`. The page stays self-contained, with no runtime data service. GitHub Actions runs these checks for pushes and pull requests. Checks cover county mappings, routes, sharing behavior and data synchronization; they do not establish WCAG compliance, remote link availability or print pagination. Browser and print review remain necessary.

New York canonical records live in `data/public/ny-programs.json`, `data/public/ny-regional-referrals.json` and `data/public/new-york-county-veterans-offices.json`. The same build generates `ny.html`, `data/public/new-york-resources.json` and `share-ny.html`. `tests/new-york.cjs` runs the Ohio and Pennsylvania regressions plus New York checks. Ohio remains the default edition, with existing URLs and QR codes preserved.

Michigan canonical records live in `data/public/mi-programs.json`, `data/public/mi-regional-referrals.json` and `data/public/michigan-county-veterans-offices.json`. The build generates `mi.html`, `data/public/michigan-resources.json` and `share-mi.html`. `tests/michigan.cjs` runs all four editions' checks.

Kentucky canonical records live in `data/public/ky-programs.json`, `data/public/ky-regional-referrals.json` and `data/public/kentucky-county-veterans-offices.json`. The build generates `ky.html`, `data/public/kentucky-resources.json` and `share-ky.html`. `tests/kentucky.cjs` runs all five editions' checks, and `tests/feedback.cjs` runs those plus the correction-link checks.

Older integration scripts and research candidates are historical research tools, not the public build. Do not publish their output over the current public data without review.

## Maintenance and next research

See the [maintenance process](docs/MAINTENANCE.md), [verification queue](docs/VERIFICATION-QUEUE.md) and [distribution plan](docs/DISSEMINATION.md). Source review is not telephone confirmation. No outreach was sent as part of this update.

## Repository layout

| Path | Purpose |
|---|---|
| `index.html` | Public guide, interface and generated embedded data |
| `bingo.html`, `data/public/ohio-bingo.json`, `docs/BINGO.md` | Ohio bingo page, canonical venue records and source/expansion notes |
| `share.html`, `share-pa.html`, `share-ny.html`, `share-mi.html`, `share-ky.html` | State-specific QR flyers and newsletter introductions |
| `pa.html`, `ny.html`, `mi.html`, `ky.html` | Generated Pennsylvania, New York, Michigan and Kentucky editions |
| `assets/` | VHG logo, QR code and social preview image |
| `prototype-data.json` | Canonical current public resource records |
| `data/public/` | County contacts, generated regional projection and future post directory |
| `scripts/build_public.py`, `scripts/pa_edition.py`, `scripts/ny_edition.py`, `scripts/mi_edition.py`, `scripts/ky_edition.py` | Public data synchronization and state edition generation |
| `scripts/validate_public.py`, `tests/*.cjs` | Data, asset and functional checks |
| `docs/` | Scope, maintenance, evidence and research priorities |
| `research/`, `data/integrated/`, `data/seed/`, `data/batches/` | Historical working material; not the live source of truth |

Ohio includes four additional source-reviewed aid routes: county-based civil legal aid, American Legion Department Service Officers, utility assistance and DAV medical transportation. The Ohio aid view links these routes and directs emergency financial assistance questions to the selected county veterans office. Statewide routing does not guarantee local services, eligibility or funding.
