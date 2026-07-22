"""Tests for the episode cache - same TTL-based staleness pattern used
by every RSS-based provider in this family (ovos-skill-ovosblog,
ovos-skill-arxiv-papers, ovos-skill-365tomorrows-stories)."""
import time
from unittest.mock import MagicMock

from conftest import FeedFetchError


def test_refresh_episodes_uses_fresh_cache_without_scraping(skill):
    fresh_episodes = [{"title": "Cached Story", "author": "X", "url": "https://x/y.mp3", "pubdate": ""}]
    skill._write_index_cache(fresh_episodes)
    skill.fetch_episodes = MagicMock(side_effect=AssertionError("should not fetch when cache is fresh"))

    skill.refresh_episodes()

    assert skill.episodes == fresh_episodes


def test_refresh_episodes_falls_back_to_stale_cache_on_fetch_failure(skill):
    stale_episodes = [{"title": "Old Story", "author": "X", "url": "https://x/y.mp3", "pubdate": ""}]
    skill._write_index_cache(stale_episodes)
    # force staleness
    cache_file = skill._index_cache_filename()
    with skill.file_system.open(cache_file, "r") as f:
        import json
        data = json.load(f)
    data["fetched_at"] = time.time() - 999999
    with skill.file_system.open(cache_file, "w") as f:
        json.dump(data, f)

    skill.fetch_episodes = MagicMock(side_effect=FeedFetchError("network down"))

    skill.refresh_episodes()

    assert skill.episodes == stale_episodes


def test_refresh_episodes_writes_cache_after_successful_fetch(skill):
    new_episodes = [{"title": "Fresh Story", "author": "X", "url": "https://x/y.mp3", "pubdate": ""}]
    skill.fetch_episodes = MagicMock(return_value=new_episodes)

    skill.refresh_episodes()

    assert skill.episodes == new_episodes
    cached = skill._read_index_cache()
    assert cached == new_episodes
