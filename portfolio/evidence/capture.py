#!/usr/bin/env python3
"""Capture real FlowMate states and validate every screenshot against concrete UI evidence.

Run: python portfolio/evidence/capture.py
Artifacts: portfolio/evidence/output/{*.png,manifest.json,report.html}
No fabricated mockups, no changes to production pages, no third-party credentials.
"""
from __future__ import annotations

import asyncio
import hashlib
import html
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

SITE = os.getenv("FLOWMATE_CAPTURE_URL", "https://leelee00000.github.io/Solution1/")
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = "https://github.com/leelee00000/Solution1"
CLAIMS = {
    "01_galaxy": {
        "caption": "探索视图把带有日期的机会放在星系中，时间尺可调整范围，右侧显示所选机会的真实详情。行星尺寸不代表竞赛评级。",
        "must_show": ["#orbit", "#title", "#zoomValue", "#planetLegend"],
        "code_note": "Canvas绘制；星球按日期定位，不以大小评选机会价值。",
    },
    "02_library": {
        "caption": "机会库支持按名称搜索，显示对应的机会条目及查看详情入口。",
        "must_show": ["#panelTitle", "#libraryResults article.panel-row"],
        "code_note": "输入框筛选本地静态机会资料；不是实时联网搜索。",
    },
    "03_eligibility": {
        "caption": "资格路径将公开条件、个人匹配的待确认项和来源核实入口并列呈现；它不等于官方审核通过。",
        "must_show": ["#panelTitle", "#panelContent h3", "#panelContent .path-facts"],
        "code_note": "三态初筛并保留不确定性；来源检查过期可能使状态保持待核。",
    },
    "04_simulator": {
        "caption": "用户在可能性预演中调整成长目标、顾虑和投入时长，得到假设性行动规划；这不是LLM预测。",
        "must_show": ["#futureTitle", "[data-goal='能力']", "[data-risk='能力不足']", "#hoursValue", "#weeksValue"],
        "code_note": "模板化路径与用户输入的确定性运算，不调用语言模型。",
    },
}
records: list[dict] = []
checks: list[dict] = []
errors: list[str] = []


def require(condition: bool, detail: str) -> None:
    checks.append({"pass": bool(condition), "test": detail})
    if not condition:
        raise AssertionError(detail)


async def visible_geometry(page, selector: str) -> dict:
    element = page.locator(selector).first
    count = await element.count()
    require(count > 0, f"element exists: {selector}")
    box = await element.bounding_box()
    require(box is not None and box["width"] > 1 and box["height"] > 1,
            f"element is rendered: {selector}")
    viewport = page.viewport_size
    overlap_x = max(0, min(box["x"] + box["width"], viewport["width"]) - max(box["x"], 0))
    overlap_y = max(0, min(box["y"] + box["height"], viewport["height"]) - max(box["y"], 0))
    ratio = overlap_x * overlap_y / (box["width"] * box["height"])
    require(ratio > 0.36, f"element is substantially inside actual screenshot: {selector} ({ratio:.2f})")
    return {"selector": selector, "bounding_box": {k: round(v, 1) for k, v in box.items()}, "visible_ratio": round(ratio, 3)}


