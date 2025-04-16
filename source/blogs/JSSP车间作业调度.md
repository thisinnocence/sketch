# JSSP车间作业调度

✨ Job-Shop Scheduling Problem (JSSP) 通用建模与最小例解析

## 📌 问题背景

**作业车间调度问题（Job-Shop Scheduling Problem, JSSP）** 是生产调度中的经典 NP-Hard 问题。目标是在满足一系列资源和顺序约束的前提下，安排若干作业（Jobs）在不同机器（Machines）上按工序依次执行，使得所有作业完成所需的时间（即 Makespan）最小。

---

## 🧾 通用问题建模

### 📐 符号定义

- 作业集合：$\mathcal{J} = \{J_1, J_2, \dots, J_n\}$
- 机器集合：$\mathcal{M} = \{M_1, M_2, \dots, M_m\}$
- 作业 $J_i$ 包含 $k_i$ 道工序（operations）：$O_{i1}, O_{i2}, \dots, O_{i{k_i}}$
- 每道工序 $O_{ij}$：
  - 加工所需机器：$M_{ij} \in \mathcal{M}$
  - 加工耗时：$p_{ij}$
  - 开始时间变量：$S_{ij}$
- 总完成时间（Makespan）：$C_{\max}$

---

### ✅ 约束建模

1. **工序顺序约束**（作业内部工序需按序加工）：

   对所有作业 $J_i$，其工序必须满足顺序依赖：

   $$
   S_{i,j} + p_{i,j} \leq S_{i,j+1}, \quad \forall i \in [1, n],\; \forall j \in [1, k_i - 1]
   $$

