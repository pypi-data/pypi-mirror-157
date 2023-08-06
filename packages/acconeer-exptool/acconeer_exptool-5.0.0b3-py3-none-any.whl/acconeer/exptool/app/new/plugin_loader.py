from __future__ import annotations

from .app_model import Plugin


def load_default_plugins() -> list[Plugin]:
    from acconeer.exptool.a121.algo.distance._detector_plugin import DISTANCE_DETECTOR_PLUGIN
    from acconeer.exptool.a121.algo.sparse_iq._plugin import SPARSE_IQ_PLUGIN

    return [
        SPARSE_IQ_PLUGIN,
        DISTANCE_DETECTOR_PLUGIN,
    ]
