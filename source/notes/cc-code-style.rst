C++ 编程风格
==============

谷歌C++编程风格
-----------------

- https://google.github.io/styleguide/cppguide.html
- https://zh-google-styleguide.readthedocs.io/en/latest/google-cpp-styleguide/index.html

已有项目建议保持项目的风格，保持命名风格一致性比具体用哪种风格更重要。新项目(可参考谷歌编程风格)：
  
  - 类型名： ``UpperCamelCase``
  - 普通函数名： ``UpperCamelCase``
  - 类成员函数： ``UpperCamelCase``
  - 普通变量名： ``snake_case``
  - struct成员变量： ``snake_case``
  - class成员变量： ``snake_case_``
  - 常量名： ``kUppperCamelCase``
  - 枚举名： ``kUpperCamelCase`` ， 这个类似常量
  - 缩进：统一两个空格，而 ``public/private/protected`` 缩进一个空格
  - 缩写处理：缩写按单词处理，例如 HttpServer 而不是 HTTPServer
  - 布尔变量：用 ``is_ / has_ / can_ / should_`` 前缀，例如 is_valid，而不是 validFlag
  - 文件命名：一律 ``snake_case``
  - 命名空间：禁止头文件用 ``using namespace``, 在 ``.cc`` 文件中可以使用命名空间别名 ``namespace foo = my_project::foo; ``
  - 禁止使用宏定义常量（#define），用 ``constexpr`` 或 ``const`` 代替
  - 单行注释用 ``//``
  - 类、函数、复杂逻辑前建议加简短注释，说明用途而不是实现细节
  - 指针和引用的靠近： ``char* ptr``（星号靠近类型）， ``const std::string& name``（引用符号靠近类型）
  - 头文件保护： ``#ifndef/#define/#endif`` 形式的 include guard，或 ``#pragma once``
  - 函数参数: 输入参数在前，输出参数在后；尽量使用返回值而不是输出参数
  - 类成员顺序： public → protected → private，并且每个区域内部按类型分组（类型别名、常量、构造/析构、方法、数据成员）
  - 优先使用 ``std::unique_ptr`` / ``std::shared_ptr``，避免裸 ``new/delete``
  - 头文件顺序： 自己的 .h → C 系统库 → C++ 标准库 → 其他库 → 本项目其他头文件。每组之间空一行
  - 不鼓励使用异常（throw），推荐返回 Status 或 bool
  - 行宽还是推荐 80

.. note::

  https://google.github.io/styleguide/cppguide.html#Function_Names

  - 大多数函数名：遵循UpperCamelCase，即每个单词的首字母都大写，例如 ``CalculatePrice()``
  - 存取器（Getter/Setter）：可以作为特例，使用 snake_case。例如， ``int count()`` 或 ``int get_count()``

  https://google.github.io/styleguide/cppguide.html#Variable_Names

  - 普通变量：The names of variables (including function parameters) and data members are ``snake_case``，包括了
    全局变量等，谷歌不规矩全局作用域的全局变量，推荐用 class内部的static变量或者namespace中的全局变量。PS: 如果确实是有
    这个变量，我个人觉得可以加个 ``g_`` 前缀，很好的一眼区分和普通变量。
  - 类成员变量： Data members of classes, both static and non-static, 和普通变量一样, 但是 **下划线结尾**，对
    于static **constant** class members例外;
  - 结构体成员变量： Data members of structs, both static and non-static, 和普通变量一样, 也没有下划线结尾；
  
  https://google.github.io/styleguide/cppguide.html#Constant_Names

  Variables declared ``constexpr`` or ``const``, and whose value is fixed for the duration of the program, are named 
  with a leading ``"k"`` followed by ``mixed case``， such as ``kUpperCamelCase``. Underscores can be used as separators 
  in the rare cases where capitalization cannot be used for separation.

  https://google.github.io/styleguide/cppguide.html#Enumerator_Names

  Enumerators (for both scoped and unscoped enums) should be named like constants, not like macros. 
  That is, use ``kEnumName`` not ENUM_NAME. such as ``kOk = 0, kOutOfMemory,`` .

  https://google.github.io/styleguide/cppguide.html#Namespace_Names

  Namespace names are ``snake_case`` (all lowercase, with underscores between words). 在头文件中，
  当你在命名空间外使用该命名空间里的东西时，必须使用完整的命名空间名。因为在头文件中，使用不完整的命名空间
  别名（例如 using namespace some_namespace;）是被严格禁止的。因为会直接被其他 .cc 文件导入了这个。

    - 完整限定（fully qualified）：指使用完整的命名空间路径，比如 ``google::protobuf::Message`` 。
    - 不完整别名（unqualified aliases）：指像 ``using namespace std;`` 这样的语句。它会把整个命名空间的内容导入到当前作用域，
      这在头文件中是危险的，因为它可能导致包含该头文件的其他代码文件出现意外的命名冲突。

项目举例参考:

