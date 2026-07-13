.. Michael Wu Copyright 2026,-

:Authors: Michael Wu
:Version: 0.2

数据结构与算法
***************

Overview
========

最近作为面试官面了不少人，总结一下核心算法和数据结构的知识点。

.. csv-table:: Data Structure & Algorithm Overview
   :header: "章节", "内容", "备注"
   :widths: 18, 64, 18

   "复杂度分析", "时间复杂度、空间复杂度、Big O", "基础"
   "线性结构", "数组、链表、栈、队列、字符串", "基础"
   "非线性结构", "树、二叉树、堆、Hash Table、图", "基础"
   "基础算法", "查找、排序、遍历", "基础"
   "图算法", "DFS、BFS、最短路径、最小生成树、拓扑排序、并查集", "基础"
   "算法范式", "递归、分治、回溯、贪心、动态规划", "基础"
   "高级数据结构", "Trie、Segment Tree、Fenwick Tree、Skip List、Bloom Filter", "进阶"
   "工程应用", "标准库容器、索引、缓存、调度、路由、图搜索", "进阶"

术语:

- Big O: 表示算法复杂度的渐进上界，忽略常数和低阶项，描述输入规模 n 趋近于无穷大时的增长趋势。
- BFS: Breadth-First Search，从起点开始，先访问所有邻居，再逐层向外扩展。
- DFS: Depth-First Search，从起点开始，沿着一条路径一直走到底，再回溯到上一个分叉点。
- Trie: 前缀树，一种多叉树，用于存储字符串集合，支持高效的前缀查询。
- Segment Tree: 线段树，一种二叉树，用于高效处理区间查询和更新问题。
- Fenwick Tree: 树状数组，一种数据结构，用于高效处理前缀和查询和单点更新。
- Skip List: 跳表，一种基于多层链表的概率性数据结构，支持快速查找、插入和删除。
- Bloom Filter: 布隆过滤器，一种空间效率高的概率性数据结构，用于测试元素是否在集合中。标准 Bloom Filter
  只支持插入，允许把不存在的元素误判为存在，但不会把已插入的元素误判为不存在。

关键定义：

- 时间复杂度：时间复杂度是衡量算法执行时间随输入规模增长而增长的度量，通常用 Big O 表示。
- 空间复杂度：空间复杂度是衡量算法执行过程中所需额外空间随输入规模增长而增长的度量，通常用 Big O 表示。

线性结构
========

Linear structure
----------------

元素按线性次序组织，重点掌握存储方式、基本操作、复杂度及典型应用。

.. csv-table:: Linear structure core knowledge
   :header: "结构", "结构与实现", "经典算法 / 技巧", "核心考点"

   "数组", "连续内存、下标访问、动态扩容", "二分查找、双指针、滑动窗口、前缀和", "随机访问 O(1)；中间增删 O(n)；扩容的摊还分析"
   "链表", "单链表、双链表、循环链表；指针连接", "反转、合并、快慢指针、环检测", "已知节点增删 O(1)；查找 O(n)；指针边界与虚拟头节点"
   "栈", "LIFO, 数组或链表实现", "括号匹配、表达式求值、单调栈、DFS", "push / pop O(1)；栈溢出；递归与显式栈的转换"
   "队列", "FIFO, 循环数组/链表/deque 实现", "BFS、层序遍历、单调队列、滑动窗口", "入队 / 出队 O(1)；空与满的判定；环形下标"
   "字符串", "字符序列；可变 / 不可变；编码", "朴素匹配、KMP、双指针", "子串与子序列；匹配复杂度；边界、编码与拷贝成本"

术语解释：

- KMP: Knuth-Morris-Pratt 算法，字符串匹配算法，通过预处理模式串构建部分匹配表，避免重复比较。
- Deque: Double-ended queue，双端队列，支持在两端进行插入和删除操作。``std::queue<T>`` 默认使用
  ``std::deque<T>``，也可以指定 ``std::list<T>`` 等满足接口要求的底层容器。

快慢指针
----------

快慢指针判断是否包含环, Floyd Cycle Detection 算法，时间复杂度 O(n)，空间复杂度 O(1), 只额外维护固定数量
的变量，不会随着链表长度 n 增长而增加额外存储。

