from __future__ import annotations

from notifier.models import SendResult
from notifier.senders.base import Sender


class StdoutSender(Sender):
    def send_text(self, target: str, message: str) -> SendResult:
        print(f"\n--- WeChat target: {target} ---")
        print(message)
        print("--- end ---\n")
        return SendResult(ok=True, message="printed to stdout")
