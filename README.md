# SteeraMed Core

[English](README.md) | [中文](README.zh-CN.md)

[![PyPI](https://img.shields.io/badge/steeramed--core-0.1.0-blue)](https://pypi.org/project/steeramed-core/)
[![Python](https://img.shields.io/badge/python-3.9+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Preprint](https://img.shields.io/badge/preprint-2025-orange)](https://doi.org/10.20944/preprints202605.1578.v1)

**First N-of-1 Steerable Medicine World Model — Personalized intervention evidence chains from DNA methylation data.**

> Select a patient case → Generate individualized drug evidence in 30 seconds.

## What is Steerable Medicine?

Traditional systems biology:
- Population statistics → average effects → universal guidelines
- "Is this drug effective for the population?"

Steerable Medicine (SMWM):
- Individual perturbation → matched PPI modules → personalized evidence chain
- "Is this drug effective **for you**?"

| | Systems Biology | Steerable Medicine |
|---|---|---|
| Unit of analysis | Population | Individual (N-of-1) |
| Question | Group average | Personal match |
| Output | General guideline | 4-layer evidence chain |
| Drug ranking | Clinical trials | SA alignment + bootstrap |

## Four-Layer Evidence Chain

```
Layer 1: PPI Module Perturbation  ← "What's different in your biology?"
Layer 2: Compound SA Alignment    ← "Which compounds can correct it?"
Layer 3: Mechanism Annotation     ← "Why does this compound work?"
Layer 4: Bootstrap Confidence     ← "How reliable is this result?"
```

## Quick Start

```bash
pip install steeramed-core
python -m steeramed_core
```

Interactive case selector:

```
🧬 SteeraMed Core — N-of-1 Evidence Chain Explorer
═════════════════════════════════════════════════════

Select a patient case:
  [1] 🧓 Aging · Population Screening
  [2] 🧑 RA · 51M · T-cell Perturbation
  [3] 🧑 Depression · 52M · Innate Immunity

Enter choice [1-3]: 2

✅ Generated 4 figures in results/:
  📊 hallmark_bar.png      — Hallmark perturbation profile
  💊 drug_ranking.png       — Top-10 compound ranking
  🔗 evidence_network.png  — Drug-PPI-Hallmark alignment
  📋 patient_card.png       — One-page patient summary
```

Batch mode:

```bash
python -m steeramed_core --all          # all cases
python -m steeramed_core --case ra_303  # specific case
python -m steeramed_core --list         # list available cases
```

## Gallery

**Patient Summary Card** (Aging case):

![Patient Card](docs/aging_patient_card.png)

**Drug Ranking** (RA case):

![Drug Ranking](docs/ra_drug_ranking.png)

**Hallmark Perturbation** (Aging case):

![Hallmark Bar](docs/aging_hallmark_bar.png)

**Patient Summary Card** (RA case):

![RA Patient Card](docs/ra_patient_card.png)

## Available Cases

| Case | Disease | Key Finding | Evidence |
|------|---------|-------------|----------|
| Aging · Population | GSE40279 | Niacin #1, 2/5 geroprotectors | MODERATE |
| RA · 51M | GSE42861 | 6/10 known RA drugs, pentoxifylline #1 | STRONG |
| Depression · 52M | GSE128235 | creatine #1, innate immunity | EXPLORATORY |

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

## Data Sources

- **PPI Network**: STRING v12.0 (CC BY 4.0)
- **Compound Targets**: STITCH (CC BY-NC, academic use only)
- **Methylation Data**: GEO (public domain)
- **Hallmark Gene Sets**: MSigDB (CC BY 4.0)

## Citation

If you use SteeraMed Core in your research:

```bibtex
@article{xiong2026steeramed,
  title={SteeraMed: A Biomedical World Model for N-of-1 Intervention Reasoning across Chronic Diseases and Aging},
  author={Xiong, Jianghui},
  journal={Preprints.org},
  year={2026},
  doi={10.20944/preprints202605.1578.v1}
}
```

## Disclaimer

This software generates hypothesis-generating insights only. It is not a medical device and does not provide treatment recommendations. Always consult qualified healthcare professionals for medical decisions.

## License

MIT License. Note: STITCH compound-target data is CC BY-NC; commercial use requires separate licensing.
