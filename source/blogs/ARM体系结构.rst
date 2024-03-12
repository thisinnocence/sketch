.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

ARM体系结构
===========

ARMv8异常等级和安全态
------------------------

ARMv8-A 有两种 security states, Secure and Non-secure. The Non-secure state 也叫做 Normal World. 

.. image:: pic/Exception-level.png
    :scale: 50%

| ARM CPU的执行mode改变受到特权程序控制或者异常自动触发。可以参考：
| https://developer.arm.com/documentation/den0024/a/Fundamentals-of-ARMv8/Changing-Exception-levels


AArch64 Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^

某些指令可以产生异常:

- The Supervisor Call (SVC) instruction enables User mode programs to request an OS service.
- The Hypervisor Call (HVC) instruction enables the guest OS to request hypervisor services.
- The Secure monitor Call (SMC) instruction enables the Normal world to request Secure world services.

参考： https://developer.arm.com/documentation/100933/latest/AArch64-Exception-and-Interrupt-Handling

GIC中断控制器
----------------

主要参考ARM官方文档:  https://developer.arm.com/documentation/ihi0069/h/?lang=en

GIC的组成和中断的分类：

.. image:: pic/gic-compose.png
    :scale: 60%

然后中断的上报流程可以看，不包括LPI（都是消息中断)：

.. image:: pic/gic_step.png
    :scale: 50%

按照安全非安全进行分组如下，以及对应的使用场景：

.. image:: pic/gic_safe_group.png
    :scale: 45%

结合QEMU和Linux的源码实现，可以更好的理解其实现细节。

FIQ is higher priority than IRQ. 

The GIC is accessed as a memory-mapped peripheral. All cores can access the common
Distributor, but the CPU interface is banked, that is, each core uses the same address to access
its own private CPU interface. It is not possible for a core to access the CPU interface of another
core。

In the Distributor, software must configure the priority, target, security and enable individual
interrupts. The Distributor must subsequently be enabled through its control register
(GICD_CTLR). For each CPU interface, software must program the priority mask and
preemption settings.

Each CPU interface block itself must be enabled through its control register (GICD_CTLR).
This prepares the GIC to deliver interrupts to the core.

When the core takes an interrupt, it jumps to the top-level interrupt vector obtained from the
vector table and begins execution.

The top-level interrupt handler reads the Interrupt Acknowledge Register from the CPU
Interface block to obtain the interrupt ID.

As well as returning the interrupt ID, the read causes the interrupt to be marked as active in the
Distributor. Once the interrupt ID is known (identifying the interrupt source), the top-level
handler can now dispatch a device-specific handler to service the interrupt.

When the device-specific handler finishes execution, the top-level handler writes the same
interrupt ID to the End of Interrupt (EoI) register in the CPU Interface block, indicating the end
of interrupt processing.