# Lapdex skill 插件

本分支将“拉普老师傅”的六类工作流、本地知识库、Office 工具和模板打包为一个独立的 `lapu-laoshifu` 技能目录。Lapdex 发现一个入口；业务工作流由入口按需读取。

适配原理、目录映射、加载器依据及维护流程见 [拉普老师傅适配 Lapdex 的设计与实施](lapdex-adaptation.md)。

适配依据是 Lapdex 官方 `2026.6993.738.0` 发布包中的 `lapdex-agent-skill-authoring` 和技能加载器：支持用户技能目录 `~/.lapdex/skills/`、YAML frontmatter 和 `SKILL.md`；扫描时跳过 `references/` 支持目录。本包采用用户技能安装方式，不需要修改 Lapdex 安装目录或内置技能。这里的“插件”指可分发的 skill 资源包，不是工具进程或 Connector。

## 获取与安装

本仓库 `dist/` 提供 `lapu-laoshifu-lapdex-0.1.0.zip` 及同名 `.zip.sha256`。ZIP 内保留顶层 `lapu-laoshifu/`：

```text
~/.lapdex/skills/lapu-laoshifu/
├─ SKILL.md
├─ bundle-manifest.json
└─ references/kd/
   ├─ AGENTS.md
   ├─ source/                    知识库、原文快照、词典、检索脚本及校验
   └─ skills/                    六类工作流及 Office 工具、Logo、模板
```

用系统解压工具将完整的顶层目录解压到 `~/.lapdex/skills/`，不要只复制 `SKILL.md`。Windows 默认路径为 `%USERPROFILE%\.lapdex\skills\lapu-laoshifu\`；如果设置了自定义技能目录，使用该目录。

也可以在仓库根目录用 Python 3.10+ 安装：

```powershell
python scripts/package_lapdex.py --check dist/lapu-laoshifu-lapdex-0.1.0.zip
python scripts/package_lapdex.py --install dist/lapu-laoshifu-lapdex-0.1.0.zip --dry-run
python scripts/package_lapdex.py --install dist/lapu-laoshifu-lapdex-0.1.0.zip
```

自定义技能目录时添加 `--skills-dir "目标技能目录"`。安装器校验归档完整性和路径后安装；目标目录存在时拒绝覆盖。用户可能已经在技能内维护了知识库，升级前应备份旧目录并审阅知识差异，再将旧目录另行保存后安装新包。

安装后等待技能缓存刷新（所核对版本约 30 秒），必要时重新打开 Lapdex，查看“技能与工具”中是否出现 `lapu-laoshifu` 并启用。若没有出现，先核对活动 profile、自定义技能目录、文件层级及 `SKILL.md` 是否完整，不要改写应用内置技能。

## 使用示例与运行条件

可以直接提出任务，也可以在提问中点名“拉普老师傅”或 `lapu-laoshifu`：

```text
用拉普老师傅查询硼扩散有哪些简称，说明出处和适用范围。
解释 Longji OD 数据的 ZoneID，先核对本地资料，拿不准的地方说明依据。
用拉普老师傅处理这份工艺说明，统一术语并保留待确认项。
按拉普拉斯模板规范化这个文件夹中的 Word、Excel、PPT，另存副本。
```

| 能力 | 运行条件 |
|---|---|
| 直接读取知识和工作流 | Lapdex 能读取本地技能资源 |
| `kb.py` 检索、简称查询、完整性校验 | Python 3.10+，仅标准库；不调用模型 API 或外部数据库 |
| Office 原生规范化 | Windows、Python 3.10+、PowerShell 和相应 Microsoft Office 应用 |
| Excel/Word/PPT 专业内容核对 | 按对应工作流使用本地知识和用户材料；复杂版式需要视觉复核 |

不依赖 Codex 插件、Codex 缓存中的 Python 或 `.agents/skills` 联接。原始资料清单中的旧机器路径保留为出处记录，脚本从自身安装位置定位本包资源。知识维护写在本地安装副本中，不会自动同步或推送回本仓库。

## 从源码重新打包

```powershell
python scripts/package_lapdex.py
python scripts/package_lapdex.py --check dist/lapu-laoshifu-lapdex-0.1.0.zip
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s source/tests -v
```

`--output "发布目录"` 可指定输出位置。默认不覆盖已有发行文件；明确需要重新生成同版本发行包时使用 `--force`。`--force` 只用于发行文件，不允许覆盖已安装的用户知识库。

打包入口模板为 `integrations/lapdex/SKILL.md`，构建时将它放到插件根。原有 `source/`、`skills/` 和 `AGENTS.md` 整体放入 `references/kd/`，保持原始字节与相对目录；不包含 `.git`、目录联接、本机配置、缓存和模型凭据。`bundle-manifest.json` 记录随包文件的大小和 SHA-256，用于检查内容损坏或打包遗漏，不是数字签名或发布者身份认证。

发布格式参考：[官方 AppInstaller](https://llm.laplace-tech.com:8087/lapdex-releases/releases/win32/stable/stable.appinstaller)。本次静态核对的发布包版本为 `2026.6993.738.0`，对应包内 `tools/skill_manager_tool.py`、`agent/skill_utils.py`、`tools/skills_tool.py`。上游发布地址会更新，不能据此宣称所有后续版本均已兼容。

## 验证范围

本分支验证打包、归档校验、安装到隔离目录、知识库检索及原始资料哈希。**尚未完成 Lapdex 实机加载与调用验证，也未在虚拟机执行 Office 规范化。** 自动发现、模型选择工作流和具体文件输出仍需使用者在自己的 Lapdex 版本中核对。

2026-11-02 的宿主机验证结果：

- 7 项打包/安装测试、27 项知识库测试通过；通用 skill frontmatter 校验通过。
- 从上述官方版本中抽取校验器和目录遍历函数，在隔离环境核对新技能格式，并确认安装后的目录只被发现为 1 个技能。没有启动 Lapdex 后端；这是函数级兼容检查。
- ZIP 安装到含中文和空格的新目录后，从无关工作目录运行 `verify`、`index --check`、`crosswalk --check`、简称查询及工艺检索通过。16 份原始快照保持 SHA-256；34 份索引文档及 75 个简称概念校验通过。
- `OD` 仍返回带范围的多个候选，没有因适配自动合并；独立工作流试读能按 Longji 来源区分检测位置与温区。
- Office `doctor` 读到草案配置及三类完整模板；未启动 Office，未将依赖检查计作版式验证。
