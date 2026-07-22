"""Smoke tests - is this actually an OCP skill, not an OVOSSkill/
ovos.common_reading.* provider."""
from conftest import VoicesOfTomorrowSkill, FeedFetchError, MediaType, PlaybackType


def test_imports_cleanly():
    assert VoicesOfTomorrowSkill is not None
    assert issubclass(FeedFetchError, Exception)


def test_is_an_ocp_skill_not_a_common_reading_provider():
    from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(VoicesOfTomorrowSkill, OVOSCommonPlaybackSkill)
    # deliberately NOT the OVOSSkill/ovos.common_reading.* pattern used
    # by every other provider in this family - see module docstring
    assert not hasattr(VoicesOfTomorrowSkill, "handle_search")


def test_search_handler_is_registered_as_ocp_search():
    method = VoicesOfTomorrowSkill.search_voices_of_tomorrow
    assert getattr(method, "is_ocp_search_handler", False) is True