2. **机器互斥约束**（同一台机器不能同时加工多个工序）：

   对任意两个不同作业 $J_i$ 和 $J_{i'}$ 中的工序 $O_{ij}$ 和 $O_{i'j'}$，若使用相同机器：

   $$
   \text{if } M_{ij} = M_{i'j'} \text{ then: } \\
   S_{ij} + p_{ij} \leq S_{i'j'} \quad \text{or} \quad S_{i'j'} + p_{i'j'} \leq S_{ij}
   $$

3. **非负时间约束**：

   所有开始时间必须为非负：

   $$
   S_{ij} \geq 0, \quad \forall i, j
   $$

---

### 🎯 目标函数

我们要最小化所有作业完成时间中的最大值（Makespan）：

$$
\min C_{\max} = \max_{i \in [1,n]} \left( S_{i,k_i} + p_{i,k_i} \right)
$$

注释：​Makespan（最大完成时间）​​：所有作业中最后一个完成作业的结束时间。

---

## 📘 最简单的2作业-2工序示例

为方便理解，我们从一个实例开始：

### 实例输入：

- **Job1**：
  - $O_{11}$：在 $M_1$ 加工，耗时 $p_{11} = 2$
  - $O_{12}$：在 $M_2$ 加工，耗时 $p_{12} = 3$

- **Job2**：
  - $O_{21}$：在 $M_2$ 加工，耗时 $p_{21} = 3$
  - $O_{22}$：在 $M_1$ 加工，耗时 $p_{22} = 2$

### 最优解

**最有任务调度**

- **Job1**：
  - $O_{11}$：$[0, 2]$ on $M_1$
  - $O_{12}$：$[3, 6]$ on $M_2$
  
- **Job2**：
  - $O_{21}$：$[0, 3]$ on $M_2$
  - $O_{22}$：$[3, 5]$ on $M_1$

**机器占用时间线**

- $M_1$：0–2（Job1），3–5（Job2）
- $M_2$：0–3（Job2），3–6（Job1）

因此，总完成时间：

$$
C_{\max} = 6
$$

---

## 🛠️ 求解工具推荐

以下是适合 JSSP 问题求解的主流工具：

| 工具         | 类型         | 支持语言     | 特点               |
|--------------|--------------|--------------|--------------------|
| **CPLEX**    | 商业 MILP     | OPL, Python  | 高效精确，工业级   |
| **Gurobi**   | 商业 MILP/CP | Python       | 强大通用 MILP 求解 |
| **OR-Tools** | 开源 CP-SAT  | Python       | 轻量快速，Google 出品 |
| **Lingo**    | 商业建模语言 | 内置语法     | 上手快，适合教学   |

### 📌 OR-Tools 建模示例

针对上面的例子：

```python
from ortools.sat import cp_model_pb2
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple

# ===================== 类型别名定义 =====================
IntVar = cp_model.IntVar
IntervalVar = cp_model.IntervalVar
Operation = Dict[str, int]  # 工序类型：包含 machine 和 duration 的字典
Job = List[Operation]  # 作业类型：工序列表

# ===================== 固定输入数据 =====================
jobs_data: List[Job] = [
    [  # Job1的工序 (M1耗时2 → M2耗时3)
        {"machine": 0, "duration": 2},
        {"machine": 1, "duration": 3}
    ],
    [  # Job2的工序 (M2耗时3 → M1耗时2)
        {"machine": 1, "duration": 3},
        {"machine": 0, "duration": 2}
    ]
]

# ===================== OR-Tools 建模 =====================
model: cp_model.CpModel = cp_model.CpModel()
horizon: int = sum(op["duration"] for job in jobs_data for op in job)

# --------------- 1. 定义变量 ---------------
intervals_dict: Dict[Tuple[int, int], Tuple[IntVar, IntVar, IntervalVar]] = {}
machine_intervals: Dict[int, List[IntervalVar]] = {}

for job_id, job in enumerate(jobs_data):
    for op_id, op in enumerate(job):
        suffix: str = f'j{job_id}_o{op_id}'
        start: IntVar = model.NewIntVar(0, horizon, f'start_{suffix}')
        end: IntVar = model.NewIntVar(0, horizon, f'end_{suffix}')
        interval: IntervalVar = model.NewIntervalVar(
            start, op["duration"], end, f'interval_{suffix}'
        )
        intervals_dict[(job_id, op_id)] = (start, end, interval)

        machine: int = op["machine"]
        if machine not in machine_intervals:
            machine_intervals[machine] = []
        machine_intervals[machine].append(interval)

# --------------- 2. 添加工序顺序约束 ---------------
for job_id, job in enumerate(jobs_data):
    for op_id in range(len(job) - 1):
        _, end_current, _ = intervals_dict[(job_id, op_id)]
        start_next, _, _ = intervals_dict[(job_id, op_id + 1)]
        model.Add(end_current <= start_next)

# --------------- 3. 添加机器互斥约束 ---------------
for machine, intervals_list in machine_intervals.items():
    model.AddNoOverlap(intervals_list)

# --------------- 4. 定义目标函数 ---------------
makespan: IntVar = model.NewIntVar(0, horizon, 'makespan')
all_ends: List[IntVar] = [
    intervals_dict[(job_id, len(job) - 1)][1] for job_id, job in enumerate(jobs_data)
]
model.AddMaxEquality(makespan, all_ends)
model.Minimize(makespan)

# ===================== 求解并输出结果 =====================
solver: cp_model.CpSolver = cp_model.CpSolver()
status: cp_model_pb2.CpSolverStatus = solver.Solve(model)  # 状态码直接使用 int 类型

if status == cp_model.OPTIMAL:
    print(f"最优解 Makespan = {solver.Value(makespan)}")

    # 输出每个工序的时间
    print("\n工序调度详情:")
    for job_id, job in enumerate(jobs_data):
        print(f"\nJob {job_id}:")
        for op_id, op in enumerate(job):
            start_val: int = solver.Value(intervals_dict[(job_id, op_id)][0])
            end_val: int = solver.Value(intervals_dict[(job_id, op_id)][1])
            print(f"  Op{op_id}: 机器{op['machine']} [{start_val}-{end_val}]")

    # 按机器输出时间线
    print("\n机器占用时间线:")
    for machine in machine_intervals:
        print(f"\nMachine {machine}:")
        timeline: List[Tuple[int, int, str]] = []
        for job_id, job in enumerate(jobs_data):
            for op_id, op in enumerate(job):
                if op["machine"] == machine:
                    start_val = solver.Value(intervals_dict[(job_id, op_id)][0])
                    end_val = solver.Value(intervals_dict[(job_id, op_id)][1])
                    timeline.append((start_val, end_val, f'Job{job_id}_Op{op_id}'))
        # 按开始时间排序输出
        for start, end, name in sorted(timeline, key=lambda x: x[0]):
            print(f"  {start}–{end}: {name}")
else:
    print("未找到最优解")
```

运行结果：

```txt
最优解 Makespan = 6

工序调度详情:

Job 0:
  Op0: 机器0 [0-2]
  Op1: 机器1 [3-6]

Job 1:
  Op0: 机器1 [0-3]
  Op1: 机器0 [3-5]

机器占用时间线:

Machine 0:
  0–2: Job0_Op0
  3–5: Job1_Op1

Machine 1:
  0–3: Job1_Op0
  3–6: Job0_Op1
```

---

## 🔍 延伸讨论与总结

- **数学建模核心**：构造工序时间变量，限制顺序与资源冲突，目标最小化 $C_{\max}$。
- **扩展性**：可以进一步支持：
  - 每工序有多个可选机器（灵活作业车间）
  - 限制机器空闲时间、设置优先级等
- **大型问题**：对于大规模 JSSP，可采用遗传算法、模拟退火、禁忌搜索等启发式方法。
