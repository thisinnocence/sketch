.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

Linux操作系统
==============

后面主要针对ARM64架构的相关代码进行介绍。

编译Linux kernel
------------------

首先下载下载对应版本的Linux源码，可以去 https://www.kernel.org/ 或github下载，然后
使用menuconfig勾选RAM disks支持，并调整大小为: 65536 kb，主要方便后面用QEMU拉起进行调试。

.. code-block:: bash

    make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 O=build menuconfig -j32
      Device Drivers > Block devices
        <*>   RAM block device support
          (16)    Default number of RAM disks (NEW)
          (65536) Default RAM disk size (kbytes)

    make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 O=build -j32
    file build/arch/arm64/boot/Image 

编译initrd
----------------

从 https://busybox.net 下载源码，然后交叉编译

.. code-block:: bash

    make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 menuconfig -j32 
        Settings
        [*] Build static binary (no shared libs)

    make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 install -j32
    file _install/bin/busybox

然后制作ARM64 initrd

.. code-block:: bash

    #!/bin/bash

    MOUNT_DIR=mnt
    CURR_DIR=`pwd`

    rm initrd.ext4
    dd if=/dev/zero of=initrd.ext4 bs=1M count=32
    mkfs.ext4 initrd.ext4

    mkdir -p $MOUNT_DIR
    mount initrd.ext4 $MOUNT_DIR
    cp -arf busybox/_install/* $MOUNT_DIR

    cd $MOUNT_DIR
    mkdir -p etc dev mnt proc sys tmp mnt etc/init.d/

    echo "proc /proc proc defaults 0 0" > etc/fstab
    echo "tmpfs /tmp tmpfs defaults 0 0" >> etc/fstab
    echo "sysfs /sys sysfs defaults 0 0" >> etc/fstab

    echo "#!/bin/sh" > etc/init.d/rcS
    echo "mount -a" >> etc/init.d/rcS
    echo "mount -o remount,rw /" >> etc/init.d/rcS
    echo "echo -e \"Welcome to ARM64 Linux\"" >> etc/init.d/rcS
    chmod 755 etc/init.d/rcS

    echo "::sysinit:/etc/init.d/rcS" > etc/inittab
    echo "::respawn:-/bin/sh" >> etc/inittab
    echo "::askfirst:-/bin/sh" >> etc/inittab
    chmod 755 etc/inittab

    cd dev
    mknod console c 5 1
    mknod null c 1 3
    mknod tty1 c 4 1

    cd $CURR_DIR
    umount $MOUNT_DIR
    echo "make initrd ok!"

然后就可以使用QEMU来拉起了。

ARM DTS设备树
--------------

DTS基础知识
^^^^^^^^^^^^^^^

| 官方地址： https://www.devicetree.org/
| 文档specification： https://github.com/devicetree-org/devicetree-specification ，也是一个sphinx工程。

关于ARM Linux的DTS，历史渊源是Linus非常不满意ARM硬件细节硬编码到代码里，把代码弄的一团乱，然后社区才引入了DTS这个机制。这个
机制用来描述一个硬件平台的硬件资源，起源于 OpenFirmware (OF)。社区当时讨论的方案是：

.. note:: 

    - ARM的核心代码仍然保存在arch/arm目录下
    - ARM SoC core architecture code保存在arch/arm目录下
    - ARM SOC的周边外设模块的驱动保存在drivers目录下
    - ARM SOC的特定代码在arch/arm/mach-xxx目录下
    - ARM SOC board specific的代码被移除，由DeviceTree机制来负责传递硬件拓扑和硬件资源信息。

本质上，Device Tree改变了原来用hardcode方式将HW 配置信息嵌入到内核代码的方法，改用bootloader传递一个DB的形式。对于操作系统，一个
系统要能够运行到多种硬件平台，还有对一个平台多种特定的单板期间，那么为了内核的通用性，内核启动就要感知：

1. 识别platform的信息
2. runtime的配置参数
3. 设备的拓扑结构以及特性

在系统启动阶段，bootloader会加载内核并将控制权转交给内核，此外， 还需要把上述的三个参数信息传递给kernel，以便kernel可以有较大的灵活性。
可以看这篇文章： https://e-mailky.github.io/2019-01-14-dts-1 

Device Tree由一系列被命名的结点（node）和属性（property）组成，而结点本身可包含 **子结点** 。所谓属性， 其实就是成对出现的name和value。
在Device Tree中，可描述的信息包括（原先这些信息大多被hard code到kernel中）：

- CPU的数量和类别
- 内存基地址和大小
- 总线和桥
- 外设连接
- 中断控制器和中断使用情况
- GPIO控制器和GPIO使用情况
- Clock控制器和Clock使用情况

基本上就是画一棵电路板上CPU、总线、设备组成的树，Bootloader会将这棵树传递给内核，然后内核可以识别这棵树， 并根据它展开
出Linux内核中的platform_device、i2c_client、spi_device等设备，而这些设备用到的内存、IRQ等资源， 也被传递给了内核，
内核会将这些资源绑定给展开的相应的设备。

.. note:: 
    是否Device Tree要描述系统中的所有硬件信息？答案是否定的。基本上，那些可以动态探测到的设备是不需要描述的， 例如USB device。
    不过对于SOC上的usb hostcontroller，它是无法动态识别的，需要在device tree中描述。

    同样的道理， 在computersystem中，PCI device可以被动态探测到，不需要在device tree中描述，但是PCI bridge如果不能被探测，
    那么就需要描述之。

基本上，在ARM Linux在，一个 ``.dts`` 文件对应一个ARM的machine，一般放置在内核的 ``arch/arm/boot/dts/`` 目录。一个SoC可能对应多个machine，
Linux内核为了简化，把SoC公用的部分或者多个machine共同的部分一般提炼为 ``.dtsi`` ，类似于C语言的头文件。 其他的machine对应的.dts就
include这个.dtsi。

正常情况下所有的dts文件以及dtsi文件都含有一个根节点 ``/`` , include文件也不会造成多个根节点，Device Tree Compiler会对DTS的node进行合并。
device tree的基本单元是node。这些node被组织成树状结构，除了root node，每个node都只有一个parent。一个device tree文件中只能有
一个root node。每个node中包含了若干的 ``property/value`` 来描述该node的一些特性。

每个node用节点名字（node name）标识，节点名字的格式是 ``node-name@unit-address`` 。

.. note:: 
    如果该node没有reg属性（后面会描述这个property）， 那么该节点名字中必须不能包括@和unit-address。
    unit-address的具体格式是和设备挂在那个bus上相关。例如对于cpu，其unit-address就是从0开始编址，以此加一。

在一个树状结构的device tree中，如何引用一个node呢？要想唯一指定一个node必须使用full path，
例如 ``/node-name-1/node-name-2/node-name-N`` 。

下面的资料也很不错：
    - https://community.arm.com/oss-platforms/w/docs/525/device-tree
    - https://elinux.org/images/f/f9/Petazzoni-device-tree-dummies_0.pdf

QEMU导出dts
^^^^^^^^^^^^^

QEMU可以有个功能，可以导出来machine的dts. 在 :doc:`/blogs/QEMU仿真虚拟化` 例子里，可以通过加入下面的配置导出virt machine的dts，
如下 ::

    在 virt.cfg 中，machine项加入下面配置即可
    [machine]
        dumpdtb = "virt.dtb"

然后在执行拉起命令，就可以导出来 virt.dtb 文件。然后可以反编译出来看下具体配置

.. code-block:: bash

    dtc -I dtb -O dts virt.dtb > virt.dts

导出的内容如下，通过QEMU virt machine可以看一个完整的DTS主要包括什么：

.. code-block:: dts

    /dts-v1/;

    / {
        interrupt-parent = <0x8003>;
        model = "linux,dummy-virt";
        #size-cells = <0x02>;
        #address-cells = <0x02>;
        compatible = "linux,dummy-virt";

        psci {
            migrate = <0xc4000005>;
            cpu_on = <0xc4000003>;
            cpu_off = <0x84000002>;
            cpu_suspend = <0xc4000001>;
            method = "hvc";
            compatible = "arm,psci-1.0\0arm,psci-0.2\0arm,psci";
        };

        memory@40000000 {
            reg = <0x00 0x40000000 0x01 0x00>;
            device_type = "memory";
        };

        platform-bus@c000000 {
            interrupt-parent = <0x8003>;
            ranges = <0x00 0x00 0xc000000 0x2000000>;
            #address-cells = <0x01>;
            #size-cells = <0x01>;
            compatible = "qemu,platform\0simple-bus";
        };

        fw-cfg@9020000 {
            dma-coherent;
            reg = <0x00 0x9020000 0x00 0x18>;
            compatible = "qemu,fw-cfg-mmio";
        };

        virtio_mmio@a000000 {
            dma-coherent;
            interrupts = <0x00 0x10 0x01>;
            reg = <0x00 0xa000000 0x00 0x200>;
            compatible = "virtio,mmio";
        };
        // 还有很多其他 virtio

        gpio-keys {
            compatible = "gpio-keys";

            poweroff {
                gpios = <0x8005 0x03 0x00>;
                linux,code = <0x74>;
                label = "GPIO Key Poweroff";
            };
        };

        pl061@9030000 {
            phandle = <0x8005>;
            clock-names = "apb_pclk";
            clocks = <0x8000>;
            interrupts = <0x00 0x07 0x04>;
            gpio-controller;
            #gpio-cells = <0x02>;
            compatible = "arm,pl061\0arm,primecell";
            reg = <0x00 0x9030000 0x00 0x1000>;
        };

        pcie@10000000 {
            interrupt-map-mask = <0x1800 0x00 0x00 0x07>;
            interrupt-map = <0x00 0x00 0x00 0x01 0x8003 0x00 0x00 0x00 0x03 0x04 0x00 0x00 0x00 0x02 0x8003 0x00 0x00 0x00 0x04 0x04 0x00 0x00 0x00 0x03 0x8003 0x00 0x00 0x00 0x05 0x04 0x00 0x00 0x00 0x04 0x8003 0x00 0x00 0x00 0x06 0x04 0x800 0x00 0x00 0x01 0x8003 0x00 0x00 0x00 0x04 0x04 0x800 0x00 0x00 0x02 0x8003 0x00 0x00 0x00 0x05 0x04 0x800 0x00 0x00 0x03 0x8003 0x00 0x00 0x00 0x06 0x04 0x800 0x00 0x00 0x04 0x8003 0x00 0x00 0x00 0x03 0x04 0x1000 0x00 0x00 0x01 0x8003 0x00 0x00 0x00 0x05 0x04 0x1000 0x00 0x00 0x02 0x8003 0x00 0x00 0x00 0x06 0x04 0x1000 0x00 0x00 0x03 0x8003 0x00 0x00 0x00 0x03 0x04 0x1000 0x00 0x00 0x04 0x8003 0x00 0x00 0x00 0x04 0x04 0x1800 0x00 0x00 0x01 0x8003 0x00 0x00 0x00 0x06 0x04 0x1800 0x00 0x00 0x02 0x8003 0x00 0x00 0x00 0x03 0x04 0x1800 0x00 0x00 0x03 0x8003 0x00 0x00 0x00 0x04 0x04 0x1800 0x00 0x00 0x04 0x8003 0x00 0x00 0x00 0x05 0x04>;
            #interrupt-cells = <0x01>;
            ranges = <0x1000000 0x00 0x00 0x00 0x3eff0000 0x00 0x10000 0x2000000 0x00 0x10000000 0x00 0x10000000 0x00 0x2eff0000 0x3000000 0x80 0x00 0x80 0x00 0x80 0x00>;
            reg = <0x40 0x10000000 0x00 0x10000000>;
            msi-map = <0x00 0x8004 0x00 0x10000>;
            dma-coherent;
            bus-range = <0x00 0xff>;
            linux,pci-domain = <0x00>;
            #size-cells = <0x02>;
            #address-cells = <0x03>;
            device_type = "pci";
            compatible = "pci-host-ecam-generic";
        };

        pl031@9010000 {
            clock-names = "apb_pclk";
            clocks = <0x8000>;
            interrupts = <0x00 0x02 0x04>;
            reg = <0x00 0x9010000 0x00 0x1000>;
            compatible = "arm,pl031\0arm,primecell";
        };

        pl011@9000000 {
            clock-names = "uartclk\0apb_pclk";
            clocks = <0x8000 0x8000>;
            interrupts = <0x00 0x01 0x04>;
            reg = <0x00 0x9000000 0x00 0x1000>;
            compatible = "arm,pl011\0arm,primecell";
        };

        pmu {
            interrupts = <0x01 0x07 0x304>;
            compatible = "arm,armv8-pmuv3";
        };

        intc@8000000 {
            phandle = <0x8003>;
            reg = <0x00 0x8000000 0x00 0x10000 0x00 0x8010000 0x00 0x10000>;
            compatible = "arm,cortex-a15-gic";
            ranges;
            #size-cells = <0x02>;
            #address-cells = <0x02>;
            interrupt-controller;
            #interrupt-cells = <0x03>;

            v2m@8020000 {
                phandle = <0x8004>;
                reg = <0x00 0x8020000 0x00 0x1000>;
                msi-controller;
                compatible = "arm,gic-v2m-frame";
            };
        };

        flash@0 {
            bank-width = <0x04>;
            reg = <0x00 0x00 0x00 0x4000000 0x00 0x4000000 0x00 0x4000000>;
            compatible = "cfi-flash";
        };

        cpus {
            #size-cells = <0x00>;
            #address-cells = <0x01>;

            cpu-map {

                socket0 {

                    cluster0 {

                        core0 {
                            cpu = <0x8002>;
                        };

                        core1 {
                            cpu = <0x8001>;
                        };
                    };
                };
            };

            cpu@0 {
                phandle = <0x8002>;
                reg = <0x00>;
                enable-method = "psci";
                compatible = "arm,cortex-a57";
                device_type = "cpu";
            };

            cpu@1 {
                phandle = <0x8001>;
                reg = <0x01>;
                enable-method = "psci";
                compatible = "arm,cortex-a57";
                device_type = "cpu";
            };
        };

        timer {
            interrupts = <0x01 0x0d 0x304 0x01 0x0e 0x304 0x01 0x0b 0x304 0x01 0x0a 0x304>;
            always-on;
            compatible = "arm,armv8-timer\0arm,armv7-timer";
        };

        apb-pclk {
            phandle = <0x8000>;
            clock-output-names = "clk24mhz";
            clock-frequency = <0x16e3600>;
            #clock-cells = <0x00>;
            compatible = "fixed-clock";
        };

        chosen {
            linux,initrd-end = <0x00 0x4a000000>;
            linux,initrd-start = <0x00 0x48000000>;
            bootargs = "nokaslr root=/dev/ram init=/linuxrc console=ttyAMA0 console=ttyS0";
            stdout-path = "/pl011@9000000";
            rng-seed = <0xa6ca99d8 0x114f19f2 0x9ab0b35a 0x4dd25395 0x57bd4bc2 0x380a39c3 0x6301f6d1 0xea19cd2>;
            kaslr-seed = <0x53566464 0x74519bb2>;
        };
    };

然后结合文档就可以理解各个关键属性，以及对应的硬件IP是什么了。