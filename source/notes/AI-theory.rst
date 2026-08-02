.. Michael Wu Copyright 2026,-

:Authors: Michael Wu
:Version: 1.0

AI 理论知识
************

Overview
========

本文基于一套 AI 岗位笔试题整理知识框架，题目链接:

https://mp.weixin.qq.com/s/WOVzb4PmcH9qpjNjzamOXg

覆盖数学基础、机器学习、深度学习训练、多模态、LLM 推理系统、
Mixture of Experts（MoE，混合专家）和 Pipeline Parallelism（流水线并行）。

知识地图
========

.. csv-table:: AI Theory Knowledge
   :header: "方向", "原题考点", "mental model"
   :widths: 18, 38, 44

   "概率与线性代数", "方差、概率密度、PCA、SVD、向量相似度", "随机性如何传播；矩阵如何分解和降维"
   "机器学习", "正则化、交叉熵、聚类、推荐相似度", "目标函数、数据假设和泛化之间的关系"
   "深度学习", "隐藏层、残差连接、Swish、梯度裁剪", "前向表示与反向梯度是同一计算图的两面"
   "多模态", "Late Fusion、双分支梯度平衡", "模态如何编码、融合，以及如何避免单一模态主导"
   "LLM 训练", "Activation Checkpointing、低精度、显存组成", "用计算换显存；参数、梯度、优化器状态和激活分别占多少"
   "LLM 推理", "KV Cache、滑动窗口、PagedAttention、Perplexity", "自回归状态如何增长，以及服务系统如何管理动态内存"
   "大模型并行", "MoE 路由、容量、Pipeline 划分", "计算、显存、通信和负载均衡之间的约束"
   "编程算法", "Top-K、模拟、前缀和、分段 DP、单调队列", "把 AI 场景翻译成确定的数据结构与状态转移"

- PCA（Principal Component Analysis，主成分分析）：一种线性无监督降维方法，寻找方差最大的正交方向，
  用较少的主成分保留数据中的主要变化；对不同量纲的特征通常要先标准化。
- SVD（Singular Value Decomposition，奇异值分解）：把矩阵分解为 :math:`A=U\Sigma V^T`，适用于
  方阵和矩形矩阵；截断较小奇异值可用于低秩近似、压缩和降噪。
- KV Cache：在自回归推理中缓存各层历史 Token 的 Key 和 Value，生成新 Token 时只计算当前位置，避免重复
  计算整个前缀；代价是显存随层数、上下文长度、KV head 数和数据类型增长。
- MoE（Mixture of Experts，混合专家）：Router 为每个 Token 选择少量专家参与计算，以稀疏激活扩大模型
  参数容量；核心工程问题是路由质量、专家负载、容量限制和跨设备通信。
- Top-K：从一组候选中选出分数最高的 K 项。实现可用完整排序、heap、``partial_sort`` 或 selection；
  工程题还必须明确同分时的 tie-break 和结果是否要求有序。
- PagedAttention：把 KV Cache 划分为固定大小的逻辑块，再映射到可不连续的物理块，按需分配以减少预留和
  内存碎片，并支持前缀块共享；块太大会增加内部碎片，太小会增加块表和寻址开销。
- Perplexity（困惑度）：语言模型平均负对数似然的指数，表示模型对一段 Token 序列的『意外程度』；在同一
  模型和 Tokenizer 下通常越低越可预测，但不能单独等同于事实性、可读性或数据质量。
- Pipeline Parallelism（流水线并行）：把连续模型层切成多个 Stage，并用 Micro-batch 让不同 Stage 并行
  工作；性能取决于最慢 Stage、Pipeline Bubble、激活通信量和调度策略。
- Activation Checkpointing（激活检查点）：前向传播只保存部分边界激活，反向传播时重新执行局部前向，
  用额外计算换取更低的训练激活显存；它不同于用于断点续训的模型 Checkpoint 文件。
- Late Fusion（后融合）：不同模态先由独立编码器提取表示，再在较后层或决策层融合；模块化较强，但细粒度
  跨模态交互通常弱于更早进行的 Cross-attention 或 Early Fusion。
- 交叉熵：衡量用预测分布表示真实分布时的平均负对数似然。真实分布固定时，最小化交叉熵等价于最小化
  KL divergence；One-hot 标签下，只取真实类别对应预测概率的负对数。
- 正则化：控制模型有效复杂度、降低过拟合风险的一类方法，包括 L2 penalty、Dropout、数据增强和
  Early Stopping 等；对自适应优化器，weight decay 与 L2 penalty 不再天然等价。
- 梯度裁剪：限制梯度范数或幅值，防止梯度爆炸；可在全模型或单分支上裁剪，影响不同模态的梯度缩放。
- Swish/SiLU：非线性激活函数 :math:`x\sigma(x)`，在较大正输入时导数趋近 1，通常比饱和型 sigmoid
  更有利于梯度传播。
- Residual Connection（残差连接）：在深层网络中引入恒等或投影 shortcut，提供更直接的信息与梯度路径，
  缓解优化困难；不能保证训练出的深层网络一定优于浅层网络。
- 向量相似度：

  - Cosine similarity（余弦相似度）：衡量非零向量方向的相似性，归一化后取值在 [-1, 1]。
  - Euclidean distance（欧氏距离）：同时受向量方向和模长影响，适合衡量绝对差异。
  - Pearson correlation coefficient（皮尔逊相关系数）：中心化和归一化后的线性相关度，可消除均值偏移和
    正比例尺度变化的影响，但要求存在共同观测项且两个变量的方差非零。

- 隐藏层：

  - 通过逐层线性变换和非线性激活，学习从输入到任务相关表示的层次化映射。
  - 多层之间若没有非线性激活，深度不会增加函数表达能力。
  - 『低层学局部、高层学语义』是一种常见观察，不是所有网络和任务的严格定理。

- 滑动窗口：

  - Sliding Window Attention 限制每个新 Token 只关注最近 W 个位置，窗口外位置不参与当前注意力。
  - Sliding Window Cache 进一步淘汰或覆盖窗口外 KV；只有实际使用这种有界缓存时，单层、单序列的缓存
    空间才被限制在 O(W)。
  - 代价是当前层不能直接访问窗口外信息，但旧信息仍可能通过较早层的表示间接向后传播。
  - 不同模型对窗口边界、全局 token、分层窗口和 Prefill 的实现可能不同。

