.. Michael Wu Copyright 2026,-

:Authors: Michael Wu
:Version: 0.2

LLM Runtime
***********

Overview
========

简单了解一下 LLM 的底层实现。从传统程序员熟悉的进程、内存、文件格式和 CPU hot path 等视角类比入手来理解。
先把 inference runtime 当成一个普通 Linux process 看：它加载什么文件，分配什么内存，主循环怎么跑，CPU 时
间花在哪里。

以 ``llama2.c`` 为例，一个最小的 LLM runtime 运行时：

.. code-block:: text

   LLM runtime process
       |
       |  argv: model weights file, tokenizer file, prompt, sampling params
       v
   load / mmap model weights
       |
       |  load binary weights into memory or map them into process address space
       v
   heap activation buffers
       |
       |  allocate temporary tensors and KV cache
       v
   decode loop
       |
       |  consume prompt tokens, then generate one token at a time
       v
   stdout token stream

这里的模型权重文件不是 ELF 里的东西，而是 LLM runtime 额外加载的数据文件。普通 ELF 进程只有自己
的 text / data / shared library 等常规进程地址空间映射；``llama2.c`` 这类推理程序会再通过 argv
拿到模型权重文件路径，把模型参数映射进自己的 address space。

``checkpoint`` 是 ML 领域常见术语，通常指训练过程中保存下来的模型状态快照。它可能包含 weights、optimizer
state、训练步数等信息。到了 inference 阶段，真正需要的主要是 weights. ``llama2.c`` 文档里也把这个输入文件
叫 checkpoint，可以理解为『模型权重文件』。

传统 web 服务端进程通常是 request -> handler -> I/O -> response。LLM runtime 更像一个紧凑的数值计算程序：

- 输入不是 HTTP request，而是 prompt text
- 第一层解析不是 msg parser，而是 tokenizer
- 主要热路径不是业务逻辑分支，而是大量 ``matmul`` (matrix multiplication)、归一化、attention 和采样。
- 模型参数不是代码段，而是一个巨大的只读数据集，通常来自模型权重文件。
- 每一步生成都依赖之前 token 的状态，这是自回归生成（autoregressive），所以 decode loop 是顺序推进的。

.. note::

   这里先把范围收窄到 inference runtime。Training 还要处理 backward、optimizer、gradient、
   activation checkpointing、distributed data parallel 等问题，复杂度高很多。把 inference 看明白之后，
   再回头看 training 会更顺。

   再解释一下 autoregressive, 它是指模型在生成下一个 token 时，会把之前生成的 token 作为输入。每一步
   生成都依赖之前的状态，所以生成过程是顺序的，不能并行预测所有 token。终止条件通常是生成了 ``EOS`` token 或
   达到最大长度。

   这里的热点 ``matmul`` 是指矩阵乘法。默认浮点模型主要跑 float32 / float16 / bfloat16 这类浮点矩阵乘；
   量化模型会把权重压成 int8 等整数格式，再用整数或混合精度 kernel 计算，累加和输出阶段可能再转回更高精度。
   关于模型的量化可以看：:ref:`模型的量化 <llm-runtime-quantization>`。

推理框架 llama2.c
====================

llama2.c 介绍
---------------

教学 demo 很多，最后还是 Andrej Karpathy 的 ``llama2.c`` 最适合这个切入点。原因很直接：它用一个 C 文件把
Llama 2 风格模型的 CPU 推理路径跑通，代码短，又接近真实 runtime 的骨架。

.. csv-table:: Demo Choice
   :header: "项目", "代码规模 / 关注点", "适合建立的模型", "取舍"
   :widths: 18, 32, 30, 20

   "llama2.c", "``run.c`` 约 973 行 C；model weights + tokenizer + decode loop", "推理 runtime、内存布局、CPU 热点", "贴近系统背景"
   "picoGPT", "GPT-2 forward pass 可压到几十行 NumPy", "Transformer forward 的最小数学路径", "系统 runtime 味道弱"
   "nanoGPT", "PyTorch 训练 / finetune 仓库，代码仍然很短", "训练 loop、GPT 模型定义、实验流程", "偏 training stack"

``llama2.c`` 的价值不在于工程性能追到生产级，而在于它把复杂系统压成几个清楚的组件：

