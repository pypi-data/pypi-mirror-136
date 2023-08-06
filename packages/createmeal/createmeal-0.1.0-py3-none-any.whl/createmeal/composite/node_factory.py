import os
import json

from .node import Node
from .string_node import StringNode
from .self_closing_tag_node import SelfClosingTagNode

dirname = os.path.dirname(__file__)
attrs_path = os.path.join(dirname,"attributes.json")
self_closing_tags_path = os.path.join(dirname,"attributes.json")
           
FIELD_ATTRIBUTES = "attributes"

with open(attrs_path, 'r') as f:
    attrs = json.load(f)
           
with open(self_closing_tags_path, 'r') as f:
    self_closing_tags = json.load(f)    

class NodeFactory():
    @staticmethod
    def get_node(value):
        if type(value) is str:
            return StringNode(value)

        if type(value) is list:
            nodes = []
            for child in value:
                node = NodeFactory.get_node(child)
                if type(node) is list:
                    nodes = nodes + node
                else:
                    nodes.append(node)
            return nodes

        if type(value) is dict:
            nodes = []
            for key in value:
                entryValue = value[key]
                if (NodeFactory.is_attr(key,entryValue)) or (key==FIELD_ATTRIBUTES):
                    continue

                if NodeFactory.is_self_closing_tag(key):
                    node = SelfClosingTagNode(key)
                else:
                    node = Node(key)
                    children = NodeFactory.get_node(entryValue)
                    node.add_children(children)
                attrs = NodeFactory.get_attrs(entryValue)
                if len(attrs):
                    for attr in attrs:
                        node.set_attribute(attr.key,attr.value)
                nodes.append(node)

            return nodes

        return None

    @staticmethod
    def is_self_closing_tag(name):
        if type(name) is not str:
            return False

        return  name.split(" ")[0] in self_closing_tags

    @staticmethod
    def get_object_node(name):
        return Node(name)

    @staticmethod
    def get_attrs(value,skipAttrValidation=False):
        if value == None:
            return None
        
        attrs = []

        if type(value) is list:
            for item in value:
                if item == FIELD_ATTRIBUTES:
                    return NodeFactory.process_attribute_array(item)
                newAttrs = NodeFactory.get_attrs(item)
                if type(newAttrs) is list:
                    attrs = attrs + newAttrs
                else:
                    attrs.append(newAttrs)
        elif type(value) is object:
            for key in value:
                if key == FIELD_ATTRIBUTES:
                    return NodeFactory.process_attribute_array(key)
                if skipAttrValidation or NodeFactory.is_attr(key,value[key]):
                    attrs.append({"key": key,"value": value[key]})
            return attrs

        return attrs

    @staticmethod
    def process_attribute_array(value):
        attrs = []
        for attr in value:
            attrs = attrs + NodeFactory.get_attrs(attr,True)
        return attrs

    @staticmethod
    def is_attr(name,value=""):
        if type(name) is str:
            return (name in attrs) and (type(value) is str)
        if type(name) is dict:
            for key in name:
                if (key in attrs) and type(name[key]) is str:
                    return True
    
    @staticmethod
    def to_html(jsonDoc):
        nodes = []
        if type(jsonDoc) is list:
            for child in jsonDoc:
                node = NodeFactory.get_node(child)
                if type(node) is list:
                    nodes = nodes + node
                else:
                    nodes.append(node)
        if type(jsonDoc) is dict:
            newNode = NodeFactory.get_node(jsonDoc)
            if type(newNode) is list:
                nodes = nodes + newNode
            else:
                nodes.append(newNode)
        
        if len(nodes)>0:
            return "".join([node.to_html() for node in nodes])
        