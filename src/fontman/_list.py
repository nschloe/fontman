import json

from rich import box
from rich.console import Console
from rich.table import Table

from .tools import get_dir


def list_fonts():
    fontman_dir = get_dir()

    table = Table(show_header=False)
    table.box = box.SIMPLE

    table.add_column("Name")
    table.add_column("Release")

    for directory in sorted(fontman_dir.glob("*")):
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
