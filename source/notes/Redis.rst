.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

Redis
*****

Intro
=====

基础概念
-----------------

https://github.com/redis/redis

对于构建 real-time data-driven applications 的开发者来说，Redis 是一个常用且性能很强的
cache、data structure server、document 和 vector query engine。

Redis 是一个 key-value 内存数据库，key 是 binary-safe string，value 可以是 string、list、set、hash、
zset、stream 等多种数据结构。

从使用者视角看：

.. code-block:: bash

    key                             # 二进制安全字符串，通常按 UTF-8 文本来命名
    value                           # Redis object，不只是简单 byte array

    SET k "hello"                   # string value，可以存文本
    SET img "\xff\xd8..."           # string value，也可以存二进制
    LPUSH q a b c                   # list value
    HSET user:1 name michael        # hash value

``string`` 类型的 value 本身是 binary-safe 的，可以保存任意 bytes，不要求是 UTF-8，也不要求以 ``\0`` 结尾。
但 list、set、hash、zset、stream 不是一整块原始二进制，而是 Redis 自己管理的结构化对象。

从源码视角看，value 外面统一包了一层 ``robj``：

.. code-block:: c

    struct redisObject {
        unsigned type:4;            // 逻辑类型：string / list / set / hash / zset / stream
        unsigned encoding:4;        // 内部编码：int / embstr / raw / listpack / quicklist / skiplist
        void *ptr;                  // 指向真实底层数据
    };

所以 Redis 的核心模型更准确地说是：

.. code-block:: bash

    key -> robj(type, encoding, ptr)

    string -> int / embstr / raw              # 小整数、小字符串、大字符串不同编码
    list   -> listpack / quicklist            # 紧凑数组 + 链式结构
    hash   -> listpack / hashtable            # 小 hash 紧凑存，大 hash 转 dict
    set    -> intset / hashtable              # 纯整数小集合用 intset
    zset   -> listpack / skiplist + dict      # 排序和查找兼顾
    stream -> rax + listpack                  # radix tree 索引 stream entry

也就是说，网络协议上传输的是 bytes，``string`` value 可以是纯二进制；但 Redis 在内存里会根据 value
的逻辑类型和大小选择不同 encoding，而不是所有 value 都按一块裸二进制保存。

多种语言SDK
-----------------

Redis 有很多语言的 client library / SDK。它们通常不是 Redis server 的一部分，而是在应用进程里
连接 ``redis-server``，把本地 API 调用转换成 Redis 命令。

.. code-block:: bash

    app code
        -> redis client library              # Python / Node.js / Java / Go ...
        -> RESP protocol                     # Redis Serialization Protocol
        -> redis-server                      # 真正执行命令、读写内存数据结构

常见选择：

.. code-block:: bash

    Python      -> redis-py                  # pip install redis
    Node.js     -> ioredis / node-redis      # npm package
    Java        -> Jedis / Lettuce / Redisson
    Go          -> go-redis
    Rust        -> redis-rs
    C           -> hiredis
    C#          -> StackExchange.Redis
    PHP         -> phpredis / predis
    Ruby        -> redis-rb

使用时大体都是同一个模型：

.. code-block:: python

    import redis

    r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

    r.set("name", "michael")                # 对应 Redis 命令：SET name michael
    print(r.get("name"))                    # 对应 Redis 命令：GET name
    r.incr("counter")                       # 对应 Redis 命令：INCR counter

所以学习 Redis 时，先理解 Redis 命令和数据结构，再看具体语言 SDK，会更容易建立统一模型。

使用场景
----------

Redis 在很多场景中都很适合使用，例如：

- Caching：支持多种 eviction policies、key expiration 和 hash-field expiration。
- Distributed Session Store：支持灵活的 session 数据建模，例如 string、JSON、hash。
- Data Structure Server：提供 strings、lists、sets、hashes、sorted sets、JSON 等底层数据结构，
  并在这些结构之上支持 counters、queues、leaderboards、rate limiters 等高层语义，同时支持
  transactions 和 scripting。
- NoSQL Data Store：支持 key-value、document 和 time series 数据存储。
- Search and Query Engine：可以为 hash/JSON documents 建索引，并通过 Redis Search 支持
  vector search、full-text search、geospatial queries、ranking 和 aggregations。
- Event Store & Message Broker：可以用 lists 实现 queues，用 sorted sets 实现 priority queues，
  用 sets 做 event deduplication，也支持 streams 和 pub/sub。
