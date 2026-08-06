.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

AI 学习笔记
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
    **『我还不能接受把所有东西丢进神经网络里，然后让它自己整理』** 这种套路。

    我打印了几篇Yann LeCun的旧论文，然后脱机工作，假装自己正身处某地的山间小屋，但现实是——我还是偷偷在YouTube上看了不少
    **斯坦福CS231N** 的视频，并从中学到了很多东西。我一般很少看这种演讲视频，会觉得有点浪费时间，但这样『见风使舵』的感觉也不赖。

    个人体验而言， 这是高效的一周，因为我把书本上的知识固化成了真实经验 。我的实践模式也很常规：

        **先用hacky代码写一版，再根据视频教程重写一个全新的、整洁的版本，然后两者交叉检查，不断优化。**

    我曾在反向传播上反复跌倒了好几次，最后得出的经验是比较数值差异非常重要！有趣的一点是，即使每个部分好像都错得离谱，
    神经网络似乎还是能正常训练的，甚至只要大多数时候符号是正确的，它就能不断进步。

    如果要说这一周的学习有什么最精彩的心得，那应该就是神经网络非常简单，它只需寥寥几行代码就能实现突破性的进步。
    我觉得这和图形学中的光线追踪有异曲同工之妙，只要我们有足够的数据、时间和耐心，追踪与光学表面发生交互作用的光线，
    得到光线经过路径的物理模型，我们就能生成最先进的图像。

经典视频教程:

- `Open AI传奇研究员Andrej Karpathy教你理解和构建GPT Tokenizer <https://www.bilibili.com/video/BV11x421Z7QZ/?vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_
- `10分钟入门神经网络 PyTorch 手写数字识别 <https://www.bilibili.com/video/BV1GC4y15736/?spm_id_from=333.337.search-card.all.click&vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_

PyTorch
-------

- https://github.com/pytorch/examples
- https://pytorch.org/tutorials/beginner/pytorch_with_examples.html
- https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html

CNN
---

基于 https://github.com/pytorch/examples/blob/main/mnist/main.py 来详细解析:

MNIST 是 28 x 28 的灰度手写数字图片；每张图的标签是 ``0`` 到 ``9`` 之一。这个任务很小，适合把 CNN 的数据流、
反向传播和训练/推理状态一次走通。下面的程序保留官方样例的两层卷积、一次池化和两层全连接结构；为了少引入一个概念，
它把官方的 ``log_softmax() + nll_loss()`` 改成了等价的 ``CrossEntropyLoss``。后者接收 ``logits``（未归一化分数），
所以模型末尾不要手写 ``softmax``。

把下面内容保存为 ``mnist_cnn.py``。先按 `PyTorch 安装页 <https://pytorch.org/get-started/locally/>`_ 为自己的 CPU 或 GPU
安装 ``torch`` 和 ``torchvision``，然后执行 ``python mnist_cnn.py``。首次运行会把 MNIST 下载到当前目录的 ``data/``。

.. code-block:: python

    import torch
    from torch import nn
    from torch.nn import functional as F
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms


    # ``cuda`` 也覆盖 PyTorch 的 ROCm 后端；没有可用加速器时退回 CPU。
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(0)


    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            # (B, 1, 28, 28) -> (B, 32, 26, 26)
            self.conv1 = nn.Conv2d(in_channels=1, out_channels=32,
                                  kernel_size=3)
            # (B, 32, 26, 26) -> (B, 64, 24, 24)
            self.conv2 = nn.Conv2d(in_channels=32, out_channels=64,
                                  kernel_size=3)
            self.dropout1 = nn.Dropout(p=0.25)
            self.fc1 = nn.Linear(64 * 12 * 12, 128)
            self.dropout2 = nn.Dropout(p=0.5)
            self.fc2 = nn.Linear(128, 10)

        def forward(self, x):
            x = F.relu(self.conv1(x))        # (B, 32, 26, 26)
            x = F.relu(self.conv2(x))        # (B, 64, 24, 24)
            x = F.max_pool2d(x, kernel_size=2)  # (B, 64, 12, 12)
            x = self.dropout1(x)
            x = torch.flatten(x, start_dim=1)   # (B, 9216)
            x = F.relu(self.fc1(x))          # (B, 128)
            x = self.dropout2(x)
            return self.fc2(x)               # (B, 10)，每类一个 logit


    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    train_set = datasets.MNIST("data", train=True, download=True,
                               transform=transform)
    test_set = datasets.MNIST("data", train=False, download=True,
                              transform=transform)
    train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=1_000)

    model = Net().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)


    def train_one_epoch():
        model.train()  # 启用 Dropout，训练时每批随机屏蔽一部分激活。
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()       # PyTorch 默认累加梯度，故每批清一次。
            logits = model(images)      # 前向传播，同时建立自动求导图。
            loss = criterion(logits, labels)
            loss.backward()             # 从标量 loss 反向填充每个参数的 .grad。
            optimizer.step()            # 用梯度原地更新参数。
            total_loss += loss.item() * images.size(0)
        return total_loss / len(train_set)


    @torch.inference_mode()
    def evaluate():
        model.eval()  # 关闭 Dropout；本例没有 BatchNorm，但它也依赖此状态。
        correct = 0
        for images, labels in test_loader:
            logits = model(images.to(device))
            prediction = logits.argmax(dim=1)
            correct += (prediction == labels.to(device)).sum().item()
        return correct / len(test_set)


    for epoch in range(1, 6):
        loss = train_one_epoch()
        accuracy = evaluate()
        print(f"epoch={epoch}: loss={loss:.4f}, accuracy={accuracy:.2%}")

输入、形状与卷积
^^^^^^^^^^^^^^^^

深度学习框架把一批图片表示为四维张量 ``(B, C, H, W)``：``B`` 是 batch 中图片数，``C`` 是通道数，``H``、``W`` 是高和宽。
因此 DataLoader 取出 64 张 MNIST 图后，``images.shape`` 为 ``(64, 1, 28, 28)``；标签 ``labels.shape`` 为 ``(64,)``，
其中每个元素是类别编号，而不是 one-hot 向量。批处理不是算法上的要求，而是让矩阵乘法和 GPU 并行有足够工作可做的工程折中。

