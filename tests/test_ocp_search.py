"""Tests for search_voices_of_tomorrow() - the @ocp_search()-decorated
handler. Unlike the ovos.common_reading.* bus protocol used by every
other provider in this family, OCP calls this method directly - there's
no bus message to mock, just a (phrase, media_type) call and a list of
result dicts back."""
from conftest import MediaType, PlaybackType


def test_specific_title_match_returns_that_episode(skill):
    results = skill.search_voices_of_tomorrow("play a lighthouse through time", None)

    assert len(results) >= 1
    top = max(results, key=lambda r: r["match_confidence"])
    assert top["title"] == "A Lighthouse Through Time"
    assert top["uri"].endswith(".mp3")
    assert top["media_type"] == MediaType.PODCAST
    assert top["playback"] == PlaybackType.AUDIO


def test_collection_phrase_matches_all_episodes(skill):
    results = skill.search_voices_of_tomorrow("play voices of tomorrow", None)

    titles = {r["title"] for r in results}
    assert titles == {"A Lighthouse Through Time", "Terminal Bar"}


def test_unrelated_phrase_returns_no_results(skill):
    results = skill.search_voices_of_tomorrow("play some jazz music", None)
    assert not results


def test_no_episodes_loaded_returns_nothing(skill):
    skill.episodes = []
    results = skill.search_voices_of_tomorrow("play voices of tomorrow", None)
    assert not results


def test_artist_defaults_when_author_missing(skill):
    skill.episodes = [{"title": "Mystery Story", "author": "", "url": "https://x/y.mp3", "pubdate": ""}]

    results = skill.search_voices_of_tomorrow("mystery story", None)

    assert results[0]["artist"] == "365tomorrows"
