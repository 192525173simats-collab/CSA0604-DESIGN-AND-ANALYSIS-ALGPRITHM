/*
    DESIGN AND ANALYSIS OF ALGORITHMS - ASSIGNMENT 4A
    Optional executable practice implementation of Tasks 1-6.

    Compile:
        g++ -std=c++17 -O2 daa_assignment4a.cpp -o daa_assignment4a

    Run:
        ./daa_assignment4a

    On Windows:
        daa_assignment4a.exe

    Note:
    The supplied Part I brief asks for language-independent pseudocode.
    This C++ file is for practice/validation, not a substitute for that submission.
*/

#include <algorithm>
#include <climits>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

const long long INF = numeric_limits<long long>::max() / 4;

// ------------------------------------------------------------------
// TASK 1: FRACTIONAL KNAPSACK (Greedy)
// ------------------------------------------------------------------

struct Package {
    string id;
    double weight;
    double value;
};

struct FractionalResult {
    vector<pair<string, double>> selected; // package ID and selected fraction
    double totalWeight = 0.0;
    double totalValue = 0.0;
};

FractionalResult fractionalKnapsack(vector<Package> packages, double capacity) {
    if (capacity < 0) throw invalid_argument("Capacity cannot be negative.");

    for (const auto& p : packages) {
        if (p.weight <= 0) throw invalid_argument("Package weight must be positive.");
    }

    sort(packages.begin(), packages.end(),
         [](const Package& a, const Package& b) {
             return (a.value / a.weight) > (b.value / b.weight);
         });

    FractionalResult result;
    double remaining = capacity;

    for (const auto& p : packages) {
        if (remaining <= 1e-12) break;

        double fraction = min(1.0, remaining / p.weight);
        if (fraction > 0) {
            result.selected.push_back({p.id, fraction});
            double loaded = fraction * p.weight;
            result.totalWeight += loaded;
            result.totalValue += fraction * p.value;
            remaining -= loaded;
        }
    }
    return result;
}

// ------------------------------------------------------------------
// TASK 2: JOB SEQUENCING WITH DEADLINES (Greedy)
// ------------------------------------------------------------------

struct DeadlineJob {
    string id;
    int deadline;
    int profit;
};

struct JobSequenceResult {
    vector<string> slots; // index 0 represents slot 1
    int totalProfit = 0;
};

JobSequenceResult jobSequencing(vector<DeadlineJob> jobs) {
    int maxDeadline = 0;
    for (const auto& job : jobs) {
        if (job.deadline < 0) throw invalid_argument("Deadline cannot be negative.");
        maxDeadline = max(maxDeadline, job.deadline);
    }

    sort(jobs.begin(), jobs.end(),
         [](const DeadlineJob& a, const DeadlineJob& b) {
             return a.profit > b.profit;
         });

    JobSequenceResult result;
    result.slots.assign(maxDeadline, "");

    for (const auto& job : jobs) {
        for (int slot = min(job.deadline, maxDeadline) - 1; slot >= 0; --slot) {
            if (result.slots[slot].empty()) {
                result.slots[slot] = job.id;
                result.totalProfit += job.profit;
                break;
            }
        }
    }
    return result;
}

// ------------------------------------------------------------------
// TASK 3: 0/1 KNAPSACK USING DYNAMIC PROGRAMMING
// ------------------------------------------------------------------

struct Item {
    string id;
    int weight;
    int value;
};

struct KnapsackResult {
    int maximumValue = 0;
    vector<string> selectedItems;
    vector<vector<int>> dp;
};

