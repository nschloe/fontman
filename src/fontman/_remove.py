import argparse
import shutil

from .tools import get_dir, get_version_text


def _cli_remove(argv=None):
    parser = argparse.ArgumentParser(
        description=("Remove installed fonts."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "repo", nargs="+", type=str, help="GitHub repository fonts to remove"
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
        remove(repo)


def remove(repo: str):
    fontman_dir = get_dir()

    dirname = repo.replace("/", "-").lower()

    directory = fontman_dir / dirname
    if not directory.exists():
        raise RuntimeError(f"Could not find font at {directory}")

    shutil.rmtree(directory)

    print(f"Successfully removed {repo} font")
