.. Michael Wu 版权所有 2024~2027

:Authors: Michael Wu
:Version: 1.0

diary-2024
************************

240203 开始使用sphinx
==========================

Why sphinx
-------------

说一下为什么选择sphinx，一个好的笔记平台能够更好让人养成写作思考的习惯。经过一段时间
在项目中的使用，发现sphinx能够很好的做到这点，让人聚焦内容。还有很多其他优势: 

1. 文档能够很方便通过Git项目进行托管，方便持续演进更新。
2. 支持渲染成各种想要的样式进行公开发布，有github、readthedoc等免费的发布平台。
3. 还有高速的检索能力，方便分享和查阅。
4. 广泛备用在各种知名开源项目，如Python, Linux, 各种工具支持完善。

入门sphinx
-------------

Google ``sphinx 指南`` 查到了很多文章，下面几个很不错：

- sphinx入门指南:  https://iridescent.ink/HowToMakeDocs/Basic/Sphinx.html
- 语法速查手册: https://docutils.sourceforge.io/docs/user/rst/quickref.html
- 工程搭建指导：  https://yanghongfei.readthedocs.io/zh/latest/index.html

而且还可以查这些工程的源码，在github上看他们的 ``conf.py`` 配置，以及目录结构，插件等，都
十分的方便，可以快速参考来进行自己的rst编写。几个工程源码：

- https://github.com/yanghongfei/ReadtheDocs/tree/master/source
- https://github.com/Kenneth-Lee/MySummary/tree/master
- https://github.com/antsfamily/HowToMakeDocs/tree/master/docs/source

都可以很方便的参考。后续遇到工程上的问题，就持续改这个工程就行了。有git跟踪，这里就不详细赘述工程细节了。
