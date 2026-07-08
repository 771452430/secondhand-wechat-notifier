from __future__ import annotations

from notifier.config import SenderConfig
from notifier.senders.base import Sender
from notifier.senders.stdout import StdoutSender
from notifier.senders.wxauto_mac import WxAutoMacSender


def create_sender(config: SenderConfig) -> Sender:
    if config.type == "stdout":
        return StdoutSender()
    if config.type == "macos-accessibility":
        return WxAutoMacSender()
    raise ValueError(f"unsupported sender.type: {config.type}")