KnapsackResult zeroOneKnapsack(const vector<Item>& items, int capacity) {
    if (capacity < 0) throw invalid_argument("Capacity cannot be negative.");
    for (const auto& item : items) {
        if (item.weight < 0) throw invalid_argument("Item weight cannot be negative.");
    }

    int n = static_cast<int>(items.size());
    vector<vector<int>> dp(n + 1, vector<int>(capacity + 1, 0));

    for (int i = 1; i <= n; ++i) {
        for (int c = 0; c <= capacity; ++c) {
            dp[i][c] = dp[i - 1][c]; // exclude item
            if (items[i - 1].weight <= c) {
                int includeValue =
                    items[i - 1].value +
                    dp[i - 1][c - items[i - 1].weight];
                dp[i][c] = max(dp[i][c], includeValue);
            }
        }
    }

    KnapsackResult result;
    result.maximumValue = dp[n][capacity];
    result.dp = dp;

    int c = capacity;
    for (int i = n; i >= 1; --i) {
        if (dp[i][c] != dp[i - 1][c]) {
            result.selectedItems.push_back(items[i - 1].id);
            c -= items[i - 1].weight;
        }
    }
    reverse(result.selectedItems.begin(), result.selectedItems.end());
    return result;
}

// ------------------------------------------------------------------
// TASK 4: WORD BREAK - CORRECTED DYNAMIC PROGRAMMING
// ------------------------------------------------------------------

struct WordBreakResult {
    bool possible = false;
    vector<string> words;
};

WordBreakResult wordBreak(const string& text,
                          const unordered_set<string>& dictionary) {
    int n = static_cast<int>(text.size());
    vector<bool> dp(n + 1, false);
    vector<int> previous(n + 1, -1);
    dp[0] = true;

    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j < i; ++j) {
            // Both conditions are essential:
            // prefix [0,j) must be segmentable and text[j,i) must be a word.
            string candidate = text.substr(j, i - j);
            if (dp[j] && dictionary.count(candidate)) {
                dp[i] = true;
                previous[i] = j;
                break;
            }
        }
    }

    WordBreakResult result;
    result.possible = dp[n];

    if (result.possible) {
        int position = n;
        while (position > 0) {
            int start = previous[position];
            if (start < 0) break;
            result.words.push_back(text.substr(start, position - start));
            position = start;
        }
        reverse(result.words.begin(), result.words.end());
    }
    return result;
}

// ------------------------------------------------------------------
// TASK 5A: DIJKSTRA - NON-NEGATIVE EDGE WEIGHTS
// ------------------------------------------------------------------

struct Edge {
    int from;
    int to;
    int weight;
};

struct ShortestPathResult {
    vector<long long> distance;
    vector<int> predecessor;
};

ShortestPathResult dijkstra(int vertices,
                            const vector<Edge>& edges,
                            int source) {
    if (source < 0 || source >= vertices)
        throw invalid_argument("Invalid source vertex.");

    vector<vector<pair<int, int>>> graph(vertices);
    for (const auto& e : edges) {
        if (e.weight < 0)
            throw invalid_argument("Dijkstra requires non-negative edge weights.");
        graph[e.from].push_back({e.to, e.weight});
    }

    vector<long long> dist(vertices, INF);
    vector<int> pred(vertices, -1);
    priority_queue<pair<long long, int>,
                   vector<pair<long long, int>>,
                   greater<pair<long long, int>>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [currentDistance, u] = pq.top();
        pq.pop();

        if (currentDistance != dist[u]) continue;

        for (auto [v, weight] : graph[u]) {
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pred[v] = u;
                pq.push({dist[v], v});
            }
        }
    }
    return {dist, pred};
}

// ------------------------------------------------------------------
// TASK 5B: BELLMAN-FORD - NEGATIVE EDGES AND CYCLE DETECTION
// ------------------------------------------------------------------

struct BellmanFordResult {
    vector<long long> distance;
    vector<int> predecessor;
    bool reachableNegativeCycle = false;
};

BellmanFordResult bellmanFord(int vertices,
                              const vector<Edge>& edges,
                              int source) {
    if (source < 0 || source >= vertices)
        throw invalid_argument("Invalid source vertex.");

    vector<long long> dist(vertices, INF);
    vector<int> pred(vertices, -1);
    dist[source] = 0;

    for (int i = 1; i <= vertices - 1; ++i) {
        bool changed = false;
        for (const auto& e : edges) {
            if (dist[e.from] != INF &&
                dist[e.from] + e.weight < dist[e.to]) {
                dist[e.to] = dist[e.from] + e.weight;
                pred[e.to] = e.from;
                changed = true;
            }
        }
        if (!changed) break;
    }

    bool negativeCycle = false;
    for (const auto& e : edges) {
        if (dist[e.from] != INF &&
            dist[e.from] + e.weight < dist[e.to]) {
            negativeCycle = true;
            break;
        }
    }
    return {dist, pred, negativeCycle};
}

