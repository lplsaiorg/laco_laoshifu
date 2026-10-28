# 常用简称与缩写对照表

由 `tools/kb.py crosswalk` 从 [glossary.json](../glossary.json) 生成，请维护主表后重新生成。

一行对应一个概念；中文简称、英文缩写、现场代码与指标符号可以共同指向它。
确认状态与适用范围属于每个名称，局部记录不代表全厂规则。候选及禁用自动展开的名称仅供查证，不作为自动同义替换。

用户明确确认的工作约定仅在其适用范围内优先。新数据来源的名称含义仍须核实，不能从拼音首字母或文件共现猜定。

同一简称可能对应多个中文概念。先按工序、设备、字段、单位、路径与版本推断并给出依据；仍不能判断时向用户确认，确认前暂停依赖该含义的处理。见[名称消歧工作流](../workflows/name-disambiguation.md)。

## 电池技术

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 铝背表面场 | Al-BSF<br>Aluminum Back Surface Field<br>整理补充 | — | Al-BSF：整理补充；KD光伏知识库的铝背表面场语境；非现场点位或状态码映射 | 原文给出铝背场中文与Al-BSF，英文全称为整理展开；Al为铝元素符号。 | [来源1](../references/kd/05_screen_printed_cells.md) |
| 本征薄层异质结 | HIT<br>Heterojunction with Intrinsic Thin-layer<br>原文明示 | — | HIT：知识资料明确；KD光伏知识库的本征薄层异质结语境；非现场点位或状态码映射 | 英文为08第1节明确展开，中文为对应译名；原文带商标标记。不是把所有HJT产品认定为同一品牌。 | [来源1](../references/kd/08_hjt_cells.md) |
| 异质结技术 | HJT<br>Heterojunction Technology<br>整理补充 | — | HJT：整理补充；KD光伏知识库的异质结技术语境；非现场点位或状态码映射 | 本条全称为整理采用的行业展开。08第1节将HJT写为Heterojunction with Intrinsic Thin-Layer，且同节把该展开用于HIT；保留原文并在此区分。旧HIT、SHJ别名仅为检索兼容，不表示字母全称相同。 | [来源1](../references/kd/08_hjt_cells.md) |
| 交指式背接触 | IBC<br>Interdigitated Back Contact<br>原文明示 | — | IBC：知识资料明确；KD光伏知识库的交指式背接触语境；非现场点位或状态码映射 | 描述接触布局，不应与HJT、TOPCon一律作为互斥路线。 | [来源1](../references/kd/09_high_efficiency_cells.md) |
| 钝化发射极背面电池 | PERC<br>Passivated Emitter and Rear Cell<br>原文明示 | — | PERC：知识资料明确；KD光伏知识库的钝化发射极背面电池语境；非现场点位或状态码映射 | 背面接触结构与TOPCon不同，工艺参数不可直接套用。 | [来源1](../references/kd/06_perc_cells.md) |
| 光伏 | PV<br>Photovoltaic<br>整理补充 | — | PV：整理补充；KD光伏知识库的光伏语境；非现场点位或状态码映射 | 英文全称为整理展开；属于行业概念，不代表本厂产品或组织定义。控制系统语境中的PV也可能指过程值，须由数据字典确认。 | [来源1](../references/kd/11_module_manufacturing.md) |
| 硅异质结 | SHJ<br>Silicon Heterojunction<br>整理补充 | — | SHJ：整理补充；KD光伏知识库的硅异质结语境；非现场点位或状态码映射 | 英文全称为整理展开；与HJT属于相关技术语境，但SHJ、HJT、HIT各自字母展开不同。 | [来源1](../references/kd/08_hjt_cells.md) |
| 隧穿氧化钝化接触 | TOPCon<br>Tunnel Oxide Passivated Contact<br>原文明示 | — | TOPCon：知识资料明确；KD光伏知识库的隧穿氧化钝化接触语境；非现场点位或状态码映射 | 属于电池技术/接触结构，不等于某一唯一配方或设备。 | [来源1](../references/kd/07_topcon_cells.md) |

