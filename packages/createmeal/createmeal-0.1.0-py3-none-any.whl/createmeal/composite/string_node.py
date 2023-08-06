from .node import Node

class StringNode(Node):
    def get_open_tag(self):
        return self.name
        
    def get_close_tag(self):
        return ""