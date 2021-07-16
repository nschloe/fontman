import argparse
import datetime
import io
import json
import shutil
import tarfile
import zipfile

import requests

from .tools import get_dir, get_version_text


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
        assets = res_json['assets']

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
            "tag": res_json["tag_name"],
        }

        with open(target_dir / "fontman.json", "w") as f:
            json.dump(db, f, indent=2)

        tag = res_json["tag_name"]
        print(f"Successfully updated to {repo} {tag}")
