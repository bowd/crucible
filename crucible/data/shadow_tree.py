from typing import NewType, Callable, Optional
from rich.text import Text

NodeID = NewType("NodeID", str)
FilterKey = NewType("FilterKey", str)
Filter = Callable[["ShadowNode"], bool]


class ShadowTree():
    nodes: dict[NodeID, "ShadowNode"] = {}
    root: "ShadowNode"
    filters: dict[FilterKey, Filter] = {}
    __focused__: NodeID

    def __init__(self):
        self.filters = {}
        self.root = ShadowNode(NodeID("root"))
        self.__focused__ = self.root.id
        self.add_node(self.root)

    def set_root(self, root: "ShadowNode"):
        if (self.root):
            self.remove_node(self.root)
        self.root = root
        self.root.tree = self
        self.__focused__ = self.root.id
        self.add_node(root)

    def remove_node(self, node: "ShadowNode"):
        if (self.nodes.get(node.id)):
            self.nodes.pop(node.id)
        for child in node.children:
            self.remove_node(child)

    def add_node(self, node: "ShadowNode"):
        self.nodes[node.id] = node
        for child in node.children:
            self.add_node(child)

    def set_focused(self, id: NodeID):
        self.__focused__ = id

    @property
    def focused(self):
        focused = self.nodes[self.__focused__]
        if focused is None:
            raise ValueError("Focused node not found")
        while focused.hidden and focused.parent:
            focused = focused.parent
        return focused.id

    def get_node(self, id: NodeID):
        return self.nodes.get(id)

    def add_filter(self, key: FilterKey, filter: Filter):
        self.filters[key] = filter

    def remove_filter(self, key):
        self.filters.pop(key)

    def add_filters(self, filters: dict[FilterKey, Filter]):
        self.filters.update(filters)


class ShadowNode():
    __id__: NodeID
    expanded: bool
    children: list["ShadowNode"]

    tree: Optional[ShadowTree] = None
    parent: Optional["ShadowNode"] = None

    def __init__(self, id: NodeID, expanded: bool = False):
        self.__id__ = id
        self.expanded = expanded
        self.children = []

    @property
    def id(self):
        if self.parent:
            return self.parent.id + "::" + self.__id__
        else:
            return self.__id__

    @property
    def hidden(self):
        if self.tree:
            for filter in self.tree.filters.values():
                if filter(self):
                    return True
        return False

    def toggle_expanded(self, expanded):
        self.expanded = expanded

    def add_children_from_node(self, node: "ShadowNode"):
        for child in node.children:
            if self.tree:
                self.tree.remove_node(child)
            self.add_child(child)
        node.children = []

    def add_child(self, child: "ShadowNode"):
        self.children.append(child)
        child.parent = self
        if (self.tree):
            child.tree = self.tree
            self.tree.add_node(child)
        return child

    def replace_child(self, index, child: "ShadowNode"):
        old_child = self.children[index]
        self.children[index] = child
        child.parent = self
        child.tree = self.tree
        if self.tree:
            self.tree.remove_node(old_child)
            self.tree.add_node(child)

    @property
    def label(self):
        return self.__display__()

    def __display__(self) -> str | Text:
        return "__display__ not implemented for:  " + str(self)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
