.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.1

C/C++笔记
***********

C++11/14/17/20 实用特性
=======================

C++11 实用特性
--------------------

- 就地初始化，直接在类内对成员变量进行初始化，简化构造函数， {} 可避免窄化转换, 不涉及窄化转换时可用 ``=`` 进行初始化。
- 统一初始化，使用花括号 ``{}`` 进行初始化，避免了窄化转换，可以初始化数组、容器和类对象。
- 模板变长参数，允许模板接受任意数量和类型的参数，增强了模板的灵活性和可扩展性。
- 模板别名，使用 ``using`` 关键字为模板类型创建别名，简化了复杂类型的使用和阅读。
- 右值引用和移动语义，允许资源的高效转移，减少不必要的拷贝，提高性能。
- 智能指针 ``unique_ptr、shared_ptr、weak_ptr``, 提供自动内存管理，防止内存泄漏和悬空指针。
- ``constexpr`` 允许在编译时计算常量表达式，提高性能和代码的安全性。
- ``override`` 和 ``final`` 关键字，增强了类的继承和多态的安全性和可读性。
- 默认和删除的函数，允许显式地指定类的特殊成员函数的行为，简化了类的设计和实现。
- 委托构造函数，允许一个构造函数调用另一个构造函数，减少代码重复，提高代码的可维护性。
- ``auto`` 关键字，允许编译器自动推导变量的类型，简化了代码的编写和阅读。
- ``for range`` 循环，简化了对容器和数组的遍历，提高了代码的可读性。
- ``nullptr`` 关键字，提供了类型安全的空指针，避免了传统的 NULL 宏带来的问题。
- 强类型枚举，使用 ``enum class`` 定义枚举类型，避免了枚举值的隐式转换和命名冲突。
- 静态断言，使用 ``static_assert`` 在编译时检查条件，提高代码的安全性和正确性。
- 多线程支持，提供了线程、互斥锁、条件变量等多线程编程的基础设施，简化了并发编程。
- 字符串转换函数，提供了更方便和安全的字符串转换函数，如 ``std::to_string`` 和 ``std::stoi``。
- 正则表达式库 ``<regex>`` ，提供了强大的字符串模式匹配和处理功能。
- 时间库 ``<chrono>`` ，提供高精度计时和时间段处理功能。

C++14 实用特性
--------------------

- 函数返回值类型推导，允许编译器自动推导函数的返回类型，简化了函数的定义和阅读。
- ``lambda`` 参数类型可用 auto 推导, 使得lambda更加的强大和灵活。
- ``lambda`` 支持初始化捕获（init-capture），允许 lambda 表达式捕获变量时使用移动语义，增强了 lambda 的性能和安全性。
- 变量模板，允许定义模板变量，简化了常量和静态变量的使用。如： ``template<typename T> constexpr T pi = T(3.14159);``
- ``constexpr`` 增强，允许在 constexpr 函数中使用更多的语句和控制结构，增强了编译时计算的能力。
- ``std::make_unique``，提供了一种安全和简洁的方式来创建 ``std::unique_ptr``，避免了手动使用 new 关键字。
- ``std::shared_timed_mutex``，共享定时互斥锁，允许多个线程同时读取，但只有一个线程可以写入，提高了并发性能，有超时功能。
- ``std::shared_lock``，配合 ``shared_mutex/shared_timed_mutex`` 使用的 RAII 读锁​。
- ``std::integer_sequence``，提供了一种编译时整数序列，简化了模板元编程和参数包展开。
- 二进制字面量，允许使用二进制格式表示整数，增强了代码的可读性和表达能力。如： ``0b1010`` 表示十进制的 10
- 数字分隔符，允许在数字字面量中使用单引号作为分隔符，增强了大数字的可读性。如： ``1'000'000`` 表示一百万。

C++17 实用特性
--------------------