- Vector Store for GenAI：可以和 AI applications 集成，例如 LangGraph、mem0，用于 short-term memory、
  long-term memory、LLM response caching、semantic caching 和 retrieval augmented generation (RAG)。
- Real-Time Analytics：可用于 personalization、recommendations、fraud detection 和 risk assessment。

一个简单的场景如下：有个 web app，单机部署，是 node.js fastify + sqlite 服务，然后会有 PV/UV 等统计。
如果每次都去读写 sqlite，性能可能不够好。这时可以进行缓存优化：

- 不用 redis 时，直接在 node.js 里维护一个内存对象，定时把数据 dump 到 sqlite，进程优雅退出时 flush 一下。
  直接每次读写 sqlite 的话，可能会有明显的性能问题，尤其是高并发时。
- 使用 Redis 时，把 PV/UV 这种高频计数先写到 Redis，定时或异步聚合后再落到 sqlite。
  例如 PV 可以用 ``INCR``，UV 可以按天用 ``PFADD``/``PFCOUNT`` 做近似统计，或者用 ``SET`` 做精确去重。

那么适不适合可以按照下面几个维度来考虑：

- Redis 的价值在于把高频、小粒度、可聚合的写请求从 sqlite 前面挡住，让 sqlite 只处理低频的批量写入。
  这样可以减少 sqlite 的写锁竞争、磁盘 IO 和事务开销。
- 但单机服务不一定一开始就需要 Redis。进程内内存对象方案最简单，少一个外部依赖，适合数据允许短时间丢失、
  只有一个 node.js 进程、统计逻辑也比较简单的场景。
- 当出现多进程部署、多个实例共享统计数据、需要独立重启 web app、希望统计数据有更好的恢复能力时，
  Redis 就比进程内对象更合适。

本质上，Redis 在这里不是替代 sqlite，而是作为 sqlite 前面的 write buffer / aggregation layer：
请求路径里先做快速内存更新，后台再把聚合结果持久化。

使用步骤
------------

本地启动：

.. code-block:: bash

    cd ~/github/redis                 # Redis 源码目录
    make -j$(nproc)                   # 编译

    ./src/redis-server redis.conf     # 启动 server，默认 127.0.0.1:6379
    ./src/redis-cli ping              # PONG

命令行试一下：

.. code-block:: bash

    ./src/redis-cli

    SET name michael                  # 写
    GET name                          # 读
    INCR counter                      # 计数
    EXPIRE counter 60                 # 60 秒过期
    TTL counter                       # 看剩余时间

Python demo：

.. code-block:: python

    import redis

    r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

    r.set("name", "michael")          # string
    print(r.get("name"))

    r.incr("counter")                 # counter
    print(r.get("counter"))

    r.expire("counter", 60)           # TTL
    print(r.ttl("counter"))

思路：

.. code-block:: bash

    app -> Redis                      # 高频读写先进内存
    Redis -> DB / file                # 后台定时持久化或聚合


代码导读
==========

代码目录 layout
----------------

核心代码基本在 ``src/``：

.. code-block:: bash

    src/
    ├── server.c / server.h                      # 进程启动、全局 server 状态、命令分发、核心结构定义
    ├── ae.c                                     # 事件循环抽象
    ├── ae_epoll.c / ae_kqueue.c / ae_select.c   # 不同 OS 的事件后端，Linux 下主要走 epoll
    ├── networking.c                             # client 连接、RESP 解析、请求 buffer、响应 buffer
    ├── commands.c / commands.def                # 命令表，把命令名映射到对应的 xxxCommand 函数
    ├── db.c                                     # keyspace 读写、过期、删除、rename、scan 等通用逻辑
    ├── object.c / object.h                      # robj 对象创建、编码、引用计数、释放
    ├── t_string.c / t_hash.c / t_list.c         # string、hash、list 命令实现
    ├── t_set.c / t_zset.c / t_stream.c          # set、zset、stream 命令实现
    ├── dict.c / sds.c / quicklist.c             # dict、SDS、quicklist 等基础数据结构
    ├── listpack.c / intset.c / rax.c            # listpack、intset、radix tree 等紧凑结构
    └── rdb.c / aof.c / replication.c / cluster.c / module.c  # 持久化、复制、集群和 module 机制

从请求到命令执行
------------------

可以先把主路径看成下面这条链：

