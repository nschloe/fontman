import argparse
import datetime
import io
import json
import shutil
import tarfile
import zipfile

import requests

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
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    args = parser.parse_args(argv)

    for repo in args.repo:
        install(repo)


def install(repo: str):
    # The latest release is the most recent non-prerelease, non-draft release, sorted by
    # the created_at attribute.
    url = f"https://api.github.com/repos/{repo}/releases/latest"

    dirname = repo.replace("/", "-").lower()

    res = requests.get(url)
    if not res.ok:
        raise RuntimeError(f"Failed request to {url} ({res.status_code})")

    res_json = res.json()
    assert not res_json["prerelease"]
    assert not res_json["draft"]

    fontman_dir = get_dir()
    db_file = fontman_dir / dirname / "fontman.json"
    if db_file.exists():
        with open(db_file, "r") as f:
            db = json.load(f)

        if db["tag"] == res_json["tag_name"]:
            tag = res_json["tag_name"]
            print(f"Already have latest release {tag} of {repo}")
            return

        # remove the directory
        shutil.rmtree(fontman_dir / dirname)

    assets = res_json["assets"]

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

    target_dir = fontman_dir / dirname
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
        "last-updated": datetime.datetime.now().isoformat(),
        "tag": res_json["tag_name"],
    }

    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)

    tag = res_json["tag_name"]
    print(f"Successfully installed {tag} of {repo}")