``Conv2d(1, 32, 3)`` 有 32 个可学习的 3 x 3 滤波器。每一个滤波器跨越全部输入通道，在图像上滑动，产生一个特征图；所以
输出通道从 1 变成 32。这里没有 padding、stride 默认为 1，空间尺寸的公式是 ``H_out = H_in - K + 1``，故 28 变 26，
第二层再由 26 变 24。卷积的关键不是『识别边缘』这个特定效果，而是 **局部连接和权重共享**：同一组 3 x 3 权重用于所有位置，
于是参数量不随图片面积线性增长，也让模型能在不同位置寻找同一种局部模式。

``ReLU(x) = max(0, x)`` 是逐元素非线性。没有它以及后续非线性，任意层线性卷积/全连接的组合仍可折叠成一层线性变换，
表达能力不会随层数实质增加。``max_pool2d(..., 2)`` 将每个不重叠的 2 x 2 区块取最大值，使 24 x 24 变成 12 x 12；
它降低后续计算量，也使小幅平移的影响较小，但同时不可逆地丢掉了空间细节。

``flatten(x, 1)`` 保留第 0 维的 batch，把每张图的 ``64 * 12 * 12 = 9216`` 个数拼成特征向量。因此 ``fc1`` 的输入必须是
``9216``，这正是最常见的 CNN 形状错误来源。可先在 ``forward`` 中临时打印 ``x.shape``，或用 ``assert x.shape[1:] ==
(64, 12, 12)`` 定位问题；不要凭感觉修改 ``Linear`` 的输入维度。

模型、损失与预测
^^^^^^^^^^^^^^^^^^^^

``fc2`` 输出的 ``(B, 10)`` 不是概率，而是每个类别的 logit，即可比较的原始分数。``argmax(dim=1)`` 选最大分数的下标，
正好就是预测数字。``CrossEntropyLoss`` 在内部完成数值稳定的 ``log_softmax`` 和负对数似然：它推动正确标签对应的分数高于其他
九类。把 ``softmax`` 后的概率再传给 ``CrossEntropyLoss`` 是常见错误，会改变其数学含义并损失数值稳定性。

参数并不只在卷积层。``conv1`` 有 ``32 * (1 * 3 * 3 + 1) = 320`` 个参数，``conv2`` 有 18,496 个；而 ``fc1`` 约有
118 万个。这也解释了为什么现代 CNN 常继续下采样、使用 global average pooling，或以更紧凑的模块取代巨大的全连接层。
``Dropout`` 在训练时随机置零部分激活，降低对特定神经元组合的依赖；在评估时必须关闭，所以 ``model.train()`` 与
``model.eval()`` 不是装饰性调用，而是模型状态切换。

训练循环的实际语义
^^^^^^^^^^^^^^^^^^^^^^

一次 batch 的执行顺序是：从 DataLoader 得到 CPU 张量，``.to(device)`` 将该 batch 复制到 CPU/GPU；``model(images)``
执行前向计算并记录依赖图；``loss.backward()`` 依据链式法则反向遍历该图，累积每个 ``Parameter.grad``；最后
``optimizer.step()`` 用 Adam 的状态和梯度更新参数。``zero_grad()`` 必不可少，因为 PyTorch 的梯度累加是有意设计的，
它可支持将多个小 batch 累积为一个更大的有效 batch。

训练集的 ``shuffle=True`` 会在每轮重排样本，避免同类样本连续出现导致梯度带偏。测试集不用 shuffle，因为这里只关心总准确率。
``torch.inference_mode()`` 让验证过程不构建反向传播图，因而节省内存和调度开销；它和 ``model.eval()`` 解决的是不同问题：
前者控制自动求导，后者控制 Dropout、BatchNorm 等模块的行为。

可以把整个程序看成两条相交的数据流：

.. code-block:: text

    图片 + 标签 -> DataLoader -> device -> Net -> logits -> loss
                                                   |         |
                                                   |         v
                                      预测 <- argmax      backward
                                                                 |
                                                                 v
    Parameter <--------------------------- optimizer.step <- .grad

先确保这份小程序能在 CPU 上完整运行、准确率逐轮提高，再观察 GPU 利用率或把 ``num_workers``、``pin_memory`` 等数据加载参数
作为性能实验的变量。它们优化的是主机到设备的供给链路，不改变 CNN 的数学结果；过早调整它们通常只会把学习问题和性能问题混在一起。

用数学描述网络与训练
^^^^^^^^^^^^^^^^^^^^^^^^

不必先读下标很多的卷积公式。先把网络理解为一个可调的计算器：输入一张图片，经过一串固定种类的运算，最后输出 10 个数。
这 10 个数分别对应『它像 0、像 1、……、像 9』的程度。搭建 ``Net``，就是写出这串运算；训练，就是不断调整其中的可调数字，
让正确数字的分数变大。

一张图片怎样变成十个分数
""""""""""""""""""""""""""""

下面是 ``forward`` 的数学版。``->`` 表示上一步的输出成为下一步的输入；括号内是每张图片的数据形状：

.. code-block:: text

    x (1, 28, 28)
      -> 卷积 + ReLU (32, 26, 26)
      -> 卷积 + ReLU (64, 24, 24)
      -> 最大池化     (64, 12, 12)
      -> flatten      (9216)
      -> 全连接 + ReLU (128)
      -> 全连接        (10) = s

卷积的一个输出值，本质上只是一个小区域的加权求和。假设当前看到的是 3 x 3 的九个像素 :math:`x_{u,v}`，卷积核中有九个
可训练权重 :math:`w_{u,v}`，再加一个偏置 :math:`b`：

.. math::

    z = b + \sum_{u=0}^{2}\sum_{v=0}^{2} w_{u,v}x_{u,v}.

也就是说，逐项相乘，再全部相加。卷积核在图片的每个位置重复做同一件事，所以同一组 :math:`w` 能学会在任意位置响应某种局部图案，
例如一条笔画的边缘。代码的第一层有 32 组这样的权重，故产生 32 张特征图；第二层有 64 组。多通道时只是把所有输入通道的
加权和继续相加，计算规则没有变化。

``ReLU`` 也很简单：:math:`\operatorname{ReLU}(z)=\max(0,z)`，负数变成 0，正数原样通过。最大池化则把相邻 2 x 2 的四个
数留下最大的一个；它没有参数，只是压缩位置尺寸。``flatten`` 也没有计算含义，只是把 :math:`64\times12\times12` 个数按顺序
排成长度 9216 的数组。

最后两层全连接就是更大规模的加权求和：

.. math::

    h = \operatorname{ReLU}(Aq+a), \qquad s = Bh+b.

其中 :math:`q` 是长度 9216 的 flatten 结果，:math:`h` 是 128 个中间特征，:math:`s` 是 10 个类别分数。矩阵乘法
:math:`Aq` 可看作一次并行计算 128 个『加权求和』。卷积核、:math:`A`、:math:`B` 和各层偏置合起来，就是模型参数 :math:`\theta`。
``Dropout`` 仅在训练时随机把部分中间数置零，以免模型过度依赖少数特征；评估时关闭它。

怎样判断这次答案错得多不多
""""""""""""""""""""""""""""""

假设某张图片的真实标签是 3，网络给出的 10 个分数是 :math:`s=(s_0,\ldots,s_9)`。softmax 把它们变成和为 1 的概率：

.. math::

    p_k = \frac{e^{s_k}}{\sum_{j=0}^{9}e^{s_j}}.

我们只关心正确类别的概率 :math:`p_3`。该图片的损失是：

.. math::

    L = -\log p_3.

若模型给数字 3 的概率是 0.9，损失约为 0.105；若概率是 0.1，损失约为 2.303。也就是说，**答得越自信且正确，损失越小；
自信地答错，损失很大**。``CrossEntropyLoss`` 正是在一个 batch 内对每张图片的这个损失取平均。它内部会完成 softmax，
所以代码传入的是原始分数 ``logits``，而不是已经 softmax 的概率。

怎样从错误中调整参数
""""""""""""""""""""""