.. code-block:: c

   typedef struct Node {
       int value;
       struct Node *next;
   } Node;

   // Fast pointer moves 2 steps, slow pointer moves 1 step; 
   // if they meet, there is a cycle
   bool has_cycle(const Node *head) {
       const Node *slow = head;
       const Node *fast = head;

       while (fast != NULL && fast->next != NULL) {
           slow = slow->next;
           fast = fast->next->next;
           if (slow == fast) {
               return true;
           }
       }
       return false;
   }

字符串匹配
-------------

对于字符串匹配，朴素算法时间复杂度 O(mn)，KMP 算法时间复杂度 O(m + n)，其中 m 和 n 分别是文本串和模式串的长度。

在 C/C++ 中，标准主要规定接口行为，具体搜索算法由库实现决定：

- C：C 标准不规定 ``strstr`` 的算法和复杂度；glibc 对较短模式使用 modified Horspool，对长模式使用 Two-Way，musl 主要使用 Two-Way。
- C++17：标准只规定 ``std::string::find`` 的结果，不规定具体算法和复杂度；朴素实现的最坏复杂度为 O(mn)，
  标准库可以使用更高效的算法。

.. note::

   字符串匹配算法的选择取决于模式串长度、文本串长度以及是否需要处理特殊字符（如通配符）。实际的标准库
   通常会根据模式串长度和实现细节选择合适的算法，以在平均情况下提供更好的性能。
   对于常见的 leetcode 中的字符串匹配类的题目，C/C++ 的 ``strstr`` 或 ``std::string::find`` 的实现
   通常足够高效。

   C++11 引入了 ``std::regex``，提供正则表达式匹配功能，可以处理更复杂的模式匹配需求，但其性能可能不如专门的字符串匹配算法。

哈希表
========

哈希表通过 Hash 函数将 key 映射到 Bucket，重点掌握冲突处理、装载因子、扩容与复杂度退化。

.. csv-table:: Hash Table
   :header: "主题", "结构与实现", "经典算法 / 技巧", "核心考点"

   "基本结构", "key 经 Hash 函数映射到 Bucket；Map / Set", "insert、find、erase、去重、频次统计", "平均 O(1)，最坏 O(n)；通常不保证遍历顺序"
   "Hash 函数", "将 key 稳定、均匀地分布到 Bucket", "取模、位混合、组合字段 Hash", "相等的 key 必须有相同 Hash；避免使用可变 key"
   "冲突处理", "链地址法；开放定址法", "线性探测、二次探测、双重 Hash", "聚集问题；开放定址删除需要 Tombstone"
   "装载因子与扩容", "load factor = 元素数 / Bucket 数；超阈值后 rehash", "扩容、缩容、渐进式 rehash", "C++17 rehash 平均 O(n)、最坏 O(n²)；iterator 失效，pointer / reference 保持有效"
   "典型应用", "用空间换取查询时间", "Two Sum、分组、缓存、索引、集合运算", "根据是否需要有序性选择 Hash Table 或 Balanced BST"

术语解释：

- Bucket: 哈希表中存储元素的容器，通常是链表或数组。
- Tombstone: 开放定址法中标记已删除元素的占位符，避免破坏探测序列。

基于 hash 的数据结构，C++17 里的 ``unordered_map`` 和 ``unordered_set`` 通常使用链地址法处理冲突，
平均时间复杂度为 O(1)，最坏情况为 O(n)。C++17 标准不规定具体实现细节，但常见实现
如 libstdc++ 和 libc++ 都采用了类似的设计。

Java ``HashMap`` 在 Bucket 节点达到 8 且表容量至少为 64 时可转为红黑树。
C++ ``unordered_map`` 技术上也可采用类似策略，但 libstdc++ 和 libc++ 等常见实现没有这样做，主要权衡包括：

- 标准约束：只要求平均 O(1)，允许最坏 O(n)，没有树化要求。
- 内存开销：红黑树节点还需要父子指针和颜色信息。
- 实现复杂度：树化会增加 Bucket、节点、迭代器及 ABI 的维护成本。
- 实际收益：Hash 分布正常时长冲突链很少，树化的额外成本难以摊薄。
- 排序问题：C++ 无序容器只要求 Hash 和相等比较；完全相同的 Hash 且 key 不可比较时，树化也难以保证 O(log n) 查找。
- 最坏保证：若需要 O(log n) 的最坏复杂度，应使用 ``std::map`` / ``std::set``。

树
===

Tree
----

树是层次化的非线性结构，重点掌握遍历、递归定义、高度与操作复杂度。

