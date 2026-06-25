"""Radio Tuga MediaProvider plugin for OVOS.

Exposes a curated catalog of Portuguese internet-radio stations to the OCP
pipeline as a
:class:`~ovos_plugin_manager.templates.media_provider.MediaProvider`. Replaces
the deprecated OCP search skill ``skill-ovos-radio-tuga``.

The station catalog is a static, bundled JSON list (``res/radios_pt.json``,
scraped from radios-online.pt / myTuner) keyed by station page URL, each value
holding ``name``, ``image`` and ``stream`` fields. There is no per-query search
endpoint, so :meth:`RadioTugaMediaProvider.search` is a local fuzzy filter over
the catalog: each station name is scored against ``signals.title`` with a
Damerau-Levenshtein similarity and stations above a confidence threshold are
returned as :class:`mediavocab.Release` objects (one ``RADIO`` ``Work`` per
station, one continuous-stream ``Release``).
"""
import json
from os.path import dirname, join
from typing import ClassVar, List, Optional, Set

from ovos_utils.log import LOG
from ovos_utils.parse import MatchStrategy, fuzzy_match

from mediavocab import MediaType, Release, Signals, StreamMode, Work

from ovos_plugin_manager.templates.media_provider import MediaProvider

from ovos_media_provider_radio_tuga.version import __version__  # noqa: F401

_STATIONS_PATH = join(dirname(__file__), "res", "radios_pt.json")
_ARTIST = "Radios de Portugal"


def load_stations(path: str = _STATIONS_PATH) -> List[dict]:
    """Load the bundled station catalog, dropping entries with no stream URL."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data.values() if s.get("stream")]


class RadioTugaMediaProvider(MediaProvider):
    """Search the Portuguese radio catalog and return playable radio releases."""

    name: ClassVar[str] = "radio_tuga"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        # min fuzzy confidence (0-100) for a station to be returned
        self.min_confidence: int = int(self.config.get("min_confidence", 60))
        # max stations to return per search, overridable via plugin config
        self.max_results: int = int(self.config.get("max_results", 10))
        self.stations: List[dict] = load_stations()

    @staticmethod
    def _station_to_release(station: dict, confidence: float) -> Release:
        """Build a RADIO Release. ``confidence`` is a 0.0-1.0 fraction."""
        work = Work(title=station["name"],
                    media_type=MediaType.RADIO,
                    broadcaster_country="PT",
                    language="pt")
        return Release(work=work,
                       uri=station["stream"],
                       image=station.get("image", ""),
                       stream_mode=StreamMode.CONTINUOUS,
                       match_confidence=max(0.0, min(1.0, confidence)))

    def search(self, signals: Signals, lang: str = "en-us", *,
               supported_playback_types: Optional[Set[str]] = None,
               blocked_genres: Optional[Set[str]] = None,
               region: Optional[str] = None,
               session_id: Optional[str] = None) -> List[Release]:
        """Fuzzy-match ``signals.title`` against the bundled Portuguese radio
        catalog and return the best-scoring stations as ``RADIO`` releases.

        A bare ``RADIO`` request with no title browses the catalog (returns up
        to ``max_results`` stations). Returns ``[]`` on any error or no match.
        """
        title = (signals.title or "").strip().lower()

        releases: List[Release] = []
        try:
            if not title:
                # bare RADIO request -> browse the catalog
                for station in self.stations[:self.max_results]:
                    releases.append(self._station_to_release(station, 1.0))
                return releases

            threshold = self.min_confidence / 100.0
            scored = []
            for station in self.stations:
                score = fuzzy_match(
                    station["name"].lower(), title,
                    strategy=MatchStrategy.DAMERAU_LEVENSHTEIN_SIMILARITY)
                if score < threshold:
                    continue
                scored.append((score, station))
            scored.sort(key=lambda k: k[0], reverse=True)
            for score, station in scored[:self.max_results]:
                releases.append(self._station_to_release(station, score))
        except Exception:
            LOG.exception("Radio Tuga search failed")
            return []
        return releases
