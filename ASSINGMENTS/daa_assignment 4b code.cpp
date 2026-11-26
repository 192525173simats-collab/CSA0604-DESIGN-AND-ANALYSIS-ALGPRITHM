// DAA Assignment 4B - Part II
// C++17 implementation of all six tasks in the supplied assignment.

#include <bits/stdc++.h>
using namespace std;

using ll = long long;
const ll INF = (1LL << 60);

// TASK 1: WORD WRAP USING DYNAMIC PROGRAMMING
void wordWrap() {
    cout << "\n========== TASK 1: WORD WRAP DP ==========\n";
    vector<string> words = {
        "Dynamic", "programming", "helps", "arrange",
        "words", "into", "clean", "lines"
    };
    int W = 16;
    int n = (int)words.size();

    vector<ll> dp(n + 1, INF);
    vector<int> nextBreak(n, -1);
    dp[n] = 0;

    for (int i = n - 1; i >= 0; --i) {
        int used = 0;
        for (int j = i; j < n; ++j) {
            used += (j == i ? 0 : 1) + (int)words[j].size();
            if (used > W) break;

            int extra = W - used;
            ll lineCost = (j == n - 1) ? 0LL : 1LL * extra * extra;
            if (lineCost + dp[j + 1] < dp[i]) {
                dp[i] = lineCost + dp[j + 1];
                nextBreak[i] = j + 1;
            }
        }
    }

    if (n > 0 && nextBreak[0] == -1) {
        cout << "No valid layout: at least one word exceeds the width.\n";
        return;
    }

    cout << "Line width: " << W << "\n";
    cout << "Minimum penalty: " << dp[0] << "\n";
    cout << "Formatted lines:\n";

    for (int i = 0; i < n; ) {
        int j = nextBreak[i];
        int used = 0;
        for (int k = i; k < j; ++k) {
            if (k > i) cout << ' ';
            cout << words[k];
            used += (int)words[k].size() + (k == i ? 0 : 1);
        }
        int unused = W - used;
        ll penalty = (j == n) ? 0LL : 1LL * unused * unused;
        cout << " | used=" << used
             << ", unused=" << unused
             << ", line penalty=" << penalty << "\n";
        i = j;
    }

    cout << "DP suffix costs: ";
    for (ll value : dp) cout << value << ' ';
    cout << "\n";
}

// TASK 2: FRACTIONAL KNAPSACK AND 0/1 KNAPSACK
struct Item {
    string name;
    int weight;
    int value;
};

void knapsack() {
    cout << "\n========== TASK 2: KNAPSACK ==========\n";
    vector<Item> items = {
        {"A", 10, 60}, {"B", 20, 100}, {"C", 30, 120}
    };
    const int capacity = 50;

    vector<Item> sortedItems = items;
    sort(sortedItems.begin(), sortedItems.end(),
         [](const Item& a, const Item& b) {
             return (double)a.value / a.weight >
                    (double)b.value / b.weight;
         });

    double remaining = capacity;
    double fractionalValue = 0.0;
    cout << "Fractional selection: ";
    for (const auto& item : sortedItems) {
        if (remaining <= 0) break;
        double fraction = min(1.0, remaining / item.weight);
        fractionalValue += fraction * item.value;
        remaining -= fraction * item.weight;
        cout << item.name << "(" << fixed << setprecision(2)
             << fraction << ") ";
    }
    cout << "\nFractional maximum value: "
         << fractionalValue << "\n";

    int n = (int)items.size();
    vector<vector<int>> dp(n + 1, vector<int>(capacity + 1, 0));

    for (int i = 1; i <= n; ++i) {
        for (int c = 0; c <= capacity; ++c) {
            dp[i][c] = dp[i - 1][c];
            if (items[i - 1].weight <= c) {
                dp[i][c] = max(
                    dp[i][c],
                    items[i - 1].value +
                    dp[i - 1][c - items[i - 1].weight]
                );
            }
        }
    }

    vector<string> selected;
    int c = capacity;
    for (int i = n; i > 0; --i) {
        if (dp[i][c] != dp[i - 1][c]) {
            selected.push_back(items[i - 1].name);
            c -= items[i - 1].weight;
        }
    }
    reverse(selected.begin(), selected.end());

    cout << "0/1 maximum value: " << dp[n][capacity] << "\n";
    cout << "0/1 selected items: ";
    for (const auto& name : selected) cout << name << ' ';
    cout << "\nCounterexample: ratio-greedy chooses A+B = 160, "
         << "while optimal 0/1 DP chooses B+C = 220.\n";
}

// TASK 3: DIJKSTRA, BELLMAN-FORD, FLOYD-WARSHALL AND WARSHALL
struct Edge {
    int from, to, weight;
};