- 聚类：

  - 无监督学习的一种，依据表示空间中的结构自行形成簇。
  - 与分类不同，聚类不需要预定义类别标签。
  - 常见流程包括文本 embedding、选择距离或相似度度量、K-means/层次聚类，再由人工解释和命名簇。

- 推荐相似度：

  - 当用户存在均值偏移或正比例评分尺度差异，并且有足够的共同评分项时，Pearson correlation coefficient
    通常比直接计算绝对距离更适合衡量兴趣变化趋势。
  - 欧氏距离和曼哈顿距离直接比较绝对分值，容易把评分习惯误认为兴趣差异。

- 优化器：

  - 标准 SGD 在系数按学习率适当换算时，L2 penalty 与 weight decay 可以得到相同更新式。
  - 对 Adam 等自适应优化器，两者不再天然等价，因此 AdamW 把 weight decay 与梯度更新解耦。
  - Bias、LayerNorm 参数等也经常不做 weight decay。

选择题解析
============

1. 独立随机变量的线性组合
--------------------------

**题目**：已知独立随机变量 :math:`X\sim N(1,2)`、:math:`Y\sim N(2,3)`，求
:math:`Z=2X-Y` 的方差。

**答案**：:math:`11`。

期望和方差是两套不同规则：

.. math::

   \operatorname{E}[aX+bY]
   =a\operatorname{E}[X]+b\operatorname{E}[Y]

.. math::

   \operatorname{Var}(aX+bY)
   =a^2\operatorname{Var}(X)+b^2\operatorname{Var}(Y)
    +2ab\operatorname{Cov}(X,Y)

独立意味着 :math:`\operatorname{Cov}(X,Y)=0`，所以
:math:`\operatorname{Var}(Z)=2^2\times 2+(-1)^2\times 3=11`。系数在方差中要平方，
负号不会把方差变成负数。

**扩展知识**：不独立时必须保留协方差项；『不相关』只能推出协方差为零，通常不能推出独立。
联合正态分布是重要例外：联合正态变量不相关可以推出独立。正态变量的线性组合仍为正态变量，
本题还可得到 :math:`Z\sim N(0,11)`。

2. Activation Checkpointing 的目的
----------------------------------

**题目**：训练大模型时使用 Activation Checkpointing 的主要目的是什么？

**答案**：降低训练时的激活显存峰值。

自动微分通常在前向传播时保存反向传播需要的中间张量。Checkpointing 只保留部分边界激活，
反向传播走到该区域时重新执行前向计算：

.. code-block:: text

   普通训练：forward -> 保存大量 activation -> backward
   重计算：  forward -> 只存 checkpoint -> 局部重算 -> backward

它没有减少模型参数，也不会自动提高数值精度；代价通常是更多计算和更长训练时间。PyTorch 还要
处理 Dropout 等随机操作的 RNG state，否则重算前向可能与原前向不一致。

**扩展知识**：训练显存大致由参数、梯度、优化器状态、激活和临时工作区组成。Checkpointing
主要压缩激活项；ZeRO/FSDP 主要切分参数、梯度和优化器状态；两者解决的不是同一个问题，可以组合。

3. 概率密度函数归一化
----------------------

**题目**：连续随机变量的概率密度为

.. math::

   f(x)=
   \begin{cases}
   c(1-x^2), & -1\le x\le 1\\
   0, & \text{其他}
   \end{cases}

求常数 :math:`c`。

**答案**：:math:`c=\frac{3}{4}`。

概率密度必须非负且在全定义域积分为 1：

.. math::

   1=\int_{-1}^{1}c(1-x^2)\,dx
    =c\left[x-\frac{x^3}{3}\right]_{-1}^{1}
    =\frac{4c}{3}

因此 :math:`c=3/4`。连续型变量在单点上的概率为零，:math:`f(x)` 可以大于 1；真正的概率是
对区间积分后的面积。

**扩展知识**：归一化常数在概率模型中很常见。Softmax 的分母、Bayesian posterior 的 evidence
以及 energy-based model 的 partition function，都承担把相对分数归一化为概率分布的角色。

4. L2 正则化
-------------

**题目**：为什么深度学习优化中常用 L2 正则化？

**考试答案**：限制权重大小，降低过拟合风险，并通常改善训练稳定性。

在原目标函数后加入权重平方惩罚：

.. math::

   L_{total}=L_{data}+\frac{\lambda}{2}\lVert W\rVert_2^2

其梯度多出 :math:`\lambda W`，每次更新都会把权重向零拉回。它不能保证全局最优、不能消除所有
零特征值，也不保证缩短训练时间。

**严格边界**：『权重更小』通常有助于控制模型复杂度，但不能单凭 L2 就保证对输入扰动鲁棒。
网络的输入敏感度还取决于各层算子范数、激活函数和数据分布。

**扩展知识**：经典 SGD 中 L2 penalty 与 weight decay 可以得到相同更新式；对 Adam 这类自适应
优化器，两者不再天然等价，因此 AdamW 把 weight decay 与梯度更新解耦。Bias、LayerNorm 参数等
也经常不做 weight decay。

5. One-hot 标签与交叉熵
------------------------

**题目**：真实标签 :math:`y=[0,1,0]`，模型概率 :math:`p=[0.1,0.8,0.1]`，求交叉熵。

**答案**：:math:`-\log 0.8`，若使用自然对数，约为 :math:`0.2231`。

.. math::

   H(y,p)=-\sum_i y_i\log p_i=-\log p_{true}

One-hot 标签只有真实类别对应位置为 1，其余项全部消失。预测给真实类别的概率越接近 1，损失越接近 0；
概率越接近 0，损失越大。

**扩展知识**：实现时通常直接把 logits 交给 CrossEntropyLoss，由框架用 LogSoftmax 与 NLLLoss
的数值稳定组合计算，不要先手工 Softmax。Label smoothing 会把 one-hot 标签变成软分布，降低模型
过度自信；类别不平衡时还可能加入 class weight 或改用 focal loss。

