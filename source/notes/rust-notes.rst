.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 0.1

Rust 语言特性
*************

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

