from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.9)

    def load(self, audio_path: Path) -> None:
        self._player.setSource(QUrl.fromLocalFile(str(audio_path.resolve())))

    def play(self) -> None:
        self._player.play()

    def stop(self) -> None:
        self._player.stop()

    def is_available(self) -> bool:
        return self._player.source().isValid()
