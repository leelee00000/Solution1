"""Preview or apply a JSON/JSONL catalogue batch. No automatic official verification."""
import argparse,copy,hashlib,json,os,tempfile,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from catalogue import ROOT,validate_catalogue

def read_batch(path=None,url=None):
 if url:
  if not url.startswith('https://'):raise ValueError('Remote catalogue endpoints must use HTTPS')
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'application/json, application/x-ndjson'}),timeout=30) as response:
   raw=response.read(32*1024*1024+1)
  if len(raw)>32*1024*1024:raise ValueError('Batch exceeds 32 MiB')
  text=raw.decode('utf-8-sig')
 else:text=Path(path).read_text(encoding='utf-8-sig')
 try:payload=json.loads(text)
 except json.JSONDecodeError:payload=[json.loads(line) for line in text.splitlines() if line.strip()]
 if isinstance(payload,dict):
  if payload.get('schemaVersion',1)!=1:raise ValueError('Unsupported schemaVersion')
  payload=[payload] if 'id' in payload and 'source' in payload else payload.get('opportunities')
 if not isinstance(payload,list) or any(not isinstance(row,dict) for row in payload):raise ValueError('Expected an opportunity array, envelope or JSONL records')
 return payload

def facts(row):
 result=copy.deepcopy(row);result.pop('a',None)
 source=result['source']
 for key in ['lastAttemptAt','lastAttemptResult']:source.pop(key,None)
 return result

def prepare(root,rows,mode='upsert',supplied_reviews=None,allow_identity_change=False):
 original=json.loads((root/'data/opportunities.json').read_text());reviews=json.loads((root/'data/source-reviews.json').read_text())
 supplied={r['id']:r for r in (supplied_reviews or {}).get('reviews',[])}
 if len(supplied)!=len((supplied_reviews or {}).get('reviews',[])):raise ValueError('Duplicate review ID')
 review_index={r['id']:r for r in reviews['reviews']};review_index.update(supplied);reviews['reviews']=list(review_index.values())
 incoming={};old={r['id']:r for r in original['opportunities']}
 for row in rows:
  ident=row.get('id')
  if not isinstance(ident,str):raise ValueError('Each record needs an explicit stable ID; IDs are never generated from list position')
  if ident in incoming:raise ValueError(f'Duplicate batch ID: {ident}')
  if ident in old and not allow_identity_change and any(row.get(k)!=old[ident].get(k) for k in ['name','field']):raise ValueError(f'{ident}: identity changed; use a new ID for a different edition/scope, or explicitly allow a reviewed name correction')
  if ident in old and row.get('source',{}).get('verification')=='verified' and facts(row)!=facts(old[ident]) and ident not in supplied:raise ValueError(f'{ident}: changed verified facts need an explicitly supplied manual review')
  incoming[ident]=copy.deepcopy(row)
 merged={} if mode=='replace' else dict(old);merged.update(incoming)
 candidate={**original,'opportunities':list(merged.values())};validate_catalogue(candidate,reviews)
 added=[i for i in merged if i not in old];updated=[i for i in merged if i in old and merged[i]!=old[i]];removed=[i for i in old if i not in merged]
 report={'mode':mode,'incoming':len(rows),'before':len(old),'after':len(merged),'added':added,'updated':updated,'removed':removed,'unchanged':len(merged)-len(added)-len(updated),'verification':'Schema/identity checks only; manual review is not inferred from HTTP success.'}
 health=json.loads((root/'data/source-health.json').read_text());existing={r['id']:r for r in health.get('results',[])};changed=set(added+updated)
 health['results']=[existing[i] if i in existing and i not in changed else {'id':i,'url':r['source']['url'],'reviewedAt':r['source']['verifiedAt'],'reviewedBodyHash':r['source'].get('evidence',{}).get('bodySha256'),'referenceHash':r['source'].get('evidence',{}).get('monitorHash'),'status':'unreviewed','message':'新导入或更新，尚未完成自动来源检查'} for i,r in merged.items()]
 # This is an import revision, not a fresh source-check timestamp.
 health['catalogueRevision']=hashlib.sha256(json.dumps(candidate,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 return report,{'data/opportunities.json':candidate,'data/source-reviews.json':reviews,'data/source-health.json':health}

def apply_files(root,files,report):
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');backup=root/'artifacts/import-backups'/stamp;backup.mkdir(parents=True)
 old={};temporary={}
 try:
  for name,value in files.items():
   target=root/name;old[name]=target.read_bytes() if target.exists() else None
   if old[name] is not None:(backup/Path(name).name).write_bytes(old[name])
   with tempfile.NamedTemporaryFile('w',dir=target.parent,prefix='.catalogue-',suffix='.tmp',delete=False,encoding='utf-8') as f:
    json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');temporary[name]=Path(f.name)
  (backup/'manifest.json').write_text(json.dumps({'state':'prepared','report':{**report,'applied':False}},ensure_ascii=False,indent=2)+'\n')
  for name,temp in temporary.items():os.replace(temp,root/name)
  (backup/'manifest.json').write_text(json.dumps({'state':'applied','report':{**report,'applied':True}},ensure_ascii=False,indent=2)+'\n')
 except Exception:
  for name,raw in old.items():
   if raw is not None:(root/name).write_bytes(raw)
   elif (root/name).exists():(root/name).unlink()
  raise
 finally:
  for temp in temporary.values():temp.unlink(missing_ok=True)
 return str(backup)

def main():
 parser=argparse.ArgumentParser(description=__doc__);source=parser.add_mutually_exclusive_group(required=True);source.add_argument('--input',type=Path);source.add_argument('--url');parser.add_argument('--mode',choices=['upsert','replace'],default='upsert');parser.add_argument('--reviews',type=Path);parser.add_argument('--allow-identity-change',action='store_true',help='Explicitly permit an audited name/scope correction; never recycle IDs for different contests');parser.add_argument('--apply',action='store_true');parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--report',type=Path);args=parser.parse_args()
 writing=False;applied=False
 try:
  rows=read_batch(args.input,args.url);review=json.loads(args.reviews.read_text()) if args.reviews else None
  report,files=prepare(args.root,rows,args.mode,review,args.allow_identity_change);report['applied']=args.apply
  if args.apply:
   writing=True;report['backup']=apply_files(args.root,files,report);applied=True
  if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(report,ensure_ascii=False,indent=2))
 except Exception as error:
  state='Import applied, but report output failed' if applied else 'Import write failed; inspect artifacts/import-backups if recovery is needed' if writing else 'Import rejected; catalogue unchanged'
  parser.exit(1,f'{state}: {error}\n')
if __name__=='__main__':main()
