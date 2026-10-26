"""Read-only official source capture. Connectivity and hashes never certify content."""
import argparse,concurrent.futures,hashlib,json,re,subprocess,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.chunks=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.skip+=1
  if tag in ('p','div','br','li','tr','h1','h2','h3'):self.chunks.append('\n')
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,text):
  if not self.skip:self.chunks.append(text)
def fetch(url,referer=None):
 headers={'User-Agent':'FlowMate-source-check/0.1'}
 if referer:headers['Referer']=referer
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=20) as response:
  raw=response.read(5000000)
  return raw,response.url,response.status,response.headers.get_content_charset() or 'utf-8'
def check(row,capture):
 url=row['source']['url']
 try:
  parts=urlsplit(url);raw,final,status,charset=fetch(url,referer=parts.scheme+'://'+parts.netloc+'/')
  html=raw.decode(charset,errors='replace');title=re.search(r'<title[^>]*>(.*?)</title>',html,re.S|re.I)
  result={'id':row['id'],'url':url,'http':status,'finalUrl':final,'title':re.sub(r'\s+',' ',title[1]).strip() if title else None,'verification':'manual-content-review-required'}
  if capture:
   target=ROOT/'artifacts/source-captures';target.mkdir(parents=True,exist_ok=True)
   document=row['source'].get('evidence',{}).get('documentUrl',url)
   if document!=url:raw,final,status,charset=fetch(document,referer=url)
   if document.lower().endswith('.pdf'):
    file=target/(row['id']+'.pdf');file.write_bytes(raw);textfile=target/(row['id']+'.txt')
    subprocess.run(['pdftotext','-layout',str(file),str(textfile)],check=True,capture_output=True);text=textfile.read_text()
   else:
    file=target/(row['id']+'.html');file.write_bytes(raw);decoded=raw.decode(charset,errors='replace');parser=Text()
    if decoded.lstrip().startswith('{'):
     payload=json.loads(decoded)
     if payload.get('status')==1 and isinstance(payload.get('info',{}).get('rs'),dict):
      article=payload['info']['rs'];parser.feed(article.get('content',''));body='\n'.join(x.strip() for x in ''.join(parser.chunks).splitlines() if x.strip());text=article.get('title','')+'\n'+body
     elif isinstance(payload.get('data'),dict) and 'competitionInfo' in payload['data']:
      payload=payload['data'];parser.feed(payload.get('competitionInfo',''));body='\n'.join(x.strip() for x in ''.join(parser.chunks).splitlines() if x.strip());text='\n'.join([payload.get('competitionName',''),'API报名开始：'+str(payload.get('signStartDt','')),'API报名截止：'+str(payload.get('signEndDt','')),body])
     else:raise ValueError('Unsupported public JSON notice format')
    else:
     parser.feed(decoded);text='\n'.join(x.strip() for x in ''.join(parser.chunks).splitlines() if x.strip())
    (target/(row['id']+'.txt')).write_text(text)
   result.update(documentUrl=document,capturedFile=str(file.relative_to(ROOT)),rawSha256=hashlib.sha256(raw).hexdigest(),bodySha256=hashlib.sha256(text.encode()).hexdigest())
  return result
 except Exception as error:return {'id':row['id'],'url':url,'error':str(error),'verification':'pending'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--capture',action='store_true',help='Retain public official HTML/PDF and extracted text for manual review; requires pdftotext for PDF.');args=parser.parse_args()
 rows=json.loads((ROOT/'data/opportunities.json').read_text())['opportunities']
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(lambda row:check(row,args.capture),rows))
 output={'attemptedAt':datetime.now(timezone.utc).isoformat(),'description':'Read-only: read official notice content before changing source.verification. HTTP 200 is not verification.','results':results}
 (ROOT/'artifacts').mkdir(exist_ok=True);(ROOT/'artifacts/source-reachability.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');print(json.dumps(output,ensure_ascii=False,indent=2))
 if any('error' in r for r in results):raise SystemExit(1)
if __name__=='__main__':main()
