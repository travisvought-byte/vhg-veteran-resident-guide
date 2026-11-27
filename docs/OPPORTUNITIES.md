# Veteran programs, grants and events

https://guide.vethomeguard.org/opportunities/ puts in one place the programs, grants, scholarships, events, discounts,
retreats and state benefits open to veterans and their families, one page per state, local ones first. Started
November 27, 2026 with Ohio, then Pennsylvania and Michigan, the two states that publish their programs most completely
(see "Next states" below).

## What a reader sees

- **A state page** (`opportunities/oh/`): pick your county and the page moves the programs that name it to the top,
  then programs elsewhere in your region, then statewide ones, then local ones in the rest of the state, then
  programs open in every state, then ones worth the trip. Pick a kind of help to see only that kind. Without
  scripts every program is still listed, statewide first. `?county=delaware&cat=education` opens a page already
  filtered; every Ohio county office page links to its state page that way.
- **Every listing**: what it is, who can apply, how and where to apply (with the program's own link and phone), the
  deadline or date, where it happens and what travel is covered, the cost, how many it serves and the odds of getting
  in, the source page and the date it was read. Each also has its own page (`opportunities/oh/<slug>.html`) for search.
- **Deadlines and dates coming up**: counted from the newest checked date in the data, not from the day the site is
  built, so a rebuild gives the same page.
- **The nationwide page** (`opportunities/us/`): full listings for programs open in every state and those worth the
  trip. Every state guide links to its own state's page, or to this page until its state is added.
- **Business funding** (`opportunities/business/`): every grant, pitch prize and fund for veteran and military
  spouse business owners (a `business` listing with an `award`), in a captioned table of award, equity and whether
  you can apply now, then as full listings grouped open now (nearest deadline first), open year-round, by invitation
  only and between rounds. Below them: what we could not confirm, and the training and help listings. The hub, the
  nationwide page, every state page and every business listing link to it. Added November 27, 2026 from a widely
  shared list of 12 veteran business grants; each was read on its own site, and figures the list gave that the
  programs don't publish are under "What we could not confirm".

## How many it serves, and the odds

Shown only when the program publishes the figure, with the page and the year it covers:

- `capacity.served`, `applicants`, `slots`, `waitlist`: the program's own words, figure by figure.
- `odds`: `{"text", "basis"}`. `published` when the program states its acceptance rate or that it funds every
  eligible applicant; `computed` when we divided its published awards by its published applicants (the page says
  "our arithmetic from the program's own figures").
- Nothing published means the listing says "not published by the program". We never estimate.

## Data

`data/opportunities/<st>.json` holds one state's statewide, county and regional programs;
`data/opportunities/national.json` holds programs open in every state (`scope: national`) and ones held in one place
(`scope: travel`). Each listing:

| Field | Meaning |
| --- | --- |
| `id` | `<st>-` or `us-` and a short slug; the page address drops the prefix |
| `name`, `organization`, `summary`, `eligibility`, `how_to_apply` | Plain text, in our words, from the program's page |
| `category` | `benefits`, `money`, `education`, `housing`, `jobs`, `business`, `health`, `recreation`, `tickets`, `events`, `family`, `volunteer` |
| `apply_url`, `phone` | The program's own application page and phone |
| `deadline`, `deadline_date` | The deadline or date in words, and as `YYYY-MM-DD` when there is one |
| `scope`, `state`, `counties`, `regions` | `state`, `county`, `region`, `national` or `travel`; the counties a local program names, or the region when it names none |
| `host` | For a travel program held in a state with a page: `{"state", "counties"}`, so it shows as local there (the Golden Age Games in Cleveland) |
| `location`, `travel`, `cost` | Where it happens, what travel is covered, what it costs |
| `award`, `equity` | Business funding only: what it pays, in the program's words, and `true`, `false` or `null` (not stated) for whether it takes a share of the business. On these listings `deadline_date` is the application deadline, never an event date |
| `invite_only` | `true` when you can't apply directly (you get in through the program's own course or boot camp) |
| `unconfirmed` | A figure or rule shared elsewhere, or conflicting on the program's own pages, that we could not confirm |
| `capacity`, `odds` | See above |
| `source_url`, `source_title`, `checked_on` | The page read and the day |
| `evidence` | The ladder in [MINING.md](MINING.md). Only **A** and **B** are published; **C** (search excerpt only) waits for a full read |
| `status` | `open`, `rolling`, `paused` or `closed`; `closed` is not published |
| `found_via` | `meta_ad_library:<ad id>` when an ad led us to it, `shared_funding_list_<date>` for the business funding list; the details still come from the program's own site |
| `notes` | What the page did not say, conflicts, what to recheck |

