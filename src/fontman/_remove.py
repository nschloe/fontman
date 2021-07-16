import argparse
import json
import shutil
from typing import List

from rich.console import Console

from .tools import get_dir, get_version_text


def _cli_remove(argv=None):
    parser = argparse.ArgumentParser(
        description=("Remove installed fonts."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "name", nargs="+", type=str, help="GitHub repository fonts to remove"
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    args = parser.parse_args(argv)
    return remove(args.name)


def remove(names: List[str]):
    fontman_dir = get_dir()

    scheduled_dirs = []
    for directory in fontman_dir.glob("*"):
        if not ((directory / "fontman.json").exists()):
            continue
        for name in names:
            if name.lower() in directory.name.lower():
                scheduled_dirs.append(directory)
                break

    console = Console()

    if len(scheduled_dirs) == 0:
        console.print("Found no fonts to remove.", style="yellow")
        return 1

    repos = []
    for directory in sorted(scheduled_dirs):
        with open(directory / "fontman.json") as f:
            d = json.load(f)
        repos.append(d["repo"])

    console.print("The following fonts are scheduled for removal:\n")
    for repo in repos:
        console.print(f"  {repo}")

    console.print("\nRemove? \\[y/N] ", end="")
    choice = input().lower()
    if choice not in ["y", "yes"]:
        console.print("Abort.")
        return 1

    for repo, directory in zip(repos, scheduled_dirs):
        shutil.rmtree(directory)
        console.print(f"Successfully removed {repo}")

    return 0
