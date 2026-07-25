"""Benchmark deterministic and randomized Lomuto Quicksort."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import random
import statistics
import sys
import time
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.deterministic_quicksort import deterministic_quicksort_measured
from src.metrics import QuickSortMetrics
from src.randomized_quicksort import randomized_quicksort_measured


DATASET_SIZES = [100, 1000, 3500, 5000, 7000, 10000]
DATASET_TYPES = ["random", "sorted", "reverse_sorted", "repeated_values"]
DEFAULT_TRIALS = 5
DATASET_SEED = 53205
PIVOT_SEED = 104729
RESULTS_DIRECTORY = PROJECT_ROOT / "results"
CSV_PATH = RESULTS_DIRECTORY / "quicksort_results.csv"
RUNTIME_CHART_PATH = RESULTS_DIRECTORY / "quicksort_runtime_chart.png"
COMPARISONS_CHART_PATH = RESULTS_DIRECTORY / "quicksort_comparisons_chart.png"

CSV_FIELDNAMES = [
    "algorithm",
    "dataset_type",
    "size",
    "trial_count",
    "median_time_seconds",
    "mean_time_seconds",
    "standard_deviation_seconds",
    "minimum_time_seconds",
    "maximum_time_seconds",
    "comparisons",
    "swaps",
    "partition_calls",
    "logical_recursive_calls",
    "maximum_logical_depth",
    "pivot_selections",
    "status",
    "error_message",
]

AlgorithmRunner = Callable[
    [list[int], int], tuple[list[int], QuickSortMetrics]
]


def validate_trial_count(trials: int) -> None:
    """Require a positive integer number of measured trials."""
    if isinstance(trials, bool) or not isinstance(trials, int) or trials <= 0:
        raise ValueError("trials must be a positive integer")


def generate_dataset(
    dataset_type: str,
    size: int,
    seed: int = DATASET_SEED,
) -> list[int]:
    """Create one deterministic input distribution."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError("size must be a nonnegative integer")

    generator = random.Random(seed + size)
    if dataset_type == "random":
        return generator.sample(range(-20 * size, 20 * size + 1), size)
    if dataset_type == "sorted":
        return list(range(size))
    if dataset_type == "reverse_sorted":
        return list(range(size, 0, -1))
    if dataset_type == "repeated_values":
        return [generator.randrange(10) for _ in range(size)]
    raise ValueError(f"unknown dataset type: {dataset_type}")


def _deterministic_runner(
    values: list[int], unused_seed: int
) -> tuple[list[int], QuickSortMetrics]:
    del unused_seed
    return deterministic_quicksort_measured(values, in_place=True)


def _randomized_runner(
    values: list[int], seed: int
) -> tuple[list[int], QuickSortMetrics]:
    return randomized_quicksort_measured(values, seed=seed, in_place=True)


def _median_count(metrics: list[QuickSortMetrics], attribute: str) -> int | str:
    if not metrics:
        return ""
    return int(statistics.median(getattr(item, attribute) for item in metrics))


def run_benchmark_case(
    algorithm_name: str,
    runner: AlgorithmRunner,
    dataset_type: str,
    dataset: list[int],
    trials: int,
    pivot_seed: int,
) -> dict[str, object]:
    """Run one warm-up and timed trials, returning a complete CSV row."""
    validate_trial_count(trials)
    expected = sorted(dataset)
    durations: list[float] = []
    measured_metrics: list[QuickSortMetrics] = []
    status = "completed"
    error_message = ""

    try:
        warmup_result, _ = runner(list(dataset), pivot_seed)
        if warmup_result != expected:
            raise RuntimeError("warm-up output did not match Python sorted()")

        for trial_index in range(trials):
            trial_values = list(dataset)
            trial_seed = pivot_seed + trial_index
            start = time.perf_counter()
            result, metrics = runner(trial_values, trial_seed)
            duration = time.perf_counter() - start
            if result != expected:
                raise RuntimeError(
                    f"trial {trial_index + 1} output did not match Python sorted()"
                )
            durations.append(duration)
            measured_metrics.append(metrics)
    except Exception as error:
        status = "failed"
        error_message = f"{type(error).__name__}: {error}"

    return {
        "algorithm": algorithm_name,
        "dataset_type": dataset_type,
        "size": len(dataset),
        "trial_count": len(durations),
        "median_time_seconds": statistics.median(durations) if durations else "",
        "mean_time_seconds": statistics.mean(durations) if durations else "",
        "standard_deviation_seconds": (
            statistics.stdev(durations) if len(durations) > 1 else 0.0
        ),
        "minimum_time_seconds": min(durations) if durations else "",
        "maximum_time_seconds": max(durations) if durations else "",
        "comparisons": _median_count(measured_metrics, "comparisons"),
        "swaps": _median_count(measured_metrics, "swaps"),
        "partition_calls": _median_count(measured_metrics, "partition_calls"),
        "logical_recursive_calls": _median_count(
            measured_metrics, "logical_recursive_calls"
        ),
        "maximum_logical_depth": _median_count(
            measured_metrics, "maximum_logical_depth"
        ),
        "pivot_selections": _median_count(measured_metrics, "pivot_selections"),
        "status": status,
        "error_message": error_message,
    }


