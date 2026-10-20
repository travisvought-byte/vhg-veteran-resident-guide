# VHG resource assistance — pilot (not live email automation)

This folder contains the first functional component of a future **email and web-based veteran assistance navigator**. The goal is for veterans, relatives, care teams and advocates to describe a need in plain English, then receive *specific, source-linked starting points* for assistance.

## What works now

- `assistant/index.html` is a browser-based, accessible intake and resource-matching preview. The user chooses a supported state/county, describes a general need, sees matching resource cards, and can copy a draft email response.
- `engine.mjs` contains deterministic, testable matching and email composition logic; it reads the published resource records rather than inventing programs.
- `benefits-housing-checklists.mjs` adds six official-source pathways for pension, survivor benefits and veteran housing help, with document preparation, proper intake contacts and next steps. No private documents are collected.
- `handoff.mjs` builds a dedicated US Letter print layout for all ten supported program checklists, including a recipient, locally published veteran office contact when appropriate, every preparatory step, submission route, official source URLs and three follow-up questions. Each matching resource has a **Print one-page handoff** button; the on-screen guide and private intake narrative are excluded from print. Chromium PDF page-count checks guard against accidental two-page handoffs. No checkmark history or personal details are saved.
- `accessibility-checklists.mjs` adds specific, source-reviewed HISA, SAH, SHA and Ohio waiver home-modification preparation checklists. Each item identifies who must act, with official submission routes and follow-up instructions. Browser checkmarks are transient only, and are never sent, persisted, or treated as proof of eligibility. Copyable drafts include the document-preparation reminders, without completion status.
- `program-guidance.mjs` is a source-linked, 12-program pilot of **explicit beneficiary audiences, eligibility screening notes and practical official application or intake steps**. Curated audiences override the conservative, existing fallback classifier. Listings without a curated entry keep their original program-specific next-step wording; no universal form or eligibility promise is inferred.
- `draft-email.mjs` turns JSON intake into a **draft** email on standard output. No email is sent or stored.
- `tests/assistant.mjs` exercises safety messaging, published contact data, eleven-state source status filters and beneficiary-aware routing and draft output.
- This prototype supports **all eleven published state editions** (OH, PA, NY, MI, KY, UT, IN, WV, TX, FL and CA), using the same data paths as the current public guide. A CI test checks the registry mapping. It does **not** represent fully researched county-level service coverage.

## Test it

```sh
node tests/assistant.mjs
node tests/assistant-browser.cjs # requires npm ci and Playwright Chromium
printf '%s' '{"state":"OH","county":"Muskingum","person":"veteran","message":"A disabled veteran needs a wheelchair ramp and housing support."}' | node assistant/draft-email.mjs
python3 -m http.server 8000
# Open http://localhost:8000/assistant/ in a browser
```

A browser is necessary: ES modules and JSON fetches won't work reliably with a `file://` URL.

## What is not yet active

- No inbound mailbox integration or autoresponder. No Apps Script or email trigger is shipped or activated by this navigator-only branch.
- No mail platform, provider credentials or public API endpoint.
- No third-party model calls; the pilot uses rules/terms to match program records, **not an LLM**. It is intentionally labeled as a pilot.
- No user profiles, case histories, email lists, sensitive-data collection or cloud storage.

The public guide links to this opt-in **guided assistance beta** after release, while the existing guide stays the main entry point. The beta works entirely in the visitor's browser and does not transmit intake messages, store cases or send email. Curated guidance links directly to the VA or relevant state pages for HISA (Form 10-0103), SAH/SHA (Form 26-4555), veteran and survivor pensions, DIC, Aid and Attendance, housing intake, Ohio waiver modifications, PA Link and California ADRC. Each example is only an intake route, not a decision or a claim that forms apply to everyone. The form explicitly asks who needs assistance so that veteran-only resources are not recommended to nonveterans. A caregiver identifies the person receiving care. Unknown roles receive general resources until eligibility context is clarified. Never add names, medical details, VA claim numbers, Social Security numbers, private emails or case histories to the public GitHub repository, PR discussion, logs or test fixtures.

