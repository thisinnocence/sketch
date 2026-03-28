.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 0.1

RUST笔记
***********

安全理念
=========

Rust 的安全特性来自下面的设计哲学：

内存和生命周期安全：

- Ownership: 每个值在任意时刻只有一个 owner，owner 负责其生命周期管理，当 owner 离开作用域时自动 drop 掉；
- Move semantics: 默认是 move 语义而非 copy，值被 move 后原变量立即失效，只有实现 Copy 的类型才会发生隐式复制；
- Borrowing: 同一数据在同一时刻只能多 ``&T`` 或者单 ``&mut T``, 满足Aliasing XOR Mutability, 要么共享只读，要么独占可变;
- Lifetimes: 所有引用都带有生命周期约束，编译器编译阶段会借此来保证 lifetime(ref) ≤ lifetime(data)；
- Unsafe boundary: 编译器无法证明安全的操作(如裸指针、FFI、手动内存)必须放入 unsafe, unsafe 不改变规则只改变验证方式;

状态和控制流安全：

- Algebraic Data Types (Enum): 使用代数数据类型精确建模状态空间(如 Option / Result)，避免 null、非法状态和未定义分支；
- Pattern Matching: ``match`` 必须穷尽所有可能分支(exhaustiveness checking)，保证控制流完备性并消除遗漏分支；
- Error Handling: 基于 Result<T, E> 的显式错误传播(? 运算符)，将错误纳入类型系统，避免异常隐式传播和未处理错误；

类型和并发安全： 

- Type System: 类型系统用于表达不变量，使非法状态在编译期不可表示；
- Concurrency Safety: 基于 ``Send / Sync`` trait 和 Aliasing XOR Mutability，编译期保证数据竞争安全；

Algebraic Data Type(代数数据类型), 意思是类型可以像代数一样组合，核心有两种运算：

- Sum（加法）：表示从多个候选(tag)中选择一个，总的可能性是各个分支之和（如 enum）；
- Product（乘法））：表示多个字段(payload)组合在一起，总的可能性是各字段组合的乘积（如 struct/tuple）； 

在内存模型上, Rust 的 enum 通常表示为 tag + payload 的 tagged union, tag 标识 当前 payload,
加上一块能容纳最大 payload 的数据空间，同时编译器也会做内存布局优化。

编译系统
==========

rustc
-----

对于 C/C++ 程序，编译器会给每个源文件（编译单元）编译一个 ``.o``, 然后链接器会把所有的 ``.o`` 连接成 可执行/库。其中，
在编译每个源文件的时候，编译器会拿到编译flag，比如 ``-O2, -Wall`` 类似，还有 ``-Idir`` 配置依赖的头文件搜索路径，头文件
里放置了类型、宏、函数接口声明等，这些会觉得了编译调用的时候按照 calling convention 生成对应的调用代码。然后会预留一个符号，
最终链接的时候，去组合链接符号最终地址。

Rust区别于C/C++的一大特点是没有头文件，采用的是 metadata + 符号导出，类似 Go、Python 等现代语言。
对于 Rust 程序，基本的编译单元已经不是每个源文件了，因为其必须知道自己依赖的其他文件的相关依赖等，否则无法编译。
所以，Rust的基本编译单元是 crate, 1个 crate 会包括 1个或者多个 rust 源文件， 故 Crate 内有改动，整个 Crate 都
要分析，这就不能像 C/C++ 一样只编译对应的单个源文件了。

由于 crate 可能是多个 rs 源文件，然后 crate 引入了 root 的概念，每个 Crate 必须有一个且仅有一个 Crate Root 文件。
这个也是每个 crate 构建的起点，后续会通过 mod 等递归找后续的依赖的源文件。比如 ``mod network;`` 会让编译器去
寻找 ``network.rs`` 或 ``network/mod.rs`` 类似的查找规则也比较简单。

对于 crate, 还有下面说明:

- 对于可执行二进制（Executable），默认是 src/main.rs
- 对于可执行二进制，要有入口 ``fn main`` 函数，否则要 ``#![no_main]`` 自己制定入口
- 对于库（Library），则默认是 src/lib.rs，且默认是 静态库 ``.rlib``

    - rlib (Rust Lib ``.rlib``)：默认类型，专供 Rust 项目间依赖的静态库，包含编译器所需的元数据。
    - staticlib (Static C Lib ``.a``)：生成标准的 .a 或 .lib 静态库，用于将 Rust 代码嵌入到 C/C++ 项目中。
    - cdylib (C Dynamic Lib ``.so``)：生成 C 兼容的动态库（.so），常用于被或 C/C++ 调用。
    - dylib (Rust Dynamic Lib ``.so``)：Rust 专用动态库，因 ABI 不稳定，要求调用方必须使用相同版本的编译器，很少用。
    - proc-macro (Procedural Macro ``.so``)：一种特殊的动态库，仅在编译期间由编译器加载，用于实现自定义属性或派生宏。

crate root 如果不用默认，也可以配置指定, 对 rustc 来说，crate root 就是你传给它的那个 rs 源文件。
对于每个 crate，编译后除了bin二进制生成，还会有这个 crate 对应的 metadata, 在编译阶段为其他 crate 提
供“接口语义信息”（类型、trait、符号、泛型等），用于类型检查和代码生成。类似更强大的自动生成的头文件。

如果一个工程最终的构建目标是多个crate构成的，rustc 可以把把每个 crate 编译成 object/rlib，并调用 linker 将
多个 crate 最终链接成一个 ``.a/.so`` 或 ``bin`` 。这里必须用 ``rustc`` 去驱动 ``ld`` 链接，
``rustc`` 需要调用 ``ld`` 前需要做一些前置处理：

- 符号修饰（Mangling）：Rust 为了支持泛型和多态，生成的符号名极其复杂且带有版本哈希，手动识别这些符号几乎不可能。
- 运行时集成：rustc 需要确保链接了 Rust 专属的运行时库（如 libstd、libcore），负责初始化内存分配器、处理 Panic 和线程栈。
- 依赖图解析：rustc 会自动解析 Crate 之间复杂的依赖拓扑，并生成上百个包含正确顺序和路径的链接参数（-L 和 -l）。
- 平台适配（ABI）：不同操作系统和架构对链接器的要求不同，rustc 屏蔽了这些底层差异，确保生成符合当前环境的二进制格式。
- 单态化与优化：许多泛型代码直到链接阶段（LTO）才真正确定，rustc 必须指导链接器如何处理这些跨 Crate 的代码优化。

在 rust 的构建目录，也会经常看到 ``.o`` 后缀的文件，这个要注意，跟 C语言编译出来的 ``.o`` 不一样。

