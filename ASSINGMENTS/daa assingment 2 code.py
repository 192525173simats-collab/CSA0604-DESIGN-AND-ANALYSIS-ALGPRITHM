"""
DAA ASSIGNMENT 2 (CO2)
Brute-Force and Exhaustive-Search Techniques
Complete Python implementation for Q1-Q7.

Requirements:
    Python 3.9+
    pip install matplotlib

Run:
    python daa_assignment2.py

Outputs:
    results/experiment_results.csv
    results/experiment_summary.txt
    results/closest_pair_comparison.png
    results/sorting_comparison.png
    results/hull_examples.png
"""

import csv
import math
import random
import time
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


SEED = 42
OUT = Path("results")
OUT.mkdir(exist_ok=True)


# ============================================================
# Q1. SORTING UNDER DIFFERENT DATA CONDITIONS
# ============================================================

def selection_sort(data):
    a = data.copy()
    comparisons = swaps = 0
    n = len(a)

    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[min_index]:
                min_index = j
        if min_index != i:
            a[i], a[min_index] = a[min_index], a[i]
            swaps += 1

    return a, comparisons, swaps


def bubble_sort(data):
    a = data.copy()
    comparisons = swaps = 0
    n = len(a)

    for end in range(n - 1, 0, -1):
        changed = False
        for j in range(end):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                changed = True
        if not changed:
            break

    return a, comparisons, swaps


def insertion_sort(data):
    a = data.copy()
    comparisons = moves = 0

    for i in range(1, len(a)):
        key = a[i]
        j = i - 1

        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break

        a[j + 1] = key
        if j + 1 != i:
            moves += 1

    return a, comparisons, moves


def run_q1(rng, rows):
    n = 1000
    sorted_data = list(range(n))
    reverse_data = sorted_data[::-1]
    edge_data = list(range(1, n + 1)) + [0]
    random_data = rng.sample(range(1_000_000), n)
    mostly_sorted = list(range(950)) + rng.sample(range(950, 5000), 50)
    duplicates = [rng.randrange(5) for _ in range(n)]

    datasets = {
        "Already sorted": sorted_data,
        "Reverse sorted": reverse_data,
        "One smallest at end": edge_data,
        "Random": random_data,
        "95 percent sorted": mostly_sorted,
        "Many duplicates": duplicates,
    }

    print("\nQ1 - SORTING")
    for dataset_name, values in datasets.items():
        print(f"\n{dataset_name}: n={len(values)}")
        for algorithm_name, algorithm in (
            ("Selection", selection_sort),
            ("Bubble", bubble_sort),
            ("Insertion", insertion_sort),
        ):
            start = time.perf_counter()
            result, comparisons, moves = algorithm(values)
            elapsed = time.perf_counter() - start
            assert result == sorted(values)

            rows.append({
                "question": "Q1",
                "dataset": dataset_name,
                "algorithm": algorithm_name,
                "n": len(values),
                "operations": comparisons,
                "secondary_operations": moves,
                "time_seconds": elapsed,
            })
            print(
                f"{algorithm_name:10s} comparisons={comparisons:9,d} "
                f"swaps/moves={moves:9,d} time={elapsed:.6f}s"
            )


# ============================================================
# Q2. SEQUENTIAL SEARCH
# ============================================================

def sequential_search(records, key):
    comparisons = 0
    for index, record in enumerate(records):
        comparisons += 1
        if record[0] == key:
            return index, comparisons
    return -1, comparisons


def run_q2(rng, rows):
    print("\nQ2 - SEQUENTIAL SEARCH")
    for n in (100, 1_000, 10_000, 100_000):
        records = [(i, f"Technician-{i % 100}", i * 10, i % 8)
                   for i in range(n)]
        tests = {
            "First": 0,
            "Middle": n // 2,
            "Last": n - 1,
            "Unsuccessful": n + 10,
        }

        for label, key in tests.items():
            start = time.perf_counter()
            index, comparisons = sequential_search(records, key)
            elapsed = time.perf_counter() - start

            expected = -1 if label == "Unsuccessful" else key
            assert (index == -1) if expected == -1 else (records[index][0] == expected)

            rows.append({
                "question": "Q2",
                "dataset": label,
                "algorithm": "Sequential Search",
                "n": n,
                "operations": comparisons,
                "secondary_operations": "",
                "time_seconds": elapsed,
            })
            print(
                f"n={n:>6,d} {label:12s} "
                f"comparisons={comparisons:>7,d} time={elapsed:.6f}s"
            )

        random_keys = rng.sample(range(n), min(1000, n))
        total = sum(sequential_search(records, key)[1] for key in random_keys)
        print(f"n={n:>6,d} average successful comparisons={total / len(random_keys):.2f}")


# ============================================================
# Q3. BRUTE-FORCE STRING MATCHING
# ============================================================

