import re
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, cast

__all__ = ["to_defaultdict", "Backend", "Language", "Platform"]


def to_defaultdict(dct: Dict, default: Any = None) -> defaultdict:
    return defaultdict(lambda: default, dct)


class Backend:
    def __init__(self, backend_str: Optional[str]) -> None:
        self.val = self.parse(backend_str)

    @staticmethod
    def parse(backend_str: Optional[str]) -> Optional[str]:
        if backend_str is None:
            return None

        return (
            backend_str if re.match(r"(cpu|cu\d+)", backend_str) is not None else None
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            other = Backend(other)
        elif not isinstance(other, Backend):
            return False

        return self.val is None or other.val is None or self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)

    def __str__(self) -> str:
        return str(self.val)


class Language:
    def __init__(self, language_str: str) -> None:
        self.major, self.minor = self.parse(language_str)

    @staticmethod
    def parse(language_str: str) -> Tuple[int, Optional[int]]:
        match = re.match(r"(py|cp)(?P<major>\d)(?P<minor>\d)?", language_str)
        if match is None:
            raise ValueError

        major = int(match.group("major"))
        minor_str = cast(Optional[str], match.group("minor"))
        minor = int(minor_str) if minor_str is not None else None

        return major, minor

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            other = Language(other)
        elif not isinstance(other, Language):
            return False

        if not self.major == other.major:
            return False

        return self.minor is None or other.minor is None or self.minor == other.minor

    def __hash__(self) -> int:
        return hash((self.major, self.minor))

    def __str__(self) -> str:
        str = f"{self.major}"
        if self.minor is not None:
            str += f".{self.minor}"
        return str


class Platform:
    def __init__(self, platform_str: str):
        self.val = self.parse(platform_str)

    @staticmethod
    def parse(platform_str: str) -> Optional[str]:
        if platform_str == "Linux" or "linux" in platform_str:
            return "linux"
        elif platform_str == "Windows" or platform_str.startswith("win"):
            return "windows"
        elif platform_str == "Darwin" or platform_str.startswith("macosx"):
            return "macos"
        else:
            return None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            other = Platform(other)
        elif not isinstance(other, Platform):
            return False

        return self.val is None or other.val is None or self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)

    def __str__(self) -> str:
        return str(self.val)
