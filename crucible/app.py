from textual.app import App
from screens.suite import SuiteScreen


class Crucible(App):
    CSS_PATH = "crucible.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    MODES = {
        "app": SuiteScreen
    }

    def on_mount(self) -> None:
        self.switch_mode("app")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    Crucible().run()
