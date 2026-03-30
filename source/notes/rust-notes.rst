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

函数与返回值
============

返回值语法
----------

Rust 函数签名里的返回值，写在参数列表后面的 ``->`` 后面。例如：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

这里的含义很直接：

- ``fn`` 表示函数定义；
- ``add(a: i32, b: i32)`` 是函数名和参数列表；
- ``-> i32`` 表示这个函数返回 ``i32`` 类型的值。

如果函数签名里没有写 ``->`` ，那它的返回类型就是 ``()`` ，也就是 unit type。例如：

.. code-block:: rust

    fn log_msg() {
        println!("hello");
    }

这等价于：

.. code-block:: rust

    fn log_msg() -> () {
        println!("hello");
    }

``()`` 是什么
-------------

``()`` 叫 unit type，可以理解成“空值类型”或“没有有意义返回值”的类型。它只有一个值，也写作 ``()`` 。

这和 C/C++ 的 ``void`` 有点像，但并不完全一样：

- C/C++ 的 ``void`` 更像“没有值”；
- Rust 的 ``()`` 是一个真实存在的类型，而且它确实有一个值。

所以 Rust 里“没有返回值”这件事，更准确地说是“返回 unit type”。

表达式与返回
------------

Rust 是表达式导向语言，函数体最后一个没有分号的表达式，通常就会成为返回值。例如：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

这里 ``a + b`` 后面没有分号，所以它是函数的返回值。

如果写成：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b;
    }

那就不对了，因为分号会把表达式变成语句；这个函数体最后就只剩下 ``()`` ，和 ``i32`` 返回类型不匹配。

当然，Rust 也支持显式 ``return`` ：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        return a + b;
    }

但日常更常见的写法，通常是让最后一个表达式自然返回。

Result 与错误传播
-----------------

Rust 日常错误处理不是靠 C++ 那种通用异常机制，而是显式返回 ``Result<T, E>`` 。

例如：

.. code-block:: rust

    fn parse_num(s: &str) -> Result<i32, std::num::ParseIntError> {
        s.parse()
    }

这里：

- ``T`` 是成功时的值类型；
- ``E`` 是失败时的错误类型；
- ``Result<i32, ParseIntError>`` 表示“要么得到一个 ``i32`` ，要么得到一个解析错误”。

这种设计的关键点是：错误被放进类型系统，而不是像异常那样隐式穿透控制流。

``anyhow::Result<()>`` 是什么
-----------------------------

工程代码里经常能看到：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        Ok(())
    }

这里要拆成两层理解：

- ``()`` 表示成功时没有额外返回值；
- ``anyhow::Result<T>`` 是 ``anyhow`` crate 提供的一个类型别名。

它大致等价于：

.. code-block:: rust

    fn main() -> Result<(), anyhow::Error> {
        Ok(())
    }

也就是说， ``anyhow::Result<()>`` 本质上还是一个普通的 ``Result<T, E>`` ，只是把错误类型固定成了
``anyhow::Error`` ，写起来更短，也更适合应用层快速汇总各种错误。

为什么 ``main`` 可以返回 ``Result``
------------------------------------

很多人第一次看到下面这种写法会奇怪：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        run()?;
        Ok(())
    }

因为在 C/C++ 心智里， ``main`` 往往直接返回整数退出码。

Rust 这里更一般化一些： ``main`` 并不只允许返回整数或 ``()`` ，它可以返回一个实现了
``std::process::Termination`` 的类型。 ``Result<(), E>`` 正是其中一种常见情况。

因此：

- 如果 ``main`` 返回 ``Ok(())`` ，程序通常按成功退出；
- 如果返回 ``Err(e)`` ，运行时会把它当成失败处理，并给出对应的退出状态和错误输出。

所以 ``fn main() -> anyhow::Result<()>`` 的工程含义其实很朴素：

- 成功时返回空值；
- 失败时把错误直接往上交给进程退出逻辑。

为什么这样写很常见
------------------

这种写法在工程里很常见，原因主要有三点：

- 可以直接在 ``main`` 里使用 ``?`` 传播错误；
- 不需要手工把每一步错误都 ``match`` 展开；
- 可以让“程序入口逻辑”和“错误退出逻辑”保持很薄。