.. code-block:: bash

    client request
        -> networking.c                  # 读 socket，解析 RESP，请求参数放到 client.argv
        -> server.c:processCommand()     # 查命令表，检查权限、参数、server 状态
        -> server.c:call()               # 调用 redisCommand.proc
        -> t_string.c:setCommand()       # 具体命令实现，例如 SET
        -> db.c:setKey()                 # 更新 keyspace
        -> networking.c                  # 回复写入 client 输出 buffer，等 socket 可写时发送

Redis 启动入口在 ``src/server.c`` 的 ``main()``，初始化配置、数据库、网络监听和事件循环后进入：

.. code-block:: c

    aeMain(server.el);                    // 进入主事件循环，server.el 是 aeEventLoop

.. code-block:: c

    while (!eventLoop->stop) {
        aeProcessEvents(eventLoop, AE_ALL_EVENTS |
                                   AE_CALL_BEFORE_SLEEP |
                                   AE_CALL_AFTER_SLEEP);  // 处理 fd 事件、timer、before/after sleep hook
    }

核心结构
----------

``client`` 表示一个连接，定义在 ``server.h``：

.. code-block:: c

    typedef struct client {
        connection *conn;                 // 底层连接抽象，TCP / TLS / Unix socket
        sds querybuf;                     // 客户端请求 buffer
        int argc;                         // 当前命令参数个数
        robj **argv;                      // RESP 解析后的参数数组
        redisDb *db;                      // 当前 SELECT 的 DB
        struct redisCommand *cmd;         // 当前命令
        struct redisCommand *lastcmd;     // 上一个命令，便于命令查找复用
        struct redisCommand *realcmd;     // 原始命令，用于统计和错误归因
        list *reply;                      // 待发送响应
    } client;

``redisCommand`` 是命令描述符，命令表最终会落到这个结构：

.. code-block:: c

    struct redisCommand {
        const char *declared_name;        // 命令名，例如 "set"
        redisCommandProc *proc;           // 真正执行命令的函数指针，例如 setCommand
        int arity;                        // 参数个数约束，负数表示至少 N 个参数
        uint64_t flags;                   // 命令属性，例如 read-only / write / admin
        uint64_t acl_categories;          // ACL 分类
        long long microseconds, calls;    // 运行时统计
    };

``redisDb`` 是数据库实例。当前源码里 keyspace 用 ``kvstore`` 表示：

.. code-block:: c

    typedef struct redisDb {
        kvstore *keys;                    // 真正的 key -> value 存储
        kvstore *expires;                 // key 的过期时间
        dict *blocking_keys;              // BLPOP / XREAD 等阻塞命令等待的 key
        dict *ready_keys;                 // 已经 ready、需要唤醒 client 的 key
        dict *watched_keys;               // WATCH / MULTI / EXEC 的 CAS 状态
        int id;                           // DB 编号
    } redisDb;

``robj`` 是 Redis 值对象的统一外壳，定义在 ``object.h``：

.. code-block:: c

    struct redisObject {
        unsigned type:4;                  // 用户可见类型：string / list / hash / set / zset / stream
        unsigned encoding:4;              // 内部编码：int / embstr / raw / listpack / quicklist / skiplist
        unsigned refcount : OBJ_REFCOUNT_BITS;  // 引用计数
        unsigned iskvobj : 1;             // 是否作为 kvobj 使用
        unsigned metabits :8;             // key metadata / expiry 相关 bit
        unsigned lru:LRU_BITS;            // LRU 时间或 LFU 信息
        void *ptr;                        // 指向真实底层结构
    };

数据结构映射
--------------

``type`` 是用户看到的数据类型，``encoding`` 是内部实现。同一个 Redis 类型会根据数据规模选择不同编码：

.. code-block:: bash

    string   -> SDS / int / embstr              # 小整数、小字符串、大字符串会走不同编码
    list     -> quicklist / listpack            # 面向两端 push/pop，减少小对象开销
    hash     -> listpack / hashtable            # 小 hash 紧凑存储，大 hash 转 dict
    set      -> intset / hashtable              # 纯整数小集合用 intset，否则用 dict
    zset     -> listpack / skiplist + dict      # 小 zset 紧凑存储，大 zset 兼顾排序和查找
    stream   -> radix tree (rax) + listpack     # rax 做 ID 索引，listpack 存 entry
    keyspace -> kvstore / dict                  # DB 里的 key -> value 主索引

建议先从 ``GET`` / ``SET`` 读起：

