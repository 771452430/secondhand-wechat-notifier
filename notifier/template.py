from __future__ import annotations

from typing import Any


class SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def render_template(template: str, values: dict[str, Any]) -> str:
    normalized = {key: _stringify(value) for key, value in values.items()}
    return template.format_map(SafeDict(normalized)).strip()


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
