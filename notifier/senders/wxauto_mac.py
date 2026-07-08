from __future__ import annotations

import platform

from notifier.models import SendResult
from notifier.senders.base import Sender


class WxAutoMacSender(Sender):
    """macOS Accessibility sender backed by wxauto-mac.

    wxauto-mac itself mixes Accessibility APIs and keyboard/clipboard events.
    This adapter keeps that implementation isolated from notifier core.
    """

    def __init__(self, language: str = "cn"):
        self.language = language

    def send_text(self, target: str, message: str) -> SendResult:
        if platform.system() != "Darwin":
            return SendResult(ok=False, message="macos-accessibility sender requires macOS")

        try:
            from wxauto_mac import WeChat
        except Exception as exc:
            return SendResult(ok=False, message=f"wxauto-mac is not available: {exc}")

        try:
            wx = WeChat(language=self.language)
            if hasattr(wx, "SendMsg"):
                wx.SendMsg(message, target)
                return SendResult(ok=True, message="sent by wxauto-mac SendMsg")
            if hasattr(wx, "SendToFriend"):
                ok = bool(wx.SendToFriend(target, message))
                return SendResult(ok=ok, message="sent by wxauto-mac SendToFriend" if ok else "wxauto-mac returned false")
            return SendResult(ok=False, message="wxauto-mac has no supported send method")
        except Exception as exc:
            return SendResult(ok=False, message=str(exc))
