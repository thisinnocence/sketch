.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 0.2

Rust 工程实践
*************

这篇文章面向有深厚 C/C++ 背景、但希望用工程视角理解 Rust 的读者。行文顺序不是从 ``cargo`` 开始，而是从最底层的
``rustc`` 和编译单元开始，一层层把抽象往上叠：

- 先理解 ``rustc`` 到底在编译什么；
- 再理解小型 Rust 工程为什么应该先从单 crate 开始；
- 然后再引入 ``cargo`` 和 ``package`` 这一层；
- 接着进入 ``workspace`` 管理多 package；
- 最后再讨论 C/Rust 混合工程与大型工程的组织方法。

如果用一句话概括全文主线，就是：

.. code-block:: text

    rustc -> crate -> 单 crate 小工程 -> cargo/package -> workspace -> 混合工程 -> 大型工程

.. _rust-engineering-compile:

Rustc 与 Crate
==============

对于 C/C++ 程序，最熟悉的模型是：

- 每个 ``.c/.cc`` 基本可以看作一个编译单元；
- 编译器先把每个编译单元编成 ``.o`` ；
- 链接器再把多个 ``.o`` 和库拼成最终产物。

Rust 最需要先纠正的地方是：它的基础编译单元不是单个 ``.rs`` 文件，而是 ``crate`` 。

编译单元
--------

Rust 没有 C/C++ 那种头文件模型。它不是靠 ``.h`` 提前暴露声明，再让另一个源文件独立编译；它要求编译器在编译一个
crate 时，已经看见这个 crate 的模块树、类型定义、trait、泛型约束和依赖元数据。

所以 Rust 的基本编译边界是：

- 一个 crate 对应一次 ``rustc`` 的主要编译输入；
- crate 内可以有很多 ``.rs`` 文件；
- crate root 通过 ``mod`` 声明把这些文件纳入当前 crate 的模块树；
- crate 之间不是靠头文件互相可见，而是靠编译后产生的 metadata 和符号。

对 C/C++ 工程师来说，最接近的理解可以是：

- C/C++ 的一个 translation unit 更像“预处理展开后的单个源文件”；
- Rust 的一个 crate 更像“一个已经把内部源码组织完整收口好的编译目标”。

Crate Root
----------

每个 crate 都有且仅有一个 crate root，也就是这个 crate 的入口源文件。常见情况是：

