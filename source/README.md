# KD 工作知识库

本知识库服务于光伏制造相关的数据处理、技术文档和程序开发，重点是 TOPCon 与管式硼扩散、氧化、LPCVD、PECVD。以 `C:\work\OEE\git\OEE_algo\KD\OEE_docs\kd` 的 16 份 Markdown 为初始资料，原文保存为独立快照；原目录不改动。

建立日期：2026-10-28（Asia/Shanghai）。这是参考资料整理与工作方法，不是已核准的工厂规范，也未对原文外部引用逐条重新核验。

## 先读什么

| 当前问题 | 入口 | 何时回到原文 |
|---|---|---|
| 工艺路线、上下游、不同电池技术 | [工艺地图](knowledge/process-map.md) | 确认路线顺序、技术结构和参考数值 |
| 炉管、舟、温区、真空、气路、配方步骤 | [设备知识](knowledge/equipment.md) | 对比设备参数、步骤和测量上下文 |
| IV、EL、PL、寿命、材料、质量关联 | [质量与材料](knowledge/quality-and-materials.md) | 检查测试条件、指标定义和缺陷证据 |
| 中文简称、英文缩写、数据集代号与多别名 | [名称对照表](knowledge/name-crosswalk.md)、[术语表](glossary.json)，或 `abbr` 命令 | 确认概念、状态、适用范围与来源性质 |
| 同一缩写有多种中文含义、来源定义冲突 | [名称消歧工作流](workflows/name-disambiguation.md) | 结合当前上下文判断；仍不能确定时向用户确认 |
| OEE、状态、配方和原文有歧义的数值 | [缺口与冲突](knowledge/gaps-and-conflicts.md) | 决定哪些结论可以给出、哪些需要确认 |
| 表格、SQL、日志、时间序列、批次分析 | [数据工作流](workflows/data-analysis.md) | 使用真实字段前确认字典和口径 |
| 技术说明、报告、需求、SOP 草稿 | [文档工作流](workflows/document-writing.md) | 重要工艺主张给出文件与章节 |
| Word/Excel/PPT 模板、样式、公司 Logo 与批量规范化 | [laplace-office-standardize](../skills/laplace-office-standardize/SKILL.md) | 区分模板草案与正式版本，检查输出内容和版面 |
| 采集、清洗、指标、接口、程序修改 | [程序工作流](workflows/software-development.md) | 为实现选择上下文并确定有意义的边界测试 |

首次接触领域可先读 [原始总目录](references/kd/00_index.md)，之后只加载当前任务相关章节。[术语表](glossary.json) 是概念与多简称的唯一主表，[名称对照表](knowledge/name-crosswalk.md) 由它生成；[catalog.json](catalog.json) 是机器可读文档目录、章节行号和文件哈希。

## 资料层次与可信范围

- `references/kd/`：原样复制的参考资料；它描述工艺背景和典型条件，不能自动代表现场标准。
- `knowledge/`：基于原文整理的领域地图、解释和冲突清单。引用用于回查；建议与待确认项有明确标记。
- `evidence/`：数据集研究证据，保留目录、字段或样例的具体语境；局部观察不等于经确认的全厂定义。
- `workflows/`：本次建立的 Agent 工作建议，指导如何应用领域知识，不是原文宣称的工厂制度。
- `templates/`：任务所需的数据契约、报告、文档输入和程序变更模板；未填写的 `null` 表示未知，不表示零或已确认。
- `evidence/`：用户名称约定及数据集中的必要摘录，保留原文件相对路径、行号和适用范围，不复制完整生产数据。
- `manifest.json`：原文路径、导入时间、上游修改时间、字节数和 SHA-256。导入日期不等于资料事实的生效日期。
- `tools/kb.py`：仅使用 Python 标准库的本地检索与校验工具，不调用网络、向量数据库或模型 API。

