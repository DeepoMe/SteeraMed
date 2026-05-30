<div align="center">

**[English](README.md) | [中文](README.zh-CN.md)**

# 🧬 SteeraMed Core

**Steerable Biomedical World Model for N-of-1 Intervention Reasoning**

[![PyPI](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Technical Report](https://img.shields.io/badge/report-preprints.org-orange.svg)](https://doi.org/10.20944/preprints202605.1578.v1)
[![Live Demo](https://img.shields.io/badge/demo-agent.steerable.world-purple.svg)](https://agent.steerable.world)

</div>

---

**One command → all figures from the paper. Zero configuration.**

```bash
pip install steeramed-core && python -m steeramed_core reproduce --fig all
```

---

## 🖼️ What You Get

### Aging Patient View — Personalized Hallmark Report

<table><tr>
<td width="50%"><img src="docs/fig4_aging_patient.png" alt="Aging Patient View" width="100%"/></td>
<td width="50%"><img src="docs/fig_s1_aging_evidence.png" alt="Aging Evidence Chain" width="100%"/></td>
</tr></table>

*Left: Hallmark-based biological age assessment with compound recommendations. Right: Four-layer evidence chain — PPI perturbation, compound ranking, mechanism network, bootstrap confidence.*

### Rheumatoid Arthritis — N=1 Evidence Chain

<table><tr>
<td width="50%"><img src="docs/fig6_ra_evidence.png" alt="RA Evidence Chain" width="100%"/></td>
<td width="50%"><img src="docs/fig7_ra_patient.png" alt="RA Patient View" width="100%"/></td>
</tr></table>

*Patient GSM1052147 (Male, 51y). 10 perturbed PPI modules identified. Top compound: Pentoxifylline (SA=9.49).*

### Depression — N=1 Evidence Chain

<table><tr>
<td width="50%"><img src="docs/fig8_dep_evidence.png" alt="Depression Evidence Chain" width="100%"/></td>
<td width="50%"><img src="docs/fig_s2_dep_patient.png" alt="Depression Patient View" width="100%"/></td>
</tr></table>

*Patient GSM3667899 (Male, 52y). Neutrophil degranulation pathway dominant. Top compound: Creatine (SA=9.58).*

---

## ⚡ Quick Start

### Install & Reproduce

```bash
# Install
pip install steeramed-core

# Reproduce all paper figures (generates 6 PNGs in results/)
python -m steeramed_core reproduce --fig all

# Or reproduce specific disease
python -m steeramed_core reproduce --fig aging
python -m steeramed_core reproduce --fig ra
python -m steeramed_core reproduce --fig dep
```

All figures are generated using **built-in example patient data** — no downloads, no API keys, no configuration.

### Use as a Library

```python
from steeramed_core import load_example_patient
from steeramed_core.viz.evidence_view import plot_evidence_chain
from steeramed_core.viz.patient_view import plot_patient_view

# Load built-in example patient
patient = load_example_patient("ra_patient_303")
print(patient.summary())

# Generate publication-quality figures
plot_evidence_chain(patient, save="evidence.pdf")
plot_patient_view(patient, save="report.png")
```

### Core Algorithm: SA Score

```python
from steeramed_core.core.semo import compute_sa_score
import numpy as np

delta = np.random.randn(1000)
target_idx = [10, 20, 30, 40, 50]
non_target_idx = list(range(100, 900))

sa = compute_sa_score(delta, target_idx, non_target_idx)
print(f"Steerability Alignment score: {sa:.3f}")
```

---

## 🏗️ How It Works

SteeraMed reasons about **which compounds can steer an individual patient's molecular state back toward health**, using only DNA methylation data and public databases (STRING PPI + STITCH compound-target).

### Four-Layer Evidence Chain

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: PPI Module Perturbation                       │
│  Which protein interaction modules are dysregulated?     │
│  Method: Welch t-test on module gene delta vectors       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Compound Steerability Alignment (SA)           │
│  Which compounds target those perturbed modules?         │
│  Method: Importance-weighted SA score ranking            │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Mechanism Annotation                           │
│  How do compound targets map to PPI module hubs?         │
│  Method: Target → PPI neighbor → hub gene tracing        │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Bootstrap Confidence                           │
│  How stable is the ranking under resampling?             │
│  Method: 1000-iteration bootstrap with top-k stability   │
└─────────────────────────────────────────────────────────┘
```

### N=1 Delta Vector

For each patient, SteeraMed computes an individualized delta vector:

$$\Delta_i = x_i - \bar{x}_{matched}$$

where matched controls are selected by age (±5 years) and sex. This delta vector is then used to identify perturbed PPI modules and rank candidate compounds.

---

## 📁 Project Structure

```
steeramed_core/
├── core/
│   ├── config.py            # Disease presets (RA, depression, aging, breast cancer)
│   ├── semo.py              # SA score + Welch t-test + importance voting
│   ├── delta.py             # N=1 delta vector + age/sex matching
│   └── evidence_chain.py    # Four-layer evidence chain dataclass
├── viz/
│   ├── theme.py             # Unified visual theme (Nature-grade palette)
│   ├── patient_view.py      # Patient-friendly three-panel card view
│   └── evidence_view.py     # Scientist four-panel evidence chain
├── presets/
│   ├── datasets.json        # Dataset metadata (GSE IDs, sample sizes)
│   ├── positive_controls.json
│   └── example_patients/    # Built-in patient data (3 examples)
│       ├── aging_patient_rep.json
│       ├── ra_patient_303.json
│       └── dep_patient_61.json
└── examples/
    ├── reproduce_aging_patient_view.py   # Fig 4 + Fig S1
    ├── reproduce_ra_evidence_chain.py    # Fig 6 + Fig 7
    └── reproduce_dep_evidence_chain.py   # Fig 8 + Fig S2
```

---

## 📊 Supported Diseases

| Disease | GEO Dataset | Tissue | N Cases | N Controls |
|---------|-------------|--------|---------|------------|
| Aging | GSE40279 | Whole blood | 473 (old) | 109 (young) |
| Rheumatoid Arthritis | GSE42861 | Whole blood | 354 | 335 |
| Depression | GSE128235 | Whole blood | 324 | 209 |
| Breast Cancer | GSE51032 | — | 235 | 424 |

---

## 🌐 Live Demo

Experience the interactive version at **[agent.steerable.world](https://agent.steerable.world)** — the same SteeraMed algorithms with animated visualizations, demo cases, and CSV upload support.

---

## 📝 Technical Report

> Xiong J. *SteeraMed: A Biomedical World Model for N-of-1 Intervention Reasoning across Chronic Diseases and Aging.* Preprints.org, 2026. DOI: [10.20944/preprints202605.1578.v1](https://doi.org/10.20944/preprints202605.1578.v1)

```bibtex
@article{xiong2026steeramed,
  title={SteeraMed: A Biomedical World Model for N-of-1 Intervention Reasoning across Chronic Diseases and Aging},
  author={Xiong, Jianghui},
  journal={Preprints.org},
  year={2026},
  doi={10.20944/preprints202605.1578.v1}
}
```

---

## ⚠️ Disclaimer

This software generates **hypothesis-generating insights only**. It is not a medical device and does not provide treatment recommendations. Always consult qualified healthcare professionals for medical decisions.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
