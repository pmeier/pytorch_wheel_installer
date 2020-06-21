from tox import hookimpl
from tox.action import Action
from tox.config import Parser, TestenvConfig
from tox.venv import VirtualEnv

from .cli import (
    argument_meta,
    get_backend,
    get_language,
    get_platform,
)
from .core import find_links

from typing import Callable, Any, Optional

TYPE_TO_TYPESTR = {bool: "bool", str: "string"}

from copy import copy


def add_argument(parser, name, meta, **kwargs):
    meta = copy(meta)
    meta.update(kwargs)
    parser.add_argument(f"--pytorch-{name}", **meta)


def add_testenv_attribute(parser, name, meta, **kwargs):
    meta = copy(meta)
    meta.update(kwargs)
    typestr = TYPE_TO_TYPESTR[meta.pop("type")]
    parser.add_testenv_attribute(f"pytorch_{name}", type=typestr, **meta)


def add_argument_and_testenv_attribute(
    parser, name, meta=None, argument_kwargs=None, testenv_attribute_kwargs=None
) -> None:
    if meta is None:
        meta = argument_meta(name)
    if argument_kwargs is None:
        argument_kwargs = {}
    if testenv_attribute_kwargs is None:
        testenv_attribute_kwargs = {}
    add_argument(parser, name, meta, **argument_kwargs)
    add_testenv_attribute(parser, name, meta, **testenv_attribute_kwargs)


def postprocessor(
    name: str, select: Optional[Callable[[Any, Any], Any]] = None
) -> Callable[[TestenvConfig, Any], Any]:
    if select is None:

        def select(arg: Any, value: Any) -> Any:
            return arg if arg is not None else value

    def postprocess(testenv_config: TestenvConfig, value: Any) -> Any:
        arg = getattr(testenv_config.config.option, f"pytorch_{name}")
        return select(arg, value)

    return postprocess


@hookimpl
def tox_addoption(parser: Parser) -> None:
    add_argument_and_testenv_attribute(
        parser,
        "install",
        meta={
            "type": bool,
            "default": False,
            help: "Install PyTorch distributions from the latest wheels.",
        },
        argument_kwargs={"action": "store_true"},
        testenv_attribute_kwargs={
            "postprocess": postprocessor(
                "install", select=lambda arg, value: arg or value
            )
        },
    )

    for name in ("install", "distribution", "backend", "language", "platform"):
        add_argument_and_testenv_attribute(parser, name)


@hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> None:
    config = venv.envconfig
    if not config.pytorch_install:
        return None

    def get_default(value, default_fn):
        return value if value is not None else default_fn()

    distribution = config.pytorch_distribution
    backend = get_default(config.pytorch_backend, get_backend)
    language = get_default(config.pytorch_language, get_language)
    platform = get_default(config.pytorch_platform, get_platform)

    links = find_links(distribution, backend, language, platform)
    action.popen((venv.getcommandpath("pip"), "install", *links))
