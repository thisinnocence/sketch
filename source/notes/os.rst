.. Michael Wu Copyright 2026,-

:Authors: Michael Wu
:Version: 0.3

操作系统
*********

Overview
========

这份笔记按 MIT OS 本科课程（典型是 6.S081 / xv6）的知识结构整理：从硬件边界出发，理解 kernel 如何把
CPU, memory, disk, device 抽象成 process, virtual memory, file, pipe, socket 等可组合的接口。

.. csv-table:: Operating System Overview
   :header: "章节", "内容", "核心问题"
   :widths: 18, 54, 28

   "Kernel / User", "privilege mode, system call, trap, interrupt", "用户程序如何安全进入内核"
   "Architecture", "ISA, privilege level, MMU, cache, interrupt, atomic instruction", "OS 依赖哪些硬件机制"
   "Process", "process, thread, context switch, scheduler", "CPU 如何在多个执行流之间复用"
   "Virtual Memory", "address space, page table, TLB, copy-on-write", "每个进程如何看见独立内存"
   "Concurrency", "lock, semaphore, sleep / wakeup, condition, deadlock", "共享状态如何保持正确"
   "File System", "inode, directory, buffer cache, logging", "磁盘块如何变成层次化文件"
   "I/O and Device", "driver, DMA, interrupt, polling", "外设如何和 kernel 协作"
   "Network", "packet, socket, protocol stack", "字节流和数据报如何跨机器传输"
   "Reliability", "crash consistency, isolation, least privilege", "系统失败时如何不破坏抽象"

术语：

- Kernel: 运行在 privileged mode 的核心程序，负责管理硬件资源并向用户程序提供受控接口。
- User mode: 普通应用运行的低权限模式，不能直接执行特权指令，也不能直接访问 kernel memory.
- System call: 用户程序请求 kernel 服务的同步入口，例如 ``fork``, ``exec``, ``read``, ``write``.
- Trap: 从 user mode 切到 kernel mode 的统一机制，来源可以是 system call, exception 或 interrupt.
- Process: 运行中程序的抽象，包含 address space, 寄存器状态、打开文件、当前目录等资源。
- Thread: CPU 执行流的抽象，拥有独立 registers / stack, 可与同进程线程共享 address space.
- Page table: virtual address 到 physical address 的映射表，同时保存权限位。
- Inode: file system 中描述文件元数据和数据块位置的对象。

关键定义：

- 操作系统的核心职责：抽象硬件、复用资源、隔离错误、提供持久化与通信接口。
- OS 设计的核心矛盾：接口要简单稳定，实现要处理并发、失败、性能和硬件细节。

Architecture
============

OS 不是直接运行在『抽象计算机』上，而是依赖 CPU, MMU, 中断控制器、cache, 总线和设备控制器提供的机制。
本科 OS 课程里不需要展开完整 CPU 设计，但要知道哪些体系结构能力会直接决定 kernel 的实现方式。

ISA 和 ABI
-----------

ISA (Instruction Set Architecture) 定义 CPU 能执行什么指令、有哪些寄存器、trap 指令如何编码、内存访问如何表达。
ABI (Application Binary Interface) 定义函数调用、参数传递、栈布局、system call number, 返回值等二进制约定。

.. code-block:: text

   C function call
       |
       |  compiler follows ABI
       v
   registers + stack + return address
       |
       |  CPU executes ISA instructions
       v
   instruction stream

OS 关心 ISA / ABI 的地方：

- Context switch 要保存和恢复 architecture-defined registers.
- System call 参数通常通过寄存器传给 kernel.
- Signal / trap return 要恢复用户态 PC, SP 和状态寄存器。
- Boot code, trap entry, spinlock 等路径会直接写 assembly.

Privilege Level
---------------

CPU privilege level 是 user / kernel isolation 的硬件基础。

以 RISC-V 为例，常见模式是 U-mode, S-mode, M-mode, xv6-riscv 主要运行在 S-mode, 用户程序运行在 U-mode.

.. code-block:: text

   U-mode: user program
       |
       |  ecall / interrupt / exception
       v
   S-mode: kernel
       |
       |  sret
       v
   U-mode: user program

核心点：

- User mode 不能执行 privileged instruction.
- Page table permission 会限制 user mode 可访问的 virtual address.
- Trap 发生时，CPU 保存 ``sepc``, ``scause``, ``sstatus`` 等少量控制状态并跳到 kernel 配置好的
  trap vector; 通用寄存器由 trap entry 软件保存。

