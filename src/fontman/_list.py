import argparse
import json

from rich import box
from rich.console import Console
from rich.table import Table

from .tools import get_dir, get_version_text


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

    return list_fonts()


def list_fonts():
    fontman_dir = get_dir()

    table = Table(show_header=False)
    table.box = box.SIMPLE

    table.add_column("Name")
    table.add_column("Release")

    for directory in sorted(fontman_dir.glob("*")):
        if not directory.is_dir():
            continue
        if not (directory / "fontman.json").exists():
            continue

        with open(directory / "fontman.json") as f:
            d = json.load(f)

        table.add_row(d["repo"], d["tag"])

    console = Console()
    if table.row_count == 0:
        console.print(
            f"Found no fontman-installed fonts in {fontman_dir}", style="yellow"
        )
    else:
        console.print(f"Installed fonts (in {fontman_dir}):")
        console.print(table)

    return 0