- 模型权重文件：保存二进制模型参数，``llama2.c`` 文档里称为 ``checkpoint``。
- ``tokenizer``：文本和 token id 的互转。
- ``Transformer``：模型配置、权重指针、运行时状态。
- ``forward``：单 token 前向计算。
- ``Sampler``：从 logits 里选下一个 token。
- ``generate`` / ``chat``：外层 decode loop。

.. note::

   ``logits`` 是模型给 vocab 里每个候选 token 打的原始分数，通常是 float，可以是负数、0 或正数，
   没有固定上下界。它不是概率，更像『未归一化的偏好分数』。

   一个 token 的 logit 越高，表示模型越倾向选它；越低，表示模型越不倾向选它。真正重要的是不同 token
   之间的相对差值：``10`` 和 ``9`` 差距不大，两个 token 都还有机会；``10`` 和 ``0`` 差距很大，前者会
   明显压过后者。理论上，经过 ``softmax`` 后，每个值都会落在 ``(0, 1)`` 区间内，所有值加起来等于 ``1``，
   这些相对差距才会变成概率分布；实际浮点计算中，极小值可能下溢成 ``0``。

llama2.c 模块
---------------

从系统程序角度看，``llama2.c`` 的模块边界比深度学习框架更容易理解。

.. csv-table:: llama2.c Runtime Modules
   :header: "模块", "大致职责", "系统视角"
   :widths: 22, 44, 34

   "``Config``", "保存模型维度、层数、head 数、vocab size、context length", "类似文件头里的 ABI / layout metadata"
   "``TransformerWeights``", "把模型权重文件中的连续权重切成多个 typed pointer", "类似对 mmap 区域做结构化视图"
   "``RunState``", "保存 activation buffer、临时向量、attention buffer、KV cache", "进程 heap 上的工作区"
   "``Tokenizer``", "把 UTF-8 文本编码成 token id，再把 token id 解码回文本片段", "文本编码层"
   "``Sampler``", "根据 logits、temperature、top-p 和随机数选择下一个 token", "策略层，不改变模型权重"
   "``forward``", "对当前 token 和当前位置执行一次 Transformer 前向计算", "CPU 热路径"
   "``generate`` / ``chat``", "维护 token 序列、调用 forward、打印输出", "主事件循环"

这些结构可以分成两类：启动阶段准备好的东西，和每生成一个 token 都会走的东西。

.. code-block:: text

   启动阶段：

       模型权重文件
           ->  TransformerWeights
           ->  得到一组只读的权重指针

       malloc 出来的工作区
           ->  RunState
           ->  保存 activation buffer 和 KV cache

   生成阶段：

       prompt text
           ->  Tokenizer
           ->  token ids

       当前 token id + position
           ->  forward() // 跑一遍 Transformer，计算当前位置的输出
           ->  logits    // vocab 里每个 token 的下一步分数，分数最高不一定直接选
                         // vocab 是模型能输出的 token 表

       logits
           ->  Sampler   // 按 temperature / top-p 等策略 select 一个 token
           ->  next token id

llama2.c 实现
--------------

结合 ``run.c`` 里的 ``generate``、``forward`` 和 ``matmul``，核心路径类似下面伪代码:

.. code-block:: python

   function forward(token, pos):
       # 单 token 的 Transformer 计算
       x = embedding[token]

       # 逐层跑 Transformer block，模型有 n_layers 层就循环 n_layers 次
       for each layer:
           h = rmsnorm(x)
           q = matmul(h, Wq)
           k = matmul(h, Wk)  # 写入当前 position 的 KV cache
           v = matmul(h, Wv)  # 写入当前 position 的 KV cache
           attn = attention(q, KV cache[0..pos])
           x = x + matmul(attn, Wo)

           h = rmsnorm(x)
           ffn = silu(matmul(h, W1)) * matmul(h, W3)
           x = x + matmul(ffn, W2)

       x = rmsnorm(x)
       logits = matmul(x, classifier_weight)
       return logits

   function sampler_select(logits):
       # temperature 为 0 时直接 argmax；否则 softmax 后按 top-p 等策略采样
       return next_token

   function main(prompt):
       # generate(): 自回归外层循环
       prompt_tokens = tokenizer.encode(prompt)
       token = prompt_tokens[0]
       pos = 0

       while pos < max_steps:
           # 每轮 loop 都调用一次 forward()
           logits = forward(token, pos)

           # 先消耗 prompt tokens，prompt 结束后才开始采样生成
           if pos < len(prompt_tokens) - 1:
               next = prompt_tokens[pos + 1]
           else:
               next = sampler_select(logits)

           # llama2.c 这里会把 prompt 阶段和生成阶段的 token 都 decode / print
           # prompt encode 后再 decode，语义通常一样，但不保证 byte-for-byte 完全相同
           #     原因是 decode 可能处理 BOS 后空格、特殊 token、byte fallback 等 tokenizer 规则
           print(tokenizer.decode(token, next))
           token = next
           pos += 1