.. note::

    Rust 的 .o 是按编译优化单元（CGU Codegen Unit）划分的，与源文件没有直接对应关系。CGU 的划分
    是 rustc 在 MIR → LLVM IR 阶段，把一个 crate 按“函数/模块粒度 + 优化策略”拆分成多个独立代码
    生成单元，用于并行编译与控制优化边界。也是LLVM 优化的边界。

工程组织与构建实践
==================

cargo
-----

对于外部依赖处理，Rust有官方的包管理Cargo, 极大的方便了三方库的依赖处理。Cargo 读取 Cargo.toml 里的清单，把
下载好的依赖库路径传递给 ``rustc``, 比如当在代码里写 ``use serde;`` 时，编译器会去 Cargo 准备好的外部仓库清单里匹配。
Cargo 传递的类似参数 ``--extern serde=...``

此外，Cargo不仅仅是包管理，还会静态检查，组织编译等。当然，编译的话也可以用其他构建编排工具去调用 ``rustc``
对 cargo 来说，crate root 由 ``Cargo.toml`` 中 ``[[bin]]`` 或 ``[lib]`` 的 ``path`` 字段显式指定。

cargo 构建过程
^^^^^^^^^^^^^^^^^

使用 Cargo 大概构建过程就是:

- 1 解析工程配置

  - 读取 ``Cargo.toml``
  - 解析 ``[dependencies]`` 、features、profiles 等

- 2 解析依赖图
 
  - 构建完整 crate graph（包含 transitive deps）
  - 做版本选择（semver resolution）

- 3 获取依赖

  - 从 registry / git / path 下载或加载
  - 本地缓存（ ``$CARGO_HOME`` ）

- 4 编排构建

  - 拓扑排序 crate（按依赖顺序）
  - 区分 ``build.rs`` / proc-macro / normal crate
  - 增量编译决策（fingerprint）

- 5 生成 rustc 参数, 对每个 crate 生成类似：

  - ``-L`` （依赖搜索路径）
  - ``--extern`` （依赖绑定）
  - ``--cfg`` （feature / target cfg）
  - ``--crate-type`` （bin / lib / cdylib / staticlib）
  - ``--edition`` / ``-C`` （优化、LTO 等）

- 6 调用 rustc

  - 按 DAG 顺序逐个编译 crate
  - 并行执行（jobserver）
  - 处理编译缓存（incremental）
  - 输出到 ``target/``
  - 区分 debug / release / target triple

cargo workspace
^^^^^^^^^^^^^^^

当一个 Rust 工程里不止一个 crate 时，单独给每个 crate 各放一个 ``Cargo.toml`` 很快就会开始乱：
版本不好统一、构建输出目录重复、lockfile 分散、命令执行也麻烦。Cargo workspace 就是用来解决这个问题的。

workspace 本质上不是一个新的 crate，而是一层“构建和依赖编排的上层组织”。它把多个成员 crate 组织到一起，
统一管理依赖解析、构建输出目录和部分公共配置。可以把它理解成 Cargo 视角下的“多 crate 工程根”。

一个典型目录结构如下：

