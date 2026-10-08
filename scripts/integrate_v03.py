#!/usr/bin/env python3
"""
Integration pass: seed v0.2 + B01 + R-01 + R-02 + R-05  ->  dataset v0.3.0 candidate.

Run from the repository root:   python3 scripts/integrate_v03.py
Standard library only. Inputs are read, hashed and never modified.

Outputs (new files only):
  data/integrated/dataset_v0.3.1-candidate.json
  data/integrated/integration_report.md

Principles (see docs/integration-v0.3-rules.md):
  - Nothing is invented. A field without a source stays null.
  - Later research packets win for contact, verification and office details;
    every overwrite of a different non-null value is logged as a conflict.
  - Historical seed fields are kept in provenance.historical_fields, never re-dated.
  - Mobility tags (D-019) are derived only from fields that already carry a source.
  - Facilities are held (not reconciled) until Stage 1 is accepted.
"""
import hashlib, json, os, re, sys
from datetime import date
from repair_integration import repair, extra_checks, REPAIRS

TODAY = date.today().isoformat()
OUT_DIR = "data/integrated"

INPUTS = [
    # (label, path, required)
    ("seed", "data/seed/Ohio_Senior_Disability_Directory_Starter.json", True),
    ("B01", "data/batches/B01/b01_resources.json", True),
    ("R-01", "research/returns/R-01/records.json", True),
    ("R-02", "research/returns/R-02/records.json", False),
    ("R-05", "research/returns/R-05/records.json", False),
]
SCHEMA_PATH = "data/schema/schema_v0.3.json"

PILOT = ["Morrow", "Knox", "Marion", "Delaware"]

NEEDS_ENUM = {"help_at_home", "child_development_autism", "caregiver_respite",
              "equipment_home_accessibility", "benefits_and_funding", "care_facilities",
              "transportation", "veteran_services", "dd_intake_service_coordination",
              "education_special_education", "employment_transition", "general_navigation"}
AGE_ENUM = {"prenatal", "under_3", "age_3_5", "school_age", "transition_age", "adult_18_59",
            "older_adult_60_plus", "caregiver", "veteran", "veteran_dependent", "all_ages"}
PROGRAM_TYPES = {"navigation_service", "eligibility_intake", "benefit_or_grant", "direct_service",
                 "guidance_hub", "existing_directory", "lookup_instruction", "navigation_bundle"}
VERIF_ENUM = ["imported_unverified", "official_search_extract_only", "official_source_reviewed",
              "agency_confirmed", "needs_recheck", "withdrawn_or_closed_confirmed"]

# ---- B01 vocabulary -> schema v0.3 enums (rule M-1). Unmapped values are reported, never guessed.
NEEDS_MAP = {
    "developmental_disability_intake": ["dd_intake_service_coordination"],
    "service_coordination": ["dd_intake_service_coordination"],
    "long_term_support_navigation": ["general_navigation"],
    "help_at_home": ["help_at_home"],
    "care_assessment": ["help_at_home"],
    "benefits_navigation": ["benefits_and_funding", "veteran_services"],
    "benefits_application_help": ["benefits_and_funding"],
    "home_accessibility_navigation": ["equipment_home_accessibility"],
    "medically_necessary_home_accessibility": ["equipment_home_accessibility"],
    "home_accessibility_funding": ["equipment_home_accessibility"],
    "developmental_concerns": ["child_development_autism"],
    "early_intervention": ["child_development_autism"],
    "school_evaluation": ["education_special_education"],
    "transition_planning": ["employment_transition"],
    "family_navigation": ["general_navigation"],
}
AGE_MAP = {
    "under_3": ["under_3"],
    "age_3_plus": ["age_3_5", "school_age", "transition_age", "adult_18_59", "older_adult_60_plus"],
    "preschool_3_5": ["age_3_5"],
    "school_age": ["school_age"],
    "transition_age": ["transition_age"],
    "adults": ["adult_18_59", "older_adult_60_plus"],
    "older_adults": ["older_adult_60_plus"],
    "younger_disabled_adults": ["adult_18_59"],
    "disabled_adults": ["adult_18_59"],
    "caregivers": ["caregiver"],
    "veterans": ["veteran"],
    "service_members": ["veteran"],
    "eligible_dependents": ["veteran_dependent"],
    "all_ages": ["all_ages"],
}
AGE_FLAGGED = {"children": "B01 'children' has no exact enum; left out of age_life_stage pending review",
               "service_members": "mapped to 'veteran'; schema has no active-duty value"}
TYPE_MAP = {"navigation_service": "navigation_service", "program": "benefit_or_grant",
            "program_navigation_bundle": "navigation_bundle", "program_entry_route": "eligibility_intake",
            "guidance_hub": "guidance_hub"}

