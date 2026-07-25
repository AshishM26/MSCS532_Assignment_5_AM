"""Contract tests for benchmark helpers without running the full study."""

import csv
from pathlib import Path
import tempfile
import unittest

from benchmarks.benchmark_quicksort import (
    COMPARISONS_CHART_PATH,
    CSV_FIELDNAMES,
    CSV_PATH,
    DATASET_TYPES,
    PROJECT_ROOT,
    RUNTIME_CHART_PATH,
    create_charts,
    generate_dataset,
    run_benchmark,
    run_benchmark_case,
    validate_trial_count,
    write_results_csv,
)
from src.metrics import QuickSortMetrics


class BenchmarkContractTests(unittest.TestCase):
    def test_dataset_generation_is_deterministic(self) -> None:
        first = generate_dataset("random", 100, seed=42)
        second = generate_dataset("random", 100, seed=42)
        self.assertEqual(first, second)

    def test_all_required_distributions_are_generated(self) -> None:
        for dataset_type in DATASET_TYPES:
            with self.subTest(dataset_type=dataset_type):
                values = generate_dataset(dataset_type, 100)
                self.assertEqual(len(values), 100)
        self.assertEqual(generate_dataset("sorted", 5), [0, 1, 2, 3, 4])
        self.assertEqual(generate_dataset("reverse_sorted", 5), [5, 4, 3, 2, 1])
        self.assertTrue(
            all(0 <= value <= 9 for value in generate_dataset("repeated_values", 100))
        )

    def test_algorithms_receive_independent_input_copies(self) -> None:
        received_lists: list[list[int]] = []

        def recording_runner(
            values: list[int], unused_seed: int
        ) -> tuple[list[int], QuickSortMetrics]:
            del unused_seed
            received_lists.append(values)
            values[:] = sorted(values)
            return values, QuickSortMetrics()

        dataset = [4, 1, 3, 2]
        row = run_benchmark_case(
            "Recording Algorithm",
            recording_runner,
            "random",
            dataset,
            trials=3,
            pivot_seed=1,
        )
        self.assertEqual(row["status"], "completed")
        self.assertEqual(len(received_lists), 4)
        self.assertEqual(len({id(values) for values in received_lists}), 4)
        self.assertEqual(dataset, [4, 1, 3, 2])

    def test_csv_field_names_match_schema(self) -> None:
        expected = [
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
        self.assertEqual(CSV_FIELDNAMES, expected)

    def test_trial_validation_rejects_nonpositive_values(self) -> None:
        for value in [0, -1, True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_trial_count(value)

    def test_incorrect_output_is_recorded_as_failure(self) -> None:
        def incorrect_runner(
            values: list[int], unused_seed: int
        ) -> tuple[list[int], QuickSortMetrics]:
            del unused_seed
            return values, QuickSortMetrics()

        row = run_benchmark_case(
            "Incorrect Algorithm",
            incorrect_runner,
            "reverse_sorted",
            [3, 2, 1],
            trials=2,
            pivot_seed=1,
        )
        self.assertEqual(row["status"], "failed")
        self.assertIn("did not match", str(row["error_message"]))

    def test_result_paths_are_inside_repository(self) -> None:
        for path in [CSV_PATH, RUNTIME_CHART_PATH, COMPARISONS_CHART_PATH]:
            with self.subTest(path=path.name):
                relative = path.relative_to(PROJECT_ROOT)
                self.assertFalse(relative.is_absolute())
                self.assertEqual(relative.parts[0], "results")

    def test_chart_generation_accepts_synthetic_rows(self) -> None:
        rows = []
        for dataset_type in DATASET_TYPES:
            for algorithm in [
                "Deterministic Last-Pivot Quicksort",
                "Randomized Quicksort",
            ]:
                rows.append(
                    {
                        "algorithm": algorithm,
                        "dataset_type": dataset_type,
                        "size": 10,
                        "median_time_seconds": 0.001,
                        "comparisons": 25,
                        "status": "completed",
                    }
                )

        with tempfile.TemporaryDirectory() as directory:
            runtime_path = Path(directory) / "runtime.png"
            comparisons_path = Path(directory) / "comparisons.png"
            create_charts(rows, runtime_path, comparisons_path)
            self.assertGreater(runtime_path.stat().st_size, 0)
            self.assertGreater(comparisons_path.stat().st_size, 0)

    def test_csv_writer_uses_documented_header(self) -> None:
        row = {field: "" for field in CSV_FIELDNAMES}
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "results.csv"
            write_results_csv([row], output_path)
            with output_path.open(newline="", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                self.assertEqual(reader.fieldnames, CSV_FIELDNAMES)
                self.assertEqual(len(list(reader)), 1)

    def test_max_size_filters_required_sizes(self) -> None:
        rows = run_benchmark(trials=1, max_size=100, show_progress=False)
        self.assertEqual(len(rows), 8)
        self.assertEqual({row["size"] for row in rows}, {100})


if __name__ == "__main__":
    unittest.main()
