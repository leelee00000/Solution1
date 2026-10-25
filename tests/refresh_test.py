import copy,hashlib,json,sys,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from refresh_data import monitor_hash,assess,refresh_due,refresh
class RefreshTests(unittest.TestCase):
 def setUp(self):
  self.body='Official notice\nApply by 2026-11-20\nEligible full-time students'
  self.row={'id':'fm-001','source':{'url':'https://example.edu/notice','verification':'verified','verifiedAt':'2026-10-25','evidence':{'monitorHash':monitor_hash(self.body)}}}
 def test_normalized_whitespace_unchanged(self):self.assertEqual(assess(self.row,'Official notice  Apply by 2026-11-20\n Eligible full-time students')['status'],'unchanged')
 def test_changed_deadline_requires_review(self):self.assertEqual(assess(self.row,self.body.replace('11-20','11-25'))['status'],'changed')
 def test_failure_preserves_reviewed_information(self):
  before=copy.deepcopy(self.row);self.assertEqual(assess(self.row,error='403 Forbidden')['status'],'unreachable');self.assertEqual(self.row,before)
 def test_http_success_cannot_certify_pending(self):
  self.row['source']['verification']='pending';self.assertEqual(assess(self.row,self.body)['status'],'unreviewed')
 def test_known_footer_is_not_part_of_review_region(self):
  self.row['source']['evidence']={'monitorHash':monitor_hash('HEAD facts END visits:1',{'start':'HEAD','end':'END'}),'monitorRegion':{'start':'HEAD','end':'END'}}
  self.assertEqual(assess(self.row,'HEAD facts END visits:2')['status'],'unchanged');self.assertEqual(assess(self.row,'HEAD revised END visits:2')['status'],'changed')
 def test_missing_region_requires_review(self):
  self.row['source']['evidence']['monitorRegion']={'start':'Missing','end':'END'};self.assertEqual(assess(self.row,self.body)['status'],'changed')
 def test_scheduler_checks_expired_reports(self):
  now=datetime(2026,10,25,tzinfo=timezone.utc);self.assertFalse(refresh_due({'checkedAt':(now-timedelta(hours=23)).isoformat()},now));self.assertTrue(refresh_due({'checkedAt':(now-timedelta(hours=25)).isoformat()},now));self.assertTrue(refresh_due({},now))
 def test_refresh_writes_atomic_report_without_touching_catalogue(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'data').mkdir();(root/'artifacts/source-captures').mkdir(parents=True)
   catalogue=json.dumps({'opportunities':[self.row]});(root/'data/opportunities.json').write_text(catalogue);(root/'artifacts/source-captures/fm-001.txt').write_text(self.body)
   report=refresh(root,capture_fn=lambda row:{'http':200},now=datetime(2026,10,25,tzinfo=timezone.utc));self.assertEqual(report['results'][0]['status'],'unchanged');self.assertEqual((root/'data/opportunities.json').read_text(),catalogue);self.assertEqual(json.loads((root/'data/source-health.json').read_text()),report)
 def test_partial_refresh_never_renews_unchecked_sources(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'data').mkdir();(root/'artifacts/source-captures').mkdir(parents=True)
   second=copy.deepcopy(self.row);second['id']='fm-002';rows=[self.row,second]
   (root/'data/opportunities.json').write_text(json.dumps({'opportunities':rows}))
   for row in rows:(root/'artifacts/source-captures'/f"{row['id']}.txt").write_text(self.body)
   earlier=datetime(2026,10,20,tzinfo=timezone.utc);later=datetime(2026,10,26,tzinfo=timezone.utc)
   refresh(root,capture_fn=lambda row:{'http':200},now=earlier)
   report=refresh(root,capture_fn=lambda row:{'http':200},now=later,only_ids=['fm-001'])
   self.assertEqual(report['checkedCount'],1);entries={r['id']:r for r in report['results']}
   self.assertEqual(entries['fm-001']['checkedAt'],later.isoformat());self.assertEqual(entries['fm-002']['checkedAt'],earlier.isoformat());self.assertTrue(refresh_due(report,later))
 def test_limited_checks_choose_oldest_records_next(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'data').mkdir();(root/'artifacts/source-captures').mkdir(parents=True)
   second=copy.deepcopy(self.row);second['id']='fm-002';rows=[self.row,second]
   (root/'data/opportunities.json').write_text(json.dumps({'opportunities':rows}))
   for row in rows:(root/'artifacts/source-captures'/f"{row['id']}.txt").write_text(self.body)
   seen=[]
   def capture(row):seen.append(row['id']);return {'http':200}
   refresh(root,capture_fn=capture,now=datetime(2026,10,25,tzinfo=timezone.utc),limit=1)
   refresh(root,capture_fn=capture,now=datetime(2026,10,26,tzinfo=timezone.utc),limit=1)
   self.assertEqual(seen,['fm-001','fm-002'])
if __name__=='__main__':unittest.main()