# ---- Organization assignments (rule M-2). Each is the publisher named on the record's own official URL.
ORG_ASSIGN = {
    "morrow-dd-intake": ("org-morrow-dd", "Morrow County Board of Developmental Disabilities", "county_board_dd", ["Morrow"]),
    "delaware-dd-intake": ("org-delaware-dd", "Delaware County Board of Developmental Disabilities", "county_board_dd", ["Delaware"]),
    "knox-dd-intake": ("org-knox-dd", "Knox County Board of Developmental Disabilities", "county_board_dd", ["Knox"]),
    "marion-dd-intake": ("org-marion-dd", "Marion County Board of Developmental Disabilities", "county_board_dd", ["Marion"]),
    "district5-adrn": ("org-aaa5", "Area Agency on Aging District 5", "area_agency_on_aging", None),
    "coaaa-navigation": ("org-coaaa", "Central Ohio Area Agency on Aging", "area_agency_on_aging", None),
    "morrow-vso": ("org-morrow-vso", None, "county_veterans_service", ["Morrow"]),
    "knox-vso": ("org-knox-vso", None, "county_veterans_service", ["Knox"]),
    "marion-vso": ("org-marion-vso", None, "county_veterans_service", ["Marion"]),
    "delaware-vso": ("org-delaware-vso", None, "county_veterans_service", ["Delaware"]),
    "va-hisa": ("org-us-va", "U.S. Department of Veterans Affairs", "federal_agency", []),
    "va-adapted-housing": ("org-us-va", "U.S. Department of Veterans Affairs", "federal_agency", []),
    # help-me-grow, special-education, ohio-ltss: operator left unassigned for human review (no guess).
}

# ---- Canonical organization IDs (rule M-4). Packets used batch-prefixed IDs; one organization gets one ID.
ORG_ALIAS = {
    "r02-va": "org-us-va", "r02-ohio-dvs": "org-ohio-dvs", "r02-county-vsc": "org-ohio-county-vscs",
    "r02-alliance": "org-national-alliance-care-at-home",
    "r05-district5": "org-aaa5", "r05-coaaa": "org-coaaa", "r05-helpline": "org-helpline-delmor",
    "r05-pathways": "org-pathways-central-ohio", "r05-easterseals": "org-easterseals-cseo",
    "r05-aging": "org-ohio-aging", "r05-cms": "org-us-cms", "r05-ood": "org-ohio-ood",
    "r05-dro": "org-disability-rights-ohio",
}
for _c in ("morrow", "knox", "marion", "delaware"):
    ORG_ALIAS[f"r05-{_c}-dd"] = f"org-{_c}-dd"
    ORG_ALIAS[f"r05-{_c}-jfs"] = f"org-{_c}-jfs"

def canon_doc(doc, label):
    """Rewrite batch-prefixed organization IDs everywhere they appear in a v0.3 packet."""
    doc = json.loads(json.dumps(doc))
    c = lambda i: ORG_ALIAS.get(i, i)
    for o in doc.get("organizations", []):
        if o["organization_id"] in ORG_ALIAS:
            R.idmap.append((ORG_ALIAS[o["organization_id"]], f"organization ID {o['organization_id']} ({label}) mapped to canonical ID"))
        o["organization_id"] = c(o["organization_id"])
    for p in doc.get("programs", []):
        p["organization_id"] = c(p.get("organization_id"))
    for r in doc.get("relationships", []):
        r["from_id"], r["to_id"] = c(r["from_id"]), c(r["to_id"])
    for s in doc.get("sources", []):
        for cl in s.get("claims", []):
            cl["entity_id"] = c(cl["entity_id"])
    return doc

# ---- helpers -------------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

OFFICE_MAILBOXES = {"board", "info", "intake", "contactus", "vets", "vso", "hmgreferrals",
                    "exceptionalchildren", "preschoolspecialeducation"}
PHONE_RE = re.compile(r"^\(?\d{3}\)?[-. ]?\d{3}-\d{4}")

class Report:
    def __init__(self):
        self.conflicts, self.flags, self.notes, self.idmap = [], [], [], []
    def conflict(self, eid, field, kept, replaced, src):
        self.conflicts.append((eid, field, kept, replaced, src))
    def flag(self, eid, msg):
        self.flags.append((eid, msg))

R = Report()

def weakest(*vals):
    vals = [v for v in vals if v]
    order = {v: i for i, v in enumerate(VERIF_ENUM)}
    # needs_recheck and withdrawn are not on the strength ladder; they dominate.
    for special in ("withdrawn_or_closed_confirmed", "needs_recheck"):
        if special in vals:
            return special
    return min(vals, key=lambda v: order.get(v, 0)) if vals else "imported_unverified"

