import os
import subprocess
from collections import namedtuple

from textual import log

from crucible.context import DIR
from crucible.parser.parser import output

RunConfig = namedtuple(
    "RunConfig", [
        "profile",
        "match_contract",
        "match_test",
        "match_path",
        "verbose"
    ]
)


class ForgeRunner():
    def run(self, config: RunConfig):
        result = subprocess.run(
            ["sh", "-c", f"cd {DIR} && {self.make_command(config)}"],
            capture_output=True,  # Python >= 3.7 only
            text=True  # Python >= 3.7 only
        )
        try:
            return output.parse_string(result.stdout, parse_all=True)
        except Exception as e:
            self.save_fixture(config, result.stdout)
            raise e

    def save_fixture(self, config: RunConfig, fixture: str):
        fixture_path = f"/tmp/{config.match_contract}_{config.match_test}.txt"
        with open(fixture_path, "w") as f:
            f.write(fixture)

    def make_command(self, config: RunConfig):
        args = ["forge", "test"]
        env = os.environ.copy()
        env["FOUNDRY_PROFILE"] = config.profile
        if config.match_path:
            args.append(f"--match-path {config.match_path}")
        if config.match_contract:
            args.append(f"--match-contract {config.match_contract}")
        if config.match_test:
            args.append(f"--match-test \"^{config.match_test}\\(\\)$\"")
        if config.verbose:
            args.append("-vvvvv")
        command = " ".join(args)
        return command


runner = ForgeRunner()
