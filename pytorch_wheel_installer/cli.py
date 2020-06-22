import argparse
import re
import subprocess
import sys
from platform import system
from typing import Any, Callable, Dict, Optional

from .__init__ import __name__ as name  # type: ignore[import]
from .__init__ import __version__ as version
from .core import find_links
from .utils import Backend, Language, Platform, to_defaultdict

__all__ = [
    "entry_point",
    "description",
    "Argument",
    "get_argument",
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

    subprocess.check_call(" ".join((args.install_cmd, *links)), shell=True)


def parse_input() -> argparse.Namespace:
    # TODO: Use default parser
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="Show version and exit.",
    )

    get_argument("distribution").add_as_cli_argument(parser)
    get_argument("backend").add_as_cli_argument(parser)
    get_argument("platform").add_as_cli_argument(parser)
    get_argument("language").add_as_cli_argument(parser)

    parser.add_argument(
        "-ni",
        "--no-install",
        action="store_true",
        default=False,
        help=(
            "If given, the selected wheels are written to STDOUT instead of "
            "installed."
        ),
    )
    parser.add_argument(
        "-ic",
        "--install-cmd",
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


try:
    from tox.config import Parser as ToxParser
except ImportError:
    from typing_extensions import Protocol

    class ToxParser(Protocol):  # type: ignore[no-redef]
        def add_argument(self, *args: Any, **kwargs: Any) -> None:
            ...

        def add_testenv_attribute(
            self,
            name: str,
            type: str,
            help: str,
            default: Any = None,
            postprocess: Optional[Callable[[Any, Any], Any]] = None,
        ) -> None:
            ...


class Argument:
    TYPE_TO_TYPESTR: Dict[Callable[[str], Any], str] = {bool: "bool", str: "string"}

    def __init__(
        self,
        name: str,
        help: str,
        metavar: Optional[str] = None,
        type: Callable[[str], Any] = str,
        default: Any = None,
        action: str = "store",
    ) -> None:
        self.name = name.lower()
        self.help = help
        if metavar is None:
            metavar = name.upper()
        self.metavar = metavar
        self.type = type
        self.default = default
        self.action = action

    def add_as_cli_argument(self, parser: argparse.ArgumentParser) -> None:
        short_option = f"-{self.name[0]}"
        long_option = f"--{self.name.replace('_', '-')}"
        if self.action == "store":
            kwargs: Dict[str, Any] = {"metavar": self.metavar, "type": self.type}
        else:
            kwargs = {}
        parser.add_argument(
            short_option,
            long_option,
            default=self.default,
            action=self.action,
            help=self.help,
            **kwargs,
        )

    def add_as_tox_argument(self, parser: ToxParser) -> None:
        option = f"--pytorch-{self.name.replace('_', '-')}"
        if self.action == "store":
            kwargs: Dict[str, Any] = {"metavar": self.metavar, "type": self.type}
        else:
            kwargs = {}
        parser.add_argument(
            option, default=self.default, action=self.action, help=self.help, **kwargs
        )

    def add_as_tox_testenv_attribute(
        self, parser: ToxParser, postprocess: Optional[Callable[[Any, Any], Any]] = None
    ) -> None:
        if postprocess is None:
            postprocess = self.postprocessor(self.name)

        name = f"pytorch_{self.name}"
        typestr = self.TYPE_TO_TYPESTR[self.type]
        parser.add_testenv_attribute(
            name, typestr, self.help, default=self.default, postprocess=postprocess
        )

    @staticmethod
    def postprocessor(
        name: str, select: Optional[Callable[[Any, Any], Any]] = None
    ) -> Callable[[Any, Any], Any]:
        if select is None:

            def select(arg: Any, value: Any) -> Any:
                return arg if arg is not None else value

        def postprocess(testenv_config: Any, value: Any) -> Any:
            arg = getattr(testenv_config.config.option, f"pytorch_{name}")
            return select(arg, value)  # type: ignore[misc]

        return postprocess


HELP = to_defaultdict(
    {
        "distribution": (
            "PyTorch distribution e.g. 'torch', 'torchvision'. Multiple distributions "
            "can be given as a comma-separated list. Defaults to 'torch,torchvision'."
        ),
        "backend": (
            "Computation backend e.g. 'cpu' or 'cu102'. If not given the backend is "
            "automatically detected from the available hardware preferring CUDA over "
            "CPU."
        ),
        "language": (
            "Language implementation and version tag e.g. 'py3', 'cp36'. Defaults to "
            "the language version used to run this."
        ),
        "platform": (
            "Platform e.g. 'linux', 'windows', 'macos', or 'any'. Defaults to the "
            "platform that is used to run this."
        ),
    },
    default="",
)

DEFAULT = to_defaultdict({"distribution": "torch,torchvision"})


def get_argument(
    name: str, help: Optional[str] = None, default: Any = None, **kwargs: Any,
) -> Argument:
    if help is None:
        help = HELP[name]
    if default is None:
        default = DEFAULT[name]
    return Argument(name, help, default=default, **kwargs)


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
