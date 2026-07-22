"""Tests for fetch_episodes() - RSS parsing against a real captured
sample of the feed's structure (not live network calls)."""
from unittest.mock import MagicMock

import pytest
import requests
from conftest import FeedFetchError

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
<title>Voices of Tomorrow Archives - 365tomorrows</title>
<item>
    <title>A Lighthouse Through Time</title>
    <link>https://365tomorrows.com/2026/03/27/a-lighthouse-through-time-2/</link>
    <dc:creator><![CDATA[Otto Maton]]></dc:creator>
    <pubDate>Fri, 27 Mar 2026 21:23:46 +0000</pubDate>
    <enclosure url="https://365tomorrows.com/wp-content/uploads/2026/03/VOT_LighthouseThroughTime.mp3" length="3939801" type="audio/mpeg" />
</item>
<item>
    <title>No Audio Here</title>
    <link>https://365tomorrows.com/2020/01/01/no-audio/</link>
    <dc:creator><![CDATA[Someone]]></dc:creator>
    <pubDate>Wed, 01 Jan 2020 00:00:00 +0000</pubDate>
</item>
</channel>
</rss>"""


def _fake_response(content, status_ok=True):
    r = MagicMock()
    r.content = content.encode("utf-8")
    if status_ok:
        r.raise_for_status = MagicMock()
    else:
        r.raise_for_status = MagicMock(side_effect=requests.HTTPError("500"))
    return r


def test_fetch_episodes_parses_title_author_and_enclosure_url(skill, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _fake_response(SAMPLE_FEED))

    episodes = skill.fetch_episodes()

    assert len(episodes) == 1  # the item with no <enclosure> is skipped
    assert episodes[0]["title"] == "A Lighthouse Through Time"
    assert episodes[0]["author"] == "Otto Maton"
    assert episodes[0]["url"] == "https://365tomorrows.com/wp-content/uploads/2026/03/VOT_LighthouseThroughTime.mp3"


def test_fetch_episodes_skips_items_without_enclosure(skill, monkeypatch):
    """Regression guard: an item with no playable audio must not be
    returned as a 'result' with no uri."""
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _fake_response(SAMPLE_FEED))
    episodes = skill.fetch_episodes()
    assert all(ep["url"] for ep in episodes)


def test_fetch_episodes_network_error_raises(skill, monkeypatch):
    def fail(*a, **kw):
        raise requests.ConnectionError("boom")
    monkeypatch.setattr(requests, "get", fail)

    with pytest.raises(FeedFetchError):
        skill.fetch_episodes()


def test_fetch_episodes_http_error_raises(skill, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _fake_response(SAMPLE_FEED, status_ok=False))

    with pytest.raises(FeedFetchError):
        skill.fetch_episodes()


def test_fetch_episodes_malformed_xml_raises(skill, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _fake_response("not xml at all <<<"))

    with pytest.raises(FeedFetchError):
        skill.fetch_episodes()


def test_fetch_episodes_no_usable_items_raises(skill, monkeypatch):
    empty_feed = '<?xml version="1.0"?><rss><channel><title>Empty</title></channel></rss>'
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _fake_response(empty_feed))

    with pytest.raises(FeedFetchError):
        skill.fetch_episodes()
