"""
DAA Assignment 5 (CO5) - Search, Complexity and Approximation Engineering
Python 3 implementation for Part B:
B1 Graph Colouring (backtracking + DSATUR + instrumentation)
B2 Adversarial graph comparison
B3 Exact and Greedy Set Cover
B4 First Fit Decreasing Bin Packing + exact small-instance checker
"""

from dataclasses import dataclass
from itertools import combinations
import math
import random
import time


# ---------------------------------------------------------------------
# B1 - GRAPH COLOURING
# ---------------------------------------------------------------------

@dataclass
class SearchStats:
    nodes: int = 0
    attempts: int = 0
    rejected: int = 0
    backtracks: int = 0
    max_depth: int = 0

    def as_tuple(self):
        return (self.nodes, self.attempts, self.rejected,
                self.backtracks, self.max_depth)


def build_adjacency(n, edges):
    if n < 0:
        raise ValueError("Number of vertices cannot be negative.")
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError("Edge contains an invalid vertex.")
        if u == v:
            raise ValueError("Self-loop detected.")
        adj[u].add(v)
        adj[v].add(u)
    return adj


def colour_graph(n, edges, m, order="input", trace=None):
    """Return (colour list or None, statistics). Colours are 0..m-1."""
    if m < 0:
        raise ValueError("Number of colours cannot be negative.")
    if order not in ("input", "dsatur"):
        raise ValueError("order must be 'input' or 'dsatur'.")

    adj = build_adjacency(n, edges)
    colours = [-1] * n
    stats = SearchStats()

    def select_vertex():
        if order == "input":
            return next((v for v in range(n) if colours[v] == -1), None)

        best_vertex = None
        best_key = None
        for v in range(n):
            if colours[v] != -1:
                continue
            saturation = len({colours[u] for u in adj[v]
                              if colours[u] != -1})
            uncoloured_degree = sum(colours[u] == -1 for u in adj[v])
            key = (saturation, uncoloured_degree, -v)
            if best_key is None or key > best_key:
                best_key = key
                best_vertex = v
        return best_vertex

    def solve(depth):
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, depth)
        if depth == n:
            return True

        v = select_vertex()
        if trace is not None:
            trace.append(f"{'  ' * depth}Choose vertex {v}")

        for c in range(m):
            stats.attempts += 1
            if any(colours[u] == c for u in adj[v]):
                stats.rejected += 1
                if trace is not None:
                    trace.append(f"{'  ' * depth}Reject vertex {v}, colour {c}")
                continue

            colours[v] = c
            if trace is not None:
                trace.append(f"{'  ' * depth}Assign vertex {v}, colour {c}")

            if solve(depth + 1):
                return True

            colours[v] = -1
            stats.backtracks += 1
            if trace is not None:
                trace.append(f"{'  ' * depth}Backtrack vertex {v}, undo colour {c}")

        return False

    success = solve(0)
    return (colours[:] if success else None), stats


def is_proper_colouring(n, edges, colouring, m):
    if colouring is None or len(colouring) != n:
        return False
    if any(c < 0 or c >= m for c in colouring):
        return False
    return all(colouring[u] != colouring[v] for u, v in edges)


def run_b1():
    print("\n========== B1: GRAPH COLOURING ==========")
    sample_edges = [(0, 1), (0, 2), (1, 2),
                    (1, 4), (2, 4), (3, 4)]
    trace = []
    answer, stats = colour_graph(5, sample_edges, 3, "input", trace)
    print("Sample graph colouring:", answer)
    print("Valid colouring:", is_proper_colouring(5, sample_edges, answer, 3))
    print("Statistics (nodes, attempts, rejected, backtracks, max depth):",
          stats.as_tuple())
    print("Search trace:")
    for line in trace:
        print(" ", line)

    petersen = ([(i, (i + 1) % 5) for i in range(5)]
                + [(i, i + 5) for i in range(5)]
                + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    k4 = [(a, b) for a in range(4) for b in range(a + 1, 4)]
    c5 = [(i, (i + 1) % 5) for i in range(5)]
    cases = [
        ("Petersen graph, m=3", 10, petersen, 3, True),
        ("Complete graph K4, m=3", 4, k4, 3, False),
        ("Single vertex, m=1", 1, [], 1, True),
        ("Empty graph", 0, [], 2, True),
        ("Five isolated vertices", 5, [], 1, True),
        ("One edge, m=1", 2, [(0, 1)], 1, False),
        ("Odd cycle C5, m=2", 5, c5, 2, False),
    ]

    print("\nValidation tests:")
    for order in ("input", "dsatur"):
        for name, n, edges, m, expected in cases:
            result, st = colour_graph(n, edges, m, order)
            actual = result is not None
            valid = result is None or is_proper_colouring(n, edges, result, m)
            passed = actual == expected and valid
            print(f"{'PASS' if passed else 'FAIL':4} {order:6} "
                  f"{name:28} expected={expected!s:5} "
                  f"actual={actual!s:5} nodes={st.nodes:6} "
                  f"colouring={result}")


def random_graph(n, probability, seed):
    rng = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(i + 1, n)
            if rng.random() < probability]


