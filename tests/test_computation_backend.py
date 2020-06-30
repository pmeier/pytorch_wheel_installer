import subprocess

import pytest

from pytorch_wheel_installer import computation_backend

try:
    subprocess.check_call("nvcc --version", shell=True)
    CUDA_AVAILABLE = True
except subprocess.CalledProcessError:
    CUDA_AVAILABLE = False


skip_if_cuda_unavailable = pytest.mark.skipif(
    not CUDA_AVAILABLE, reason="Requires CUDA."
)


def test_detect_computation_backend_no_nvcc(mocker):
    mocker.patch(
        "pytorch_wheel_installer.computation_backend.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, ""),
    )

    assert isinstance(
        computation_backend.detect_computation_backend(), computation_backend.CPUBackend
    )


def test_detect_computation_backend_unknown_release(mocker):
    mocker.patch(
        "pytorch_wheel_installer.computation_backend.subprocess.check_output",
        return_value=b"release unknown",
    )

    assert isinstance(
        computation_backend.detect_computation_backend(), computation_backend.CPUBackend
    )


@skip_if_cuda_unavailable
def test_detect_computation_backend_cuda_smoke():
    assert isinstance(
        computation_backend.detect_computation_backend(),
        computation_backend.CUDABackend,
    )
