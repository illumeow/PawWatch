import pytest

from pawwatch import alarm


class SyncThread:
    """Runs the target right away, so tests don't wait on background threads."""

    def __init__(self, target, args=(), daemon=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


@pytest.fixture(autouse=True)
def fake_outputs(monkeypatch):
    calls = {"sound": 0, "telegram": []}
    monkeypatch.setattr(alarm, "_play_sound", lambda: calls.__setitem__("sound", calls["sound"] + 1))
    monkeypatch.setattr(alarm, "_send_telegram", lambda token, chat, text: calls["telegram"].append(text))
    monkeypatch.setattr(alarm, "_last_video", {})
    monkeypatch.setattr(alarm, "_last_wall", float("-inf"))
    monkeypatch.setattr(alarm, "MIN_WALL_GAP_S", 0.0)
    monkeypatch.setattr(alarm.threading, "Thread", SyncThread)
    for var in ("PAWWATCH_MUTE", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        monkeypatch.delenv(var, raising=False)
    return calls


def test_one_alarm_per_jump_not_per_frame(fake_outputs):
    for frame in range(50):  # cat sits on the counter for 10 s at 5 fps
        alarm.trigger("cam_counter", "forbidden", 1000 + frame * 0.2)
    alarm.trigger("cam_counter", "forbidden", 1000 + 60)  # jumps up again a minute later
    assert fake_outputs["sound"] == 2


def test_mute(fake_outputs, monkeypatch):
    monkeypatch.setenv("PAWWATCH_MUTE", "1")
    alarm.trigger("cam_counter", "forbidden", 1000)
    assert fake_outputs["sound"] == 0


def test_telegram_only_when_configured(fake_outputs, monkeypatch):
    alarm.trigger("cam_counter", "forbidden", 1000)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "c")
    alarm.trigger("cam_counter", "forbidden", 2000)
    assert len(fake_outputs["telegram"]) == 1
    assert "no-go spot (cam_counter)" in fake_outputs["telegram"][0]