- 结构化绑定，允许将结构体或元组的成员直接绑定到多个变量，简化了代码的编写和阅读，如：方便遍历 ``map/pair`` 等。
- ``if/switch`` 语句中的初始化，允许在 ``if`` 或 ``switch`` 语句中声明和初始化变量，增强了变量的作用域和可读性。
- 内联变量，允许在头文件中定义变量而不会导致重复定义错误，简化了常量和静态变量的使用，如 ``inline int global_var = 42``;
- 类模板参数推导，允许编译器自动推导构造函数模板的参数类型，简化了模板类的使用和实例化。
- 折叠表达式，允许对参数包进行递归操作，简化了模板元编程和参数包展开。
- 嵌套命名空间namespace定义简写，简化了命名空间的组织和管理。
- ``[[nodiscard]], [[maybe_unused]], [[fallthrough]]`` 等属性，增强了代码的安全性和可读性。
- ``std::variant``，提供了一种类型安全的联合体，可以存储不同类型的值，增强了类型的灵活性和安全性, 里面可以有string等复杂类型。
- ``std::optional``，表示一个可能包含值也可能不包含值的对象，简化了可选值的处理和检查。
- ``std::any``，提供了一种类型安全的容器，可以存储任意类型的值，增强了类型的灵活性和安全性。
- ``std::apply``，允许将函数应用于参数包，简化了函数调用和参数传递。
- ``std::make_from_tuple``，允许从元组创建对象，简化了对象的构造和初始化。
- ``std::string_view``，提供了一种轻量级的字符串视图，避免了不必要的字符串拷贝，提高性能。
- ``std::filesystem``，提供了一套跨平台的文件系统操作接口，简化了文件和目录的管理和操作。
- ``as_const`` 函数，是 <utility> 中的一个函数模板，作用是返回 const T&, 新增的工具函数。
- ``constexpr if`` 在编译期根据条件选择代码分支，避免无效代码实例化，简化模板元编程逻辑。
- ``std::scoped_lock`` C++17 引入的 RAII 锁管理器，可同时安全锁定多个互斥量，避免死锁。

C++20 实用特性
--------------------

- modules，提供了一种新的代码组织和管理方式，替代了传统的头文件和预处理器指令，提高了编译速度和代码的可维护性。
- ranges, 提供了一套新的范围库，简化了对容器和序列的操作和处理，增强了代码的表达能力和可读性。
- concepts，提供了一种新的模板约束机制，增强了模板的类型安全性和可读性。
- coroutines，提供了一种新的异步编程模型，简化了异步代码的编写和管理，提高了代码的可读性和性能。
- lambda 表达式更新，支持使用模板参数，constexpr确认，对 =this 的捕获等。
- constexpr 增强：大量标准库算法和容器操作被标记为 constexpr 使用，更多代码编译期执行。
- std::format ，提供了一种类型安全且灵活的字符串格式化方式，替代了传统的 printf 风格格式化。
- ``<=>`` 三路比较运算符（太空船操作符），简化了自定义类型的比较操作，自动生成所有比较运算符。

class
=====

class keywords
----------------

一些关于class的关键字：

- ``override`` 是一种安全校验，是可选的，你意图是覆盖父类的父方法，那么就会校验父类有没有，函数签名匹配不匹配，编译器拦截低级错误。
- ``final`` 是一种安全校验，是可选的，你的类或者类成员函数不想让人继承就用 ``final`` 修饰。
- ``virtual`` 是必须的，类的成员函数如果想被子类重写，必须是 ``virtual``, 如果一个基类打算被继承，那么它的析构函数必须是虚函数。
  子类中覆盖父类的virtual函数时， ``virtual`` 关键字可选，一般无需再加，建议加上 ``override`` 来明确语义方便编辑器检查。
- ``default`` 这个关键字指定默认特殊成员函数，包括：构造、析构、拷贝构造、拷贝赋值、移动构造、移动赋值。某些特定成员函数的用户
  自定义声明会抑制（阻止）编译器自动生成其他特定的成员函数，但是你还需要，并且编译器默认实现的也满足需求，此时可以使用 ``default``。
- ``delete`` 同样针对上面的特殊类成员函数：构造、析构、移动构造、拷贝构造、赋值运算符等，
  这个关键字可以做到显示的删除，让其不能够被移动，被赋值等，方便后续实现 ``unique_ptr`` 等特性。
- ``explicit`` 关键字，防止单参数构造函数被隐式转换，避免一些低级错误。
- ``mutable`` 关键字，指定类的成员变量可以在 const 成员函数中被修改。
- ``static`` 关键字，指定类的成员变量或成员函数属于类本身，而不是类的某个实例。静态成员变量在所有实例间共享，
  静态成员函数只能访问静态成员变量和其他静态成员函数。

