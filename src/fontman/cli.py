import argparse
import sys
from importlib import metadata

from .main import install


def _update(argv=None):
    return


def _install(argv=None):
    # Parse command line arguments.
    parser = _get_parser()
    args = parser.parse_args(argv)
    print(args)
    for repo in args.repo:
        install(repo)


def get_version():
    try:
        return metadata.version("fontman")
    except Exception:
        return "unknown"


def _get_parser():
    parser = argparse.ArgumentParser(
        description=("Dummy fontman executable."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "repo", nargs="+", type=str, help="GitHub repository to install"
    )

    __copyright__ = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    version_text = "\n".join(
        [
            "fontman {} [Python {}.{}.{}]".format(
                get_version(),
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            __copyright__,
        ]
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=version_text,
        help="display version information",
    )

    return parser