6. PCA 前的标准化
-----------------

**题目**：PCA 前为什么通常先标准化特征？

**答案**：避免量纲或数值范围大的特征仅凭尺度主导协方差和方差。

常见标准化为 :math:`z=(x-\mu)/\sigma`。PCA 寻找投影后方差最大的正交方向；身高用米还是毫米，
不应仅因单位变化就完全改变主成分。

**严格边界**：标准化不是 PCA 的数学前置条件。若所有特征单位一致，或者绝对方差本身就代表业务
重要性，可以只中心化而不缩放。对标准化数据做 covariance PCA，等价于基于原数据相关系数矩阵做 PCA。

**扩展知识**：PCA 是线性、无监督的降维方法。它最大化保留方差，也等价于最小化给定维数下的平方
重构误差；它不使用类别标签，因此最大方差方向不一定最利于分类。

7. 多模态 Late Fusion
----------------------

**题目**：VQA 等任务中的 Late Fusion 是什么？

**答案**：图像、文本等模态先由独立编码器提取表示，在较后层或决策层融合。

.. code-block:: text

   image -> ViT ---------+
                        +-> fusion -> prediction
   text  -> Transformer -+

Early Fusion 更早地把 token、embedding 或原始特征放进共同模型；Late Fusion 保留各模态独立性，
模块化更强，但跨模态细粒度交互发生得更晚。

**扩展知识**：实际系统还有 intermediate/hybrid fusion、cross-attention 和共享 token space。
选择融合位置时要权衡跨模态对齐能力、缺失模态鲁棒性、计算成本和是否能复用预训练编码器。

8. 隐藏层的作用
---------------

**题目**：深度神经网络隐藏层的主要作用是什么？

**答案**：通过逐层线性变换与非线性激活，学习从输入到任务相关表示的层次化映射。

单个典型层可写成 :math:`h=\phi(Wx+b)`。如果多层之间没有非线性激活，那么多个线性层的复合仍只是
一个线性变换，深度不会增加函数表达能力。

**扩展知识**：『低层学局部、高层学语义』是一种常见观察，不是所有网络和任务的严格定理。
隐藏层也不会显式『存储损失』；损失是计算图末端的标量，反向传播通过链式法则把梯度传回各层参数。

9. 未标注问题的自动归类
------------------------

**题目**：对大量未标注的客服问题自动归类属于哪种学习？

**答案**：在原题设定下属于无监督学习，更准确的任务名称是 clustering（聚类）。

Classification 通常学习预先定义的类别，需要带标签训练样本；Clustering 根据表示空间中的结构自行形成簇。
一个常见流程是文本 embedding、相似度计算、K-means/层次聚类，再由人工解释和命名簇。

**扩展知识**：若先用少量人工标签再扩展到大量未标注数据，则可能属于半监督学习；用预训练模型生成
pseudo-label 是伪标签学习；没有人工类别但使用对比学习训练表示，通常称自监督学习。

10. 评分尺度与 Pearson 相关系数
--------------------------------

**题目**：不同用户有明显评分尺度差异时，什么相似度更合适？

**答案**：Pearson correlation coefficient（皮尔逊相关系数）。

.. math::

   r_{xy}=\frac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}
   {\sqrt{\sum_i(x_i-\bar{x})^2}\sqrt{\sum_i(y_i-\bar{y})^2}}

中心化消除了『有人习惯打高分、有人习惯打低分』的均值偏移，归一化又消除了正比例尺度差异。
欧氏距离和曼哈顿距离直接比较绝对分值，容易把评分习惯误认为兴趣差异。

**扩展知识**：Pearson 只衡量线性相关，至少要有共同评分项，零方差用户的相关系数无定义。推荐系统还要
处理共同评分太少带来的偶然高相关，常用 shrinkage、最小共同项阈值或显式 bias model。

11. PagedAttention 的 Block Size
--------------------------------

**题目**：把 PagedAttention 的 Block Size 设为 1，主要问题是什么？

**答案**：每个 token 都对应一个块，块表和分配元数据增多，索引与 kernel 管理开销上升，局部性也可能变差。

PagedAttention 借鉴操作系统分页：逻辑连续的 KV Cache 可以映射到非连续物理块，序列增长时按需分配，
从而减少预留和外部碎片。块大小是一组折中：

- 太大：最后一个块的内部碎片增加，细粒度复用变差。
- 太小：块表更长、调度和地址转换更多、kernel 访问更零散。

**严格边界**：不要死记『默认 16 或 32』。vLLM 的可用值和默认值可能随平台、模型、后端和版本变化；
稳定考点是 block size 的时间/空间折中。

**扩展知识**：PagedAttention 管理的是推理状态，不会改变模型数学结果。Prefix caching、beam search 和
parallel sampling 还可以共享相同前缀的物理 KV block，并通过引用计数和 copy-on-write 管理分叉。

12. Perplexity 与数据质量
-------------------------

**题目**：模型对符合目标分布的高质量文本通常给出怎样的 Perplexity？

**考试答案**：通常更低。

对长度为 :math:`T` 的 token 序列，平均负对数似然和困惑度为：

.. math::

   \operatorname{NLL}=-\frac{1}{T}\sum_{t=1}^{T}\log p(x_t\mid x_{<t})

.. math::

   \operatorname{PPL}=\exp(\operatorname{NLL})

PPL 越低，表示在当前 tokenizer、模型和上下文设置下，模型给实际 token 的条件概率越高。

**严格边界**：低 PPL 不等于高质量。重复模板、训练集泄漏、短且简单的文本也可能得到很低 PPL；领域外
但事实准确的文本可能 PPL 较高。不同 tokenizer 下的 token 数不同，PPL 也不宜直接横向比较。

**扩展知识**：数据筛选通常组合去重、语言识别、毒性/隐私过滤、启发式质量规则、模型打分和人工抽检，
而不是只用一个 PPL 阈值。

13. Sliding Window KV Cache
---------------------------

