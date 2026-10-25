import copy,json,sys,tempfile,unittest,os
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from import_catalogue import prepare,apply_files,read_batch
from catalogue import validate_catalogue
class ImportTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);(self.root/'data').mkdir()
  for name in ['opportunities.json','source-reviews.json','source-health.json']:(self.root/'data'/name).write_bytes((ROOT/'tests/fixtures'/name).read_bytes())
  self.base=json.loads((self.root/'data/opportunities.json').read_text());self.row=copy.deepcopy(self.base['opportunities'][7]);self.row.update(id='fm-10001',name='TEST ONLY fixture',field='TEST ONLY')
  self.row.pop('a',None);self.row['dates'].update(start=None,end=None,deadlineAt=None)
 def bytes(self):return {p.name:p.read_bytes() for p in (self.root/'data').glob('*.json')}
 def test_preview_has_no_side_effects_and_apply_creates_recoverable_backup(self):
  before=self.bytes();report,files=prepare(self.root,[self.row]);self.assertEqual(report['added'],['fm-10001']);self.assertEqual(self.bytes(),before)
  old_checked=files['data/source-health.json']['checkedAt'];backup=apply_files(self.root,files,report);self.assertTrue((Path(backup)/'opportunities.json').exists());self.assertEqual(json.loads((self.root/'data/opportunities.json').read_text())['opportunities'][-1]['id'],'fm-10001');health=json.loads((self.root/'data/source-health.json').read_text());self.assertEqual(health['checkedAt'],old_checked);self.assertEqual(health['results'][-1]['status'],'unreviewed')
 def test_write_failure_restores_all_previous_files(self):
  before=self.bytes();report,files=prepare(self.root,[self.row]);replace=os.replace;calls=0
  def fail_second(src,dst):
   nonlocal calls
   calls+=1
   if calls==2:raise OSError('simulated disk error')
   return replace(src,dst)
  with patch('import_catalogue.os.replace',side_effect=fail_second):
   with self.assertRaises(OSError):apply_files(self.root,files,report)
  self.assertEqual(self.bytes(),before)
 def test_upsert_is_idempotent_and_replace_is_explicit(self):
  r,f=prepare(self.root,[self.row]);apply_files(self.root,f,r);again,_=prepare(self.root,[self.row]);self.assertEqual(again['added'],[]);self.assertEqual(again['updated'],[])
  replaced,_=prepare(self.root,[self.row],mode='replace');self.assertEqual(replaced['after'],1);self.assertEqual(len(replaced['removed']),16)
 def test_duplicate_identity_and_invalid_batch_rejected_without_mutation(self):
  before=self.bytes()
  for batch in [[self.row,self.row],[self.row,{**self.row,'id':'fm-10002'}],[{**self.row,'id':'wrong'}]]:
   with self.assertRaises(Exception):prepare(self.root,batch)
   self.assertEqual(before,self.bytes())
 def test_recycled_ids_cannot_silently_rebind_favourites(self):
  row=copy.deepcopy(self.base['opportunities'][7]);row['name']='Entirely different competition'
  with self.assertRaisesRegex(ValueError,'identity changed'):prepare(self.root,[row])
 def test_fake_verified_rows_and_mutated_verified_facts_are_rejected(self):
  row=copy.deepcopy(self.row);row['source']=copy.deepcopy(self.base['opportunities'][5]['source']);row['eligibility']=copy.deepcopy(self.base['opportunities'][5]['eligibility'])
  with self.assertRaisesRegex(ValueError,'manual review'):prepare(self.root,[row])
  row=copy.deepcopy(self.base['opportunities'][5]);row['dates']['end']='2026-12-31'
  with self.assertRaisesRegex(ValueError,'manual review'):prepare(self.root,[row])
 def test_unknown_dates_stay_unknown_and_no_visual_angle_required(self):
  _,files=prepare(self.root,[self.row]);row=files['data/opportunities.json']['opportunities'][-1];self.assertIsNone(row['dates']['end']);self.assertNotIn('a',row)
 def test_date_and_team_rules_are_validated(self):
  row=copy.deepcopy(self.row);row['dates'].update(start='2026-12-31',end='2026-01-01')
  with self.assertRaisesRegex(ValueError,'start is after'):prepare(self.root,[row])
  row=copy.deepcopy(self.row);row['dates'].update(end='2026-12-31',deadlineAt='2026-12-31T10:00:00Z')
  with self.assertRaisesRegex(ValueError,'Beijing'):prepare(self.root,[row])
 def test_five_thousand_record_batch_is_valid_without_touching_live_data(self):
  rows=[]
  for i in range(5000):
   row=copy.deepcopy(self.row);row['id']='fm-'+str(10000+i);row['name']='TEST ONLY '+str(i);rows.append(row)
  before=self.bytes();report,files=prepare(self.root,rows)
  self.assertEqual(report['after'],5016);self.assertEqual(len(report['added']),5000);self.assertEqual(len(files['data/source-health.json']['results']),5016);self.assertEqual(before,self.bytes())
 def test_json_envelope_and_jsonl_adapters(self):
  for text in [json.dumps(self.row)+'\n',json.dumps([self.row]),json.dumps({'schemaVersion':1,'opportunities':[self.row]}),json.dumps(self.row)+'\n'+json.dumps({**self.row,'id':'fm-10002'})+'\n']:
   p=self.root/'batch.json';p.write_text(text);self.assertEqual(read_batch(p)[0]['id'],self.row['id'])
 def test_schema_checks_duplicate_stable_ids_even_when_rows_differ(self):
  data=copy.deepcopy(self.base);data['opportunities'].append({**data['opportunities'][0],'note':'different'})
  with self.assertRaisesRegex(ValueError,'Duplicate stable ID'):validate_catalogue(data)
if __name__=='__main__':unittest.main()
