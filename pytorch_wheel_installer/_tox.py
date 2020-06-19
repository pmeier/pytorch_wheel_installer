from tox import hookimpl
from tox.action import Action
from tox.config import Parser
from tox.venv import VirtualEnv

from .cli import (
    add_backend_argument,
    add_distribution_argument,
    add_language_argument,
    add_platform_argument,
    get_backend,
    get_language,
    get_platform,
)
from .core import find_links


@hookimpl
def tox_addoption(parser: Parser) -> None:
    parser.add_argument(
        "--pytorch-install",
        action="store_true",
        help=(
            "Install PyTorch distributions from the latests wheels before the other "
            "dependencies."
        ),
    )

    add_distribution_argument(parser, "--pytorch-distribution")
    add_backend_argument(parser, "--pytorch-backend")
    add_language_argument(parser, "--pytorch-language")
    add_platform_argument(parser, "--pytorch-platform")


@hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> None:
    args = venv.envconfig.config.option
    if not args.pytorch_install:
        return None

    backend = (
        args.pytorch_backend if args.pytorch_backend is not None else get_backend()
    )
    language = (
        args.pytorch_language if args.pytorch_language is not None else get_language()
    )
    platform = (
        args.pytorch_platform if args.pytorch_platform is not None else get_platform()
    )

    links = find_links(args.pytorch_distribution, backend, language, platform)
    action.popen((venv.getcommandpath("pip"), "install", *links))