.. code-block:: cpp

  // see: 类成员函数名, 普通变量名, 类成员变量名, 常量名, 类型名
  // @file: https://github.com/google/googletest/blob/main/googletest/src/gtest-filepath.cc
  const char kPathSeparator = '/';
  FilePath FilePath::RemoveExtension(const char* extension) const {
    const std::string dot_extension = std::string(".") + extension;
    if (String::EndsWithCaseInsensitive(pathname_, dot_extension)) {
      return FilePath(
          pathname_.substr(0, pathname_.length() - dot_extension.length()));
    }
    return *this;
  }

  // see: 普通函数命名，变量名
  // @file: https://github.com/google/googletest/blob/main/googletest/src/gtest-typed-test.cc
  static const char* SkipSpaces(const char* str) {
    while (IsSpace(*str)) str++;
    return str;
  }

  // see: 函数名，变量名
  // @file: https://chromium.googlesource.com/chromium/src/+/refs/heads/main/cc/scheduler/begin_frame_tracker.cc
  bool BeginFrameTracker::HasLast() const {
    DCHECK(HasFinished())
        << "Tried to use last viz::BeginFrameArgs before the frame is finished.";
    return current_args_.IsValid();
  }

  // see: public 缩进 1 个空格
  // @file: https://github.com/google/googletest/blob/main/googletest/test/production.h
  class PrivateCode {
   public:
    // Declares a friend test that does not use a fixture.
    FRIEND_TEST(PrivateCodeTest, CanAccessPrivateMembers);

    // Declares a friend test that uses a fixture.
    FRIEND_TEST(PrivateCodeFixtureTest, CanAccessPrivateMembers);

    PrivateCode();

    int x() const { return x_; }

   private:
    void set_x(int an_x) { x_ = an_x; }
    int x_;
  };

  // see: 命名空间的行首无所进，结尾出用注释来显示的指出闭合的是哪个 namespace
  // @file: https://chromium.googlesource.com/chromium/src/+/refs/heads/main/cc/scheduler/scheduler.h
  namespace perfetto {
  namespace protos {
  namespace pbzero {
  class ChromeCompositorSchedulerStateV2;
  }
  }  // namespace protos
  }  // namespace perfetto

.. note::

  Google 风格将 函数和类型 都归为 ``UpperCamelCase`` ，这种做法使得代码库中的所有“可调用实体”（函数和类型构造函数）都以大写开头，形
  成了一种视觉上的统一。
  
  同时使用 ``UpperCamelCase`` 和 ``lowerCamelCase``，有时候可能会让人混淆。Google 风格通过将规则简化为两种主要
  风格 (``UpperCamelCase`` 和 ``snake_case``)，并且每种风格都有明确的用途，从而避免了这种混淆。

  When Google's large-scale C++ projects include a small amount of C code, the C code itself will 
  follow the ``snake_case`` naming convention because that's the standard style for the C language community.

C++ Core Guidelines
---------------------

是目前最权威、最受推崇的 C++ 指南之一。它由 C++ 之父 Bjarne Stroustrup 和其他 C++ 专家共同维护。它的目标不是为了统一
代码格式（比如缩进），而是为了指导开发者如何编写更现代、更安全、更高效的 C++ 代码。

https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#c-core-guidelines

对于命名规则的建议：Rationale: Consistency in naming and naming style increases readability. 就是统一就好。

https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rl-name

LLVM Coding Standards
-----------------------

LLVM关于命名风格相关：

https://llvm.org/docs/CodingStandards.html#the-low-level-issues

LLVM 命名风格如下：

- 类型名： UpperCamelCase, (including classes, structs, enums, typedefs, etc), 并且是名词；
- 变量名： UpperCamelCase， 应该是名词，因为表示的是状态；
- 函数名： lowerCamelCase， 应该是动词短语；
- Enum declarations (e.g. enum Foo {...}) are types, 同类型也是 UpperCamelCase;
- Enumerators (e.g. enum { Foo, Bar }) and public member 也是 UpperCamelCase；

.. note::

  - LLVM对于变量的命名是 UpperCamelCase, 这个我不太习惯，还是倾向于谷歌的 snake_case, 或者有时候个人也倾向 lowerCamelCase, QT的也是 lowerCamelCase
  - LLVM对函数的命名是 lowerCamelCase, 这个QT也是 lowerCamelCase, 但是谷歌、虚幻引擎的是 UpperCamelCase, C社区都是 snake_case, 我经常混用 :)

这个是QT的风格说明： https://wiki.qt.io/Qt_Coding_Style

C Coding Standards
---------------------

- https://www.kernel.org/doc/html/v4.10/process/coding-style.html
- https://qemu-project.gitlab.io/qemu/devel/style.html#naming

风格如下：

- 变量名： 基本一律 snake_case
- 函数名： 基本一律 snake_case
- 类型名： 
    - QEMU 的结构体命名是 UpperCamelCase
    - linux 的结构体命名是 snake_case, 如果用了 typedef 会用 ``_t`` 后缀

使用clang-format
---------------------

一致性最重要，过时的匈牙利前缀命名法要避免。其他的都是个人习惯，新项目达成内部团队一致。个人倾向于谷歌的风格。

使用 clang-format 十分方便，而且 clang-format 内置了 Google Style，可以添加下面的头文件：

https://github.com/google/googletest/blob/main/.clang-format

内容：

.. code-block:: yaml

    # Run manually to reformat a file:
    # clang-format -i --style=file <file>
    Language:        Cpp
    BasedOnStyle:  Google

查看详细内容可以:

.. code-block:: bash

    clang-format --style=Google --dump-config


在项目的根目录下放一个 clang-format 文件即可，也可以基于这个少量定制，比如适当的放宽行宽放到 100 等。可用下面的定制：

.. code-block:: yaml

    Language:        Cpp
    BasedOnStyle:  Google

    # 最大行宽 100 (谷歌默认80)
    ColumnLimit:     100

    # 函数后面的 { 换行 (谷歌默认不换行)
    BreakBeforeBraces: Custom
    BraceWrapping:
      AfterFunction: true
    
    # 缩进4个空格 （谷歌默认2个空格）
    IndentWidth: 4
    # public/private/protected 缩进2个，把上面缩进2个，如果-4就是不缩进（谷歌默认缩进1个）
    AccessModifierOffset: -2

上面就是自定义少量修改的 style 了。