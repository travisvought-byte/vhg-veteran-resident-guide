# Utah coverage and evidence

Initial referral edition, source-reviewed October 14, 2026. Utah is the sixth state in the shared guide. It includes all 29 counties and 66 resources: 33 shared federal/national resources, 10 Utah programs, 12 aging agency contacts and 11 regional ombudsman contacts.

## County boundaries

- Veterans: [UDVMA regional offices](https://veterans.utah.gov/regional-offices/) explicitly assigns all counties to four regions. Each county uses its published regional manager's number. These are regional referrals, not 29 separate county offices. The directory also lists other representatives; the guide links to the full list and does not imply that the manager is the only available representative.
- Aging: [Utah Commission on Aging](https://ucoa.utah.edu/area-agencies-on-aging.php) supplies the 12 county service areas; [DAAS locations](https://daas.utah.gov/locations/) supplies published routing numbers. Agency names are normalized for display. Numbers are presented as published routing contacts, not confirmed specialist intake lines.
- Ombudsmen: [DAAS ombudsman locations](https://daas.utah.gov/ombudsman-locations-3/) independently assigns all counties to 11 regions and publishes a state escalation contact. County-specific cards use the regional number; the statewide program card uses the state ombudsman's number, not the records-request line.

Important differences preserved in the data: Summit uses Salt Lake Metro for veterans and Mountainland for aging; Millard and Sanpete use Central Utah for veterans and R6 for aging. Uintah County has its own aging contact; Daggett and Duchesne use Uintah Basin. All three share an ombudsman region. Morgan and Weber share an aging agency and ombudsman but use the Northern Utah veterans region.

The MAG directory lists Uintah among Uintah Basin's counties while also listing a separate Uintah County agency. The county-specific DAAS entry and Commission on Aging map support the separate Uintah County aging route used here. MAG also publishes some different general/specialist agency numbers. This edition consistently uses the DAAS-published numbers; current intake should be confirmed directly.

## Utah programs and sources

| Routes | Official source |
|---|---|
| Accredited claims assistance and remote appointment options | [UDVMA claims assistance](https://veterans.utah.gov/va-claims-assistance/) |
| State aging referral office | [DAAS contact](https://daas.utah.gov/contact-2/) |
| Caregiver support, Alternatives Program and SHIP | [DAAS services](https://daas.utah.gov/services/) |
| Aging Waiver and New Choices Waiver | [Utah Medicaid](https://medicaid.utah.gov/medicaid-long-term-care-and-waiver-programs/) |
| Equipment demonstrations, lending, reuse, customization and financing | [Utah State University UATP](https://idrpp.usu.edu/uatp/about-us/) |
| Resident advocacy and state escalation | [DAAS ombudsman contacts](https://daas.utah.gov/ombudsman-locations-3/) |
| Community resource navigation | [Utah 211](https://211utah.org/) |

Source pages were read through retrieved official page text. No telephone calls, direct intake confirmations, partner relationships or current funding checks are claimed. Each Utah resource retains the source URL, review method, review date and direct-confirmation flag. County contacts carry their independent regional source and selection note. No fabricated page hashes are used.

## Boundaries and remaining research

Aging Waiver screening requires age 65+, financial eligibility and nursing-facility level of care. Waiver capacity is limited. New Choices has its own requirements; menu option 6 is displayed as an instruction, not encoded as a phone extension. UATP does not guarantee a permanent ramp, installation, equipment availability or financing approval. VA adaptation requirements remain separate.

This is a referral backbone, not a complete local inventory. Individual posts, senior-center schedules, repair contractors, direct SSVF providers and transportation routes still need deeper local research. Vision and hearing views offer general assistive-technology and aging referrals; specialist services are not comprehensively mapped. Utah 211 is linked for user navigation; its listings were not copied into this directory. Ohio bingo remains Ohio-only.

## Maintenance

Canonical records: `data/public/ut-programs.json`, `data/public/ut-regional-referrals.json`, `data/public/utah-county-veterans-offices.json`. UI routing source: `states/ut/edition.json` and `states/ut/adapter.js`. Run the standard public build and validation. The build generates `utah-resources.json`, the shared bundle, `ut.html` redirect and `share-ut.html`; the QR asset points to `?state=UT`.
