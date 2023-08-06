class Node():
    def __init__(self,name):
        self.children = []
        self.attributes = []
        self.name = name
        self.no_value_attributes=["html"]

    def add(self,child):
        self.children.append(child)

    def add_children(self,children):
        if children and type(children) is list and len(children)>0:
            self.children = self.children + children
        elif type(children) is dict:
            self.add(children)

    def set_attribute(self,key,value):
        if key in self.no_value_attributes or value is None:
            self.attributes.append(key)
        else:
            self.attributes.append(f"{key}={value}")

    def get_attributes(self):
        return " ".join(self.attributes)
    
    def get_open_tag(self):
        if len(self.attributes) > 0:
            return f"<{self.name} {self.get_attributes()}>"
        else:
            return f"<{self.name}>"
    
    def get_close_tag(self):
        return f"</{self.name}>"

    def get_child(self,index):
        return self.children[index]

    def has_children(self):
        return len(self.children) > 0
    
    def to_html(self):
        html_children = []
        for i in range(len(self.children)):
            html_children.append(self.get_child(i).to_html())

        return f"{self.get_open_tag()}{''.join(html_children)}{self.get_close_tag()}"            