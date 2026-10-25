"""Embed the canonical JSON catalogue without breaking file:// offline usage."""
import argparse,json,re
from catalogue import validate_catalogue
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
data=json.loads((ROOT/'data/opportunities.json').read_text())
validate_catalogue(data,json.loads((ROOT/'data/source-reviews.json').read_text()))
ids={item['id'] for item in data['opportunities']}
html=(ROOT/'index.html').read_text()
embedded=json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')
result=re.sub(r'(<script id="opportunity-data" type="application/json">).*?(</script>)',lambda m:m[1]+embedded+m[2],html,count=1,flags=re.S)
catalogue_result=result
health_file=ROOT/'data/source-health.json'
health=json.loads(health_file.read_text()) if health_file.exists() else {'schemaVersion':1,'checkedAt':None,'results':[]}
health_embedded=json.dumps(health,ensure_ascii=False,indent=2).replace('<','\\u003c')
result=re.sub(r'(<script id="source-health-data" type="application/json">).*?(</script>)',lambda m:m[1]+health_embedded+m[2],result,count=1,flags=re.S)
if args.check:
 if catalogue_result!=html:raise SystemExit('index.html has stale embedded catalogue; run python tools/build.py')
 print(f'Embedded catalogue matches canonical JSON ({len(ids)} records).')
else:
 (ROOT/'index.html').write_text(result)
 print(f'Embedded {len(ids)} records; file:// remains supported.')
