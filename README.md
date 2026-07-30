# ovos-media-provider-radio-tuga

This is an OVOS **MediaProvider** plugin for Portuguese internet radio. It replaces the
deprecated OCP search skill
[`skill-ovos-radio-tuga`](https://github.com/TigreGotico/skill-ovos-radio-tuga).

The OCP pipeline loads MediaProvider plugins in-process, gates them by routing,
and calls `search()` directly. It does not broadcast `ovos.common_play.query`
over the bus and wait for skills to answer. This plugin ships a static catalog
of Portuguese radio stations (`res/radios_pt.json`). It exposes each matching
station as a [`mediavocab.Release`](https://github.com/TigreGotico/mediavocab)
with `MediaType.RADIO` and `StreamMode.CONTINUOUS`.

The catalog is a fixed list. `search()` runs as a local fuzzy filter: it scores
each station name against `signals.title` with Damerau-Levenshtein similarity
and returns the stations above a confidence threshold, best match first.

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
