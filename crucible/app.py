from textual.app import App
from crucible.screens.suite import SuiteScreen


class Crucible(App):
    CSS_PATH = "crucible.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    MODES = {
        "app": SuiteScreen
    }

    def on_mount(self) -> None:
        self.switch_mode("app")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


def crucible():
    Crucible().run()


if __name__ == "__main__":
    crucible()