.. csv-table:: Tree
   :header: "结构", "结构与实现", "经典算法 / 技巧", "核心考点"

   "树基础", "根、父子节点、叶子、子树、深度、高度", "DFS、BFS、递归与迭代遍历", "n 个节点有 n - 1 条边；时间 O(n)；辅助空间取决于树高"
   "二叉树", "每个节点至多两个子节点", "前序、中序、后序、层序；重建、高度、直径、LCA", "遍历顺序；递归与栈；空树、单节点和退化链表"
   "二叉搜索树(BST)", "左子树 < 根 < 右子树", "查找、插入、删除、合法性校验、第 k 小", "平均 O(log n)，最坏 O(n)；删除节点的三种情况"
   "平衡二叉搜索树", "AVL、Red-Black Tree；通过旋转维持平衡", "左旋、右旋、插入 / 删除后再平衡", "树高 O(log n)；理解平衡目的与旋转原理，细节属进阶"
   "Heap / Priority Queue", "完全二叉树；通常用数组存储；大/小顶堆", "heapify、push、pop、Top-K、堆排序", "建堆 O(n)；插入、删除堆顶或已知下标 O(log n)；按值查找 O(n)"
   "Huffman Tree", "带权路径长度最小的二叉树", "贪心构造、Huffman 编码", "WPL；前缀码；优先队列构造 O(n log n)"

术语解释：

- WPL（Weighted Path Length，带权路径长度）：所有叶子节点的『权值 × 路径长度』之和。
- AVL（Adelson-Velsky and Landis）Tree：任意节点的左右子树高度差不超过 1 的自平衡二叉搜索树。
- LCA（Lowest Common Ancestor，最近公共祖先）：树中同时为两个节点祖先且深度最大的节点。
- Auxiliary Space（辅助空间）：算法除输入数据外使用的额外工作空间；树的递归遍历中，recursion stack 占用 O(h)，h 为树高。
- Perfect Binary Tree：每一层都被节点填满；若根为第 0 层，高度为 h 时共有 ``2^(h+1) - 1`` 个节点。
- Complete Binary Tree（完全二叉树）：除最后一层外均填满，最后一层从左向右连续排列；满二叉树是其特例。
- Tree Reconstruction（树重建）：根据遍历序列还原树；节点值唯一时，前序 + 中序或后序 + 中序可唯一确定二叉树。
- Tree Height（树高）：根节点到最深叶子节点的最长路径；路径按边数或节点数计算需事先约定。
- Tree Diameter（树的直径）：任意两个节点之间的最长路径，不一定经过根节点；可用后序遍历在 O(n) 时间内求解。
- Order Statistic（顺序统计）：按有序集合中的排名查询第 ``k`` 小 / 大元素；BST 可用中序遍历求解，平衡树若额外保存子树大小，可在 O(log n) 时间内查询。

典型的树遍历，使用递归：

.. code-block:: cpp

    struct TreeNode {
        int val;
        TreeNode *left;
        TreeNode *right;
        TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    };

    void pre_order(TreeNode* root, vector<int>& res) {
        if (!root) return;
        res.push_back(root->val);
        pre_order(root->left, res);
        pre_order(root->right, res);
    }

B-tree 与 B+ tree
-----------------

二叉搜索树适合内存中的动态有序集合；数据库或文件系统面对磁盘 / SSD page 时，更关心减少 I/O 次数。
这就需要让一个节点容纳更多索引分支，用更高的 fan-out（扇出，即一个节点可以指向的子节点数量）降低树高，
B-tree 是这种多路搜索树的经典结构。

B-tree（B 树）是一种高度平衡的多路搜索树。每个节点可以保存多个有序 key，内部节点通过 child pointer
指向不同的 key range，所有叶子节点位于同一层。

B+ tree（B+ 树）是 B-tree 的一种变体。内部节点只保存用于查找的 key 和 child pointer，record 或
record pointer 全部放在叶子节点；所有叶子节点位于同一层，并通常按 key 顺序连接。point lookup 通过内部
节点定位 leaf，range scan 则找到起始 key 后沿 leaf 链顺序读取。工程实现通常让一个节点接近一个 page 大小，
以减少 I/O 次数。

Trie 与 Radix Tree
------------------

Trie（前缀树）是一种按 key 的字符、byte 或 bit 逐层分支的多叉树。从 root 到某个节点的路径表示一个
prefix，terminal 标记用于区分完整 key 和普通前缀。若 child 可以 O(1) 访问，查找长度为 ``L`` 的 key
需要 O(L) 时间，与集合中的 key 数量没有直接关系。使用固定 child array 实现的 Trie 可能预留大量空
pointer。

