# MSCS532 Assignment 5

- **Student:** Ashish Mahajan
- **Course:** MSCS 532-B01 - Algorithms and Data Structures
- **Instructor:** Dr. Michael Solomon
- **Assignment:** Assignment 5 - Quicksort Algorithm: Implementation, Analysis, and Randomization
- **Repository:** [MSCS532_Assignment_5_AM](https://github.com/AshishM26/MSCS532_Assignment_5_AM)

## Overview

This project implements deterministic and randomized Quicksort using shared, in-place Lomuto partitioning. It analyzes their time and space complexity and compares both pivot policies on four input distributions.

- Implement final-element deterministic and uniformly randomized pivots.
- Explain correctness and best-, expected-, and worst-case complexity.
- Measure runtime, comparisons, swaps, partitions, and logical depth.
- Compare reproducible random, sorted, reverse-sorted, and repeated-value inputs.

The full discussion is available in [report.md](report.md).

## Algorithm Design

Deterministic Quicksort uses `values[high]` as the pivot. Randomized Quicksort uses a local `random.Random` instance to choose an index from `low` through `high`, moves that pivot to `high`, and calls the same partition function. Lomuto partitioning places values less than or equal to the pivot on its left and greater values on its right.

Each algorithm supports:

- copy mode, which preserves the input and returns a new list; and
- in-place mode, which rearranges and returns the same list object.

Both versions recurse through the smaller partition and iterate through the larger one. This protects the physical Python stack without changing the logical decomposition or deterministic \(\Theta(n^2)\) worst case.

## Difference from Assignment 3

Assignment 3 used first-pivot and three-way partitioning. Assignment 5 is an independent implementation using final-element deterministic pivots and two-region Lomuto partitioning.

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

The suite contains 55 tests covering correctness, validation, metrics, stack safety, reproducibility, and benchmark contracts.

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

The benchmark uses fixed seeds, one warm-up, five fresh timed trials, `time.perf_counter()`, and verification against `sorted()`.

## Generated Outputs

- `results/quicksort_results.csv`: 48 completed benchmark rows.
- `results/quicksort_runtime_chart.png`: median runtime by distribution.
- `results/quicksort_comparisons_chart.png`: median comparisons by distribution.

Running a reduced benchmark overwrites these files with the selected subset. Run the default command again to restore the complete assignment results.

## Actual Findings

The size-10,000 results from the current five-trial CSV are:

| Distribution | Deterministic median | Randomized median | Deterministic comparisons | Randomized comparisons |
|---|---:|---:|---:|---:|
| Random | 3.238983 s | 3.224975 s | 155,468 | 155,656 |
| Sorted | 8.466383 s | 3.199326 s | 49,995,000 | 152,462 |
| Reverse sorted | 7.556488 s | 3.234181 s | 49,995,000 | 153,721 |
| Repeated values | 5.194373 s | 5.426506 s | 5,031,031 | 5,051,490 |

In this run, both algorithms behaved similarly on random unique data. Deterministic ordered inputs showed quadratic growth, while randomized ordered inputs remained near the random-input comparison scale. Repeated values remained costly because two-region Lomuto partitioning does not group equal keys.

## Known Limitations

- Results describe one instrumented Python implementation; no significance test was performed.
- Metrics and pivot traces add time and memory overhead.
- Duplicate values can unbalance two-region Lomuto partitioning.
- Randomization does not eliminate the \(\Theta(n^2)\) worst case.

## References

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

Hoare, C. A. R. (1962). Quicksort. *The Computer Journal, 5*(1), 10–16. https://doi.org/10.1093/comjnl/5.1.10

Python Software Foundation. (n.d.). *random — Generate pseudo-random numbers*. https://docs.python.org/3/library/random.html

Python Software Foundation. (n.d.). *time — Time access and conversions*. https://docs.python.org/3/library/time.html