.. note::

  对于 ``=default`` 关键字，注意以下几点:

  1. ​用户声明了自定义的拷贝操作（拷贝构造或拷贝赋值），会抑制移动操作（移动构造和移动赋值）的自动生成。
  2. ​用户声明了自定义的移动操作、析构函数或构造函数，会抑制拷贝操作和移动操作的自动生成。
  3. ​用户声明了任何构造函数（包括拷贝构造、移动构造），会抑制默认构造函数的自动生成。

  对于 ``explicit`` 关键字，除非你有一个非常好的理由允许隐式转换，否则应该尽量为所有的单参构造函
  数（以及除拷贝构造外的多参构造函数）都加上 explicit关键字。这是一种防御编程，不是必须，是为了
  让编程的意图更加的清晰，还有就是可以一定程度的省去临时对象开销。防止的就是这种情况：你本以传递1个参数，
  你并不想传递那个类的对象，但是编译器帮你隐式转换了，导致了低级错误，而编译期无法检测出来。

三/五/零之法则
----------------

https://c-cpp.com/cpp/language/rule_of_three

C++中有一个重要的设计原则，三/五/零之法则：

- 零法则（Rule of Zero）： 现代 C++ 的首选。如果你的类不拥有任何需要手动管理的资源（如裸指针），那么你不需要自定义任何特殊成员函数,
  让编译器自动生成即可。当有意将某个基类用于多态用途时，可能必须将其析构函数声明为公开的虚函数。由于这会阻拦隐式移动（并弃用隐式
  复制）的生成，因而必须将各特殊成员函数声明为预置的。然而这使得类有可能被切片，这是多态类经常把复制定义为弃置的原因。
- 三法则（Rule of Three）： C++98 时代的法则。如果你的类拥有需要手动管理的资源，且你自定义了以下三者中的任何一个，就应该自
  定义所有三个：析构函数、拷贝构造函数和拷贝赋值运算符。
- 五法则（Rule of Five）： C++11 引入移动语义后的扩展。在三法则的基础上，为了支持移动语义，还应该提供 移动构造函数 和 移动赋值运算 符。

.. note::

  黄金准则： 在现代 C++ 中，尽量使用“零法则”。你的类成员应仅由基本类型、智能指针和标准库容器组成。

一个典型的多态积累定义：

.. code-block:: cpp

    class Animal {
     public:
      // 必须有虚析构函数，以支持多态
      virtual ~Animal() = default;

      // 显式禁用复制，以防止对象切片
      Animal(const Animal&) = delete;
      Animal& operator=(const Animal&) = delete;

      // 显式预置移动，如果需要
      // Animal(Animal&&) = default;
      // Animal& operator=(Animal&&) = default;
      
      // 其他虚函数
      virtual void eat() = 0;
  };

移动语义
========

移动语义： 内部资源的转移（比如raw_data指针、文件描述符fd等等)，核心实是实现了移动构造、移动赋值这两个特殊的成员函数和运算符的重载。

右值：右值通常是字面量、临时对象或即将被销毁的对象，如字面量、临时对象、没有被赋值给任何左值的临时对象。这种类型如果
内部实现了移动语义的方法，编译器遇到的时候优先进行移动赋值和和构造，从而减少不必要的资源拷贝，提高效率。

