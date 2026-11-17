#!/usr/bin/env python3
import asyncio, json, hashlib, os
from pathlib import Path
from datetime import datetime,timezone
from playwright.async_api import async_playwright
URL = "https://interaction-works-lee.xiaogoubai2u.chatgpt.site/"
OUT = Path(__file__).parent / "output"
OUT.mkdir(parents=True,exist_ok=True)
async def inspect(page,label):
    errors=[]
    page.on("pageerror",lambda e: errors.append(str(e)))
    try:
        response=await page.goto(URL,wait_until="domcontentloaded",timeout=60000)
        await page.wait_for_timeout(6000)
        try: await page.wait_for_load_state("networkidle",timeout=6000)
        except Exception: pass
        await page.wait_for_timeout(900)
    except Exception as e:
        errors.append("navigation:"+str(e))
        response=None
    try:
        data=await page.evaluate("""() => ({
          text:(document.body?.innerText||'').slice(0,24000),
          title:document.title,
          links:Array.from(document.querySelectorAll('a')).slice(0,130).map(a=>({text:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,120),href:a.href})),
          buttons:Array.from(document.querySelectorAll('button,[role=button]')).slice(0,120).map((b,i)=>({i,text:(b.innerText||b.getAttribute('aria-label')||'').trim().slice(0,130),title:b.title,visible:!!b.getClientRects().length})),
          images:Array.from(document.querySelectorAll('img')).slice(0,90).map(a=>({alt:a.alt,src:a.currentSrc||a.src,loaded:a.complete&&a.naturalWidth>0,naturalWidth:a.naturalWidth,naturalHeight:a.naturalHeight})),
          iframe:Array.from(document.querySelectorAll('iframe')).map(a=>({title:a.title,src:a.src})),
          headings:Array.from(document.querySelectorAll('h1,h2,h3')).slice(0,65).map(x=>({tag:x.tagName,text:x.innerText.slice(0,160)})),
          docHeight:document.documentElement.scrollHeight,
          docWidth:document.documentElement.scrollWidth
        })""")
    except Exception as e:
        errors.append("evaluate:"+str(e)); data={}
    pic=OUT/(label+".png")
    try:
        png=await page.screenshot(path=str(pic),full_page=True,animations="disabled",timeout=25000)
        data["screenshot"]={"file":pic.name,"size":len(png),"sha256":hashlib.sha256(png).hexdigest()}
    except Exception as e: errors.append("screenshot:"+str(e))
    data.update({"label":label,"requested_url":URL,"actual_url":page.url,"http_status":response.status if response else None,"errors":errors})
    return data
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        results=[]
        for label,size in [("desktop",{"width":1440,"height":900}),("tablet",{"width":900,"height":1160}),("mobile",{"width":390,"height":844})]:
            page=await browser.new_page(viewport=size,device_scale_factor=1,locale="zh-CN",reduced_motion="reduce")
            results.append(await inspect(page,label))
            await page.close()
        await browser.close()
    result={"capturedAtUTC":datetime.now(timezone.utc).isoformat(),"pages":results}
    (OUT/"inspection.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    for x in results:
        print("VIEW",x["label"],"HTTP",x["http_status"],"TITLE",x.get("title"),"URL",x["actual_url"],flush=True)
        print("HEADINGS",[(h["tag"],h["text"]) for h in x.get("headings",[])][:25],flush=True)
        print("ERRORS",x["errors"],flush=True)
        print("TEXT",x.get("text","")[:3800].replace("\\n"," | "),flush=True)
if __name__=="__main__": asyncio.run(main())