- 二进制 crate 的默认 root 是 ``src/main.rs`` ；
- 库 crate 的默认 root 是 ``src/lib.rs`` ；
- 额外二进制 crate 常见是 ``src/bin/*.rs`` ；
- integration test crate 常见是 ``tests/*.rs`` 。

crate root 负责继续声明模块树，比如：

.. code-block:: rust

    mod config;
    mod parser;

这表示当前 crate 还包含 ``config.rs`` 和 ``parser.rs`` 这两个模块文件，或者对应目录形式。

这里最重要的结论是：

- ``.rs`` 文件不等于 crate；
- crate 由 crate root 和模块树共同构成；
- 目录只是文件容器，不是编译边界本身。

四层抽象
--------

Rust 工程里最容易混淆的四个概念其实正好对应四个层级：

.. code-block:: text

    workspace
    └── package
        └── crate
            └── module

- ``module``: crate 内部怎么拆源码；
- ``crate``: ``rustc`` 到底在编译哪个单元；
- ``package``: Cargo 怎样描述、依赖、发布这一组目标；
- ``workspace``: Cargo 引入的多 package 统一编排层。

本文后面会按这个顺序依次详细说明。

仅用 Rustc
==========

如果你有 C/C++ 背景，可以先手工跑几次 ``rustc`` ，进行对比理解。

最小示例
--------

目录：

.. code-block:: text

    hello/
    `- main.rs

代码：

.. code-block:: rust

    fn main() {
        println!("hello");
    }

直接编译：

.. code-block:: bash

    rustc main.rs

这一步里， ``main.rs`` 本身就是 crate root，编译结果是一个 binary crate。

.. note::

    关于这里为什么可以直接使用 ``println!`` ，以及 ``std`` / prelude / 宏默认可见性的区别，
    可参见 :ref:`rust-std-prelude` 。

单 Crate 多文件
---------------

目录：

.. code-block:: text

    hello/
    |- main.rs
    |- config.rs
    `- parser.rs

``main.rs``:

.. code-block:: rust

    mod config;
    mod parser;

    fn main() {
        println!("{}", parser::parse(config::load()));
    }

这里虽然有三个 ``.rs`` 文件，但仍然只有一个 crate，因为只有一个 crate root: ``main.rs`` 。

这和 C/C++ 的差异非常大：

- 在 C/C++ 里， ``config.cc`` 和 ``parser.cc`` 往往各自编译成独立 ``.o`` ；
- 在 Rust 里， ``config.rs`` 和 ``parser.rs`` 只是当前 crate 的模块文件，不是独立编译目标。

所以 Rust 工程里“先按模块拆代码”比“先按编译单元拆代码”更自然。

手工编译库 Crate
-----------------

如果你想手工理解 crate 之间如何依赖，可以先做一个库：

目录：

.. code-block:: text

    math/
    `- lib.rs

``lib.rs``:

.. code-block:: rust

    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

编译成 Rust 库：

.. code-block:: bash

    rustc --crate-type=rlib lib.rs

这里产物通常是 ``libmath.rlib`` 一类文件。它不只是静态代码块，里面还带着给 Rust 编译器使用的 metadata。

再做一个依赖这个库的二进制：

目录：

.. code-block:: text

    app/
    `- main.rs

``main.rs``:

.. code-block:: rust

    use math::add;

    fn main() {
        println!("{}", add(1, 2));
    }

手工链接时，核心参数是：

.. code-block:: bash

    rustc main.rs --extern math=./libmath.rlib

这一步非常值得亲手做一次，因为它会直接揭示 Cargo 的本质职责之一：

- Cargo 不是魔法；
- 它本质上是在帮你准备依赖图；
- 然后给每个 ``rustc`` 调用生成正确的 ``--extern`` 、 ``-L`` 、 ``--cfg`` 、 ``--crate-type`` 等参数。

Crate Graph
-----------

站在 ``rustc`` 视角，一个 Rust 工程首先不是“目录树”，而是“crate graph”：

- 每个节点是一个 crate；
- 节点内部是自己的模块树；
- 节点之间通过依赖关系连接；
- Cargo 或其他上层工具负责把这个图编排出来。

因此对 C/C++ 工程师来说，理解 Rust 工程最稳的第一性原理是：

- 先别从目录看；
- 先问“当前到底有几个 crate”；
- 再问“每个 crate 的 root 是谁”；
- 最后才问“这些 crate 是靠什么工具编排出来的”。

单 Crate 起步
=============

把 ``rustc`` 模型理解以后，就可以进入第一个工程化结论：

.. note::

    对绝大多数小型 Rust 工程，推荐起点不是 workspace，也不是很多 crate，而是单 package、单核心 crate，
    用模块边界先把代码组织起来。

拆分时机
--------

很多 C/C++ 工程师刚接触 Rust 时，容易把“工程化”理解成“尽早拆多个库”。但在 Rust 里，过早拆 crate 往往会过早冻结边界。

小工程早期更常见的状态是：

- 需求和边界还在快速变；
- 模块之间类型会频繁移动；
- 错误类型、配置对象、trait 边界还不稳定；
- 复用关系还只是“可能”，不是“已经稳定存在”。

这时如果一开始就拆成很多 crate，常见副作用是：

- 到处需要 ``pub`` 和 re-export；
- 本来只是内部重构，变成跨 crate API 调整；
- feature、依赖、可见性边界都被迫提前设计；
- 心智成本迅速上升。

更实用的策略是：

1. 先把工程当成一个单 crate 系统；
2. 用模块边界而不是 crate 边界管理复杂度；
3. 等职责边界稳定后，再考虑拆 crate 或上 workspace。

小型骨架
--------

如果是一个命令行工具或服务型程序，比较稳妥的起点通常是：

.. code-block:: text

    my-app/
    |- Cargo.toml
    `- src/
       |- main.rs
       |- lib.rs
       |- config.rs
       |- error.rs
       |- app.rs
       `- storage/
          `- mod.rs

这里虽然还没展开讲 Cargo，但先看结构也没问题。这个骨架的关键点不是“文件多”，而是职责分工清晰：

- ``main.rs``: 进程入口；
- ``lib.rs``: 程序能力入口；
- ``config.rs``: 配置；
- ``error.rs``: 错误类型；
- ``app.rs``: 业务主流程；
- ``storage/``: 某个子系统。

入口与能力
----------

工程实践里一个很有价值的习惯是：

- ``main.rs`` 只负责启动；
- 真正逻辑尽量进 ``lib.rs`` 和其子模块。

例如：

.. code-block:: rust

    // main.rs
    fn main() -> anyhow::Result<()> {
        my_app::run()
    }

.. code-block:: rust

    // lib.rs
    mod app;
    mod config;
    mod error;

    pub fn run() -> anyhow::Result<()> {
        app::run()
    }

这样做的好处很现实：

- 更容易写测试；
- 更容易加第二个 bin；
- 更容易把能力给别的 crate 复用；
- 以后要拆 crate 时迁移成本更低。

模块拆分
--------

Rust 小工程里最推荐的拆法是按职责切模块，比如：

- ``config`` ;
- ``http`` ;
- ``storage`` ;
- ``domain`` ;
- ``cli`` 。

不太推荐一上来就出现下面这种目录：

- ``types.rs`` ;
- ``traits.rs`` ;
- ``utils.rs`` ;
- ``common.rs`` 。

原因很简单：这种拆法往往不是业务边界，而只是“语言元素收纳盒”。一旦工程变大，边界很快会模糊。

一个实用判断标准是：

- 如果某个模块名字能直接回答“它负责什么”，通常是好模块；
- 如果某个模块名字只是在回答“里面装了什么语法成分”，通常边界不够好。

Cargo 与 Package
================

理解了 ``rustc`` 和单 crate 小工程以后，再看 Cargo 就会很自然。

Cargo 职责
----------

Cargo 当然负责依赖下载，但它更重要的职责其实是“Rust 工程编排器”。它主要做几件事：

- 读取 ``Cargo.toml`` 清单；
- 解析 package 和依赖图；
- 下载或定位依赖；
- 生成对每个 crate 的 ``rustc`` 调用参数；
- 调度构建、测试、文档、示例和 benchmark；
- 管理 ``target/`` 缓存与增量构建。

所以从工程视角看，Cargo 更像：

- C/C++ 世界里“包管理 + 构建系统 + 测试入口 + 文档入口”的组合；
- 只是它和 Rust 编译模型是天然耦合的，因此比 CMake + Conan 这一类组合更统一。

Package 的作用
--------------

很多人第一次学 Rust，会觉得已经有 crate 了，为什么还要 package。

原因是：

- ``crate`` 回答的是“编译单元是什么”；
- ``package`` 回答的是“这个项目如何声明、依赖、发布和组织若干目标”。

比如同一个项目里可以同时有：

- 一个 ``lib.rs`` 对应的 library crate；
- 一个 ``main.rs`` 对应的 binary crate；
- 若干 ``src/bin/*.rs`` 对应的额外 binary crate。

它们可能共享：

- 同一份名字、版本、license；
- 同一组依赖；
- 同一份 feature 定义；
- 同一个发布边界。

这时 ``package`` 就很必要，因为“多个 crate 共享一份清单”本来就是工程常态。

一个 Package 多个 Crate
-----------------------

例如：

.. code-block:: text

    my-tool/
    |- Cargo.toml
    `- src/
       |- lib.rs
       |- main.rs
       `- bin/
          `- admin.rs

这里的关系是：

- ``my-tool`` 是一个 package；
- ``lib.rs`` 是一个 library crate；
- ``main.rs`` 是一个 binary crate；
- ``bin/admin.rs`` 是另一个 binary crate。

也就是说，package 不是 crate，crate 也不是模块。工程上最好把这三层彻底分开看。

默认布局
--------

Cargo 值得信任的一点是，它对目录布局有很成熟的默认约定。最常见的是：

.. code-block:: text

    my-crate/
    |- Cargo.toml
    |- Cargo.lock
    |- src/
    |  |- lib.rs
    |  |- main.rs
    |  `- bin/
    |- tests/
    |- examples/
    |- benches/
    |- build.rs
    `- .cargo/
       `- config.toml

这些位置不是“行业装饰品”，而是直接会被工具链理解：

- ``tests/`` 下每个顶层文件通常会被当成一个 integration test crate；
- ``examples/`` 下每个示例都是一个可编译目标；
- ``benches/`` 下是基准目标；
- ``build.rs`` 是构建脚本；
- ``.cargo/config.toml`` 放 target、linker、runner 等 Cargo 级配置。

构建流程
--------

可以把 Cargo 的主要构建流程理解为：

1. 解析 ``Cargo.toml`` ；
2. 构建完整依赖图；
3. 获取 registry/git/path 依赖；
4. 判断哪些 crate 需要重编；
5. 为每个 crate 生成对应 ``rustc`` 参数；
6. 按依赖顺序并行调度编译；
7. 把产物和缓存写入 ``target/`` 。

其中最关键的一层仍然没有变：

.. note::

    Cargo 不是替代 ``rustc`` 的另一个编译器；Cargo 是上层编排器，真正做 Rust 编译工作的仍然是 ``rustc`` 。

测试与文档
----------

Rust 工具链的一个优势是：测试、示例、文档这些目标和 crate/package 模型天然对齐。

例如：

- ``#[cfg(test)]`` 单元测试会编进当前 crate；
- ``tests/*.rs`` 会被当成额外的测试 crate；
- ``cargo doc`` 围绕库 API 生成文档；
- ``examples/*.rs`` 和普通目标一样可以构建运行。

这也是为什么 Rust 工程在“测试工程化”上往往比传统 C/C++ 轻很多。不是因为测试不复杂，而是因为工具链先把基本台子搭好了。

Workspace
=========

当单 package 逐渐撑不住时，才轮到 workspace 出场。

引入时机
--------

下面这些信号通常说明工程已经跨过“单 package 最舒服”的阶段：

- 已经存在多个职责明确、边界稳定的 crate；
- 某些能力需要独立复用或独立发布；
- 同一个仓库里有应用、库、代码生成工具、测试支撑模块；
- 你开始需要统一依赖版本、统一构建输出和统一 CI 入口。

如果这些问题还没出现，就不要为了“看起来正规”过早上 workspace。

核心作用
--------

workspace 本质上不是新的编译单元，而是多 package 的统一编排层。它主要提供：

- 多个 member package 的统一入口；
- 共享一份依赖解析结果；
- 通常共享一个 ``Cargo.lock`` ；
- 通常共享一个 ``target/`` ；
- 支持集中声明部分公共配置与依赖版本。

典型结构如下：

.. code-block:: text

    hello-workspace/
    |- Cargo.toml
    |- Cargo.lock
    |- app/
    |  |- Cargo.toml
    |  `- src/main.rs
    |- core/
    |  |- Cargo.toml
    |  `- src/lib.rs
    `- tools/
       `- codegen/
          |- Cargo.toml
          `- src/main.rs

根 ``Cargo.toml`` 可以只是：

.. code-block:: toml

    [workspace]
    members = ["app", "core", "tools/codegen"]
    resolver = "3"

这种只有 ``[workspace]`` 的根清单通常叫 virtual manifest。它自己不是 package，只是工程总入口。

Crate 拆分
----------

这是 Rust 工程实践里最核心的判断题之一。比较稳妥的拆分条件通常是：

- 有明确且稳定的 API 边界；
- 某部分逻辑天然应被多个上层目标复用；
- 该部分有独立测试、发布、演进节奏；
- 把它放在独立 crate 后，复杂度净减少而不是净增加。

如果只是因为目录大、文件多，还不够成为拆 crate 的理由。很多问题在模块层就能解决。

演化路径
--------

很实用的演化顺序通常是：

1. 单 package，主要靠模块拆分；
2. 同一个 package 内形成 ``lib.rs`` + ``main.rs`` 的结构；
3. 某些能力边界稳定后，先拆成同仓库 path dependency；
4. 当 crate 数量明显增加，再把这些 package 收编进 workspace；
5. 最后再考虑公共依赖继承、统一 profile、统一工具链配置。

这个顺序的核心思想是：先让边界自然长出来，再用上层工具承认这个边界，而不是反过来。

常用配置
--------

现代工程里，workspace 常见会集中管理一部分配置：

.. code-block:: toml

    [workspace]
    members = ["app", "core", "ffi"]
    resolver = "3"

    [workspace.package]
    version = "0.1.0"
    edition = "2024"
    license = "MIT"

    [workspace.dependencies]
    anyhow = "1"
    serde = { version = "1", features = ["derive"] }

对应 member package 可以写：

.. code-block:: toml

    [package]
    name = "app"
    version.workspace = true
    edition.workspace = true
    license.workspace = true

    [dependencies]
    anyhow.workspace = true
    serde.workspace = true

这样做的价值不是“语法好看”，而是减少版本漂移和配置分叉。

这里的 ``resolver`` 不是随便的数字，而是 Cargo 的依赖解析/feature 解析策略版本。
其中 ``"2"`` 主要表示“新的 feature resolver”：

- 不再把未参与当前目标构建的平台依赖 feature 无脑合并进来；
- build-dependencies 和 proc-macro 的 feature，不再和 normal dependency 强行共用；
- dev-dependencies 的 feature，只有在真的构建测试或示例时才参与。

这样做的核心目的是避免 feature 误合并，减少“测试或构建脚本里开了某个 feature，
结果把正式产物也污染了”这类问题。

不过按当前 Cargo 官方文档， ``edition = "2021"`` 默认对应 ``resolver = "2"`` ，
而 ``edition = "2024"`` 默认对应 ``resolver = "3"`` 。 ``"3"`` 在 ``"2"`` 的基础上，
进一步把 Rust 版本兼容性纳入依赖解析默认行为。所以如果示例里已经写 ``edition = "2024"`` ，
那更自然的写法就是 ``resolver = "3"`` 。

混合工程
========

对有 C/C++ 背景的团队来说，Rust 很少是平地起一个纯 Rust 世界。更真实的情况往往是混合工程：

- Rust 调已有 C/C++ 库；
- C/C++ 调 Rust 写的新模块；
- 现有构建系统里逐步引入 Rust；
- 一部分模块继续保留在 C/C++ ，另一部分迁到 Rust。

这时要先判断 Rust 在混合系统中的角色。

Rust 调 C/C++
-------------

这种情况常见于：

- 复用现有成熟 C/C++ 库；
- 依赖平台 SDK；
- 接第三方系统库。

Rust 侧通常会涉及：

- ``unsafe extern "C"`` 声明；
- ``bindgen`` 生成绑定；
- 在 ``build.rs`` 里探测库路径、头文件、链接参数；
- 必要时配合 ``pkg-config`` 或 ``cmake`` crate。

工程上最关键的原则不是“绑定工具怎么用”，而是：

- FFI 边界必须薄；
- 所有 ``unsafe`` 尽量收口在少数模块里；
- 边界两侧的数据所有权、生命周期、错误约定必须写清楚。

C/C++ 调 Rust
-------------

如果是把 Rust 作为一个可被旧系统调用的新模块，常见产物类型是：

- ``staticlib``: 供 C/C++ 静态链接；
- ``cdylib``: 供 C/C++ 动态加载。

此时 Rust crate 更像“给 C ABI 暴露接口的库”，关键点通常是：

- 公开接口必须用 ``extern "C"`` ；
- 数据布局需要 ``#[repr(C)]`` ；
- panic 不能跨 FFI 边界传播；
- 所有权转移、内存分配和释放责任必须成对设计。

对 C/C++ 背景读者来说，这里要特别牢记：

.. note::

    Rust 在内部可以非常高层，但一旦跨到 C ABI 边界，工程纪律要回到非常朴素、非常显式的层次。

推荐目录
--------

如果仓库已经比较大，混合工程更适合直接按 workspace 组织，例如：

.. code-block:: text

    hybrid-system/
    |- Cargo.toml
    |- rust/
    |  |- core/
    |  |- ffi/
    |  `- tools/
    |- cpp/
    |  |- include/
    |  |- src/
    |  `- CMakeLists.txt
    `- scripts/

其中一个很稳妥的思路是：

- ``rust/core`` 放纯 Rust 逻辑，不直接碰 ABI；
- ``rust/ffi`` 只负责 FFI 边界适配；
- C/C++ 侧只和 ``ffi`` 层对接，不直接耦合 Rust 内部实现。

这样一来，即使 Rust 内部类型系统和模块结构不断演进，ABI 边界仍然可以尽量稳定。

Build.rs
--------

混合工程里 ``build.rs`` 很常见，但也最容易被滥用。它适合做的是：

- 编译少量配套 C 文件；
- 生成绑定代码；
- 探测链接参数和系统库；
- 传递必要的 ``cargo:rustc-link-lib`` / ``cargo:rustc-link-search`` 。

不适合做的是：

- 塞入一大堆不可追踪的构建逻辑；
- 把工程主构建系统偷偷复制一份进去；
- 让不同平台行为变得不可预测。

经验上， ``build.rs`` 应该尽量只承担“桥接”职责，而不是变成第二套构建系统。

大型工程
========

当工程继续扩大以后，真正重要的已经不是“目录怎么摆最好看”，而是边界怎么治理。

边界治理
--------

1. 先稳住层级关系。

典型地可以把 crate 分成几层：

- 基础设施层：日志、配置、错误、通用 runtime 适配；
- 领域能力层：业务核心逻辑；
- 接口适配层：HTTP、CLI、gRPC、FFI；
- 应用装配层：最终可执行程序。

最忌讳的是底层 crate 反向依赖上层接口层。

2. 让 crate 边界对应稳定职责，而不是对应组织架构或短期目录习惯。

好的 crate 边界通常代表：

- 一块清晰能力；
- 一组稳定语义；
- 明确的拥有者；
- 可独立验证的行为。

3. 把共享代码和“顺手复用代码”区分开。

很多大型工程膨胀的起点都是一个无边界的 ``common`` 或 ``utils`` crate。工程上更好的策略是：

- 只有真的被多方稳定依赖的能力才抽共享 crate；
- 临时复用优先复制或局部重构，不要急着抽公共库；
- 公共 crate 一旦出现，必须控制 API 面。

4. 把 FFI、proc-macro、codegen 这类特殊 crate 单独隔离。

这些 crate 的构建行为、调试方式、错误模式都和普通业务 crate 不一样。隔离以后，整个工作区更容易维护。

5. 把编译时间和依赖膨胀当成一等工程问题。

Rust 在大型工程里很容易出现：

- 依赖树过深；
- feature 组合复杂；
- 宏和泛型导致编译成本升高；
- 一点点改动触发大量重编。

因此大型工程里要经常问：

- 这个 crate 真的需要公开这么多泛型吗；
- 这个依赖是不是可以落到边缘层；
- 这个公共 crate 会不会把整个工作区都拖慢。

组织形态
--------

一个比较健康的 workspace 往往更接近下面这种样子：

.. code-block:: text

    product/
    |- Cargo.toml
    |- crates/
    |  |- foundation/
    |  |  |- config/
    |  |  |- error/
    |  |  `- runtime/
    |  |- domain/
    |  |  |- account/
    |  |  `- billing/
    |  |- adapters/
    |  |  |- http-api/
    |  |  |- cli/
    |  |  `- ffi/
    |  `- tools/
    |     |- codegen/
    |     `- xtask/
    `- apps/
       |- server/
       `- admin-cli/

这个结构的重点不是目录名字，而是下面几件事：

- 核心能力在中间层，不直接依赖最外层接口；
- 最终应用只做装配，不承载复杂业务；
- 工具型 crate 单独放，不污染核心依赖图；
- 边界按职责划分，而不是按语言特性切碎。

常见误区
--------

workspace 只是组织工具，不会自动带来好架构。常见误区包括：

- 一个业务对象拆成一堆极细的 crate；
- 到处互相 path dependency；
- 用 crate 边界代替模块设计；
- 为了“可复用”过早抽象，最后反而所有 crate 都强耦合。

如果出现这些症状，问题不在 Cargo，而在边界设计。

学习路径
========

对有 C/C++ 背景的人，比较稳妥的 Rust 工程学习顺序应该是：

1. 先用 ``rustc`` 理解 crate、crate root、模块树、``--extern`` 这些最低层概念；
2. 再做单 crate 小工程，学会用模块控制复杂度；
3. 然后再引入 Cargo，理解 package、默认目录、测试和构建编排；
4. 当多 package 需求真实出现时，再引入 workspace；
5. 如果进入存量系统，再学习 FFI 和混合工程边界；
6. 最后才讨论大型工程里的 crate 分层、依赖治理和编译成本控制。

这个顺序的价值在于：

- 每一层抽象都建立在前一层之上；
- 你不会把 Cargo 当成黑盒；
- 你会知道什么时候该升一层抽象，什么时候不该。

总结
====

Rust 工程实践里，最容易犯的错误不是语法不会，而是抽象上得太快。对 C/C++ 背景读者，最稳的方式永远是先从最低层建模：

- 先认清 ``rustc`` 编译的是 crate，不是单文件；
- 先把小工程压在单 crate 或单 package 范围内；
- 再用 Cargo 把构建、依赖、测试和发布组织起来；
- 再在边界稳定后引入 workspace；
- 最后进入混合工程和大型工程治理。