**题目**：滑动窗口大小为 20；Prefill 处理 30 个 token，Decode 已生成 15 个 token。此时保留多少 token，
当前自注意力上下文长度是多少？

**答案**：在题目明确采用严格滑动窗口语义时，都是 20。

总历史长度已经达到 45，但每个新 token 只访问最近 :math:`W=20` 个位置，旧 KV 会被淘汰或不再参与注意力。
滑动窗口把随序列长度线性增长的单层缓存限制在 :math:`O(W)`，代价是不能直接访问更早信息。

**扩展知识**：不同模型对窗口边界、全局 token、分层窗口和 Prefill 的实现可能不同。KV Cache 的粗略元素量
与 :math:`2\times L\times W\times H_{kv}\times D` 成正比，其中 2 代表 K 和 V，:math:`L` 是层数，
:math:`H_{kv}` 是 KV head 数，:math:`D` 是 head dimension；再乘 batch/sequence 数和 dtype 字节数。

14. Singular Value Decomposition
--------------------------------

**题目**：关于 SVD，哪项描述正确？

**答案**：任意实矩阵都可写成 :math:`A=U\Sigma V^T`；完整 SVD 中 :math:`U`、:math:`V` 可取正交矩阵，
奇异值非负。

SVD 不要求 :math:`A` 是方阵或可逆矩阵。若 :math:`A\in\mathbb{R}^{m\times n}`，其奇异值平方是
:math:`A^TA` 的特征值。经济型 SVD 中 :math:`U`、:math:`V` 可能不是方阵，更准确地说其列正交归一。

**扩展知识**：保留前 :math:`k` 个最大奇异值可得到最优 rank-k 近似，这是 PCA、低秩压缩、LoRA 直觉和
推荐系统矩阵分解的重要线性代数基础。奇异值很小还意味着逆问题对噪声敏感，可用 condition number 衡量。

15. 余弦相似度与欧氏距离
-------------------------

**题目**：二者最准确的区别是什么？

**答案**：余弦相似度主要比较非零向量方向；普通欧氏距离同时受到方向和模长影响。

.. math::

   \cos(x,y)=\frac{x\cdot y}{\lVert x\rVert_2\lVert y\rVert_2}

向量单位化后，二者存在严格关系：

.. math::

   \lVert \hat{x}-\hat{y}\rVert_2^2=2-2\cos(x,y)

因此它们的数值并不相等，但在单位向量集合上按相似度排序与按距离反向排序是等价的。原题选 A 是因为
B 中『结果等价』容易被误读成数值相等。

**扩展知识**：Embedding 检索使用 cosine、inner product 还是 L2 必须与训练目标、是否归一化和索引类型
一致。零向量的 cosine 无定义，工程代码通常用 epsilon 防止除零，但这只是约定，不改变数学定义。

16. Activation Checkpointing 的正确描述
----------------------------------------

**题目**：『反向时需要额外前向重算』『一定降低训练时间』『只用于推理』『减少保存激活』哪些正确？

**答案**：第一项和第四项。

第 2 题考主要目的，本题考完整 trade-off。Checkpointing 不等于保存模型到磁盘的 training checkpoint；
前者是计算图内的显存优化，后者是故障恢复和续训状态持久化。它主要用于需要反向传播的训练阶段，推理没有
同样的反向激活保存压力。

**扩展知识**：Checkpoint 切得越细，通常保存越少、重算越多。实际选择还受算子计算强度、通信重叠、
Dropout RNG state 和编译器 graph capture 影响，并非显存越省越好。

17. 训练与推理显存优化
-----------------------

**题目**：PagedAttention、Checkpointing、降低 KV dtype 位宽，以及『KV Cache 与层数无关』哪些合理？

**答案**：前三种优化合理；KV Cache 与层数无关是错误的。

- PagedAttention：减少推理时 KV Cache 的预留和碎片问题。
- Activation Checkpointing：减少训练时保存的激活。
- FP8/INT8 等低位宽 KV：每个元素字节数降低，但要考虑 kernel 支持和精度。
- KV Cache：每层都要保存自己的 K/V，因此通常随层数线性增长。

**扩展知识**：还应区分 weight quantization 与 KV Cache quantization。前者主要降低权重带宽和容量；后者
降低每个活动请求随上下文增长的状态。连续 batching 通过动态加入/移出请求提升设备利用率，但也让缓存调度
和延迟公平性更复杂。

18. ResNet Shortcut Connection
------------------------------

**题目**：残差连接有哪些正确作用？

**答案**：恒等 shortcut 有助于梯度传播和深层网络优化，也可推广到 MLP、CNN、RNN 和 Transformer；
但不能保证实际训练出的深层网络必然优于浅层网络。

残差块写成：

.. math::

   y=x+F(x;W)

反向传播中存在不经过 :math:`F` 的直接梯度路径：

.. math::

   \frac{\partial L}{\partial x}
   =\frac{\partial L}{\partial y}
    \left(I+\frac{\partial F}{\partial x}\right)

这缓解了深层网络的 degradation/optimization 问题，但『存在一个可表示浅层模型的参数解』不等于优化器一定
找到它，也不等于测试性能一定更好。输入输出维度不同时，shortcut 可能需要 projection。

**扩展知识**：Transformer 中每个 Attention 和 FFN 子层周围也有 residual connection；Pre-Norm 与
Post-Norm 的差异会影响深层网络的梯度稳定性。

19. 点积、余弦相似度与 Attention
--------------------------------

**题目**：余弦是 L2 归一化后的点积吗？点积包含模长信息吗？用 cosine 替换 Attention logits 有什么风险？

**答案**：对非零向量，前两项都成立。Cosine 被限制在 :math:`[-1,1]`，若没有足够的 scale/temperature，
Softmax logits 差距可能过小，注意力分布会过平。

标准 scaled dot-product attention 为：

.. math::

   \operatorname{Attention}(Q,K,V)
   =\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V

:math:`1/\sqrt{d_k}` 用来控制点积方差随维度增长。Cosine attention 则消除了 Q/K 模长信息，通常需要可学习
或显式温度恢复合适的 logit 动态范围。

