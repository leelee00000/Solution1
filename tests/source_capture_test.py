import json,sys,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from check_sources import check
class CaptureTests(unittest.TestCase):
 def test_public_cms_capture_uses_article_not_dynamic_metadata(self):
  with tempfile.TemporaryDirectory() as directory:
   row={'id':'fm-900','source':{'url':'https://example.org/','evidence':{'documentUrl':'https://example.org/api/cms?id=1'}}}
   payload={'status':1,'info':{'rs':{'title':'Official rules','content':'<p>本科可参与</p><p>省赛及国赛</p>','hits':987654,'user_id':777}}}
   def fetch(url,referer=None):return ((json.dumps(payload).encode() if 'api/' in url else b'<title>Home</title>'),url,200,'utf-8')
   with patch('check_sources.ROOT',Path(directory)),patch('check_sources.fetch',side_effect=fetch):result=check(row,True)
   body=(Path(directory)/'artifacts/source-captures/fm-900.txt').read_text();self.assertEqual(body,'Official rules\n本科可参与\n省赛及国赛');self.assertEqual(result['bodySha256'],hashlib.sha256(body.encode()).hexdigest());self.assertEqual(result['verification'],'manual-content-review-required');self.assertNotIn('987654',body)
 def test_unknown_json_is_not_treated_as_a_verified_empty_document(self):
  with tempfile.TemporaryDirectory() as directory:
   row={'id':'fm-901','source':{'url':'https://example.org/notice'}}
   with patch('check_sources.ROOT',Path(directory)),patch('check_sources.fetch',return_value=(b'{"status":0,"error":"not available"}','https://example.org/notice',200,'utf-8')):result=check(row,True)
   self.assertIn('error',result);self.assertEqual(result['verification'],'pending')
if __name__=='__main__':unittest.main()
