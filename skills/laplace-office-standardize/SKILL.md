---
name: laplace-office-standardize
description: 将拉普拉斯 Word、Excel、PPT 文件按选定模板与公司样式规范化并应用公司 Logo，支持单文件和文件夹批量处理；用于 .docx/.xlsx/.pptx 的版式与品牌统一，不用于仅询问工艺知识或改写业务结论。
---

# 拉普拉斯 Office 文档规范化

对选定文件的副本套用模板、统一样式并嵌入公司 Logo，交付规范化文件和处理报告。使用本目录 `scripts/office.py`；解析 `SKILL.md` 真实路径，避免目录联接影响资源定位。

## 选择模板与输入

- 默认配置：[company-profile.json](assets/company-profile.json)。内含本次提供的原始 Logo、DOTX/XLTX/POTX 路径、字体和版式参数；`approval_status=draft` 表示可审阅草案，不能称为已批准公司标准。
- 用户提供正式模板时，复制配置为新版本并更新相应模板路径、字体、页边距及 Logo 规则。保持模板来源、适用文档类型与确认状态；不要从公司名称推断未提供的品牌要求。
- 明确输入文件/文件夹和新输出目录。默认另存副本，脚本拒绝覆盖输入和已有输出。`.doc/.xls/.ppt` 等旧格式先用对应 Office 转换为现代格式；加密、受保护、含宏或数字签名的文件单独处理，不静默移除保护或宏。

## 执行

在项目根运行以下命令；Python 不可用时使用知识库入口记录的本机解释器。原生模板接口需要 Windows、Microsoft Word、Excel、PowerPoint 和 PowerShell；`doctor` 只检查依赖，不打开应用。

```powershell
python skills/laplace-office-standardize/scripts/office.py doctor
python skills/laplace-office-standardize/scripts/office.py apply "输入文件夹" --output "新的输出目录" --recursive --dry-run
python skills/laplace-office-standardize/scripts/office.py apply "输入文件夹" --output "新的输出目录" --recursive --pdf
```

使用其他配置时，在子命令前加 `--profile "配置路径"`。仅在用户要求建立模板或本套模板确实缺失时用 `templates`；生成文件保留草案状态。模板文件存在时不会被该命令覆盖。

按需阅读 [格式与保真约定](references/format-contract.md)，尤其是 Excel 表头行与 Logo 位置、PPT 画布和复杂对象的适用范围。脚本不重写专业正文，也不自动重算或修正业务指标；需要内容修订时另用文档知识工作流。

## 检查与交付

- 检查 `standardization-report.json`：逐文件的成功/失败、配置版本、内容保真检查、原文件/输出哈希、版式复核提示。失败文件不会以成功结果交付。
- `processed_needs_visual_review` 只表示原生处理及程序检查通过。打开输出或查看 `--pdf` 生成的复核副本，确认 Word 分页/表格、Excel 打印页与公式显示、PPT 的文字溢出和 Logo 遮挡；复杂图表、组合对象及嵌入对象重点查看。
- Logo 始终按比例使用原图；只替换本工具以 `LaplaceDocs.CompanyLogo` 标记的对象，重复处理不应叠加多个本工具 Logo。其他原有图片与品牌元素需按实际模板核对。
- 交付输出文件与必要的失败/复核清单，说明采用的是草案还是批准模板。只有实际完成视觉检查后，才表述为已检查版式。
