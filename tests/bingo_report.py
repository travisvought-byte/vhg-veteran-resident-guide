"""Regression checks for the October 2 official report extraction."""
import json
from pathlib import Path
report=json.loads((Path(__file__).resolve().parents[1]/'data/source/ohio-bingo-authorizations-2026-10-02.json').read_text())
rows=report['records']
assert report['pages']==545
assert len(rows)==report['license_column_rows']==6297
assert len(report['license_like_tokens_outside_license_column'])==10
assert sum(len(r['authorizations']) for r in rows)==report['bingo_type_entries']==6855
assert all(r[k] for r in rows for k in ('organization_display','license_number','street_address','city','zip','county','tax_status'))
assert sum(a['bingo_type']=='Type I' for r in rows for a in r['authorizations'])==717
coalton=next(r for r in rows if r['source_page']==127 and r['street_address']=='10 East 1st St')
assert coalton['authorizations'][0]=={'bingo_type':'Type I','authorized_days':None,'weeks_of_play':None}
assert coalton['authorizations'][2]['weeks_of_play']==52
assert 'Saturday' in coalton['authorizations'][2]['authorized_days']
botkins=next(r for r in rows if r['license_number']=='1047-28')
assert botkins['zip']=='Botkins' and botkins['city']=='OH'
assert sum('invalid_zip_in_source' in r['quality_flags'] for r in rows)==9
assert sum(a['authorized_days'] is None for r in rows for a in r['authorizations'] if a['bingo_type']=='Type I')==16
assert all(0<=a['weeks_of_play']<=53 for r in rows for a in r['authorizations'] if a['weeks_of_play'] is not None)
print('Report extraction regression checks passed')

wrapped=next(r for r in rows if r['source_page']==1 and r['street_address'].startswith('9210'))
assert wrapped['street_address']=='9210 Cincinnati Columbus Rd.'
assert wrapped['city']=='West Chester'
norwood=next(r for r in rows if r['source_page']==189 and r['license_number']=='0289-32')
assert norwood['city']=='Norwood'
assert '(513)531-1684' in norwood['street_address']
assert sum('repeated_site_in_source' in r['quality_flags'] for r in rows)==6
assert sum(r['county_normalized'] is None for r in rows)==3
assert all(r['county_normalized']=='Allen' for r in rows if r['county']=='ALLEN')
