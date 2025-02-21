.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

QEMU TCG
===========

decodetree
-----------

TCG翻译前端, aarch64 是手写的翻译。arm32则是使用了decodetree机制。decodetree的语法规则如下：

https://www.qemu.org/docs/master/devel/decodetree.html

如上面连接, decodetree的语法规则是：::

  field_def     := '%' identifier ( field )* ( !function=identifier )?
  field         := unnamed_field | named_field
  unnamed_field := number ':' ( 's' ) number
  named_field   := identifier ':' ( 's' ) number

解释，使用了 vscode copilot的gpt-4o模型解释了下。

符号解释
^^^^^^^^^^

- ``:=``：定义符号，表示左边的非终结符由右边的表达式定义。
- ``|``：选择符号，表示可以选择多个选项中的一个。
- ``*``：零或多个，表示前面的元素可以出现零次或多次。
- ``?``：零或一次，表示前面的元素可以出现零次或一次。
- ``()``：分组符号，用于将多个元素组合在一起，作为一个整体进行操作。
- ``!``：在 decodetree 语法中， ``!``  用于指定一个函数，将字段的值传递给该函数进行处理。
- ``''``：单引号用于表示字面量，即必须精确匹配的字符串。
  
有的会有点类似正则表达式中的一些通配符。

符号应用
^^^^^^^^^^

- field_def := '%' identifier ( field )* ( !function=identifier )?：

    - ``%``：表示字段定义的开始。
    - ``identifier``：字段的名称。
    - ``( field )*``：零个或多个字段。
    - ``( !function=identifier )?``：可选的函数调用，指定一个函数来处理字段的值。

- field := unnamed_field | named_field：

    - ``unnamed_field`` 或 ``named_field``：字段可以是匿名字段或命名字段。

- unnamed_field := number ':' ( 's' ) number：

    - ``number``：字段的起始位置。
    - ``':'``：分隔符。
    - ``( 's' )``：可选的符号，表示字段是有符号的。
    - ``number``：字段的长度。

- named_field := identifier ':' ( 's' ) number：

    - ``identifier``：字段的名称。
    - ``':'``：分隔符。
    - ``( 's' )``：可选的符号，表示字段是有符号的。
    - ``number``：字段的长度。

举例：

- ``%disp 0:s16``  字段从第 0 位开始，有 16 位长，并且是有符号, ``disp`` 通常是 ``displacement`` 的缩写,
  表示一个位移量，用于计算内存地址或跳转地址
- ``%imm9 16:6 10:3`` 字段由两个部分组成：第一个部分从第 16 位开始，有 6 位长；第二个部分从第 10 位开始，有 3 位长。
- ``%shimm8 5:s8 13:1 !function=expand_shimm8`` 字段由两个部分组成：第一个部分从第 5 位开始，有 8 位
  长，并且是有符号的；第二个部分从第 13 位开始，有 1 位长。字段的值将传递给 ``expand_shimm8`` 函数进行处理。

注意：

- 命名字段可以引用其他字段，但不能形成循环引用。
- 格式和模式可以互相引用对方的字段，但不能同时这样做，以避免循环引用。

field举例 ::

    +---------------------------+---------------------------------------------+
    | Input                     | Generated code                              |
    +===========================+=============================================+
    | %disp   0:s16             | sextract(i, 0, 16)                          |
    +---------------------------+---------------------------------------------+
    | %imm9   16:6 10:3         | extract(i, 16, 6) << 3 | extract(i, 10, 3)  |
    +---------------------------+---------------------------------------------+
    | %disp12 0:s1 1:1 2:10     | sextract(i, 0, 1) << 11 |                   |
    |                           |    extract(i, 1, 1) << 10 |                 |
    |                           |    extract(i, 2, 10)                        |
    +---------------------------+---------------------------------------------+
    | %shimm8 5:s8 13:1         | expand_shimm8(sextract(i, 5, 8) << 1 |      |
    |   !function=expand_shimm8 |               extract(i, 13, 1))            |
    +---------------------------+---------------------------------------------+
    | %sz_imm 10:2 sz:3         | expand_sz_imm(extract(i, 10, 2) << 3 |      |
    |   !function=expand_sz_imm |               extract(a->sz, 0, 3))         |
    +---------------------------+---------------------------------------------+

参数集
^^^^^^^^^^

Syntax::

  args_def    := '&' identifier ( args_elt )+ ( !extern )?
  args_elt    := identifier (':' identifier)?

