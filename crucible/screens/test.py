from textual.screen import Screen
from textual.widgets import LoadingIndicator, Header, Footer, Static
from textual.scroll_view import ScrollView
from textual.reactive import reactive

from data.trace_tree import TraceTree
from data.shadow_tree import NodeID
from data.node_filters import isCall

from .tree import Tree
from runner import runner, RunConfig


class LoadingTest(Static):
    def __init__(self, test, **kwargs):
        super().__init__(**kwargs)
        self.test = test

    def compose(self):
        yield Static(f"Running {self.test}", classes="loading-text")
        yield LoadingIndicator(classes="loading-indicator")


class TestScreen(Screen):
    BINDINGS = [
        ("b", "back", "Back"),
        ("r", "run_test", "Rerun test"),
        ("f", "filters", "Filters")
    ]
    loading = reactive(False, recompose=True)
    verbose_test = reactive(None, recompose=True)
    tree: TraceTree = None
    title = reactive(None)
    filters = reactive([], recompose=True)

    def __init__(self, test_node, **kwargs):
        super().__init__(classes="test-screen", **kwargs)
        self.test = test_node.test
        self.suite = test_node.suite
        self.title = f"{self.suite.contract.split(":")[-1]}::{self.test.test}"

    def on_mount(self) -> None:
        self.call_after_refresh(self.action_run_test)

    async def action_filters(self) -> None:
        if len(self.tree.filters) == 0:
            self.tree.add_filters({
                'vm::prank': isCall("VM", "prank"),
                'console::log': isCall("console", "log"),
            })
        else:
            self.tree.filters = {}
        await self.recompose()
        self.call_after_refresh(self.focus_child, "tree")

    def compose(self):
        yield Header(show_clock=True)
        if self.loading:
            yield LoadingTest(self.test.test, classes="loading-tests")
        elif self.tree:
            yield Tree(self.tree, id="tree")
            if self.test.logs.strip():
                yield Static("Logs:\n" + self.test.logs, id="logs")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    def node_selected(self, node_id: NodeID):
        pass

    def action_run_test(self) -> None:
        self.loading = True
        self.run_worker(self.update(), thread=True)

    async def update(self) -> None:
        run_config = RunConfig("default",
                               self.suite.contract.split(':')[-1],
                               self.test.test,
                               None)
        output = runner.run(run_config)
        self.test = output.suites[0].tests[0]
        self.tree = TraceTree(output)
        self.loading = False
        self.call_after_refresh(self.focus_child, "tree")

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
