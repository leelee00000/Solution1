"""Detect official notice changes without editing reviewed dates or eligibility."""
import argparse,concurrent.futures,hashlib,json,os,re,tempfile,unicodedata
from datetime import datetime,timedelta,timezone
from pathlib import Path
from check_sources import check
ROOT=Path(__file__).resolve().parents[1]
def monitor_text(text,region=None):
 if region:
  start=text.find(region['start']);end=text.find(region['end'],start+len(region['start']))
  if start<0 or end<0:raise ValueError('Reviewed content region is missing')
  text=text[start:end]
 return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',text).replace('\ufeff','')).strip()
def monitor_hash(text,region=None):return hashlib.sha256(monitor_text(text,region).encode()).hexdigest()
def assess(row,text=None,error=None):
 result={'id':row['id'],'url':row['source']['url'],'reviewedAt':row['source']['verifiedAt'],'reviewedBodyHash':row['source'].get('evidence',{}).get('bodySha256'),'referenceHash':row['source'].get('evidence',{}).get('monitorHash')}
 if error:return {**result,'status':'unreachable','message':'未能完成来源检查，保留历史核验资料','error':str(error)}
 source=row['source'];evidence=source.get('evidence',{})
 if source['verification']!='verified':return {**result,'status':'unreviewed','message':'已读取官网信息，但报名截止冲突尚未澄清' if source.get('lastAttemptResult')=='official-public-api-and-notice-deadline-conflict' else '已采集页面，但尚未完成正文人工核验'}
 try:digest=monitor_hash(text,evidence.get('monitorRegion'))
 except ValueError:return {**result,'status':'changed','message':'原核验正文区域已变化，需要重新核对公告'}
 reference=evidence.get('monitorHash')
 if not reference:return {**result,'status':'unreviewed','message':'缺少可比较的核验快照，需要人工确认'}
 if digest==reference:return {**result,'status':'unchanged','contentHash':digest,'message':'与已核验正文快照一致；不等于报名审核通过'}
 return {**result,'status':'changed','contentHash':digest,'message':'正文与已核验快照不同；原日期和资格暂不作为当前确认信息'}
def refresh_due(report,now=None,hours=24):
 now=now or datetime.now(timezone.utc)
 try:
  rows=report.get('results') or [{}]
  return any(not row.get('checkedAt',report.get('checkedAt')) or now-datetime.fromisoformat(row.get('checkedAt',report['checkedAt']))>=timedelta(hours=hours) for row in rows)
 except (KeyError,TypeError,ValueError):return True
def write_report(report,root=ROOT):
 target=root/'data/source-health.json';target.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',dir=target.parent,prefix='source-health-',suffix='.tmp',delete=False) as file:
  json.dump(report,file,ensure_ascii=False,indent=2);file.write('\n');name=file.name
 os.replace(name,target)
def refresh(root=ROOT,capture_fn=None,now=None,only_ids=None,limit=None):
 rows=json.loads((root/'data/opportunities.json').read_text())['opportunities'];now=now or datetime.now(timezone.utc)
 if only_ids and set(only_ids)-{row['id'] for row in rows}:raise ValueError('Unknown source IDs')
 if limit is not None and limit<1:raise ValueError('limit must be positive')
 selected=[row for row in rows if not only_ids or row['id'] in only_ids]
 try:previous=json.loads((root/'data/source-health.json').read_text())
 except (OSError,ValueError):previous={}
 existing={row['id']:row for row in previous.get('results',[])}
 if limit is not None:selected=sorted(selected,key=lambda row:(existing.get(row['id'],{}).get('checkedAt',previous.get('checkedAt')) or '',row['id']))[:limit]
 capture_fn=capture_fn or (lambda row:check(row,True))
 def one(row):
  try:
   captured=capture_fn(row)
   if 'error' in captured:return assess(row,error=captured['error'])
   text=(root/'artifacts/source-captures'/f'{row["id"]}.txt').read_text()
   return assess(row,text=text)
  except Exception as error:return assess(row,error=error)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:fresh=list(pool.map(one,selected))
 updates={row['id']:{**row,'checkedAt':now.isoformat()} for row in fresh};results=[]
 for row in rows:
  ident=row['id']
  if ident in updates:results.append(updates[ident]);continue
  prior=existing.get(ident);source=row['source'];evidence=source.get('evidence',{})
  if prior and prior.get('url')==source['url'] and prior.get('reviewedBodyHash')==evidence.get('bodySha256') and prior.get('referenceHash')==evidence.get('monitorHash'):results.append({**prior,'checkedAt':prior.get('checkedAt',previous.get('checkedAt'))})
  else:results.append({'id':ident,'url':source['url'],'reviewedAt':source['verifiedAt'],'reviewedBodyHash':evidence.get('bodySha256'),'referenceHash':evidence.get('monitorHash'),'status':'unreviewed','checkedAt':None,'message':'此次未检查该来源，需复核'})
 report={'schemaVersion':1,'checkedAt':now.isoformat(),'nextCheckAfter':(now+timedelta(hours=24)).isoformat(),'checkedCount':len(selected),'description':'自动检查仅比较官方正文快照；不自动修改日期、资格或人工核验结论。','results':results};write_report(report,root);return report
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--if-stale',action='store_true');parser.add_argument('--ids',nargs='+');parser.add_argument('--limit',type=int);args=parser.parse_args()
 try:existing=json.loads((ROOT/'data/source-health.json').read_text())
 except (OSError,ValueError):existing={}
 if args.if_stale and not refresh_due(existing):print('Source report is within the 24-hour check interval.');return
 report=refresh(only_ids=args.ids,limit=args.limit);print(json.dumps(report,ensure_ascii=False,indent=2))
 if any(r['status']=='unreachable' for r in report['results']):raise SystemExit(1)
if __name__=='__main__':main()
