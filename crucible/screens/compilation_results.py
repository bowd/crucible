from rich.text import Text
from textual import log
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Static


class CompilationResults(ScrollableContainer):
    errors = reactive([], recompose=True)
    warnings = reactive([], recompose=True)

    BINDINGS = [
        ("j", "scroll_down", "Scroll down"),
        ("k", "scroll_up", "Scroll up")
    ]

    def __init__(self, output, **kwargs):
        super().__init__(**kwargs)
        self.errors = output.compilation.errors
        self.warnings = output.compilation.warnings
        log(self.errors)
        log(self.warnings)

    def compose(self):
        log(self.errors)
        log(self.warnings)
        if self.errors:
            for error in self.errors:
                yield Static(Text(f"Error [{error.code}]: {error.message}",
                                  style="red"))
                yield Static(error.hint.strip() + "\n")
        if self.warnings:
            for warning in self.warnings:
                code = warning.code
                if code == '':
                    code = hash(f"{warning.message}") % 1000000
                yield Static(Text(f"Warning [{code}]: {warning.message}",
                                  style="yellow"))
                yield Static(warning.hint.strip() + "\n")
