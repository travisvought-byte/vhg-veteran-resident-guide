# Roadmap: what Vet Home Guard still needs

Written November 15, 2026, from an audit of vethomeguard.org, guide.vethomeguard.org and this repository. It replaces the four-county [stage plan](stage-plan.md) as the working list. Update it when something ships or a decision changes; keep private matters (donors, cases, outreach contacts) out of it.

## Where things stand

- **Coverage.** 51 editions. Forty-nine states and D.C. have full county editions (3,068 counties and equivalents; Colorado, Alabama, Maryland, Wisconsin, Minnesota and Oklahoma added November 15, 2026, and New Jersey, Oregon, Louisiana, Nevada, Kansas, Nebraska, New Mexico, Mississippi, Idaho, South Dakota, New Hampshire, Maine, Hawaii, Delaware, Rhode Island, Vermont, Wyoming, D.C., Montana, Alaska, North Dakota, Iowa, Connecticut and Massachusetts November 16). Arkansas is still a starter edition: the state veterans agency plus national aging, ombudsman and Medicare counseling routes.
- **Evidence.** 3,335 resource records across the editions. 3,019 (90.5%) carry full official-source review, 310 were matched from search excerpts, and 6 are flagged as imported or due a recheck. Of the 1,810 veterans office contacts, 152 were matched from search excerpts. Contacts are checked against published sources, not by telephone.
- **Links.** 1,727 distinct links on 839 websites. Until this month nothing checked them.
- **Ohio extras.** 924 nursing homes and 817 assisted living facilities, the bingo finder, 88 county boards of DD in the family guide.
- **Sibling sites.** The bingo finder (ohiobingo.org), the Ohio family guide (ohiomom.org), mobility and disability resources (mobilitytalk.org) and the cannabis directory (ohioweed.org) each own their subject. This guide links to them and does not copy them.
- **vethomeguard.org.** Eight pages and four forms on a code-based Wix site. Its source is not in a repository yet. The owner's direction on November 17, 2026 (decision D-022) is that this guide becomes vethomeguard.org and covers every veteran; section 0 below is the plan.

## Done in the November 15 pass

| What | Where |
| --- | --- |
| Starter states show their contacts as soon as the state is chosen; phone header fits the first screen; footer date comes from the records; site icon | Pull request "Starter states show their contacts at once" |
| Monthly link check that opens one issue for broken or moved links | Pull request "Monthly link check" (this one) |
| A page per state that search engines can read, with every county's veterans office and phone | Pull request "A page for every state" |
| vethomeguard.org home page: search that answers by need, a state picker, links into the right part of the guide | Built and tested; waiting for the owner's go-ahead to publish |

## 0. One site for every veteran

Owner's direction, November 17, 2026 (decision D-022): Vet Home Guard and the veteran guide are one thing. vethomeguard.org is the guide, for all veterans; seniors, caregivers and long-term care are one section of it.

**Done November 17, 2026**

- Thirteen national records, each read on its official page that day, shared by all 51 editions: VA disability compensation, Supplemental Claims, the PACT Act and toxic exposure screening, the Women Veterans Call Center, Vet Centers, military sexual trauma counseling, the GI Bill, Veteran Readiness and Employment, American Job Centers, VA home loans, Veteran ID cards, discharge upgrades and VA Solid Start.
- Seven needs added to the first screen under "For every veteran": disability pay and claims, VA health care and toxic exposure, counseling and mental health, school and the GI Bill, jobs and training, records and discharge upgrades, and just left the service. Home loans joined the housing view. The older needs sit under "Seniors, caregivers and long-term care" and "Families".
- The guide is titled Veteran Resource Guide. Link labels on the bingo, facilities, family and advocacy pages still say "Veteran Resident Resource Guide"; change them with the address move, when every page is rebuilt anyway.

**Topics still to research and add** (official sources only, same record format): the other decision review options (Higher-Level Review, Board Appeal), CHAMPVA and other family health benefits, VA dental care, VA life insurance, veteran-owned small business help, federal hiring preference, transition classes before discharge, National Guard and Reserve benefits, Veterans Justice Outreach and veterans treatment courts, and each state's own benefits (property tax relief, tuition, licenses) from its veterans agency.

**One address** (steps 4 and 5 need the owner)

1. Bring the eight vethomeguard.org pages (home, refer, volunteer, partner, sponsor, about, contact, donate), their stylesheet and their Wix form scripts into this repository, and check each form loads from here.
2. Give the guide the same header, menu and look, so it reads as one site. Rebuild the first screen at the same time; it runs about 29 phone screens today.
3. Change the published address to `https://www.vethomeguard.org/` in `scripts/state_registry.py` (`BASE_URL`), the sitemap, `robots.txt`, canonical tags and new QR codes.
4. Point `www.vethomeguard.org` and the bare domain at this site: the A and www CNAME records in the Wix account, and the custom domain in this repository's Pages settings. Email records are not touched. Do this and step 3 together, DNS first, so no link points at a page that is not there yet.
5. Keep `guide.vethomeguard.org` forwarding, path for path, so printed QR codes and flyers keep working. GitHub Pages serves one custom domain per repository, so this needs a small forwarding repository (the bingo and cannabis subdomains were retired the same way).
6. Tell Search Console about the change of address and resubmit the sitemap.

