from pathlib import Path

from evaluation.experiments import run_all_experiments


def test_all_optimization_experiments_return_measurements() -> None:
    report = run_all_experiments(Path(__file__).parents[1] / "data" / "products.csv")
    names = {item["name"] for item in report["experiments"]}
    assert names == {
        "sequential_vs_parallel",
        "retry_strategy",
        "tool_authorization",
        "validation_strategy",
        "ranking_strategy",
        "duplicate_operations",
    }
    for experiment in report["experiments"]:
        assert experiment["baseline"]
        assert experiment["optimized"]
        assert experiment["measurements"]


def test_evaluation_reports_parallel_speedup_and_retry_recovery() -> None:
    report = run_all_experiments(Path(__file__).parents[1] / "data" / "products.csv")
    by_name = {item["name"]: item for item in report["experiments"]}
    assert by_name["sequential_vs_parallel"]["measurements"]["speedup"] >= 0
    retry = by_name["retry_strategy"]["optimized"]
    assert retry["retries"] == 1
    assert retry["recovery_success"] is True
