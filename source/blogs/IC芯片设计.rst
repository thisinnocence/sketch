.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

IC芯片设计
============

verilog入门
------------

verilog入门资料
^^^^^^^^^^^^^^^

Verilog HDL（简称 Verilog ）是一种硬件描述语言，用于数字电路的系统设计。搜了一些资料：

- https://www.runoob.com/w3cnote/verilog-tutorial.html
- `夏宇闻-Verilog经典教程pdf <https://github.com/wtcat/DeveloperDoc/blob/master/%E5%A4%8F%E5%AE%87%E9%97%BB-Verilog%E7%BB%8F%E5%85%B8%E6%95%99%E7%A8%8B.pdf>`_ 
- `Verilog HDL教程（共172页pdf电子书下载） <https://bbs.elecfans.com/jishu_1610362_1_1.html>`_ 
- https://www.asic-world.com/verilog/intro1.html
- https://www.chipverify.com/tutorials/verilog


verilog与c语言对比关键字和控制结构:

.. image:: pic/verilog-comp-c.png
    :scale: 45%

而 C 与 Verilog 相对应的运算符几乎一样。所以有C基础，学起来Verilog会更快。

Verilog HDL是专门为复杂数字逻辑电路和系统的设计仿真而开发的，本身就非常适合复杂数字逻辑电路和系统的仿真和综合。
由于Verilog HDL在其门级描述的底层，也就是在晶体管开关的描述方面比VHDL有强得多得功能，所以即使是VHDL的设计环境，
在底层实质上也是由Verilog HDL描述的器件库所支持的。

说一下逻辑综合，有点类似C语言的编译。综合（synthesize），就是在标准单元库和特定的设计约束的基础上，将设计的高层次
描述（Verilog 建模）转换为门级网表的过程。逻辑综合的目的是产生物理电路门级结构，并在逻辑、时序上进行一定程度的优化，
寻求逻辑、面积、功耗的平衡，增强电路的可测试性。但不是所有的 Verilog 语句都是可以综合成逻辑单元的，例如时延语句。

对比chisel
^^^^^^^^^^^^

- `问chisel语言未来是否会影响传统Verilog数字设计工程师? <https://www.zhihu.com/question/468593551/answer/1975018258>`_ 
- `快速学习-chisel为入门例子 <https://mysummary.readthedocs.io/zh/latest/%E8%8A%B1%E6%9C%B5%E7%9A%84%E6%B8%A9%E5%AE%A4/%E5%BF%AB%E9%80%9F%E5%AD%A6%E4%B9%A0.html#id1>`_ 
- `RISC-V开源项目为什么选用chisel这种新的高层次建模语言，而不是SystemVerilog? <https://www.zhihu.com/question/58584770>`_ 
- `数字IC工程师必须关注的开发潮流 <https://xueqiu.com/4927163759/130286419>`_ 

摘录上面链接一个经典例子：

