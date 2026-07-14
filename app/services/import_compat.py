from __future__ import annotations

import sys


def prepare_f5_tts_import() -> None:
    try:
        import six
    except ImportError:
        return

    del six
    for finder in sys.meta_path:
        if finder.__class__.__name__ == "_SixMetaPathImporter" and not hasattr(finder, "path"):
            finder.path = None
