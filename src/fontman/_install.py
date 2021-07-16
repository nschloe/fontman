import argparse
import datetime
import io
import json
import shutil
import tarfile
import zipfile
from typing import Optional

import requests
from rich.console import Console

from .tools import get_dir, get_version_text


def _cli_install(argv=None):
    parser = argparse.ArgumentParser(
        description=("Install fonts from GitHub."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "repo", nargs="+", type=str, help="GitHub repository fonts to install"
    )

    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        help="File containing a GitHub token (can be - [stdin])",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    args = parser.parse_args(argv)

    token = args.token_file.readline().strip() if args.token_file else None

    for repo in args.repo:
        install(repo, token)


def install(repo: str, token: Optional[str] = None):
    dirname = repo.replace("/", "_").lower()
    target_dir = get_dir() / dirname

    console = Console()

    db_file = target_dir / "fontman.json"
    if db_file.exists():
        console.print(f"{repo} is already installed", style="yellow")
        return

    if target_dir.exists():
        console.print(
            "Target directory exists but does not contain fontman-installed font",
            style="red",
        )
        return

    tag, assets = _fetch_info_rest(repo, token)
    _download_and_install(target_dir, repo, assets, tag)
    console.print(f"Successfully installed [bold]{repo} {tag}[/]")


def _download_and_install(target_dir, repo, assets, tag_name):
    if len(assets) == 0:
        raise RuntimeError("Release without assets")
    elif len(assets) == 1:
        asset = assets[0]
    else:
        # If there are multiple assets, choose one. First, create a rating.
        ratings = [0] * len(assets)
        for k, item in enumerate(assets):
            if "otf" in item["name"].lower():
                ratings[k] += 2
            elif "ttf" in item["name"].lower():
                ratings[k] += 1

        max_rating_assets = [
            asset for asset, rating in zip(assets, ratings) if rating == max(ratings)
        ]
        # pick the one with the smallest size
        asset = min(max_rating_assets, key=lambda item: item["size"])

    url = asset["browser_download_url"]
    res = requests.get(url, stream=True)
    if not res.ok:
        raise RuntimeError(f"Failed to fetch resource from {url}")

    if target_dir.exists():
        shutil.rmtree(target_dir)

    if asset["content_type"] in ["application/zip", "application/x-zip-compressed"]:
        with zipfile.ZipFile(io.BytesIO(res.content), "r") as z:
            z.extractall(target_dir)
    elif asset["content_type"] == "application/x-gzip":
        with tarfile.open(fileobj=res.raw, mode="r|gz") as f:
            f.extractall(target_dir)
    elif asset["content_type"] == "application/x-xz":
        with tarfile.open(fileobj=res.raw, mode="r|xz") as f:
            f.extractall(target_dir)
    else:
        raise RuntimeError(f"Unknown content type {asset['content_type']}")

    # add database file
    db = {
        "repo": repo,
        "last-updated": datetime.datetime.now().isoformat(),
        "tag": tag_name,
    }
    with open(target_dir / "fontman.json", "w") as f:
        json.dump(db, f, indent=2)


def _fetch_info_rest(repo, token=None):
    # The latest release is the most recent non-prerelease, non-draft release, sorted by
    # the created_at attribute.
    url = f"https://api.github.com/repos/{repo}/releases/latest"

    headers = {}
    if token is not None:
        headers["Authorization"] = f"token {token}"

    res = requests.get(url, headers=headers)
    if not res.ok:
        raise RuntimeError(f"Failed request to {url} ({res.status_code}, {res.reason})")

    res_json = res.json()
    assert not res_json["prerelease"]
    assert not res_json["draft"]

    return res_json["tag_name"], res_json["assets"]


# def _fetch_info_graphql(repo):
#     url = "https://api.github.com/graphql"
#
#     # headers = {"Authorization": "token TOKEN"}
#
#     owner, name = repo.split("/")
#
#     query = f"""
#     {{
#       repository(owner: "{owner}", name: "{name}") {{
#         latestRelease
#     }}
#     """
#     res = requests.post(url,json={"query": query})
#
#     if not res.ok:
#         raise RuntimeError(f"Failed request to {url} ({res.status_code}, {res.reason})")
#
#     print(res.json())
#
#     exit(1)
#
#     return res_json["tag_name"], res_json["assets"]
