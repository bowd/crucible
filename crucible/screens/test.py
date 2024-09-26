from typing import Optional

from textual import work
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive

from crucible.data.trace_tree import TraceTree
from crucible.data.suite_tree import TestNode, SuiteNode
from crucible.data.shadow_tree import ShadowTree, FilterKey
from crucible.data.node_filters import isCall
from crucible.runner import RunConfig
from crucible.screens.run_forge_test import RunForgeTest

from .tree import Tree


class TestScreen(Screen):
    BINDINGS = [
        ("b", "back", "Back"),
        ("r", "run_test", "Rerun test"),
        ("f", "filters", "Filters")
    ]
    shadow_tree = reactive(None, recompose=True)
    title = reactive(None)
    filters = reactive([], recompose=True)

    def __init__(self, node, **kwargs):
        super().__init__(classes="test-screen", **kwargs)
        self.node = node
        if isinstance(node, TestNode):
            self.suite = node.suite
            self.title = f"{self.suite.contract.split(
                ":")[-1]}::{self.suite.tests[0].test}"
        elif isinstance(node, SuiteNode):
            self.suite = node.suite
            self.title = f"{self.suite.contract.split(":")[-1]}"

    def on_mount(self) -> None:
        self.action_run_test()

    async def action_filters(self) -> None:
        if not self.shadow_tree:
            return
        if len(self.shadow_tree.filters) == 0:
            self.shadow_tree.add_filters({
                FilterKey('vm::label'): isCall("VM", "label"),
                FilterKey('vm::addr'): isCall("VM", "addr"),
                FilterKey('console::log'): isCall("console", "log"),
            })
        else:
            self.shadow_tree.filters = {}
        await self.recompose()
        self.call_after_refresh(self.focus_child, "tree")

    def compose(self):
        yield Header(show_clock=True)
        if self.shadow_tree:
            yield Tree(self.shadow_tree, id="tree")
            # if self.test.logs.strip():
            #     yield Static("Logs:\n" + self.test.logs, id="logs")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    @work
    async def action_run_test(self) -> None:
        run_config = self.get_run_config()
        output = await self.app.push_screen_wait(
            RunForgeTest(run_config, title=self.title or "")
        )
        self.suite = output.suites[0]
        self.shadow_tree = TraceTree(output)
        self.call_after_refresh(self.focus_child, "tree")

    def get_run_config(self) -> RunConfig:
        if isinstance(self.node, TestNode):
            return RunConfig("default",
                             self.suite.contract.split(':')[-1],
                             self.suite.tests[0].test,
                             None,
                             True)
        elif isinstance(self.node, SuiteNode):
            return RunConfig("default",
                             self.suite.contract.split(':')[-1],
                             None,
                             None,
                             True)
        else:
            raise ValueError(f"Unexpected node type: {type(self.node)}")

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