async def capture(page, ident: str, facts: dict) -> None:
    item = CLAIMS[ident]
    geometry = [await visible_geometry(page, sel) for sel in item["must_show"]]
    path = OUT / f"{ident}.png"
    png = await page.screenshot(path=str(path), full_page=False, animations="disabled")
    require(png.startswith(b"\x89PNG\r\n\x1a\n"), f"PNG signature: {ident}")
    width, height = struct.unpack(">II", png[16:24])
    require(width >= 1200 and height >= 700, f"real screenshot pixel dimensions: {ident} {width}x{height}")
    require(len(png) > 40_000, f"nontrivial screenshot byte count: {ident} {len(png)}")
    record = {
        "claim_id": ident,
        "image": path.name,
        "caption": item["caption"],
        "code_note": item["code_note"],
        "actual_ui_state": facts,
        "visible_dom_evidence": geometry,
        "browser_url": page.url,
        "width": width,
        "height": height,
        "file_bytes": len(png),
        "sha256": hashlib.sha256(png).hexdigest(),
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    records.append(record)
    print(f"PASS {ident}: {facts}", flush=True)


def create_report(manifest: dict) -> None:
    content = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8">',
               '<meta name="viewport" content="width=device-width,initial-scale=1">',
               '<title>FlowMate · 实际界面图文取证</title>',
               '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1120px;margin:32px auto;padding:0 20px;color:#20283c;background:#faf9f5}article{padding:24px;background:white;border:1px solid #dcdfe3;border-radius:14px;margin:26px 0}img{width:100%;height:auto;border:1px solid #ececef}code{overflow-wrap:anywhere}small{color:#64748b}strong{color:#0c6753}</style>',
               '<h1>FlowMate · 真实运行截图与文案匹配报告</h1>',
               '<p>仅对实际运行页面的DOM文本、用户操作状态、截图可见区域及文件完整性做程序化核验。不能替代人工视觉判断、用户测试或实时赛事信息核实。</p>',
               f'<p><strong>结果：{html.escape(manifest["status"])}</strong> · 截图 {len(manifest["screenshots"])} 张 · 检查 {len(manifest["checks"])} 项</p>']
    for r in manifest["screenshots"]:
        content.append(f'<article><h2>{html.escape(r["claim_id"])} · {html.escape(r["caption"])}</h2><img src="{html.escape(r["image"])}" alt="实际浏览器截图"><p><small>真实页面证据：{html.escape(json.dumps(r["actual_ui_state"],ensure_ascii=False))}</small></p><p><small>代码层边界：{html.escape(r["code_note"])}</small></p></article>')
    content.append('</html>')
    (OUT / "report.html").write_text("\n".join(content), encoding="utf-8")