vector<ll> dijkstra(const vector<vector<pair<int,int>>>& graph,
                    int source, vector<int>& parent,
                    vector<int>& finalOrder) {
    int n = (int)graph.size();
    vector<ll> dist(n, INF);
    vector<bool> visited(n, false);
    using State = pair<ll,int>;
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [currentDistance, u] = pq.top();
        pq.pop();

        if (visited[u]) continue;
        visited[u] = true;
        finalOrder.push_back(u);

        for (auto [v, weight] : graph[u]) {
            if (!visited[v] && currentDistance + weight < dist[v]) {
                dist[v] = currentDistance + weight;
                parent[v] = u;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}

bool bellmanFord(int n, const vector<Edge>& edges, int source,
                 vector<ll>& dist) {
    dist.assign(n, INF);
    dist[source] = 0;

    for (int i = 1; i < n; ++i) {
        bool changed = false;
        for (const auto& e : edges) {
            if (dist[e.from] != INF &&
                dist[e.from] + e.weight < dist[e.to]) {
                dist[e.to] = dist[e.from] + e.weight;
                changed = true;
            }
        }
        if (!changed) break;
    }

    for (const auto& e : edges) {
        if (dist[e.from] != INF &&
            dist[e.from] + e.weight < dist[e.to]) {
            return false; // reachable negative cycle
        }
    }
    return true;
}

void routing() {
    cout << "\n========== TASK 3: ROUTING ALGORITHMS ==========\n";
    const int n = 8;
    vector<Edge> edges = {
        {0,1,4}, {0,2,8}, {1,2,2}, {1,3,5},
        {2,3,1}, {2,4,7}, {3,4,3}, {3,5,6},
        {4,5,2}, {4,6,5}, {5,6,1}, {6,7,2},
        {5,7,6}
    };

    vector<vector<pair<int,int>>> graph(n);
    for (const auto& e : edges)
        graph[e.from].push_back({e.to, e.weight});

    vector<int> parent(n, -1), order;
    vector<ll> dist = dijkstra(graph, 0, parent, order);

    cout << "Dijkstra distances from A:\n";
    for (int i = 0; i < n; ++i)
        cout << char('A' + i) << " = "
             << (dist[i] == INF ? -1 : dist[i]) << "\n";

    cout << "Finalisation order: ";
    for (int v : order) cout << char('A' + v) << ' ';
    cout << "\n";

    cout << "Shortest paths from A:\n";
    for (int v = 0; v < n; ++v) {
        if (dist[v] == INF) continue;
        vector<int> path;
        for (int x = v; x != -1; x = parent[x]) path.push_back(x);
        reverse(path.begin(), path.end());
        cout << char('A' + v) << ": ";
        for (int i = 0; i < (int)path.size(); ++i) {
            if (i) cout << " -> ";
            cout << char('A' + path[i]);
        }
        cout << "\n";
    }

    // Negative edge example where Dijkstra's greedy finalisation is unsafe.
    vector<Edge> negativeEdges = {
        {0,1,2}, {0,2,5}, {2,1,-10}
    };
    vector<ll> bfDist;
    bool noNegativeCycle = bellmanFord(3, negativeEdges, 0, bfDist);
    cout << "Bellman-Ford negative-edge example: "
         << "S->X(2), S->Y(5), Y->X(-10)\n";
    cout << "Shortest distance S to X = " << bfDist[1]
         << ", reachable negative cycle = "
         << (noNegativeCycle ? "No" : "Yes") << "\n";

    vector<Edge> cycleEdges = {
        {0,1,1}, {1,2,-2}, {2,1,1}
    };
    bool cycleFree = bellmanFord(3, cycleEdges, 0, bfDist);
    cout << "Negative-cycle test: "
         << (cycleFree ? "No reachable negative cycle"
                       : "Reachable negative cycle detected") << "\n";

    vector<vector<ll>> fw(n, vector<ll>(n, INF));
    vector<vector<bool>> reach(n, vector<bool>(n, false));

    for (int i = 0; i < n; ++i) {
        fw[i][i] = 0;
        reach[i][i] = true;
    }
    for (const auto& e : edges) {
        fw[e.from][e.to] = min(fw[e.from][e.to], (ll)e.weight);
        reach[e.from][e.to] = true;
    }

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (fw[i][k] != INF && fw[k][j] != INF)
                    fw[i][j] = min(fw[i][j], fw[i][k] + fw[k][j]);
                reach[i][j] = reach[i][j] ||
                              (reach[i][k] && reach[k][j]);
            }
        }
    }

    cout << "Floyd-Warshall distance matrix (-1 = unreachable):\n";
    for (const auto& row : fw) {
        for (ll x : row)
            cout << (x == INF ? -1 : x) << '\t';
        cout << "\n";
    }

    cout << "Warshall reachability matrix (1 = reachable):\n";
    for (const auto& row : reach) {
        for (bool x : row) cout << (x ? 1 : 0) << ' ';
        cout << "\n";
    }
}

