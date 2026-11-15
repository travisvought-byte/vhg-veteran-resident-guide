#!/usr/bin/env python3
"""Validate a researched JSON batch and merge by ID; refuses conflicting records by default."""
import argparse,json
from pathlib import Path
from bingo_network import validate
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('batch',type=Path)
p.add_argument('--replace',action='store_true',help='Explicitly replace conflicting existing IDs')
p.add_argument('--write',action='store_true',help='Write canonical JSON; otherwise preview only')
a=p.parse_args()
file=ROOT/'data/bingo/venues.json'
old=json.loads(file.read_text());batch=json.loads(a.batch.read_text())
states=json.loads((ROOT/'data/bingo/states.json').read_text())
validate(states,batch)
merged={r['id']:r for r in old}
for r in batch:
 if r['id'] in merged and r!=merged[r['id']] and not a.replace:
  raise SystemExit('Conflicting ID: '+r['id']+'. Review and use --replace if intentional.')
 merged[r['id']]=r
result=sorted(merged.values(),key=lambda r:(r['state'],r['id']))
validate(states,result)
print(f'{len(old)} existing; {len(batch)} batch; {len(result)} after merge')
if a.write:
 temp=file.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');temp.replace(file)
 print('Saved. Run python3 scripts/build_public.py and node tests/bingo-network.cjs.')
else: print('Preview only. Add --write to save.')
