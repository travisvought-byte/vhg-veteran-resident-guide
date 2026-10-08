# Veteran Resident Resource Guide (working title)

A Veteran Home Guardians (VHG) resource that helps long-term care facility staff, residents and families identify veteran and surviving-spouse residents and connect each one to the right County Veterans Service Office, with verified routes to general aging and disability help.

**Status:** Public statewide resource guide. County veterans office contacts cover all 88 Ohio counties. Most county phones are source-published entries from the Ohio AMVETS 2025–2026 Guidebook; individual offices have not all been directly confirmed. The older research files remain working material.

**Coverage:** All 88 Ohio counties for county veterans office contacts and statewide/federal referral routes. Local program research remains strongest in the original Morrow, Knox, Marion and Delaware pilot.

**Live guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/

See [statewide coverage and sources](docs/STATEWIDE.md) for scope, provenance and maintenance details.

**Project owner:** Travis Vought, Founder & Chair, Veteran Home Guardians.

---

## 1. Why this exists

Ohio already publishes the general pieces:

- County Veterans Service Office listings (Ohio Department of Veterans Services; VA Central Ohio county resource pages; Ohio Legal Help).
- Facility search and comparison (Ohio Department of Aging's Long-Term Care Consumer Guide / quality navigator; CMS Care Compare).
- Aging and disability navigation (Area Agencies on Aging through the Aging and Disability Resource Network; 211; county boards of developmental disabilities).

What we did not find is an Ohio resource written for **facility staff** that helps them ask residents about military service, recognize when a veteran or surviving spouse may be missing benefits, and hand that person to their county office. Other states have built this (for example, the Missouri Long-Term Care Ombudsman veteran/spouse benefits packet). That facility-facing gap is the purpose of this project.

The existing listings also disagree with each other. Two of the four pilot county offices show different street addresses across official sources. A handoff only works if the contact is right, so verified, dated county office records are the core asset.

This project links to existing resources rather than rebuilding them.

**Scope clarification — October 6, 2026:** This is a resource guide for veterans, surviving spouses, families and care-facility staff. Care facilities are an audience and a separate VHG outreach list, not an inventory in the guide. The 25 historical facility candidates stay in the seed for outreach only. Facility/provider listings are not required for guide completion; relevant support-program entry points remain resources.

## 2. Audiences

| Audience | What they need |
|---|---|
| Facility social workers, admissions and discharge staff | A screening question, a short list of benefit topics worth raising, and the correct county office for each resident |
| Residents and families | Plain language: who to call, what to bring, what to ask |
| County Veterans Service Offices | Referrals that arrive in the form they prefer, with the right documents |
| VHG Guardians | A consistent reference to leave with facilities and use on visits |

## 3. Deliverables

1. **County Veteran Handoff Sheet** (one per county, printable). Confirmed county office contact, hours and visit options, what to bring, what to ask for, nearest VA clinic, and the general help lines.
2. **Facility Staff Guide** (short, printable). How to ask about service at admission and later, benefit topics to raise with the county office, what staff should and should not do, and a warning about benefit advisers who charge fees.
3. **Searchable directory** (static site built from this repository's data). County, need and audience filters; every listing shows its source, last-checked date and verification level.
4. **Verified dataset** with provenance for every published field.
5. **Maintenance process**: named owner, review schedule, correction route.

## 4. Scope

**In scope:** veteran and surviving-spouse routing in the four pilot counties; a linked layer of general aging and disability entry points (any disability, any age) with one line of guidance each; the long-term care facility setting.

**Out of scope for the pilot:** rebuilding facility comparison tools; inventories of home-care agencies or vendors; statewide coverage; eligibility determinations; claims preparation; any handling of resident information.

**Expansion rule:** the county office layer can extend across Ohio's 88 counties only after the pilot shows facilities use it and someone owns maintenance.

## 5. Operating boundaries

These hold for every deliverable.

1. **Route, never decide.** The guide tells people where to go and what to ask. Eligibility belongs to the VA, the county office or the program administrator.
2. **County offices handle claims.** VHG, Guardians and facility staff do not prepare or file VA claims. Accredited county service officers do. (Research task R-03 confirms the exact accreditation rules.)
3. **No resident data.** Nothing about any resident is collected, stored or committed to this repository. The guide supports a handoff; it does not track one.
4. **No implied partnership.** Listing an agency or facility does not mean it works with VHG. VHG is identified as publisher.
5. **Evidence before publication.** Every published field traces to a source with a review date. AI-assisted research is analyst support; a person verifies and approves before anything is published.
6. **Amounts and deadlines carry their effective period.** Nothing is carried into a new year without recheck.

## 6. Critical parts

If only these are done well, the project succeeds:

1. Four confirmed county office records, including each office's preferred referral method and whether it serves residents who cannot travel.
2. A one-page staff guide that fits into the admission routine.
3. A boundary statement that keeps VHG and facility staff on the right side of claims accreditation and privacy.
4. A named maintenance owner and a dated review cycle.

Everything else is supporting.

## 7. How work moves

| Role | Responsibility |
|---|---|
| Travis | Organizational decisions, outreach approval, confirmation calls, publication |
| Claude | Scope, task packets, architecture, review and integration |
| ChatGPT / Codex | Research against official sources, bounded batches, validation |

Task packets live in `research/tasks/`. Returns go in `research/returns/<task-id>/`. Claude reviews returns before anything is merged into `data/`. See `docs/decisions.md` for the decision log and `docs/premortem.md` for failure modes.

## 8. Repository layout

```
README.md               Project charter (this file)
docs/
  premortem.md          How this could fail, and the countermeasures
  decisions.md          Decision log
  stage-plan.md         Stages and completion gates
research/
  tasks/                Task packets issued to ChatGPT/Codex
  returns/              Returned research, one folder per task
data/
  schema/               Dataset schema (v0.3 draft)
  seed/                 Original working seed (v0.2), unchanged
  batches/              Earlier research batches (B01), unmerged
print/                  Handoff sheets and staff guide (later)
site/                   Static directory site (later)
```


Regional referral update: all 88 county selections now include matched aging-agency and long-term-care ombudsman contacts, with directory sources and review dates. The printable handoff includes these contacts. See [coverage and sources](docs/STATEWIDE.md).

Accessibility update: a dedicated ramps/home modification pathway includes HISA application steps, VA and Ohio funding routes, county referral contacts, and a printable project tracker. Open the [accessibility guide](https://travisvought-byte.github.io/vhg-veteran-resident-guide/?view=accessibility).