// TASK 4: ASSEMBLY LINE SCHEDULING
void assemblyLine() {
    cout << "\n========== TASK 4: ASSEMBLY LINE DP ==========\n";
    vector<int> a1 = {7, 9, 3, 4, 8, 4};
    vector<int> a2 = {8, 5, 6, 4, 5, 7};
    vector<int> t1 = {2, 3, 1, 3, 4};
    vector<int> t2 = {2, 1, 2, 2, 1};
    int entry1 = 2, entry2 = 4, exit1 = 3, exit2 = 2;
    int n = (int)a1.size();

    vector<int> f1(n), f2(n), pred1(n, 1), pred2(n, 2);
    f1[0] = entry1 + a1[0];
    f2[0] = entry2 + a2[0];

    for (int j = 1; j < n; ++j) {
        int stay1 = f1[j - 1] + a1[j];
        int transfer1 = f2[j - 1] + t2[j - 1] + a1[j];
        if (stay1 <= transfer1) {
            f1[j] = stay1;
            pred1[j] = 1;
        } else {
            f1[j] = transfer1;
            pred1[j] = 2;
        }

        int stay2 = f2[j - 1] + a2[j];
        int transfer2 = f1[j - 1] + t1[j - 1] + a2[j];
        if (stay2 <= transfer2) {
            f2[j] = stay2;
            pred2[j] = 2;
        } else {
            f2[j] = transfer2;
            pred2[j] = 1;
        }

        cout << "Station " << j + 1
             << ": line1 stay=" << stay1
             << ", transfer=" << transfer1
             << "; line2 stay=" << stay2
             << ", transfer=" << transfer2 << "\n";
    }

    int bestTime;
    int line;
    if (f1[n - 1] + exit1 <= f2[n - 1] + exit2) {
        bestTime = f1[n - 1] + exit1;
        line = 1;
    } else {
        bestTime = f2[n - 1] + exit2;
        line = 2;
    }

    vector<int> route(n);
    for (int j = n - 1; j >= 0; --j) {
        route[j] = line;
        line = (line == 1) ? pred1[j] : pred2[j];
    }

    cout << "Optimal line sequence: ";
    for (int x : route) cout << "L" << x << ' ';
    cout << "\nMinimum production time: " << bestTime << "\n";
}

// TASK 5: KRUSKAL, PRIM AND BORUVKA MST
struct DSU {
    vector<int> parent, rankValue;
    DSU(int n) : parent(n), rankValue(n, 0) {
        iota(parent.begin(), parent.end(), 0);
    }
    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }
    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) return false;
        if (rankValue[a] < rankValue[b]) swap(a, b);
        parent[b] = a;
        if (rankValue[a] == rankValue[b]) ++rankValue[a];
        return true;
    }
};