## 设备

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 射频 | RF<br>Radio Frequency<br>整理补充 | — | RF：整理补充；KD光伏知识库的射频语境；非现场点位或状态码映射 | 英文全称为整理展开；RF不是功率单位，也不等于所有设备均固定13.56 MHz。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| 右舟编号 | — | RBoatId | RBoatId：数据集明确；810 ZP/BP配方执行记录的右舟，不是另一台独立设备 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 左舟编号 | — | LBoatId | LBoatId：数据集明确；810 ZP/BP配方执行记录的左舟，不是另一台独立设备 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 温度设定值 | — | SV | SV：数据集明确；Longji特征说明中恒温/氧化/扩散沉积子阶段的温度设定值；不推断所有SV列相同 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 炉管温区编号 | — | wenqu | wenqu：数据集明确；Longji清洗建模结果的6个温区编号；由11个OD检测位置加权映射，不与ZoneID等值 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 炉管编号 | — | TubeID、tube_id | TubeID：数据集明确；Longji OD原始表的炉管编号1–6；不自动跨MES/物理管号体系转换<br>tube_id：数据集明确；Longji文件名解析得到的炉管编号，解析自Tube{tube_id} | — | [来源1](../evidence/dataset-other-aliases.json) |
| 舟编号 | — | BoatID、boat_id、舟号 | BoatID：数据集明确；Longji OD表的舟编号；是可复用载具编号，不是批次号<br>boat_id：数据集明确；Longji文件名解析字段，来源为文件名BoatID部分<br>舟号：数据集明确；810过程表的载具编号；不删除业务前缀或前导零 | — | [来源1](../evidence/dataset-other-aliases.json) |

