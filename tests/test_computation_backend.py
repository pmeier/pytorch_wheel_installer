import subprocess

import pytest

from pytorch_wheel_installer import computation_backend as cb


@pytest.fixture
def generic_backend():
    class GenericComputationBackend(cb.ComputationBackend):
        @property
        def local(self):
            return "generic"

    return GenericComputationBackend()


def test_ComputationBackend_eq(generic_backend):
    assert generic_backend == generic_backend
    assert generic_backend == generic_backend.local


def test_ComputationBackend_hash_smoke(generic_backend):
    assert isinstance(hash(generic_backend), int)


def test_ComputationBackend_repr_smoke():
    assert isinstance(repr(generic_backend), str)


def test_ComputationBackend_from_str_cpu():
    string = "cpu"
    backend = cb.ComputationBackend.from_str(string)
    assert isinstance(backend, cb.CPUBackend)


def test_ComputationBackend_from_str_cuda(subtests):
    major, minor = 12, 3
    strings = (
        f"cu{major}{minor}",
        f"cu{major}.{minor}",
        f"cuda{major}{minor}",
        f"cuda{major}.{minor}",
    )
    for string in strings:
        with subtests.test(string=string):
            backend = cb.ComputationBackend.from_str(string)
            assert isinstance(backend, cb.CUDABackend)
            assert backend.major == major
            assert backend.minor == minor


def test_ComputationBackend_from_str_unknown(subtests):
    strings = ("unknown", "cudann")
    for string in strings:
        with subtests.test(string=string):
            with pytest.raises(RuntimeError):
                cb.ComputationBackend.from_str(string)


def test_CPUBackend():
    backend = cb.CPUBackend()
    assert backend == "cpu"


def test_CUDABackend():
    major = 42
    minor = 21
    backend = cb.CUDABackend(major, minor)
    assert backend == f"cu{major}{minor}"


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

    assert isinstance(cb.detect_computation_backend(), cb.CPUBackend)


def test_detect_computation_backend_unknown_release(mocker):
    mocker.patch(
        "pytorch_wheel_installer.computation_backend.subprocess.check_output",
        return_value=b"release unknown",
    )

    assert isinstance(cb.detect_computation_backend(), cb.CPUBackend)


@skip_if_cuda_unavailable
def test_detect_computation_backend_cuda_smoke():
    assert isinstance(cb.detect_computation_backend(), cb.CUDABackend,)