以 Armv8-A / AArch64 为例，exception level 分为 EL0, EL1, EL2 和 EL3. 通常 user program 运行在 EL0,
Linux kernel 运行在 EL1; EL2 主要用于 hypervisor, EL3 主要用于 secure monitor.

.. code-block:: text

   EL0: user program
       |
       |  SVC / interrupt / exception
       v
   EL1: kernel
       |
       |  ERET
       v
   EL0: user program

核心点：

- ``SVC`` 指令用于从 EL0 发起 system call, 异常入口地址由 ``VBAR_EL1`` 指定。
- Exception 进入 EL1 时，CPU 把返回地址和原状态保存到 ``ELR_EL1``, ``SPSR_EL1``, 并通过
  ``ESR_EL1`` 记录异常原因；发生 address fault 时，``FAR_EL1`` 通常保存相关 virtual address.
- 通用寄存器仍由 exception entry 软件保存，处理完成后 ``ERET`` 根据 ``ELR_EL1`` 和 ``SPSR_EL1``
  返回原执行上下文。

Memory Hierarchy
----------------

现代机器的内存层次大致是 register, cache, DRAM, SSD / disk. OS 主要管理 DRAM 和 disk, 但 cache / TLB 会影响
context switch, memory ordering 和 I/O coherence.

.. code-block:: text

   CPU register
       |
       v
   L1 / L2 / L3 cache
       |
       v
   DRAM
       |
       v
   SSD / disk

OS 相关考点：

- Cache miss 会让同样的算法在不同内存访问模式下性能差异巨大。
- Spatial locality (空间局部性) / temporal locality (时间局部性) 决定 cache hit rate, kernel 会通过连续布局
  和复用热数据降低 cache miss.
- 多个 CPU 修改同一 cache line 中互不相关的数据也会产生 false sharing, 因此 per-CPU data 和
  cache-line alignment 对多核性能很重要。
- Cache coherence 保证多个 CPU 最终看到一致的 cache line 内容，但不保证不同 load / store 按源码顺序
  对其他 CPU 可见；memory ordering 还需要 architecture 提供的 barrier 和 atomic 语义。
- NUMA 系统中 local memory 与 remote memory 的访问成本不同，scheduler 和 allocator 需要考虑 CPU affinity
  与 memory placement.
- DMA 让设备直接在内存和设备之间传输数据，减少 CPU 搬运数据的工作；driver 必须处理 buffer ownership,
  地址映射，以及非 cache-coherent 平台上的 cache 一致性问题。

以 RISC-V 为例，``FENCE`` 约束 memory access 顺序，``LR`` / ``SC`` 和 AMO 通过 ``aq`` / ``rl`` bit 提供
acquire / release 语义。

以 AArch64 为例， ``DMB`` / ``DSB`` / ``ISB`` 提供不同范围的 ordering 和 synchronization; lock / atomic
operation 常使用带 acquire / release 语义的 ``LDAR`` / ``STLR``, ``LDAXR`` / ``STLXR`` 或 LSE atomic
instruction.

MMU 和 TLB
----------

MMU (Memory Management Unit) 根据 page table 把 virtual address 翻译成 physical address. TLB 是地址翻译缓存，
减少每次访存都遍历 page table 的成本。

.. code-block:: text

   virtual address
       |
       |  TLB hit
       v
   physical address

   virtual address
       |
       |  TLB miss
       v
   page table walk
       |
       v
   physical address + TLB fill

OS 相关考点：

- Page table entry 不只是地址映射，还包含 valid, read, write, execute, user 等权限位。
- 切换进程时通常要切换 page table root, TLB 中旧 address space 的缓存不能误用。
- Page fault 是 VM 功能的入口，可用于 lazy allocation, copy-on-write 和 demand paging.

Interrupt 和 Exception
----------------------

Interrupt 是外设或 timer 产生的异步事件；exception 是当前指令导致的同步异常；system call 通常也是一种受控 trap.

.. code-block:: text

   current instruction stream
       |
       +--> timer interrupt      -> preemption / scheduling
       +--> device interrupt     -> I/O completion
       +--> page fault           -> VM handler
       +--> system call          -> syscall dispatcher

OS 相关考点：

