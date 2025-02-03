from typing import TYPE_CHECKING

import platformdirs

if TYPE_CHECKING:
    from pathlib import Path


def normalize_dirname(string: str) -> str:
    return string.replace("/", "_").lower()


def get_dir() -> Path:
    fontman_dir = platformdirs.user_data_path() / "fonts" / "fontman"
    fontman_dir.mkdir(parents=True, exist_ok=True)
    return fontman_dir
