"""
Preset data loaders for example patients, positive controls, and dataset info.

All data files are stored in the ``presets/`` package directory alongside
this module.
"""
import json
from pathlib import Path
from typing import Optional

_PRESETS_DIR = Path(__file__).parent
_PATIENTS_DIR = _PRESETS_DIR / "example_patients"


def load_example_patient(name: str) -> "EvidenceChain":
    """Load a bundled example patient as an EvidenceChain.

    Args:
        name: Patient stem name (e.g. ``"ra_patient_303"``). Must
            match a ``<name>.json`` file in the ``example_patients/``
            directory.

    Returns:
        A fully reconstructed ``EvidenceChain``.

    Raises:
        FileNotFoundError: If no JSON file matches the given name.
    """
    from steeramed_core.core.evidence_chain import EvidenceChain

    path = _PATIENTS_DIR / f"{name}.json"
    if not path.exists():
        available = [p.stem for p in _PATIENTS_DIR.glob("*.json")]
        raise FileNotFoundError(
            f"Example patient '{name}' not found. Available: {available}"
        )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return EvidenceChain.from_dict(data)


def load_positive_controls(disease: str) -> list:
    """Load the positive-control compound list for a disease.

    Args:
        disease: Disease identifier (e.g. ``"ra"``, ``"depression"``).
            Aliases like ``"mdd"`` → ``"depression"`` are accepted.

    Returns:
        List of positive-control compound records.

    Raises:
        KeyError: If the disease is not in the positive-controls registry.
    """
    path = _PRESETS_DIR / "positive_controls.json"
    with open(path, encoding="utf-8") as f:
        all_controls = json.load(f)
    key = _disease_key(disease)
    if key not in all_controls:
        raise KeyError(f"Disease '{disease}' not in positive controls. Available: {list(all_controls.keys())}")
    return all_controls[key]


def load_dataset_info(disease: str) -> dict:
    """Load GEO dataset metadata for a disease.

    Args:
        disease: Disease identifier or alias.

    Returns:
        Dict with dataset metadata (GEO ID, sample counts, etc.).

    Raises:
        KeyError: If the disease is not in the dataset registry.
    """
    path = _PRESETS_DIR / "datasets.json"
    with open(path, encoding="utf-8") as f:
        info = json.load(f)
    key = _disease_key(disease)
    if key not in info:
        raise KeyError(f"Disease '{disease}' not in datasets. Available: {list(info.keys())}")
    return info[key]


def _disease_key(disease: str) -> str:
    """Normalise a disease name to its canonical registry key."""
    mapping = {
        "ra": "ra", "rheumatoid_arthritis": "ra",
        "breast_cancer": "breast_cancer", "bc": "breast_cancer",
        "depression": "depression", "mdd": "depression",
        "aging": "aging", "age": "aging",
    }
    return mapping.get(disease.lower(), disease.lower())