- Timer interrupt 是 preemptive scheduling 的基础。
- Device interrupt 让进程可以 sleep 等 I/O 完成，而不是一直 polling.
- Trap handler 必须保存现场，并区分事件来源。

Device 和 Bus
--------------

OS 通过 bus 和 device controller 访问外设。Driver 不直接『操作磁盘文件』，而是读写设备寄存器、提交 descriptor,
处理中断，并把结果交给上层 file system 或 network stack.

.. code-block:: text

   kernel driver
       |
       |  MMIO register / descriptor ring
       v
   device controller
       |
       |  DMA
       v
   memory buffer
       |
       |  interrupt when done
       v
   kernel driver

OS 相关考点：

- MMIO 把设备寄存器放进 physical address space, kernel 再通过 page table 建立可访问的 virtual mapping.
- DMA 让设备直接在设备和 memory buffer 之间传输数据，减少 CPU copy, 但要求 driver 明确 buffer lifetime.
- Interrupt handler 通常只做短路径工作，复杂处理交给后续上下文。

.. note::

   ARM / RISC-V 这类架构通常采用统一的物理地址空间：DRAM, 设备寄存器、interrupt controller 等都映射在
   physical address space 中，CPU 通过普通 load / store 访问设备寄存器，这就是 MMIO. x86 历史上同时
   保留了另一套独立 I/O port space, 需要用专门的 ``in`` / ``out`` 指令访问，这叫 PIO (Port-mapped I/O).
   最新 x86-64 处理器为了兼容性仍然保留 PIO 机制，操作系统和固件也还能访问传统端口设备；但现代 PCIe,
   NVMe, GPU, 网卡和大多数 SoC 外设主要都走 MMIO. 原因是 MMIO 更适合统一地址译码、page table 权限控制、
   虚拟化映射、PCIe BAR, 批量寄存器窗口和高性能 DMA 设备模型。简单说：PIO 还在，但主流新设备基本以
   MMIO 为中心。

Kernel 和 System Call
======================

Kernel 是硬件与 user program 之间的受信任层。用户程序不能直接修改 page table, 关闭中断、访问任意磁盘块，
这些操作必须通过 system call 进入 kernel.

.. csv-table:: Kernel Boundary
   :header: "主题", "机制", "核心考点"

   "Privilege", "CPU 区分 user mode / supervisor mode", "特权指令只能在 kernel 中执行"
   "System call", "用户态设置 syscall number 和参数后执行 trap instruction", "参数校验；返回值；错误码"
   "Trap frame", "保存用户态寄存器、PC, stack 等上下文", "kernel 返回用户态时恢复现场"
   "Interrupt", "外设或 timer 异步打断当前执行", "统一进入 trap handler; 可触发调度"
   "Exception", "page fault, 非法指令、除零等同步异常", "可恢复异常与致命异常要区分"

简化的 system call 路径：

.. code-block:: text

   user program
       |
       |  ecall / syscall
       v
   trap entry
       |
       |  save user registers into trapframe
       v
   syscall dispatcher
       |
       |  validate args, call kernel implementation
       v
   return to user
       |
       |  restore registers, switch privilege mode
       v
   user program continues

核心心智模型：

- User program 看到的是稳定 API.
- Kernel 看到的是不可信参数和硬件状态。
- System call 的边界处必须做权限检查、地址检查和资源生命周期管理。

Process
=======

Process 是 address space, 打开文件等 OS 资源的容器，thread 才是 CPU 调度的执行流。xv6 中每个 process
只有一个 thread, 因此 xv6 可以直接以 process 作为调度对象。

.. csv-table:: Process Core
   :header: "主题", "结构与实现", "核心考点"

   "进程状态", "unused, runnable, running, sleeping, zombie", "状态转换由 scheduler, sleep / wakeup, exit / wait 驱动"
   "Context switch", "保存当前 CPU registers, 恢复另一个执行流 registers", "现代 OS 切换 thread; xv6 切换 process 的 kernel thread / scheduler context"
   "fork", "复制当前进程的 address space 和资源引用", "父子进程返回值不同；可用 copy-on-write 优化"
   "exec", "用新程序镜像替换当前 address space", "PID 不变；打开文件通常保留"
   "exit / wait", "子进程退出后由父进程回收状态", "zombie 保存退出码，避免资源泄漏"
   "pipe", "kernel buffer + file descriptor", "单机进程间通信；读写阻塞语义"

