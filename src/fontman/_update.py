import json

from rich import box
from rich.console import Console
from rich.table import Table

from ._install import _download_and_install, _fetch_info_rest, _pick_asset
from .tools import get_dir


def update_all(token_file=None) -> int:
    token = token_file.readline().strip() if token_file else None

    fontman_dir = get_dir()

    update_list = []

    for directory in sorted(fontman_dir.glob("*")):
        if not (directory / "fontman.json").exists():
            continue

        with open(directory / "fontman.json") as f:
            d = json.load(f)

        old_tag = d["tag"]
        new_tag, assets = _fetch_info_rest(d["repo"], token=token)

        if old_tag != new_tag:
            asset = _pick_asset(assets)
            update_list.append((directory, d["repo"], old_tag, new_tag, asset))

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
    table.add_column("size")
    for _, repo, old_tag, new_tag, asset in update_list:
        size_mb = asset["size"] / 1024 / 1024
        table.add_row(f"{repo}:", old_tag, "→", new_tag, f"[{size_mb:.1f} MB]")
    console.print(table)

    console.print("Update? [Y/n] ", end="")
    choice = console.input().lower()
    if choice in ["n", "no"]:
        console.print("Abort.")
        return 1

    with console.status("Updating..."):
        for target_dir, repo, _, new_tag, asset in update_list:
            _download_and_install(target_dir, repo, asset, new_tag)
            console.print(f"Successfully updated to {repo} {new_tag}")

    return 0
