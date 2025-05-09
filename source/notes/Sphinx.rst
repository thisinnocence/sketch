.. Michael Wu 版权所有

:Authors: Michael Wu
:Version: 1.0

Sphinx文档系统
==========================

Why sphinx
-------------

说一下为什么选择sphinx，一个好的笔记平台能够更好让人养成写作思考的习惯。经过一段时间
在项目中的使用，发现sphinx能够很好的做到这点，让人聚焦内容。还有很多其他优势:

1. 文档能够很方便通过Git项目进行托管，方便持续演进更新。
2. 支持渲染成各种想要的样式进行公开发布，有github、readthedoc等免费的发布平台。
3. 还有高速的检索能力，方便分享和查阅。
4. 广泛被用在各种知名开源项目，如Python, Linux, 各种工具支持完善。
5. 语法多样，表达力强，在聚焦内容的同时，尽可能满足笔记结构化的需求。

入门sphinx
-------------

Google ``sphinx 指南`` 查到了很多文章，下面几个很不错：

- sphinx入门指南:  https://iridescent.ink/HowToMakeDocs/Basic/Sphinx.html
- 语法速查手册: https://docutils.sourceforge.io/docs/user/rst/quickref.html
- 工程搭建指导：  https://yanghongfei.readthedocs.io/zh/latest/index.html
- 各种主题选择： https://sphinx-themes.org/#themes

| PS: 下面的这个主题行宽挺宽，而且左右导航也都有回头试试：
| https://sphinx-themes.org/sample-sites/sphinx-wagtail-theme/kitchen-sink/really-long/

而且还可以查这些工程的源码，在github上看他们的 ``conf.py`` 配置，以及目录结构，插件等，都
十分的方便，可以快速参考来进行自己的rst编写。几个工程源码：

- https://github.com/yanghongfei/ReadtheDocs/tree/master/source
- https://github.com/Kenneth-Lee/MySummary/tree/master
- https://github.com/antsfamily/HowToMakeDocs/tree/master/docs/source

都可以很方便的参考。后续遇到工程上的问题，就持续改这个工程就行了。有git跟踪，这里就不详细赘述工程细节了。

vscode插件技巧
------------------

vscode支持rst主要使用插件 ``reStructuredText``

标题快捷键
^^^^^^^^^^^^^^^^

通常情况下，并没有特定字符分配标题级别，结构是根据标题的连续出现确定的。在Python开发者指南中。这些约定提供了
一种通过特定字符表示不同级别标题的方法。参考Python的RST文档风格指南：

https://devguide.python.org/documentation/markup/#sections

* ``#`` with overline, for parts
* ``*`` with overline, for chapters
* ``=``, for sections
* ``-``, for subsections
* ``^``, for subsubsections
* ``"``, for paragraphs

| 有的会出现上下都有特定字符，但是 **上划线也不是必须** ，主要是有个缩进的作用，提高格式美观。
| 这个插件可以支持 ``ctrl+k ctrl+=`` ，来给选中的字符下面加上=，不过要看 keymap 是否冲突。
| https://docs.restructuredtext.net/articles/section

有用的snippets
^^^^^^^^^^^^^^^^

https://docs.restructuredtext.net/articles/snippets

.. table::
    :align: left

    =================== ==============
    Keyword             Description
    =================== ==============
    ``code``            Code block
    ``image``           Image
    ``link``            Link
    ``attention``       Attention
    ``note``            Note
    ``warning``         Warning
    ``error``           Error
    ``hint``            Hint
    ``important``       Important
    ``caution``         Caution
    ``tip``             Tip
    ``rubric``          Rubric (footnote)
    ``doc``             Doc reference
    ``ref``             Label reference
    ``label``           Label
    ``literalinclude``  Literal include
    =================== ==============

快速编辑表格
^^^^^^^^^^^^^^

下面是vscode插件的功能：

https://tatsuyanakamori.github.io/vscode-reStructuredText/en/sec02_functions/table.html#creating-a-table

- 自动转逗号分隔符格式为表格
- 根据 ``3x4`` 快速转换表格

还有一些很方便的方法详细看上面链接。

快速插入图片
^^^^^^^^^^^^^^^

通过 ``.. image:: imagepath`` 实现插入图像: ::

    .. image:: picture.jpeg
       :height: 100px
       :width: 200 px
       :scale: 50 %
       :alt: 对于不能显示图片的时候, 显示这些文字
       :align: right

| 也可以使用图像指令 ``figure``, 包含图例和标题。
| https://iridescent.ink/HowToMakeDocs/Basic/reST.html#directives

