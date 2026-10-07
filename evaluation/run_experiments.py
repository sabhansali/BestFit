"""Command-line entry point for the optimization experiment report."""

import json
from pathlib import Path

from evaluation.experiments import run_all_experiments


if __name__ == "__main__":
    report = run_all_experiments(Path(__file__).parents[1] / "data" / "products.csv")
    print(json.dumps(report, indent=2))