**严格边界**：缺少 scale 会增加优化困难，不代表所有模型都『必然无法收敛』。两个零向量的点积是 0，
cosine 则无定义，原题的零向量负点积说法本身不可能成立。

20. 多模态分支的梯度平衡
--------------------------

**题目**：文本 Transformer 与图像 ViT 经 Linear + Swish 融合后共同反向传播，如何判断梯度失衡、
Swish 和分支裁剪的说法？

**原文答案**：A、B、C、D。

两分支梯度尺度差异过大时，确实可能使某一模态更快主导融合层；可观察每个分支的 gradient norm、参数更新量、
单模态消融结果和缺失模态性能。Swish/SiLU 为：

.. math::

   \operatorname{swish}(x)=x\sigma(x)

.. math::

   \operatorname{swish}'(x)=\sigma(x)+x\sigma(x)(1-\sigma(x))

当 :math:`x` 很大且为正时导数趋近 1，正区间的梯度传播通常好于饱和型 sigmoid。

**严格边界**：不应为了『幅值一致』而无条件归一化两个分支；梯度不同可能正是任务信号不同。D 只有在
明确只对 ViT 参数集合做 clip 时才不改变文本分支梯度；若对全模型做 global norm clipping，图像分支的大梯度
会改变统一缩放系数，从而同时缩放文本分支。

**扩展知识**：可选方法包括 loss weighting、GradNorm、分支独立 optimizer/learning rate、gradient clipping、
modality dropout 和分阶段冻结/解冻。判断方案好坏要看验证集和模态鲁棒性，而不只是 gradient norm 是否相等。

编程题一：MoE 动态路由与容量掩码
======================================

题目重述
--------

有 :math:`N` 个 Token、:math:`E` 个专家，每个 Token 激活 :math:`K` 个专家，每个专家最多接收
:math:`C` 个 Token。第 :math:`i` 个 Token 对第 :math:`j` 个专家的分数是 :math:`S_{i,j}`。

按 Token 输入顺序处理：

1. 对当前 Token 按『分数降序、专家下标升序』选择 Top-K。
2. 若所选专家当前 :math:`load[j]<C`，则路由生效并令 :math:`load[j]` 加一；否则丢弃。
3. 最后输出负载平方和 :math:`P=\sum_{j=0}^{E-1}load[j]^2` 和整个 ``load`` 数组。

约束为：

.. code-block:: text

   1 <= N <= 10^4
   1 <= E <= 100
   1 <= K <= E
   0 <= C <= N
   0 <= S[i][j] <= 10^4

输入输出
--------

.. code-block:: text

   输入：
   N E K C
   接下来 N 行，每行 E 个专家分数

   输出：
   负载平方和 P
   load[0] load[1] ... load[E-1]

样例一：

.. code-block:: text

   输入
   4 3 2 2
   1 5 4
   8 1 2
   3 6 5
   2 7 9

   输出
   9
   1 2 2

逐步模拟：

.. csv-table:: MoE Routing Trace
   :header: "Token", "Top-K", "容量处理", "处理后的 load"

   "0", "专家 1、2", "都接收", "[0, 1, 1]"
   "1", "专家 0、2", "都接收", "[1, 1, 2]"
   "2", "专家 1、2", "专家 1 接收，专家 2 已满", "[1, 2, 2]"
   "3", "专家 1、2", "都已满", "[1, 2, 2]"

最终 :math:`P=1^2+2^2+2^2=9`。

样例二专门检查同分 tie-break：

.. code-block:: text

   输入
   4 4 2 2
   5 5 5 1
   2 8 8 9
   1 2 9 9
   7 7 1 1

   输出
   13
   2 2 1 2

Token 0 的专家 0、1、2 同为 5，选择下标更小的 0、1；Token 1 的第二名在专家 1、2 之间同为 8，
选择专家 1。最终负载为 ``[2, 2, 1, 2]``，平方和为 13。

算法推导
--------

每行只需要知道 Top-K 专家，不需要显式保存两个 :math:`N\times E` 路由掩码。令 ``order`` 保存
``0..E-1`` 的专家下标，按 ``(-score[j], j)`` 排序后检查前 K 个即可。

原题特别说明同一 Token 的 K 次容量判断使用 Token 开始时的负载。由于 Top-K 专家下标互不重复，
专家 ``j`` 的更新只改变 ``load[j]``，不会影响当前 Token 对其他专家的判断，因此直接顺序更新与
使用负载快照等价。

正确性证明
----------

对 Token 下标做数学归纳。

**归纳基**：处理任何 Token 前，算法和题目定义的负载都为全零。

**归纳假设**：处理 Token :math:`i` 前，算法的 ``load`` 与题目定义一致。

**归纳步骤**：排序关键字首先让高分专家靠前，同分时让小下标靠前，所以前 K 项恰好是题目定义的 Top-K。
对每个入选专家，算法仅在 ``load[j] < C`` 时加一，与容量掩码规则完全相同；未入选或已满专家不变。
由于入选专家不重复，各次更新互不干扰。故处理 Token :math:`i` 后负载仍与题目一致。

归纳完成后，算法得到所有专家的真实负载；逐项平方求和即为题目要求的惩罚值。

复杂度
------

完整排序版本每个 Token 使用 :math:`O(E\log E)` 时间，总时间
:math:`O(NE\log E)`；``scores`` 按行读取，额外空间为 :math:`O(E)`。
由于 :math:`E\le 100`，完整排序简单且足够快。若 E 很大而 K 很小，可改用大小为 K 的 heap、
``partial_sort`` 或 selection，将 Top-K 阶段优化到 :math:`O(E\log K)` 或平均 :math:`O(E)`。

C++17 实现
----------

