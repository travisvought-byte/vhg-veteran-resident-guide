# Resource mining

How new listings are found, traced and checked before they reach a state edition. The pipeline lives in
`scripts/mining/` and `data/mining/`, follows the evidence rules in [Maintenance](MAINTENANCE.md), and can be rerun
from a cold start with the commands below.

## The pieces

| Piece | File | What it holds |
| --- | --- | --- |
| Source registry | `data/mining/sources.json` | Every discovery source: who publishes it, how it is read, what it yields, its evidence level, its recheck cadence and its status. |
| Harvest files | `data/mining/harvest/<source id>-<date>.json` | What one source said on one day, row by row, with how it was read. |
| Snapshots | `data/mining/snapshots/<source id>/<date>.json` | Raw open datasets fetched by the monthly workflow, with the download URL and a sha256. |
| Candidates | `data/mining/candidates.csv` | Every harvest row, normalized, deduplicated and matched against what is already published. |
| Source ledger | `data/mining/source-ledger.json` | Every source behind a published record, with its oldest review and the date it is due again. The recheck queue. |
| Coverage | `data/mining/coverage.json`, [COVERAGE.md](COVERAGE.md) | Each state's county reach, records and evidence strength, ranked thinnest first, plus the country pages. |

## Evidence ladder

Every harvest row and every published record maps to one level.

- **A**: the agency itself confirmed the contact, and the confirmation is recorded.
- **B**: the official source was read in full: page text, PDF, spreadsheet or open dataset.
- **C**: an official source seen only through a search excerpt, page metadata or a partial read.
- **D**: a secondary published directory, such as an association guidebook or a national directory.
- **E**: a lead only, such as a social post, an unofficial aggregator or AI output. Never published.

Search results are leads. A page that failed to load, asked for a bot check or refused the request is not a review:
note it in the source registry and skip it. Never work around a block.

## Source statuses

`active` is used in the pipeline. `benchmark` gives counts for the coverage report and no listings. `manual` is read
by a person or assistant and recorded as a harvest file. `to_verify` is named but not yet opened. `needs_owner` would
need an account, key or payment, which is the owner's decision (a keyed source the owner has set up, like the VA
Facilities API, is `active` with a `key_env` naming its secret). `rejected` is too old or not official.

## Rerun from a cold start

Offline steps, any machine:

```
python3 scripts/mining/coverage.py      # which states are thinnest
python3 scripts/mining/ledger.py --due  # which published sources are due for a recheck
python3 scripts/mining/candidates.py    # what the harvest files add, and what conflicts
python3 tests/mining.py                 # registry, harvest files and generated reports are consistent
```

Network step, run monthly by `.github/workflows/mine-sources.yml` (or by hand from Actions, "Run workflow"):

```
python3 scripts/mining/fetch_open_data.py
```

The workflow pushes its results to a `mining/run-<date>` branch for review. It never changes a published edition.

The committed coverage report, ledger and candidates table are snapshots: they are refreshed by that workflow and
whenever a harvest is added, so a change to a state's data does not have to regenerate them. `tests/mining.py` checks
that the builders run and that the registry and harvest files are sound; `--check` on each script compares against
the committed snapshot when you want that.

## Adding a harvest

1. Pick the thinnest state in [COVERAGE.md](COVERAGE.md), and its official source from `sources.json` (add one if it
   is new, with status `active` or `manual`).
2. Read the source itself in full. Write `data/mining/harvest/<source id>-<date>.json` with `source_id`, `source_url`,
   `source_title`, `retrieved_on`, `review_method` (a method on the evidence ladder) and `how_read`, then one row per
   listing: `state`, `county`, `category`, `name`, `organization`, `phone`, `other_phones`, `address`, `hours`,
   `confidence` (`clear` or `uncertain`) and `note`. A row with no phone, or a value the source does not tie to it, is
   `uncertain` and its note says why. Leave out personal names, personal emails, cell and fax numbers.
3. Run `python3 scripts/mining/candidates.py`. Rows marked `new` are ready to move into the state's source sheet
   (`data/source/states/<code>.json`, then `scripts/make_county_state.py`). `phone_conflict` and `uncertain` rows wait
   for a person.
4. Run the offline steps above and the repository checks, and commit the harvest, the edition and the regenerated
   reports together.

## Cadence

Monthly: the open-data fetch and coverage report (the workflow). Quarterly: veterans offices, aging agencies and
ombudsman contacts whose ledger `due_on` has passed (90 days). Twice a year: programs (180 days). Each pass starts
with the thinnest states.

## What is not mined

Paid data, anything behind a sign-in, and sites that block automated reading.

## The VA Facilities API key

The VA Facilities API is the one keyed source. The owner registers the free developer key at developer.va.gov and
adds it to this repository as the Actions secret `VA_FACILITIES_API_KEY` (Settings, Secrets and variables, Actions,
New repository secret). No one else handles the key: it is not written in any file, issue, note or message. The
workflow passes it to `fetch_open_data.py`, which sends it only in the `apikey` request header. The key is a sandbox key,
so the registry points the source at `sandbox-api.va.gov`. When the VA grants production access, set the repository
variable `VA_FACILITIES_API_BASE` (Settings, Secrets and variables, Actions, Variables) to
`https://api.va.gov/services/va_facilities/v1/facilities`; nothing else changes. If the configured host refuses the
key, the fetcher tries the other host once. Each snapshot records which environment answered. Sandbox data is a
benchmark: a listing built from it is checked against production or the facility's own page before it is published. Without the secret, the run marks the source as skipped and carries on. No advertising code is added to the guide.

## Publishing VA locations

The VA Facilities API snapshot lands on the monthly `mining/run-<date>` review branch. To publish a batch of states:

```
git fetch origin mining/run-<date>
git show FETCH_HEAD:data/mining/snapshots/va-facilities-api/<date>.json > /tmp/va.json
python3 scripts/mining/va_listings.py --snapshot /tmp/va.json --states AZ,MA,WY   # or --states all
python3 scripts/build_public.py
python3 tests/mining.py
```

`va_listings.py` writes `data/public/va-facilities/<st>.json`: closed and temporarily closed facilities are left out,
rows are unique by VA facility id (and by name, address and phone), phones already in the state's guide are marked
`also_in_guide`, and each row cites its VA page and the retrieval date. `build_public.py` then builds `va-locations/<st>/` and
links it from the state's guide. Rerunning with a newer snapshot replaces a state's file in full.
