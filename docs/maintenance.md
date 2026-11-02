# 拉普老师傅：源码维护参考

[返回项目首页](../README.md) · [Lapdex 用户手册](usage.md) · [实际效果与完整案例](examples/README.md)

本页面向维护源码工作区的开发者，保留技能分工、Office处理细节及知识维护命令。Lapdex 安装和日常使用请看[用户手册](usage.md)。下列相对路径命令均在含有 `AGENTS.md`、`source/` 和 `skills/` 的开发工作区根目录运行。

本分支提供六类业务工作流及打包工具；Lapdex v0.1.0 发行包以一个技能入口调用这些资源，尚未包含私有记忆。打包、脚本安装及验证范围见 [Lapdex 发行技术说明](lapdex.md)。

[技能分工](#skills) · [Office处理范围](#office) · [知识入口](#knowledge) · [使用命令](#commands) · [目录结构](#structure) · [建设与维护](#roadmap) · [私有记忆](#memory)

<a id="skills"></a>

## 六类业务工作流，各自负责什么

拉普老师傅是这套技能的统一名称。Agent 根据任务读取相应 skill，再按需查询知识或调用工具；当前路由入口见 [AGENTS.md](../AGENTS.md)。

| 当前 skill | 职责 | 主要产出 |
|---|---|---|
| [kd-context](../skills/kd-context/SKILL.md) | 专业知识查询与名称消歧 | 带出处和适用范围的解释、需要确认的问题 |
| [kd-data-analysis](../skills/kd-data-analysis/SKILL.md) | 数据检查与分析 | 字段、单位、粒度和指标口径检查，分析结果与限制 |
| [kd-document-writing](../skills/kd-document-writing/SKILL.md) | 文档编写、修订与内容检查 | 技术说明、报告草稿、修改摘要与待确认事项 |
| [kd-software-development](../skills/kd-software-development/SKILL.md) | 业务相关程序开发与审查 | 数据契约、程序实现建议或修改、验证依据 |
| [kd-knowledge-maintenance](../skills/kd-knowledge-maintenance/SKILL.md) | 知识和术语维护 | 有来源与范围的知识更新、同步后的对照表和索引 |
| [laplace-office-standardize](../skills/laplace-office-standardize/SKILL.md) | Office 格式与品牌规范化 | 规范化副本、逐文件保真报告、可选 PDF 复核材料 |

知识库提供专业依据，skills 规定处理任务的方法，脚本执行可重复的操作。例如整理一份分析报告，可以组合数据分析、文档编写和 Office 规范化三个技能。

技能实体保存在 `skills/`，`.agents/skills/` 中的目录联接连接到这些实体目录。

<a id="office"></a>

## Office 标准化的当前范围

首版工具支持 Windows 上已安装的 Microsoft Word、Excel 和 PowerPoint，处理 `.docx/.xlsx/.pptx` 并另存副本。当前 [样式配置](../skills/laplace-office-standardize/assets/company-profile.json) 和原生模板均为**可审阅草案**，Logo 使用用户提供的原图。正式模板提供后可通过新配置版本替换。

| 文档类型 | 当前处理内容 | 处理时保留的内容 |
|---|---|---|
| Word | 复制模板样式、按现有语义样式统一字体/字号、页边距、页眉 Logo | 主正文、直接强调、原有图片与其他页眉内容 |
| Excel | 正文字体、指定表头行、行列适配、工作表空白区 Logo 和打印页眉 Logo | 数值、公式、数字格式、单元格位置与工作表结构 |
| PowerPoint / PPT | 应用设计模板、字体与占位符字号、逐页 Logo | 页面数量、原画布、文本和原有对象；复杂版式逐页复核 |

模板应按文档用途记录版本和适用范围，例如技术说明、分析报告、客户方案、培训资料。Logo 应用规则需规定素材版本、放置位置、比例、留白以及哪些页面使用；具体要求以纳入项目的公司规范为准。

每批输出 `standardization-report.json`，记录逐文件结果、配置版本、输入/输出哈希、内容检查与复核提示。可用 `--pdf` 输出原生 Office 复核副本。当前不把任意 Excel 表格重排成另一套单元格布局，也不自动重排 PPT 自由布局；详见 [格式与保真约定](../skills/laplace-office-standardize/references/format-contract.md)。

模板草案预览：[Word](../skills/laplace-office-standardize/assets/templates/word.pdf) · [Excel](../skills/laplace-office-standardize/assets/templates/excel.pdf) · [PPT](../skills/laplace-office-standardize/assets/templates/powerpoint.pdf)。

<a id="knowledge"></a>

## 专业知识与资料入口

| 主题 | 内容 | 入口 |
|---|---|---|
| 工艺路线 | 硅材料、硅片、电池、组件；PERC、TOPCon、HJT 等路线的区别 | [工艺地图](../source/knowledge/process-map.md) |
| 管式设备 | 硼扩散、氧化、LPCVD、PECVD；炉管、舟、温区和工步 | [设备知识](../source/knowledge/equipment.md) |
| 测试与质量 | I-V、EL、PL、寿命、效率及相关材料 | [质量与材料](../source/knowledge/quality-and-materials.md) |
| 名称与简称 | 英文全称、中文名、别名、用途和出处 | [术语主表](../source/glossary.json) |
| 资料差异 | 单位、参数、工艺顺序等冲突及现场信息缺口 | [缺口与冲突](../source/knowledge/gaps-and-conflicts.md) |
| 文档工作方法 | 编写、内容检查、依据记录与交付建议 | [文档工作流](../source/workflows/document-writing.md) |

当前知识以光伏工艺与设备为起点，覆盖 TOPCon、PERC、HJT，以及管式扩散、氧化、LPCVD 和 PECVD。初始工艺参考来自 `KD\OEE_docs\kd` 的 **16 份 Markdown**，原文以快照形式保存在本项目中。

后续可继续纳入拉普拉斯的产品资料、设备说明、确认后的术语表、文档规范和典型案例。专业知识、公司规定、数据观察和工作建议分别保留来源及适用范围。

### 同一个概念，可以有多个名称

项目采用“概念 → 多个名称”的业务思路，既考虑英文缩写，也考虑中文简称和数据集中的代号。

| 概念 | 名称示例 | 来源与使用约定 |
|---|---|---|
| 硼扩散 | 硼扩、BK | 用户给出的业务约定 |
| PECVD | PE | 用户给出的业务约定；结合沉积工序语境解释 |
| 磷扩散 | PK | 用户给出的业务约定；读取具体数据集时核对字段说明 |

以上示例已接入名称查询，**具体条目与适用范围以 [glossary.json](../source/glossary.json) 为准**。`PK`、`OD` 等名称可能存在多义，需按[名称消歧流程](../source/workflows/name-disambiguation.md)核对上下文，仍不能判断时向用户确认。数据集代号保留厂区、设备、字段或文件范围；仅凭字母或拼音不能确认含义。

<a id="commands"></a>

## 使用方式与命令

### 接入 Agent 工作区

在项目根目录打开 Agent 会话，让它先读取 [AGENTS.md](../AGENTS.md)。Windows 下可运行以下命令建立本机技能发现入口：

```powershell
& .\source\tools\connect-skills.ps1
```

技能实体位于 `skills/`，`.agents/skills/` 是本机生成的目录联接，不随 Git 提交。没有自动发现时，可直接指定对应 `SKILL.md`。知识查询依赖本地 Python；Office 批量规范化还需要 Windows 和已安装的 Microsoft Office。

### 当前可用：基于知识库编写与修订文档

在本工作区工作时，可先让 Agent 读取 [AGENTS.md](../AGENTS.md)，再提出具体要求：

```text
参考本项目知识库，修订这份拉普拉斯设备技术说明。
统一专业术语、中文简称、英文缩写和计量单位，
检查重要参数与结论的依据，列出冲突及待确认事项。
沿用已有文档风格，并提供修改摘要。
```

也可以直接指定技能文件：

```text
使用 skills/kd-document-writing/SKILL.md，
为这份设备分析材料写一份技术说明，沿用原有术语与文档风格。
```

### 当前可用：模板、样式与公司 Logo 规范化

可以直接指定新技能与输入文件夹：

```text
使用 laplace-office-standardize，处理这个文件夹中的 Word、Excel、PPT。
按选定模板与样式配置统一格式，应用公司 Logo，保留原文件，
输出到新目录，并检查内容保真报告和 PDF 复核副本。
```

```powershell
# 检查本机 Office、配置、Logo 与模板；不启动 Office
python skills/laplace-office-standardize/scripts/office.py doctor

# 先查看批量处理计划，再另存规范化副本和 PDF
python skills/laplace-office-standardize/scripts/office.py apply "输入文件夹" --output "新的输出目录" --recursive --dry-run
python skills/laplace-office-standardize/scripts/office.py apply "输入文件夹" --output "新的输出目录" --recursive --pdf
```

旧版 `.doc/.xls/.ppt` 先转换为现代格式；加密、受保护、含宏/数字签名及外部数据连接文件使用专门保真流程。公司正式模板尚未提供时，处理报告保留 `approval_status=draft`。

### 使用本地命令查询

检索工具需要 **Python 3.10 或以上版本**，核心工具仅使用标准库，无需模型 API 或向量数据库。以下命令在项目根目录运行：

```powershell
# 定位相关知识与原文段落
python source/tools/kb.py search "硼扩散 炉管" --limit 5

# 查询英文缩写的全称、中文含义、用途和出处
python source/tools/kb.py abbr "LPCVD"

# 按类别查看，或输出供程序使用的 JSON
python source/tools/kb.py abbr --category testing --limit 10
python source/tools/kb.py abbr "PECVD" --json

# 查看实际可用的命令与选项
python source/tools/kb.py --help
```

`search` 返回文件、章节、行号和摘录；命中内容是定位线索，引用关键结论前仍应阅读原文上下文。索引缺失或过期时，可先用 `rg -n "关键词" source` 查找资料。

如果本机 `python` 指向 Windows 应用执行别名，可使用实际安装的 Python；本机已知解释器的调用示例见 [知识库使用说明](../source/README.md)。

<a id="structure"></a>

## 当前目录与职责

```text
KD/
├─ README.md                    项目价值、精选效果与快速开始
├─ AGENTS.md                    Agent 的项目工作约定与技能路由
├─ skills/                      当前六类工作流的实体目录
│  ├─ kd-context/
│  ├─ kd-data-analysis/
│  ├─ kd-document-writing/
│  ├─ kd-software-development/
│  ├─ kd-knowledge-maintenance/
│  └─ laplace-office-standardize/ 模板、Logo、批量处理脚本与保真约定
├─ .agents/skills/               指向 skills/ 的本地目录联接
├─ source/
│  ├─ README.md                 知识库详细导航与维护说明
│  ├─ references/kd/            原始工艺资料快照
│  ├─ knowledge/                工艺、设备、质量及冲突整理
│  ├─ evidence/                 数据集研究的证据摘录
│  ├─ workflows/                数据、文档和程序的工作建议
│  ├─ templates/                数据契约、报告和变更检查模板
│  ├─ glossary.json             术语与名称主表
│  ├─ catalog.json              文件、章节与哈希索引
│  ├─ manifest.json             原文来源与快照哈希清单
│  ├─ tools/                    本地检索、索引与校验工具
│  └─ tests/                    工具行为验证
└─ docs/
   ├─ usage.md                  Lapdex 用户手册
   ├─ maintenance.md            本指南：源码能力、使用命令与维护
   ├─ images/                   总览、流程与九张功能对比图
   ├─ examples/                 完整案例导航、实际回答、Office原稿与输出
   ├─ comparison-scenarios.json  功能图文与素材引用
   └─ tools/                    对比图生成与示例导出工具
```

| 需要准备的工作材料 | 可复用模板 |
|---|---|
| 文档中数据的含义、对象关系、时间与指标口径 | [数据契约](../source/templates/data-contract.yaml) |
| 分析输入、处理规则、结果和证据 | [分析报告](../source/templates/analysis-report.md) |
| 文档读者、用途、范围和交付要求 | [文档简报](../source/templates/document-brief.md) |
| 支撑程序变更的业务边界与验证依据 | [变更检查](../source/templates/change-checklist.md) |

<a id="roadmap"></a>

## 建设路线与维护

后续围绕“专业判断更贴近业务、重复工作更省事”推进。以下为建议路线，试点部门、首批任务与验收目标待结合实际使用需求确定。

| 下一步 | 具体工作 | 如何判断有效 |
|---|---|---|
| 补齐适用知识 | 接入现场确认的术语、字段说明、产品资料和正式模板 | 关键解释可追溯，版本与适用范围清楚 |
| 验证高频任务 | 选择一个使用团队，围绕真实任务验证查询、编写、检查和格式处理 | 记录达到同等交付质量所需的总人工时间与返工次数 |
| 扩展重复操作 | 将试点中稳定、反复出现的处理步骤沉淀为脚本与 skills | 可重复执行，有输入输出记录和检查结果 |

专业性评估关注业务含义是否正确、重要结论是否有依据；文档规范性评估关注模板与规则符合程度。效率评估包含提问、核对和修改输出的人工时间，现有对比案例不代表已取得统计意义上的准确率或工时收益。

### 当前建设基础

| 阶段 | 建设重点 | 状态 |
|---|---|---|
| 专业知识基础 | 工艺资料、术语、来源、冲突记录与本地检索 | 当前已有 |
| 文档内容规范 | 依托现有工作流编写、修订与检查；逐步形成公司规则和独立检查能力 | 已有基础，继续完善 |
| 公司模板与品牌资料 | 已保存用户提供的 Logo，随附 DOTX/XLTX/POTX 草案；继续接入正式公司模板 | 已有草案，待正式规范 |
| Office 标准化处理 | 原生模板接口、样式规范化、Logo、内容检查与复核副本 | 首版已实现 |
| 批量处理与交付检查 | 单文件/文件夹递归处理、另存副本、逐文件报告 | 首版已实现，复杂布局继续完善 |

新增知识时，先明确它属于原始资料、现场确认规则、数据观察还是工作建议，再放入对应位置。术语与名称从主表维护，重要条目附来源、版本、适用范围和确认状态。

常用的只读检查：

```powershell
python source/tools/kb.py index --check
python source/tools/kb.py verify
python -B -m unittest discover -s source/tests -v
```

修改可检索知识后，通过维护工作流更新索引；需要刷新原文时，再审阅差异并更新快照。[manifest.json](../source/manifest.json) 与 [catalog.json](../source/catalog.json) 各有职责：前者记录原始快照依据，后者记录当前可检索文件；重建索引不会重新签署原文哈希。

更多维护步骤与当前工具说明见 [知识库入口](../source/README.md) 和 [维护技能](../skills/kd-knowledge-maintenance/SKILL.md)。

### 内容与规范的维护原则

- **典型工艺值保留参考性质。** 文献温度、压力和周期不直接成为现场报警限、正式配方或判废线。
- **指标保留计算条件。** 光伏转换效率与设备 OEE 分别解释；OEE 需明确状态映射、计划时间、理想节拍和质量计数规则。
- **结论保留证据层次。** 原文事实、数据观察、分析推断、建议和待确认事项有清晰标记；相关性不能直接证明根因。
- **现场定义保留版本。** 已确认且适用的现场文件用于解释具体任务；与旧资料不同的地方记录差异和范围。
- **校验结果保留能力范围。** 文件哈希、索引和链接检查证明本地资料完整性，技术事实与生产适用性仍需相应证据。

公司模板、品牌素材和文档规则纳入后，同样记录版本、适用范围及确认状态。专业内容检查与格式检查共同服务于规范文档交付。

<a id="memory"></a>

### 私有记忆版本范围

Lapdex v0.1.0 尚未随附私有记忆工作流。跨对话保存与复用待后续版本接入、验证；当前会话约定不视为已持久保存。
