import argparse
import json

from .tools import get_dir, get_version_text

from rich import box
from rich.console import Console
from rich.table import Table


def _cli_list(argv=None):
    parser = argparse.ArgumentParser(
        description=("List installed fonts."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    list_fonts()


def list_fonts():
    fontman_dir = get_dir()

    console = Console()
    console.print("Installed fonts:")
    table = Table(show_header=False)
    table.box = box.SIMPLE

    table.add_column("Name")
    table.add_column("Release")

    for p in fontman_dir.glob("*"):
        if not p.is_dir():
            continue
        if not (p / "fontman.json").exists():
            continue

        with open(p / "fontman.json") as f:
            d = json.load(f)

        table.add_row(d["repo"], d["tag"])

    console.print(table)
