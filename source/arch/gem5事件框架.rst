gem5 事件框架
=================

源码基线 `24a11f7a95 <https://github.com/gem5/gem5/tree/24a11f7a951899a70fa76f3d072e7792c313e65b>`__\ 。以 Classic Cache 和 ``MemCtrl`` 的 Timing
访存路径为例。

**请求已经产生，但资源何时可用还未知，请求放在哪里，由谁唤醒？**
取决于接收方是否已经接收请求。被拒绝时，上游保留请求，等下游通知
Retry。已接收时，组件可以先把请求放进自己的队列，再由内部仲裁推进。

.. list-table::
   :header-rows: 1

   * - 阶段
     - 保存位置
     - 下一步由谁触发
   * - 请求被拒绝
     - 上游的 Pending/Blocked 状态
     - 下游恢复接收后发出 Retry，上游重新发送
   * - 请求已接收，等待服务
     - 组件内部的 Request Queue 等状态
     - 组件根据资源状态和时序约束推进仲裁
   * - 回调已调度
     - EventQueue 保存 Event 和触发 Tick
     - ``serviceOne()`` 取出事件，将仿真时间推进到该 Tick，再调用 ``process()``

Cache MSHR 满时，请求留在上游
--------------------------------------

MSHR（Miss Status Holding Register）记录正在处理的 cache miss。
假设 Tick 1000 时，CPU 发起一条 Load，而 L1 Cache 因 MSHR 已满
阻塞了请求入口。

1. 上游调用 ``sendTimingReq(pkt)``\ ，Cache 返回 ``false``\ 。被拒绝的
   Packet 由这一跳的发送方保留，等待 Retry。
2. 后续某个 Tick，下级响应返回。若处理响应后释放了 MSHR，Cache
   清除 ``Blocked_NoMSHRs``\ 。当所有阻塞原因都清除且有待通知的发送方时，
   Cache 端口将 ``sendRetryEvent`` 调度到 ``curTick() + 1``\ 。
3. 该事件调用 ``sendRetryReq()``\ ，直接进入对端的 ``recvReqRetry()``\ 。
   上游由此重新尝试发送，接收结果以这次 ``sendTimingReq()`` 的返回值为准。

`BaseCache 响应与 Retry <https://github.com/gem5/gem5/blob/24a11f7a951899a70fa76f3d072e7792c313e65b/src/mem/cache/base.cc>`__ ·
`Timing 协议回调 <https://github.com/gem5/gem5/blob/24a11f7a951899a70fa76f3d072e7792c313e65b/src/mem/protocol/timing.cc#L95>`__

.. mermaid::

   sequenceDiagram
       participant Up as 上游发送方
       participant L1 as L1 Cache
       participant Down as 下级存储
       participant EQ as EventQueue

       Up->>L1: Tick 1000 · sendTimingReq(Packet N)
       L1-->>Up: MSHR 已满，返回 false
       Note over Up: 保留 Packet N，等待 Retry
       Down->>L1: 某个 Tick · 已在途的 miss 返回响应
       L1->>L1: 释放 MSHR，清除阻塞
       L1->>EQ: schedule(sendRetryEvent, curTick() + 1)
       EQ->>L1: 执行 sendRetryEvent
       L1->>Up: sendRetryReq() → recvReqRetry()
       Up->>L1: 再次 sendTimingReq(Packet N)
       L1-->>Up: 本次接收成功，返回 true

``SimpleMemobj`` 提供了最小实现。它的 ``MemSidePort`` 用
``blockedPacket`` 保存发送失败的 Packet，收到 ``recvReqRetry()`` 后
取出并重发，再次失败就重新保存。它在解除自身阻塞后也可以直接发出
Retry，因此唤醒和重发可以发生在同一个调用栈内。
`SimpleMemobj <https://github.com/gem5/gem5/blob/24a11f7a951899a70fa76f3d072e7792c313e65b/src/learning_gem5/part2/simple_memobj.cc>`__

MemCtrl 接收请求后，仍需等待内部资源
--------------------------------------------------

- **读队列容量不足。** ``recvTimingReq()`` 设置 ``retryRdReq`` 并返回
  ``false``\ 。上游保留请求。读响应处理释放容量后，\ ``MemCtrl`` 发出 Retry。
- **读请求已入队。** 待访问 DRAM 的请求进入 ``readQueue``\ 。
  ``nextReqEvent`` 驱动控制器按队列状态和 DRAM 时序约束选取请求。
  即使仲裁事件已经有了触发 Tick，某条请求何时访问 DRAM Bank 仍取决于
  后续仲裁和资源状态。

Wait Queue 的职责分布在发送方和资源组件的状态中。
组件决定何时接收、仲裁和唤醒。EventQueue 按明确的 Tick 执行回调，
挂起的请求由资源状态变化或组件调度的事件推进。
`EventQueue::serviceOne() <https://github.com/gem5/gem5/blob/24a11f7a951899a70fa76f3d072e7792c313e65b/src/sim/eventq.cc#L224>`__

通用抽象：资源约束下的离散事件仿真
---------------------------------------------------

假设仿真引擎正在执行事件 ``ev₁``\ ，其回调产生了一个后续事件 ``ev₂``\ 。
此时 ``ev₂`` 依赖的资源何时 ready 还未知。调度器先把 ``ev₂`` 的待调度
记录挂到该资源的 **Wait Queue**\ ，也可以用按资源索引的其他数据结构保存。
这条记录携带后续回调和资源依赖，等启动时间确定后再加入事件队列。

资源状态变化时，\ **Resource Scheduler** 被唤醒并重新检查条件。
条件仍未满足时，记录继续挂起。条件满足时，调度器取出记录，
为 ``ev₂`` 确定触发时间并加入 **Scheduled Events**\ 。

.. mermaid::

   sequenceDiagram
       participant E as 仿真引擎
       participant S as 资源调度器
       participant R as 资源
       participant Q as 该资源的等待队列

       E->>E: 在 t₁ 执行 ev₁ 的回调
       E->>S: 回调产生 ev₂，请求使用资源
       S->>R: 查询资源何时可用
       R-->>S: ready 时间未知
       S->>Q: 保存 ev₂ 的待调度记录
       Note over E,Q: ev₁ 返回，仿真引擎继续处理其他事件
       loop 每次相关资源状态变化
           R->>S: 通知状态变化
           S->>Q: 查看 ev₂ 的待调度记录
           S->>S: 重新检查启动条件
           Note over Q: 条件仍未满足时保留记录
       end
       S->>Q: 条件满足，取出 ev₂ 的记录
       S->>E: 将 ev₂ 加入事件队列，触发时间为 t₂
       E->>E: 在 t₂ 执行 ev₂ 的回调

**待处理操作记录谁在等，资源调度器决定谁能启动，已调度事件记录何时执行回调。**
