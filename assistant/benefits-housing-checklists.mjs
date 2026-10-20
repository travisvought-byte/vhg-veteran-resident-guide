// Explicit, source-checked pension/survivor/housing preparation routes.
// Do not collect or retain any document, claim number, identity, or user progress.
// Official sources reviewed 2026-10-19. Agency decides eligibility and required evidence.
export const BENEFITS_HOUSING_CHECKLISTS = Object.freeze({
  "r02-va-pension": {
    "title": "Veterans Pension — application preparation",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Check eligibility and timing",
        "items": [
          {
            "text": "Review qualifying wartime service, age or permanent disability, household income and net-worth conditions with an accredited representative.",
            "responsible": "Applicant / accredited representative"
          },
          {
            "text": "Ask whether an intent to file is useful before a paper application; starting the application with a verified VA.gov account may establish its effective date automatically.",
            "responsible": "Applicant / accredited representative"
          }
        ]
      },
      {
        "title": "Gather documents privately",
        "items": [
          {
            "text": "Have military service dates and discharge information, Social Security number and VA file number if assigned ready for the official VA form.",
            "responsible": "Applicant"
          },
          {
            "text": "Gather household gross monthly income, assets, unreimbursed medical expenses, work and marital history, and dependent information.",
            "responsible": "Applicant"
          },
          {
            "text": "If under age 65, obtain medical records supporting the pension claim; VA may request more evidence.",
            "responsible": "Applicant",
            "condition": "Only if under age 65"
          }
        ]
      },
      {
        "title": "Apply and follow up",
        "items": [
          {
            "text": "Apply on VA.gov or complete VA Form 21P-527EZ. You can also use QuickSubmit, mail to the VA Pension Intake Center, or visit a VA regional office.",
            "responsible": "Applicant / accredited representative"
          },
          {
            "text": "For postal submissions, verify the current Pension Intake Center address on VA.gov; retain proof of submission and the application copy.",
            "responsible": "Applicant",
            "condition": "Only if mailing"
          },
          {
            "text": "Check claim status on VA.gov and respond to VA requests for additional evidence.",
            "responsible": "Applicant"
          }
        ]
      }
    ],
    "submit": {
      "text": "Apply using VA.gov or VA Form 21P-527EZ. VA lists QuickSubmit, VA regional office and Pension Intake Center mail routes.",
      "label": "VA Veterans Pension application instructions",
      "url": "https://www.va.gov/pension/how-to-apply/"
    },
    "followUp": "Keep the VA confirmation; check claim status and respond to evidence requests promptly.",
    "sources": [
      "https://www.va.gov/pension/how-to-apply/",
      "https://www.va.gov/pension/how-to-apply/fully-developed-claim/"
    ]
  },
  "r02-survivors-pension": {
    "title": "Survivors Pension — surviving family application",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Confirm the correct survivor route",
        "items": [
          {
            "text": "Determine whether the claimant is a surviving spouse or dependent child; check the deceased veteran's qualifying wartime service and survivor requirements.",
            "responsible": "Claimant / accredited representative"
          },
          {
            "text": "Ask an accredited representative whether to consider an intent to file before collecting documents for a paper claim.",
            "responsible": "Claimant / accredited representative"
          }
        ]
      },
      {
        "title": "Prepare the VA application privately",
        "items": [
          {
            "text": "Have relationship evidence, deceased veteran's service information and death details available; enter identifying data only on the VA application.",
            "responsible": "Claimant"
          },
          {
            "text": "Gather income, asset, dependent and eligible care-expense information as requested for Survivors Pension.",
            "responsible": "Claimant"
          },
          {
            "text": "Review VA Form 21P-534EZ, which also includes DIC and accrued-benefit claims; select the appropriate benefits.",
            "responsible": "Claimant / accredited representative"
          }
        ]
      },
      {
        "title": "Submit and track",
        "items": [
          {
            "text": "Apply through the official online survivor-benefits application or submit Form 21P-534EZ through the VA-approved channel.",
            "responsible": "Claimant / accredited representative"
          },
          {
            "text": "For a paper claim, verify and use the VA Pension Intake Center address shown on the official page; keep a copy and receipt.",
            "responsible": "Claimant",
            "condition": "Only if mailing"
          },
          {
            "text": "Watch for a VA decision or evidence request; VA says requested information may need a response within 30 days.",
            "responsible": "Claimant"
          }
        ]
      }
    ],
    "submit": {
      "text": "Use the VA survivor-benefits online application or VA Form 21P-534EZ. Verify mail and in-person options with VA.",
      "label": "VA survivor-benefits application",
      "url": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/apply-for-dic-survivors-pension-accrued-benefits-form-21p-534ez/"
    },
    "followUp": "Track the claim; respond within the deadline stated on any VA evidence request. Ask an accredited representative for help.",
    "sources": [
      "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/apply-for-dic-survivors-pension-accrued-benefits-form-21p-534ez/",
      "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/survivors-pension/"
    ]
  },
  "r02-dic": {
    "title": "Dependency and Indemnity Compensation (DIC)",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Check the claimant and qualifying circumstance",
        "items": [
          {
            "text": "Identify whether the claimant is a surviving spouse or dependent child of a veteran; other categories may require a different VA form.",
            "responsible": "Claimant / accredited representative"
          },
          {
            "text": "Review the death and service-related eligibility rules, including applicable service-connected disability or qualifying rating history.",
            "responsible": "Claimant / accredited representative"
          }
        ]
      },
      {
        "title": "Prepare evidence privately",
        "items": [
          {
            "text": "Gather the death certificate, relationship evidence, service records and any relevant VA rating or medical evidence as requested by VA.",
            "responsible": "Claimant"
          },
          {
            "text": "For a surviving spouse or child of a veteran, review Form 21P-534EZ; for an active-duty death, ask the military casualty assistance officer about Form 21P-534a.",
            "responsible": "Claimant / casualty assistance officer",
            "condition": "Active-duty deaths use a distinct route"
          },
          {
            "text": "For surviving parents, VA uses Form 21P-535; this navigator's surviving-spouse category is not a parents' eligibility determination.",
            "responsible": "Claimant / accredited representative",
            "condition": "Only for surviving parent"
          }
        ]
      },
      {
        "title": "Submit and follow up",
        "items": [
          {
            "text": "Apply online where offered or through an accredited representative, VA QuickSubmit, Pension Intake Center mail, or a VA regional office.",
            "responsible": "Claimant / accredited representative"
          },
          {
            "text": "Ask whether an intent to file is appropriate before a paper filing to preserve a potential effective date.",
            "responsible": "Claimant / accredited representative"
          },
          {
            "text": "Retain submission confirmation and check claim status; respond to VA requests for evidence.",
            "responsible": "Claimant"
          }
        ]
      }
    ],
    "submit": {
      "text": "For surviving spouses or children of veterans, use the official VA 21P-534EZ application. Active-duty survivors and surviving parents have different forms.",
      "label": "Official VA DIC application guidance",
      "url": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/dependency-indemnity-compensation/"
    },
    "followUp": "Record the submission date and track the claim. Ask a VA-accredited representative about any denial, evidence request or appeal.",
    "sources": [
      "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/dependency-indemnity-compensation/",
      "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/apply-for-dic-survivors-pension-accrued-benefits-form-21p-534ez/"
    ]
  },
  "r02-aid-attendance-housebound": {
    "title": "Aid and Attendance / Housebound pension additions",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Confirm the base benefit and care need",
        "items": [
          {
            "text": "Check whether the person receives or may qualify for VA pension; Aid and Attendance and Housebound are additions, not a standalone general disability grant.",
            "responsible": "Applicant / accredited representative"
          },
          {
            "text": "Document needs for another person's daily assistance or qualifying housebound status; the two additions cannot be received at the same time.",
            "responsible": "Applicant / clinician"
          }
        ]
      },
      {
        "title": "Prepare the medical/facility documents",
        "items": [
          {
            "text": "Ask the medical examiner to complete VA Form 21-2680, including the examination section.",
            "responsible": "Medical examiner and applicant"
          },
          {
            "text": "If the applicant is in a nursing home, ask the facility to complete VA Form 21-0779.",
            "responsible": "Nursing home official",
            "condition": "Only for a nursing-home resident"
          },
          {
            "text": "Prepare supporting medical and care-expense information requested for the pension addition; share it with VA, not VHG.",
            "responsible": "Applicant"
          }
        ]
      },
      {
        "title": "Apply and monitor",
        "items": [
          {
            "text": "Use the VA online application, mail Form 21-2680 to the VA Pension Intake Center, or bring it to a VA regional office as directed.",
            "responsible": "Applicant / accredited representative"
          },
          {
            "text": "Check claim status and respond if VA requests more medical information.",
            "responsible": "Applicant"
          },
          {
            "text": "Ask the representative whether the pension and the addition should be considered together when first applying.",
            "responsible": "Applicant / accredited representative",
            "condition": "Only if pension has not yet been granted"
          }
        ]
      }
    ],
    "submit": {
      "text": "Use VA's Aid and Attendance/Housebound page for its online application or Form 21-2680 submission to the Pension Intake Center; add Form 21-0779 if in a nursing home.",
      "label": "VA Aid and Attendance application",
      "url": "https://www.va.gov/pension/aid-attendance-housebound/"
    },
    "followUp": "Ask whether the medical examination and any nursing-home verification were received and whether further information is needed.",
    "sources": [
      "https://www.va.gov/pension/aid-attendance-housebound/",
      "https://www.va.gov/forms/21-2680/",
      "https://www.va.gov/forms/21-0779/"
    ]
  },
  "va-housing-help": {
    "title": "Veteran housing help — first contact",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Make contact immediately",
        "items": [
          {
            "text": "If housing is lost or at risk, call the VA National Call Center for Homeless Veterans: 877-424-3838. It is available 24 hours a day, seven days a week.",
            "responsible": "Veteran, family, advocate or care team"
          },
          {
            "text": "Alternatively, use the official VA homeless-help chat; no application documents are required before making the first call.",
            "responsible": "Veteran or supporter"
          }
        ]
      },
      {
        "title": "Explain the situation",
        "items": [
          {
            "text": "Tell the VA counselor the state/county and whether the veteran needs a safe place tonight or is facing an upcoming eviction.",
            "responsible": "Caller"
          },
          {
            "text": "Ask the counselor which local VA homeless coordinator or other staff member can take the next step.",
            "responsible": "Caller / VA counselor"
          },
          {
            "text": "Ask about available prevention, rapid-rehousing or housing-stability programs; availability varies by location.",
            "responsible": "Caller / VA counselor"
          }
        ]
      },
      {
        "title": "Record next steps privately",
        "items": [
          {
            "text": "Write down the receiving office, contact method and follow-up time for yourself; do not submit this information to VHG.",
            "responsible": "Caller"
          },
          {
            "text": "If no one connects you with local assistance, call the official VA line again and ask how to reach the local homelessness team.",
            "responsible": "Caller"
          }
        ]
      }
    ],
    "submit": {
      "text": "Call 877-424-3838 or use the official VA homeless assistance chat. No advance paperwork is required for the first contact.",
      "label": "VA National Call Center for Homeless Veterans",
      "url": "https://department.va.gov/homeless/nationalcallcenter/"
    },
    "followUp": "Ask who is coordinating local assistance and whether any immediate shelter or prevention options are available. No program funding is guaranteed.",
    "sources": [
      "https://department.va.gov/homeless/nationalcallcenter/",
      "https://department.va.gov/homeless/quick-guide-va-programs-and-services-for-homeless-and-at-risk-veterans/"
    ]
  },
  "va-ssvf": {
    "title": "SSVF — veteran family housing stability",
    "reviewedOn": "2026-10-19",
    "sections": [
      {
        "title": "Find the correct local provider",
        "items": [
          {
            "text": "Start with VA homeless assistance at 877-424-3838 if there is an immediate housing need; ask about local SSVF services.",
            "responsible": "Veteran or supporter"
          },
          {
            "text": "Use the official VA SSVF provider directory to identify an awarded provider that covers the household's county.",
            "responsible": "Veteran, advocate or case worker"
          }
        ]
      },
      {
        "title": "Request screening",
        "items": [
          {
            "text": "Tell the provider whether the household is homeless, at risk of losing housing or needs rapid re-housing.",
            "responsible": "Applicant"
          },
          {
            "text": "Ask whether SSVF prevention or rapid rehousing is offered in the county and whether intake is currently open.",
            "responsible": "Applicant / SSVF provider"
          },
          {
            "text": "Ask the provider what service, veteran status, income or household documents it needs; do not send these to VHG.",
            "responsible": "Applicant / SSVF provider"
          }
        ]
      },
      {
        "title": "Follow through",
        "items": [
          {
            "text": "Schedule the provider's intake and ask whether other VA or community referrals are appropriate if SSVF cannot assist.",
            "responsible": "Applicant / provider"
          },
          {
            "text": "Record the provider contact and next appointment privately, and ask how to follow up if no response arrives.",
            "responsible": "Applicant"
          }
        ]
      }
    ],
    "submit": {
      "text": "Contact an SSVF provider serving the county through the official VA awarded-provider list or VA's homeless assistance intake. There is no single national SSVF applicant form.",
      "label": "VA SSVF program and providers",
      "url": "https://department.va.gov/homeless/supportive-services-for-veteran-families/"
    },
    "followUp": "Ask whether provider intake is open, what verification is required, and when a screening decision or referral may be available.",
    "sources": [
      "https://department.va.gov/homeless/supportive-services-for-veteran-families/",
      "https://department.va.gov/homeless/nationalcallcenter/"
    ]
  }
});
export function getBenefitsHousingChecklist(programId) {
  return BENEFITS_HOUSING_CHECKLISTS[String(programId||"").toLowerCase()] || null;
}
