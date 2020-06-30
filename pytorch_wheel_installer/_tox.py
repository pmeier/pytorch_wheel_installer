from typing import Optional

from tox import hookimpl
from tox.action import Action
from tox.config import Parser, TestenvConfig
from tox.venv import VirtualEnv

from .cli import get_help
from .computation_backend import ComputationBackend
from .find import find_links


@hookimpl
def tox_addoption(parser: Parser) -> None:
    parser.add_testenv_attribute(
        "pytorch_distributions",
        "line-list",
        help="each line specifies a PyTorch distribution in pip/setuptools format",
        default=(),
    )

    def postprocess_computation_backend(
        testenv_config: TestenvConfig, value: Optional[str]
    ) -> Optional[ComputationBackend]:
        if value is None:
            return None

        return ComputationBackend.from_str(value)

    parser.add_testenv_attribute(
        "pytorch_computation_backend",
        "string",
        get_help("computation_backend"),
        postprocess=postprocess_computation_backend,
    )


@hookimpl
def tox_testenv_install_deps(venv: VirtualEnv, action: Action) -> None:
    config = venv.envconfig
    distributions = config.pytorch_distributions
    if not distributions:
        return None

    links = find_links(
        distributions, computation_backend=config.pytorch_computation_backend
    )

    action.setactivity("installdeps-pytorch", ", ".join(links))
    venv._install(links, action=action)
