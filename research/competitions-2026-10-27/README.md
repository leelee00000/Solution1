# FlowMate 本科生竞赛资料库 · 2026-10-27

本轮资料整理完成，共 **131 条资料记录**：**51 条近期报名项目，涉及 26 个赛事体系**；21 条待核候选；59 条已截止归档。**本轮没有核实到100项符合该窗口的独立赛事**，不能把总资料数或赛道数宣传为当前独立赛事数。

[下载 Excel 资料库](FlowMate-competitions-2026-10-27.xlsx?raw=true) · [CSV](competitions.csv?raw=true) · [完整 JSON](competitions.json) · [近期 JSON](recent-eligible.json) · [来源核验索引](sources.json)

## 范围与计数

- 核验日：2026年10月27日，北京时间；观察窗口至2026年12月27日。
- 面向本科生；确认有省级或全国赛制；当前公开报名窗口内或窗口内即将启动。全国赛制不等于教育部认定，更不等于任何学校已认定加分。
- 近期项目中，**40 条截止落在两个月内，10 条当前开放但截止更晚，1 条学校另定截止**。如只需要两月内截止，筛选 `isDeadlineWithinWindow=true`。
- 一条是具体报名项目或学校通道；主赛事去重看 `series`。例如蓝桥杯的软件赛、电子赛不同报名内容分列，但软件赛内语言科目不拆条；同一赛事的不同校内截止不能冒充不同独立赛事。
- 7 条近期记录有明确学校限制，不能推荐给其他学校；其余全国赛事也可能有更早的校内登记或推荐要求。
- 抓取 992 个URL缓存，其中 861 个读取到内容。抓取量包含目录、历史通知、重复转载和不符合条件页面；它不是赛事数，也不代表全部逐字段审校完成。

## 文件说明

| 文件 | 用途 |
|---|---|
| FlowMate-competitions-2026-10-27.xlsx | 说明与统计、近期项目、待核、归档、来源索引，均可筛选 |
| competitions.csv | UTF-8 BOM，便于Excel或表格系统接入 |
| competitions.json | 完整资料；research-1契约，包含资格、学校、日期、费用、备注、来源和稳定key |
| recent-eligible.json | 严格主库的近期子集；仍需结合学校和个人资格判断 |
| sources.json | 来源URL、读取方法、SHA256依据、关联ID和核验日；不转载全文 |
| identity-map.json | 稳定key到研究记录ID的映射；后续更新保留ID |

这批JSON是研究资料契约，**不是当前 `data/opportunity.schema.json` 的直接导入批次**。接入原网站时先按key与原21条对照、保留既有收藏ID，再映射 `dates/source/eligibility/competition` 字段；不得把待核候选自动升级为已核验。当前没有修改网站线上资料或页面。

## 日期和资格处理

1. 只写日期的公告不补造23:59；“11月6日前”保留日期并在备注提示精确时刻未知。
2. 10月27日24:00在精确时间字段表示为10月28日00:00；原报名日仍为10月27日。下游系统须处理这一午夜边界。
3. 报名、缴费、作品提交、校内推荐和决赛日期分别理解，不拿比赛时间冒充报名截止。
4. “公告报名窗口内”只核对公开时间与所列资格；没有登录报名后台验证系统接受提交，也不等于用户本人通过资格审核。
5. 未知费用、人数、专业等保留未明确；不填造“免费”“不限”。校内比赛自身奖项不冒充省赛或国赛奖项。

## 本轮发现的关键冲突

