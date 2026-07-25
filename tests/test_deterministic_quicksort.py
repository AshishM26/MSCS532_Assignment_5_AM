"""Tests for deterministic last-pivot Lomuto Quicksort."""

import random
import unittest

from src.deterministic_quicksort import (
    deterministic_quicksort,
    deterministic_quicksort_measured,
)


class DeterministicQuickSortTests(unittest.TestCase):
    def test_empty_list(self) -> None:
        self.assertEqual(deterministic_quicksort([]), [])

    def test_single_element(self) -> None:
        self.assertEqual(deterministic_quicksort([7]), [7])

    def test_two_values(self) -> None:
        self.assertEqual(deterministic_quicksort([9, 2]), [2, 9])

    def test_random_values(self) -> None:
        values = random.Random(532).sample(range(-500, 500), 100)
        self.assertEqual(deterministic_quicksort(values), sorted(values))

    def test_sorted_values(self) -> None:
        values = list(range(50))
        self.assertEqual(deterministic_quicksort(values), values)

    def test_reverse_sorted_values(self) -> None:
        values = list(range(50, 0, -1))
        self.assertEqual(deterministic_quicksort(values), sorted(values))

    def test_repeated_values(self) -> None:
        values = [4, 1, 4, 2, 4, 1, 3, 3]
        self.assertEqual(deterministic_quicksort(values), sorted(values))

    def test_all_equal_values(self) -> None:
        values = [6] * 80
        self.assertEqual(deterministic_quicksort(values), values)

    def test_negative_values(self) -> None:
        values = [-4, -10, -1, -7, -3]
        self.assertEqual(deterministic_quicksort(values), sorted(values))

    def test_mixed_values(self) -> None:
        values = [0, 12, -5, 8, -2, 12, 3]
        self.assertEqual(deterministic_quicksort(values), sorted(values))

    def test_copy_mode_preserves_input(self) -> None:
        values = [31, 41, 59, 26, 41, 58]
        original = list(values)
        result = deterministic_quicksort(values)
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_in_place_mode_returns_same_object(self) -> None:
        values = [4, 2, 5, 1, 3]
        result = deterministic_quicksort(values, in_place=True)
        self.assertIs(result, values)
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_invalid_container_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            deterministic_quicksort((3, 2, 1))  # type: ignore[arg-type]

    def test_invalid_element_and_boolean_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            deterministic_quicksort([3, "2", 1])  # type: ignore[list-item]
        with self.assertRaises(TypeError):
            deterministic_quicksort([3, True, 1])

    def test_invalid_in_place_flag_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            deterministic_quicksort([3, 2, 1], in_place=1)  # type: ignore[arg-type]

    def test_metrics_are_populated_consistently(self) -> None:
        _, metrics = deterministic_quicksort_measured([5, 4, 3, 2, 1])
        self.assertGreater(metrics.comparisons, 0)
        self.assertEqual(metrics.partition_calls, metrics.pivot_selections)
        self.assertEqual(len(metrics.pivot_trace), metrics.pivot_selections)
        self.assertGreater(metrics.logical_recursive_calls, metrics.partition_calls)

    def test_ordered_input_has_more_work_than_shuffled_input(self) -> None:
        ordered = list(range(200))
        shuffled = list(ordered)
        random.Random(32).shuffle(shuffled)
        _, ordered_metrics = deterministic_quicksort_measured(ordered)
        _, shuffled_metrics = deterministic_quicksort_measured(shuffled)
        self.assertGreater(ordered_metrics.comparisons, shuffled_metrics.comparisons)
        self.assertGreater(
            ordered_metrics.maximum_logical_depth,
            shuffled_metrics.maximum_logical_depth,
        )

    def test_large_ordered_input_is_recursion_safe(self) -> None:
        values = list(range(1500))
        result, metrics = deterministic_quicksort_measured(values)
        self.assertEqual(result, values)
        self.assertEqual(metrics.maximum_logical_depth, len(values))

    def test_identical_runs_have_identical_metrics(self) -> None:
        values = [9, 1, 8, 2, 7, 3, 6, 4, 5]
        first_result, first_metrics = deterministic_quicksort_measured(values)
        second_result, second_metrics = deterministic_quicksort_measured(values)
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_metrics, second_metrics)


if __name__ == "__main__":
    unittest.main()