Radix Tree（压缩前缀树）会把只有一个 child 的连续路径压缩成一条带字符串或 bit sequence 的 edge，从而减少
节点数量和内存占用。这类结构常用于命令补全、词典查询和 IP longest-prefix match；若 child 使用 Hash Table
或 Balanced BST，还要计入相应的 child lookup 成本。

工程中的树
----------

.. csv-table:: Tree in Practice
   :header: "需求", "常见结构", "原因"
   :widths: 28, 28, 44

   "语法和层次关系", "AST / 普通多叉树", "结构天然具有 parent-child 关系"
   "外部存储索引与范围查询", "B+ tree", "分支多、树高低，适合 page I/O 和顺序扫描"
   "前缀与最长前缀匹配", "Trie / Radix Tree", "查询路径由 key 的字符、byte 或 bit 决定"
   "区间重叠查询", "Interval Tree", "节点维护子树区间信息，可跳过不可能重叠的分支"

图
===

Graph
-----

图由顶点和边组成，重点掌握建模、存储、遍历，以及根据边权和图的性质选择算法。

.. csv-table:: Graph
   :header: "主题", "结构与实现", "经典算法 / 技巧", "核心考点"

   "图基础", "有向 / 无向、带权 / 无权；顶点、边、度、路径、环", "建图、入度 / 出度统计", "邻接矩阵空间 O(V²)；邻接表空间 O(V + E)"
   "图遍历", "邻接表 / 邻接矩阵；visited 状态", "DFS、BFS、连通分量、环检测、路径恢复", "邻接表下 O(V + E)；DFS 用递归 / 栈，BFS 用队列"
   "拓扑排序", "DAG；依赖关系与入度", "Kahn 算法（BFS）、DFS 后序", "仅适用于 DAG；结果可能不唯一；可检测有向环"
   "最短路径", "根据无权、边权非负、含负权等条件选择算法", "BFS、Dijkstra、Bellman-Ford、Floyd-Warshall", "BFS：O(V + E)；Dijkstra 不允许负权边；Floyd-Warshall：O(V³)"
   "最小生成树(MST)", "连通、带权无向图；覆盖所有顶点且边权和最小", "Kruskal + Union-Find、Prim + Heap", "与最短路径的区别；Kruskal 通常为 O(E log E)"
   "并查集(DSU)", "parent 数组、按秩 / 大小合并、路径压缩", "find、union、动态连通性、环检测", "均摊复杂度接近 O(1)；擅长合并与查询，不擅长删除"

术语解释：

- DAG（Directed Acyclic Graph，有向无环图）：没有环的有向图。
- DSU（Disjoint Set Union, 并查集）：也常常叫做 Union-Find，一种支持合并和查询连通性的高效数据结构。
- MST（Minimum Spanning Tree，最小生成树）：覆盖所有顶点且边权和最小的生成树。
- Dijkstra 算法：用于计算单源最短路径的算法，要求图中所有边权非负。
- Bellman-Ford 算法：用于计算单源最短路径，允许负权边，并能检测源点可达的负权环；受负权环影响的顶点
  不存在有限最短路径。
- Floyd-Warshall 算法：用于计算任意两点间最短路径的动态规划算法，适用于稠密图。

图的构建和存储
---------------

图的存储结构，C++17 数据结构举例：

图的构造：

.. code-block:: cpp

   // 邻接表：无权图, graph[i] 存储与顶点 i 相邻的顶点列表
   using Graph = std::vector<std::vector<int>>;

   // 邻接表：有权图, weighted_graph[i] 存储与顶点 i 相邻的边列表
   struct Edge {
       int to;     // 邻接点
       int weight; // 边权
   };
   using WeightedGraph = std::vector<std::vector<Edge>>;

   void construct_graph() {
       const int n = 5;

       // 邻接表：空间 O(V + E)，适合稀疏图
       Graph graph(n);
       graph[0].push_back(1);  // 0 -> 1

       // 带权邻接表：Edge = {邻接点, 边权}
       WeightedGraph weighted_graph(n);
       weighted_graph[0].push_back(Edge{1, 10});  // 0 -10-> 1

       // 带权邻接矩阵：nullopt 表示无边，因而可以表示权重为 0 的边
       std::vector<std::vector<std::optional<int>>> matrix(
           n, std::vector<std::optional<int>>(n));
       matrix[0][1] = 1;  // 0 -1-> 1
   }

