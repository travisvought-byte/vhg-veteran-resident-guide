# Adding a state

Established October 18, 2026. Every state follows the same standard: each county resolves to a veterans contact, a local aging contact and a long-term-care ombudsman route, each backed by an official published source and a review date. A state is added with data and configuration only. No build code changes are needed.

## What a state consists of

| File | Contents |
|---|---|
| `data/public/<slug>-county-veterans-offices.json` | One record per county: veterans contact phone, organization, `source_url`, review date. Where the state uses regional rather than county offices, each county carries its published regional contact (see Utah and Kentucky). |
| `data/public/<code>-regional-referrals.json` | Aging agencies (`regional_role: "aging_agency"`) and ombudsman programs (`regional_role: "ombudsman"`), each with the counties it serves in `service_area`. |
| `data/public/<code>-programs.json` | State programs: claims help, aging and disability navigation, waiver screening, health insurance counseling, assistive technology, a statewide ombudsman where there is no regional map. |
| `states/registry.json` | One entry naming the state, its files and its coverage statement. |
| `states/<code>/edition.json` | Ordered wording, routing and link changes applied to the shared guide template. |
| `states/<code>/adapter.js` | State-specific display functions, one per line. |

Federal resources are shared automatically from `data/public/federal-resource-ids.json`.

## 1. Research the three data files

Use official published sources: the state veterans agency's county or regional directory, the state unit on aging's agency map, and the state long-term-care ombudsman program. Record what each source supports and nothing more. Copy the record shape from an existing state; Utah's files are the most compact example.

Rules the checks enforce:

- Every county has a veterans phone and a `source_url`.
- Every county appears in at least one aging agency's `service_area`.
- Every county is covered by a county-mapped ombudsman or a statewide ombudsman program.
- Every resource has an `https` official link, a `record_status` and a `last_reviewed_on` date.
- `service_area` values are exact county names from the offices file, or `statewide`.
- No program id starts with another registered state's code. By convention, ids start with the state's own lowercase code (`in-claims`, `in-aging-region-1`).

When a county has the same name as the state (New York, Ohio and Utah counties), its records stay county-limited automatically. Only list a name in `statewide_area_names` if the state's records use it to mean statewide.

## 2. Add the registry entry

Add one object to `states/registry.json`, in the order the state should appear in the menu:

| Field | Meaning |
|---|---|
| `code`, `name` | Two-letter code and display name |
| `page`, `share_page`, `qr` | `<code>.html`, `share-<code>.html`, `assets/guide-qr-<code>.svg` |
| `counties` | Expected county count; the build stops if the offices file differs |
| `programs`, `referrals`, `offices` | The three canonical data files |
| `resources` | Generated combined file: `data/public/<slug>-resources.json` |
| `statewide_area_names` | Usually `[]` |
| `coverage_scope` | One-sentence coverage statement for the state page |
| `coverage_note` | Optional extra paragraph in the guide's coverage details |
| `share_description`, `share_replacements` | Sharing-kit wording |

## 3. Write the edition and adapter

Copy the closest existing state folder and adjust it:

- `states/ut/` for regional veterans contacts with separate aging and ombudsman maps.
- `states/mi/` for county veterans offices with statewide ombudsman routing.
- `states/pa/` for county offices with a mix of local and statewide ombudsman routes.

`edition.json` holds an ordered list of operations:

| Operation | Effect |
|---|---|
| `clear_data` | Removes the base state's records before any wording changes. Always first. |
| `replace` | Replaces text (`old`, `new`, optional `count`). Used for the state name, county count, links and source wording. |
| `regex` | Pattern replacement (`pattern`, `new`, optional `count`, `dotall`). |
| `declare` | Sets `priority`, `routes` or `seniorTopics` to a JSON value: which program ids appear for each need. |
| `line` | Replaces one template line that starts with `prefix`. |
| `adapter` | Applies `adapter.js`. |
| `embed_data` | Adds the state's records. Always last. |

Each line of `adapter.js` is one function. A function the template already has (`renderCounty`, `officeCard`, `audience` and others) is replaced; any other function is added as a helper. Keep wording consistent with the existing states: plain language, no eligibility determinations, and a clear next step for each contact.

## 4. Build and check

```sh
python3 scripts/build_public.py
python3 scripts/make_qr.py          # creates the sharing QR code; needs: pip install qrcode
python3 scripts/build_public.py --check
python3 scripts/build_public.py --test-fixtures
python3 scripts/validate_public.py
node tests/feedback.cjs
npm test
npm run test:browser
```

`tests/states.cjs` and `tests/editions-browser.cjs` read the registry, so the new state is checked automatically: county coverage, sources, state isolation, county panels, county-limited resources, deep links and loading.

The build writes the state's records to `assets/editions/<code>.js`. Visitors download it only when they choose the state, so adding states does not slow the default page.

## 5. Document and publish

Add `docs/<STATE>.md` describing sources, county boundaries, known gaps and the review date, following `docs/UTAH.md`. A state is ready to publish when every check passes and its coverage statement accurately describes what was and was not reviewed.