def run_benchmark(
    trials: int = DEFAULT_TRIALS,
    max_size: int | None = None,
    *,
    show_progress: bool = True,
) -> list[dict[str, object]]:
    """Run all selected algorithm, distribution, and size combinations."""
    validate_trial_count(trials)
    if max_size is not None and (
        isinstance(max_size, bool) or not isinstance(max_size, int) or max_size <= 0
    ):
        raise ValueError("max_size must be a positive integer")

    sizes = [
        size for size in DATASET_SIZES if max_size is None or size <= max_size
    ]
    if not sizes:
        raise ValueError("max_size excludes every required dataset size")

    algorithms = [
        ("Deterministic Last-Pivot Quicksort", _deterministic_runner),
        ("Randomized Quicksort", _randomized_runner),
    ]
    rows: list[dict[str, object]] = []

    for dataset_type in DATASET_TYPES:
        for size in sizes:
            dataset = generate_dataset(dataset_type, size)
            for algorithm_name, runner in algorithms:
                if show_progress:
                    print(
                        f"Running {algorithm_name:38} "
                        f"{dataset_type:16} n={size:5} trials={trials}",
                        flush=True,
                    )
                row = run_benchmark_case(
                    algorithm_name,
                    runner,
                    dataset_type,
                    dataset,
                    trials,
                    PIVOT_SEED + size * 10,
                )
                rows.append(row)
                if show_progress:
                    print(
                        f"  status={row['status']} "
                        f"median={row['median_time_seconds']} "
                        f"comparisons={row['comparisons']}",
                        flush=True,
                    )
    return rows


def write_results_csv(
    rows: list[dict[str, object]], output_path: Path = CSV_PATH
) -> None:
    """Write benchmark rows with the documented schema."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=CSV_FIELDNAMES, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def _completed_rows(
    rows: list[dict[str, object]], dataset_type: str, algorithm: str
) -> list[dict[str, object]]:
    return sorted(
        (
            row
            for row in rows
            if row["dataset_type"] == dataset_type
            and row["algorithm"] == algorithm
            and row["status"] == "completed"
        ),
        key=lambda row: int(row["size"]),
    )


def create_charts(
    rows: list[dict[str, object]],
    runtime_path: Path = RUNTIME_CHART_PATH,
    comparisons_path: Path = COMPARISONS_CHART_PATH,
) -> None:
    """Generate distribution panels for runtime and comparison growth."""
    algorithms = [
        "Deterministic Last-Pivot Quicksort",
        "Randomized Quicksort",
    ]

    for metric, y_label, title, output_path in [
        (
            "median_time_seconds",
            "Median time (seconds)",
            "Deterministic and Randomized Quicksort Runtime",
            runtime_path,
        ),
        (
            "comparisons",
            "Median comparisons",
            "Deterministic and Randomized Quicksort Comparisons",
            comparisons_path,
        ),
    ]:
        figure, axes = plt.subplots(2, 2, figsize=(12, 8))
        for axis, dataset_type in zip(axes.flat, DATASET_TYPES):
            for algorithm in algorithms:
                matching = _completed_rows(rows, dataset_type, algorithm)
                axis.plot(
                    [int(row["size"]) for row in matching],
                    [float(row[metric]) for row in matching],
                    marker="o",
                    label=algorithm,
                )
            axis.set_title(dataset_type.replace("_", " ").title())
            axis.set_xlabel("Input size")
            axis.set_ylabel(y_label)
            axis.grid(alpha=0.3)

        axes[0, 0].legend(loc="upper left")
        figure.suptitle(title, y=0.995)
        figure.tight_layout(rect=(0, 0, 1, 0.94))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output_path, dpi=160)
        plt.close(figure)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trials",
        type=int,
        default=DEFAULT_TRIALS,
        help="measured trials per combination (default: 5)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=None,
        help="largest required dataset size to include",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    rows = run_benchmark(arguments.trials, arguments.max_size)
    write_results_csv(rows)
    create_charts(rows)
    completed = sum(row["status"] == "completed" for row in rows)
    print(
        f"\nSaved {len(rows)} rows ({completed} completed) to "
        f"{CSV_PATH.relative_to(PROJECT_ROOT)}"
    )
    print(f"Saved runtime chart to {RUNTIME_CHART_PATH.relative_to(PROJECT_ROOT)}")
    print(
        "Saved comparison chart to "
        f"{COMPARISONS_CHART_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