- args_def：

    - ``&``：表示参数集定义的开始。
    - ``identifier``：参数集的名称。
    - ``( args_elt )+``：一个或多个参数元素 ``（args_elt）`` 。
    - ``( !extern )?``：可选的 ``!extern`` 标记，表示参数集的结构体已经在其他地方声明过。

- args_elt：

    - ``identifier ('``:' identifier)?：参数元素的定义。
    - 第一个 ``identifier`` 是参数的名称。
    - 可选的 ``':'`` identifier 是参数的类型。如果没有指定类型，默认类型是 int。

举例：

- ``&reg3 ra rb rc``: 一个名为 reg3 的参数集, 包含三个参数，名称分别为 ra、rb 和 rc，默认类型是 int
- ``&loadstore reg base offset``: 名为 loadstore 的参数集, 三个参数，名称分别为 reg、base 和 offset，默认类型是 int

``!extern`` 如果参数集定义中包含 !extern 标记，表示该参数集的结构体已经在其他地方声明过，通常用于多个解码
器协作的情况。 比如 ::

    &shared_args reg base offset !extern

格式
^^^^^^^

Syntax::

  fmt_def      := '@' identifier ( fmt_elt )+
  fmt_elt      := fixedbit_elt | field_elt | field_ref | args_ref
  fixedbit_elt := [01.-]+
  field_elt    := identifier ':' 's'? number
  field_ref    := '%' identifier | identifier '=' '%' identifier
  args_ref     := '&' identifier

- fmt_def：

    - ``@``：表示格式定义的开始。
    - ``identifier``：格式的名称。
    - ``( fmt_elt )+``：一个或多个格式元素 ``（fmt_elt）`` 。

- fmt_elt:

    - ``fixedbit_elt``：固定位元素。表示一段连续的比特，可以是 1、0、. 或 -。
    - ``field_elt``：字段元素。表示一个简单字段，指定了名称和位宽。
    - ``field_ref``：字段引用。引用一个已定义的字段，可以重命名。
    - ``args_ref``：参数引用。参数引用，引用一个参数集。

- fixedbit_elt

    - ``[01.-]+``：表示一段连续的比特，可以是 1、0、. 或 -。
    
      - ``1`` 和 ``0`` 表示固定的比特值。
      - . 表示该比特将任意，0或者1。
      - - 表示该比特将被忽略。

- field_elt

    - ``identifier ':' 's'? number``：字段元素，指定了名称和位宽。
    - ``identifier``：字段的名称。
    - ``':'``：分隔符。
    - ``'s'?``：可选的符号，表示字段是有符号的。
    - ``number``：字段的长度。

- field_ref

    - ``% identifier``：字段引用，引用一个已定义的字段。
    - ``identifier '=' '%' identifier``：字段引用，引用一个已定义的字段，并重命名。

- args_ref

    - ``& identifier``：参数引用，引用一个参数集。

举例: ::

    @opr    ...... ra:5 rb:5 ... 0 ....... rc:5

    @opr：定义一个名为 opr 的格式。
    ......：表示 6 个不关心的比特位。
    ra:5：表示一个名为 ra 的字段，位宽为 5 位。
    rb:5：表示一个名为 rb 的字段，位宽为 5 位。
    ... 0：表示 3 个不关心的比特位，接着是一个固定的 0。
    .......：表示 7 个不关心的比特位。
    rc:5：表示一个名为 rc 的字段，位宽为 5 位。

一个例子
^^^^^^^^^^

对于这个指令 ::

    # *** RV64I Base Instruction Set *** 比特模式和布局
    addw     0000000 .....  ..... 000 ..... 0111011 @r

    # Formats 32:
    @r       .......   ..... ..... ... ..... ....... &r    %rs2 %rs1 %rd

    # Argument sets:
    &r    rd rs1 rs2

    # Fields:
    %rd        7:5
    %rs1       15:5
    %rs2       20:5



- @r：表示使用 @r 格式，该格式定义了指令的字段布局和参数集, 参数高位到低位；
- &r：表示使用 &r 参数集，该参数集定义了指令的参数。%rs2 %rs1 %rd：表示指令的字段引用，分别对
  应 rs2、rs1 和 rd 字段。

添加1个求平方的指令
^^^^^^^^^^^^^^^^^^^^^^^^

代码实现链接：

https://github.com/thisinnocence/qemu/commit/624ba758cbbb67484aa9fcb7036f6010dcb2acc5

后面详细补充依稀 riscv 指令知识，以及QEMU TCG的详细实现。
