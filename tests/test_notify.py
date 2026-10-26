import json
import urllib.error

import pytest

from pawwatch import notify


@pytest.fixture
def posted(monkeypatch):
    """Captures each request instead of sending it."""
    requests = []

    class Response:
        def close(self):
            pass

    def urlopen(req, timeout):
        requests.append(req)
        return Response()

    monkeypatch.setattr(notify.urllib.request, "urlopen", urlopen)
    for var in ("LINE_CHANNEL_TOKEN", "LINE_USER_ID", "DISCORD_WEBHOOK_URL"):
        monkeypatch.delenv(var, raising=False)
    return requests


def test_nothing_sent_unless_configured(posted, monkeypatch):
    monkeypatch.setenv("LINE_CHANNEL_TOKEN", "t")  # LINE needs the user ID too
    assert notify.channels() == []
    assert notify.send("hi") == []
    assert posted == []


def test_line_push(posted, monkeypatch):
    monkeypatch.setenv("LINE_CHANNEL_TOKEN", "token")
    monkeypatch.setenv("LINE_USER_ID", "U123")
    assert notify.send("Tangerine ate twice today.") == ["LINE"]
    (req,) = posted
    assert req.full_url == notify.LINE_PUSH
    assert req.get_header("Authorization") == "Bearer token"
    assert json.loads(req.data) == {"to": "U123", "messages": [{"type": "text", "text": "Tangerine ate twice today."}]}


def test_discord_webhook(posted, monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.test/hook")
    assert notify.send("hi") == ["Discord"]
    (req,) = posted
    assert req.full_url == "https://discord.test/hook"
    assert json.loads(req.data) == {"content": "hi"}
    assert req.get_header("User-agent") == "PawWatch"


def test_failure_is_reported_not_raised(monkeypatch, capsys):
    def urlopen(req, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(notify.urllib.request, "urlopen", urlopen)
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.test/hook")
    monkeypatch.delenv("LINE_CHANNEL_TOKEN", raising=False)
    assert notify.send("hi") == []
    assert "Discord failed" in capsys.readouterr().out