| 来源 | 处理 |
|---|---|
| [辽宁人力资源管理赛项](https://cxxy.lntu.edu.cn/info/1134/5675.htm) | 同页2026/2025年报名截止冲突，放待核 |
| [大学生数字技能互联网+赛](https://www.cnccac.com/hlw) | 正文12月10日、浮层12月11日，放待核 |
| [数据要素长沙理工大学通知](https://www.csust.edu.cn/stxy/info/1053/10965.htm) | 正文与表格节点不同，保留原文差异；北京理工大学通道另记 |
| [米兰设计周学校通知](https://www.lncu.edu.cn/cxcyxy/29098.html) | 学校3月31日与既有官方CMS4月口径未统一，放待核，不覆盖原站记录 |
| [云南大学化学赛通道](https://jwc.ynu.edu.cn/info/1009/4382.htm) | 报名11月30日明确；后续作品区间年份倒置，只有报名日进入主库 |

## 近期报名项目清单

下面是报名项目，不是51个独立主赛事。费用、完整资格与备注见Excel/JSON。

| 编号 | 项目 | 公告报名截止 | 范围 |
|---|---|---|---|
| fm-1040 | [2026年辽宁省大学生管理决策模拟大赛 · 领导力潜质提升赛道](https://cxxy.lntu.edu.cn/info/1134/5655.htm) | 2026-10-27 | 辽宁省 |
| fm-1042 | [2026年山东省大学生物理创新大赛（理论竞赛）](https://sci.upc.edu.cn/2026/1010/c6838a502286/page.htm) | 2026-10-30 | 山东省 |
| fm-1039 | [2026年辽宁省大学生动漫与媒体创意设计大赛](https://www.lncu.edu.cn/cxcyxy/29153.html) | 2026-10-30 | 辽宁省 |
| fm-1020 | [第十一届全国大学生软件测试大赛 · 凯云杯嵌入式测试](https://www.cuit.edu.cn/info/1006/17092.htm) | 2026-10-30 | 全国 |
| fm-1021 | [第十一届全国大学生软件测试大赛 · 微信小微AI助手评测专项赛](https://www.cuit.edu.cn/info/1006/17092.htm) | 2026-10-30 | 全国 |
| fm-1019 | [第十一届全国大学生软件测试大赛 · 慕测杯Web应用测试](https://www.cuit.edu.cn/info/1006/17092.htm) | 2026-10-30 | 全国 |
| fm-1018 | [第十一届全国大学生软件测试大赛 · 拓思杯开发者测试](https://www.cuit.edu.cn/info/1006/17092.htm) | 2026-10-30 | 全国 |
| fm-1066 | [好创意 · 第3届河马杯大学生AI创意微短剧专项赛](https://www.cdec.org.cn/articleDetail/2364) | 2026-10-31 | 全国 |
| fm-1065 | [好创意 · 重生纪元·恐龙AI创作专项赛](https://www.cdec.org.cn/articleDetail/2299) | 2026-10-31 | 全国 |
| fm-1034 | [未来设计师NCDA · AI漫剧出海OPC优才选拔](https://www.ncda.org.cn/dsjs/dsnr/mtsd/9C3/) | 2026-10-31 | 全国 |
| fm-1024 | [正大杯第十七届全国大学生市场调查与分析大赛（本科组）](https://newoaa.shisu.edu.cn/3c/b9/c6353a212153/page.htm) | 2026-10-31 | 全国 |
| fm-1013 | [第十一届华为ICT大赛中国赛 · 实践赛](https://pec.xjtu.edu.cn/info/1191/5551.htm) | 2026-10-31 | 全国 |
| fm-1014 | [第十一届华为ICT大赛中国赛 · 挑战赛](https://pec.xjtu.edu.cn/info/1191/5551.htm) | 2026-10-31 | 全国 |
| fm-1025 | [第十二届中金所杯全国大学生金融知识大赛](https://www.e-cffex.com.cn/web/zxgg/20260807/2593.html) | 2026-10-31 | 全国 |
| fm-1009 | [第八届全国高校计算机能力挑战赛 · 大数据挑战赛](https://www.ncccu.org.cn/index/Paper/case2.html) | 2026-11-06 | 全国 |
| fm-1037 | [第十四届全国大学生数字媒体科技作品及创意竞赛 · OPC数字新消费专项赛](https://www.cmit.cn/uploadfile/2026/1012/45828.html) | 2026-11-06 | 全国 |
| fm-1043 | [首届上海市大学生化学实验创新设计大赛](https://www.sspu.edu.cn/2026/1023/c3028a172893/page.htm) | 2026-11-06 | 上海市 |
| fm-1038 | [2026年辽宁省大学生智慧海洋科技创新大赛](https://www.lncu.edu.cn/cxcyxy/29171.html) | 2026-11-08 | 辽宁省 |
| fm-1045 | [第六届全国大学生化学实验创新设计大赛 · 大连理工大学报名通道](https://chem.dlut.edu.cn/info/1010/13800.htm) | 2026-11-12 | 大连理工大学校内选拔通道 |
| fm-1008 | [第八届全国高校计算机能力挑战赛 · 人工智能挑战赛](https://www.ncccu.org.cn/index/Paper/case1.html) | 2026-11-13 | 全国 |
| fm-1023 | [第九届传智杯全国大学生数智创新与AI应用大赛](https://jwc.xjtu.edu.cn/info/1172/10505.htm) | 2026-11-18 | 全国 |
| fm-1012 | [第八届全国高校计算机能力挑战赛 · 数字媒体创新设计赛](https://www.ncccu.org.cn/index/Paper/case7.html) | 2026-11-19 | 全国 |
| fm-1047 | [2027年全国高校商业精英挑战赛品牌策划竞赛 · 品牌策划赛道（南京工业大学通道）](https://jgy.njtech.edu.cn/info/1012/6045.htm) | 2026-11-20 | 南京工业大学校内选拔通道 |
| fm-1048 | [2027年全国高校商业精英挑战赛品牌策划竞赛 · 数字营销赛道（南京工业大学通道）](https://jgy.njtech.edu.cn/info/1012/6045.htm) | 2026-11-20 | 南京工业大学校内选拔通道 |
| fm-1022 | [第十二届数维杯全国大学生数学建模挑战赛（秋季赛）](https://www.nmmcm.org.cn/News/198.html) | 2026-11-20 | 全国 |
| fm-1010 | [第八届全国高校计算机能力挑战赛 · Office高级应用赛](https://www.ncccu.org.cn/index/Paper/case3.html) | 2026-11-25 | 全国 |
| fm-1011 | [第八届全国高校计算机能力挑战赛 · 程序设计挑战赛](https://www.ncccu.org.cn/index/Paper/case4.html) | 2026-11-25 | 全国 |
| fm-1035 | [2026新锐设计竞赛·华灿奖 · 创意赛道](https://www.lncu.edu.cn/cxcyxy/29091.html) | 2026-11-27 | 全国 |
| fm-1067 | [好创意 · 古建山西·潮创三晋专项赛](https://www.cdec.org.cn/articleDetail/2331) | 2026-11-30 | 全国 |
| fm-1046 | [第六届全国大学生化学实验创新设计大赛 · 云南大学报名通道](https://jwc.ynu.edu.cn/info/1009/4382.htm) | 2026-11-30 | 云南大学校内选拔通道 |
| fm-1016 | [第十一届华为ICT大赛中国赛 · 创新赛](https://pec.xjtu.edu.cn/info/1191/5551.htm) | 2026-11-30 | 全国 |
| fm-1015 | [第十一届华为ICT大赛中国赛 · 精英赛](https://pec.xjtu.edu.cn/info/1191/5551.htm) | 2026-11-30 | 全国 |
| fm-1017 | [第十一届华为ICT大赛中国赛 · 编程赛](https://pec.xjtu.edu.cn/info/1191/5551.htm) | 2026-11-30 | 全国 |
| fm-1026 | [第十二届国际大学生智能农业装备创新大赛](https://due.xjtu.edu.cn/info/1172/10541.htm) | 2026-11-30 | 全国 |
| fm-1007 | [第十八届蓝桥杯 · 主视觉与赛事IP文创设计专项赛](https://jwc.xjtu.edu.cn/info/1172/10507.htm) | 2026-11-30 | 全国 |
| fm-1030 | [第四届全国大学生职业规划大赛 · 辽宁省报名规则](https://jyt.ln.gov.cn/jyt/gk/zxtz/2026102110290659632/index.shtml) | 2026-12-16 | 辽宁省 |
| fm-1004 | [第十八届蓝桥杯 · 人工智能赛](https://jwc.xjtu.edu.cn/info/1172/10507.htm) | 2026-12-18 | 全国 |
| fm-1002 | [第十八届蓝桥杯 · 电子赛](https://dasai.lanqiao.cn/pages/v7/dasai/competition/individual_competition.html) | 2026-12-18 | 全国 |
| fm-1001 | [第十八届蓝桥杯 · 软件赛](https://dasai.lanqiao.cn/pages/v7/dasai/competition/individual_competition.html) | 2026-12-18 | 全国 |
| fm-1003 | [第十八届蓝桥杯 · 鸿蒙应用开发](https://dasai.lanqiao.cn/pages/v7/dasai/competition/individual_competition.html) | 2026-12-18 | 全国 |
| fm-1041 | [第五届湖北省大学生信创大赛（本科段）](https://jky.yangtzeu.edu.cn/info/1026/3563.htm) | 2026-12-30 | 湖北省 |
| fm-1027 | [2027年第四届大学生数据要素素质大赛](https://jwb.bit.edu.cn/xs/pyfa_2/tzgg__26/92c0d995fa3a4e5180339fc6940d35b0.htm) | 2026-12-31 | 北京理工大学报名通道 |
| fm-1044 | [第十三届北京市大学生生物学竞赛](https://jw.beijing.gov.cn/gjc/tzgg_15688/202610/t20261010_4895831.html) | 2027-01-15 | 北京市 |
| fm-1028 | [第十二届全国大学生生命科学竞赛（科学探究类）](https://www.czu.cn/_t454/2026/1008/c6a178013/pagem.htm) | 2027-01-15 | 全国 |
| fm-1036 | [2026新锐设计竞赛·华灿奖 · 定向赛道](https://www.lncu.edu.cn/cxcyxy/29094.html) | 2027-03-05 | 全国 |
| fm-1006 | [第十八届蓝桥杯 · 数字科技创新赛](https://jwc.xjtu.edu.cn/info/1172/10507.htm) | 2027-04-26 | 全国 |
| fm-1005 | [第十八届蓝桥杯 · 视觉艺术设计赛](https://jwc.xjtu.edu.cn/info/1172/10507.htm) | 2027-04-26 | 全国 |
| fm-1032 | [第4届红色文化创意设计专项赛 · 好创意学生通道](https://www.cdec.org.cn/articleDetail/2542) | 2027-04-30 | 全国 |
| fm-1033 | [第5届老字号·新国潮创新设计专项赛 · 好创意](https://www.cdec.org.cn/articleDetail/2527) | 2027-05-01 | 全国 |
| fm-1031 | [第21届中国好创意暨全国数字艺术设计大赛 · 常规赛学生单元](https://www.cdec.org.cn/articleDetail/2363) | 2027-05-31 | 全国 |
| fm-1029 | [第四届全国大学生职业规划大赛（学生赛道）](https://www.moe.gov.cn/srcsite/A15/s7063/202610/t20261010_1453481.html) | 学校另定，最晚边界见原文 | 全国 |

资料为公开来源的AI辅助整理快照；未声称全网穷尽、主办方审核或人类签字审校。发布前应重新检查临近截止及冲突条目。
