"""
SEMO (Steerable Epigenetic Module Optimization) core algorithms.

Implements the Steerability Alignment (SA) score and compound ranking
pipeline from the SteeraMed framework.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict

from steeramed_core.core.config import (
    SEMO_MIN_INTERSECTION,
    SEMO_MIN_NON_TARGET,
    PATIENT_TOP_K,
)


@dataclass
class CompoundRanking:
    """Ranked compound with SA-based importance score."""

    rank: int
    compound_id: str
    compound_name: str
    importance: int
    mean_abs_sa: float
    is_known_drug: bool
    n_targets: int
    sa_scores: List[dict] = field(default_factory=list)


def welch_t(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Welch's t-statistic for two independent samples.

    Args:
        a: First sample array. NaN values are removed before computation.
        b: Second sample array. NaN values are removed before computation.

    Returns:
        Welch's t-statistic. Returns 0.0 when either sample has fewer
        than 2 elements or when the pooled standard error is zero.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    n1, n2 = len(a), len(b)
    m1, m2 = np.mean(a), np.mean(b)
    v1, v2 = np.var(a, ddof=1), np.var(b, ddof=1)
    se = np.sqrt(v1 / n1 + v2 / n2)
    return float((m1 - m2) / se) if se > 1e-15 else 0.0


def compute_sa_score(
    delta: np.ndarray,
    target_idx: List[int],
    non_target_idx: List[int],
) -> float:
    """Compute Steerability Alignment (SA) score for one compound–module pair.

    The SA score is the Welch's t-statistic comparing delta values at
    target gene positions (compound ∩ PPI module) versus non-target
    positions (module genes not targeted by the compound). A positive
    SA indicates the compound's targets align with the direction of
    perturbation in that module.

    Args:
        delta: Gene-level delta vector (patient minus matched controls).
        target_idx: Indices of compound–module intersection genes.
        non_target_idx: Indices of module genes not targeted by the compound.

    Returns:
        SA score (float). Returns 0.0 when either gene set is below
        the minimum size thresholds (SEMO_MIN_INTERSECTION,
        SEMO_MIN_NON_TARGET).
    """
    delta = np.asarray(delta, dtype=float)
    if len(target_idx) < SEMO_MIN_INTERSECTION or len(non_target_idx) < SEMO_MIN_NON_TARGET:
        return 0.0
    return welch_t(delta[target_idx], delta[non_target_idx])


def compute_sa_matrix(
    delta_matrix: np.ndarray,
    pairs: List[Dict],
) -> np.ndarray:
    """Compute SA scores for all samples × all compound–module pairs.

    Vectorised across samples for performance. Each pair dict must
    contain ``inter_idx`` (or ``target_idx``) and ``non_idx``
    (or ``non_target_idx``) keying lists of gene-position indices.

    Args:
        delta_matrix: Shape (n_samples, n_genes). Gene-level delta
            values for every sample.
        pairs: List of compound–module pair dicts. Each dict has keys:

            - ``inter_idx`` or ``target_idx`` — indices of intersection genes.
            - ``non_idx`` or ``non_target_idx`` — indices of non-target genes.
            - ``compound_id``, ``compound_name``, etc. (metadata, unused here).

    Returns:
        ndarray of shape (n_samples, n_pairs) with SA scores.
        Entries are 0.0 where a pair does not meet minimum gene counts.
    """
    delta_matrix = np.asarray(delta_matrix, dtype=float)
    n_samples = delta_matrix.shape[0]
    n_pairs = len(pairs)
    sa = np.zeros((n_samples, n_pairs))

    for pi, p in enumerate(pairs):
        i_idx = p.get("inter_idx", p.get("target_idx", []))
        n_idx = p.get("non_idx", p.get("non_target_idx", []))
        if len(i_idx) < SEMO_MIN_INTERSECTION or len(n_idx) < SEMO_MIN_NON_TARGET:
            continue
        ni, nn = len(i_idx), len(n_idx)

        i_data = delta_matrix[:, i_idx]
        n_data = delta_matrix[:, n_idx]
        m_i = i_data.mean(axis=1)
        m_n = n_data.mean(axis=1)
        v_i = i_data.var(axis=1, ddof=1)
        v_n = n_data.var(axis=1, ddof=1)
        se = np.sqrt(v_i / ni + v_n / nn)
        sa[:, pi] = np.where(se > 1e-15, (m_i - m_n) / se, 0.0)

    return sa


def rank_compounds_by_importance(
    sa_matrix: np.ndarray,
    pairs: List[Dict],
    top_k: int = PATIENT_TOP_K,
) -> List[CompoundRanking]:
    """Rank compounds by cross-sample importance voting.

    For each sample, compounds are ranked by |SA|. The top-k compounds
    per sample receive one "vote". Compounds are then globally ranked
    by (total votes, mean |SA|) descending.

    Args:
        sa_matrix: Shape (n_samples, n_pairs). Output of
            ``compute_sa_matrix``.
        pairs: Compound–module pair dicts (same list passed to
            ``compute_sa_matrix``). Each dict should contain:

            - ``compound_id`` or ``compound`` — unique compound identifier.
            - ``compound_name`` — human-readable name.
            - ``is_known_drug`` — whether it is an FDA-approved drug.
            - ``n_targets`` — number of known protein targets.
            - ``inter_idx``/``target_idx``, ``intersection``/``target_genes``
              — gene-level metadata for the SA detail records.
            - ``ppi_hub`` — hub gene of the matched PPI module.

        top_k: Number of top compounds to count per sample.

    Returns:
        List of ``CompoundRanking`` sorted by importance (descending).
    """
    n_samples, n_pairs = sa_matrix.shape
    abs_sa = np.abs(sa_matrix)

    compound_votes = defaultdict(int)
    compound_sa_values = defaultdict(list)
    compound_info = {}

    for s in range(n_samples):
        ranked = np.argsort(abs_sa[s])[::-1][:top_k]
        for pi in ranked:
            if pi >= n_pairs:
                continue
            p = pairs[pi]
            cid = p.get("compound_id", p.get("compound", f"unknown_{pi}"))
            compound_votes[cid] += 1
            compound_sa_values[cid].append(sa_matrix[s, pi])
            if cid not in compound_info:
                compound_info[cid] = {
                    "compound_name": p.get("compound_name", cid),
                    "is_known_drug": p.get("is_known_drug", False),
                    "n_targets": p.get("n_targets", len(p.get("inter_idx", p.get("target_idx", [])))),
                    "sa_details": [],
                }
            compound_info[cid]["sa_details"].append({
                "ppi_hub": p.get("ppi_hub", ""),
                "sa": float(sa_matrix[s, pi]),
                "target_genes": p.get("intersection", p.get("target_genes", [])),
            })

    sorted_compounds = sorted(
        compound_votes.keys(),
        key=lambda c: (compound_votes[c], np.mean(np.abs(compound_sa_values[c]))),
        reverse=True,
    )

    results = []
    for rank, cid in enumerate(sorted_compounds, 1):
        info = compound_info[cid]
        sa_vals = compound_sa_values[cid]
        results.append(CompoundRanking(
            rank=rank,
            compound_id=cid,
            compound_name=info["compound_name"],
            importance=compound_votes[cid],
            mean_abs_sa=float(np.mean(np.abs(sa_vals))),
            is_known_drug=info["is_known_drug"],
            n_targets=info["n_targets"],
            sa_scores=info["sa_details"],
        ))

    return results
