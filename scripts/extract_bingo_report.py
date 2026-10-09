"""Preserve report cells verbatim; authorizations are not verified event schedules."""
import re,json,collections,hashlib,xml.etree.ElementTree as ET
import argparse, subprocess, tempfile
from pathlib import Path
parser=argparse.ArgumentParser(description='Extract Ohio authorized bingo locations with page provenance. Requires Poppler pdftotext.')
parser.add_argument('pdf',type=Path);parser.add_argument('output',type=Path)
args=parser.parse_args();src=str(args.pdf)
county_names={r['county'].casefold():r['county'] for r in json.loads((Path(__file__).resolve().parents[1]/'data/public/ohio-county-veterans-offices.json').read_text())}
with tempfile.NamedTemporaryFile(suffix='.html',delete=False) as f: bbox_path=f.name
subprocess.run(['pdftotext','-bbox-layout',src,bbox_path],check=True)
ns={'x':'http://www.w3.org/1999/xhtml'}
class Page:
 def __init__(self,p): self.p=p
 def get_text(self,kind): return [(float(w.get('xMin')),float(w.get('yMin')),float(w.get('xMax')),float(w.get('yMax')),w.text or '') for w in self.p.findall('.//x:word',ns)]
doc=[Page(p) for p in ET.parse(bbox_path).findall('.//x:page',ns)];rows=[];issues=[];license_tokens=0;type_tokens=0;outside_license_tokens=[]
for pi,page in enumerate(doc):
 w=page.get_text('words'); headers={key:next((a[0] for a in sorted(w,key=lambda z:z[1]) if a[4]==key and a[1]<160),None) for key in ['Lic.','Street','Zip','Bingo','Days']}
 if any(x is None for x in headers.values()):issues.append((pi+1,'headers'));continue
 bounds=[headers[x]-2 for x in ['Lic.','Street','Zip','Bingo','Days']]
 anchors=sorted([a for a in w if re.fullmatch(r'\d{4}-\d{2}',a[4]) and abs(a[0]-headers['Lic.'])<5],key=lambda a:a[1])
 license_tokens += len(anchors)
 type_tokens += sum(b[4]=='Type' and abs(b[0]-headers['Bingo'])<5 for b in w)
 outside_license_tokens.extend(dict(page=pi+1,value=b[4],x=b[0],y=b[1]) for b in w if re.fullmatch(r'\d{4}-\d{2}',b[4]) and abs(b[0]-headers['Lic.'])>=5)
 for ai,a in enumerate(anchors):
  top=a[1]-1;bottom=anchors[ai+1][1]-1 if ai+1<len(anchors) else min([b[1]-1 for b in w if b[4]=='Printed:'] or [570])
  cols=[[] for _ in range(6)]
  for b in w:
   if not(top<=b[1]<bottom):continue
   ci=sum(b[0]>=cut for cut in bounds);cols[ci].append(b)
  def lines(items):
   groups=[]
   for b in sorted(items,key=lambda z:(round(z[1],1),z[0])):
    if not groups or abs(groups[-1][0]-b[1])>2:groups.append([b[1],[]])
    groups[-1][1].append(b)
   return [(y,' '.join(x[4] for x in sorted(g,key=lambda z:z[0]))) for y,g in groups]
  lc=[lines(c) for c in cols];z=lc[3];ct=z[1][1] if len(z)>1 else None;city_y=lc[2][-1][0] if len(lc[2])>1 else None
  street=' '.join(t for y,t in lc[2] if city_y is None or y<city_y-2);city=' '.join(t for y,t in lc[2] if city_y is not None and y>=city_y-2)
  types=[(y,t) for y,t in lc[4] if t.startswith('Type ')]
  auth=[]
  for ti,(y,t) in enumerate(types):
   end=types[ti+1][0]-1 if ti+1<len(types) else bottom
   typename=' '.join(t for ly,t in lc[4] if y-2<=ly<end)
   dl=[t for ly,t in lc[5] if y-2<=ly<end]
   wn=int(dl[-1]) if dl and dl[-1].isdigit() else None
   auth.append(dict(bingo_type=typename,authorized_days=' '.join(dl[:-1] if wn is not None else dl) or None,weeks_of_play=wn))
  row=dict(authorizations=auth,source_page=pi+1,organization_display=' '.join(t for y,t in lc[0]),organization_lines=[t for y,t in lc[0]],license_number=a[4],tax_status=' '.join(t for y,t in lc[1][1:]),street_address=street,city=city,zip=z[0][1] if z else None,county=ct)
  row['address_lines']=[t for y,t in lc[2]]
  row['zip_county_lines']=[t for y,t in z]
  row['county_normalized']=county_names.get((ct or '').casefold())
  row['source_row_on_page']=ai+1
  row['quality_flags']=[]
  if row['county_normalized'] is None: row['quality_flags'].append('unrecognized_county_in_source')
  if len(lc[2])>2: row['quality_flags'].append('multiline_address_in_source')
  if not re.fullmatch(r'\d{5}(-\d{4})?',row['zip'] or ''): row['quality_flags'].append('invalid_zip_in_source')
  if row['city'] in ('OH','Ohio'): row['quality_flags'].append('city_contains_state_in_source')
  if any(a['authorized_days'] is None for a in auth): row['quality_flags'].append('authorization_schedule_blank_in_source')
  rows.append(row)
# A separate page-level word count detects dropped or borrowed schedule text.
for pi,page in enumerate(doc):
 w=page.get_text('words')
 lic_x=next(a[0] for a in sorted(w,key=lambda z:z[1]) if a[4]=='Lic.' and a[1]<160)
 day_x=next(a[0] for a in sorted(w,key=lambda z:z[1]) if a[4]=='Days' and a[1]<160)
 page_rows=[r for r in rows if r['source_page']==pi+1]
 top=min(a[1] for a in w if re.fullmatch(r'\d{4}-\d{2}',a[4]) and abs(a[0]-lic_x)<5)-1
 bottom=min(a[1] for a in w if a[4]=='Printed:')-1
 expected=collections.Counter(a[4] for a in w if a[0]>=day_x-2 and top<=a[1]<bottom)
 actual=collections.Counter(t for r in page_rows for a in r['authorizations'] for t in ((a['authorized_days'] or '').split()+([str(a['weeks_of_play'])] if a['weeks_of_play'] is not None else [])))
 assert expected==actual, f'Schedule word reconciliation failed on page {pi+1}'
assert len(rows)==license_tokens
assert sum(len(r['authorizations']) for r in rows)==type_tokens, 'Unassigned bingo types'
assert not issues, issues
site_groups=collections.defaultdict(list)
for row in rows:
 site_groups[(row['license_number'],row['street_address'].casefold(),row['city'].casefold(),row['county'].casefold())].append(row)
for group in site_groups.values():
 if len(group)>1:
  for row in group: row['quality_flags'].append('repeated_site_in_source')
args.output.parent.mkdir(parents=True,exist_ok=True)
json.dump(dict(license_column_rows=license_tokens,bingo_type_entries=type_tokens,license_like_tokens_outside_license_column=outside_license_tokens,source_filename=src.split('/')[-1],source_sha256=hashlib.sha256(open(src,'rb').read()).hexdigest(),report_date='2026-10-02',report_year=2026,pages=len(doc),records=rows),args.output.open('w'),indent=2)

Path(bbox_path).unlink()
assert not issues, issues
print(f'Extracted {len(rows)} locations from {len(doc)} pages to {args.output}')
