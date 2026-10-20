// First curated referral/application routes for the assistance pilot.
// Re-check official source URLs and requirements before expanding.
// This is *routing metadata*, never an eligibility decision or an application.
export const PROGRAM_GUIDANCE = Object.freeze({
  "va-hisa": {
    "audience": "veteran",
    "audienceLabel": "Veteran receiving VA medical care; medical necessity and benefit limits require VA review",
    "application": {
      "label": "VA Form 10-0103 — HISA application",
      "url": "https://www.va.gov/vaforms/medical/pdf/10-0103-fill.pdf"
    },
    "steps": [
      "Ask the VA care team to assess and document the needed accessibility modification.",
      "Ask the VA facility's Prosthetic and Sensory Aids Service for its HISA submission requirements, including plans and bids.",
      "Review VA Form 10-0103; submit it to the VA health facility where the veteran receives care, not through this website."
    ],
    "source": "https://www.va.gov/vaforms/medical/pdf/10-0103-fill.pdf"
  },
  "va-sah": {
    "audience": "veteran",
    "audienceLabel": "Veteran or service member; qualifying disability and property requirements must be assessed",
    "application": {
      "label": "VA adapted housing grants — online application or Form 26-4555",
      "url": "https://www.va.gov/housing-assistance/disability-housing-grants/how-to-apply/"
    },
    "steps": [
      "Review VA's SAH disability and home requirements before beginning construction.",
      "Apply online or use VA Form 26-4555; ask the VA or an accredited representative for help.",
      "Wait for VA's individual grant review and project guidance before committing to alterations."
    ],
    "source": "https://www.va.gov/housing-assistance/disability-housing-grants/how-to-apply/"
  },
  "va-sha": {
    "audience": "veteran",
    "audienceLabel": "Veteran or service member; SHA disability and housing criteria must be assessed",
    "application": {
      "label": "VA adapted housing grants — online application or Form 26-4555",
      "url": "https://www.va.gov/housing-assistance/disability-housing-grants/how-to-apply/"
    },
    "steps": [
      "Review the SHA-specific eligibility and housing rules with VA.",
      "Apply online or use VA Form 26-4555; request an accredited representative if needed.",
      "Ask VA what project documentation and approval must be in place before work starts."
    ],
    "source": "https://www.va.gov/housing-assistance/disability-housing-grants/how-to-apply/"
  },
  "r02-va-pension": {
    "audience": "veteran",
    "audienceLabel": "Wartime veteran; age or disability, service, income, and net-worth tests apply",
    "application": {
      "label": "Apply for Veterans Pension — online or Form 21P-527EZ",
      "url": "https://www.va.gov/pension/how-to-apply/"
    },
    "steps": [
      "Review wartime service and pension eligibility with an accredited representative.",
      "Gather service, income, net-worth and relevant medical or care-expense information privately.",
      "Apply on VA.gov or use VA Form 21P-527EZ; ask whether an intent to file is appropriate."
    ],
    "source": "https://www.va.gov/pension/how-to-apply/"
  },
  "r02-survivors-pension": {
    "audience": "survivor",
    "audienceLabel": "Qualifying surviving spouse or dependent child; survivors' service and financial criteria apply",
    "application": {
      "label": "Apply for Survivors Pension — Form 21P-534EZ",
      "url": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/survivors-pension/"
    },
    "steps": [
      "Review survivor relationship, qualifying wartime service and financial requirements with an accredited representative.",
      "Prepare the relevant family, service and financial evidence privately.",
      "Use the VA's survivor-benefits application (Form 21P-534EZ) or ask an accredited representative to help submit it."
    ],
    "source": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/survivors-pension/"
  },
  "r02-dic": {
    "audience": "survivor",
    "audienceLabel": "Potential qualifying surviving spouse or dependent child; service/death criteria require VA review",
    "application": {
      "label": "Apply for DIC or Survivors Pension — Form 21P-534EZ",
      "url": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/apply-for-dic-survivors-pension-accrued-benefits-form-21p-534ez/"
    },
    "steps": [
      "Review the service-related death and survivor criteria with an accredited representative.",
      "Gather family relationship and death/service evidence privately.",
      "For surviving spouses or children of veterans, use VA Form 21P-534EZ; other claimant categories may need different forms."
    ],
    "source": "https://www.va.gov/family-and-caregiver-benefits/survivor-compensation/dependency-indemnity-compensation/"
  },
  "r02-aid-attendance-housebound": {
    "audience": "veteran_or_survivor",
    "audienceLabel": "Qualifying VA pension recipients; added care needs or housebound status must be documented",
    "application": {
      "label": "Aid and Attendance/Housebound application — VA Form 21-2680",
      "url": "https://www.va.gov/pension/aid-attendance-housebound/"
    },
    "steps": [
      "Check whether the person receives or may qualify for VA pension, and discuss Aid and Attendance versus Housebound.",
      "Ask a medical examiner to complete VA Form 21-2680 as applicable.",
      "For a nursing-home resident, ask the facility and VA about Form 21-0779 before submission."
    ],
    "source": "https://www.va.gov/pension/aid-attendance-housebound/"
  },
  "va-housing-help": {
    "audience": "veteran",
    "audienceLabel": "Veteran experiencing homelessness or at risk of losing housing; family and supporters may also make contact",
    "application": {
      "label": "VA homeless assistance — call 877-424-3838",
      "url": "https://www.va.gov/resources/homeless-help/"
    },
    "steps": [
      "Call the National Call Center for Homeless Veterans at 877-424-3838 or use VA's housing-help chat.",
      "Tell the counselor the county, immediate housing situation and whether a safe place to stay is available.",
      "Ask for a local housing-services connection; the counselor determines appropriate program referrals."
    ],
    "source": "https://www.va.gov/resources/homeless-help/"
  },
  "va-ssvf": {
    "audience": "veteran",
    "audienceLabel": "Veteran family experiencing or at risk of homelessness; SSVF provider determines eligibility and coverage",
    "application": {
      "label": "VA homeless-help intake and SSVF referral",
      "url": "https://www.va.gov/resources/homeless-help/"
    },
    "steps": [
      "Contact VA homeless assistance or a published SSVF provider serving the county.",
      "Explain whether the household is homeless, at risk of eviction or struggling to remain housed.",
      "Ask the provider to screen for local SSVF prevention or rapid-rehousing services and available funds."
    ],
    "source": "https://department.va.gov/homeless/supportive-services-for-veteran-families/"
  },
  "ohio-waiver-home-modifications": {
    "audience": "any",
    "audienceLabel": "Eligible Ohio waiver participants; authorization depends on individual waiver and service plan",
    "application": {
      "label": "Ohio Medicaid home modification rule and conditions",
      "url": "https://codes.ohio.gov/ohio-administrative-code/rule-5160-44-13"
    },
    "steps": [
      "If already enrolled in a relevant waiver, ask the waiver case manager to assess the accessibility need.",
      "If not enrolled, ask a county aging or Medicaid intake organization which waiver screening route applies.",
      "Request the service-plan authorization and applicable provider requirements before arranging work."
    ],
    "source": "https://codes.ohio.gov/ohio-administrative-code/rule-5160-44-13"
  },
  "pa-link": {
    "audience": "any",
    "audienceLabel": "Pennsylvania aging or disability information and referral; individual programs have their own requirements",
    "application": {
      "label": "Request PA Link aging and disability resources",
      "url": "https://www.pa.gov/services/aging/request-aging-and-disability-resources-through-pa-link"
    },
    "steps": [
      "Start with PA Link's official request page.",
      "Describe the county and needed service, without sending detailed medical or financial records through this tool.",
      "Ask for the correct local aging or disability intake contact and its application steps."
    ],
    "source": "https://www.pa.gov/services/aging/request-aging-and-disability-resources-through-pa-link"
  },
  "ca-adrc": {
    "audience": "any",
    "audienceLabel": "California aging and disability navigation; service availability depends on local partners",
    "application": {
      "label": "California Aging and Disability Resource Connection",
      "url": "https://www.aging.ca.gov/Programs_and_Services/Aging_and_Disability_Resource_Connection/"
    },
    "steps": [
      "Use the California ADRC program information to locate an applicable local contact.",
      "Give the county and describe the needed aging or disability support.",
      "Request a referral to the appropriate provider and ask for an explanation of enrollment requirements."
    ],
    "source": "https://www.aging.ca.gov/Programs_and_Services/Aging_and_Disability_Resource_Connection/"
  }
});
export function getProgramGuidance(programId) {
  return PROGRAM_GUIDANCE[String(programId||"").toLowerCase()] || null;
}