典型 Unix process lifecycle:

.. code-block:: c

   int pid = fork();

   if (pid == 0) {
       // Child: replace current address space with a new program.
       char *argv[] = {"echo", "hello", 0};
       exec("echo", argv);
       exit(1); // exec returns only on failure.
   } else {
       // Parent: wait for child to become zombie, then reap it.
       wait(0);
   }

``fork`` 和 ``exec`` 分离是 Unix 的重要设计：

- ``fork`` 复制执行上下文，方便父进程在子进程中修改 file descriptor, 环境变量、工作目录。
- ``exec`` 加载新程序，复用同一个 PID 和已安排好的进程资源。
- Shell 的 pipeline, 重定向、后台任务都建立在这个组合之上。

Scheduling
==========

Scheduling Basics
-----------------

Scheduler 决定 runnable process 何时获得 CPU. 课程重点不是记住复杂策略，而是理解 preemption, context switch
和 sleep / wakeup 如何组合。

.. csv-table:: Scheduling
   :header: "主题", "机制", "核心考点"

   "Timer interrupt", "周期性打断 running process", "实现 preemption, 避免进程独占 CPU"
   "Round-robin", "轮流运行 runnable process", "简单公平；不考虑优先级和交互延迟"
   "Sleep", "进程等待某个 channel / condition", "睡眠时让出 CPU, 不忙等"
   "Wakeup", "事件发生后唤醒等待者", "避免 lost wakeup 是并发正确性的关键"
   "Context switch cost", "保存 / 恢复寄存器，可能影响 cache / TLB", "过度切换会降低吞吐"

.. note::

   以当前 Linux 主线实现来看，调度通常分成两步：先标记当前任务需要重新调度，再在安全点真正调用
   ``schedule()``.

   - Timer tick, wakeup 或跨 CPU 事件会让 scheduler 重新评估是否需要抢占；需要时设置
     ``TIF_NEED_RESCHED``, 部分配置还会使用 ``TIF_NEED_RESCHED_LAZY``.
   - Syscall 准备返回 user mode 时，``exit_to_user_mode_loop()`` 会检查这些 reschedule flag, 并在需要时调用
     ``schedule()``.
   - Interrupt 从 user mode 进入时，退出路径也走类似的 user-mode return 处理。
   - Interrupt 发生在 kernel mode 时，如果 preempt count 允许，IRQ exit 路径可通过 ``preempt_schedule_irq()``
     触发抢占。
   - 任务主动等待 I/O, 锁或条件时，会进入 sleep 并调用 ``schedule()`` 让出 CPU.

Linux Scheduling Trigger
------------------------

Linux 并没有一个常驻 kernel thread 负责轮询是否需要调度。Timer, wakeup 和跨 CPU 事件会在各自的当前
执行上下文中触发抢占判断；需要抢占时先设置 ``TIF_NEED_RESCHED``, 目标 CPU 之后在允许调度的安全点调用
``schedule()``.

Timer tick 发生在 timer interrupt context:

.. code-block:: text

   timer IRQ
       -> tick_sched_handle()
       -> update_process_times()
       -> sched_tick()
       -> scheduling class 的 task_tick()
       -> resched_curr()
       -> 设置 TIF_NEED_RESCHED

这里通常只标记需要调度，不直接在 hard IRQ 中切换任务。IRQ 退出时，如果允许抢占，可以通过
``preempt_schedule_irq()`` 进入 scheduler.

Wakeup 发生在执行唤醒操作的当前上下文：

.. code-block:: text

   device completion / lock release / condition satisfied
       -> wake_up()
       -> try_to_wake_up()
       -> ttwu_queue()
       -> wakeup_preempt()
       -> resched_curr()

调用者可能是 device ISR, softirq, 正在执行 syscall 的普通进程或 kernel thread, 并不固定属于某一种上下文。

如果被唤醒任务应在另一个 CPU 上运行，wakeup CPU 会向目标 CPU 发送 reschedule IPI
(Inter-Processor Interrupt, 核间中断):

在 Arm GIC 中，IPI 通常通过 SGI (Software Generated Interrupt, 软件生成中断) 实现。IPI 表示核间通信的
用途，SGI 是 GIC 提供的具体中断机制；GICv3 / GICv4 中可以通过 ``ICC_SGI1R_EL1`` 等寄存器向目标 CPU
发送 SGI.

