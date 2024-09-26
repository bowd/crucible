from textual import work, log
from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.reactive import reactive

from crucible.runner import RunConfig
from crucible.data.suite_tree import TestNode, SuiteTree

from .test import TestScreen
from .tree import Tree
from .run_forge_test import RunForgeTest
from .run_test_commands import RunTestCommands


class SuiteScreen(Screen):
    COMMANDS = {RunTestCommands}
    BINDINGS = [
        ("r", "run_suite", "Run Suite"),
        ("ENT", "run_test", "Run Test")
    ]
    loading = reactive(False, recompose=True)
    shadow_tree = reactive(None, recompose=True)
    title = reactive("All Tests")

    async def on_mount(self) -> None:
        self.action_run_suite()

    def compose(self):
        yield Header(show_clock=True)
        if self.shadow_tree:
            yield Tree(self.shadow_tree, id="tree")
        yield Footer()

    @work
    async def action_run_suite(self) -> None:
        output = await self.app.push_screen_wait(
            RunForgeTest(RunConfig("default", None, None, None, False),
                         "full test suite")
        )
        self.shadow_tree = SuiteTree(output)
        self.call_after_refresh(self.focus_child, "tree")

    def on_test_selected(self, evt):
        node = evt.node
        if isinstance(node, TestNode):
            if node.test.test == "setUp":
                self.app.push_screen(TestScreen(node.parent))
            else:
                self.app.push_screen(TestScreen(node))

    def on_tree_node_selected(self, evt):
        if not self.shadow_tree:
            return
        node = self.shadow_tree.get_node(evt.node.data)
        if isinstance(node, TestNode):
            log(node.test)
            if node.test.test == "setUp":
                self.app.push_screen(TestScreen(node.parent))
            else:
                self.app.push_screen(TestScreen(node))

    def focus_child(self, id) -> None:
        self.set_focus(self.get_child_by_id(id))
