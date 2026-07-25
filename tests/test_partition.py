"""Tests for shared Lomuto partition behavior and metrics."""

import unittest

from src.metrics import QuickSortMetrics
from src.partition import lomuto_partition


class LomutoPartitionTests(unittest.TestCase):
    def assert_partition_invariant(
        self, values: list[int], low: int, high: int, pivot_index: int
    ) -> None:
        pivot = values[pivot_index]
        self.assertTrue(all(value <= pivot for value in values[low:pivot_index]))
        self.assertTrue(all(value > pivot for value in values[pivot_index + 1 : high + 1]))

    def test_unsorted_list(self) -> None:
        values = [8, 3, 1, 7, 4, 2, 6, 5]
        pivot_index = lomuto_partition(values, 0, len(values) - 1)
        self.assertEqual(values[pivot_index], 5)
        self.assert_partition_invariant(values, 0, len(values) - 1, pivot_index)

    def test_sorted_list(self) -> None:
        values = [1, 2, 3, 4, 5]
        pivot_index = lomuto_partition(values, 0, 4)
        self.assertEqual(pivot_index, 4)
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_reverse_sorted_list(self) -> None:
        values = [5, 4, 3, 2, 1]
        pivot_index = lomuto_partition(values, 0, 4)
        self.assertEqual(pivot_index, 0)
        self.assertEqual(values[0], 1)

    def test_repeated_pivot_values_go_left(self) -> None:
        values = [4, 2, 4, 1, 4]
        pivot_index = lomuto_partition(values, 0, 4)
        self.assertEqual(pivot_index, 4)
        self.assert_partition_invariant(values, 0, 4, pivot_index)

    def test_two_element_list(self) -> None:
        values = [2, 1]
        pivot_index = lomuto_partition(values, 0, 1)
        self.assertEqual(values, [1, 2])
        self.assertEqual(pivot_index, 0)

    def test_returned_index_is_within_bounds(self) -> None:
        values = [9, 2, 6, 4, 7, 3]
        pivot_index = lomuto_partition(values, 1, 4)
        self.assertGreaterEqual(pivot_index, 1)
        self.assertLessEqual(pivot_index, 4)

    def test_left_and_right_invariants(self) -> None:
        values = [10, -3, 7, 7, 2, 9, 5]
        pivot_index = lomuto_partition(values, 0, 6)
        self.assert_partition_invariant(values, 0, 6, pivot_index)

    def test_comparisons_equal_nonpivot_elements(self) -> None:
        metrics = QuickSortMetrics()
        lomuto_partition([5, 1, 4, 2, 3], 0, 4, metrics)
        self.assertEqual(metrics.comparisons, 4)
        self.assertEqual(metrics.partition_calls, 1)

    def test_swap_count_omits_self_swaps(self) -> None:
        sorted_metrics = QuickSortMetrics()
        lomuto_partition([1, 2], 0, 1, sorted_metrics)
        self.assertEqual(sorted_metrics.swaps, 0)

        reverse_metrics = QuickSortMetrics()
        lomuto_partition([2, 1], 0, 1, reverse_metrics)
        self.assertEqual(reverse_metrics.swaps, 1)

    def test_invalid_bounds_are_rejected(self) -> None:
        values = [3, 2, 1]
        for low, high in [(-1, 2), (0, 3), (2, 1)]:
            with self.subTest(low=low, high=high):
                with self.assertRaises(IndexError):
                    lomuto_partition(values, low, high)

    def test_values_outside_bounds_are_unchanged(self) -> None:
        values = [99, 4, 1, 3, 88]
        lomuto_partition(values, 1, 3)
        self.assertEqual(values[0], 99)
        self.assertEqual(values[4], 88)

    def test_invalid_argument_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            lomuto_partition((3, 2, 1), 0, 2)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            lomuto_partition([3, True, 1], 0, 2)
        with self.assertRaises(TypeError):
            lomuto_partition([3, 2, 1], 0.0, 2)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            lomuto_partition([3, 2, 1], 0, 2, object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