.. code-block:: text

   CPU 0: resched_curr(CPU 1 runqueue)
       -> 设置 CPU 1 当前任务的 TIF_NEED_RESCHED
       -> smp_send_reschedule(CPU 1)

   CPU 1: reschedule IPI
       -> scheduler_ipi()
       -> IRQ exit 时进入 scheduler

Virtual Memory
==============

Virtual memory 给每个进程提供独立、连续、受保护的 address space. 真实 physical memory 由 kernel 和 MMU 管理。

.. csv-table:: Virtual Memory
   :header: "主题", "机制", "核心考点"

   "Address space", "text, data, heap, stack, guard page", "进程隔离；用户指针不能直接信任"
   "Page table", "virtual page -> physical page + permission bits", "PTE_V, PTE_R, PTE_W, PTE_X, PTE_U"
   "TLB", "地址翻译缓存", "切换 page table 或修改映射后需要考虑 flush"
   "Page fault", "访问未映射或权限不允许的页面", "可用于 lazy allocation, copy-on-write, demand paging"
   "Copy-on-write", "fork 时共享物理页并标记 read-only", "写入触发 page fault 后再复制"
   "mmap", "把 file 或 anonymous memory 映射进 address space", "统一文件 I/O 与内存访问"

地址翻译模型：

.. code-block:: text

   virtual address
       |
       |  split into VPN + offset
       v
   page table walk / TLB lookup
       |
       |  check valid bit and permission bits
       v
   physical page number + offset
       |
       v
   physical address

内存相关的常见 bug:

- Kernel 解引用 user pointer 前没有检查地址范围和权限。
- Page table 更新后忘记处理 TLB stale entry.
- ``fork`` 后父子共享资源的引用计数处理错误。
- Page fault handler 中持锁路径过长，导致死锁或调度问题。

Concurrency
===========

OS kernel 本身是高度并发程序：多个 CPU, interrupt handler, system call, background worker 都可能访问共享状态。

.. csv-table:: Concurrency
   :header: "主题", "机制", "核心考点"

   "Race condition", "多个执行流并发读写共享状态", "结果依赖 interleaving, 必须用同步约束"
   "Spinlock", "忙等直到获得锁", "适合短临界区；持锁时通常不能 sleep"
   "Sleeplock / mutex", "拿不到锁时 sleep", "适合长临界区或 I/O; 不能在 interrupt context 随意使用"
   "Semaphore", "带计数的同步原语；P/down 获取，V/up 释放", "既可做互斥，也可做资源计数和执行顺序约束"
   "Condition", "等待某个谓词为真", "检查条件和 sleep 必须原子化，避免 lost wakeup"
   "Deadlock", "循环等待资源", "固定锁顺序；避免持锁调用未知代码"
   "Reference count", "对象被共享时统计引用", "最后一个引用释放资源；increment / decrement 要同步"

Lock
----

常见锁类型：

- Spinlock (自旋锁): 拿不到锁时忙等，适合 kernel 短临界区，持锁期间通常不能 sleep.
- Mutex (互斥锁): 发生竞争时可以阻塞 / sleep, 适合允许睡眠的普通线程上下文；临界区仍应尽量短。
- Read-write lock (读写锁): 允许多个 reader 并发，writer 独占，适合读多写少场景。
- Semaphore (信号量): 带计数的同步机制，可用于互斥，也可表示多个可用资源。
- Seqlock (顺序锁): writer 之间必须串行执行并在更新前后改变序号，reader 无锁读取，发现序号变化就重试。
- RCU (Read-Copy-Update): reader 读取已发布的数据，writer 发布新状态，并在 grace period 后回收旧对象，
  适合高频读路径。
- Futex: Linux 用户态同步的基础机制，快路径在用户态，竞争时进入 kernel sleep / wakeup.

.. note::

   普通用户态业务代码很少直接使用纯自旋锁。原因是用户态线程可能被 OS 抢占：如果持锁线程被调度走，
   其他线程继续自旋只会白白消耗 CPU. 自旋锁更适合 kernel 中预计等待时间极短、且持锁路径不能 sleep 的
   临界区。现代用户态锁即使使用 spin, 也通常是 hybrid lock: 先短暂自旋几轮，拿不到再通过 futex 等机制
   进入 kernel sleep.

锁的基本原则：

