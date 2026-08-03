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

经典视频教程:

- `Open AI传奇研究员Andrej Karpathy教你理解和构建GPT Tokenizer <https://www.bilibili.com/video/BV11x421Z7QZ/?vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_
- `10分钟入门神经网络 PyTorch 手写数字识别 <https://www.bilibili.com/video/BV1GC4y15736/?spm_id_from=333.337.search-card.all.click&vd_source=f7b8e2d66d4b85cd95e1a463f568439f>`_

PyTorch
-------

- https://github.com/pytorch/examples
- https://pytorch.org/tutorials/beginner/pytorch_with_examples.html
- https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html

CNN
^^^

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
""""""""""""""""

深度学习框架把一批图片表示为四维张量 ``(B, C, H, W)``：``B`` 是 batch 中图片数，``C`` 是通道数，``H``、``W`` 是高和宽。
因此 DataLoader 取出 64 张 MNIST 图后，``images.shape`` 为 ``(64, 1, 28, 28)``；标签 ``labels.shape`` 为 ``(64,)``，
其中每个元素是类别编号，而不是 one-hot 向量。批处理不是算法上的要求，而是让矩阵乘法和 GPU 并行有足够工作可做的工程折中。

``Conv2d(1, 32, 3)`` 有 32 个可学习的 3 x 3 滤波器。每一个滤波器跨越全部输入通道，在图像上滑动，产生一个特征图；所以
输出通道从 1 变成 32。这里没有 padding、stride 默认为 1，空间尺寸的公式是 ``H_out = H_in - K + 1``，故 28 变 26，
第二层再由 26 变 24。卷积的关键不是“识别边缘”这个特定效果，而是 **局部连接和权重共享**：同一组 3 x 3 权重用于所有位置，
于是参数量不随图片面积线性增长，也让模型能在不同位置寻找同一种局部模式。

``ReLU(x) = max(0, x)`` 是逐元素非线性。没有它以及后续非线性，任意层线性卷积/全连接的组合仍可折叠成一层线性变换，
表达能力不会随层数实质增加。``max_pool2d(..., 2)`` 将每个不重叠的 2 x 2 区块取最大值，使 24 x 24 变成 12 x 12；
它降低后续计算量，也使小幅平移的影响较小，但同时不可逆地丢掉了空间细节。

``flatten(x, 1)`` 保留第 0 维的 batch，把每张图的 ``64 * 12 * 12 = 9216`` 个数拼成特征向量。因此 ``fc1`` 的输入必须是
``9216``，这正是最常见的 CNN 形状错误来源。可先在 ``forward`` 中临时打印 ``x.shape``，或用 ``assert x.shape[1:] ==
(64, 12, 12)`` 定位问题；不要凭感觉修改 ``Linear`` 的输入维度。

模型、损失与预测
""""""""""""""""""""

``fc2`` 输出的 ``(B, 10)`` 不是概率，而是每个类别的 logit，即可比较的原始分数。``argmax(dim=1)`` 选最大分数的下标，
正好就是预测数字。``CrossEntropyLoss`` 在内部完成数值稳定的 ``log_softmax`` 和负对数似然：它推动正确标签对应的分数高于其他
九类。把 ``softmax`` 后的概率再传给 ``CrossEntropyLoss`` 是常见错误，会改变其数学含义并损失数值稳定性。

参数并不只在卷积层。``conv1`` 有 ``32 * (1 * 3 * 3 + 1) = 320`` 个参数，``conv2`` 有 18,496 个；而 ``fc1`` 约有
118 万个。这也解释了为什么现代 CNN 常继续下采样、使用 global average pooling，或以更紧凑的模块取代巨大的全连接层。
``Dropout`` 在训练时随机置零部分激活，降低对特定神经元组合的依赖；在评估时必须关闭，所以 ``model.train()`` 与
``model.eval()`` 不是装饰性调用，而是模型状态切换。

训练循环的实际语义
""""""""""""""""""""""

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
""""""""""""""""""""""""

不必先读下标很多的卷积公式。先把网络理解为一个可调的计算器：输入一张图片，经过一串固定种类的运算，最后输出 10 个数。
这 10 个数分别对应“它像 0、像 1、……、像 9”的程度。搭建 ``Net``，就是写出这串运算；训练，就是不断调整其中的可调数字，
让正确数字的分数变大。

一张图片怎样变成十个分数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
:math:`Aq` 可看作一次并行计算 128 个“加权求和”。卷积核、:math:`A`、:math:`B` 和各层偏置合起来，就是模型参数 :math:`\theta`。
``Dropout`` 仅在训练时随机把部分中间数置零，以免模型过度依赖少数特征；评估时关闭它。

