from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.models.settings import Emotion, SplitMode
from app.ui.main_window import MainWindow


def test_split_mode_and_emotion_are_independent() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    window.paragraphs_radio.setChecked(True)
    window.dramatic_radio.setChecked(True)
    settings = window._collect_settings()

    assert window.paragraphs_radio.isChecked()
    assert window.dramatic_radio.isChecked()
    assert settings.split_mode is SplitMode.PARAGRAPHS
    assert settings.emotion is Emotion.DRAMATIC

    window.close()
    app.processEvents()
