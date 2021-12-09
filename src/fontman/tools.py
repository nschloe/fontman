from pathlib import Path

import appdirs


def normalize_dirname(string: str) -> str:
    return string.replace("/", "_").lower()


def get_dir() -> Path:
    fontman_dir = Path(appdirs.user_data_dir()) / "fonts" / "fontman"
    fontman_dir.mkdir(parents=True, exist_ok=True)
    return fontman_dir