.. code-block:: text

    hello-workspace/
    |- Cargo.toml
    |- Cargo.lock
    |- target/
    |- app/
    |  |- Cargo.toml
    |  `- src/main.rs
    `- utils/
       |- Cargo.toml
       `- src/lib.rs

根目录的 ``Cargo.toml`` 通常只放 workspace 清单，例如：

.. code-block:: toml

    [workspace]
    members = ["app", "utils"]
    resolver = "2"

这种只有 ``[workspace]`` 而没有 ``[package]`` 的根清单，通常叫 virtual manifest。它自己不是一个 crate，
只是整个工程的组织入口。

其中几个关键行为：

- 所有 member crate 共享一份依赖解析结果，因此通常整个 workspace 只有一个 ``Cargo.lock`` ；
- 所有 member 默认共享根目录下的 ``target/`` ，避免每个 crate 各自生成一套构建产物；
- 在 workspace 根执行 ``cargo build`` 时，Cargo 会按依赖图统一调度所有需要构建的成员；
- crate 之间如果是 path 依赖，Cargo 会把它们直接纳入同一个工程图，而不是当成外部包处理；

比如 ``app`` 依赖 ``utils``:

.. code-block:: toml

    [dependencies]
    utils = { path = "../utils" }

这样 ``app`` 构建时， ``utils`` 会先作为同 workspace 中的本地 crate 被编译，然后再参与最终链接。

如果根目录除了 ``[workspace]`` 还带 ``[package]`` ，那么根目录自己也是一个 crate，这种情况常见于：

- 根目录本身就是一个可构建的应用/库；
- 同时它还想顺手管理若干子 crate；

不过大部分多 crate 工程，用 virtual manifest 更清晰，因为“工程根”和“具体 crate”这两个角色不会混在一起。

workspace 常见还有几个补充字段：

.. code-block:: toml

    [workspace]
    members = ["app", "utils", "tools/codegen"]
    exclude = ["tmp-demo"]
    default-members = ["app"]
    resolver = "2"

- ``members``: 声明哪些子目录属于当前 workspace；
- ``exclude``: 从匹配结果里排除某些目录；
- ``default-members``: 在根目录直接执行 ``cargo build`` / ``cargo test`` 时，默认只操作这些成员；
- ``resolver``: feature 解析策略，现代工程通常直接用 ``"2"`` ；

除了成员组织，workspace 还支持一部分“集中继承配置”。例如统一版本、edition、license，或者统一第三方依赖版本：

.. code-block:: toml

    [workspace.package]
    version = "0.1.0"
    edition = "2024"
    license = "MIT"

    [workspace.dependencies]
    anyhow = "1"
    serde = { version = "1", features = ["derive"] }

对应 member crate 里可以写：

.. code-block:: toml

    [package]
    name = "app"
    version.workspace = true
    edition.workspace = true
    license.workspace = true

    [dependencies]
    anyhow.workspace = true
    serde.workspace = true

这样做的好处很直接：版本只维护一份，避免多个 crate 各自写一遍然后慢慢漂移。

不过要注意，workspace 只是“统一编排”，不是“自动合并 crate”：

- 每个 member 仍然是独立 crate，仍有自己的 crate root、依赖、feature 和编译边界；
- 一个成员改动后，Cargo 只会重编受影响的 crate 图，不是把整个 workspace 无脑全量重编；
- workspace 不改变 Rust 的模块系统， ``mod`` 还是 crate 内部的源码组织手段，不能拿来跨 crate 引文件；

日常最常用的几个命令：

.. code-block:: bash

    cargo build                  # 在 workspace 根构建默认成员
    cargo build --workspace      # 构建所有成员
    cargo test -p utils          # 只测试某个 package
    cargo run -p app             # 运行指定二进制成员
    cargo check --workspace      # 对整个工程做快速静态检查

.. note::

    ``workspace`` 是 Cargo 层面的工程组织； ``crate`` 是 rustc 层面的编译单元； ``mod`` 是 crate 内部的源码拆分方式。
    这三个概念很容易混，但其实正好对应了 工程级 / 编译级 / 源码级 三个层次。

Rust 工程组织
-------------

前面讲的是 Cargo 和 workspace 在构建层面的职责；落到工程落地时，更常见的问题是：
目录怎么摆，单 crate 什么时候够用，什么时候该拆成 workspace，以及纯 Rust 工程和 C/Rust 混合工程的组织重点到底有什么不同。

纯 Rust 工程的默认约定
^^^^^^^^^^^^^^^^^^^^^^

如果是业界里一个“纯 Rust”工程，通常首先会遵守 Cargo 的默认目录约定。原因很简单：
工具链、IDE、文档生成、测试发现、示例构建、CI 命令几乎都围绕这些约定工作。遵守约定，
能明显降低理解成本，也减少自己手写额外配置的需要。

最常见的单 crate 目录大致如下：

.. code-block:: text

    my-crate/
    |- Cargo.toml
    |- Cargo.lock
    |- src/
    |  |- lib.rs
    |  |- main.rs
    |  |- config.rs
    |  |- model.rs
    |  |- service/
    |  |  |- mod.rs
    |  |  `- user.rs
    |  `- bin/
    |     `- admin.rs
    |- tests/
    |  `- api_test.rs
    |- examples/
    |  `- basic.rs
    |- benches/
    |  `- parser.rs
    |- build.rs
    |- rustfmt.toml
    |- clippy.toml
    `- .cargo/
       `- config.toml

不过这里不是说所有文件都必须同时存在，而是说 Cargo 为这些名字提供了清晰约定：

- ``src/lib.rs``: 库 crate 的默认 crate root，也是对外 API 的主要收口点；
- ``src/main.rs``: 主二进制的默认入口，适合放程序启动、参数解析、初始化等；
- ``src/bin/*.rs``: 一个 package 下挂多个独立二进制时使用，每个文件对应一个可执行程序；
- ``tests/``: integration test，每个文件会被当成单独的测试 crate 编译；
- ``examples/``: 可编译、可运行的示例代码，常用于演示公开 API 的使用方式；
- ``benches/``: benchmark 代码，一般配合 Criterion 等库使用；
- ``build.rs``: 构建脚本，只在确实需要编译期探测、代码生成、链接外部库时才加；
- ``.cargo/config.toml``: 放 target、runner、alias、linker 等 cargo 级别配置；

这里需要特别注意一个容易混淆的点： ``Cargo.toml`` 的 package 维度，和 ``src/`` 里的 crate 入口维度，不完全是同一个概念。
一个 package 最常见是“一个 lib + 零个或多个 bin”：

- 如果只有 ``src/lib.rs`` ，那它是一个纯库 package；
- 如果只有 ``src/main.rs`` ，那它是一个纯可执行 package；
- 如果两者都存在，那么同一个 package 会同时产出一个 library crate 和一个 binary crate；

后一种在业界很常见，因为它可以让 ``main.rs`` 只是很薄的一层壳，把真正业务逻辑都放进 ``lib.rs`` 对应的库里，
这样测试、复用和后续拆分都会更容易。

小型纯 Rust 工程的默认起点
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果问题进一步收窄成“一个小型工程刚开始时该怎么搭”，推荐答案其实更明确：
对绝大多数小型 Rust 工程，优先从单一 crate / 单一 package 开始，通常是最稳妥的。

这里说的“小型”，不只是代码行数少，更是说它满足下面几类特征：

- 当前只有一个可执行程序，或者一个明确的库；
- 核心逻辑还在快速变化，边界没有完全稳定；
- 团队人数不多，协作复杂度有限；
- 暂时没有强烈的独立发布、独立复用、独立构建需求；

在这种阶段，过早拆成 workspace、多 crate、多层 feature，通常收益不大，反而会引入额外复杂度：

- 依赖版本需要多处维护；
- API 边界会被过早“冻结”；
- 模块之间原本可以直接重构，现在会被 crate 边界阻挡；
- 新人需要先理解工程拓扑，再理解业务逻辑；

因此，一个很实用的经验法则是：

- 小型工程优先单 crate；
- 先用模块边界管理复杂度；
- 等模块边界稳定后，再决定是否升级成多 crate；

单 crate 的优势，不只是“文件更少”，而是它天然更适合早期迭代：

- 改动成本低：模块之间移动类型、函数、trait 时，不需要反复改公开 API；
- 心智负担低：工程图就是一个 package，不必先分辨 workspace / member / path dependency；
- 测试直接：单元测试、integration test、examples 都能围绕一套代码组织；
- 工具链简单：``cargo check`` / ``cargo test`` / ``cargo run`` 就能覆盖大部分日常开发；

很多工程在一开始其实并不需要回答下面这些问题：

- 哪个子模块该不该独立发包？
- 哪些 feature 要跨 crate 传递？
- 哪个 crate 才是稳定公共 API？

如果这些问题当前都还不明确，那通常说明还没到拆 crate 的时机。换句话说，单 crate 不是“简陋版本”，
而是很多小型工程在工程实践上最合理的默认起点。

一个小型纯 Rust 工程，目录通常可以克制到下面这样：

.. code-block:: text

    my-app/
    |- Cargo.toml
    |- Cargo.lock
    |- src/
    |  |- main.rs
    |  |- lib.rs
    |  |- cli.rs
    |  |- config.rs
    |  |- error.rs
    |  |- app.rs
    |  `- storage/
    |     `- mod.rs
    |- tests/
    |  `- smoke_test.rs
    |- .gitignore
    |- rustfmt.toml
    |- clippy.toml
    `- README.md

这里面最核心的思想不是“文件越多越专业”，而是：

- 根目录只放工程级文件；
- ``src/`` 只放源码；
- 测试、示例、benchmark 分别落在各自标准位置；

如果工程更小，甚至可以再收缩成：

.. code-block:: text

    my-app/
    |- Cargo.toml
    `- src/
       |- main.rs
       `- lib.rs

这两种都很正常。关键不在于一开始目录是不是“完整”，而在于是否遵守约定、是否便于继续扩展。

对这类小型工程，比较推荐的文件职责大致如下：

- ``Cargo.toml``: 唯一清单入口，描述 package 信息、依赖、feature、profile；
- ``Cargo.lock``: 可执行程序通常应该提交；库 crate 是否提交要看团队策略；
- ``src/main.rs``: 进程入口，负责启动流程；
- ``src/lib.rs``: 业务入口与公共 API 门面；
- ``src/config.rs``: 配置读取、默认值、环境变量映射；
- ``src/error.rs``: 错误类型、``Result`` 别名、错误转换；
- ``src/cli.rs``: 命令行参数解析；
- ``tests/``: 从外部视角验证程序行为；
- ``README.md``: 项目说明、构建方式、运行示例；

这里尤其建议保留 ``lib.rs``，哪怕当前只是个小工具。原因很现实：

- 这样 ``main.rs`` 可以保持很薄；
- 后续写 integration test 更方便；
- 如果未来出现第二个 bin 或需要抽公共逻辑，不必大改；

小型工程里常见的约定文件也不需要一上来全加满，更合理的顺序通常是：

- 先只有 ``Cargo.toml`` + ``src/``；
- 需要格式统一时再加 ``rustfmt.toml``；
- 需要工具链锁定时再加 ``rust-toolchain.toml``；
- 需要系统级构建桥接时再加 ``build.rs``；

也就是说，文件应该为需求服务，而不是为了“看起来像业界工程”而堆出来。

``lib.rs`` 和 ``main.rs`` 的职责
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

很多刚接触 Rust 的人会把所有代码直接堆进 ``main.rs`` ，小 demo 没问题，但真实工程通常不会这么做。
比较常见的组织方式是：

- ``main.rs`` 负责“启动流程”；
- ``lib.rs`` 负责“可复用逻辑”；

例如一个命令行工具， ``main.rs`` 常见只做几件事：

- 解析命令行参数；
- 初始化日志、配置、运行时；
- 调用库层入口；
- 处理退出码和错误打印；

而真正的业务实现、协议处理、数据库访问、领域逻辑，通常会放在 ``lib.rs`` 及其子模块里。
原因主要有下面几点：

- library 更容易做单元测试，不必每次都通过进程级入口去测；
- integration test 可以直接依赖这个库 crate，而不是只能黑盒跑二进制；
- 当工程后面要拆 workspace、多二进制复用同一逻辑时，迁移成本更低；
- 文档生成（ ``cargo doc`` ）主要围绕库 API 展开，公共接口放在库层更自然；

一个常见例子如下：

.. code-block:: text

    my-app/
    |- Cargo.toml
    `- src/
       |- main.rs
       |- lib.rs
       |- cli.rs
       |- app.rs
       `- infra/
          `- mod.rs

