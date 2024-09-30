.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

OS笔记
===========

因为Linux太过复杂，为了方便了解一下基本原理，还有 aarch64 体系结构编程，这里教学类的简单的OS学习一下。

启动
-----

https://github.com/thisinnocence/qemu-virt-hello/blob/master/kernel/start.S

ChatGPT的解释 ::

  BEGIN_FUNC(_start)
    mrs  x1, mpidr_el1          // 获取多处理器ID寄存器的值到x1
    and  x1, x1, #3             // 检查处理器ID的最低两位, <=> x1 & 0b11
    cmp  x1, #0                 // 比较处理器ID是否为0
    bne  hang                   // 如果不是0，跳转到 hang

  primary:
    bl  arm64_elX_to_el1        // 跳转到 arm64_elX_to_el1

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
    b  hang                     // 跳转回 hang
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

根据 mpidr_el1 选择主核来启动，其他的核挂起。

ARM bare metal 编程
----------------------

体系结构强相关的编程，bare metal 裸机编程很有帮助，聚焦体系结构。可以 fork 下面的 project 学习:

- 裸机hello world程序 : https://github.com/thisinnocence/aarch64-bare-metal-qemu
- 裸机带着GIC中断的程序: https://github.com/thisinnocence/armv8-bare-metal