## 工艺

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 原子层沉积 | ALD<br>Atomic Layer Deposition<br>整理补充 | — | ALD：整理补充；KD光伏知识库的原子层沉积语境；非现场点位或状态码映射 | 英文全称为整理展开；不能仅由ALD缩写推定前驱体、温度或膜厚。 | [来源1](../references/kd/06_perc_cells.md) |
| BP工序（数据集标识） | — | BP、bp | BP：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线<br>bp：数据集明确；Peip_Trace的bp_*字段前缀 | 仅确认BP属于资料所述镀膜设备记录；未找到BP=背镀/背钝的直接说明，不能按字母猜正背面。BP与ZP是不同工序代码，不能当作彼此可替换的同义词。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 化学气相沉积 | CVD<br>Chemical Vapor Deposition<br>整理补充 | — | CVD：整理补充；KD光伏知识库的化学气相沉积语境；非现场点位或状态码映射 | 英文全称为整理展开；不能由CVD推定低压、等离子体或某一具体膜种。 | [来源1](../references/kd/04_cell_processing_basics.md) |
| 激光局部开口 | LCO<br>Laser Contact Opening<br>原文明示 | — | LCO：知识资料明确；KD光伏知识库的激光局部开口语境；非现场点位或状态码映射 | 与SE、LECO分别编码；文献开口率不是本厂默认规格。 | [来源1](../references/kd/06_perc_cells.md) |
| 激光增强接触优化 | LECO<br>Laser Enhanced Contact Optimization<br>原文明示 | — | LECO：知识资料明确；KD光伏知识库的激光增强接触优化语境；非现场点位或状态码映射 | 与SE激光掺杂及PERC的LCO激光开口不是同一工序。 | [来源1](../references/kd/07_topcon_cells.md) |
| 低压化学气相沉积 | LPCVD<br>Low-Pressure Chemical Vapor Deposition<br>原文明示 | — | LPCVD：知识资料明确；KD光伏知识库的低压化学气相沉积语境；非现场点位或状态码映射 | 工艺名也常用于设备简称；氧化与沉积步骤的温压条件分别记录。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| LP工序（数据集标识） | — | LP、lp | LP：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线<br>lp：数据集明确；Peip_Trace的lp_*字段前缀 | 该组资料明确工序标识和LP-01来源，但未直接展开LP=LPCVD。方案L520把LP异常关联到poly-Si厚度/掺杂，只能作为工艺背景佐证，不能单凭该机理认定同义。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 多主栅 | MBB<br>Multi Busbar<br>原文明示 | — | MBB：知识资料明确；KD光伏知识库的多主栅语境；非现场点位或状态码映射 | 不由MBB缩写推定主栅数量；主栅与细栅、焊带分别识别。 | [来源1](../references/kd/11_module_manufacturing.md) |
| 等离子体增强化学气相沉积 | PECVD<br>Plasma-Enhanced Chemical Vapor Deposition<br>整理补充 | PE | PECVD：整理补充；KD光伏知识库的等离子体增强化学气相沉积语境；非现场点位或状态码映射<br>PE：用户确认；KD本次用户明确的工作语境；不自动推广为全部工厂或历史数据定义 | 15原文展开为Plasma-Enhanced CVD；本条补全CVD。管式、板式及HJT用途不能套用同一温度。 | [来源1](../references/kd/15_tube_furnace_equipment.md) / [来源2](../evidence/user-aliases.json) |
| 物理气相沉积 | PVD<br>Physical Vapor Deposition<br>整理补充 | — | PVD：整理补充；KD光伏知识库的物理气相沉积语境；非现场点位或状态码映射 | 英文全称为整理展开；磁控溅射是PVD方法之一，不是所有PVD的同义工艺。 | [来源1](../references/kd/08_hjt_cells.md) |
| 选择性发射极 | SE<br>Selective Emitter<br>整理补充 | — | SE：整理补充；KD光伏知识库的选择性发射极语境；非现场点位或状态码映射 | 英文全称为整理展开；不能把不同区域方阻合成为单一验收阈值。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| ZP工序（数据集标识） | — | ZP、zp | ZP：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线<br>zp：数据集明确；Peip_Trace的zp_*字段前缀 | 仅确认ZP属于资料所述镀膜设备记录；未找到ZP=正镀/正钝的直接说明。不能因其文件名包含Coating就认定特定PECVD材料或正背面。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 一次工艺执行 | — | Run | Run：数据集明确；810工艺执行文件及Longji过程数据中的运行序号/一次执行；不等同舟编号或全局唯一批次号 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 工艺运行记录 | — | PR、report_* | PR：数据集明确；仅限Longji工艺时序记录；不擅自补写Process Record等英文展开<br>report_*：数据集明确；仅限Shangrao每个Run的工艺时序表名前缀，不是通用PR文件格式 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 氧化 | — | YH、yh | YH：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线<br>yh：数据集明确；Peip_Trace的yh_*字段前缀 | OX-01是该数据源目录/设备标识。资料直接支持YH与氧化有关，不据此推定该站一定采用干氧、湿氧或某一固定配方。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 硼扩散 | — | 硼扩、BK、bk | 硼扩：用户确认；KD本次用户明确的工作语境；不自动推广为全部工厂或历史数据定义<br>BK：用户确认；KD本次用户明确的工作语境；不自动推广为全部工厂或历史数据定义<br>BK：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线<br>bk：数据集明确；Peip_Trace的bk_*字段前缀 | RB01在该资料中是源设备目录，不能作为全行业硼扩散的通用同义词。中文简称“硼扩”和BK的当前工作约定另有用户直接定义，本文件仅记录dataset证据。 | [来源1](../references/kd/15_tube_furnace_equipment.md) / [来源2](../evidence/user-aliases.json) / [来源3](../evidence/dataset-800g-aliases.json) |
| 磷扩散 | — | PK、磷扩 | PK：用户确认；KD本次用户明确的工作语境；不自动推广为全部工厂或历史数据定义<br>磷扩：整理补充；KD当前磷扩散工序的中文简称；整理补充，不代表所有外部数据集命名 | 当前用户明确PK指磷扩散。800G旧方案曾写pk为退火，历史标签另列且禁止自动展开；不得用旧资料否定本次已确认的工作命名。 | [来源1](../evidence/user-aliases.json) / [来源2](../references/kd/04_cell_processing_basics.md) |
| 退火（800G旧文档标签） | — | pk | pk：数据集明确；仅限2026-08-18 FDC方案18.1的原文命名；不自动展开 | 用户本次明确“磷扩散=PK”，“磷扩”为整理补充；此条只保留历史文档的冲突证据，不应将PK合并为通用“退火”别名，也不能用旧文档覆盖用户当前工作定义。需以后续工艺/数据字典确认实际站点语义。<br>已确认的当前用户命名PK=磷扩散优先；旧文档的pk=退火仍作为历史证据保留，auto_expand=false，不能据此自动替换当前PK。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 配方名称 | — | RecipeName、Recipe | RecipeName：数据集明确；仅限810 ZP/BP配方记录表的名称列；名称不等于完整配方版本<br>Recipe：数据集明确；Longji过程文件名中的配方名称部分 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 配方执行开始时间 | — | BeginTime | BeginTime：数据集明确；810 ZP/BP RecipeRecord1–6的执行开始时间；不与文件名结束时间混用 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 配方执行结束时间 | — | EndTime | EndTime：数据集明确；810 ZP/BP RecipeRecord1–6的执行结束时间 | — | [来源1](../evidence/dataset-other-aliases.json) |

