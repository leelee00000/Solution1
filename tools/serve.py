"""Local static development server with scheduled, read-only source checks."""
import argparse,json,threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from refresh_data import refresh,refresh_due
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  if self.path.split('?')[0].endswith('/data/source-health.json'):self.send_header('Cache-Control','no-store')
  super().end_headers()
def refresh_if_due():
 try:report=json.loads((ROOT/'data/source-health.json').read_text())
 except (OSError,ValueError):report={}
 if refresh_due(report):refresh()
def monitor(stop):
 while not stop.is_set():
  try:refresh_if_due()
  except Exception as error:print('Source check could not finish:',type(error).__name__,flush=True)
  stop.wait(60)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8000);parser.add_argument('--no-refresh',action='store_true');args=parser.parse_args()
 stop=threading.Event();server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
 if not args.no_refresh:threading.Thread(target=monitor,args=(stop,),daemon=True).start()
 print('FlowMate static server started; source checks are read-only and run when 24 hours old.',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:stop.set();server.server_close()
if __name__=='__main__':main()
