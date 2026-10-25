# FlowMate

在线网页：https://leelee00000.github.io/Solution1/

V80延续版本：稳定ID生成行星外观，支持星系拖动、暂停、下盖上遮挡、机会对比、收藏、资格初筛与单文件离线使用。个人资料只存当前浏览器。

## 数据接入

[资料接入接口、导入命令与限制](docs/data-ingestion.md) · [规范数据](data/opportunities.json) · [JSON Schema](data/opportunity.schema.json)

支持JSON、JSONL和公开HTTPS JSON；默认预检，显式apply才写入。官方核验需要原文证据与人工审校，不能从HTTP200推断。当前真实资料16条；5000条仅为隔离压力测试。

## 开发与验证

需要Python、Node、Chromium；来源PDF检查需要pdftotext。云环境可运行 `bash tools/setup.sh` 安装固定版本依赖。

启动 `npm start`，在另一终端激活 `.venv` 后执行 `npm test`。功能回归使用固定资料夹具，当前生产数据单独检查；更换资料不要求保留旧样本。

导入后运行 `.venv/bin/python tools/build.py` 生成自包含index.html，再提交发布。Pages仅静态托管，不运行来源抓取后台。
