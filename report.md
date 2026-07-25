# Assignment 5 Report

## Quicksort Algorithm: Implementation, Analysis, and Randomization

- **Student:** Ashish Mahajan
- **Course:** MSCS 532-B01 - Algorithms and Data Structures
- **Instructor:** Dr. Michael Solomon
- **Repository:** [MSCS532_Assignment_5_AM](https://github.com/AshishM26/MSCS532_Assignment_5_AM)

## 1. Introduction

Quicksort orders values by selecting a pivot, partitioning the current region around that pivot, and solving the two resulting subproblems. Its practical efficiency depends strongly on partition balance. This project compares a deterministic final-element pivot with a uniformly selected random pivot while holding the in-place Lomuto partition method constant. The comparison combines recurrence analysis, correctness reasoning, instrumented operation counts, and reproducible timing.

## 2. Assignment Objectives

The objectives were to implement both Quicksort variants clearly, analyze best/average/worst time and space behavior, explain how randomization affects pivot quality, and empirically compare the algorithms across multiple sizes and input distributions. The implementation also had to remain correct on edge cases, preserve inputs in copy mode, support true in-place mode, and avoid Python recursion-limit failures on adversarial ordered data.

## 3. Deterministic Quicksort Design

Deterministic Quicksort always selects the final active element, `values[high]`, as the pivot. It never substitutes a middle, first, random, or median-of-three pivot. After Lomuto partition returns the pivot's final index, the algorithm sorts the regions before and after that index.

To protect Python's physical call stack, the implementation recursively processes the smaller region and continues iteratively through the larger region. The pivot rule, partition sequence, comparisons, and logical recursion tree remain those of last-pivot Quicksort. Consequently, the optimization prevents `RecursionError` but does not reduce worst-case quadratic work.

## 4. Lomuto Partition Design

The shared partition function uses `values[high]` as the pivot. It scans indexes `low` through `high - 1` once. When a value is less than or equal to the pivot, the boundary of the left region advances and the value is exchanged into that region. Finally, the pivot is exchanged with the first element of the right region.

One comparison is recorded for each scanned array value compared with the pivot. An exchange counts as a swap only when its two indexes differ; self-swaps are omitted. Thus, a partition of \(n\) active elements makes exactly \(n-1\) counted comparisons and uses \(O(1)\) partition auxiliary space.

## 5. Randomized Quicksort Design

Randomized Quicksort creates a local `random.Random(seed)` instance. For each nontrivial subarray, it selects an index uniformly from the inclusive range \([low, high]\), records the choice, swaps that value into `high`, and calls the same Lomuto function. It never calls `random.seed()` or modifies module-global random state.

Using the same partition implementation isolates pivot policy as the primary experimental difference. A fixed seed reproduces the pivot trace and metrics. Different seeds can produce different decompositions while still producing the same correct ascending result.

## 6. Input Validation and Edge Cases

Public sorting functions require a list containing integers that are not Boolean values. Non-list containers, floats, strings, Boolean elements, and non-Boolean `in_place` arguments raise clear `TypeError` exceptions. Partition bounds must satisfy \(0 \leq low \leq high < len(values)\).

Tests cover empty, one-element, two-element, sorted, reverse-sorted, repeated, all-equal, negative, and mixed lists. Copy mode returns a new list and leaves the caller's input unchanged. In-place mode returns the exact same list object.

## 7. Correctness Discussion

Immediately before each Lomuto loop iteration, the scanned subarray has three regions: values through the left boundary are at most the pivot, scanned values after that boundary are greater than the pivot, and remaining values are unclassified. Processing the next value preserves this invariant by either extending the left region or leaving the value in the greater-than region. Placing the pivot after the left boundary establishes the required final partition.

Quicksort correctness follows by induction on subarray size. Empty and one-element regions are already sorted. For a larger region, partition puts the pivot in its final sorted position. The inductive hypothesis sorts both strictly smaller regions, so their concatenation with the pivot is sorted. Automated tests check this invariant and compare complete results with Python's trusted `sorted()` output.

## 8. Best-Case Time Analysis

When pivots repeatedly divide the input into two approximately equal regions, each recursion level performs \(\Theta(n)\) total partition work and the tree has \(\Theta(\log n)\) levels:

\[
T(n)=2T(n/2)+\Theta(n).
\]

The Master Theorem or a balanced recursion tree gives:

\[
T(n)=\Theta(n\log n).
\]

Perfect balance at every node is not required for this growth; consistently bounded partition ratios are sufficient.

## 9. Average and Expected-Case Time Analysis

For a randomized pivot with sorted rank \(q\), the two subproblem sizes are \(q-1\) and \(n-q\). Every rank has probability \(1/n\), producing:

\[
E[T(n)] =
\frac{1}{n}\sum_{q=1}^{n}
\left(E[T(q-1)] + E[T(n-q)]\right)
+\Theta(n).
\]

The expected recursive work averages across every possible split, and the linear term represents partitioning. Substitution or the standard expected-comparison analysis bounds the recurrence by \(O(n\log n)\); comparison sorting supplies the corresponding expected lower bound in the general case, yielding expected \(\Theta(n\log n)\) (Cormen et al., 2022). Individual partitions need not be balanced. Instead, sufficiently balanced splits occur often enough that the expected total depth-weighted work remains logarithmic per element.

For random input order, deterministic final-pivot Quicksort also has average \(\Theta(n\log n)\) behavior because the final value's rank behaves like a random rank. Randomized selection makes this expectation less dependent on the original ordering.

## 10. Worst-Case Time Analysis

If every pivot is the smallest or largest active value, one subproblem has size \(n-1\) and the other is empty:

\[
T(n)=T(n-1)+\Theta(n)=\Theta(n^2).
\]

Ascending unique input always makes the final element the largest deterministic pivot. Descending unique input makes it an extreme pivot at every level as well. At \(n=10{,}000\), the expected deterministic count from summing \(1+2+\cdots+9{,}999\) is 49,995,000 comparisons, exactly matching the CSV.

Randomization makes a long sequence of extreme pivot ranks unlikely and removes systematic dependence on initial ordering. It does not make that sequence impossible, so randomized Quicksort retains a \(\Theta(n^2)\) mathematical worst case.

## 11. Space Complexity and Stack Behavior

Lomuto partition itself uses \(O(1)\) auxiliary space. A naive recursive Quicksort has expected stack depth \(O(\log n)\) and worst-case depth \(O(n)\). This implementation recurses only into the smaller partition and iterates over the larger one, limiting the physical Python call stack to \(O(\log n)\), even when logical depth reaches \(n\).

Copy mode creates an \(O(n)\) list copy to preserve the caller's input. In-place mode avoids that full output copy. The requested measured implementation also stores an \(O(n)\) pivot trace and counters; this instrumentation is additional experimental memory, not part of the constant-space partition operation.

## 12. Experimental Methodology

The benchmark compared deterministic last-pivot and randomized Quicksort on sizes 100, 1,000, 3,500, 5,000, 7,000, and 10,000. Distributions were random mostly unique integers, ascending unique integers, descending unique integers, and values drawn from 0 through 9.

Fixed seeds made datasets and randomized pivot schedules reproducible. Each combination used an untimed warm-up and five measured trials. Every trial received a fresh input copy, used `time.perf_counter()`, and was verified against Python's `sorted()`. Dataset creation, CSV writing, and chart generation were excluded from timing. The CSV records median, mean, standard deviation, minimum, maximum, comparisons, swaps, partitions, logical calls, depth, pivot selections, and failure details.

## 13. Runtime Results

![Runtime comparison](results/quicksort_runtime_chart.png)

The current CSV contains 48 completed rows. The size-10,000 summary is:

| Distribution | Algorithm | Median seconds | Comparisons | Swaps | Logical depth |
|---|---|---:|---:|---:|---:|
| Random | Deterministic | 3.238983 | 155,468 | 81,230 | 29 |
| Random | Randomized | 3.224975 | 155,656 | 75,344 | 31 |
| Sorted | Deterministic | 8.466383 | 49,995,000 | 0 | 10,000 |
| Sorted | Randomized | 3.199326 | 152,462 | 10,072 | 30 |
| Reverse sorted | Deterministic | 7.556488 | 49,995,000 | 5,000 | 10,000 |
| Reverse sorted | Randomized | 3.234181 | 153,721 | 60,164 | 31 |
| Repeated values | Deterministic | 5.194373 | 5,031,031 | 19,039 | 1,049 |
| Repeated values | Randomized | 5.426506 | 5,051,490 | 29,954 | 1,051 |

These are measurements from this run, not universal runtime constants. No statistical-significance test was performed.

## 14. Comparison-Count Results

![Comparison-count analysis](results/quicksort_comparisons_chart.png)

Comparison counts provide a less system-dependent view than elapsed time. Random unique inputs produced about 155,000 comparisons for both algorithms at size 10,000. Deterministic ordered inputs produced 49,995,000, visibly following quadratic growth. Randomized ordered inputs remained around 152,000–154,000 comparisons, consistent with expected \(n\log n\) growth.

The deterministic sorted case recorded zero swaps under the documented counting rule because every `<= pivot` placement and final pivot placement was a self-swap. This does not imply zero work: the algorithm still performed nearly 50 million comparisons.

## 15. Deterministic Versus Randomized Interpretation

On random unique data, deterministic and randomized medians were nearly equal in this run because the final deterministic value did not systematically have an extreme rank. Random pivot selection added pivot exchanges but did not materially change the total comparison scale.

On sorted and reverse-sorted unique data, the deterministic pivot was always extreme, whereas random selection produced shallow logical trees with depths 30 and 31. The observed comparison contrast supports the theoretical explanation that randomization reduces sensitivity to input order. It does not demonstrate that randomized Quicksort is always faster or that its worst case has disappeared.

## 16. Effect of Input Distribution

Input distribution changed deterministic behavior substantially. Random unique input produced logical depth 29 at size 10,000, while both ordered unique inputs reached depth 10,000. Randomized logical depth stayed between 30 and 31 for the three unique-value distributions in the recorded median metrics.

Runtime did not scale in exact proportion to comparisons because Python loop execution, list access, function calls, tuple recording, swaps, allocation, and system scheduling contribute different costs. Asymptotic analysis predicts growth patterns rather than exact seconds.

## 17. Effect of Repeated Values

With Lomuto's `<= pivot` rule, every value equal to the pivot enters the left region. Equal keys are not collected into a completed middle region. With only ten possible values, both pivot policies repeatedly processed large groups of duplicates.

At size 10,000, deterministic and randomized versions recorded approximately 5.03 and 5.05 million comparisons and logical depths above 1,000. Randomization did not resolve the structural duplicate problem because any selected pivot still used the same two-region partition. This differs from Assignment 3's three-way partition, which grouped values equal to the pivot.

## 18. Practical Applications

Quicksort's in-place partitioning can be useful when array-like data must be ordered with limited auxiliary storage. Its concepts apply to database and search preprocessing, data-processing pipelines, and resource-constrained software. Algorithm selection should still consider stability, duplicate frequency, adversarial ordering, memory limits, and language-specific constant factors rather than assuming one Quicksort policy is optimal for every workload.

## 19. Limitations

The benchmark represents one instrumented Python implementation and one execution environment. Five trials support a course-scale comparison but not a formal statistical performance study. Metrics and pivot-trace storage add time and \(O(n)\) experimental memory. The code intentionally omits hybrid small-partition cutoffs, three-way partitioning, median-of-three pivots, and introspective worst-case fallback because they would change the assigned Lomuto pivot-policy comparison.

The random inputs were deterministic pseudo-random samples rather than every possible permutation. Randomized results depend on the documented seed schedule, although fixed seeds reproduce them. Wall-clock measurements can vary with processor state and other system activity.

## 20. Conclusion

The implementation demonstrates that pivot policy can change Quicksort's behavior without changing its partition function. Deterministic last-pivot Quicksort was competitive on random unique data but exhibited the predicted \(\Theta(n^2)\) comparison growth on sorted and reverse-sorted inputs. Randomization made performance much less dependent on initial unique-value ordering and produced observed comparison counts consistent with expected \(\Theta(n\log n)\).

The repeated-value study also showed randomization's boundary: two-region Lomuto partitioning remained unbalanced when many values equaled the pivot. Stack-safe smaller-side recursion prevented Python failures in all cases, but it did not conceal the logical depth or quadratic work.

## 21. References

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

Hoare, C. A. R. (1962). Quicksort. *The Computer Journal, 5*(1), 10–16. https://doi.org/10.1093/comjnl/5.1.10

Python Software Foundation. (n.d.). *random — Generate pseudo-random numbers*. https://docs.python.org/3/library/random.html

Python Software Foundation. (n.d.). *time — Time access and conversions*. https://docs.python.org/3/library/time.html
