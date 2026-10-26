import json,copy,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from catalogue import validate_catalogue
class DesignTests(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((ROOT/'tests/fixtures/design-opportunities.json').read_text());self.reviews=json.loads((ROOT/'tests/fixtures/design-source-reviews.json').read_text());self.rows={r['id']:r for r in self.data['opportunities']}
 def test_verified_bachelor_and_level_claims_have_traceable_quotes(self):
  validate_catalogue(self.data,self.reviews)
  for i in range(17,22):
   row=self.rows[f'fm-{i:03}'];c=row['competition'];self.assertIn(c['levelBasis'],row['source']['evidence']['quotes']);self.assertIn(c['bachelorBasis'],row['source']['evidence']['quotes']);self.assertEqual(c['universityRecognition'],'unconfirmed')
 def test_presentation_scope_does_not_claim_tongji_credit_recognition(self):
  row=self.rows['fm-019'];self.assertEqual(row['eligibility']['schools'],[]);self.assertIn('不据此推断',row['note']);self.assertIn('同济',row['note'])
 def test_milan_month_is_not_promoted_to_a_fake_day(self):
  row=self.rows['fm-021'];self.assertIsNone(row['dates']['end']);self.assertIsNone(row['dates']['deadlineAt']);self.assertIn('2027年4月',row['note'])
 def test_special_tracks_keep_their_own_dates_and_conditional_author_counts(self):
  self.assertEqual(self.rows['fm-017']['dates']['end'],'2027-05-31');self.assertEqual(self.rows['fm-018']['dates']['end'],'2027-04-30');self.assertEqual(self.rows['fm-019']['dates']['end'],'2027-05-01');self.assertEqual(self.rows['fm-018']['eligibility']['teamSize']['max'],8);self.assertEqual(self.rows['fm-020']['eligibility']['teamSize'],{'min':1,'max':5})
 def test_pending_or_unquoted_level_claims_are_rejected(self):
  for field in ['levelBasis','bachelorBasis']:
   bad=copy.deepcopy(self.data);next(r for r in bad['opportunities'] if r['id']=='fm-017')['competition'][field]='Unsupported claim'
   with self.assertRaisesRegex(ValueError,'quoted evidence'):validate_catalogue(bad,self.reviews)
  bad=copy.deepcopy(self.data);r=next(r for r in bad['opportunities'] if r['id']=='fm-017');r['source']['verification']='pending'
  with self.assertRaisesRegex(ValueError,'quoted evidence'):validate_catalogue(bad,self.reviews)
if __name__=='__main__':unittest.main()
