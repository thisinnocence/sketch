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