其中 ``main.rs`` 可能非常薄：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        my_app::run()
    }

而 ``lib.rs`` 暴露相对稳定的入口：

.. code-block:: rust

    pub mod app;
    mod cli;
    mod infra;

    pub fn run() -> anyhow::Result<()> {
        let args = cli::parse();
        app::run(args)
    }

这种写法的核心思想是：把“进程入口”与“程序能力”分开。前者只有一个，后者往往需要被测试、被示例、被其他 bin 复用。

``src`` 目录内部如何拆模块
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``src/`` 目录内部属于 Rust 模块系统的范畴。一个常见误区是把文件系统层次，误认为就是最终对外的模块层次；
其实文件只是承载方式，真正决定模块树的是 ``mod`` / ``pub mod`` 声明以及 re-export。

现代 Rust 工程里，一个模块常见有两种落地形式：

- ``foo.rs``: 适合模块比较小，内容集中；
- ``foo/mod.rs`` 加 ``foo/*.rs``: 适合这个模块本身还有多个子模块；

例如下面两种都合法：

.. code-block:: text

    src/
    |- lib.rs
    |- parser.rs
    `- parser/
       |- lexer.rs
       `- ast.rs

或者：

.. code-block:: text

    src/
    |- lib.rs
    |- parser.rs
    |- lexer.rs
    `- ast.rs

很多老资料会大量使用 ``mod.rs`` ，这是历史上更常见的写法。现在 Rust 也支持：

- ``foo.rs`` 作为模块 ``foo`` 的定义文件；
- 同时在 ``foo/`` 目录下放它的子模块文件；

所以现代工程里更常见的是：

.. code-block:: text

    src/
    |- lib.rs
    |- parser.rs
    `- parser/
       |- lexer.rs
       `- ast.rs

对应 ``lib.rs``:

.. code-block:: rust

    pub mod parser;

对应 ``parser.rs``:

.. code-block:: rust

    pub mod lexer;
    pub mod ast;

这种方式通常比到处放 ``mod.rs`` 更直观，因为目录名和模块入口文件不会同名叠在一起。

从工程实践看，模块拆分通常遵循几个原则：

- 先按职责拆，而不是按语言特性拆；例如优先拆 ``config`` 、 ``http`` 、 ``storage`` ，而不是拆成 ``structs`` 、 ``traits`` 、 ``utils`` ；
- ``lib.rs`` 主要做模块声明与对外 re-export，不要把大量实现细节都堆进去；
- 子模块内部尽量保持高内聚，避免随处 ``pub`` 暴露导致边界失控；
- 如果一个模块只有父模块会用，优先 ``mod`` 或 ``pub(crate)`` ，不要上来就对外公开；
- ``utils.rs`` 这类名字要克制使用，很多时候它只是“暂时不知道该放哪”的信号；

关于 ``lib.rs`` 本身，一个很常见的最佳实践是把它当成“包的公开门面”，而不是“最大的实现文件”。
例如：

.. code-block:: rust

    mod config;
    mod error;
    pub mod client;

    pub use client::Client;
    pub use error::{Error, Result};

这样外部使用者看到的是比较稳定、紧凑的 API 面，而不是被迫知道内部所有模块细节。

``tests`` / ``examples`` / ``benches`` 的常见用法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rust 工程里，测试代码一般不只一种形态，常见会分成三层：

- 单元测试（unit test）：通常写在模块内部的 ``#[cfg(test)] mod tests`` ；
- 集成测试（integration test）：放在 ``tests/`` 目录下；
- 示例与基准：分别放在 ``examples/`` 与 ``benches/`` ；

单元测试更适合测局部实现细节，因为它可以直接访问当前模块的私有项；而 ``tests/`` 下的 integration test
更像从外部使用者视角验证公共 API 和系统行为。

例如：

.. code-block:: rust

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn parse_ok() {
            assert!(parse("42").is_ok());
        }
    }

而 ``tests/api_test.rs`` 则通常写成：

.. code-block:: rust

    use my_crate::Client;

    #[test]
    fn client_can_connect() {
        let _ = Client::new();
    }

这两类测试的差异，本质上是：

- 模块内测试偏白盒；
- ``tests/`` 下测试偏黑盒；

业界实践上，通常建议：

- 核心算法、边界条件、多分支逻辑优先写单元测试；
- 公共接口、模块协作、对外行为保证放 integration test；
- ``examples/`` 里的代码尽量保持“真的能运行”，不要把它当伪代码文档；
- benchmark 放到独立目录，不要和功能测试混在一起；

单 crate 何时够用，何时拆成 workspace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

很多工程一开始并不需要 workspace。一个经验上比较合理的顺序是：

- 先从单 package 开始；
- 当公共逻辑明确需要被多个二进制、多个库、或不同发布边界复用时，再拆成多个 crate；

也就是说，是否拆 crate，不要只看“文件多不多”，而要看“边界是否已经稳定”。

下面几种情况，比较适合继续保持单 crate：

- 代码规模还不大，核心逻辑强耦合；
- 目前只有一个可执行程序；
- 所谓“模块边界”还经常变化；
- 团队还在快速试错，过早拆 crate 只会增加 feature、版本和依赖管理成本；

而下面几种情况，通常可以考虑拆 workspace / 多 crate：

- 一个共享库被多个 bin、多个服务、多个工具共同依赖；
- 想把 proc-macro、代码生成器、核心库、CLI 明确隔离；
- 不同子系统的依赖差异很大，放一起会让编译时间和依赖面失控；
- 需要更清晰的发布边界，甚至部分 crate 需要单独发到 crates.io；

一个较常见的业界结构类似：

.. code-block:: text

    my-workspace/
    |- Cargo.toml
    |- Cargo.lock
    |- crates/
    |  |- core/
    |  |  |- Cargo.toml
    |  |  `- src/lib.rs
    |  |- storage/
    |  |  |- Cargo.toml
    |  |  `- src/lib.rs
    |  `- cli/
    |     |- Cargo.toml
    |     `- src/main.rs
    `- tools/
       `- xtask/
          |- Cargo.toml
          `- src/main.rs

这里 ``crates/`` 只是社区里常见习惯，不是 Cargo 强制要求。有人也会直接用 ``app/`` 、 ``libs/`` 、 ``tools/`` 。
重点不在目录名，而在于边界是否稳定、是否便于理解。

小型 C/Rust 混合工程的推荐组织方式
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果工程是小型 C/Rust 混合项目，推荐思路和纯 Rust 工程有一点不同：
这里通常不是“一个单 crate 就够了”，而是“Rust 侧仍然尽量简单，但 C/Rust 边界要尽早清楚”。

原因是混合工程的主要复杂度，往往不在 Rust 模块内部，而在下面这些地方：

- C 头文件与 Rust 绑定怎么对应；
- 最终由谁驱动链接；
- 生成代码放在哪里；
- unsafe 和原始 FFI 应该落在哪一层；

所以小型混合工程更推荐的不是“马上搞大 workspace”，而是：

- 整个工程尽量只有一个系统构建入口；
- Rust 侧先保持一个或少数几个 crate；
- FFI 层和业务层尽量分开；

一个小型混合工程，比较推荐的目录可以类似这样：

.. code-block:: text

    hybrid-demo/
    |- meson.build
    |- include/
    |  `- demo.h
    |- src/
    |  `- demo.c
    |- rust/
    |  |- Cargo.toml
    |  |- build.rs
    |  `- src/
    |     |- lib.rs
    |     |- ffi.rs
    |     `- service.rs
    |- tests/
    `- README.md

这个结构里，推荐把职责分清：

- 根目录 ``meson.build`` 或其他系统构建文件：负责最终产物；
- ``include/`` 和 ``src/``: C 侧头文件与实现；
- ``rust/src/ffi.rs``: 原始 ``extern "C"``、绑定类型、unsafe 转换；
- ``rust/src/service.rs``: 更高层的 Rust 逻辑；
- ``rust/src/lib.rs``: 收口 Rust 对外能力；
- ``rust/build.rs``: 在必要时桥接系统构建结果；

如果工程再稍微大一点，更推荐把 Rust 侧拆成“ffi crate + 业务 crate”，但仍然不需要一开始就拆太多：

.. code-block:: text

    hybrid-demo/
    |- CMakeLists.txt
    |- csrc/
    |- include/
    `- rust/
       |- Cargo.toml
       |- ffi/
       |  |- Cargo.toml
       |  `- src/lib.rs
       `- app/
          |- Cargo.toml
          `- src/lib.rs

这类拆分的核心不是为了显得架构复杂，而是为了把 raw FFI 和业务逻辑隔开。

纯 Rust 与 C/Rust 混合时的组织重点
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

两类工程最核心的区别可以概括成一句话：

- 纯 Rust 工程优先以模块边界组织；
- 混合工程优先以语言边界和构建边界组织；

对于纯 Rust 小工程，最重要的是：

- ``src/`` 内职责清晰；
- ``main.rs`` 和 ``lib.rs`` 分工清楚；
- 模块不要过度拆分；

对于混合工程，最重要的是：

- 先明确谁是最终 build 的拥有者；
- FFI 边界集中，而不是散在业务模块里；
- 生成代码、头文件、绑定文件有固定落点；

所以一个很实用的判断标准是：

- 如果你的主要问题是“Rust 模块怎么拆”，大概率还是纯 Rust 工程思路；
- 如果你的主要问题是“Cargo 和 CMake/Meson 谁说了算、头文件怎么进 Rust”，那已经是混合工程思路；

不推荐的组织方式与升级路径
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

下面几种做法，在小型 Rust 或小型混合工程里都不太推荐：

- 一开始就拆成很多 crate，但每个 crate 之间还高度耦合；
- 只有一个二进制程序，却把大量逻辑硬拆成 workspace 多成员；
- 把所有辅助代码都丢进 ``utils.rs`` / ``common.rs``，导致职责越来越模糊；
- 让 ``main.rs`` 变成几百上千行的大文件；
- 在很多业务模块里直接写 ``extern "C"`` 或裸指针操作；
- 没有明确谁负责最终构建，导致 Cargo 和 Meson/CMake 各管一半；

这些问题的共同点是：不是目录本身错了，而是工程边界没有立住。

一个小型工程开始变复杂时，通常可以按下面顺序升级，而不是一步跳到很重的结构：

- 1 先把 ``main.rs`` 做薄，把业务逻辑沉到 ``lib.rs``；
- 2 再把 ``config``、``error``、``app``、``storage`` 这类职责拆成模块；
- 3 如果出现第二个可执行程序，再考虑 ``src/bin/``；
- 4 如果出现稳定公共边界，再考虑拆独立 crate；
- 5 如果同时有多个独立 crate，再考虑 workspace；

对于混合工程，也有类似顺序：

- 1 先明确系统构建入口；
- 2 再把 Rust 原始 FFI 和业务逻辑分层；
- 3 如果绑定层开始膨胀，再把 FFI 单独拆 crate；
- 4 如果不同子系统的依赖与发布边界明显不同，再考虑多 crate/workspace；

这比一开始就设计一个“看起来很大厂”的目录树，通常更稳妥。

工程实践上的几个常见建议
^^^^^^^^^^^^^^^^^^^^^^^^^^^

除了目录本身，纯 Rust 工程在业界里还有一些比较稳定的实践倾向：

- 尽量遵守 Cargo 默认约定，少改 crate root 路径，除非确实有集成历史包袱；
- ``main.rs`` 保持薄，业务逻辑沉到 ``lib.rs`` 和子模块；
- 优先用模块边界解决问题，只有当复用/发布/依赖边界稳定时再升级成多 crate；
- 谨慎使用 ``pub`` ，公开 API 一旦被依赖，后续收缩成本会很高；
- ``build.rs`` 只在必要时使用，因为它会引入额外构建复杂度和缓存失效点；
- feature flag 用于可选能力与依赖裁剪，不要把它当成大规模条件编译拼图；
- 工程根常见会放 ``rustfmt.toml`` 、 ``clippy.toml`` 、 ``rust-toolchain.toml`` ，用于统一格式、lint 和工具链版本；
- CI 里常见至少跑 ``cargo fmt --check`` 、 ``cargo clippy`` 、 ``cargo test`` 、 ``cargo check --workspace`` ；

关于 feature flag，再补一条很重要的经验：feature 更适合表达“增量能力”，不适合表达互相缠绕的大型产品矩阵。
如果 feature 组合已经让测试矩阵和代码路径变得难以穷尽，通常说明 crate 边界或产品分层需要重新整理。

另外，Rust 工程里还经常会看到一个 ``xtask`` crate。它本质上只是团队约定，不是官方机制，
思路是用 Rust 自己写工程脚本，而不是堆很多 Bash/Python 脚本。例如封装下面这些任务：

- 代码生成；
- 打包发布；
- 本地开发辅助命令；
- 一些跨平台但不适合塞进 ``build.rs`` 的自动化流程；

它常见长这样：

.. code-block:: bash

    cargo run -p xtask -- codegen
    cargo run -p xtask -- release

这种方式的优点是脚本也能复用同一套依赖管理、类型系统和跨平台能力，但前提是团队真的愿意维护它；
如果只是非常简单的几条命令，直接放 Makefile 或 CI 配置里也未必不好。

.. note::

    对多数 Rust 工程来说，最稳妥的起点通常不是“先设计一个很复杂的目录树”，而是：
    先遵守 Cargo 默认约定，用 ``src/lib.rs`` / ``src/main.rs`` / ``tests/`` 这些基础结构把边界立住；
    等代码增长后，再根据复用边界、发布边界和依赖边界，决定是否拆成 workspace 多 crate。

.. note::

    对小型 Rust 工程，最推荐的默认起点通常就是一个单 crate：
    纯 Rust 场景下，优先用 ``src/main.rs`` + ``src/lib.rs`` + 若干职责模块；
    C/Rust 混合场景下，优先保证构建入口唯一、FFI 边界集中、Rust 侧 crate 数量克制。

C/Rust 混合工程（以 QEMU 为例）
--------------------------------

纯 Rust 工程的默认世界观，通常是 Cargo 作为唯一的构建入口；但像 QEMU 这种历史悠久、体量巨大、以 C 为主体的系统软件，
真实情况往往不是“全部重写”，而是“在已有 C 工程中渐进引入 Rust”。这种工程的重点，不是把目录做得像标准 Cargo 项目，
而是把下面几件事同时处理好：

- 最终产物仍然能被原有主构建系统稳定地产出；
- Rust 代码能享受到 Cargo 生态的开发体验（lint、fmt、doc、IDE）；
- C 和 Rust 的边界清晰，unsafe 尽量集中；
- 改一个头文件、一个设备模型、一个绑定层时，不会把整个工程无脑重编；

QEMU 是这类工程里非常有代表性的例子：主工程仍以 C 和 Meson/Ninja 为中心，但 Rust 代码已经被系统性纳入同一套大工程构建。
它不是“Rust 主工程 + 少量 C glue”，而是反过来，“C 主工程 + 若干渐进接入的 Rust 子系统”。

从目录组织上，可以把它理解成下面这种形态：

.. code-block:: text

    qemu/
    |- meson.build
    |- include/
    |- hw/
    |  |- char/
    |  |  `- pl011.c
    |  `- timer/
    |     `- hpet.c
    |- rust/
    |  |- Cargo.toml
    |  |- meson.build
    |  |- qemu-api/
    |  |- qemu-api-macros/
    |  |- hw/
    |  |  |- char/
    |  |  |  `- pl011/
    |  |  `- timer/
    |  |     `- hpet/
    |  |- bindings/
    |  `- tests/
    `- subprojects/

这个结构的关键信号很明显：

- 整个仓库根仍然是 C 工程的根， ``meson.build`` 在最外层；
- Rust 代码整体收敛到 ``rust/`` 子树，而不是零散混进所有 C 目录；
- 具体设备模型的 Rust 实现，仍然按 QEMU 原有子系统语义组织，例如 ``hw/char/pl011`` 、 ``hw/timer/hpet`` ；
- 绑定生成、宏 crate、测试 crate 等“Rust 特有基础设施”集中放在 ``rust/`` 下统一管理；

这种组织方式非常适合“大型存量 C 工程渐进引入 Rust”，因为它既保留了原工程的心智模型，也没有把 Rust 代码变成完全脱离主树的外部插件。

QEMU 这类工程为什么不能让 Cargo 独自统管
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果一个工程最终的链接、配置探测、平台差异处理、代码生成、子项目管理，本来就是由 Meson/CMake/Bazel 之类系统构建工具掌控，
那么 Cargo 通常就不适合直接当“唯一真相来源”。QEMU 的情况就很典型：

- 最终二进制并不只是 Rust 产物，而是大量 C 对象文件、生成代码、系统库、平台配置一起链接出来；
- 很多 Rust 代码依赖 C 侧生成的头文件、配置宏、对象文件或 glue code；
- 测试也常常不是纯 Rust 单元测试，而是依赖整个 QEMU 运行时与辅助 C 代码；

因此在这类工程里，最稳定的思路通常是：

- 系统级构建、最终链接、平台探测交给主构建系统；
- Rust 开发体验、lint、fmt、doc、依赖描述交给 Cargo workspace；

QEMU 官方文档对这个分工说得很直接：Rust 代码是通过 Meson 集成进模拟器的，Meson 直接调用 ``rustc`` 生成静态库，
再与 C 代码一起链接；而 Cargo 主要用于 ``clippy`` 、 ``rustfmt`` 、 ``rustdoc`` 这类 Rust 开发工作流。

这类分工的核心思想可以概括成一句话：

- Cargo 负责“描述 Rust 世界”；
- Meson 负责“产出整个系统”；

这和很多初学者理解的“Cargo 一定是最终 build 的入口”不同。在混合工程里，更合理的问题往往是：
哪个工具最了解最终产物的全貌？如果答案不是 Cargo，那 Cargo 就更适合做 Rust 子世界的工具入口，而不是全局链接入口。

Meson 和 Cargo 的职责分工
^^^^^^^^^^^^^^^^^^^^^^^^^^^

以 QEMU 这种工程为例，Meson 和 Cargo 最常见的职责边界大致如下：

Meson 更适合负责：

- 宿主机/目标机能力探测；
- C 编译选项、系统库、平台 ABI 差异；
- 生成配置头、生成源码、组织子目录；
- 调度 bindgen、rustc、cc 等多语言工具链；
- 把 Rust 静态库和 C 对象一起做最终链接；
- 统一测试入口、统一安装与打包；

Cargo 更适合负责：

- Rust crate graph 与 path dependency 描述；
- workspace 级别 edition、lint、依赖版本约束；
- ``cargo clippy`` / ``cargo fmt`` / ``cargo doc`` ；
- 给 rust-analyzer 等工具提供可理解的 Rust 项目模型；

QEMU 里还有一个很典型的做法：为了让 Cargo 工作流与 Meson 生成产物协同，专门使用 ``build.rs`` 去拾取 Meson build 目录下的生成文件，
再放到 Cargo 预期的位置。这个做法本质上是在解决一个现实问题：

- Meson 才知道系统构建过程中生成了什么；
- Cargo/IDE 又需要“看见”这些生成物，才能把 Rust 项目体验做完整；

所以在混合工程里， ``build.rs`` 不一定只是“编译 Rust 原生 C 依赖”的脚本，它也可以是“把系统级构建结果桥接给 Cargo 工具链”的适配层。

如果抽象成一般规律，大致可以写成：

- 主构建系统是最终真相来源（source of truth）；
- Cargo workspace 是 Rust 子树的开发真相来源；
- ``build.rs`` / 环境变量 / 生成目录拷贝，是两者之间的桥；

因此，看到一个 C/Rust 混合工程同时有 ``meson.build`` 和 ``Cargo.toml`` ，不要马上觉得“重复”。
很多时候它们分别在回答不同问题：

- ``Cargo.toml`` 回答：Rust 代码如何组织、如何 lint、如何做局部文档化；
- ``meson.build`` 回答：整个产品怎样真正被构建、链接、测试、发布；

QEMU 中 Rust crate 的分层思路
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

QEMU 的代表性，不只在于“用了 Rust”，更在于它没有把 Rust 代码随意堆成一个大 crate，而是明显按职责分层。
从工程抽象上，可以把这类混合工程里的 Rust 部分理解成下面几层：

- 原始绑定层（raw FFI / bindings）；
- 安全封装层（safe wrapper / API layer）；
- 过程宏与元编程层（proc-macro）；
- 具体业务或设备实现层（leaf crates）；

QEMU 文档里明确提到，绑定不是只做一个巨大的总绑定库，而是按子系统拆分，例如 util、qom、chardev、hw core、migration、system 等。
这样做有两个很现实的好处：

- C 头文件改动时，受影响的 Rust crate 范围更小；
- 不会让所有绑定类型都堆进一个巨大命名空间和一个巨型 crate 里；

这其实是混合工程里很值得借鉴的一条经验：raw FFI crate 不要按“语言”切，而要按“子系统依赖边界”切。

对于 QEMU，可以把典型职责理解为：

- 绑定层 crate：负责把 C 接口、结构体、枚举、宏常量映射进 Rust；
- ``qemu-api`` 这类上层 crate：负责把原始绑定包装成更可用、更 Rust 化的接口；
- ``qemu-api-macros`` ：负责派生宏、元数据提取、样板代码生成；
- ``pl011`` 、 ``hpet`` 这类 leaf crate：负责具体设备模型的业务实现；

这和一般社区里推荐的混合工程拆分法其实非常一致：

- ``foo-sys`` 或 bindings crate 负责“不好看但真实”的原始接口；
- ``foo`` 或 api crate 负责“安全、可维护、符合 Rust 习惯”的包装；
- 真正业务 crate 只依赖包装层，不直接四处碰裸 FFI；

这么拆的主要目的，不是“看起来更模块化”，而是为了明确下面这些边界：

- unsafe 边界；
- 重新编译边界；
- API 稳定边界；
- 团队协作边界；
- 测试边界；

多个 crate 拆分的真实目的
^^^^^^^^^^^^^^^^^^^^^^^^^^^

在混合工程里，crate 拆分往往比纯 Rust 应用更有价值，因为它不仅是源码组织，更直接关系到 FFI 边界与构建成本。
以 QEMU 这类工程为例，多个 crate 一般至少在解决下面几类问题：

- 1 隔离 raw FFI

  把 bindgen 生成物、 ``extern "C"`` 、裸指针转换集中在少数 crate 中，避免业务代码层到处散落 unsafe。

- 2 控制重编成本

  头文件或 wrapper 变化时，只让受影响的绑定子树重编，而不是所有设备 crate 全部重编。

- 3 明确宿主构建与目标构建差异

  例如 ``proc-macro`` crate 本质上运行在宿主编译器环境中，天然就应该单独拆分，不能和目标侧库随意混在一起。

- 4 保持 API 语义分层

  绑定层的 API 通常不漂亮也不稳定；上层封装 crate 可以把对外语义收口，减少叶子 crate 直接依赖底层细节。

- 5 给测试和迁移留空间

  当团队希望把某个 C 子系统逐步替换成 Rust 时，先替换 leaf crate，再逐步沉淀公共 wrapper，比一开始就做大一统 crate 更可控。

所以，不要把“多个 crate”简单理解成“Rust 社区喜欢这样分”。对于混合工程来说，它更多是在做“架构隔离”和“编译隔离”。

QEMU 里的命名和目录命名实践
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

QEMU 官方文档专门讨论了 Rust 命名约定，这一点很值得注意。C 世界里的命名，经常带有很强的前缀风格，例如：

- ``QEMUTimer``
- ``timer_mod``
- ``sysbus_connect_irq``
- ``qdev_realize``

到了 Rust 侧，通常不会机械保留所有 C 前缀，而是会做“Rust 化映射”：

- 类型名用 Rust 的类型风格；
- 方法名去掉重复的前缀；
- 但如果在继承层次/语义层次里出现重名或歧义，则保留必要前缀来区分；

QEMU 文档里给出的例子很典型：

- ``QEMUTimer`` 对应到 ``timer::Timer`` ；
- ``timer_mod`` 对应到 ``Timer::modify`` ；
- ``sysbus_connect_irq`` 对应到 ``SysBusDeviceMethods::connect_irq`` ；

而如果类层次里同名语义容易混淆，则下层类型的方法名会保留更多前缀。

这背后的通用经验是：

- C 的命名常常在弥补“没有命名空间”；
- Rust 已经有模块、类型、trait 这些命名空间能力，所以前缀可以适度去掉；
- 但不能为了“更像 Rust”就把语义差异抹平；

因此，对于混合工程的目录和命名，比较好的实践通常是：

- 目录名尽量沿用原 C 工程的领域结构，例如 ``hw/char`` 、 ``block`` 、 ``migration`` ；
- crate 名体现角色，例如 ``*-sys`` 、 ``*-macros`` 、 ``*-api`` 、具体模块名；
- Rust ``use`` 时的名字要符合 Rust 习惯，但目录层次不要和原工程脱钩；
- 不要发明大量和原 C 工程不一致的新术语，否则跨语言读代码时心智切换成本会很高；

QEMU 还有一个很细但很有代表性的点：目录名可以是 ``qemu-api`` ，而 Rust crate 名/导入名是 ``qemu_api`` 。
这说明目录命名和 Rust 代码里的标识符命名，最好分别遵守各自社区的常规，而不是强行统一成一种风格。

QEMU 特化的实践
^^^^^^^^^^^^^^^^

下面这些做法，更偏 QEMU 这个项目自身的结构与约束，并不一定要机械照搬到所有混合工程：

- Meson 是绝对主导的系统构建入口，Cargo 不是最终二进制的拥有者；
- Rust 当前主要聚焦在特定设备模型/子系统上，而不是平均渗透到全部模块；
- Rust 侧接口深度依赖 QOM、SysBusDevice、Migration、MemoryRegion 等 QEMU 内部对象模型；
- 由于 QOM 对象共享引用很多，QEMU 文档特别强调应优先 ``&self`` + interior mutability，而不是轻易从裸指针恢复 ``&mut self`` ；
- QEMU 还引入了和 Big QEMU Lock 相关的专门 cell 类型，用来表达锁语义与 interior mutability；
- 新增第三方 Rust 依赖时，除了改 ``Cargo.toml`` ，还要让 Meson 学会如何构建这些 crate，并维护对应 subproject；

这些做法背后都不是“Rust 语言必然要求”，而是因为 QEMU 已有的大工程现实：

- 历史包袱重；
- C 抽象模型成熟；
- 并发/锁模型不是从 Rust 原生设计出来的；
- 最终构建和发布流程必须继续统一在现有工程系统下；

因此看 QEMU 时，要分清楚：

- 哪些是“Rust 语言的通用最佳实践”；
- 哪些是“为了接住 QEMU 现有架构而做的适配”；

更通用的 C/Rust 混合工程实践
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

如果把 QEMU 的经验抽象出来，对一般 C/Rust 混合工程更普适的建议大致有下面这些：

- 只保留一个最终构建真相来源。可以是 Meson、CMake、Bazel，但最好不要让 Cargo 和系统构建同时争夺最终链接控制权；
- 把 FFI 层做薄，且集中。业务 crate 不要直接依赖大段 ``bindgen`` 输出；
- unsafe 优先包进专门 crate、trait、wrapper 或宏里，而不是散在叶子业务逻辑里；
- 绑定按子系统边界拆，而不是一口气生成一个巨型 ``bindings.rs`` ；
- proc-macro 单独成 crate，因为它天然属于宿主侧编译时依赖；
- 对外 API 和内部 FFI API 分开，前者服务工程可维护性，后者服务真实互操作；
- 目录结构尽量同时让 C 工程开发者和 Rust 工程开发者都能快速定位代码；
- 如果测试依赖完整系统运行时，就让系统构建工具负责集成测试；Cargo 更适合跑纯 Rust lint、格式化、文档和部分单元测试；

其中最重要的一条其实是：

- 不要为了“让 Rust 看起来更纯”而破坏整个工程原本已经稳定的构建和发布模型；

在混合工程里，真正高质量的 Rust 接入，往往不是“Cargo 感最强”的那种，而是：

- Rust 层获得了足够好的类型安全和开发体验；
- 同时又不强迫整个大工程为它推倒重来；

一个更通用的推荐目录模板
^^^^^^^^^^^^^^^^^^^^^^^^^^

如果以后自己设计一套类似 QEMU 的 C/Rust 混合工程，一个比较稳妥的模板可以是：

.. code-block:: text

    hybrid-project/
    |- meson.build
    |- include/
    |- src/
    |- subsystems/
    |- rust/
    |  |- Cargo.toml
    |  |- meson.build
    |  |- bindings/
    |  |- core-sys/
    |  |- core-api/
    |  |- macros/
    |  |- modules/
    |  |  |- device-a/
    |  |  `- device-b/
    |  `- tests/
    |- generated/
    `- subprojects/

对应职责大致可以约定为：

- ``include/`` 、 ``src/`` 、 ``subsystems/``: C 主体和现有子系统；
- ``rust/bindings/``: bindgen 配置、wrapper header、生成参数脚本；
- ``rust/*-sys`` 或等价目录：原始 FFI 边界；
- ``rust/*-api``: 安全包装与高层抽象；
- ``rust/macros``: proc-macro；
- ``rust/modules/*``: 真正的业务/设备/后端实现；
- ``subprojects/``: 需要被系统构建工具显式认识的第三方依赖；

这类模板最重要的不是目录名字本身，而是目录背后的层次关系：

- 原始绑定不要和业务实现混在一起；
- 宏 crate 不要和普通目标侧库混在一起；
- 系统构建工具需要知道的第三方依赖，要有明确落点；
- 生成代码和手写代码尽量分开；

.. note::

    QEMU 这类工程最值得借鉴的，不是它用了哪些具体 crate 名字，而是它把问题拆成了几层：
    主构建系统负责最终产物，Cargo 负责 Rust 子世界，绑定层和业务层分离，proc-macro 单独隔离，
    目录结构尽量保持和原 C 工程的子系统语义一致。
