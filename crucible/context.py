import tomllib
import os
# This file contains the Context class which is used to
# parse and store the context of the current execution.

# DIR = os.path.abspath("../mento/mento-core")
DIR = os.getcwd()
FOUNDRY_TOML = os.path.join(DIR, "foundry.toml")


class Context():
    def __init__(self):
        if (not os.path.exists(FOUNDRY_TOML)):
            return
        with open(FOUNDRY_TOML, "rb") as f:
            self.foundry_config = tomllib.load(f)


context = Context()
