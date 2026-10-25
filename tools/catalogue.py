"""Shared catalogue contract: stable identities, explicit evidence and exact dates."""
import json,unicodedata,re
from datetime import datetime,timedelta
from pathlib import Path
from urllib.parse import urlparse
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]

def business_key(row):
 def norm(value):return re.sub(r'\s+','',unicodedata.normalize('NFKC',value)).casefold()
 return (norm(row['name']),norm(row['field']),row['cat'],row['direction'],tuple(sorted(norm(s) for s in row['eligibility']['schools'])),row['dates']['end'])

def validate_catalogue(data,reviews=None):
 schema=json.loads((ROOT/'data/opportunity.schema.json').read_text())
 Draft202012Validator(schema,format_checker=FormatChecker()).validate(data)
 ids=set();keys={};registry={r['id']:r for r in (reviews or {}).get('reviews',[])}
 for row in data['opportunities']:
  ident=row['id']
  if ident in ids:raise ValueError(f'Duplicate stable ID: {ident}')
  ids.add(ident);key=business_key(row)
  if key in keys:raise ValueError(f'Duplicate opportunity/scope/deadline: {keys[key]} and {ident}')
  keys[key]=ident;dates=row['dates'];source=row['source'];rules=row['eligibility']
  if not urlparse(source['url']).hostname:raise ValueError(f'{ident}: source URL has no hostname')
  if dates['start'] and dates['end'] and dates['start']>dates['end']:raise ValueError(f'{ident}: start is after deadline')
  if dates.get('deadlineAt'):
   exact=datetime.fromisoformat(dates['deadlineAt'])
   if dates['deadlineAt'][:10]!=dates['end'] or exact.utcoffset()!=timedelta(hours=8):raise ValueError(f'{ident}: exact deadline must match the Beijing calendar date')
  team=rules['teamSize']
  if team and team['min'] is not None and team['max'] is not None and team['min']>team['max']:raise ValueError(f'{ident}: team minimum exceeds maximum')
  req=rules['requirements']
  if len({r['id'] for r in req})!=len(req) or any(not r['quote'].strip() or not r['label'].strip() for r in req):raise ValueError(f'{ident}: duplicate or empty eligibility requirements')
  if rules['rulesComplete'] and source['verification']!='verified':raise ValueError(f'{ident}: pending source cannot have complete verified rules')
  if source['verification']=='verified' and reviews is not None:
   review=registry.get(ident);evidence=source.get('evidence',{})
   if not review or any([review.get('url')!=source['url'],review.get('reviewedAt')!=source['verifiedAt'],review.get('bodySha256')!=evidence.get('bodySha256'),review.get('quotes')!=evidence.get('quotes')]):raise ValueError(f'{ident}: missing or mismatched manual review evidence')
 return data