``matmul`` 在源码里就是矩阵乘法热点：把一段输入向量和权重矩阵相乘，输出新向量。

``llama2.c`` 没考虑多 session 并发，因为它是教学用的单进程命令行 demo：一次只维护一份 ``RunState``、
一份 ``KV cache`` 和一个 decode loop。真正的 serving runtime 还要处理多个 session 的调度、batching
和 KV cache 隔离，后面单独展开。如果考虑的话，可以做类似下面的改造：

.. code-block:: python

   model = load_model_weights_once()
   waiting_queue = Queue()
   active_sessions = []

   function submit_request(prompt):
       session = SessionState(
           prompt_tokens = tokenizer.encode(prompt),
           pos = 0,
           kv_cache = allocate_kv_cache(),
           output_stream = new_stream(),
       )

       if can_fit(session):
           active_sessions.append(session)
       else:
           waiting_queue.push(session)  # 超过并发数或 KV cache 预算，先排队

   function scheduler_loop():
       while true:
           batch = pick_ready_sessions(active_sessions)

           # 共享同一份 model weights，但每个 session 带自己的 pos / KV cache
           logits_batch = model.forward_batch(batch)

           for session, logits in zip(batch, logits_batch):
               next = session.select_next_token(logits)
               session.stream(tokenizer.decode(session.token, next))
               session.advance(next)

               if session.done():
                   active_sessions.remove(session)
                   free(session.kv_cache)

           while waiting_queue and has_capacity():
               active_sessions.append(waiting_queue.pop())

概念数据流
==========

整体路径
--------

前面的 ``llama2.c 实现`` 更像源码级伪代码，关注函数怎么调用。这里换成概念图，先把术语和数据对象对齐，
后面讲内存、``KV cache`` 和并发时会反复用到这些词。

这里解释几个关键概念：

- tokenizer encode: 把输入文本切成 token，并转换成 token id 数组。
- tokenizer decode: 把模型输出的 token id 转回文本片段，用来逐步打印。
- logits over vocabulary: 模型输出的分数向量，长度等于 vocab size，每个位置对应一个 token 的分数。

.. note::

   Tokenizer decode 可以近似理解成 ``id -> text piece`` 的查表；encode 不是简单的 ``string -> id`` map。
   encode 通常要按 BPE / SentencePiece 这类规则做切分和 merge，最后才得到一串 token id。

整体流程大概如下：

.. code-block:: text

   prompt text
       |
       |  tokenizer encode
       v
   prompt token ids // token id 是整数编号，类似 vocab 表里的 index
       |
       v
   decode loop <----------------------------------+
       |                                          |
       |  forward(token, pos)                     |
       v                                          |
   logits over vocabulary                         |
       |                                          |
       |  sampler                                 |
       v                                          |
   next token id                                  |
       |                                          |
       |  tokenizer decode                        |
       v                                          |
   print text piece -- 继续生成下一个 token -------+

核心是 loop。模型不会一次预测完整 answer，而是自回归地预测下一个 token。现代 runtime 通常先用 prefill
一次处理多个 prompt token，再进入逐 token decode；``llama2.c`` 为了保持实现简单，prompt 阶段也逐 token
调用 ``forward``：

.. code-block:: text

   prompt: "Linux kernel is"

   prompt phase: feed prompt tokens one by one (llama2.c)
   step 1: predict " a"
   step 2: feed " a", predict " monolithic"
   step 3: feed " monolithic", predict " kernel"
   ...

单步内部状态
------------

上面的图说明外层数据流，这里只看 decode loop 里的一步。关键差异是 ``forward`` 不只是算 logits，
还会把当前 token 的 K/V 写进 ``KV cache``，下一步 attention 会继续用这些历史状态。