// ------------------------------------------------------------------
// TASK 5C: FLOYD-WARSHALL - ALL-PAIRS SHORTEST PATHS
// ------------------------------------------------------------------

vector<vector<long long>> floydWarshall(
    int vertices, const vector<Edge>& edges) {

    vector<vector<long long>> dist(
        vertices, vector<long long>(vertices, INF));

    for (int i = 0; i < vertices; ++i) dist[i][i] = 0;

    for (const auto& e : edges) {
        dist[e.from][e.to] = min(
            dist[e.from][e.to], static_cast<long long>(e.weight));
    }

    for (int k = 0; k < vertices; ++k) {
        for (int i = 0; i < vertices; ++i) {
            for (int j = 0; j < vertices; ++j) {
                if (dist[i][k] != INF && dist[k][j] != INF) {
                    dist[i][j] = min(dist[i][j],
                                     dist[i][k] + dist[k][j]);
                }
            }
        }
    }
    return dist;
}

// ------------------------------------------------------------------
// TASK 6: WEIGHTED INTERVAL SCHEDULING (DYNAMIC PROGRAMMING)
// ------------------------------------------------------------------

struct IntervalJob {
    string id;
    int start;
    int finish;
    int value;
};

struct IntervalResult {
    int maximumValue = 0;
    vector<string> selectedJobs;
    vector<int> predecessor;
    vector<int> optimal;
};