Ohio regions (Northwest, Northeast, Central, Southwest, Southeast) are in `scripts/build_opportunities.py`; they order
programs, they are not official boundaries.

## Facebook and Instagram ads

The public [Meta Ad Library](https://www.facebook.com/ads/library/) opens without signing in and shows every active
ad for a search term. It is read in a browser (it loads by script) and logged as a `manual` source in
`data/mining/sources.json`. An ad is a lead (evidence E): we find the organization's own website by search, never
through the ad, read the program page and only then list it, with `found_via` naming the ad. Each pass's outcomes go
in `data/mining/opportunity-leads/meta-ad-library-<date>.json`: ads reviewed, how many were programs, commercial
or lead generation, and for each program ad whether it was listed, already covered, held or out of scope.

First pass, November 27, 2026: 466 ads across 20 search terms (Ohio cities, Honor Flight, stand downs, grants,
scholarships, retreats, job fairs, housing); 42 were about veteran programs and 15 of those led to 17 listings. Most of
the rest were for-profit schools, lenders and lead-generation forms, which are never listed.

## Rebuild and check

```
python3 scripts/build_public.py         # writes opportunities/, assets/opportunities.js, the state links, county blocks and sitemap
python3 tests/opportunities.py          # data rules, published-only figures, pages, links, sitemap
node tests/opportunities.cjs            # the county and kind-of-help picker (jsdom)
```

To add a state: write `data/opportunities/<st>.json` (same fields), add its regions to `REGIONS` if it has local
programs, rebuild. Its guide page then links to its own page instead of the nationwide one.

## Next states

Ranked November 27, 2026 by how completely each state publishes its own programs on one official page or guide:
Pennsylvania and Michigan (done), then New Jersey (2026 benefits guide), Georgia (2026 resource guide), Florida (2026
benefits guide), West Virginia and Kentucky (Ohio neighbors; Kentucky's summary is undated and needs each item
rechecked), Tennessee, Illinois and Indiana.

## Still to check

- Ohio's controlled hunts for hunters with mobility impairments: ohiodnr.gov and wildohio.gov refused every read.
  The Cuyahoga County homeless stand down (no 2026 or 2027 date or eligibility published) and Delaware County's
  visiting-veterans volunteer program (described only in a flyer image) wait for a readable page.
- Ad leads not yet read on their own sites: Warrior Bonfire Program, America's Warrior Partnership, the USAA and Alamo
  Bowl spouse scholarship, and 75th Ranger Adaptive Sports. The Semper Fi Buckeye Foundation is held until it runs its
  first experience (planned for 2027).
- Ohio programs rarely publish how many they serve; only 3 of 73 Ohio listings carry a figure.
- Texas has a page only for the TWU Veteran Entrepreneur Grant so far; its own programs are not gathered yet. Whether
  that grant is open to men needs TWU's answer (its FAQ and guidelines disagree).
- Business funding between rounds (Veteran Shark Tank, Founders First, VetsinTech, Clemson, Women Veterans Giving,
  Farmer Veteran Coalition, TWU, Warrior Rising): recheck for next-round dates; Rice's 2027 application deadline is
  not published yet.
