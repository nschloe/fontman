import json

from rich import box
from rich.console import Console
from rich.table import Table

from ._install import _download_and_install, _fetch_info_rest
from .tools import get_dir


def update_all(token_file=None):
    token = token_file.readline().strip() if token_file else None

    fontman_dir = get_dir()

    update_list = []

    for directory in sorted(fontman_dir.glob("*")):
        if not directory.is_dir():
            continue
        if not (directory / "fontman.json").exists():
            continue

        with open(directory / "fontman.json") as f:
            d = json.load(f)

        old_tag = d["tag"]
        new_tag, assets = _fetch_info_rest(d["repo"], token)

        if old_tag != new_tag:
            update_list.append((directory, d["repo"], old_tag, new_tag, assets))

    console = Console()

    if len(update_list) == 0:
        console.print("All installed fonts up-to-date.")
        return 0

    console.print("Available updates:")
    table = Table(show_header=False)
    table.box = box.SIMPLE
    table.add_column("Name")
    table.add_column("old")
    table.add_column("arrow")
    table.add_column("new")
    for _, repo, old_tag, new_tag, assets in update_list:
        table.add_row(f"{repo}:", old_tag, "→", new_tag)
    console.print(table)

    console.print("Update? [Y/n] ", end="")
    choice = input().lower()
    if choice in ["n", "no"]:
        console.print("Abort.")
        return 1

    for target_dir, repo, _, new_tag, assets in update_list:
        _download_and_install(target_dir, repo, assets, new_tag)
        console.print(f"Successfully updated to {repo} {new_tag}")

    return 0
