"""Validate the source contract; no public opportunity or date is fabricated here."""
import json,unittest,subprocess,copy
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
ROOT=Path(__file__).resolve().parents[1]
class DataContract(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((ROOT/'tests/fixtures/opportunities.json').read_text());self.schema=json.loads((ROOT/'data/opportunity.schema.json').read_text())
 def test_current_production_catalogue_is_valid_independently_of_fixture(self):
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  from catalogue import validate_catalogue
  validate_catalogue(json.loads((ROOT/'data/opportunities.json').read_text()),json.loads((ROOT/'data/source-reviews.json').read_text()))
 def test_catalogue_schema(self):
  Draft202012Validator.check_schema(self.schema)
  Draft202012Validator(self.schema,format_checker=FormatChecker()).validate(self.data)
 def test_verified_records_have_reviewed_evidence(self):
  reviews={r['id']:r for r in json.loads((ROOT/'tests/fixtures/source-reviews.json').read_text())['reviews']}
  verified=[i for i in self.data['opportunities'] if i['source']['verification']=='verified']
  self.assertEqual(len(verified),15)
  for it in verified:
   self.assertEqual(it['source']['evidence']['quotes'],reviews[it['id']]['quotes'])
   self.assertEqual(it['source']['evidence']['bodySha256'],reviews[it['id']]['bodySha256'])
   self.assertEqual(it['source']['verifiedAt'],reviews[it['id']]['reviewedAt'])
  pending=[i for i in self.data['opportunities'] if i['source']['verification']=='pending']
  self.assertEqual([i['id'] for i in pending],['fm-008'])
 def test_school_restrictions_not_lost(self):
  items={i['id']:i for i in self.data['opportunities']}
  self.assertEqual(items['fm-006']['eligibility']['schools'],['同济大学'])
  self.assertEqual(items['fm-006']['eligibility']['enrollmentYears'],[2025,2026])
  self.assertEqual(items['fm-003']['eligibility']['schools'],['重庆交通大学'])
 def test_unknown_dates_are_still_unknown(self):
  self.assertTrue(all(i['dates']['award'] is None for i in self.data['opportunities']))
  self.assertIsNone(next(i for i in self.data['opportunities'] if i['id']=='fm-009')['dates']['start'])
 def test_stage_deadlines_and_conditional_constraints(self):
  items={i['id']:i for i in self.data['opportunities']}
  self.assertEqual(items['fm-003']['dates']['end'],'2026-11-20')
  self.assertEqual(items['fm-003']['eligibility']['studyYears'],[])
  self.assertEqual(items['fm-003']['eligibility']['leaderStudyYears'],[2,3])
  self.assertEqual(items['fm-004']['dates']['end'],'2026-11-08')
  self.assertEqual(items['fm-005']['dates']['end'],'2026-05-15')
  self.assertEqual(items['fm-013']['eligibility']['schools'],['长沙理工大学'])
  self.assertIsNone(items['fm-008']['dates']['end'])
  self.assertEqual(items['fm-008']['source']['verification'],'pending')
 def test_new_tracks_preserve_scope_and_team_constraints(self):
  items={i['id']:i for i in self.data['opportunities']}
  model=items['fm-015'];agri=items['fm-016']
  self.assertEqual(model['eligibility']['teamSize'],{'min':1,'max':3})
  self.assertEqual(model['dates']['deadlineAt'],'2027-04-26T14:00:00+08:00')
  self.assertEqual(agri['eligibility']['schools'],['西安交通大学'])
  self.assertEqual(agri['dates']['end'],'2026-10-30')
  self.assertEqual(agri['eligibility']['teamSize'],{'min':2,'max':5})
  self.assertIn('11月30日',agri['note'])
  self.assertEqual(agri['eligibility']['studyModes'],[])
 def test_verification_without_evidence_is_rejected(self):
  invalid=copy.deepcopy(self.data)
  del invalid['opportunities'][0]['source']['evidence']
  with self.assertRaises(ValidationError):Draft202012Validator(self.schema).validate(invalid)
 def test_deadline_times_match_calendar_date(self):
  for it in self.data['opportunities']:
   if it['dates']['deadlineAt']:self.assertEqual(it['dates']['deadlineAt'][:10],it['dates']['end'])
 def test_self_check_rules_have_unique_keys_and_explicit_conditions(self):
  for it in self.data['opportunities']:
   rules=it['eligibility']['requirements']
   self.assertEqual(len({r['id'] for r in rules}),len(rules))
   self.assertTrue(all(r['quote'].strip() and r['label'].strip() for r in rules))
   if it['eligibility']['rulesComplete']:self.assertEqual(it['source']['verification'],'verified')
  items={it['id']:it for it in self.data['opportunities']}
  self.assertEqual(next(r for r in items['fm-003']['eligibility']['requirements'] if r['id']=='leader-clear')['whenRole'],'负责人')
  self.assertTrue(items['fm-009']['eligibility']['requirements'])
 def test_offline_bundle_matches_canonical_data(self):
  subprocess.run(['python',str(ROOT/'tools/build.py'),'--check'],check=True)
if __name__=='__main__':unittest.main()
