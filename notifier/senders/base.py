from __future__ import annotations

from abc import ABC, abstractmethod

from notifier.models import SendResult


class Sender(ABC):
    @abstractmethod
    def send_text(self, target: str, message: str) -> SendResult:
        raise NotImplementedError