在实现的时候，判断是否是自身对象指针(对象的自赋值移动），转移后raw_data指针置空等。编译器如何识别呢？对于 *右值类型* ，可以
被 ``T&&`` 引用，编译器在遇到构造或者赋值的时候，触发移动语义，即调用对应的移动构造和移动赋值运算符。 ``std::move`` 的本质
是一个类型的转换，告诉编译器，这个是右值类型，可以调用后续移动语义的方法了。

智能指针
==========

有了上面的 C++11 引入的语言特性后，我们就可以用库的方式来实现智能指针了。实现智能指针的语言特性基础（编译器级别的语法）有：

- ``RAII`` 机制，对象生命周期结束自动析构（调用析构函数），典型就是超出作用域自动析构，编译器会帮你调用析构函数；
- ``default/delete``, 方便显示的对赋值构造等特殊成员函数的实现进行控制；
- 移动语义，对于可被 ``T&&`` 引用的类型，编译器编译是会去调用对应的移动构造或者赋值的实现；
- ``class`` 的模板机制，任意类型都可以传给class来进行对应实例的管理；
- 运算符重载，方便智能指针像普通指针一样使用，重载了 ``* ->`` 等指针操作符, 还有 ``operator bool()`` 方便做非空判断；
- 显式构造函数 (``explicit``) 主要用于单参构造函数，避免不必要的隐式转换；

unique_ptr
--------------

它是1个泛型class，传入类型 T 的实例，可以被自动管理，这个unique_ptr只会被1个左值所拥有，确保了在程序的任何一个时间点都是
被唯一的左值拥有所有权。同样，作为指针，它重载了 ``* ->`` 这些指针操作，可以像普通指针一样使用。

实现原理：

- 用 delete 关键字去掉赋值和拷贝构造函数的实现，从而禁止普通的赋值与拷贝；
- 实现移动赋值和移动构造函数，被赋值给其他的时候，要用 ``std::move`` 来显示转移；

注意点：

- ``get`` 方法慎用，这个是获取内部的raw_ptr，我们不要把 ``unique_ptr`` 和裸指针混用；
- ``reset`` 后，重置了uniptre，会显示释放掉原来的数据；
- ``release`` 后，会返回 raw_ptr，后续要自己来管理了，注意避免泄漏，这种方法用的很少；

shared_ptr
----------

是1个泛型class，传入T类型，后续自动管理T类型的实例数据；与前面的 ``unique_ptr`` 不一样的是，它可以同时被多个左值所持有，
内部的 raw_ptr 会有引用计数。

实现原理：

- 实现赋值运算符、赋值构造，在内部会对资源进行引用计数；
- 实现移动构造和移动赋值等，移动语义，不会改变 raw_ptr 引用计数；
- 如果raw_ptr引用计数为0了，释放对应内存资源；

注意点：

- 遇到循环引用，比如父子对象互相引用，那么需要使用 ``weak_ptr`` 辅助；
- 通用不要和通过 ``get`` 方法获取的raw指针混用；

weak_ptr
----------

也是个泛型class，常配合 ``shared_ptr`` 使用，不会导致 ``shared_ptr`` 内部data的引用计数增加，更多的
是一个 *观察* 的模式。因为 ``weak_ptr`` 不参与资源管理，访问前先 ``lock``, 然后会判断是否 ``lock`` 成功
非空指针，然后才能访问其指向的实例。

实现原理：

- ``weak_ptr`` 的赋值和拷贝构造​: 操作的是弱引用计数。它不会增加强引用计数，因此不会阻止所指向的对象被释放。弱引用计数为0时，释放
  用于管理引用计数的*控制块*本身。
- ``shared_ptr`` 的赋值和拷贝构造​: 操作的是强引用计数。强引用计数为0时，释放管理的对象资源。

.. note::

  使用 ``shared_ptr`` 出现循环引用会发生什么，假设有两个类 A 和 B，A 持有一个指向 B 的 ``shared_ptr``，B 持有一个指
  向 A 的 ``shared_ptr`` 。再假设我们创建了 A 和 B 的实例，并让它们互相引用：

  .. code-block:: cpp

    struct B; // 前向声明
    struct A {
        std::shared_ptr<B> b_ptr; // A 持有 B 的 shared_ptr
        ~A() { std::cout << "A destroyed" << std::endl; }
    };
    struct B {
        std::shared_ptr<A> a_ptr; // B 持有 A 的 shared_ptr
        ~B() { std::cout << "B destroyed" << std::endl; }
    };

    // 那么在我们给 A 和 B 赋值后：
    {
      auto a = std::make_shared<A>(); // a 刚创建，内部成员都是空，a 的引用计数是 1
      auto b = std::make_shared<B>(); // b 刚创建，内部成员都是空，b 的引用计数是 1
      a->b_ptr = b; // 注意： a 持有 b 的 shared_ptr， b 的引用计数 + 1
      b->a_ptr = a; // 注意： b 持有 a 的 shared_ptr， a 的引用计数 + 1
      // 现在 a 和 b 的引用计数都是 2
      // 现在 a 和 b 互相引用，形成循环引用
      // 当 a 和 b 超出作用域时，它们的引用计数都不会变成 0
      // 因为 a 和 b 互相引用，导致它们的引用计数都至少是 1
      // 所以它们的析构函数都不会被调用，资源不会被释放
      // 这就导致了内存泄漏

      // 这种，任何一方如果可以正常销毁，其内部引用别人的关联对象也会销毁，最终另1个对象也会销毁了
      // 如果 A 强引用了 B, 那么 B 就应该弱引用 A 了
    }

lambda
=======

C++中的 lambda 是一种匿名函数，大大的增加了语言的表达能力。在函数内有时候需要增加1个小的辅助函数，就可以直接内部实现，不用在外
部专门进行声明和定义了，而且更加方便的是其可以捕获其所在的作用域内的变量，有值、引用、移动等多种捕获方式。

常见的使用场景有：比如对一个对象数组或者vector进行排序，可以很方便的传递一个比较函数，因为比较函数通常都是比较简短的，这种使
用lambda就是最方便的。因为其可以捕获其所在作用域的其他对象，这个特点就会让其比普通的函数更加的强大和方便。

.. note::

    lambda 捕获变量的原理，是编译器在后台为你生成一个匿名类，并把捕获的变量作为这个类的成员，通过构造函数进行初始化，从而实
    现了将外部状态“打包”到函数对象中的闭包特性。

STL
=======

迭代器
------

C++ 迭代器是基于运算符重载的类，它提供了一种统一的接口，让你能够像操作指针一样遍历不同容器中的元素。库与编译器特性共同协作实现。
核心思想是将指针的行为泛化。重载了 ``* -> ++ -- == !=`` 等运算符，从而实现类似指针的行为。

容器类(vector/list/map)都提供内置嵌套的迭代器，方便遍历集合。

.. note::

  特别注意可能会导致迭代期失效的操作。比如：C++ 语言标准明确规定了 std::vector::erase 会导致迭代器失效，因为其本质
  是删除元素后，可能会移动其他元素来填补空缺，从而使得原有的迭代器指向无效的位置。此时，正确的做法是，erase 操作后，使用
  erase 返回的新迭代器继续遍历。其他不同容器进行删除操作后，失效的规则也不一样。

vector
------

vector 底层是连续内存，维护了一个 array，然后就是大小，自动扩容等；emplace_back 方法在 C++11 中引入的特性来提高性能。
相比 push_back, 会减少不必要的拷贝和移动操作，直接在容器的内存位置上构造对象。

.. note::

  vector 的 emplace_back 和 push_back 的区别：

  - push_back 是将一个已经存在的对象拷贝或者移动到容器中，可能会涉及额外的拷贝或移动开销。
  - emplace_back 则是在容器的内存位置上直接构造对象，避免了不必要的拷贝和移动，提高了性能。
  - emplace_back 可构造函数的参数，直接在容器内构造对象，而 push_back 只能接受一个完整的对象。

  people.emplace_back(Person("Alice", 30)); // 错误，多构造了对象导致了多余的拷贝或者移动
  people.emplace_back("Bob", 25); // 正确，直接传递构造函数参数

list, forward_list
-------------------

list 是双向链表，forward_list 是单向链表，底层是节点指针的链式存储结构，适合频繁插入和删除操作的场景。这种由于对缓存
不友好，遍历性能不如 vector/deque，用的比较少。

deque, stack, queue
-------------------

deque 是双端队列，底层是分段连续内存，支持在两端高效插入和删除操作。stack 和 queue 是基于 deque 实现的适配器容器。
deque 和 vector 的区别：

- deque 底层是分段连续内存，而 vector 是单一连续内存。
- deque 适合需要频繁在两端插入和删除元素的场景，而 vector 更适合随机访问和按索引访问的场景。
- deque 也支持随机访问，重载了 ``[]`` 和 ``at()`` 方法，性能略逊于 vector。

map, multimap
---------------

map 是基于红黑树实现的有序关联容器，适合需要按键排序和范围查询的场景。multimap 也是，只不过允许多个元素拥有相同的键。

.. note::

  对于multimap，即使有重复的key，红黑树特性依然满足：左子树小于根节点，右子树大于根节点。

  - 插入元素时，当键等价时，它们被视为不严格小于也不严格大于，所以可以被放在任何一边，这里保持新插入的元素放在右子树。
  - 查找元素时，equal_range() 方法返回一个 std::pair，表示具有指定键的所有元素的范围 ``[first, second)``。

- std::map 的 insert 方法返回一个 std::pair，其中包含一个迭代器和一个布尔值(表示是否成功)。
- std::multimap 的 insert 方法返回一个迭代器，指向新插入的元素。
- std::map 使用 [] 操作符访问 map 时，如果键不存在，会自动插入一个默认值；而 multimap 不支持 [] 操作符。

multimap 的插入和查找代码举例：

.. code-block:: cpp

  void foo() {
      std::multimap<int, std::string> myMultimap;

      // 插入元素，用{}来统一初始化
      myMultimap.insert({1, "Alice"});
      myMultimap.insert({2, "Bob"});
      myMultimap.insert({1, "Charlie"}); // 允许重复的键
      myMultimap.insert({3, "David"});

      // 查找键为 1 的所有元素
      auto range = myMultimap.equal_range(1);
      std::cout << "Elements with key 1:" << std::endl;
      for (auto it = range.first; it != range.second; ++it) {
          // 这个 it 是迭代期，it->first 是 key, it->second 是 value
          std::cout << it->first << ": " << it->second << std::endl;
      }
  }

priority_queue
------------------

priority_queue 底层默认 vector 做容器，用 max-heap 最大对组织元素。最大堆父节点总是大于子节点，是一个完全二叉树，
满足：每个父节点的值都大于或等于其子节点的值。这意味着最大的元素总是在树的根部。通常用数组实现利用数组索引间的数学
关系（如 父节点索引 = (子节点索引-1)/2）来模拟树形结构，从而避免使用指针，节省内存并提高缓存效率。

- 访问最大元素： 使用 top() 方法，时间复杂度为 O(1)。
- 插入新元素： 使用 push() 方法，时间复杂度为 O(log n)，因为可能需要调整堆以维护堆属性。
- 删除最大元素： 使用 pop() 方法，时间复杂度为 O(log n)，同样需要调整堆。

.. note::

  对于 priority_queue 的一些注意点，比较函数和优先级正好相反，less 是最大堆，greater 是最小堆。

  - 默认是最大堆, 比较器是 ``std::less<T>``，top() 方法返回堆顶最大元素。
  - 如果要最小堆，可以使用 ``std::greater<T>`` 作为比较器。

  也可以自定义比较器，使用 lambda 表达式或者函数对象来定义元素的优先级。

  因为会涉及到大量的交换操作，priority_queue 适合存储小型对象，大型对象会影响性能。对于大对象，建议存储指针或者智能指针。这个
  对于 C++ 标准库的其他容器也是类似的，大对象对性能影响较大，都用指针或者智能指针。不要用引用，因为引用不能重新绑定，不适合被
  容器管理。

.. code-block:: cpp

  // 最小堆
  std::priority_queue<int, std::vector<int>, std::greater<int>> minHeap;

  // 自定义比较器，lambda函数，按字符串长度排序
  auto cmp = [](const std::string &a, const std::string &b) {
      return a.length() > b.length(); // 长度短的优先级高
  };
  std::priority_queue<std::string, std::vector<std::string>, decltype(cmp)> customHeap(cmp);

copy, remove
----------------

算法库里有变动型 (Mutating) 算法和非变动型 (Non-mutating) 算法。

- 变动型算法会修改输入范围的元素，比如 ``std::remove`` 会重新排列元素，将不需要的元素移到末尾，并返回新的逻辑结尾迭代器。
- 非变动型算法不会修改输入范围的元素，比如 ``std::copy`` 会将元素从一个范围复制到另一个范围。

C++社区鼓励使用这种算法，而不是手写循环。这种方式更简洁、易读，并且经过高度优化。一些例子如下：

.. code-block:: cpp

  // 使用 std::copy 复制元素
  std::vector<int> source = {1, 2, 3, 4, 5};
  std::vector<int> destination(5);
  std::copy(source.begin(), source.end(), destination.begin());

  // 使用 std::remove 移除元素
  std::vector<int> vec = {1, 2, 3, 4, 5, 3};
  auto newEnd = std::remove(vec.begin(), vec.end(), 3); // 移除值为3的元素
  // vec 现在是 {1, 2, 4, 5, ?, ?}，?表示未定义的值
  // newEnd 指向新的逻辑结尾
  // 下面的 erase 实际删除元素
  vec.erase(newEnd, vec.end()); // 实际删除元素

编程风格
==========

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

编程风格总结
-------------

一致性最重要，过时的匈牙利前缀命名法要避免。其他的都是个人习惯，新项目达成内部团队一致。个人倾向于谷歌的风格。

笔记
===========

- 语言特性: https://github.com/thisinnocence/cc-notes/tree/master/cpp-notes
- 编译系统: https://github.com/thisinnocence/cc-notes/tree/master/build-system
- 网络编程: https://github.com/thisinnocence/cc-notes/tree/master/network