.. note::

    芯片开发周期过长已经是阻碍半导体数字设计快速发展的重要瓶颈。

    Verilog HDL能实现完整的数字电路开发，但是其代码密度低，许多团队为了加速开发还必须配合团队约定的coding style自行开发
    的Python/Perl等脚本来自动生成代码，然而这种方式的可移植性存在问题。

    之前EDA业界也在尝试把C代码直接编译成Verilog的高级语言综合（High-Level Synthesis），但该尝试目前仅获得了有限的成功。
    U.C. Berkeley在设计和开发RISC-V标准和Core的过程中，引入了Chisel这样的开发工具，并且很大程度上反哺和改进了Chisel。

    举一个非常不恰当的栗子，我们以设计一个CPU为例：

    你本科熬了几年图书馆，挤破了头进入国内某微电子学院做了研究生，老师进来和你说我有个很好的想法，能够有效的改进指令效率或者多核性能
    或者功耗。老师说你做个5级流水线CPU把，还要把cache、总线、外设之类也做了（没缓存搞什么多核？）。好吧，我承认你很聪明，
    不出几个月你把CPU写的差不多了，然后cache、总线、外设这些大头还远着呢。又过了几个月你天天啃《量化研究方法》，然后终于把cache实现了。
    然后你写了个GPIO，又挂了个SRAM，好吧，你终于实现了一个小的CPU了。为了降低难度，你用了学术界最爱的MIPS体系结构，
    用了最土的wishbone总线。然后你开始了撸软件了，因为用了MIPS，你的难度已然降低了很多，而且你不用考虑编译器的问题了，
    你又吭哧了好几个月，写了个巨土的bootloader，终于把程序加载了。尽管后面可能还要在FPGA上跑起来，要发顶作的同学还要去申请经费流个片，
    这估计又要好久好久。但到目前为止你终于可以开始评估下你的设计的好坏了。

    你跑了一堆benchmark，得出了一些结果，然后你才开始把导师的idea应用到你的设计中。然后，然后，你就硕士毕业了，
    放心吧，你的这个摊子，你的学弟们会接锅的。

    这里尽管很多东西不那么真实，但是不得不说大学教授的很多项目，都是好几届学生慢慢做才做下来的，而且做归做，评估归评估。
    做完了哪里不好还得继续改进，因为有了架构，离实现到最后变成芯片还远着呢。更何况，评估一个设计好坏这件事本身或许难度更大。
    以上的故事暴露了一个问题，对于改进硬件架构这件事，反馈环实在太长了。

    所以扯了半天，我其实就想说一句话，硬件设计太耗时，Verilog写的蛋疼，需求要是变一点，那些个接口就得跟着变。要是速度上不去了，
    我要是想换个架构，又要花好久。或许SystemVerilog好一点，但你真的爱她吗？ // 难道SystemVerilog有什么坑？

    chisel的代码密度更高，面向对象和高级语言特性支持的更好。和SystemVerilog提供的一步到位相比，Chisel首先生成通用的Verilog，
    然后交由后端处理的方式，降低了对EDA工具的要求。还有更重要的一点，它是开源和免费的。

    Chisel的封装和抽象对 **通用的电路** 描述很有帮助，但是对某些 **定制化的电路，它的优势其实没有这么明显** 。
    这也是为什么目前能看到名气比较大的项目都是一些CPU、NPU等。里面有很多模块都是相同的单元在重复，所以很适合用Chisel封装。
    并且，Chisel在验证阶段（特别是最花时间的集成验证）中能做到东西基本为0。这一点就导致它很难对整个项目的进度有质的影响。

verilog开发环境
------------------

从 https://zhuanlan.zhihu.com/p/436976157 得出一个信息：
知名的Verilog仿真工具主要为三大EDA厂商的产品：mentor的modelsim/questasim，candence的NC-verilog，synopsys的VCS。
但这三个玩意难安装，要收费，启动也慢，有时候我们就是想简单的看一下设计功能对不对，结果新建一个工程都费了牛劲了。
不够灵活方便。

前面 https://www.runoob.com/w3cnote/verilog-install.html 也提到了环境相关：记忆中，Quartus II + Modelsim 的联合仿真
功能既强大，又安装方便。几年后重新进行此过程，发现步骤也有些许繁琐，花费了我一晚上的时间来搞定。很多细节也在上面提出，多多注意就好。
不过，大家以后有机会进行大型的数字模块仿真时，就会发现此方法的有效性。

然后免费环境有如下的方案，参考： `ubuntu安装vim,iverilog和gtkwave并进行测试与仿真 <https://blog.csdn.net/ZikY_0827/article/details/127939852>`_ 
安装方法： ::

  apt install iverilog
  apt install gtkwave

然后就可以命令行写verilog代码，运行并看波形了，适合入门verilog写小练习。

online verilog练习网站： https://hdlbits.01xz.net/wiki/Step_one

  - `HDLBits: 在线学习 Verilog （〇） <https://zhuanlan.zhihu.com/p/56646479>`_ 
  - `Verilog HDL刷题网站推荐——HDLBits <https://zhuanlan.zhihu.com/p/184031850>`_

该网站很适合Verilog初学者快速上手，也适用于日常练手，其自带基于 **Modelsim** 的在线仿真功能，能够在编写完代码后快速得到反馈，
极大地方便了调试。HDLbits中共有178道题目，大部分题目比较基础，但在组合逻辑、时序逻辑两个模块中也有一些具有挑战性的题。

一些博主分享的答案：

  - `HDLBits 中文导学 <https://zhuanlan.zhihu.com/c_1131528588117385216>`_ 
  - https://github.com/jerrylioon/Solutions-to-HDLbits-Verilog-sets
  - https://github.com/xiaop1/Verilog-Practice

如果是纯粹学习维护，不防用这个online的网站。

verilator介绍
-------------

see: https://verilator.org/guide/latest/overview.html

The Verilator package converts Verilog 1 and SystemVerilog 2 hardware description language (HDL) designs 
into a C++ or SystemC model that, after compiling, can be executed.

| 还支持：SystemVerilog Direct Programming Interface(DPI)
| https://verilator.org/guide/latest/connecting.html#direct-programming-interface-dpi