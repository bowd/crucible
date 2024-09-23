from rich.text import Text


def light(text):
    return Text(text, style="dim light_slate_grey")


def bold(text):
    return Text(text, style="bold")


def default(text):
    return Text(text, style="default")


def keyword(text):
    return Text(text, style="bold yellow")


def event(text):
    return Text(text, style="bold blue")


def ret(text):
    return Text(text, style="bold dark_cyan")


def revert(text):
    return Text(text, style="bold red")
