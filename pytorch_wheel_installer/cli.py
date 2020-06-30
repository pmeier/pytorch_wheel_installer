import argparse
import subprocess
import sys

from .__init__ import __name__ as name  # type: ignore[import]
from .__init__ import __version__ as version
from .computation_backend import ComputationBackend
from .find import find_links

__all__ = [
    "entry_point",
    "get_help",
]


def entry_point() -> None:
    args = parse_input()
    if args.version:
        print(f"{name}=={version}")
        sys.exit()

    if not args.distributions:
        sys.exit()

    links = find_links(args.distributions, computation_backend=args.computation_backend)

    if args.no_install:
        print("\n".join(links))
        sys.exit()

    subprocess.check_call(" ".join((args.install_cmd, *links)), shell=True)


def parse_input() -> argparse.Namespace:
    # TODO: Use default parser
    parser = argparse.ArgumentParser(
        description="Install PyTorch from the stable wheels. The computation backend "
        "is autodetected from the available hardware preferring CUDA over CPU."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="show version and exit.",
    )
    parser.add_argument(
        "distributions",
        help="PyTorch distributions in pip/setuptools format",
        nargs="*",
    )
    parser.add_argument(
        "-b", "--computation-backend", help=get_help("computation_backend"),
    )
    parser.add_argument(
        "-n",
        "--no-install",
        action="store_true",
        default=False,
        help=("print wheel links instead of installing"),
    )
    parser.add_argument(
        "-c",
        "--install-cmd",
        type=str,
        default="pip install",
        help="installation command. Defaults to 'pip install'",
    )

    args = parser.parse_args()

    if args.computation_backend is not None:
        args.computation_backend = ComputationBackend.from_str(args.computation_backend)

    return args


HELP = {"computation_backend": "pin PyTorch computation backend, e.g. 'cpu' or 'cu102'"}


def get_help(name: str) -> str:
    try:
        return HELP[name]
    except KeyError:
        raise RuntimeError("No help available for name '{name}'")
