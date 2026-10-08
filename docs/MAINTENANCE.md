# Public guide maintenance

Established October 8, 2026. Publisher and correction contact: Travis Vought, Veteran Home Guardians, travis@vethomeguard.org. Backup reviewer: not yet assigned. This documented process is not a scheduled reminder or a claim that all contacts have been directly confirmed.

## Review priorities

1. Handle reports of wrong numbers, closed programs and misleading application instructions first. If a route is unreliable, label or remove the affected advice while investigating.
2. Recheck ramp and home modification application instructions monthly and whenever a program announces a change. Check annual funding limits at the fiscal-year boundary before adding amounts.
3. Review county, aging agency and ombudsman contacts quarterly, beginning with the four pilot counties. Ask about current intake and assistance for people who cannot travel; a working website alone does not confirm this.
4. Recheck other program records at least every six months. Clear the lower-evidence queue before expanding low-priority listings.

These intervals are the intended maintenance standard. Record completed checks, not scheduled checks, as review dates.

## Correction handling

Accept public corrections by email or GitHub issue. Ask for program name, county, affected field, official source and date. Do not request diagnoses, resident names, financial documents or claim identifiers. Track recipient-specific outreach and personal information in VHG's private systems.

Review the source and distinguish full source review, indexed excerpt, directory entry and direct agency confirmation. A failed fetch or a matching search excerpt does not justify upgrading a record to full-source-reviewed or agency-confirmed. Preserve unresolved conflicts and older evidence. Add public confirmation details only when actually obtained.

## Publishing a data change

For Ohio, edit `prototype-data.json` for programs or `data/public/ohio-county-veterans-offices.json` for county contacts. For Pennsylvania, edit `data/public/pa-programs.json` and `data/public/pennsylvania-county-veterans-offices.json`; the combined PA dataset and pages are generated. Shared federal records remain in `prototype-data.json`, with PA inclusion controlled by `data/public/federal-resource-ids.json`. Run `python3 scripts/build_public.py`, then all README checks. This generates both embedded data and the regional JSON from the canonical files; do not hand-edit those projections. Update the public edition date only for a substantive publication update, while keeping individual record dates honest.

Review the affected route in a browser and inspect printing when print content changes. Publish and verify the live result. Update `docs/VERIFICATION-QUEUE.md` when evidence statuses change; the queue is a dated snapshot, not an automatic status service.
