.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

QEMU仿真虚拟化
================

环境与版本信息
--------------

环境信息参考: `使用QEMU调试ARM64 Linux内核v6.0.9 <https://blog.csdn.net/thisinnocence/article/details/127931774>`_  
相对上面的环境，下面使用QEMU v8.2.0最新版本，Linux还是v6.0.9版本，编译出来的是arm64架构的Linux
启动脚本进行了些修改，把部分参数挪到了启动文件中，使用 ``-readconfig`` 参数加载配置文件，具体如下:

启动脚本：

.. code-block:: bash

    # start.sh
    qemu/build/aarch64-softmmu/qemu-system-aarch64 \
        -nographic \
        -cpu cortex-a57 \
        -readconfig virt.cfg

配置文件：

.. code-block:: ini

    # virt.cfg 文件
    [machine]
        type = "virt"
        kernel = "linux-6.0.9/build/arch/arm64/boot/Image"
        append = "nokaslr root=/dev/ram init=/linuxrc console=ttyAMA0 console=ttyS0"
        initrd = "initrd.ext4"

    [smp-opts]
        cpus = "2"

    [memory]
        size = "4G"

加载kernel和initrd
-----------------------

这里直接使用QEMU命令行传递内核和initrd，关键的流程步骤:
1. load kernel
2. load initrd
3. load dtb
执行时的callstack如下 ::

    // 1. load kernel
    #0  load_uboot_image (filename=0x555557a469b0 "linux-6.0.9/build/arch/arm64/boot/Image", ep=0x7fffffffd748, loadaddr=0x7fffffffd750, is_linux=0x7fffffffd724, image_type=2 '\002', translate_fn=0x0, translate_opaque=0x0, as=0x555557bcc6c0) at ../hw/core/loader.c:646
    #1  0x00005555559a89bc in load_uimage_as (filename=0x555557a469b0 "linux-6.0.9/build/arch/arm64/boot/Image", ep=0x7fffffffd748, loadaddr=0x7fffffffd750, is_linux=0x7fffffffd724, translate_fn=0x0, translate_opaque=0x0, as=0x555557bcc6c0) at ../hw/core/loader.c:784
    #2  0x0000555555df23ab in arm_setup_direct_kernel_boot (cpu=0x555557b3ca90, info=0x5555579d19b8) at ../hw/arm/boot.c:976
    #3  0x0000555555df2cfe in arm_load_kernel (cpu=0x555557b3ca90, ms=0x5555579d1800, info=0x5555579d19b8) at ../hw/arm/boot.c:1239
    #4  0x0000555555dfa6b2 in machvirt_init (machine=0x5555579d1800) at ../hw/arm/virt.c:2336
    #5  0x00005555559b1215 in machine_run_board_init (machine=0x5555579d1800, mem_path=0x0, errp=0x7fffffffd980) at ../hw/core/machine.c:1509
    #6  0x0000555555d14a46 in qemu_init_board () at ../system/vl.c:2613
    #7  0x0000555555d14cb4 in qmp_x_exit_preconfig (errp=0x5555575a7f20 <error_fatal>) at ../system/vl.c:2704
    #8  0x0000555555d174ed in qemu_init (argc=6, argv=0x7fffffffdc88) at ../system/vl.c:3753
    #9  0x00005555561af787 in main (argc=6, argv=0x7fffffffdc88) at ../system/main.c:47

    // 2. load initrd
    #0  load_uboot_image (filename=0x555557a46e60 "initrd.ext4", ep=0x0, loadaddr=0x7fffffffd6f0, is_linux=0x0, image_type=3 '\003', translate_fn=0x0, translate_opaque=0x0, as=0x555557bcc6c0) at ../hw/core/loader.c:636
    #1  0x00005555559a8a3c in load_ramdisk_as (filename=0x555557a46e60 "initrd.ext4", addr=1207959552, max_sz=2013265920, as=0x555557bcc6c0) at ../hw/core/loader.c:797
    #2  0x0000555555df2731 in arm_setup_direct_kernel_boot (cpu=0x555557b3ca90, info=0x5555579d19b8) at ../hw/arm/boot.c:1048
    #3  0x0000555555df2cfe in arm_load_kernel (cpu=0x555557b3ca90, ms=0x5555579d1800, info=0x5555579d19b8) at ../hw/arm/boot.c:1239

    // 3. load dtb
    #0  arm_load_dtb (addr=1241513984, binfo=0x5555579d19b8, addr_limit=0, as=0x555557bcc6c0, ms=0x5555579d1800) at ../hw/arm/boot.c:518
    #1  0x0000555555df9176 in virt_machine_done (notifier=0x5555579d1958, data=0x0) at ../hw/arm/virt.c:1681
    #2  0x00005555563c7f0c in notifier_list_notify (list=0x555557579390 <machine_init_done_notifiers>, data=0x0) at ../util/notify.c:39
    #3  0x00005555559b1352 in qdev_machine_creation_done () at ../hw/core/machine.c:1557
    #4  0x0000555555d14bbe in qemu_machine_creation_done () at ../system/vl.c:2677
    #5  0x0000555555d14cbe in qmp_x_exit_preconfig (errp=0x5555575a7f20 <error_fatal>) at ../system/vl.c:2706
    #6  0x0000555555d174ed in qemu_init (argc=6, argv=0x7fffffffdc88) at ../system/vl.c:3753