把所有可训练数字合并记为 :math:`\theta`，例如某个卷积核的一个权重，或全连接矩阵里的一个元素。训练的核心更新只有一行：

.. math::

    \theta \leftarrow \theta - \eta\frac{\partial L}{\partial\theta}.

这里 :math:`\frac{\partial L}{\partial\theta}` 是『把这个参数略微增大时，损失会向哪个方向、变化多快』的测量值；
:math:`\eta` 是学习率，控制这一步走多远。减号表示沿着让损失下降的方向移动。``loss.backward()`` 用链式法则算出所有参数的
这个导数；``optimizer.step()`` 则执行更新。本例使用的 Adam 是梯度下降的实用变体：它还会根据各参数近期梯度的大小调整步长，
但不改变『根据损失的导数修改参数』这一主线。

对应到训练循环，程序逻辑只有下面四步：

.. code-block:: text

    logits = model(images)            # 按前面的计算图得到 s
    loss = criterion(logits, labels)  # 用真实标签计算平均 L
    loss.backward()                   # 计算每个参数的 ∂L/∂θ
    optimizer.step()                  # 按梯度更新参数 θ

每个 batch 重复这四步。``zero_grad()`` 放在 ``backward()`` 前，是因为 PyTorch 默认会把本次导数加到上次的 ``.grad`` 中；
通常每个 batch 都希望从零开始计算，才需要清空。经过许多 batch 后，参数逐步变成能让正确类别分数更高的一组值。

把一个卷积手算一遍
""""""""""""""""""""

先只看一个卷积核、一个位置，不考虑整张图片。假设它看到的 3 x 3 像素块和当前卷积核如下，偏置 :math:`b=-1`：

.. code-block:: text

    像素块 x                 卷积核 w
    1  0  2                  1  0  1
    0  1  0                  0  1  0
    2  0  1                  1  0  1

这一次的卷积输出是对应位置相乘后再求和：

.. math::

    z = -1 + 1\times1 + 0\times0 + 2\times1
        + 0\times0 + 1\times1 + 0\times0
        + 2\times1 + 0\times0 + 1\times1 = 6.

经过 ReLU 仍为 6。若计算结果是 :math:`-2`，ReLU 的输出就为 0。然后卷积核向右移动一个像素，取到另一块 3 x 3 数据，
用 **完全相同的九个权重** 再算一次；从左到右、从上到下扫完，就得到一张特征图。这和普通全连接层的根本区别在于：
全连接层会给每个输入位置独立的权重，卷积层则复用这九个权重。

上例的数字并不是预先设计出来的『边缘检测规则』。训练开始时它们通常是随机小数；反向传播会把有助于降低损失的权重慢慢推大，
无用或有害的权重推小。最终某些卷积核常会对边缘、笔画拐角或局部纹理有反应，但这是数据和损失共同塑造的结果。

形状、通道和 batch
""""""""""""""""""""

形状 ``(B, C, H, W)`` 可以从数据布局理解：``B`` 是一次处理的图片数，``C`` 是每个像素位置包含几个数，``H``、``W`` 是二维坐标。
MNIST 是灰度图，所以一张图为 ``(1, 28, 28)``；普通 RGB 图片会是 ``(3, H, W)``，三个通道分别是红、绿、蓝。DataLoader 将
64 张 MNIST 图拼成 ``(64, 1, 28, 28)``，并不是把它们接成一张大图，而是在最前面添加一个可并行计算的 batch 维。

第一层的 ``Conv2d(1, 32, 3)`` 表示 32 个不同的 3 x 3 核；每个核读一个灰度通道，因此输出为 ``(32, 26, 26)``。
尺寸从 28 到 26 的原因很具体：不补边时，3 x 3 窗口最左能从 0 开始，最右只能从 25 开始，共有 ``28 - 3 + 1 = 26`` 个位置。
若输入是 RGB，``Conv2d(3, 32, 3)`` 的每个输出核会有三张 3 x 3 权重片，分别处理 R/G/B 后相加；它不是先独立选一个颜色通道。

``max_pool2d`` 的含义也可以手算。一个 2 x 2 区域为 ``[[1.2, -0.3], [0.7, 0.4]]`` 时，输出是 ``1.2``。它只选择值，不做
乘法或学习，故不增加参数；代价是之后无法知道这个最大值原来位于四个位置中的哪一个。CNN 用这种有损压缩换取更少的后续计算，
以及对几个像素范围内小位移更稳定的响应。

把一次训练更新手算一遍
""""""""""""""""""""""""""

反向传播不需要先被当作神秘机制。假设先只观察一个参数 :math:`\theta`，当前值是 0.50，计算得到的梯度为
:math:`\frac{\partial L}{\partial\theta}=4`，学习率 :math:`\eta=0.01`。一次普通梯度下降后：

.. math::

    \theta_{new}=0.50-0.01\times4=0.46.

这里正梯度表示『把该参数增大一点，损失会增大』，所以更新把它减小。若梯度为 :math:`-4`，更新会得到 0.54，表示应增大该参数。
真实 CNN 有约 120 万个参数；``backward()`` 正是在一次调用中为每一个参数求出这样的梯度，``step()`` 再统一更新它们。