# ---- seed v0.2 -> programs -------------------------------------------------------------------
def seed_resources(seed):
    for key, val in seed.items():
        if isinstance(val, list) and "resource" in key.lower():
            return key, val
    return None, []

def seed_to_program(rec):
    pid = rec.get("id") or slug(rec.get("name", "unnamed"))
    county = rec.get("county")
    if county and county in PILOT:
        area = [county]
    elif county:
        area = [county]
        R.flag(pid, f"seed service_area kept verbatim ('{county}'); not normalized")
    else:
        area = []
    phone = rec.get("phone")
    prog = {
        "program_id": pid,
        "name": rec.get("name"),
        "program_type": "navigation_service",
        "organization_id": None,
        "official_url": rec.get("url"),
        "needs_supported": [],
        "age_life_stage": [],
        "service_area": area,
        "description": rec.get("offers"),
        "eligibility_summary": rec.get("eligibility"),
        "eligibility_decision_owner": None,
        "application_or_referral_route": None,
        "next_step": rec.get("action"),
        "constraints": [rec["limits"]] if rec.get("limits") else [],
        "public_contact": {"phone": phone if phone and PHONE_RE.match(phone) else None,
                           "phone_label": None, "email": None, "contact_type": None, "web_route": None},
        "internal_contact": None,
        "verification": {"record_status": "imported_unverified", "identity": "imported_unverified",
                         "contact": "imported_unverified", "last_reviewed_on": rec.get("reviewed_on")},
        "relationship_to_vhg": "external_resource_not_confirmed_partner",
        "availability_not_established": empty_availability(),
        "unresolved_questions": [],
        "provenance": {"seed_record_id": pid, "batch_ids": ["seed-v0.2"], "historical_fields": rec},
    }
    if phone and not PHONE_RE.match(phone):
        R.flag(pid, f"seed phone field is guidance text, not a number: '{phone}' (kept in historical_fields)")
    R.flag(pid, "seed-only record: program_type defaulted to navigation_service; needs, ages and operator need review")
    return prog

def empty_availability():
    return {k: None for k in ("accepting_referrals", "waitlist_status", "appointment_availability",
                              "remaining_funds", "payer_acceptance")}

# ---- B01 resource -> program + sources ------------------------------------------------------
def map_list(values, table, eid, what):
    out = []
    for v in values or []:
        if v in AGE_FLAGGED and what == "age":
            R.flag(eid, AGE_FLAGGED[v])
        if v in table:
            for m in table[v]:
                if m not in out:
                    out.append(m)
        elif v not in AGE_FLAGGED:
            R.flag(eid, f"unmapped {what} value '{v}' dropped from enum field (kept in provenance)")
    return out