| 为方便插入剪切板图片，可以使用 ``Paste Image`` 插件， 插件配置说明：
| https://github.com/mushanshitiancai/vscode-paste-image

配置快捷键 Keyboard Shortcuts, 我个人喜欢 ``ALT + v``, 然后配置自动生成路径, 然后再
vscode的settings.json中加入下面的配置即可：

.. code-block:: json

    {
        "pasteImage.path": "${currentFileDir}/pic",
        "pasteImage.filePathConfirmInputBoxMode": "onlyName",
        "pasteImage.encodePath": "none",
        "pasteImage.prefix": ".. image:: "
    }

.. tip::
    使用 ``windows + v`` 可以看windows的剪切板里有什么图片


表格编辑
----------

| 大部分情况 CSV 表格真的非常的方便， 参考：
| https://docutils.sourceforge.io/docs/ref/rst/directives.html#tables
| https://docutils.sourceforge.io/docs/ref/rst/directives.html#csv-table-1
| 遇到一个单元格内的内容很长需要换行是，我们把内容放到引号里即可，就如上面链接里的例子一样。

网格table:

https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#tables


交叉引用
-------------------

文档内任意位置引用
^^^^^^^^^^^^^^^^^^^^^^^^

| 参考: https://sphinx-doc-zh.readthedocs.io/en/latest/markup/inline.html#ref-role
| 在文档内部任意交叉引用, 使用标准的 reST Label，必须整个文档内部全局唯一，有两个方式 ：

在标题前面加label，可以使用 ``:ref:`label-name```
::

    .. _my-reference-label:

    Section to cross-reference
    --------------------------

    This is the text of the section.

    It refers to the section itself, see :ref:`my-reference-label`.

这种同样使用与图像标签

::

    .. _my-figure:

    .. figure:: whatever

    Figure caption

脚注参考引用
^^^^^^^^^^^^^^^^^^^^^^^^

脚注:  https://iridescent.ink/HowToMakeDocs/Basic/reST.html#footnotes

包含两步:

- 在文档底部放置脚注主体, 以 ``rubric`` 指令标示: ::

    .. rubric:: Footnotes

    .. [#name] 这里是脚注内容

- 在需要插入脚注的地方插入脚注名 ``[#name]``

其中, 使用 ``[#name]_`` 可以实现自动编号, 当然你也可以使用数字来指示确定的脚注编号 ``[1]_`` .

举例:

::

    我后面插入了一个自编号的脚注 [#f1]_ , 后面又跟了一个手动编号的脚注 [2]_ , 后面还跟着一个自动编号的 [#fn]_ .

    .. rubric:: Footnotes

    .. [#f1] 我是自编号脚注1
    .. [2] 我是手动编号脚注2
    .. [#fn] 我是自编号脚注3

我后面插入了一个自编号的脚注 [#f1]_ , 后面又跟了一个手动编号的脚注 [2]_ , 后面还跟着一个自动编号的 [#fn]_ .

.. rubric:: Footnotes

.. [#f1] 我是自编号脚注1
.. [2] 我是手动编号脚注2
.. [#fn] 我是自编号脚注3

sphinx_rtd_theme Q&A
------------------------------------

1. 左侧导航栏展开层级问题

今天周末差不多陆陆续续整了一整天的sphinx工程。期间，遇到了一个左侧导航栏无法展开超过三级的问题，折腾了好久。定位的过程搜了
很多资料，也看了生成的网页HTML源码，都没有解决。但是网上的其他工程都没有问题，那就可以得出结论一定是自己配置的问题，不是
index.rst 的问题，就是 conf.py 的问题，最后一点点的改配置，然后再去生成，终于结局了问题。导致问题的关键配置是

.. attention::
    | 在 conf.py 文件，下面这一行加了后就会有bug，需要删除！
    | html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

2. 默认块 ``::`` 的样式问题, ::

    pygments_style = 'sphinx'

这样默认块主题就是sphinx默认的样式。

公式的写法
--------------

参考： https://www.osgeo.cn/sphinx-note/rest-math2.html

有很多公式的写法，很好参考。

支持markdown
---------------

可以添加 myst_parser 插件，支持markdown语法。同时vscode配置一下插件，防止 toc 误报：

.. code-block:: js

    {
        "restructuredtext.confPath": "${workspaceFolder}/conf.py", // 确保插件读取 Sphinx 配置
        "restructuredtext.languageServer.enabled": true,           // 启用语言服务器
        "restructuredtext.supportedFileSuffixes": [".rst", ".md"]  // 显式声明支持的扩展名
    }
