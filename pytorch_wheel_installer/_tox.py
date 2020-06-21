from copy import copy
from typing import Any, Callable, Dict, Optional

from tox import hookimpl
from tox.action import Action
from tox.config import Parser, TestenvConfig
from tox.venv import VirtualEnv

from .cli import argument_meta, description, get_backend, get_language, get_platform
from .core import find_links

TYPE_TO_TYPESTR = {bool: "bool", str: "string"}


def add_argument(
    parser: Parser, name: str, meta: Dict[str, Any], **kwargs: Any
) -> None:
    meta = copy(meta)
    meta.update(kwargs)
    parser.add_argument(f"--pytorch-{name}", **meta)


def add_testenv_attribute(
    parser: Parser, name: str, meta: Dict[str, Any], **kwargs: Any
) -> None:
    meta = copy(meta)
    meta.update(kwargs)
    try:
        typestr = TYPE_TO_TYPESTR[meta.pop("type")]
    except KeyError:
        meta.pop("action")
        typestr = "bool"
    try:
        meta.pop("metavar")
    except KeyError:
        pass
    parser.add_testenv_attribute(f"pytorch_{name}", type=typestr, **meta)


def add_argument_and_testenv_attribute(
    parser: Parser,
    name: str,
    meta: Optional[Dict[str, Any]] = None,
    argument_kwargs: Optional[Dict[str, Any]] = None,
    testenv_attribute_kwargs: Optional[Dict[str, Any]] = None,
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
        a = select(arg, value)  # type: ignore[misc]
        print(arg, value, a)
        return a

    return postprocess


@hookimpl
def tox_addoption(parser: Parser) -> None:
    # parser.add_argument("--pytorch-install", action="store_true", help=description())
    # parser.add_testenv_attribute(
    #     "pytorch_install",
    #     "bool",
    #     help=description(),
    #     default=False,
    #     postprocess=postprocessor("install", select=lambda arg, value: arg or value),
    # )
    add_argument_and_testenv_attribute(
        parser,
        "install",
        meta={"action": "store_true", "default": False, "help": description()},
        testenv_attribute_kwargs={
            "postprocess": postprocessor(
                "install", select=lambda arg, value: arg or value
            )
        },
    )

    for name in ("distribution", "backend", "language", "platform"):
        add_argument_and_testenv_attribute(parser, name)


@hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> None:
    config = venv.envconfig
    print(config.pytorch_install)
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