.. code-block:: cpp

   #include <algorithm>
   #include <cstdint>
   #include <iostream>
   #include <numeric>
   #include <vector>

   int main() {
       std::ios::sync_with_stdio(false);
       std::cin.tie(nullptr);

       int n, e, k, capacity;
       if (!(std::cin >> n >> e >> k >> capacity)) {
           return 0;
       }

       std::vector<int> load(e, 0);
       std::vector<int> score(e);
       std::vector<int> order(e);

       for (int token = 0; token < n; ++token) {
           for (int expert = 0; expert < e; ++expert) {
               std::cin >> score[expert];
           }

           std::iota(order.begin(), order.end(), 0);
           std::sort(order.begin(), order.end(),
                     [&](int lhs, int rhs) {
                         if (score[lhs] != score[rhs]) {
                             return score[lhs] > score[rhs];
                         }
                         return lhs < rhs;
                     });

           for (int rank = 0; rank < k; ++rank) {
               const int expert = order[rank];
               if (load[expert] < capacity) {
                   ++load[expert];
               }
           }
       }

       std::int64_t penalty = 0;
       for (int value : load) {
           penalty += static_cast<std::int64_t>(value) * value;
       }

       std::cout << penalty << '\n';
       for (int expert = 0; expert < e; ++expert) {
           if (expert != 0) {
               std::cout << ' ';
           }
           std::cout << load[expert];
       }
       std::cout << '\n';
       return 0;
   }

Python 实现
-----------

.. code-block:: python

   import sys


   def main() -> None:
       first = sys.stdin.buffer.readline().split()
       if not first:
           return

       n, e, k, capacity = map(int, first)
       load = [0] * e

       for _ in range(n):
           score = list(map(int, sys.stdin.buffer.readline().split()))
           order = sorted(range(e), key=lambda j: (-score[j], j))

           for expert in order[:k]:
               if load[expert] < capacity:
                   load[expert] += 1

       penalty = sum(value * value for value in load)
       print(penalty)
       print(*load)


   if __name__ == "__main__":
       main()

从题目到真实 MoE
-----------------

这道题是 MoE dispatch 的简化模拟，但要区分教学模型与真实训练：

- Router 通常输出概率或 logits，可能采用 Top-1/Top-2，并把 gate weight 乘到专家输出上。
- Capacity 常由 batch token 数、专家数和 capacity factor 共同决定；超额 token 可能丢弃、重路由或走共享专家。
- 多设备 Expert Parallelism 还要执行 All-to-All，把 Token 发到专家所在设备，再把结果发回。
- :math:`\sum load_j^2` 在总路由数固定时偏好均衡分布，但若 token 可以丢弃，单独最小化它会错误地奖励
  『少处理 token』。真实系统通常使用归一化 load-balancing auxiliary loss，并同时约束路由质量和丢弃率。
- Router collapse/dead expert 是常见问题，还会考 entropy、expert utilization、router z-loss 和 capacity factor。

编程题二：流水线并行阶段划分
==================================

题目重述
--------

模型有 :math:`n` 个按顺序执行的层，要切成恰好 :math:`p` 个非空、连续 stage。第 :math:`i` 层计算时间为
``time[i]``；若在第 :math:`k` 层后切分，要支付 ``comm[k]``。每个 stage 的计算时间之和不能超过 :math:`T`，
求最小总通信开销；不存在合法方案时输出 ``-1``。

.. code-block:: text

   1 <= n <= 1000
   1 <= p <= n
   1 <= T <= 100000
   1 <= time[i] <= 100
   1 <= comm[i] <= 10

输入输出与样例
--------------

.. code-block:: text

   输入
   n p T
   time[1] time[2] ... time[n]
   comm[1] comm[2] ... comm[n-1]

   输出
   最小通信开销；无解输出 -1

样例一：

.. code-block:: text

   输入
   5 3 10
   2 4 6 3 7
   1 1 1 1

   输出
   2

可切为 ``[2, 4] | [6, 3] | [7]``，三个 stage 时间分别为 6、9、7，边界通信代价为
``comm[2] + comm[4] = 2``。

样例二：

.. code-block:: text

   输入
   4 2 7
   3 5 4 2
   1 2 3

   输出
   -1

前缀和与 DP
-----------

使用 1-based 层下标，定义：

.. math::

   pre[i]=\sum_{t=1}^{i}time[t]

层 :math:`k+1..i` 的计算时间为 :math:`pre[i]-pre[k]`。再定义
:math:`dp_s[i]` 为『前 i 层恰好切成 s 个非空 stage 的最小通信开销』。最后一个 stage 为
:math:`k+1..i` 时：

.. math::

   dp_s[i]=\min_k\{dp_{s-1}[k]+comm[k]\}

其中必须满足：

.. math::

   s-1\le k\le i-1,\qquad pre[i]-pre[k]\le T

``k >= s-1`` 保证前 k 层至少能形成 s-1 个非空 stage，``k <= i-1`` 保证最后一个 stage 非空。
基础状态为：

.. math::

   dp_1[i]=
   \begin{cases}
   0, & pre[i]\le T\\
   +\infty, & \text{其他}
   \end{cases}

朴素枚举每个 k 的复杂度是 :math:`O(pn^2)`。

为什么能用单调队列
------------------

因为所有 ``time[i]`` 都为正数，前缀和严格递增。对固定 i，满足
:math:`pre[i]-pre[k]\le T` 的 k 是一个连续后缀。令 ``left[i]`` 是最小合法 k，则当前转移窗口为：

.. math::

   \max(s-1,left[i])\le k\le i-1

当 i 递增时，窗口左右端点都只向右移动。对固定阶段数 s，候选值
``dp_prev[k] + comm[k]`` 一旦算出就不再变化，因此可用递增单调队列维护滑动窗口最小值：

1. i 向右移动时，把新切分点 ``k=i-1`` 加入队尾。
2. 加入前弹出队尾所有不小于新值的候选；它们更差且更早过期。
3. 弹出所有 ``k < max(s-1, left[i])`` 的队首过期候选。
4. 队首就是当前窗口最小值。

``left[i]`` 本身也可用双指针在线性时间求出。每个 k 在每一轮 DP 中最多入队一次、出队一次，
所以每轮是 :math:`O(n)`。

正确性证明
----------

先对阶段数 s 做归纳。

**基础状态**：s=1 时只有一个 stage，前 i 层总时间不超过 T 当且仅当方案合法，且没有边界通信，
所以 ``dp[1][i]`` 的初始化正确。

**归纳假设**：``dp[s-1][k]`` 已正确表示前 k 层恰好分成 s-1 段的最优代价。