内核启动是需要Bootloader的，硬件初始化，把内核从文件加载到内存，PC设置到入口等等。

选项解析与初始化
-----------------

首先说一下怎么看qemu所支持的参数 ::

    ./qemu-system-aarch64 -help   // 可以看所有参数
    ./qemu-system-aarch64 -d help // 可以看调试所支持项
    在编译的build目录下有个 qemu-options.def，也有所有的标砖的参数

展开看下QEMU启动一个machine的选项与配置 ::

    qemu_init
        // 1. qemu_add各种opts数据结构
        // 2. pass of option parsing, qemu-options.def 里有各种定义
        // QEMU_OPTION_readconfig
        |   qemu_read_config_file
        |   |   qemu_config_foreach  // 解析配置文件
        |   |       qemu_config_foreach // 跳过空行和注释解析到字典中
        |   qemu_validate_options // 从解析的字典结构判断选项合法性
        |       // 指定了 -kernel 选项，才能指定 -initrd 和 -append
        qemu_validate_options
        qemu_process_sugar_options // 有些 cpu 选项 Deprecated ，可以看文档具体
        qemu_init_main_loop
        qemu_create_machine
        |   select_machine
        |       machine_type = machine类型名字字符串
        |       machine_class = find_machine(machine_type, machines);
        |       current_machine = MACHINE(object_new_with_class(OBJECT_CLASS(machine_class))); // 全局变量machine
        machine_class = MACHINE_GET_CLASS(current_machine);
        current_machine->cpu_type = xx // 解析CPU类型
        qmp_x_exit_preconfig
            qemu_init_board
            |   machine_run_board_init
            |       machine_class = MACHINE_GET_CLASS(machine);
            |       machine_class->init(machine); // 函数指针是 machvirt_init
            |           cpuobj = object_new(possible_cpus->cpus[n].type); // 初始化cpu对象
            |           object_property_set_bool(cpuobj, "has_el3", false, NULL); // 如果secure模式
            |           create_gic
            |           create_uart
            |           ... // 各种设备create
            |           vms->bootinfo = .. // 赋值 bootinfo
            |               arm_load_kernel
            |                   arm_setup_direct_kernel_boot
            qemu_machine_creation_done
                arm_load_dtb

上面就是使用QEMU解析命令行参数和配置文件启动virt(arm machine)跑Linux的流程。

TCG的原理
-----------

| QEMU仿真的核心机制是DBT(Dynamic Binary Translate), 在TCG模块不停的翻译Guest的指令为Host的指令。
| see: `QEMU - Binary Translation <https://www.slideshare.net/RampantJeff/qemu-binary-translation>`_ 

