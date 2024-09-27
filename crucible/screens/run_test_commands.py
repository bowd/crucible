from functools import partial
from typing import cast, TYPE_CHECKING

from textual.command import Hit, Hits, Provider
from textual.message import Message

from rapidfuzz import process, fuzz, utils
from crucible.data.suite_tree import TestNode

if TYPE_CHECKING:
    from .suite import SuiteScreen


class TestSelected(Message):
    def __init__(self, node):
        self.node = node
        super().__init__()


class RunTestCommands(Provider):
    def parse_tests(self) -> list:
        screen: "SuiteScreen" = cast("SuiteScreen", self.screen)
        if screen.shadow_tree is None:
            return []
        return self.parse_test_node(screen.shadow_tree.root)

    def parse_test_node(self, node):
        if isinstance(node, TestNode):
            return [node]
        else:
            return [
                test_node
                for child in node.children
                for test_node in self.parse_test_node(child)
            ]

    async def startup(self) -> None:
        """Called once when the command palette is opened, prior to searching."""
        worker = self.app.run_worker(self.parse_tests, thread=True)
        self.test_nodes = await worker.wait()
        self.choices = [f"run {node.suite.contract} {
            node.test.test}" for node in self.test_nodes]

    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)
        hits = process.extract(query, self.choices,
                               scorer=fuzz.token_set_ratio, limit=20,
                               processor=utils.default_process)

        for hit in hits:
            command, score, index = hit
            yield Hit(
                score,
                matcher.highlight(command),
                partial(self.screen.post_message, TestSelected(
                    self.test_nodes[index])),
            )
