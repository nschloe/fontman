import pathlib
import sys
from importlib import metadata

import appdirs


def normalize_dirname(string):
    return string.replace("/", "_").lower()


def get_version_text(prog):
    try:
        version = metadata.version("fontman")
    except Exception:
        version = "unknown"

    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    version_text = "\n".join(
        [
            f"{prog} {version} [Python {python_version}]",
            "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>",
        ]
    )
    return version_text


def get_dir():
    fontman_dir = pathlib.Path(appdirs.user_data_dir()) / "fonts" / "fontman"
    fontman_dir.mkdir(parents=True, exist_ok=True)
    return fontman_dir