例如：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        let cfg = load_config()?;
        run_server(cfg)?;
        Ok(())
    }

这里的 ``?`` 含义是：如果左边是 ``Err`` ，就立刻提前返回；如果是 ``Ok`` ，就把里面的成功值取出来继续执行。

对应用程序来说，这种风格通常非常自然，因为入口层本来就只是“调用若干步骤，失败就退出”。

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

.. _rust-std-prelude:

标准库与 Prelude
----------------

很多刚接触 Rust 的人，会看到下面这样的最小程序：

.. code-block:: rust

    fn main() {
        println!("hello");
    }

然后马上产生一个疑问：这里既没有写 ``use`` ，也没有写 ``std::`` ，为什么 ``println!`` 可以直接用。

这里需要把三件事分开：

- 普通 Rust 程序默认会接入标准库，也就是通常会自动有 ``std`` 这个 crate；
- 每个模块会自动拿到一小部分 prelude 名字，但这只是很小的核心子集，不是整个 ``std`` ；
- 像 ``println!`` 这类常用宏，一般也可以直接使用。

所以更准确地说，不是“整个 ``std`` 都默认导入了”，而是“标准库默认接入，同时只有少量常用名字会自动进入作用域”。

prelude 里大致只有最常用的核心类型和 trait，比如 ``Option`` 、 ``Result`` 、 ``Box`` 、 ``Vec`` 、
``String`` 、 ``Clone`` 、 ``Copy`` 、 ``Drop`` 、 ``Default`` 、 ``Iterator`` 、 ``IntoIterator`` 、
``From`` 、 ``Into`` 这类。

但绝大多数标准库内容都不会自动进作用域，比如 ``HashMap`` 、 ``File`` 、 ``TcpStream`` 、 ``Mutex`` 等，
仍然要写完整路径或显式 ``use`` 。

如果切到 ``#![no_std]`` 场景，情况还会进一步变化：这时标准库不会按普通程序那样默认参与进来，能直接使用的名字集合也会随之收缩。

路径与 use
----------

Rust 里的 ``use`` 语句，本质上是在把某个路径对应的名字引入当前作用域。例如：

.. code-block:: rust

    use math::add;

很多人看到这句时，会误以为 ``use`` 路径的第一个单词必须是 crate 名。其实不对。

``use`` 路径的第一个段，常见可以是下面几类：

- 外部 crate 名，例如 ``use math::add;`` ；
- ``crate`` ，表示当前 crate 根，例如 ``use crate::parser::parse;`` ；
- ``self`` ，表示当前模块，例如 ``use self::inner::Foo;`` ；
- ``super`` ，表示父模块，例如 ``use super::config::Config;`` ；
- 当前作用域里已经可见的模块名或条目。

所以更准确地说， ``use`` 路径的第一个词不一定是 crate ；它只需要能在当前名字解析规则下成立即可。

例如：

.. code-block:: rust

    use math::add;              // 外部 crate
    use crate::util::parse;     // 当前 crate 根
    use self::inner::Foo;       // 当前模块
    use super::config::Config;  // 父模块

如果是 ``use math::add;`` 这种写法，那么 ``math`` 往往表示一个外部 crate 名。但它之所以能这样写，
不是因为 ``use`` 的语法强制第一个词必须是 crate，而是因为在当前编译环境里， ``math`` 这个名字正好被解析成了一个外部 crate 。

.. _rust-attributes:

Attribute 语法
--------------

Rust 里经常会看到以 ``#`` 开头的写法，例如：

.. code-block:: rust

    #[cfg(test)]
    #[derive(Debug, Clone)]
    #[allow(dead_code)]

    fn foo() {}

或者：

.. code-block:: rust

    #![no_std]

这类语法统一叫 attribute。它不是 C/C++ 预处理器那种文本替换，而是附着在 crate、模块、函数、
结构体、字段、trait、impl 等条目上的编译期元信息或指令。

两种基本形式
^^^^^^^^^^^^

attribute 最基本有两种写法：

- ``#[xxx]``: 外层属性，作用到后面的那个条目；
- ``#![xxx]``: 内层属性，作用到当前包围它的整体，最常见是整个 crate 或整个模块。