**归纳步骤**：任何把前 i 层分成 s 段的合法方案，都有唯一最后切分点 k。其前半部分最优代价由归纳假设
给出，最后一段合法条件正是 :math:`pre[i]-pre[k]\le T`，新增边界代价正是 ``comm[k]``；反过来，
任一满足约束的 k 都能构造合法的 s 段方案。因此状态转移枚举且只枚举全部合法方案。

单调队列始终删除窗口外候选；对窗口内候选，只删除一个值不小于且更早过期的候选，所以不会删除未来可能
成为唯一最优解的元素。队首因此等于状态转移要求的最小值。归纳完成后 ``dp[p][n]`` 即为答案。

复杂度
------

前缀和和 ``left`` 为 :math:`O(n)`；p 轮 DP 每轮 :math:`O(n)`，总时间 :math:`O(pn)`。
使用滚动数组后，空间复杂度为 :math:`O(n)`。

C++17 实现
----------

.. code-block:: cpp

   #include <algorithm>
   #include <cstdint>
   #include <deque>
   #include <iostream>
   #include <limits>
   #include <utility>
   #include <vector>

   int main() {
       std::ios::sync_with_stdio(false);
       std::cin.tie(nullptr);

       int n, stages;
       std::int64_t limit;
       if (!(std::cin >> n >> stages >> limit)) {
           return 0;
       }

       std::vector<std::int64_t> prefix(n + 1, 0);
       for (int i = 1; i <= n; ++i) {
           std::int64_t value;
           std::cin >> value;
           prefix[i] = prefix[i - 1] + value;
       }

       // comm[k] 是在第 k 层后切分的代价；不会访问 comm[n]。
       std::vector<std::int64_t> comm(n, 0);
       for (int k = 1; k < n; ++k) {
           std::cin >> comm[k];
       }

       // left[i]：最后一段以 i 结尾时，满足时间约束的最小 k。
       std::vector<int> left(n + 1, 0);
       int low = 0;
       for (int i = 1; i <= n; ++i) {
           while (low < i && prefix[i] - prefix[low] > limit) {
               ++low;
           }
           left[i] = low;
       }

       const std::int64_t inf = std::numeric_limits<std::int64_t>::max() / 4;
       std::vector<std::int64_t> dp(n + 1, inf);
       for (int i = 1; i <= n; ++i) {
           if (prefix[i] <= limit) {
               dp[i] = 0;
           }
       }

       for (int s = 2; s <= stages; ++s) {
           std::vector<std::int64_t> next(n + 1, inf);
           std::deque<std::pair<int, std::int64_t>> queue;

           for (int i = s; i <= n; ++i) {
               const int cut = i - 1;
               if (dp[cut] != inf) {
                   const std::int64_t candidate = dp[cut] + comm[cut];
                   while (!queue.empty() &&
                          queue.back().second >= candidate) {
                       queue.pop_back();
                   }
                   queue.emplace_back(cut, candidate);
               }

               const int first_valid = std::max(s - 1, left[i]);
               while (!queue.empty() && queue.front().first < first_valid) {
                   queue.pop_front();
               }
               if (!queue.empty()) {
                   next[i] = queue.front().second;
               }
           }
           dp.swap(next);
       }

       std::cout << (dp[n] == inf ? -1 : dp[n]) << '\n';
       return 0;
   }

Python 实现
-----------

.. code-block:: python

   import sys
   from collections import deque


   def min_communication(
       n: int,
       stages: int,
       limit: int,
       times: list[int],
       comm: list[int],
   ) -> int:
       prefix = [0] * (n + 1)
       for i in range(1, n + 1):
           prefix[i] = prefix[i - 1] + times[i]

       left = [0] * (n + 1)
       low = 0
       for i in range(1, n + 1):
           while low < i and prefix[i] - prefix[low] > limit:
               low += 1
           left[i] = low

       inf = 10**30
       dp = [inf] * (n + 1)
       for i in range(1, n + 1):
           if prefix[i] <= limit:
               dp[i] = 0

       for stage in range(2, stages + 1):
           next_dp = [inf] * (n + 1)
           candidates: deque[tuple[int, int]] = deque()

           for i in range(stage, n + 1):
               cut = i - 1
               if dp[cut] != inf:
                   value = dp[cut] + comm[cut]
                   while candidates and candidates[-1][1] >= value:
                       candidates.pop()
                   candidates.append((cut, value))

               first_valid = max(stage - 1, left[i])
               while candidates and candidates[0][0] < first_valid:
                   candidates.popleft()
               if candidates:
                   next_dp[i] = candidates[0][1]

           dp = next_dp

       return -1 if dp[n] == inf else dp[n]


   def main() -> None:
       data = list(map(int, sys.stdin.buffer.read().split()))
       if not data:
           return

       n, stages, limit = data[:3]
       pos = 3
       times = [0] + data[pos : pos + n]
       pos += n
       comm = [0] + data[pos : pos + n - 1]
       print(min_communication(n, stages, limit, times, comm))


   if __name__ == "__main__":
       main()

从题目到真实 Pipeline Parallelism
---------------------------------

原题把 stage 的计算量压成标量时间，把通信压成切分边代价，是图划分问题的一维简化。真实系统还要考虑：

- 将 mini-batch 切成 micro-batch，使多个 stage 同时工作，减少 pipeline bubble。
- Forward/Backward 的时间和显存不同，最慢 stage 决定稳态吞吐，不能只限制每段小于 T。
- 激活张量大小决定点对点通信量；同一边在 forward 和 backward 都可能通信。
- GPipe 是 fill-drain schedule；1F1B 在稳态交替执行一次 forward 和一次 backward，通常降低峰值激活显存。
- Pipeline Parallelism 可与 Data Parallelism、Tensor Parallelism 和 Expert Parallelism 组成 3D/4D 并行。
- 自动划分通常是多目标优化：stage latency、memory、communication、拓扑和重计算策略共同决定最优边界。

知识点扩展
======================

理论题
--------