- 先定义被保护的数据，再定义保护它的 lock.
- 临界区尽量短，但不能短到破坏 invariant.
- 不要持有 spinlock 做可能 sleep 的操作。
- 多把锁必须有稳定顺序，否则很容易 deadlock.

Atomic Operation
----------------

Lock 的底层依赖 CPU 提供的 atomic read-modify-write 能力，不同架构的表达方式不同：

- x86 / x86-64: 常见是带 ``LOCK`` prefix 的指令，例如 ``lock cmpxchg``, ``lock xadd``.
- ARM / RISC-V: 常见是 load-reserved / store-conditional, 例如 ARM ``LDXR`` / ``STXR``, RISC-V ``LR`` / ``SC``.
- C / C++ ``compare_exchange``, Linux ``cmpxchg`` 通常是上层封装，底层会映射到具体 CPU 的原子机制。
- 多核上还要考虑 memory ordering: CPU 和编译器可能重排普通 load / store, 锁的 acquire / release 需要提供 barrier 语义。

.. code-block:: text

   获取锁：
       原子地执行『如果 lock 为 0, 就把它改为 1』
       如果修改失败，说明锁已被占用，等待后重试

   临界区：
       访问由 lock 保护的共享状态

   释放锁：
       以 release ordering 把 lock 改回 0

核心点：

- 普通 ``load`` + ``store`` 不能实现锁，因为两个 CPU 可能同时看到 unlocked.
- Atomic operation 提供不可分割的 read-modify-write.
- Lock acquire / release 还要提供 memory barrier 语义，保证临界区内的读写不会越过锁边界。

.. note::

   锁最终依赖 CPU 提供的原子操作和 memory ordering 保证：一次 atomic read-modify-write 不会被其他 CPU
   对同一位置的冲突访问穿插。具体机制因架构和内存类型而异：x86 对普通 cacheable memory 通常利用
   cache coherence 完成 locked operation, 特殊情况可能使用 bus lock; RISC-V ``LR`` / ``SC`` 则通过
   reservation 判断期间是否发生冲突。软件里的 spinlock, mutex 都建立在这些硬件保证之上。

Semaphore
---------

Semaphore (信号量) 是一个带整数计数的同步原语。计数表示当前可用资源数，``P`` / ``down`` 表示申请资源，
``V`` / ``up`` 表示释放资源。P / V 名字来自荷兰语：

- ``P`` 是 proberen (try / test), 表示尝试获取资源；
- ``V`` 是 verhogen (increase), 表示增加计数、释放资源；

信号量通常是一种 sleep-based 同步机制：任务执行 ``P`` / ``down`` 时，如果有可用许可，就取走一个并继续；
否则进入 semaphore 的等待队列并睡眠。其他任务执行 ``V`` / ``up`` 时，会新增一个许可；如果已有任务等待，
实现可以把许可直接交给其中一个任务并将其唤醒。检查计数、修改计数和操作等待队列必须由实现原子地完成。
需要注意的是，semaphore 不完全等同于 mutex; binary semaphore 可以用于互斥，但 semaphore 更一般，它还可以
表达多个同类资源的数量，并且通常不强调 owner, 释放者不一定是获取者。

.. code-block:: text

   P / down: 申请一个许可
       有许可：取走一个许可，继续执行
       无许可：进入等待队列并睡眠

   V / up: 释放一个许可
       有任务正在等待：把许可交给其中一个任务，并将其唤醒
       没有任务等待：可用许可数加 1

   上述判断、计数变化和等待队列操作是一个不可分割的同步过程。

信号量和 mutex / condition variable 的区别：

- Mutex 保护临界区，强调『谁进入共享数据』。
- Condition variable 等待某个条件，必须和 mutex 配合使用，强调『条件何时成立』。
- Semaphore 自带计数，强调『还有多少资源可用』。

.. note::

   线程池就用到了 Semaphore 的思想：空闲 worker 数、任务队列容量、最多并发任务数，本质上都是可消费的
   计数资源。实际项目里不一定直接调用 ``sem_wait`` / ``sem_post``, 因为 thread pool, connection pool,
   blocking queue, rate limiter 往往已经把这种计数和等待逻辑封装好了；业务代码看起来主要是在用 lock.

   一般说，拿到信号量就是拿到了一个资源许可，可以继续执行。计数上限为 1 的 binary semaphore 也能限制
   同一时刻只有一个任务进入临界区，但它不等同于 mutex: mutex 有 owner, 通常必须由持锁任务解锁；semaphore
   通常没有 owner, 释放许可的任务可以不是申请许可的任务。