def run_b2():
    print("\n========== B2: ADVERSARIAL INPUT COMPARISON ==========")
    # Both graphs have 14 vertices and 3 colours.
    easy_edges = [(i, i + 1) for i in range(13)]
    hidden_edges = ([(i, i + 1) for i in range(9)]
                    + [(a, b) for a in range(10, 14)
                       for b in range(a + 1, 14)])
    graphs = [
        ("Graph A: path", 14, easy_edges, 3),
        ("Graph B: path + hidden K4", 14, hidden_edges, 3),
    ]

    print(f"{'Graph':30} {'Order':8} {'Nodes':>10} {'Attempts':>10} "
          f"{'Rejected':>10} {'Backtracks':>12} {'Result'}")
    for name, n, edges, m in graphs:
        for order in ("input", "dsatur"):
            colouring, st = colour_graph(n, edges, m, order)
            result = "colourable" if colouring is not None else "not colourable"
            print(f"{name:30} {order:8} {st.nodes:10} {st.attempts:10} "
                  f"{st.rejected:10} {st.backtracks:12} {result}")


# ---------------------------------------------------------------------
# B3 - SET COVER: EXACT SEARCH AND GREEDY APPROXIMATION
# ---------------------------------------------------------------------

def exact_set_cover(universe_size, centres):
    """Find minimum number of centres by enumerating subsets by size."""
    if universe_size < 0:
        raise ValueError("Universe size cannot be negative.")
    full_mask = (1 << universe_size) - 1
    masks = []
    for centre in centres:
        mask = 0
        for zone in centre:
            if not 0 <= zone < universe_size:
                raise ValueError("A centre contains an invalid zone.")
            mask |= 1 << zone
        masks.append(mask)

    examined = 0
    if full_mask == 0:
        return [], examined

    for size in range(1, len(centres) + 1):
        for selected in combinations(range(len(centres)), size):
            examined += 1
            covered = 0
            for index in selected:
                covered |= masks[index]
            if covered == full_mask:
                return list(selected), examined
    return None, examined


def greedy_set_cover(universe_size, centres, trace=None):
    """Repeatedly choose the centre covering the most uncovered zones."""
    uncovered = set(range(universe_size))
    selected = []
    evaluations = 0
    centre_sets = [set(c) for c in centres]

    while uncovered:
        best_index = None
        best_gain = 0
        for i, centre in enumerate(centre_sets):
            evaluations += 1
            gain = len(uncovered & centre)
            if gain > best_gain:
                best_gain = gain
                best_index = i

        if best_index is None:
            return None, evaluations

        selected.append(best_index)
        uncovered -= centre_sets[best_index]
        if trace is not None:
            trace.append((best_index, best_gain, sorted(uncovered)))

    return selected, evaluations


def random_set_cover_instance(n, m, seed, density=0.30):
    rng = random.Random(seed)
    centres = []
    for _ in range(m):
        size = max(1, int(round(n * density * rng.uniform(0.5, 1.5))))
        centres.append(set(rng.sample(range(n), min(size, n))))
    # Ensure every zone is covered by at least one candidate centre.
    for zone in range(n):
        if not any(zone in centre for centre in centres):
            rng.choice(centres).add(zone)
    return centres


def run_b3():
    print("\n========== B3: EXACT VS GREEDY SET COVER ==========")
    for case_no, (n, m, seed) in enumerate(
            [(10, 8, 11), (12, 9, 22), (14, 10, 33)], start=1):
        centres = random_set_cover_instance(n, m, seed)
        exact, exact_ops = exact_set_cover(n, centres)
        greedy, greedy_ops = greedy_set_cover(n, centres)
        print(f"Instance {case_no}: zones={n}, centres={m}, seed={seed}")
        print("  Exact:", exact, "size =", None if exact is None else len(exact),
              "combinations =", exact_ops)
        print("  Greedy:", greedy, "size =", None if greedy is None else len(greedy),
              "evaluations =", greedy_ops)

    print("\nGreedy counterexample:")
    universe_size = 14
    centres = [
        {0, 1, 2, 3, 7, 8, 9, 10},  # C
        set(range(0, 7)),           # A
        set(range(7, 14)),          # B
    ]
    trace = []
    greedy, greedy_ops = greedy_set_cover(universe_size, centres, trace)
    exact, exact_ops = exact_set_cover(universe_size, centres)
    print("  Exact optimal centre indices:", exact)
    print("  Greedy centre indices:", greedy)
    print("  Greedy steps (chosen index, gain, remaining zones):")
    for step in trace:
        print("   ", step)
    print("  Exact size:", len(exact), "| Greedy size:", len(greedy))

    print("\nScalability experiment:")
    print(f"{'Zones':>7} {'Centres':>8} {'Exact combos':>14} "
          f"{'Greedy evals':>14} {'Exact size':>12} {'Greedy size':>12}")
    for n, m, seed in [(10, 8, 1), (15, 12, 2), (20, 16, 3),
                       (25, 20, 4), (30, 24, 5), (35, 28, 6),
                       (40, 32, 7), (45, 36, 8), (50, 40, 9)]:
        centres = random_set_cover_instance(n, m, seed, 0.25)
        exact, exact_ops = exact_set_cover(n, centres)
        greedy, greedy_ops = greedy_set_cover(n, centres)
        print(f"{n:7} {m:8} {exact_ops:14} {greedy_ops:14} "
              f"{len(exact) if exact is not None else '-':>12} "
              f"{len(greedy) if greedy is not None else '-':>12}")


