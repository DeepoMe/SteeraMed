"""
Reproduce Fig 8 (Depression N=1 Evidence Chain) + Fig S2 (Depression Patient View).

Usage:
    python -m steeramed_core.examples.reproduce_dep_evidence_chain
"""
from pathlib import Path

from steeramed_core.presets import load_example_patient
from steeramed_core.viz.evidence_view import plot_evidence_chain
from steeramed_core.viz.patient_view import plot_patient_view


def main():
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    print("Loading Depression patient #61 data...")
    patient = load_example_patient("dep_patient_61")
    print(patient.summary())

    print("\nGenerating Fig 8: Depression N=1 Evidence Chain...")
    fig1 = plot_evidence_chain(patient, output_path=str(out_dir / "fig8_dep_evidence.png"))
    print(f"  -> {out_dir / 'fig8_dep_evidence.png'}")

    print("Generating Fig S2: Depression Patient View...")
    fig2 = plot_patient_view(patient, output_path=str(out_dir / "fig_s2_dep_patient.png"))
    print(f"  -> {out_dir / 'fig_s2_dep_patient.png'}")

    print("\nDone! Check the results/ directory.")


if __name__ == "__main__":
    main()
