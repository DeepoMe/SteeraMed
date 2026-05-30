"""
Reproduce Fig S1 (Aging N=1 Evidence Chain) + Fig 4 (Aging Patient View).

Usage:
    python -m steeramed_core.examples.reproduce_aging_patient_view
"""
from pathlib import Path

from steeramed_core.presets import load_example_patient
from steeramed_core.viz.evidence_view import plot_evidence_chain
from steeramed_core.viz.patient_view import plot_patient_view


def main():
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    print("Loading aging representative patient data...")
    patient = load_example_patient("aging_patient_rep")
    print(patient.summary())

    print("\nGenerating Fig S1: Aging N=1 Evidence Chain...")
    fig1 = plot_evidence_chain(patient, output_path=str(out_dir / "fig_s1_aging_evidence.png"))
    print(f"  -> {out_dir / 'fig_s1_aging_evidence.png'}")

    print("Generating Fig 4: Aging Patient View...")
    fig2 = plot_patient_view(patient, output_path=str(out_dir / "fig4_aging_patient.png"))
    print(f"  -> {out_dir / 'fig4_aging_patient.png'}")

    print("\nDone! Check the results/ directory.")


if __name__ == "__main__":
    main()
