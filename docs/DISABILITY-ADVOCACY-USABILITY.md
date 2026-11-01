# Disability advocacy: usability comparison and next steps

Reviewed November 1, 2026. This is a desk review of providers’ published documentation, not a hands-on accessibility audit or a claim about completion rates. No test letters were sent. The current implementation extends the original MIF example in issue #60 / PR #61.

| Tool | Documented strength | What this portal should learn |
| --- | --- | --- |
| Resistbot | Matches constituents with officials and delivers letters. It offers preview, multiple delivery methods and user-created campaigns. Its FAQ describes address requirements and delivery limits. | Explain each next action, let people review their own words, and support several communication methods. Do not claim a copied message was delivered. |
| Action Network | Matches addresses to federal/state targets and delivers through supported official APIs/forms or email. Some target forms require extra fields. | The biggest remaining gap is delivery: a production integration could remove the copy/paste handoff, but needs accurate target matching, accessible form completion, clear data practices, delivery errors and confirmations. |
| VoterVoice | Embeddable action center, configurable widgets/profile fields, mobile presentation and placement of important tools first. | Keep the central task prominent and reduce optional fields and competing widgets. No purchase or integration decision made. |
| National Council on Independent Living | Dedicated advocacy/action center and published action alerts. | Disability-specific campaign curation matters. A future alert needs an exact policy ask, correct decision maker, dated primary-source status and an expiry/recheck owner. Broad evergreen requests are not live bill alerts. |
| W3C cognitive accessibility guidance | Clear labels, short step-by-step instructions, examples and short critical paths. | Provide the instructions beside the task, keep edits intact, use plain language, and make task outcomes explicit. This is design guidance, not a conformance certification. |

Primary documentation:
- https://resist.bot/about
- https://help.actionnetwork.org/hc/en-us/articles/203112859-How-do-letters-get-delivered-to-targets
- https://votervoice.zendesk.com/hc/en-us/articles/1260804006470-The-Action-Center-Settings-Page
- https://ncil.org/advocacy-action/
- https://ncil.org/news/announcements/
- https://www.w3.org/WAI/WCAG2/supplemental/patterns/o4p07-step-instructions/
- https://www.w3.org/WAI/WCAG2/supplemental/

## Implemented after comparison

1. A visible choice between finding practical help and asking for policy change.
2. Three linked steps: choose a request, make it yours, contact lawmakers.
3. Short messages by default; an explicit detailed-letter option. Changes preserve the existing draft until Build message.
4. Editable subject line with its own Copy button, body character count and focus moved to the message after an explicit build.
5. Official Ohio House and Senate contacts open in new tabs so the draft stays open. Federal contacts use USAGov. No district is inferred from ZIP alone.
6. The send step explains copy/paste, required official-form details, review, confirmation and follow-up. The same message can support a call, relay call or printed letter.
7. Topic sharing includes only topic, lawmaker level and message format. A new shared-link visit starts with a matching draft; later changes preserve edits and contact routes.
8. Personal text remains in the open page only. Copy/download/print act on exact edited text; sharing excludes it. No completion or delivery is inferred from clicking a link.

## Highest-value next work

- **Test with people before expanding topics.** Recruit five to eight disabled users and supporters, including keyboard/switch users, screen-reader users and people with cognitive or fatigue-related access needs. Participation should be voluntary and compensated where possible. This is a proposed test, not completed research.
- **Observe real tasks:** distinguish help from policy change; choose the responsible level of government; make one personal edit; reach the correct official contact while keeping the draft; recover from a copy failure; share a topic without sharing personal text. Do not require participants to send a real letter.
- **Measure completion, wrong turns, assistance needed, lost edits and abandonment.** Target at least four of five independent completions of each core task in an initial round; treat that as a product goal, not statistical proof or current performance. Investigate every access barrier even if the aggregate goal passes.
- **Then pilot one delivery route.** Choose a supported campaign platform or official lookup integration based on user testing, actual costs, target coverage, accessibility and data terms. Retain a manual route. Do not store a new address/contact database just to reproduce a mature delivery service.
- **Add specific current campaigns selectively.** Each needs the actual bill/rule or decision, a concrete requested action, relevant recipient, review date and retirement rule. Publish meaningful outcomes only when supported by official evidence or clearly identified voluntary user reports.

## Verification limits

Automated DOM checks cover source structure, explicit rebuilds, both jurisdictions, both message lengths, exact copy/download/print, clear, safe share links and no personal storage. Browser checks cover responsive widths and no-JavaScript access. Live browser review checks presentation and keyboard-friendly controls. These do not replace assistive-technology testing or observation of actual users, and the portal does not automatically deliver messages.
