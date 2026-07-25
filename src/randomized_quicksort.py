"""Randomized Lomuto Quicksort with isolated reproducible randomness."""

from __future__ import annotations

import random

from src.metrics import QuickSortMetrics
from src.partition import _swap, lomuto_partition


def _validate_sort_arguments(values: list[int], in_place: bool) -> None:
    if not isinstance(values, list):
        raise TypeError("values must be a list of integers")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("every value must be an integer and not a Boolean")
    if not isinstance(in_place, bool):
        raise TypeError("in_place must be a Boolean")


def randomized_quicksort(
    values: list[int],
    *,
    seed: int | None = None,
    in_place: bool = False,
) -> list[int]:
    """Return values sorted with uniformly selected subarray pivots.

    A local ``random.Random`` instance makes a supplied seed reproducible
    without changing module-global random state.
    """
    result, _ = randomized_quicksort_measured(
        values, seed=seed, in_place=in_place
    )
    return result


def randomized_quicksort_measured(
    values: list[int],
    *,
    seed: int | None = None,
    in_place: bool = False,
) -> tuple[list[int], QuickSortMetrics]:
    """Return the sorted values and randomized operation metrics."""
    _validate_sort_arguments(values, in_place)
    items = values if in_place else list(values)
    metrics = QuickSortMetrics()
    random_generator = random.Random(seed)

    def sort_subarray(low: int, high: int, logical_depth: int) -> None:
        while True:
            metrics.logical_recursive_calls += 1
            metrics.maximum_logical_depth = max(
                metrics.maximum_logical_depth, logical_depth
            )
            if low >= high:
                return

            selected_index = random_generator.randint(low, high)
            metrics.pivot_selections += 1
            metrics.pivot_trace.append((low, high, selected_index))
            _swap(items, selected_index, high, metrics)
            pivot_index = lomuto_partition(items, low, high, metrics)

            left_low, left_high = low, pivot_index - 1
            right_low, right_high = pivot_index + 1, high
            left_size = max(0, left_high - left_low + 1)
            right_size = max(0, right_high - right_low + 1)
            next_depth = logical_depth + 1

            if left_size < right_size:
                sort_subarray(left_low, left_high, next_depth)
                low, high = right_low, right_high
            else:
                sort_subarray(right_low, right_high, next_depth)
                low, high = left_low, left_high
            logical_depth = next_depth

    sort_subarray(0, len(items) - 1, 1)
    return items, metrics
