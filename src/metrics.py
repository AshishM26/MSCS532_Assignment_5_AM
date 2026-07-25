"""Operation metrics shared by both Quicksort implementations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QuickSortMetrics:
    """Record implementation-level work for one sorting execution.

    A comparison is counted whenever a partition element is compared with its
    pivot. A swap is counted only when two different indexes are exchanged.
    ``pivot_trace`` stores ``(low, high, selected_index)`` for reproducibility.
    """

    comparisons: int = 0
    swaps: int = 0
    partition_calls: int = 0
    logical_recursive_calls: int = 0
    maximum_logical_depth: int = 0
    pivot_selections: int = 0
    pivot_trace: list[tuple[int, int, int]] = field(default_factory=list)

    def reset(self) -> None:
        """Reset all counters and recorded pivot choices."""
        self.comparisons = 0
        self.swaps = 0
        self.partition_calls = 0
        self.logical_recursive_calls = 0
        self.maximum_logical_depth = 0
        self.pivot_selections = 0
        self.pivot_trace.clear()
