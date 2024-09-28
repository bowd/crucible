import re
from typing import TypeGuard, Iterator
from enum import Enum
from textual import log
from rich.text import Text
from .shadow_tree import ShadowNode, ShadowTree


class NodeStatus(Enum):
    FAIL = 0
    PASS = 1
    SKIP = 2


def is_suite_tree_node(node: ShadowNode) -> TypeGuard["SuiteTreeNode"]:
    return isinstance(node, SuiteTreeNode)


def has_status(status: NodeStatus):
    def __has_status__(node: SuiteTreeNode):
        return node.status == status
    return __has_status__


class SuiteTreeNode(ShadowNode):
    def __display__(self):
        if self.status == NodeStatus.PASS:
            return Text(" ", style="green") + Text(self.__title__(), style="default")
        elif self.status == NodeStatus.SKIP:
            return Text("󱔕 ", style="yellow") + Text(self.__title__(), style="light")
        elif self.status == NodeStatus.FAIL:
            return Text("❌ "+self.__title__(), style="red")
        return Text("[InvalidStatus] " + self.__title__())

    def __title__(self):
        return str(self.__id__)

    def __suite_tree_children__(self) -> Iterator["SuiteTreeNode"]:
        return filter(is_suite_tree_node, self.children)

    def __failed_children__(self) -> list["SuiteTreeNode"]:
        return list(filter(
            has_status(NodeStatus.FAIL),
            self.__suite_tree_children__()))

    def __skipped_children__(self) -> list["SuiteTreeNode"]:
        return list(filter(
            has_status(NodeStatus.SKIP),
            self.__suite_tree_children__()))

    @property
    def status(self) -> NodeStatus:
        if len(self.__failed_children__()) > 0:
            return NodeStatus.FAIL
        if len(self.__skipped_children__()) == len(self.children):
            return NodeStatus.SKIP
        return NodeStatus.PASS

    def merge_up(self, child) -> None | ShadowNode:
        pass


class SuitePathNode(SuiteTreeNode):
    def __init__(self, segment):
        super().__init__(id=segment, expanded=True)

    def merge_up(self, child):
        merged_node = None
        if isinstance(child, SuitePathNode):
            merged_node = SuitePathNode(f"{self.__id__}/{child.__id__}")
            merged_node.tree = self.tree
            merged_node.add_children_from_node(child)
        elif isinstance(child, SuiteNode):
            merged_node = SuiteNode(
                f"{self.__id__}/{child.__id__}", child.suite)
            merged_node.tree = self.tree
            merged_node.add_children_from_node(child)
        return merged_node

    def __title__(self):
        if (self.__id__.startswith("root/")):
            return str(self.__id__).replace("root/", "")
        else:
            return str(self.__id__)


class TestPathNode(SuiteTreeNode):
    def __init__(self, segment, suite):
        super().__init__(id=segment, expanded=False)
        self.suite = suite

    def merge_up(self, child):
        merged_node = None
        if isinstance(child, TestPathNode):
            merged_node = TestPathNode(
                f"{self.__id__}/{child.__id__}", self.suite)
        elif isinstance(child, TestNode):
            merged_node = TestNode(
                f"{self.__id__}/{child.__id__}", child.test, child.suite)
        if merged_node:
            merged_node.tree = self.tree
            merged_node.add_children_from_node(child)
        return merged_node


class SuiteNode(SuiteTreeNode):
    def __init__(self, segment, suite):
        super().__init__(id=segment, expanded=False)
        self.suite = suite

    def __title__(self):
        total_tests = self.suite.passed + self.suite.failed + self.suite.skipped
        return f"{self.__id__} [{self.suite.passed}/{total_tests}]"


class TestNode(SuiteTreeNode):
    def __init__(self, label, test, suite):
        super().__init__(label, expanded=False)
        self.test = test
        self.suite = suite

    @property
    def status(self):
        if self.test.result == "PASS":
            return NodeStatus.PASS
        elif self.test.result == "FAIL":
            return NodeStatus.FAIL
        elif self.test.result == "SKIP":
            return NodeStatus.SKIP
        else:
            raise ValueError(f"Unexpected result: {self.test.result}")


class SuiteTree(ShadowTree):
    def __init__(self, output):
        super().__init__()
        self.output = output
        self.set_root(SuitePathNode("root"))
        for suite in self.output.suites:
            suite_node = self.__add_suite__(suite)
            for test in suite.tests:
                self.__add_test__(test, suite, suite_node)
        self.__normalize__(self.root)
        self.__sort_children__(self.root)

    def __sort_children__(self, node):
        node.children.sort(
            key=lambda x: (x.status.value, -1 * len(x.children), x.__id__))
        for child in node.children:
            self.__sort_children__(child)

    def __normalize__(self, node, child_index=0):
        if len(node.children) == 1:
            child = node.children[0]
            merged_node = node.merge_up(child)
            if merged_node:
                if node.parent:
                    node.parent.replace_child(child_index, merged_node)
                else:
                    self.set_root(merged_node)
                self.__normalize__(merged_node, child_index)
            else:
                self.__normalize__(child, 0)
        else:
            for (i, child) in enumerate(node.children.copy()):
                self.__normalize__(child, i)

    def __add_test__(self, test, suite, suite_node):
        path = re.split(r"[:/_]", test.test)
        if path[0] == "test" or path[0] == "testFuzz" or path[0] == "invariant":
            path = path[1:]
        test_label = path.pop()
        current_node = suite_node
        for segment in path:
            found_child = False
            for child in current_node.children:
                if child.__id__ == segment and not isinstance(child, TestNode):
                    current_node = child
                    found_child = True
                    break
            if not found_child:
                current_node = current_node.add_child(
                    TestPathNode(segment, suite))
        current_node.add_child(TestNode(test_label, test, suite))

    def __add_suite__(self, suite):
        path = re.split(r"[:/_]", suite.contract)
        suite_label = path.pop()
        current_node = self.root
        for segment in path:
            found_child = False
            for child in current_node.children:
                if child.__id__ == segment:
                    current_node = child
                    found_child = True
                    break
            if not found_child:
                current_node = current_node.add_child(SuitePathNode(segment))
        return current_node.add_child(SuiteNode(suite_label, suite))
