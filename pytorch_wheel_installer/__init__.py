import warnings
from os import path

from .__about__ import *

try:
    with open(path.join(path.dirname(__file__), "__version__"), "r") as fh:
        __version__ = fh.read().strip()
except FileNotFoundError:
    msg = (
        "The file pytorch_wheel_installer/__version__ does not exist, but should have been "
        "autogenerated during the setup. Please check your installation."
    )
    warnings.warn(msg)
    __version__ = __base_version__
