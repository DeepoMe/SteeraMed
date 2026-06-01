# SteeraMed Core

[English](README.md) | [中文](README.zh-CN.md)

[![PyPI](https://img.shields.io/badge/steeramed--core-0.1.0-blue)](https://pypi.org/project/steeramed-core/)
[![Python](https://img.shields.io/badge/python-3.9+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Preprint](https://img.shields.io/badge/preprint-2025-orange)](https://doi.org/10.20944/preprints202605.1578.v1)

**SteeraMed：可驭生物医学世界模型** — 基于 DNA 甲基化数据的个体化干预证据链，面向长寿、衰老和慢性疾病。

> 选择患者案例 → 30 秒生成个体化药物证据。
> [SteeraMed.com](https://steeramed.com) · [论文](https://doi.org/10.20944/preprints202605.1578.v1)

## 什么是生物医学世界模型？

传统系统生物学：
- 群体统计 → 平均效应 → 通用指南
- "这个药对群体有效吗？"

可驭生物医学世界模型 (SBWM)：
- 个体扰动 → 匹配 PPI 模块 → 个体化证据链
- "这个药对**你**有效吗？"

核心区别：
| | 系统生物学 | 可驭生物医学世界模型 |
|---|---|---|
| 分析单位 | 群体 | 个体 (N-of-1) |
| 核心问题 | 群体均值 | 个人匹配 |
| 输出 | 通用指南 | 四层证据链 |
| 药物排名 | 临床试验 | SA 对齐 + Bootstrap |

## 四层证据链

```
Layer 1: PPI 模块扰动      ← "你的生物学有什么不同？"
Layer 2: 化合物 SA 对齐    ← "哪些化合物可以纠正？"
Layer 3: 机制注释          ← "为什么这个化合物有效？"
Layer 4: Bootstrap 置信度  ← "这个结果有多可靠？"
```

## 快速开始

```bash
pip install steeramed-core
python -m steeramed_core
```

交互式案例选择器：

```
🧬 SteeraMed Core — N-of-1 证据链浏览器
═════════════════════════════════════════════════════

选择患者案例：
  [1] 🧓 衰老 · 群体筛查
  [2] 🧑 类风湿关节炎 · 51岁男 · T细胞扰动
  [3] 🧑 抑郁症 · 52岁男 · 先天免疫

输入选择 [1-3]: 2

✅ 已生成 4 张图表到 results/：
  📊 hallmark_bar.png      — Hallmark 扰动画像
  💊 drug_ranking.png       — Top-10 化合物排名
  🔗 evidence_network.png  — 药物-PPI-Hallmark 对齐
  📋 patient_card.png       — 单页患者摘要
```

批量模式：

```bash
python -m steeramed_core --all          # 所有案例
python -m steeramed_core --case ra_303  # 指定案例
python -m steeramed_core --list         # 列出可用案例
```

## Patient View 展示

**衰老 Patient View** — 群体级筛查（GSE40279，473 老年 vs 青年）。三面板卡片展示扰动的衰老 hallmarks、Top-10 化合物排名（烟酸 #1）和 Bootstrap 置信度：

![衰老 Patient View](docs/fig4_aging_patient.png)

**抑郁症 Patient View** — N-of-1 案例：52 岁男性（GSE128235）。先天免疫主导的扰动画像，肌酸排名第一：

![抑郁症 Patient View](docs/fig_s2_dep_patient.png)

<details>
<summary>更多图表</summary>

**科学家视图 — RA 证据链**（GSE42861，51 岁）：

![RA 证据链](docs/fig6_ra_evidence.png)

**Patient View — RA**（GSE42861，51 岁）：

![RA Patient View](docs/fig7_ra_patient.png)

**科学家视图 — 抑郁症证据链**（GSE128235，52 岁）：

![抑郁症证据链](docs/fig8_dep_evidence.png)

**科学家视图 — 衰老证据链**（GSE40279）：

![衰老证据链](docs/fig_s1_aging_evidence.png)

**Hallmark 扰动柱状图**（衰老）：

![Hallmark 扰动](docs/aging_hallmark_bar.png)

</details>

## 可用案例

| 案例 | 疾病 | 关键发现 | 证据等级 |
|------|------|---------|---------|
| 衰老 · 群体 | GSE40279 | 烟酸 #1，2/5 衰老保护剂 | MODERATE |
| RA · 51岁男 | GSE42861 | 6/10 已知 RA 药物，己酮可可碱 #1 | STRONG |
| 抑郁症 · 52岁男 | GSE128235 | 肌酸 #1，先天免疫通路 | EXPLORATORY |

## API

```python
import json
from pathlib import Path
from steeramed_core.viz.patient_card import plot_patient_card
from steeramed_core.viz.drug_ranking import plot_drug_ranking

p = Path(__file__).parent / "steeramed_core" / "presets" / "example_patients"
data = json.loads((p / "ra_patient_303.json").read_text(encoding="utf-8"))
fig = plot_patient_card(data)
fig.savefig("my_patient_card.png", dpi=300)
```

## 数据来源与致谢

本包包含来自以下开放数据库的预计算结果。衷心感谢原始数据提供者：

- **PPI 网络**: STRING v12.5 — Szklarczyk et al., *Nucleic Acids Res* 53(D1), 2025. [CC BY 4.0](https://string-db.org/cgi/access?footer_active_subpage=licensing)
- **化合物-靶点互作**: STITCH — Kuhn et al., *Nucleic Acids Res* 36(Database), 2008. [CC BY-NC](http://stitch-db.org) — **本包仅将 STITCH 衍生数据用于学术研究；商业应用需获得 [EMBL 单独授权](mailto:stitch@embl.de)**
- **甲基化数据**: GEO (NCBI) — 公共领域
- **Hallmark 基因集**: MSigDB — Liberzon et al., *PNAS* 112(25), 2015. [CC BY 4.0](https://www.gsea-msigdb.org/gsea/msigdb_license.jsp)

> **注意**：本仓库分发的是**预计算分析结果**（如排名化合物列表、PPI 模块摘要），而非原始 STRING 或 STITCH 数据库。希望访问或再分发底层数据库的用户必须遵守其各自的许可条款。

## 引用

如果您在研究中使用 SteeraMed Core，请引用两篇伴生论文：

- 框架论文：Xiong J. *World Models for Biomedicine: A Steerability Framework.* [doi:10.20944/preprints202605.0366.v1](https://doi.org/10.20944/preprints202605.0366.v1)
- 实现论文：Xiong J. *SteeraMed: A Biomedical World Model for N-of-1 Intervention Reasoning across Chronic Diseases and Aging.* [doi:10.20944/preprints202605.1578.v1](https://doi.org/10.20944/preprints202605.1578.v1)

```bibtex
@article{xiong2026steeramed,
  title={SteeraMed: A Biomedical World Model for N-of-1 Intervention Reasoning across Chronic Diseases and Aging},
  author={Xiong, Jianghui},
  journal={Preprints.org},
  year={2026},
  doi={10.20944/preprints202605.1578.v1}
}
@article{xiong2026framework,
  title={World Models for Biomedicine: A Steerability Framework},
  author={Xiong, Jianghui},
  journal={Preprints.org},
  year={2026},
  doi={10.20944/preprints202605.0366.v1}
}
```

## 免责声明

本软件仅生成假设生成性洞见，不是医疗器械，不提供治疗建议。医疗决策请务必咨询合格的专业医护人员。

## 关键词

`biomedical world model` · `medical world model` · `steerability` · `longevity` · `aging` · `personalized medicine` · `n-of-1` · `DNA methylation` · `epigenetics` · `drug ranking` · `PPI network` · `evidence chain` · `precision medicine` · `intervention reasoning` · `rheumatoid arthritis` · `depression` · `hallmark` · `methylation age`

## 许可证

MIT 许可证。仅适用于本仓库的**代码**。

`steeramed_core/presets/` 中的**预计算数据文件**包含 STITCH (CC BY-NC) 的衍生结果，仅供**学术研究和教育用途**。商业用途需获得 [EMBL 授权](mailto:stitch@embl.de)。