File System
===========

File system 把 block device 组织成 file / directory, 并提供 crash 后仍可恢复的一致性语义。

.. csv-table:: File System
   :header: "主题", "结构与实现", "核心考点"

   "Block device", "固定大小 block 的读写接口", "磁盘只认识 block, 不认识文件"
   "Buffer cache", "缓存最近使用的 disk block", "减少 I/O; 也提供 block 级同步点"
   "Inode", "文件类型、大小、link count, data block 指针", "文件名不在 inode 里，目录项才保存 name -> inode"
   "Directory", "特殊文件，内容是 name 到 inode number 的映射", "路径解析逐级查目录"
   "File descriptor", "进程级整数句柄，指向 kernel open file object", "dup, fork, pipe 都依赖引用关系"
   "Logging", "先写 journal, 再提交真实位置", "保证 crash consistency"

路径查找模型：

.. code-block:: text

   /usr/bin/sh
      |
      v
   root inode
      |
      |  lookup "usr" in root directory
      v
   usr inode
      |
      |  lookup "bin"
      v
   bin inode
      |
      |  lookup "sh"
      v
   file inode

File descriptor 不是文件本身：

.. code-block:: text

   process fd table
       fd 0 ----\
       fd 1 -----+--> open file object --> inode --> disk blocks
       fd 2 ----/

   # dup() 让多个 fd 指向同一个 open file object, 因此共享 file offset.
   # fork() 后父子进程的 fd table entry 也会引用同一个 open file object.

Crash consistency 的基本思路：

- Metadata update 通常涉及多个 block, 例如 inode, bitmap, directory entry.
- Crash 可能发生在任意两个写之间，造成 leak, dangling pointer 或目录不一致。
- Journal / log 把一组更新变成 crash-atomic transaction: 恢复时忽略未提交事务，重放已经提交但尚未完整写入
  最终位置的事务，因此恢复后要么不体现该事务，要么体现它的全部更新。

I/O and Device
==============

Device driver 是 kernel 中理解具体硬件协议的部分。OS 通过 driver 把复杂设备包装成统一抽象。

.. csv-table:: Device I/O
   :header: "主题", "机制", "核心考点"

   "MMIO", "把设备寄存器映射到内存地址", "读写特殊地址就是读写设备寄存器"
   "Interrupt", "设备完成工作后通知 CPU", "避免 CPU 一直 polling"
   "DMA", "设备直接读写内存 buffer", "减少 CPU 拷贝；需要处理 cache 和权限"
   "Driver", "初始化设备、提交请求、处理中断", "上层抽象与硬件细节的边界"
   "Polling", "CPU 循环检查设备状态", "简单但浪费 CPU, 适合早期启动或短等待"

典型 I/O 路径：

.. code-block:: text

   user read()
       |
       v
   file system / pipe / socket layer
       |
       v
   driver submits request to device
       |
       v
   process sleeps
       |
       v
   device interrupt
       |
       v
   driver wakes process

Network
=======

Network stack 把网卡收发的 packet 组织成 socket API. 课程中重点是分层、buffer ownership 和并发边界。

.. csv-table:: Network Stack
   :header: "层次", "抽象", "核心考点"

   "Ethernet / NIC", "frame 收发", "MAC address; driver ring buffer; interrupt / polling"
   "IP", "跨网络转发 packet", "best-effort; fragmentation; routing"
   "UDP", "datagram", "无连接；不保证可靠和顺序；应用自己处理丢包"
   "TCP", "reliable byte stream", "sequence number, ACK, retransmit, flow control, congestion control"
   "Socket", "file descriptor 风格的网络端点", "read / write / close 与协议状态机绑定"

Security and Isolation
======================

OS 的安全基础是 isolation: 让一个用户程序无法破坏 kernel 或其他进程。

.. csv-table:: Isolation
   :header: "主题", "机制", "核心考点"

   "User / kernel split", "CPU privilege mode + page table permission", "用户态不能执行特权指令或访问 kernel memory"
   "Process isolation", "独立 address space", "一个进程崩溃不应破坏另一个进程"
   "File permission", "uid, gid, mode bit", "资源访问必须通过权限检查"
   "Capability", "持有句柄才可访问对象", "file descriptor 是一种 capability 风格接口"
   "Input validation", "检查 user pointer, 长度、整数溢出", "syscall 边界默认不信任调用者"

