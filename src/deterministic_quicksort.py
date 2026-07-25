"""Deterministic last-pivot Quicksort using shared Lomuto partitioning."""

from __future__ import annotations

from src.metrics import QuickSortMetrics
from src.partition import lomuto_partition


def _validate_sort_arguments(values: list[int], in_place: bool) -> None:
    if not isinstance(values, list):
        raise TypeError("values must be a list of integers")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("every value must be an integer and not a Boolean")
    if not isinstance(in_place, bool):
        raise TypeError("in_place must be a Boolean")


def deterministic_quicksort(
    values: list[int],
    *,
    in_place: bool = False,
) -> list[int]:
    """Return values in ascending order using each subarray's final pivot.

    Copy mode preserves the caller's list. In-place mode rearranges and returns
    that same list object.
    """
    result, _ = deterministic_quicksort_measured(values, in_place=in_place)
    return result


def deterministic_quicksort_measured(
    values: list[int],
    *,
    in_place: bool = False,
) -> tuple[list[int], QuickSortMetrics]:
    """Return the sorted values and deterministic operation metrics."""
    _validate_sort_arguments(values, in_place)
    items = values if in_place else list(values)
    metrics = QuickSortMetrics()

    def sort_subarray(low: int, high: int, logical_depth: int) -> None:
        while True:
            metrics.logical_recursive_calls += 1
            metrics.maximum_logical_depth = max(
                metrics.maximum_logical_depth, logical_depth
            )
            if low >= high:
                return

            metrics.pivot_selections += 1
            metrics.pivot_trace.append((low, high, high))
            pivot_index = lomuto_partition(items, low, high, metrics)

            left_low, left_high = low, pivot_index - 1
            right_low, right_high = pivot_index + 1, high
            left_size = max(0, left_high - left_low + 1)
            right_size = max(0, right_high - right_low + 1)
            next_depth = logical_depth + 1

            # Only the smaller side consumes another physical Python frame.
            if left_size < right_size:
                sort_subarray(left_low, left_high, next_depth)
                low, high = right_low, right_high
            else:
                sort_subarray(right_low, right_high, next_depth)
                low, high = left_low, left_high
            logical_depth = next_depth

    sort_subarray(0, len(items) - 1, 1)
    return items, metrics
