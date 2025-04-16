# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
import sphinx

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'wu-sketch'
copyright = '2024, Michael-Wu'
author = 'Michael-Wu'

sys.path.append(os.path.abspath("./_extensions"))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# https://www.sphinx-doc.org/en/master/usage/markdown.html#configuration
extensions = [
    'chinese_space',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',  # math
    'myst_parser',  # markdown
]

# myst_parser options for markdown
myst_enable_extensions = [
    "dollarmath",    # 支持 $...$ 行内数学公式
    "amsmath",       # 支持 LaTeX 公式环境（如 \begin{align}）
    "colon_fence",   # 支持 ::: 语法定义代码块
    "html_image",    # 支持 HTML 图片标签
    # 其他扩展...
]

# Display todos by setting to True
todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = []

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
#html_theme = 'sphinx_rtd_theme'
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()] # 这行会引起左侧导航树bug，一定要注释掉
# html_theme_options = {
#     'navigation_depth': 5,
# }

html_theme = 'furo'

html_static_path = ['_static']
pygments_style = 'sphinx'

def setup(app):
    app.add_css_file('my_theme.css')