![Crucible Logo](https://raw.githubusercontent.com/bowd/crucible/refs/heads/main/docs/crucible.webp)

Crucible is a terminal UI application wrapper for [forge test](https://github.com/foundry-rs/foundry) built with [Textual](https://textual.textualize.io/) (💖).
It provides an interactive environment to navigate your test tree and the trace output of running a test with full verbosity.

## Installation

I recommend using [pipx](https://pipx.pypa.io/stable/installation/), which installes applications distributed via pypi into their own virtual environment.

```bash
$ pipx install forge-curcible
```

This will install the `crucible` executable.

## Running 

To run it just navigate to the root of a foundry project and run:

```
$ crucible
```

The app should run the full test suite and output a tree representation:

![Example Test Suite view](https://raw.githubusercontent.com/bowd/crucible/refs/heads/main/docs/suite-view.png)

You can navigate the tree via the arrows or vim-style (recommended 🤓). 
You can also press CTRL+P to bring up the command pallet where you can fuzzy-find tests to run:

![Example Search view](https://raw.githubusercontent.com/bowd/crucible/refs/heads/main/docs/search-view.png)

Once you pick a test you will see the trace view:

![Example Test Trace view](https://raw.githubusercontent.com/bowd/crucible/refs/heads/main/docs/trace-view.png)

## Disclaimer

This is very alpha software so it might not work. It employs a grammer to parse the forge output.
I've tried it on a variety of tests but it could still fail when opening a test. If it happens it will create
a `/tmp/<test-name>.txt` file with the output. Please open an issue and attach the output.

## Upcoming features

- **Trace filtering**: Have a list of customizable filters that can be toggled to hide trace lines from the output. The current filtering feature just filters `console.log`, `VM.label` and `VM.addr`.
- **Trace search**: Jump to trace line by fuzzy searching on the function call or event name.
- **Profile switch**: Switch the foundry profile that you're using to run the tests, should automatically detect existing profiles.
- **Custom labling**: Ability to do in-app labeling of addresses or bytes32 identifiers.
- **External decoding**: Use public resources to decode function calls and events which could come up in fork-tests.







