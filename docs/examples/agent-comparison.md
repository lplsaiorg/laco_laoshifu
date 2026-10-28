# 同一输入的实际回答示例

一侧按要求未读取本项目 skills、知识库或外网；另一侧读取相应 skill 和本地依据。由不同 Agent 完成的一次回答，输入保持一致。
以下保留完整原文。它们是可审阅案例，不是严格的模型 A/B 性能评测；没有重复试验、盲评或准确率统计。
部分问题两侧都给出正确或审慎的结论，图示如实保留这些一致点。

原始记录：[未使用项目 skill](baseline-answers.json) · [使用项目 skill](skill-answers.json)

<a id="knowledge"></a>

## 专业知识支持

**相同输入**

在光伏管式工艺中，用两句话区分BK与PE，并说明依据和不确定项。

**未使用本项目 skill：原始回答**

按光伏管式工艺的常见语境，BK通常指硼扩散，PE通常指等离子体增强化学气相沉积（PECVD），前者将硼引入硅片形成掺杂层，后者通过等离子体促进薄膜沉积。依据是行业命名习惯和工序机理，但这些缩写不能脱离数据源唯一解释，具体膜层、设备路线以及该项目中的命名仍需原文或字段说明确认。

**使用 kd-context：原始回答**

按本项目已确认的命名，BK指硼扩散，典型用途是通过热扩散形成硼掺杂发射极；PE指PECVD，即利用等离子体增强沉积薄膜，可用于减反射或钝化等不同膜层。依据是用户名称约定和《管式热处理与沉积设备》第1.1、4.1节，实际设备、膜种、工步与配方尚需核对，不能只凭代号确定温度或工艺限值。

**本例可见的差异**

本例两边均识别工序；skill 侧补充可查证的项目依据。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-context/SKILL.md)
- [user-aliases.json](../../source/evidence/user-aliases.json)
- [15_tube_furnace_equipment.md](../../source/references/kd/15_tube_furnace_equipment.md)

<a id="names"></a>

## 简称与上下文消歧

**相同输入**

Longji OD数据包含TubeID、BoatID、ZoneID、P1-P5、Homogen、Quality。这里OD指什么，ZoneID是温区吗？

**未使用本项目 skill：原始回答**

仅凭这些列无法唯一确定OD；它可能是光密度、外径等英文术语的缩写，也可能是企业内部工序或数据集代号，现有字段不足以支持选定其中一个。ZoneID字面上是区域编号，可能表示炉管温区，也可能表示取样位置或其他分区；需查看数据说明、典型取值及其与TubeID、P1-P5的对应关系。Homogen和Quality也不能单独作为温区解释的证据。

**使用 kd-context：原始回答**

依据Longji来源及这组字段，本次OD按方阻检测数据理解（上下文判断），原资料已明确采用这一名称；P1–P5是五个测点的方阻值。ZoneID是1–11号硅片检测位置，不是炉管加热温区；Longji建模资料将11个检测位置映射到6个温区，不能把两种编号直接等同。该解释限定于Longji数据，也不据此猜测OD的英文全称。

**本例可见的差异**

本地数据说明让回答从多种可能收敛到有依据的解释。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-context/SKILL.md)
- [dataset-other-aliases.json](../../source/evidence/dataset-other-aliases.json)
- [name-disambiguation.md](../../source/workflows/name-disambiguation.md)

<a id="data"></a>

## 数据口径核对

**相同输入**

日志字段tube,batch,time,temp,pressure,state,count，两条记录T1,B01,08:00,610,10,1,0和T1,B01,08:30,615,10,1,500。请计算OEE并判断是否超温。

**未使用本项目 skill：原始回答**

两点间隔30分钟，count由0增至500；若它是累计产量且期间未复位，可得产量增量500、平均产出1000计数单位/小时，这还不能得到OEE。缺少计划生产时间、运行及停机状态码含义、理论节拍和合格数，无法计算可用率、性能率与质量率；温度单位、测点、工序步骤及配方限也未提供，只能确认原值升高5，不能判断超温。

**使用 kd-data-analysis：原始回答**

现有数据不能确定OEE或是否超温。可先报告：两记录时刻相差30分钟，count原值增加500，温度原值由610升至615；这些不能直接认定为整批周期、良品产量或连续运行时长。OEE还需状态码映射、计划生产时间、理想节拍及合格数量口径；超温判断还需温度单位、测点、工步和适用配方限。state=1及行业典型温度都不能补出这些定义。

**本例可见的差异**

本例两边都不臆算 OEE；skill 侧补充批量设备的口径边界。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-data-analysis/SKILL.md)
- [data-analysis.md](../../source/workflows/data-analysis.md)
- [equipment.md](../../source/knowledge/equipment.md)
- [gaps-and-conflicts.md](../../source/knowledge/gaps-and-conflicts.md)