数值微分能帮助理解导数的含义：若把参数从 :math:`\theta` 改成 :math:`\theta+\epsilon`，可以用
:math:`[L(\theta+\epsilon)-L(\theta)]/\epsilon` 近似它的梯度。这样逐个参数试探在 CNN 中太慢；自动求导利用计算图和链式法则，
一次反向遍历就能复用中间结果求出全部梯度。这正是 ``loss.backward()`` 相比手写有限差分的价值。

一个 batch 的损失是多张图片损失的平均值。例如两张图片的损失分别是 0.1 和 2.3，batch loss 为 1.2。用 batch 的平均梯度更新，
是对整个训练集梯度的带噪声近似：batch 越大，估计通常越稳定；batch 越小，单步更快但抖动更明显。``shuffle=True`` 让每个 batch
混合不同样本，避免数据文件本身的排序系统性影响更新方向。

训练指标要怎样看
""""""""""""""""""

损失和准确率回答不同问题。准确率只看 ``argmax`` 是否等于标签，因而把正确类别从 0.51 提升到 0.99 不会改变这一个样本的准确率；
交叉熵会继续奖励这种更确定的正确预测，也会严厉惩罚『很确定但错了』的预测。因此训练时通常同时看 ``loss`` 和 ``accuracy``。

MNIST 有 10 个类别，完全随机猜测的长期平均准确率约为 10%。刚开始训练时，训练集和测试集准确率都应从接近该水平逐步提升。
若训练集持续变好而测试集变差，说明模型开始记住训练样本的细节而不善于泛化，这叫过拟合；``Dropout``、更多数据或数据增强等方法
都在缓解这个问题。测试阶段调用 ``model.eval()`` 和 ``torch.inference_mode()``，是为了关闭训练专用的随机性，并且不再建立求梯度的
计算图；这让测试结果稳定，也避免无用的内存开销。

Transformer
-----------

Introduction
^^^^^^^^^^^^

Transformer 可以先理解成一叠重复的『读上下文，再加工自己』的模块。它不靠 RNN 那样按顺序把状态一路传下去，也不像 CNN
只看固定邻域；每个 token 都能根据当前任务，从序列中的其他 token 取回有用信息。因此它特别适合处理语言中相距很远的关联。

.. code-block:: text

    文本 -> token -> token embedding + 位置信息
         -> [self-attention -> 前馈网络] 重复 N 层
         -> logits -> 下一个 token 的概率

.. image:: pic/transformer-architecture-attention-is-all-you-need.png
   :scale: 35%
   :align: left
   :alt: Attention Is All You Need 论文中的 Transformer encoder-decoder 结构图

`Attention Is All You Need <https://arxiv.org/abs/1706.03762>`_ 的 Figure 1：左侧是 encoder，右侧是 decoder；decoder 比 encoder
多出 masked self-attention 和读取 encoder 输出的 cross-attention。后面的 decoder-only 模型保留的正是右侧中不依赖左侧 encoder
的生成主干。

位置信息
""""""""""""

位置信息指的是：每个 token 在序列中的相对或绝对位置。

例如 ``我 喜欢 你`` 与 ``你 喜欢 我`` 包含相同的三个 token，但主语和宾语互换，含义相反。若只有 token embedding，两个
序列只是同一组向量的不同排列，模型不知道 ``我`` 在第 1 个位置还是第 3 个位置。绝对位置编码可以把第 0、1、2 个位置的向量
分别加到 ``我``、``喜欢``、``你`` 的 embedding 上；相对位置则直接告诉 attention：『这个 token 在我左边 1 格』或『右边 2 格』。

前馈网络
""""""""""""

前馈网络：每个 token 独立加工自己，通常是两层全连接加非线性。它不会让 token 之间交换信息，但能让模型学习更复杂的特征组合。

可以把 attention 想成一次小组讨论：每个 token 先听其他 token 发言，把有用信息带回来；FFN 则像它回到自己座位后，共用的一台
小加工机。以 ``我 喜欢 苹果`` 为例，``苹果`` 经 attention 已拿到『谁喜欢它、喜欢这个动作』等上下文线索；FFN 不再询问其他
token，而是把『苹果本身 + 刚得到的关系』组合、变换成更适合下一层使用的表示，例如更明显地携带『这里像宾语』的特征。

第一层全连接可以把向量暂时展开，像同时尝试许多种特征组合；非线性决定哪些组合保留；第二层再压回原来的维度。所有 token
共用同一台 FFN 加工机，但带入的上下文不同，产物自然不同。简记为：**attention 负责收集信息，FFN 负责消化信息**。

编码、解码与 embedding
^^^^^^^^^^^^^^^^^^^^^^^

这三个词容易混在一起，因为它们都可被翻译成『编码/解码』，但处在不同层次。先把一段文字送入 GPT 的数据流拆开：

.. code-block:: text

    『我喜欢苹果』
        -> tokenizer.encode()  -> token IDs，例如 [314, 98, 271]
        -> embedding lookup    -> (T, d_model) 的浮点向量
        -> Transformer blocks  -> 含上下文的 (T, d_model) 向量
        -> vocab linear + softmax -> 下一个 token 的概率
        -> 采样/argmax         -> 新 token ID
        -> tokenizer.decode()  -> 显示给人的文字

``tokenizer.encode`` 的本质是按 tokenizer 的规则将文本切成词表定义的 token，并查表映射为整数 token ID；token 是离散的符号单元，
ID 是它在词表中的编号/index，而不是 token 本身，也不表示数值大小或语义距离。

词表不是业界统一标准，更不是类似 RFC 的协议；它是 **训练某个 tokenizer 时产生的模型资产**。开发者先选取有代表性的文本语料，
确定 normalizer、预切分规则和 BPE、WordPiece 或 Unigram 等算法，再指定词表大小、最低频率与 special token。以 BPE 为例，
它从较小的基础符号集合出发，反复把语料中常共同出现的片段合并，直到达到目标词表规模；因此语料、算法参数或 special token
不同，最终的『token -> ID』表就会不同。

