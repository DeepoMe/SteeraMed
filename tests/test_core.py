"""
Unit tests for steeramed_core core algorithms.
"""
import numpy as np
import pytest
from scipy import stats as sp_stats

from steeramed_core.core.semo import welch_t, compute_sa_score
from steeramed_core.core.delta import (
    match_controls,
    compute_n1_delta,
    compute_group_delta,
)
from steeramed_core.core.evidence_chain import EvidenceChain, PPIModule, CompoundMatch

_RNG = np.random.RandomState(42)


class TestWelchT:
    def test_symmetry(self):
        a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        b = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
        assert welch_t(a, b) == pytest.approx(-welch_t(b, a), abs=1e-10)

    def test_identical_groups(self):
        a = np.array([1.0, 2.0, 3.0])
        assert welch_t(a, a) == pytest.approx(0.0, abs=1e-10)

    def test_against_scipy(self):
        rng = np.random.RandomState(42)
        a = rng.randn(50)
        b = rng.randn(50) + 0.5
        sp_result = sp_stats.ttest_ind(a, b, equal_var=False)
        assert welch_t(a, b) == pytest.approx(sp_result.statistic, abs=1e-6)

    def test_single_element(self):
        assert welch_t(np.array([1.0]), np.array([2.0])) == 0.0


class TestSAScore:
    def test_basic(self):
        delta = _RNG.randn(100)
        target = [0, 1, 2, 3, 4]
        non_target = list(range(10, 90))
        sa = compute_sa_score(delta, target, non_target)
        assert isinstance(sa, float)
        assert not np.isnan(sa)

    def test_minimum_genes(self):
        delta = _RNG.randn(100)
        assert compute_sa_score(delta, [0], list(range(10, 90))) == 0.0
        assert compute_sa_score(delta, list(range(5)), [10]) == 0.0

    def test_all_same_delta(self):
        delta = np.ones(100) * 0.5
        assert compute_sa_score(delta, [0, 1, 2], [10, 11, 12]) == 0.0


class TestMatchControls:
    def test_basic_matching(self):
        ages = np.array([30, 32, 35, 40, 45, 50, 55, 60])
        sexes = np.array(["M", "M", "F", "M", "F", "M", "M", "F"])
        idx = match_controls(33, "M", ages, sexes, k=3, caliper=5)
        assert len(idx) >= 1
        for i in idx:
            assert sexes[i] == "M"
            assert abs(ages[i] - 33) <= 5 or len([j for j in range(len(ages)) if sexes[j] == "M" and abs(ages[j] - 33) <= 5]) < 3

    def test_no_match_returns_empty(self):
        ages = np.array([80, 85, 90])
        sexes = np.array(["F", "F", "F"])
        idx = match_controls(30, "M", ages, sexes, k=3, caliper=5)
        assert len(idx) == 0


class TestN1Delta:
    def test_basic(self):
        patient = np.array([0.5, 0.6, 0.7])
        controls = np.array([[0.4, 0.5, 0.6], [0.3, 0.4, 0.5]])
        delta = compute_n1_delta(patient, controls)
        assert delta.shape == (3,)
        expected = patient - controls.mean(axis=0)
        np.testing.assert_array_almost_equal(delta, expected)


class TestGroupDelta:
    def test_basic(self):
        import pandas as pd
        df = pd.DataFrame(
            {"s1": [0.1, 0.2, 0.3], "s2": [0.4, 0.5, 0.6], "s3": [0.7, 0.8, 0.9]},
            index=["gene1", "gene2", "gene3"],
        )
        case_mask = np.array([False, False, True])
        delta = compute_group_delta(df, case_mask)
        assert delta.shape == (3,)


class TestEvidenceChain:
    def test_from_dict(self):
        data = {
            "patient_id": "TEST001",
            "age": 45,
            "sex": "F",
            "disease": "ra",
            "perturbed_modules": [
                {"hub_gene": "BRCA1", "delta": 0.05, "p_value": 1e-10, "n_genes": 50, "hallmark": None}
            ],
            "top_compounds": [
                {
                    "rank": 1,
                    "compound_id": "CIDm00000001",
                    "compound_name": "TestDrug",
                    "importance": 5,
                    "mean_abs_sa": 8.5,
                    "is_known_drug": True,
                    "n_targets": 100,
                    "matched_modules": [],
                }
            ],
            "bootstrap_stability": {"TestDrug": 0.42},
            "meta": {"n_total_compounds": 500},
        }
        chain = EvidenceChain.from_dict(data)
        assert chain.patient_id == "TEST001"
        assert chain.age == 45
        assert len(chain.perturbed_modules) == 1
        assert chain.perturbed_modules[0].hub_gene == "BRCA1"
        assert len(chain.top_compounds) == 1
        assert chain.top_compounds[0].compound_name == "TestDrug"
        assert chain.top_compounds[0].is_known_drug is True

    def test_to_dict_roundtrip(self):
        data = {
            "patient_id": "TEST002",
            "age": None,
            "sex": None,
            "disease": "aging",
            "perturbed_modules": [],
            "top_compounds": [],
            "bootstrap_stability": {},
            "meta": {},
        }
        chain = EvidenceChain.from_dict(data)
        d = chain.to_dict()
        assert d["patient_id"] == "TEST002"
        assert d["age"] is None
        assert d["disease"] == "aging"

    def test_extra_fields_ignored(self):
        data = {
            "patient_id": "TEST003",
            "age": None,
            "sex": None,
            "disease": "ra",
            "perturbed_modules": [
                {"hub_gene": "X", "delta": 0.1, "p_value": 0.01, "n_genes": 5, "hallmark": None, "extra_field": "ignored"}
            ],
            "top_compounds": [
                {"rank": 1, "compound_id": "C1", "compound_name": "D1", "importance": 1,
                 "mean_abs_sa": 0.0, "is_known_drug": False, "n_targets": 1, "matched_modules": [],
                 "votes": 99, "pct": 0.5, "is_geroprotector": True}
            ],
            "bootstrap_stability": {},
            "meta": {},
        }
        chain = EvidenceChain.from_dict(data)
        assert chain.perturbed_modules[0].hub_gene == "X"
        assert chain.top_compounds[0].compound_name == "D1"

    def test_summary_does_not_crash(self):
        data = {
            "patient_id": "TEST004",
            "age": 60,
            "sex": "M",
            "disease": "aging",
            "perturbed_modules": [
                {"hub_gene": "A", "delta": 0.01, "p_value": 1e-5, "n_genes": 10, "hallmark": "Chronic Inflammation"}
            ],
            "top_compounds": [
                {"rank": 1, "compound_id": "C1", "compound_name": "Niacin", "importance": 100,
                 "mean_abs_sa": 0.0, "is_known_drug": False, "n_targets": 200, "matched_modules": []}
            ],
            "bootstrap_stability": {"Niacin": 30.4},
            "meta": {"n_total_compounds": 1482},
        }
        chain = EvidenceChain.from_dict(data)
        s = chain.summary()
        assert "Niacin" in s
        assert "TEST004" in s
