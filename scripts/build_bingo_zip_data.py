"""Build compact ZIP centroids from the attributed free_zipcode_data CSV."""
import argparse,csv,json,hashlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('csv',type=Path);args=p.parse_args()
root=Path(__file__).resolve().parents[1];coords={}
for r in csv.DictReader(args.csv.open()):
 try: lat,lon=float(r['lat']),float(r['lon'])
 except ValueError: continue
 if len(r['code'])==5 and r['code'].isdigit() and -90<=lat<=90 and -180<=lon<=180 and (lat or lon):coords[r['code']]=[round(lat,5),round(lon,5)]
(root/'data/public/us-zip-centroids.json').write_text(json.dumps(coords,separators=(',',':'))+'\n')
meta=dict(source_url='https://github.com/midwire/free_zipcode_data/blob/develop/all_us_zipcodes.csv',source_sha256=hashlib.sha256(args.csv.read_bytes()).hexdigest(),source_commit=subprocess.check_output(['git','-C',str(args.csv.parent),'rev-parse','HEAD'],text=True).strip(),retrieved_on='2026-10-09',license='CC BY 3.0',original_provider='GeoNames; distributed by Midwire free_zipcode_data',coordinate_method='ZIP centroids, approximate straight-line miles, not driving distance',zip_count=len(coords))
(root/'data/public/us-zip-centroids-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print('ZIP coordinates:',len(coords))
