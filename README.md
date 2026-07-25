# MSCS532 Assignment 5

- **Student:** Ashish Mahajan
- **Course:** MSCS 532-B01 - Algorithms and Data Structures
- **Instructor:** Dr. Michael Solomon
- **Assignment:** Assignment 5 - Quicksort Algorithm: Implementation, Analysis, and Randomization
- **Repository:** [MSCS532_Assignment_5_AM](https://github.com/AshishM26/MSCS532_Assignment_5_AM)

## Overview

This project implements deterministic and randomized Quicksort using a shared, in-place Lomuto partition function. It analyzes best-, expected-, and worst-case performance and compares both pivot policies on random, sorted, reverse-sorted, and repeated-value inputs.

The assignment requirements and learning objectives are to:

- implement correct deterministic and randomized Quicksort;
- use the final element as the deterministic pivot;
- select each randomized pivot uniformly from the active subarray;
- explain partition correctness and time/space complexity;
- measure runtime, comparisons, swaps, partitions, and logical recursion;
- compare input distributions with reproducible experiments; and
- connect measured behavior to asymptotic analysis without overstating results.

The full discussion is available in [report.md](report.md).

## Algorithm Design

Deterministic Quicksort always uses `values[high]` as the pivot. Randomized Quicksort uses a local `random.Random` instance to choose an inclusive index from `low` through `high`, moves that pivot to `high`, and calls the same Lomuto partition function. Neither algorithm changes global random state.

Lomuto partitioning places values less than or equal to the pivot on its left and greater values on its right. Swaps are counted only when two different indexes are exchanged. Each algorithm supports:

- copy mode, which preserves the input and returns a new list; and
- in-place mode, which rearranges and returns the same list object.

Both versions recursively process the smaller partition and iteratively continue through the larger partition. This preserves the required pivot policies and logical Quicksort decomposition while keeping the physical Python call stack within \(O(\log n)\). It does not change deterministic Quicksort's \(\Theta(n^2)\) worst-case work.

## Difference from Assignment 3

Assignment 3 used first-pivot deterministic Quicksort and randomized Quicksort with three-way partitioning. Assignment 5 is a fresh Chapter 7 implementation: deterministic pivots come from the final position, both algorithms rearrange the input through shared Lomuto partitioning, and duplicate pivot values remain in a two-region partition. Assignment 5 does not import from or depend on Assignment 3.

## Repository Structure

```text
MSCS532_Assignment_5_AM/
├── .gitignore
├── README.md
├── report.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── metrics.py
│   ├── partition.py
│   ├── deterministic_quicksort.py
│   └── randomized_quicksort.py
├── benchmarks/
│   ├── __init__.py
│   └── benchmark_quicksort.py
├── tests/
│   ├── __init__.py
│   ├── test_partition.py
│   ├── test_deterministic_quicksort.py
│   ├── test_randomized_quicksort.py
│   └── test_benchmark_contract.py
└── results/
    ├── quicksort_results.csv
    ├── quicksort_runtime_chart.png
    └── quicksort_comparisons_chart.png
```

## Environment and Setup

- Python 3.11 or later
- `matplotlib` 3.8 or later, below version 4
- Python standard library for algorithms, randomness, testing, timing, CSV output, and statistics

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

The suite contains 55 tests covering partition invariants, edge cases, invalid inputs, copy and in-place behavior, stack safety, seed reproduction, global random-state isolation, and benchmark contracts.

## Running the Benchmark

Run the complete required study with five trials per combination:

```bash
python3 benchmarks/benchmark_quicksort.py
```

Optional smaller runs:

```bash
python3 benchmarks/benchmark_quicksort.py --trials 3
python3 benchmarks/benchmark_quicksort.py --max-size 5000
```

The benchmark uses fixed dataset and pivot seeds, one warm-up, fresh input copies, `time.perf_counter()`, and output verification against Python's `sorted()`. Dataset creation, CSV writing, and chart creation are outside measured execution time.

## Generated Outputs

- `results/quicksort_results.csv`: 48 completed rows covering two algorithms, four distributions, and six sizes from 100 through 10,000.
- `results/quicksort_runtime_chart.png`: median runtime panels by distribution.
- `results/quicksort_comparisons_chart.png`: median comparison-count panels by distribution.

Running a reduced benchmark overwrites these files with the selected subset. Run the default command again to restore the complete assignment results.

## Actual Findings

The size-10,000 results from the current five-trial CSV are:

| Distribution | Deterministic median | Randomized median | Deterministic comparisons | Randomized comparisons |
|---|---:|---:|---:|---:|
| Random | 3.238983 s | 3.224975 s | 155,468 | 155,656 |
| Sorted | 8.466383 s | 3.199326 s | 49,995,000 | 152,462 |
| Reverse sorted | 7.556488 s | 3.234181 s | 49,995,000 | 153,721 |
| Repeated values | 5.194373 s | 5.426506 s | 5,031,031 | 5,051,490 |

In this run, both algorithms behaved similarly on random unique data. Deterministic last-pivot Quicksort showed quadratic comparison growth on sorted and reverse-sorted unique values, while randomized pivot selection remained near the unique-random comparison scale. Repeated values caused millions of comparisons for both versions because two-region Lomuto partitioning does not group all equal keys into a completed middle region.

## Known Limitations

- Results describe one instrumented Python implementation on one machine; no statistical-significance test was performed.
- Metrics and pivot-trace collection add overhead to measured time and memory.
- Lomuto partitioning can create unbalanced subproblems when many values equal the pivot.
- Randomization reduces dependence on input ordering but does not eliminate the mathematical \(\Theta(n^2)\) worst case.
- The implementation does not add hybrid insertion-sort cutoffs, median-of-three pivots, or three-way partitioning because those changes would alter the assigned comparison.

## References

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

Hoare, C. A. R. (1962). Quicksort. *The Computer Journal, 5*(1), 10–16. https://doi.org/10.1093/comjnl/5.1.10

Python Software Foundation. (n.d.). *random — Generate pseudo-random numbers*. https://docs.python.org/3/library/random.html

Python Software Foundation. (n.d.). *time — Time access and conversions*. https://docs.python.org/3/library/time.html