.. csv-table:: Inferred Theory Topics
   :header: "主题", "可能问法", "必须掌握"
   :widths: 22, 38, 40

   "概率统计", "条件概率、Bayes、协方差、MLE/MAP、置信区间", "公式假设；独立、不相关、条件独立的区别"
   "优化", "SGD/AdamW、学习率、梯度累积、裁剪、正则化", "更新公式；收敛与显存/吞吐 trade-off"
   "归一化", "BatchNorm 与 LayerNorm 为什么适用场景不同", "统计维度、train/eval 行为、小 batch 问题"
   "Transformer", "为何除以 sqrt(d_k)、MHA/GQA/MQA、位置编码", "Tensor shape、复杂度、KV Cache 的来源"
   "模型评估", "Precision/Recall/F1/AUC、PPL、BLEU/ROUGE", "类别不平衡、阈值、数据泄漏和指标局限"
   "训练并行", "DP/DDP、TP、PP、EP、ZeRO/FSDP", "切分对象、通信 collective、显存节省和适用边界"
   "推理优化", "量化、Continuous Batching、Prefix Cache、Speculative Decoding", "延迟、吞吐、显存和精度"
   "MoE", "Top-K、capacity factor、负载均衡、dead expert", "路由质量、通信和专家利用率"
   "多模态", "ViT、cross-attention、对比学习、模态对齐", "Early/Late Fusion、缺失模态、梯度失衡"
   "RAG/Agent", "召回与重排、chunk、tool calling、评测", "检索错误与生成错误分层，权限和提示注入风险"
   "AI 系统", "算术强度、memory-bound、GPU/NPU kernel", "FLOPs 不等于速度；带宽、layout、融合和并行度"

举一反三
------------

1. **为何 Attention 除以** :math:`\sqrt{d_k}`？
   若 Q/K 分量近似独立且方差固定，点积方差随 :math:`d_k` 增长；缩放可避免 Softmax 过早饱和和梯度过小。
2. **BatchNorm 与 LayerNorm 的区别？**
   BatchNorm 跨 batch 样本统计同一通道，训练和推理状态不同；LayerNorm 在单样本特征维归一化，适合变长序列
   和小 batch，因此 Transformer 通常使用 LayerNorm/RMSNorm。
3. **Adam 为什么比 SGD 占更多显存？**
   Adam 通常为每个参数保存一阶矩和二阶矩；混合精度训练还可能保存 FP32 master weight。
4. **类别极不平衡时为什么 Accuracy 会误导？**
   全预测为多数类也可能很高；应结合 confusion matrix、Precision、Recall、F1、PR-AUC 和业务代价。
5. **GQA 为什么能降低 KV Cache？**
   多个 query head 共享更少的 K/V head，缓存量随 KV head 数下降，但可能付出一定模型质量或 kernel 适配成本。
6. **Data/Tensor/Pipeline Parallelism 分别切什么？**
   DP 复制模型切数据，TP 切单层张量计算，PP 切连续层，EP 切专家；它们分别引入 gradient all-reduce、
   layer 内 collective、stage P2P 和 token all-to-all。
7. **INT8/FP8 量化为何不一定加速？**
   还取决于硬件指令、kernel、反量化、内存布局和 batch size；模型变小不等于端到端延迟必然降低。
8. **如何定位 MoE expert collapse？**
   观察每个专家 token count、router probability、丢弃率、entropy 和跨设备通信；再调 auxiliary loss、
   capacity factor、router noise 或共享专家，而不是只看总 loss。

编程题
--------------

编程仍是侧重经典算法：

- **Top-K/路由/调度**：排序、heap、quickselect、稳定 tie-break、容量模拟。
- **连续分段**：前缀和、DP、二分、滑动窗口、单调队列、分治优化。
- **显存块管理**：区间合并、free list、LRU、引用计数、分页模拟。
- **计算图与依赖**：DAG 拓扑排序、关键路径、最短路、并查集。
- **Batching/Scheduling**：优先队列、事件模拟、最大吞吐或最小等待时间。
- **Tensor shape**：广播规则、矩阵维度、stride/layout、reshape/transpose 后的索引。
- **数据处理**：Hash、去重、滑动统计、采样、字符串/token 序列处理。
- **工程边界**：64-bit 溢出、浮点误差、稳定排序、空输入、无法划分、时间和空间复杂度。

在 AI 领域场景用到算法，如『Token 路由』先看成带 tie-break 的 Top-K 和容量计数；『模型 stage』
先看成有上限的连续数组分段；『KV block』先看成动态分页和引用计数。场景陌生时，数据结构和状态转移仍然熟悉。

总结
====

这套题的重点不是某一个模型，而是 AI 工程的三层能力：

1. **数学层**：能从概率、损失函数、向量和矩阵公式推出结论，并说清公式成立条件。
2. **模型与系统层**：能解释训练和推理中的显存、计算、通信、精度和吞吐 trade-off。
3. **编程层**：能把 MoE、KV Cache、Pipeline 等术语还原为排序、模拟、DP、队列和图算法，并给出证明与复杂度。

只了解『Checkpointing 省显存』『PagedAttention 管 KV Cache』还不够。要进一步追问『省的是哪部分显存』『为什么
块不能无限小』『为什么合法切分点形成连续窗口』『真实 MoE 为什么不能只最小化负载平方和』，才算建立了
可以迁移的知识框架。

References
==========

- `PyTorch Activation Checkpointing <https://docs.pytorch.org/docs/stable/checkpoint.html>`_
- `Attention Is All You Need <https://arxiv.org/abs/1706.03762>`_
- `Deep Residual Learning for Image Recognition <https://arxiv.org/abs/1512.03385>`_
- `Efficient Memory Management for Large Language Model Serving with PagedAttention <https://arxiv.org/abs/2309.06180>`_
- `vLLM Automatic Prefix Caching Design <https://docs.vllm.ai/en/latest/design/prefix_caching.html>`_
- `Switch Transformers <https://arxiv.org/abs/2101.03961>`_
- `GShard <https://arxiv.org/abs/2006.16668>`_
- `GPipe <https://arxiv.org/abs/1811.06965>`_
- `PyTorch Pipeline Parallelism <https://docs.pytorch.org/docs/stable/distributed.pipelining.html>`_
