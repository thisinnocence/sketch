# Configuration file for the Sphinx documentation builder.
import os
import sys

# --- Project Information ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'wu-sketch'
copyright = '2025, Michael-Wu'
author = 'Michael-Wu'

# --- General Configuration ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
language = 'zh_CN'
templates_path = ['_templates']  # 自定义模板目录, 如 footer.html
sys.path.append(os.path.abspath('./_extensions'))  # 自定义扩展目录

extensions = [
    'chinese_space',        # 自定义扩展（放在 _extensions/ 目录）
    'sphinx.ext.todo',      # TODO 功能
    'sphinx_copybutton',    # 代码块复制按钮
    'sphinx.ext.mathjax',   # LaTeX 数学公式支持
    'myst_parser',          # Markdown 解析
    'sphinx_wagtail_theme', # wagtail 主题支持
]

# Markdown Support
# https://www.sphinx-doc.org/en/master/usage/markdown.html#configuration
# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",     # 支持 LaTeX 公式环境（如 \begin{align}）
    "dollarmath",  # 支持行内数学公式（如 $E=mc^2$）
]
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
todo_include_todos = True  # 显示文档中的 TODO 项

# --- HTML output ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# 
html_static_path = ['_static']     # 静态文件目录（CSS/JS/图片）
html_css_files = ['my_theme.css']  # 自定义 CSS 文件（可选）
#
# https://sphinx-wagtail-theme.readthedocs.io/en/latest/customizing.html
html_theme = 'sphinx_wagtail_theme'  # wagtail 主题
html_theme_options = dict(
    project_name = "wu-sketch",
    github_url = "https://github.com/thisinnocence/sketch"
)
#
# https://pygments.org/styles/
# pygments_style = 'sphinx'  # 代码高亮, 可配套 furo 主题
# html_theme = 'furo'        # furo 主题