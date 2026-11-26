"""
DESIGN AND ANALYSIS OF ALGORITHMS - ASSIGNMENT 3 (CO3)
Divide-and-Conquer Algorithms
Implementation of Q1-Q6 from the supplied assignment.

Run:
    python daa_assignment3.py

No external packages are required.
Q7 is not implemented because the supplied assignment document does not
provide the actual problem statement for its first-principles design task.
"""

import random
import time
from math import sqrt
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------
# Q1(A): Divide-and-Conquer Maximum and Minimum
# ---------------------------------------------------------------------

def find_min_max(arr: List[int], low: int = 0,
                 high: Optional[int] = None) -> Tuple[int, int, int]:
    """Return (minimum, maximum, comparison_count)."""
    if not arr:
        raise ValueError("Array must not be empty.")
    if high is None:
        high = len(arr) - 1

    if low == high:
        return arr[low], arr[low], 0

    if high == low + 1:
        if arr[low] < arr[high]:
            return arr[low], arr[high], 1
        return arr[high], arr[low], 1

    mid = (low + high) // 2
    min_l, max_l, count_l = find_min_max(arr, low, mid)
    min_r, max_r, count_r = find_min_max(arr, mid + 1, high)

    minimum = min(min_l, min_r)
    maximum = max(max_l, max_r)
    return minimum, maximum, count_l + count_r + 2


# ---------------------------------------------------------------------
# Q1(B): Binary Search
# ---------------------------------------------------------------------

def binary_search(arr: List[int], target: int) -> Tuple[int, int]:
    """Return (index, comparisons); index is -1 when not found."""
    low, high = 0, len(arr) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if arr[mid] == target:
            return mid, comparisons
        if target < arr[mid]:
            high = mid - 1
        else:
            low = mid + 1

    return -1, comparisons


# ---------------------------------------------------------------------
# Q2: Merge Sort and Quick Sort
# ---------------------------------------------------------------------

