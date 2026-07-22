"""
skill OVOS Voices of Tomorrow
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

OCP (ovos-common-play) skill for "Voices of Tomorrow" - pre-recorded
audio readings of some of 365tomorrows.com's flash fiction stories.

Deliberately a SEPARATE skill and SEPARATE repo from
ovos-skill-365tomorrows-stories, even though they share a source: that
one is a *text* provider for ovos-common-reading-pipeline-plugin
(reads text aloud via TTS, content_type "story"/"tale"); this one plays
*pre-recorded audio files* via OCP. Different skill type entirely -
an OVOSCommonPlaybackSkill with an @ocp_search() handler, not an
OVOSSkill answering ovos.common_reading.* bus messages. See
ovos-common-reading-pipeline-plugin#25 and that plugin's README
("What this is not: an audiobook or audio-file player... already well
covered by OCP media skills").

Researched first (see ovos-common-reading-pipeline-plugin#25 discussion):
no existing "Voices of Tomorrow" skill, and no generic/configurable
podcast-RSS OCP skill to point at this feed instead - the closest thing,
ovos-skill-news, is a fixed hardcoded catalog of live radio streams, not
a configurable single-podcast player. ovos-skill-hppodcraft (The H.P.
Lovecraft Literary Podcast) is the closest architectural precedent - a
single dedicated podcast-source OCP skill - and this follows that same
pattern.
"""

from os.path import join, dirname
import json
import time
import xml.etree.ElementTree as ET

import requests
from ovos_plugin_common_play.ocp.media import MediaType, PlaybackType
from ovos_utils.parse import fuzzy_match
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, ocp_search


class FeedFetchError(Exception):
    """Raised when the podcast feed could not be fetched or parsed."""


FEED_URL = "https://365tomorrows.com/category/voices-of-tomorrow/feed"
# a handful of new episodes a year (sporadic, not daily, by design - see
# README) - no need to check more often than once a day
INDEX_CACHE_TTL = 60 * 60 * 24

COLLECTION_ALIASES = ["voices of tomorrow", "365tomorrows podcast",
                       "the 365tomorrows podcast", "flash fiction podcast"]
COLLECTION_MATCH_THRESHOLD = 0.6
TITLE_MATCH_THRESHOLD = 0.5
SOURCE_NAME = "365tomorrows.com"
LICENSE_NOTICE = "Creative Commons Attribution-NonCommercial-NoDerivs 3.0"

class VoicesOfTomorrowSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          supported_media=[MediaType.PODCAST, MediaType.AUDIO],
                          skill_icon=join(dirname(__file__), "ui", "icon.png"),
                          skill_voc_filename="voices_of_tomorrow",
                          **kwargs)

    def initialize(self):
        self.episodes = []  # list of {title, author, url, length, pubdate}
        self.refresh_episodes()

    def _index_cache_filename(self):
        return "episodes.json"

    def _read_index_cache(self):
        cache_file = self._index_cache_filename()
        if not self.file_system.exists(cache_file):
            return None
        try:
            with self.file_system.open(cache_file, "r") as f:
                cached = json.load(f)
        except (OSError, ValueError) as e:
            self.log.warning(f"could not read episode cache: {e}")
            return None
        if time.time() - cached.get("fetched_at", 0) > INDEX_CACHE_TTL:
            return None
        return cached.get("episodes")

    def _write_index_cache(self, episodes):
        try:
            with self.file_system.open(self._index_cache_filename(), "w") as f:
                json.dump({"fetched_at": time.time(), "episodes": episodes}, f)
        except OSError as e:
            self.log.warning(f"could not write episode cache: {e}")

    def _read_raw_cache_ignoring_staleness(self):
        """Used only as a last-resort fallback when a fresh fetch fails
        - unlike _read_index_cache(), this ignores INDEX_CACHE_TTL, so
        it can recover an old episode list rather than returning
        nothing (a real bug found in testing: refresh_episodes() used
        to call _read_index_cache() again in its except branch, which
        just returned None a second time for the same staleness reason)."""
        cache_file = self._index_cache_filename()
        if not self.file_system.exists(cache_file):
            return None
        try:
            with self.file_system.open(cache_file, "r") as f:
                return json.load(f).get("episodes")
        except (OSError, ValueError) as e:
            self.log.warning(f"could not read stale episode cache: {e}")
            return None

    def refresh_episodes(self):
        cached = self._read_index_cache()
        if cached is not None:
            self.episodes = cached
            return
        try:
            fetched = self.fetch_episodes()
        except FeedFetchError as e:
            self.log.error(f"could not fetch Voices of Tomorrow feed, using stale cache if any: {e}")
            self.episodes = self._read_raw_cache_ignoring_staleness() or []
            return
        self.episodes = fetched
        self._write_index_cache(fetched)

    def fetch_episodes(self):
        """RSS parse - same DC_CREATOR_TAG/ElementTree approach as
        ovos-skill-365tomorrows-stories's index building, but pulling
        <enclosure> (the playable audio URL) instead of the linked
        article page."""
        try:
            r = requests.get(FEED_URL, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            raise FeedFetchError(f"could not fetch {FEED_URL}: {e}") from e
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError as e:
            raise FeedFetchError(f"could not parse feed XML: {e}") from e

        episodes = []
        for item in root.iter("item"):
            enclosure = item.find("enclosure")
            title = item.findtext("title")
            if enclosure is None or not enclosure.get("url") or not title:
                continue
            creator_tag = "{http://purl.org/dc/elements/1.1/}creator"
            episodes.append({
                "title": title.strip(),
                "author": (item.findtext(creator_tag) or "").strip(),
                "url": enclosure.get("url"),
                "pubdate": item.findtext("pubDate") or "",
            })
        if not episodes:
            raise FeedFetchError("feed parsed but contained no usable <item>/<enclosure> pairs")
        return episodes

    @ocp_search()
    def search_voices_of_tomorrow(self, phrase, media_type):
        if not self.episodes:
            return
        phrase_lower = phrase.lower()

        collection_score = max(
            (fuzzy_match(phrase_lower, alias) for alias in COLLECTION_ALIASES),
            default=0.0,
        )

        results = []
        for ep in self.episodes:
            title_score = fuzzy_match(phrase_lower, ep["title"].lower())
            # a specific title match should win outright; otherwise fall
            # back to the collection-level ('play voices of tomorrow')
            # score, which matches every episode with the same
            # confidence - OCP is expected to offer/queue them as a set
            confidence = title_score if title_score >= TITLE_MATCH_THRESHOLD else collection_score
            if confidence < COLLECTION_MATCH_THRESHOLD and title_score < TITLE_MATCH_THRESHOLD:
                continue
            results.append({
                "media_type": MediaType.PODCAST,
                "playback": PlaybackType.AUDIO,
                "uri": ep["url"],
                "title": ep["title"],
                "artist": ep["author"] or "365tomorrows",
                "match_confidence": int(confidence * 100),
                "skill_icon": self.skill_icon,
            })
        return results
