# Michigan expansion

Published-source review: October 8, 2026. The Michigan edition is `mi.html`, with its QR flyer and newsletter introduction in `share-mi.html`. Ohio remains the default edition; the selector links all four state editions.

## Coverage

- Veterans referral routes for all 83 counties: 77 use the Michigan Association of County Veteran Counselors (MACVC) public directory and six use official county, provider or state pages.
- 82 county or regional veterans contacts. Ionia uses the MVAA statewide referral number, clearly labeled as a referral to the new county office rather than a direct county phone.
- 16 regional aging agencies cover all 83 counties. Each county has one match except Wayne, which has two agencies with explicit city boundaries.
- 58 resource records: 33 shared federal/national records, 14 Michigan programs and 16 aging agencies.
- County handoffs, senior and disability topics, accessibility planning, private audience share links and a Michigan QR sharing kit.
- Dedicated local ombudsman numbers, individual post contacts, repair providers and local funding availability remain research work. Ombudsman help uses the verified statewide routing number.

## Source and contact evidence

MACVC's public county lookup and counselor profiles were read in full. The chosen phone is normally the most frequently listed number across that county's profiles, with a published veterans extension preferred when available. This selects a published contact, not a telephone-confirmed central intake line. The guide displays the association source accurately; it does not label association pages as government verification. Profile URLs, source hashes, county lookup URLs and review dates are retained. Personal profile biographies and email addresses are not copied into the guide.

Six gaps in the association directory use independent full-page review:

| County | Referral | Source |
|---|---|---|
| Barry | 269-945-1296; county services coordinated through Barry County United Way | [Provider page](https://www.bcunitedway.org/get-help/veteran-affairs/) |
| Branch | 517-279-4322 | [County office](https://branchcounty.gov/departments/va/) |
| Clinton | 517-887-4390; shared Ingham/Clinton service | [County page](https://www.clinton-county.org/458/Veterans-Services) |
| Ionia | 800-642-4838; MVAA statewide referral to the new county office | [July 30, 2026 state announcement](https://www.michigan.gov/mvaa/news/2026/07/30/mvaa-veteran-service-officer-available-at-new-ionia-county-veterans-services-office) |
| Jackson | 517-788-4425 | [County directory](https://mijackson.org/Directory.aspx?did=86) |
| Saginaw | 517-898-7902; county-supported YMCA Veterans Service Hub | [County page](https://www.saginawcountymi.gov/departments/county-administrator-and-finance/veterans-services/) |

Leelanau's MACVC lookup lists Grand Traverse County Veterans Affairs. This shared arrangement is shown explicitly and should be confirmed at intake. Berrien retains the published extension 8224; Missaukee retains extension 507. Counselors can have different direct work numbers; published directory entries do not establish current appointment availability or accreditation beyond the publisher's description.

All 14 Michigan program pages were read in full and retain source hashes. Michigan's current SHIP and care counseling route is MI Options, 800-803-7174. MATP device trials and loans use 800-578-0280. Disability Rights Michigan uses 800-288-5923. These are separate organizations; MDRC/MATP and DRM are not interchangeable. Home Help covers approved personal assistance and explicitly excludes home repairs. MI Choice environmental adaptations require separate eligibility, assessment and service-plan authorization.

Aging county boundaries come from the [official MDHHS aging-agency directory](https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Adult-and-Childrens-Services/Adults-and-Seniors/BPHASA/AAAs_Counties-Served_Phone-Numbers.pdf?hash=BB954F66F011910DAD158209ABAEE29B&rev=82e44c5b933747a9b8fcc00edb69600e), revised October 30, 2024 and still linked from MDHHS. Its full text was reviewed and its hash retained. Twelve agency phones also use full agency-owned webpage review. Four phone sources retain full official PDF review: Kalamazoo, Region IV, Western Michigan and NEMCSA Region 9. The 2024 directory date is preserved separately from the October 2026 review date; this does not claim a new publication or direct agency confirmation.

Wayne County's two aging contacts are shown together in county, senior and accessibility handoffs:

| Agency | Service boundary within Wayne County |
|---|---|
| Detroit Area Agency on Aging (1A), 313-446-4444 | Detroit, Hamtramck, Highland Park, Harper Woods, Grosse Pointe, Grosse Pointe Farms, Grosse Pointe Park, Grosse Pointe Shores and Grosse Pointe Woods |
| The Senior Alliance (1C), 734-722-2830 | Wayne County communities outside those nine cities |

The aging map is not a MI Choice waiver-provider assignment. MI Choice has its own provider list and overlapping service arrangements. The guide links the official waiver-agency list for screening and uses the person's supports coordinator for enrolled participants.

## Maintenance and validation

Canonical sources: `data/public/mi-programs.json`, `data/public/mi-regional-referrals.json` and `data/public/michigan-county-veterans-offices.json`. The builder generates the self-contained Michigan page, combined resource JSON and sharing page. Source-review labels for shared federal records are retained.

Run `python3 scripts/build_public.py --check`, `python3 scripts/validate_public.py` and `node tests/michigan.cjs`. Michigan's test suite also runs Ohio, Pennsylvania and New York regression checks, covering every county, both Wayne city scopes, labeled state fallback, extensions, nonmilitary senior routes, accessibility branches, print actions, source isolation and four-state switching.

Automated print checks exercise content and print actions, not visual pagination. Browser, mobile, accessibility and visual print review remain pending. No telephone confirmation or outreach has been performed. No eligibility determination or funding commitment is made by the guide.
