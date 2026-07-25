"""Shared in-place Lomuto partition implementation."""

from __future__ import annotations

from src.metrics import QuickSortMetrics


def _swap(
    values: list[int],
    first_index: int,
    second_index: int,
    metrics: QuickSortMetrics | None = None,
) -> None:
    """Exchange different indexes and update the optional swap count."""
    if first_index == second_index:
        return
    values[first_index], values[second_index] = (
        values[second_index],
        values[first_index],
    )
    if metrics is not None:
        metrics.swaps += 1


def _validate_partition_arguments(
    values: list[int],
    low: int,
    high: int,
    metrics: QuickSortMetrics | None,
) -> None:
    if not isinstance(values, list):
        raise TypeError("values must be a list of integers")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("every value must be an integer and not a Boolean")
    if (
        isinstance(low, bool)
        or isinstance(high, bool)
        or not isinstance(low, int)
        or not isinstance(high, int)
    ):
        raise TypeError("low and high must be integer indexes")
    if low < 0 or high >= len(values) or low > high:
        raise IndexError("partition bounds must satisfy 0 <= low <= high < len(values)")
    if metrics is not None and not isinstance(metrics, QuickSortMetrics):
        raise TypeError("metrics must be QuickSortMetrics or None")


def lomuto_partition(
    values: list[int],
    low: int,
    high: int,
    metrics: QuickSortMetrics | None = None,
) -> int:
    """Partition ``values[low:high + 1]`` around ``values[high]``.

    Values at or left of the returned pivot index are less than or equal to the
    pivot; values to its right are greater. Elements outside the supplied
    inclusive bounds are not accessed or modified.
    """
    _validate_partition_arguments(values, low, high, metrics)
    if metrics is not None:
        metrics.partition_calls += 1

    pivot = values[high]
    smaller_or_equal_end = low - 1
    for current in range(low, high):
        if metrics is not None:
            metrics.comparisons += 1
        if values[current] <= pivot:
            smaller_or_equal_end += 1
            _swap(values, smaller_or_equal_end, current, metrics)

    pivot_index = smaller_or_equal_end + 1
    _swap(values, pivot_index, high, metrics)
    return pivot_index