## Proposed email / AI deployment (next stage)

Use **help@vethomeguard.org** as a real, monitored VHG address. The domain owner retains control. Wire an approved inbound email service or mailbox integration to a **private server-side** endpoint; GitHub Pages is static and cannot securely hold API secrets or run email webhooks.

1. **Receive:** Authenticate the provider's webhook signature or mailbox access; rate-limit abuse, deduplicate message IDs and reject obvious auto-responses. Do not process forwarded attachments automatically.
2. **Minimize:** Extract a plain-language issue, state, county and basic eligibility context. Redact or avoid sending names, diagnoses, claims identifiers and financial documents to an AI model. Do not publish intake or prompts to GitHub.
3. **Retrieve:** Look up the versioned, approved VHG dataset for that state. Build a list of applicable resources with program IDs, links, source-review dates and limitations. Include county veterans offices as first contacts when supported.
4. **Reason carefully:** An optional AI model may organize the request, ask for missing location/needs details and write a readable explanation **using only the retrieved citations and facts**. The model must not invent eligibility, availability, funding, partners or contact details; must label uncertainty and ask to confirm intake. Guard against prompt injection in emails and resource text.
5. **Triage:** For urgent danger, direct the person to 911; for suicidal thoughts or crisis, 988 then press 1 or text 838255. An email assistant is not a crisis monitoring service, so automated acknowledgments must never imply 24/7 human intervention. Uncertain high-stakes decisions require human review.
6. **Draft first:** Queue responses for authorized VHG review. Do not send automatically until live reliability tests, mailbox ownership, privacy notices, sender authentication, abuse controls, accessibility and escalation coverage are confirmed. Send only through an authorized outbound service with DKIM/SPF/DMARC and bounce handling.
7. **Measure:** Track aggregated categories, response times, source corrections and verified outcomes without retaining unnecessary personal histories. Offer a concise correction route, deletion contact and human assistance route.

## Printable handoff checks

To print, search for a relevant accessibility program and use **Print one-page handoff** on its program card; the browser print dialog can save it as a PDF. The sheet contains no typed request narrative, checkmark status, names, medical records or benefits identifiers. It is not submitted to an agency or persisted on VHG servers. Print formatting targets US Letter. Run `node tests/assistant-browser.cjs` for a Chromium PDF regression test covering ten accessibility, pension, survivor and housing handoffs.

## Accessibility checklist caveats

- HISA involves a VA physician's prescription, completed VA Form 10-0103, a written itemized project estimate and a color before photo; renters additionally need notarized owner permission. The clinical team may provide specific requirements, and VA may inspect the site.
- SAH/SHA initially use VA Form 26-4555 or the online route. Do not imply a contractor bid is required to submit the initial application.
- Ohio waiver modifications must be authorized by the service plan and appropriate agency. Provider proposals, permits, inspections and owner consent are part of the provider/agency process, not a general grant application.
- No applicant name, address, SSN, diagnosis, benefit ID, saved application or completion status is requested by this navigator. The checkboxes intentionally reset on reload or a new request.

## Quality / release gates

- Test realistic requests including uncertain eligibility, local gaps, housing crises, senior needs, scams or bad data, out-of-scope locations and nonsensical input.
- Confirm source status filtering and keep official *source reviewed* distinct from *currently accepting referrals*.
- Test deliverability, duplicate prevention, malicious replies, prompt injection, accessibility, error handling and privacy.
- Establish owner-approved inbox and outbound provider settings **before** activating any sends.
- Manual review by a VHG operator is the default for the initial release; expand automation only for well-supported low-risk requests.

**Design principle:** The system helps people find the *next useful call*, rather than purporting to award benefits, guarantee assistance, or substitute for an accredited representative.