.. code-block:: text

   step i:

       input: token_i, position_i, KV cache[0..i-1]

       forward(token_i, position_i)
           |
           +-- compute K_i / V_i
           |       |
           |       v
           |   append to KV cache[i]
           |
           +-- attend to KV cache[0..i]
           |
           v
       logits
           |
           |  sampler select
           v
       token_{i+1}

   next step:

       input: token_{i+1}, position_{i+1}, KV cache[0..i]

和普通 server 的 event loop 不同，LLM decode loop 的每次迭代都很重。一次迭代通常会穿过所有 Transformer layer，
然后在 vocab 维度上得到一组 logits。

多 session 并发
---------------

如果部署成服务，同时来了多个请求，模型权重通常是共享的，只读；每个 session 自己保存 prompt token、
当前位置、``KV cache``、sampler 状态和输出流。

.. code-block:: text

   read-only model weights
       |
       +-- session A: token pos, KV cache, sampler state, output stream
       |
       +-- session B: token pos, KV cache, sampler state, output stream
       |
       +-- session C: token pos, KV cache, sampler state, output stream

   scheduler:

       step A -> step B -> step C -> step A -> ...

这和普通 web server 的并发不太一样。普通请求经常是 handler 阻塞在 I/O 上；LLM session 每往前走一个 token，
都要跑一遍重计算。实际 serving runtime 会做调度，把多个 session 的下一步 token 放到一起算，也就是 batching。

.. code-block:: text

   no batching:

       forward(session A, one token)
       forward(session B, one token)
       forward(session C, one token)

   batching:

       forward([A token, B token, C token])

并发时最关键的状态是 ``KV cache``。模型权重可以共享，但 ``KV cache`` 不能混；它记录的是每个 session
自己的历史上下文。session 越多、context 越长，``KV cache`` 占用越大，调度器要在吞吐、延迟和内存之间权衡。

进程和内存视角
==============

模型权重文件
------------

模型权重文件更像一个外置的 ``.rodata`` 数据文件：里面不是指令，也不是进程运行时状态，而是模型配置和一大块
只读权重。它不是 ELF section，只是从访问属性上看，更接近被 runtime 映射进来的 read-only data blob。
``llama2.c`` 会读取文件头得到 ``Config``，然后把后面的权重区域映射或读入内存。

这个阶段我更关心的不是『权重为什么有用』，而是它的访问模式：

- 权重在推理时是 read-only。
- 权重体积极大，远大于代码段。
- 主要访问发生在 ``matmul``，顺序读和 cache locality 很关键。
- 多进程部署时，read-only mmap 理论上可以被 page cache 和物理页共享。

``TransformerWeights`` 不复制权重，而是把连续内存解释成不同 tensor：

.. code-block:: text

   model weights mapped memory
       |
       +-- token_embedding_table
       +-- rms_att_weight
       +-- wq
       +-- wk
       +-- wv
       +-- wo
       +-- rms_ffn_weight
       +-- w1 / w2 / w3
       +-- final rms weight
       +-- classifier weight

这和在 kernel / hypervisor 里解析 ELF、device table、firmware blob 很像：先读 header，再按 layout 把 offset
变成 typed view。区别是这里的数据规模很大，而且会被 CPU 反复扫描。

RunState
--------

在 ``llama2.c`` 中，``RunState`` 是这次模型执行使用的 mutable workspace。它包含当前 token 前向计算要用的
临时向量，以及跨 token 保留的 ``KV cache``。

.. csv-table:: RunState Mental Model
   :header: "数据", "生命周期", "作用"
   :widths: 24, 28, 48

   "activation buffer", "一次 forward 内反复复用", "保存当前 layer 的中间结果，如 ``x``、``xb``、``hb``"
   "attention buffer", "一次 attention 计算内复用", "保存当前位置对历史位置的 attention score"
   "logits", "每一步生成后更新", "vocab 中每个 token 的下一步分数"
   "key cache", "启动时一次性分配；有效内容随 position 增加", "保存历史 token 的 K 向量，避免重复计算"
   "value cache", "启动时一次性分配；有效内容随 position 增加", "保存历史 token 的 V 向量，attention 需要读取"

KV cache 是理解 LLM latency 的关键。没有 KV cache 时，每生成一个新 token 都要重新跑一遍历史 prefix 的
Transformer 计算，其中包括重新计算所有历史 token 的 K/V。有了 KV cache，新 token 只计算自己的 K/V，
然后和历史 K/V 做 attention。

