from textual import log
from textual.widgets import Tree as TreeWidget

from crucible.data.shadow_tree import ShadowNode, ShadowTree


class Tree(TreeWidget):
    shadow_tree: ShadowTree
    nodes_by_shadow_node_id: dict

    BINDINGS = [
        ("l", "move_expand", "expand"),
        ("h", "move_collpase", "collpase"),
        ("k", "cursor_up", "up"),
        ("j", "cursor_down", "down"),
        # ("c", "copy", "copy"),
        # ("i", "inspect", "inspect"),
    ]

    def __init__(self, shadow_tree: ShadowTree, **kwargs):
        super().__init__(shadow_tree.root.label, shadow_tree.root.id, **kwargs)
        self.shadow_tree = shadow_tree
        self.nodes_by_shadow_node_id = {}

        self.root.expand()
        self.add_node(self.root, shadow_tree.root)
        if self.shadow_tree.focused is not None:
            log("Focused on init: ", self.shadow_tree.focused)
            self.call_after_refresh(
                self.move_to,
                self.nodes_by_shadow_node_id[self.shadow_tree.focused])

    def add_node(self, parent, node: ShadowNode):
        self.nodes_by_shadow_node_id[node.id] = parent
        for child in node.children:
            if (child.hidden):
                continue
            if child.children:
                child_node = parent.add(
                    child.label, child.id, expand=child.expanded)
            else:
                child_node = parent.add_leaf(child.label, child.id)
            self.add_node(child_node, child)

    def action_move_down(self):
        assert self.cursor_node is not None
        if self.cursor_node.is_last or not self.cursor_node.parent:
            return
        node_index = self.cursor_node.parent.children.index(self.cursor_node)
        self.move_to(self.cursor_node.parent.children[node_index + 1])

    def action_move_up(self):
        assert self.cursor_node is not None
        if self.cursor_node.parent is None:
            return
        node_index = self.cursor_node.parent.children.index(self.cursor_node)
        if node_index:
            self.move_to(self.cursor_node.parent.children[node_index - 1])

    def action_move_expand(self):
        assert self.cursor_node is not None
        if self.cursor_node.children:
            if self.cursor_node.is_expanded:
                self.move_to(self.cursor_node.children[0])
            else:
                self.cursor_node.expand()
                # self.call_after_refresh(
                #     self.move_to,
                #     self.cursor_node.children[0])

    def action_move_collpase(self):
        assert self.cursor_node is not None
        if self.cursor_node.is_expanded:
            self.cursor_node.collapse()

    def action_inspect(self):
        if self.cursor_node:
            node = self.shadow_tree.get_node(self.cursor_node.data)
            log(node.test)
            log(node.suite)

        assert self.cursor_node is not None
        if self.cursor_node.is_expanded:
            self.cursor_node.collapse()

    def move_to(self, node):
        self.scroll_to_node(node)
        self.move_cursor(node)

    def on_tree_node_expanded(self, evt):
        node = self.shadow_tree.get_node(evt.node.data)
        if node:
            node.toggle_expanded(True)

    def on_tree_node_collapsed(self, evt):
        node = self.shadow_tree.get_node(evt.node.data)
        if node:
            node.toggle_expanded(False)

    def on_tree_node_highlighted(self, evt):
        log("Focus: ", evt.node.data)
        self.shadow_tree.set_focused(evt.node.data)
