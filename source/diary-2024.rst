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
4. 广泛被用在各种知名开源项目，如Python, Linux, 各种工具支持完善。
5. 语法多样，表达力强，在聚焦内容的同时，尽可能满足笔记结构化的需求。

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

vscode插件技巧
------------------

vscode支持rst主要使用插件 ``reStructuredText``

有用的 snippets
++++++++++++++++

https://docs.restructuredtext.net/articles/snippets

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
++++++++++++++

快速编辑表格的技巧：

https://tatsuyanakamori.github.io/vscode-reStructuredText/en/sec02_functions/table.html#creating-a-table

- 自动转逗号分隔符格式为表格
- 根据 ``3x4`` 快速转换表格
  
还有一些很方便的方法详细看上面链接。

快速插入图片
+++++++++++++++

通过 ``.. image:: imagepath`` 实现插入图像: ::

    .. image:: picture.jpeg
       :height: 100px
       :width: 200 px
       :scale: 50 %
       :alt: 对于不能显示图片的时候, 显示这些文字
       :align: right

也可以使用图像指令 ``figure``, 包含图例和标题。

https://iridescent.ink/HowToMakeDocs/Basic/reST.html#directives

为方便插入剪切板图片，可以使用 ``Paste Image`` 插件， 插件配置说明：

https://github.com/mushanshitiancai/vscode-paste-image

配置快捷键 Keyboard Shortcuts, 我个人喜欢 ``Alt + v``, 然后配置自动生成路径, 然后再
vscode的settings.json中加入下面的配置即可：

.. code-block:: js

    {
        "pasteImage.path": "${currentFileDir}/pic",
        "pasteImage.filePathConfirmInputBoxMode": "onlyName",
        "pasteImage.encodePath": "none",
        "pasteImage.prefix": ".. image:: ",
    }

.. tip:: 
    使用 ``win + v`` 可以看剪切板里有什么图片
