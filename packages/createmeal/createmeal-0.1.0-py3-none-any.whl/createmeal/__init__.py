from .composite.node_factory import NodeFactory

def toHtml(jsonDoc):
    return NodeFactory.to_html(jsonDoc)