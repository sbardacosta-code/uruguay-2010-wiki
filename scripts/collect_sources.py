from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urljoin
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from lxml import html
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ('S01','Group A Matches','en.wikipedia.org','2010 FIFA World Cup Group A'),
 ('S02','Knockout Stage Matches','en.wikipedia.org','2010 FIFA World Cup knockout stage'),
 ('S03','World Cup Squads','en.wikipedia.org','2010 FIFA World Cup squads'),
 ('S04','South American Qualification','en.wikipedia.org','2010 FIFA World Cup qualification (CONMEBOL)'),
 ('S05','Costa Rica Uruguay Playoff','en.wikipedia.org','2010 FIFA World Cup qualification (CONCACAF–CONMEBOL play-off)'),
 ('S06','World Cup Overview','en.wikipedia.org','2010 FIFA World Cup'),
 ('S07','World Cup Group Draw','en.wikinews.org','Final draw sets groups for FIFA World Cup 2010'),
]

def extract(data):
 tree=html.fromstring(data)
 nodes=tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," mw-parser-output ")]')
 if not nodes: raise ValueError('Article body not found')
 body=max(nodes,key=lambda e:len(e.text_content()))
 for e in list(body.xpath('.//script|.//style|.//noscript|.//comment()')):
  if e.getparent() is not None:e.getparent().remove(e)
 for cl in ['noprint','nomobile','mf-mobile-only','mw-editsection','navbox','metadata','ambox','reflist','sistersitebox']:
  for e in list(body.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," '+cl+' ")]')):
   if e.getparent() is not None:e.drop_tree()
 for e in body.xpath('.//img[@alt]'):
  alt=e.get('alt','')
  if any(x in alt.lower() for x in ['goal','card','substitution','captain','scored','penalty']):e.tail=' '+alt+' '+(e.tail or '')
 # Preserve table row relationships rather than scattering each cell on a line.
 for table in reversed(body.xpath('.//table')):
  rows=[]
  for tr in table.xpath('./tr|./thead/tr|./tbody/tr|./tfoot/tr'):
   cells=[' '.join(cell.text_content().split()) for cell in tr.xpath('./th|./td')]
   if cells:rows.append(' | '.join(cells))
  if rows and table.getparent() is not None:
   replacement=html.Element('pre');replacement.text='\n\n'+'\n'.join(rows)+'\n\n'
   replacement.tail=table.tail;table.getparent().replace(table,replacement)
 for e in body.xpath('.//br'):e.tail='\n'+(e.tail or '')
 for e in body.xpath('.//p|.//h1|.//h2|.//h3|.//h4|.//li|.//tr'):e.tail='\n\n'+(e.tail or '')
 for e in body.xpath('.//td|.//th'):e.tail=' | '+(e.tail or '')
 text='\n\n'.join(' '.join(x.split()).strip(' |') for x in body.text_content().splitlines() if x.strip(' \n\t|'))+'\n'
 return text

def collect(item):
 sid,name,domain,title=item
 url='https://'+domain+'/wiki/'+quote(title.replace(' ','_'),safe=':_-()')
 with urlopen(Request(url,headers={'User-Agent':'PersonalWikiResearch/1.0 (educational source collection)'}),timeout=40) as response:
  data=response.read();resolved=response.url
 tree=html.fromstring(data)
 text=extract(data)
 original=ROOT/'vault/raw/originals'/(name+'.html');original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(data)
 raw=ROOT/'vault/raw'/(name+'.txt');raw.write_text(text,encoding='utf-8')
 licenses=sorted(set('https:'+u if u.startswith('//') else u for u in tree.xpath('//a[contains(@href,"creativecommons.org/licenses/")]/@href|//link[contains(@rel,"license")]/@href')))
 permanent=tree.xpath('//*[@id="t-permalink"]/a/@href') or tree.xpath('//a[contains(@href,"oldid=")]/@href')
 publisher='Wikipedia' if 'wikipedia' in domain else 'Wikinews'
 entry=dict(id=sid,title=title,publisher=publisher,authors=publisher+' contributors',language='en',url=url,resolved_url=resolved,permanent_url=urljoin(resolved,permanent[0]) if permanent else url,history_url='https://'+domain+'/w/index.php?title='+quote(title.replace(' ','_'))+'&action=history',retrieved_at=datetime.now(timezone.utc).isoformat(),license_urls=licenses,original_html=str(original.relative_to(ROOT)),text_path=str(raw.relative_to(ROOT)),html_sha256=hashlib.sha256(data).hexdigest(),text_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),word_count=len(text.split()),transformation='Text extracted from the English article body. Navigation, reference-list markup and interface elements excluded; whitespace and tables normalized; relevant image alternative text retained. No translation, factual corrections or summarization. Downloaded HTML preserved byte for byte.')
 print(sid,entry['word_count'],'words',licenses,flush=True)
 return entry

if __name__=='__main__':
 result=[];failures=[]
 with ThreadPoolExecutor(max_workers=3) as pool:
  jobs=[(s,pool.submit(collect,s)) for s in SOURCES]
  for source,job in jobs:
   try:result.append(job.result())
   except Exception as exc:failures.append(dict(id=source[0],error=str(exc)));print('FAILED',source[0],exc,flush=True)
 (ROOT/'research/sources.json').write_text(json.dumps(dict(sources=result,failures=failures),ensure_ascii=False,indent=2)+'\n')
 if failures:raise SystemExit(1)