.. code-block:: bash

    t_string.c:getCommand() / setCommand()      # 命令入口
        -> object.c / object.h                  # 值对象 robj，编码和引用计数
        -> db.c:lookupKeyRead()                 # GET 读 keyspace
        -> db.c:setKey()                        # SET 写 keyspace
        -> networking.c:addReply*()             # 生成响应，等待事件循环写回 client

从 OS 视角看
================

Redis 经常被描述为『内存数据库』，但从 OS 视角看，它更像是一个对 Linux 内核能力使用得非常克制的
高性能网络服务：主要工作线程用事件循环处理网络 IO 和命令执行，数据放在用户态内存中，持久化、
复制、后台删除等工作则尽量拆到子进程或后台线程里，避免阻塞主事件循环。

进程与线程模型
----------------

Redis 的核心路径是单线程事件循环：

- 一个主线程负责 ``accept/read/write``、解析 RESP 协议、执行命令、返回结果。
- 命令执行通常在主线程串行完成，所以单个 Redis 实例天然避免了复杂的锁竞争。
- 后台线程用于处理部分慢操作，例如异步关闭连接、惰性释放大对象、部分 IO 辅助工作等。
- ``BGSAVE`` 和 ``BGREWRITEAOF`` 使用 ``fork()`` 派生子进程完成，父进程继续服务请求。

这个设计的关键点不是『完全单线程』，而是 **用户请求的关键路径尽量单线程化** 。这样 CPU cache 局部性
更好，锁开销更少，性能更可预测。

事件驱动 IO
------------

Redis 在 Linux 上通常基于 ``epoll`` 做 IO 多路复用。主线程维护一个事件循环：

1. 等待 socket 可读/可写事件。
2. 读取客户端请求并解析命令。
3. 在内存数据结构上执行命令。
4. 把响应写回 socket，写不完的部分挂到输出缓冲区，等下次可写事件继续发送。

这意味着 Redis 的吞吐瓶颈通常来自几个地方：

- 单核 CPU 执行命令的能力。
- 网络包处理和内核协议栈开销。
- 大 key、大 value 导致的内存拷贝和输出缓冲区膨胀。
- 慢命令阻塞事件循环，让后续客户端排队等待。

可以用下面命令观察 Redis 进程的系统调用行为：

.. code-block:: bash

    strace -f -p $(pidof redis-server)

生产环境不要长时间挂 ``strace``，它会明显影响性能。排障时更常用的是 ``perf``、``ss``、
``INFO``、``SLOWLOG`` 等低侵入工具。

内存视角
----------

Redis 把数据主要放在进程虚拟地址空间里，由 Linux 负责页表、物理页分配、回收和换页。从 OS 角度，
Redis 性能高度依赖内存行为：

- 热数据命中内存，命令执行路径短。
- 如果发生 swap，访问延迟会从纳秒/微秒级恶化到毫秒级，Redis 会出现明显抖动。
- 大量小对象会带来 allocator 元数据开销和内存碎片。
- ``fork()`` 后父子进程共享物理页，依赖 copy-on-write 机制。

Redis 常见内存指标：

.. code-block:: text

    used_memory
    used_memory_rss
    mem_fragmentation_ratio
    used_memory_peak

简单理解：

- ``used_memory`` 是 Redis allocator 视角看到的已用内存。
- ``used_memory_rss`` 是 OS 视角看到的常驻物理内存。
- ``mem_fragmentation_ratio`` 明显偏高时，可能是内存碎片，也可能是刚释放完大量 key 后 RSS 还没归还 OS。

``fork()`` 与写时复制
----------------------

Redis 后台持久化常用 ``fork()``：

- 父进程继续处理请求。
- 子进程拿到 fork 时刻的数据快照。
- 子进程把快照写到 RDB 或重写 AOF。

Linux 使用 copy-on-write，所以 ``fork()`` 本身不会立刻复制全部内存页。但如果后台保存期间父进程继续
写数据，被修改的内存页就需要复制一份。这会带来两个影响：

- 内存瞬时占用可能上升，极端情况下触发 OOM。
- 页复制会增加 CPU 和内存带宽压力，导致延迟抖动。

所以大实例做 ``BGSAVE`` 或 AOF rewrite 时，要预留足够内存，不要只按 ``used_memory`` 估算。
可以关注：

.. code-block:: bash

    redis-cli INFO persistence
    redis-cli INFO memory

持久化与文件系统
------------------

Redis 持久化主要有 RDB 和 AOF 两种：

- RDB 是某个时间点的内存快照，适合全量备份和快速加载。
- AOF 记录写命令，数据恢复粒度更细，但文件会不断增长，需要 rewrite。

