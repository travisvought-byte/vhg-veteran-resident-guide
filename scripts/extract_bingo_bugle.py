"""Extract directory facts, including malformed rows; never auto-publish fuzzy matches."""
import argparse, hashlib, html, json, re
from pathlib import Path

def extract(source):
    cells=re.findall(r'<(?:td|th)\b([^>]*)>(.*?)</(?:td|th)>',source,re.S|re.I)
    clean=lambda value:re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',value))).strip()
    rows=[];i=0
    while i<len(cells)-8:
        if 'hall_address' in cells[i][0] and 'hall_address' in cells[i+1][0] and all('hall_address' not in x[0] for x in cells[i+2:i+9]):
            row=[clean(x[1]) for x in cells[i:i+9]]
            rows.append(dict(name=row[0],location=row[1],days=dict(zip(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],row[2:]))))
            i+=9
        else:i+=1
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--reviewed-on',required=True);a=p.parse_args()
    content=a.html.read_bytes();rows=extract(content.decode())
    result=dict(source_url='https://ohiobingobugle.com/game_directory.html',reviewed_on=a.reviewed_on,sha256=hashlib.sha256(content).hexdigest(),rows=rows)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(f'Extracted {len(rows)} rows. Review identity, expired dates and issue ads before publishing.')
