import re
import subprocess
from abc import ABC, abstractmethod
from typing import Any

__all__ = [
    "ComputationBackend",
    "CPUBackend",
    "CUDABackend",
    "detect_computation_backend",
]


class ComputationBackend(ABC):
    @property
    @abstractmethod
    def local(self) -> str:
        ...

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ComputationBackend):
            return self.local == other.local
        elif isinstance(other, str):
            return self.local == other
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.local)

    def __repr__(self) -> str:
        return self.local

    @classmethod
    def from_str(cls, string: str) -> "ComputationBackend":
        string = string.lower()
        try:
            if string == "cpu":
                return CPUBackend()
            elif string.startswith("cu"):
                match = re.match(r"^cu(da)?(?P<version>[\d.]+)$", string)
                if match is None:
                    raise Exception

                version = match.group("version")
                if "." in version:
                    major, minor = version.split(".")
                else:
                    major = version[:-1]
                    minor = version[-1]

                return CUDABackend(int(major), int(minor))

        except Exception:
            pass

        raise RuntimeError(f"Unable to parse {string} into a computation backend")


class CPUBackend(ComputationBackend):
    @property
    def local(self) -> str:
        return "cpu"


class CUDABackend(ComputationBackend):
    def __init__(self, major: int, minor: int) -> None:
        self.major = major
        self.minor = minor

    @property
    def local(self) -> str:
        return f"cu{self.major}{self.minor}"


NVCC_RELEASE_PATTERN = re.compile(r"release (?P<major>\d+)[.](?P<minor>\d+)")


def detect_computation_backend() -> ComputationBackend:
    fallback = CPUBackend()
    try:
        output = (
            subprocess.check_output("nvcc --version", shell=True)
            .decode("utf-8")
            .strip()
        )
        match = NVCC_RELEASE_PATTERN.findall(output)
        if not match:
            return fallback

        major, minor = match[0]
        return CUDABackend(int(major), int(minor))
    except subprocess.CalledProcessError:
        return fallback
