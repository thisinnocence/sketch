.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

OS笔记
===========

因为Linux太过复杂，为了方便了解一下基本原理，还有 aarch64 体系结构编程，这里针对一下教学或者简单的OS学习一下。

启动
-----

https://github.com/thisinnocence/qemu-virt-hello/blob/master/kernel/start.S

ChatGPT的解释 ::

  BEGIN_FUNC(_start)
    mrs  x1, mpidr_el1          // 获取多处理器ID寄存器的值到x1
    and  x1, x1, #3             // 检查处理器ID的最低两位, <=> x1 & 0b11
    cmp  x1, #0                 // 比较处理器ID是否为0
    bne  hang                   // 如果不是0，跳转到hang标签

  primary:
    bl  arm64_elX_to_el1        // 跳转到arm64_elX_to_el1函数

    // set exception vector
    adr  x0, exception_vector   // 获取异常向量表的地址
    msr  vbar_el1, x0           // 设置异常向量表寄存器

    // setup stack
    ldr  x0, =stack             // 加载堆栈地址
    mov  sp, x0                 // 设置堆栈指针

    // jump to C code
    b  main                     // 跳转到main函数
    // never return

  hang:
    wfi                         // 等待中断
    b  hang                     // 跳转回hang标签
  END_FUNC(_start)

在编译的中间文件 kernel/kernel.asm 中可以看到 ::

  0000000040000000 <_start>:
      40000000:	d53800a1 	mrs	x1, mpidr_el1
      40000004:	92400421 	and	x1, x1, #0x3
      40000008:	f100003f 	cmp	x1, #0x0
      4000000c:	540000e1 	b.ne	40000028 <hang>  // b.any
  
  0000000040000010 <primary>:
      40000010:	94000615 	bl	40001864 <arm64_elX_to_el1>
      40000014:	10007f60 	adr	x0, 40001000 <exception_vector>
      40000018:	d518c000 	msr	vbar_el1, x0
      4000001c:	580000a0 	ldr	x0, 40000030 <hang+0x8>
      40000020:	9100001f 	mov	sp, x0
      40000024:	14000641 	b	40001928 <main>
  
  0000000040000028 <hang>:
      40000028:	d503207f 	wfi
      4000002c:	17ffffff 	b	40000028 <hang>
      40000030:	40005008 	.inst	0x40005008 ; undefined

首先是选择住核启动：

https://developer.arm.com/documentation/ddi0601/2024-03/AArch64-Registers/MPIDR-EL1--Multiprocessor-Affinity-Register?lang=en

MPIDR_EL1(Multiprocessor Affinity Register)的作用：

.. note::

    | In a multiprocessor system, provides an additional PE identification mechanism. (most for schedule)
    | 叫亲和性就是因为可能经常和绑定任务thread有关，所以这么叫。

    | Aff0, bits [7:0]
    | Affinity level 0. The value of the MPIDR.{Aff2, Aff1, Aff0} or 
    |   MPIDR_EL1.{Aff3, Aff2, Aff1, Aff0} set of fields of each PE must be unique within the system as a whole.
    | This field has an IMPLEMENTATION DEFINED value.