from textual.screen import Screen
from textual.widgets import LoadingIndicator, Header, Footer, Static
from textual.reactive import reactive
from textual.command import Hit, Hits, Provider

from screens.test import TestScreen
from runner import runner, RunConfig
from data.suite_tree import SuiteTree, TestNode
from data.shadow_tree import NodeID
from functools import partial

from .tree import Tree


class LoadingTestSuite(Static):
    def compose(self):
        yield Static("Running full test suite", classes="loading-text")
        yield LoadingIndicator(classes="loading-indicator")


class RunTestCommands(Provider):
    def parse_tests(self) -> list:
        return self.parse_test_node(self.screen.tree.root)

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

    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)

        screen = self.screen
        assert isinstance(screen, SuiteScreen)

        hits = []
        for node in self.test_nodes:
            command = f"run {node.suite.contract} {node.test.test}"
            score = matcher.match(command)
            if score > 0.98:
                hits.append(Hit(
                    score,
                    matcher.highlight(command),
                    partial(screen.select_test, node),
                ))
        hits.sort(reverse=True, key=lambda hit: hit.score)
        for hit in hits[0:10]:
            yield hit


class SuiteScreen(Screen):
    COMMANDS = {RunTestCommands}
    BINDINGS = [
        ("r", "run_suite", "Run Suite"),
        ("ENT", "run_test", "Run Test")
    ]
    loading = reactive(False, recompose=True)
    tree = reactive(None, recompose=True)
    title = reactive("All Tests")

    def on_mount(self) -> None:
        self.call_after_refresh(self.action_run_suite)

    def compose(self):
        yield Header(show_clock=True)
        if self.loading:
            yield LoadingTestSuite(classes="loading-tests")
        elif self.tree:
            yield Tree(self.tree, id="tree")
        yield Footer()

    def action_run_suite(self) -> None:
        self.loading = True
        self.run_worker(self.update(), thread=True)

    def node_selected(self, node_id: NodeID):
        node = self.tree.get_node(node_id)
        if isinstance(node, TestNode):
            self.app.push_screen(TestScreen(node))

    async def update(self) -> None:
        output = runner.run(RunConfig("default", None, None, None))
        self.tree = SuiteTree(output)
        self.loading = False
        self.call_after_refresh(self.focus_child, "tree")

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