图BFS遍历与回溯
------------------

图 BFS 遍历，如果是无权图(每个边权重相同)，BFS 可以找到从起点到其他顶点的最短路径:

.. code-block:: cpp

   // 邻接表, graph[i] 存储与顶点 i 相邻的顶点列表
   using Graph = std::vector<std::vector<int>>;

   // 对于 BFS 适合使用邻接表存储图，因为它可以在 O(V + E) 时间内访问所有邻居；对于稠密图，邻接矩阵通常更合适
   void bfs(const Graph& graph, int start) {
       std::vector<bool> visited(graph.size(), false); // 辅助信息，标记顶点是否已访问
       std::queue<int> que; // 存储待访问的顶点, BFS 算法辅助数据结构

       visited[start] = true;
       que.push(start);

       while (!que.empty()) {
           const int u = que.front();
           que.pop();
           std::cout << u << " "; // 输出访问顺序

           for (const int v : graph[u]) {
               if (!visited[v]) {
                  visited[v] = true;
                  que.push(v);
               }
           }
       }
   }

图 BFS 遍历 + 回溯：

.. code-block:: cpp

   // 邻接表, graph[i] 存储与顶点 i 相邻的顶点列表
   using Graph = std::vector<std::vector<int>>;

   // 返回 start 到 target 的最短路径；空 vector 表示不可达
   std::vector<int> bfs_path(const Graph& graph, int start, int target) {
       std::vector<int> parent(graph.size(), -1); // 同时用作 visited
       std::queue<int> queue;

       parent[start] = start;
       queue.push(start);

       while (!queue.empty()) {
           const int u = queue.front();
           queue.pop();

           if (u == target) {
               break;
           }

           for (const int v : graph[u]) {
               if (parent[v] != -1) {
                   continue;
               }
               parent[v] = u;
               queue.push(v);
           }
       }

       if (parent[target] == -1) {
           return {};
       }

       std::vector<int> reversed_path;
       for (int v = target; v != start; v = parent[v]) {
           reversed_path.push_back(v);
       }
       reversed_path.push_back(start);

       return std::vector<int>(reversed_path.rbegin(), reversed_path.rend());
   }

Dijkstra 算法
----------------

一个 C++17 的例子：

.. code-block:: cpp

    using Edge = std::pair<int, int>; // {to, weight}
    using Graph = std::vector<std::vector<Edge>>; // 邻接表

    // 非负权图单源最短路径算法，返回 start 到 target 的最短路径；空 vector 表示不可达
    std::vector<int> dijkstra(const Graph& graph, int start, int target) {
        const long long INF = std::numeric_limits<long long>::max();
        std::vector<long long> dist(graph.size(), INF);
        std::vector<int> parent(graph.size(), -1);

        // 最小堆，存储 {distance, vertex}，用于选择当前距离最小的顶点
        using QueueEntry = std::pair<long long, int>;
        std::priority_queue<QueueEntry, std::vector<QueueEntry>, std::greater<>> pq;
        
        dist[start] = 0;
        pq.push({0, start});
        
        while (!pq.empty()) {
            auto [d, u] = pq.top(); 
            pq.pop();
            if (d != dist[u]) continue;
            if (u == target) break;
            
            for (auto [v, w] : graph[u]) {
                // 松弛操作：尝试通过 u 改善 v 的距离
                if (d > INF - static_cast<long long>(w)) continue; // 防止整数溢出
                const long long candidate = d + w;
                if (dist[v] > candidate) {
                    dist[v] = candidate;
                    parent[v] = u; // 记录前驱节点，用于路径回溯
                    pq.push({dist[v], v});
                }
            }
        }
        
        // 回溯路径
        if (dist[target] == INF) return {};
        std::vector<int> path;
        for (int v = target; v != -1; v = parent[v]) {
            path.push_back(v);
        }
        std::reverse(path.begin(), path.end());
        return path;
    }

排序算法
========

排序的核心是掌握时间 / 空间复杂度、稳定性、原地性及适用场景。在比较决策树模型下，对任意输入进行排序的
最坏时间下界为 Ω(n log n)。