对于原文的效率纪录、市场份额、成本和“量产推荐”等时间相关描述，应保留原文年份与范围。用户要求当前行业信息时再查询相应权威资料；不要把 2024–2026 的历史内容改写成当前事实。检索命中只提供线索，最终结论须阅读上下文。

当前已补充数据集的局部名称与字段解释，尚不能代表现役全厂数据库、点位映射或设备编码，也未确认排班、OEE 定义、正式配方版本及验收/报警限。优先使用用户提供且适用于本任务的现场文件；补入知识库时记录来源、版本、生效范围和确认状态。不得把分析假设写成确认规则。

## 检索与校验

从 `D:\work\KD` 运行，Python 3.10 以上即可，无需安装包：

```powershell
python source/tools/kb.py search "硼扩散 炉管" --limit 5
python source/tools/kb.py search "OEE 状态 分母" --category workflows --json
python source/tools/kb.py search "氮化硅" --category references
python source/tools/kb.py index --check
python source/tools/kb.py verify
```

本机的 `python` 命令可能指向 Windows 应用执行别名；本次使用的解释器可这样调用：

```powershell
$kdPython = 'C:\Users\tianw\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $kdPython source/tools/kb.py search "LPCVD 压力"
& $kdPython -m unittest discover -s source/tests -v
```

检索按标题、关键词、中文双字片段和术语别名评分，已确认简称可展开检索，未确认候选只展示、不自动扩为同义词。结果返回文件、章节、起止行号、证据类型、来源状态和摘录；历史快照会明确标记。支持 `--category references|knowledge|workflows|templates|evidence` 和 `--limit 1..50`。这是轻量字面检索，不能保证语义召回；无命中、索引缺失/过期或工具不可运行时，换简称、设备名或用 `rg -n "关键词" source` 搜索。普通分析不必为此修改原文或刷新快照。

维护后先运行 `crosswalk` 同步名称对照表，再运行 `index` 更新目录及 `verify` 校验。`index` **不更新原文清单**，也不会掩盖原文被修改的问题。`verify` 检查快照 SHA-256、索引一致性、本地文件链接及术语出处路径，不核验外部网址、章节锚点、工业适用性或技术事实。工具从脚本的真实路径定位知识库，可在其他工作目录调用。

## 常用简称、缩写与数据集代号

命令：`python source/tools/kb.py abbr [QUERY] [--category technology|equipment|process|testing|materials|metrics] [--limit N] [--json]`。

```powershell
python source/tools/kb.py abbr
python source/tools/kb.py abbr "硼扩"
python source/tools/kb.py abbr "PE"
python source/tools/kb.py abbr "BK"
python source/tools/kb.py abbr "PK"
python source/tools/kb.py abbr "硼扩散" --json
python source/tools/kb.py abbr --category testing --limit 10
```

省略 `QUERY` 列出清单；可用中文简称、英文缩写、数据集代号、概念全称或别名查询，兼容大小写及 Unicode 规范化。按“硼扩散”等概念查询可查看多个简称，没有英文缩写的概念也可查。本次用户确认：硼扩散包括“硼扩/BK”，PECVD 可简称“PE”，磷扩散可简称“PK”；各项含义还应结合记录的适用范围使用。

结果显示全称、多个简称、用途、备注、确认状态、适用范围和来源。`short_names` 中 `kind` 区分 `chinese_short|english_short|dataset_code|symbol`，`status` 区分 `user_confirmed|dataset_explicit|dataset_inferred|knowledge_explicit|curated`，`scope` 保留厂区、数据集或字段语境。候选不自动扩同义或全局替换字段/日志；不能把 LP 猜成磷扩散，也不能按拼音猜 TX 等代号。数据集局部证据不会自动变成全厂规则。