因此，token 本身不是模型使用的浮点表示。词表的一个条目通常是类似『苹果』、``ing`` 或 ``<|im_end|>`` 的文本/字节片段，
外加它的整数 ID；浮点数存放在另一张可训练的 embedding 矩阵中。Unigram 一类 tokenizer 还可能为条目保存一个浮点评分，
但它只用于选择切分方案，不是 token 本身的语义向量。若词表大小为 ``V``、隐藏维度为 ``d_model``，矩阵形状为
``(V, d_model)``。用 ID ``314`` 查 embedding 矩阵的第 314 行，得到的不是一个标量，而是一个长度为 ``d_model`` 的浮点 **向量**：

.. code-block:: text

    词表：       ID 314 -> 『苹果』             # 符号/文本，不含浮点数
    embedding：  第 314 行 -> [0.12, -0.31, ...] # d_model 个浮点数构成的向量

这个向量是该 token 进入 Transformer 前的初始表示；加上位置信息并经过多层 attention/FFN 后，它会变成依赖上下文的向量。
所以同一个 token 在不同句子中的最终表示可以不同，但词表 ID 不变。不要把『词表』和『embedding 矩阵』混成一张表：前者回答
『这个 ID 对应哪个符号？』，后者回答『模型当前如何用一组浮点数表示这个符号？』。

发布『开放权重』模型时，完整可运行的发布包通常不只包含 ``*.safetensors`` 权重分片，也会带上 tokenizer 与配置；否则使用者无法
把文本转换成模型 embedding 所期待的 ID。以官方 `Qwen2.5-7B-Instruct 文件列表 <https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/main>`_
为例，除权重和 ``config.json`` 外，还包含 ``tokenizer.json``、``tokenizer_config.json``、``vocab.json`` 与 ``merges.txt``。
其中 ``tokenizer.json`` 是 Fast Tokenizer 的完整序列化描述；``vocab.json`` 是 token 到 ID 的映射，``merges.txt`` 是 BPE 的合并规则；
``tokenizer_config.json`` 则说明 tokenizer 类型、special token 和聊天模板等运行约定。

`DeepSeek-V3 的官方文件列表 <https://huggingface.co/deepseek-ai/DeepSeek-V3/tree/main>`_ 采用另一种打包方式：根目录提供
``tokenizer.json`` 与 ``tokenizer_config.json``，而不单独列出 ``vocab.json``/``merges.txt``；前者已携带完整 tokenizer 描述，
后者包含 ``LlamaTokenizerFast`` 类型、特殊 token 与聊天模板。两种形式都能让推理框架复原相同的『文本 -> ID』规则，文件名不同
不代表 tokenizer 的地位不同。

这里也要区分术语：这类发布通常称为 **开放权重**，不等于公开预训练语料，也不必然等于代码和所有资产都采用同一种开源许可证。
Qwen2.5-7B-Instruct 在其模型页标注为 Apache-2.0；DeepSeek-V3 的官方仓库代码使用 MIT，而 Base/Chat 模型权重另受
Model License 约束。下载或再分发前，应分别查看权重、代码与 tokenizer 文件对应的许可证。

这个词表及其切分规则会随 checkpoint 一起保存，例如 ``tokenizer.json``，有时拆为 ``vocab``、``merges`` 和配置文件。它必须与
模型的 embedding 矩阵和输出词表严格配套：ID 为 314 时，模型只把它解释为第 314 行对应的那个 token。不同模型可以有意复用
同一个 tokenizer，但不能默认互换 tokenizer 或直接复用 ID；否则同一串整数会查到错误的 token 与 embedding，模型输入的语义随即错位。

从概念上说，token 是 tokenizer 词表中的 **离散符号**。`Tokenizer API <https://huggingface.co/docs/tokenizers/main/api/tokenizer>`_
的 ``id_to_token`` 返回字符串，``token_to_id`` 返回整数；因此它通常能显示为文本，但不应机械理解为原始输入中一个完整的 UTF-8
子串。normalizer 可先改变 Unicode 表示，WordPiece 会用 ``##`` 标记续接片段，byte-level/byte-fallback tokenizer 还可能以
字符或 ``<0xNN>`` 形式表示原始字节，special token 则根本不对应用户输入片段。只有 embedding lookup 之后，这个离散符号才变为
可做矩阵运算的浮点向量；`ByteFallback 文档 <https://huggingface.co/docs/tokenizers/main/en/api/decoders#bytefallback>`_ 展示了
字节 token 如何在解码时才重新组合为 UTF-8 文本。

所以 token 不是自然语言意义上的『最小词汇片段』，而是相对于当前 tokenizer 词表和算法选出的一个片段。它可能恰好是完整词，
也可能是词的一部分、单个字符、一个或多个字节，或特殊控制符。例如同一个英文长词可被不同词表切成不同的子词组合；一个中文词也
可以是一个 token、多个汉字 token，或与相邻标点/空白按规则组合的片段。所谓『最小』只表示 tokenizer 已选定该 token 后不会在
这一次 encode 中继续拆分它，并不表示它是语言学上不可再分的最小单位。

.. attention::

   **token ID 是整数索引，不是 float。** 输入模型前，它的形状通常是 ``(B, T)``，元素是词表行号；``[314, 98, 271]`` 的
   数据类型可以是 ``int32`` 或 ``int64``，但不能是 ``float16`` 或 ``float32``，否则 ``314.0`` 既不是稳定的数组下标，也会暗示
   ID 之间存在可计算的大小和距离关系。PyTorch 的 ``nn.Embedding`` 当前接受 ``IntTensor`` (int32) 或 ``LongTensor`` (int64)
   作为索引；教材和许多 PyTorch/Hugging Face 训练代码仍常将 ``input_ids`` 统一为 ``torch.long`` (int64)。

   从存储角度说，常见词表远小于 :math:`2^{31}`，int32 足以表示 token ID，推理引擎也可能在内部使用 int32 以节省带宽；但输入
   ID 相比 embedding、KV cache 和激活所占内存很小，故通用训练接口更看重兼容性而常用 int64。不要改用 unsigned int：主流
   ``Embedding`` 接口定义的是有符号 int32/int64，且 uint 在许多张量算子中的支持较受限。

   真正参与矩阵乘法、attention 和反向传播的是查表后的 embedding、权重和激活，它们是浮点数。当前的大模型训练/推理常用 mixed
   precision：计算和大部分张量使用 BF16 或 FP16 以节省显存和提高吞吐，部分累加、归一化或优化器状态保留 FP32 以维持数值稳定；
   具体 dtype 取决于硬件和框架。可记作：**ID 用整数作地址，embedding 之后才用浮点数作计算。**

