"""
Configuration constants for SteeraMed core algorithms.

STRING PPI and STITCH scores are integer values in [0, 1000].
Age caliper is in years.
"""

PPI_SCORE_CUTOFF: int = 400       # STRING combined score threshold (0-1000)
PPI_MIN_SIZE: int = 20            # minimum genes per PPI module
PPI_MAX_SIZE: int = 800           # maximum genes per PPI module
PPI_DIFF_OVERLAP_MIN: int = 3     # minimum overlap between compound targets and PPI module
PPI_TOP_N: int = 100              # number of top-delta PPI modules to keep

STITCH_SCORE: int = 200           # STITCH combined score threshold (0-1000)
CHEM_MIN_TARGETS_DEFAULT: int = 60   # minimum known targets for a compound
CHEM_MAX_TARGETS_DEFAULT: int = 300  # maximum known targets (promiscuity filter)

SEMO_MIN_INTERSECTION: int = 3   # minimum gene overlap (compound ∩ PPI module)
SEMO_MIN_NON_TARGET: int = 3     # minimum non-target genes in module
SEMO_TOP_CHEM_PER_PPI: int = 10  # top compounds per PPI module
MAX_SEMO_PAIRS: int = 10000      # safety cap on compound–module pairs

PATIENT_TOP_K: int = 50          # top-k features for patient-level ranking
BOOTSTRAP_N_ITER: int = 200      # bootstrap iterations (N-of-1)
BOOTSTRAP_GROUP_N_ITER: int = 100  # bootstrap iterations (group-level)

MATCH_K: int = 10                # number of matched controls per case
MATCH_CALIPER: int = 5           # age-matching caliper in years
MATCH_MIN_CONTROLS: int = 3      # fallback minimum controls when caliper is too tight

DISEASE_PRESETS = {
    "ra": {                       # Rheumatoid arthritis (GSE42861, whole blood)
        "geo_dataset": "GSE42861",
        "n_cases": 354,
        "n_controls": 335,
        "match_k": 10,
        "match_caliper": 5,
        "ppi_score": 400,
        "ppi_min_size": 20,
        "ppi_max_size": 800,
        "stitch_score": 200,
        "chem_min_targets": 60,
        "chem_max_targets": 300,
        "top_n_ppi": 100,
        "top_k_features": 200,
        "patient_top_k": 50,
    },
    "breast_cancer": {            # Breast cancer (GSE51032, whole blood)
        "geo_dataset": "GSE51032",
        "n_cases": 235,
        "n_controls": 424,
        "match_k": 15,
        "match_caliper": 5,
        "ppi_score": 400,
        "ppi_min_size": 20,
        "ppi_max_size": 800,
        "stitch_score": 200,
        "chem_min_targets": 60,
        "chem_max_targets": 300,
        "top_n_ppi": 100,
        "top_k_features": 200,
        "patient_top_k": 50,
    },
    "depression": {               # Major depressive disorder (GSE128235, whole blood)
        "geo_dataset": "GSE128235",
        "n_cases": 324,
        "n_controls": 209,
        "match_k": 10,
        "match_caliper": 5,
        "ppi_score": 400,
        "ppi_min_size": 20,
        "ppi_max_size": 800,
        "stitch_score": 200,
        "chem_min_targets": 5,
        "chem_max_targets": None,
        "top_n_ppi": 100,
        "top_k_features": 200,
        "patient_top_k": 50,
    },
    "aging": {                    # Healthy aging (GSE40279, Hannum cohort)
        "geo_dataset": "GSE40279",
        "young_max": 50,
        "old_min": 55,
        "ppi_score": 400,
        "ppi_min_size": 20,
        "ppi_max_size": 800,
        "stitch_score": 200,
        "chem_min_targets": 5,
        "chem_max_targets": None,
        "top_n_ppi": 100,
        "top_k_features": 200,
        "patient_top_k": 50,
    },
}