def brute_force_string_match(text, pattern):
    """Return all match positions and the number of character comparisons."""
    n, m = len(text), len(pattern)
    matches = []
    comparisons = 0

    if m == 0:
        return list(range(n + 1)), 0
    if m > n:
        return matches, 0

    for start in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j += 1

        if j == m:
            matches.append(start)

    return matches, comparisons


def run_q3(rng, rows):
    print("\nQ3 - BRUTE-FORCE STRING MATCHING")
    n, m = 10_000, 50

    tests = {
        "Low work": ("A" * n, "B" + "A" * (m - 1)),
        "High work": ("A" * n, "A" * (m - 1) + "B"),
        "Full matches": ("A" * n, "A" * m),
    }

    alphabet = "ACGT"
    random_text = "".join(rng.choice(alphabet) for _ in range(n))
    random_pattern = "".join(rng.choice(alphabet) for _ in range(m))
    tests["Random DNA"] = (random_text, random_pattern)

    for label, (text, pattern) in tests.items():
        start = time.perf_counter()
        matches, comparisons = brute_force_string_match(text, pattern)
        elapsed = time.perf_counter() - start

        rows.append({
            "question": "Q3",
            "dataset": label,
            "algorithm": "Brute-force string matching",
            "n": len(text),
            "operations": comparisons,
            "secondary_operations": len(matches),
            "time_seconds": elapsed,
        })
        print(
            f"{label:14s} comparisons={comparisons:>9,d} "
            f"matches={len(matches):>6,d} time={elapsed:.6f}s"
        )


# ============================================================
# Q4. CLOSEST PAIR: BRUTE FORCE AND SWEEP REDESIGN
# ============================================================

def squared_distance(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def closest_pair_brute(points):
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    best = float("inf")
    best_pair = None
    pairs_examined = 0
    distance_calculations = 0

    for i in range(len(points) - 1):
        for j in range(i + 1, len(points)):
            pairs_examined += 1
            distance_calculations += 1
            d2 = squared_distance(points[i], points[j])
            if d2 < best:
                best = d2
                best_pair = (points[i], points[j])

    return best_pair, math.sqrt(best), pairs_examined, distance_calculations


def closest_pair_sweep(points):
    """
    Sort by x. Stop scanning when dx^2 >= current best squared distance.
    A y-gap test avoids unnecessary full distance calculations.

    This is the assignment's sweep redesign. Its typical performance is
    much better, but its worst case remains O(n^2), e.g. equal x-values.
    """
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    ordered = sorted(points, key=lambda p: (p[0], p[1]))
    best = float("inf")
    best_pair = None
    pairs_examined = 0
    distance_calculations = 0

    for i in range(len(ordered) - 1):
        x1, y1 = ordered[i]

        for j in range(i + 1, len(ordered)):
            x2, y2 = ordered[j]
            dx = x2 - x1

            if dx * dx >= best:
                break

            pairs_examined += 1
            dy = y2 - y1

            if dy * dy >= best:
                continue

            distance_calculations += 1
            d2 = dx * dx + dy * dy

            if d2 < best:
                best = d2
                best_pair = (ordered[i], ordered[j])

    return best_pair, math.sqrt(best), pairs_examined, distance_calculations


def make_points(rng, n, mode):
    if mode == "uniform":
        return [(rng.random() * 100_000, rng.random() * 100_000)
                for _ in range(n)]

    if mode == "clustered":
        centers = [(0, 0), (1000, 1000), (2000, 0), (0, 2000), (2000, 2000)]
        points = []
        for _ in range(n):
            cx, cy = rng.choice(centers)
            points.append((rng.gauss(cx, 50), rng.gauss(cy, 50)))
        return points

    if mode == "vertical line":
        return [(5.0, float(i)) for i in range(n)]

    raise ValueError("Unknown point distribution")


def run_q4(rng, rows):
    print("\nQ4 - CLOSEST PAIR")
    for mode, sizes in (
        ("uniform", (100, 500, 1000, 2000, 4000)),
        ("clustered", (2000, 4000)),
        ("vertical line", (500, 1000, 2000)),
    ):
        for n in sizes:
            points = make_points(rng, n, mode)

            start = time.perf_counter()
            brute = closest_pair_brute(points)
            brute_time = time.perf_counter() - start

            start = time.perf_counter()
            sweep = closest_pair_sweep(points)
            sweep_time = time.perf_counter() - start

            # Compare the exact minimum distance, allowing float rounding.
            assert math.isclose(brute[1], sweep[1], rel_tol=1e-12, abs_tol=1e-12)

            for algorithm, result, elapsed in (
                ("Closest pair brute force", brute, brute_time),
                ("Closest pair sweep", sweep, sweep_time),
            ):
                rows.append({
                    "question": "Q4/Q7",
                    "dataset": mode,
                    "algorithm": algorithm,
                    "n": n,
                    "operations": result[2],
                    "secondary_operations": result[3],
                    "time_seconds": elapsed,
                })

            print(
                f"{mode:12s} n={n:>5,d} "
                f"brute pairs={brute[2]:>12,d}, "
                f"sweep pairs={sweep[2]:>10,d}, "
                f"sweep distances={sweep[3]:>5,d}, "
                f"times={brute_time:.4f}s/{sweep_time:.4f}s"
            )


# ============================================================
# Q5. BRUTE-FORCE CONVEX HULL USING SUPPORTING LINES
# ============================================================

def cross(o, a, b):
    return ((a[0] - o[0]) * (b[1] - o[1])
            - (a[1] - o[1]) * (b[0] - o[0]))


def all_collinear(points):
    if len(points) < 3:
        return True
    return all(cross(points[0], points[1], p) == 0 for p in points[2:])


def brute_force_convex_hull(points):
    """
    Test every point pair as a possible supporting-line edge.
    Returns hull vertices in counter-clockwise order and cross-test count.
    Collinear boundary points are reduced to the two extreme endpoints.
    """
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts, 0
    if len(pts) == 2:
        return pts, 0

    if all_collinear(pts):
        return [pts[0], pts[-1]], len(pts) * (len(pts) - 1) * (len(pts) - 2)

    directed_edges = []
    tests = 0

    for i, p in enumerate(pts):
        for j, q in enumerate(pts):
            if i == j:
                continue

            saw_left = False
            saw_right = False
            valid_segment = True

            for r in pts:
                if r == p or r == q:
                    continue

                tests += 1
                side = cross(p, q, r)

                if side > 0:
                    saw_left = True
                elif side < 0:
                    saw_right = True
                else:
                    # A collinear point outside segment PQ means P-Q
                    # is not the extreme boundary segment.
                    if not (
                        min(p[0], q[0]) <= r[0] <= max(p[0], q[0])
                        and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])
                    ):
                        valid_segment = False
                        break

                if saw_left and saw_right:
                    valid_segment = False
                    break

            if not valid_segment:
                continue

            if not saw_right:
                directed_edges.append((p, q))
            elif not saw_left:
                directed_edges.append((q, p))

    # Build the boundary by following directed edges.
    next_point = {}
    for p, q in directed_edges:
        next_point[p] = q

    if not next_point:
        return [], tests

    start = min(next_point)
    hull = [start]
    current = start
    visited = {start}

    for _ in range(len(next_point) + 1):
        nxt = next_point.get(current)
        if nxt is None or nxt == start:
            break
        if nxt in visited:
            break
        hull.append(nxt)
        visited.add(nxt)
        current = nxt

    return hull, tests


