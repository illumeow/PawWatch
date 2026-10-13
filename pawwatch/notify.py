"""Text messages to the owner's phone: LINE and/or Discord. Text only, never frames. Owner: B.

Environment (each channel is used only when its variables are set; with none set, nothing is sent):
    LINE_CHANNEL_TOKEN, LINE_USER_ID   LINE Messaging API push to one user (LINE Notify closed in 2025)
    DISCORD_WEBHOOK_URL                a Discord channel's webhook
"""

import json
import os
import urllib.request

LINE_PUSH = "https://api.line.me/v2/bot/message/push"
TIMEOUT_S = 10


def channels() -> list[str]:
    """Names of the configured channels, e.g. ["LINE", "Discord"]."""
    found = []
    if os.environ.get("LINE_CHANNEL_TOKEN") and os.environ.get("LINE_USER_ID"):
        found.append("LINE")
    if os.environ.get("DISCORD_WEBHOOK_URL"):
        found.append("Discord")
    return found


def send(text: str) -> list[str]:
    """Send `text` to every configured channel; returns the ones that took it. Blocks up to TIMEOUT_S per channel."""
    sent = []
    for name in channels():
        if name == "LINE":
            ok = _post(
                LINE_PUSH,
                {"to": os.environ["LINE_USER_ID"], "messages": [{"type": "text", "text": text}]},
                {"Authorization": f"Bearer {os.environ['LINE_CHANNEL_TOKEN']}"},
                name,
            )
        else:
            ok = _post(os.environ["DISCORD_WEBHOOK_URL"], {"content": text}, {}, name)
        if ok:
            sent.append(name)
    return sent


def _post(url: str, body: dict, headers: dict[str, str], name: str) -> bool:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        # Discord's webhooks refuse urllib's default user agent
        headers={"Content-Type": "application/json", "User-Agent": "PawWatch", **headers},
    )
    try:
        urllib.request.urlopen(req, timeout=TIMEOUT_S).close()
    except Exception as e:  # noqa: BLE001 — a failed message must never stop the pipeline
        print(f"[notify] {name} failed: {e}", flush=True)
        return False
    return True
