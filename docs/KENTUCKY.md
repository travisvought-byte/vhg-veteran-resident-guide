# Kentucky expansion

Published-source review: October 8, 2026. The Kentucky edition is `ky.html`; its QR flyer and newsletter introduction are in `share-ky.html`. The selector and sharing navigation connect all five editions. Ohio remains the default.

## Coverage

- All 120 counties have KDVA regional benefits representatives. These are county-to-region referrals, not claims that each county operates its own office.
- 138 county-to-representative assignments preserve multiple contacts where published. Christian County includes a separately labeled Fort Campbell assignment alongside its general regional contact.
- 15 regional aging and disability contacts cover every county exactly once.
- 15 district long-term-care ombudsman contacts cover every county exactly once. These use a dedicated ombudsman directory rather than assuming general aging intake handles advocacy.
- Six Hart-Supported Living coordinator regions cover every county exactly once, independently of veterans and aging districts.
- 81 resources: 28 shared federal/national records, 17 Kentucky programs and 36 regional records.
- County handoffs, nonmilitary senior and disability routes, accessibility planning, private audience share links and a Kentucky QR sharing kit.

## Sources and evidence

The [KDVA county directory](https://veterans.ky.gov/Benefits/Pages/Your-Benefits-Representative.aspx), [CHFS aging and disability directory](https://www.chfs.ky.gov/agencies/dail/Pages/adrc.aspx), [state-endorsed district ombudsman directory](https://ombuddy.org/find-an-ombudsman/) and [Hart-Supported Living directory](https://www.chfs.ky.gov/agencies/dail/Pages/hslp.aspx) were read as full retrieved official page text, including all county entries. The [CHFS ombudsman page](https://www.chfs.ky.gov/agencies/dail/Pages/ltcomb.aspx) identifies the state program and links its ombudsman provider. Kentucky government sites rejected direct HTML downloads; full indexed page text was available. Evidence therefore records `full_official_page_text` and SHA-256 of normalized retrieved text, rather than claiming a raw HTML fetch or telephone confirmation. Source URLs, review dates and separate phone/coverage evidence remain in canonical JSON.

County names are normalized to Kentucky's canonical spellings. The Hart source contains Larue, Metcalf, Gerrard, Nichols and Elliot; these map to LaRue, Metcalfe, Garrard, Nicholas and Elliott. Punctuation in published phones is normalized without changing digits. The malformed Lake Cumberland ADRC phone is independently corroborated as 270-866-7092 on its [agency-owned staff page](https://www.lcadd.org/aging-and-independent-living-staff/).

The maps are independent. For example, Carroll's KDVA representatives belong to region 8, its aging/ombudsman district is Northern Kentucky, and its Hart coordinator is region 4. Kentucky's Ohio County is handled as a county; it is never treated as a statewide service-area synonym.

All 17 Kentucky program pages received full page-text review. Shared federal/national records retain their existing evidence labels. Important program distinctions are visible:

- SHIP uses 877-293-7447, **menu option 2**, not a telephone extension.
- HCB requires separate Medicaid financial eligibility, disability or age criteria and nursing-facility level of care. The reviewed page reports a waiting list; confirm current status and service-plan approval.
- Homecare serves eligible adults age 60+ at risk of institutional care. Waiting lists and locally offered services vary.
- [RampUp! KY](https://www.katsnet.org/rampup/) loans temporary portable ramps for up to six months, with limited inventory. It does not build ramps. Applicants arrange pickup, return, setup and installation; suitability is not guaranteed.
- KATS equipment loans may have nominal fees, late fees and shipping costs. Assistive technology financing is an approved loan requiring repayment, not a grant.
- National Family Caregiver Support and the Kentucky grandparent caregiver program have different eligibility rules.
- TAP specialized-phone applications require a qualifying communication disability and the published one-year Kentucky residency condition.
- The KDVA homelessness-prevention page links an FY 2026 application. Confirm the current cycle, form and funding; its rent/utility assistance is not a general repair grant.
- Hart-Supported Living requires an application and funding review. A coordinator referral does not establish grant approval or current funding availability.

## Maintenance and validation

Edit `data/public/ky-programs.json`, `data/public/ky-regional-referrals.json` and `data/public/kentucky-county-veterans-offices.json`. The builder generates the combined resource JSON, self-contained page and sharing kit.

Run `python3 scripts/build_public.py --check`, `python3 scripts/validate_public.py` and `node tests/kentucky.cjs`. Kentucky's test suite includes all earlier state regressions and checks every Kentucky county's separate maps, all listed veterans representatives, Fort Campbell scope, dedicated ombudsman extensions, SHIP menu handling, county isolation, senior and accessibility routing, print actions, sharing privacy and five-state switching.

Telephone confirmation, current funding and capacity checks, individual post contacts, repair providers, browser/mobile/accessibility review and visual print pagination remain pending. Automated print checks establish actions and content, not visual layout. No outreach has been sent and no resident information is collected.
