"""
Reproduce Fig 6 (RA N=1 Evidence Chain) + Fig 7 (RA Patient View).

Usage:
    python -m steeramed_core.examples.reproduce_ra_evidence_chain
"""
from pathlib import Path

from steeramed_core.presets import load_example_patient
from steeramed_core.viz.evidence_view import plot_evidence_chain
from steeramed_core.viz.patient_view import plot_patient_view


def main():
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    print("Loading RA patient #303 data...")
    patient = load_example_patient("ra_patient_303")
    print(patient.summary())

    print("\nGenerating Fig 6: RA N=1 Evidence Chain...")
    fig1 = plot_evidence_chain(patient, output_path=str(out_dir / "fig6_ra_evidence.png"))
    print(f"  -> {out_dir / 'fig6_ra_evidence.png'}")

    print("Generating Fig 7: RA Patient View...")
    fig2 = plot_patient_view(patient, output_path=str(out_dir / "fig7_ra_patient.png"))
    print(f"  -> {out_dir / 'fig7_ra_patient.png'}")

    print("\nDone! Check the results/ directory.")


if __name__ == "__main__":
    main()
