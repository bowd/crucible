from textual import work
from textual.containers import Container
from textual.screen import ModalScreen
from textual.reactive import reactive
from textual.widgets import LoadingIndicator, Static
from textual.worker import Worker, WorkerState

from crucible.runner.runner import runner, RunConfig


class RunForgeTest(ModalScreen):
    tests: str
    run_config: RunConfig
    output = reactive(None)

    def __init__(
            self,
            run_config: RunConfig,
            title: str = "tests...",
            *args, **kwargs):
        super().__init__(*args, id="run-forge-test", **kwargs)
        self.run_config = run_config
        self.title = title

    def compose(self):
        yield Container(
            Static(f"Running {self.title}", classes="loading-text"),
            LoadingIndicator(classes="loading-indicator"),
            classes="modal-box"
        )

    def on_mount(self):
        self.load()

    @work(thread=True)
    async def load(self):
        return runner.run(self.run_config)

    def on_worker_state_changed(self, evt: Worker.StateChanged) -> None:
        if evt.state == WorkerState.SUCCESS:
            self.dismiss(evt.worker.result)