def run_q5(rng, rows):
    print("\nQ5 - BRUTE-FORCE CONVEX HULL")

    square = [(0, 0), (10, 0), (10, 10), (0, 10),
              (5, 5), (3, 7), (7, 3), (2, 2), (8, 6), (6, 9)]

    boundary_collinear = square + [
        (5, 0), (10, 5), (5, 10), (0, 5), (5, 5), (5, 5)
    ]

    circle = [
        (round(40 * math.cos(2 * math.pi * i / 12), 6),
         round(40 * math.sin(2 * math.pi * i / 12), 6))
        for i in range(12)
    ] + [(rng.uniform(-10, 10), rng.uniform(-10, 10)) for _ in range(10)]

    for label, points in (
        ("Square with interior points", square),
        ("Collinear boundary and duplicates", boundary_collinear),
        ("Circle with interior points", circle),
    ):
        hull, tests = brute_force_convex_hull(points)
        rows.append({
            "question": "Q5",
            "dataset": label,
            "algorithm": "Brute-force convex hull",
            "n": len(set(points)),
            "operations": tests,
            "secondary_operations": len(hull),
            "time_seconds": "",
        })
        print(f"{label}: hull vertices={len(hull)}, cross tests={tests}")
        print("Hull:", hull)


# ============================================================
# Q6. EXHAUSTIVE SEARCH FOR 0/1 PACKAGE SELECTION
# ============================================================

def exhaustive_knapsack(items, capacity):
    """
    items: list of (weight, value)
    Examines every one of the 2^n possible subsets.
    """
    n = len(items)
    best_value = -1
    best_mask = 0
    feasible_count = 0

    for mask in range(1 << n):
        total_weight = 0
        total_value = 0

        for i, (weight, value) in enumerate(items):
            if mask & (1 << i):
                total_weight += weight
                total_value += value

        if total_weight <= capacity:
            feasible_count += 1
            if total_value > best_value:
                best_value = total_value
                best_mask = mask

    chosen = [
        i for i in range(n) if best_mask & (1 << i)
    ]

    return best_value, chosen, feasible_count, (1 << n)


