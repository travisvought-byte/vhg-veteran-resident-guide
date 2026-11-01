#!/usr/bin/env python3
"""Build the disability action hub from dated sources and reusable topic records."""
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def outputs():
 data=json.loads((ROOT/'data/disability-advocacy.json').read_text())
 sources={s['id']:s for s in data['sources']}
 assert len(sources)==len(data['sources'])
 assert len({t['id'] for t in data['topics']})==len(data['topics'])
 cards=[]
 for t in data['topics']:
  assert set(t['asks'])=={'OH','US'} and all(s in sources for s in t['sources'])
  citations=''.join(f'<li><a href="{html.escape(sources[s]["url"],quote=True)}">{html.escape(sources[s]["title"])}</a> · {html.escape(sources[s]["kind"])} · checked {sources[s]["reviewed_on"]}</li>' for s in t['sources'])
  cards.append(f'<article id="{t["id"]}" class="topic"><p class="eyebrow">{html.escape(t["tag"])}</p><h3>{html.escape(t["title"])}</h3><p>{html.escape(t["summary"])}</p><details><summary>Policy requests and sources</summary><h4>Proposed Ohio request</h4><p>{html.escape(t["asks"]["OH"])}</p><h4>Proposed federal request</h4><p>{html.escape(t["asks"]["US"])}</p><ul>{citations}</ul></details><p><a href="{html.escape(t["help_url"],quote=True)}">{html.escape(t["help"])}</a></p><a class="button topic-action" href="#compose" data-topic="{t["id"]}">Write about this</a></article>')
 options=''.join(f'<option value="{t["id"]}">{html.escape(t["title"])}</option>' for t in data['topics'])
 default='Dear Ohio state lawmaker,\n\n'+data['topics'][0]['asks']['OH']+'\n\nPlease tell me what your office can do and how people with disabilities can take part.\n\nThank you.'
 page=(ROOT/'templates/disability-advocacy.html').read_text().replace('__CARDS__','\n'.join(cards)).replace('__OPTIONS__',options).replace('__DEFAULT__',html.escape(default)).replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c'))
 return {'disability-advocacy.html':page}
if __name__=='__main__':
 for path,text in outputs().items(): (ROOT/path).write_text(text)
 print('Built disability advocacy hub: five topics, Ohio and federal requests.')