**tokenizer 编码/解码** 是文本格式转换。``encode`` 先按 tokenizer 的规则把 Unicode 文本切成词表定义的离散符号单元，
这些单元才是严格意义上的 token；然后查词表，把每个 token 映射为对应的整数 token ID。因而 ID 是 token 在词表中的编号/index，
不是 token 本身，也不是它的数值特征；日常讨论中常把 ID 或序列位置也简称为 token，读资料时需看上下文。token 也不必是自然语言
的『最小单位』：BPE 等子词 tokenizer 会根据词表把『苹果』切成一个或多个片段，英文长词也可能拆开，另有表示句子边界或角色的
special token。不同 tokenizer 的词表和切分规则不同，同一段文本得到的 ID 序列也可能不同。

``decode`` 将 ID 序列按同一词表拼回文本。ID 只是编号，``314`` 比 ``98`` 大没有语义上的『更接近』；模型不能直接对离散整数做
有意义的梯度计算，所以接下来才是 **token embedding**：从一张可训练矩阵中按 ID 取出一行长度为 ``d_model`` 的浮点向量。训练会让
在相似上下文出现的 token 向量形成可复用的几何模式；再加上前面介绍的位置信息，才得到 Transformer 的初始输入。

**Transformer encoder/decoder** 则是网络结构的命名，并不等于 ``tokenizer.encode/decode``。经典的 encoder-decoder Transformer
常用于翻译：encoder 不看未来限制地读取完整源句，输出每个源 token 的上下文表示；decoder 逐 token 生成目标句，既用 causal
self-attention 看已生成的目标 token，又通过 cross-attention 读取 encoder 的源句表示。

.. code-block:: text

    encoder-decoder：源文本 -> encoder -> 源句表示
                                  ^          |
    目标文本 <--- tokenizer.decode <- decoder -+ 逐 token 生成

GPT 是 **decoder-only** 模型：它没有单独的 encoder，prompt 和已生成的 token 一起放入带 causal mask 的 decoder，持续预测下一个
token。BERT 一类则是 **encoder-only**：它可双向读取完整输入，适合抽取、分类或获得文本表示，但原生结构不按 GPT 的方式逐 token
生成。故阅读模型资料时，先问清『encode/decode』说的是 tokenizer 的格式转换，还是 Transformer 的 encoder/decoder 模块。

什么是 decoder-only
""""""""""""""""""""

这里的正确术语是 **decoder-only**，不是『只做 tokenizer.decode()』。它指模型结构只保留经典图中 decoder 的自回归生成路径：
删除左侧 encoder，也删除 decoder 中读取 encoder 输出的 cross-attention；保留 token embedding、位置编码、masked self-attention、
FFN、残差/归一化以及输出到词表的 linear + softmax。因此它只需要一串 token 作为输入：用户的 prompt 是已知前缀，模型在其后续写。

.. code-block:: text

    完整 encoder-decoder：源句 -> encoder -> cross-attention -> decoder -> 目标句
    decoder-only（GPT）：   prompt + 已生成 token -> masked decoder -> 下一个 token

causal mask 是关键：位置 ``t`` 只能读取 ``0..t``，不能偷看将来 token。训练时，可以把一整段序列并行送进模型，用 mask 保持这个限制，
令每个位置预测右移一格的目标；推理时才是真正的逐步循环：预测一个 token，把它接到末尾，再预测下一个。虽然没有 encoder，最后一个
位置仍能通过多层 masked self-attention 读取完整 prompt 和全部已生成历史，所以能回答问题、总结、写代码；只是它没有为『输入句』
单独建立可双向读取的 encoder 表示。

这也解释了名称中的 decoder：它来自经典 encoder-decoder 架构中『根据已有输出自回归地产生下一个符号』的那一半，而不是文件格式
转换意义上的 ``tokenizer.decode``。GPT、Llama、Qwen 和 DeepSeek 等文本生成模型通常属于 decoder-only；机器翻译等需要显式区分
源序列和目标序列的任务，仍可使用完整 encoder-decoder 架构。

Self-attention：每个 token 怎样读取上下文
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

一句文本先被切成 token，并映射为向量；再加入位置信息，否则模型只会看到一组无序的向量。对某个 token 的当前向量，模型会
生成三份表示：Query（它想找什么）、Key（我可被怎样匹配）和 Value（我的内容）。将 Query 与所有 Key 的相似度归一化为权重，
再对 Value 加权求和，就得到包含上下文的新表示：

.. math::

    A = \operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right),
    \qquad H = AV.

这里的每一行权重表示『当前 token 应从哪些 token 取多少信息』。multi-head attention 只是并行做多组不同的查询，
让不同 head 可以分别关注指代、语法或远距离关联等不同线索。用于生成的模型还会加 causal mask，禁止当前位置读取未来 token；
而 BERT 一类 encoder 可以同时查看左右两侧上下文。

一个 block、训练与生成
^^^^^^^^^^^^^^^^^^^^^^^^

self-attention 负责让 token 之间交换信息；随后每个 token 独立通过同一个前馈网络（FFN）做非线性变换。两步外侧的 residual
connection 保留原来的信息并帮助深层训练，LayerNorm 则稳定数值。因此可以把一个 block 记成：**attention 负责通信，FFN
负责加工，残差让信息和梯度顺畅通过**。

以 GPT 为例，训练目标通常是『根据前面的 token 预测下一个 token』，用交叉熵让正确 token 的 logit 更高。推理时模型每次选出
一个新 token，再把它接回输入，循环生成文本；已计算过的 Key/Value 会缓存为 KV cache，避免每一步重复读取整段历史。它学到的是
从训练数据中预测后续 token 的规律，而不是天然具备事实校验或可靠推理能力。

核心实现：一个最小的 GPT block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

下面的代码将 `Attention Is All You Need <https://arxiv.org/abs/1706.03762>`_ 的核心算子缩成一个 GPT 式 decoder block。
写法参考了经典的 `The Annotated Transformer <https://nlp.seas.harvard.edu/2018/04/03/attention.html>`_，但省略了 tokenizer、
embedding、位置编码、语言模型输出层和训练循环，只留下『一个 token 怎样读历史，再更新自己』的主干。

