"""
N-of-1 delta vector computation and age/sex matched control selection.
"""
import numpy as np
import pandas as pd

from steeramed_core.core.config import MATCH_K, MATCH_CALIPER, MATCH_MIN_CONTROLS


def match_controls(
    case_age: float,
    case_sex: str,
    control_ages: np.ndarray,
    control_sexes: np.ndarray,
    k: int = MATCH_K,
    caliper: float = MATCH_CALIPER,
    min_controls: int = MATCH_MIN_CONTROLS,
) -> np.ndarray:
    """Select matched controls for a single case patient.

    Matching strategy:
        1. Filter controls by same sex AND age within ``caliper`` years.
        2. If fewer than ``min_controls`` pass, fall back to same-sex
           only (nearest age, ignoring caliper).
        3. If still too few, return empty array.

    Args:
        case_age: Age of the case patient.
        case_sex: Sex of the case patient (e.g. ``"M"`` or ``"F"``).
        control_ages: Ages of all candidate controls.
        control_sexes: Sexes of all candidate controls (same length).
        k: Maximum number of controls to select.
        caliper: Maximum age difference in years.
        min_controls: Minimum controls required; triggers fallback.

    Returns:
        Array of integer indices into the control pool.
    """
    sex_ok = control_sexes == case_sex
    age_diff = np.abs(control_ages.astype(float) - float(case_age))
    within_caliper = age_diff <= caliper
    eligible = sex_ok & within_caliper
    if not np.any(eligible):
        sex_only_idx = np.where(sex_ok)[0]
        if len(sex_only_idx) >= min_controls:
            age_diff_sex = np.abs(control_ages[sex_only_idx].astype(float) - float(case_age))
            sorted_order = np.argsort(age_diff_sex)
            selected = sex_only_idx[sorted_order[:k]]
            return selected
        return np.array([], dtype=int)
    eligible_idx = np.where(eligible)[0]
    eligible_age_diffs = age_diff[eligible_idx]
    sorted_order = np.argsort(eligible_age_diffs)
    n_select = min(k, len(eligible_idx))
    if n_select < min_controls:
        sex_only_idx = np.where(sex_ok)[0]
        if len(sex_only_idx) >= min_controls:
            age_diff_sex = np.abs(control_ages[sex_only_idx].astype(float) - float(case_age))
            sorted_order = np.argsort(age_diff_sex)
            selected = sex_only_idx[sorted_order[:k]]
            return selected
        return np.array([], dtype=int)
    return eligible_idx[sorted_order[:n_select]]


def compute_n1_delta(
    patient_gene_values: np.ndarray,
    matched_control_values: np.ndarray,
) -> np.ndarray:
    """Compute the N-of-1 delta vector for one patient.

    Args:
        patient_gene_values: 1-D array of gene-level values for the patient.
        matched_control_values: 2-D array of shape (n_controls, n_genes).

    Returns:
        1-D delta vector of shape (n_genes,), computed as
        patient minus mean of matched controls (NaN-safe).
    """
    ctrl_mean = np.nanmean(matched_control_values, axis=0)
    delta = patient_gene_values.astype(float) - ctrl_mean
    return delta


def compute_all_deltas(
    gene_df: pd.DataFrame,
    case_mask: np.ndarray,
    ages: np.ndarray,
    sexes: np.ndarray,
    k: int = MATCH_K,
    caliper: float = MATCH_CALIPER,
) -> np.ndarray:
    """Compute N-of-1 delta vectors for every case patient.

    Args:
        gene_df: DataFrame with genes as rows and samples as columns.
        case_mask: Boolean array (length n_samples); True = case.
        ages: Numeric array of sample ages.
        sexes: Array of sample sexes.
        k: Controls per case (passed to ``match_controls``).
        caliper: Age caliper in years.

    Returns:
        ndarray of shape (n_cases, n_genes). Rows where no controls
        were found are filled with NaN.
    """
    sample_matrix = gene_df.values.T.astype(float)
    n_samples, n_genes = sample_matrix.shape
    case_indices = np.where(case_mask)[0]
    control_indices = np.where(~case_mask)[0]
    control_ages = ages[control_indices].astype(float)
    control_sexes = sexes[control_indices]
    control_matrix = sample_matrix[control_indices]
    deltas = np.full((len(case_indices), n_genes), np.nan)
    for i, ci in enumerate(case_indices):
        matched = match_controls(
            case_age=float(ages[ci]),
            case_sex=str(sexes[ci]),
            control_ages=control_ages,
            control_sexes=control_sexes,
            k=k,
            caliper=caliper,
        )
        if len(matched) == 0:
            continue
        patient_vals = sample_matrix[ci]
        ctrl_vals = control_matrix[matched]
        deltas[i] = compute_n1_delta(patient_vals, ctrl_vals)
    return deltas


def compute_group_delta(
    gene_df: pd.DataFrame,
    case_mask: np.ndarray,
) -> np.ndarray:
    """Compute group-level delta (case mean minus control mean).

    Args:
        gene_df: DataFrame with genes as rows and samples as columns.
        case_mask: Boolean array (length n_samples); True = case.

    Returns:
        1-D array of shape (n_genes,) with mean delta per gene.
    """
    sample_matrix = gene_df.values.T.astype(float)
    case_vals = sample_matrix[case_mask]
    ctrl_vals = sample_matrix[~case_mask]
    case_mean = np.nanmean(case_vals, axis=0)
    ctrl_mean = np.nanmean(ctrl_vals, axis=0)
    return case_mean - ctrl_mean
