import argparse
import re
import subprocess
import sys
from platform import system
from typing import Any, Dict, Optional, Type

from .__init__ import __name__ as name  # type: ignore[import]
from .__init__ import __version__ as version
from .core import find_links
from .utils import Backend, Language, Platform

__all__ = [
    "entry_point",
    "description",
    "argument_meta",
    "get_backend",
    "get_language",
    "get_platform",
]


def entry_point() -> None:
    args = parse_input()
    if args.version:
        print(f"{name}=={version}")
        sys.exit()

    links = find_links(args.distribution, args.backend, args.language, args.platform)

    if args.no_install:
        print("\n".join(links))
        sys.exit()

    subprocess.check_call(" ".join((args.pip_cmd, *links)), shell=True)


def parse_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        default=False,
        help="Show version and exit.",
    )

    parser.add_argument("--distribution", "-d", **argument_meta("distribution"))
    parser.add_argument("--backend", "-b", **argument_meta("backend"))
    parser.add_argument("--language", "-l", **argument_meta("language"))
    parser.add_argument("--platform", "-p", **argument_meta("platform"))

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
        "--install-cmd",
        "-ic",
        type=str,
        default="pip install",
        help="Command that is used to install the wheels. Defaults to 'pip install'",
    )

    args = parser.parse_args()

    if args.backend is None:
        args.backend = get_backend()
    if args.language is None:
        args.language = get_language()
    if args.platform is None:
        args.platform = get_platform()

    return args


def description() -> str:
    return "Install PyTorch from the latest wheels."


HELP = {
    "distribution": (
        "PyTorch distribution e.g. 'torch', 'torchvision'. Multiple distributions can "
        "be given as a comma-separated list. Defaults to 'torch,torchvision'."
    ),
    "backend": (
        "Computation backend e.g. 'cpu' or 'cu102'. If not given the backend is "
        "automatically detected from the available hardware preferring CUDA over CPU."
    ),
    "language": (
        "Language implementation and version tag e.g. 'py3', 'cp36'. Defaults to the "
        "language version used to run this."
    ),
    "platform": (
        "Platform e.g. 'linux', 'windows', 'macos', or 'any'. Defaults to the platform "
        "that is used to run this."
    ),
}


def argument_meta(
    name: str,
    metavar: Optional[str] = None,
    type: Type = str,
    default: Any = None,
    help: Optional[str] = None,
) -> Dict[str, Any]:
    if name == "install":
        raise ZeroDivisionError
    if metavar is None:
        metavar = name.upper()
    if help is None:
        help = HELP[name]
    return {"metavar": metavar, "type": type, "default": default, "help": help}


def get_backend() -> Backend:
    fallback = Backend("cpu")
    try:
        output = (
            subprocess.check_output("nvcc --version", shell=True)
            .decode("utf-8")
            .strip()
        )
        match = re.findall(r"release (?P<major>\d+)[.](?P<minor>\d+)", output)[0]
        if not match:
            return fallback

        major, minor = match
        return Backend(f"cu{major}{minor}")
    except subprocess.CalledProcessError:
        return fallback


def get_language() -> Language:
    major, minor = sys.version_info[:2]
    return Language(f"py{major}{minor}")


def get_platform() -> Platform:
    platform = Platform(system())
    if platform.val is not None:
        return platform

    msg = (
        f"Platform '{platform}' is not recognized. Try setting it manually with "
        "--platform"
    )
    raise RuntimeError(msg)
