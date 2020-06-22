from typing import Any, Callable

from tox import hookimpl
from tox.action import Action
from tox.config import Parser
from tox.venv import VirtualEnv

from .cli import (
    Argument,
    description,
    get_argument,
    get_backend,
    get_language,
    get_platform,
)
from .core import find_links


@hookimpl
def tox_addoption(parser: Parser) -> None:
    argument = Argument(
        "install", description(), type=bool, default=False, action="store_true"
    )
    argument.add_as_tox_argument(parser)
    argument.add_as_tox_testenv_attribute(
        parser,
        postprocess=Argument.postprocessor(
            argument.name, select=lambda arg, value: arg or value
        ),
    )

    for name in ("distribution", "backend", "language", "platform"):
        argument = get_argument(name)
        argument.add_as_tox_argument(parser)
        argument.add_as_tox_testenv_attribute(parser)


@hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> None:
    config = venv.envconfig
    if not config.pytorch_install:
        return None

    def get_default(value: Any, default_fn: Callable) -> Any:
        return value if value is not None else default_fn()

    distribution = config.pytorch_distribution
    backend = get_default(config.pytorch_backend, get_backend)
    language = get_default(config.pytorch_language, get_language)
    platform = get_default(config.pytorch_platform, get_platform)

    links = find_links(distribution, backend, language, platform)
    action.popen((venv.getcommandpath("pip"), "install", *links))
