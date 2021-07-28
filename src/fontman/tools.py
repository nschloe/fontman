import pathlib

import appdirs


def normalize_dirname(string):
    return string.replace("/", "_").lower()


def get_dir():
    fontman_dir = pathlib.Path(appdirs.user_data_dir()) / "fonts" / "fontman"
    fontman_dir.mkdir(parents=True, exist_ok=True)
    return fontman_dir