## 测试表征

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 自动光学检测 | AOI<br>Automated Optical Inspection<br>整理补充 | — | AOI：整理补充；KD光伏知识库的自动光学检测语境；非现场点位或状态码映射 | 英文与标准中文为整理补充。13第10节标题将AOI用于较广的在线检测列表，其中四探针、I-V等不能一律归为光学检测。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 电致发光 | EL<br>Electroluminescence<br>原文明示 | — | EL：知识资料明确；KD光伏知识库的电致发光语境；非现场点位或状态码映射 | 原文在成像章节写Electroluminescence Imaging；EL本身指电致发光，图像特征不是独立判废规则。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 外量子效率 | EQE<br>External Quantum Efficiency<br>原文明示 | — | EQE：知识资料明确；KD光伏知识库的外量子效率语境；非现场点位或状态码映射 | 随波长变化的量子效率不等于电池整体转换效率。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 电流-电压 | I-V<br>Current-Voltage<br>整理补充 | — | I-V：整理补充；KD光伏知识库的电流-电压语境；非现场点位或状态码映射 | IV为兼容写法；光照/暗态和电池/组件分别标注，英文展开为整理补充。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 内量子效率 | IQE<br>Internal Quantum Efficiency<br>整理补充 | — | IQE：整理补充；KD光伏知识库的内量子效率语境；非现场点位或状态码映射 | 英文全称为整理展开；使用原文简式时需确认其适用条件与反射率定义。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 光致发光 | PL<br>Photoluminescence<br>原文明示 | — | PL：知识资料明确；KD光伏知识库的光致发光语境；非现场点位或状态码映射 | 原文在成像章节写Photoluminescence Imaging；PL与EL激励方式不同，亮度不能直接合并。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 标准测试条件 | STC<br>Standard Test Conditions<br>原文明示 | — | STC：知识资料明确；KD光伏知识库的标准测试条件语境；非现场点位或状态码映射 | 指标列名不能证明实际测试已满足STC；STC温度是电池温度。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 五个测点的方阻值 | — | P1~P5 | P1~P5：数据集明确；Longji OD中5个测量点方阻值；不能因810也有P/Vd就把所有同名列物理定义视为已确认 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 故障检测与分类 | — | FDC、故障检测与诊断 | FDC：数据集明确；800G FDC应用方案的项目定义<br>故障检测与诊断：数据集明确；该方案标题采用的中文工作称谓 | 英文明确展开为Fault Detection and Classification，标题中文采用故障检测与诊断，属于同一项目的工作称谓，不表示Classification与Diagnosis字面同义。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 方阻检测数据 | — | OD、方阻检测 | OD：数据集明确；仅限Longji原始/清洗数据及810相应检测目录；不据此推断英文全称或其他OD含义；不自动展开<br>方阻检测：数据集明确；Longji扩散炉检测数据中的中文称呼 | OD在本知识库中同时出现方阻检测与膜厚检测语境，本条仅在所述数据源适用，不自动做全局同义展开；查询时应并列显示多个语境。 | [来源1](../evidence/dataset-other-aliases.json) |
| 测试 | — | cs | cs：数据集明确；800G本地分析资料与Peip_Trace工序字段族；不推广到其他产线 | cs为该方案中的测试工序/测试机语境；不自行扩展为特定测试设备品牌。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 硅片检测位置编号 | — | ZoneID | ZoneID：数据集明确；Longji OD中1–11号检测位置；不是炉管6个加热温区编号 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 膜厚检测数据 | — | OD | OD：数据集明确；800G LP后中间质检数据；不自动展开 | 这里确认OD数据的用途，未找到OD字母的英文全称，不猜Optical Density、Optical Detection或其他展开；OD也不是膜厚数值本身。<br>OD在本知识库中同时出现方阻检测与膜厚检测语境，本条仅在所述数据源适用，不自动做全局同义展开；查询时应并列显示多个语境。 | [来源1](../evidence/dataset-800g-aliases.json) |

