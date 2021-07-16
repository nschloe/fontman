import argparse
import json

import requests

from .tools import get_dir, get_version_text
from ._install import _download_and_install


def _cli_update(argv=None):
    parser = argparse.ArgumentParser(
        description=("Update fonts from GitHub."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    parser.parse_args(argv)

    update_all()


def update_all():
    fontman_dir = get_dir()

    update_list = []

    for directory in fontman_dir.glob("*"):
        if not directory.is_dir():
            continue
        if not (directory / "fontman.json").exists():
            continue

        with open(directory / "fontman.json") as f:
            d = json.load(f)

        repo = d["repo"]

        url = f"https://api.github.com/repos/{repo}/releases/latest"

        res = requests.get(url)
        if not res.ok:
            raise RuntimeError(f"Failed request to {url} ({res.status_code})")

        res_json = res.json()
        assert not res_json["prerelease"]
        assert not res_json["draft"]

        if d["tag"] != res_json["tag_name"]:
            update_list.append((directory, repo, d["tag"], res_json))

    if len(update_list) == 0:
        print("All installed fonts up-to-date.")
        return

    print("Available updates:")
    for _, repo, old_tag, res_json in update_list:
        print()
        print(f"  {repo}:")
        print(f"  {old_tag}  →  {res_json['tag_name']}")

    print()
    print("Update? [y/N] ", end="")
    choice = input().lower()
    if choice not in ["y", "yes"]:
        print("Abort.")
        return 1

    for target_dir, repo, _, res_json in update_list:
        tag = res_json["tag_name"]
        _download_and_install(target_dir, repo, res_json["assets"], tag)
        print(f"Successfully updated to {repo} {tag}")