.. code-block:: python

    import math

    import torch
    from torch import nn


    class CausalSelfAttention(nn.Module):
        def __init__(self, d_model, n_heads):
            super().__init__()
            assert d_model % n_heads == 0
            self.n_heads = n_heads
            self.head_dim = d_model // n_heads
            self.qkv = nn.Linear(d_model, 3 * d_model)
            self.out = nn.Linear(d_model, d_model)

        def forward(self, x):
            # x: (B, T, C)，T 是 token 数，C 是 d_model。
            batch_size, length, channels = x.shape
            q, k, v = self.qkv(x).chunk(3, dim=-1)

            # (B, T, C) -> (B, n_heads, T, head_dim)
            def split_heads(tensor):
                return tensor.view(batch_size, length, self.n_heads,
                                   self.head_dim).transpose(1, 2)

            q, k, v = map(split_heads, (q, k, v))
            scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)

            # 第 i 个位置只能读取 0..i，不能偷看未来 token。
            causal_mask = torch.ones(length, length, device=x.device,
                                     dtype=torch.bool).tril()
            scores = scores.masked_fill(~causal_mask, float("-inf"))
            weights = scores.softmax(dim=-1)
            context = weights @ v

            # 拼回所有 head，回到 (B, T, C)。
            context = context.transpose(1, 2).contiguous().view(
                batch_size, length, channels)
            return self.out(context)


    class GPTBlock(nn.Module):
        def __init__(self, d_model=64, n_heads=4):
            super().__init__()
            self.norm1 = nn.LayerNorm(d_model)
            self.attention = CausalSelfAttention(d_model, n_heads)
            self.norm2 = nn.LayerNorm(d_model)
            self.ffn = nn.Sequential(
                nn.Linear(d_model, 4 * d_model),
                nn.GELU(),
                nn.Linear(4 * d_model, d_model),
            )

        def forward(self, x):
            x = x + self.attention(self.norm1(x))  # residual connection
            return x + self.ffn(self.norm2(x))     # residual connection


    x = torch.randn(2, 8, 64)  # 2 个序列，每个序列 8 个 token
    print(GPTBlock()(x).shape)  # torch.Size([2, 8, 64])

``self.qkv(x)`` 一次线性变换产生 Q、K、V；拆成多个 head 后，``q @ k.transpose(-2, -1)`` 得到每个 token 对历史位置的打分。
下三角 mask 将未来位置改成负无穷，softmax 后它们的权重为 0；``weights @ v`` 就是『按相关性拿回上下文内容』。最后的 ``out``
混合各个 head 的结果。

``GPTBlock`` 把这一步放进 residual connection，再接逐 token 的 FFN。这里使用常见的 pre-norm 写法：先 LayerNorm，再做
attention 或 FFN；原始论文的完整 Transformer 还包含 encoder、decoder 的 cross-attention 等组件。把多个 block 堆叠起来，
并在前后补上 embedding、位置编码与输出到词表的线性层，才是一个可训练的语言模型。

预训练与后训练
--------------

前面的 GPT block 只规定了『输入 token，预测下一个 token』的计算方式；它本身还不会聊天、遵循指令或拒绝危险请求。把一个基础模型
变成可用助手，通常可概括为两段训练：**预训练让模型从大量文本中学习语言和世界的统计规律；后训练让它在这些能力之上更符合人的任务、
偏好和安全要求**。

.. code-block:: text

    大量原始文本 -> 预训练 -> base model
    指令示范、偏好数据 -> 后训练 -> assistant model
    评测、红队、部署监控 ----------------^ 反复反馈与修正

这不是两套完全不同的网络。通常仍是同一个 Transformer，仍以梯度下降更新参数；主要变化是训练数据、损失函数和『什么算好答案』的定义。
预训练消耗的 token 和计算量通常远大于后训练；后训练的数据量虽小得多，却会显著影响模型对用户呈现出的性格和行为。

.. note::

   **预训练数据不是『下载一堆网页就开始训练』。** 语料通常混合自然语言文档、书籍和新闻、百科/问答、代码、数学与科学材料、
   多语言文本等类型；具体比例取决于目标模型。代码比例较高会增强编程模式，更多高质量多语言材料会改善相应语言，但任何一种来源
   过多都可能让模型的输出分布失衡。规模要以 **token 数** 而不是文件数或 GB 衡量：面向单一领域的实验可从亿到百亿 token
   起步；训练通用 base model 通常会到千亿至数万亿 token。公开的 Llama 3 模型卡报告其预训练使用超过 15 万亿 token，
   但这只是一个实例，不是所有模型的固定配方；参数量、计算预算、数据质量、是否重复训练样本和推理成本都会改变合适的量级。

   准备流程通常是：先确认数据的许可和来源，保存可追溯的原始清单；再解析正文、统一编码和格式、识别语言/领域，进行精确及近似
   去重、质量过滤，并按要求处理隐私信息、恶意代码或不适宜内容；最后按目标比例采样、切分训练/验证/测试集并分片。还要在训练前
   做 benchmark contamination 检查，避免评测题及其答案混入训练集。每一步都应记录输入量、保留率、token 数与版本，否则后续很难
   重现结果，也无法定位能力或偏差来自哪一批数据。

预训练：先学会续写
^^^^^^^^^^^^^^^^^^^^

预训练的原始样本可以是文档、书籍、代码或网页等文本。tokenizer 将文本变为 token 序列 ``x_1, x_2, ..., x_T``；对 decoder-only
语言模型，训练时把前面的 token 作为上下文，要求模型预测下一个 token：

.. math::

    L_{\mathrm{pretrain}} = -\sum_{t=1}^{T-1}
    \log p_\theta(x_{t+1}\mid x_1,\ldots,x_t).

这和 MNIST 中的交叉熵是同一种基本思想：正确 token 的概率越高，损失越小。区别在于分类标签不再是 10 个数字之一，而是词表中
可能的下一个 token；每个位置都能提供一个训练信号。例如文本为 ``猫 喜欢 鱼``，模型依次学习『``猫`` 后可能出现什么』、
『``猫 喜欢`` 后可能出现什么』。在海量、多样的上下文中重复这种任务，模型会逐渐形成词法、语法、代码模式、事实关联和一些
解决问题的策略。

『预测下一个 token』不是把资料库逐句背下来。它学习的是参数中的统计压缩：相似模式共用表示，罕见或矛盾信息也可能被混淆；训练数据
之外的最新事件更不会自动知道。因此 base model 可以续写自然文本，却未必会把问题当成指令、给出结构化回答，或在不确定时如实说明。

