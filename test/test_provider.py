"""Unit tests for RadioTugaMediaProvider.

The station catalog is a static bundled JSON list, so there is no network to
mock; tests run against the real package data and against an injected fake
catalog for deterministic scoring assertions.
"""
from mediavocab import MediaType, Release, Signals, StreamMode

from ovos_media_provider_radio_tuga import (RadioTugaMediaProvider,
                                            load_stations)


def test_instantiation():
    prov = RadioTugaMediaProvider()
    assert prov.name == "radio_tuga"


def test_bundled_catalog_loads():
    stations = load_stations()
    assert len(stations) > 100
    assert all(s.get("stream") for s in stations)
    assert all("name" in s for s in stations)


def test_search_accepts_context_kwargs():
    """The provider accepts the pipeline's request-context kwargs."""
    prov = RadioTugaMediaProvider()
    results = prov.search(
        Signals(medium=MediaType.RADIO, title="rfm"),
        lang="pt-pt",
        supported_playback_types={"audio"},
        blocked_genres={"adult"},
        region="PT",
        session_id="sess-1",
    )
    assert isinstance(results, list)
    assert all(isinstance(r, Release) for r in results)


def test_search_finds_known_station():
    prov = RadioTugaMediaProvider()
    results = prov.search(Signals(medium=MediaType.RADIO, title="RFM"))
    assert results
    top = results[0]
    assert isinstance(top, Release)
    assert top.work.media_type == MediaType.RADIO
    assert top.work.broadcaster_country == "PT"
    assert top.stream_mode == StreamMode.CONTINUOUS
    assert top.uri
    assert "rfm" in top.work.title.lower()


def test_results_sorted_by_confidence():
    prov = RadioTugaMediaProvider()
    results = prov.search(Signals(medium=MediaType.RADIO, title="radio"))
    confidences = [r.match_confidence for r in results]
    assert confidences == sorted(confidences, reverse=True)


def test_search_no_query_browses_catalog():
    prov = RadioTugaMediaProvider({"max_results": 5})
    results = prov.search(Signals(medium=MediaType.RADIO))
    assert len(results) == 5
    assert all(isinstance(r, Release) for r in results)


def test_search_respects_max_results():
    prov = RadioTugaMediaProvider({"max_results": 3, "min_confidence": 0})
    results = prov.search(Signals(medium=MediaType.RADIO, title="radio"))
    assert len(results) <= 3


def test_search_no_match_returns_empty():
    prov = RadioTugaMediaProvider({"min_confidence": 95})
    results = prov.search(
        Signals(medium=MediaType.RADIO, title="zzzzz no such station qqqq"))
    assert results == []


def test_search_swallows_errors():
    prov = RadioTugaMediaProvider()
    prov.stations = [{"stream": "x"}]  # missing "name" -> KeyError caught
    assert prov.search(Signals(medium=MediaType.RADIO, title="x")) == []
