from __future__ import annotations

import sys

from app.services.import_compat import prepare_f5_tts_import


def test_prepare_f5_tts_import_adds_path_to_six_importer() -> None:
    prepare_f5_tts_import()

    six_importers = [
        finder for finder in sys.meta_path if finder.__class__.__name__ == "_SixMetaPathImporter"
    ]

    assert six_importers
    assert all(hasattr(finder, "path") for finder in six_importers)
