from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NotificationItem:
    source_name: str
    source_label: str
    item_id: str
    title: str
    created_at: str
    url: str
    fields: dict[str, Any]

    @property
    def dedupe_key(self) -> str:
        return f"{self.source_name}:{self.item_id}"


@dataclass(frozen=True)
class SendResult:
    ok: bool
    message: str = ""