void minimumSpanningTrees() {
    cout << "\n========== TASK 5: MINIMUM SPANNING TREE ==========\n";
    const int n = 6;
    vector<Edge> edges = {
        {0,1,4}, {0,2,3}, {1,2,1}, {1,3,2},
        {2,3,4}, {2,4,5}, {3,4,2}, {3,5,7}, {4,5,3}
    };

    // Kruskal
    vector<Edge> sortedEdges = edges;
    sort(sortedEdges.begin(), sortedEdges.end(),
         [](const Edge& a, const Edge& b) {
             return a.weight < b.weight;
         });

    DSU kruskalDSU(n);
    int kruskalCost = 0, chosen = 0;
    cout << "Kruskal selected edges: ";
    for (const auto& e : sortedEdges) {
        if (kruskalDSU.unite(e.from, e.to)) {
            cout << char('A' + e.from) << "-"
                 << char('A' + e.to) << "(" << e.weight << ") ";
            kruskalCost += e.weight;
            ++chosen;
        }
    }
    cout << "\nKruskal total cost: " << kruskalCost
         << ", edges selected: " << chosen << "\n";

    // Prim
    vector<vector<pair<int,int>>> graph(n);
    for (const auto& e : edges) {
        graph[e.from].push_back({e.to, e.weight});
        graph[e.to].push_back({e.from, e.weight});
    }

    vector<bool> used(n, false);
    using PrimState = tuple<int,int,int>; // weight, vertex, parent
    priority_queue<PrimState, vector<PrimState>,
                   greater<PrimState>> pq;
    pq.push({0, 0, -1});
    int primCost = 0, primEdges = 0;

    cout << "Prim selected edges: ";
    while (!pq.empty()) {
        auto [weight, u, parent] = pq.top();
        pq.pop();
        if (used[u]) continue;
        used[u] = true;

        if (parent != -1) {
            cout << char('A' + parent) << "-"
                 << char('A' + u) << "(" << weight << ") ";
            primCost += weight;
            ++primEdges;
        }

        for (auto [v, w] : graph[u])
            if (!used[v]) pq.push({w, v, u});
    }
    cout << "\nPrim total cost: " << primCost
         << ", edges selected: " << primEdges << "\n";

    // Boruvka
    DSU boruvkaDSU(n);
    int components = n, boruvkaCost = 0;
    cout << "Boruvka phases:\n";

    while (components > 1) {
        vector<int> cheapest(n, -1);

        for (int i = 0; i < (int)edges.size(); ++i) {
            const auto& e = edges[i];
            int a = boruvkaDSU.find(e.from);
            int b = boruvkaDSU.find(e.to);
            if (a == b) continue;

            if (cheapest[a] == -1 ||
                edges[cheapest[a]].weight > e.weight)
                cheapest[a] = i;
            if (cheapest[b] == -1 ||
                edges[cheapest[b]].weight > e.weight)
                cheapest[b] = i;
        }

        bool changed = false;
        for (int i = 0; i < n; ++i) {
            int index = cheapest[i];
            if (index == -1) continue;
            const auto& e = edges[index];
            if (boruvkaDSU.unite(e.from, e.to)) {
                cout << char('A' + e.from) << "-"
                     << char('A' + e.to) << "(" << e.weight << ") ";
                boruvkaCost += e.weight;
                --components;
                changed = true;
            }
        }
        cout << "\n";
        if (!changed) break;
    }

    cout << "Boruvka total cost: " << boruvkaCost << "\n";
}

// TASK 6: TRAVELLING SALESPERSON USING HELD-KARP DP
void travellingSalesperson() {
    cout << "\n========== TASK 6: TSP HELD-KARP DP ==========\n";

    // Vertex 0 is the hub; vertices 1..5 are delivery locations.
    vector<vector<int>> cost = {
        {0, 10, 15, 20, 12, 18},
        {10, 0, 35, 25, 17, 22},
        {15, 35, 0, 30, 20, 16},
        {20, 25, 30, 0, 11, 19},
        {12, 17, 20, 11, 0, 13},
        {18, 22, 16, 19, 13, 0}
    };

    int n = (int)cost.size() - 1; // number of delivery locations
    int totalMasks = 1 << n;
    const int TSP_INF = 1e9;

    vector<vector<int>> dp(totalMasks, vector<int>(n, TSP_INF));
    vector<vector<int>> parent(totalMasks, vector<int>(n, -1));
    long long statesVisited = 0;

    for (int j = 0; j < n; ++j)
        dp[1 << j][j] = cost[0][j + 1];

    for (int mask = 1; mask < totalMasks; ++mask) {
        for (int j = 0; j < n; ++j) {
            if (!(mask & (1 << j))) continue;
            ++statesVisited;

            int previousMask = mask ^ (1 << j);
            if (previousMask == 0) continue;

            for (int i = 0; i < n; ++i) {
                if (!(previousMask & (1 << i))) continue;
                int candidate = dp[previousMask][i] +
                                cost[i + 1][j + 1];
                if (candidate < dp[mask][j]) {
                    dp[mask][j] = candidate;
                    parent[mask][j] = i;
                }
            }
        }
    }

    int fullMask = totalMasks - 1;
    int bestCost = TSP_INF, last = -1;

    for (int j = 0; j < n; ++j) {
        int candidate = dp[fullMask][j] + cost[j + 1][0];
        if (candidate < bestCost) {
            bestCost = candidate;
            last = j;
        }
    }

    vector<int> route;
    int mask = fullMask;
    while (last != -1) {
        route.push_back(last + 1);
        int previous = parent[mask][last];
        mask ^= (1 << last);
        last = previous;
    }
    reverse(route.begin(), route.end());

    cout << "Minimum tour cost: " << bestCost << "\n";
    cout << "Optimal route: Hub";
    for (int vertex : route)
        cout << " -> " << char('A' + vertex);
    cout << " -> Hub\n";
    cout << "DP endpoint states processed: " << statesVisited << "\n";
}

int main() {
    cout << "DESIGN AND ANALYSIS OF ALGORITHMS\n";
    cout << "ASSIGNMENT 4 - PART II (C++17)\n";

    wordWrap();
    knapsack();
    routing();
    assemblyLine();
    minimumSpanningTrees();
    travellingSalesperson();

    cout << "\nAll six task implementations completed.\n";
    return 0;
}
