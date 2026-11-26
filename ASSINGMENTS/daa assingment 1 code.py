"""
DAA Assignment 1
Design, Analysis and Validation of an Efficient Search Strategy
for a Student Record System

Algorithms:
1. Iterative Linear Search
2. Recursive Binary Search
3. Hash Table with Separate Chaining

Run:
    pip install matplotlib
    python student_search_implementation.py

The program creates:
    results.json
    performance_plots.png
"""

import json
import math
import random
import time
from pathlib import Path

import matplotlib.pyplot as plt


# ------------------------------------------------------------
# 1. LINEAR SEARCH (ITERATIVE)
# ------------------------------------------------------------
def linear_search(records, key):
    comparisons = 0

    for index, value in enumerate(records):
        comparisons += 1
        if value == key:
            return index, comparisons

    return -1, comparisons


# ------------------------------------------------------------
# 2. BINARY SEARCH (RECURSIVE)
#    Input list must be sorted.
# ------------------------------------------------------------
def binary_search(records, key, low=0, high=None):
    if high is None:
        high = len(records) - 1

    if low > high:
        return -1, 0

    middle = (low + high) // 2
    comparisons = 1

    if records[middle] == key:
        return middle, comparisons

    if key < records[middle]:
        result, extra = binary_search(records, key, low, middle - 1)
    else:
        result, extra = binary_search(records, key, middle + 1, high)

    return result, comparisons + extra


# ------------------------------------------------------------
# 3. HASH TABLE WITH SEPARATE CHAINING
# ------------------------------------------------------------
def is_prime(number):
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2

    return True


def next_prime(number):
    number = max(2, number)
    while not is_prime(number):
        number += 1
    return number


class ChainedHashTable:
    def __init__(self, records):
        # Keep load factor at or below approximately 0.75.
        self.bucket_count = next_prime(math.ceil(len(records) / 0.75))
        self.buckets = [[] for _ in range(self.bucket_count)]

        for record in records:
            bucket_index = record % self.bucket_count
            self.buckets[bucket_index].append(record)

    def search(self, key):
        bucket_index = key % self.bucket_count
        chain = self.buckets[bucket_index]
        comparisons = 0

        for value in chain:
            comparisons += 1
            if value == key:
                return True, comparisons

        return False, comparisons

    def longest_chain(self):
        return max((len(chain) for chain in self.buckets), default=0)


# ------------------------------------------------------------
# HELPER FUNCTIONS FOR EXPERIMENTS
# ------------------------------------------------------------
def average_search_time(search_function, queries):
    start = time.perf_counter()

    total_comparisons = 0
    for key in queries:
        _, comparisons = search_function(key)
        total_comparisons += comparisons

    elapsed = time.perf_counter() - start
    average_time_us = (elapsed / len(queries)) * 1_000_000
    average_comparisons = total_comparisons / len(queries)

    return average_time_us, average_comparisons


def make_absent_keys(records, count, rng):
    existing = set(records)
    absent = []

    while len(absent) < count:
        candidate = rng.randrange(100_000_000, 1_000_000_000)
        if candidate not in existing:
            existing.add(candidate)
            absent.append(candidate)

    return absent