def b01_to_program(r, sources):
    pid = r["resource_id"]
    pc = r.get("public_contact") or {}
    contact = {"phone": pc.get("phone"), "phone_label": "main office" if pc.get("phone") else None,
               "email": pc.get("email"), "contact_type": None,
               "web_route": pc.get("locator_url") or pc.get("application_url")}
    if pc.get("locator_url") or pc.get("application_url"):
        contact["contact_type"] = "web_form_or_locator"
    elif pc.get("phone"):
        contact["contact_type"] = "office"
    extra_contacts = {k: v for k, v in pc.items() if k not in ("phone", "email", "locator_url", "application_url", "address") and v}
    internal = None
    email = pc.get("email")
    if email and email.split("@")[0].lower() not in OFFICE_MAILBOXES:
        R.flag(pid, f"email '{email}' looks like a named individual (D-006): moved to internal_contact")
        contact["email"] = None
        internal = {"name": None, "email": email, "note": "Moved from public_contact under D-006 pending review"}
    # source entities
    access = set()
    for i, s in enumerate(r.get("sources") or []):
        sid = f"{pid}-s{i+1}"
        access.add(s.get("access_method"))
        sources.append({
            "source_id": sid, "url": s["url"], "publisher": None,
            "access_method": s.get("access_method"), "date_reviewed": s.get("date_reviewed"),
            "published_date": s.get("published_date"),
            "published_effective_period": str(s["published_effective_year"]) if s.get("published_effective_year") else None,
            "fetch_failed": False,
            "claims": [{"entity_id": pid, "fields": s.get("fields_supported") or []}],
        })
    base = r.get("verification_status") or "official_source_reviewed"
    contact_status = "official_search_extract_only" if "official_search_extract_reviewed" in access else base
    prog = {
        "program_id": pid,
        "name": r.get("name"),
        "program_type": TYPE_MAP.get(r.get("record_type"), "navigation_service"),
        "organization_id": ORG_ASSIGN[pid][0] if pid in ORG_ASSIGN else None,
        "official_url": r.get("official_url"),
        "needs_supported": map_list(r.get("needs_supported"), NEEDS_MAP, pid, "needs"),
        "age_life_stage": map_list(r.get("age_life_stage"), AGE_MAP, pid, "age"),
        "service_area": normalize_area(r.get("geography", {}).get("service_area", []), pid),
        "description": r.get("service_description"),
        "eligibility_summary": r.get("eligibility_summary"),
        "eligibility_decision_owner": r.get("eligibility_decision_owner"),
        "application_or_referral_route": r.get("application_or_referral_route"),
        "next_step": r.get("next_step"),
        "payment_or_funding_summary": r.get("payment_or_funding_summary"),
        "constraints": r.get("constraints") or [],
        "public_contact": contact,
        "internal_contact": internal,
        "verification": {"record_status": weakest(base, contact_status), "identity": base,
                         "contact": contact_status, "last_reviewed_on": r.get("reviewed_on")},
        "relationship_to_vhg": r.get("relationship_to_vhg", "external_resource_not_confirmed_partner"),
        "availability_not_established": empty_availability(),
        "unresolved_questions": r.get("unresolved_questions") or [],
        "provenance": {"seed_record_id": r.get("seed_record_id"), "batch_ids": ["OH-SDR-S1-B01"],
                       "historical_fields": r.get("preserved_seed_fields")},
        "b01_original_vocab": {"needs_supported": r.get("needs_supported"), "age_life_stage": r.get("age_life_stage")},
    }
    if extra_contacts:
        prog["additional_published_contacts"] = extra_contacts
    if pc.get("address"):
        prog["b01_published_address"] = pc["address"]
    if r.get("record_type") not in TYPE_MAP:
        R.flag(pid, f"record_type '{r.get('record_type')}' defaulted to navigation_service")
    if pid not in ORG_ASSIGN:
        R.flag(pid, "operator organization not assigned (no single operator confirmed); needs review")
    return prog

def normalize_area(area, eid):
    out = []
    for a in area:
        if a in PILOT or re.fullmatch(r"[A-Z][a-z]+", a):
            out.append(a)
        elif "statewide" in a.lower() or "all ohio" in a.lower():
            out.append("statewide")
        elif "federal" in a.lower():
            out.append("federal")
        else:
            out.append(a)
            R.flag(eid, f"service_area value kept verbatim: '{a}'")
    return out

# ---- generic v0.3 merge ---------------------------------------------------------------------
LATER_WINS_WHOLE = ("public_contact", "verification", "office_details", "internal_contact")
UNION_LISTS = ("needs_supported", "age_life_stage", "service_area", "constraints", "unresolved_questions", "what_to_ask")

def merge_entity(old, new, eid, label):
    out = dict(old)
    for k, v in new.items():
        if k == "provenance":
            p = dict(old.get("provenance") or {})
            ids = list(p.get("batch_ids") or [])
            for b in (v or {}).get("batch_ids") or []:
                if b not in ids:
                    ids.append(b)
            p["batch_ids"] = ids
            if not p.get("seed_record_id"):
                p["seed_record_id"] = (v or {}).get("seed_record_id")
            out["provenance"] = p
        elif k in LATER_WINS_WHOLE:
            if v is not None:
                if k == "public_contact":
                    v = dict(v)
                    for ck, earlier in (old.get(k) or {}).items():
                        if v.get(ck) is None and earlier is not None:
                            # R-01 explicitly suppresses the conflicting Morrow email.
                            suppressed = eid == "morrow-vso" and label == "R-01" and ck == "email"
                            if not suppressed:
                                v[ck] = earlier
                                R.notes.append(f"{eid}.{k}.{ck}: ordinary unknown null in {label} retained earlier sourced value; no new review date implied.")
                if old.get(k) not in (None, v) and k == "public_contact":
                    for ck in set((old.get(k) or {}).keys()) | set(v.keys()):
                        a, b = (old.get(k) or {}).get(ck), v.get(ck)
                        if a not in (None, b):
                            R.conflict(eid, f"{k}.{ck}", b, a, label)
                out[k] = v
        elif k in UNION_LISTS:
            merged = list(old.get(k) or [])
            for item in v or []:
                if item not in merged:
                    merged.append(item)
            out[k] = merged
        elif v is None:
            continue  # a later null never erases a sourced earlier value
        elif old.get(k) is None:
            out[k] = v
        elif old.get(k) != v:
            R.conflict(eid, k, v, old.get(k), label)
            out[k] = v
    return out

