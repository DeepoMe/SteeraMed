"""SteeraMed Core CLI — N-of-1 Evidence Chain Explorer."""

import sys
import json
from pathlib import Path

_PRESETS_DIR = Path(__file__).parent / "presets"
_RESULTS_DIR = Path.cwd() / "results"

_FIGURE_DEFS = [
    ("hallmark_bar", "plot_hallmark_bar", "Hallmark perturbation profile", "\U0001f4ca"),
    ("drug_ranking", "plot_drug_ranking", "Top-10 compound ranking", "\U0001f48a"),
    ("evidence_network", "plot_evidence_network", "Drug-PPI-Hallmark alignment", "\U0001f517"),
    ("patient_card", "plot_patient_card", "One-page patient summary", "\U0001f4cb"),
]


def _load_catalog():
    with open(_PRESETS_DIR / "catalog.json", encoding="utf-8") as f:
        return json.load(f)


def _print_banner(version):
    print()
    print("\U0001f9ec SteeraMed Core \u2014 N-of-1 Evidence Chain Explorer")
    print("\u2550" * 51)
    print()


def _print_catalog(catalog):
    print("Select a patient case:")
    print()
    for i, c in enumerate(catalog, 1):
        print(f"  [{i}] {c['emoji']} {c['display']}")
        print(f"      {c['summary']} \u00b7 {c['evidence']}")
        print()
    print(f"Enter choice [1-{len(catalog)}]: ", end="", flush=True)


def _generate_case(entry):
    import matplotlib.pyplot as plt

    case_id = entry["id"]
    json_path = _PRESETS_DIR / "example_patients" / entry["file"]

    print(f"\nLoading {entry['emoji']} {entry['display']}...\n")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for suffix, func_name, desc, icon in _FIGURE_DEFS:
        mod = __import__(f"steeramed_core.viz.{suffix}", fromlist=[func_name])
        func = getattr(mod, func_name)
        fig = func(data)
        out_path = _RESULTS_DIR / f"{case_id}_{suffix}.png"
        fig.savefig(str(out_path), dpi=300, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        generated.append((f"{case_id}_{suffix}.png", desc, icon))

    print(f"\u2705 Generated 4 figures in results/:")
    for fname, desc, icon in generated:
        print(f"  {icon} {fname:40s} \u2014 {desc}")


def main():
    args = sys.argv[1:]
    catalog = _load_catalog()

    if "--list" in args:
        for c in catalog:
            print(f"  {c['id']:12s}  {c['emoji']} {c['display']}")
        return

    if "--all" in args:
        for entry in catalog:
            _generate_case(entry)
            print()
        return

    if "--case" in args:
        idx = args.index("--case")
        if idx + 1 >= len(args):
            print("Error: --case requires an ID argument")
            sys.exit(1)
        case_id = args[idx + 1]
        entry = next((c for c in catalog if c["id"] == case_id), None)
        if entry is None:
            print(f"Error: case '{case_id}' not found in catalog")
            sys.exit(1)
        _generate_case(entry)
        return

    from steeramed_core import __version__

    _print_banner(__version__)
    _print_catalog(catalog)

    choice = input().strip()

    try:
        n = int(choice)
        if 1 <= n <= len(catalog):
            _generate_case(catalog[n - 1])
            return
    except ValueError:
        pass

    entry = next((c for c in catalog if c["id"] == choice), None)
    if entry:
        _generate_case(entry)
        return

    print(f"Invalid choice: {choice}")
    sys.exit(1)


if __name__ == "__main__":
    main()
