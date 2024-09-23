from textual import log
from textual.widgets import Tree as TreeWidget
from data.shadow_tree import ShadowNode, ShadowTree, NodeID


class Tree(TreeWidget):
    shadow_tree: ShadowTree
    nodes_by_shadow_node_id: dict

    BINDINGS = [
        ("h", "move_left", "left"),
        ("j", "move_down", "down"),
        ("k", "move_up", "up"),
        ("l", "move_right", "right"),
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
        if self.cursor_node.is_last or self.cursor_node.is_root:
            return
        node_index = self.cursor_node.parent.children.index(self.cursor_node)
        self.move_to(self.cursor_node.parent.children[node_index + 1])

    def action_move_up(self):
        if self.cursor_node.is_root:
            return
        node_index = self.cursor_node.parent.children.index(self.cursor_node)
        if node_index:
            self.move_to(self.cursor_node.parent.children[node_index - 1])

    def action_move_right(self):
        if self.cursor_node.children:
            if not self.cursor_node.is_expanded:
                self.cursor_node.expand()
            self.call_after_refresh(
                self.move_to,
                self.cursor_node.children[0])

    def action_move_left(self):
        if not self.cursor_node.is_root:
            self.move_to(self.cursor_node.parent)

    def move_to(self, node):
        self.scroll_to_node(node)
        self.move_cursor(node)

    def on_tree_node_highlighted(self, evt):
        log("Focus: ", evt.node.data)
        self.shadow_tree.set_focused(evt.node.data)

    def on_tree_node_selected(self, evt):
        self.screen.node_selected(evt.node.data)