## 材料

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 减反射涂层 | ARC<br>Anti-Reflection Coating<br>原文明示 | — | ARC：知识资料明确；KD光伏知识库的减反射涂层语境；非现场点位或状态码映射 | 是功能性膜层称谓，不限定材料，也不能据此推定实际膜种。 | [来源1](../references/kd/04_cell_processing_basics.md) |
| 硼硅玻璃 | BSG<br>Borosilicate Glass<br>原文明示 | — | BSG：知识资料明确；KD光伏知识库的硼硅玻璃语境；非现场点位或状态码映射 | 与PSG不同；保护作用和去除条件取决于实际工艺路线。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| 乙烯-醋酸乙烯酯共聚物 | EVA<br>Ethylene-Vinyl Acetate<br>整理补充 | — | EVA：整理补充；KD光伏知识库的乙烯-醋酸乙烯酯共聚物语境；非现场点位或状态码映射 | 英文全称及共聚物表述为整理展开；具体胶膜牌号和层压窗口须有实际材料规范。 | [来源1](../references/kd/14_key_materials.md) |
| 氧化铟锡 | ITO<br>Indium Tin Oxide<br>整理补充 | — | ITO：整理补充；KD光伏知识库的氧化铟锡语境；非现场点位或状态码映射 | 英文全称为整理展开；不能将ITO膜厚套用于全部TCO材料。 | [来源1](../references/kd/08_hjt_cells.md) |
| 聚烯烃弹性体 | POE<br>Polyolefin Elastomer<br>整理补充 | — | POE：整理补充；KD光伏知识库的聚烯烃弹性体语境；非现场点位或状态码映射 | 英文全称为整理展开；材料类别不代表具体牌号、配方或验收标准。 | [来源1](../references/kd/14_key_materials.md) |
| 磷硅玻璃 | PSG<br>Phosphosilicate Glass<br>整理补充 | — | PSG：整理补充；KD光伏知识库的磷硅玻璃语境；非现场点位或状态码映射 | 原文明确中文名称，英文全称为整理展开；不与BSG合并。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| 透明导电氧化物 | TCO<br>Transparent Conductive Oxide<br>整理补充 | — | TCO：整理补充；KD光伏知识库的透明导电氧化物语境；非现场点位或状态码映射 | 英文全称为整理展开；ITO是TCO的一种，TCO不等于ITO。 | [来源1](../references/kd/08_hjt_cells.md) |

