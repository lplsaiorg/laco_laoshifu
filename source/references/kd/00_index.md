# 光伏电池工艺知识库

## 概述

本知识库系统整理了晶硅太阳能电池从原料提纯到组件封装的全套制造工艺，涵盖传统工艺（Al-BSF）及先进技术（PERC、TOPCon、HJT），并扩展至钙钛矿新兴技术、电池测试表征和关键材料。内容来源：[PVEducation.org](https://www.pveducation.org/)、[PV-Manufacturing.org](https://pv-manufacturing.org/) 及 2024-2025 年学术文献与行业报告。

## 知识库目录

### 硅材料与基础工艺

| 文件 | 内容 |
|------|------|
| [01_silicon_purification.md](01_silicon_purification.md) | 硅原料提纯（冶金级→西门子法→太阳能级/电子级） |
| [02_crystal_growth.md](02_crystal_growth.md) | 晶体生长（直拉法CZ、区熔法FZ、多晶铸锭、大尺寸化） |
| [03_wafer_preparation.md](03_wafer_preparation.md) | 硅片制备（金刚线切割、损伤去除、制绒、RCA清洗） |
| [04_cell_processing_basics.md](04_cell_processing_basics.md) | 基础电池工艺（POCl₃扩散、SiNₓ ARC、烧结曲线） |

### 晶硅电池技术

| 文件 | 内容 |
|------|------|
| [05_screen_printed_cells.md](05_screen_printed_cells.md) | Al-BSF 丝网印刷电池完整工艺 |
| [06_perc_cells.md](06_perc_cells.md) | PERC：AlOₓ背面钝化、激光开口、LID与Ga掺杂 |
| [07_topcon_cells.md](07_topcon_cells.md) | TOPCon：SiOₓ/poly-Si、四大沉积路线、LECO、铜电镀降本（含27.79%记录） |
| [08_hjt_cells.md](08_hjt_cells.md) | HJT：a-Si:H/ITO/低温银浆、极低温度系数、叠层底电池 |
| [09_high_efficiency_cells.md](09_high_efficiency_cells.md) | PERL、激光埋栅（LGBC）、IBC 高效结构 |

### 新兴技术与系统

| 文件 | 内容 |
|------|------|
| [10_technology_comparison.md](10_technology_comparison.md) | 技术/性能/成本/市场全面对比与2030路线图 |
| [11_module_manufacturing.md](11_module_manufacturing.md) | 组件封装：焊接/叠层/层压/EVA/POE/双玻/EL测试 |
| [12_perovskite_cells.md](12_perovskite_cells.md) | 钙钛矿：ABX₃结构、p-i-n工艺、狭缝涂布、叠层34.5%+ |
| [13_cell_testing_characterization.md](13_cell_testing_characterization.md) | 测试表征：I-V/EQE/EL/PL/少子寿命/STC标准 |
| [14_key_materials.md](14_key_materials.md) | 关键材料：银浆/铝浆/EVA/POE/背板/焊带/CVD气体 |
| [15_tube_furnace_equipment.md](15_tube_furnace_equipment.md) | **管式热处理与沉积设备**：硼扩散炉/干氧氧化炉/LPCVD/PECVD 工艺参数与设备结构 |

## 电池工艺演进路径

```
多晶硅棒（西门子法提纯，9N+）
    ↓ CZ直拉 / FZ区熔 / 多晶铸锭
硅锭 → 金刚线切割 → 硅片（150~200 µm）
    ↓ 制绒 → 扩散 → 边缘隔离 → 钝化/ARC → 金属化 → 烧结 → 测试
    ↓ 技术分支
┌───────────┬──────────┬───────────┬──────────┐
│  Al-BSF   │   PERC   │  TOPCon   │   HJT    │
│ 传统/退出  │ AlOₓ背钝化│ SiOₓ/polySi│ a-Si:H叠层│
│  ~20%     │  ~22%    │  ~25.5%   │  ~26%+   │
└───────────┴──────────┴───────────┴──────────┘
    ↓ 组件封装
焊接（MBB/半片）→ 叠层 → 层压（EVA/POE）→ 装框 → 测试（EL/IV）→ 组件
    ↓ 下一代（研发/早期商业化）
钙钛矿/硅叠层（32.76%~34.5%，2025-2026）
```

## 关键效率指标（2025年）

| 技术 | 组件效率范围 | 温度系数 | 年衰减率 | 市场地位 |
|------|------------|--------|---------|---------|
| Al-BSF | ~19% | -0.45%/°C | ~0.6%/年 | 逐步退出 |
| PERC | 20.5%~22% | -0.34~-0.40%/°C | ~0.5%/年 | 成熟/产能收缩 |
| TOPCon | 21.5%~23.5% | -0.30~-0.32%/°C | ~0.4%/年 | 主流（占新增~70%+）单结记录27.79% |
| HJT | 21.5%~23.5% | -0.24~-0.27%/°C | ~0.3%/年 | 高端市场扩张 |

## 知识库统计

| 类别 | 文件数 | 主要覆盖 |
|------|------|---------|
| 硅材料与基础工艺 | 4 | 提纯→晶体→硅片→基础工艺 |
| 晶硅电池技术 | 5 | Al-BSF/PERC/TOPCon/HJT/高效结构 |
| 新兴技术与系统 | 5 | 技术对比/组件封装/钙钛矿/测试/材料 |
| **合计** | **15** | — |

## 参考来源

- [PVEducation.org](https://www.pveducation.org/pvcdrom/manufacturing-si-cells)
- [PV-Manufacturing.org](https://pv-manufacturing.org/)
- [EPJ Photovoltaics 2024-2025](https://www.epj-pv.org/)
- [PV Magazine 2025-2026](https://www.pv-magazine.com/)
- [Nature Reviews Clean Technology 2025](https://www.nature.com/nrct)
- ITRPV (International Technology Roadmap for Photovoltaics) 2022-2025
- 国金证券/东北证券光伏行业研究报告 2024-2025