.. csv-table:: 排序算法核心知识
   :header: "算法", "核心思想", "时间复杂度（最好 / 平均 / 最坏）", "空间 / 稳定性", "核心考点"

   "Bubble Sort", "交换相邻逆序元素", "O(n) / O(n²) / O(n²)", "O(1) / 稳定", "无交换时提前结束"
   "Selection Sort", "每轮选出最小元素", "O(n²) / O(n²) / O(n²)", "O(1) / 不稳定", "比较次数固定；交换次数少"
   "Insertion Sort", "将元素插入已排序区间", "O(n) / O(n²) / O(n²)", "O(1) / 稳定", "适合小规模或基本有序数据"
   "Merge Sort", "分治；合并两个有序区间", "O(n log n) / O(n log n) / O(n log n)", "O(n) / 稳定", "递归拆分与 merge；适合外部排序"
   "Quick Sort", "partition 后递归排序两侧", "O(n log n) / O(n log n) / O(n²)", "平均 O(log n)，最坏 O(n) / 不稳定", "pivot 选择、partition、随机化与栈深度"
   "Heap Sort", "建堆后反复取堆顶", "O(n log n) / O(n log n) / O(n log n)", "O(1) / 不稳定", "建堆 O(n)；下沉 O(log n)"

C/C++ 标准库提供的排序算法：

- ``qsort``：C 标准只规定按比较函数排序，不规定具体算法和复杂度；相等元素的顺序未指定，因此不保证稳定。
- ``std::sort``：不稳定，标准保证 O(n log n) 次比较；常见实现是 introsort。
- ``std::stable_sort``：稳定；空间充足时 O(n log n)，否则 O(n log² n)；常见实现基于 merge sort。
- ``std::partial_sort``：将前 k 个元素排好序，其余元素顺序未指定，复杂度约为 O(n log k)；常见实现使用 heap。
- ``std::nth_element``：平均 O(n)，不保证稳定；保证第 n 个元素就位，并保证前半区元素不大于后半区元素，
  但不完整排序；常见实现基于 quickselect 或 introselect。

算法范式
==========

算法范式是解决一类问题的通用思维模式，重点是识别问题结构、定义状态并证明正确性。

.. csv-table:: 算法范式核心知识
   :header: "范式", "核心思想", "经典问题", "核心考点"

   "递归", "用更小规模的同类问题定义当前问题", "树遍历、DFS、阶乘、汉诺塔", "终止条件、递归关系、调用栈深度与重复计算"
   "分治", "分解为相互独立的子问题，分别求解后合并", "Merge Sort、Quick Sort、二分查找", "分解、求解、合并；递推公式/主定理"
   "回溯", "沿状态空间 DFS；选择、探索、撤销选择", "排列、组合、子集、N-Queens", "状态恢复、去重、剪枝；最坏通常为指数级"
   "贪心", "每步选择当前最优解，且不回退", "区间调度、Huffman Tree、Kruskal、Prim", "需证明贪心选择性；常用交换论证；局部最优不一定导出全局最优"
   "动态规划（DP）", "利用重叠子问题和最优子结构复用计算结果", "背包、LCS、LIS、路径计数", "状态定义、转移方程、初始化、遍历顺序；记忆化与递推；空间优化"

术语解释：

- LCS（Longest Common Subsequence，最长公共子序列）：两个序列共有的最长子序列，元素不要求连续。
- LIS（Longest Increasing Subsequence，最长递增子序列）：序列中严格递增的最长子序列。

LCS 的动态规划解法举例：

.. code-block:: cpp

    // 返回 LCS 的长度, 不要求连续
    int longestCommonSubsequence(string& text1, string& text2) {
        int m = text1.size(), n = text2.size();
        vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
        
        for (int i = 1; i <= m; ++i) {
            for (int j = 1; j <= n; ++j) {
                if (text1[i-1] == text2[j-1]) {
                    dp[i][j] = dp[i-1][j-1] + 1;
                } else {
                    // 允许跳过字符，继承前面的结果(子序列不要求连续)
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
                }
            }
        }
        return dp[m][n];
    }

总结
=====

作为面试官，面试基础知识，我个人最关注的 CS 核心专业课是：

- 数据结构与算法
- 操作系统
- 计算机体系结构

配合的语言主要是 C/C++，最贴近底层，能体现对内存、指针、性能的理解。

对于大多数数据结构和算法而言，理解其核心思想与设计原理，远比死记硬背具体实现更有价值。
在实际工程中，我们需要的往往不是机械地套用某种固定的数据结构或算法流程，而是能够将它们
灵活地融入复杂的业务逻辑与代码体系之中——例如侵入式链表、带有大量嵌套引用和功能字段的
复杂图结构等。只有真正理解了底层机制，才能在这些场景中做出合理的设计和优化。