一个实用判断：

- 如果数据来自 user space, disk, network, 都应视为不可信。
- 如果对象能被多个进程或 CPU 共享，就必须明确 lifetime 和 permission.
- 如果 kernel panic 可以由普通用户触发，通常就是 isolation bug.

xv6 OS demo
===========

xv6 的价值在于小：它不是生产 OS, 但把核心路径压缩到可以读完的规模。

.. code-block:: text

   xv6-riscv/
   |-- user/
   |   |-- sh.c              # shell: fork / exec / wait / pipe / redirection 的入口样例
   |   |-- init.c            # 第一个用户进程，启动 shell
   |   `-- *.c               # user commands, 最终通过 system call 使用 kernel
   |
   |-- kernel/
   |   |-- entry.S           # CPU 进入 kernel 后的早期启动代码
   |   |-- start.c           # machine mode 初始化，切到 supervisor mode
   |   |-- main.c            # kernel 初始化主线
   |   |
   |   |-- trap.c            # syscall / interrupt / exception 的 C 层处理逻辑
   |   |-- trampoline.S      # user trap entry / return, 保存和恢复用户寄存器
   |   |-- kernelvec.S       # kernel trap entry / return, 保存和恢复内核寄存器
   |   |-- syscall.c         # syscall table 和 dispatcher
   |   |-- sysproc.c         # process 相关 syscall 实现
   |   |-- sysfile.c         # file 相关 syscall 实现
   |   |
   |   |-- proc.c            # process lifecycle, scheduler, sleep / wakeup
   |   |-- swtch.S           # context switch 的 register 保存 / 恢复
   |   |-- vm.c              # page table, address space, copyin / copyout
   |   |-- kalloc.c          # physical page allocator
   |   |
   |   |-- file.c            # open file object 和 file descriptor 层
   |   |-- fs.c              # inode, directory, block mapping
   |   |-- bio.c             # buffer cache
   |   |-- log.c             # file system transaction / crash consistency
   |   |-- pipe.c            # pipe buffer, sleep / wakeup 的经典例子
   |   |
   |   |-- virtio_disk.c     # disk driver, descriptor, DMA, interrupt
   |   |-- uart.c            # console device driver
   |   |-- plic.c            # interrupt controller
   |   `-- spinlock.c        # spinlock 和 memory ordering
   |
   `-- mkfs/                 # 构造 xv6 file system image

源码:

.. code-block:: text

   user/sh.c
       |
       |  fork, exec, wait, pipe, read, write
       v
   syscall layer
       |
       +--> proc.c       # process lifecycle / scheduler
       +--> vm.c         # address space / copyin / copyout
       +--> fs.c         # inode / path / file data
       +--> pipe.c       # IPC buffer and sleep / wakeup
       +--> trap.c       # syscall, interrupt, exception

References
==========

- `MIT 6.1810: Operating System Engineering <https://pdos.csail.mit.edu/6.1810/2025/>`_
- `MIT 6.1810 Fall 2025 overview <https://pdos.csail.mit.edu/6.1810/2025/overview.html>`_
- `MIT OpenCourseWare: 6.1810 Operating System Engineering, Fall 2023 <https://ocw.mit.edu/courses/6-1810-operating-system-engineering-fall-2023/>`_
- `xv6, a simple Unix-like teaching operating system <https://pdos.csail.mit.edu/6.828/xv6>`_
- `xv6 RISC-V source <https://github.com/mit-pdos/xv6-riscv>`_
- `xv6 book source <https://github.com/mit-pdos/xv6-riscv-book>`_

Summary
=======

操作系统的核心不是某个单点机制，而是一组抽象边界：

- ``process`` 抽象资源容器，``thread`` 抽象 CPU 执行流。
- ``virtual memory`` 抽象内存并提供隔离。
- ``file descriptor`` 抽象文件、pipe, device, socket.
- ``system call`` 是 user program 主动请求 kernel 服务的受控入口；exception 也会被动地使执行流进入 kernel.
- ``lock`` 和 ``sleep / wakeup`` 让 kernel 在并发下保持状态一致性。

OS 一直在做三件事：把硬件能力封装成稳定接口，在多个用户和程序之间安全复用资源，
并在并发和失败场景下维持这些接口的语义。
