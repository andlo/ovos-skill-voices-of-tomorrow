# <img src='ui/icon.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Voices of Tomorrow

An **OCP** (ovos-common-play) skill - plays pre-recorded audio readings
of [365tomorrows.com](https://365tomorrows.com) flash fiction stories.

[![Tests](https://github.com/andlo/ovos-skill-voices-of-tomorrow/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-voices-of-tomorrow/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-voices-of-tomorrow.svg)](https://pypi.org/project/ovos-skill-voices-of-tomorrow/)

## This is deliberately NOT a common-reading provider

[ovos-skill-365tomorrows-stories](https://github.com/andlo/ovos-skill-365tomorrows-stories)
reads the *text* of 365tomorrows stories aloud via TTS, as a provider
for
[ovos-common-reading-pipeline-plugin](https://github.com/andlo/ovos-common-reading-pipeline-plugin).
This is a completely different, separate skill: it plays *pre-recorded
audio files* of "Voices of Tomorrow" readings via OCP, exactly matching
the distinction documented in that plugin's README ("What this is not:
an audiobook or audio-file player... already well covered by OCP media
skills"). Same source, two different skill types, two different repos.

## What was checked before building this

No existing "Voices of Tomorrow" skill, and no generic/configurable
podcast-RSS OCP skill to point at this feed instead of a dedicated one.
The closest thing, `ovos-skill-news`, turned out to be a fixed,
hardcoded catalog of live radio streams (new feeds added via PRs to its
own source), not a configurable single-podcast player. The closest real
architectural precedent is
[skill-hppodcraft](https://github.com/JarbasSkills/skill-hppodcraft)
(The H.P. Lovecraft Literary Podcast) - a single dedicated podcast-
source OCP skill - and this follows that same pattern.

## Install
```bash
pip install ovos-skill-voices-of-tomorrow
```

## Source

RSS feed: `https://365tomorrows.com/category/voices-of-tomorrow/feed`,
with genuine `<enclosure>` tags pointing at playable MP3/M4A files.
This is a sporadic, occasional series (episodes appear every few months
to years, not daily) rather than a regularly-updated show - the episode
list is cached for 24h, refreshed on skill load, with a stale-cache
fallback if the feed can't be reached.

Same license as the main site: Creative Commons
Attribution-NonCommercial-NoDerivs 3.0.

## Examples
- "play voices of tomorrow"
- "play the 365tomorrows podcast"
- "play a lighthouse through time"

## Category
**Entertainment**

## Tags
#podcast #ocp #scifi #audio
