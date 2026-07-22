"""Shared pytest fixtures for the voices-of-tomorrow skill test suite."""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("voices_of_tomorrow_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

VoicesOfTomorrowSkill = _module.VoicesOfTomorrowSkill
FeedFetchError = _module.FeedFetchError
MediaType = _module.MediaType
PlaybackType = _module.PlaybackType


class FakeFileSystem:
    def __init__(self, base):
        self.base = base
        self.path = str(base)

    def exists(self, name):
        return (self.base / name).exists()

    def open(self, name, mode="r"):
        return open(self.base / name, mode)


def _sample_episodes():
    return [
        {"title": "A Lighthouse Through Time", "author": "Otto Maton",
         "url": "https://365tomorrows.com/wp-content/uploads/2026/03/VOT_LighthouseThroughTime.mp3",
         "pubdate": "Fri, 27 Mar 2026 21:23:46 +0000"},
        {"title": "Terminal Bar", "author": "Susan Anthony",
         "url": "https://365tomorrows.com/wp-content/uploads/2025/12/Terminal_Bar.m4a",
         "pubdate": "Sat, 27 Dec 2025 05:00:16 +0000"},
    ]


@pytest.fixture
def skill(tmp_path):
    s = VoicesOfTomorrowSkill.__new__(VoicesOfTomorrowSkill)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-voices-of-tomorrow.test"
    s.skill_icon = "icon.png"
    s.file_system = FakeFileSystem(tmp_path)
    s.episodes = _sample_episodes()
    return s
