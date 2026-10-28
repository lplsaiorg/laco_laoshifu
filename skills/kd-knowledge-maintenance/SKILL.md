---
name: kd-knowledge-maintenance
description: 在用户要求更新 KD 本地知识库时导入资料、核对冲突，维护概念多简称、数据集代号、出处与索引；适用于 source 知识和 skills 路由维护，不因普通查询自动改写知识库。
---

# KD 知识库维护

使新增信息可检索、可追溯，并保留资料事实与现场约定之间的区别。

## 定位与判断变更范围

解析本 `SKILL.md` 的真实路径，逐级向上找同时含 `source/README.md` 与 `source/tools/kb.py` 的 KD 根目录。不要使用 `.agents/skills` 目录联接的表面层级推导路径。读取 [知识库入口](../../source/README.md)、可用的 `source/catalog.json` 和 [缺口与冲突](../../source/knowledge/gaps-and-conflicts.md)，确认用户要求更新的主题、来源和覆盖范围。

索引缺失、过期或工具不能运行时，先读 README 并用 `rg -n "关键词" source/references/kd source/knowledge source/workflows` 查证，再按本维护流程修复或重建索引；索引问题本身不构成刷新原文快照的理由。

一般分析任务产生的临时假设不自动升级为共享知识。现场状态表、数据库字段、配方或验收要求应附提供者/文件、版本、生效范围及确认状态；对缺失的元数据明确记为待确认。

一词多义按 [名称消歧流程](../../source/workflows/name-disambiguation.md) 先列候选，再结合本次适用的用户定义、工序设备、路径、字段邻列、单位、技术路线与版本判断；推断标“上下文推断”并附依据，不按频率、首条结果或拼音认定。仍多义、缺证据或冲突时必须列 2–3 候选或请求原句/来源确认，答复前不做依赖该含义的合并改名、计算与最终结论，继续独立检查。已有适用的明确用户定义不重复问，新来源不盲套旧定义。单次推断或确认不自动推广全库；用户要求入库时记录 scope、来源和版本，保留局部适用范围。

## 更新相应层次

- 原始资料保存在 `source/references/kd/`，不为解决摘要中的矛盾而悄悄改写原文。现有快照的变更需按工具约定显式更新，查看差异后再同步摘要；没有来源的结论不能伪装成原文内容。
- 用户明确要求从原始目录刷新快照时，在项目根运行 `python source/tools/kb.py snapshot --source "原始目录"`；已有文件变化时先审阅差异，再按工具帮助使用 `--update`。默认不删除历史快照；删除或移动应限于用户请求的明确范围。
- 领域解释写入 `source/knowledge/`，任务执行建议写入 `source/workflows/`；将待补数据字典、口径和原文矛盾记入 `gaps-and-conflicts.md`。保留各自性质，避免在多个文件复制一套数值表。
- 名称同源维护在 `source/glossary.json` 的概念主表，不另建重复词典。概念可有多个中文简称、英文缩写与数据集代号，不强制有英文缩写。保留 `aliases` 字符串兼容；`short_names` 每项记录 `name`、`kind`（`chinese_short|english_short|dataset_code|symbol`）、`status`（`user_confirmed|dataset_explicit|dataset_inferred|knowledge_explicit|curated`）、`scope`、`sources`，保留厂区/数据集/字段语境。数据集证据放 `source/evidence/` 并引用；推断候选不自动升级为确认同义词，局部证据不授予全厂规则。
- 英文缩写仍维护 `abbreviation`、`english_full_name`、`chinese_full_name`、`category`、`usage`、`notes`、`sources`，以 `full_name_status` 区分 `source_explicit` 与 `curated_translation`。同名简称分别说明上下文，不按 LP、TX 等拼音猜义；符号与化学式不强行展开。`knowledge/name-crosswalk.md` 从主表生成，禁止独立手改。模板不加入未确认的工厂默认值。
- 调整 skills 仅限于业务入口、触发条件或工作流确有变化时；保持相对知识路径和真实路径定位方式。不要因知识更新改变用户的其他 Agent 设置。

## 验证与交付

在项目根执行：

```powershell
python source/tools/kb.py crosswalk
python source/tools/kb.py index
python source/tools/kb.py verify
python source/tools/kb.py crosswalk --check
python source/tools/kb.py index --check
python source/tools/kb.py search "本次新增的术语" --limit 5
```

用真实新增词替换最后一条查询，并打开命中内容确认来源和语义。修改简称时，另用 `python source/tools/kb.py abbr "本次新增的简称" --json` 和概念全称分别查询，核对同概念多简称、确认状态、适用范围与出处；检查候选未自动参与同义词扩展。对照表与索引都是派生文件，先 `crosswalk` 再 `index/verify`，不能通过手改派生文件掩盖正文问题。若工具契约与上例不一致，先读 `python source/tools/kb.py --help` 和子命令帮助。

若改动技能且环境存在 `skill-creator` 的 `scripts/quick_validate.py`，验证实际改动的技能目录；不存在时至少核对 YAML frontmatter、名称、路径与触发边界。验证失败先修复本次变更造成的问题。

交付中列明更新的主题与来源、仍未解决的冲突和实际验证结果，不把本次导入时间当作原文发布日期。