## 指标

| 概念 | 标准英文缩写/符号 | 中文简称/现场代号等 | 名称范围与确认状态 | 注意事项 | 出处 |
|---|---|---|---|---|---|
| 填充因子 | FF<br>Fill Factor<br>整理补充 | ff | FF：整理补充；KD光伏知识库的填充因子语境；非现场点位或状态码映射<br>FF：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>ff：数据集明确；800G Peip_Trace成品电性能字段/显示标签 | 英文全称为整理展开；0.83与83%必须明确表达形式。<br>本分析资料明确eta/ff为百分数，不推广到别的文件或系统。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |
| 短路电流 | Isc<br>Short-Circuit Current<br>整理补充 | ISC、isc | Isc：整理补充；KD光伏知识库的短路电流语境；非现场点位或状态码映射<br>ISC：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>isc：数据集明确；800G Peip_Trace成品电性能字段/显示标签 | 英文全称为整理展开；不可与电流密度Jsc混用。<br>ISC与Jsc不同；字段单位和电池面积不可由代号自动推定。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |
| 复合电流密度 | J0<br>Recombination Current Density<br>整理补充 | — | J0：整理补充；KD光伏知识库的复合电流密度语境；非现场点位或状态码映射 | J₀是物理量符号，非首字母缩写；本条英文为语境译名。不同文献也以J₀描述饱和电流密度，应核对模型，且不等于总电流I₀。 | [来源1](../references/kd/15_tube_furnace_equipment.md) |
| 短路电流密度 | Jsc<br>Short-Circuit Current Density<br>整理补充 | jsc | Jsc：整理补充；KD光伏知识库的短路电流密度语境；非现场点位或状态码映射<br>jsc：数据集明确；800G Peip_Trace产品电性能字段 | 英文全称为整理展开；与Isc换算须明确面积及A、mA单位。<br>电流指标表按顺序给出jsc=短路电流密度；不能与isc混用。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |
| 最大功率点 | MPP<br>Maximum Power Point<br>整理补充 | — | MPP：整理补充；KD光伏知识库的最大功率点语境；非现场点位或状态码映射 | 英文全称为整理展开；MPP为工作点，Pmax为该点的功率值，不能混为同一物理量。 | [来源1](../references/kd/13_cell_testing_characterization.md) |
| 设备综合效率 | OEE<br>Overall Equipment Effectiveness<br>整理补充 | — | OEE：整理补充；KD光伏知识库的设备综合效率语境；非现场点位或状态码映射 | 行业常用概念与英文展开，不是已确认的本厂公式。现场状态映射、计划时间、理想节拍、质量计数及聚合规则仍须确认；不等于光伏转换效率。 | [来源1](../workflows/data-analysis.md) |
| 最大功率 | Pmax<br>Maximum Power<br>整理补充 | pmpp | Pmax：整理补充；KD光伏知识库的最大功率语境；非现场点位或状态码映射<br>pmpp：数据集明确；800G Peip_Trace产品电性能字段 | 英文全称为整理展开；Pmax=Imp×Vmp，不能以Voc×Isc替代。<br>pmpp为本数据集最大输出功率字段，对应知识库Pmax语境；与MPP工作点不同。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |
| Rs | — | rser、Rs | rser：数据集明确；800G Peip_Trace产品电性能字段<br>Rs：知识资料明确；原始电池测试资料的I-V指标语境；实际单位及器件层级另行核对 | rser为本数据集字段，知识库常用符号Rs；电阻与面积归一电阻不可直接互换。 | [来源1](../evidence/dataset-800g-aliases.json) / [来源2](../references/kd/13_cell_testing_characterization.md) |
| Rsh | — | RSHUNT、rshunt、Rsh | RSHUNT：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>rshunt：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>Rsh：知识资料明确；原始电池测试资料的I-V指标语境；实际单位及器件层级另行核对 | 与知识库Rsh为同一类电阻量，但Ω或Ω·cm²及归一方式须确认。 | [来源1](../evidence/dataset-800g-aliases.json) / [来源2](../references/kd/13_cell_testing_characterization.md) |
| 开路电压 | Voc<br>Open-Circuit Voltage<br>整理补充 | VOC、voc | Voc：整理补充；KD光伏知识库的开路电压语境；非现场点位或状态码映射<br>VOC：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>voc：数据集明确；800G Peip_Trace成品电性能字段/显示标签 | 英文全称为整理展开；V与mV、单片与组件分别标注。<br>与知识库Voc属于相同指标的大小写变体；具体电压单位须读原始数据字典。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |
| 反向电流测量1（数据集字段） | — | irev1 | irev1：数据集明确；800G Peip_Trace产品电性能字段 | 两项均属反向电流指标，但1/2的测量电压、条件和差异未在该表说明，不能互为同一测量值。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 反向电流测量2（数据集字段） | — | irev2 | irev2：数据集明确；800G Peip_Trace产品电性能字段 | 两项均属反向电流指标，但1/2的测量电压、条件和差异未在该表说明，不能互为同一测量值。 | [来源1](../evidence/dataset-800g-aliases.json) |
| 方阻中位数 | — | rs_median | rs_median：数据集明确；Longji每条OD记录P1–P5的中位数，不是原Average字段 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 最大功率点电压 | — | umpp、Vmp | umpp：数据集明确；800G Peip_Trace产品电性能字段<br>Vmp：知识资料明确；原始电池测试资料的I-V指标语境；实际单位及器件层级另行核对 | U与V均可作电压符号；umpp是本数据集字段，不能仅按字符相似度与其他系统字段合并。 | [来源1](../evidence/dataset-800g-aliases.json) / [来源2](../references/kd/13_cell_testing_characterization.md) |
| 最大功率点电流 | — | impp、Imp | impp：数据集明确；800G Peip_Trace产品电性能字段<br>Imp：知识资料明确；原始电池测试资料的I-V指标语境；实际单位及器件层级另行核对 | 由字段表的有序列举对应；与知识库Imp为同一指标语境，实际单位待确认。 | [来源1](../evidence/dataset-800g-aliases.json) / [来源2](../references/kd/13_cell_testing_characterization.md) |
| 检测均匀性 | — | Homogen、Homogeneity | Homogen：数据集明确；Longji OD为(Max-Min)/Average；810 PK为原始比例，需保留数据源口径<br>Homogeneity：数据集明确；810 BK均匀性字段为百分数字符串；当前分析除以100，同概念不同表示不能原值直接合并 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 温区级加权方阻 | — | rs_wenqu | rs_wenqu：数据集明确；Longji/Shangrao清洗结果的温区级加权标签，非原始温区传感器测量 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 温度跟踪积分误差特征 | — | IAE | IAE：数据集明确；Longji恒温特征中的积分误差；英文全称和时间积分实现需另外看实际公式，不能只按简称赋单位 | — | [来源1](../evidence/dataset-other-aliases.json) |
| 转换效率 | — | ETA、eta、η | ETA：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>eta：数据集明确；800G Peip_Trace成品电性能字段/显示标签<br>η：知识资料明确；原始电池测试资料的I-V指标语境；实际单位及器件层级另行核对 | ETA为效率字段/显示代号，不是另行创造的英文首字母展开；同资料说明eta/ff使用百分数，见model第63行。不能从本数据集推定所有外部效率字段均为百分数。 | [来源1](../references/kd/13_cell_testing_characterization.md) / [来源2](../evidence/dataset-800g-aliases.json) |

## 查证方式

```powershell
python source/tools/kb.py abbr "硼扩散"
python source/tools/kb.py abbr "BK" --json
python source/tools/kb.py abbr "PE"
python source/tools/kb.py abbr "PK"
```

来源中的证据摘录保留数据集相对路径与行号；原始数据集保持只读，不纳入本表复制。
