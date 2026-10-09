# Official Ohio bingo report extraction

Source: user-provided October 2, 2026 authorized locations report. Source SHA-256 is recorded in the dataset.

Run `python3 scripts/extract_bingo_report.py SOURCE.pdf data/source/ohio-bingo-authorizations-2026-10-02.json` (requires Poppler), then `python3 tests/bingo_report.py`.

The parser uses positional column headers, license-column row anchors, and separate vertical regions for each bingo type. Organization/DBA lines are preserved without guessing which is which. Every record retains its source page. Row-wide schedule fields are deliberately absent: Type III schedules must not become Type I schedules.

Reconciled: 545 pages, 6,297 location rows, 6,855 bingo-type entries. Ten additional license-shaped tokens are street addresses. Type I has 717 entries; sixteen have blank schedules. Visual checks on pages 88 and 127 confirm misplaced address fields and blank schedules.

Nine ZIP fields are malformed in the source. Raw values and quality flags are preserved; county strings also remain verbatim. No guessed repairs. Repeated licenses represent different locations and are not deduplicated by license alone.

This source dataset is not a verified event calendar. Authorization dates do not prove upcoming sessions, public admission, accessibility, prices, or current operation. The Type I entries feed the separate public bingo page; Type II and III entries remain source data.

## Second review

All schedule-column words independently reconcile against all 545 pages, with no omissions or cross-type borrowing. Wrapped street continuations are retained in the street field; city is the final address line. All 232 multiline address cells remain available as raw lines. Visual checks on pages 1 and 189 confirmed this correction, including a source address containing a phone number.

County names receive a separate case-only canonical field; raw county text remains unchanged. Three unrecognized source county strings (OH, COLUMBIAN, Huron, OH) remain unresolved. Six rows form three repeated-site pairs: one pair has different bingo types, one has identical authorizations, and one has different authorized days. All rows are preserved and flagged, so 6,297 is a source-row count, not a claim of unique venues.