# ---------------------------------------------------------------------
# B4 - BIN PACKING: FIRST FIT DECREASING
# ---------------------------------------------------------------------

def first_fit_decreasing(workloads, capacity):
    """Sort demands descending; put each in the first server with enough room."""
    if capacity <= 0:
        raise ValueError("Capacity must be positive.")
    for demand in workloads:
        if not (0 < demand <= capacity):
            raise ValueError(f"Demand {demand} outside (0, capacity].")

    # Each server stores [remaining capacity, assigned workloads].
    servers = []
    fit_checks = 0

    for demand in sorted(workloads, reverse=True):
        placed = False
        for server in servers:
            fit_checks += 1
            if server[0] >= demand:
                server[0] -= demand
                server[1].append(demand)
                placed = True
                break
        if not placed:
            servers.append([capacity - demand, [demand]])

    return servers, fit_checks


def exact_minimum_bins(workloads, capacity):
    """Exact branch-and-bound checker for small test cases only."""
    if capacity <= 0 or any(w <= 0 or w > capacity for w in workloads):
        raise ValueError("Every demand must be in (0, capacity].")

    items = sorted(workloads, reverse=True)
    if not items:
        return 0

    best = [len(items)]
    bins = []

    def search(index):
        if len(bins) >= best[0]:
            return
        if index == len(items):
            best[0] = len(bins)
            return

        demand = items[index]
        seen_remaining = set()
        for i in range(len(bins)):
            if bins[i] in seen_remaining:
                continue
            if bins[i] + demand <= capacity:
                seen_remaining.add(bins[i])
                bins[i] += demand
                search(index + 1)
                bins[i] -= demand

        bins.append(demand)
        search(index + 1)
        bins.pop()

    search(0)
    return best[0]


def display_packing(title, workloads, capacity):
    servers, checks = first_fit_decreasing(workloads, capacity)
    lower_bound = math.ceil(sum(workloads) / capacity)
    print(f"\n{title}")
    print("Capacity:", capacity, "| Workloads:", len(workloads),
          "| Total demand:", sum(workloads),
          "| Lower bound:", lower_bound)
    print("Servers used:", len(servers), "| Fit checks:", checks)
    for i, (remaining, assigned) in enumerate(servers, start=1):
        print(f"  Server {i}: {sorted(assigned, reverse=True)} "
              f"load={capacity - remaining}, remaining={remaining}")
    return servers


def run_b4():
    print("\n========== B4: BIN PACKING - FIRST FIT DECREASING ==========")
    normal = [42, 69, 17, 38, 25, 55, 8, 31, 64, 12,
              47, 23, 76, 5, 33, 58, 19, 81, 27, 36]
    display_packing("Normal workload case", normal, 100)
    print("Exact minimum for normal case:",
          exact_minimum_bins(normal, 100))

    challenge = [31, 43, 29, 37, 53, 30, 43, 27]
    display_packing("Challenge workload case", challenge, 100)
    print("Exact minimum for challenge case:",
          exact_minimum_bins(challenge, 100))
    print("One optimal packing: [37, 31, 29], [53, 43], [43, 30, 27]")

    print("\nScale test:")
    print(f"{'Items':>8} {'Servers':>9} {'Lower bound':>13} "
          f"{'Fit checks':>12} {'Time (s)':>12}")
    for n in (1000, 5000, 20000):
        rng = random.Random(n)
        workloads = [rng.randint(1, 60) for _ in range(n)]
        start = time.perf_counter()
        servers, checks = first_fit_decreasing(workloads, 100)
        elapsed = time.perf_counter() - start
        lower_bound = math.ceil(sum(workloads) / 100)
        print(f"{n:8} {len(servers):9} {lower_bound:13} "
              f"{checks:12} {elapsed:12.6f}")


# ---------------------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------------------

def main():
    print("DESIGN AND ANALYSIS OF ALGORITHMS - ASSIGNMENT 5 (CO5)")
    print("Search, Complexity and Approximation Engineering")
    run_b1()
    run_b2()
    run_b3()
    run_b4()
    print("\nAll Assignment 5 implementation tasks completed.")


if __name__ == "__main__":
    main()
