"""Create offline Xiaohongshu artifact; run from repo root. No npm build dependency."""
import json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/minitool-dist'
OUT.mkdir(parents=True,exist_ok=True)
html=(ROOT/'index.html').read_text()
html=re.sub(r'<script\b[^>]*>.*?</script>','',html,flags=re.S)
html=re.sub(r'\s+target=[\"\'][^\"\']*[\"\']','',html)
html=re.sub(r'(<meta[^>]*name="viewport"[^>]*content=")[^"]*',r'\g<1>width=device-width, initial-scale=1.0, viewport-fit=cover',html)

def colors(text):
 def rgba(m):
  h=m.group(1);return 'rgba(%d,%d,%d,%.4f)'%(int(h[:2],16),int(h[2:4],16),int(h[4:6],16),int(h[6:],16)/255)
 return re.sub(r'#([0-9a-fA-F]{8})(?![0-9a-fA-F])',rgba,text)

def css_fallbacks(css):
 # Insert physical inset properties and local scalar fallbacks before enhancements.
 def inset(m):
  vals=m.group(1).split();imp=''
  if '!important' in vals[-1]: vals[-1]=vals[-1].replace('!important','');imp='!important'
  if len(vals)==1: vals*=4
  elif len(vals)==2: vals*=2
  elif len(vals)==3: vals.append(vals[1])
  return ''.join(k+':'+v+imp+';' for k,v in zip(['top','right','bottom','left'],vals))+m.group(0)
 css=re.sub(r'(?<![a-z-])gap:([^;}]+)',lambda m:'grid-gap:'+m.group(1)+';'+m.group(0),css)
 css=re.sub(r'\binset:([^;}]+);?',inset,css)
 def scalar(m):
  prop,val=m.group(1),m.group(2)
  if not re.search(r'(?<![a-z-])(clamp|min|max)\(',val):return m.group(0)
  def replace(match):
   func=match.group(1);args=match.group(2).split(',');return args[1] if func=='clamp' else args[-1] if func=='min' else args[0]
  fallback=re.sub(r'\b(clamp|min|max)\(([^()]+)\)',replace,val)
  if fallback==val: # Nested max(calc(...),var(...)) used only for main min-height.
   if prop=='min-height':fallback='100vh!important'
   else:return m.group(0)
  return prop+':'+fallback+';'+prop+':'+val
 return colors(re.sub(r'([a-z-]+):([^;{}]+)',scalar,css))
html=re.sub(r'<style>(.*?)</style>',lambda m:'<style>'+css_fallbacks(m.group(1))+'</style>',html,flags=re.S)
# Flex gap fallback uses real layout measurement; Grid gap is supported in Chrome 61.
html=html.replace('</head>','<link rel="stylesheet" href="./compat.css"></head>')
html=html.replace('</body>','<script src="./data.js"></script><script src="./runtime.js"></script><script src="./app.js"></script></body>')
(OUT/'index.html').write_text(html)
data='window.FLOWMATE_CATALOGUE='+json.dumps(json.loads((ROOT/'data/opportunities.json').read_text()),ensure_ascii=False,separators=(',',':'))+';\nwindow.FLOWMATE_HEALTH='+json.dumps(json.loads((ROOT/'data/source-health.json').read_text()),ensure_ascii=False,separators=(',',':'))+';\n'
(OUT/'data.js').write_text(data)
(OUT/'runtime.js').write_text((ROOT/'minitool/runtime.js').read_text())
(OUT/'compat.css').write_text((ROOT/'minitool/compat.css').read_text())
# Boot only after asynchronous platform storage has been read.
(OUT/'app.js').write_text('window.FMReady.then(function(){\n'+colors((ROOT/'minitool/app.js').read_text())+'\n}).catch(function(error){var box=document.querySelector(".beta-notice");if(box)box.textContent="测试版加载失败，请重新打开小工具。";console.error(error);});\n')
package=ROOT/'artifacts/FlowMate-minitool-20261027.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(OUT.iterdir()):z.write(path,path.name)
print(json.dumps({'artifact':str(package),'zipBytes':package.stat().st_size,'files':{p.name:p.stat().st_size for p in OUT.iterdir()}},ensure_ascii=False,indent=2))
