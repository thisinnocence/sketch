.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

AI学习笔记
===========

我对AI的认识一直停留在理论和宏观，记点笔记实操一下。刚开始入门一个领域，从整体，多维度，各个细节切入都影响不大，关键是后续
逐渐丰满对一个领域的知识框架，逐渐把点串起来，前期多看，跟对领域主流的框架、技术点，慢慢尝试就行。

突然想到了卡马克的入门AI的博客： `约翰·卡马克（John Carmack）：学习神经网络这一周 <https://zhuanlan.zhihu.com/p/34391263>`_ 

.. note::

    我想从头开始用C++编写一些神经网络实现。我最喜欢的还是Windows的Visual Studio，所以其实我完全可以回避这些问题。
    我只是单纯觉得在老式UNIX风格下进行长达一周的沉浸式工作会很有趣，即使进度会慢一些。

    我并没有真正探索完整个系统，因为我把95%的时间都花在基础的 vi/make/gdb 操作上了。我很喜欢那些实用的帮助手册页面，
    虽然一直在摸索自己能在这个系统里做什么，但我实在不想上网直接搜。

    在这之前， **我其实已经对大多数机器学习算法有了成熟的了解** ，而且也做过一些线性分类器和决策树之类的工作。但出于某些原因，
    我还没碰过神经网络，这在某种程度上可能是因为深度学习太时髦了，导致我对它持保守意见，或许也有一些反思性的偏见。
    **“我还不能接受把所有东西丢进神经网络里，然后让它自己整理”** 这种套路。

    我打印了几篇Yann LeCun的旧论文，然后脱机工作，假装自己正身处某地的山间小屋，但现实是——我还是偷偷在YouTube上看了不少
    **斯坦福CS231N** 的视频，并从中学到了很多东西。我一般很少看这种演讲视频，会觉得有点浪费时间，但这样“见风使舵”的感觉也不赖。

    个人体验而言， 这是高效的一周，因为我把书本上的知识固化成了真实经验 。我的实践模式也很常规：
    
        **先用hacky代码写一版，再根据视频教程重写一个全新的、整洁的版本，然后两者交叉检查，不断优化。**

    我曾在反向传播上反复跌倒了好几次，最后得出的经验是比较数值差异非常重要！有趣的一点是，即使每个部分好像都错得离谱，
    神经网络似乎还是能正常训练的，甚至只要大多数时候符号是正确的，它就能不断进步。

    如果要说这一周的学习有什么最精彩的心得，那应该就是神经网络非常简单，它只需寥寥几行代码就能实现突破性的进步。
    我觉得这和图形学中的光线追踪有异曲同工之妙，只要我们有足够的数据、时间和耐心，追踪与光学表面发生交互作用的光线，
    得到光线经过路径的物理模型，我们就能生成最先进的图像。

大模型的课程： `Open AI传奇研究员Andrej Karpathy教你理解和构建GPT Tokenizer <https://www.bilibili.com/video/BV11x421Z7QZ/?vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_ 

AMD GPU对PyTorch的支持
-----------------------

| ADM ROCm 官网： https://rocm.docs.amd.com/en/latest
| PyTorch社区关于ROCm的讨论: https://github.com/pytorch/pytorch/issues/106608
| 结论就是，截至当前(2024.4), PyTorch对Windows ROCm支持还不行(包括WLS2)，只支持物理机装Ubuntu，还有些小问题。

| 微软出的 DirectML 平台：
| https://learn.microsoft.com/zh-cn/windows/ai/directml/gpu-pytorch-windows
| https://learn.microsoft.com/zh-cn/windows/ai/directml/gpu-pytorch-wsl?source=recommendations

没有明确说支持AMD的显卡驱动，支持ROCm，看来 PyTorch 对 AMD显卡当前支持还不友好。如果是A卡，只能先跑CPU版本了。

PyTorch入门
-----------------

| https://github.com/pytorch/examples
| https://pytorch.org/tutorials/beginner/pytorch_with_examples.html
| https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html

官方的教程例子质量挺高的。

第一个例子手写数字识别
^^^^^^^^^^^^^^^^^^^^^^

| PyTorch有官方样例代码库： https://github.com/pytorch/examples/blob/main/mnist/main.py ，用的是封装好的CNN。
| B栈这个没用什么库，更方便理解底层实现： `10分钟入门神经网络 PyTorch 手写数字识别 <https://www.bilibili.com/video/BV1GC4y15736/?spm_id_from=333.337.search-card.all.click&vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_ 

详细看下入门代码。