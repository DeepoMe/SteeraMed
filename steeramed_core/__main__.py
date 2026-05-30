"""
CLI entry point: python -m steeramed_core

Usage:
    python -m steeramed_core reproduce [--fig aging|ra|dep|all]
    python -m steeramed_core info
"""
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]

    if not args or args[0] == "info":
        _print_info()
        return

    if args[0] == "reproduce":
        fig = "all"
        if "--fig" in args:
            idx = args.index("--fig")
            if idx + 1 < len(args):
                fig = args[idx + 1]
        _reproduce(fig)
        return

    print(f"Unknown command: {args[0]}")
    print("Usage: python -m steeramed_core [reproduce [--fig aging|ra|dep|all] | info]")
    sys.exit(1)


def _print_info():
    from steeramed_core import __version__
    print(f"steeramed-core v{__version__}")
    print()
    print("Available example patients:")
    patients_dir = Path(__file__).parent / "presets" / "example_patients"
    for p in sorted(patients_dir.glob("*.json")):
        size_kb = p.stat().st_size / 1024
        print(f"  {p.stem} ({size_kb:.0f} KB)")
    print()
    print("Commands:")
    print("  reproduce --fig aging   Generate Fig 4 + Fig S1 (Aging)")
    print("  reproduce --fig ra      Generate Fig 6 + Fig 7 (RA)")
    print("  reproduce --fig dep     Generate Fig 8 + Fig S2 (Depression)")
    print("  reproduce --fig all     Generate all figures")
    print("  info                    Show this info")


def _reproduce(fig):
    if fig in ("aging", "all"):
        from steeramed_core.examples.reproduce_aging_patient_view import main as run_aging
        print("=" * 50)
        print("  Aging Patient View")
        print("=" * 50)
        run_aging()
        print()

    if fig in ("ra", "all"):
        from steeramed_core.examples.reproduce_ra_evidence_chain import main as run_ra
        print("=" * 50)
        print("  RA N=1 Evidence Chain")
        print("=" * 50)
        run_ra()
        print()

    if fig in ("dep", "all"):
        from steeramed_core.examples.reproduce_dep_evidence_chain import main as run_dep
        print("=" * 50)
        print("  Depression N=1 Evidence Chain")
        print("=" * 50)
        run_dep()
        print()

    print("All done! Check the results/ directory.")


if __name__ == "__main__":
    main()