<a id="document"></a>

## 文档编写与修订

**相同输入**

拟写硼扩异常分析报告开头：批次B01，温度原值1020/1030，未提供单位、工序步骤、配方限。给出可审阅的简短结论。

**未使用本项目 skill：原始回答**

批次B01硼扩异常初步核查：现有资料记录温度原值1020和1030，两值相差10，但尚未提供单位、记录时序、测点、工序步骤及适用配方限。当前结论限于确认存在两条不同的温度记录，证据不足以认定超温、工艺失控或产品质量异常；需补齐原始记录与配方依据，再核对偏差及其影响。本结论为资料核查阶段意见，供审阅和补充证据。

**使用 kd-document-writing：原始回答**

批次B01记录了1020、1030两个温度原值，数值相差10，单位尚未提供。目前只能确认上述数据观察，不能据此认定硼扩超温，也没有证据建立温度与质量异常的因果关系。待核对温度单位、测点、工序步骤、配方版本及有效上下限后，再按对应工步复核。本结论为待核实的分析草稿，行业典型温度不作为本批次合格线。

**本例可见的差异**

两边都保留不确定性；skill 侧让依据与待确认写法更统一。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-document-writing/SKILL.md)
- [document-writing.md](../../source/workflows/document-writing.md)
- [equipment.md](../../source/knowledge/equipment.md)
- [gaps-and-conflicts.md](../../source/knowledge/gaps-and-conflicts.md)

<a id="software"></a>

## 程序业务规则实现

**相同输入**

设计设备pressure转Pa函数的输入输出规则，支持Pa/mbar/Torr和未知单位。只给规则和一个110 Torr样例。

**未使用本项目 skill：原始回答**

输入包含有限数值value与明确单位unit，另行保留绝压或表压类型；输出包含value_pa、status及原值原单位。可统一单位字符串的空白和大小写，Pa、mbar、Torr分别乘1、100、101325/760，计算时保留精度、展示时再舍入。未知或缺失单位返回value_pa=null及原因，禁止猜测单位；非数值或无穷值返回输入错误。样例：110 Torr→14665.46 Pa，压力类型保持不变。

**使用 kd-software-development：原始回答**

输入为有限数值、明确单位及可选压力基准；保留原值、原单位和绝压/表压/未知标记。Pa直接返回，mbar乘100，Torr乘101325/760；输出value_pa与状态。未知单位返回value_pa=null、status=unknown_unit，不猜单位或填零；无效数值单独报错。样例：110 Torr约为14665.46 Pa，原始110 Torr仍保留；单位换算不改变压力基准。

**本例可见的差异**

本例换算结果一致；skill 侧将失败状态落到项目契约。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-software-development/SKILL.md)
- [software-development.md](../../source/workflows/software-development.md)
- [data-analysis.md](../../source/workflows/data-analysis.md)
- [gaps-and-conflicts.md](../../source/knowledge/gaps-and-conflicts.md)

<a id="maintenance"></a>

## 知识与规范维护

**相同输入**

当前工作约定PK=磷扩散；一份800G历史文档写pk=退火。如何维护这两个解释？给精简规则。

**未使用本项目 skill：原始回答**

保留两个有范围的解释：当前工作约定中的PK=磷扩散；该800G历史文档中的pk=退火。分别记录适用项目或数据源、技术路线、版本或日期、原文位置及确认状态，不以大小写直接判定为不同概念，也不把任何一条推广为全局规则。查询时先按来源和版本匹配；上下文仍冲突则列出候选并确认。历史原文保留，不批量替换，后续修订通过版本和变更记录维护。

**使用 kd-knowledge-maintenance：原始回答**

分别保留两个概念与来源：当前PK=磷扩散标为user_confirmed，范围限定本次工作约定；历史pk=退火标为dataset_explicit，注明800G文档版本，并设auto_expand=false。保留原文与冲突备注，避免全局替换；解释该历史原句时按其标签说明，新来源仍不明确时再确认。名称维护在同一主表，更新后生成对照表并校验索引，不把局部命名升级为全厂工艺定义。

**本例可见的差异**

两边都保留范围；skill 侧给出项目字段和可执行维护步骤。

**使用侧的本地依据**

- [SKILL.md](../../skills/kd-knowledge-maintenance/SKILL.md)
- [user-aliases.json](../../source/evidence/user-aliases.json)
- [dataset-800g-aliases.json](../../source/evidence/dataset-800g-aliases.json)
- [glossary.json](../../source/glossary.json)
- [name-disambiguation.md](../../source/workflows/name-disambiguation.md)
