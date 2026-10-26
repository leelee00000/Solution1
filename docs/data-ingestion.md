# 资料接入接口 v1

网站：https://leelee00000.github.io/Solution1/

资料读接口：`GET /Solution1/data/opportunities.json`。这是公开静态快照，不是实时爬虫或公共写接口。来源映射成同一契约后，可使用 JSON、JSONL 或公开 HTTPS JSON 批量接入。已有5000条模拟记录的导入和浏览器压力验证；当前真实资料21条，模拟数据不进入线上库。

## 稳定身份与外观

- `id` 为 `fm-` 加3–9位数字；不足三位左补零，四位以上不再补零，避免显示编号碰撞。一个届次、赛项和适用范围使用一个永久ID；同一记录更新保留ID，不同竞赛不得复用旧ID。
- 来源系统应持久化“上游记录键→FlowMate ID”映射，不能按每批行号重建ID。名称/范围的有意更正需显式 `--allow-identity-change`；不同届次仍须新ID。
- 外观版本 `paper-v1` 通过ID和独立命名空间生成固定种子、受光/纹理参数与初始相位。排序、增删和换批不改变同一ID外观；颜色仍由方向决定。旧 `a` 角度已弃用，新记录无需填写。
- 星系与详情使用同一ID种子。材质不包含竞赛评级信息。收藏与路径使用ID；暂时不在当前批次的收藏ID保留，不重新绑定到新记录。

## 数据契约

批次可为数组、`{"schemaVersion":1,"opportunities":[...]}`，或每行一条记录的JSONL。完整字段见 `data/opportunity.schema.json`，批次入口见 `data/import-batch.schema.json`。

|字段|要求|
|---|---|
|id、name、cat、direction|稳定ID，真实名称，现有类别和方向枚举|
|org、aud、field、note|主办单位、面向对象、明确的全国/校内/地区范围与限制说明|
|dates|start/end/award/deadlineAt/published；未知为null；timezone为Asia/Shanghai；精确截止统一+08:00，保留官方原文依据|
|source|公开公告URL、来源类型、核验状态、核验时间和抓取记录；新抓取默认pending，不冒充已核验|
|eligibility|学校/地区/学历/学籍/年级/角色/队伍规则；未知不猜；rulesComplete默认false，复杂条件留逐项自查|
|source.evidence|已核验记录需要原文摘录、正文摘要与人工审校登记；HTTP200不代表内容核验|

## 操作流程

在仓库根目录执行；先安装 `requirements-test.txt` 中固定的JSON Schema依赖（云环境可用 `.venv/bin/python`）。

```sh
# 只预检，不修改当前资料
.venv/bin/python tools/import_catalogue.py --input incoming.json --report artifacts/import-preview.json

# JSONL或公开HTTPS JSON也可作为来源；远程响应上限32MiB
.venv/bin/python tools/import_catalogue.py --input incoming.jsonl
.venv/bin/python tools/import_catalogue.py --url https://your-data-service.example/opportunities.json

# 预检通过后按ID增量更新；未出现在本批次的记录保留
.venv/bin/python tools/import_catalogue.py --input incoming.json --apply

# 明确要换整批时使用replace；预检报告会列出删除ID
.venv/bin/python tools/import_catalogue.py --input replacement.json --mode replace --report artifacts/replacement-preview.json
.venv/bin/python tools/import_catalogue.py --input replacement.json --mode replace --apply

# 人工核验登记格式见data/source-reviews.json；新核验或变更已核验事实须提供对应登记
.venv/bin/python tools/import_catalogue.py --input reviewed.json --reviews reviewed-evidence.json --apply

# 生成单文件网页，再发布；导入并不自动发布
.venv/bin/python tools/build.py
.venv/bin/python tools/build.py --check
```

域名示例仅说明接口形态，不是已接入的数据提供商。CSV、Excel、任意网页HTML和带认证/分页的供应商接口，需先做字段映射或来源适配，不能直接声称全网自动接入。

预检检查重复ID、重复记录范围、字段枚举、日期与时区、人数范围、原文证据登记和核验条件。默认不写文件；`--apply`才写规范资料、审校登记和监测状态。旧文件备份到 `artifacts/import-backups/时间戳/`；各文件原子替换，普通写入异常回滚。进程/机器意外中断仍应检查备份及manifest，不承诺跨文件数据库事务。整个规范资料文件通过校验后才可构建。

## 分批检查与页面承载

```sh
# 仅检查选中ID
.venv/bin/python tools/refresh_data.py --ids fm-006 fm-009
# 优先检查最久未检查的100条，下次运行会轮到其他旧记录
.venv/bin/python tools/refresh_data.py --limit 100
```

每条来源保留自己的checkedAt；检查一批不会把其他记录的旧检查时间刷成“最新”。导入只更新catalogueRevision，不伪造检查时间，不自动把pending升级verified。自动检测只能发现变更，仍需人工审校。

星系每组12项，机会库/日程/收藏每页50项，完整记录仍可搜索、筛选和切换。来源清单先显示50项，其余可进入机会库。过滤缓存与来源ID索引避免每帧重复全库计算。

固定业务回归使用 `tests/fixtures/`，生产规范数据另做通用契约与浏览器检查，因此换批不需要保留旧样本才能跑测试。5000条模拟记录只在临时测试上下文和临时目录，绝不发布为真实机会。

## 目前的边界

接口、批量校验和分页已具备，可以开始分批接入真实来源。现有真实记录为21条（含具体赛项/校内阶段），不是5000条已核验竞赛。大量真实信息还需具体官方来源适配、人工证据审校、阶段与范围拆分、持续变更处理。GitHub Pages本身不运行抓取任务或写入API；自动采集、定时大规模审校和跨设备账户需要后端任务服务。

## 本科与赛制层级字段

可选competition对象记录赛系、具体赛道、level（national/provincial/unknown）、bachelorEntry和对应原文basis。已确认层级或本科允许值必须来自已核验正文，并存在于source.evidence.quotes；校内认定目前明确保持unconfirmed，不从赛事冠名、联盟高校或全国征集范围推断加分。选录实例见 [设计本科候选](design-opportunities.md)。当前真实记录21条，5000条仍仅是隔离测试。

跨组比较会保留同一筛选范围内的候选；只有改变筛选后不再匹配的候选才移除。