从 OS 视角看，持久化性能受这些因素影响：

- 页缓存：Redis 写文件通常先进入 Linux page cache，再由内核回写到磁盘。
- ``fsync`` 策略：决定数据落盘频率，也决定延迟和可靠性的权衡。
- 磁盘 IO：慢盘或 IO 拥塞会拖慢 AOF 刷盘和 RDB 保存。
- 文件系统：ext4/xfs 等文件系统的日志和分配策略会影响尾延迟。

AOF 的 ``appendfsync`` 常见策略：

.. code-block:: text

    always
    everysec
    no

一般线上常见配置是 ``everysec``：最多损失约 1 秒数据，换取更好的吞吐和延迟表现。``always`` 更强一致，
但每次写命令都可能等待刷盘，延迟代价很高。

网络栈与连接
--------------

Redis 是典型的 TCP 服务。客户端连接多、请求小、响应快时，OS 网络栈的细节会直接影响表现：

- ``backlog`` 太小会导致高峰期连接排队不足。
- 文件描述符上限太低会限制最大连接数。
- 输出缓冲区过大可能挤占内存，尤其是慢客户端或 pub/sub 场景。
- loopback、本机 Unix socket、跨机 TCP 的延迟差异很明显。

常用观察命令：

.. code-block:: bash

    ss -lntp | grep redis
    ss -antp | grep redis-server
    lsof -p $(pidof redis-server) | wc -l

调度与 CPU
-----------

Redis 主线程通常只能吃满一个 CPU core。即使命令非常快，只要单核到达瓶颈，继续加客户端也只会增加排队。

几个实践点：

- 单实例适合低延迟和简单运维，但吞吐上限受单核限制。
- 多实例或 Redis Cluster 可以把 key 分片到多个进程，利用多核。
- 避免把 Redis 和 CPU 密集型服务混部在同一组核心上。
- 容器环境要注意 CPU quota，Redis 看到的 CPU 数量和实际可用时间片可能不一致。

如果怀疑 CPU 成为瓶颈，可以看：

.. code-block:: bash

    top -H -p $(pidof redis-server)
    perf top -p $(pidof redis-server)
    redis-cli --latency

虚拟内存配置
--------------

Redis 常见 Linux 配置项：

.. code-block:: bash

    sysctl vm.overcommit_memory
    sysctl vm.swappiness
    cat /sys/kernel/mm/transparent_hugepage/enabled

常见建议：

- ``vm.overcommit_memory = 1``：避免 ``fork()`` 时因为内核保守估算内存而失败。
- 尽量关闭或降低 swap 影响：Redis 被换出后延迟会非常差。
- 关闭 Transparent Huge Pages：THP 可能造成内存分配和 copy-on-write 延迟抖动。

这些配置不是 Redis 『业务逻辑』的一部分，但会直接影响 ``fork()``、内存分配、延迟稳定性。

慢请求与阻塞
--------------

因为核心命令路径串行执行，一个慢命令会阻塞后面的所有客户端请求。常见风险：

- ``KEYS *`` 扫描全量 key 空间。
- 对大 list/set/zset/hash 做一次性大范围读取或删除。
- Lua 脚本运行时间过长。
- 删除大 key 触发大量内存释放。
- AOF 刷盘或后台 rewrite 造成 IO 压力。

排查入口：

.. code-block:: bash

    redis-cli SLOWLOG GET 20
    redis-cli LATENCY DOCTOR
    redis-cli INFO commandstats

大 key 删除可以优先考虑 ``UNLINK``，它把真正的内存释放放到后台线程，减少主线程阻塞。

把 Redis 当成 OS 进程来调优
---------------------------

可以按下面路径建立排障思路：

1. 延迟高：先看 ``SLOWLOG``、``LATENCY DOCTOR``，确认是不是慢命令。
2. CPU 高：看单核是否打满，再看命令统计和热点 key。
3. 内存高：看 ``INFO memory``，区分数据量、碎片、输出缓冲区和 copy-on-write。
4. IO 高：看 AOF/RDB 状态、磁盘延迟、``appendfsync`` 策略。
5. 连接异常：看 ``connected_clients``、fd 限制、``ss`` 队列和客户端输出缓冲区。

从这个角度看，Redis 的高性能来自三个约束：

- 数据尽量在内存中完成。
- 请求关键路径尽量少用锁、少切线程。
- 慢 IO 和重任务尽量挪到后台，但仍要接受 OS 资源竞争的影响
