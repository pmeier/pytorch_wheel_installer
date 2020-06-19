import argparse
import re
import subprocess
import sys
from platform import system

from .__init__ import __version__  # type: ignore[import]
from .core import main
from .utils import Backend, Language, Platform

__all__ = ["entry_point", "parse_input"]


def entry_point() -> None:
    args = parse_input()
    if args.version:
        print(f"pytorch_wheel_selector=={__version__}")
        sys.exit()
    main(args)


def parse_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install PyTorch from the latest wheels."
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        default=False,
        help="Show version and exit.",
    )
    parser.add_argument(
        "--distribution",
        "-d",
        type=str,
        default="torch,torchvision",
        help=(
            "PyTorch distributions e.g. 'torch', 'torchvision'. Multiple distributions "
            "can be given as a comma-separated list. Defaults to 'torch,torchvision'."
        ),
    )
    parser.add_argument(
        "--backend",
        "-b",
        type=str,
        default=None,
        help=(
            "Computation backend e.g. 'cpu' or 'cu102'. If not given the backend is "
            "automatically detected from the available hardware preferring CUDA over "
            "the CPU."
        ),
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default=None,
        help=(
            "Language implementation and version tag e.g. 'py3', 'cp36'. Defaults to "
            "the language version used to run this."
        ),
    )
    parser.add_argument(
        "--platform",
        "-p",
        type=str,
        default=None,
        help=(
            "Platform e.g. 'linux', 'windows', 'macos', or 'any'. Defaults to the "
            "platform that is used to run this."
        ),
    )
    parser.add_argument(
        "--no-install",
        "-ni",
        action="store_true",
        default=False,
        help=(
            "If given, the selected wheels are written to STDOUT instead of "
            "installed."
        ),
    )
    parser.add_argument(
        "--pip-cmd",
        "-pc",
        type=str,
        default="pip install",
        help=(
            "pip command that is used to install the wheels. Defaults to 'pip install'"
        ),
    )
    args = parser.parse_args()

    args.distributions = args.distribution.split(",")

    if args.backend is None:
        args.backend = get_backend()
    if args.language is None:
        args.language = get_language()
    if args.platform is None:
        args.platform = get_platform()

    return args


def get_backend() -> Backend:
    default_backend = Backend("cpu")
    try:
        output = (
            subprocess.check_output("nvcc --version", shell=True)
            .decode("utf-8")
            .strip()
        )
        match = re.findall(r"release (?P<major>\d+)[.](?P<minor>\d+)", output)[0]
        if not match:
            return default_backend

        major, minor = match
        return Backend(f"cu{major}{minor}")
    except subprocess.CalledProcessError:
        return default_backend


def get_language() -> Language:
    major, minor = sys.version_info[:2]
    return Language(f"cp{major}{minor}")


def get_platform() -> Platform:
    platform = Platform(system())
    if platform.val is not None:
        return platform

    msg = (
        f"Platform '{platform}' is not recognized. Try setting it manually with "
        "--platform"
    )
    raise RuntimeError(msg)
