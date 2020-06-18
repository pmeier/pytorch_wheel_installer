import re
import subprocess
import sys
from platform import system as _system

import pytest

from pytorch_wheel_installer import cli

try:
    subprocess.check_call("nvcc --version", shell=True)
    CUDA_AVAILABLE = True
except subprocess.CalledProcessError:
    CUDA_AVAILABLE = False


skip_if_cuda_available = pytest.mark.skipif(
    CUDA_AVAILABLE, reason="Requires CUDA to be unavailable."
)
skip_if_cuda_unavailable = pytest.mark.skipif(
    not CUDA_AVAILABLE, reason="Requires CUDA."
)


def skip_if_not_system(system, name=None):
    if name is None:
        name = system
    return pytest.mark.skipif(_system() != system, reason=f"Requires {name}.")


skip_if_not_linux = skip_if_not_system("Linux")
skip_if_not_windows = skip_if_not_system("Windows")
skip_if_not_macos = skip_if_not_system("Darwin", name="macOS")


@skip_if_cuda_available
def test_get_backend_cpu():
    assert cli.get_backend() == "cpu"


@skip_if_cuda_unavailable
def test_get_backend_cuda():
    assert re.match(r"cu\d+", str(cli.get_backend())) is not None


def test_get_language():
    major, minor = sys.version_info[:2]
    assert cli.get_language() == f"py{major}{minor}"


@skip_if_not_linux
def test_get_platform_linux():
    assert cli.get_platform() == "linux"


@skip_if_not_windows
def test_get_platform_windows():
    assert cli.get_platform() == "windows"


@skip_if_not_macos
def test_get_platform_macos():
    assert cli.get_platform() == "macos"