把Guest的汇编指令翻译为Host的汇编指令，有个论文做的统计是大概是原来指令数的10多倍。那么为什么会多执行了这么多？很简单，比如
下面的情况：

- 访问内存的指令(访存指令)，肯定需要调用到对应内存的回调；
- 访问IO的指令(IO指令)，也会调用到对应IO的仿真回调函数；
- 特定系统寄存器的访问(系统寄存器读写指令)，也会调用到对应的helper函数中；
- 指令执行出现异常后的处理，这个也需要额外的处理；

这片文章讲的很不错: `QEMU tcg源码分析与unicorn原理 <https://bbs.kanxue.com/thread-277163.htm>`_ ，讲了下面几个点：

.. note:: 

    1. 普通算术逻辑运算指令如何更新Host体系结构相关寄存器
    2. 内存读写如何处理
    3. 分支指令(条件跳转、非条件跳转、返回指令）
    4. 目标机器没有的指令、特权指令、敏感指令
    5. 非普通内存读写如设备寄存器访问MMIO
    6. 指令执行出现了同步异常如何处理(如系统调用)
    7. 硬件中断如何处理

QEMU会 ``mmap`` 一段空间，放到 ``code_gen_buffer`` 这个指针指向的位置，加入执行权限，然后来存放TCG对Guest指令进行翻译后的指令, 
可以看 ``/qemu/tcg/region.c`` 相关的实现。

这些情况必须正确处理了，才能够做到一个真正的仿真。TCG是按照TB(Translate Block)进行一块一块的翻译。遇到函数调用类似 ``callq`` 等
就会有跳转，这时就会执行另一个TB。每个TB处理都会有 prologue, epilogue 的预处理和后处理，方便做特殊处理，比如遇到异常等，如下：

.. image:: pic/tcg_exec_trans.png
    :scale: 60%

TCG会把翻译过得指令给缓存起来，下次遇到同样的TB，就可以直接执行这些翻译过的指令了，这样就提高了效率，大概执行的流程如下：

.. image:: pic/qemu-tcg-flow.png
    :scale: 60%

| 上面执行过程也可以看出，当遇到 Exception 时，会去执行异常处理，如中断、IO访问等。

还可以使用 ``-d help`` 看支持的选项，把tcg翻译前后的指令打印出来，先安装 ``apt install libcapstone-dev`` 支持反汇编。
还是用前面的环境配置，用下面一行命令拉起  ::
    
    qemu-system-aarch64 -nographic -cpu cortex-a57 -readconfig virt.cfg -d in_asm,out_asm -D a.log

    运行后的日志就被打印到 a.log 里了，大概如下，可以明显看出，一条guest会有很多host指令 ：
    IN: 
    0xffff8000083ca030:  910163e0  add      x0, sp, #0x58
    0xffff8000083ca034:  f9002fe3  str      x3, [sp, #0x58]
    0xffff8000083ca038:  b90063e4  str      w4, [sp, #0x60]
    0xffff8000083ca03c:  940345d5  bl       #0xffff80000849b790

    OUT: [size=296]
      -- guest addr 0x0000000000000030 + tb prologue
    0x7f985d36c280:  8b 5d f0                 movl     -0x10(%rbp), %ebx
    0x7f985d36c283:  85 db                    testl    %ebx, %ebx
    0x7f985d36c285:  0f 8c b3 00 00 00        jl       0x7f985d36c33e
    0x7f985d36c28b:  c6 45 f4 00              movb     $0, -0xc(%rbp)
    0x7f985d36c28f:  48 8b 9d 38 01 00 00     movq     0x138(%rbp), %rbx
    0x7f985d36c296:  4c 8d 63 58              leaq     0x58(%rbx), %r12
    0x7f985d36c29a:  4c 89 65 40              movq     %r12, 0x40(%rbp)
      -- guest addr 0x0000000000000034
    0x7f985d36c29e:  4c 8d 63 58              leaq     0x58(%rbx), %r12
    0x7f985d36c2a2:  4c 8b 6d 58              movq     0x58(%rbp), %r13
    0x7f985d36c2a6:  49 8b fc                 movq     %r12, %rdi
    0x7f985d36c2a9:  48 c1 ef 07              shrq     $7, %rdi
    0x7f985d36c2ad:  48 23 bd 10 ff ff ff     andq     -0xf0(%rbp), %rdi
    0x7f985d36c2b4:  48 03 bd 18 ff ff ff     addq     -0xe8(%rbp), %rdi
    0x7f985d36c2bb:  49 8d 74 24 07           leaq     7(%r12), %rsi
    0x7f985d36c2c0:  48 81 e6 00 f0 ff ff     andq     $0xfffffffffffff000, %rsi
    0x7f985d36c2c7:  48 3b 77 08              cmpq     8(%rdi), %rsi
    0x7f985d36c2cb:  0f 85 79 00 00 00        jne      0x7f985d36c34a
    0x7f985d36c2d1:  48 8b 7f 18              movq     0x18(%rdi), %rdi
    0x7f985d36c2d5:  4d 89 2c 3c              movq     %r13, 0(%r12, %rdi)

中断的仿真
-----------

QEMU在tcg大循环不停的翻译执行Guest的指令，然后遇到了IO/Exception后，就去执行对应处理 ::

    (gdb) bt
    #0  cpu_exit (cpu=0x5555563bf3fb <qemu_cond_broadcast+71>) at ../hw/core/cpu-common.c:85
    #1  0x00005555561aa4fe in mttcg_kick_vcpu_thread (cpu=0x555557b3d370) at ../accel/tcg/tcg-accel-ops-mttcg.c:130
    #2  0x0000555555d00121 in qemu_cpu_kick (cpu=0x555557b3d370) at ../system/cpus.c:462
    #3  0x00005555561a9d9c in tcg_handle_interrupt (cpu=0x555557b3d370, mask=2) at ../accel/tcg/tcg-accel-ops.c:100
    <||>
    #4  0x0000555555cffb21 in cpu_interrupt (cpu=0x555557b3d370, mask=2) at ../system/cpus.c:256
    #5  0x0000555555e82e75 in arm_cpu_set_irq (opaque=0x555557b3d370, irq=0, level=1) at ../target/arm/cpu.c:954
    #6  0x00005555561b72ad in qemu_set_irq (irq=0x555557b25420, level=1) at ../hw/core/irq.c:44
    #7  0x0000555555a72fd3 in gic_update_internal (s=0x555557c859f0, virt=false) at ../hw/intc/arm_gic.c:222
    #8  0x0000555555a73048 in gic_update (s=0x555557c859f0) at ../hw/intc/arm_gic.c:229
    #9  0x0000555555a73902 in gic_set_irq (opaque=0x555557c859f0, irq=27, level=1) at ../hw/intc/arm_gic.c:419
    #10 0x00005555561b72ad in qemu_set_irq (irq=0x555557c9eb40, level=1) at ../hw/core/irq.c:44
    <||>
    #11 0x0000555555e93f8c in gt_update_irq (cpu=0x555557b3d370, timeridx=1) at ../target/arm/helper.c:2615
    #12 0x0000555555e941ca in gt_recalc_timer (cpu=0x555557b3d370, timeridx=1) at ../target/arm/helper.c:2690
    #13 0x0000555555e94f8b in arm_gt_vtimer_cb (opaque=0x555557b3d370) at ../target/arm/helper.c:3083
    #14 0x00005555563defc4 in timerlist_run_timers (timer_list=0x5555576e9c80) at ../util/qemu-timer.c:576
    #15 0x00005555563df070 in qemu_clock_run_timers (type=QEMU_CLOCK_VIRTUAL) at ../util/qemu-timer.c:590
    #16 0x00005555563df356 in qemu_clock_run_all_timers () at ../util/qemu-timer.c:672
    #17 0x00005555563da2b8 in main_loop_wait (nonblocking=0) at ../util/main-loop.c:603
    #18 0x0000555555d0e37e in qemu_main_loop () at ../system/runstate.c:782
    #19 0x00005555561af751 in qemu_default_main () at ../system/main.c:37
    #20 0x00005555561af790 in main (argc=6, argv=0x7fffffffdf18) at ../system/main.c:48

定时中断从io-thread报上去，然后执行到cpu_exit，在tcg里面设置一个标记，大循环中检测到后，pc指针设置到中断向量表的位置去执行中断。

串口pl011的仿真
----------------

| 官方手册： https://developer.arm.com/documentation/ddi0183/latest/
| 寄存器:  https://developer.arm.com/documentation/ddi0183/g/programmers-model/summary-of-registers

Data Register, UARTDR 的偏移是0，屏幕打印就是这个寄存器的值。点开细节描述就是： ``7:0`` 就是 data. 看QEMU pl011.c实现：

.. code-block:: c

    pl011_write()
        case 0: ch = value; // 这个就是要打印的value
        qemu_chr_fe_write_all(&s->chr, &ch, 1); // 这个换成printf仍然可以打出来值
            qemu_chr_write // char设备的backend实现

一个执行的流程 ::

    (gdb) b writev
    (gdb) bt
    #0  __GI___writev (fd=1, iov=0x7ffe5b9fa450, iovcnt=1) at ../sysdeps/unix/sysv/linux/writev.c:25
    <||>
    #1  0x00005555561ca6c9 in qio_channel_file_writev (ioc=0x555557a26390, iov=0x7ffe5b9fa450, niov=1, fds=0x0, nfds=0, flags=0, errp=0x0) at ../io/channel-file.c:126
    #2  0x00005555561d353e in qio_channel_writev_full (ioc=0x555557a26390, iov=0x7ffe5b9fa450, niov=1, fds=0x0, nfds=0, flags=0, errp=0x0) at ../io/channel.c:109
    #3  0x00005555562e8090 in io_channel_send_full (ioc=0x555557a26390, buf=0x7ffe5b9fa75c, len=1, fds=0x0, nfds=0) at ../chardev/char-io.c:123
    #4  0x00005555562e813e in io_channel_send (ioc=0x555557a26390, buf=0x7ffe5b9fa75c, len=1) at ../chardev/char-io.c:146
    #5  0x00005555562f2a7a in fd_chr_write (chr=0x5555576e7740, buf=0x7ffe5b9fa75c "[\177", len=1) at ../chardev/char-fd.c:45
    #6  0x00005555562efe2f in qemu_chr_write_buffer (s=0x5555576e7740, buf=0x7ffe5b9fa75c "[\177", len=1, offset=0x7ffe5b9fa560, write_all=false) at ../chardev/char.c:122
    #7  0x00005555562effdb in qemu_chr_write (s=0x5555576e7740, buf=0x7ffe5b9fa75c "[\177", len=1, write_all=false) at ../chardev/char.c:174
    #8  0x00005555562e6ea0 in qemu_chr_fe_write (be=0x55555794ccc0, buf=0x7ffe5b9fa75c "[\177", len=1) at ../chardev/char-fe.c:42
    #9  0x00005555562e82cb in mux_chr_write (chr=0x55555794cc00, buf=0x7ffe5b9fa75c "[\177", len=1) at ../chardev/char-mux.c:49
    #10 0x00005555562efe2f in qemu_chr_write_buffer (s=0x55555794cc00, buf=0x7ffe5b9fa75c "[\177", len=1, offset=0x7ffe5b9fa6d0, write_all=true) at ../chardev/char.c:122
    #11 0x00005555562effdb in qemu_chr_write (s=0x55555794cc00, buf=0x7ffe5b9fa75c "[\177", len=1, write_all=true) at ../chardev/char.c:174
    #12 0x00005555562e6eea in qemu_chr_fe_write_all (be=0x555557d01cb0, buf=0x7ffe5b9fa75c "[\177", len=1) at ../chardev/char-fe.c:53
    <||>
    #13 0x000055555599535b in pl011_write (opaque=0x555557d017f0, offset=0, value=91, size=4) at ../hw/char/pl011.c:268
    #14 0x00005555561413a2 in memory_region_write_accessor (mr=0x555557d01b20, addr=0, value=0x7ffe5b9fa878, size=4, shift=0, mask=4294967295, attrs=...) at ../system/memory.c:497
    #15 0x00005555561416b9 in access_with_adjusted_size (addr=0, value=0x7ffe5b9fa878, size=2, access_size_min=4, access_size_max=4, access_fn=0x5555561412a8 <memory_region_write_accessor>, mr=0x555557d01b20, attrs=...) at ../system/memory.c:573
    #16 0x00005555561447e7 in memory_region_dispatch_write (mr=0x555557d01b20, addr=0, data=91, op=MO_16, attrs=...) at ../system/memory.c:1521
    #17 0x000055555619c498 in int_st_mmio_leN (cpu=0x555557b3e370, full=0x7ffe54141f50, val_le=91, addr=18446603336393150464, size=2, mmu_idx=2, ra=140734882528523, mr=0x555557d01b20, mr_offset=0) at ../accel/tcg/cputlb.c:2545
    #18 0x000055555619c5f6 in do_st_mmio_leN (cpu=0x555557b3e370, full=0x7ffe54141f50, val_le=91, addr=18446603336393150464, size=2, mmu_idx=2, ra=140734882528523) at ../accel/tcg/cputlb.c:2581
    #19 0x000055555619cd2d in do_st_2 (cpu=0x555557b3e370, p=0x7ffe5b9faa10, val=91, mmu_idx=2, memop=MO_16, ra=140734882528523) at ../accel/tcg/cputlb.c:2739
    #20 0x000055555619d06f in do_st2_mmu (cpu=0x555557b3e370, addr=18446603336393150464, val=91, oi=18, ra=140734882528523) at ../accel/tcg/cputlb.c:2812
    #21 0x000055555619db37 in helper_stw_mmu (env=0x555557b40b30, addr=18446603336393150464, val=91, oi=18, retaddr=140734882528523) at ../accel/tcg/ldst_common.c.inc:93
    #22 0x00007fff64ae3d56 in code_gen_buffer ()
    <...tcg thread...>

上面断了 POSIX 标准库中的 writev 函数，主要用途在于提高写入操作的效率，特别是当需要将多个不连续的数据缓冲区写入时。

然后就是捕获键盘的输入，这个肯定涉及了interrupt，等OS启动到串口可以命令是，给 pl011 中报中断的地方打断点 ::

    // gic interrupt
    #0  cpu_interrupt (cpu=0x555557b3e370, mask=2) at ../system/cpus.c:255
    #1  0x0000555555e83bfc in arm_cpu_set_irq (opaque=0x555557b3e370, irq=0, level=1) at ../target/arm/cpu.c:954
    #2  0x00005555561b8040 in qemu_set_irq (irq=0x555557b26420, level=1) at ../hw/core/irq.c:44
    #3  0x0000555555a73d0a in gic_update_internal (s=0x555557c869f0, virt=false) at ../hw/intc/arm_gic.c:222
    #4  0x0000555555a73d7f in gic_update (s=0x555557c869f0) at ../hw/intc/arm_gic.c:229
    #5  0x0000555555a74639 in gic_set_irq (opaque=0x555557c869f0, irq=33, level=1) at ../hw/intc/arm_gic.c:419
    #6  0x00005555561b8040 in qemu_set_irq (irq=0x555557bee5c0, level=1) at ../hw/core/irq.c:44
    <||> // pl011
    #7  0x0000555555994de4 in pl011_update (s=0x555557d017f0) at ../hw/char/pl011.c:120
    #8  0x00005555559956f7 in pl011_put_fifo (opaque=0x555557d017f0, value=97) at ../hw/char/pl011.c:358
    #9  0x0000555555995729 in pl011_receive (opaque=0x555557d017f0, buf=0x7fffffffc9c0 "a\317\377\377\377\177", size=1) at ../hw/char/pl011.c:364
    <||> // char backend, 这里键盘输入的是a, buf里value就是a
    #10 0x00005555562e8c4b in mux_chr_read (opaque=0x55555794cc00, buf=0x7fffffffc9c0 "a\317\377\377\377\177", size=1) at ../chardev/char-mux.c:235
    #11 0x00005555562f00d7 in qemu_chr_be_write_impl (s=0x5555576e7740, buf=0x7fffffffc9c0 "a\317\377\377\377\177", len=1) at ../chardev/char.c:202
    #12 0x00005555562f013f in qemu_chr_be_write (s=0x5555576e7740, buf=0x7fffffffc9c0 "a\317\377\377\377\177", len=1) at ../chardev/char.c:214
    #13 0x00005555562f2bb3 in fd_chr_read (chan=0x5555576ed090, cond=G_IO_IN, opaque=0x5555576e7740) at ../chardev/char-fd.c:72
    #14 0x00005555561cf5b1 in qio_channel_fd_source_dispatch (source=0x5555586664a0, callback=0x5555562f2a7c <fd_chr_read>, user_data=0x5555576e7740) at ../io/channel-watch.c:84
    <||> // event loop
    #15 0x00007ffff736b04e in g_main_context_dispatch () at /lib/x86_64-linux-gnu/libglib-2.0.so.0
    #16 0x00005555563dae7d in glib_pollfds_poll () at ../util/main-loop.c:290
    #17 0x00005555563daefb in os_host_main_loop_wait (timeout=510442109) at ../util/main-loop.c:313
    #18 0x00005555563db00c in main_loop_wait (nonblocking=0) at ../util/main-loop.c:592
    #19 0x0000555555d0f0b5 in qemu_main_loop () at ../system/runstate.c:782
    #20 0x00005555561b04e4 in qemu_default_main () at ../system/main.c:37
    #21 0x00005555561b0523 in main (argc=6, argv=0x7fffffffdc88) at ../system/main.c:48

在上面的第5层栈帧，可以看到 irq=33, 而前面前面一层调用还是irq=1， 跟virt的DTS一致，参考： :ref:`virt_dts`

.. code-block:: dts

    pl011@9000000 {
        clock-names = "uartclk\0apb_pclk";
        clocks = <0x8000 0x8000>;
        interrupts = <0x00 0x01 0x04>;
        reg = <0x00 0x9000000 0x00 0x1000>;
        compatible = "arm,pl011\0arm,primecell";
    }; 

这里面QEMU做了一个特殊的处理，看第5层函数栈帧实现:

.. code-block:: c

    /* Process a change in an external IRQ input.  */
    static void gic_set_irq(void *opaque, int irq, int level)
    {
        /* Meaning of the 'irq' parameter:
        *  [0..N-1] : external interrupts
        *  [N..N+31] : PPI (internal) interrupts for CPU 0
        *  [N+32..N+63] : PPI (internal interrupts for CPU 1
        *  ...
        */
        if (irq < (s->num_irq - GIC_INTERNAL))
            /* The first external input line is internal interrupt 32.  */
            irq += GIC_INTERNAL; // GIC_INTERNAL 32
    }

这里就对中断号做了特殊处理，external interrupts 是所有核共享的，放到到 ``[0, N-1]``， 而前32个中断号是每个核私有的，
可以看那 :doc:`/blogs/ARM体系结构` 里GIC章节。每个核私有中断包括了SGI/PPI，这样好处就是让CPU核和中断编号就对应了起来了，
就又了注释中所说明的， ``[N..N+31]`` 就是CPU0, 然后就是CPU1。巧妙在数据结构关系中建立了这个逻辑。

后面可以看下 Linux 内核里相关的实现再。
