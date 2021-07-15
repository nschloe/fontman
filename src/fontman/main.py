import datetime
import json
import urllib
import zipfile
from rich import print
import pathlib
import requests
import shutil
import urllib.request


repo = "adobe-fonts/source-code-pro"
url = f"https://api.github.com/repos/{repo}/releases/latest"

fontman_dir = pathlib.Path("/tmp/fontman/")
fontman_dir.mkdir(parents=True, exist_ok=True)

dirname = repo.replace("/", "-").lower()

fontman_db = fontman_dir / "fontman-db.json"
if fontman_db.exists():
    with open(fontman_db, "r") as f:
        db = json.load(f)
else:
    db = {}


res = requests.get(url)
assert res.ok
res_json = res.json()

print(res_json)

if res_json["prerelease"] or res_json["draft"]:
    exit(1)

if repo in db:
    if db[repo]["tag"] == res_json["tag_name"]:
        # up-to-date
        exit(1)

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

with open(fontman_db, "w") as f:
    json.dump(db, f, indent=2)