async def main() -> None:
    manifest = {
        "status": "INCOMPLETE",
        "site": SITE,
        "source_repo": SOURCE,
        "method": "Playwright Chromium real UI interactions + DOM state + viewport geometry + PNG file integrity",
        "scope_limit": "DOM与截图状态匹配不等于视觉语义100%正确；原站的报名时效、主办方审核及AI模型能力不在此证明范围",
        "screenshots": records,
        "checks": checks,
        "errors": errors,
    }
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(viewport={"width": 1500, "height": 1000},
                                              device_scale_factor=1, locale="zh-CN",
                                              reduced_motion="reduce", color_scheme="light")
                page.on("pageerror", lambda e: errors.append(str(e)))
                response = await page.goto(SITE, wait_until="domcontentloaded", timeout=60_000)
                require(response is not None and response.status == 200, f"site HTTP200: {SITE}")
                await page.locator("#orbit").wait_for(state="visible")
                await page.locator("#title").wait_for(state="visible")
                await page.wait_for_timeout(900)
                require(await page.title() == "FlowMate · Find your next orbit", "actual source page title")
                require((await page.locator("#orbit").bounding_box())["height"] > 100, "canvas has positive display height")
                # Do not trust a canvas element alone; verify some pixels are actually drawn.
                stats = await page.locator("#orbit").evaluate("""c => {
                    let ctx=c.getContext('2d'), w=c.width,h=c.height;
                    if(!ctx || w<50 || h<50) return {colors:0,w,h};
                    let d=ctx.getImageData(0,0,w,h).data, seen=new Set();
                    for(let y=2;y<h;y+=Math.max(1,Math.floor(h/28)))
                      for(let x=2;x<w;x+=Math.max(1,Math.floor(w/28))){
                        let i=(y*w+x)*4; seen.add(d[i]+'-'+d[i+1]+'-'+d[i+2]+'-'+d[i+3]);
                      }
                    return {colors:seen.size,w,h};
                }""")
                require(stats["colors"] >= 8, f"canvas renders varied content (sample colors={stats['colors']})")

                # Select a real opportunity from the native library; no invented item names.
                await page.locator('button[data-nav="机会库"]').click()
                await page.locator("#panelOverlay.open").wait_for(state="visible")
                search = page.locator('#panelContent input[aria-label="搜索机会库"]')
                await search.fill("好创意")
                first = page.locator("#libraryResults article.panel-row").first
                await first.wait_for(state="visible")
                selected = (await first.locator("h3").inner_text()).strip()
                require("好创意" in selected, "actual library result matches the query 好创意")
                await first.get_by_role("button", name="查看详情").click()
                await page.locator("#panelOverlay.open").wait_for(state="hidden")
                require((await page.locator("#title").inner_text()).strip() == selected,
                        "selected opportunity agrees with real detail title")
                require("未评级" in await page.locator("#planetLegend").inner_text(),
                        "planet size not described as competition ranking")
                require("12" in await page.locator("#zoomValue").inner_text(), "visible default 12-month time range")
                await page.wait_for_timeout(280)
                await capture(page, "01_galaxy", {"selected_opportunity": selected,
                                                   "range_text": await page.locator("#zoomValue").inner_text(),
                                                   "canvas_colors_sampled": stats["colors"]})

                await page.locator('button[data-nav="机会库"]').click()
                await page.locator("#panelOverlay.open").wait_for(state="visible")
                search = page.locator('#panelContent input[aria-label="搜索机会库"]')
                await search.fill("好创意")
                first = page.locator("#libraryResults article.panel-row").first
                await first.wait_for(state="visible")
                library_name = (await first.locator("h3").inner_text()).strip()
                require(library_name == selected, "same opportunity appears in searched library")
                require(await search.input_value() == "好创意", "search control retains actual query")
                await capture(page, "02_library", {"query": "好创意", "first_result": library_name,
                                                   "header": await page.locator("#panelTitle").inner_text()})
                await page.locator("#closePanel").click()
                await page.locator("#panelOverlay.open").wait_for(state="hidden")

                await page.locator("#pathBtn").click()
                await page.locator("#panelOverlay.open").wait_for(state="visible")
                path_name = (await page.locator("#panelContent h3").first.inner_text()).strip()
                require(path_name == selected, "eligibility path refers to selected opportunity")
                require("资格路径" in await page.locator("#panelTitle").inner_text(),
                        "actual eligibility dialog title")
                matched = await page.locator("#panelContent").inner_text()
                require("个人匹配" in matched and "核实" in matched, "eligibility panel includes fit and verification")
                await capture(page, "03_eligibility", {"opportunity": path_name,
                                                        "title": await page.locator("#panelTitle").inner_text(),
                                                        "has_self_check": await page.locator(".self-check-form").count() > 0})
                await page.locator("#closePanel").click()
                await page.locator("#panelOverlay.open").wait_for(state="hidden")

                await page.locator("#simulateBtn").click()
                await page.locator("#futureOverlay.open").wait_for(state="visible")
                await page.locator('[data-goal="能力"]').click()
                await page.locator('[data-risk="能力不足"]').click()
                for selector,value in [("#hoursRange","8"),("#weeksRange","10")]:
                    await page.locator(selector).evaluate(
                        "(el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));}", value
                    )
                require("8" in await page.locator("#hoursValue").inner_text(), "hours control now shows 8")
                require("10" in await page.locator("#weeksValue").inner_text(), "weeks control now shows 10")
                require((await page.locator("#futureHours").inner_text()).strip() == "80", "8 x 10 = 80 hours in UI")
                require("10周后" in await page.locator("#futureStory").inner_text(), "outcome responds to weeks")
                require("预演一种可能的未来" in await page.locator("#futureTitle").inner_text(),
                        "actual scenario title")
                require("chosen" in (await page.locator('[data-goal="能力"]').get_attribute("class") or ""),
                        "goal choice selected visually")
                require("chosen" in (await page.locator('[data-risk="能力不足"]').get_attribute("class") or ""),
                        "risk choice selected visually")
                await capture(page, "04_simulator", {"goal":"能力","risk":"能力不足",
                                                      "hours_per_week":8,"weeks":10,"total_hours":80,
                                                      "title":await page.locator("#futureTitle").inner_text()})
                # A successful capture makes no claim that official information is fresh.
                require(len(errors) == 0, "no uncaught JavaScript runtime errors")
                manifest["status"] = "PASS"
            finally:
                await browser.close()
    except Exception as exc:
        manifest["status"] = "FAIL"
        errors.append(f"{type(exc).__name__}: {exc}")
        raise
    finally:
        (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        create_report(manifest)
        print("Verification:", manifest["status"], "| images:", len(records),
              "| checks:", len(checks), "| errors:", errors, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
