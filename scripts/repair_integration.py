"""Repairs for the working resource guide; source packets remain unchanged."""
import copy

REPAIRS = []
OPERATOR_REVIEWS = [
    ('help-me-grow', 'org-ohio-dcy', 'Ohio Department of Children and Youth', 'https://www.brightbeginningskids.org/HelpMeGrow.aspx', 'Help Me Grow operates under DCY; statewide intake is delivered through contractors.'),
    ('special-education', 'org-ohio-dew', 'Ohio Department of Education and Workforce', 'https://education.ohio.gov/Topics/Special-Education/Families-of-Students-with-Disabilities', 'Publisher of this state guidance hub; local educational agencies decide and deliver services.'),
    ('ohio-ltss', 'org-ohio-medicaid', 'Ohio Department of Medicaid', 'https://www.ohiohelps.org/Provider', 'OhioHelps is operated under contract with ODM; receiving programs retain eligibility authority.'),
]

def repair(programs, orgs, sources, relationships, today):
    for pid, oid, name, url, note in OPERATOR_REVIEWS:
        sid = 'repair-' + pid + '-operator'
        orgs[oid] = {'organization_id': oid, 'name': name, 'org_type': 'state_agency',
            'official_url': url, 'service_area': ['statewide'],
            'public_contact': {'phone': None, 'phone_label': None, 'email': None, 'contact_type': None, 'web_route': None},
            'internal_contact': None, 'verification': {'record_status': 'imported_unverified',
                'identity': 'official_source_reviewed', 'contact': 'imported_unverified', 'last_reviewed_on': today},
            'relationship_to_vhg': 'external_resource_not_confirmed_partner',
            'provenance': {'seed_record_id': None, 'batch_ids': ['repair-2026-10-06']}}
        programs[pid]['organization_id'] = oid
        sources.append({'source_id': sid, 'url': url, 'publisher': name, 'access_method': 'page_text_reviewed',
            'date_reviewed': today, 'published_date': None, 'published_effective_period': None, 'fetch_failed': False,
            'claims': [{'entity_id': pid, 'fields': ['organization_id']}, {'entity_id': oid, 'fields': ['name', 'official_url']}]})
        relationships.append({'from_id': oid, 'to_id': pid, 'type': 'provides_program', 'evidence_source_ids': [sid], 'note': note})
        REPAIRS.append({'entity_id': pid, 'field': 'organization_id', 'selected': oid, 'reason': note, 'source_ids': [sid]})

    entities = dict(orgs, **programs)
    for s in sources:
        for c in s.get('claims', []):
            mapped = []
            for field in c.get('fields', []):
                if field == 'geography':
                    mapped.append('service_area')
                    REPAIRS.append({'source_id': s['source_id'], 'entity_id': c['entity_id'], 'old_field': field, 'field': 'service_area', 'reason': 'B01 geography.service_area converted to v0.3 service_area.'})
                elif field == 'service_description':
                    mapped.append('description')
                    REPAIRS.append({'source_id': s['source_id'], 'entity_id': c['entity_id'], 'old_field': field, 'field': 'description', 'reason': 'B01 service_description converted to description.'})
                elif field == 'public_contact.address':
                    REPAIRS.append({'source_id': s['source_id'], 'entity_id': c['entity_id'], 'old_field': field, 'status': 'historical_only', 'reason': 'Old address was replaced by sourced office_details; do not claim support for the replacement value.'})
                else:
                    mapped.append(field)
            c['fields'] = mapped

    # Keep the alternative wording and its actual evidence dates for review.
    # No unsourced detail is promoted to the current next_step field.
    for pid in ['morrow-dd-intake', 'knox-dd-intake', 'marion-dd-intake', 'delaware-dd-intake', 'district5-adrn', 'coaaa-navigation']:
        REPAIRS.append({'entity_id': pid, 'field': 'next_step', 'status': 'source_specific_wording_review_pending',
            'reason': 'Current R-05 guidance retained; B01 alternatives remain in full conflict audit. Application checklists are not prerequisites to initial contact.'})

def path_exists(entity, path):
    for part in path.split('.'):
        if isinstance(entity, list) and part.isdigit():
            if int(part) >= len(entity):
                return False
            entity = entity[int(part)]
            continue
        if not isinstance(entity, dict) or part not in entity:
            return False
        entity = entity[part]
    return True

def extra_checks(ds):
    errors = []
    entities = {e[key]: e for collection, key in [('programs','program_id'),('organizations','organization_id')] for e in ds[collection]}
    source_ids = [s['source_id'] for s in ds['sources']]
    if len(set(source_ids)) != len(source_ids): errors.append(('error', 'duplicate source IDs'))
    for collection, key in [('organizations','organization_id'),('decisions','decision_id')]:
        ids = [e[key] for e in ds[collection]]
        if len(set(ids)) != len(ids): errors.append(('error', 'duplicate ' + key))
    for s in ds['sources']:
        for c in s.get('claims', []):
            for field in c.get('fields', []):
                if not path_exists(entities.get(c['entity_id']), field):
                    errors.append(('error', f"{s['source_id']}: unresolved claim field {c['entity_id']}.{field}"))
    for rel in ds['relationships']:
        for sid in rel.get('evidence_source_ids', []):
            if sid not in source_ids: errors.append(('error', 'unknown relationship evidence ' + sid))
    if ds['facilities']: errors.append(('error', 'Facility outreach records entered the resource guide'))
    for p in ds['programs']:
        if p['program_id'].endswith('-vso') and p['verification']['record_status'] != 'needs_recheck':
            errors.append(('error', 'County office lost its pending confirmation status'))
    return errors