IntervalResult weightedIntervalScheduling(vector<IntervalJob> jobs) {
    sort(jobs.begin(), jobs.end(),
         [](const IntervalJob& a, const IntervalJob& b) {
             if (a.finish != b.finish) return a.finish < b.finish;
             return a.start < b.start;
         });

    int n = static_cast<int>(jobs.size());
    vector<int> p(n + 1, 0);
    vector<int> finish(n + 1, 0);

    for (int i = 1; i <= n; ++i) finish[i] = jobs[i - 1].finish;

    // Find the last compatible job for each job.
    for (int i = 1; i <= n; ++i) {
        int low = 1, high = i - 1, answer = 0;
        while (low <= high) {
            int mid = (low + high) / 2;
            if (finish[mid] <= jobs[i - 1].start) {
                answer = mid;
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        p[i] = answer;
    }

    vector<int> opt(n + 1, 0);
    for (int i = 1; i <= n; ++i) {
        int take = jobs[i - 1].value + opt[p[i]];
        int skip = opt[i - 1];
        opt[i] = max(take, skip);
    }

    vector<string> selected;
    int i = n;
    while (i > 0) {
        int take = jobs[i - 1].value + opt[p[i]];
        int skip = opt[i - 1];

        if (take > skip) {
            selected.push_back(jobs[i - 1].id);
            i = p[i];
        } else {
            --i;
        }
    }
    reverse(selected.begin(), selected.end());

    return {opt[n], selected, p, opt};
}

// ------------------------------------------------------------------
// DISPLAY HELPERS AND SAMPLE RUNS
// ------------------------------------------------------------------

void printDistances(const vector<long long>& dist) {
    for (int i = 0; i < static_cast<int>(dist.size()); ++i) {
        cout << "Vertex " << i << ": ";
        if (dist[i] == INF) cout << "UNREACHABLE\n";
        else cout << dist[i] << '\n';
    }
}

void runTask1() {
    cout << "\n========== TASK 1: FRACTIONAL KNAPSACK ==========\n";
    vector<Package> packages = {
        {"A", 10, 60}, {"B", 20, 100}, {"C", 30, 120}
    };
    auto result = fractionalKnapsack(packages, 40);

    for (auto [id, fraction] : result.selected)
        cout << "Package " << id << " selected fraction: " << fraction << '\n';

    cout << "Total weight: " << result.totalWeight << '\n';
    cout << "Maximum value: " << result.totalValue << '\n';
}

void runTask2() {
    cout << "\n========== TASK 2: JOB SEQUENCING ==========\n";
    vector<DeadlineJob> jobs = {
        {"A", 2, 80}, {"B", 1, 35}, {"C", 2, 60},
        {"D", 3, 40}, {"E", 1, 25}
    };
    auto result = jobSequencing(jobs);

    for (int i = 0; i < static_cast<int>(result.slots.size()); ++i) {
        cout << "Slot " << i + 1 << ": "
             << (result.slots[i].empty() ? "EMPTY" : result.slots[i]) << '\n';
    }
    cout << "Total profit: " << result.totalProfit << '\n';
}

void runTask3() {
    cout << "\n========== TASK 3: 0/1 KNAPSACK ==========\n";
    vector<Item> items = {
        {"P", 2, 12}, {"Q", 3, 20}, {"R", 4, 25}, {"S", 5, 30}
    };
    auto result = zeroOneKnapsack(items, 7);

    cout << "Selected items: ";
    for (const auto& id : result.selectedItems) cout << id << " ";
    cout << "\nMaximum value: " << result.maximumValue << '\n';
}

void runTask4() {
    cout << "\n========== TASK 4: WORD BREAK ==========\n";
    string text = "ab";
    unordered_set<string> dictionary = {"b"};
    auto failing = wordBreak(text, dictionary);
    cout << "Text: " << text << ", dictionary: {b}\n";
    cout << "Can segment? " << (failing.possible ? "YES" : "NO") << '\n';

    text = "catsand";
    dictionary = {"cat", "cats", "and", "sand"};
    auto valid = wordBreak(text, dictionary);
    cout << "Text: " << text << ", dictionary: {cat, cats, and, sand}\n";
    cout << "Can segment? " << (valid.possible ? "YES" : "NO") << '\n';
    if (valid.possible) {
        cout << "Segmentation: ";
        for (const auto& word : valid.words) cout << word << " ";
        cout << '\n';
    }
}

void runTask5() {
    cout << "\n========== TASK 5: SHORTEST PATHS ==========\n";
    // Vertices: A=0, B=1, C=2, D=3, E=4
    vector<Edge> graph = {
        {0, 1, 4}, {0, 2, 7}, {1, 2, 2},
        {1, 3, 6}, {2, 3, 1}, {3, 4, 3}, {2, 4, 8}
    };

    cout << "Dijkstra from A:\n";
    auto d = dijkstra(5, graph, 0);
    printDistances(d.distance);

    cout << "\nBellman-Ford from A:\n";
    auto b = bellmanFord(5, graph, 0);
    printDistances(b.distance);
    cout << "Reachable negative cycle: "
         << (b.reachableNegativeCycle ? "YES" : "NO") << '\n';

    cout << "\nFloyd-Warshall distance matrix:\n";
    auto allPairs = floydWarshall(5, graph);
    for (const auto& row : allPairs) {
        for (long long value : row) {
            if (value == INF) cout << "INF ";
            else cout << value << " ";
        }
        cout << '\n';
    }
}

void runTask6() {
    cout << "\n========== TASK 6: WEIGHTED INTERVAL SCHEDULING ==========\n";
    vector<IntervalJob> jobs = {
        {"J1", 1, 3, 20}, {"J2", 2, 5, 50},
        {"J3", 4, 6, 30}, {"J4", 6, 8, 40},
        {"J5", 5, 9, 60}, {"J6", 8, 10, 30},
        {"J7", 9, 11, 50}, {"J8", 11, 13, 40}
    };
    auto result = weightedIntervalScheduling(jobs);

    cout << "Selected jobs: ";
    for (const auto& id : result.selectedJobs) cout << id << " ";
    cout << "\nMaximum total value: " << result.maximumValue << '\n';
}

int main() {
    cout << "DAA ASSIGNMENT 4A - TASKS 1 TO 6\n";
    cout << "Optional C++ practice implementation\n";

    try {
        runTask1();
        runTask2();
        runTask3();
        runTask4();
        runTask5();
        runTask6();
    } catch (const exception& ex) {
        cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

    cout << "\nAll sample tasks completed.\n";
    return 0;
}
