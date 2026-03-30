.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 0.2

Rust 语言笔记
*************

安全模型
========

Rust 的很多语法和工程习惯，最终都可以追到它的安全模型。粗看起来点很多，实际可以压缩成三组。

内存与生命周期
--------------

- Ownership: 每个值在任意时刻只有一个 owner；owner 负责生命周期，离开作用域时自动 drop；
- Move: 默认是 move 语义而不是 copy；值被 move 后，原变量立即失效；
- Borrowing: 同一数据在同一时刻只能多 ``&T`` 或者单 ``&mut T`` ，也就是
  Aliasing XOR Mutability；
- Lifetimes: 所有引用都带生命周期约束，编译器据此保证
  lifetime(ref) ≤ lifetime(data)；
- Unsafe: 编译器无法直接证明安全的操作，例如裸指针、FFI、手动内存管理，必须显式放入
  ``unsafe`` 边界。

状态与控制流
------------

- ADT: 用 ``enum`` 和 ``struct`` 精确表达状态空间，减少 null、非法状态和遗漏分支；
- Match: ``match`` 必须穷尽所有可能分支，控制流更完整；
- Result: 错误通过 ``Result<T, E>`` 显式进入类型系统，而不是像异常那样隐式传播。

类型与并发
----------

- Type System: 类型系统用于表达不变量，让非法状态尽量在编译期不可表示；
- Send / Sync: 并发安全通过 trait 和借用规则建模，目标是把数据竞争尽量前移到编译期；
- Interior Mutability: 某些共享但可变的模式，不靠放松规则，而靠更显式的类型包装。

ADT
---

Algebraic Data Type，代数数据类型，意思是类型可以像代数一样组合。最核心的两种组合方式是：

- Sum: 多个候选分支里选一个，总可能性是各分支之和，例如 ``enum`` ；
- Product: 多个字段组合在一起，总可能性是各字段组合的乘积，例如 ``struct`` 和 tuple。

在内存模型上，Rust 的 ``enum`` 常常可以理解成 tag + payload 的 tagged union：tag 表示当前是
哪个分支，payload 放具体数据。编译器还会做布局优化，不一定总是最朴素的“标签 + 最大 payload 空间”形式。

函数
====

返回值
------

Rust 函数签名里的返回值写在参数列表后的 ``->`` 后面。例如：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

这里：

- ``fn`` 表示函数定义；
- ``add(a: i32, b: i32)`` 是函数名和参数列表；
- ``-> i32`` 表示返回 ``i32`` 类型的值。

如果函数签名里没有写 ``->`` ，那返回类型就是 ``()`` 。

Unit
----

``()`` 叫 unit type，可以理解成“空值类型”。它只有一个值，也写作 ``()`` 。

这和 C/C++ 的 ``void`` 有点像，但不完全一样：

- C/C++ 的 ``void`` 更像“没有值”；
- Rust 的 ``()`` 是一个真实存在的类型，而且确实有一个值。

所以 Rust 里“没有有意义返回值”，更准确的说法通常是“返回 unit type”。

表达式
------

Rust 是表达式导向语言。函数体最后一个没有分号的表达式，通常就是返回值。例如：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

这里 ``a + b`` 没有分号，所以它作为函数返回值。

如果写成：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        a + b;
    }

那就不对，因为分号会把表达式变成语句；函数体最后只剩 ``()`` ，和 ``i32`` 不匹配。

Rust 当然也支持显式 ``return`` ：

.. code-block:: rust

    fn add(a: i32, b: i32) -> i32 {
        return a + b;
    }

但更常见的写法，是让最后一个表达式自然返回。

Result
------

Rust 日常错误处理不是依赖 C++ 那种通用异常机制，而是显式返回 ``Result<T, E>`` 。

例如：

.. code-block:: rust

    fn parse_num(s: &str) -> Result<i32, std::num::ParseIntError> {
        s.parse()
    }

这里：

- ``T`` 是成功时的值类型；
- ``E`` 是失败时的错误类型；
- ``Result<i32, ParseIntError>`` 表示“要么得到一个 ``i32`` ，要么得到一个解析错误”。

这种设计的关键点是：错误被放进类型系统，而不是隐式穿透控制流。

Main
----

工程代码里经常能看到：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        Ok(())
    }

这里要拆开看：

- ``()`` 表示成功时没有额外返回值；
- ``anyhow::Result<T>`` 是 ``anyhow`` crate 提供的类型别名；
- 它本质上仍然是普通的 ``Result<T, E>`` 。

大致可以理解成：

.. code-block:: rust

    fn main() -> Result<(), anyhow::Error> {
        Ok(())
    }

为什么 ``main`` 能这样写？因为 Rust 的 ``main`` 不只允许返回整数或 ``()`` ，它可以返回实现了
``std::process::Termination`` 的类型。 ``Result<(), E>`` 正是很常见的一种。

所以：

- ``Ok(())`` 通常表示成功退出；
- ``Err(e)`` 会被运行时当成失败处理。

这也是为什么应用入口经常写成：

.. code-block:: rust

    fn main() -> anyhow::Result<()> {
        let cfg = load_config()?;
        run_server(cfg)?;
        Ok(())
    }

这里 ``?`` 的含义是：如果左边是 ``Err`` ，就立刻提前返回；如果是 ``Ok`` ，就取出成功值继续执行。

名字解析
========

.. _rust-std-prelude:

