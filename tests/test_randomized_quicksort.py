"""Tests for randomized Lomuto Quicksort and seed isolation."""

import random
import unittest

from src.randomized_quicksort import (
    randomized_quicksort,
    randomized_quicksort_measured,
)


class RandomizedQuickSortTests(unittest.TestCase):
    def test_required_edge_cases(self) -> None:
        cases = [
            [],
            [1],
            [2, 1],
            list(range(20)),
            list(range(20, 0, -1)),
            [4, 1, 4, 2, 4, 1],
            [8] * 30,
            [-4, -2, -9, -1],
            [0, 8, -3, 5, -1],
        ]
        for values in cases:
            with self.subTest(values=values[:5]):
                self.assertEqual(
                    randomized_quicksort(values, seed=532), sorted(values)
                )

    def test_copy_mode_preserves_input(self) -> None:
        values = [31, 41, 59, 26, 41, 58]
        original = list(values)
        result = randomized_quicksort(values, seed=10)
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_in_place_mode_returns_same_object(self) -> None:
        values = [5, 3, 1, 4, 2]
        result = randomized_quicksort(values, seed=10, in_place=True)
        self.assertIs(result, values)
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_fixed_seed_reproduces_metrics_and_pivots(self) -> None:
        values = list(range(50, 0, -1))
        first_result, first_metrics = randomized_quicksort_measured(values, seed=77)
        second_result, second_metrics = randomized_quicksort_measured(values, seed=77)
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_metrics, second_metrics)
        self.assertEqual(first_metrics.pivot_trace, second_metrics.pivot_trace)

    def test_different_seeds_produce_correct_output(self) -> None:
        values = list(range(60, 0, -1))
        for seed in [1, 2, 3, 4]:
            with self.subTest(seed=seed):
                self.assertEqual(
                    randomized_quicksort(values, seed=seed), sorted(values)
                )

    def test_different_seeds_can_change_metrics(self) -> None:
        values = list(range(100))
        _, first_metrics = randomized_quicksort_measured(values, seed=1)
        _, second_metrics = randomized_quicksort_measured(values, seed=2)
        self.assertNotEqual(first_metrics.pivot_trace, second_metrics.pivot_trace)
        self.assertNotEqual(first_metrics.comparisons, second_metrics.comparisons)

    def test_global_random_state_is_unchanged(self) -> None:
        random.seed(2026)
        state_before = random.getstate()
        randomized_quicksort([5, 1, 4, 2, 3], seed=99)
        self.assertEqual(random.getstate(), state_before)

    def test_invalid_container_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            randomized_quicksort((3, 2, 1), seed=1)  # type: ignore[arg-type]

    def test_invalid_elements_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            randomized_quicksort([3, 2.0, 1], seed=1)  # type: ignore[list-item]
        with self.assertRaises(TypeError):
            randomized_quicksort([3, False, 1], seed=1)

    def test_invalid_in_place_flag_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            randomized_quicksort([3, 2, 1], seed=1, in_place="yes")  # type: ignore[arg-type]

    def test_large_sorted_input_is_recursion_safe(self) -> None:
        values = list(range(1500))
        self.assertEqual(randomized_quicksort(values, seed=532), values)

    def test_pivot_indexes_stay_inside_active_subarray(self) -> None:
        _, metrics = randomized_quicksort_measured(list(range(100)), seed=12)
        self.assertTrue(metrics.pivot_trace)
        for low, high, selected in metrics.pivot_trace:
            self.assertLessEqual(low, selected)
            self.assertLessEqual(selected, high)

    def test_pivot_and_partition_counts_match(self) -> None:
        _, metrics = randomized_quicksort_measured([7, 2, 9, 1, 5], seed=8)
        self.assertEqual(metrics.pivot_selections, metrics.partition_calls)
        self.assertEqual(len(metrics.pivot_trace), metrics.pivot_selections)

    def test_random_random_instance_seed_types_are_supported(self) -> None:
        values = [4, 2, 3, 1]
        self.assertEqual(
            randomized_quicksort(values, seed="assignment-5"), [1, 2, 3, 4]
        )


if __name__ == "__main__":
    unittest.main()