## 1. Be found

The guide is one address to a search engine. The state a visitor chooses is drawn by script, and every state view names the home page as its canonical address, so "Knox County veterans service office phone" cannot land on this guide today.

1. **A page per state** (in review, see above). Plain HTML built from the same records, one per state, linking into the full guide.
2. **A page per county** for the twenty-eight full editions (2,227 pages), built the same way. Each needs only the office, phone, source, review date and a link into the guide for that county. Do this after the state pages have been indexed for a few weeks, so the result can be measured.
3. **Search Console** for guide.vethomeguard.org and vethomeguard.org: submit both sitemaps and watch which searches bring people in. Needs the owner to add one DNS record.
4. **Link previews.** `bingo.html`, `facilities.html`, `flyers.html`, the share pages and the assistant have no preview image, and the assistant has no description.

## 2. Go deeper where veterans live

5. **Turn starter states into county editions**, largest veteran populations first (Census ACS table S2101 gives the order; Colorado, Alabama, Maryland, Wisconsin, Minnesota, Oklahoma, New Jersey, Oregon, Louisiana, Nevada, Kansas, Nebraska, New Mexico, Mississippi, Idaho, South Dakota, New Hampshire, Maine, Hawaii, Delaware, Rhode Island, Vermont, Wyoming, D.C., Montana, Alaska, North Dakota, Iowa, Connecticut and Massachusetts are done; the rest follow in that order). `scripts/make_county_state.py` builds a full edition from one research sheet, `data/source/states/<code>.json`; the method is in [ADDING-A-STATE.md](ADDING-A-STATE.md). In states without county veterans offices, map each county to the state field office that serves it, as Kentucky, Utah, Georgia and Virginia do.
6. **Raise the search-excerpt records to full source review.** Read the official page and record what it says. The 310 are one shared Medicare record repeated in each edition plus 260 state records: aging agencies, legal aid, ombudsman offices, VA health systems and state programs. California (25), Washington (18), Tennessee (15) and Arizona (14) hold the most, and each starter state has three or four national routes to re-read. The 152 office contacts come next.
7. **Nursing homes for every state.** The Ohio finder is built from a CMS file that is national. The same builder can publish each state's nursing homes; assisted living stays Ohio-only until another state's licensing list is added.
8. **Posts in the four pilot counties.** [COMMUNITY-NETWORK.md](COMMUNITY-NETWORK.md) describes the record; `data/public/community-posts.json` is still empty.

## 3. Stay right without hand-checking

The standing rule is that published contacts are not rechecked by phone and are corrected when someone reports a problem. These keep that promise honest.

9. **Act on the link report each month.** When the issue "Guide links to review" opens, correct the listed records from the publisher's own site and rebuild. A scheduled assistant task can open that pull request on its own.
10. **Refresh the two Ohio facility files** when CMS and the Ohio Department of Health publish new ones ([FACILITIES.md](FACILITIES.md) has the steps). Monthly for CMS.
11. **A backup maintainer**, and a stated turnaround for corrections (issue #47). One person holds every key today.
12. **Retire the November fundraiser** banner and `november-campaign.html` on December 1.

## 4. Easier to use

13. **Search that understands plain words.** The guide's search needs the exact phrase: "widow" finds nothing, though survivor help is there. Give it the same word list the vethomeguard.org home page now uses, and let several words match in any order. State adapters replace parts of the results code, so change it once in the shared runtime and test every state.
14. **Five real users** (issue #46): a veteran, a surviving spouse, a family caregiver, a senior who is not a veteran and a facility worker each try one real task. Nothing else will show whether the first screen makes sense to them.
15. **Spanish.** The family guide's Spanish is a machine-assisted draft waiting for a native speaker. The main guide has no Spanish at all; start with the first screen and the crisis numbers.
16. **Print on paper and on an iPhone.** Automated checks cover layout; nobody has printed the handoff on a real printer.

## 5. vethomeguard.org

17. **Publish the new home page** (ready).
18. **Put the site's source in a repository** with the same check-and-publish workflow the OhioMom repository uses, so every change can be reviewed and undone. Needs an empty repository and three Wix secrets from the owner.
19. **A privacy page.** The referral form collects details about a third person. Say what is collected, who sees it and how long it is kept.
20. **One public email address.** The guide uses travis@vethomeguard.org and the site uses the Gmail address.
21. **Say what a gift pays for** on the donate page, in the owner's own numbers.
22. **Count page views** on the site the way the guide does (GoatCounter, page views only), so the search box can be judged by use.

## 6. Needs a decision before any building

- **Service provider directory with hourly rates.** Who may be listed (license, insurance), who checks, how rates are collected and kept current, and which county goes first. A provider form and one county are enough to start.
- **Guided assistance (beta).** Either run the five-user pilot and finish it ([ASSISTANCE_MVP.md](ASSISTANCE_MVP.md)), or fold its checklists into the main guide and retire the separate page.
- **Review of the boundary wording** by an attorney or accredited representative, so the guide keeps routing people to free accredited help and never reads as claims advice.

## Not planned

- Telephone confirmation of contacts, and "unverified" warnings on listings.
- Collecting or storing anything about a resident.
- Ranking or rating facilities.