Prelude
-------

很多人第一次看到下面的程序会奇怪：

.. code-block:: rust

    fn main() {
        println!("hello");
    }

为什么这里既没有写 ``use`` ，也没有写 ``std::`` ， ``println!`` 却可以直接用？

这里最好拆成三件事：

- 普通 Rust 程序默认会接入标准库，也就是通常会自动有 ``std`` 这个 crate；
- 每个模块会自动拿到一小部分 prelude 名字，但这只是一个很小的核心子集；
- 像 ``println!`` 这类常用宏，通常也可以直接使用。

所以更准确地说，不是“整个 ``std`` 都默认导入了”，而是“标准库默认接入，同时只有少量常用名字自动进作用域”。

prelude 里大致只有最常用的核心类型和 trait，例如 ``Option`` 、 ``Result`` 、 ``Box`` 、 ``Vec`` 、
``String`` 、 ``Clone`` 、 ``Copy`` 、 ``Drop`` 、 ``Default`` 、 ``Iterator`` 、 ``IntoIterator`` 、
``From`` 、 ``Into`` 这类。

但绝大多数标准库内容都不会自动进作用域，例如 ``HashMap`` 、 ``File`` 、 ``TcpStream`` 、
``Mutex`` 等，仍然要写完整路径或显式 ``use`` 。

如果切到 ``#![no_std]`` 场景，情况还会进一步变化：标准库不会按普通程序那样默认参与进来，可直接使用的名字集合也会随之收缩。

Use
---

Rust 里的 ``use`` 语句，本质上是在把某个路径对应的名字引入当前作用域。例如：

.. code-block:: rust

    use math::add;

很多人看到这句时，会误以为 ``use`` 路径的第一个词必须是 crate 名。其实不对。

``use`` 路径的第一个段，常见可以是下面几类：

- 外部 crate 名，例如 ``use math::add;`` ；
- ``crate`` ，表示当前 crate 根，例如 ``use crate::parser::parse;`` ；
- ``self`` ，表示当前模块，例如 ``use self::inner::Foo;`` ；
- ``super`` ，表示父模块，例如 ``use super::config::Config;`` ；
- 当前作用域里已经可见的模块名或条目。

所以更准确地说， ``use`` 路径的第一个词不一定是 crate；它只需要能在当前名字解析规则下成立即可。

例如：

.. code-block:: rust

    use math::add;              // 外部 crate
    use crate::util::parse;     // 当前 crate 根
    use self::inner::Foo;       // 当前模块
    use super::config::Config;  // 父模块

如果是 ``use math::add;`` 这种写法，那么 ``math`` 往往表示一个外部 crate 名。但它之所以能这样写，
不是因为 ``use`` 的语法强制第一个词必须是 crate，而是因为当前编译环境里， ``math`` 这个名字正好被解析成了外部 crate 。

.. _rust-attributes:

Attribute
---------

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

形式
^^^^

attribute 最基本有两种写法：

- ``#[xxx]``: 外层属性，作用到后面的条目；
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

用途
^^^^

从工程理解上，attribute 大致在做下面几类事情：

- 条件编译；
- 代码生成；
- lint 控制；
- crate/module 配置；
- 测试、文档、链接相关标记。

也就是说，attribute 不是“运行时注解”，而是编译期语义的一部分。

分类
^^^^

最常见的 attribute 大致可以分成下面几类。

1. 条件编译

.. code-block:: rust

    #[cfg(test)]
    mod tests {}

    #[cfg(target_os = "linux")]
    fn platform_init() {}

2. 派生实现

.. code-block:: rust

    #[derive(Debug, Clone, PartialEq)]
    struct Point {
        x: i32,
        y: i32,
    }

3. lint 控制

.. code-block:: rust

    #[allow(dead_code)]
    fn helper() {}

    #[warn(unused_variables)]
    fn demo() {
        let x = 1;
    }

常见的 lint 级别有 ``allow`` 、 ``warn`` 、 ``deny`` 、 ``forbid`` 。

4. crate 级配置

.. code-block:: rust

    #![no_std]
    #![allow(unused_imports)]

5. 测试相关

.. code-block:: rust

    #[test]
    fn works() {}

    #[should_panic]
    fn must_fail() {
        panic!("boom");
    }

6. 布局与 FFI

.. code-block:: rust

    #[repr(C)]
    struct Header {
        len: u32,
        kind: u32,
    }

``#[repr(C)]`` 这类属性常用于 C ABI、内存布局和枚举表示方式相关场景。

Cfg
^^^

很多 C/C++ 背景的人会把 ``#[cfg(...)]`` 立刻类比成 ``#ifdef`` ，这个类比只能算一半对。

共同点是：

- 两者都能根据条件决定某段代码是否参与当前构建。

关键差异是：

- ``#ifdef`` 是预处理器做文本替换，发生在真正编译前；
- ``#[cfg(...)]`` 是 Rust 编译器理解的条件编译，不是简单文本替换；
- 它控制的是“某个 item 是否进入当前编译图”，而不是“先把哪段源代码文本展开出来”。

因此 Rust 的 ``cfg`` 往往比 C/C++ 宏条件编译更结构化，也更不容易把代码切得支离破碎。

编译模型
========

Rust 的编译单元、crate root、产物类型、metadata、链接和 CGU，更适合和工程组织一起看。
这些内容可参见 :ref:`rust-engineering-compile` 。
