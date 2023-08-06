#!/usr/bin/env python3

# For Bash completion, this needs to be in the first 1024 bytes of the file:
# PYTHON_ARGCOMPLETE_OK

# See: https://stat.ripe.net/docs/02.data-api/

import json
import logging
import os
import sys

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, Generator, Tuple

import requests

from argcomplete import autocomplete
from jinja2 import Environment, PackageLoader, select_autoescape

from .filters import as_table, colourise
from .logging import Loggable


Spec = Dict[str, Dict[str, Any]]


class CommandError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


class Command(Loggable):

    # This is a bit of a hack to allow us to get the remaining arguments passed
    # once we exclude the ones we know are meant for the primary command.
    PRIMARY_COMMAND_ARGS = ("json", "quiet")

    URL_TEMPLATE = "https://stat.ripe.net/data/{name}/data.json"

    def __init__(self) -> None:

        self.parser = self._get_parser()
        autocomplete(self.parser)

        self.args = self.parser.parse_args()
        self._log_level = getattr(
            logging, "WARNING" if self.args.quiet else "INFO"
        )

    def __call__(self) -> int:

        status, result = self._fetch()

        writer = sys.stdout
        return_code = 0
        if not status == 200:
            writer = sys.stderr
            return_code = status

        if self.args.json:
            writer.write(json.dumps(result, indent=2))
            return return_code

        environment = Environment(
            loader=PackageLoader("ripe.stat.cli"),
            autoescape=select_autoescape(),
        )
        environment.filters["as_table"] = as_table
        environment.filters["colourise"] = colourise

        if not self.args.subcommand:
            self.parser.print_help()
            return 1

        writer.write(
            environment.get_template(
                f"{self.args.subcommand}/template.jinja"
            ).render(
                result["data"],
            )
        )

        return return_code

    def _get_parser(self):

        parser = ArgumentParser(
            description="A simple wrapper around the RIPEStat API."
        )

        for flag in self.PRIMARY_COMMAND_ARGS:
            parser.add_argument(
                f"--{flag}",
                action="store_true",
                default=False,
            )

        subparsers = parser.add_subparsers(dest="subcommand")

        for name, spec in self._get_specs():
            subparser = subparsers.add_parser(name)
            for argument, is_required in spec["arguments"].items():
                if is_required:
                    subparser.add_argument(argument)
                else:
                    subparser.add_argument(f"--{argument}")

        return parser

    def _fetch(self) -> Tuple[int, dict]:

        # Used for testing without having to hammer the API.  It's also good
        # for coding on trains 🚆
        if os.getenv("MOCK_RIPESTAT"):
            source = (
                Path(__file__).parent
                / "tests"
                / "data"
                / f"{self.args.subcommand}.json"
            )
            with source.open("r") as f:
                return 200, json.load(f)

        params = {}
        for k, v in vars(self.args).items():
            if k not in self.PRIMARY_COMMAND_ARGS:
                params[k] = v

        response = requests.get(
            self.URL_TEMPLATE.format(name=self.args.subcommand),
            params=params,
        )

        return response.status_code, response.json()

    @staticmethod
    def _get_specs() -> Generator[Tuple[str, Spec], None, None]:
        templates_folder = Path(__file__).parent / "templates"
        for path in templates_folder.glob("*/spec.json"):
            with path.open() as f:
                yield path.parent.name, json.load(f)


def main():
    try:
        sys.exit(Command()())
    except CommandError as exception:
        sys.stderr.write("{}\n".format(exception))
        sys.exit(exception.code)


if __name__ == "__main__":
    main()
