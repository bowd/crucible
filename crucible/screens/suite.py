from functools import partial

from textual.screen import Screen
from textual.message import Message
from textual.widgets import LoadingIndicator, Header, Footer, Static
from textual.reactive import reactive
from textual.command import Hit, Hits, Provider

from rapidfuzz import process, fuzz

from crucible.runner import runner, RunConfig
from crucible.data.suite_tree import SuiteTree, TestNode
from crucible.data.shadow_tree import ShadowTree

from .test import TestScreen
from .tree import Tree


class LoadingTestSuite(Static):
    def compose(self):
        yield Static("Running full test suite", classes="loading-text")
        yield LoadingIndicator(classes="loading-indicator")


class TestSelected(Message):
    def __init__(self, node):
        self.node = node
        super().__init__()


class RunTestCommands(Provider):
    def parse_tests(self) -> list:
        if isinstance(self.screen, SuiteScreen):
            return self.parse_test_node(self.screen.shadow_tree.root)
        return []

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

        screen = self.screen
        assert isinstance(screen, SuiteScreen)

        hits = process.extract(query, self.choices,
                               scorer=fuzz.WRatio, limit=10)

        for hit in hits:
            command, score, index = hit
            yield Hit(
                score,
                matcher.highlight(command),
                partial(screen.post_message, TestSelected(
                    self.test_nodes[index])),
            )


class SuiteScreen(Screen):
    COMMANDS = {RunTestCommands}
    BINDINGS = [
        ("r", "run_suite", "Run Suite"),
        ("ENT", "run_test", "Run Test")
    ]
    loading = reactive(False, recompose=True)
    shadow_tree = reactive(ShadowTree(), recompose=True)
    title = reactive("All Tests")

    def on_mount(self) -> None:
        self.call_after_refresh(self.action_run_suite)

    def compose(self):
        yield Header(show_clock=True)
        if self.loading:
            yield LoadingTestSuite(classes="loading-tests")
        elif self.tree:
            yield Tree(self.shadow_tree, id="tree")
        yield Footer()

    def action_run_suite(self) -> None:
        self.loading = True
        self.run_worker(self.update(), thread=True)

    def on_test_selected(self, evt):
        node = evt.node
        if isinstance(node, TestNode):
            self.app.push_screen(TestScreen(node))

    def on_tree_node_selected(self, evt):
        node = self.shadow_tree.get_node(evt.node.data)
        if isinstance(node, TestNode):
            self.app.push_screen(TestScreen(node))

    async def update(self) -> None:
        output = runner.run(RunConfig("default", None, None, None))
        self.shadow_tree = SuiteTree(output)
        self.loading = False
        self.call_after_refresh(self.focus_child, "tree")

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
