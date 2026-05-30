"""
SteeraMed Core — Steerable Biomedical World Model for N-of-1 Intervention Reasoning.

Reproduce all figures from:
    Xiong J. (2026) SteeraMed: A Biomedical World Model for N-of-1
    Intervention Reasoning. Preprints.org. DOI: 10.20944/preprints202605.1578.v1
"""

__version__ = "0.1.0"

__all__ = ["EvidenceChain", "load_example_patient"]


def __getattr__(name):
    if name == "EvidenceChain":
        from steeramed_core.core.evidence_chain import EvidenceChain
        return EvidenceChain
    if name == "load_example_patient":
        from steeramed_core.presets import load_example_patient
        return load_example_patient
    raise AttributeError(f"module 'steeramed_core' has no attribute {name!r}")