# ------------------------------------------------------------
# MAIN EXPERIMENT
# ------------------------------------------------------------
def run_experiments():
    rng = random.Random(42)

    dataset_sizes = [1_000, 10_000, 100_000, 1_000_000]

    # Fewer linear queries are used for large datasets because
    # linear search examines records one by one.
    linear_query_counts = {
        1_000: 200,
        10_000: 200,
        100_000: 40,
        1_000_000: 10,
    }

    results = {}

    for n in dataset_sizes:
        print(f"\nRunning experiment for {n:,} student records...")

        # Generate unique 9-digit registration numbers.
        records = rng.sample(range(100_000_000, 1_000_000_000), n)

        # Prepare queries.
        linear_count = linear_query_counts[n]
        linear_hits = rng.sample(records, linear_count)
        linear_misses = make_absent_keys(records, linear_count, rng)

        binary_hits = rng.sample(records, 5_000)
        binary_misses = make_absent_keys(records, 5_000, rng)

        hash_hits = binary_hits
        hash_misses = binary_misses

        # Preprocessing: sorting and hash-table construction.
        sort_start = time.perf_counter()
        sorted_records = sorted(records)
        sort_time = time.perf_counter() - sort_start

        hash_start = time.perf_counter()
        hash_table = ChainedHashTable(records)
        hash_build_time = time.perf_counter() - hash_start

        # Search wrappers.
        def linear(key):
            return linear_search(records, key)

        def binary(key):
            return binary_search(sorted_records, key)

        def hashed(key):
            found, comparisons = hash_table.search(key)
            return found, comparisons

        # Correctness validation against Python set membership.
        reference = set(records)

        for key in linear_hits + binary_hits + hash_hits:
            assert key in reference

        for key in linear_misses + binary_misses + hash_misses:
            assert key not in reference

        for key in binary_hits[:100]:
            index, _ = binary(key)
            assert index != -1 and sorted_records[index] == key

        for key in binary_misses[:100]:
            index, _ = binary(key)
            assert index == -1

        for key in hash_hits[:100]:
            found, _ = hash_table.search(key)
            assert found is True

        for key in hash_misses[:100]:
            found, _ = hash_table.search(key)
            assert found is False

        # Measure average time and comparisons.
        linear_hit_time, linear_hit_comp = average_search_time(
            linear, linear_hits
        )
        linear_miss_time, linear_miss_comp = average_search_time(
            linear, linear_misses
        )

        binary_hit_time, binary_hit_comp = average_search_time(
            binary, binary_hits
        )
        binary_miss_time, binary_miss_comp = average_search_time(
            binary, binary_misses
        )

        hash_hit_time, hash_hit_comp = average_search_time(
            hashed, hash_hits
        )
        hash_miss_time, hash_miss_comp = average_search_time(
            hashed, hash_misses
        )

        # Best and worst examples.
        linear_best = linear_search(records, records[0])[1]
        linear_worst = linear_search(records, records[-1])[1]

        binary_best_key = sorted_records[len(sorted_records) // 2]
        binary_best = binary_search(sorted_records, binary_best_key)[1]

        # Sample successful searches to estimate the deepest observed hit.
        binary_worst_observed = max(
            binary_search(sorted_records, key)[1]
            for key in rng.sample(records, min(300, n))
        )

        results[str(n)] = {
            "sort_time_seconds": sort_time,
            "hash_build_time_seconds": hash_build_time,
            "hash_bucket_count": hash_table.bucket_count,
            "linear": {
                "successful_time_us": linear_hit_time,
                "unsuccessful_time_us": linear_miss_time,
                "successful_comparisons": linear_hit_comp,
                "unsuccessful_comparisons": linear_miss_comp,
                "best_comparisons": linear_best,
                "worst_comparisons": linear_worst,
                "query_count": linear_count,
            },
            "binary": {
                "successful_time_us": binary_hit_time,
                "unsuccessful_time_us": binary_miss_time,
                "successful_comparisons": binary_hit_comp,
                "unsuccessful_comparisons": binary_miss_comp,
                "best_comparisons": binary_best,
                "worst_observed_comparisons": binary_worst_observed,
            },
            "hash": {
                "successful_time_us": hash_hit_time,
                "unsuccessful_time_us": hash_miss_time,
                "successful_comparisons": hash_hit_comp,
                "unsuccessful_comparisons": hash_miss_comp,
                "longest_chain": hash_table.longest_chain(),
            },
            "correctness": "All validation checks passed",
        }

        print(
            f"Linear hit comparisons: {linear_hit_comp:.2f} | "
            f"Binary hit comparisons: {binary_hit_comp:.2f} | "
            f"Hash hit comparisons: {hash_hit_comp:.2f}"
        )

    # Save experimental results as JSON.
    output_json = Path("results.json")
    output_json.write_text(json.dumps(results, indent=4), encoding="utf-8")

    # --------------------------------------------------------
    # PERFORMANCE GRAPHS
    # --------------------------------------------------------
    sizes = dataset_sizes

    linear_times = [
        results[str(n)]["linear"]["successful_time_us"] for n in sizes
    ]
    binary_times = [
        results[str(n)]["binary"]["successful_time_us"] for n in sizes
    ]
    hash_times = [
        results[str(n)]["hash"]["successful_time_us"] for n in sizes
    ]

    linear_comparisons = [
        results[str(n)]["linear"]["successful_comparisons"] for n in sizes
    ]
    binary_comparisons = [
        results[str(n)]["binary"]["successful_comparisons"] for n in sizes
    ]
    hash_comparisons = [
        results[str(n)]["hash"]["successful_comparisons"] for n in sizes
    ]

    sort_times = [
        results[str(n)]["sort_time_seconds"] for n in sizes
    ]
    hash_build_times = [
        results[str(n)]["hash_build_time_seconds"] for n in sizes
    ]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, linear_times, marker="o", label="Linear Search")
    plt.plot(sizes, binary_times, marker="o", label="Binary Search")
    plt.plot(sizes, hash_times, marker="o", label="Hash Search")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of student records (n)")
    plt.ylabel("Average successful search time (microseconds)")
    plt.title("Search Time Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, linear_comparisons, marker="o", label="Linear Search")
    plt.plot(sizes, binary_comparisons, marker="o", label="Binary Search")
    plt.plot(sizes, hash_comparisons, marker="o", label="Hash Search")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of student records (n)")
    plt.ylabel("Average key comparisons")
    plt.title("Average Comparisons Performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, sort_times, marker="o", label="Sorting")
    plt.plot(sizes, hash_build_times, marker="o", label="Hash Table Build")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of student records (n)")
    plt.ylabel("Preprocessing time (seconds)")
    plt.title("Preprocessing Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("performance_plots.png", dpi=300)
    plt.show()

    print("\nAll experiments completed successfully.")
    print("Files created: results.json and performance_plots.png")


if __name__ == "__main__":
    run_experiments()
