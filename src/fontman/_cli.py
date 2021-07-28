import argparse
from importlib import metadata
from sys import version_info

from ._install import install_fonts
from ._list import list_fonts
from ._remove import remove
from ._update import update_all


def cli(argv=None):
    parser = argparse.ArgumentParser(
        description=("Manage fonts."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(),
        help="display version information",
    )

    subparsers = parser.add_subparsers(title="subcommands")

    parser_install = subparsers.add_parser(
        "install", help="Install new fonts", aliases=["i", "inst", "add"]
    )
    _cli_install(parser_install)
    parser_install.set_defaults(
        func=lambda args: install_fonts(args.repos, args.token_file, args.force)
    )

    parser_list = subparsers.add_parser(
        "list", help="List installed fonts", aliases=["l"]
    )
    parser_list.set_defaults(func=lambda _: list_fonts())

    parser_remove = subparsers.add_parser(
        "remove", help="Remove fonts", aliases=["rm", "uninstall"]
    )
    _cli_remove(parser_remove)
    parser_remove.set_defaults(func=lambda args: remove(args.names))

    parser_update = subparsers.add_parser(
        "update", help="Update installed fonts", aliases=["upgrade", "up"]
    )
    _cli_update(parser_update)
    parser_update.set_defaults(func=lambda args: update_all(args.token_file))

    # args = parser.parse_args(argv)
    # token = args.token_file.readline().strip() if args.token_file else None
    # return update_all(token)

    args = parser.parse_args(argv)
    return args.func(args)


def _cli_install(parser):
    parser.add_argument(
        "repos", nargs="+", type=str, help="GitHub repository fonts to install"
    )

    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        help="File containing a GitHub token (can be - [stdin])",
    )

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Force re-installation (default: false)",
    )

    # token = args.token_file.readline().strip() if args.token_file else None

    # for repo in args.repo:
    #     install(repo, token, args.force)


def _cli_remove(parser):
    parser.add_argument(
        "names", nargs="+", type=str, help="GitHub repository fonts to remove"
    )


def _cli_update(parser):
    parser.add_argument(
        "-t",
        "--token-file",
        type=argparse.FileType("r"),
        help="File containing a GitHub token (can be - [stdin])",
    )


def get_version_text():
    try:
        version = metadata.version("fontman")
    except Exception:
        version = "unknown"

    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    version_text = "\n".join(
        [
            f"fontman {version} [Python {python_version}]",
            "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>",
        ]
    )
    return version_text