def is_v03(doc):
    return isinstance(doc, dict) and "programs" in doc and "organizations" in doc

# ---- mobility tags (D-019, rule M-3) ----------------------------------------------------------
def tag(status, note, source_ids, rule):
    return {"status": status, "note": note, "source_ids": source_ids, "derived_by": rule}

def derive_mobility(p, claims_index):
    pid, mob = p["program_id"], {}
    od = p.get("office_details") or {}
    is_vso = pid.endswith("-vso")
    # transportation: only from a published-services field that carries sources
    ps = od.get("published_services") or {}
    if ps.get("value") and any("transport" in s.lower() for s in ps["value"]):
        note = "Office publishes transportation among its services. Ask about scheduling and eligibility."
        tn = od.get("transport_nontravel_note") or {}
        if tn.get("value"):
            note += " " + tn["value"]
        mob["transportation"] = tag("published_by_source", note, ps.get("source_ids", []), "M-3a")
    elif is_vso:
        mob["transportation"] = tag("not_yet_confirmed", "Ask whether the office arranges rides to VA appointments.", [], "M-3a")
    # travel alternative (facility / home visits, phone or video)
    if is_vso:
        vals = [od.get("facility_visit"), od.get("home_visit")]
        if any(v and v.get("value") for v in vals if isinstance(v, dict)):
            mob["travel_alternative"] = tag("published_by_source", "See office_details visit fields.", [], "M-3b")
        else:
            mob["travel_alternative"] = tag("not_yet_confirmed",
                "Ask whether staff visit residents in facilities, or offer phone or video appointments.", [], "M-3b")
    # equipment / home accessibility: needs field must be source-backed
    if "equipment_home_accessibility" in p.get("needs_supported", []):
        backed = claims_index.get((pid, "needs_supported")) or claims_index.get((pid, "eligibility_summary"))
        if backed:
            mob["equipment_home_access"] = tag("published_by_source",
                p.get("next_step") or "See program record.", backed, "M-3c")
        else:
            note = ("Ask how the office helps start an equipment or home-accessibility request." if is_vso else
                    "Record lists home accessibility, but no source claim backs that field yet.")
            mob["equipment_home_access"] = tag("not_yet_confirmed", note, [], "M-3c")
    # help at home after discharge
    if "help_at_home" in p.get("needs_supported", []):
        backed = claims_index.get((pid, "needs_supported"))
        mob["discharge_home_support"] = tag("published_by_source" if backed else "not_yet_confirmed",
            p.get("next_step") or "See program record.", backed or [], "M-3d")
    return mob