.. note::

   **预训练后的 base model 已有能力，但它的接口仍是『续写』。** 给出合适的上下文，它通常能续写连贯文本、概括或改写已给材料、
   翻译常见表达、按示例完成分类/抽取等模式匹配任务，以及补全符合上下文的代码。这些能力来自训练中反复压缩到的语言、代码和知识
   模式；few-shot prompting 就是把少量输入/输出示例放进上下文，让模型续写同一种模式。它并不保证事实正确、计算无误或稳定遵守
   任意格式，因此聊天式指令遵循、工具调用和安全边界仍需要后训练及外部验证。

   常说的『涌现推理』应谨慎理解。较大模型在某些算术、符号和常识基准上，加入展示中间步骤的 chain-of-thought（CoT）提示后，
   成绩会明显提升；这说明模型可以利用生成的中间 token 把复杂任务拆成多步，而不等于已经证明其内部具有可靠、通用的思维过程。
   『能力在某一规模突然出现』的强说法也仍有争议：离散的准确率指标可能把连续的小幅改进显示成阈值跳变。实际判断应看不同规模、
   多个连续指标、未泄漏测试集，以及答案能否被工具或规则核验，而不要只看一段看似合理的推理文字。

后训练：让能力变成可控行为
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

后训练（post-training）是一个总称，不等于某个唯一算法。它常按下面的顺序组合；不同团队会使用不同的数据配比和具体目标：

#. **监督微调（Supervised Fine-Tuning，SFT）**：给模型看 ``用户问题 -> 高质量回答`` 的示范，并继续以交叉熵训练。例如对
   ``解释虚拟内存``，目标回答会直接从解释开始，而不是随机续写网页片段。它教会模型对话格式、任务类型和基本指令遵循。
#. **偏好学习或偏好优化**：对于同一个提示，让标注者或规则比较回答 A、B，记录哪一个更有帮助、更准确或更安全。它关注的是
   『两个都能说通时，人更希望看见哪一个』。
#. **安全与能力评测**：用保留的任务集、对抗提示和人工审查寻找问题，再补充示范或偏好数据，反复训练和评测。评测不是训练损失的
   装饰；它决定哪些失败模式会被发现和修正。

SFT 的一个样本可写成 ``prompt = "把下面内容翻成英文"``、``answer = "..."``。训练时通常将 prompt 和 answer 接在同一
token 序列中，但只（或主要）对 answer 部分计算损失：prompt 是条件，模型应学会生成后面的回答，而不是复述用户问题。

.. note::

   **后训练数据的关键是高质量的行为信号与覆盖面，而不是复制预训练语料的规模。** 常见类型包括：单轮或多轮的
   ``instruction -> answer`` 示范；同一问题下 ``chosen/rejected`` 的偏好对；带有拒答、改写和对抗提示的安全样本；
   工具调用的 ``问题 -> 调用参数 -> 工具结果 -> 回答`` 轨迹；以及独立保留、不能混入训练的能力和安全评测集。人写、专家审核、
   程序可执行验证和模型合成数据都可参与，但合成数据必须抽检、去重并验证，否则会把已有错误反复放大。

   没有『训练成助手需要 N 条数据』的固定答案。一个窄任务可能用数百到数万条高质量示范就有明显变化；通用助手常扩展到数十万、
   数百万甚至更多的样本/对话 token，但仍通常远小于预训练的千亿至数万亿 token。作为历史实例，InstructGPT 论文公开的实验
   使用约 1.3 万条 SFT prompts、3.3 万条偏好 prompts 和 3.1 万条 PPO prompts；这说明相对小而贴近真实使用分布的数据，
   也能显著改变模型行为，不能把它外推成所有现代系统的配方。

   通过后训练，模型更可能把自然语言视为任务、遵守输出格式和角色边界、在多轮对话中维持上下文、按偏好给出更有帮助的回答，
   并在特定风险场景拒绝或改为安全替代方案。工具轨迹还能教会它何时检索、调用 API 或执行代码；但它仍可能选错工具、编造结果，
   而且后训练过强会损伤某些 base model 能力。因此这些能力须用保留评测和真实工具执行来验证，不能由训练名称保证。

偏好怎样进入梯度
^^^^^^^^^^^^^^^^^^

偏好数据常表示为 ``(prompt, chosen, rejected)``：在相同 prompt 下，``chosen`` 是更好的回答，``rejected`` 是较差回答。
只用 SFT 时，模型只看到 chosen；而偏好优化还显式利用『为什么另一个不够好』的比较信号。

一种经典路线是 RLHF（Reinforcement Learning from Human Feedback）：先用偏好对训练 reward model，使它给较好回答较高分；再把
语言模型当作 policy，用强化学习提高 reward，同时加入约束，避免模型为了提高分数而偏离 SFT 模型太远。这里的 reward 是人类偏好的
近似器，不是真理函数；若奖励模型遗漏了事实性或安全性的情况，优化它可能产生 reward hacking，即答案更会讨好评分器、却不一定更好。

DPO（Direct Preference Optimization）则是另一类常用思路：不单独训练 reward model 后再跑强化学习，而是直接让当前模型相对一个
reference model，提高 ``chosen`` 相比 ``rejected`` 的相对概率。概念上，它仍在用偏好把『回答分布』往人希望的方向推；工程流程
通常更直接，但同样依赖偏好数据的覆盖范围与质量。

可以用下面的关系把这些名词串起来：

.. code-block:: text

    SFT：模仿一份好答案
    偏好数据：在 A、B 两份答案中选较好的一份
    RLHF：偏好数据 -> reward model -> 强化学习更新语言模型
    DPO：偏好数据 -----------------------> 直接更新语言模型

边界：能力、知识与对齐
^^^^^^^^^^^^^^^^^^^^^^

预训练主要决定模型『知道和能表示什么模式』，后训练主要塑造它『遇到请求时倾向怎样回应』；这只是有用的分工，而不是绝对边界。
高质量 SFT 也能补充特定任务技能，预训练数据选择也会影响安全与偏见。后训练不能可靠地凭空注入大量新知识，更不能保证每次输出都
正确；它也可能因过强的拒答或格式偏好损伤某些原本的能力。

因此，部署时不能把『经过后训练』理解为真实性证明。需要把模型输出和适当的工具、检索、权限控制、内容策略以及面向实际场景的评测
结合起来。对用户而言，最实用的判断是：模型给出的流畅回答是按训练分布生成的候选文本；涉及事实、代码执行、医疗、法律或金钱决策时，
仍应回到可验证的来源和结果。
