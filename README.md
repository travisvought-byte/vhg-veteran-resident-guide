# Ohio Veteran Resident Resource Guide

A free Veteran Home Guardians (VHG) guide for veterans, surviving spouses, seniors, people with disabilities, families and care teams. It helps people find their first contact and prepare a useful referral.

**Live guide:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/

**Sharing kit:** https://travisvought-byte.github.io/vhg-veteran-resident-guide/share.html

**Publisher and project owner:** Travis Vought, Founder & Chair, Veteran Home Guardians. Contact: travis@vethomeguard.org.

## Current scope

- Veterans office contacts for all 88 Ohio counties, plus matched aging agency and long-term-care ombudsman contacts.
- 106 resource records, displayed as 102 cards after removing four duplicate legacy county office cards.
- Veterans benefits, surviving-spouse support, care, housing and resident rights routes.
- Ramps and home accessibility: HISA, adapted housing, Ohio waiver routes, rural repair and discharge coordination, with an application checklist and paper follow-up tracker.
- A dedicated seniors and disability section without a military-service requirement.
- Official American Legion, AMVETS and VFW locators. Individual county post contacts and a contractor network are not yet populated.
- Printable county handoffs, audience-specific share links, a one-page QR flyer and newsletter introduction.

Statewide referral coverage is not an exhaustive statewide inventory of local services. Local program research remains strongest in Morrow, Knox, Marion and Delaware. Most county phones come from a source publication; hours, intake and availability must be confirmed with the office. See [coverage and evidence](docs/STATEWIDE.md).

## Operating boundaries

The guide routes people to agencies; it does not decide eligibility, prepare claims or promise funding. Claims assistance belongs with accredited representatives. No resident records or application information are collected. Keep personal information out of GitHub issues. Listing an organization does not imply a partnership or endorsement.

## Update and verify

Canonical public program data lives in `prototype-data.json`; canonical county contacts live in `data/public/ohio-county-veterans-offices.json`. Edit those sources, preserve evidence and review dates, then run:

```sh
python3 scripts/build_public.py
python3 scripts/build_public.py --check
python3 scripts/validate_public.py
node tests/accessibility.cjs
```

The build updates embedded data in `index.html` and the regional referral projection. The page stays self-contained, with no runtime data service. GitHub Actions runs these checks for pushes and pull requests. Checks cover county mappings, routes, sharing behavior and data synchronization; they do not establish WCAG compliance, remote link availability or print pagination. Browser and print review remain necessary.

Older integration scripts and research candidates are historical research tools, not the public build. Do not publish their output over the current public data without review.

## Maintenance and next research

See the [maintenance process](docs/MAINTENANCE.md), [verification queue](docs/VERIFICATION-QUEUE.md) and [distribution plan](docs/DISSEMINATION.md). Source review is not telephone confirmation. No outreach was sent as part of this update.

## Repository layout

| Path | Purpose |
|---|---|
| `index.html` | Public guide, interface and generated embedded data |
| `share.html` | Printable QR flyer and reusable newsletter introduction |
| `assets/` | VHG logo, QR code and social preview image |
| `prototype-data.json` | Canonical current public resource records |
| `data/public/` | County contacts, generated regional projection and future post directory |
| `scripts/build_public.py` | Public data synchronization |
| `scripts/validate_public.py`, `tests/accessibility.cjs` | Data, asset and functional checks |
| `docs/` | Scope, maintenance, evidence and research priorities |
| `research/`, `data/integrated/`, `data/seed/`, `data/batches/` | Historical working material; not the live source of truth |
