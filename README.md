# ovos-media-provider-radio-tuga

OVOS **MediaProvider** plugin for Portuguese internet radio. Replaces the
deprecated OCP search skill
[`skill-ovos-radio-tuga`](https://github.com/TigreGotico/skill-ovos-radio-tuga).

Instead of broadcasting `ovos.common_play.query` over the bus and waiting for
skills to answer, the OCP pipeline loads MediaProvider plugins in-process, gates
them by routing, and calls `search()` directly. This plugin ships a curated,
static catalog of Portuguese radio stations (`res/radios_pt.json`) and exposes
each matching station as a [`mediavocab.Release`](https://github.com/TigreGotico/mediavocab)
with `MediaType.RADIO` and `StreamMode.CONTINUOUS`.

The catalog is a fixed list, so `search()` is a local fuzzy filter: each station
name is scored against `signals.title` with a Damerau-Levenshtein similarity and
stations above a confidence threshold are returned, best first.

## Install

```bash
pip install ovos-media-provider-radio-tuga
```

## Routing

| Axis | Value |
|------|-------|
| `media` | `RADIO` |
| `playback_type` | `AUDIO` |
| `genre_filter` | *(none)* |

## Entry point

```toml
[project.entry-points."opm.media.provider"]
radio_tuga = "ovos_media_provider_radio_tuga:RadioTugaMediaProvider"
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `min_confidence` | `60` | Minimum fuzzy-match confidence (0-100) for a station to be returned. |
| `max_results` | `10` | Maximum number of matching stations returned per search. |

## License

Apache-2.0