# ---- main ------------------------------------------------------------------------------------
def main():
    root_ok = all(os.path.exists(p) for _, p, req in INPUTS if req)
    if not root_ok:
        missing = [p for _, p, req in INPUTS if req and not os.path.exists(p)]
        sys.exit("Run from the repository root. Missing required inputs: " + ", ".join(missing))

    derived, docs = [], {}
    for label, path, req in INPUTS:
        if os.path.exists(path):
            docs[label] = load(path)
            derived.append({"name": path, "batch_id": label, "sha256": sha256(path)})
        else:
            R.notes.append(f"Optional input not found, skipped: {path}")

    programs, orgs, sources, relationships = {}, {}, [], []

    # 1. seed
    seed = docs["seed"]
    skey, srecs = seed_resources(seed)
    if not srecs:
        R.notes.append("Seed resource list not found by key; seed programs not imported. Inspect seed keys: "
                       + ", ".join(seed.keys()))
    for rec in srecs:
        p = seed_to_program(rec)
        programs[p["program_id"]] = p
    seed_facility_count = sum(len(v) for k, v in seed.items() if isinstance(v, list) and "facilit" in k.lower())

    # 2. B01 (replaces seed records it updates; keeps seed fields as history)
    for r in docs["B01"]["resources"]:
        p = b01_to_program(r, sources)
        pid = p["program_id"]
        if pid in programs:
            R.idmap.append((pid, "seed -> B01 update (seed fields kept in provenance.historical_fields)"))
            p["provenance"]["batch_ids"] = ["seed-v0.2", "OH-SDR-S1-B01"]
            # remove the seed-only review flag for records B01 re-reviewed
            R.flags = [f for f in R.flags if not (f[0] == pid and f[1].startswith("seed"))]
        else:
            R.idmap.append((pid, "B01 addition"))
        programs[pid] = p
        if pid in ORG_ASSIGN:
            oid, oname, otype, area = ORG_ASSIGN[pid]
            if oid not in orgs and oname:
                orgs[oid] = {"organization_id": oid, "name": oname, "org_type": otype,
                             "official_url": None, "service_area": area if area is not None else p["service_area"],
                             "public_contact": {"phone": None, "phone_label": None, "email": None,
                                                "contact_type": None, "web_route": None},
                             "internal_contact": None,
                             "verification": {"record_status": "official_source_reviewed",
                                              "identity": "official_source_reviewed",
                                              "contact": "imported_unverified", "last_reviewed_on": p["verification"]["last_reviewed_on"]},
                             "relationship_to_vhg": "external_resource_not_confirmed_partner",
                             "provenance": {"seed_record_id": None, "batch_ids": ["OH-SDR-S1-B01"]}}
                R.flag(oid, "organization created from program publisher; official_url and contact left null for review")
            relationships.append({"from_id": oid, "to_id": pid, "type": "provides_program",
                                  "evidence_source_ids": [s["source_id"] for s in sources if s["claims"][0]["entity_id"] == pid][:1],
                                  "note": "Operator inferred from the program's own official URL (rule M-2)."})

    # SAH/SHA split (B01 notes): children of the bundle, no new facts invented
    if "va-adapted-housing" in programs:
        for cid, cname in (("va-sah", "VA Specially Adapted Housing (SAH) grant"),
                           ("va-sha", "VA Special Housing Adaptation (SHA) grant")):
            programs[cid] = {
                "program_id": cid, "name": cname, "program_type": "benefit_or_grant",
                "organization_id": "org-us-va", "parent_program_id": "va-adapted-housing",
                "official_url": programs["va-adapted-housing"]["official_url"],
                "needs_supported": ["equipment_home_accessibility"], "age_life_stage": ["veteran"],
                "service_area": ["federal"], "description": None, "eligibility_summary": None,
                "eligibility_decision_owner": "VA Veterans Benefits Administration.",
                "application_or_referral_route": "See parent route va-adapted-housing.", "next_step": None,
                "amounts": [], "constraints": ["Amounts intentionally null until current-year VA limits are rechecked."],
                "public_contact": {"phone": None, "phone_label": None, "email": None, "contact_type": None, "web_route": None},
                "internal_contact": None,
                "verification": {"record_status": "official_source_reviewed", "identity": "official_source_reviewed",
                                 "contact": "imported_unverified", "last_reviewed_on": programs["va-adapted-housing"]["verification"]["last_reviewed_on"]},
                "relationship_to_vhg": "external_resource_not_confirmed_partner",
                "availability_not_established": empty_availability(), "unresolved_questions": [
                    "Program-specific eligibility text to be split from the bundle source on next review."],
                "provenance": {"seed_record_id": None, "batch_ids": ["OH-SDR-S1-B01", "integration-split"]},
            }
            relationships.append({"from_id": cid, "to_id": "va-adapted-housing", "type": "part_of",
                                  "evidence_source_ids": [], "note": "Split per B01 notes; shared application route."})
            R.idmap.append((cid, "split from va-adapted-housing bundle"))

    # 3. v0.3-shaped research returns, in order
    for label in ("R-01", "R-02", "R-05"):
        doc = docs.get(label)
        if doc is None:
            continue
        if is_v03(doc):
            doc = canon_doc(doc, label)
        if not is_v03(doc):
            R.notes.append(f"{label} is not v0.3-shaped (keys: {', '.join(doc.keys()) if isinstance(doc, dict) else type(doc).__name__}); "
                           "skipped. Needs a mapping before merge.")
            continue
        for o in doc.get("organizations", []):
            oid = o["organization_id"]
            orgs[oid] = merge_entity(orgs[oid], o, oid, label) if oid in orgs else o
        for p in doc.get("programs", []):
            pid = p["program_id"]
            if pid in programs:
                programs[pid] = merge_entity(programs[pid], p, pid, label)
                R.idmap.append((pid, f"updated by {label}"))
            else:
                programs[pid] = p
                R.idmap.append((pid, f"{label} addition"))
        existing_src = {s["source_id"]: s for s in sources}
        for s in doc.get("sources", []):
            sid = s["source_id"]
            if sid in existing_src:
                if existing_src[sid]["url"] != s["url"]:
                    new_id = f"{sid}-{slug(label)}"
                    R.flag(sid, f"source_id collision with different URL in {label}; renamed to {new_id}")
                    s = dict(s, source_id=new_id)
                    sources.append(s)
                else:
                    existing_src[sid]["claims"].extend(s.get("claims", []))
            else:
                sources.append(s)
        relationships.extend(doc.get("relationships", []))

    repair(programs, orgs, sources, relationships, TODAY)

    # 4. claim index, then mobility tags
    claims_index = {}
    for s in sources:
        for c in s.get("claims", []):
            for f in c.get("fields", []):
                claims_index.setdefault((c["entity_id"], f.split(".")[0]), []).append(s["source_id"])
    mobility_count = 0
    for p in programs.values():
        mob = derive_mobility(p, claims_index)
        if mob:
            p["mobility"] = mob
            mobility_count += 1

    # 5. dataset
    dataset = {
        "dataset": {"version": "0.3.1-candidate", "prepared_on": TODAY, "publication_status": "internal_working",
                    "scope": {"state": "Ohio", "pilot_counties": PILOT,
                              "intended_population": "Veterans, surviving spouses, families and care-facility staff using support resources; "
                                                     "general aging and disability resources are a linked layer",
                              "facility_inventory": "excluded; retained separately for VHG outreach"},
                    "derived_from": derived},
        "organizations": sorted(orgs.values(), key=lambda o: o["organization_id"]),
        "programs": sorted(programs.values(), key=lambda p: p["program_id"]),
        "locations": [],
        "facilities": [],
        "pathways": [],
        "sources": sources,
        "relationships": relationships,
        "funding_leads": [],
        "decisions": [
            {"decision_id": "D-017", "date": TODAY, "owner": "Travis", "status": "decided",
             "decision": "Resource guide for veterans, families and care-facility staff. Facility inventory is excluded and retained separately for outreach.",
             "reason": "Explicit owner instruction on October 6, 2026.", "affected_ids": []},
            {"decision_id": "D-018", "date": TODAY, "owner": "Travis / Codex working implementation", "status": "open",
             "decision": "Integration precedence: Packets are applied in a reproducible order; current corrected verification and office details are used; "
                         "ordinary unknown nulls preserve earlier sourced values; explicit conflict suppression stays null; full overwrites are retained in the audit.",
             "reason": "Preserves competing evidence and flags same-date wording conflicts for review.", "affected_ids": []},
            {"decision_id": "D-019", "date": TODAY, "owner": "Travis / Codex working implementation", "status": "open",
             "decision": "Add program.mobility tags (transportation, travel_alternative, equipment_home_access, "
                         "discharge_home_support) with status confirmed_by_office / published_by_source / "
                         "not_yet_confirmed / not_researched, derived only from source-backed fields.",
             "reason": "Supports the mobility-first interface requested by Travis on 2026-10-02.", "affected_ids": []},
        ],
    }
    R.notes.append(f"Facilities held: {seed_facility_count} seed facilities remain in the seed file only "
                   "(excluded from guide scope under D-017; available for separate outreach). Pathways from B01 not yet converted.")
    R.notes.append("Seed funding leads and scenarios not carried into this candidate; they remain in the seed file.")

    # drop "left null for review" flags for organizations a later packet filled in
    filled = {o["organization_id"] for o in orgs.values() if o.get("official_url")}
    R.flags = [f for f in R.flags if not (f[0] in filled and f[1].startswith("organization created"))]

    # 6. checks (stdlib; mirrors key schema constraints)
    problems = validate(dataset) + extra_checks(dataset)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_json = os.path.join(OUT_DIR, "dataset_v0.3.1-candidate.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    write_report(dataset, problems, mobility_count, os.path.join(OUT_DIR, "integration_report.md"))
    print(f"Wrote {out_json}: {len(dataset['organizations'])} organizations, {len(dataset['programs'])} programs, "
          f"{len(dataset['sources'])} sources, {len(dataset['relationships'])} relationships.")
    print(f"Conflicts logged: {len(R.conflicts)}. Review flags: {len(R.flags)}. "
          f"Errors: {sum(1 for k, _ in problems if k == 'error')}. "
          f"Seed records pending review: {sum(1 for k, _ in problems if k == 'pending')}.")
    with open(os.path.join(OUT_DIR, "integration_audit.json"), "w", encoding="utf-8") as f:
        json.dump({"input_hashes": derived, "conflicts": [{"entity_id": e, "field": field, "selected": kept, "previous": previous, "packet": packet} for e, field, kept, previous, packet in R.conflicts], "repairs": REPAIRS, "validation": problems}, f, indent=2, ensure_ascii=False)
    return 1 if any(k == "error" for k, _ in problems) else 0

def validate(ds):
    problems = []
    org_ids = {o["organization_id"] for o in ds["organizations"]}
    prog_ids = {p["program_id"] for p in ds["programs"]}
    all_ids = org_ids | prog_ids
    idre = re.compile(r"^[a-z0-9][a-z0-9-]*$")
    seen = set()
    for p in ds["programs"]:
        pid = p["program_id"]
        if pid in seen: problems.append(f"duplicate program_id {pid}")
        seen.add(pid)
        if not idre.match(pid): problems.append(f"{pid}: id pattern")
        if p.get("program_type") not in PROGRAM_TYPES: problems.append(f"{pid}: program_type {p.get('program_type')}")
        for n in p.get("needs_supported", []):
            if n not in NEEDS_ENUM: problems.append(f"{pid}: needs value {n}")
        for a in p.get("age_life_stage", []):
            if a not in AGE_ENUM: problems.append(f"{pid}: age value {a}")
        oid = p.get("organization_id")
        if oid and oid not in org_ids: problems.append(f"{pid}: organization_id {oid} not found")
        if oid is None and p.get("program_type") not in ("existing_directory", "lookup_instruction"):
            seed_only = (p.get("provenance") or {}).get("batch_ids") == ["seed-v0.2"]
            problems.append(("pending" if seed_only else "error",
                             f"{pid}: no operator organization (allowed only for existing_directory / lookup_instruction)"))
        v = p.get("verification") or {}
        for k in ("record_status", "identity", "contact"):
            if v.get(k) not in VERIF_ENUM: problems.append(f"{pid}: verification.{k} {v.get(k)}")
        par = p.get("parent_program_id")
        if par and par not in prog_ids: problems.append(f"{pid}: parent {par} not found")
    for s in ds["sources"]:
        for c in s.get("claims", []):
            if c["entity_id"] not in all_ids:
                problems.append(f"source {s['source_id']}: claim on unknown entity {c['entity_id']}")
    for r in ds["relationships"]:
        for end in ("from_id", "to_id"):
            if r[end] not in all_ids: problems.append(f"relationship {r['from_id']}->{r['to_id']}: {end} unknown")
        if r["type"] == "refers_to" and not r.get("evidence_source_ids"):
            problems.append(f"relationship {r['from_id']}->{r['to_id']}: refers_to needs evidence")
    return [p if isinstance(p, tuple) else ("error", p) for p in problems]

def write_report(ds, problems, mobility_count, path):
    L = [f"# Integration report — dataset v0.3.1 candidate", "",
         f"Prepared {TODAY} by scripts/integrate_v03.py. Internal working file; not accepted data and not for publication.", "",
         "## Inputs (unchanged; hashes recorded)", ""]
    for d in ds["dataset"]["derived_from"]:
        L.append(f"- `{d['name']}` ({d['batch_id']}) sha256 `{d['sha256']}`")
    L += ["", "## Result", "",
          f"- Organizations: {len(ds['organizations'])}",
          f"- Programs: {len(ds['programs'])}",
          f"- Sources: {len(ds['sources'])}",
          f"- Relationships: {len(ds['relationships'])}",
          f"- Programs with mobility tags: {mobility_count}", "",
          "## Record map", "", "| ID | What happened |", "|---|---|"]
    for pid, what in R.idmap:
        L.append(f"| `{pid}` | {what} |")
    L += ["", "## Conflicts (later value kept; earlier value shown for review)", ""]
    if R.conflicts:
        L += ["| Entity | Field | Kept | Replaced | From |", "|---|---|---|---|---|"]
        for eid, f, kept, rep, src in R.conflicts:
            L.append(f"| `{eid}` | {f} | {json.dumps(kept)[:120]} | {json.dumps(rep)[:120]} | {src} |")
    else:
        L.append("None.")
    L += ["", "## Review flags (human decision needed)", ""]
    for eid, msg in R.flags:
        L.append(f"- `{eid}`: {msg}")
    errors = [m for k, m in problems if k == "error"]
    pending = [m for k, m in problems if k == "pending"]
    L += ["", "## Check results", ""]
    L += [f"- {m}" for m in errors] or ["All structural and reference checks passed."]
    L += ["", "## Seed-only records awaiting review (expected; not errors)", "",
          "These came from the v0.2 seed and no research packet has re-reviewed them yet. "
          "They need an operator, type, needs and ages before acceptance.", ""]
    L += [f"- {m}" for m in pending] or ["None."]
    L += ["", "## Notes", ""] + [f"- {n}" for n in R.notes]
    L += ["", "## Not done in this pass", "",
          "- No phone confirmations; no record is `agency_confirmed`.",
          "- Facilities, pathways, funding leads and scenarios not converted (see Notes).",
          "- Mobility tags are derived proposals (rules M-3a–d); each carries `derived_by` and its source IDs.", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

if __name__ == "__main__":
    sys.exit(main())
