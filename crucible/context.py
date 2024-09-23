import tomllib
import os
from textual import log
# This file contains the Context class which is used to
# parse and store the context of the current execution.

DIR = os.path.abspath("../mento/mento-core")  # os.getcwd()
FOUNDRY_TOML = os.path.join(DIR, "foundry.toml")


class Context():

    def __init__(self):
        with open(FOUNDRY_TOML, "rb") as f:
            self.foundry_config = tomllib.load(f)


context = Context()
