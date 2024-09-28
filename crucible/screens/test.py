from typing import Any, Optional

from textual import work
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive

from crucible.data.trace_tree import TraceTree
from crucible.data.suite_tree import TestNode, SuiteNode
from crucible.data.shadow_tree import ShadowTree, FilterKey
from crucible.data.node_filters import isCall
from crucible.runner.runner import RunConfig
from crucible.screens.run_forge_test import RunForgeTest

from .tree import Tree
from .compilation_results import CompilationResults


class TestScreen(Screen):
    BINDINGS = [
        ("b", "back", "Back"),
        ("r", "run_test", "Rerun test"),
        ("f", "filters", "Filters")
    ]
    shadow_tree: Optional[ShadowTree] = None
    filters = reactive([], recompose=True)
    logs = None
    output: Any = reactive(None, recompose=True)

    def __init__(self, node, **kwargs):
        super().__init__(classes="test-screen", **kwargs)
        self.node = node
        if isinstance(node, TestNode):
            self.title = f"{node.suite.contract.split(
                ":")[-1]}::{node.test.test}"
        elif isinstance(node, SuiteNode):
            self.title = f"{node.suite.contract.split(":")[-1]}"

    def on_mount(self) -> None:
        self.action_run_test()

    def compose(self):
        yield Header(show_clock=True)
        if self.output and self.output.compilation.failed:
            yield CompilationResults(self.output, id="compilation")
        elif self.shadow_tree:
            yield Tree(self.shadow_tree, id="tree")
            if self.logs and self.logs.strip():
                yield Static("Logs:\n" + self.logs, id="logs")
        yield Footer()

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

    def action_back(self) -> None:
        self.app.pop_screen()

    @work
    async def action_run_test(self) -> None:
        run_config = self.get_run_config()
        output = await self.app.push_screen_wait(
            RunForgeTest(run_config, title=self.title or "")
        )

        self.output = output
        if self.output.compilation.failed:
            self.call_after_refresh(self.focus_child, "compilation")
        else:
            self.shadow_tree = TraceTree(output)
            self.logs = output.suites[0].tests[0].logs
            self.call_after_refresh(self.focus_child, "tree")

    def get_run_config(self) -> RunConfig:
        if isinstance(self.node, TestNode):
            return RunConfig("default",
                             self.node.suite.contract.split(':')[-1],
                             self.node.test.test,
                             None,
                             True)
        elif isinstance(self.node, SuiteNode):
            return RunConfig("default",
                             self.node.suite.contract.split(':')[-1],
                             None,
                             None,
                             True)
        else:
            raise ValueError(f"Unexpected node type: {type(self.node)}")

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