.. code-block:: text

   token 0: compute K0, V0 -> store
   token 1: compute K1, V1 -> attend to K0..K1 / V0..V1
   token 2: compute K2, V2 -> attend to K0..K2 / V0..V2

这也是为什么 context 越长，单 token 越慢：即使 K/V 不重算，attention 仍要看更长的历史。

Tokenizer
---------

Tokenizer 是文本到模型整数输入的编码层。输入通常是 UTF-8 text，tokenizer 按 vocab / merge 规则切成 token，
再把 token 转成 integer token id。模型不直接处理字符串，而是处理这些整数 id；真正的文本片段保存在
tokenizer 的 vocab / merge 规则里。

.. code-block:: text

   "hello world"
       |
       v
   [token_id_0, token_id_1, ...]
       |
       v
   embedding lookup

几个容易踩错的点：

- token 不等于字符，也不等于单词。
- 一个中文字符、一个英文词片段、一个空格前缀，都可能成为 token 的一部分。
- decode 时要把 token id 还原成 text piece，逐步打印才像 streaming output。
- vocab size 越大，最后的 classifier projection、softmax 和采样通常也越贵，其中 classifier projection 更重。

一次 token 的 forward path
===========================

一个 token 的 forward pass 可以压成下面这条路径：

.. code-block:: text

   token id
       |
       v
   embedding lookup
       |
       v
   for each layer:
       RMSNorm
       Q/K/V projection
       RoPE
       append K/V cache
       attention over previous positions
       output projection
       residual add
       RMSNorm
       feed-forward network
       residual add
       |
       v
   final RMSNorm
       |
       v
   classifier matmul
       |
       v
   logits[vocab_size]

Embedding
---------

Embedding lookup 可以理解为一个大数组索引：

.. code-block:: text

   token_embedding_table[token_id] -> vector<float>[dim]

这一步没有复杂控制流，就是把 token id 映射成 ``dim`` 维浮点向量。后面的所有层都在这个向量空间里做计算。

RMSNorm
-------

``RMSNorm`` 是归一化层，作用是稳定数值范围。系统视角看，它是一次向量扫描：

.. code-block:: text

   x -> square sum -> scale -> multiply learned weight

它不像 ``matmul`` 那样占最多 FLOPs，但会读写整条向量，所以仍然受 memory bandwidth 和 cache 影响。

Attention
---------

Attention 的核心是让当前 token 读取历史 token 的信息。当前 token 生成 ``Q``，每个历史 token 有缓存下来的
``K`` 和 ``V``。

.. code-block:: text

   Q(current token) dot K(history token) -> score
   softmax(scores)                      -> weights
   sum(weights * V(history token))      -> context vector

从系统角度看，attention 的代价会随着 position 增长。第 10 个 token 只看 10 个位置，第 1000 个 token 要看
1000 个位置。KV cache 解决的是『不要重算历史 K/V』，不是『不要读取历史 K/V』。

``llama2.c`` 还支持 grouped-query attention：当 ``n_kv_heads < n_heads`` 时，多个 query head 共享一组
K/V head。此时 KV cache 每个位置的宽度不是 ``dim``，而是：

.. code-block:: text

   kv_dim = dim * n_kv_heads / n_heads

这样可以减少 KV cache 占用和读取量。

Feed Forward Network
--------------------

Feed Forward Network 主要是几次矩阵乘和非线性函数。Llama 2 风格模型常见的是 SwiGLU 结构。这里先不展开数学，
把它当成每层里另一个大 FLOPs 区域。

.. code-block:: text

   x -> w1 matmul -> activation
   x -> w3 matmul -> gate
   activation * gate -> w2 matmul -> output

Calc logits
-----------

所有 layer 结束后，runtime 会把最终 hidden state 投影到 vocab size：

.. code-block:: text

   hidden[dim] x classifier_weight[vocab_size][dim] -> logits[vocab_size]

``logits`` 不是概率，而是未归一化分数。Sampler 会根据 temperature、top-p 等策略把 logits 变成下一个 token。

推理执行热点
============

Matmul
------

LLM inference 的执行热点主要是 ``matmul``。如果把整个 runtime 当 perf profile 看，很多时间会落在：

- attention 里的 Q/K/V projection。
- attention output projection。
- FFN 里的 ``w1``、``w2``、``w3``。
- 最后的 classifier projection。

