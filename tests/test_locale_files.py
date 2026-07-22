"""Tests confirming every bundled locale has both a skill.json (Skills
Store visibility) and a voices_of_tomorrow.voc (trigger phrase
recognition) - the 8 languages shared with the other skills in this
family, plus Swedish and Norwegian."""
import json
from pathlib import Path

import pytest

LOCALE_DIR = Path(__file__).resolve().parents[1] / "locale"
EXPECTED_LANGS = ["en-us", "da-dk", "de-de", "es-es", "fr-fr", "it-it",
                   "nl-nl", "pt-pt", "sv-se", "nb-no"]


def test_all_ten_languages_present():
    actual = {p.name for p in LOCALE_DIR.iterdir() if p.is_dir()}
    assert actual == set(EXPECTED_LANGS)


@pytest.mark.parametrize("lang", EXPECTED_LANGS)
def test_skill_json_is_valid_for_every_language(lang):
    data = json.loads((LOCALE_DIR / lang / "skill.json").read_text())
    assert data["skill_id"] == "ovos-skill-voices-of-tomorrow.andlo"
    assert data["name"]
    assert data["description"]


@pytest.mark.parametrize("lang", EXPECTED_LANGS)
def test_voc_file_has_trigger_phrases_for_every_language(lang):
    lines = (LOCALE_DIR / lang / "voices_of_tomorrow.voc").read_text().strip().splitlines()
    assert len(lines) > 0
    assert "voices of tomorrow" in [l.strip() for l in lines]
