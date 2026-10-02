# Research instructions (applies to every task)

You are performing research for the Veteran Resident Resource Guide, a Veteran Home Guardians project in Morrow, Knox, Marion and Delaware counties, Ohio. Read `README.md` (charter) and the task packet before starting. You have no access to Claude's conversation; everything you need is in this repository or attached.

## Rules

1. **Research only.** Do not contact agencies, submit forms, or draft outreach unless the packet explicitly asks for a draft script. A draft is never sent by you.
2. **Official sources first.** Government, agency and program pages, statutes, regulations and official PDFs. Secondary sources may help you find an official source but do not support a published field on their own.
3. **Cite every field.** Each source records: URL, fields it supports, date reviewed, published date or effective period if shown, and access method (`page_text_reviewed`, `pdf_text_reviewed`, `official_search_extract_reviewed`).
4. **Unknown stays null.** Do not infer eligibility, availability, wait times, remaining funds, payer acceptance, partnerships or closures. A failed page fetch is not evidence of closure.
5. **Conflicts are findings.** When two official sources disagree, record both, with dates, and do not pick one silently.
6. **Amounts carry their period.** Any dollar figure or deadline includes the year or period it applies to and its source. Do not carry a prior-year figure forward as current.
7. **No resident or personal information.** Use office and role contacts. If only a named staff contact is published, record it in an `internal_contact` field.
8. **No internal references.** Do not include session-specific retrieval IDs; the URL and date are the provenance.
9. **Plain language.** Notes intended for staff or families should be readable by a non-specialist.

## Return format

Place returns in `research/returns/<task-id>/`:

- `records.json` — structured records following `data/schema/schema_v0.3.json` where the packet says so.
- `notes.md` — findings, conflicts, unresolved questions, items needing an owner decision, and validation performed.
- Any other file the packet requests.

End `notes.md` with a short list of exactly what you could not confirm.
