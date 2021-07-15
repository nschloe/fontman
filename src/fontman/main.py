import datetime
import json
import pathlib
import shutil
import urllib
import urllib.request
import zipfile

import requests
from rich import print

fontman_dir = pathlib.Path("/tmp/fontman/")
fontman_dir.mkdir(parents=True, exist_ok=True)


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

    print(res_json)
    db_file = fontman_dir / "fontman-db.json"
    if db_file.exists():
        with open(db_file, "r") as f:
            db = json.load(f)
    else:
        db = {}

    if repo in db:
        if db[repo]["tag"] == res_json["tag_name"]:
            tag = res_json["tag_name"]
            print(repr(repo))
            print(f"Already have latest release {tag} of {repo}")
            return

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

    # update database
    db[repo] = {
        "last-updated": datetime.datetime.now().isoformat(),
        "tag": res_json["tag_name"],
        "directory": dirname,
    }

    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)

    tag = res_json["tag_name"]
    print(f"Successfully installed {tag} of {repo}")
