.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

ARM体系结构
===========

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