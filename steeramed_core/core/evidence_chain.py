"""
Four-layer evidence chain data structures for SteeraMed N=1 analysis.

Layer 1: PPI Module Perturbation
Layer 2: Compound Steerability Alignment
Layer 3: Mechanism Annotation
Layer 4: Bootstrap Confidence
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json


@dataclass
class PPIModule:
    """A perturbed PPI module from Layer 1 analysis."""

    hub_gene: str
    delta: float
    p_value: float
    n_genes: int
    hallmark: Optional[str] = None


@dataclass
class CompoundMatch:
    """A compound ranked by Steerability Alignment (Layer 2)."""

    rank: int
    compound_id: str
    compound_name: str
    importance: int
    mean_abs_sa: float
    is_known_drug: bool
    n_targets: int
    matched_modules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EvidenceChain:
    """Complete four-layer evidence chain for one patient.

    Layers:
        1. ``perturbed_modules`` — PPI modules with significant delta.
        2. ``top_compounds`` — Compounds ranked by SA importance.
        3. ``mechanism_map`` — Compound → PPI hub / hallmark annotation.
        4. ``bootstrap_stability`` — Fraction of bootstrap iterations
           each compound remained in the top-10.
    """

    patient_id: str
    disease: str
    age: Optional[int] = None
    sex: Optional[str] = None
    perturbed_modules: List[PPIModule] = field(default_factory=list)
    top_compounds: List[CompoundMatch] = field(default_factory=list)
    mechanism_map: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    bootstrap_stability: Dict[str, float] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceChain":
        """Reconstruct an EvidenceChain from a plain dict.

        Extra keys in nested dicts (e.g. from newer versions) are
        silently ignored so that backward-compatible loading works.
        """
        _pm_fields = {f.name for f in PPIModule.__dataclass_fields__.values()}
        _cm_fields = {f.name for f in CompoundMatch.__dataclass_fields__.values()}
        perturbed = [
            PPIModule(**{k: v for k, v in m.items() if k in _pm_fields})
            for m in data.get("perturbed_modules", [])
        ]
        compounds = [
            CompoundMatch(**{k: v for k, v in c.items() if k in _cm_fields})
            for c in data.get("top_compounds", [])
        ]
        return cls(
            patient_id=data["patient_id"],
            disease=data["disease"],
            age=data.get("age"),
            sex=data.get("sex"),
            perturbed_modules=perturbed,
            top_compounds=compounds,
            mechanism_map=data.get("mechanism_map", {}),
            bootstrap_stability=data.get("bootstrap_stability", {}),
            meta=data.get("meta", {}),
        )

    def to_dict(self) -> dict:
        """Convert the entire evidence chain to a nested dict."""
        d = asdict(self)
        return d

    def to_json(self, indent: int = 2) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def summary(self) -> str:
        """Human-readable multi-line summary of all four layers."""
        lines = [
            f"Patient: {self.patient_id}",
            f"Disease: {self.disease}",
        ]
        if self.age is not None:
            lines.append(f"Age: {self.age}")
        if self.sex is not None:
            lines.append(f"Sex: {self.sex}")

        lines.append(f"\n--- Layer 1: Perturbed PPI Modules ({len(self.perturbed_modules)}) ---")
        for m in self.perturbed_modules[:5]:
            hm = m.hallmark or "N/A"
            lines.append(
                f"  {m.hub_gene}: delta={m.delta:.4f}, p={m.p_value:.2e}, "
                f"n_genes={m.n_genes}, hallmark={hm}"
            )
        if len(self.perturbed_modules) > 5:
            lines.append(f"  ... and {len(self.perturbed_modules) - 5} more")

        lines.append(f"\n--- Layer 2: Top Compounds ({len(self.top_compounds)}) ---")
        for c in self.top_compounds[:5]:
            tag = "[Rx]" if c.is_known_drug else "[OTC/NP]"
            lines.append(
                f"  #{c.rank} {c.compound_name} {tag}: "
                f"importance={c.importance}, mean_abs_sa={c.mean_abs_sa:.4f}, "
                f"n_targets={c.n_targets}"
            )
        if len(self.top_compounds) > 5:
            lines.append(f"  ... and {len(self.top_compounds) - 5} more")

        lines.append(f"\n--- Layer 3: Mechanism Map ({len(self.mechanism_map)} compounds) ---")
        for cid, mech in list(self.mechanism_map.items())[:3]:
            hubs = mech.get("ppi_hubs", [])
            tg = mech.get("target_genes", [])
            hm = mech.get("hallmarks", [])
            lines.append(f"  {cid}: hubs={hubs[:3]}, targets={len(tg)}, hallmarks={hm}")
        if len(self.mechanism_map) > 3:
            lines.append(f"  ... and {len(self.mechanism_map) - 3} more")

        lines.append(f"\n--- Layer 4: Bootstrap Stability ({len(self.bootstrap_stability)} compounds) ---")
        sorted_bs = sorted(self.bootstrap_stability.items(), key=lambda x: x[1], reverse=True)
        for cid, pct in sorted_bs[:5]:
            lines.append(f"  {cid}: {pct:.1f}% in top-10")
        if len(sorted_bs) > 5:
            lines.append(f"  ... and {len(sorted_bs) - 5} more")

        n_known = self.meta.get("n_known_drugs_in_top10", "N/A")
        n_total = self.meta.get("n_total_compounds", "N/A")
        lines.append(f"\n--- Meta ---")
        lines.append(f"  Total compounds screened: {n_total}")
        lines.append(f"  Known drugs in top-10: {n_known}")

        return "\n".join(lines)
