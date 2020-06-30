from typing import Any

__all__ = [
    "get_public_or_private_attr",
]


def get_public_or_private_attr(obj: Any, attr: str) -> Any:
    try:
        return getattr(obj, attr)
    except AttributeError:
        try:
            return getattr(obj, f"_{attr}")
        except AttributeError:
            msg = f"'{type(obj)}' has no attribute '{attr}' or '_{attr}'"
            raise AttributeError(msg)