怎样判断这次答案错得多不多
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

把所有可训练数字合并记为 :math:`\theta`，例如某个卷积核的一个权重，或全连接矩阵里的一个元素。训练的核心更新只有一行：

.. math::

    \theta \leftarrow \theta - \eta\frac{\partial L}{\partial\theta}.

这里 :math:`\frac{\partial L}{\partial\theta}` 是“把这个参数略微增大时，损失会向哪个方向、变化多快”的测量值；
:math:`\eta` 是学习率，控制这一步走多远。减号表示沿着让损失下降的方向移动。``loss.backward()`` 用链式法则算出所有参数的
这个导数；``optimizer.step()`` 则执行更新。本例使用的 Adam 是梯度下降的实用变体：它还会根据各参数近期梯度的大小调整步长，
但不改变“根据损失的导数修改参数”这一主线。

对应到训练循环，程序逻辑只有下面四步：

.. code-block:: text

    logits = model(images)            # 按前面的计算图得到 s
    loss = criterion(logits, labels)  # 用真实标签计算平均 L
    loss.backward()                   # 计算每个参数的 ∂L/∂θ
    optimizer.step()                  # 按梯度更新参数 θ

每个 batch 重复这四步。``zero_grad()`` 放在 ``backward()`` 前，是因为 PyTorch 默认会把本次导数加到上次的 ``.grad`` 中；
通常每个 batch 都希望从零开始计算，才需要清空。经过许多 batch 后，参数逐步变成能让正确类别分数更高的一组值。

把一个卷积手算一遍
~~~~~~~~~~~~~~~~~~~~

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

上例的数字并不是预先设计出来的“边缘检测规则”。训练开始时它们通常是随机小数；反向传播会把有助于降低损失的权重慢慢推大，
无用或有害的权重推小。最终某些卷积核常会对边缘、笔画拐角或局部纹理有反应，但这是数据和损失共同塑造的结果。

形状、通道和 batch
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

反向传播不需要先被当作神秘机制。假设先只观察一个参数 :math:`\theta`，当前值是 0.50，计算得到的梯度为
:math:`\frac{\partial L}{\partial\theta}=4`，学习率 :math:`\eta=0.01`。一次普通梯度下降后：

.. math::

    \theta_{new}=0.50-0.01\times4=0.46.

这里正梯度表示“把该参数增大一点，损失会增大”，所以更新把它减小。若梯度为 :math:`-4`，更新会得到 0.54，表示应增大该参数。
真实 CNN 有约 120 万个参数；``backward()`` 正是在一次调用中为每一个参数求出这样的梯度，``step()`` 再统一更新它们。

数值微分能帮助理解导数的含义：若把参数从 :math:`\theta` 改成 :math:`\theta+\epsilon`，可以用
:math:`[L(\theta+\epsilon)-L(\theta)]/\epsilon` 近似它的梯度。这样逐个参数试探在 CNN 中太慢；自动求导利用计算图和链式法则，
一次反向遍历就能复用中间结果求出全部梯度。这正是 ``loss.backward()`` 相比手写有限差分的价值。

一个 batch 的损失是多张图片损失的平均值。例如两张图片的损失分别是 0.1 和 2.3，batch loss 为 1.2。用 batch 的平均梯度更新，
是对整个训练集梯度的带噪声近似：batch 越大，估计通常越稳定；batch 越小，单步更快但抖动更明显。``shuffle=True`` 让每个 batch
混合不同样本，避免数据文件本身的排序系统性影响更新方向。

训练指标要怎样看
~~~~~~~~~~~~~~~~~~

损失和准确率回答不同问题。准确率只看 ``argmax`` 是否等于标签，因而把正确类别从 0.51 提升到 0.99 不会改变这一个样本的准确率；
交叉熵会继续奖励这种更确定的正确预测，也会严厉惩罚“很确定但错了”的预测。因此训练时通常同时看 ``loss`` 和 ``accuracy``。

MNIST 有 10 个类别，完全随机猜测的长期平均准确率约为 10%。刚开始训练时，训练集和测试集准确率都应从接近该水平逐步提升。
若训练集持续变好而测试集变差，说明模型开始记住训练样本的细节而不善于泛化，这叫过拟合；``Dropout``、更多数据或数据增强等方法
都在缓解这个问题。测试阶段调用 ``model.eval()`` 和 ``torch.inference_mode()``，是为了关闭训练专用的随机性，并且不再建立求梯度的
计算图；这让测试结果稳定，也避免无用的内存开销。
