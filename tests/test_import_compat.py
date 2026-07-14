from __future__ import annotations

import sys

from app.services.import_compat import prepare_f5_tts_import


def test_prepare_f5_tts_import_adds_private_path_to_six_importer() -> None:
    __import__("six")
    six_importers = [
        finder for finder in sys.meta_path if finder.__class__.__name__ == "_SixMetaPathImporter"
    ]
    for finder in six_importers:
        if hasattr(finder, "_path"):
            del finder._path

    prepare_f5_tts_import()

    assert six_importers
    assert all(finder._path == [] for finder in six_importers)