例如：

.. code-block:: rust

    #[derive(Debug)]
    struct User {
        id: u64,
    }

这里 ``#[derive(Debug)]`` 是作用在 ``User`` 这个结构体上的外层属性。

.. code-block:: rust

    #![no_std]

这里 ``#![no_std]`` 是 crate 级内层属性，作用对象是整个 crate。

attribute 在做什么
^^^^^^^^^^^^^^^^^^

从工程理解上，attribute 大致在做下面几类事情：

- 条件编译：决定某些代码在当前构建条件下要不要进入编译图；
- 代码生成：让编译器或宏系统自动生成部分实现；
- lint 控制：告诉编译器某些告警该报、忽略或提升为错误；
- crate/module 配置：调整整个 crate 或模块的编译方式与语言行为；
- 测试/文档/链接相关标记：给工具链额外语义。

也就是说，attribute 不是“运行时注解”，而是编译期语义的一部分。

常见种类
^^^^^^^^

工程里最常见的 attribute 可以大致分成下面几类。

1. 条件编译

.. code-block:: rust

    #[cfg(test)]
    mod tests {}

    #[cfg(target_os = "linux")]
    fn platform_init() {}

这类 attribute 告诉编译器：只有满足某些条件时，这段代码才参与当前编译。

2. 派生实现

.. code-block:: rust

    #[derive(Debug, Clone, PartialEq)]
    struct Point {
        x: i32,
        y: i32,
    }

这类写法最常见于结构体和枚举，表示自动生成一些标准 trait 的实现。

3. lint 控制

.. code-block:: rust

    #[allow(dead_code)]
    fn helper() {}

    #[warn(unused_variables)]
    fn demo() {
        let x = 1;
    }

这类 attribute 用来控制告警策略。常见的有 ``allow`` 、 ``warn`` 、 ``deny`` 、 ``forbid`` 。

4. crate 级配置

.. code-block:: rust

    #![no_std]
    #![allow(unused_imports)]

这类属性通常写在 crate root 顶部，影响整个 crate。

5. 测试相关

.. code-block:: rust

    #[test]
    fn works() {}

    #[should_panic]
    fn must_fail() {
        panic!("boom");
    }

这类属性告诉测试 harness：哪个函数是测试，测试是否预期 panic。

6. 表示布局或 FFI 语义

.. code-block:: rust

    #[repr(C)]
    struct Header {
        len: u32,
        kind: u32,
    }

这类属性常用于和 C ABI、内存布局、枚举表示方式相关的场景。

``cfg`` 和 C/C++ 宏的区别
^^^^^^^^^^^^^^^^^^^^^^^^^^

很多 C/C++ 背景的人会把 ``#[cfg(...)]`` 立刻类比成 ``#ifdef`` ，这个类比只能算一半对。

共同点是：

- 两者都能根据条件决定某段代码是否参与当前构建。

但关键差异是：

- ``#ifdef`` 是预处理器做文本替换，发生在真正编译前；
- ``#[cfg(...)]`` 是 Rust 编译器理解的条件编译，不是简单文本替换；
- 它控制的是“某个 item 是否进入当前编译图”，而不是“先把哪段源代码文本展开出来”。

因此 Rust 的 ``cfg`` 往往比 C/C++ 宏条件编译更结构化，也更不容易把代码切得支离破碎。

你应该优先记住什么
^^^^^^^^^^^^^^^^^^^^

如果先不追求完整，最值得先记住的是：

- ``#[xxx]`` 作用在后面的条目；
- ``#![xxx]`` 作用在当前模块或整个 crate；
- ``#[cfg(...)]`` 控制条件编译；
- ``#[derive(...)]`` 让编译器或宏系统自动生成实现；
- ``#[allow/warn/deny/forbid(...)]`` 控制 lint；
- ``#[test]`` / ``#[should_panic]`` 服务测试；
- ``#[repr(C)]`` 常用于 FFI 与内存布局。

把这些最常见的看熟之后，再去接触更细的 attribute 家族，例如宏属性、文档属性、链接属性、
稳定性属性，就会容易很多。