同一英文缩写可以有多个中文义，按[名称消歧工作流](workflows/name-disambiguation.md)先核对原句、工序设备、路线、邻列单位及来源版本。JSON 的 `disambiguation` 返回 `status`、`requires_context_review`、`next_action` 和带 `term/scopes/sources` 的 `candidates`；有歧义或无命中时还提供建议用的 `confirmation_prompt`。工具只列候选和提示，不自动按关键词选义，也没有 `--context` 参数。Agent 复核上下文后仍不能判断，必须向用户确认；答复前暂停依赖该含义的处理，其他独立工作可继续。已有适用的用户定义不重复询问，一次推断不自动变成全库约定。

所有名称同源维护在 `glossary.json`。旧 `aliases` 保留为相关检索提示词，可能包含气源、结构等相关概念，不能一律当作严格同义词；`abbr` 和对照表使用明确维护的名称与 `short_names`。对照表覆盖已维护简称/缩写的概念，其余普通术语仍可用 `search` 检索。`full_name_status` 仍区分 `source_explicit`（原文明确全称）与 `curated_translation`（整理补充），不能把所有全称归于原文。Voc、J₀、η 等符号、化学式与 OEE 口径需结合上下文，不强行展开为英文缩写。

[名称对照表](knowledge/name-crosswalk.md) 从主表生成，不单独手改。维护名称后按顺序运行：

```powershell
python source/tools/kb.py crosswalk
python source/tools/kb.py index
python source/tools/kb.py verify
python source/tools/kb.py crosswalk --check
```

`crosswalk --check` 仅检查生成表是否与主表一致。数据集研究证据保存在 `evidence/`，可从各名称的 `sources` 回查。

## 使用 skills

| skill | 用法示例 |
|---|---|
| [kd-context](../skills/kd-context/SKILL.md) | “查询硼扩散的常用简称，解释 PE、BK、PK 的含义与适用范围。” |
| [kd-data-analysis](../skills/kd-data-analysis/SKILL.md) | “分析这份批次数据，先检查单位、粒度和 OEE 口径。” |
| [kd-document-writing](../skills/kd-document-writing/SKILL.md) | “基于知识库写管式设备分析报告，标注待确认事项。” |
| [laplace-office-standardize](../skills/laplace-office-standardize/SKILL.md) | “按选定模板处理这些 Word、Excel、PPT，应用公司 Logo，另存副本并复核。” |
| [kd-software-development](../skills/kd-software-development/SKILL.md) | “修改设备日志清洗程序，支持炉管与批次粒度。” |
| [kd-knowledge-maintenance](../skills/kd-knowledge-maintenance/SKILL.md) | “把新的点位表和确认口径补入知识库并检查冲突。” |

实体文件位于 `D:\work\KD\skills\`。本工作区另以 `.agents/skills/` 目录联接接入 Codex 项目技能发现；项目根 [AGENTS.md](../AGENTS.md) 提供未自动发现时的读取入口。Codex 的扫描目录和链接支持依据 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。如当前会话未显示新 skills，可在此工作区开启新会话；也可直接指定对应 `SKILL.md` 路径。

在 Windows 移动/复制整个工作区后，目录联接可能仍指向旧地址。先检查 `.agents/skills/` 的目标；确认移除旧联接而保留实体 skills 后，运行 `& .\source\tools\connect-skills.ps1` 重新建立。本脚本不会自动删除或覆盖已有的不同目标。

## 更新资料

普通资料整理优先编辑派生知识及工作流，并保留原文。只有任务要求导入/更新原文快照时，执行：

```powershell
python source/tools/kb.py snapshot --source 'C:\work\OEE\git\OEE_algo\KD\OEE_docs\kd'
# 已有原文变化时，先审阅差异，再显式加 --update。
python source/tools/kb.py crosswalk
python source/tools/kb.py index
python source/tools/kb.py verify
```

导入只读取指定目录顶层的 `.md`，按字节复制。已从上游移除的旧文件保留并标记 `not_in_latest_import`，供历史追溯；不自动删除旧知识。更新后同步检查派生结论、冲突、术语和技能引用，不仅更新索引。详细操作见维护 skill。
