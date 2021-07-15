import argparse
import datetime
import json
import shutil
import urllib
import urllib.request
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
        raise RuntimeError(f"Failed request to {url}")

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

    # pick the OTF source
    asset = None
    for asset in res_json["assets"]:
        if asset["name"].lower().startswith("otf"):
            break
    assert asset is not None

    assert asset["content_type"] == "application/zip"
    # res = requests.get(asset["browser_download_url"])
    url = asset["browser_download_url"]
    filehandle, _ = urllib.request.urlretrieve(url)
    zip_file_object = zipfile.ZipFile(filehandle, "r")
    if (fontman_dir / dirname).exists():
        shutil.rmtree(fontman_dir / dirname)
    zip_file_object.extractall(fontman_dir / dirname)

    # adde database file
    db = {
        "last-updated": datetime.datetime.now().isoformat(),
        "tag": res_json["tag_name"],
    }

    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)

    tag = res_json["tag_name"]
    print(f"Successfully installed {tag} of {repo}")