def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr[:]

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(arr: List[int]) -> List[int]:
    """Quick Sort using the last element as pivot, as in the assignment."""
    result = arr[:]

    def partition(low: int, high: int) -> int:
        pivot = result[high]
        i = low - 1
        for j in range(low, high):
            if result[j] <= pivot:
                i += 1
                result[i], result[j] = result[j], result[i]
        result[i + 1], result[high] = result[high], result[i + 1]
        return i + 1

    def sort(low: int, high: int) -> None:
        if low < high:
            p = partition(low, high)
            sort(low, p - 1)
            sort(p + 1, high)

    # Use an iterative fallback for very deep recursion while retaining
    # the same last-element-pivot partition strategy.
    stack = [(0, len(result) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            p = partition(low, high)
            # Push larger partition first so smaller one is processed first.
            left = (low, p - 1)
            right = (p + 1, high)
            if left[1] - left[0] > right[1] - right[0]:
                stack.append(left)
                stack.append(right)
            else:
                stack.append(right)
                stack.append(left)
    return result


# ---------------------------------------------------------------------
# Q3: Karatsuba Integer Multiplication
# ---------------------------------------------------------------------

def karatsuba(x: int, y: int) -> int:
    """Karatsuba multiplication for non-negative integers."""
    if x < 0 or y < 0:
        # Handle signs while applying Karatsuba to magnitudes.
        sign = -1 if (x < 0) != (y < 0) else 1
        return sign * karatsuba(abs(x), abs(y))

    if x < 10 or y < 10:
        return x * y

    digits = max(len(str(x)), len(str(y)))
    m = (digits + 1) // 2
    base = 10 ** m

    a, b = divmod(x, base)
    c, d = divmod(y, base)

    z2 = karatsuba(a, c)
    z0 = karatsuba(b, d)
    z1 = karatsuba(a + b, c + d) - z2 - z0

    return z2 * (base ** 2) + z1 * base + z0


# ---------------------------------------------------------------------
# Q4: Conventional and Strassen Matrix Multiplication
# ---------------------------------------------------------------------

def conventional_matrix_multiply(A: List[List[int]],
                                 B: List[List[int]]) -> List[List[int]]:
    n = len(A)
    if n == 0 or any(len(row) != n for row in A):
        raise ValueError("A must be a non-empty square matrix.")
    if len(B) != n or any(len(row) != n for row in B):
        raise ValueError("B must be an n x n square matrix.")

    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            for j in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


def _add_matrix(A, B):
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def _subtract_matrix(A, B):
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def _split_matrix(A):
    n = len(A)
    mid = n // 2
    a11 = [row[:mid] for row in A[:mid]]
    a12 = [row[mid:] for row in A[:mid]]
    a21 = [row[:mid] for row in A[mid:]]
    a22 = [row[mid:] for row in A[mid:]]
    return a11, a12, a21, a22


def _combine_blocks(c11, c12, c21, c22):
    top = [c11[i] + c12[i] for i in range(len(c11))]
    bottom = [c21[i] + c22[i] for i in range(len(c21))]
    return top + bottom


def strassen_matrix_multiply(A: List[List[int]],
                             B: List[List[int]],
                             threshold: int = 2) -> List[List[int]]:
    """Strassen multiplication; pads matrices to the next power of two."""
    n = len(A)
    if n == 0 or any(len(row) != n for row in A):
        raise ValueError("A must be a non-empty square matrix.")
    if len(B) != n or any(len(row) != n for row in B):
        raise ValueError("B must be an n x n square matrix.")

    size = 1
    while size < n:
        size *= 2

    Ap = [[0] * size for _ in range(size)]
    Bp = [[0] * size for _ in range(size)]
    for i in range(n):
        for j in range(n):
            Ap[i][j] = A[i][j]
            Bp[i][j] = B[i][j]

    def recurse(X, Y):
        m = len(X)
        if m <= threshold:
            return conventional_matrix_multiply(X, Y)

        a11, a12, a21, a22 = _split_matrix(X)
        b11, b12, b21, b22 = _split_matrix(Y)

        m1 = recurse(_add_matrix(a11, a22), _add_matrix(b11, b22))
        m2 = recurse(_add_matrix(a21, a22), b11)
        m3 = recurse(a11, _subtract_matrix(b12, b22))
        m4 = recurse(a22, _subtract_matrix(b21, b11))
        m5 = recurse(_add_matrix(a11, a12), b22)
        m6 = recurse(_subtract_matrix(a21, a11), _add_matrix(b11, b12))
        m7 = recurse(_subtract_matrix(a12, a22), _add_matrix(b21, b22))

        c11 = _add_matrix(_subtract_matrix(_add_matrix(m1, m4), m5), m7)
        c12 = _add_matrix(m3, m5)
        c21 = _add_matrix(m2, m4)
        c22 = _add_matrix(_add_matrix(_subtract_matrix(m1, m2), m3), m6)
        return _combine_blocks(c11, c12, c21, c22)

    padded_result = recurse(Ap, Bp)
    return [row[:n] for row in padded_result[:n]]


# ---------------------------------------------------------------------
# Q5: Closest Pair of Points - Brute Force and Divide and Conquer
# ---------------------------------------------------------------------

def distance(p, q) -> float:
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def closest_pair_brute(points):
    if len(points) < 2:
        raise ValueError("At least two points are required.")
    best_pair = (points[0], points[1])
    best_distance = distance(*best_pair)
    checks = 0

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = distance(points[i], points[j])
            checks += 1
            if d < best_distance:
                best_distance = d
                best_pair = (points[i], points[j])

    return best_pair, best_distance, checks


def closest_pair_divide_conquer(points):
    """O(n log n) closest pair algorithm for 2-D points."""
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    px = sorted(points, key=lambda p: (p[0], p[1]))
    py = sorted(points, key=lambda p: (p[1], p[0]))
    checks = [0]

    def brute_small(arr):
        best = (arr[0], arr[1])
        best_d = distance(*best)
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                checks[0] += 1
                d = distance(arr[i], arr[j])
                if d < best_d:
                    best, best_d = (arr[i], arr[j]), d
        return best, best_d

    def solve(x_sorted, y_sorted):
        n = len(x_sorted)
        if n <= 3:
            return brute_small(x_sorted)

        mid = n // 2
        left_x = x_sorted[:mid]
        right_x = x_sorted[mid:]
        mid_x = right_x[0][0]

        left_set = set(left_x)
        left_y = [p for p in y_sorted if p in left_set]
        right_y = [p for p in y_sorted if p not in left_set]

        pair_l, dist_l = solve(left_x, left_y)
        pair_r, dist_r = solve(right_x, right_y)

        if dist_l <= dist_r:
            best_pair, delta = pair_l, dist_l
        else:
            best_pair, delta = pair_r, dist_r

        strip = [p for p in y_sorted if abs(p[0] - mid_x) < delta]
        for i in range(len(strip)):
            # The standard planar packing argument requires checking
            # no more than the next seven points in y-order.
            for j in range(i + 1, min(i + 8, len(strip))):
                if strip[j][1] - strip[i][1] >= delta:
                    break
                checks[0] += 1
                d = distance(strip[i], strip[j])
                if d < delta:
                    delta = d
                    best_pair = (strip[i], strip[j])

        return best_pair, delta

    pair, best_distance = solve(px, py)
    return pair, best_distance, checks[0]


# ---------------------------------------------------------------------
# Q6(A): Median of Medians - k-th Smallest Element
# ---------------------------------------------------------------------

def median_of_medians(arr: List[int], k: int) -> int:
    """Return the k-th smallest item using 1-based rank k."""
    if not 1 <= k <= len(arr):
        raise ValueError("k must be between 1 and the array length.")

    def select(values, rank):
        if len(values) <= 5:
            return sorted(values)[rank - 1]

        medians = []
        for i in range(0, len(values), 5):
            group = sorted(values[i:i + 5])
            medians.append(group[len(group) // 2])

        pivot = select(medians, (len(medians) + 1) // 2)
        lower = [x for x in values if x < pivot]
        equal = [x for x in values if x == pivot]
        upper = [x for x in values if x > pivot]

        if rank <= len(lower):
            return select(lower, rank)
        if rank <= len(lower) + len(equal):
            return pivot
        return select(upper, rank - len(lower) - len(equal))

    return select(arr[:], k)


# ---------------------------------------------------------------------
# Q6(B): Meet-in-the-Middle Subset Sum
# ---------------------------------------------------------------------

def _subset_sums(values):
    sums = [0]
    for value in values:
        sums += [s + value for s in sums]
    return sums


def meet_in_middle_subset_sum(arr: List[int], target: int):
    """Return (found, one_subset_that_matches)."""
    mid = len(arr) // 2
    left, right = arr[:mid], arr[mid:]

    left_sums = _subset_sums(left)
    right_sums = _subset_sums(right)
    right_lookup = {}

    # Keep one subset representation for each right-half sum.
    for mask in range(1 << len(right)):
        total = 0
        chosen = []
        for bit, value in enumerate(right):
            if mask & (1 << bit):
                total += value
                chosen.append(value)
        right_lookup.setdefault(total, chosen)

    for left_sum in left_sums:
        needed = target - left_sum
        if needed in right_lookup:
            # Reconstruct one left subset matching left_sum.
            left_chosen = []
            for mask in range(1 << len(left)):
                total = 0
                chosen = []
                for bit, value in enumerate(left):
                    if mask & (1 << bit):
                        total += value
                        chosen.append(value)
                if total == left_sum:
                    left_chosen = chosen
                    break
            return True, left_chosen + right_lookup[needed]

    return False, []


# ---------------------------------------------------------------------
# Experiment helpers
# ---------------------------------------------------------------------

def timed_call(function, *args):
    start = time.perf_counter()
    result = function(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed


def run_demo():
    print("=" * 68)
    print("DAA ASSIGNMENT 3 - DIVIDE AND CONQUER IMPLEMENTATION")
    print("=" * 68)

    # Q1(A)
    data = [14, 6, 9, 21, 3, 17, 12, 8]
    mn, mx, comparisons = find_min_max(data)
    print("\nQ1(A) MAXIMUM AND MINIMUM")
    print("Array:", data)
    print(f"Minimum = {mn}, Maximum = {mx}")
    print("Comparisons:", comparisons)

    # Q1(B)
    sorted_data = [3, 7, 11, 15, 19, 23, 27]
    index, count = binary_search(sorted_data, 19)
    print("\nQ1(B) BINARY SEARCH")
    print("Sorted array:", sorted_data)
    print("Target: 19")
    print("Index:", index, "| Comparisons:", count)

    # Q2
    sort_data = [38, 27, 43, 3, 9, 82, 10]
    print("\nQ2 MERGE SORT AND QUICK SORT")
    print("Original:", sort_data)
    print("Merge Sort:", merge_sort(sort_data))
    print("Quick Sort:", quick_sort(sort_data))

    # Q3
    x, y = 12345678, 87654321
    print("\nQ3 KARATSUBA MULTIPLICATION")
    print(f"{x} x {y} = {karatsuba(x, y)}")
    print("Verified with normal multiplication:", karatsuba(x, y) == x * y)

    # Q4
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    conventional = conventional_matrix_multiply(A, B)
    strassen = strassen_matrix_multiply(A, B)
    print("\nQ4 STRASSEN MATRIX MULTIPLICATION")
    print("Matrix A:", A)
    print("Matrix B:", B)
    print("Conventional result:", conventional)
    print("Strassen result:", strassen)
    print("Verified:", conventional == strassen)

    # Q5
    points = [(1, 1), (2, 4), (3, 2), (4, 5),
              (6, 1), (7, 3), (8, 5), (9, 2)]
    brute, brute_d, brute_checks = closest_pair_brute(points)
    divide, divide_d, divide_checks = closest_pair_divide_conquer(points)
    print("\nQ5 CLOSEST PAIR OF POINTS")
    print("Points:", points)
    print("Brute force:", brute, "| Distance:", round(brute_d, 4),
          "| Checks:", brute_checks)
    print("Divide and conquer:", divide, "| Distance:", round(divide_d, 4),
          "| Checks:", divide_checks)
    print("Verified distance:", abs(brute_d - divide_d) < 1e-9)

    # Q6(A)
    selection_data = [12, 3, 5, 7, 4, 19, 26, 1, 9]
    k = 4
    kth = median_of_medians(selection_data, k)
    print("\nQ6(A) MEDIAN OF MEDIANS")
    print("Array:", selection_data)
    print(f"{k}-th smallest element:", kth)
    print("Verified:", kth == sorted(selection_data)[k - 1])

    # Q6(B)
    subset_data, target = [3, 5, 7, 10], 15
    found, subset = meet_in_middle_subset_sum(subset_data, target)
    print("\nQ6(B) MEET-IN-THE-MIDDLE SUBSET SUM")
    print("Array:", subset_data, "| Target:", target)
    print("Subset found:", found, "| Subset:", subset)
    print("Subset total:", sum(subset) if found else "N/A")

    print("\nQ7 FIRST-PRINCIPLES DESIGN CHALLENGE")
    print("Not implemented: the supplied assignment does not specify")
    print("the actual problem statement for Q7. Add that statement")
    print("before selecting an algorithm and writing its implementation.")

    print("\nAll Q1-Q6 demonstration checks completed.")


if __name__ == "__main__":
    run_demo()
