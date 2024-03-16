import os
from docutils.nodes import NodeVisitor, Text, TextElement, literal_block

def setup(app):
    app.connect('doctree-resolved', process_chinese_para)

def process_chinese_para(app, doctree, docname):
    doctree.walk(ParaVisitor(doctree))

# 只替换连个中文字符中间的空格
def mix_replace(text: str) -> str:
    new_text = text
    pos = 0
    while True:
        pos = new_text.find(os.linesep, pos)
        if pos < 0:
            break
        if pos - 1 < 0:
            pos = pos + 1
            continue
        if pos + 1 > len(new_text) - 1:
            break
        before = new_text[pos - 1]
        after = new_text[pos + 1]
        if len(before.encode()) > 1 and len(after.encode()) > 1:
            new_text = new_text[:pos] + new_text[(pos + 1):]
        else:
            pos = pos + 1
    return new_text

class ParaVisitor(NodeVisitor):
    def dispatch_visit(self, node):
        if isinstance(node, TextElement) and not isinstance(node, literal_block):
            for i in range(len(node.children)):
                if type(node[i]) == Text:
                    # node[i] = Text(node[i].astext().replace('\r', '').replace('\n', ''))
                    node[i] = Text(mix_replace(node[i].astext()))