朴素 ``matmul`` 很容易写，但快的 ``matmul`` 是另一个世界：cache blocking、SIMD、prefetch、NUMA、thread
partition、quantized kernel 都会影响吞吐。``llama2.c`` 的意义是先让你看清调用点和数据流。

Memory bandwidth
----------------

推理不只是算力问题，也是内存带宽问题。权重很大，每生成一个 token 都要读大量参数。小模型可以放进 cache
更多部分，大模型会更频繁地从 DRAM 拉数据。

一个粗略判断：

.. code-block:: text

   if weights fit cache better:
       latency improves
   else:
       DRAM bandwidth becomes visible

这就是为什么量化不仅减少磁盘大小，也可能提高推理速度：同样的内存带宽能搬更多参数。

OpenMP
------

``llama2.c`` 提供 OpenMP 构建方式，把部分计算并行到多个 CPU thread。直觉上它类似把 ``matmul`` 的输出行或
元素切给多个 worker。

几个实际的坑：

- thread 数不是越多越好，超过内存带宽或 cache 能承受的范围后收益会下降。
- 小 batch / 单 token decode 的并行粒度有限。
- 多线程会增加调度、同步和 cache contention。
- 对系统调优来说，要同时看 CPU utilization、LLC miss、memory bandwidth 和 tokens/s。

.. _llm-runtime-quantization:

模型的量化
------------

默认 ``run.c`` 走 float32，容易读懂，但权重大、内存带宽压力大。量化版本把权重和部分计算转成 int8 等更低精度，
用少量精度损失换更小的模型权重文件和更高吞吐。

量化损失的不是『概率精度』本身，而是更前面的数值精度。大致链路是：

.. code-block:: text

   float weights
       |
       |  quantize
       v
   int8 / int4 weights
       |
       |  matmul with scale / dequantize
       v
   logits 有轻微误差
       |
       |  softmax / sampler
       v
   token 概率分布变化
       |
       v
   可能选到不同 token

如果误差很小，输出看起来基本不变；如果量化太激进，或者某些 layer / head 对精度很敏感，logits 排名会被扰动，
后面的采样就可能走到不同路径。直观表现就是回答质量下降、推理变粗糙，俗称『降智』。

.. csv-table:: Precision Tradeoff
   :header: "形式", "优点", "代价"
   :widths: 18, 42, 40

   "float32", "代码简单，数值路径直观", "模型权重文件大，带宽压力大，CPU 慢"
   "int8 quantization", "模型更小，内存读更少，整数计算可能更快", "代码复杂，需要 scale / dequantize，精度略降"
   "4-bit / lower", "进一步降低带宽和存储", "kernel 更复杂，对质量和硬件支持更敏感"

总结
=======

LLM runtime 的经典示例 llama2.c 作为一个普通进程运行起来后，首先加载一大块只读参数，分配一批工作 buffer，
然后在一个顺序 decode loop 里反复执行数值计算。复杂性主要来自几个方面：

- 参数规模大，导致内存带宽和 cache 行为非常重要。
- 生成是 token-by-token 的，导致 latency 被循环结构放大。
- attention 依赖历史上下文，导致 KV cache 成为 runtime 状态的核心。

理解了这个架构，再去看更复杂的 runtime，例如 ``llama.cpp``、vLLM、TensorRT-LLM、PyTorch / CUDA 后端，
就不会只看到一堆框架名，而能看出它们分别在优化哪一层：模型格式、kernel、memory layout、batching、
KV cache 管理、scheduler 或 serving protocol。

参考
========

- `karpathy/llama2.c <https://github.com/karpathy/llama2.c>`_
- `llama2.c/run.c <https://github.com/karpathy/llama2.c/blob/master/run.c>`_
- `jaymody/picoGPT <https://github.com/jaymody/picoGPT>`_
- `karpathy/nanoGPT <https://github.com/karpathy/nanoGPT>`_
- `Attention Is All You Need <https://arxiv.org/abs/1706.03762>`_
- `Llama 2: Open Foundation and Fine-Tuned Chat Models <https://arxiv.org/abs/2307.09288>`_
- `TinyStories: How Small Can Language Models Be and Still Speak Coherent English? <https://arxiv.org/abs/2305.07759>`_
- `GPT in 60 Lines of NumPy <https://jaykmody.com/blog/gpt-from-scratch/>`_