def dp_knapsack(items, capacity):
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for cap in range(capacity, weight - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - weight] + value)
    return dp[capacity]


def run_q6(rng, rows):
    print("\nQ6 - EXHAUSTIVE 0/1 KNAPSACK")

    sample_items = [(3, 40), (4, 50), (5, 70), (2, 30), (6, 60)]
    best, chosen, feasible, examined = exhaustive_knapsack(sample_items, 10)
    assert best == dp_knapsack(sample_items, 10) == 140
    print(
        f"Small example: best value={best}, selected package indexes="
        f"{[i + 1 for i in chosen]}, feasible={feasible}/{examined}"
    )

    for n in (10, 14, 16, 18, 20):
        items = [
            (rng.randint(5, 40), rng.randint(10, 100))
            for _ in range(n)
        ]
        capacity = sum(weight for weight, _ in items) // 2

        start = time.perf_counter()
        best, chosen, feasible, examined = exhaustive_knapsack(items, capacity)
        elapsed = time.perf_counter() - start

        # Independent DP validation.
        assert best == dp_knapsack(items, capacity)

        rows.append({
            "question": "Q6",
            "dataset": "Random packages",
            "algorithm": "Exhaustive knapsack",
            "n": n,
            "operations": examined,
            "secondary_operations": feasible,
            "time_seconds": elapsed,
        })
        print(
            f"n={n:2d} subsets={examined:>9,d} feasible={feasible:>9,d} "
            f"best value={best:>5,d} time={elapsed:.4f}s"
        )


# ============================================================
# SAVE RESULTS AND CREATE GRAPHS
# ============================================================

def save_results(rows):
    csv_path = OUT / "experiment_results.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    summary_path = OUT / "experiment_summary.txt"
    with summary_path.open("w", encoding="utf-8") as file:
        file.write("DAA Assignment 2 - Experimental Run Summary\n")
        file.write("=" * 48 + "\n")
        file.write(f"Random seed: {SEED}\n")
        file.write(f"Total recorded experiment rows: {len(rows)}\n")
        file.write("All correctness assertions completed successfully.\n")
        file.write("Execution times depend on the computer and Python version.\n")

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {summary_path}")


def create_graphs(rows):
    if plt is None:
        print("Matplotlib is not installed; skipping graphs.")
        print("Install it with: pip install matplotlib")
        return

    # Sorting comparisons on each dataset.
    sorting = [r for r in rows if r["question"] == "Q1"]
    if sorting:
        labels = list(dict.fromkeys(r["dataset"] for r in sorting))
        algorithms = ("Selection", "Bubble", "Insertion")

        plt.figure(figsize=(11, 5))
        width = 0.25
        positions = list(range(len(labels)))

        for offset, algorithm in enumerate(algorithms):
            values = [
                next(r["operations"] for r in sorting
                     if r["dataset"] == label and r["algorithm"] == algorithm)
                for label in labels
            ]
            plt.bar(
                [p + (offset - 1) * width for p in positions],
                values,
                width=width,
                label=algorithm,
            )

        plt.xticks(positions, labels, rotation=20, ha="right")
        plt.ylabel("Key comparisons")
        plt.title("Q1 - Sorting Algorithm Comparisons")
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT / "sorting_comparison.png", dpi=200)
        plt.close()

    # Closest-pair comparison.
    closest = [r for r in rows if r["question"] == "Q4/Q7"]
    uniform = [r for r in closest if r["dataset"] == "uniform"]
    if uniform:
        brute = [r for r in uniform if r["algorithm"] == "Closest pair brute force"]
        sweep = [r for r in uniform if r["algorithm"] == "Closest pair sweep"]

        plt.figure(figsize=(8, 5))
        plt.plot([r["n"] for r in brute], [r["operations"] for r in brute],
                 marker="o", label="Brute force: pairs")
        plt.plot([r["n"] for r in sweep], [r["operations"] for r in sweep],
                 marker="o", label="Sweep: pairs examined")
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Number of points")
        plt.ylabel("Pairs examined")
        plt.title("Q4/Q7 - Closest Pair Operation Comparison")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(OUT / "closest_pair_comparison.png", dpi=200)
        plt.close()

    print(f"Graphs saved in: {OUT.resolve()}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    rng = random.Random(SEED)
    rows = []

    print("=" * 65)
    print("DAA ASSIGNMENT 2 - IMPLEMENTATION (Q1 TO Q7)")
    print("=" * 65)

    run_q1(rng, rows)
    run_q2(rng, rows)
    run_q3(rng, rows)
    run_q4(rng, rows)
    run_q5(rng, rows)
    run_q6(rng, rows)

    save_results(rows)
    create_graphs(rows)

    print("\nAll implemented questions completed.")
    print("Check the 'results' folder for CSV, summary and graph files.")


if __name__ == "__main__":
    main()
