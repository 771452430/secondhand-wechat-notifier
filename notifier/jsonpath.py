from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def get_path(data: Any, path: str, default: Any = None) -> Any:
    if not path:
        return data

    current = data
    for part in path.split("."):
        if current is None:
            return default

        if isinstance(current, Mapping):
            current = current.get(part, default)
            continue

        if isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
            try:
                current = current[int(part)]
                continue
            except (ValueError, IndexError):
                return default

        return default

    return current
