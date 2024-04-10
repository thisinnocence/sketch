.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

IC芯片设计
============

verilog入门
------------

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